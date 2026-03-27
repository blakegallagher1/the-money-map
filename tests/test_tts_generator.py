"""Tests for TTS model/voice fallback selection."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "tts_generator.py"
SPEC = importlib.util.spec_from_file_location("tts_generator", MODULE_PATH)
tts_generator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(tts_generator)


class _FakeResponse:
    def __init__(self) -> None:
        self.saved_path = None

    def stream_to_file(self, path: str) -> None:
        self.saved_path = path


class _FakeSpeechApi:
    def __init__(self, allowed_pairs: set[tuple[str, str]]) -> None:
        self.allowed_pairs = allowed_pairs
        self.calls: list[tuple[str, str]] = []

    def create(self, *, model: str, voice: str, input: str, instructions: str, response_format: str):
        self.calls.append((model, voice))
        assert input
        assert instructions
        assert response_format == "wav"
        if (model, voice) in self.allowed_pairs:
            return _FakeResponse()
        raise RuntimeError("simulated unsupported model/voice")


class _FakeClient:
    def __init__(self, allowed_pairs: set[tuple[str, str]]) -> None:
        self.audio = type("Audio", (), {"speech": _FakeSpeechApi(allowed_pairs)})()


def test_voice_candidates_prefer_requested_then_fallback() -> None:
    """Requested voice should be first, then configured fallbacks."""
    original_fallback = tts_generator.TTS_FALLBACK_VOICES
    tts_generator.TTS_FALLBACK_VOICES = ["cedar", "marin"]
    try:
        assert tts_generator._voice_candidates("marin") == ["marin", "cedar"]
    finally:
        tts_generator.TTS_FALLBACK_VOICES = original_fallback


def test_create_speech_falls_back_to_secondary_voice() -> None:
    """If primary voice fails, fallback voice should be used."""
    original_model = tts_generator.TTS_MODEL
    original_fallback_model = tts_generator.TTS_FALLBACK_MODEL
    original_fallback_voices = tts_generator.TTS_FALLBACK_VOICES
    tts_generator.TTS_MODEL = "primary-model"
    tts_generator.TTS_FALLBACK_MODEL = "fallback-model"
    tts_generator.TTS_FALLBACK_VOICES = ["cedar"]
    try:
        client = _FakeClient({("primary-model", "cedar")})
        _, model, voice = tts_generator._create_speech_with_fallback(
            client, "Hello world", "Speak clearly", "marin"
        )
        assert (model, voice) == ("primary-model", "cedar")
        assert client.audio.speech.calls == [("primary-model", "marin"), ("primary-model", "cedar")]
    finally:
        tts_generator.TTS_MODEL = original_model
        tts_generator.TTS_FALLBACK_MODEL = original_fallback_model
        tts_generator.TTS_FALLBACK_VOICES = original_fallback_voices
