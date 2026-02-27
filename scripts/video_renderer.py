# scripts/video_renderer.py
# ─────────────────────────────────────────────
# Core video rendering utilities shared by episode_renderer and render_pilot
# ─────────────────────────────────────────────

import os
import sys
import math
import datetime
import tempfile
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip
)
from config.settings import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS,
    COLOR_BG, COLOR_ACCENT, COLOR_POSITIVE, COLOR_NEGATIVE,
    COLOR_TEXT, COLOR_SUBTEXT, COLOR_GRID, COLOR_NEUTRAL, OUTPUT_DIR
)

# ── Color helpers ─────────────────────────────

def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


BG_RGB       = hex_to_rgb(COLOR_BG)
ACCENT_RGB   = hex_to_rgb(COLOR_ACCENT)
POS_RGB      = hex_to_rgb(COLOR_POSITIVE)
NEG_RGB      = hex_to_rgb(COLOR_NEGATIVE)
TEXT_RGB     = hex_to_rgb(COLOR_TEXT)
SUBTEXT_RGB  = hex_to_rgb(COLOR_SUBTEXT)
GRID_RGB     = hex_to_rgb(COLOR_GRID)
NEUTRAL_RGB  = hex_to_rgb(COLOR_NEUTRAL)

# ── Font loading ──────────────────────────────

def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try to load a system font; fall back to PIL default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── Background ────────────────────────────────

