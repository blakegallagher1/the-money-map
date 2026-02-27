# scripts/thumbnail_gen.py
# ─────────────────────────────────────────────
# Generates thumbnails with key stat and YoY change
# ─────────────────────────────────────────────

import os
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw
from config.settings import (
    COLOR_BG, COLOR_ACCENT, COLOR_POSITIVE, COLOR_NEGATIVE,
    COLOR_TEXT, COLOR_SUBTEXT, OUTPUT_DIR
)
from scripts.video_renderer import hex_to_rgb, make_bg_array, draw_grid, _load_font


def generate_thumbnail(
        title: str,
        indicator_label: str,
        latest_value: str,
        yoy_pct: float,
        out_path: str = None) -> str:
    """
    Generate a 1280x720 YouTube thumbnail.
    Returns the file path.
    """
    W, H = 1280, 720
    bg = draw_grid(make_bg_array(W, H), spacing=60, alpha=0.06)
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img)

    # Top accent bar
    draw.rectangle([(0, 0), (W, 8)], fill=hex_to_rgb(COLOR_ACCENT))

    # Brand label
    font_brand = _load_font(28)
    draw.text((40, 24), "THE MONEY MAP", font=font_brand, fill=hex_to_rgb(COLOR_ACCENT))

    # Main title (large, bold)
    font_title = _load_font(64, bold=True)
    margin = 60
    lines = []
    words = title.split()
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font_title) <= W - margin * 2:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = 90
    for line in lines[:3]:  # max 3 lines
        draw.text((margin, y), line, font=font_title, fill=hex_to_rgb(COLOR_TEXT))
        y += 76

    # Big stat box (right side)
    box_x, box_y = W - 420, H // 2 - 60
    box_w, box_h = 380, 200
    draw.rounded_rectangle([(box_x, box_y), (box_x + box_w, box_y + box_h)],
                           radius=20, fill=(10, 16, 40))
    draw.rounded_rectangle([(box_x, box_y), (box_x + box_w, box_y + 6)],
                           radius=3, fill=hex_to_rgb(COLOR_ACCENT))

    font_val = _load_font(80, bold=True)
    font_yoy = _load_font(38)
    font_lbl = _load_font(24)

    vw = draw.textlength(latest_value, font=font_val)
    draw.text((box_x + (box_w - vw) // 2, box_y + 18), latest_value,
              font=font_val, fill=hex_to_rgb(COLOR_TEXT))

    yoy_color = COLOR_POSITIVE if yoy_pct >= 0 else COLOR_NEGATIVE
    yoy_str = f"{'▲' if yoy_pct >= 0 else '▼'} {abs(yoy_pct):.1f}% YoY"
    yw = draw.textlength(yoy_str, font=font_yoy)
    draw.text((box_x + (box_w - yw) // 2, box_y + 112),
              yoy_str, font=font_yoy, fill=hex_to_rgb(yoy_color))

    lw = draw.textlength(indicator_label, font=font_lbl)
    draw.text((box_x + (box_w - lw) // 2, box_y + 162),
              indicator_label, font=font_lbl, fill=hex_to_rgb(COLOR_SUBTEXT))

    # Bottom bar
    draw.rectangle([(0, H - 8), (W, H)], fill=hex_to_rgb(COLOR_ACCENT))

    # Save
    if not out_path:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(OUTPUT_DIR, f"thumbnail_{ts}.png")

    img.save(out_path)
    print(f"Thumbnail saved to {out_path}")
    return out_path


if __name__ == "__main__":
    generate_thumbnail(
        title="Mortgage Rates Hit 6.81%: Is Housing Finally Cooling Down?",
        indicator_label="30-Year Mortgage Rate",
        latest_value="6.81%",
        yoy_pct=-3.8,
    )
