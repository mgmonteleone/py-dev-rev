"""HTML / Markdown to DevRev Rich Text (ProseMirror JSON) converter.

Converts HTML or Markdown content to the ``devrev/rt`` format used by
DevRev's UI for inline article rendering.  Without this conversion,
content appears as an attachment rather than rendered inline.

The ``devrev/rt`` format is a ProseMirror / Tiptap JSON document
structure wrapped in an ``{"article": ..., "artifactIds": []}`` envelope.

Supported input formats
-----------------------
* **HTML** – parsed with *BeautifulSoup 4* for robust DOM walking.
* **Markdown** – first converted to HTML via the *markdown* library
  (with ``tables``, ``fenced_code``, and ``codehilite`` extensions),
  then parsed identically.
* **Plain text** – wrapped in a single ``<p>`` before conversion.
* **Existing devrev/rt JSON** – detected and returned unchanged.
"""

from __future__ import annotations

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
