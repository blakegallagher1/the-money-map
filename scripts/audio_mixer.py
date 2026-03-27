"""
Audio Mixer for Brick & Yield
Selects mood-matched background music and mixes it with voiceover.

Pipeline:
1. Normalize voiceover to -16 LUFS (YouTube standard)
2. Select mood-matched background music
3. Mix music at -18dB below voiceover with fade-in/out
"""
import os
import subprocess
import sys
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_DIR = os.path.join(BASE, 'assets', 'music')

# Music track mapping by sentiment
MUSIC_TRACKS = {
    "tense": "tense.mp3",
    "hopeful": "hopeful.mp3",
    "neutral": "neutral.mp3",
    "dramatic": "dramatic.mp3",
}

# Volume level for background music (0.0-1.0, relative to voiceover)
# 0.12 ≈ -18dB below voiceover
MUSIC_VOLUME = 0.12
FADE_IN_SEC = 2.0
FADE_OUT_SEC = 3.0

# Loudness normalization target (YouTube recommends -14 to -16 LUFS)
TARGET_LUFS = -16
TARGET_TRUE_PEAK = -1.5
TARGET_LRA = 11
AUDIO_QUALITY_REPORT = "audio_quality_report.json"
MUSIC_PROVENANCE_REPORT = "music_provenance.json"


def get_audio_duration(path):
    """Get duration of an audio file in seconds."""
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())


def _extract_loudnorm_json(stderr_text):
    """Extract loudnorm JSON payload from ffmpeg stderr."""
    json_start = stderr_text.rfind('{')
    json_end = stderr_text.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        try:
            return json.loads(stderr_text[json_start:json_end])
        except json.JSONDecodeError:
            return None
    return None


def measure_loudness(path):
    """Measure integrated LUFS and true peak using ffmpeg loudnorm."""
    cmd = [
        'ffmpeg', '-y', '-i', path,
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
        '-f', 'null', '-'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    payload = _extract_loudnorm_json(result.stderr)
    if not payload:
        return {
            "integrated_lufs": None,
            "true_peak_dbtp": None,
            "lra": None,
            "measured": False,
        }
    return {
        "integrated_lufs": payload.get("input_i"),
        "true_peak_dbtp": payload.get("input_tp"),
        "lra": payload.get("input_lra"),
        "threshold": payload.get("input_thresh"),
        "target_offset": payload.get("target_offset"),
        "measured": True,
    }


def _write_json(path, payload):
    """Persist structured report payload."""
    with open(path, "w") as handle:
        json.dump(payload, handle, indent=2)


def _build_music_provenance(music_path, final_audio_path):
    """Build provenance metadata for the selected music source."""
    if not music_path:
        return {
            "source": "none",
            "license_id": "voice_only",
            "file_path": final_audio_path,
            "music_enabled": False,
        }

    normalized = os.path.abspath(music_path)
    filename = os.path.basename(normalized)
    stem, _ = os.path.splitext(filename)

    if "/assets/music/" in normalized.replace("\\", "/"):
        source = "static_library"
        license_id = stem
    elif "/output/" in normalized.replace("\\", "/"):
        source = "ai_generated"
        license_id = "generated_track"
    else:
        source = "external"
        license_id = stem or "unknown"

    return {
        "source": source,
        "license_id": license_id,
        "file_path": normalized,
        "music_enabled": True,
    }


def normalize_voiceover(input_path, output_path):
    """Normalize voiceover to target LUFS for consistent volume across episodes.

    Uses ffmpeg loudnorm filter (EBU R128) in two-pass mode for accurate results.
    Target: -16 LUFS, -1.5 dBTP, 11 LRA (YouTube recommended range).
    """
    # Pass 1: Measure current loudness
    measure_cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-af', f'loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}:print_format=json',
        '-f', 'null', '-'
    ]
    measure_result = subprocess.run(
        measure_cmd, capture_output=True, text=True, timeout=120
    )

    measured = _extract_loudnorm_json(measure_result.stderr)
    if measured:
        measured_i = measured.get('input_i', str(TARGET_LUFS))
        measured_tp = measured.get('input_tp', str(TARGET_TRUE_PEAK))
        measured_lra = measured.get('input_lra', str(TARGET_LRA))
        measured_thresh = measured.get('input_thresh', '-26.0')
        target_offset = measured.get('target_offset', '0.0')
    else:
        measured_i = str(TARGET_LUFS)
        measured_tp = str(TARGET_TRUE_PEAK)
        measured_lra = str(TARGET_LRA)
        measured_thresh = '-26.0'
        target_offset = '0.0'

    # Pass 2: Apply normalization with measured values
    normalize_filter = (
        f'loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}'
        f':measured_I={measured_i}:measured_TP={measured_tp}'
        f':measured_LRA={measured_lra}:measured_thresh={measured_thresh}'
        f':offset={target_offset}:linear=true'
    )

    normalize_cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-af', normalize_filter,
        '-ar', '44100',
        output_path
    ]

    result = subprocess.run(
        normalize_cmd, capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"  Warning: Loudness normalization failed, using raw voiceover: {result.stderr[-200:]}")
        return input_path

    print(f"  Normalized voiceover to {TARGET_LUFS} LUFS")
    return output_path


