"""Generate still-image visuals for a narrated episode from a JSON plan.

Uses the OpenAI Images API directly via the Python SDK — no external CLI dependency.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any

from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parent.parent
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


def generate_image(
    plan: dict[str, Any],
    image: dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
) -> Path:
    """Generate one image via the OpenAI SDK, or skip if it already exists."""
    output_format = str(image.get("output_format", plan.get("output_format", "png")))
    out_path = image_path(plan["slug"], image["id"], output_format)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists() and not force and not dry_run:
        print(f"Skipping {image['id']} (already exists)")
        return out_path

    model = str(image.get("model", plan.get("model", "gpt-image-1.5")))
    size = str(image.get("size", plan.get("size", "1536x1024")))
    quality = str(image.get("quality", plan.get("quality", "high")))
    prompt = image["prompt"]

    if dry_run:
        print(f"  [dry-run] Would generate: model={model} size={size} quality={quality}")
        print(f"  [dry-run] Prompt: {prompt[:120]}...")
        print(f"  [dry-run] Output: {out_path}")
        return out_path

    client = OpenAI()
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        response_format="b64_json",
        n=1,
    )

    image_data = base64.b64decode(response.data[0].b64_json)
    out_path.write_bytes(image_data)
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
