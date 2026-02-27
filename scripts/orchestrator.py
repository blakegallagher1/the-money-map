"""
The Money Map — Full Pipeline Orchestrator

Usage:
    python orchestrator.py              # Full pipeline
    python orchestrator.py --step data  # Run from specific step
    python orchestrator.py --dry-run    # Show what would be produced
"""
import json
import os
import sys
import time
import argparse
from datetime import datetime

sys.path.insert(0, '/home/user/workspace/the-money-map')

BASE = '/home/user/workspace/the-money-map'
DATA_DIR = os.path.join(BASE, 'data')
OUTPUT_DIR = os.path.join(BASE, 'output')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")


def step_data():
    log("STEP 1: Fetching fresh economic data from FRED...")
    from scripts.data_ingestion import FREDClient
    client = FREDClient()
    result = client.fetch_all()
    
    out_path = os.path.join(DATA_DIR, 'latest_data.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    log(f"  Fetched {len(result['data'])} indicators")
    return result


def step_story():
    log("STEP 2: Discovering stories...")
    from scripts.story_discovery import build_story_package
    
    data_path = os.path.join(DATA_DIR, 'latest_data.json')
    pkg = build_story_package(data_path)
    
    log(f"  Top story: {pkg['primary']['name']}")
    log(f"  YoY change: {pkg['primary']['yoy_pct']:.1f}%")
    return pkg


def step_script(story_pkg):
    log("STEP 3: Writing script...")
    from scripts.script_writer import generate_script
    
    script_data = generate_script(story_pkg)
    
    out_path = os.path.join(DATA_DIR, 'latest_script.json')
    with open(out_path, 'w') as f:
        json.dump(script_data, f, indent=2)
    
    vo_path = os.path.join(DATA_DIR, 'voiceover_script.txt')
    with open(vo_path, 'w') as f:
        f.write(script_data['script'])
    
    log(f"  Title: {script_data['title']}")
    log(f"  Words: {script_data['word_count']}")
    return script_data


def step_voiceover():
    log("STEP 4: Voiceover generation...")
    vo_path = os.path.join(OUTPUT_DIR, 'voiceover.mp3')
    script_path = os.path.join(DATA_DIR, 'voiceover_script.txt')
    
    if os.path.exists(vo_path):
        age_hours = (time.time() - os.path.getmtime(vo_path)) / 3600
        if age_hours < 2:
            log(f"  Using existing voiceover ({age_hours:.1f}h old)")
            return vo_path
    
    log(f"  TTS needed for: {script_path}")
    return {"needs_tts": True, "script_path": script_path, "output_path": vo_path}


def step_render():
    log("STEP 5: Rendering video...")
    import subprocess
    result = subprocess.run(
        [sys.executable, os.path.join(BASE, 'scripts/render_pilot.py')],
        capture_output=True, text=True, timeout=600
    )
    
    if result.returncode != 0:
        log(f"  RENDER FAILED: {result.stderr[-500:]}")
        raise RuntimeError(f"Render failed: {result.stderr[-500:]}")
    
    video_path = os.path.join(OUTPUT_DIR, 'pilot_episode.mp4')
    log(f"  Video: {video_path}")
    return video_path


def step_thumbnail():
    log("STEP 6: Generating thumbnail...")
    from scripts.thumbnail_gen import generate_thumbnail
    
    script_path = os.path.join(DATA_DIR, 'latest_script.json')
    with open(script_path) as f:
        script_data = json.load(f)
    
    thumb_path = os.path.join(OUTPUT_DIR, 'thumbnail.png')
    generate_thumbnail(script_data, thumb_path)
    return thumb_path


def step_upload_prep():
    log("STEP 7: Preparing upload package...")
    from scripts.youtube_uploader import YouTubeUploader
    
    script_path = os.path.join(DATA_DIR, 'latest_script.json')
    video_path = os.path.join(OUTPUT_DIR, 'pilot_episode.mp4')
    thumb_path = os.path.join(OUTPUT_DIR, 'thumbnail.png')
    
    with open(script_path) as f:
        script_data = json.load(f)
    
    uploader = YouTubeUploader()
    package = uploader.prepare_upload_package(script_data, video_path, thumb_path)
    log(f"  Title: {package['title']}")
    return package


def run_full_pipeline(start_step='data'):
    log("=" * 60)
    log("THE MONEY MAP — EPISODE PIPELINE")
    log(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)
    
    steps = ['data', 'story', 'script', 'voiceover', 'render', 'thumbnail', 'upload']
    start_idx = steps.index(start_step) if start_step in steps else 0
    
    results = {}
    
    try:
        if start_idx <= 0: results['data'] = step_data()
        if start_idx <= 1: results['story'] = step_story()
        if start_idx <= 2: results['script'] = step_script(results.get('story') or step_story())
        if start_idx <= 3: results['voiceover'] = step_voiceover()
        if start_idx <= 4: results['render'] = step_render()
        if start_idx <= 5: results['thumbnail'] = step_thumbnail()
        if start_idx <= 6: results['upload'] = step_upload_prep()
        
        log("PIPELINE COMPLETE")
        
        run_log = {'timestamp': datetime.now().isoformat(), 'status': 'success', 'steps_run': steps[start_idx:]}
        with open(os.path.join(DATA_DIR, 'last_run.json'), 'w') as f:
            json.dump(run_log, f, indent=2, default=str)
        
        return results
        
    except Exception as e:
        log(f"PIPELINE ERROR: {e}")
        run_log = {'timestamp': datetime.now().isoformat(), 'status': 'error', 'error': str(e)}
        with open(os.path.join(DATA_DIR, 'last_run.json'), 'w') as f:
            json.dump(run_log, f, indent=2, default=str)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The Money Map Pipeline')
    parser.add_argument('--step', default='data',
                       choices=['data', 'story', 'script', 'voiceover', 'render', 'thumbnail', 'upload'])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    if not args.dry_run:
        run_full_pipeline(args.step)
