"""
Module 4: Video Renderer — Generates cinematic animated data visualizations.
Produces individual scene clips (PNG frame sequences → MP4 via ffmpeg).

Visual Style: Dark, clean, Bloomberg-meets-Netflix aesthetic.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import numpy as np
import json
import os
import subprocess
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import COLORS, FRED_API_KEY

# -- Global matplotlib config --
plt.rcParams.update({
    'figure.facecolor': COLORS['bg_dark'],
    'axes.facecolor': COLORS['bg_dark'],
    'axes.edgecolor': COLORS['border'],
    'text.color': COLORS['text_primary'],
    'axes.labelcolor': COLORS['text_secondary'],
    'xtick.color': COLORS['text_muted'],
    'ytick.color': COLORS['text_muted'],
    'grid.color': COLORS['grid'],
    'grid.alpha': 0.3,
    'font.family': 'sans-serif',
    'font.size': 14,
    'axes.grid': True,
    'grid.linestyle': '--',
    'axes.spines.top': False,
    'axes.spines.right': False,
})


def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))


def render_title_card(title: str, subtitle: str, output_dir: str, num_frames: int = 90):
    """Render an animated title card sequence."""
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(num_frames):
        progress = i / max(num_frames - 1, 1)
        
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        fig.patch.set_facecolor(COLORS['bg_dark'])
        
        # Animated grid background
        grid_alpha = 0.08 * min(progress * 3, 1.0)
        for x in np.arange(0, 1.1, 0.05):
            ax.axvline(x, color=COLORS['accent_teal'], alpha=grid_alpha, linewidth=0.3)
        for y in np.arange(0, 1.1, 0.05):
            ax.axhline(y, color=COLORS['accent_teal'], alpha=grid_alpha, linewidth=0.3)
        
        # Fade-in title
        title_alpha = min(progress * 2.5, 1.0)
        if progress > 0.1:
            # Slide up effect
            y_offset = max(0, 0.02 * (1 - min((progress - 0.1) * 5, 1.0)))
            ax.text(0.5, 0.55 + y_offset, title, fontsize=46, fontweight='bold',
                   ha='center', va='center', color=COLORS['text_primary'],
                   alpha=title_alpha, family='sans-serif')
        
        # Subtitle fade-in (delayed)
        if progress > 0.35:
            sub_alpha = min((progress - 0.35) * 3, 1.0)
            ax.text(0.5, 0.42, subtitle, fontsize=22, ha='center', va='center',
                   color=COLORS['accent_teal'], alpha=sub_alpha)
        
        # Bottom accent line (draws in)
        if progress > 0.2:
            line_progress = min((progress - 0.2) * 2.5, 1.0)
            line_width = 0.3 * line_progress
            ax.plot([0.5 - line_width/2, 0.5 + line_width/2], [0.35, 0.35],
                   color=COLORS['accent_teal'], linewidth=2, alpha=0.8)
        
        # Channel name (bottom right)
        if progress > 0.5:
            ch_alpha = min((progress - 0.5) * 3, 1.0)
            ax.text(0.95, 0.06, "THE MONEY MAP", fontsize=13, ha='right', va='bottom',
                   color=COLORS['text_muted'], alpha=ch_alpha, fontweight='bold',
                   style='italic')
        
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(output_dir, f"frame_{i:04d}.png"),
                   facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    
    return num_frames


def render_main_chart(series_data: list, metric_name: str, unit: str, 
                      accent_color: str, output_dir: str, num_frames: int = 150):
    """Render the main animated line chart with progressive reveal."""
    os.makedirs(output_dir, exist_ok=True)
    
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in series_data]
    values = [d['value'] for d in series_data]
    
    # Reverse so oldest is first
    dates = dates[::-1]
    values = values[::-1]
    
    n_points = len(values)
    y_min = min(values) * 0.92
    y_max = max(values) * 1.08
    
    for i in range(num_frames):
        progress = i / max(num_frames - 1, 1)
        
        # How many data points to show (progressive reveal)
        show_up_to = max(2, int(progress * n_points * 1.1))
        show_up_to = min(show_up_to, n_points)
        
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        
        # Chart title
        ax.text(0.02, 1.08, metric_name.upper(), transform=ax.transAxes,
               fontsize=28, fontweight='bold', color=COLORS['text_primary'],
               va='top')
        
        # Subtitle with latest value
        if progress > 0.3:
            latest_val = values[show_up_to - 1]
            if unit == '%':
                val_str = f"{latest_val:.1f}%"
            elif unit == '$':
                val_str = f"${latest_val:,.0f}"
            else:
                val_str = f"{latest_val:,.1f}"
            
            ax.text(0.02, 1.02, f"Latest: {val_str}", transform=ax.transAxes,
                   fontsize=18, color=accent_color, va='top')
        
        # Draw the line (progressive reveal with gradient)
        x_data = dates[:show_up_to]
        y_data = values[:show_up_to]
        
        # Main line
        ax.plot(x_data, y_data, color=accent_color, linewidth=2.5, 
                solid_capstyle='round', zorder=3)
        
        # Fill under the line
        ax.fill_between(x_data, y_min, y_data, alpha=0.08, color=accent_color)
        
        # Glowing dot at the current point
        if len(x_data) > 0:
            ax.scatter([x_data[-1]], [y_data[-1]], color=accent_color, s=80, 
                      zorder=5, edgecolors='white', linewidths=1.5)
            # Glow effect
            ax.scatter([x_data[-1]], [y_data[-1]], color=accent_color, s=200,
                      alpha=0.2, zorder=4)
        
        ax.set_xlim(dates[0], dates[-1])
        ax.set_ylim(y_min, y_max)
        
        # Format y-axis
        if unit == '%':
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
        elif unit in ('$', '$/gallon'):
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.2f'))
        elif unit == 'billions $':
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda x, p: f"${x/1000:.1f}T" if x >= 1000 else f"${x:.0f}B"))
        elif unit == 'millions $':
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda x, p: f"${x/1e6:.1f}T" if x >= 1e6 else f"${x/1000:.0f}B"))
        
        # Source attribution
        ax.text(0.99, -0.08, "Source: FRED (Federal Reserve Economic Data)",
               transform=ax.transAxes, fontsize=10, color=COLORS['text_muted'],
               ha='right', va='top')
        
        ax.text(0.01, -0.08, "THE MONEY MAP",
               transform=ax.transAxes, fontsize=10, color=COLORS['text_muted'],
               ha='left', va='top', fontweight='bold')
        
        plt.tight_layout(pad=2)
        plt.savefig(os.path.join(output_dir, f"frame_{i:04d}.png"),
                   facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    
    return num_frames


def render_comparison_panel(metrics: list, output_dir: str, num_frames: int = 120):
    """Render animated comparison bars for related metrics."""
    os.makedirs(output_dir, exist_ok=True)
    
    accent_colors = [COLORS['accent_teal'], COLORS['accent_blue'], 
                     COLORS['accent_coral'], COLORS['accent_amber']]
    
    for i in range(num_frames):
        progress = i / max(num_frames - 1, 1)
        
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ax.axis('off')
        
        # Header
        header_alpha = min(progress * 3, 1.0)
        ax.text(0.5, 0.92, "THE CONNECTED INDICATORS", fontsize=30, 
               fontweight='bold', ha='center', va='center',
               color=COLORS['text_primary'], alpha=header_alpha,
               transform=ax.transAxes)
        
        # Render each metric as a horizontal bar card
        n_metrics = min(len(metrics), 4)
        for j, m in enumerate(metrics[:n_metrics]):
            # Staggered reveal
            delay = 0.15 * j
            card_progress = max(0, min((progress - delay - 0.2) * 3, 1.0))
            
            if card_progress <= 0:
                continue
            
            y_pos = 0.72 - j * 0.18
            color = accent_colors[j % len(accent_colors)]
            
            # Metric name
            ax.text(0.08, y_pos + 0.03, m['name'], fontsize=20, 
                   fontweight='bold', color=COLORS['text_primary'],
                   alpha=card_progress, transform=ax.transAxes, va='center')
            
            # Value
            val = m['latest_value']
            unit = m.get('unit', '')
            if unit == '%':
                val_str = f"{val:.1f}%"
            elif unit in ('$', '$/gallon'):
                val_str = f"${val:,.2f}"
            elif unit == 'billions $':
                val_str = f"${val/1000:.1f}T" if val >= 1000 else f"${val:,.0f}B"
            elif unit == 'millions $':
                val_str = f"${val/1e6:.1f}T" if val >= 1e6 else f"${val/1000:,.0f}B"
            else:
                val_str = f"{val:,.1f}"
            
            ax.text(0.92, y_pos + 0.03, val_str, fontsize=22,
                   fontweight='bold', color=color, alpha=card_progress,
                   transform=ax.transAxes, ha='right', va='center')
            
            # YoY change badge
            yoy = m.get('yoy_pct')
            if yoy is not None:
                badge_color = COLORS['positive'] if yoy > 0 else COLORS['negative']
                arrow = "▲" if yoy > 0 else "▼"
                ax.text(0.92, y_pos - 0.025, f"{arrow} {abs(yoy):.1f}% YoY",
                       fontsize=14, color=badge_color, alpha=card_progress * 0.9,
                       transform=ax.transAxes, ha='right', va='center')
            
            # Separator line
            ax.plot([0.08, 0.92], [y_pos - 0.055, y_pos - 0.055],
                   color=COLORS['border'], linewidth=0.5, alpha=card_progress * 0.5,
                   transform=ax.transAxes)
        
        # Source
        ax.text(0.5, 0.05, "Source: FRED  |  THE MONEY MAP", fontsize=11,
               ha='center', color=COLORS['text_muted'], alpha=min(progress*2, 0.7),
               transform=ax.transAxes)
        
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(output_dir, f"frame_{i:04d}.png"),
                   facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    
    return num_frames


def render_stat_callout(value: str, label: str, change_pct: float,
                        output_dir: str, num_frames: int = 90):
    """Render a big animated stat callout (for hook/punchline moments)."""
    os.makedirs(output_dir, exist_ok=True)
    
    is_negative = change_pct < 0
    accent = COLORS['negative'] if is_negative else COLORS['positive']
    arrow = "▼" if is_negative else "▲"
    
    for i in range(num_frames):
        progress = i / max(num_frames - 1, 1)
        
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        fig.patch.set_facecolor(COLORS['bg_dark'])
        
        # Subtle pulsing grid
        grid_alpha = 0.05 + 0.02 * np.sin(progress * 4 * np.pi)
        for x in np.arange(0, 1.1, 0.04):
            ax.axvline(x, color=accent, alpha=grid_alpha, linewidth=0.2)
        for y in np.arange(0, 1.1, 0.04):
            ax.axhline(y, color=accent, alpha=grid_alpha, linewidth=0.2)
        
        # Big number (counts up)
        if progress > 0.05:
            num_alpha = min((progress - 0.05) * 3, 1.0)
            
            # Number animation: show final value with scale effect
            scale = 1.0 + max(0, 0.3 * (1 - min((progress - 0.05) * 4, 1.0)))
            fontsize = int(72 * scale)
            
            ax.text(0.5, 0.55, value, fontsize=fontsize, fontweight='bold',
                   ha='center', va='center', color=COLORS['text_primary'],
                   alpha=num_alpha)
        
        # Label
        if progress > 0.2:
            label_alpha = min((progress - 0.2) * 3, 1.0)
            ax.text(0.5, 0.38, label.upper(), fontsize=22, ha='center',
                   va='center', color=COLORS['text_secondary'], alpha=label_alpha,
                   fontweight='bold', letterspace=0.15 if hasattr(ax, 'letterspace') else None)
        
        # Change badge
        if progress > 0.4:
            badge_alpha = min((progress - 0.4) * 3, 1.0)
            ax.text(0.5, 0.28, f"{arrow} {abs(change_pct):.1f}% Year Over Year",
                   fontsize=24, ha='center', va='center', color=accent,
                   alpha=badge_alpha, fontweight='bold')
        
        # Channel watermark
        if progress > 0.6:
            wm_alpha = min((progress - 0.6) * 2, 0.5)
            ax.text(0.95, 0.04, "THE MONEY MAP", fontsize=11, ha='right',
                   color=COLORS['text_muted'], alpha=wm_alpha, fontweight='bold')
        
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(output_dir, f"frame_{i:04d}.png"),
                   facecolor=fig.get_facecolor(), dpi=100)
        plt.close(fig)
    
    return num_frames


def frames_to_video(frame_dir: str, output_path: str, fps: int = 30, duration_override: float = None):
    """Convert PNG frame sequence to MP4 using ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frame_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr[:500]}")
        raise RuntimeError(f"ffmpeg failed: {result.returncode}")
    return output_path


