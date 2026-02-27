"""
Generalized episode renderer for The Money Map.
Takes a story key and produces a full video + voiceover script + thumbnail.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import json
import os
import subprocess
from datetime import datetime
import sys

sys.path.insert(0, '/home/user/workspace/the-money-map')
from config.settings import COLORS, FRED_SERIES
from scripts.data_ingestion import FREDClient
from scripts.story_discovery import analyze_data, find_related_series
from scripts.script_writer import generate_script
from scripts.thumbnail_gen import generate_thumbnail

plt.rcParams.update({
    'figure.facecolor': COLORS['bg_dark'], 'axes.facecolor': COLORS['bg_dark'],
    'axes.edgecolor': COLORS['border'], 'text.color': COLORS['text_primary'],
    'axes.labelcolor': COLORS['text_secondary'], 'xtick.color': COLORS['text_muted'],
    'ytick.color': COLORS['text_muted'], 'grid.color': COLORS['grid'], 'grid.alpha': 0.3,
    'font.family': 'sans-serif', 'font.size': 14, 'axes.grid': True,
    'grid.linestyle': '--', 'axes.spines.top': False, 'axes.spines.right': False,
})

BASE = '/home/user/workspace/the-money-map'
RENDER_FPS = 5


def f2v(frame_dir, output_path):
    """Convert frames to video."""
    subprocess.run(["ffmpeg", "-y", "-framerate", str(RENDER_FPS), "-i",
        os.path.join(frame_dir, "frame_%04d.png"), "-c:v", "libx264", "-preset", "fast",
        "-crf", "23", "-r", "30", "-pix_fmt", "yuv420p", output_path],
        capture_output=True, text=True, timeout=300, check=True)


def format_value(val, unit):
    """Format a value with its unit for display."""
    if unit == '%':
        return f"{val:.1f}%"
    elif unit in ('$', '$/gallon'):
        return f"${val:,.2f}"
    elif unit == 'millions $':
        if val >= 1e6:
            return f"${val/1e6:.1f}T"
        elif val >= 1000:
            return f"${val/1000:,.0f}B"
        else:
            return f"${val:,.0f}M"
    elif unit == 'billions $':
        if val >= 1000:
            return f"${val/1000:.1f}T"
        else:
            return f"${val:,.0f}B"
    elif unit == 'index':
        return f"{val:,.1f}"
    elif unit == 'thousands':
        if val >= 1000:
            return f"{val/1000:,.1f}M"
        else:
            return f"{val:,.0f}K"
    else:
        return f"{val:,.1f}"


def render_episode(story, related, script_data, episode_num):
    """Render a full episode video for the given story."""
    ep_dir = os.path.join(BASE, 'output', f'ep{episode_num}')
    os.makedirs(ep_dir, exist_ok=True)
    
    # Fetch historical observations for chart
    client = FREDClient()
    series = client.get_series(story['series_id'])
    observations = series['observations']
    
    val = story['latest_value']
    unit = story['unit']
    display_val = format_value(val, unit)
    is_neg = story['yoy_pct'] < 0
    neg_accent = COLORS['negative'] if is_neg else COLORS['positive']
    chart_accent = COLORS['negative'] if is_neg else COLORS['accent_teal']
    arrow = "▼" if is_neg else "▲"
    
    # ─── SCENE 1: TITLE (25 frames = 5s) ───
    print(f"  Scene 1: Title...")
    d = os.path.join(ep_dir, "f_title"); os.makedirs(d, exist_ok=True)
    title = script_data['title']
    for i in range(25):
        p = i / 24
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ga = 0.06 * min(p * 3, 1.0)
        for x in np.arange(0, 1.1, 0.05):
            ax.axvline(x, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
        for y in np.arange(0, 1.1, 0.05):
            ax.axhline(y, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
        ta = min(p * 2.5, 1.0)
        if p > 0.1:
            yo = max(0, 0.02 * (1 - min((p - 0.1) * 5, 1.0)))
            if len(title) > 35 and '—' in title:
                parts = title.split('—')
                ax.text(0.5, 0.58 + yo, parts[0].strip(), fontsize=38, fontweight='bold',
                       ha='center', va='center', color=COLORS['text_primary'], alpha=ta,
                       wrap=True)
                ax.text(0.5, 0.45 + yo, '— ' + parts[1].strip(), fontsize=28,
                       ha='center', va='center', color=COLORS['accent_coral'], alpha=ta,
                       wrap=True)
            else:
                ax.text(0.5, 0.55 + yo, title, fontsize=36, fontweight='bold',
                       ha='center', va='center', color=COLORS['text_primary'], alpha=ta,
                       wrap=True)
        if p > 0.35:
            ax.text(0.5, 0.34, f"Data as of {story['latest_date']}", fontsize=18,
                   ha='center', color=COLORS['accent_teal'], alpha=min((p - 0.35) * 3, 1.0))
        if p > 0.2:
            lp2 = min((p - 0.2) * 2.5, 1.0); lw2 = 0.3 * lp2
            ax.plot([0.5 - lw2/2, 0.5 + lw2/2], [0.29, 0.29], color=COLORS['accent_teal'], lw=2, alpha=0.8)
        if p > 0.5:
            ax.text(0.95, 0.05, "THE MONEY MAP", fontsize=12, ha='right',
                   color=COLORS['text_muted'], alpha=min((p - 0.5) * 3, 1.0), fontweight='bold', style='italic')
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    f2v(d, os.path.join(ep_dir, "scene_01.mp4"))
    
    # ─── SCENE 2: STAT CALLOUT (75 frames = 15s) ───
    print(f"  Scene 2: Stat Callout...")
    d = os.path.join(ep_dir, "f_callout"); os.makedirs(d, exist_ok=True)
    for i in range(75):
        p = i / 74
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ga = 0.04 + 0.012 * np.sin(p * 3 * np.pi)
        for x in np.arange(0, 1.1, 0.04):
            ax.axvline(x, color=neg_accent, alpha=ga, lw=0.2)
        for y in np.arange(0, 1.1, 0.04):
            ax.axhline(y, color=neg_accent, alpha=ga, lw=0.2)
        if p > 0.05:
            na = min((p - 0.05) * 3, 1.0)
            sc = 1.0 + max(0, 0.12 * (1 - min((p - 0.05) * 4, 1.0)))
            ax.text(0.5, 0.55, display_val, fontsize=int(72 * sc), fontweight='bold',
                   ha='center', va='center', color=COLORS['text_primary'], alpha=na)
        if p > 0.2:
            ax.text(0.5, 0.38, story['name'].upper(), fontsize=22, ha='center',
                   color=COLORS['text_secondary'], alpha=min((p - 0.2) * 3, 1.0), fontweight='bold')
        if p > 0.35:
            ax.text(0.5, 0.27, f"{arrow} {abs(story['yoy_pct']):.1f}% Year Over Year",
                   fontsize=24, ha='center', color=neg_accent, alpha=min((p - 0.35) * 3, 1.0), fontweight='bold')
        ax.text(0.95, 0.04, "THE MONEY MAP", fontsize=11, ha='right',
               color=COLORS['text_muted'], alpha=0.4, fontweight='bold')
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    f2v(d, os.path.join(ep_dir, "scene_02.mp4"))
    
    # ─── SCENE 3: MAIN CHART (250 frames = 50s) ───
    print(f"  Scene 3: Main Chart...")
    d = os.path.join(ep_dir, "f_chart"); os.makedirs(d, exist_ok=True)
    dates_raw = [datetime.strptime(o['date'], '%Y-%m-%d') for o in observations][::-1]
    vals_raw = [o['value'] for o in observations][::-1]
    n = len(vals_raw)
    if n < 2:
        print("    WARNING: Not enough data points for chart, using placeholder")
        n = 2
        vals_raw = [val * 0.9, val]
        dates_raw = [datetime(2024, 1, 1), datetime(2025, 12, 1)]
    ymin = min(vals_raw) * 0.92; ymax = max(vals_raw) * 1.08
    
    for i in range(250):
        p = i / 249
        show = max(2, int(p * n * 1.05)); show = min(show, n)
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ax.text(0.02, 1.08, story['name'].upper(), transform=ax.transAxes,
               fontsize=26, fontweight='bold', color=COLORS['text_primary'], va='top')
        if p > 0.15:
            lv = vals_raw[show - 1]
            vs2 = format_value(lv, unit)
            ax.text(0.02, 1.02, f"Latest: {vs2}", transform=ax.transAxes,
                   fontsize=17, color=chart_accent, va='top')
        xd = dates_raw[:show]; yd = vals_raw[:show]
        ax.plot(xd, yd, color=chart_accent, lw=2.5, solid_capstyle='round', zorder=3)
        ax.fill_between(xd, ymin, yd, alpha=0.06, color=chart_accent)
        if len(xd) > 0:
            ax.scatter([xd[-1]], [yd[-1]], color=chart_accent, s=60, zorder=5, edgecolors='white', linewidths=1.5)
            ax.scatter([xd[-1]], [yd[-1]], color=chart_accent, s=180, alpha=0.15, zorder=4)
        ax.set_xlim(dates_raw[0], dates_raw[-1]); ax.set_ylim(ymin, ymax)
        if unit == '%':
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
        elif unit in ('$', '$/gallon'):
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.2f'))
        ax.text(0.99, -0.07, "Source: FRED (Federal Reserve Economic Data)", transform=ax.transAxes,
               fontsize=10, color=COLORS['text_muted'], ha='right', va='top')
        ax.text(0.01, -0.07, "THE MONEY MAP", transform=ax.transAxes, fontsize=10,
               color=COLORS['text_muted'], ha='left', va='top', fontweight='bold')
        plt.tight_layout(pad=2)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
        if i % 50 == 0:
            print(f"    frame {i}/250")
    f2v(d, os.path.join(ep_dir, "scene_03.mp4"))
    
    # ─── SCENE 4: COMPARISON (125 frames = 25s) ───
    print(f"  Scene 4: Comparison...")
    d = os.path.join(ep_dir, "f_comp"); os.makedirs(d, exist_ok=True)
    comp = [{"name": story['name'], "latest_value": story['latest_value'],
             "unit": story['unit'], "yoy_pct": story['yoy_pct']}]
    for r in related[:3]:
        comp.append(r)
    acols = [COLORS['accent_teal'], COLORS['accent_blue'], COLORS['accent_coral'], COLORS['accent_amber']]
    
    for i in range(125):
        p = i / 124
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(COLORS['bg_dark']); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        ax.text(0.5, 0.92, "THE CONNECTED INDICATORS", fontsize=28, fontweight='bold',
               ha='center', color=COLORS['text_primary'], alpha=min(p * 3, 1.0), transform=ax.transAxes)
        for j, m in enumerate(comp[:4]):
            cp2 = max(0, min((p - 0.12 * j - 0.15) * 3, 1.0))
            if cp2 <= 0:
                continue
            yp = 0.72 - j * 0.17; col = acols[j % 4]
            ax.text(0.08, yp + 0.02, m['name'], fontsize=19, fontweight='bold',
                   color=COLORS['text_primary'], alpha=cp2, transform=ax.transAxes, va='center')
            v2 = m['latest_value']; u2 = m.get('unit', '')
            vs3 = format_value(v2, u2)
            ax.text(0.92, yp + 0.02, vs3, fontsize=21, fontweight='bold', color=col,
                   alpha=cp2, transform=ax.transAxes, ha='right', va='center')
            yoy2 = m.get('yoy_pct')
            if yoy2 is not None:
                bc = COLORS['positive'] if yoy2 > 0 else COLORS['negative']
                ar2 = "▲" if yoy2 > 0 else "▼"
                ax.text(0.92, yp - 0.025, f"{ar2} {abs(yoy2):.1f}% YoY", fontsize=13,
                       color=bc, alpha=cp2 * 0.85, transform=ax.transAxes, ha='right', va='center')
            ax.plot([0.08, 0.92], [yp - 0.055, yp - 0.055], color=COLORS['border'],
                   lw=0.5, alpha=cp2 * 0.4, transform=ax.transAxes)
        ax.text(0.5, 0.05, "Source: FRED  |  THE MONEY MAP", fontsize=11,
               ha='center', color=COLORS['text_muted'], alpha=min(p * 2, 0.6), transform=ax.transAxes)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    f2v(d, os.path.join(ep_dir, "scene_04.mp4"))
    
    # ─── SCENE 5: CLOSING (65 frames = 13s) ───
    print(f"  Scene 5: Closing...")
    d = os.path.join(ep_dir, "f_close"); os.makedirs(d, exist_ok=True)
    for i in range(65):
        p = i / 64
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ga = 0.05 * min(p * 2, 1.0)
        for x in np.arange(0, 1.1, 0.05):
            ax.axvline(x, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
        for y in np.arange(0, 1.1, 0.05):
            ax.axhline(y, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
        ax.text(0.5, 0.58, "THE MONEY MAP", fontsize=52, fontweight='bold',
               ha='center', color=COLORS['text_primary'], alpha=min(p * 2, 1.0))
        if p > 0.2:
            ax.text(0.5, 0.44, "Subscribe for weekly data-driven analysis", fontsize=20,
                   ha='center', color=COLORS['accent_teal'], alpha=min((p - 0.2) * 2.5, 1.0))
        if p > 0.3:
            lp3 = min((p - 0.3) * 2, 1.0); lw3 = 0.25 * lp3
            ax.plot([0.5 - lw3/2, 0.5 + lw3/2], [0.38, 0.38], color=COLORS['accent_teal'], lw=2, alpha=0.7)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    f2v(d, os.path.join(ep_dir, "scene_05.mp4"))
    
    # ─── ASSEMBLE ───
    print(f"  Assembling...")
    with open(os.path.join(ep_dir, "concat.txt"), 'w') as f:
        for s in range(1, 6):
            f.write(f"file 'scene_{s:02d}.mp4'\n")
    
    silent = os.path.join(ep_dir, "silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
        os.path.join(ep_dir, "concat.txt"), "-c", "copy", silent],
        capture_output=True, text=True, timeout=120, check=True, cwd=ep_dir)
    
    return ep_dir, silent


def produce_episode(story_key, episode_num, all_data):
    """Full production: script → render → assemble with voiceover + thumbnail.
    
    Returns dict with all output paths and metadata. 
    Voiceover must be added externally via TTS tool.
    """
    # Find the story in scored data
    analysis = analyze_data(os.path.join(BASE, 'data/latest_data.json'))
    story = None
    for s in analysis['stories']:
        if s['key'] == story_key:
            story = s
            break
    
    if not story:
        raise ValueError(f"Story key '{story_key}' not found in data")
    
    related = find_related_series(story_key, all_data)
    
    # Build story package
    pkg = {
        'primary': story,
        'related': related,
        'all_ranked': analysis['stories'][:10],
    }
    
    # Generate script
    print(f"\n{'='*60}")
    print(f"EPISODE {episode_num}: {story['name']}")
    print(f"{'='*60}")
    
    script_data = generate_script(pkg)
    print(f"  Title: {script_data['title']}")
    print(f"  Words: {script_data['word_count']}, ~{script_data['estimated_duration_sec']}s")
    
    # Save script
    ep_data_dir = os.path.join(BASE, 'data', f'ep{episode_num}')
    os.makedirs(ep_data_dir, exist_ok=True)
    
    with open(os.path.join(ep_data_dir, 'script.json'), 'w') as f:
        json.dump(script_data, f, indent=2)
    with open(os.path.join(ep_data_dir, 'voiceover_script.txt'), 'w') as f:
        f.write(script_data['script'])
    
    # Render video
    ep_dir, silent_path = render_episode(story, related, script_data, episode_num)
    
    # Generate thumbnail
    thumb_path = os.path.join(BASE, 'output', f'ep{episode_num}', 'thumbnail.png')
    generate_thumbnail(script_data, thumb_path)
    
    return {
        'episode_num': episode_num,
        'story_key': story_key,
        'title': script_data['title'],
        'script_path': os.path.join(ep_data_dir, 'script.json'),
        'voiceover_script': os.path.join(ep_data_dir, 'voiceover_script.txt'),
        'silent_video': silent_path,
        'thumbnail': thumb_path,
        'ep_dir': ep_dir,
    }
