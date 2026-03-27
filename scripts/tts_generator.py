"""
The Money Map — TTS Voiceover Generator

Supports:
- OpenAI Speech API (gpt-4o-mini-tts) with voice fallback and director-style instructions.
- ElevenLabs Text-to-Speech REST API (POST /v1/text-to-speech/{voice_id}) for more natural prosody.

Configure provider via TTS_PROVIDER env (openai | elevenlabs). See config/settings.py.

Usage:
    from scripts.tts_generator import generate_voiceover
    path = generate_voiceover()  # Uses defaults from settings
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from openai import OpenAI

# Allow running from repo root or scripts/
try:
    from config.settings import (
        OPENAI_API_KEY,
        TTS_MODEL,
        TTS_VOICE,
        TTS_INSTRUCTIONS,
        TTS_FALLBACK_MODEL,
        TTS_FALLBACK_VOICES,
        TTS_PROVIDER,
        ELEVENLABS_API_KEY,
        ELEVENLABS_VOICE_ID,
        ELEVENLABS_MODEL_ID,
        ELEVENLABS_OUTPUT_FORMAT,
        ELEVENLABS_API_BASE,
        ELEVENLABS_MAX_CHARS,
        ELEVENLABS_STABILITY,
        ELEVENLABS_SIMILARITY,
        ELEVENLABS_STYLE,
        ELEVENLABS_SPEED,
        ELEVENLABS_APPLY_TEXT_NORMALIZATION,
        ELEVENLABS_LANGUAGE_CODE,
        TTS_ELEVENLABS_FALLBACK_OPENAI,
        VOICEOVER_NORMALIZE,
    )
except ImportError:
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from config.settings import (
        OPENAI_API_KEY,
        TTS_MODEL,
        TTS_VOICE,
        TTS_INSTRUCTIONS,
        TTS_FALLBACK_MODEL,
        TTS_FALLBACK_VOICES,
        TTS_PROVIDER,
        ELEVENLABS_API_KEY,
        ELEVENLABS_VOICE_ID,
        ELEVENLABS_MODEL_ID,
        ELEVENLABS_OUTPUT_FORMAT,
        ELEVENLABS_API_BASE,
        ELEVENLABS_MAX_CHARS,
        ELEVENLABS_STABILITY,
        ELEVENLABS_SIMILARITY,
        ELEVENLABS_STYLE,
        ELEVENLABS_SPEED,
        ELEVENLABS_APPLY_TEXT_NORMALIZATION,
        ELEVENLABS_LANGUAGE_CODE,
        TTS_ELEVENLABS_FALLBACK_OPENAI,
        VOICEOVER_NORMALIZE,
    )

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
OUTPUT_DIR = os.path.join(BASE, "output")

try:
    from scripts.voiceover_normalize import normalize_for_tts
except ImportError:
    from voiceover_normalize import normalize_for_tts

# OpenAI TTS has a 4096 character limit per request
MAX_CHARS_OPENAI = 4096

_PREV_NEXT_SNIP = 500


def _split_script(text, max_chars):
    """Split script into chunks at sentence boundaries, respecting the char limit."""
    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        candidate = (current_chunk + " " + sentence).strip() if current_chunk else sentence
        if len(candidate) <= max_chars:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _concatenate_audio_files(file_paths, output_path):
    """Concatenate multiple WAV files using ffmpeg."""
    if len(file_paths) == 1:
        os.rename(file_paths[0], output_path)
        return

    list_file = output_path + ".list"
    try:
        with open(list_file, "w") as f:
            for path in file_paths:
                f.write(f"file '{path}'\n")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_file,
                "-c",
                "copy",
                output_path,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)


def _audio_duration_seconds(path: str) -> float:
    """Measure WAV/MP3 duration with ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    return float(result.stdout.strip())


def _voice_candidates(requested_voice):
    """Build ordered voice candidates with primary-first fallback behavior."""
    requested = (requested_voice or TTS_VOICE or "").strip()
    fallback = [v for v in TTS_FALLBACK_VOICES if v and v != requested]
    return [requested, *fallback] if requested else fallback


