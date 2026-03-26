"""
Episode history and performance tracker.

The tracker stores produced episode metadata and optional channel analytics so the
pipeline can avoid repetitive topics and learn from prior performance.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from uuid import uuid4

from typing import Any


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(BASE, 'data', 'episode_history.json')


def _normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Normalize legacy + fresh entries into a consistent dictionary shape."""
    normalized = {
        "episode_id": entry.get("episode_id") or uuid4().hex,
        "date": entry.get("date") or datetime.now().strftime("%Y-%m-%d"),
        "metric_key": entry.get("metric_key") or entry.get("primary_metric", {}).get("key"),
        "title": entry.get("title") or "Untitled Episode",
        "score": entry.get("score") if isinstance(entry.get("score"), (int, float)) else 0,
        "video_url": entry.get("video_url"),
        "video_id": entry.get("video_id"),
        "thumbnail_path": entry.get("thumbnail_path"),
        "status": entry.get("status") or "recorded",
        "primary_metric": entry.get("primary_metric", {}),
        "quality_gate": entry.get("quality_gate", {}),
        "analytics": entry.get("analytics", {}),
        "script_slug": entry.get("script_slug"),
        "source": entry.get("source", "orchestrator"),
    }
    if not normalized["metric_key"] and entry.get("primary_metric"):
        normalized["metric_key"] = entry.get("primary_metric", {}).get("key")
    return normalized


def _load_raw_history() -> list[dict[str, Any]]:
    """Load history without normalization."""
    if not os.path.exists(HISTORY_PATH):
        return []

    with open(HISTORY_PATH) as f:
        return json.load(f)


def load_history() -> list[dict[str, Any]]:
    """Load episode history from disk, normalized for downstream consumers."""
    raw = _load_raw_history()
    history: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            history.append(_normalize_entry(item))
    return history


def save_history(history: list[dict[str, Any]]) -> None:
    """Save episode history to disk."""
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history, f, indent=2)


def record_episode(
    metric_key: str,
    title: str,
    score: float,
    *,
    video_url: str | None = None,
    video_id: str | None = None,
    thumbnail_path: str | None = None,
    status: str = "recorded",
    quality_gate: dict[str, Any] | None = None,
    status_details: str | None = None,
    script_slug: str | None = None,
    source: str = "orchestrator",
) -> dict[str, Any]:
    """Append a production event to the episode log."""
    history = load_history()

    entry: dict[str, Any] = {
        "episode_id": uuid4().hex,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "metric_key": metric_key,
        "title": title,
        "score": float(score),
        "video_url": video_url,
        "video_id": video_id,
        "thumbnail_path": thumbnail_path,
        "status": status,
        "status_details": status_details,
        "quality_gate": quality_gate or {},
        "analytics": {},
        "script_slug": script_slug,
        "source": source,
    }

    history.append(entry)
    save_history(history)
    return entry


def update_episode_status(video_id: str, status: str, *, details: str | None = None) -> dict[str, Any] | None:
    """Update the status for the episode matching a video id."""
    history = load_history()
    for entry in reversed(history):
        if entry.get("video_id") != video_id:
            continue

        entry["status"] = status
        if details:
            entry["status_details"] = details
        entry["updated_at"] = datetime.now().isoformat()
        save_history(history)
        return entry
    return None


def update_episode_analytics(
    video_id: str,
    analytics: dict[str, Any],
) -> dict[str, Any] | None:
    """Attach analytics payload to a logged episode."""
    history = load_history()
    for entry in reversed(history):
        if entry.get("video_id") != video_id:
            continue

        entry["analytics"] = dict(entry.get("analytics", {}))
        entry["analytics"].update(analytics)
        entry["updated_at"] = datetime.now().isoformat()
        save_history(history)
        return entry
    return None


def get_recency_penalty(metric_key, weeks_lookback=8):
    """Penalty for recently covered topics from history."""
    try:
        weeks = int(weeks_lookback)
    except (TypeError, ValueError):
        weeks = 8

    history = load_history()
    now = datetime.now()

    for entry in reversed(history):
        if entry.get('metric_key') != metric_key:
            continue

        try:
            ep_date = datetime.strptime(entry['date'], "%Y-%m-%d")
        except (ValueError, TypeError, KeyError):
            continue

        days_ago = (now - ep_date).days
        if days_ago <= 28:
            return -30
        if days_ago <= 7 * weeks:
            return -15

    return 0


def get_covered_metrics(weeks: int = 4):
    """Get metric keys covered in the last N weeks."""
    history = load_history()
    cutoff = datetime.now() - timedelta(weeks=weeks)
    covered: set[str] = set()

    for entry in history:
        try:
            ep_date = datetime.strptime(entry['date'], "%Y-%m-%d")
            if ep_date >= cutoff:
                key = entry.get('metric_key')
                if key:
                    covered.add(key)
        except (ValueError, TypeError, KeyError):
            continue

    return covered


def get_recent_titles(weeks: int = 8) -> list[str]:
    """Get recent episode titles for novelty checks."""
    history = load_history()
    cutoff = datetime.now() - timedelta(weeks=weeks)
    titles: list[str] = []
    for entry in history:
        try:
            ep_date = datetime.strptime(entry['date'], "%Y-%m-%d")
            if ep_date >= cutoff:
                title = entry.get('title')
                if title:
                    titles.append(str(title))
        except (ValueError, TypeError, KeyError):
            continue
    return titles


def get_metric_health_score(metric_key: str) -> float:
    """Compute a 0..1 health score for a metric based on past engagement."""
    history = load_history()
    metric_entries = [
        entry
        for entry in history
        if entry.get("metric_key") == metric_key and entry.get("analytics")
    ]
    if not metric_entries:
        return 0.5

    quality_scores = []
    for entry in metric_entries:
        analytics = entry.get("analytics") or {}
        views = analytics.get("views")
        avg_view_duration = analytics.get("average_view_duration")
        retention = analytics.get("audience_retention")

        if views in (None, 0):
            continue

        view_score = min(1.0, float(views) / 20000.0) if isinstance(views, (int, float)) else 0.5
        duration_score = 0.0
        if isinstance(avg_view_duration, (int, float)) and avg_view_duration > 0:
            duration_score = min(1.0, avg_view_duration / 180.0)

        retention_score = 0.0
        if isinstance(retention, (int, float)):
            retention_score = max(0.0, min(1.0, retention / 100.0))

        quality_scores.append((view_score + duration_score + retention_score) / 3.0)

    if not quality_scores:
        return 0.5

    return sum(quality_scores) / len(quality_scores)


def get_episode_count() -> int:
    """Get total episode count."""
    return len(load_history())


if __name__ == "__main__":
    history = load_history()
    print(f"Total episodes: {len(history)}")

    if history:
        print("\nRecent episodes:")
        for ep in history[-5:]:
            print(f"  [{ep['date']}] {ep['metric_key']}: {ep['title']}")

    covered = get_covered_metrics(weeks=4)
    print(f"\nCovered in last 4 weeks: {covered or 'none'}")