def make_bg_array(w: int = VIDEO_WIDTH, h: int = VIDEO_HEIGHT) -> np.ndarray:
    """Create a dark navy gradient background as a numpy array."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    top = np.array([10, 14, 26], dtype=np.float32)
    bot = np.array([5, 8, 18],  dtype=np.float32)
    for y in range(h):
        t = y / h
        img[y, :] = (top * (1 - t) + bot * t).astype(np.uint8)
    return img


# ── Grid overlay ──────────────────────────────

def draw_grid(img: np.ndarray, spacing: int = 80, alpha: float = 0.08) -> np.ndarray:
    """Draw subtle grid lines on a background array."""
    overlay = img.copy().astype(np.float32)
    color = np.array([26, 32, 53], dtype=np.float32)
    h, w = img.shape[:2]
    for x in range(0, w, spacing):
        overlay[:, x] = color
    for y in range(0, h, spacing):
        overlay[y, :] = color
    return (img.astype(np.float32) * (1 - alpha) + overlay * alpha).astype(np.uint8)


# ── PIL image → MoviePy clip ──────────────────

def pil_to_clip(pil_img: Image.Image, duration: float) -> ImageClip:
    arr = np.array(pil_img.convert("RGB"))
    return ImageClip(arr).set_duration(duration)


# ── Text wrapping ─────────────────────────────

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int,
              draw: ImageDraw.ImageDraw) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        w = draw.textlength(test, font=font)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ══════════════════════════════════════════════
# Scene builders
# ══════════════════════════════════════════════

def build_title_card(
        title: str,
        indicator_label: str,
        latest_value: str,
        yoy_pct: float,
        duration: float = 4.0) -> ImageClip:
    """Scene 1 — full-screen title card."""
    bg = draw_grid(make_bg_array())
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img)
    W, H = VIDEO_WIDTH, VIDEO_HEIGHT

    # Accent bar at top
    draw.rectangle([(0, 0), (W, 6)], fill=ACCENT_RGB)

    # "THE MONEY MAP" brand watermark
    font_brand = _load_font(28)
    draw.text((60, 30), "THE MONEY MAP", font=font_brand, fill=ACCENT_RGB)

    # Main title
    font_title = _load_font(72, bold=True)
    margin = 100
    lines = wrap_text(title, font_title, W - margin * 2, draw)
    y = H // 2 - len(lines) * 80 // 2 - 60
    for line in lines:
        tw = draw.textlength(line, font=font_title)
        draw.text(((W - tw) // 2, y), line, font=font_title, fill=TEXT_RGB)
        y += 88

    # Key stat pill
    stat_str = f"{latest_value}"
    yoy_color = POS_RGB if yoy_pct >= 0 else NEG_RGB
    yoy_str = f"{'▲' if yoy_pct >= 0 else '▼'} {abs(yoy_pct):.1f}% YoY"

    font_stat = _load_font(56, bold=True)
    font_yoy  = _load_font(36)
    stat_w = draw.textlength(stat_str, font=font_stat)
    yoy_w  = draw.textlength(yoy_str, font=font_yoy)
    pill_w = max(stat_w, yoy_w) + 60
    pill_h = 120
    pill_x = (W - pill_w) // 2
    pill_y = y + 20
    draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)],
        radius=16, fill=(15, 20, 40)
    )
    draw.text((pill_x + 30, pill_y + 10),  stat_str, font=font_stat, fill=TEXT_RGB)
    draw.text((pill_x + 30, pill_y + 72),  yoy_str,  font=font_yoy,  fill=yoy_color)

    # Bottom accent bar
    draw.rectangle([(0, H - 6), (W, H)], fill=ACCENT_RGB)

    return pil_to_clip(img, duration)


def build_stat_callout(
        label: str,
        value: str,
        yoy_pct: float,
        context_text: str,
        duration: float = 5.0) -> ImageClip:
    """Scene 2 — large stat callout with supporting text."""
    bg = draw_grid(make_bg_array())
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img)
    W, H = VIDEO_WIDTH, VIDEO_HEIGHT

    draw.rectangle([(0, 0), (W, 6)], fill=ACCENT_RGB)

    font_label  = _load_font(36)
    font_value  = _load_font(120, bold=True)
    font_yoy    = _load_font(48)
    font_ctx    = _load_font(32)

    # Label
    lw = draw.textlength(label, font=font_label)
    draw.text(((W - lw) // 2, 120), label, font=font_label, fill=tuple(SUBTEXT_RGB))

    # Big value
    vw = draw.textlength(value, font=font_value)
    draw.text(((W - vw) // 2, 180), value, font=font_value, fill=TEXT_RGB)

    # YoY badge
    yoy_color = POS_RGB if yoy_pct >= 0 else NEG_RGB
    yoy_str = f"{'▲' if yoy_pct >= 0 else '▼'} {abs(yoy_pct):.1f}% year-over-year"
    yw = draw.textlength(yoy_str, font=font_yoy)
    draw.text(((W - yw) // 2, 350), yoy_str, font=font_yoy, fill=yoy_color)

    # Divider
    draw.rectangle([(W // 4, 440), (3 * W // 4, 443)], fill=ACCENT_RGB)

    # Context text
    lines = wrap_text(context_text, font_ctx, W - 300, draw)
    y = 470
    for line in lines:
        lw2 = draw.textlength(line, font=font_ctx)
        draw.text(((W - lw2) // 2, y), line, font=font_ctx, fill=tuple(SUBTEXT_RGB))
        y += 44

    draw.rectangle([(0, H - 6), (W, H)], fill=ACCENT_RGB)
    return pil_to_clip(img, duration)


def build_chart_clip(
        dates: list,
        values: list,
        label: str,
        unit: str,
        yoy_pct: float,
        duration: float = 8.0,
        fps: int = FPS) -> object:
    """Scene 3 — animated line chart (frames rendered as video)."""
    from moviepy.editor import VideoClip

    W, H = VIDEO_WIDTH, VIDEO_HEIGHT
    n = len(values)
    total_frames = int(duration * fps)

    # Pre-compute chart geometry
    pad_l, pad_r, pad_t, pad_b = 160, 80, 120, 140
    chart_w = W - pad_l - pad_r
    chart_h = H - pad_t - pad_b
    v_min = min(values) * 0.95
    v_max = max(values) * 1.05
    v_range = v_max - v_min or 1.0

    def val_to_y(v):
        return pad_t + chart_h - int((v - v_min) / v_range * chart_h)

    def idx_to_x(i):
        return pad_l + int(i / max(n - 1, 1) * chart_w)

    bg_base = draw_grid(make_bg_array())

    def make_frame(t):
        progress = min(t / (duration * 0.75), 1.0)   # animate over first 75%
        points_to_draw = max(2, int(progress * n))

        img = Image.fromarray(bg_base.copy())
        draw = ImageDraw.Draw(img)

        font_label = _load_font(32, bold=True)
        font_axis  = _load_font(22)

        # Title
        draw.rectangle([(0, 0), (W, 6)], fill=ACCENT_RGB)
        tw = draw.textlength(label, font=font_label)
        draw.text(((W - tw) // 2, 30), label, font=font_label, fill=TEXT_RGB)

        # Y-axis gridlines + labels
        for i in range(5):
            v = v_min + (v_range * i / 4)
            y = val_to_y(v)
            draw.rectangle([(pad_l, y), (W - pad_r, y + 1)], fill=GRID_RGB)
            label_str = f"{v:.1f}{unit}"
            draw.text((pad_l - 10 - draw.textlength(label_str, font=font_axis), y - 11),
                      label_str, font=font_axis, fill=tuple(SUBTEXT_RGB))

        # X-axis date labels (show ~6)
        step = max(1, n // 6)
        for i in range(0, n, step):
            x = idx_to_x(i)
            date_label = dates[i][:7]   # YYYY-MM
            draw.text((x - 20, H - pad_b + 10), date_label, font=font_axis, fill=tuple(SUBTEXT_RGB))

        # Animated line
        pts = [(idx_to_x(i), val_to_y(values[i])) for i in range(points_to_draw)]
        if len(pts) >= 2:
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i + 1]], fill=ACCENT_RGB, width=3)

        # Dot at current tip
        if pts:
            cx, cy = pts[-1]
            draw.ellipse([(cx - 6, cy - 6), (cx + 6, cy + 6)], fill=ACCENT_RGB)

        # YoY badge (appears at 50% progress)
        if progress > 0.5:
            yoy_color = COLOR_POSITIVE if yoy_pct >= 0 else COLOR_NEGATIVE
            yoy_str = f"YoY: {'▲' if yoy_pct >= 0 else '▼'}{abs(yoy_pct):.1f}%"
            font_yoy = _load_font(36, bold=True)
            yw = draw.textlength(yoy_str, font=font_yoy)
            bx, by = W - pad_r - yw - 40, pad_t + 20
            draw.rounded_rectangle([(bx - 10, by - 8), (bx + yw + 10, by + 44)],
                                   radius=8, fill=(15, 20, 40))
            draw.text((bx, by), yoy_str, font=font_yoy, fill=hex_to_rgb(yoy_color))

        draw.rectangle([(0, H - 6), (W, H)], fill=ACCENT_RGB)
        return np.array(img.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(fps)


def build_comparison_dashboard(
        main_item: dict,
        related: list,
        duration: float = 6.0) -> ImageClip:
    """Scene 4 — comparison dashboard showing main + related indicators."""
    bg = draw_grid(make_bg_array())
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img)
    W, H = VIDEO_WIDTH, VIDEO_HEIGHT

    draw.rectangle([(0, 0), (W, 6)], fill=ACCENT_RGB)

    font_title = _load_font(40, bold=True)
    font_label = _load_font(28)
    font_value = _load_font(52, bold=True)
    font_yoy   = _load_font(28)

    category = main_item.get("category", "Indicators")
    title_text = f"{category} Dashboard"
    tw = draw.textlength(title_text, font=font_title)
    draw.text(((W - tw) // 2, 30), title_text, font=font_title, fill=TEXT_RGB)

    # Build card list: main + up to 3 related
    cards = [{"label": main_item["label"], "latest": main_item["latest"],
              "unit": main_item["unit"], "yoy_pct": main_item["yoy_pct"],
              "is_main": True}]
    for r in related[:3]:
        cards.append({"label": r["label"], "latest": r["latest"],
                      "unit": r["unit"], "yoy_pct": r["yoy_pct"], "is_main": False})

    n_cards = len(cards)
    card_w = (W - 120) // n_cards - 20
    card_h = 340
    start_y = 130
    gap = 20
    total_w = n_cards * card_w + (n_cards - 1) * gap
    start_x = (W - total_w) // 2

    for i, card in enumerate(cards):
        x = start_x + i * (card_w + gap)
        y = start_y

        # Card background
        bg_color = (15, 22, 48) if card["is_main"] else (10, 16, 34)
        draw.rounded_rectangle([(x, y), (x + card_w, y + card_h)],
                               radius=16, fill=bg_color)
        if card["is_main"]:
            draw.rounded_rectangle([(x, y), (x + card_w, y + 4)],
                                   radius=2, fill=ACCENT_RGB)

        # Label
        label_lines = wrap_text(card["label"], font_label, card_w - 30, draw)
        ly = y + 20
        for ll in label_lines[:2]:
            draw.text((x + 15, ly), ll, font=font_label, fill=tuple(SUBTEXT_RGB))
            ly += 36

        # Value
        val_str = f"{card['latest']}{card['unit']}"
        draw.text((x + 15, ly + 10), val_str, font=font_value, fill=TEXT_RGB)

        # YoY
        yoy_c = POS_RGB if card["yoy_pct"] >= 0 else NEG_RGB
        yoy_s = f"{'▲' if card['yoy_pct'] >= 0 else '▼'} {abs(card['yoy_pct']):.1f}%"
        draw.text((x + 15, ly + 80), yoy_s, font=font_yoy, fill=yoy_c)

    # Source attribution
    font_small = _load_font(20)
    draw.text((60, H - 50), "Source: Federal Reserve Bank of St. Louis (FRED)",
              font=font_small, fill=tuple(SUBTEXT_RGB))

    draw.rectangle([(0, H - 6), (W, H)], fill=ACCENT_RGB)
    return pil_to_clip(img, duration)


def build_closing_card(
        channel_name: str = "The Money Map",
        cta: str = "Like & Subscribe for weekly economic insights",
        duration: float = 4.0) -> ImageClip:
    """Scene 5 — closing card with CTA."""
    bg = draw_grid(make_bg_array())
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img)
    W, H = VIDEO_WIDTH, VIDEO_HEIGHT

    draw.rectangle([(0, 0), (W, 6)], fill=ACCENT_RGB)

    font_logo = _load_font(96, bold=True)
    font_sub  = _load_font(36)
    font_cta  = _load_font(32)

    # Logo
    lw = draw.textlength(channel_name, font=font_logo)
    draw.text(((W - lw) // 2, H // 2 - 140), channel_name, font=font_logo, fill=TEXT_RGB)

    # Subtitle
    sub = "Weekly Economic Analysis"
    sw = draw.textlength(sub, font=font_sub)
    draw.text(((W - sw) // 2, H // 2 - 20), sub, font=font_sub, fill=tuple(ACCENT_RGB))

    # Divider
    draw.rectangle([(W // 3, H // 2 + 40), (2 * W // 3, H // 2 + 43)], fill=GRID_RGB)

    # CTA
    cta_w = draw.textlength(cta, font=font_cta)
    draw.text(((W - cta_w) // 2, H // 2 + 60), cta, font=font_cta, fill=tuple(SUBTEXT_RGB))

    draw.rectangle([(0, H - 6), (W, H)], fill=ACCENT_RGB)
    return pil_to_clip(img, duration)
