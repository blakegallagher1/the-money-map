"""Tests for YouTube ingest encoding profile selection."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_assembly.py"
SPEC = importlib.util.spec_from_file_location("final_assembly", MODULE_PATH)
final_assembly = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(final_assembly)


def test_youtube_bitrate_selection_for_4k_standard_and_high_fps() -> None:
    """4K should use top YouTube-recommended bitrate per fps band."""
    assert final_assembly._youtube_target_video_bitrate(2160, 30.0) == "45M"
    assert final_assembly._youtube_target_video_bitrate(2160, 60.0) == "68M"


def test_youtube_encode_args_enforce_h264_aac_48k_stereo() -> None:
    """Export args should enforce YouTube ingest-friendly codec/audio settings."""
    args = final_assembly._youtube_encode_args(2160, 30.0)
    assert "-c:v" in args and "libx264" in args
    assert "-profile:v" in args and "high" in args
    assert "-pix_fmt" in args and "yuv420p" in args
    assert "-b:v" in args and "45M" in args
    assert "-c:a" in args and "aac" in args
    assert "-ac" in args and "2" in args
    assert "-ar" in args and "48000" in args
    assert "-b:a" in args and "384k" in args