def render_full_episode(script_data: dict, series_data: list, output_dir: str) -> list:
    """Render all visual scenes for a complete episode."""
    os.makedirs(output_dir, exist_ok=True)
    scenes = []
    
    primary = script_data["primary_metric"]
    title = script_data["title"]
    
    print("🎬 Rendering Scene 1: Title Card...")
    title_dir = os.path.join(output_dir, "scene_01_title")
    render_title_card(
        title=title,
        subtitle=f"Data as of {primary['latest_date']}",
        output_dir=title_dir,
        num_frames=90
    )
    title_video = os.path.join(output_dir, "scene_01_title.mp4")
    frames_to_video(title_dir, title_video)
    scenes.append(title_video)
    
    print("🎬 Rendering Scene 2: Stat Callout (Hook)...")
    callout_dir = os.path.join(output_dir, "scene_02_callout")
    
    # Format the value for display
    val = primary['latest_value']
    unit = primary['unit']
    if unit == '%':
        display_val = f"{val:.1f}%"
    elif unit in ('$', '$/gallon'):
        display_val = f"${val:,.2f}"
    elif unit == 'billions $':
        display_val = f"${val/1000:.1f}T" if val >= 1000 else f"${val:,.0f}B"
    elif unit == 'millions $':
        display_val = f"${val/1e6:.1f}T" if val >= 1e6 else f"${val/1000:,.0f}B"
    else:
        display_val = f"{val:,.1f}"
    
    render_stat_callout(
        value=display_val,
        label=primary['name'],
        change_pct=primary['yoy_pct'],
        output_dir=callout_dir,
        num_frames=90
    )
    callout_video = os.path.join(output_dir, "scene_02_callout.mp4")
    frames_to_video(callout_dir, callout_video)
    scenes.append(callout_video)
    
    print("🎬 Rendering Scene 3: Main Chart...")
    chart_dir = os.path.join(output_dir, "scene_03_chart")
    accent = COLORS['negative'] if primary['yoy_pct'] < 0 else COLORS['accent_teal']
    render_main_chart(
        series_data=series_data,
        metric_name=primary['name'],
        unit=primary['unit'],
        accent_color=accent,
        output_dir=chart_dir,
        num_frames=150
    )
    chart_video = os.path.join(output_dir, "scene_03_chart.mp4")
    frames_to_video(chart_dir, chart_video)
    scenes.append(chart_video)
    
    print("🎬 Rendering Scene 4: Comparison Panel...")
    comp_dir = os.path.join(output_dir, "scene_04_comparison")
    # Build metrics list from primary + related
    comparison_metrics = [
        {
            "name": primary['name'],
            "latest_value": primary['latest_value'],
            "unit": primary['unit'],
            "yoy_pct": primary['yoy_pct'],
        }
    ]
    # Get related data from script sections
    with open(os.path.join(os.path.dirname(output_dir), "data", "latest_data.json")) as f:
        all_data = json.load(f)["data"]
    
    from scripts.story_discovery import find_related_series
    related = find_related_series(primary['key'], all_data)
    for r in related[:3]:
        comparison_metrics.append(r)
    
    render_comparison_panel(
        metrics=comparison_metrics,
        output_dir=comp_dir,
        num_frames=120
    )
    comp_video = os.path.join(output_dir, "scene_04_comparison.mp4")
    frames_to_video(comp_dir, comp_video)
    scenes.append(comp_video)
    
    print(f"✅ Rendered {len(scenes)} scenes.")
    return scenes


if __name__ == "__main__":
    # Test: render scenes from latest data
    import requests
    from scripts.data_ingestion import FREDClient
    from scripts.story_discovery import build_story_package
    from scripts.script_writer import generate_script
    
    data_path = "/home/user/workspace/the-money-map/data/latest_data.json"
    pkg = build_story_package(data_path)
    script = generate_script(pkg)
    
    # Fetch full time series for the primary metric
    client = FREDClient()
    series = client.get_series(script['primary_metric']['series_id'])
    
    output_dir = "/home/user/workspace/the-money-map/output/episode_test"
    scenes = render_full_episode(script, series['observations'], output_dir)
    
    for s in scenes:
        size = os.path.getsize(s) / 1024
        print(f"  📹 {os.path.basename(s)}: {size:.0f} KB")