def select_music(script_data, output_dir=None):
    """Pick a background music track — AI-generated or static.

    Priority order:
    1. Generate a unique track via Suno API (if SUNO_API_KEY is set)
    2. Use a cached AI-generated track for this mood
    3. Fall back to static tracks in assets/music/
    4. Return None (episode will have voice-only audio)

    Returns the path to the selected music file, or None if no music available.
    """
    from scripts.music_generator import determine_mood, generate_episode_music

    mood = determine_mood(script_data)

    # Try AI generation first (uses cache if available)
    ai_track = generate_episode_music(mood, output_dir=output_dir)
    if ai_track and os.path.exists(ai_track):
        print(f"  Using AI-generated music: {mood}")
        return ai_track

    # Fall back to static tracks
    print(f"  AI music unavailable — checking static tracks for '{mood}'...")
    track_file = MUSIC_TRACKS.get(mood, "neutral.mp3")
    track_path = os.path.join(MUSIC_DIR, track_file)

    if os.path.exists(track_path):
        print(f"  Selected static music: {mood} ({track_file})")
        return track_path

    # Try fallback to any available static track
    for name, filename in MUSIC_TRACKS.items():
        fallback = os.path.join(MUSIC_DIR, filename)
        if os.path.exists(fallback):
            print(f"  Fallback static music: {name} ({filename})")
            return fallback

    print("  No music available (set SUNO_API_KEY for AI generation, or add tracks to assets/music/)")
    return None


def mix_audio(voiceover_path, music_path, output_path):
    """Mix voiceover with background music using ffmpeg.

    - Music loops to match voiceover length
    - Music volume at ~-18dB below voiceover
    - 2s fade-in at start, 3s fade-out at end
    """
    vo_duration = get_audio_duration(voiceover_path)
    fade_out_start = max(0, vo_duration - FADE_OUT_SEC)

    # ffmpeg filter chain:
    # 1. Loop music to fill voiceover duration
    # 2. Lower music volume to MUSIC_VOLUME
    # 3. Fade in at start, fade out at end
    # 4. Mix with voiceover (voiceover is dominant)
    filter_complex = (
        f"[1:a]volume={MUSIC_VOLUME},"
        f"afade=t=in:d={FADE_IN_SEC},"
        f"afade=t=out:st={fade_out_start}:d={FADE_OUT_SEC}[music];"
        f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[out]"
    )

    cmd = [
        'ffmpeg', '-y',
        '-i', voiceover_path,
        '-stream_loop', '-1', '-i', music_path,
        '-filter_complex', filter_complex,
        '-map', '[out]',
        '-c:a', 'aac', '-b:a', '320k',
        '-t', str(vo_duration),
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        raise RuntimeError(f"Audio mixing failed: {result.stderr[-500:]}")

    mixed_duration = get_audio_duration(output_path)
    print(f"  Mixed audio: {mixed_duration:.1f}s ({output_path})")
    return output_path


def process_audio(voiceover_path, script_data, output_dir):
    """Full audio pipeline: normalize → select music → mix.

    Returns path to final audio (mixed if music available, normalized voiceover otherwise).
    """
    # Step 1: Normalize voiceover loudness
    normalized_path = os.path.join(output_dir, 'voiceover_normalized.wav')
    voiceover_path = normalize_voiceover(voiceover_path, normalized_path)

    # Step 2: Select and mix music
    music_path = select_music(script_data, output_dir=output_dir)
    final_audio_path = voiceover_path
    if music_path is None:
        print("  Skipping music mix — no tracks available")
        final_audio_path = voiceover_path
    else:
        mixed_path = os.path.join(output_dir, 'mixed_audio.wav')
        final_audio_path = mix_audio(voiceover_path, music_path, mixed_path)

    # Persist compliance artifacts for pre-upload quality gate.
    loudness = measure_loudness(final_audio_path)
    loudness_payload = {
        "generated_at": datetime.now().isoformat(),
        "target_lufs": TARGET_LUFS,
        "target_true_peak_dbtp": TARGET_TRUE_PEAK,
        "audio_path": os.path.abspath(final_audio_path),
        "metrics": loudness,
    }
    provenance_payload = {
        "generated_at": datetime.now().isoformat(),
        "audio_path": os.path.abspath(final_audio_path),
        **_build_music_provenance(music_path, final_audio_path),
    }
    _write_json(os.path.join(output_dir, AUDIO_QUALITY_REPORT), loudness_payload)
    _write_json(os.path.join(output_dir, MUSIC_PROVENANCE_REPORT), provenance_payload)
    return final_audio_path


if __name__ == "__main__":
    import json
    # Test with an existing episode
    script_path = os.path.join(BASE, 'data', 'ep1_v2', 'script.json')
    with open(script_path) as f:
        script_data = json.load(f)

    vo_path = os.path.join(BASE, 'output', 'voiceover.wav')
    if os.path.exists(vo_path):
        result = process_audio(vo_path, script_data, os.path.join(BASE, 'output'))
        print(f"Result: {result}")
    else:
        print("No voiceover.wav found — run TTS first")
