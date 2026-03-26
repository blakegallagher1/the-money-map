"""
Topic Research Dossier

Before writing scripts, this module builds a compact research dossier for the
selected story using the configured LLM. The dossier improves script quality and
adds external context, credibility signals, and differentiation guidance.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (  # noqa: E402
    RESEARCH_PROMPT_MODEL,
    RESEARCH_DOSSIER_MAX_WORDS,
)


DEFAULT_DOSSIER_SYSTEM = """You are a senior content strategist for a finance YouTube channel.

Produce a concise topic dossier in JSON with these keys:

- summary: one to two sentences explaining why this topic is current.
- angle: one primary framing angle that is surprising/differentiated.
- watch_outs: list of 3 risks to avoid (over-hype, bad causal claims, weak sourcing).
- source_list: 2-6 likely data/news sources the script should reference.
- novelty: how to differentiate this episode from similar previous economic clips.
- disclosed_synthetic_content: boolean whether synthetic visuals are likely to require disclosure.
- title_variants: list of 3 headline-level title options.
- hook_directions: list of 3 specific hook alternatives.
- confidence: number from 0.0 to 1.0.
"""


def slugify(value: str) -> str:
    """Generate a filesystem-safe identifier for a phrase."""
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return normalized.strip("-") or "topic"


def _extract_json(text: str) -> dict[str, Any] | None:
    """Extract and decode a JSON object embedded anywhere in model output."""
    clean = text.strip()
    if not clean:
        return None

    if clean.startswith("```"):
        clean = clean.replace("```json", "```").strip()
        if clean.startswith("```") and clean.endswith("```"):
            clean = clean[3:-3].strip()

    start = clean.find("{")
    end = clean.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        return json.loads(clean[start:end + 1])
    except json.JSONDecodeError:
        return None


def _default_dossier(story_pkg: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic fallback dossier when model generation is unavailable."""
    primary = story_pkg.get("primary", {})
    name = primary.get("name", "this topic")
    yoy = primary.get("yoy_pct")
    direction = "increasing" if (yoy or 0) >= 0 else "decreasing"

    return {
        "summary": (
            f"The selected signal is {name}, currently {direction} with a "
            f"{yoy if yoy is not None else 'recent'} year-over-year move."
        ),
        "angle": f"Explain why the {direction} trend in {name} matters now for households.",
        "watch_outs": [
            "Avoid unsupported causal claims beyond available data.",
            "Do not over-index on one data point without context.",
            "Keep model uncertainty explicit when framing forward-looking claims.",
        ],
        "source_list": [
            "Federal Reserve Economic Data (FRED)",
            "Recent macroeconomic releases",
        ],
        "novelty": "Pair the raw metric move with consumer outcomes and an original decision framework.",
        "disclosed_synthetic_content": True,
        "title_variants": [
            f"{name}: What the Latest Change Really Means",
            f"Why {name} Is Moving This Direction Right Now",
            f"The {name} Signal You Can Actually Use",
        ],
        "hook_directions": [
            f"Lead with one specific household-level impact tied to {name}.",
            "Open on the month-over-month surprise before stepping back to the annual move.",
            "Use a one-line counterintuitive takeaway that forces attention.",
        ],
        "confidence": 0.5,
        "model": "fallback",
    }


def _validate_dossier(dossier: dict[str, Any]) -> dict[str, Any]:
    """Normalize and clamp dossier fields for downstream use."""
    safe: dict[str, Any] = {}

    safe["summary"] = str(dossier.get("summary", "")).strip()
    safe["angle"] = str(dossier.get("angle", "")).strip()

    watch_outs = dossier.get("watch_outs", [])
    if not isinstance(watch_outs, list):
        watch_outs = []
    safe["watch_outs"] = [str(item).strip() for item in watch_outs if str(item).strip()][:6]

    source_list = dossier.get("source_list", [])
    if not isinstance(source_list, list):
        source_list = []
    safe["source_list"] = [str(item).strip() for item in source_list if str(item).strip()][:8]

    for key in ("novelty", "disclosed_synthetic_content"):
        safe[key] = dossier.get(key)

    titles = dossier.get("title_variants", [])
    if not isinstance(titles, list):
        titles = []
    safe["title_variants"] = [
        str(item).strip() for item in titles if str(item).strip()
    ][:3]

    hooks = dossier.get("hook_directions", [])
    if not isinstance(hooks, list):
        hooks = []
    safe["hook_directions"] = [
        str(item).strip() for item in hooks if str(item).strip()
    ][:3]

    confidence = dossier.get("confidence", 0.5)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5
    safe["confidence"] = max(0.0, min(1.0, confidence))

    safe["model"] = str(dossier.get("model", "gpt-5.4")).strip()
    safe["generated_at"] = datetime.now().isoformat()

    return safe


def generate_research_dossier(
    story_package: dict[str, Any],
    *,
    model: str = RESEARCH_PROMPT_MODEL,
    max_tokens: int = RESEARCH_DOSSIER_MAX_WORDS,
) -> dict[str, Any]:
    """
    Build a compact research dossier for a selected story.

    The function is best-effort: if model generation fails, a deterministic
    fallback dossier is returned so pipelines remain runnable in constrained
    environments.
    """
    primary = story_package.get("primary", {})
    related = story_package.get("related", [])

    user_prompt = (
        "Topic for dossier:\n"
        f"Primary metric: {primary.get('name', 'Unknown')}\n"
        f"Metric key: {primary.get('key', 'unknown')}\n"
        f"Latest value: {primary.get('latest_value', 'N/A')} {primary.get('unit', '')}\n"
        f"YoY: {primary.get('yoy_pct', 'N/A')}\n"
        f"Score: {primary.get('score', 'N/A')}\n"
        f"Related metrics: {[item.get('name') for item in related[:3]]}\n"
        "Output valid JSON only following the schema described in the system prompt.\n"
    )

    try:
        client = OpenAI()
        response = client.responses.create(
            model=model,
            instructions=DEFAULT_DOSSIER_SYSTEM,
            input=user_prompt,
            max_output_tokens=max_tokens,
            text={"verbosity": "high"},
            reasoning={"effort": "low"},
        )
        parsed = _extract_json(response.output_text)
        if not isinstance(parsed, dict):
            raise RuntimeError("Model output is not JSON")
        parsed["model"] = model
        dossier = _validate_dossier(parsed)
    except Exception:
        dossier = _validate_dossier(_default_dossier(story_package))

    return dossier


def save_dossier(
    metric_key: str,
    dossier: dict[str, Any],
    base_dir: str | Path | None = None,
) -> tuple[str, str]:
    """Persist dossier as markdown and JSON in the data directory."""
    base = Path(base_dir or Path(__file__).resolve().parent.parent / "data")
    data_dir = base / "dossiers"
    data_dir.mkdir(parents=True, exist_ok=True)

    stem = f"{datetime.now():%Y%m%d-%H%M%S}-{slugify(metric_key)}"
    json_path = data_dir / f"{stem}.json"
    md_path = data_dir / f"{stem}.md"

    json_path.write_text(json.dumps(dossier, indent=2))
    md_path.write_text(
        "# Topic Research Dossier\n\n"
        f"Generated: {dossier.get('generated_at')}\n\n"
        f"- Summary: {dossier.get('summary')}\n"
        f"- Angle: {dossier.get('angle')}\n"
        f"- Novelty: {dossier.get('novelty')}\n"
        f"- Disclose synthetic content: {dossier.get('disclosed_synthetic_content')}\n"
    )
    return str(json_path), str(md_path)


if __name__ == "__main__":
    print("This module is intended to be used by the orchestrator.")
