"""Tests for b-roll normalization honoring configured output profile."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "broll_generator.py"
SPEC = importlib.util.spec_from_file_location("broll_generator", MODULE_PATH)
broll_generator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(broll_generator)


def test_normalize_clip_uses_requested_dimensions_and_fps(monkeypatch) -> None:
    """ffmpeg command should use caller-provided width/height/fps."""
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class _Result:
            returncode = 0
        return _Result()

    monkeypatch.setattr(broll_generator.subprocess, "run", fake_run)
    broll_generator._normalize_clip(
        "in.mp4",
        "out.mp4",
        width=2560,
        height=1440,
        fps=30,
    )

    cmd = calls[0]
    assert "-vf" in cmd
    vf_value = cmd[cmd.index("-vf") + 1]
    assert "scale=2560:1440" in vf_value
    assert "pad=2560:1440" in vf_value
    assert "-r" in cmd and cmd[cmd.index("-r") + 1] == "30"
