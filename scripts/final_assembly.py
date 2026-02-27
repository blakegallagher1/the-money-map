"""
Final Assembly Script for The Money Map Enhanced Episodes
Interleaves data-viz scenes with AI b-roll clips and layers voiceover.

Structure per episode:
  1. Cold Open (6s) — data counter
  2. B-roll Hook (4s) — AI cinematic footage
  3. Hook + Title (18s) — title card + stat reveal
  4. Chart Walk (55s) — animated chart
  5. B-roll Context (4s) — AI cinematic footage
  6. Context + Connected Data (40s) — multi-metric cards
  7. B-roll Insight (4s) — AI cinematic footage
  8. Insight (35s) — key takeaway
  9. Close (12s) — subscribe CTA
  Total visual: ~178s → trimmed to voiceover length
"""
import subprocess
import os
import sys
import json

BASE = '/home/user/workspace/the-money-map'
BROLL_DIR = f'{BASE}/assets/broll_video'
OUTPUT_DIR = f'{BASE}/output'

EPISODE_KEYS = [
    'personal_savings_rate',
    'mortgage_rate_30yr',
    'national_debt',
    'gas_price',
    'gdp_growth'
]


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
        '-an',  # Remove audio from b-roll (we'll add our own voiceover)
        output_path
    ], capture_output=True, text=True, timeout=120, check=True)


def assemble_episode(ep_num):
    key = EPISODE_KEYS[ep_num - 1]
    print(f"\n{'='*60}")
    print(f"ASSEMBLING EPISODE {ep_num}: {key}")
    print(f"{'='*60}")
    
    work_dir = os.path.join(OUTPUT_DIR, f'ep{ep_num}_v2_assembly')
    os.makedirs(work_dir, exist_ok=True)
    
    # Data-viz video (already rendered)
    dataviz_path = os.path.join(OUTPUT_DIR, f'ep{ep_num}_v2_final.mp4')
    if not os.path.exists(dataviz_path):
        print(f"  ERROR: {dataviz_path} not found!")
        return None
    
    # B-roll clips
    broll_hook = os.path.join(BROLL_DIR, f'broll_ep{ep_num}_hook_vid.mp4')
    broll_context = os.path.join(BROLL_DIR, f'broll_ep{ep_num}_context_vid.mp4')
    broll_insight = os.path.join(BROLL_DIR, f'broll_ep{ep_num}_insight_vid.mp4')
    
    # Voiceover
    vo_path = os.path.join(BASE, f'data/ep{ep_num}_v2/voiceover.mp3')
    vo_duration = get_duration(vo_path)
    print(f"  Voiceover duration: {vo_duration:.1f}s")
    
    # Step 1: Split the data-viz video into segments
    # The data-viz has these scenes: cold_open(6s) + hook(18s) + chart(55s) + context(40s) + insight(35s) + close(12s) = 166s
    # We'll extract key segments and interleave b-roll
    
    # Normalize b-roll clips to match format
    print("  Normalizing b-roll clips...")
    broll_hook_n = os.path.join(work_dir, 'broll_hook.mp4')
    broll_context_n = os.path.join(work_dir, 'broll_context.mp4')
    broll_insight_n = os.path.join(work_dir, 'broll_insight.mp4')
    
    normalize_broll(broll_hook, broll_hook_n)
    normalize_broll(broll_context, broll_context_n)
    normalize_broll(broll_insight, broll_insight_n)
    
    # Step 2: Extract segments from data-viz
    print("  Extracting data-viz segments...")
    segments = {
        'cold_open': (0, 6),           # 0-6s
        'hook_title': (6, 24),         # 6-24s (18s)
        'chart': (24, 79),             # 24-79s (55s)
        'context': (79, 119),          # 79-119s (40s)
        'insight': (119, 154),         # 119-154s (35s)
        'close': (154, 166),           # 154-166s (12s)
    }
    
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
    
    # Step 3: Build concat list with b-roll interleaved
    # Order: cold_open → broll_hook → hook_title → chart → broll_context → context → broll_insight → insight → close
    print("  Building interleaved timeline...")
    concat_list = os.path.join(work_dir, 'concat.txt')
    ordered_clips = [
        seg_files['cold_open'],     # 6s
        broll_hook_n,                # 4s  
        seg_files['hook_title'],     # 18s
        seg_files['chart'],          # 55s
        broll_context_n,             # 4s
        seg_files['context'],        # 40s
        broll_insight_n,             # 4s
        seg_files['insight'],        # 35s
        seg_files['close'],          # 12s
    ]
    # Total: ~178s
    
    with open(concat_list, 'w') as f:
        for clip in ordered_clips:
            f.write(f"file '{clip}'\n")
    
    # Step 4: Concatenate all segments
    silent_path = os.path.join(work_dir, 'silent_interleaved.mp4')
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,
        '-c', 'copy', silent_path
    ], capture_output=True, text=True, timeout=120, check=True)
    
    silent_dur = get_duration(silent_path)
    print(f"  Interleaved video duration: {silent_dur:.1f}s")
    
    # Step 5: Mix voiceover on top
    final_path = os.path.join(OUTPUT_DIR, f'ep{ep_num}_enhanced.mp4')
    print("  Mixing voiceover...")
    subprocess.run([
        'ffmpeg', '-y', '-i', silent_path, '-i', vo_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-map', '0:v:0', '-map', '1:a:0', '-shortest',
        final_path
    ], capture_output=True, text=True, timeout=120, check=True)
    
    final_dur = get_duration(final_path)
    final_size = os.path.getsize(final_path) / (1024 * 1024)
    print(f"\n  FINAL: {final_path}")
    print(f"  Duration: {final_dur:.1f}s ({int(final_dur//60)}m{int(final_dur%60)}s)")
    print(f"  Size: {final_size:.1f} MB")
    
    # Cleanup work dir
    import shutil
    shutil.rmtree(work_dir)
    
    return final_path


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ep = int(sys.argv[1])
        assemble_episode(ep)
    else:
        for ep in range(1, 6):
            assemble_episode(ep)
