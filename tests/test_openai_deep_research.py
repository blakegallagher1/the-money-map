"""Tests for the OpenAI deep research runner helpers."""

import sys

from scripts.openai_deep_research import (
    build_seed_prompt,
    extract_citations,
    parse_args,
    render_markdown_report,
    slugify,
)


def test_slugify_normalizes_text() -> None:
    """The slug should be filesystem-safe and lowercase."""
    assert slugify("Make This Repo A YouTube Machine!") == "make-this-repo-a-youtube-machine"


def test_build_seed_prompt_includes_goal_and_context() -> None:
    """The research brief should preserve the user goal and repo context."""
    prompt = build_seed_prompt("Automate the channel.", "FILE: README.md\n```text\nHello\n```")
    assert "Automate the channel." in prompt
    assert "FILE: README.md" in prompt
    assert "Top 5 Repo Changes" in prompt


def test_parse_args_accepts_response_id(monkeypatch) -> None:
    """Resume mode should accept an existing response ID from the CLI."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["openai_deep_research.py", "--response-id", "resp_123"],
    )
    args = parse_args()
    assert args.response_id == "resp_123"


def test_extract_citations_deduplicates_urls() -> None:
    """Duplicate URL annotations should collapse into a single citation entry."""
    citations = extract_citations(
        {
            "output": [
                {
                    "content": [
                        {
                            "annotations": [
                                {"url": "https://example.com/a", "title": "Example A"},
                                {"url": "https://example.com/a", "title": "Example A"},
                                {"url": "https://example.com/b", "title": "Example B"},
                            ]
                        }
                    ]
                }
            ]
        }
    )
    assert citations == [
        ("Example A", "https://example.com/a"),
        ("Example B", "https://example.com/b"),
    ]


def test_render_markdown_report_lists_sources() -> None:
    """The Markdown renderer should append a sources section when citations exist."""
    markdown = render_markdown_report(
        goal="Automate the channel.",
        prompt_text="Expanded prompt",
        response_payload={
            "output_text": "Final report body.",
            "output": [
                {
                    "content": [
                        {
                            "annotations": [
                                {"url": "https://example.com/a", "title": "Example A"},
                            ]
                        }
                    ]
                }
            ],
        },
        research_model="o3-deep-research",
        prompt_model="gpt-5.4",
        tool_type="web_search",
    )
    assert "## Report" in markdown
    assert "Final report body." in markdown
    assert "## Sources" in markdown
    assert "[Example A](https://example.com/a)" in markdown
