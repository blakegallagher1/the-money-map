"""Tests for build_from_script command helpers."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_from_script.py"
SPEC = importlib.util.spec_from_file_location("build_from_script", MODULE_PATH)
build_from_script = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(build_from_script)


def test_build_orchestrator_command_defaults() -> None:
    """Command should target voiceover step with quality tier and no-upload."""
    cmd = build_from_script.build_orchestrator_command(
        python_executable="python3",
        quality_tier="1440",
        no_broll=False,
        no_music=False,
    )
    assert cmd[:2] == ["python3", str(build_from_script.REPO_ROOT / "scripts" / "orchestrator.py")]
    assert "--step" in cmd and "voiceover" in cmd
    assert "--quality-tier" in cmd and "1440" in cmd
    assert "--no-upload" in cmd
    assert "--no-broll" not in cmd
    assert "--no-music" not in cmd


def test_build_orchestrator_command_flags() -> None:
    """Optional flags should be present when explicitly requested."""
    cmd = build_from_script.build_orchestrator_command(
        python_executable="python3",
        quality_tier="2160",
        no_broll=True,
        no_music=True,
    )
    assert "--no-broll" in cmd
    assert "--no-music" in cmd
    assert "2160" in cmd


def test_derive_thumbnail_path() -> None:
    """Thumbnail path should derive from output filename stem."""
    output = Path("/tmp/example/my_episode.mp4")
    thumb = build_from_script.derive_thumbnail_path(output)
    assert str(thumb) == "/tmp/example/my_episode_thumbnail.png"
