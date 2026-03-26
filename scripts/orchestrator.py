"""
The Money Map — Full Pipeline Orchestrator (V2)

Enhanced pipeline with LLM scripting, background music, automated b-roll,
dynamic rendering, and YouTube API upload.

Usage:
    python orchestrator.py                    # Full pipeline
    python orchestrator.py --step data        # Run from specific step
    python orchestrator.py --dry-run          # Show what would be produced
    python orchestrator.py --script-mode llm  # Use LLM for scripts (default)
    python orchestrator.py --no-upload        # Skip YouTube upload
    python orchestrator.py --no-broll         # Skip b-roll generation
    python orchestrator.py --no-music         # Skip background music
"""
import json
import os
import sys
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
OUTPUT_DIR = os.path.join(BASE, 'output')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")


def step_data():
    log("STEP 1: Fetching fresh economic data from FRED...")
    from scripts.data_ingestion import fetch_fresh_data

    out_path = os.path.join(DATA_DIR, 'latest_data.json')
    result = fetch_fresh_data(output_path=out_path)

    log(f"  Fetched {result['series_count']} indicators")
    return result


def step_story():
    log("STEP 2: Discovering stories...")
    from scripts.story_discovery import build_story_package

    data_path = os.path.join(DATA_DIR, 'latest_data.json')
    pkg = build_story_package(data_path)

    log(f"  Top story: {pkg['primary']['name']}")
    log(f"  YoY change: {pkg['primary']['yoy_pct']:.1f}%")
    log(f"  Score: {pkg['primary']['score']}")
    return pkg


def step_research(story_pkg):
    log("STEP 2.5: Generating research dossier...")
    from scripts.topic_research import generate_research_dossier, save_dossier

    dossier = generate_research_dossier(story_pkg)
    save_dossier(story_pkg['primary']['key'], dossier)
    log(f"  Dossier summary: {dossier.get('summary', 'n/a')}")
    log(f"  Dossier confidence: {dossier.get('confidence', 'n/a')}")
    return dossier


def step_script(story_pkg, dossier=None, script_mode='llm'):
    log(f"STEP 3: Writing script (mode: {script_mode})...")

    if script_mode == 'llm':
        from scripts.llm_script_writer import generate_script
        script_data = generate_script(story_pkg, dossier=dossier)
    else:
        from scripts.enhanced_script_writer import generate_enhanced_script as generate_script
        script_data = generate_script(story_pkg)

    out_path = os.path.join(DATA_DIR, 'latest_script.json')
    with open(out_path, 'w') as f:
        json.dump(script_data, f, indent=2)

    vo_path = os.path.join(DATA_DIR, 'voiceover_script.txt')
    with open(vo_path, 'w') as f:
        f.write(script_data['script'])

    log(f"  Title: {script_data['title']}")
    log(f"  Words: {script_data['word_count']}")
    log(f"  Est. duration: ~{script_data['estimated_duration_sec']}s")
    return script_data


def step_broll(script_data):
    log("STEP 3.5: Generating b-roll clips via Luma...")
    from scripts.broll_generator import generate_broll

    broll_prompts = script_data.get('broll_prompts', {})
    if not broll_prompts:
        log("  No b-roll prompts found in script — skipping")
        return {}

    broll_dir = os.path.join(OUTPUT_DIR, 'broll_latest')
    results = generate_broll(broll_prompts, broll_dir)

    generated = sum(1 for v in results.values() if v is not None)
    log(f"  B-roll complete: {generated}/{len(results)} clips")
    return results


def step_voiceover():
    log("STEP 4: Voiceover generation...")
    vo_path = os.path.join(OUTPUT_DIR, 'voiceover.wav')
    script_path = os.path.join(DATA_DIR, 'voiceover_script.txt')

    if os.path.exists(vo_path):
        age_hours = (time.time() - os.path.getmtime(vo_path)) / 3600
        if age_hours < 2:
            log(f"  Using existing voiceover ({age_hours:.1f}h old)")
            return vo_path

    from scripts.tts_generator import generate_voiceover
    log("  Generating voiceover via OpenAI gpt-4o-mini-tts...")
    result_path = generate_voiceover(script_path=script_path, output_path=vo_path)
    log(f"  Voiceover saved: {result_path}")
    return result_path


def step_music(voiceover_path, script_data):
    log("STEP 4.5: Mixing background music...")
    from scripts.audio_mixer import process_audio

    mixed_path = process_audio(voiceover_path, script_data, OUTPUT_DIR)

    if mixed_path != voiceover_path:
        log(f"  Mixed audio saved: {mixed_path}")
    else:
        log("  No music available — using raw voiceover")

    return mixed_path


def step_render(script_data=None):
    log("STEP 5: Rendering video...")

    if script_data:
        # Use enhanced renderer with dynamic durations
        from scripts.enhanced_renderer import render_episode

        script_path = os.path.join(DATA_DIR, 'latest_script.json')
        ep_num = 'latest'
        video_path = render_episode(ep_num, script_path, OUTPUT_DIR)
    else:
        # Legacy render
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


