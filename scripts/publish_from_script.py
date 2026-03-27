"""
Publish an episode directly from a script JSON file.

This wraps the orchestrator publish flow so you can provide any script path and
run a complete build + YouTube upload without manual `data/latest_script.json`
copy steps.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
LATEST_SCRIPT_PATH = DATA_DIR / "latest_script.json"
LAST_RUN_PATH = DATA_DIR / "last_run.json"


def build_orchestrator_publish_command(
    python_executable: str,
    quality_tier: str,
    no_broll: bool,
    no_music: bool,
    min_words: int | None = None,
    force_voiceover: bool = False,
) -> list[str]:
    """Return orchestrator args for full publish from latest script."""
    command = [
        python_executable,
        str(REPO_ROOT / "scripts" / "orchestrator.py"),
        "--step",
        "voiceover",
        "--quality-tier",
        quality_tier,
    ]
    if no_broll:
        command.append("--no-broll")
    if no_music:
        command.append("--no-music")
    if min_words is not None:
        command.extend(["--min-words", str(min_words)])
    if force_voiceover:
        command.append("--force-voiceover")
    return command


def _load_last_run_url() -> str | None:
    """Read last_run.json and return uploaded video URL if present."""
    if not LAST_RUN_PATH.exists():
        return None
    try:
        payload = json.loads(LAST_RUN_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    video_url = payload.get("video_url")
    return video_url if isinstance(video_url, str) and video_url.strip() else None


def run() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", required=True, help="Path to source script JSON.")
    parser.add_argument(
        "--quality-tier",
        default="1440",
        choices=["1080", "1440", "2160"],
        help="Render quality tier (default: 1440).",
    )
    parser.add_argument(
        "--no-broll",
        action="store_true",
        help="Disable b-roll generation during publish.",
    )
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Disable music mixing during publish.",
    )
    parser.add_argument(
        "--force-voiceover",
        action="store_true",
        help="Delete cached output voiceover artifacts before publish.",
    )
    parser.add_argument(
        "--min-words",
        type=int,
        default=None,
        metavar="N",
        help="Override quality-gate minimum script word count for this publish.",
    )
    args = parser.parse_args()

    source_script = Path(args.script).expanduser().resolve()
    if not source_script.exists():
        raise FileNotFoundError(f"Script JSON not found: {source_script}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    backup_script_path = None
    if LATEST_SCRIPT_PATH.exists():
        backup_script_path = DATA_DIR / "_latest_script_backup.json"
        shutil.copy2(LATEST_SCRIPT_PATH, backup_script_path)

    try:
        shutil.copy2(source_script, LATEST_SCRIPT_PATH)

        if args.force_voiceover:
            output_dir = REPO_ROOT / "output"
            for stale in ("voiceover.wav", "voiceover_normalized.wav", "mixed_audio.wav"):
                target = output_dir / stale
                if target.exists():
                    target.unlink()

        command = build_orchestrator_publish_command(
            python_executable=sys.executable,
            quality_tier=args.quality_tier,
            no_broll=args.no_broll,
            no_music=args.no_music,
            min_words=args.min_words,
            force_voiceover=args.force_voiceover,
        )
        subprocess.run(command, cwd=str(REPO_ROOT), check=True)

        video_url = _load_last_run_url()
        if video_url:
            print(f"Published URL: {video_url}")
        else:
            print("Publish complete. No video URL found in data/last_run.json.")
        return 0
    finally:
        if backup_script_path and backup_script_path.exists():
            shutil.move(backup_script_path, LATEST_SCRIPT_PATH)


if __name__ == "__main__":
    raise SystemExit(run())
