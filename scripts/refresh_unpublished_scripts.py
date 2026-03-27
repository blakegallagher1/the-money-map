"""
Refresh saved draft episode scripts that have not been published yet.

The refresh flow keeps each draft's primary metric/topic, fetches the latest
curated FRED data, rebuilds context for that metric, regenerates the script,
and overwrites the saved draft artifacts in place.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.data_ingestion import fetch_fresh_data
from scripts.llm_script_writer import generate_script
from scripts.story_discovery import analyze_data, find_related_series
from scripts.topic_research import generate_research_dossier, save_dossier

DATA_DIR = REPO_ROOT / "data"
HISTORY_PATH = DATA_DIR / "episode_history.json"
LATEST_DATA_PATH = DATA_DIR / "latest_data.json"
REPORTS_DIR = DATA_DIR / "refresh_reports"
SCRIPT_GLOB = "ep*_v2/script.json"
PLAIN_TEXT_REPLACEMENTS = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
    }
)


def load_json(path: Path) -> dict[str, Any] | list[Any]:
    """Read a JSON file from disk."""
    return json.loads(path.read_text())


def published_titles(history: list[dict[str, Any]]) -> set[str]:
    """Return the set of titles already tied to a published YouTube URL."""
    titles: set[str] = set()
    for entry in history:
        if not isinstance(entry, dict):
            continue
        title = entry.get("title")
        video_url = entry.get("video_url")
        if isinstance(title, str) and title.strip() and isinstance(video_url, str) and video_url.strip():
            titles.add(title.strip())
    return titles


def normalize_plaintext(text: str) -> str:
    """Normalize generated narration text to ASCII-safe punctuation."""
    normalized = text.translate(PLAIN_TEXT_REPLACEMENTS)
    allowed_chars = []
    for char in normalized:
        codepoint = ord(char)
        if char in "\n\r\t" or 32 <= codepoint <= 126:
            allowed_chars.append(char)
    return "".join(allowed_chars)


def write_script_artifacts(script_path: Path, script_data: dict[str, Any]) -> None:
    """Persist a refreshed script JSON plus the plain voiceover script text."""
    script_path.write_text(json.dumps(script_data, indent=2) + "\n")
    voiceover_path = script_path.with_name("voiceover_script.txt")
    voiceover_text = normalize_plaintext(script_data.get("script", "").strip())
    voiceover_path.write_text(voiceover_text + "\n")


def select_unpublished_script_paths(
    data_dir: Path,
    history: list[dict[str, Any]],
    pattern: str = SCRIPT_GLOB,
) -> list[Path]:
    """Return versioned draft scripts whose exact title is not already published."""
    published = published_titles(history)
    selected: list[Path] = []

    for script_path in sorted(data_dir.glob(pattern)):
        payload = load_json(script_path)
        if not isinstance(payload, dict):
            continue
        title = str(payload.get("title", "")).strip()
        if title and title in published:
            continue
        selected.append(script_path)

    return selected


def build_story_package_for_metric(
    latest_data: dict[str, Any],
    ranked_stories: list[dict[str, Any]],
    metric_key: str,
) -> dict[str, Any]:
    """Build a story package for a specific metric using the latest data payload."""
    data = latest_data.get("data", {})
    stories_by_key = {
        story["key"]: story for story in ranked_stories if isinstance(story, dict) and story.get("key")
    }

    if metric_key not in stories_by_key:
        raise KeyError(f"Metric '{metric_key}' not found in latest data payload.")

    return {
        "primary": stories_by_key[metric_key],
        "related": find_related_series(metric_key, data),
        "all_ranked": ranked_stories[:10],
        "generated_at": datetime.now().isoformat(),
    }


def refresh_script(
    script_path: Path,
    latest_data: dict[str, Any],
    ranked_stories: list[dict[str, Any]],
    *,
    dry_run: bool = False,
    with_research: bool = True,
) -> dict[str, Any]:
    """Regenerate a single draft script from current data for its saved metric."""
    existing = load_json(script_path)
    if not isinstance(existing, dict):
        raise ValueError(f"Expected dict payload in {script_path}")

    primary_metric = existing.get("primary_metric", {})
    metric_key = primary_metric.get("key")
    if not isinstance(metric_key, str) or not metric_key.strip():
        raise ValueError(f"Draft script is missing primary_metric.key: {script_path}")

    story_pkg = build_story_package_for_metric(latest_data, ranked_stories, metric_key)
    dossier = None
    if with_research:
        dossier = generate_research_dossier(story_pkg)
        if not dry_run:
            save_dossier(metric_key, dossier, base_dir=DATA_DIR)

    refreshed = generate_script(story_pkg, dossier=dossier)

    if not dry_run:
        write_script_artifacts(script_path, refreshed)

    refreshed_primary = refreshed.get("primary_metric", {})
    return {
        "script_path": str(script_path.relative_to(REPO_ROOT)),
        "metric_key": metric_key,
        "old_title": existing.get("title"),
        "new_title": refreshed.get("title"),
        "old_latest_date": primary_metric.get("latest_date"),
        "new_latest_date": refreshed_primary.get("latest_date"),
        "old_latest_value": primary_metric.get("latest_value"),
        "new_latest_value": refreshed_primary.get("latest_value"),
        "old_yoy_pct": primary_metric.get("yoy_pct"),
        "new_yoy_pct": refreshed_primary.get("yoy_pct"),
        "word_count": refreshed.get("word_count"),
    }


def preview_refresh(
    script_path: Path,
    latest_data: dict[str, Any],
    ranked_stories: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize how a draft would be refreshed without regenerating it."""
    existing = load_json(script_path)
    if not isinstance(existing, dict):
        raise ValueError(f"Expected dict payload in {script_path}")

    primary_metric = existing.get("primary_metric", {})
    metric_key = primary_metric.get("key")
    if not isinstance(metric_key, str) or not metric_key.strip():
        raise ValueError(f"Draft script is missing primary_metric.key: {script_path}")

    current_story = build_story_package_for_metric(latest_data, ranked_stories, metric_key)["primary"]
    return {
        "script_path": str(script_path.relative_to(REPO_ROOT)),
        "metric_key": metric_key,
        "title": existing.get("title"),
        "old_latest_date": primary_metric.get("latest_date"),
        "new_latest_date": current_story.get("latest_date"),
        "old_latest_value": primary_metric.get("latest_value"),
        "new_latest_value": current_story.get("latest_value"),
        "old_yoy_pct": primary_metric.get("yoy_pct"),
        "new_yoy_pct": current_story.get("yoy_pct"),
    }


