"""
Render pilot episode - optimized for sandbox speed.
Renders at 5fps unique frames, outputs 30fps video via ffmpeg.
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
from config.settings import COLORS
from scripts.data_ingestion import FREDClient
from scripts.story_discovery import build_story_package, find_related_series
from scripts.script_writer import generate_script

plt.rcParams.update({
    'figure.facecolor': COLORS['bg_dark'], 'axes.facecolor': COLORS['bg_dark'],
    'axes.edgecolor': COLORS['border'], 'text.color': COLORS['text_primary'],
    'axes.labelcolor': COLORS['text_secondary'], 'xtick.color': COLORS['text_muted'],
    'ytick.color': COLORS['text_muted'], 'grid.color': COLORS['grid'], 'grid.alpha': 0.3,
    'font.family': 'sans-serif', 'font.size': 14, 'axes.grid': True,
    'grid.linestyle': '--', 'axes.spines.top': False, 'axes.spines.right': False,
})

pkg = build_story_package('/home/user/workspace/the-money-map/data/latest_data.json')
script_data = generate_script(pkg)
primary = script_data['primary_metric']
client = FREDClient()
series = client.get_series(primary['series_id'])
observations = series['observations']
with open('/home/user/workspace/the-money-map/data/latest_data.json') as f:
    all_data = json.load(f)['data']
related = find_related_series(primary['key'], all_data)

base = '/home/user/workspace/the-money-map/output/pilot'
os.makedirs(base, exist_ok=True)
RENDER_FPS = 5

def f2v(frame_dir, output_path):
    subprocess.run(["ffmpeg", "-y", "-framerate", str(RENDER_FPS), "-i",
        os.path.join(frame_dir, "frame_%04d.png"), "-c:v", "libx264", "-preset", "fast",
        "-crf", "23", "-r", "30", "-pix_fmt", "yuv420p", output_path],
        capture_output=True, text=True, timeout=300, check=True)

val = primary['latest_value']; unit = primary['unit']
display_val = f"{val:.1f}%" if unit == '%' else f"${val:,.2f}"
is_neg = primary['yoy_pct'] < 0
neg_accent = COLORS['negative'] if is_neg else COLORS['positive']
chart_accent = COLORS['negative'] if is_neg else COLORS['accent_teal']
arrow = "▼" if is_neg else "▲"

# SCENE 1: TITLE (25 frames = 5s)
print("Scene 1: Title...")
d = os.path.join(base, "f_title"); os.makedirs(d, exist_ok=True)
for i in range(25):
    p = i/24
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    fig.patch.set_facecolor(COLORS['bg_dark'])
    ga = 0.06*min(p*3,1.0)
    for x in np.arange(0,1.1,0.05):
        ax.axvline(x, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
    for y in np.arange(0,1.1,0.05):
        ax.axhline(y, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
    ta = min(p*2.5, 1.0)
    if p > 0.1:
        yo = max(0, 0.02*(1-min((p-0.1)*5,1.0)))
        t = script_data['title']
        if len(t) > 35 and '—' in t:
            parts = t.split('—')
            ax.text(0.5, 0.58+yo, parts[0].strip(), fontsize=40, fontweight='bold',
                   ha='center', va='center', color=COLORS['text_primary'], alpha=ta)
            ax.text(0.5, 0.47+yo, '— '+parts[1].strip(), fontsize=30,
                   ha='center', va='center', color=COLORS['accent_coral'], alpha=ta)
        else:
            ax.text(0.5, 0.55+yo, t, fontsize=38, fontweight='bold',
                   ha='center', va='center', color=COLORS['text_primary'], alpha=ta)
    if p > 0.35:
        ax.text(0.5, 0.37, f"Data as of {primary['latest_date']}", fontsize=18,
               ha='center', color=COLORS['accent_teal'], alpha=min((p-0.35)*3,1.0))
    if p > 0.2:
        lp2 = min((p-0.2)*2.5,1.0); lw2 = 0.3*lp2
        ax.plot([0.5-lw2/2, 0.5+lw2/2], [0.32,0.32], color=COLORS['accent_teal'], lw=2, alpha=0.8)
    if p > 0.5:
        ax.text(0.95, 0.05, "THE MONEY MAP", fontsize=12, ha='right',
               color=COLORS['text_muted'], alpha=min((p-0.5)*3,1.0), fontweight='bold', style='italic')
    plt.tight_layout(pad=0)
    plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
    plt.close(fig)
f2v(d, os.path.join(base, "scene_01.mp4"))
print("  Done")

# SCENE 2: STAT CALLOUT (75 frames = 15s)
print("Scene 2: Stat Callout...")
d = os.path.join(base, "f_callout"); os.makedirs(d, exist_ok=True)
for i in range(75):
    p = i/74
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    fig.patch.set_facecolor(COLORS['bg_dark'])
    ga = 0.04+0.012*np.sin(p*3*np.pi)
    for x in np.arange(0,1.1,0.04):
        ax.axvline(x, color=neg_accent, alpha=ga, lw=0.2)
    for y in np.arange(0,1.1,0.04):
        ax.axhline(y, color=neg_accent, alpha=ga, lw=0.2)
    if p > 0.05:
        na = min((p-0.05)*3,1.0)
        sc = 1.0+max(0, 0.12*(1-min((p-0.05)*4,1.0)))
        ax.text(0.5, 0.55, display_val, fontsize=int(72*sc), fontweight='bold',
               ha='center', va='center', color=COLORS['text_primary'], alpha=na)
    if p > 0.2:
        ax.text(0.5, 0.38, primary['name'].upper(), fontsize=22, ha='center',
               color=COLORS['text_secondary'], alpha=min((p-0.2)*3,1.0), fontweight='bold')
    if p > 0.35:
        ax.text(0.5, 0.27, f"{arrow} {abs(primary['yoy_pct']):.1f}% Year Over Year",
               fontsize=24, ha='center', color=neg_accent, alpha=min((p-0.35)*3,1.0), fontweight='bold')
    ax.text(0.95, 0.04, "THE MONEY MAP", fontsize=11, ha='right',
           color=COLORS['text_muted'], alpha=0.4, fontweight='bold')
    plt.tight_layout(pad=0)
    plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
    plt.close(fig)
f2v(d, os.path.join(base, "scene_02.mp4"))
print("  Done")

# SCENE 3: MAIN CHART (250 frames = 50s)
print("Scene 3: Main Chart...")
d = os.path.join(base, "f_chart"); os.makedirs(d, exist_ok=True)
dates_raw = [datetime.strptime(o['date'], '%Y-%m-%d') for o in observations][::-1]
vals_raw = [o['value'] for o in observations][::-1]
n = len(vals_raw); ymin = min(vals_raw)*0.92; ymax = max(vals_raw)*1.08

for i in range(250):
    p = i/249
    show = max(2, int(p*n*1.05)); show = min(show, n)
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(COLORS['bg_dark'])
    ax.text(0.02, 1.08, primary['name'].upper(), transform=ax.transAxes,
           fontsize=26, fontweight='bold', color=COLORS['text_primary'], va='top')
    if p > 0.15:
        lv = vals_raw[show-1]
        vs2 = f"{lv:.1f}%" if unit=='%' else f"${lv:,.0f}"
        ax.text(0.02, 1.02, f"Latest: {vs2}", transform=ax.transAxes,
               fontsize=17, color=chart_accent, va='top')
    xd = dates_raw[:show]; yd = vals_raw[:show]
    ax.plot(xd, yd, color=chart_accent, lw=2.5, solid_capstyle='round', zorder=3)
    ax.fill_between(xd, ymin, yd, alpha=0.06, color=chart_accent)
    if len(xd) > 0:
        ax.scatter([xd[-1]], [yd[-1]], color=chart_accent, s=60, zorder=5, edgecolors='white', linewidths=1.5)
        ax.scatter([xd[-1]], [yd[-1]], color=chart_accent, s=180, alpha=0.15, zorder=4)
    ax.set_xlim(dates_raw[0], dates_raw[-1]); ax.set_ylim(ymin, ymax)
    if unit == '%': ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
    ax.text(0.99, -0.07, "Source: FRED (Federal Reserve Economic Data)", transform=ax.transAxes,
           fontsize=10, color=COLORS['text_muted'], ha='right', va='top')
    ax.text(0.01, -0.07, "THE MONEY MAP", transform=ax.transAxes, fontsize=10,
           color=COLORS['text_muted'], ha='left', va='top', fontweight='bold')
    plt.tight_layout(pad=2)
    plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
    plt.close(fig)
    if i % 50 == 0: print(f"  frame {i}/250")
f2v(d, os.path.join(base, "scene_03.mp4"))
print("  Done")

# SCENE 4: COMPARISON (125 frames = 25s)
print("Scene 4: Comparison...")
d = os.path.join(base, "f_comp"); os.makedirs(d, exist_ok=True)
comp = [{"name": primary['name'], "latest_value": primary['latest_value'],
         "unit": primary['unit'], "yoy_pct": primary['yoy_pct']}]
for r in related[:3]: comp.append(r)
acols = [COLORS['accent_teal'], COLORS['accent_blue'], COLORS['accent_coral'], COLORS['accent_amber']]

for i in range(125):
    p = i/124
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(COLORS['bg_dark']); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    ax.text(0.5, 0.92, "THE CONNECTED INDICATORS", fontsize=28, fontweight='bold',
           ha='center', color=COLORS['text_primary'], alpha=min(p*3,1.0), transform=ax.transAxes)
    for j, m in enumerate(comp[:4]):
        cp2 = max(0, min((p-0.12*j-0.15)*3, 1.0))
        if cp2 <= 0: continue
        yp = 0.72-j*0.17; col = acols[j%4]
        ax.text(0.08, yp+0.02, m['name'], fontsize=19, fontweight='bold',
               color=COLORS['text_primary'], alpha=cp2, transform=ax.transAxes, va='center')
        v2 = m['latest_value']; u2 = m.get('unit','')
        if u2=='%': vs3=f"{v2:.1f}%"
        elif u2 in ('$','$/gallon'): vs3=f"${v2:,.2f}"
        elif u2=='billions $': vs3=f"${v2/1000:.1f}T" if v2>=1000 else f"${v2:,.0f}B"
        elif u2=='millions $': vs3=f"${v2/1e6:.1f}T" if v2>=1e6 else f"${v2/1000:,.0f}B"
        else: vs3=f"{v2:,.1f}"
        ax.text(0.92, yp+0.02, vs3, fontsize=21, fontweight='bold', color=col,
               alpha=cp2, transform=ax.transAxes, ha='right', va='center')
        yoy2 = m.get('yoy_pct')
        if yoy2 is not None:
            bc = COLORS['positive'] if yoy2>0 else COLORS['negative']
            ar2 = "▲" if yoy2>0 else "▼"
            ax.text(0.92, yp-0.025, f"{ar2} {abs(yoy2):.1f}% YoY", fontsize=13,
                   color=bc, alpha=cp2*0.85, transform=ax.transAxes, ha='right', va='center')
        ax.plot([0.08,0.92], [yp-0.055,yp-0.055], color=COLORS['border'],
               lw=0.5, alpha=cp2*0.4, transform=ax.transAxes)
    ax.text(0.5, 0.05, "Source: FRED  |  THE MONEY MAP", fontsize=11,
           ha='center', color=COLORS['text_muted'], alpha=min(p*2,0.6), transform=ax.transAxes)
    plt.tight_layout(pad=0)
    plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
    plt.close(fig)
f2v(d, os.path.join(base, "scene_04.mp4"))
print("  Done")

# SCENE 5: CLOSING (65 frames = 13s)
print("Scene 5: Closing...")
d = os.path.join(base, "f_close"); os.makedirs(d, exist_ok=True)
for i in range(65):
    p = i/64
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    fig.patch.set_facecolor(COLORS['bg_dark'])
    ga = 0.05*min(p*2,1.0)
    for x in np.arange(0,1.1,0.05):
        ax.axvline(x, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
    for y in np.arange(0,1.1,0.05):
        ax.axhline(y, color=COLORS['accent_teal'], alpha=ga, lw=0.3)
    ax.text(0.5, 0.58, "THE MONEY MAP", fontsize=52, fontweight='bold',
           ha='center', color=COLORS['text_primary'], alpha=min(p*2,1.0))
    if p > 0.2:
        ax.text(0.5, 0.44, "Subscribe for weekly data-driven analysis", fontsize=20,
               ha='center', color=COLORS['accent_teal'], alpha=min((p-0.2)*2.5,1.0))
    if p > 0.3:
        lp3 = min((p-0.3)*2,1.0); lw3 = 0.25*lp3
        ax.plot([0.5-lw3/2, 0.5+lw3/2], [0.38,0.38], color=COLORS['accent_teal'], lw=2, alpha=0.7)
    plt.tight_layout(pad=0)
    plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=100)
    plt.close(fig)
f2v(d, os.path.join(base, "scene_05.mp4"))
print("  Done")

# ASSEMBLE
print("\nAssembling final video...")
with open(os.path.join(base, "concat.txt"), 'w') as f:
    for s in range(1, 6):
        f.write(f"file 'scene_{s:02d}.mp4'\n")

silent = os.path.join(base, "silent.mp4")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
    os.path.join(base, "concat.txt"), "-c", "copy", silent],
    capture_output=True, text=True, timeout=120, check=True, cwd=base)

vo = '/home/user/workspace/the-money-map/output/voiceover.mp3'
final = '/home/user/workspace/the-money-map/output/pilot_episode.mp4'

if os.path.exists(vo):
    subprocess.run(["ffmpeg", "-y", "-i", silent, "-i", vo,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0", "-shortest", final],
        capture_output=True, text=True, timeout=120, check=True)
else:
    import shutil
    shutil.copy2(silent, final)

sz = os.path.getsize(final)/(1024*1024)
dur = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
    "-of", "csv=p=0", final], capture_output=True, text=True)
print(f"\nFinal: {final}")
print(f"Size: {sz:.1f} MB")
print(f"Duration: {dur.stdout.strip()}s")
print("PILOT EPISODE COMPLETE!")
