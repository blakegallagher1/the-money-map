"""Build a narrated, section-based video episode from a JSON episode spec."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.settings import COLORS, TTS_INSTRUCTIONS, TTS_VOICE
from scripts.tts_generator import generate_voiceover

LOGGER = logging.getLogger("custom_episode_builder")
DATA_DIR = REPO_ROOT / "data"
OUTPUT_DIR = REPO_ROOT / "output"
SORA_DIR = REPO_ROOT / "assets" / "sora"
FIG_WIDTH = 25.6
FIG_HEIGHT = 14.4
FIG_DPI = 100
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30
PANEL_ALPHA = 0.92
HIGHLIGHT_ALPHA = 0.16


def load_episode_spec(path: Path) -> dict[str, Any]:
    """Load and validate an episode specification file."""
    spec = json.loads(path.read_text())
    required_keys = {"slug", "title", "sections"}
    missing = required_keys - spec.keys()
    if missing:
        raise ValueError(f"Episode spec missing keys: {sorted(missing)}")
    if not spec["sections"]:
        raise ValueError("Episode spec must include at least one section")
    for section in spec["sections"]:
        needed = {"id", "layout", "headline", "narration"}
        absent = needed - section.keys()
        if absent:
            raise ValueError(
                f"Section {section.get('id', '<unknown>')} missing keys: {sorted(absent)}"
            )
    return spec


def build_full_script(spec: dict[str, Any]) -> str:
    """Concatenate all section narration into a single script."""
    return "\n\n".join(section["narration"].strip() for section in spec["sections"])


def color_for(section: dict[str, Any]) -> str:
    """Resolve a section accent key to a hex color."""
    return COLORS.get(section.get("accent", "accent_teal"), COLORS["accent_teal"])


def run_ffmpeg(args: list[str]) -> None:
    """Run an ffmpeg or ffprobe command and raise on failure."""
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg command failed")


def media_duration(path: Path) -> float:
    """Return media duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def resolve_visual_clips(spec: dict[str, Any], section: dict[str, Any]) -> list[Path]:
    """Resolve existing Sora clip paths for a section."""
    clip_paths: list[Path] = []
    for clip_id in section.get("visual_clips", []):
        clip_path = SORA_DIR / spec["slug"] / f"{clip_id}.mp4"
        if clip_path.exists():
            clip_paths.append(clip_path)
        else:
            LOGGER.warning("Missing visual clip for %s: %s", section["id"], clip_path)
    return clip_paths


def wrap_text(text: str, width: int) -> str:
    """Wrap text without importing additional dependencies."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for word in words:
        projected = length + len(word) + (1 if current else 0)
        if current and projected > width:
            lines.append(" ".join(current))
            current = [word]
            length = len(word)
        else:
            current.append(word)
            length = projected
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def narration_excerpt(text: str, word_limit: int = 28) -> str:
    """Return a short excerpt suitable for on-screen support copy."""
    words = text.split()
    excerpt = " ".join(words[:word_limit]).strip()
    if len(words) > word_limit:
        excerpt += " ..."
    return excerpt


def write_full_script(spec: dict[str, Any], episode_dir: Path) -> Path:
    """Persist the combined narration as a plain-text script."""
    script_path = episode_dir / "voiceover_script.txt"
    script_path.write_text(build_full_script(spec) + "\n")
    return script_path


def add_background(ax: plt.Axes, accent: str) -> None:
    """Render a dark branded background with a soft accent grid."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(COLORS["bg_dark"])
    for offset in [0.0, 0.18, 0.36, 0.54, 0.72, 0.9]:
        ax.axhline(offset, color=accent, alpha=0.05, linewidth=1.0)
        ax.axvline(offset, color=accent, alpha=0.04, linewidth=1.0)
    ax.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, color=COLORS["bg_dark"], alpha=0.88))
    ax.add_patch(Rectangle((0.0, 0.84), 1.0, 0.16, color=accent, alpha=0.08))
    ax.add_patch(Rectangle((0.0, 0.0), 1.0, 0.12, color=accent, alpha=0.06))


