"""Unit tests for the HTML/Markdown → devrev/rt content converter.

Tests are structured in three tiers:
1. **Structural validation** – every ProseMirror node type produced by the
   converter has the correct shape (type, attrs, content, marks).
2. **Golden fixture comparison** – converter output is compared against
   real devrev/rt JSON downloaded from UI-created articles (ART-2817,
   ART-2803) to ensure structural compatibility.
3. **Edge cases** – empty input, passthrough of existing devrev/rt JSON,
   plain text, markdown detection heuristic.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from devrev.utils.content_converter import html_to_devrev_rt

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(content: str) -> dict[str, Any]:
    """Shortcut: convert content and parse the JSON envelope."""
    return json.loads(html_to_devrev_rt(content))


def _doc_nodes(content: str) -> list[dict[str, Any]]:
    """Return the top-level content nodes from the converted document."""
    return _parse(content)["article"]["content"]


# ---------------------------------------------------------------------------
# 1. Envelope structure
# ---------------------------------------------------------------------------


class TestEnvelopeStructure:
    """The converter must always produce a valid devrev/rt envelope."""

    def test_envelope_has_article_and_artifact_ids(self) -> None:
        result = _parse("<p>hello</p>")
        assert "article" in result
        assert "artifactIds" in result
        assert isinstance(result["artifactIds"], list)

    def test_article_is_doc_type(self) -> None:
        result = _parse("<p>hello</p>")
        assert result["article"]["type"] == "doc"
        assert isinstance(result["article"]["content"], list)

    def test_empty_input_produces_empty_paragraph(self) -> None:
        nodes = _doc_nodes("")
        assert len(nodes) == 1
        assert nodes[0]["type"] == "paragraph"

    def test_passthrough_existing_devrev_rt(self) -> None:
        existing = json.dumps({"article": {"type": "doc", "content": []}, "artifactIds": []})
        assert html_to_devrev_rt(existing) == existing


# ---------------------------------------------------------------------------
# 2. Paragraph and text nodes
# ---------------------------------------------------------------------------


class TestParagraphAndText:
    """Paragraphs and inline text nodes."""

    def test_simple_paragraph(self) -> None:
        nodes = _doc_nodes("<p>Hello world</p>")
        assert len(nodes) == 1
        p = nodes[0]
        assert p["type"] == "paragraph"
        assert p["attrs"] == {"textAlign": None}
        assert p["content"][0] == {"type": "text", "text": "Hello world"}

    def test_plain_text_wrapped_in_paragraph(self) -> None:
        nodes = _doc_nodes("Just some text")
        assert nodes[0]["type"] == "paragraph"
        assert nodes[0]["content"][0]["text"] == "Just some text"

    def test_multiple_paragraphs(self) -> None:
        nodes = _doc_nodes("<p>First</p><p>Second</p>")
        assert len(nodes) == 2
        assert all(n["type"] == "paragraph" for n in nodes)


# ---------------------------------------------------------------------------
# 3. Headings
# ---------------------------------------------------------------------------


class TestHeadings:
    """Heading nodes with correct level attrs."""

    @pytest.mark.parametrize("level", [1, 2, 3, 4, 5, 6])
    def test_heading_levels(self, level: int) -> None:
        nodes = _doc_nodes(f"<h{level}>Title</h{level}>")
        h = nodes[0]
        assert h["type"] == "heading"
        assert h["attrs"]["level"] == level


# ---------------------------------------------------------------------------
# 4. Inline marks (bold, italic, code, links, etc.)
# ---------------------------------------------------------------------------


class TestInlineMarks:
    """Inline formatting marks."""

    def test_bold(self) -> None:
        nodes = _doc_nodes("<p><strong>bold</strong></p>")
        text = nodes[0]["content"][0]
        assert text["text"] == "bold"
        assert text["marks"] == [{"type": "bold"}]

    def test_italic(self) -> None:
        nodes = _doc_nodes("<p><em>italic</em></p>")
        text = nodes[0]["content"][0]
        assert text["marks"] == [{"type": "italic"}]

    def test_inline_code(self) -> None:
        nodes = _doc_nodes("<p><code>x = 1</code></p>")
        text = nodes[0]["content"][0]
        assert text["marks"] == [{"type": "code"}]

    def test_link(self) -> None:
        nodes = _doc_nodes('<p><a href="https://example.com">click</a></p>')
        text = nodes[0]["content"][0]
        assert text["text"] == "click"
        link_mark = text["marks"][0]
        assert link_mark["type"] == "link"
        assert link_mark["attrs"]["href"] == "https://example.com"

    def test_nested_marks(self) -> None:
        """Bold + italic nesting."""
        nodes = _doc_nodes("<p><strong><em>both</em></strong></p>")
        text = nodes[0]["content"][0]
        mark_types = {m["type"] for m in text["marks"]}
        assert "bold" in mark_types
        assert "italic" in mark_types

    def test_mixed_inline_content(self) -> None:
        """Paragraph with plain text, bold, and code."""
        nodes = _doc_nodes("<p>Hello <strong>bold</strong> and <code>code</code></p>")
        content = nodes[0]["content"]
        assert len(content) >= 4  # "Hello ", "bold", " and ", "code"
        assert content[0]["type"] == "text"
        assert content[0].get("marks") is None or content[0].get("marks") == []


# ---------------------------------------------------------------------------
# 5. Code blocks
# ---------------------------------------------------------------------------


class TestCodeBlocks:
    """Code block nodes with language detection."""

    def test_code_block_from_html(self) -> None:
        html = '<pre><code class="language-python">def f(): pass</code></pre>'
        nodes = _doc_nodes(html)
        cb = nodes[0]
        assert cb["type"] == "codeBlock"
        assert cb["attrs"]["language"] == "python"
        assert cb["content"][0]["text"] == "def f(): pass"

    def test_code_block_no_language(self) -> None:
        nodes = _doc_nodes("<pre><code>plain code</code></pre>")
        cb = nodes[0]
        assert cb["type"] == "codeBlock"
        assert cb["attrs"]["language"] is None

    def test_code_block_from_markdown(self) -> None:
        md = "```javascript\nconsole.log('hi')\n```"
        nodes = _doc_nodes(md)
        cb = nodes[0]
        assert cb["type"] == "codeBlock"
        assert cb["attrs"]["language"] == "javascript"
        assert "console.log" in cb["content"][0]["text"]

    def test_code_block_pre_without_code_tag(self) -> None:
        nodes = _doc_nodes("<pre>raw preformatted</pre>")
        cb = nodes[0]
        assert cb["type"] == "codeBlock"
        assert "raw preformatted" in cb["content"][0]["text"]


# ---------------------------------------------------------------------------
# 6. Images
# ---------------------------------------------------------------------------


class TestImages:
    """Image nodes."""

    def test_image_from_html(self) -> None:
        html = '<img src="https://example.com/img.png" alt="photo" title="My Photo">'
        nodes = _doc_nodes(html)
        # Image may be wrapped in a paragraph
        img = nodes[0]
        if img["type"] == "paragraph":
            img = img["content"][0]
        assert img["type"] == "image"
        assert img["attrs"]["src"] == "https://example.com/img.png"
        assert img["attrs"]["alt"] == "photo"
        assert img["attrs"]["title"] == "My Photo"

    def test_image_from_markdown(self) -> None:
        md = "![alt text](https://example.com/pic.jpg)"
        nodes = _doc_nodes(md)
        img = nodes[0]
        if img["type"] == "paragraph":
            img = img["content"][0]
        assert img["type"] == "image"
        assert img["attrs"]["src"] == "https://example.com/pic.jpg"
        assert img["attrs"]["alt"] == "alt text"


# ---------------------------------------------------------------------------
# 7. Tables
# ---------------------------------------------------------------------------


class TestTables:
    """Table nodes matching DevRev UI structure."""

    def test_simple_table_structure(self) -> None:
        html = """
        <table>
          <tr><th>A</th><th>B</th></tr>
          <tr><td>1</td><td>2</td></tr>
        </table>
        """
        nodes = _doc_nodes(html)
        table = nodes[0]
        assert table["type"] == "table"
        rows = table["content"]
        assert len(rows) == 2
        assert rows[0]["type"] == "tableRow"

    def test_table_cell_attrs_match_ui(self) -> None:
        """Cell attrs must match UI format: colspan, rowspan, colwidth."""
        html = "<table><tr><td>cell</td></tr></table>"
        nodes = _doc_nodes(html)
        cell = nodes[0]["content"][0]["content"][0]
        assert cell["type"] == "tableCell"
        assert cell["attrs"] == {"colspan": 1, "rowspan": 1, "colwidth": None}

    def test_table_header_attrs(self) -> None:
        html = "<table><tr><th>header</th></tr></table>"
        nodes = _doc_nodes(html)
        cell = nodes[0]["content"][0]["content"][0]
        assert cell["type"] == "tableHeader"
        assert cell["attrs"] == {"colspan": 1, "rowspan": 1, "colwidth": None}

    def test_table_cells_contain_paragraphs(self) -> None:
        """DevRev UI wraps cell text in paragraphs — our converter must too."""
        html = "<table><tr><td>text</td></tr></table>"
        nodes = _doc_nodes(html)
        cell = nodes[0]["content"][0]["content"][0]
        # Cell content must be block-level (paragraph)
        para = cell["content"][0]
        assert para["type"] == "paragraph"
        assert para["content"][0]["text"] == "text"

    def test_empty_table_cell_has_empty_paragraph(self) -> None:
        """Empty cells must still have a paragraph child (matches UI)."""
        html = "<table><tr><td></td></tr></table>"
        nodes = _doc_nodes(html)
        cell = nodes[0]["content"][0]["content"][0]
        assert cell["content"][0]["type"] == "paragraph"

    def test_table_from_markdown(self) -> None:
        md = "| X | Y |\n|---|---|\n| a | b |"
        nodes = _doc_nodes(md)
        table = nodes[0]
        assert table["type"] == "table"
        # Should have header row + data row
        assert len(table["content"]) >= 2


# ---------------------------------------------------------------------------
# 8. Lists and blockquotes
# ---------------------------------------------------------------------------


class TestListsAndBlockquotes:
    """List and blockquote nodes."""

    def test_unordered_list(self) -> None:
        html = "<ul><li>A</li><li>B</li></ul>"
        nodes = _doc_nodes(html)
        ul = nodes[0]
        assert ul["type"] == "bulletList"
        assert len(ul["content"]) == 2
        assert ul["content"][0]["type"] == "listItem"

    def test_ordered_list(self) -> None:
        html = "<ol><li>First</li><li>Second</li></ol>"
        nodes = _doc_nodes(html)
        ol = nodes[0]
        assert ol["type"] == "orderedList"

    def test_list_items_contain_paragraphs(self) -> None:
        """List items must wrap text in paragraphs (ProseMirror requirement)."""
        html = "<ul><li>item text</li></ul>"
        nodes = _doc_nodes(html)
        li = nodes[0]["content"][0]
        assert li["type"] == "listItem"
        para = li["content"][0]
        assert para["type"] == "paragraph"
        assert para["content"][0]["text"] == "item text"

    def test_blockquote(self) -> None:
        html = "<blockquote><p>A wise quote</p></blockquote>"
        nodes = _doc_nodes(html)
        bq = nodes[0]
        assert bq["type"] == "blockquote"
        assert bq["content"][0]["type"] == "paragraph"

    def test_blockquote_from_markdown(self) -> None:
        # Blockquote alone isn't detected as markdown; combine with a heading
        md = "# Title\n\n> This is a quote"
        nodes = _doc_nodes(md)
        bq = next(n for n in nodes if n["type"] == "blockquote")
        assert bq["type"] == "blockquote"


# ---------------------------------------------------------------------------
# 9. Markdown detection and conversion
# ---------------------------------------------------------------------------


class TestMarkdownConversion:
    """Markdown input is detected and converted correctly."""

    def test_markdown_heading(self) -> None:
        nodes = _doc_nodes("# Main Title")
        assert nodes[0]["type"] == "heading"
        assert nodes[0]["attrs"]["level"] == 1

    def test_markdown_bold_italic(self) -> None:
        nodes = _doc_nodes("**bold** and *italic*")
        content = nodes[0]["content"]
        bold_node = next(n for n in content if n.get("marks") and n["marks"][0]["type"] == "bold")
        assert bold_node["text"] == "bold"

    def test_markdown_link(self) -> None:
        nodes = _doc_nodes("[click](https://example.com)")
        content = nodes[0]["content"]
        link_node = next(n for n in content if n.get("marks") and n["marks"][0]["type"] == "link")
        assert link_node["text"] == "click"
        assert link_node["marks"][0]["attrs"]["href"] == "https://example.com"

    def test_markdown_unordered_list(self) -> None:
        md = "- Item A\n- Item B\n- Item C"
        nodes = _doc_nodes(md)
        assert nodes[0]["type"] == "bulletList"
        assert len(nodes[0]["content"]) == 3

    def test_markdown_ordered_list(self) -> None:
        md = "1. First\n2. Second"
        nodes = _doc_nodes(md)
        assert nodes[0]["type"] == "orderedList"

    def test_html_not_detected_as_markdown(self) -> None:
        """HTML starting with < should not be treated as markdown."""
        html = "<h1>Title</h1><p>Body</p>"
        nodes = _doc_nodes(html)
        assert nodes[0]["type"] == "heading"


# ---------------------------------------------------------------------------
# 10. Golden fixture comparison — match UI-created article structure
# ---------------------------------------------------------------------------


# Golden reference: ART-2817 has heading + table + codeBlock
# We reproduce the same content as HTML and verify structural equivalence.

_ART_2817_GOLDEN: dict[str, Any] = {
    "article": {
        "type": "doc",
        "content": [
            {
                "type": "heading",
                "attrs": {"textAlign": None, "level": 1},
                "content": [{"type": "text", "text": "Rich Text"}],
            },
            # UI adds an empty paragraph between heading and table
            {"type": "paragraph", "attrs": {"textAlign": None}},
            {
                "type": "table",
                "content": [
                    {
                        "type": "tableRow",
                        "content": [
                            {
                                "type": "tableCell",
                                "attrs": {"colspan": 1, "rowspan": 1, "colwidth": None},
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "attrs": {"textAlign": None},
                                        "content": [{"type": "text", "text": "df"}],
                                    }
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                "type": "codeBlock",
                "attrs": {"language": None},
                "content": [{"type": "text", "text": "fsdfsdfd"}],
            },
        ],
    },
    "artifactIds": [],
}


def _assert_node_shape(actual: dict[str, Any], expected: dict[str, Any], path: str = "") -> None:
    """Recursively assert that *actual* has the same structural shape as *expected*.

    Checks type, attrs keys, and content structure — but allows different
    text values and additional sibling nodes.
    """
    assert actual["type"] == expected["type"], f"{path}: type mismatch"

    if "attrs" in expected:
        assert "attrs" in actual, f"{path}: missing attrs"
        for key in expected["attrs"]:
            assert key in actual["attrs"], f"{path}: missing attr key '{key}'"

    if "content" in expected:
        assert "content" in actual, f"{path}: missing content"
        # Check that each expected child has a matching child in actual
        for i, exp_child in enumerate(expected["content"]):
            child_path = f"{path}.content[{i}]"
            assert i < len(actual["content"]), f"{child_path}: missing child"
            _assert_node_shape(actual["content"][i], exp_child, child_path)


class TestGoldenFixtures:
    """Compare converter output against real UI-created article structures."""

    def test_heading_matches_ui_structure(self) -> None:
        """Our heading node must have same shape as UI heading."""
        nodes = _doc_nodes("<h1>Rich Text</h1>")
        ui_heading = _ART_2817_GOLDEN["article"]["content"][0]
        _assert_node_shape(nodes[0], ui_heading, "heading")

    def test_table_cell_matches_ui_structure(self) -> None:
        """Table cell must have same attrs and paragraph wrapping as UI."""
        html = "<table><tr><td>df</td></tr></table>"
        nodes = _doc_nodes(html)
        cell = nodes[0]["content"][0]["content"][0]
        ui_cell = _ART_2817_GOLDEN["article"]["content"][2]["content"][0]["content"][0]
        _assert_node_shape(cell, ui_cell, "tableCell")

    def test_code_block_matches_ui_structure(self) -> None:
        """Code block must have same attrs as UI."""
        nodes = _doc_nodes("<pre><code>fsdfsdfd</code></pre>")
        ui_cb = _ART_2817_GOLDEN["article"]["content"][3]
        _assert_node_shape(nodes[0], ui_cb, "codeBlock")

    def test_full_document_heading_table_code(self) -> None:
        """Full document with heading + table + code block matches UI shape."""
        html = """
        <h1>Rich Text</h1>
        <table>
          <tr><td>df</td><td>fdf</td><td>fdfd</td></tr>
          <tr><td></td><td></td><td></td></tr>
          <tr><td></td><td></td><td>fd</td></tr>
        </table>
        <pre><code>fsdfsdfd</code></pre>
        """
        result = _parse(html)
        doc = result["article"]
        assert doc["type"] == "doc"

        # Find the key node types
        types = [n["type"] for n in doc["content"]]
        assert "heading" in types
        assert "table" in types
        assert "codeBlock" in types

        # Verify table structure depth
        table = next(n for n in doc["content"] if n["type"] == "table")
        assert len(table["content"]) == 3  # 3 rows
        first_row = table["content"][0]
        assert len(first_row["content"]) == 3  # 3 cells
        # Each cell has paragraph content
        for cell in first_row["content"]:
            assert cell["content"][0]["type"] == "paragraph"
