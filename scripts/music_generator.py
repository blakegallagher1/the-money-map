"""
AI Music Generator for Brick & Yield
Generates unique instrumental background tracks per episode via Suno V5 API.

Each mood category has a carefully crafted prompt that produces music with
real character — blues, jazz, cinematic — not generic ambient pads.

Supports multiple API providers (sunoapi.org, apiframe, evolink) via a
simple REST interface. Set SUNO_API_KEY and optionally SUNO_API_URL in env.

Usage:
    from scripts.music_generator import generate_episode_music
    path = generate_episode_music("tense", duration_hint=300, output_dir="output/")
"""

import hashlib
import json
import os
import re
import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_CACHE_DIR = os.path.join(BASE, 'assets', 'music', 'generated')

# --- API Config ---
# Default to sunoapi.org; override with SUNO_API_URL env var for other providers
SUNO_API_KEY = os.environ.get("SUNO_API_KEY", "")
SUNO_API_URL = os.environ.get("SUNO_API_URL", "https://api.sunoapi.org/api/v1")

# --- Generation Settings ---
SUNO_MODEL = os.environ.get("SUNO_MODEL", "v5")
MAX_POLL_SECONDS = 300  # 5 minutes max wait
POLL_INTERVAL = 5  # seconds between polls

# --- Mood-to-Prompt Mapping ---
# These prompts produce distinctive, character-rich instrumentals
# Genre-forward, no artist names, legally clean
MOOD_PROMPTS = {
    "tense": {
        "prompt": (
            "Dark blues instrumental with heavy slide guitar, "
            "low rumbling bass, slow 70 BPM groove, vinyl crackle texture, "
            "Mississippi delta mood meets modern cinematic tension, "
            "ominous piano stabs, no vocals, underscore for financial data narration"
        ),
        "tags": "blues, dark, cinematic, slow, instrumental, slide guitar, tension",
        "title": "Brick and Yield — Tension Bed",
    },
    "dramatic": {
        "prompt": (
            "Intense cinematic instrumental with orchestral strings building tension, "
            "deep cello drone, driving percussion at 90 BPM, "
            "brass swells on the downbeat, jazz-noir atmosphere, "
            "think film score for a Wall Street thriller, "
            "no vocals, underscore for economic data revelation"
        ),
        "tags": "cinematic, orchestral, dramatic, jazz noir, instrumental, intense",
        "title": "Brick and Yield — Drama Bed",
    },
    "hopeful": {
        "prompt": (
            "Warm jazz instrumental with brushed drums, upright bass walking line, "
            "mellow Rhodes piano chords, 95 BPM, "
            "late-night radio feel, smooth and confident, "
            "subtle brass accents, light vinyl warmth, "
            "no vocals, underscore for optimistic financial analysis"
        ),
        "tags": "jazz, warm, smooth, instrumental, Rhodes piano, brushed drums, hopeful",
        "title": "Brick and Yield — Hope Bed",
    },
    "neutral": {
        "prompt": (
            "Lo-fi jazz instrumental with soft piano, muted trumpet in the distance, "
            "gentle boom-bap drums at 85 BPM, "
            "warm analog tape saturation, vinyl crackle, "
            "rainy night atmosphere, contemplative and steady, "
            "no vocals, background music for data-driven narration"
        ),
        "tags": "lo-fi, jazz, chill, instrumental, piano, tape saturation, neutral",
        "title": "Brick and Yield — Neutral Bed",
    },
    "urgent": {
        "prompt": (
            "Hard-hitting boom-bap instrumental with gritty MPC drums, "
            "deep sub-bass, 90s hip-hop production style, 88 BPM, "
            "dark piano loop chopped and pitched down, "
            "raw and aggressive energy, East Coast boom-bap meets modern trap bass, "
            "no vocals, underscore for urgent economic warning"
        ),
        "tags": "boom-bap, hip-hop, instrumental, gritty, dark piano, urgent",
        "title": "Brick and Yield — Urgent Bed",
    },
}

# Fallback order if requested mood isn't available
MOOD_FALLBACK = {
    "tense": "dramatic",
    "dramatic": "tense",
    "hopeful": "neutral",
    "neutral": "hopeful",
    "urgent": "dramatic",
}


def _cache_key(mood, prompt):
    """Generate a cache key from mood + prompt hash."""
    h = hashlib.md5(prompt.encode()).hexdigest()[:10]
    return f"{mood}_{h}"


def _cached_path(mood, prompt):
    """Check if a track for this mood/prompt is already cached."""
    os.makedirs(MUSIC_CACHE_DIR, exist_ok=True)
    key = _cache_key(mood, prompt)
    # Check for any audio file with this key
    for ext in ('.mp3', '.wav', '.m4a'):
        path = os.path.join(MUSIC_CACHE_DIR, f"{key}{ext}")
        if os.path.exists(path):
            return path
    return None


def _download_audio(url, output_path):
    """Download an audio file from URL."""
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path


