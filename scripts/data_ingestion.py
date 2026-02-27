"""
Module 1: Data Ingestion — Pulls fresh data from FRED, Census, and BLS APIs.
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FRED_API_KEY, FRED_SERIES


class FREDClient:
    """Federal Reserve Economic Data API client."""
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: str = FRED_API_KEY):
        self.api_key = api_key
    
    def get_series(self, series_id: str, start_date: str = None, 
                   end_date: str = None, limit: int = 500) -> dict:
        """Fetch a time series from FRED."""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*10)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
            "sort_order": "desc",
            "limit": limit,
        }
        resp = requests.get(f"{self.BASE_URL}/series/observations", params=params)
        resp.raise_for_status()
        data = resp.json()
        
        observations = []
        for obs in data.get("observations", []):
            if obs["value"] != ".":
                observations.append({
                    "date": obs["date"],
                    "value": float(obs["value"]),
                })
        return {
            "series_id": series_id,
            "observations": observations,
            "count": len(observations),
        }
    
    def get_series_info(self, series_id: str) -> dict:
        """Get metadata about a series."""
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }
        resp = requests.get(f"{self.BASE_URL}/series", params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("seriess"):
            s = data["seriess"][0]
            return {
                "id": s["id"],
                "title": s["title"],
                "frequency": s.get("frequency_short", ""),
                "units": s.get("units", ""),
                "last_updated": s.get("last_updated", ""),
            }
        return {}
    
    def get_all_curated_latest(self) -> dict:
        """Pull latest values for all curated series."""
        results = {}
        for key, meta in FRED_SERIES.items():
            try:
                data = self.get_series(meta["id"], limit=60)
                if data["observations"]:
                    latest = data["observations"][0]
                    prev_year = None
                    # Find same-ish period last year
                    latest_date = datetime.strptime(latest["date"], "%Y-%m-%d")
                    for obs in data["observations"]:
                        obs_date = datetime.strptime(obs["date"], "%Y-%m-%d")
                        diff = (latest_date - obs_date).days
                        if 300 < diff < 400:
                            prev_year = obs
                            break
                    
                    yoy_change = None
                    yoy_pct = None
                    if prev_year:
                        yoy_change = latest["value"] - prev_year["value"]
                        if prev_year["value"] != 0:
                            yoy_pct = (yoy_change / prev_year["value"]) * 100
                    
                    results[key] = {
                        "name": meta["name"],
                        "series_id": meta["id"],
                        "unit": meta["unit"],
                        "latest_date": latest["date"],
                        "latest_value": latest["value"],
                        "yoy_change": round(yoy_change, 2) if yoy_change else None,
                        "yoy_pct": round(yoy_pct, 2) if yoy_pct else None,
                        "prev_year_value": prev_year["value"] if prev_year else None,
                        "prev_year_date": prev_year["date"] if prev_year else None,
                    }
            except Exception as e:
                print(f"  Warning: Failed to fetch {key} ({meta['id']}): {e}")
        return results


def fetch_fresh_data(output_path: str = None) -> dict:
    """Main entry point: fetch all fresh data and save to JSON."""
    print("=== FRED Data Ingestion ===")
    client = FREDClient()
    
    print(f"Fetching {len(FRED_SERIES)} economic indicators...")
    latest = client.get_all_curated_latest()
    print(f"Successfully fetched {len(latest)} series.")
    
    result = {
        "fetched_at": datetime.now().isoformat(),
        "source": "FRED (Federal Reserve Economic Data)",
        "series_count": len(latest),
        "data": latest,
    }
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Saved to {output_path}")
    
    return result


if __name__ == "__main__":
    data = fetch_fresh_data("/home/user/workspace/the-money-map/data/latest_data.json")
    print(f"\nFetched {data['series_count']} indicators.")
    movers = []
    for key, d in data["data"].items():
        if d.get("yoy_pct") is not None:
            movers.append((key, d["name"], d["yoy_pct"]))
    movers.sort(key=lambda x: abs(x[2]), reverse=True)
    print("\nTop 10 YoY movers:")
    for key, name, pct in movers[:10]:
        direction = "↑" if pct > 0 else "↓"
        print(f"  {direction} {name}: {pct:+.1f}%")
