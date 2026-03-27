"""
Automated B-Roll Generator for The Money Map
Generates AI video clips via Luma Dream Machine API.

Takes b-roll prompts from script JSON and produces 4-second
cinematic clips, normalized to target resolution/fps.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import LUMA_API_KEY, BROLL_DURATION, VIDEO_WIDTH, VIDEO_HEIGHT, FPS

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE, 'assets', 'broll_cache')


def _prompt_hash(prompt):
    """Generate a short hash for caching b-roll by prompt."""
    return hashlib.md5(prompt.encode()).hexdigest()[:12]


def _normalize_clip(input_path, output_path, width=VIDEO_WIDTH, height=VIDEO_HEIGHT, fps=FPS):
    """Re-encode clip to match target data-viz format."""
    subprocess.run([
        'ffmpeg', '-y', '-i', input_path,
        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
               f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-r', str(fps), '-pix_fmt', 'yuv420p',
        '-an',
        output_path
    ], capture_output=True, text=True, timeout=120, check=True)


def _check_cache(prompt):
    """Check if a b-roll clip for this prompt is already cached."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{_prompt_hash(prompt)}.mp4")
    if os.path.exists(cache_path):
        return cache_path
    return None


def _save_to_cache(prompt, clip_path):
    """Save a generated clip to the cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{_prompt_hash(prompt)}.mp4")
    subprocess.run(['cp', clip_path, cache_path], check=True)
    return cache_path


def generate_single_clip(prompt, output_path, max_retries=3, width=VIDEO_WIDTH, height=VIDEO_HEIGHT, fps=FPS):
    """Generate a single b-roll clip via Luma Dream Machine API.

    Args:
        prompt: Scene description for AI video generation
        output_path: Where to save the final normalized clip
        max_retries: Number of retries with exponential backoff
    """
    # Check cache first
    cached = _check_cache(prompt)
    if cached:
        print(f"    Using cached clip: {cached}")
        _normalize_clip(cached, output_path, width=width, height=height, fps=fps)
        return output_path

    if not LUMA_API_KEY:
        raise ValueError("LUMA_API_KEY not set. Set it in .env or environment.")

    from lumaai import LumaAI

    client = LumaAI(auth_token=LUMA_API_KEY)

    for attempt in range(max_retries):
        try:
            # Create generation request
            generation = client.generations.create(
                prompt=prompt,
                aspect_ratio="16:9",
                loop=False,
            )

            generation_id = generation.id
            print(f"    Luma generation started: {generation_id}")

            # Poll for completion
            while True:
                generation = client.generations.get(id=generation_id)

                if generation.state == "completed":
                    break
                elif generation.state == "failed":
                    raise RuntimeError(
                        f"Luma generation failed: {generation.failure_reason}"
                    )

                time.sleep(5)

            # Download the video
            video_url = generation.assets.video
            if not video_url:
                raise RuntimeError("Luma returned no video URL")

            # Download via requests
            import requests
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()

            raw_path = output_path + ".raw.mp4"
            with open(raw_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Normalize to target output format
            _normalize_clip(raw_path, output_path, width=width, height=height, fps=fps)

            # Cache for future use
            _save_to_cache(prompt, output_path)

            # Clean up raw file
            os.remove(raw_path)

            print(f"    Clip saved: {output_path}")
            return output_path

        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"    Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"B-roll generation failed after {max_retries} attempts: {e}"
                )


def generate_broll(broll_prompts, output_dir, width=VIDEO_WIDTH, height=VIDEO_HEIGHT, fps=FPS):
    """Generate all requested b-roll clips for an episode."""
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    items = list((broll_prompts or {}).items())
    if not items:
        print("  No b-roll prompts provided")
        return results

    for scene_name, prompt in items:
        if not prompt:
            print(f"  Skipping {scene_name} — no prompt provided")
            results[scene_name] = None
            continue

        output_path = os.path.join(output_dir, f'broll_{scene_name}.mp4')
        print(f"  Generating {scene_name} b-roll...")
        print(f"    Prompt: {prompt[:80]}...")

        try:
            generate_single_clip(
                prompt,
                output_path,
                width=width,
                height=height,
                fps=fps,
            )
            results[scene_name] = output_path
        except Exception as e:
            print(f"  WARNING: {scene_name} b-roll failed: {e}")
            results[scene_name] = None

    successful = sum(1 for v in results.values() if v is not None)
    print(f"  B-roll complete: {successful}/{len(results)} clips generated")
    return results


if __name__ == "__main__":
    # Test with existing episode prompts
    script_path = os.path.join(BASE, 'data', 'ep1_v2', 'script.json')
    with open(script_path) as f:
        script_data = json.load(f)

    prompts = script_data.get('broll_prompts', {})
    if prompts:
        output = os.path.join(BASE, 'output', 'broll_test')
        results = generate_broll(prompts, output)
        print(f"\nResults: {json.dumps(results, indent=2)}")
    else:
        print("No b-roll prompts found in script data")
