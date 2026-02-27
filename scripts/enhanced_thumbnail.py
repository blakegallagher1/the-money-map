"""
Enhanced Thumbnail Generator for The Money Map V2
Designed for 8%+ CTR based on YouTube best practices:
- High contrast, bold 3-5 word text overlay
- Emotion/tension via color (red = danger, green = opportunity)
- Curiosity gap — big number + emotional reaction framing
- 1280x720 (YouTube standard)
- Dark cinematic style with gradient overlays
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


# Thumbnail-specific titles — punchier than video titles, max 5 words
THUMB_HEADLINES = {
    "personal_savings_rate": "AMERICANS\nARE BROKE",
    "mortgage_rate_30yr": "RATES JUST\nCRASHED",
    "national_debt": "$37 TRILLION\nIN DEBT", 
    "gas_price": "GAS IS\nCHEAP AGAIN",
    "gdp_growth": "RECESSION\nINCOMING?",
}

# Color schemes per topic (primary accent, secondary, mood)
THUMB_SCHEMES = {
    "personal_savings_rate": {"accent": "#FF4444", "glow": "#FF6B6B", "mood": "danger"},
    "mortgage_rate_30yr": {"accent": "#22C55E", "glow": "#4ADE80", "mood": "opportunity"},
    "national_debt": {"accent": "#FF4444", "glow": "#FF6B6B", "mood": "danger"},
    "gas_price": {"accent": "#FFB84D", "glow": "#FCD34D", "mood": "caution"},
    "gdp_growth": {"accent": "#FF4444", "glow": "#FF6B6B", "mood": "danger"},
}


def generate_enhanced_thumbnail(script_data, output_path):
    """Generate a high-CTR 1280x720 YouTube thumbnail."""
    primary = script_data['primary_metric']
    key = primary['key']
    val = primary['latest_value']
    unit = primary['unit']
    yoy = primary['yoy_pct']
    
    # Format display value
    if unit == '%': display_val = f"{val:.1f}%"
    elif unit in ('$', '$/gallon'): display_val = f"${val:,.2f}"
    elif unit == 'millions $': display_val = f"${val/1e6:.1f}T" if val >= 1e6 else f"${val/1000:,.0f}B"
    elif unit == 'billions $': display_val = f"${val/1000:.1f}T" if val >= 1000 else f"${val:,.0f}B"
    else: display_val = f"{val:,.1f}"
    
    scheme = THUMB_SCHEMES.get(key, {"accent": "#FF4444", "glow": "#FF6B6B", "mood": "danger"})
    headline = THUMB_HEADLINES.get(key, f"{primary['name'].upper()}\nCHANGED")
    accent = scheme['accent']
    glow = scheme['glow']
    is_neg = yoy < 0
    arrow = "▼" if is_neg else "▲"
    
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    
    # Background — dark with subtle gradient
    fig.patch.set_facecolor('#06060A')
    
    # Diagonal gradient overlay (dark to accent tint)
    for i in range(50):
        t = i / 49
        rect = patches.Rectangle((0, t * 0.02), 1, 0.021,
                                  facecolor=accent, alpha=0.008 * (1 - t))
        ax.add_patch(rect)
    
    # Grid background — very subtle
    for x in np.arange(0, 1.1, 0.05):
        ax.axvline(x, color=accent, alpha=0.03, lw=0.3)
    for y in np.arange(0, 1.1, 0.05):
        ax.axhline(y, color=accent, alpha=0.03, lw=0.3)
    
    # LEFT SIDE: Big dramatic stat
    # Stat number — HUGE, left-aligned
    ax.text(0.06, 0.62, display_val, fontsize=95, fontweight='bold',
            ha='left', va='center', color='white', fontfamily='sans-serif')
    
    # YoY change — colored badge below stat
    badge_color = '#FF4444' if is_neg else '#22C55E'
    badge_text = f" {arrow} {abs(yoy):.1f}% "
    ax.text(0.06, 0.38, badge_text, fontsize=28, fontweight='bold',
            ha='left', va='center', color='white',
            bbox=dict(boxstyle='round,pad=0.35', facecolor=badge_color,
                      edgecolor='none', alpha=0.95))
    
    # RIGHT SIDE: Bold headline text
    headline_lines = headline.split('\n')
    for li, line in enumerate(headline_lines):
        y = 0.68 - li * 0.18
        # Text shadow/glow
        ax.text(0.96, y - 0.005, line, fontsize=58, fontweight='bold',
                ha='right', va='center', color=glow, alpha=0.15,
                fontfamily='sans-serif')
        # Main text
        ax.text(0.96, y, line, fontsize=58, fontweight='bold',
                ha='right', va='center', color=accent,
                fontfamily='sans-serif')
    
    # Accent stripe — left edge  
    stripe = patches.Rectangle((0, 0), 0.012, 1, facecolor=accent, alpha=0.95)
    ax.add_patch(stripe)
    
    # Bottom accent line
    ax.plot([0.06, 0.94], [0.22, 0.22], color=accent, lw=2, alpha=0.3)
    
    # Brand mark — bottom right
    ax.text(0.94, 0.08, "THE MONEY MAP", fontsize=15, ha='right',
            color=COLORS['accent_teal'], alpha=0.9, fontweight='bold')
    
    # Source — bottom left (very small)
    ax.text(0.06, 0.08, "FRED Data", fontsize=10, ha='left',
            color=COLORS['text_muted'], alpha=0.4)
    
    plt.tight_layout(pad=0)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), dpi=100,
                bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    return output_path


if __name__ == "__main__":
    import json
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    with open(f'/home/user/workspace/the-money-map/data/ep{ep}_v2/script.json') as f:
        script_data = json.load(f)
    out = generate_enhanced_thumbnail(script_data, f'/home/user/workspace/the-money-map/output/ep{ep}_v2_thumbnail.png')
    print(f"Thumbnail saved: {out}")
    sz = os.path.getsize(out)
    print(f"Size: {sz/1024:.0f} KB")
