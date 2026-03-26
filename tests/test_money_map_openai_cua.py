"""Tests for the repo-local Money Map OpenAI CUA helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    """Import the helper script from the repo-local skill path."""
    module_path = (
        Path(__file__).resolve().parent.parent
        / ".codex"
        / "skills"
        / "money-map-openai-cua"
        / "scripts"
        / "run_cua_task.py"
    )
    spec = importlib.util.spec_from_file_location("money_map_openai_cua", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_resolve_allow_domains_includes_start_host() -> None:
    """The helper should derive the start URL host into the allowlist."""
    module = load_module()
    allow_domains = module.resolve_allow_domains("https://studio.youtube.com/channel", ["accounts.google.com"])
    assert "studio.youtube.com" in allow_domains
    assert "accounts.google.com" in allow_domains


def test_is_allowed_url_accepts_subdomains_only() -> None:
    """Allowlist checks should permit subdomains and reject unrelated hosts."""
    module = load_module()
    allow_domains = ("youtube.com",)
    assert module.is_allowed_url("https://studio.youtube.com", allow_domains)
    assert not module.is_allowed_url("https://example.com", allow_domains)


def test_build_request_uses_ga_tool_shape() -> None:
    """The request builder should use the current GA computer tool shape."""
    module = load_module()
    config = module.RunnerConfig(
        task="Validate a page",
        model="gpt-5.4",
        start_url="https://studio.youtube.com",
        allow_domains=("studio.youtube.com",),
        display_width=1440,
        display_height=900,
        max_steps=5,
        headless=True,
        artifact_dir=Path("/tmp/cua"),
    )
    request = module.build_request(config, module.build_user_prompt(config), previous_response_id="resp_123")
    assert request["tools"][0]["type"] == "computer"
    assert request["tools"][0]["environment"] == "browser"
    assert request["previous_response_id"] == "resp_123"


def test_extract_actions_supports_ga_and_legacy_shapes() -> None:
    """The parser should normalize both actions[] and legacy action fields."""
    module = load_module()
    ga_call = {"type": "computer_call", "actions": [{"type": "click", "x": 1, "y": 2}]}
    legacy_call = {"type": "computer_call", "action": {"type": "wait"}}
    assert module.extract_actions(ga_call) == [{"type": "click", "x": 1, "y": 2}]
    assert module.extract_actions(legacy_call) == [{"type": "wait"}]


def test_build_computer_call_output_uses_expected_shape() -> None:
    """The follow-up screenshot item should match the Responses API item shape."""
    module = load_module()
    item = module.build_computer_call_output("call_123", "data:image/png;base64,abc")
    assert item["type"] == "computer_call_output"
    assert item["output"]["type"] == "computer_screenshot"
    assert item["output"]["image_url"].startswith("data:image/png;base64,")


def test_collect_output_text_joins_message_parts() -> None:
    """Final assistant text should be joined in output order."""
    module = load_module()
    payload = {
        "output": [
            {
                "type": "message",
                "content": [
                    {"type": "output_text", "text": "Draft uploaded."},
                    {"type": "output_text", "text": "Stopped before publish."},
                ],
            }
        ]
    }
    assert module.collect_output_text(payload) == "Draft uploaded.\n\nStopped before publish."