def refresh_unpublished_scripts(
    *,
    data_dir: Path = DATA_DIR,
    history_path: Path = HISTORY_PATH,
    latest_data_path: Path = LATEST_DATA_PATH,
    dry_run: bool = False,
    with_research: bool = True,
    limit: int | None = None,
) -> dict[str, Any]:
    """Refresh all unpublished versioned draft scripts and return a report."""
    if not dry_run:
        fetch_fresh_data(output_path=str(latest_data_path))

    latest_data = load_json(latest_data_path)
    if not isinstance(latest_data, dict):
        raise ValueError(f"Expected dict payload in {latest_data_path}")

    analysis = analyze_data(str(latest_data_path))
    ranked_stories = analysis.get("stories", [])
    history = load_json(history_path)
    if not isinstance(history, list):
        raise ValueError(f"Expected list payload in {history_path}")

    unpublished_paths = select_unpublished_script_paths(data_dir, history)
    if limit is not None:
        unpublished_paths = unpublished_paths[:limit]

    refreshed_scripts: list[dict[str, Any]] = []
    for script_path in unpublished_paths:
        if dry_run:
            refreshed_scripts.append(preview_refresh(script_path, latest_data, ranked_stories))
            continue
        refreshed_scripts.append(
            refresh_script(
                script_path,
                latest_data,
                ranked_stories,
                dry_run=False,
                with_research=with_research,
            )
        )

    report = {
        "generated_at": datetime.now().isoformat(),
        "as_of_date": datetime.now().strftime("%Y-%m-%d"),
        "dry_run": dry_run,
        "with_research": with_research,
        "latest_data_path": str(latest_data_path.relative_to(REPO_ROOT)),
        "refreshed_count": len(refreshed_scripts),
        "scripts": refreshed_scripts,
    }

    if not dry_run:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-unpublished-scripts.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        report["report_path"] = str(report_path.relative_to(REPO_ROOT))

    return report


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which versioned draft scripts would be refreshed without overwriting them.",
    )
    parser.add_argument(
        "--skip-research",
        action="store_true",
        help="Skip dossier generation and regenerate scripts from current data only.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Refresh at most N unpublished draft scripts.",
    )
    args = parser.parse_args()

    report = refresh_unpublished_scripts(
        dry_run=args.dry_run,
        with_research=not args.skip_research,
        limit=args.limit,
    )

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
