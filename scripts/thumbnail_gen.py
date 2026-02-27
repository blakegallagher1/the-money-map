"""
Generates YouTube thumbnails (1280x720) for each episode.
Dark cinematic style matching video aesthetic.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import sys

sys.path.insert(0, '/home/user/workspace/the-money-map')
from config.settings import COLORS


def generate_thumbnail(script_data, output_path):
    """Generate a 1280x720 YouTube thumbnail from script data."""
    primary = script_data['primary_metric']
    val = primary['latest_value']
    unit = primary['unit']
    yoy = primary['yoy_pct']
    name = primary['name']
    
    if unit == '%':
        display_val = f"{val:.1f}%"
    elif unit in ('$', '$/gallon'):
        display_val = f"${val:,.2f}"
    elif unit == 'millions $':
        display_val = f"${val/1e6:.1f}T" if val >= 1e6 else f"${val/1000:,.0f}B"
    elif unit == 'billions $':
        display_val = f"${val/1000:.1f}T" if val >= 1000 else f"${val:,.0f}B"
    else:
        display_val = f"{val:,.1f}"
    
    is_neg = yoy < 0
    accent = COLORS['negative'] if is_neg else COLORS['positive']
    arrow = "▼" if is_neg else "▲"
    
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.patch.set_facecolor(COLORS['bg_dark'])
    
    for x in np.arange(0, 1.1, 0.04):
        ax.axvline(x, color=accent, alpha=0.04, lw=0.3)
    for y in np.arange(0, 1.1, 0.04):
        ax.axhline(y, color=accent, alpha=0.04, lw=0.3)
    
    stripe = patches.Rectangle((0, 0), 0.015, 1, linewidth=0,
                                facecolor=accent, alpha=0.9)
    ax.add_patch(stripe)
    
    ax.text(0.5, 0.58, display_val, fontsize=110, fontweight='bold',
           ha='center', va='center', color='white',
           fontfamily='sans-serif')
    
    ax.text(0.5, 0.33, name.upper(), fontsize=28, fontweight='bold',
           ha='center', va='center', color=COLORS['text_secondary'],
           fontfamily='sans-serif')
    
    badge_text = f" {arrow} {abs(yoy):.1f}% YoY "
    ax.text(0.5, 0.2, badge_text, fontsize=24, fontweight='bold',
           ha='center', va='center', color='white',
           fontfamily='sans-serif',
           bbox=dict(boxstyle='round,pad=0.4', facecolor=accent, 
                    edgecolor='none', alpha=0.9))
    
    ax.text(0.95, 0.06, "THE MONEY MAP", fontsize=14, ha='right',
           color=COLORS['accent_teal'], alpha=0.8, fontweight='bold',
           fontfamily='sans-serif')
    
    ax.text(0.05, 0.06, "Source: FRED", fontsize=10, ha='left',
           color=COLORS['text_muted'], alpha=0.5)
    
    plt.tight_layout(pad=0)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), dpi=100,
               bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    return output_path


if __name__ == "__main__":
    import json
    with open('/home/user/workspace/the-money-map/data/latest_script.json') as f:
        script_data = json.load(f)
    out = generate_thumbnail(script_data, '/home/user/workspace/the-money-map/output/thumbnail.png')
    print(f"Thumbnail saved: {out}")
    sz = os.path.getsize(out)
    print(f"Size: {sz/1024:.0f} KB")