def add_chrome(ax: plt.Axes, section: dict[str, Any], index: int, total: int, accent: str) -> None:
    """Draw the shared header, footer, and progress bar."""
    kicker = section.get("kicker", "THE MONEY MAP")
    ax.text(0.06, 0.92, kicker, fontsize=22, fontweight="bold", color=accent)
    ax.text(0.94, 0.92, "THE MONEY MAP", fontsize=18, ha="right", color=COLORS["text_muted"])
    progress = (index + 1) / total
    ax.add_patch(Rectangle((0.06, 0.08), 0.88, 0.008, color=COLORS["border"], alpha=0.8))
    ax.add_patch(Rectangle((0.06, 0.08), 0.88 * progress, 0.008, color=accent, alpha=0.95))
    ax.text(
        0.94,
        0.055,
        f"{index + 1:02d} / {total:02d}",
        fontsize=15,
        ha="right",
        color=COLORS["text_secondary"],
    )


def add_bullet_panel(ax: plt.Axes, section: dict[str, Any], accent: str) -> None:
    """Draw a right-side bullet panel for section summaries."""
    panel = FancyBboxPatch(
        (0.58, 0.22),
        0.31,
        0.46,
        boxstyle="round,pad=0.018,rounding_size=0.02",
        linewidth=1.4,
        edgecolor=accent,
        facecolor=COLORS["bg_card"],
        alpha=PANEL_ALPHA,
    )
    ax.add_patch(panel)
    y_pos = 0.62
    for bullet in section.get("bullets", [])[:4]:
        ax.text(0.61, y_pos, f"\u2022 {bullet}", fontsize=22, color=COLORS["text_primary"])
        y_pos -= 0.1


def add_matrix(ax: plt.Axes, accent: str, highlight: str | None) -> None:
    """Draw the capacity/temperament quadrant matrix."""
    x0, y0, size = 0.08, 0.22, 0.4
    labels = {
        "preserve": (x0, y0, "Preserve"),
        "expose": (x0 + size / 2, y0, "Expose"),
        "reserve": (x0, y0 + size / 2, "Reserve"),
        "attack": (x0 + size / 2, y0 + size / 2, "Attack"),
    }
    ax.add_patch(Rectangle((x0, y0), size, size, fill=False, edgecolor=COLORS["border"], linewidth=2))
    ax.plot([x0 + size / 2, x0 + size / 2], [y0, y0 + size], color=COLORS["border"], linewidth=2)
    ax.plot([x0, x0 + size], [y0 + size / 2, y0 + size / 2], color=COLORS["border"], linewidth=2)
    for key, (x_pos, y_pos, label) in labels.items():
        if highlight == key:
            ax.add_patch(Rectangle((x_pos, y_pos), size / 2, size / 2, color=accent, alpha=HIGHLIGHT_ALPHA))
        ax.text(x_pos + size / 4, y_pos + size / 4, label.upper(), ha="center", va="center", fontsize=22, fontweight="bold")
    ax.text(x0 + size / 2, y0 + size + 0.05, "CAPACITY", ha="center", fontsize=18, color=COLORS["text_secondary"])
    ax.text(x0 - 0.05, y0 + size / 2, "TEMPERAMENT", rotation=90, va="center", fontsize=18, color=COLORS["text_secondary"])
    ax.text(x0 + 0.08, y0 + size + 0.01, "LOW", fontsize=14, color=COLORS["text_muted"])
    ax.text(x0 + size - 0.02, y0 + size + 0.01, "HIGH", ha="right", fontsize=14, color=COLORS["text_muted"])
    ax.text(x0 - 0.035, y0 + 0.02, "LOW", rotation=90, fontsize=14, color=COLORS["text_muted"])
    ax.text(x0 - 0.035, y0 + size - 0.02, "HIGH", rotation=90, va="top", fontsize=14, color=COLORS["text_muted"])


