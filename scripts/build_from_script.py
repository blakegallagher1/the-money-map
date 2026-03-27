"""
Build a final episode video directly from a script JSON file.

This wraps the existing orchestrator flow so you can run one command without
manually copying `data/latest_script.json` or renaming output artifacts.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUT_DIR = REPO_ROOT / "output"
LATEST_SCRIPT_PATH = DATA_DIR / "latest_script.json"
LATEST_VIDEO_PATH = OUTPUT_DIR / "latest_final.mp4"
LATEST_THUMBNAIL_PATH = OUTPUT_DIR / "thumbnail.png"


def build_orchestrator_command(
    python_executable: str,
    quality_tier: str,
    no_broll: bool,
    no_music: bool,
) -> list[str]:
    """Return orchestrator command args for render/build from latest script."""
    command = [
        python_executable,
        str(REPO_ROOT / "scripts" / "orchestrator.py"),
        "--step",
        "voiceover",
        "--quality-tier",
        quality_tier,
        "--no-upload",
    ]
    if no_broll:
        command.append("--no-broll")
    if no_music:
        command.append("--no-music")
    return command


def derive_thumbnail_path(video_output_path: Path) -> Path:
    """Derive thumbnail output path from video output path."""
    return video_output_path.with_name(f"{video_output_path.stem}_thumbnail.png")


def run() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", required=True, help="Path to source script JSON.")
    parser.add_argument("--out", required=True, help="Output MP4 path to write.")
    parser.add_argument(
        "--thumbnail-out",
        default=None,
        help="Optional thumbnail output path. Defaults to <out>_thumbnail.png.",
    )
    parser.add_argument(
        "--quality-tier",
        default="1440",
        choices=["1080", "1440", "2160"],
        help="Render quality tier (default: 1440).",
    )
    parser.add_argument(
        "--no-broll",
        action="store_true",
        help="Disable b-roll generation during build.",
    )
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Disable music mixing during build.",
    )
    parser.add_argument(
        "--force-voiceover",
        action="store_true",
        help="Delete cached output voiceover artifacts before build.",
    )
    args = parser.parse_args()

    source_script = Path(args.script).expanduser().resolve()
    output_video = Path(args.out).expanduser().resolve()
    output_thumbnail = (
        Path(args.thumbnail_out).expanduser().resolve()
        if args.thumbnail_out
        else derive_thumbnail_path(output_video)
    )

    if not source_script.exists():
        raise FileNotFoundError(f"Script JSON not found: {source_script}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_video.parent.mkdir(parents=True, exist_ok=True)
    output_thumbnail.parent.mkdir(parents=True, exist_ok=True)

    backup_script_path = None
    if LATEST_SCRIPT_PATH.exists():
        backup_script_path = DATA_DIR / "_latest_script_backup.json"
        shutil.copy2(LATEST_SCRIPT_PATH, backup_script_path)

    try:
        shutil.copy2(source_script, LATEST_SCRIPT_PATH)

        if args.force_voiceover:
            for stale in ("voiceover.wav", "voiceover_normalized.wav", "mixed_audio.wav"):
                target = OUTPUT_DIR / stale
                if target.exists():
                    target.unlink()

        command = build_orchestrator_command(
            python_executable=sys.executable,
            quality_tier=args.quality_tier,
            no_broll=args.no_broll,
            no_music=args.no_music,
        )
        subprocess.run(command, cwd=str(REPO_ROOT), check=True)

        if not LATEST_VIDEO_PATH.exists():
            raise FileNotFoundError(f"Expected final artifact missing: {LATEST_VIDEO_PATH}")
        if not LATEST_THUMBNAIL_PATH.exists():
            raise FileNotFoundError(f"Expected thumbnail artifact missing: {LATEST_THUMBNAIL_PATH}")

        shutil.copy2(LATEST_VIDEO_PATH, output_video)
        shutil.copy2(LATEST_THUMBNAIL_PATH, output_thumbnail)

        print(f"Video: {output_video}")
        print(f"Thumbnail: {output_thumbnail}")
        return 0
    finally:
        if backup_script_path and backup_script_path.exists():
            shutil.move(backup_script_path, LATEST_SCRIPT_PATH)


if __name__ == "__main__":
    raise SystemExit(run())