def generate_via_suno_api(mood, prompt_config):
    """Generate an instrumental track via Suno API.

    Returns the path to the downloaded audio file, or None on failure.
    """
    if not SUNO_API_KEY:
        print("  SUNO_API_KEY not set — skipping AI music generation")
        return None

    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt_config["prompt"],
        "tags": prompt_config["tags"],
        "title": prompt_config["title"],
        "make_instrumental": True,
        "model": SUNO_MODEL,
    }

    try:
        # Submit generation request
        print(f"  Generating {mood} background music via Suno {SUNO_MODEL}...")
        response = requests.post(
            f"{SUNO_API_URL}/generate",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        # Handle different API response formats
        task_id = (
            result.get("id") or
            result.get("task_id") or
            result.get("data", {}).get("task_id") or
            result.get("data", {}).get("id")
        )

        if not task_id:
            # Some APIs return the audio directly
            audio_url = (
                result.get("audio_url") or
                result.get("data", {}).get("audio_url")
            )
            if audio_url:
                cache_path = os.path.join(
                    MUSIC_CACHE_DIR,
                    f"{_cache_key(mood, prompt_config['prompt'])}.mp3"
                )
                os.makedirs(MUSIC_CACHE_DIR, exist_ok=True)
                _download_audio(audio_url, cache_path)
                print(f"  Music generated and cached: {cache_path}")
                return cache_path

            print(f"  Unexpected API response format: {json.dumps(result)[:200]}")
            return None

        # Poll for completion
        print(f"  Task submitted: {task_id}")
        start = time.time()
        while time.time() - start < MAX_POLL_SECONDS:
            time.sleep(POLL_INTERVAL)

            poll_response = requests.get(
                f"{SUNO_API_URL}/fetch/{task_id}",
                headers=headers,
                timeout=30,
            )
            poll_response.raise_for_status()
            poll_result = poll_response.json()

            # Normalize status from different API formats
            status = (
                poll_result.get("status") or
                poll_result.get("data", {}).get("status", "")
            ).lower()

            if status in ("completed", "complete", "success"):
                # Extract audio URL
                audio_url = None

                # Try various response formats
                tracks = (
                    poll_result.get("tracks") or
                    poll_result.get("data", {}).get("tracks") or
                    poll_result.get("output") or
                    poll_result.get("data", {}).get("output")
                )

                if isinstance(tracks, list) and tracks:
                    audio_url = tracks[0].get("audio_url") or tracks[0].get("url")
                elif isinstance(tracks, str):
                    audio_url = tracks
                else:
                    audio_url = (
                        poll_result.get("audio_url") or
                        poll_result.get("data", {}).get("audio_url")
                    )

                if audio_url:
                    cache_path = os.path.join(
                        MUSIC_CACHE_DIR,
                        f"{_cache_key(mood, prompt_config['prompt'])}.mp3"
                    )
                    os.makedirs(MUSIC_CACHE_DIR, exist_ok=True)
                    _download_audio(audio_url, cache_path)
                    print(f"  Music generated and cached: {cache_path}")
                    return cache_path
                else:
                    print(f"  Generation completed but no audio URL found: {json.dumps(poll_result)[:200]}")
                    return None

            elif status in ("failed", "error"):
                error_msg = (
                    poll_result.get("error") or
                    poll_result.get("data", {}).get("error", "Unknown error")
                )
                print(f"  Music generation failed: {error_msg}")
                return None

            else:
                elapsed = int(time.time() - start)
                print(f"  Waiting... status={status} ({elapsed}s)")

        print(f"  Music generation timed out after {MAX_POLL_SECONDS}s")
        return None

    except requests.exceptions.RequestException as e:
        print(f"  Suno API request failed: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Failed to parse Suno API response: {e}")
        return None


def generate_episode_music(mood, output_dir=None):
    """Generate or retrieve a background music track for an episode.

    Args:
        mood: One of 'tense', 'dramatic', 'hopeful', 'neutral', 'urgent'
        output_dir: Optional directory to copy the track to

    Returns:
        str: Path to the audio file, or None if generation fails
    """
    # Resolve mood to prompt config
    prompt_config = MOOD_PROMPTS.get(mood)
    if not prompt_config:
        fallback_mood = MOOD_FALLBACK.get(mood, "neutral")
        print(f"  Unknown mood '{mood}', falling back to '{fallback_mood}'")
        prompt_config = MOOD_PROMPTS[fallback_mood]
        mood = fallback_mood

    # Check cache first
    cached = _cached_path(mood, prompt_config["prompt"])
    if cached:
        print(f"  Using cached music: {cached}")
        if output_dir:
            import shutil
            dest = os.path.join(output_dir, f"bg_music_{mood}.mp3")
            shutil.copy2(cached, dest)
            return dest
        return cached

    # Generate via API
    result_path = generate_via_suno_api(mood, prompt_config)

    if result_path and output_dir:
        import shutil
        dest = os.path.join(output_dir, f"bg_music_{mood}.mp3")
        shutil.copy2(result_path, dest)
        return dest

    return result_path


def determine_mood(script_data):
    """Determine the appropriate mood from script metadata.

    Uses the same logic as the old static track selector, but with
    the expanded mood vocabulary.
    """
    yoy_pct = script_data.get('primary_metric', {}).get('yoy_pct', 0)
    tags = script_data.get('primary_metric', {}).get('tags', [])

    if 'dramatic_change' in tags and abs(yoy_pct) > 20:
        return "dramatic"
    elif 'dramatic_change' in tags:
        return "urgent"
    elif yoy_pct < -10 or 'consumer_pain_point' in tags:
        return "tense"
    elif yoy_pct > 10:
        return "hopeful"
    else:
        return "neutral"


if __name__ == "__main__":
    # Test: generate one track per mood
    for mood in MOOD_PROMPTS:
        print(f"\n--- Generating {mood} ---")
        path = generate_episode_music(mood)
        if path:
            size = os.path.getsize(path) / (1024 * 1024)
            print(f"  Result: {path} ({size:.1f} MB)")
        else:
            print(f"  No track generated (SUNO_API_KEY may not be set)")
