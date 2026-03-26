"""Tests for story discovery scoring and coverage selection."""

from pathlib import Path

from scripts import story_discovery


def test_analyze_data_selects_top_story_and_sorts_scores(tmp_path: Path, monkeypatch) -> None:
    """Story selection should return the highest-scored metric with metadata."""
    data_path = tmp_path / "latest_data.json"
    data_path.write_text(
        '{"data": {'
        '"metric_a": {"name":"Metric A","yoy_pct":15.0,"yoy_change":1.2,'
        '"latest_value":100,"latest_date":"2026-03-25","prev_year_value":120,'
        '"series_id":"A","unit":"%",},'
        '"metric_b": {"name":"Metric B","yoy_pct":-8.0,"yoy_change":-0.8,'
        '"latest_value":200,"latest_date":"2026-03-25","prev_year_value":260,'
        '"series_id":"B","unit":"$",}}'
    )

    monkeypatch.setenv("HOME", str(tmp_path))

    def _no_penalty(*_):
        return 0

    import scripts.episode_tracker

    monkeypatch.setattr(scripts.episode_tracker, "get_metric_health_score", lambda _: 0.5)
    monkeypatch.setattr(scripts.episode_tracker, "get_recency_penalty", _no_penalty)

    result = story_discovery.analyze_data(str(data_path))
    assert result["top_story"]["key"] == "metric_a"
    assert result["stories"][0]["score"] >= result["stories"][1]["score"]


def test_find_related_series_returns_known_relations() -> None:
    """The related-series helper should filter to available data entries."""
    all_data = {
        "mortgage_rate_30yr": {"name": "Mortgage Rate", "id": "a"},
        "housing_starts": {"name": "Housing Starts", "id": "b"},
        "fed_funds_rate": {"name": "Fed Funds", "id": "c"},
        "case_shiller": {"name": "Case Shiller", "id": "d"},
    }

    related = story_discovery.find_related_series("median_home_price", all_data)
    related_keys = {item["name"] for item in related}
    assert "Mortgage Rate" in related_keys
    assert "Housing Starts" in related_keys
    assert "Fed Funds" in related_keys