def render_scene_image(spec: dict[str, Any], section: dict[str, Any], index: int, output_path: Path) -> None:
    """Render a single branded scene image for a section."""
    accent = color_for(section)
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=FIG_DPI)
    add_background(ax, accent)
    add_chrome(ax, section, index, len(spec["sections"]), accent)
    ax.text(0.06, 0.78, wrap_text(section["headline"], 28), fontsize=38, fontweight="bold", color="white", va="top")
    if section.get("quote"):
        ax.text(0.06, 0.62, wrap_text(section["quote"], 34), fontsize=24, color=accent, va="top")

    layout = section["layout"]
    if layout == "framework":
        add_matrix(ax, accent, None)
    elif layout == "quadrant":
        add_matrix(ax, accent, section.get("quadrant"))
    else:
        box = FancyBboxPatch(
            (0.06, 0.26),
            0.42,
            0.17,
            boxstyle="round,pad=0.018,rounding_size=0.02",
            linewidth=1.2,
            edgecolor=accent,
            facecolor=COLORS["bg_card"],
            alpha=PANEL_ALPHA,
        )
        ax.add_patch(box)
        ax.text(
            0.09,
            0.39,
            wrap_text(narration_excerpt(section["narration"]), 40),
            fontsize=18,
            color=COLORS["text_secondary"],
            va="top",
        )

    add_bullet_panel(ax, section, accent)
    plt.tight_layout(pad=0)
    fig.savefig(output_path, facecolor=fig.get_facecolor(), dpi=FIG_DPI)
    plt.close(fig)


def generate_section_audio(section: dict[str, Any], output_path: Path, voice: str, instructions: str) -> Path:
    """Generate voiceover audio for a section narration."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
        handle.write(section["narration"].strip())
        temp_script = Path(handle.name)
    try:
        generate_voiceover(
            script_path=str(temp_script),
            output_path=str(output_path),
            voice=voice,
            instructions=instructions,
        )
    finally:
        temp_script.unlink(missing_ok=True)
    return output_path


def build_scene_clip(image_path: Path, audio_path: Path, output_path: Path) -> float:
    """Build a single section clip with a slow zoom and synced narration."""
    duration = media_duration(audio_path)
    build_section_clip(image_path, audio_path, output_path, duration, [])
    return duration


def section_visual_plan(duration: float, clip_count: int) -> tuple[float, float]:
    """Return intro and b-roll durations for a section."""
    if clip_count <= 0 or duration < 10:
        return duration, 0.0
    intro_duration = min(4.0, max(2.5, duration * 0.12))
    max_broll = min(16.0, 8.0 * clip_count, duration * 0.4)
    broll_duration = min(max_broll, max(0.0, duration - intro_duration - 3.0))
    if broll_duration < 4.0:
        return duration, 0.0
    return intro_duration, broll_duration


def still_video_filter(duration: float) -> str:
    """Return the ffmpeg filter used for animated still-image sections."""
    drift_width = VIDEO_WIDTH + 180
    drift_height = VIDEO_HEIGHT + 100
    x_range = drift_width - VIDEO_WIDTH
    y_range = drift_height - VIDEO_HEIGHT
    safe_duration = max(duration, 0.1)
    return (
        f"scale={drift_width}:{drift_height},"
        f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"
        f"x='({x_range}/2)-({x_range}*0.32*min(t/{safe_duration:.3f},1))':"
        f"y='({y_range}/2)-({y_range}*0.18*min(t/{safe_duration:.3f},1))',"
        "format=yuv420p"
    )


def build_still_video(image_path: Path, output_path: Path, duration: float) -> None:
    """Create a silent video from a still image with subtle camera drift."""
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(image_path),
            "-t",
            f"{duration:.3f}",
            "-filter:v",
            still_video_filter(duration),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-an",
            str(output_path),
        ]
    )


def normalize_video_clip(input_path: Path, output_path: Path, duration: float) -> None:
    """Normalize a video clip to the project output format and duration."""
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-t",
            f"{duration:.3f}",
            "-vf",
            (
                f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                "fps=30,format=yuv420p"
            ),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-an",
            str(output_path),
        ]
    )


def build_visual_sequence(
    image_path: Path,
    output_path: Path,
    duration: float,
    visual_clips: list[Path],
) -> None:
    """Build the silent visual sequence for a section."""
    intro_duration, broll_duration = section_visual_plan(duration, len(visual_clips))
    if not visual_clips or broll_duration == 0.0:
        build_still_video(image_path, output_path, duration)
        return

    work_dir = output_path.parent / f"{output_path.stem}_parts"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    part_paths: list[Path] = []
    intro_path = work_dir / "intro.mp4"
    build_still_video(image_path, intro_path, intro_duration)
    part_paths.append(intro_path)

    per_clip_budget = broll_duration / len(visual_clips)
    actual_broll = 0.0
    for index, clip_path in enumerate(visual_clips):
        remaining = broll_duration - actual_broll
        if remaining <= 0.05:
            break
        clip_duration = remaining if index == len(visual_clips) - 1 else min(per_clip_budget, remaining)
        normalized_path = work_dir / f"broll_{index:02d}.mp4"
        normalize_video_clip(clip_path, normalized_path, clip_duration)
        part_paths.append(normalized_path)
        actual_broll += clip_duration

    remaining_duration = max(0.0, duration - intro_duration - actual_broll)
    if remaining_duration > 0.05:
        outro_path = work_dir / "outro.mp4"
        build_still_video(image_path, outro_path, remaining_duration)
        part_paths.append(outro_path)

    concat_media(part_paths, output_path)
    shutil.rmtree(work_dir)


def mux_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    """Mux section audio onto a prebuilt silent visual sequence."""
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-shortest",
            str(output_path),
        ]
    )


def build_section_clip(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    duration: float,
    visual_clips: list[Path],
) -> None:
    """Build one final section clip, optionally splicing in Sora visuals."""
    silent_path = output_path.with_name(f"{output_path.stem}_silent.mp4")
    build_visual_sequence(image_path, silent_path, duration, visual_clips)
    mux_audio(silent_path, audio_path, output_path)
    silent_path.unlink(missing_ok=True)


def concat_media(paths: list[Path], output_path: Path) -> None:
    """Concatenate a list of media files into one output file."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
        for path in paths:
            handle.write(f"file '{path.resolve()}'\n")
        concat_file = Path(handle.name)
    try:
        run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(output_path),
            ]
        )
    finally:
        concat_file.unlink(missing_ok=True)


