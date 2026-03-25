"""Tests for the custom narrated episode builder."""

from pathlib import Path

import pytest

from scripts.custom_episode_builder import build_full_script, color_for, load_episode_spec
from scripts.episode_image_visuals import build_image_command
from scripts.episode_visual_assets import section_visual_plan, still_video_filter
from scripts.sora_episode_visuals import build_sora_command


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


def test_section_visual_plan_uses_broll_for_long_sections() -> None:
    """Long sections with available clips should reserve a b-roll window."""
    intro, broll = section_visual_plan(42.0, 2)
    assert intro < 42.0
    assert broll > 0.0


def test_still_video_filter_adds_subtle_motion() -> None:
    """Still-image sections should use an animated crop instead of a static frame."""
    filter_graph = still_video_filter(12.5)
    assert "crop=1920:1080" in filter_graph
    assert "min(t/12.500,1)" in filter_graph


def test_build_sora_command_includes_prompt_fields(tmp_path: Path) -> None:
    """The Sora command should pass through the structured prompt fields."""
    video_path = tmp_path / "shot.mp4"
    json_path = tmp_path / "shot.json"
    command = build_sora_command(
        {
            "id": "demo",
            "prompt": "quiet office at night",
            "scene": "empty office",
            "constraints": "no text",
            "seconds": "8",
        },
        model="sora-2-pro",
        size="1920x1080",
        timeout=1800,
        poll_interval=10,
        video_path=video_path,
        json_path=json_path,
        force=False,
        dry_run=False,
    )
    assert "--scene" in command
    assert "empty office" in command
    assert "--constraints" in command
    assert str(video_path) in command


def test_build_image_command_includes_prompt_fields(tmp_path: Path) -> None:
    """The image command should pass through the structured prompt fields."""
    out_path = tmp_path / "image.png"
    command = build_image_command(
        {
            "id": "desk",
            "prompt": "cinematic underwriting desk",
            "scene": "night office",
            "constraints": "no text",
        },
        model="gpt-image-1.5",
        size="1536x1024",
        quality="high",
        output_format="png",
        out_path=out_path,
        force=False,
        dry_run=False,
    )
    assert "--scene" in command
    assert "night office" in command
    assert "--constraints" in command
    assert str(out_path) in command
