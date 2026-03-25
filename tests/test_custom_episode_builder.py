"""Tests for the custom narrated episode builder."""

from pathlib import Path

import pytest

from scripts.custom_episode_builder import build_full_script, color_for, load_episode_spec


def test_load_episode_spec_requires_sections(tmp_path: Path) -> None:
    """The loader should reject specs without sections."""
    spec_path = tmp_path / "episode.json"
    spec_path.write_text('{"slug":"demo","title":"Demo","sections":[]}')
    with pytest.raises(ValueError):
        load_episode_spec(spec_path)


def test_build_full_script_joins_section_narration() -> None:
    """The builder should preserve section order when joining narration."""
    script = build_full_script(
        {
            "sections": [
                {"narration": "First section."},
                {"narration": "Second section."},
            ]
        }
    )
    assert script == "First section.\n\nSecond section."


def test_color_for_falls_back_to_default() -> None:
    """Unknown accent keys should use the repo default accent."""
    assert color_for({"accent": "not_real"}) == "#00D4AA"
