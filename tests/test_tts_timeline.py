"""Tests for section-timed voiceover generation."""

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "tts_generator.py"
SPEC = importlib.util.spec_from_file_location("tts_generator", MODULE_PATH)
tts_generator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(tts_generator)


def test_generate_voiceover_timeline_writes_manifest(monkeypatch, tmp_path: Path) -> None:
    """Timeline generation should emit ordered section timings and output paths."""
    def fake_synthesize(script_text: str, output_path: str, voice: str | None, instructions: str) -> None:
        Path(output_path).write_bytes(script_text.encode("utf-8"))

    def fake_duration(path: str) -> float:
        if path.endswith("intro.wav"):
            return 1.5
        if path.endswith("close.wav"):
            return 2.0
        return 3.5

    def fake_concat(file_paths: list[str], output_path: str) -> None:
        Path(output_path).write_bytes(b"joined-audio")

    monkeypatch.setattr(tts_generator, "_synthesize_script_text", fake_synthesize)
    monkeypatch.setattr(tts_generator, "_audio_duration_seconds", fake_duration)
    monkeypatch.setattr(tts_generator, "_concatenate_audio_files", fake_concat)

    output_path = tmp_path / "voiceover.wav"
    timeline_path = tmp_path / "voiceover_timeline.json"
    result = tts_generator.generate_voiceover_timeline(
        [
            {"id": "intro", "text": "First section."},
            {"id": "close", "text": "Second section."},
        ],
        output_path=str(output_path),
        timeline_path=str(timeline_path),
    )

    assert Path(result["output_path"]).exists()
    payload = json.loads(timeline_path.read_text())
    assert payload["section_count"] == 2
    assert payload["sections"][0]["id"] == "intro"
    assert payload["sections"][0]["start_sec"] == 0.0
    assert payload["sections"][1]["start_sec"] == 1.5
    assert payload["duration_sec"] == 3.5
