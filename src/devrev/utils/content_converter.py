"""Content format detection and conversion for DevRev articles.

Converts between HTML, Markdown, plain text, and the ``devrev/rt``
(ProseMirror JSON) format used by DevRev's UI for inline article rendering.

The ``devrev/rt`` format is a ProseMirror / Tiptap JSON document
structure wrapped in an ``{"article": ..., "artifactIds": []}`` envelope.

Supported formats
-----------------
* **HTML** – parsed with *BeautifulSoup 4* for robust DOM walking.
* **Markdown** – first converted to HTML via the *markdown* library
  (with ``tables``, ``fenced_code``, and ``codehilite`` extensions),
  then parsed identically.
* **Plain text** – wrapped in a single ``<p>`` before conversion.
* **devrev/rt JSON** – ProseMirror document envelope; detected and
  returned unchanged when converting *to* devrev/rt.

Public API
----------
* :func:`detect_content_format` – detect the format of a content string.
* :func:`html_to_devrev_rt` – convert any supported format → devrev/rt.
* :func:`devrev_rt_to_markdown` – convert devrev/rt → Markdown.
* :func:`devrev_rt_to_html` – convert devrev/rt → HTML.
"""

from __future__ import annotations

import html as html_module
import json
import re
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag  # type: ignore[attr-defined]
from markdown import markdown as md_to_html  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# Tag mapping tables
# ---------------------------------------------------------------------------

# Block-level HTML tags → ProseMirror node types
_BLOCK_TAGS: dict[str, str] = {
    "p": "paragraph",
    "h1": "heading",
    "h2": "heading",
    "h3": "heading",
    "h4": "heading",
    "h5": "heading",
    "h6": "heading",
    "blockquote": "blockquote",
    "pre": "codeBlock",
    "hr": "horizontalRule",
    "ul": "bulletList",
    "ol": "orderedList",
    "li": "listItem",
    "table": "table",
    "thead": "_skip",
    "tbody": "_skip",
    "tfoot": "_skip",
    "tr": "tableRow",
    "td": "tableCell",
    "th": "tableHeader",
}

# Inline HTML tags → ProseMirror mark types
_MARK_TAGS: dict[str, str] = {
    "strong": "bold",
    "b": "bold",
    "em": "italic",
    "i": "italic",
    "code": "code",
    "s": "strike",
    "del": "strike",
    "u": "underline",
    "a": "link",
    "sub": "subscript",
    "sup": "superscript",
}

# Transparent wrapper tags whose children are promoted to the parent.
_WRAPPER_TAGS: set[str] = {
    "div",
    "span",
    "section",
    "article",
    "main",
    "aside",
    "header",
    "footer",
    "nav",
    "figure",
    "figcaption",
    "thead",
    "tbody",
    "tfoot",
    "html",
    "body",
    "[document]",
}

# Markdown heuristic: if content contains at least one of these patterns it
# is likely Markdown rather than HTML.
_MD_PATTERNS: re.Pattern[str] = re.compile(
    r"(?m)"
    r"(?:^#{1,6}\s)"  # ATX headings
    r"|(?:^\s*[-*+]\s)"  # unordered list items
    r"|(?:^\s*\d+\.\s)"  # ordered list items
    r"|(?:^```)"  # fenced code blocks
    r"|(?:\*\*.+?\*\*)"  # bold **text**
    r"|(?:__.+?__)"  # bold __text__
    r"|(?:\[.+?\]\(.+?\))"  # links [text](url)
    r"|(?:!\[.*?\]\(.+?\))"  # images ![alt](url)
    r"|(?:^\|.+\|$)"  # table rows |a|b|
)


# ---------------------------------------------------------------------------
# DOM → ProseMirror walker
# ---------------------------------------------------------------------------


