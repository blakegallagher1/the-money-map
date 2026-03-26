"""Generate Sora clips for a narrated episode from a JSON shot plan.

Uses the OpenAI Videos SDK directly — no external CLI dependency.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets" / "sora"


def load_sora_plan(path: Path) -> dict[str, Any]:
    """Load and validate a Sora shot plan."""
    plan = json.loads(path.read_text())
    if "slug" not in plan or "shots" not in plan:
        raise ValueError("Shot plan must include slug and shots")
    if not isinstance(plan["shots"], list) or not plan["shots"]:
        raise ValueError("Shot plan must include at least one shot")
    for shot in plan["shots"]:
        missing = {"id", "prompt"} - shot.keys()
        if missing:
            raise ValueError(f"Shot missing keys: {sorted(missing)}")
    return plan


def shot_paths(slug: str, shot_id: str) -> tuple[Path, Path]:
    """Return the target video and metadata paths for a shot."""
    out_dir = ASSETS_DIR / slug
    return out_dir / f"{shot_id}.mp4", out_dir / f"{shot_id}.json"


def build_augmented_prompt(shot: dict[str, Any]) -> str:
    """Build the structured prompt text for a shot."""
    parts = [f"Use case: {shot['use_case']}", f"Primary request: {shot['prompt']}"]
    for key, label in [
        ("scene", "Scene/background"),
        ("subject", "Subject"),
        ("action", "Action"),
        ("camera", "Camera"),
        ("lighting", "Lighting/mood"),
        ("palette", "Color palette"),
        ("style", "Style/format"),
        ("timing", "Timing/beats"),
        ("audio", "Audio"),
        ("constraints", "Constraints"),
        ("negative", "Avoid"),
    ]:
        value = shot.get(key)
        if value:
            parts.append(f"{label}: {value}")
    return "\n".join(parts)


def to_jsonable(value: Any) -> Any:
    """Convert SDK objects into plain JSON-serializable structures."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


def write_download(content: Any, output_path: Path) -> None:
    """Persist downloaded SDK content to disk."""
    if hasattr(content, "write_to_file"):
        content.write_to_file(output_path)
        return
    if hasattr(content, "read"):
        output_path.write_bytes(content.read())
        return
    output_path.write_bytes(bytes(content))


def generate_shot_via_sdk(
    plan: dict[str, Any],
    shot: dict[str, Any],
    *,
    video_path: Path,
    json_path: Path,
) -> tuple[Path, Path]:
    """Generate a Sora shot using the official OpenAI SDK video methods."""
    from openai import OpenAI

    client = OpenAI()
    prompt = build_augmented_prompt(shot)
    video = client.videos.create(
        model=str(shot.get("model", plan.get("model", "sora-2-pro"))),
        prompt=prompt,
        size=str(shot.get("size", plan.get("size", "1920x1080"))),
        seconds=str(shot.get("seconds", "8")),
    )
    print(f"Started {shot['id']}: {video.id} status={video.status}")
    timeout = int(shot.get("timeout", plan.get("timeout", 1800)))
    poll_interval = int(shot.get("poll_interval", plan.get("poll_interval", 10)))
    start = time.time()
    last_status = video.status
    last_progress = getattr(video, "progress", None)
    while video.status in {"queued", "in_progress"}:
        if time.time() - start > timeout:
            raise TimeoutError(f"Sora shot timed out after {timeout}s: {shot['id']}")
        time.sleep(poll_interval)
        video = client.videos.retrieve(video.id)
        progress = getattr(video, "progress", None)
        if video.status != last_status or progress != last_progress:
            print(f"  {shot['id']}: status={video.status} progress={progress}")
            last_status = video.status
            last_progress = progress

    json_path.write_text(json.dumps({"final": to_jsonable(video)}, indent=2))
    if video.status != "completed":
        raise RuntimeError(f"Sora shot failed with status {video.status}: {shot['id']}")

    content = client.videos.download_content(video.id, variant="video")
    write_download(content, video_path)
    return video_path, json_path


def generate_shot(
    plan: dict[str, Any],
    shot: dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
) -> tuple[Path, Path]:
    """Generate one Sora shot or skip it if it already exists."""
    video_path, json_path = shot_paths(plan["slug"], shot["id"])
    video_path.parent.mkdir(parents=True, exist_ok=True)
    if video_path.exists() and not force and not dry_run:
        print(f"Skipping {shot['id']} (already exists)")
        return video_path, json_path

    if dry_run:
        prompt = build_augmented_prompt(shot)
        model = str(shot.get("model", plan.get("model", "sora-2-pro")))
        size = str(shot.get("size", plan.get("size", "1920x1080")))
        seconds = str(shot.get("seconds", "8"))
        print(f"  [dry-run] Would generate: model={model} size={size} seconds={seconds}")
        print(f"  [dry-run] Prompt: {prompt[:120]}...")
        print(f"  [dry-run] Output: {video_path}")
        return video_path, json_path

    return generate_shot_via_sdk(
        plan,
        shot,
        video_path=video_path,
        json_path=json_path,
    )


def main() -> None:
    """Run Sora clip generation for a plan file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, help="Path to a Sora shot plan JSON file")
    parser.add_argument("--shot", action="append", default=[], help="Only generate matching shot id(s)")
    parser.add_argument("--force", action="store_true", help="Regenerate clips even if they already exist")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned Sora requests without calling the API")
    args = parser.parse_args()

    plan = load_sora_plan(Path(args.plan))
    selected = set(args.shot)
    for shot in plan["shots"]:
        if selected and shot["id"] not in selected:
            continue
        print(f"Generating {shot['id']}...")
        generate_shot(plan, shot, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
