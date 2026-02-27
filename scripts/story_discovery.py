# scripts/story_discovery.py
# ─────────────────────────────────────────────
# Scores stories by viral potential, finds related indicators
# ─────────────────────────────────────────────

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import STORY_WEIGHTS, PUBLIC_INTEREST, PAIN_POINT, FRED_SERIES


class StoryDiscovery:
    def __init__(self, fred_data: dict):
        """
        fred_data: dict returned by FREDClient.fetch_all()
        """
        self.data = fred_data

    # ── Scoring ───────────────────────────────

    def score_story(self, key: str) -> float:
        """
        Score a single indicator on a 0–100 scale.
        """
        item = self.data.get(key)
        if not item:
            return 0.0

        category = item.get("category", "Market")

        # 1. Magnitude: normalized YoY % change (cap at 50% for scoring)
        magnitude = min(abs(item.get("yoy_pct", 0.0)), 50.0) / 50.0

        # 2. Public interest
        interest = PUBLIC_INTEREST.get(category, 0.5)

        # 3. Pain point
        pain = PAIN_POINT.get(category, 0.5)

        # 4. Freshness: days since last update (fresher = higher score)
        try:
            from datetime import datetime
            last = datetime.strptime(item["last_updated"], "%Y-%m-%d")
            days_old = (datetime.now() - last).days
            freshness = max(0.0, 1.0 - days_old / 90.0)   # 0 after 90 days
        except Exception:
            freshness = 0.5

        score = (
            STORY_WEIGHTS["magnitude"]       * magnitude +
            STORY_WEIGHTS["public_interest"] * interest  +
            STORY_WEIGHTS["pain_point"]      * pain      +
            STORY_WEIGHTS["freshness"]       * freshness
        ) * 100

        return round(score, 2)

    def rank_stories(self) -> list[dict]:
        """
        Score and rank all available indicators.
        Returns a sorted list of dicts with keys: key, label, score, yoy_pct, category.
        """
        ranked = []
        for key, item in self.data.items():
            score = self.score_story(key)
            ranked.append({
                "key":     key,
                "label":   item.get("label", key),
                "score":   score,
                "yoy_pct": item.get("yoy_pct", 0.0),
                "latest":  item.get("latest", 0.0),
                "unit":    item.get("unit", ""),
                "category":item.get("category", ""),
            })
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def top_story(self) -> dict:
        """
        Returns the highest-scoring story's full data package.
        """
        ranked = self.rank_stories()
        if not ranked:
            return {}
        winner = ranked[0]
        key = winner["key"]
        return self._build_story_package(key)

    def story_for_key(self, key: str) -> dict:
        """
        Returns a full story package for a specific indicator key.
        """
        return self._build_story_package(key)

    # ── Story Package ─────────────────────────

    def _build_story_package(self, key: str) -> dict:
        """
        Builds a rich story package with the main indicator + related indicators.
        """
        item = self.data.get(key)
        if not item:
            return {}

        # Find related indicators (same category, excluding self)
        category = item.get("category", "")
        related = [
            {
                "key":     k,
                "label":   v.get("label", k),
                "latest":  v.get("latest", 0.0),
                "unit":    v.get("unit", ""),
                "yoy_pct": v.get("yoy_pct", 0.0),
            }
            for k, v in self.data.items()
            if v.get("category") == category and k != key
        ]

        return {
            "key":      key,
            "item":     item,
            "related":  related,
            "score":    self.score_story(key),
            "category": category,
        }


if __name__ == "__main__":
    import json
    from pathlib import Path
    from scripts.data_ingestion import FREDClient

    client = FREDClient()
    data = client.fetch_all()

    discovery = StoryDiscovery(data)
    ranked = discovery.rank_stories()

    print("\nTop 10 Stories:")
    for i, s in enumerate(ranked[:10], 1):
        print(f"  {i:2}. [{s['score']:5.1f}] {s['label']:40s}  YoY={s['yoy_pct']:+.1f}%")

    top = discovery.top_story()
    print(f"\nWinner: {top['item']['label']}  (score={top['score']})")
