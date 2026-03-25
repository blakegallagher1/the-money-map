"""Generate still-image visuals for a narrated episode from a JSON plan."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE_CLI = Path("/Users/gallagherpropertycompany/.codex/skills/imagegen/scripts/image_gen.py")
OUTPUT_DIR = REPO_ROOT / "output" / "imagegen"


def load_image_plan(path: Path) -> dict[str, Any]:
    """Load and validate an episode image plan."""
    plan = json.loads(path.read_text())
    if "slug" not in plan or "images" not in plan:
        raise ValueError("Image plan must include slug and images")
    if not isinstance(plan["images"], list) or not plan["images"]:
        raise ValueError("Image plan must include at least one image entry")
    for image in plan["images"]:
        missing = {"id", "prompt"} - image.keys()
        if missing:
            raise ValueError(f"Image entry missing keys: {sorted(missing)}")
    return plan


def image_path(slug: str, image_id: str, output_format: str) -> Path:
    """Return the output path for one generated image."""
    return OUTPUT_DIR / slug / f"{image_id}.{output_format}"


def build_image_command(
    image: dict[str, Any],
    *,
    model: str,
    size: str,
    quality: str,
    output_format: str,
    out_path: Path,
    force: bool,
    dry_run: bool,
) -> list[str]:
    """Build a deterministic image generation command for one plan entry."""
    command = [
        "uv",
        "run",
        "--with",
        "openai",
        "--with",
        "pillow",
        "--python",
        "3.12",
        "python",
        str(IMAGE_CLI),
        "generate",
        "--model",
        str(image.get("model", model)),
        "--prompt",
        image["prompt"],
        "--size",
        str(image.get("size", size)),
        "--quality",
        str(image.get("quality", quality)),
        "--output-format",
        str(image.get("output_format", output_format)),
        "--out",
        str(out_path),
    ]
    for option in [
        "use_case",
        "scene",
        "subject",
        "style",
        "composition",
        "lighting",
        "palette",
        "materials",
        "text",
        "constraints",
        "negative",
    ]:
        value = image.get(option)
        if value:
            command.extend([f"--{option.replace('_', '-')}", str(value)])
    if force:
        command.append("--force")
    if dry_run:
        command.append("--dry-run")
    return command


def generate_image(plan: dict[str, Any], image: dict[str, Any], *, force: bool, dry_run: bool) -> Path:
    """Generate one image or skip if the target already exists."""
    output_format = str(image.get("output_format", plan.get("output_format", "png")))
    out_path = image_path(plan["slug"], image["id"], output_format)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not force and not dry_run:
        print(f"Skipping {image['id']} (already exists)")
        return out_path

    command = build_image_command(
        image,
        model=str(plan.get("model", "gpt-image-1.5")),
        size=str(plan.get("size", "1536x1024")),
        quality=str(plan.get("quality", "high")),
        output_format=output_format,
        out_path=out_path,
        force=force,
        dry_run=dry_run,
    )
    env = dict(os.environ)
    subprocess.run(command, check=True, env=env)
    return out_path


def main() -> None:
    """Run image generation for a plan file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, help="Path to an image plan JSON file")
    parser.add_argument("--image", action="append", default=[], help="Only generate matching image id(s)")
    parser.add_argument("--force", action="store_true", help="Regenerate images even if they already exist")
    parser.add_argument("--dry-run", action="store_true", help="Print planned requests without calling the API")
    args = parser.parse_args()

    plan = load_image_plan(Path(args.plan))
    selected = set(args.image)
    for image in plan["images"]:
        if selected and image["id"] not in selected:
            continue
        print(f"Generating {image['id']}...")
        output_path = generate_image(plan, image, force=args.force, dry_run=args.dry_run)
        status = "Planned" if args.dry_run else "Saved"
        print(f"{status} {output_path}")


if __name__ == "__main__":
    main()