def _model_candidates():
    """Build ordered model candidates with stable snapshot first."""
    return [TTS_MODEL, TTS_FALLBACK_MODEL] if TTS_FALLBACK_MODEL != TTS_MODEL else [TTS_MODEL]


def _create_speech_with_fallback(client, text, instructions, requested_voice):
    """Create speech with model/voice fallback."""
    last_error = None
    for model in _model_candidates():
        for voice in _voice_candidates(requested_voice):
            try:
                response = client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=text,
                    instructions=instructions,
                    response_format="wav",
                )
                return response, model, voice
            except Exception as exc:
                last_error = exc

    raise RuntimeError(
        "OpenAI TTS generation failed for all configured model/voice candidates."
    ) from last_error


def _generate_openai_voiceover(script_text, output_path, voice, instructions):
    """Synthesize full script with OpenAI and write WAV."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    chunks = _split_script(script_text, MAX_CHARS_OPENAI)

    if len(chunks) == 1:
        response, _, _ = _create_speech_with_fallback(client, chunks[0], instructions, voice)
        response.stream_to_file(output_path)
    else:
        temp_files = []
        try:
            for i, chunk in enumerate(chunks):
                temp_path = os.path.join(tempfile.gettempdir(), f"tmm_tts_chunk_{i}.wav")
                response, _, _ = _create_speech_with_fallback(client, chunk, instructions, voice)
                response.stream_to_file(temp_path)
                temp_files.append(temp_path)

            _concatenate_audio_files(temp_files, output_path)
        except Exception:
            for path in temp_files:
                if os.path.exists(path):
                    os.remove(path)
            raise


def _elevenlabs_output_is_mp3() -> bool:
    fmt = (ELEVENLABS_OUTPUT_FORMAT or "").lower()
    return fmt.startswith("mp3_")


def _mp3_bytes_to_wav(mp3_bytes: bytes, wav_path: str) -> None:
    """Decode MP3 from ElevenLabs to PCM WAV for downstream ffmpeg/loudnorm."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(mp3_bytes)
        tmp_mp3 = tmp.name
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                tmp_mp3,
                "-acodec",
                "pcm_s16le",
                "-ar",
                "44100",
                "-ac",
                "1",
                wav_path,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
    finally:
        if os.path.exists(tmp_mp3):
            os.remove(tmp_mp3)


def _elevenlabs_synthesize_chunk(
    voice_id: str,
    text: str,
    previous_text: str | None,
    next_text: str | None,
) -> bytes:
    """Call ElevenLabs Create speech API. Docs: POST /v1/text-to-speech/{voice_id}."""
    safe_voice = urllib.parse.quote(voice_id, safe="")
    url = f"{ELEVENLABS_API_BASE}/v1/text-to-speech/{safe_voice}"
    params = {"output_format": ELEVENLABS_OUTPUT_FORMAT}
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/octet-stream",
    }
    body: dict = {
        "text": text,
        "model_id": ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": ELEVENLABS_STABILITY,
            "similarity_boost": ELEVENLABS_SIMILARITY,
            "style": ELEVENLABS_STYLE,
            "speed": ELEVENLABS_SPEED,
        },
    }
    if ELEVENLABS_APPLY_TEXT_NORMALIZATION is not None:
        body["apply_text_normalization"] = ELEVENLABS_APPLY_TEXT_NORMALIZATION
    if ELEVENLABS_LANGUAGE_CODE:
        body["language_code"] = ELEVENLABS_LANGUAGE_CODE
    if previous_text:
        tail = previous_text.strip()
        if len(tail) > _PREV_NEXT_SNIP:
            tail = tail[-_PREV_NEXT_SNIP:]
        body["previous_text"] = tail
    if next_text:
        head = next_text.strip()
        if len(head) > _PREV_NEXT_SNIP:
            head = head[:_PREV_NEXT_SNIP]
        body["next_text"] = head

    resp = requests.post(
        url,
        params=params,
        headers=headers,
        data=json.dumps(body),
        timeout=300,
    )
    if resp.status_code != 200:
        detail = resp.text[:800] if resp.text else ""
        raise RuntimeError(
            f"ElevenLabs TTS failed HTTP {resp.status_code}: {detail}"
        )
    return resp.content