def step_assemble(dataviz_path, broll_paths, audio_path, script_data):
    log("STEP 5.5: Final assembly (interleaving b-roll + audio)...")
    from scripts.final_assembly import assemble_episode_dynamic

    output_path = os.path.join(OUTPUT_DIR, 'latest_final.mp4')
    result = assemble_episode_dynamic(
        dataviz_path, broll_paths, audio_path, output_path,
        script_data=script_data
    )
    log(f"  Final video: {result}")
    return result


def step_thumbnail(script_data=None):
    log("STEP 6: Generating thumbnail...")
    from scripts.enhanced_thumbnail import generate_enhanced_thumbnail

    if script_data is None:
        script_path = os.path.join(DATA_DIR, 'latest_script.json')
        with open(script_path) as f:
            script_data = json.load(f)

    thumb_path = os.path.join(OUTPUT_DIR, 'thumbnail.png')
    generate_enhanced_thumbnail(script_data, thumb_path)
    log(f"  Thumbnail: {thumb_path}")
    return thumb_path


def step_quality_gate(script_data, results):
    log("STEP 7: Running quality gate...")
    from scripts.quality_gate import quality_gate_report_path, run_quality_gate
    from scripts.episode_tracker import load_history

    artifact_paths = {
        "voiceover_path": results.get('voiceover', os.path.join(OUTPUT_DIR, 'voiceover.wav')),
        "thumbnail_path": results.get('thumbnail', os.path.join(OUTPUT_DIR, 'thumbnail.png')),
        "final_video_path": results.get(
            'final_video', os.path.join(OUTPUT_DIR, 'latest_final.mp4')
        ),
        "script_json_path": os.path.join(DATA_DIR, 'latest_script.json'),
    }

    previous_entries = load_history()
    previous_titles = [
        entry.get('title', '')
        for entry in previous_entries
        if isinstance(entry, dict) and entry.get('title')
    ]

    result = run_quality_gate(
        script_data,
        artifact_paths,
        previous_titles=previous_titles,
    )

    issues = result.get('issues', [])
    for issue in issues:
        log(f"  issue[{issue.get('severity', 'n/a')}]: {issue.get('code')}: {issue.get('message')}")

    report_path = quality_gate_report_path(result, DATA_DIR)
    log(f"  Quality gate report written: {report_path}")

    if result.get("status") != "pass":
        raise RuntimeError(f"Quality gate failed with issues: {issues}")

    return result


def step_upload(script_data, video_path, thumbnail_path):
    log("STEP 8: Uploading to YouTube...")
    from scripts.youtube_api_uploader import upload_video

    result = upload_video(
        video_path=video_path,
        title=script_data['title'],
        description=script_data.get('description', ''),
        tags=script_data.get('tags', []),
        thumbnail_path=thumbnail_path,
        privacy="public",
    )

    log(f"  Upload complete: {result['video_url']}")
    return result


def step_upload_prep(script_data=None):
    """Legacy upload prep — just generates metadata package."""
    log("STEP 7: Preparing upload package (manual upload)...")
    from scripts.youtube_uploader import YouTubeUploader

    if script_data is None:
        script_path = os.path.join(DATA_DIR, 'latest_script.json')
        with open(script_path) as f:
            script_data = json.load(f)

    video_path = os.path.join(OUTPUT_DIR, 'latest_final.mp4')
    thumb_path = os.path.join(OUTPUT_DIR, 'thumbnail.png')

    uploader = YouTubeUploader()
    package = uploader.prepare_upload_package(script_data, video_path, thumb_path)
    log(f"  Title: {package['title']}")
    return package


def step_record_episode(script_data, video_url=None):
    log("STEP 8: Recording episode in history...")
    from scripts.episode_tracker import record_episode

    primary = script_data.get('primary_metric', {})
    record_episode(
        metric_key=primary.get('key', 'unknown'),
        title=script_data.get('title', 'Untitled'),
        score=primary.get('score', 0),
        video_url=video_url,
    )
    log("  Episode recorded in history")


