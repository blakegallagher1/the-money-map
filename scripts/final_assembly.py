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

# YouTube recommended upload bitrates (SDR) by resolution and frame-rate band.
# We choose the top of each recommended range for best quality.
YOUTUBE_BITRATE_TABLE = {
    4320: {"standard": "160M", "high": "240M"},  # 8K
    2160: {"standard": "45M", "high": "68M"},    # 4K
    1440: {"standard": "16M", "high": "24M"},    # 1440p
    1080: {"standard": "8M", "high": "12M"},     # 1080p
    720: {"standard": "5M", "high": "7500k"},    # 720p
    480: {"standard": "2500k", "high": "4M"},    # 480p
    360: {"standard": "1M", "high": "1500k"},    # 360p
}


def get_duration(path):
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())


def _probe_video_stream(path):
    """Read stream metadata (width/height/fps) via ffprobe."""
    result = subprocess.run([
        'ffprobe', '-v', 'quiet',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate',
        '-of', 'json', path
    ], capture_output=True, text=True, check=True)
    info = json.loads(result.stdout or "{}")
    stream = (info.get("streams") or [{}])[0]
    rate_raw = stream.get("r_frame_rate", "30/1")
    num, den = rate_raw.split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    return {
        "width": int(stream.get("width", 1920)),
        "height": int(stream.get("height", 1080)),
        "fps": fps,
    }


def _nearest_height_tier(height):
    """Map source height to nearest YouTube bitrate tier."""
    tiers = sorted(YOUTUBE_BITRATE_TABLE.keys())
    return min(tiers, key=lambda tier: abs(tier - height))


def _youtube_target_video_bitrate(height, fps):
    """Select bitrate using YouTube SDR recommendations by height and fps."""
    tier = _nearest_height_tier(height)
    band = "high" if fps > 30 else "standard"
    return YOUTUBE_BITRATE_TABLE[tier][band]


def _youtube_encode_args(height, fps):
    """Build ffmpeg args for YouTube ingest-optimized MP4 output."""
    video_bitrate = _youtube_target_video_bitrate(height, fps)
    target_fps = max(1, int(round(fps)))
    return [
        '-c:v', 'libx264',
        '-profile:v', 'high',
        '-pix_fmt', 'yuv420p',
        '-r', str(target_fps),
        '-b:v', video_bitrate,
        '-maxrate', video_bitrate,
        '-bufsize', _double_bitrate(video_bitrate),
        '-movflags', '+faststart',
        '-c:a', 'aac',
        '-ac', '2',
        '-ar', '48000',
        '-b:a', '384k',
    ]


def _double_bitrate(bitrate_str):
    """Return a 2x bitrate string preserving ffmpeg unit suffix."""
    match = ''.join(ch for ch in bitrate_str if ch.isdigit() or ch == '.')
    unit = ''.join(ch for ch in bitrate_str if not (ch.isdigit() or ch == '.'))
    value = float(match) if match else 0.0
    doubled = value * 2
    if unit.lower() == 'k':
        return f"{int(round(doubled))}k"
    return f"{int(round(doubled))}{unit}"


def normalize_broll(broll_path, output_path, width, height, fps, duration=None):
    """Re-encode b-roll to match target data-viz format."""
    cmd = [
        'ffmpeg', '-y',
    ]
    if duration is not None:
        cmd.extend(['-stream_loop', '-1'])
    cmd.extend([
        '-i', broll_path,
        '-vf', (
            f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2'
        ),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-r', str(fps), '-pix_fmt', 'yuv420p',
    ])
    if duration is not None:
        cmd.extend(['-t', f'{float(duration):.3f}'])
    cmd.extend([
        '-an',
        output_path
    ])
    subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True)


def _load_storyboard(storyboard):
    """Load a storyboard manifest from memory or disk."""
    if isinstance(storyboard, dict):
        return storyboard
    if storyboard and os.path.exists(str(storyboard)):
        with open(storyboard) as handle:
            return json.load(handle)
    return {}