def _generate_elevenlabs_voiceover(script_text, output_path, voice_id_override: str | None):
    """Synthesize full script with ElevenLabs; chunk for API limits and use continuity hints."""
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is not set.")
    voice_id = (voice_id_override or ELEVENLABS_VOICE_ID or "").strip()
    if not voice_id:
        raise ValueError(
            "ElevenLabs requires a voice id: set ELEVENLABS_VOICE_ID or pass voice= to generate_voiceover."
        )

    max_chars = max(500, ELEVENLABS_MAX_CHARS)
    chunks = _split_script(script_text, max_chars)

    if len(chunks) == 1:
        audio = _elevenlabs_synthesize_chunk(voice_id, chunks[0], None, None)
        if _elevenlabs_output_is_mp3():
            _mp3_bytes_to_wav(audio, output_path)
        else:
            with open(output_path, "wb") as f:
                f.write(audio)
        return

    temp_files: list[str] = []
    try:
        for i, chunk in enumerate(chunks):
            prev_full = chunks[i - 1] if i > 0 else None
            nxt_full = chunks[i + 1] if i + 1 < len(chunks) else None
            audio = _elevenlabs_synthesize_chunk(
                voice_id,
                chunk,
                previous_text=prev_full,
                next_text=nxt_full,
            )
            temp_path = os.path.join(
                tempfile.gettempdir(), f"tmm_eleven_chunk_{i}.wav"
            )
            if _elevenlabs_output_is_mp3():
                _mp3_bytes_to_wav(audio, temp_path)
            else:
                with open(temp_path, "wb") as f:
                    f.write(audio)
            temp_files.append(temp_path)

        _concatenate_audio_files(temp_files, output_path)
    except Exception:
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)
        raise


def _normalize_script_text(script_text: str) -> str:
    """Apply the configured text normalization rules to narration input."""
    if VOICEOVER_NORMALIZE:
        return normalize_for_tts(script_text)
    return script_text


def _synthesize_script_text(
    script_text: str,
    output_path: str,
    voice: str | None,
    instructions: str,
) -> None:
    """Synthesize one narration chunk to disk using the configured provider."""
    provider = (TTS_PROVIDER or "openai").strip().lower()
    if provider == "elevenlabs":
        try:
            _generate_elevenlabs_voiceover(script_text, output_path, voice)
        except Exception as exc:
            if TTS_ELEVENLABS_FALLBACK_OPENAI and OPENAI_API_KEY:
                print(f"  ElevenLabs TTS failed ({exc}); falling back to OpenAI.")
                _generate_openai_voiceover(
                    script_text, output_path, voice or TTS_VOICE, instructions
                )
            else:
                raise
        return
    _generate_openai_voiceover(script_text, output_path, voice or TTS_VOICE, instructions)