def build_episode(spec_path: Path, force: bool = False, keep_build: bool = False) -> tuple[Path, Path]:
    """Generate the final voiceover and video for an episode spec."""
    spec = load_episode_spec(spec_path)
    slug = spec["slug"]
    episode_dir = DATA_DIR / slug
    build_dir = OUTPUT_DIR / f"{slug}_build"
    video_path = OUTPUT_DIR / f"{slug}.mp4"
    audio_path = episode_dir / "voiceover.mp3"
    voice = spec.get("voice", TTS_VOICE)
    instructions = spec.get("instructions", TTS_INSTRUCTIONS)

    episode_dir.mkdir(parents=True, exist_ok=True)
    if force and build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    write_full_script(spec, episode_dir)

    clip_paths: list[Path] = []
    audio_parts: list[Path] = []
    for index, section in enumerate(spec["sections"]):
        LOGGER.info("Building section %s", section["id"])
        section_audio = build_dir / f"{index:02d}_{section['id']}.mp3"
        section_image = build_dir / f"{index:02d}_{section['id']}.png"
        section_clip = build_dir / f"{index:02d}_{section['id']}.mp4"
        visual_clips = resolve_visual_clips(spec, section)
        if force or not section_audio.exists():
            generate_section_audio(section, section_audio, voice, instructions)
        render_scene_image(spec, section, index, section_image)
        section_duration = media_duration(section_audio)
        build_section_clip(section_image, section_audio, section_clip, section_duration, visual_clips)
        clip_paths.append(section_clip)
        audio_parts.append(section_audio)

    concat_media(audio_parts, audio_path)
    concat_media(clip_paths, video_path)
    if not keep_build:
        shutil.rmtree(build_dir)
    return audio_path, video_path


def main() -> None:
    """Parse CLI arguments and build the requested episode."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", required=True, help="Path to an episode JSON spec")
    parser.add_argument("--force", action="store_true", help="Regenerate section audio even if it exists")
    parser.add_argument("--keep-build", action="store_true", help="Keep intermediate assets in output/")
    args = parser.parse_args()
    audio_path, video_path = build_episode(Path(args.episode), force=args.force, keep_build=args.keep_build)
    LOGGER.info("Audio: %s", audio_path)
    LOGGER.info("Video: %s", video_path)


if __name__ == "__main__":
    main()
