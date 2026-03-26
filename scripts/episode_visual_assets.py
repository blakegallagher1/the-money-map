"""Visual asset helpers for narrated episode assembly."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "output"
SORA_DIR = REPO_ROOT / "assets" / "sora"
IMAGE_DIR = OUTPUT_DIR / "imagegen"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30
IMAGE_SUFFIXES = (".png", ".webp", ".jpg", ".jpeg")


@dataclass(frozen=True)
class VisualAsset:
    """One resolved visual asset used in a section b-roll sequence."""

    kind: str
    path: Path


def resolve_visual_assets(
    spec: dict[str, Any],
    section: dict[str, Any],
    logger: logging.Logger | None = None,
) -> list[VisualAsset]:
    """Resolve existing generated images and clips for a section."""
    slug = spec["slug"]
    assets: list[VisualAsset] = []

    for image_id in section.get("visual_images", []):
        image_path = resolve_visual_image(slug, image_id)
        if image_path:
            assets.append(VisualAsset(kind="image", path=image_path))
        elif logger:
            logger.warning("Missing visual image for %s: %s", section["id"], image_id)

    for clip_id in section.get("visual_clips", []):
        clip_path = SORA_DIR / slug / f"{clip_id}.mp4"
        if clip_path.exists():
            assets.append(VisualAsset(kind="video", path=clip_path))
        elif logger:
            logger.warning("Missing visual clip for %s: %s", section["id"], clip_path)

    return assets


def resolve_visual_image(slug: str, image_id: str) -> Path | None:
    """Return the first existing generated still image for an id."""
    for suffix in IMAGE_SUFFIXES:
        candidate = IMAGE_DIR / slug / f"{image_id}{suffix}"
        if candidate.exists():
            return candidate
    return None


def section_visual_plan(duration: float, asset_count: int) -> tuple[float, float]:
    """Return intro and b-roll durations for a section."""
    if asset_count <= 0 or duration < 10:
        return duration, 0.0
    intro_duration = min(4.0, max(2.5, duration * 0.12))
    max_broll = min(16.0, 8.0 * asset_count, duration * 0.4)
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


def build_still_video(
    image_path: Path,
    output_path: Path,
    duration: float,
    run_ffmpeg: Callable[[list[str]], None],
) -> None:
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
            "medium",
            "-crf",
            "18",
            "-an",
            str(output_path),
        ]
    )


def normalize_video_clip(
    input_path: Path,
    output_path: Path,
    duration: float,
    run_ffmpeg: Callable[[list[str]], None],
) -> None:
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
                f"fps={FPS},format=yuv420p"
            ),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-an",
            str(output_path),
        ]
    )


def build_visual_sequence(
    image_path: Path,
    output_path: Path,
    duration: float,
    visual_assets: list[VisualAsset],
    run_ffmpeg: Callable[[list[str]], None],
    concat_media: Callable[[list[Path], Path], None],
) -> None:
    """Build the silent visual sequence for a section."""
    intro_duration, broll_duration = section_visual_plan(duration, len(visual_assets))
    if not visual_assets or broll_duration == 0.0:
        build_still_video(image_path, output_path, duration, run_ffmpeg)
        return

    work_dir = output_path.parent / f"{output_path.stem}_parts"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    part_paths: list[Path] = []
    intro_path = work_dir / "intro.mp4"
    build_still_video(image_path, intro_path, intro_duration, run_ffmpeg)
    part_paths.append(intro_path)

    per_asset_budget = broll_duration / len(visual_assets)
    actual_broll = 0.0
    for index, asset in enumerate(visual_assets):
        remaining = broll_duration - actual_broll
        if remaining <= 0.05:
            break
        asset_duration = (
            remaining if index == len(visual_assets) - 1 else min(per_asset_budget, remaining)
        )
        segment_path = work_dir / f"asset_{index:02d}.mp4"
        if asset.kind == "image":
            build_still_video(asset.path, segment_path, asset_duration, run_ffmpeg)
        else:
            normalize_video_clip(asset.path, segment_path, asset_duration, run_ffmpeg)
        part_paths.append(segment_path)
        actual_broll += asset_duration

    remaining_duration = max(0.0, duration - intro_duration - actual_broll)
    if remaining_duration > 0.05:
        outro_path = work_dir / "outro.mp4"
        build_still_video(image_path, outro_path, remaining_duration, run_ffmpeg)
        part_paths.append(outro_path)

    concat_media(part_paths, output_path)
    shutil.rmtree(work_dir)