def generate_voiceover_timeline(
    sections: list[dict[str, Any]],
    *,
    output_path: str | None = None,
    timeline_path: str | None = None,
    voice: str | None = None,
    instructions: str | None = None,
) -> dict[str, Any]:
    """Generate final audio plus a section-timing manifest from ordered sections."""
    output_path = output_path or os.path.join(OUTPUT_DIR, "voiceover.wav")
    timeline_path = timeline_path or os.path.join(DATA_DIR, "voiceover_timeline.json")
    instructions = instructions or TTS_INSTRUCTIONS
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(timeline_path), exist_ok=True)

    normalized_sections: list[dict[str, Any]] = []
    temp_files: list[str] = []
    try:
        for index, section in enumerate(sections):
            section_id = str(section.get("id", f"section_{index + 1}"))
            raw_text = str(section.get("text", "")).strip()
            if not raw_text:
                continue
            normalized_text = _normalize_script_text(raw_text)
            temp_path = os.path.join(
                tempfile.gettempdir(),
                f"tmm_voice_section_{index:02d}_{section_id}.wav",
            )
            _synthesize_script_text(normalized_text, temp_path, voice, instructions)
            temp_files.append(temp_path)
            normalized_sections.append(
                {
                    "id": section_id,
                    "text": normalized_text,
                    "word_count": len(normalized_text.split()),
                    "audio_path": temp_path,
                }
            )

        if not normalized_sections:
            raise ValueError("No non-empty sections were provided for voiceover generation.")

        cursor = 0.0
        timeline_sections: list[dict[str, Any]] = []
        for section in normalized_sections:
            duration_sec = round(_audio_duration_seconds(section["audio_path"]), 3)
            timeline_sections.append(
                {
                    "id": section["id"],
                    "word_count": section["word_count"],
                    "start_sec": round(cursor, 3),
                    "end_sec": round(cursor + duration_sec, 3),
                    "duration_sec": duration_sec,
                    "text": section["text"],
                }
            )
            cursor += duration_sec

        _concatenate_audio_files(temp_files, output_path)
        final_duration = round(_audio_duration_seconds(output_path), 3)
        payload = {
            "generated_at": datetime.now().isoformat(),
            "provider": (TTS_PROVIDER or "openai").strip().lower(),
            "output_path": os.path.abspath(output_path),
            "duration_sec": final_duration,
            "section_count": len(timeline_sections),
            "sections": timeline_sections,
        }
        Path(timeline_path).write_text(json.dumps(payload, indent=2))

        tts_debug_path = os.path.join(OUTPUT_DIR, "voiceover_tts_input.txt")
        try:
            with open(tts_debug_path, "w", encoding="utf-8") as dbg:
                dbg.write("\n\n".join(section["text"] for section in normalized_sections))
        except OSError:
            pass

        return {
            "output_path": os.path.abspath(output_path),
            "timeline_path": os.path.abspath(timeline_path),
            "timeline": payload,
        }
    finally:
        for section in normalized_sections:
            temp_path = section.get("audio_path")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)


def generate_voiceover(
    script_path=None,
    output_path=None,
    voice=None,
    instructions=None,
):
    """Generate voiceover WAV from a plain-text script.

    Provider is selected by TTS_PROVIDER (openai | elevenlabs).

    Args:
        script_path: Path to plain-text script. Defaults to data/voiceover_script.txt.
        output_path: Where to save WAV. Defaults to output/voiceover.wav.
        voice: OpenAI voice name when using OpenAI; ElevenLabs voice_id when using ElevenLabs.
        instructions: Style instructions (OpenAI only; ignored for ElevenLabs).

    Plain-text scripts are passed through ``normalize_for_tts`` (prices, dates, %)
    unless VOICEOVER_NORMALIZE is false in the environment.

    Returns:
        Absolute path to the generated WAV file.
    """
    script_path = script_path or os.path.join(DATA_DIR, "voiceover_script.txt")
    output_path = output_path or os.path.join(OUTPUT_DIR, "voiceover.wav")
    instructions = instructions or TTS_INSTRUCTIONS

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(script_path, "r") as f:
        script_text = f.read().strip()

    if not script_text:
        raise ValueError(f"Script file is empty: {script_path}")

    script_text = _normalize_script_text(script_text)

    tts_debug_path = os.path.join(OUTPUT_DIR, "voiceover_tts_input.txt")
    try:
        with open(tts_debug_path, "w", encoding="utf-8") as dbg:
            dbg.write(script_text)
    except OSError:
        pass

    _synthesize_script_text(script_text, output_path, voice, instructions)

    return os.path.abspath(output_path)


if __name__ == "__main__":
    print("Generating voiceover...")
    path = generate_voiceover()
    print(f"Done: {path}")
