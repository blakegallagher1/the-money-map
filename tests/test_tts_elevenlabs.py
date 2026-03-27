"""Tests for ElevenLabs TTS REST integration."""

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "tts_generator.py"
SPEC = importlib.util.spec_from_file_location("tts_generator", MODULE_PATH)
tts = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(tts)


def test_elevenlabs_synthesize_chunk_posts_expected_payload(monkeypatch) -> None:
    """Verify Create speech request matches ElevenLabs API shape."""
    captured: dict = {}

    def fake_post(url, params=None, headers=None, data=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["data"] = data
        captured["timeout"] = timeout

        class R:
            status_code = 200
            text = ""
            content = b"\x00\x01"

        return R()

    monkeypatch.setattr(tts.requests, "post", fake_post)
    monkeypatch.setattr(tts, "ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setattr(tts, "ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    monkeypatch.setattr(tts, "ELEVENLABS_OUTPUT_FORMAT", "wav_44100")
    monkeypatch.setattr(tts, "ELEVENLABS_API_BASE", "https://api.elevenlabs.io")
    monkeypatch.setattr(tts, "ELEVENLABS_STABILITY", 0.5)
    monkeypatch.setattr(tts, "ELEVENLABS_SIMILARITY", 0.75)
    monkeypatch.setattr(tts, "ELEVENLABS_STYLE", 0.0)
    monkeypatch.setattr(tts, "ELEVENLABS_SPEED", 1.0)
    monkeypatch.setattr(tts, "ELEVENLABS_APPLY_TEXT_NORMALIZATION", None)
    monkeypatch.setattr(tts, "ELEVENLABS_LANGUAGE_CODE", "")

    out = tts._elevenlabs_synthesize_chunk(
        "voiceId123",
        "Hello world.",
        previous_text="Earlier context.",
        next_text="Later context.",
    )
    assert out == b"\x00\x01"
    assert captured["url"].endswith("/v1/text-to-speech/voiceId123")
    assert captured["params"] == {"output_format": "wav_44100"}
    assert captured["headers"]["xi-api-key"] == "test-key"
    assert captured["headers"]["Content-Type"] == "application/json"
    payload = json.loads(captured["data"])
    assert payload["text"] == "Hello world."
    assert payload["model_id"] == "eleven_multilingual_v2"
    assert payload["voice_settings"]["stability"] == 0.5
    assert "previous_text" in payload
    assert "next_text" in payload
    assert "apply_text_normalization" not in payload
    assert "language_code" not in payload


def test_elevenlabs_optional_normalization_and_language(monkeypatch) -> None:
    captured: dict = {}

    def fake_post(url, params=None, headers=None, data=None, timeout=None):
        captured["data"] = data

        class R:
            status_code = 200
            content = b"x"

        return R()

    monkeypatch.setattr(tts.requests, "post", fake_post)
    monkeypatch.setattr(tts, "ELEVENLABS_API_KEY", "k")
    monkeypatch.setattr(tts, "ELEVENLABS_MODEL_ID", "m")
    monkeypatch.setattr(tts, "ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")
    monkeypatch.setattr(tts, "ELEVENLABS_API_BASE", "https://api.elevenlabs.io")
    for name, val in (
        ("ELEVENLABS_STABILITY", 0.5),
        ("ELEVENLABS_SIMILARITY", 0.75),
        ("ELEVENLABS_STYLE", 0.0),
        ("ELEVENLABS_SPEED", 1.0),
    ):
        monkeypatch.setattr(tts, name, val)
    monkeypatch.setattr(tts, "ELEVENLABS_APPLY_TEXT_NORMALIZATION", "off")
    monkeypatch.setattr(tts, "ELEVENLABS_LANGUAGE_CODE", "en")

    tts._elevenlabs_synthesize_chunk("vid", "Hi", None, None)
    payload = json.loads(captured["data"])
    assert payload["apply_text_normalization"] == "off"
    assert payload["language_code"] == "en"
