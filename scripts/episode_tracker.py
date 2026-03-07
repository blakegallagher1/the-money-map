"""
Episode History Tracker for The Money Map
Tracks which metrics have been covered and when,
to prevent repeating topics too frequently.
"""
import json
import os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(BASE, 'data', 'episode_history.json')


def load_history():
    """Load episode history from disk."""
    if not os.path.exists(HISTORY_PATH):
        return []

    with open(HISTORY_PATH) as f:
        return json.load(f)


def save_history(history):
    """Save episode history to disk."""
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history, f, indent=2)


def record_episode(metric_key, title, score, video_url=None):
    """Record a produced episode in the history log."""
    history = load_history()

    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "metric_key": metric_key,
        "title": title,
        "score": score,
        "video_url": video_url,
    }

    history.append(entry)
    save_history(history)
    print(f"  Episode recorded: {metric_key} ({title})")
    return entry


def get_recency_penalty(metric_key, weeks_lookback=8):
    """Calculate a scoring penalty based on how recently a topic was covered.

    Returns:
        0 if never covered or covered >8 weeks ago
        -30 if covered in the last 4 weeks
        -15 if covered in the last 4-8 weeks
    """
    history = load_history()
    now = datetime.now()

    for entry in reversed(history):
        try:
            ep_date = datetime.strptime(entry['date'], "%Y-%m-%d")
        except (ValueError, KeyError):
            continue

        if entry.get('metric_key') != metric_key:
            continue

        days_ago = (now - ep_date).days

        if days_ago <= 28:  # 4 weeks
            return -30
        elif days_ago <= 56:  # 8 weeks
            return -15

    return 0


def get_covered_metrics(weeks=4):
    """Get list of metric keys covered in the last N weeks."""
    history = load_history()
    cutoff = datetime.now() - timedelta(weeks=weeks)
    covered = set()

    for entry in history:
        try:
            ep_date = datetime.strptime(entry['date'], "%Y-%m-%d")
            if ep_date >= cutoff:
                covered.add(entry['metric_key'])
        except (ValueError, KeyError):
            continue

    return covered


def get_episode_count():
    """Get total number of episodes produced."""
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
