"""
Enhanced Cinematic Renderer for The Money Map V2
Produces high-quality 1920x1080 data-viz videos with:
- Smooth animated counters 
- Glowing accent effects
- Ken Burns zoom on charts
- Particle/grid backgrounds
- Animated progress lines
- Professional lower thirds
- Section transitions with wipes

Renders at 10fps unique frames → ffmpeg upscale to 30fps.
Each episode: ~7 scenes optimized for 2:40-3:10 voiceover.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as patches
import numpy as np
import json
import os
import subprocess
import shutil
from datetime import datetime
import sys

sys.path.insert(0, '/home/user/workspace/the-money-map')
from config.settings import COLORS, FRED_SERIES
from scripts.data_ingestion import FREDClient

# Global render settings
RENDER_FPS = 10  # Render at 10fps, output 30fps
W, H = 19.2, 10.8  # Figure size (1920x1080 at 100dpi)
DPI = 100

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


def ease_out_cubic(t):
    """Smooth ease-out for animations."""
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    """Smooth ease-in-out."""
    return 3*t*t - 2*t*t*t

def glow_alpha(base, t, pulse_speed=2.0):
    """Pulsing glow effect."""
    return base + 0.02 * np.sin(t * pulse_speed * np.pi)

def draw_grid_bg(ax, color, alpha=0.04, spacing=0.05, t=0):
    """Animated subtle grid background."""
    offset = (t * 0.01) % spacing
    for x in np.arange(-spacing + offset, 1.1 + spacing, spacing):
        ax.axvline(x, color=color, alpha=alpha, lw=0.3)
    for y in np.arange(-spacing + offset/2, 1.1 + spacing, spacing):
        ax.axhline(y, color=color, alpha=alpha, lw=0.3)

def draw_particles(ax, n=30, t=0, color='#00D4AA', seed=42):
    """Floating particle effect."""
    rng = np.random.RandomState(seed)
    for _ in range(n):
        x = (rng.random() + t * 0.02 * rng.random()) % 1.0
        y = (rng.random() + t * 0.015 * rng.random()) % 1.0
        s = rng.random() * 15 + 2
        a = rng.random() * 0.12 + 0.02
        ax.scatter([x], [y], s=s, color=color, alpha=a, zorder=1)

def draw_watermark(ax, alpha=0.35):
    """Brand watermark."""
    ax.text(0.95, 0.04, "THE MONEY MAP", fontsize=11, ha='right',
            color=COLORS['text_muted'], alpha=alpha, fontweight='bold',
            style='italic', transform=ax.transAxes)

def frames_to_video(frame_dir, output_path, fps=RENDER_FPS):
    """Convert frames to video with ffmpeg."""
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps), "-i",
        os.path.join(frame_dir, "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-r", "30", "-pix_fmt", "yuv420p", output_path
    ], capture_output=True, text=True, timeout=300, check=True)


def render_scene_cold_open(script_data, base_dir, duration_sec=6):
    """Scene 1: COLD OPEN — dramatic stat drop with counter animation."""
    print("  Scene 1: Cold Open...")
    d = os.path.join(base_dir, "f_cold_open")
    os.makedirs(d, exist_ok=True)
    
    primary = script_data['primary_metric']
    val = primary['latest_value']
    unit = primary['unit']
    yoy = primary['yoy_pct']
    is_neg = yoy < 0
    accent = COLORS['negative'] if is_neg else COLORS['accent_teal']
    
    # Format target value
    if unit == '%': target_str = f"{val:.1f}%"
    elif unit in ('$', '$/gallon'): target_str = f"${val:,.2f}"
    elif unit == 'millions $': target_str = f"${val/1e6:.1f}T" if val >= 1e6 else f"${val/1000:,.0f}B"
    elif unit == 'billions $': target_str = f"${val/1000:.1f}T" if val >= 1000 else f"${val:,.0f}B"
    else: target_str = f"{val:,.1f}"
    
    n_frames = duration_sec * RENDER_FPS
    
    for i in range(n_frames):
        p = i / (n_frames - 1)
        fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        fig.patch.set_facecolor(COLORS['bg_dark'])
        
        # Animated grid
        draw_grid_bg(ax, accent, alpha=0.03 + 0.03 * ease_out_cubic(min(p*2, 1)), t=i)
        draw_particles(ax, n=20, t=i, color=accent)
        
        # Counter animation — numbers scramble then lock in
        if p < 0.7:
            # Scramble phase
            scramble_p = p / 0.7
            # Show increasingly correct digits
            if unit == '%':
                scramble_val = val * scramble_p + (1-scramble_p) * (val + np.random.uniform(-5, 5))
                display = f"{scramble_val:.1f}%"
            elif unit in ('$', '$/gallon'):
                scramble_val = val * scramble_p + (1-scramble_p) * (val + np.random.uniform(-2, 2))
                display = f"${scramble_val:,.2f}"
            elif unit == 'millions $':
                scramble_val = val * scramble_p + (1-scramble_p) * (val * (1 + np.random.uniform(-0.1, 0.1)))
                display = f"${scramble_val/1e6:.1f}T" if val >= 1e6 else f"${scramble_val/1000:,.0f}B"
            elif unit == 'billions $':
                scramble_val = val * scramble_p + (1-scramble_p) * (val * (1 + np.random.uniform(-0.1, 0.1)))
                display = f"${scramble_val/1000:.1f}T" if val >= 1000 else f"${scramble_val:,.0f}B"
            else:
                display = target_str
            alpha = min(p * 3, 1.0)
        else:
            display = target_str
            alpha = 1.0
        
        # Big number — center
        scale = 1.0 + max(0, 0.15 * (1 - ease_out_cubic(min(p * 1.5, 1.0))))
        ax.text(0.5, 0.55, display, fontsize=int(90 * scale), fontweight='bold',
                ha='center', va='center', color='white', alpha=alpha)
        
        # Underline glow
        if p > 0.5:
            gp = ease_out_cubic(min((p - 0.5) * 3, 1.0))
            line_hw = 0.18 * gp
            ax.plot([0.5 - line_hw, 0.5 + line_hw], [0.42, 0.42],
                    color=accent, lw=3, alpha=0.8 * gp, solid_capstyle='round')
            # Glow under line
            ax.plot([0.5 - line_hw, 0.5 + line_hw], [0.42, 0.42],
                    color=accent, lw=12, alpha=0.15 * gp, solid_capstyle='round')
        
        draw_watermark(ax)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=DPI)
        plt.close(fig)
    
    out = os.path.join(base_dir, "scene_01_cold_open.mp4")
    frames_to_video(d, out)
    shutil.rmtree(d)
    return out


def render_scene_hook(script_data, base_dir, duration_sec=18):
    """Scene 2: HOOK + THE NUMBER — title reveal and stat context."""
    print("  Scene 2: Hook + Title...")
    d = os.path.join(base_dir, "f_hook")
    os.makedirs(d, exist_ok=True)
    
    primary = script_data['primary_metric']
    title = script_data['title']
    yoy = primary['yoy_pct']
    is_neg = yoy < 0
    accent = COLORS['negative'] if is_neg else COLORS['accent_teal']
    arrow = "▼" if is_neg else "▲"
    
    val = primary['latest_value']
    unit = primary['unit']
    if unit == '%': display_val = f"{val:.1f}%"
    elif unit in ('$', '$/gallon'): display_val = f"${val:,.2f}"
    elif unit == 'millions $': display_val = f"${val/1e6:.1f}T" if val >= 1e6 else f"${val/1000:,.0f}B"
    elif unit == 'billions $': display_val = f"${val/1000:.1f}T" if val >= 1000 else f"${val:,.0f}B"
    else: display_val = f"{val:,.1f}"
    
    n_frames = duration_sec * RENDER_FPS
    
    for i in range(n_frames):
        p = i / (n_frames - 1)
        fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        fig.patch.set_facecolor(COLORS['bg_dark'])
        
        draw_grid_bg(ax, accent, alpha=0.025, t=i)
        draw_particles(ax, n=15, t=i, color=accent)
        
        # Title slide: split on em dash
        if '—' in title:
            parts = title.split('—')
            line1 = parts[0].strip()
            line2 = '— ' + parts[1].strip()
        else:
            line1 = title
            line2 = ''
        
        # Phase 1: Title reveal (0-40%)
        if p < 0.4:
            tp = ease_out_cubic(min(p / 0.35, 1.0))
            ax.text(0.5, 0.62, line1, fontsize=38, fontweight='bold',
                    ha='center', va='center', color='white', alpha=tp,
                    wrap=True)
            if line2 and p > 0.1:
                tp2 = ease_out_cubic(min((p - 0.1) / 0.25, 1.0))
                ax.text(0.5, 0.48, line2, fontsize=28,
                        ha='center', va='center', color=COLORS['accent_coral'], alpha=tp2)
            # Date line
            if p > 0.2:
                dp = ease_out_cubic(min((p - 0.2) / 0.15, 1.0))
                ax.text(0.5, 0.35, f"Data as of {primary['latest_date']}", fontsize=16,
                        ha='center', color=COLORS['accent_teal'], alpha=dp * 0.8)
        
        # Phase 2: Stat callout (40-100%)
        else:
            sp = ease_out_cubic(min((p - 0.4) / 0.3, 1.0))
            
            # Stat value top-center
            ax.text(0.5, 0.65, display_val, fontsize=72, fontweight='bold',
                    ha='center', va='center', color='white', alpha=sp)
            
            # Metric name
            ax.text(0.5, 0.48, primary['name'].upper(), fontsize=22, fontweight='bold',
                    ha='center', color=COLORS['text_secondary'], alpha=sp)
            
            # YoY badge
            if p > 0.55:
                bp = ease_out_cubic(min((p - 0.55) / 0.2, 1.0))
                badge = f" {arrow} {abs(yoy):.1f}% Year Over Year "
                ax.text(0.5, 0.35, badge, fontsize=22, fontweight='bold',
                        ha='center', color='white', alpha=bp,
                        bbox=dict(boxstyle='round,pad=0.5', facecolor=accent,
                                  edgecolor='none', alpha=0.85 * bp))
            
            # Divider line
            if p > 0.5:
                lp = ease_out_cubic(min((p - 0.5) / 0.15, 1.0))
                hw = 0.2 * lp
                ax.plot([0.5 - hw, 0.5 + hw], [0.55, 0.55],
                        color=accent, lw=2, alpha=0.6 * lp)
        
        draw_watermark(ax)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=DPI)
        plt.close(fig)
    
    out = os.path.join(base_dir, "scene_02_hook.mp4")
    frames_to_video(d, out)
    shutil.rmtree(d)
    return out


def render_scene_chart(script_data, base_dir, duration_sec=55):
    """Scene 3: CHART WALK — animated chart with Ken Burns zoom."""
    print("  Scene 3: Chart Walk...")
    d = os.path.join(base_dir, "f_chart")
    os.makedirs(d, exist_ok=True)
    
    primary = script_data['primary_metric']
    unit = primary['unit']
    is_neg = primary['yoy_pct'] < 0
    chart_accent = COLORS['negative'] if is_neg else COLORS['accent_teal']
    
    # Fetch chart data
    client = FREDClient()
    series = client.get_series(primary['series_id'])
    observations = series['observations']
    
    dates_raw = [datetime.strptime(o['date'], '%Y-%m-%d') for o in observations][::-1]
    vals_raw = [o['value'] for o in observations][::-1]
    n = len(vals_raw)
    ymin = min(vals_raw) * 0.92
    ymax = max(vals_raw) * 1.08
    
    n_frames = duration_sec * RENDER_FPS
    
    for i in range(n_frames):
        p = i / (n_frames - 1)
        
        # Chart draw animation (0-80%), then Ken Burns zoom (80-100%)
        if p < 0.8:
            draw_p = p / 0.8
            show = max(2, int(draw_p * n * 1.05))
            show = min(show, n)
            zoom = 1.0  # No zoom during draw
        else:
            show = n
            zoom_p = (p - 0.8) / 0.2
            zoom = 1.0 + 0.08 * ease_in_out(zoom_p)  # Subtle zoom in
        
        fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        
        # Title
        ax.text(0.02, 1.08, primary['name'].upper(), transform=ax.transAxes,
                fontsize=24, fontweight='bold', color='white', va='top')
        
        # Latest value display
        if p > 0.1:
            lv = vals_raw[show - 1]
            if unit == '%': vs = f"{lv:.1f}%"
            elif unit in ('$', '$/gallon'): vs = f"${lv:,.2f}"
            elif unit == 'millions $': vs = f"${lv/1e6:.1f}T" if lv >= 1e6 else f"${lv/1000:,.0f}B"
            elif unit == 'billions $': vs = f"${lv/1000:.1f}T" if lv >= 1000 else f"${lv:,.0f}B"
            else: vs = f"{lv:,.1f}"
            ax.text(0.02, 1.02, f"Latest: {vs}", transform=ax.transAxes,
                    fontsize=16, color=chart_accent, va='top')
        
        # Main line
        xd = dates_raw[:show]
        yd = vals_raw[:show]
        ax.plot(xd, yd, color=chart_accent, lw=2.8, solid_capstyle='round', zorder=3)
        
        # Gradient fill under line
        ax.fill_between(xd, ymin, yd, alpha=0.08, color=chart_accent)
        
        # Glowing endpoint
        if len(xd) > 0:
            ax.scatter([xd[-1]], [yd[-1]], color=chart_accent, s=60, zorder=5,
                       edgecolors='white', linewidths=1.5)
            # Outer glow
            glow_s = 200 + 50 * np.sin(i * 0.3)
            ax.scatter([xd[-1]], [yd[-1]], color=chart_accent, s=glow_s, alpha=0.12, zorder=4)
        
        # Set axis limits with Ken Burns
        x_range = (dates_raw[-1] - dates_raw[0]).days
        x_center = dates_raw[0] + (dates_raw[-1] - dates_raw[0]) * 0.6
        y_range = ymax - ymin
        y_center = (ymin + ymax) / 2
        
        if zoom > 1.0:
            from matplotlib.dates import date2num, num2date
            xc = date2num(x_center)
            x_half = x_range / (2 * zoom)
            ax.set_xlim(num2date(xc - date2num(dates_raw[0]) - x_half + date2num(dates_raw[0])),
                        dates_raw[-1])
            y_half = y_range / (2 * zoom)
            ax.set_ylim(y_center - y_half, y_center + y_half)
        else:
            ax.set_xlim(dates_raw[0], dates_raw[-1])
            ax.set_ylim(ymin, ymax)
        
        if unit == '%':
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
        elif unit in ('$', '$/gallon'):
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.2f'))
        
        # Source and brand
        ax.text(0.99, -0.07, "Source: FRED (Federal Reserve Economic Data)",
                transform=ax.transAxes, fontsize=10, color=COLORS['text_muted'],
                ha='right', va='top')
        ax.text(0.01, -0.07, "THE MONEY MAP", transform=ax.transAxes,
                fontsize=10, color=COLORS['text_muted'], ha='left', va='top', fontweight='bold')
        
        plt.tight_layout(pad=2)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=DPI)
        plt.close(fig)
        
        if i % 100 == 0:
            print(f"    frame {i}/{n_frames}")
    
    out = os.path.join(base_dir, "scene_03_chart.mp4")
    frames_to_video(d, out)
    shutil.rmtree(d)
    return out


def render_scene_context(script_data, base_dir, duration_sec=40):
    """Scene 4: CONTEXT + CONNECTED DATA — multi-metric comparison cards."""
    print("  Scene 4: Context + Connected Data...")
    d = os.path.join(base_dir, "f_context")
    os.makedirs(d, exist_ok=True)
    
    primary = script_data['primary_metric']
    is_neg = primary['yoy_pct'] < 0
    accent = COLORS['negative'] if is_neg else COLORS['accent_teal']
    
    # Load related data
    with open('/home/user/workspace/the-money-map/data/latest_data.json') as f:
        all_data = json.load(f)['data']
    
    from scripts.story_discovery import find_related_series
    related = find_related_series(primary['key'], all_data)
    
    # Build comparison items
    items = [{"name": primary['name'], "latest_value": primary['latest_value'],
              "unit": primary['unit'], "yoy_pct": primary['yoy_pct']}]
    for r in related[:3]:
        items.append(r)
    
    colors = [COLORS['accent_teal'], COLORS['accent_blue'], COLORS['accent_coral'], COLORS['accent_amber']]
    
    n_frames = duration_sec * RENDER_FPS
    
    for i in range(n_frames):
        p = i / (n_frames - 1)
        fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        
        draw_grid_bg(ax, accent, alpha=0.02, t=i)
        
        # Section title
        title_a = ease_out_cubic(min(p * 4, 1.0))
        ax.text(0.5, 0.92, "THE CONNECTED INDICATORS", fontsize=28, fontweight='bold',
                ha='center', color='white', alpha=title_a)
        
        # Subtitle
        if p > 0.05:
            sub_a = ease_out_cubic(min((p - 0.05) * 4, 1.0))
            ax.text(0.5, 0.86, "How these metrics tell the full story", fontsize=16,
                    ha='center', color=COLORS['text_secondary'], alpha=sub_a * 0.7)
        
        # Metric cards — staggered reveal
        for j, item in enumerate(items[:4]):
            card_delay = 0.1 + j * 0.12
            if p <= card_delay:
                continue
            
            cp = ease_out_cubic(min((p - card_delay) * 3, 1.0))
            ypos = 0.72 - j * 0.17
            col = colors[j % 4]
            
            # Card background
            card = patches.FancyBboxPatch((0.05, ypos - 0.055), 0.9, 0.12,
                                          boxstyle="round,pad=0.01",
                                          facecolor=COLORS['bg_card'],
                                          edgecolor=col, linewidth=1.5,
                                          alpha=cp * 0.6)
            ax.add_patch(card)
            
            # Color indicator bar
            bar = patches.Rectangle((0.05, ypos - 0.055), 0.008, 0.12,
                                    facecolor=col, alpha=cp * 0.9)
            ax.add_patch(bar)
            
            # Metric name
            ax.text(0.09, ypos + 0.02, item['name'], fontsize=18, fontweight='bold',
                    color='white', alpha=cp, va='center')
            
            # Value
            v = item['latest_value']
            u = item.get('unit', '')
            if u == '%': vs = f"{v:.1f}%"
            elif u in ('$', '$/gallon'): vs = f"${v:,.2f}"
            elif u == 'billions $': vs = f"${v/1000:.1f}T" if v >= 1000 else f"${v:,.0f}B"
            elif u == 'millions $': vs = f"${v/1e6:.1f}T" if v >= 1e6 else f"${v/1000:,.0f}B"
            elif u == 'index': vs = f"{v:,.1f}"
            elif u == 'thousands': vs = f"{v/1000:,.1f}M" if v >= 1000 else f"{v:,.0f}K"
            else: vs = f"{v:,.1f}"
            
            ax.text(0.92, ypos + 0.025, vs, fontsize=22, fontweight='bold',
                    color=col, alpha=cp, ha='right', va='center')
            
            # YoY change badge
            yoy = item.get('yoy_pct')
            if yoy is not None:
                bc = COLORS['positive'] if yoy > 0 else COLORS['negative']
                ar = "▲" if yoy > 0 else "▼"
                ax.text(0.92, ypos - 0.025, f"{ar} {abs(yoy):.1f}% YoY", fontsize=13,
                        color=bc, alpha=cp * 0.85, ha='right', va='center')
        
        # Source line
        ax.text(0.5, 0.04, "Source: FRED  |  THE MONEY MAP", fontsize=11,
                ha='center', color=COLORS['text_muted'], alpha=min(p * 2, 0.5))
        
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=DPI)
        plt.close(fig)
    
    out = os.path.join(base_dir, "scene_04_context.mp4")
    frames_to_video(d, out)
    shutil.rmtree(d)
    return out


def render_scene_insight(script_data, base_dir, duration_sec=35):
    """Scene 5: INSIGHT — key takeaway with dramatic presentation."""
    print("  Scene 5: Insight...")
    d = os.path.join(base_dir, "f_insight")
    os.makedirs(d, exist_ok=True)
    
    primary = script_data['primary_metric']
    is_neg = primary['yoy_pct'] < 0
    accent = COLORS['negative'] if is_neg else COLORS['accent_teal']
    
    # Extract key insight line from script
    sections = script_data.get('sections', {})
    insight_text = sections.get('insight', '')
    # Get first sentence as the key takeaway
    sentences = [s.strip() for s in insight_text.split('.') if len(s.strip()) > 10]
    key_line = sentences[0] + '.' if sentences else primary['name']
    # Truncate if too long for display
    if len(key_line) > 100:
        key_line = key_line[:97] + '...'
    
    n_frames = duration_sec * RENDER_FPS
    
    for i in range(n_frames):
        p = i / (n_frames - 1)
        fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        
        draw_grid_bg(ax, accent, alpha=0.03, t=i)
        draw_particles(ax, n=25, t=i, color=accent)
        
        # "THE TAKEAWAY" header
        header_a = ease_out_cubic(min(p * 4, 1.0))
        ax.text(0.5, 0.82, "THE TAKEAWAY", fontsize=18, fontweight='bold',
                ha='center', color=accent, alpha=header_a * 0.8,
                fontfamily='sans-serif')
        
        # Divider line
        if p > 0.05:
            lp = ease_out_cubic(min((p - 0.05) * 3, 1.0))
            hw = 0.08 * lp
            ax.plot([0.5 - hw, 0.5 + hw], [0.78, 0.78],
                    color=accent, lw=2, alpha=0.7 * lp)
        
        # Key insight line — large text
        if p > 0.1:
            tp = ease_out_cubic(min((p - 0.1) * 2.5, 1.0))
            # Word wrap manually
            words = key_line.split()
            lines = []
            current = []
            for w in words:
                current.append(w)
                if len(' '.join(current)) > 40:
                    lines.append(' '.join(current))
                    current = []
            if current:
                lines.append(' '.join(current))
            
            for li, line in enumerate(lines[:3]):
                y = 0.62 - li * 0.08
                ax.text(0.5, y, line, fontsize=30, fontweight='bold',
                        ha='center', va='center', color='white', alpha=tp)
        
        # Bottom stat reminder
        if p > 0.4:
            bp = ease_out_cubic(min((p - 0.4) * 2, 1.0))
            val = primary['latest_value']
            unit = primary['unit']
            if unit == '%': vs = f"{val:.1f}%"
            elif unit in ('$', '$/gallon'): vs = f"${val:,.2f}"
            elif unit == 'millions $': vs = f"${val/1e6:.1f}T" if val >= 1e6 else f"${val/1000:,.0f}B"
            elif unit == 'billions $': vs = f"${val/1000:.1f}T" if val >= 1000 else f"${val:,.0f}B"
            else: vs = f"{val:,.1f}"
            
            ax.text(0.5, 0.25, vs, fontsize=44, fontweight='bold',
                    ha='center', color=accent, alpha=bp * 0.7)
            ax.text(0.5, 0.17, primary['name'], fontsize=16,
                    ha='center', color=COLORS['text_secondary'], alpha=bp * 0.5)
        
        draw_watermark(ax)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=DPI)
        plt.close(fig)
    
    out = os.path.join(base_dir, "scene_05_insight.mp4")
    frames_to_video(d, out)
    shutil.rmtree(d)
    return out


def render_scene_close(script_data, base_dir, duration_sec=12):
    """Scene 6: CLOSE — subscribe CTA with brand outro."""
    print("  Scene 6: Closing...")
    d = os.path.join(base_dir, "f_close")
    os.makedirs(d, exist_ok=True)
    
    accent = COLORS['accent_teal']
    n_frames = duration_sec * RENDER_FPS
    
    for i in range(n_frames):
        p = i / (n_frames - 1)
        fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        
        draw_grid_bg(ax, accent, alpha=glow_alpha(0.04, p), spacing=0.05, t=i)
        draw_particles(ax, n=30, t=i, color=accent)
        
        # Brand name
        brand_a = ease_out_cubic(min(p * 2.5, 1.0))
        ax.text(0.5, 0.58, "THE MONEY MAP", fontsize=52, fontweight='bold',
                ha='center', color='white', alpha=brand_a)
        
        # Glowing underline
        if p > 0.15:
            gp = ease_out_cubic(min((p - 0.15) * 3, 1.0))
            hw = 0.22 * gp
            ax.plot([0.5 - hw, 0.5 + hw], [0.49, 0.49],
                    color=accent, lw=3, alpha=0.8 * gp, solid_capstyle='round')
            ax.plot([0.5 - hw, 0.5 + hw], [0.49, 0.49],
                    color=accent, lw=14, alpha=0.1 * gp, solid_capstyle='round')
        
        # Subscribe CTA
        if p > 0.25:
            cp = ease_out_cubic(min((p - 0.25) * 2.5, 1.0))
            ax.text(0.5, 0.40, "Subscribe for weekly data-driven analysis",
                    fontsize=20, ha='center', color=accent, alpha=cp)
        
        # "See you in the next one"
        if p > 0.5:
            sp = ease_out_cubic(min((p - 0.5) * 2, 1.0))
            ax.text(0.5, 0.30, "See you in the next one.", fontsize=16,
                    ha='center', color=COLORS['text_secondary'], alpha=sp * 0.6)
        
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=DPI)
        plt.close(fig)
    
    out = os.path.join(base_dir, "scene_06_close.mp4")
    frames_to_video(d, out)
    shutil.rmtree(d)
    return out


def render_broll_placeholder(base_dir, broll_name, duration_sec=6, accent_color=None):
    """Render a placeholder scene for where b-roll will be inserted."""
    # B-roll clips will replace these in the final assembly
    d = os.path.join(base_dir, f"f_broll_{broll_name}")
    os.makedirs(d, exist_ok=True)
    
    accent = accent_color or COLORS['accent_teal']
    n_frames = duration_sec * RENDER_FPS
    
    for i in range(n_frames):
        p = i / (n_frames - 1)
        fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
        fig.patch.set_facecolor(COLORS['bg_dark'])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        draw_grid_bg(ax, accent, alpha=0.05, t=i)
        draw_particles(ax, n=40, t=i, color=accent)
        draw_watermark(ax)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(d, f"frame_{i:04d}.png"), facecolor=fig.get_facecolor(), dpi=DPI)
        plt.close(fig)
    
    out = os.path.join(base_dir, f"broll_{broll_name}.mp4")
    frames_to_video(d, out)
    shutil.rmtree(d)
    return out


def render_episode(ep_num, script_path, output_dir):
    """Render a complete enhanced episode."""
    print(f"\n{'='*60}")
    print(f"RENDERING EPISODE {ep_num}")
    print(f"{'='*60}")
    
    with open(script_path) as f:
        script_data = json.load(f)
    
    print(f"Title: {script_data['title']}")
    
    base_dir = os.path.join(output_dir, f"ep{ep_num}_v2_render")
    os.makedirs(base_dir, exist_ok=True)
    
    # Render all scenes
    scenes = []
    scenes.append(render_scene_cold_open(script_data, base_dir, duration_sec=6))
    scenes.append(render_scene_hook(script_data, base_dir, duration_sec=18))
    scenes.append(render_scene_chart(script_data, base_dir, duration_sec=55))
    scenes.append(render_scene_context(script_data, base_dir, duration_sec=40))
    scenes.append(render_scene_insight(script_data, base_dir, duration_sec=35))
    scenes.append(render_scene_close(script_data, base_dir, duration_sec=12))
    
    # Concatenate scenes
    concat_file = os.path.join(base_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for s in scenes:
            f.write(f"file '{s}'\n")
    
    silent = os.path.join(base_dir, "silent.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", silent
    ], capture_output=True, text=True, timeout=120, check=True)
    
    # Mix with voiceover
    vo_path = f'/home/user/workspace/the-money-map/data/ep{ep_num}_v2/voiceover.mp3'
    final_path = os.path.join(output_dir, f"ep{ep_num}_v2_final.mp4")
    
    if os.path.exists(vo_path):
        subprocess.run([
            "ffmpeg", "-y", "-i", silent, "-i", vo_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0", "-shortest", final_path
        ], capture_output=True, text=True, timeout=120, check=True)
    else:
        shutil.copy2(silent, final_path)
    
    # Get info
    sz = os.path.getsize(final_path) / (1024 * 1024)
    dur_result = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", final_path
    ], capture_output=True, text=True)
    dur = dur_result.stdout.strip()
    
    print(f"\n  Final: {final_path}")
    print(f"  Size: {sz:.1f} MB")
    print(f"  Duration: {dur}s")
    
    # Cleanup render dir
    shutil.rmtree(base_dir)
    
    return final_path


if __name__ == "__main__":
    import sys
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    script_path = f'/home/user/workspace/the-money-map/data/ep{ep}_v2/script.json'
    output_dir = '/home/user/workspace/the-money-map/output'
    os.makedirs(output_dir, exist_ok=True)
    render_episode(ep, script_path, output_dir)
