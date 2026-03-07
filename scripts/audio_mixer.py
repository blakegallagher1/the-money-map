"""
Audio Mixer for The Money Map
Selects mood-matched background music and mixes it with voiceover.

Music is mixed at -18dB below voiceover with fade-in/out.
Supports sentiment-based track selection from assets/music/.
"""
import os
import subprocess
import sys

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


def get_audio_duration(path):
    """Get duration of an audio file in seconds."""
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())


def select_music(script_data):
    """Pick a background music track based on story sentiment.

    Returns the path to the selected music file, or None if no music available.
    """
    yoy_pct = script_data.get('primary_metric', {}).get('yoy_pct', 0)
    tags = script_data.get('primary_metric', {}).get('tags', [])

    # Determine sentiment
    if 'dramatic_change' in tags and abs(yoy_pct) > 20:
        sentiment = "dramatic"
    elif yoy_pct < -10 or 'consumer_pain_point' in tags:
        sentiment = "tense"
    elif yoy_pct > 10:
        sentiment = "hopeful"
    else:
        sentiment = "neutral"

    track_file = MUSIC_TRACKS.get(sentiment, "neutral.mp3")
    track_path = os.path.join(MUSIC_DIR, track_file)

    if os.path.exists(track_path):
        print(f"  Selected music: {sentiment} ({track_file})")
        return track_path

    # Try fallback to any available track
    for name, filename in MUSIC_TRACKS.items():
        fallback = os.path.join(MUSIC_DIR, filename)
        if os.path.exists(fallback):
            print(f"  Fallback music: {name} ({filename})")
            return fallback

    print("  No music tracks found in assets/music/")
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
        '-c:a', 'aac', '-b:a', '192k',
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
    """Full audio pipeline: select music + mix.

    Returns path to final audio (mixed if music available, raw voiceover otherwise).
    """
    music_path = select_music(script_data)

    if music_path is None:
        print("  Skipping music mix — no tracks available")
        return voiceover_path

    mixed_path = os.path.join(output_dir, 'mixed_audio.mp3')
    return mix_audio(voiceover_path, music_path, mixed_path)


if __name__ == "__main__":
    import json
    # Test with an existing episode
    script_path = os.path.join(BASE, 'data', 'ep1_v2', 'script.json')
    with open(script_path) as f:
        script_data = json.load(f)

    vo_path = os.path.join(BASE, 'output', 'voiceover.mp3')
    if os.path.exists(vo_path):
        result = process_audio(vo_path, script_data, os.path.join(BASE, 'output'))
        print(f"Result: {result}")
    else:
        print("No voiceover.mp3 found — run TTS first")
