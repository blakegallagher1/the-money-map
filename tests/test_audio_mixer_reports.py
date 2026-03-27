"""Tests for audio compliance report helpers."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audio_mixer.py"
SPEC = importlib.util.spec_from_file_location("audio_mixer", MODULE_PATH)
audio_mixer = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(audio_mixer)


def test_build_music_provenance_voice_only() -> None:
    """Voice-only runs should still produce required provenance fields."""
    data = audio_mixer._build_music_provenance(None, "/tmp/voiceover_normalized.wav")
    assert data["source"] == "none"
    assert data["license_id"] == "voice_only"
    assert data["file_path"]


def test_extract_loudnorm_json_handles_invalid_payload() -> None:
    """Malformed ffmpeg output should fail closed to None."""
    assert audio_mixer._extract_loudnorm_json("not-json") is None
