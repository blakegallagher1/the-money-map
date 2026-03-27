"""Tests for publish_from_script command helpers."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "publish_from_script.py"
SPEC = importlib.util.spec_from_file_location("publish_from_script", MODULE_PATH)
publish_from_script = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(publish_from_script)


def test_build_publish_command_defaults() -> None:
    """Publish command should not include no-upload flag."""
    cmd = publish_from_script.build_orchestrator_publish_command(
        python_executable="python3",
        quality_tier="1440",
        no_broll=False,
        no_music=False,
    )
    assert cmd[:2] == ["python3", str(publish_from_script.REPO_ROOT / "scripts" / "orchestrator.py")]
    assert "--step" in cmd and "voiceover" in cmd
    assert "--quality-tier" in cmd and "1440" in cmd
    assert "--no-upload" not in cmd


def test_build_publish_command_optional_flags() -> None:
    """Optional no-broll/no-music flags should be appended when requested."""
    cmd = publish_from_script.build_orchestrator_publish_command(
        python_executable="python3",
        quality_tier="2160",
        no_broll=True,
        no_music=True,
        min_words=350,
    )
    assert "--no-broll" in cmd
    assert "--no-music" in cmd
    assert "2160" in cmd
    assert "--min-words" in cmd and "350" in cmd


def test_load_last_run_url_returns_none_when_missing(tmp_path: Path, monkeypatch) -> None:
    """Missing last_run artifact should return no URL."""
    monkeypatch.setattr(publish_from_script, "LAST_RUN_PATH", tmp_path / "missing.json")
    assert publish_from_script._load_last_run_url() is None