def _extract_dataviz_segment(dataviz_path, output_path, start, duration, fps):
    """Cut a timed segment from the rendered data-viz master."""
    safe_duration = max(0.05, float(duration))
    subprocess.run([
        'ffmpeg', '-y', '-ss', f'{float(start):.3f}', '-i', dataviz_path,
        '-t', f'{safe_duration:.3f}', '-c:v', 'libx264', '-preset', 'medium',
        '-crf', '18', '-an', '-pix_fmt', 'yuv420p', '-r', str(fps), output_path
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
                              script_data=None, storyboard=None):
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
    stream_meta = _probe_video_stream(dataviz_path)
    target_width = stream_meta["width"]
    target_height = stream_meta["height"]
    target_fps = max(1, int(round(stream_meta["fps"])))
    storyboard_data = _load_storyboard(storyboard)
    print(f"  Audio duration: {audio_duration:.1f}s")
    print(f"  Target video profile: {target_width}x{target_height} @ {target_fps}fps")

    ordered_clips = []
    if storyboard_data.get("beats"):
        print(
            f"  Storyboard beats: {len(storyboard_data.get('beats', []))} "
            f"with {len(storyboard_data.get('broll_prompts', {}))} planned b-roll clips"
        )
        for index, beat in enumerate(storyboard_data.get("beats", [])):
            beat_id = beat.get("id", f"beat_{index:02d}")
            clip_path = os.path.join(work_dir, f'beat_{index:02d}_{beat_id}.mp4')
            if beat.get("visual_type") == "broll":
                asset_key = beat.get("asset_key")
                broll_src = broll_paths.get(asset_key) if broll_paths else None
                if broll_src and os.path.exists(broll_src):
                    print(f"  Normalizing storyboard b-roll: {asset_key}")
                    normalize_broll(
                        broll_src,
                        clip_path,
                        width=target_width,
                        height=target_height,
                        fps=target_fps,
                        duration=beat.get("duration_sec"),
                    )
                    ordered_clips.append(clip_path)
                    continue

            start = beat.get("dataviz_start_sec", beat.get("start_sec", 0.0))
            duration = float(beat.get("duration_sec", 0.0))
            _extract_dataviz_segment(dataviz_path, clip_path, start, duration, target_fps)
            ordered_clips.append(clip_path)
    else:
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
                normalize_broll(
                    broll_src,
                    norm_path,
                    width=target_width,
                    height=target_height,
                    fps=target_fps,
                )
                broll_normalized[scene_name] = norm_path

        # Extract segments from data-viz
        print("  Extracting data-viz segments...")
        seg_files = {}
        for name, (start, end) in segments.items():
            seg_path = os.path.join(work_dir, f'seg_{name}.mp4')
            duration = end - start
            _extract_dataviz_segment(dataviz_path, seg_path, start, duration, target_fps)
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

    # Mix audio + final YouTube ingest-optimized encode.
    print("  Mixing audio and exporting YouTube-optimized MP4...")
    stream_meta = _probe_video_stream(silent_path)
    encode_args = _youtube_encode_args(stream_meta["height"], stream_meta["fps"])
    target_video_bitrate = _youtube_target_video_bitrate(
        stream_meta["height"], stream_meta["fps"]
    )
    print(
        "  Export profile: "
        f"{stream_meta['width']}x{stream_meta['height']} @ {stream_meta['fps']:.2f}fps, "
        f"H.264 High, yuv420p, video {target_video_bitrate}, AAC 384k 48kHz stereo"
    )
    subprocess.run([
        'ffmpeg', '-y', '-i', silent_path, '-i', audio_path,
        '-map', '0:v:0', '-map', '1:a:0',
        *encode_args,
        '-shortest',
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
    vo_path = os.path.join(BASE, f'data/ep{ep_num}_v2/voiceover.wav')
    output_path = os.path.join(OUTPUT_DIR, f'ep{ep_num}_enhanced.mp4')

    return assemble_episode_dynamic(dataviz_path, broll_paths, vo_path, output_path)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ep = int(sys.argv[1])
        assemble_episode(ep)
    else:
        for ep in range(1, 6):
            assemble_episode(ep)
