"""
Final Assembly Script for The Money Map Enhanced Episodes
Interleaves data-viz scenes with AI b-roll clips and layers voiceover + music.

Supports both legacy fixed-duration episodes and new dynamic-duration episodes.
Uses mixed audio (voiceover + background music) when available.
"""
import subprocess
import os
import sys
import json
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BROLL_DIR = os.path.join(BASE, 'assets', 'broll_video')
OUTPUT_DIR = os.path.join(BASE, 'output')


def get_duration(path):
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())


def normalize_broll(broll_path, output_path):
    """Re-encode b-roll to match data-viz format (30fps, yuv420p, 1920x1080)."""
    subprocess.run([
        'ffmpeg', '-y', '-i', broll_path,
        '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-r', '30', '-pix_fmt', 'yuv420p',
        '-an',
        output_path
    ], capture_output=True, text=True, timeout=120, check=True)


def _calculate_segments(script_data):
    """Calculate segment timestamps from script data.

    Uses dynamic scene durations from calculate_scene_durations.
    """
    from scripts.enhanced_renderer import calculate_scene_durations
    durations = calculate_scene_durations(script_data)

    # Build cumulative timestamps
    scene_order = ['cold_open', 'hook', 'chart_walk', 'context', 'insight', 'close']
    segments = {}
    cursor = 0
    for scene in scene_order:
        dur = durations.get(scene, 10)
        segments[scene] = (cursor, cursor + dur)
        cursor += dur

    return segments


def assemble_episode_dynamic(dataviz_path, broll_paths, audio_path, output_path,
                              script_data=None):
    """Assemble final video with dynamic segment durations.

    Args:
        dataviz_path: Path to rendered data-viz video (silent)
        broll_paths: dict with keys 'hook', 'context', 'insight' -> file paths (or None)
        audio_path: Path to audio file (mixed voiceover+music or raw voiceover)
        output_path: Path for final output video
        script_data: Script JSON for calculating dynamic segment durations
    """
    print(f"\n{'='*60}")
    print(f"ASSEMBLING FINAL VIDEO")
    print(f"{'='*60}")

    work_dir = output_path + '_assembly'
    os.makedirs(work_dir, exist_ok=True)

    if not os.path.exists(dataviz_path):
        print(f"  ERROR: {dataviz_path} not found!")
        return None

    audio_duration = get_duration(audio_path)
    print(f"  Audio duration: {audio_duration:.1f}s")

    # Calculate segments from script data or use defaults
    if script_data:
        segments = _calculate_segments(script_data)
    else:
        segments = {
            'cold_open': (0, 6),
            'hook': (6, 24),
            'chart_walk': (24, 79),
            'context': (79, 119),
            'insight': (119, 154),
            'close': (154, 166),
        }

    print(f"  Scene segments: {segments}")

    # Normalize available b-roll clips
    broll_normalized = {}
    for scene_name in ['hook', 'context', 'insight']:
        broll_src = broll_paths.get(scene_name) if broll_paths else None
        if broll_src and os.path.exists(broll_src):
            norm_path = os.path.join(work_dir, f'broll_{scene_name}.mp4')
            print(f"  Normalizing b-roll: {scene_name}")
            normalize_broll(broll_src, norm_path)
            broll_normalized[scene_name] = norm_path

    # Extract segments from data-viz
    print("  Extracting data-viz segments...")
    seg_files = {}
    for name, (start, end) in segments.items():
        seg_path = os.path.join(work_dir, f'seg_{name}.mp4')
        duration = end - start
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(start), '-i', dataviz_path,
            '-t', str(duration), '-c:v', 'libx264', '-preset', 'fast',
            '-crf', '23', '-an', '-pix_fmt', 'yuv420p', seg_path
        ], capture_output=True, text=True, timeout=120, check=True)
        seg_files[name] = seg_path

    # Build interleaved timeline
    print("  Building interleaved timeline...")
    ordered_clips = [seg_files['cold_open']]

    if 'hook' in broll_normalized:
        ordered_clips.append(broll_normalized['hook'])
    ordered_clips.append(seg_files['hook'])
    ordered_clips.append(seg_files['chart_walk'])

    if 'context' in broll_normalized:
        ordered_clips.append(broll_normalized['context'])
    ordered_clips.append(seg_files['context'])

    if 'insight' in broll_normalized:
        ordered_clips.append(broll_normalized['insight'])
    ordered_clips.append(seg_files['insight'])
    ordered_clips.append(seg_files['close'])

    concat_list = os.path.join(work_dir, 'concat.txt')
    with open(concat_list, 'w') as f:
        for clip in ordered_clips:
            f.write(f"file '{clip}'\n")

    # Concatenate all segments
    silent_path = os.path.join(work_dir, 'silent_interleaved.mp4')
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,
        '-c', 'copy', silent_path
    ], capture_output=True, text=True, timeout=120, check=True)

    silent_dur = get_duration(silent_path)
    print(f"  Interleaved video duration: {silent_dur:.1f}s")

    # Mix audio on top
    print("  Mixing audio...")
    subprocess.run([
        'ffmpeg', '-y', '-i', silent_path, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-map', '0:v:0', '-map', '1:a:0', '-shortest',
        output_path
    ], capture_output=True, text=True, timeout=120, check=True)

    final_dur = get_duration(output_path)
    final_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n  FINAL: {output_path}")
    print(f"  Duration: {final_dur:.1f}s ({int(final_dur//60)}m{int(final_dur%60)}s)")
    print(f"  Size: {final_size:.1f} MB")

    # Cleanup work dir
    shutil.rmtree(work_dir)
    return output_path


# Legacy function for backward compatibility with existing episodes
def assemble_episode(ep_num):
    """Assemble a legacy episode by number (episodes 1-5)."""
    episode_keys = [
        'personal_savings_rate', 'mortgage_rate_30yr',
        'national_debt', 'gas_price', 'gdp_growth'
    ]

    dataviz_path = os.path.join(OUTPUT_DIR, f'ep{ep_num}_v2_final.mp4')
    broll_paths = {
        'hook': os.path.join(BROLL_DIR, f'broll_ep{ep_num}_hook_vid.mp4'),
        'context': os.path.join(BROLL_DIR, f'broll_ep{ep_num}_context_vid.mp4'),
        'insight': os.path.join(BROLL_DIR, f'broll_ep{ep_num}_insight_vid.mp4'),
    }
    vo_path = os.path.join(BASE, f'data/ep{ep_num}_v2/voiceover.mp3')
    output_path = os.path.join(OUTPUT_DIR, f'ep{ep_num}_enhanced.mp4')

    return assemble_episode_dynamic(dataviz_path, broll_paths, vo_path, output_path)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ep = int(sys.argv[1])
        assemble_episode(ep)
    else:
        for ep in range(1, 6):
            assemble_episode(ep)