def _walk(
    element: Tag | NavigableString | Any,
    marks: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Recursively walk a BS4 element tree and return ProseMirror nodes."""
    if marks is None:
        marks = []

    if isinstance(element, NavigableString):
        text = str(element)
        if not text.strip():
            return []
        node: dict[str, Any] = {"type": "text", "text": text}
        if marks:
            node["marks"] = [dict(m) for m in marks]
        return [node]

    tag = element.name.lower()

    # --- Self-closing / void elements ---
    if tag == "br":
        return [{"type": "hardBreak"}]

    if tag == "hr":
        return [{"type": "horizontalRule"}]

    if tag == "img":
        src = element.get("src", "")
        if src:
            return [
                {
                    "type": "image",
                    "attrs": {
                        "src": src,
                        "alt": element.get("alt", ""),
                        "title": element.get("title"),
                    },
                }
            ]
        return []

    # --- Inline mark tags ---
    if tag in _MARK_TAGS:
        mark: dict[str, Any] = {"type": _MARK_TAGS[tag]}
        if tag == "a":
            mark["attrs"] = {
                "href": element.get("href", ""),
                "target": element.get("target", "_blank"),
            }
        new_marks = [*marks, mark]
        nodes: list[dict[str, Any]] = []
        for child in element.children:
            nodes.extend(_walk(child, new_marks))
        return nodes

    # --- Transparent wrappers – promote children ---
    if tag in _WRAPPER_TAGS:
        nodes = []
        for child in element.children:
            nodes.extend(_walk(child, marks))
        return nodes

    # --- Code blocks: <pre> possibly containing <code> ---
    if tag == "pre":
        language = None
        code_tag = element.find("code")
        text_content = ""
        if isinstance(code_tag, Tag):
            # Extract language from class="language-xxx"
            classes: list[str] = code_tag.get("class") or []  # type: ignore[assignment]
            if isinstance(classes, list):
                for cls in classes:
                    if cls.startswith("language-"):
                        language = cls[len("language-") :]
                        break
            text_content = code_tag.get_text()
        else:
            text_content = element.get_text()
        cb_node: dict[str, Any] = {
            "type": "codeBlock",
            "attrs": {"language": language},
        }
        if text_content:
            cb_node["content"] = [{"type": "text", "text": text_content}]
        return [cb_node]

    # --- Block-level tags ---
    if tag in _BLOCK_TAGS:
        pm_type = _BLOCK_TAGS[tag]
        block = _make_block_node(tag, pm_type, element)

        # Collect children
        children: list[dict[str, Any]] = []
        for child in element.children:
            children.extend(_walk(child, marks))

        # Containers that require block-level children wrap bare inlines
        if pm_type in ("listItem", "tableCell", "tableHeader", "blockquote"):
            children = _ensure_block_children(children)

        if children:
            block["content"] = children
        elif pm_type in ("listItem", "tableCell", "tableHeader", "blockquote"):
            block["content"] = [{"type": "paragraph", "attrs": {"textAlign": None}}]

        return [block]

    # --- Unknown tags – treat as transparent wrapper ---
    nodes = []
    for child in element.children:
        nodes.extend(_walk(child, marks))
    return nodes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_INLINE_TYPES: set[str] = {"text", "hardBreak", "image"}


def _make_block_node(tag: str, pm_type: str, el: Tag) -> dict[str, Any]:
    """Build a ProseMirror block node with the correct attrs."""
    node: dict[str, Any] = {"type": pm_type}

    if pm_type == "heading":
        level = int(tag[1]) if len(tag) == 2 and tag[1].isdigit() else 1
        node["attrs"] = {"textAlign": None, "level": level}
    elif pm_type == "paragraph":
        node["attrs"] = {"textAlign": None}
    elif pm_type in ("tableCell", "tableHeader"):
        colspan_val = el.get("colspan")
        rowspan_val = el.get("rowspan")
        node["attrs"] = {
            "colspan": int(str(colspan_val)) if colspan_val else 1,
            "rowspan": int(str(rowspan_val)) if rowspan_val else 1,
            "colwidth": None,
        }
    elif pm_type == "orderedList":
        start = el.get("start")
        if start is not None:
            node["attrs"] = {"start": int(str(start))}

    return node


def _ensure_block_children(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Wrap consecutive inline nodes in a paragraph.

    ProseMirror requires that ``listItem``, ``tableCell``, ``tableHeader``,
    and ``blockquote`` contain only block-level children.
    """
    result: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []

    for n in nodes:
        if n.get("type") in _INLINE_TYPES:
            pending.append(n)
        else:
            if pending:
                result.append(
                    {"type": "paragraph", "attrs": {"textAlign": None}, "content": pending}
                )
                pending = []
            result.append(n)

    if pending:
        result.append({"type": "paragraph", "attrs": {"textAlign": None}, "content": pending})

    return result


def _is_markdown(content: str) -> bool:
    """Heuristic check: does *content* look like Markdown rather than HTML?"""
    # If it starts with an HTML tag it's almost certainly HTML.
    stripped = content.strip()
    if stripped.startswith("<") and not stripped.startswith("<!"):
        return False
    return bool(_MD_PATTERNS.search(content))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_MD_EXTENSIONS = ["tables", "fenced_code", "md_in_html"]


def html_to_devrev_rt(content: str) -> str:
    """Convert HTML or Markdown to DevRev Rich Text (ProseMirror JSON).

    The returned string is JSON-encoded and ready to be uploaded as an
    artifact with ``file_type="devrev/rt"``.

    Content detection
    -----------------
    1. If *content* is already valid ``devrev/rt`` JSON (has an ``"article"``
       key), it is returned **unchanged**.
    2. If *content* looks like **Markdown** (headings, lists, fenced code,
       links, images, tables), it is first converted to HTML via the
       ``markdown`` library, then parsed.
    3. Otherwise it is treated as **HTML** (or plain text, which is wrapped
       in a ``<p>``).

    Args:
        content: HTML, Markdown, or plain-text content string.

    Returns:
        JSON string in devrev/rt format.

    Example:
        >>> rt = html_to_devrev_rt("# Hello\\n\\nWorld")
        >>> import json; doc = json.loads(rt)
        >>> doc["article"]["type"]
        'doc'
    """
    # 1. Already devrev/rt JSON? Return as-is.
    stripped = content.strip()
    if stripped.startswith("{"):
        try:
            parsed = json.loads(stripped)
            if "article" in parsed:
                return stripped
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Detect Markdown and convert to HTML first.
    html = content
    if _is_markdown(content):
        html = md_to_html(content, extensions=_MD_EXTENSIONS)

    # 3. Parse HTML with BeautifulSoup.
    soup = BeautifulSoup(html, "html.parser")
    nodes = _walk(soup)

    # Wrap any top-level inline nodes in paragraphs.
    nodes = _ensure_block_children(nodes)

    # Guarantee at least one block node.
    if not nodes:
        nodes = [{"type": "paragraph", "attrs": {"textAlign": None}}]

    doc: dict[str, Any] = {"type": "doc", "content": nodes}
    envelope: dict[str, Any] = {"article": doc, "artifactIds": []}
    return json.dumps(envelope)


# ---------------------------------------------------------------------------
# Content format detection
# ---------------------------------------------------------------------------

#: Canonical format identifiers returned by :func:`detect_content_format`.
CONTENT_FORMAT_DEVREV_RT = "devrev/rt"
CONTENT_FORMAT_MARKDOWN = "text/markdown"
CONTENT_FORMAT_HTML = "text/html"
CONTENT_FORMAT_PLAIN = "text/plain"


def detect_content_format(content: str) -> str:
    """Detect the format of an article content string.

    The detection logic is:

    1. If *content* is valid JSON with an ``"article"`` key → ``"devrev/rt"``
    2. If *content* matches common Markdown patterns → ``"text/markdown"``
    3. If *content* contains HTML tags → ``"text/html"``
    4. Otherwise → ``"text/plain"``

    Args:
        content: The raw content string to inspect.

    Returns:
        One of ``"devrev/rt"``, ``"text/markdown"``, ``"text/html"``,
        or ``"text/plain"``.

    Example:
        >>> detect_content_format("# Hello\\n\\nWorld")
        'text/markdown'
        >>> detect_content_format("<p>Hello</p>")
        'text/html'
        >>> detect_content_format('{"article": {"type": "doc"}}')
        'devrev/rt'
        >>> detect_content_format("Just plain text")
        'text/plain'
    """
    stripped = content.strip()

    # 1. devrev/rt JSON envelope
    if stripped.startswith("{"):
        try:
            parsed = json.loads(stripped)
            if "article" in parsed:
                return CONTENT_FORMAT_DEVREV_RT
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Markdown heuristics
    if _is_markdown(content):
        return CONTENT_FORMAT_MARKDOWN

    # 3. HTML (contains tags)
    if re.search(r"<[a-zA-Z][^>]*>", stripped):
        return CONTENT_FORMAT_HTML

    # 4. Fallback
    return CONTENT_FORMAT_PLAIN


# ---------------------------------------------------------------------------
# devrev/rt → Markdown converter
# ---------------------------------------------------------------------------

# Mapping of ProseMirror heading levels to ATX prefix
_HEADING_PREFIX: dict[int, str] = {1: "#", 2: "##", 3: "###", 4: "####", 5: "#####", 6: "######"}


def _pm_nodes_to_markdown(nodes: list[dict[str, Any]], *, indent: str = "") -> str:
    """Recursively convert a list of ProseMirror nodes to Markdown."""
    parts: list[str] = []
    for node in nodes:
        ntype = node.get("type", "")
        content: list[dict[str, Any]] = node.get("content", [])
        attrs: dict[str, Any] = node.get("attrs") or {}

        if ntype == "paragraph":
            parts.append(indent + _pm_inline_to_markdown(content))
            parts.append("")

        elif ntype == "heading":
            level = attrs.get("level", 1)
            prefix = _HEADING_PREFIX.get(level, "#")
            parts.append(f"{prefix} {_pm_inline_to_markdown(content)}")
            parts.append("")

        elif ntype == "codeBlock":
            lang = attrs.get("language") or ""
            code_text = _pm_inline_to_markdown(content)
            parts.append(f"```{lang}")
            parts.append(code_text)
            parts.append("```")
            parts.append("")

        elif ntype == "blockquote":
            inner = _pm_nodes_to_markdown(content, indent="> ")
            parts.append(inner)

        elif ntype == "bulletList":
            for item in content:
                if item.get("type") == "listItem":
                    item_md = _pm_nodes_to_markdown(item.get("content", []))
                    lines = item_md.strip().split("\n")
                    if lines:
                        parts.append(f"- {lines[0]}")
                        for line in lines[1:]:
                            parts.append(f"  {line}" if line else "")
            parts.append("")

        elif ntype == "orderedList":
            start = (node.get("attrs") or {}).get("start", 1) or 1
            for idx, item in enumerate(content):
                if item.get("type") == "listItem":
                    item_md = _pm_nodes_to_markdown(item.get("content", []))
                    lines = item_md.strip().split("\n")
                    if lines:
                        parts.append(f"{start + idx}. {lines[0]}")
                        for line in lines[1:]:
                            parts.append(f"   {line}" if line else "")
            parts.append("")

        elif ntype == "horizontalRule":
            parts.append("---")
            parts.append("")

        elif ntype == "table":
            parts.append(_pm_table_to_markdown(content))
            parts.append("")

        elif ntype == "image":
            src = attrs.get("src", "")
            alt = attrs.get("alt", "")
            parts.append(f"![{alt}]({src})")
            parts.append("")

        elif ntype == "text":
            # Top-level text shouldn't happen but handle gracefully
            parts.append(_pm_text_node_to_markdown(node))

        else:
            # Unknown node – recurse into children
            if content:
                parts.append(_pm_nodes_to_markdown(content, indent=indent))

    return "\n".join(parts)


def _pm_inline_to_markdown(nodes: list[dict[str, Any]]) -> str:
    """Convert a list of ProseMirror inline nodes to a single Markdown line."""
    parts: list[str] = []
    for node in nodes:
        ntype = node.get("type", "")
        if ntype == "text":
            parts.append(_pm_text_node_to_markdown(node))
        elif ntype == "hardBreak":
            parts.append("  \n")
        elif ntype == "image":
            attrs = node.get("attrs") or {}
            src = attrs.get("src", "")
            alt = attrs.get("alt", "")
            parts.append(f"![{alt}]({src})")
        else:
            # Recurse for unknown inline types
            content = node.get("content", [])
            if content:
                parts.append(_pm_inline_to_markdown(content))
    return "".join(parts)


def _pm_text_node_to_markdown(node: dict[str, Any]) -> str:
    """Convert a ProseMirror text node (with optional marks) to Markdown."""
    text = node.get("text", "")
    marks: list[dict[str, Any]] = node.get("marks", [])

    for mark in marks:
        mtype = mark.get("type", "")
        if mtype == "bold":
            text = f"**{text}**"
        elif mtype == "italic":
            text = f"*{text}*"
        elif mtype == "code":
            text = f"`{text}`"
        elif mtype == "strike":
            text = f"~~{text}~~"
        elif mtype == "link":
            href = (mark.get("attrs") or {}).get("href", "")
            text = f"[{text}]({href})"
        # underline, subscript, superscript have no standard Markdown equiv
        # – leave text unchanged for those
    return text


def _pm_table_to_markdown(rows: list[dict[str, Any]]) -> str:
    """Convert ProseMirror table rows to a Markdown table."""
    md_rows: list[list[str]] = []
    has_header = False
    for row in rows:
        if row.get("type") != "tableRow":
            continue
        cells: list[str] = []
        for cell in row.get("content", []):
            ctype = cell.get("type", "")
            if ctype in ("tableHeader", "tableCell"):
                if ctype == "tableHeader":
                    has_header = True
                cell_content = cell.get("content", [])
                cell_text = _pm_nodes_to_markdown(cell_content).strip()
                # Collapse newlines inside a cell for table rendering
                cell_text = cell_text.replace("\n", " ")
                cells.append(cell_text)
        md_rows.append(cells)

    if not md_rows:
        return ""

    # Determine column count
    col_count = max(len(r) for r in md_rows) if md_rows else 0
    # Pad rows to equal length
    for row in md_rows:
        while len(row) < col_count:
            row.append("")

    lines: list[str] = []
    for i, row in enumerate(md_rows):
        lines.append("| " + " | ".join(row) + " |")
        if i == 0 and has_header:
            lines.append("| " + " | ".join("---" for _ in row) + " |")

    # If no explicit header, add separator after first row anyway
    if not has_header and md_rows:
        lines.insert(1, "| " + " | ".join("---" for _ in md_rows[0]) + " |")

    return "\n".join(lines)


def devrev_rt_to_markdown(content: str) -> str:
    """Convert DevRev Rich Text (ProseMirror JSON) to Markdown.

    Accepts either the full ``{"article": ..., "artifactIds": [...]}``
    envelope or just the inner ``{"type": "doc", "content": [...]}``
    document node.

    If *content* is not valid devrev/rt JSON, it is returned unchanged
    (it might already be Markdown or plain text).

    Args:
        content: JSON string in devrev/rt format, or arbitrary text.

    Returns:
        Markdown string.

    Example:
        >>> rt = '{"article": {"type": "doc", "content": [{"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Hello"}]}]}}'
        >>> devrev_rt_to_markdown(rt)
        '# Hello\\n'
    """
    stripped = content.strip()
    if not stripped.startswith("{"):
        return content

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return content

    # Unwrap envelope
    doc = parsed.get("article", parsed)
    if not isinstance(doc, dict) or doc.get("type") != "doc":
        return content

    nodes = doc.get("content", [])
    md = _pm_nodes_to_markdown(nodes)
    # Clean up excessive blank lines
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n" if md.strip() else ""


# ---------------------------------------------------------------------------
# devrev/rt → HTML converter
# ---------------------------------------------------------------------------


def _pm_nodes_to_html(nodes: list[dict[str, Any]]) -> str:
    """Recursively convert ProseMirror nodes to HTML."""
    parts: list[str] = []
    for node in nodes:
        ntype = node.get("type", "")
        content: list[dict[str, Any]] = node.get("content", [])
        attrs: dict[str, Any] = node.get("attrs") or {}

        if ntype == "paragraph":
            parts.append(f"<p>{_pm_inline_to_html(content)}</p>")

        elif ntype == "heading":
            level = attrs.get("level", 1)
            parts.append(f"<h{level}>{_pm_inline_to_html(content)}</h{level}>")

        elif ntype == "codeBlock":
            lang = attrs.get("language") or ""
            code_text = _pm_inline_to_html(content)
            if lang:
                parts.append(f'<pre><code class="language-{lang}">{code_text}</code></pre>')
            else:
                parts.append(f"<pre><code>{code_text}</code></pre>")

        elif ntype == "blockquote":
            inner = _pm_nodes_to_html(content)
            parts.append(f"<blockquote>{inner}</blockquote>")

        elif ntype == "bulletList":
            items = _pm_nodes_to_html(content)
            parts.append(f"<ul>{items}</ul>")

        elif ntype == "orderedList":
            start = attrs.get("start", 1)
            start_attr = f' start="{start}"' if start and start != 1 else ""
            items = _pm_nodes_to_html(content)
            parts.append(f"<ol{start_attr}>{items}</ol>")

        elif ntype == "listItem":
            inner = _pm_nodes_to_html(content)
            parts.append(f"<li>{inner}</li>")

        elif ntype == "horizontalRule":
            parts.append("<hr>")

        elif ntype == "table":
            inner = _pm_nodes_to_html(content)
            parts.append(f"<table>{inner}</table>")

        elif ntype == "tableRow":
            inner = _pm_nodes_to_html(content)
            parts.append(f"<tr>{inner}</tr>")

        elif ntype in ("tableCell", "tableHeader"):
            tag = "th" if ntype == "tableHeader" else "td"
            inner = _pm_nodes_to_html(content)
            parts.append(f"<{tag}>{inner}</{tag}>")

        elif ntype == "image":
            src = html_module.escape(attrs.get("src", ""), quote=True)
            alt = html_module.escape(attrs.get("alt", ""), quote=True)
            parts.append(f'<img src="{src}" alt="{alt}">')

        elif ntype == "text":
            parts.append(_pm_text_node_to_html(node))

        else:
            if content:
                parts.append(_pm_nodes_to_html(content))

    return "".join(parts)


def _pm_inline_to_html(nodes: list[dict[str, Any]]) -> str:
    """Convert ProseMirror inline nodes to an HTML fragment."""
    parts: list[str] = []
    for node in nodes:
        ntype = node.get("type", "")
        if ntype == "text":
            parts.append(_pm_text_node_to_html(node))
        elif ntype == "hardBreak":
            parts.append("<br>")
        elif ntype == "image":
            attrs = node.get("attrs") or {}
            src = html_module.escape(attrs.get("src", ""), quote=True)
            alt = html_module.escape(attrs.get("alt", ""), quote=True)
            parts.append(f'<img src="{src}" alt="{alt}">')
        else:
            content = node.get("content", [])
            if content:
                parts.append(_pm_inline_to_html(content))
    return "".join(parts)


def _pm_text_node_to_html(node: dict[str, Any]) -> str:
    """Convert a ProseMirror text node (with marks) to HTML.

    Text content and attribute values are escaped to prevent XSS and
    malformed HTML output.
    """
    text = html_module.escape(node.get("text", ""))
    marks: list[dict[str, Any]] = node.get("marks", [])

    for mark in marks:
        mtype = mark.get("type", "")
        if mtype == "bold":
            text = f"<strong>{text}</strong>"
        elif mtype == "italic":
            text = f"<em>{text}</em>"
        elif mtype == "code":
            text = f"<code>{text}</code>"
        elif mtype == "strike":
            text = f"<s>{text}</s>"
        elif mtype == "underline":
            text = f"<u>{text}</u>"
        elif mtype == "link":
            href = html_module.escape(
                (mark.get("attrs") or {}).get("href", ""), quote=True
            )
            target = html_module.escape(
                (mark.get("attrs") or {}).get("target", "_blank"), quote=True
            )
            text = f'<a href="{href}" target="{target}">{text}</a>'
        elif mtype == "subscript":
            text = f"<sub>{text}</sub>"
        elif mtype == "superscript":
            text = f"<sup>{text}</sup>"
    return text


def devrev_rt_to_html(content: str) -> str:
    """Convert DevRev Rich Text (ProseMirror JSON) to HTML.

    Accepts either the full ``{"article": ..., "artifactIds": [...]}``
    envelope or just the inner ``{"type": "doc", "content": [...]}``
    document node.

    If *content* is not valid devrev/rt JSON, it is returned unchanged.

    Args:
        content: JSON string in devrev/rt format, or arbitrary text.

    Returns:
        HTML string.

    Example:
        >>> rt = '{"article": {"type": "doc", "content": [{"type": "paragraph", "attrs": {}, "content": [{"type": "text", "text": "Hello"}]}]}}'
        >>> devrev_rt_to_html(rt)
        '<p>Hello</p>'
    """
    stripped = content.strip()
    if not stripped.startswith("{"):
        return content

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return content

    doc = parsed.get("article", parsed)
    if not isinstance(doc, dict) or doc.get("type") != "doc":
        return content

    nodes = doc.get("content", [])
    return _pm_nodes_to_html(nodes)
