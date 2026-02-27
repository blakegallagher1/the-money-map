# scripts/data_ingestion.py
# ─────────────────────────────────────────────
# FREDClient — fetches all 34 indicators with YoY calculations
# ─────────────────────────────────────────────

import os
import sys
import json
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fredapi import Fred
from config.settings import FRED_API_KEY, FRED_SERIES


class FREDClient:
    def __init__(self):
        self.fred = Fred(api_key=FRED_API_KEY)

    def fetch_series(self, series_id: str, periods: int = 24) -> dict:
        """
        Fetch the most recent `periods` observations for a FRED series.
        Returns a dict with keys: values (list), dates (list), latest, yoy_change, yoy_pct.
        """
        try:
            series = self.fred.get_series(series_id)
            series = series.dropna()
            if len(series) < 2:
                return None

            recent = series.tail(periods)
            dates = [d.strftime("%Y-%m-%d") for d in recent.index]
            values = [round(float(v), 4) for v in recent.values]

            latest = values[-1]

            # Year-over-year change
            if len(series) >= 13:
                one_year_ago = series.iloc[-13] if len(series) >= 13 else series.iloc[0]
                yoy_change = round(latest - float(one_year_ago), 4)
                yoy_pct = round((yoy_change / float(one_year_ago)) * 100, 2) if one_year_ago != 0 else 0.0
            else:
                yoy_change = 0.0
                yoy_pct = 0.0

            return {
                "series_id": series_id,
                "latest": latest,
                "yoy_change": yoy_change,
                "yoy_pct": yoy_pct,
                "dates": dates,
                "values": values,
                "last_updated": dates[-1],
            }
        except Exception as e:
            print(f"  [WARN] Failed to fetch {series_id}: {e}")
            return None

    def fetch_all(self) -> dict:
        """
        Fetch all 34 indicators defined in settings.FRED_SERIES.
        Returns a dict keyed by story key (e.g. 'MORTGAGE_RATE_30Y').
        """
        results = {}
        print(f"Fetching {len(FRED_SERIES)} FRED indicators...")
        for key, meta in FRED_SERIES.items():
            print(f"  Fetching {key} ({meta['series_id']})...", end=" ")
            data = self.fetch_series(meta["series_id"])
            if data:
                data.update(meta)   # merge in label, unit, category
                results[key] = data
                print(f"✓  latest={data['latest']}{meta['unit']}  YoY={data['yoy_pct']:+.1f}%")
            else:
                print("✗ skipped")
        print(f"\nFetched {len(results)}/{len(FRED_SERIES)} indicators.")
        return results


if __name__ == "__main__":
    client = FREDClient()
    data = client.fetch_all()
    # Save snapshot
    out = Path(__file__).parent.parent / "output" / "fred_snapshot.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSnapshot saved to {out}")
