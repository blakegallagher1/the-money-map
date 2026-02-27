"""
The Money Map — TTS Voiceover Generator

Generates voiceover audio using OpenAI's gpt-4o-mini-tts model.
Supports style control via natural language instructions for pacing,
emotion, and emphasis.

Usage:
    from scripts.tts_generator import generate_voiceover
    path = generate_voiceover()  # Uses defaults from settings
"""
import os
import re
import subprocess
import tempfile

from openai import OpenAI

# Allow running from repo root or scripts/
try:
    from config.settings import (
        OPENAI_API_KEY, TTS_MODEL, TTS_VOICE, TTS_INSTRUCTIONS,
    )
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import (
        OPENAI_API_KEY, TTS_MODEL, TTS_VOICE, TTS_INSTRUCTIONS,
    )

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
OUTPUT_DIR = os.path.join(BASE, 'output')

# OpenAI TTS has a 4096 character limit per request
MAX_CHARS_PER_REQUEST = 4096


def _split_script(text, max_chars=MAX_CHARS_PER_REQUEST):
    """Split script into chunks at sentence boundaries, respecting the char limit."""
    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r'(?<=[.!?])\s+', text)
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
    """Concatenate multiple MP3 files using ffmpeg."""
    if len(file_paths) == 1:
        os.rename(file_paths[0], output_path)
        return

    list_file = output_path + ".list"
    try:
        with open(list_file, 'w') as f:
            for path in file_paths:
                f.write(f"file '{path}'\n")

        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
             '-i', list_file, '-c', 'copy', output_path],
            capture_output=True, text=True, check=True, timeout=60,
        )
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)


def generate_voiceover(
    script_path=None,
    output_path=None,
    voice=None,
    instructions=None,
):
    """Generate voiceover MP3 from a text script using OpenAI TTS.

    Args:
        script_path: Path to plain-text script. Defaults to data/voiceover_script.txt.
        output_path: Where to save the MP3. Defaults to output/voiceover.mp3.
        voice: OpenAI voice name. Defaults to settings.TTS_VOICE.
        instructions: Style instructions. Defaults to settings.TTS_INSTRUCTIONS.

    Returns:
        str: Absolute path to the generated MP3 file.
    """
    script_path = script_path or os.path.join(DATA_DIR, 'voiceover_script.txt')
    output_path = output_path or os.path.join(OUTPUT_DIR, 'voiceover.mp3')
    voice = voice or TTS_VOICE
    instructions = instructions or TTS_INSTRUCTIONS

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(script_path, 'r') as f:
        script_text = f.read().strip()

    if not script_text:
        raise ValueError(f"Script file is empty: {script_path}")

    client = OpenAI(api_key=OPENAI_API_KEY)
    chunks = _split_script(script_text)

    if len(chunks) == 1:
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=voice,
            input=chunks[0],
            instructions=instructions,
            response_format="mp3",
        )
        response.stream_to_file(output_path)
    else:
        # Multiple chunks — generate each, then concatenate
        temp_files = []
        try:
            for i, chunk in enumerate(chunks):
                temp_path = os.path.join(
                    tempfile.gettempdir(), f"tmm_tts_chunk_{i}.mp3"
                )
                response = client.audio.speech.create(
                    model=TTS_MODEL,
                    voice=voice,
                    input=chunk,
                    instructions=instructions,
                    response_format="mp3",
                )
                response.stream_to_file(temp_path)
                temp_files.append(temp_path)

            _concatenate_audio_files(temp_files, output_path)
        except Exception:
            # Clean up temp files on error
            for path in temp_files:
                if os.path.exists(path):
                    os.remove(path)
            raise

    return os.path.abspath(output_path)


if __name__ == "__main__":
    print("Generating voiceover...")
    path = generate_voiceover()
    print(f"Done: {path}")