def run_full_pipeline(start_step='data', script_mode='llm',
                      no_upload=False, no_broll=False, no_music=False):
    log("=" * 60)
    log("THE MONEY MAP — EPISODE PIPELINE V2")
    log(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Options: script_mode={script_mode}, broll={'on' if not no_broll else 'off'}, "
        f"music={'on' if not no_music else 'off'}, upload={'auto' if not no_upload else 'manual'}")
    log("=" * 60)

    steps = ['data', 'story', 'research', 'script', 'broll', 'voiceover', 'music',
             'render', 'assemble', 'thumbnail', 'quality_gate', 'upload', 'record']
    start_idx = steps.index(start_step) if start_step in steps else 0

    results = {}

    try:
        # Step 1: Data ingestion
        if start_idx <= 0:
            results['data'] = step_data()

        # Step 2: Story discovery
        if start_idx <= 1:
            results['story'] = step_story()

        # Step 2.5: Research dossier
        dossier = None
        if start_idx <= 2:
            story = results.get('story') or step_story()
            dossier = step_research(story)

        # Step 3: Script writing
        if start_idx <= 3 and start_idx != 2:
            story = results.get('story') or step_story()
            dossier = dossier or step_research(story)
            results['script'] = step_script(story, dossier=dossier, script_mode=script_mode)

        script_data = results.get('script')
        if script_data is None:
            script_path = os.path.join(DATA_DIR, 'latest_script.json')
            with open(script_path) as f:
                script_data = json.load(f)

        # Step 3.5: B-roll generation (optional)
        if start_idx <= 4 and not no_broll:
            try:
                results['broll'] = step_broll(script_data)
            except Exception as e:
                log(f"  B-roll generation failed: {e} — continuing without b-roll")
                results['broll'] = {}
        else:
            results['broll'] = {}

        # Step 4: Voiceover
        if start_idx <= 5:
            results['voiceover'] = step_voiceover()

        # Step 4.5: Background music (optional)
        vo_path = results.get('voiceover', os.path.join(OUTPUT_DIR, 'voiceover.wav'))
        if start_idx <= 6 and not no_music:
            try:
                results['audio'] = step_music(vo_path, script_data)
            except Exception as e:
                log(f"  Music mixing failed: {e} — using raw voiceover")
                results['audio'] = vo_path
        else:
            results['audio'] = vo_path

        # Step 5: Render data-viz
        if start_idx <= 7:
            results['render'] = step_render(script_data=script_data)

        # Step 5.5: Final assembly
        if start_idx <= 8:
            dataviz_path = results.get('render', os.path.join(OUTPUT_DIR, 'latest_v2_final.mp4'))
            broll_paths = results.get('broll', {})
            audio_path = results.get('audio', vo_path)
            results['final_video'] = step_assemble(
                dataviz_path, broll_paths, audio_path, script_data
            )

        # Step 6: Thumbnail
        if start_idx <= 9:
            results['thumbnail'] = step_thumbnail(script_data)

        # Step 7: Quality gate
        if start_idx <= 10:
            results['quality_gate'] = step_quality_gate(script_data, results)

        # Step 8: Upload
        video_url = None
        if start_idx <= 11:
            final_video = results.get('final_video', os.path.join(OUTPUT_DIR, 'latest_final.mp4'))
            thumb_path = results.get('thumbnail', os.path.join(OUTPUT_DIR, 'thumbnail.png'))

            if not no_upload:
                try:
                    upload_result = step_upload(script_data, final_video, thumb_path)
                    video_url = upload_result.get('video_url')
                except Exception as e:
                    log(f"  YouTube upload failed: {e}")
                    log("  Falling back to manual upload prep...")
                    step_upload_prep(script_data)
            else:
                step_upload_prep(script_data)

        # Step 8: Record in episode history
        if start_idx <= 12:
            step_record_episode(script_data, video_url=video_url)

        log("=" * 60)
        log("PIPELINE COMPLETE")
        log("=" * 60)

        run_log = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'steps_run': steps[start_idx:],
            'script_mode': script_mode,
            'title': script_data.get('title', ''),
            'word_count': script_data.get('word_count', 0),
            'video_url': video_url,
        }
        with open(os.path.join(DATA_DIR, 'last_run.json'), 'w') as f:
            json.dump(run_log, f, indent=2, default=str)

        return results

    except Exception as e:
        log(f"PIPELINE ERROR: {e}")
        import traceback
        traceback.print_exc()
        run_log = {'timestamp': datetime.now().isoformat(), 'status': 'error', 'error': str(e)}
        with open(os.path.join(DATA_DIR, 'last_run.json'), 'w') as f:
            json.dump(run_log, f, indent=2, default=str)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The Money Map Pipeline V2')
    parser.add_argument('--step', default='data',
                       choices=['data', 'story', 'research', 'script', 'broll', 'voiceover',
                                'music', 'render', 'assemble', 'thumbnail', 'quality_gate',
                                'upload', 'record'])
    parser.add_argument('--script-mode', default='llm', choices=['llm', 'template'],
                       help='Script generation mode: llm (GPT-5.2) or template')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be produced without running')
    parser.add_argument('--no-upload', action='store_true',
                       help='Skip YouTube upload (prepare metadata only)')
    parser.add_argument('--no-broll', action='store_true',
                       help='Skip b-roll generation')
    parser.add_argument('--no-music', action='store_true',
                       help='Skip background music mixing')
    args = parser.parse_args()

    if args.dry_run:
        log("DRY RUN — showing pipeline configuration")
        log(f"  Script mode: {args.script_mode}")
        log(f"  B-roll: {'enabled' if not args.no_broll else 'disabled'}")
        log(f"  Music: {'enabled' if not args.no_music else 'disabled'}")
        log(f"  Upload: {'auto' if not args.no_upload else 'manual'}")
        log(f"  Start step: {args.step}")
    else:
        run_full_pipeline(
            start_step=args.step,
            script_mode=args.script_mode,
            no_upload=args.no_upload,
            no_broll=args.no_broll,
            no_music=args.no_music,
        )
