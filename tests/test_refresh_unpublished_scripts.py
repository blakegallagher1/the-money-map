"""Tests for unpublished draft script refresh helpers."""

import importlib.util
import json
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "refresh_unpublished_scripts.py"
)
SPEC = importlib.util.spec_from_file_location("refresh_unpublished_scripts", MODULE_PATH)
refresh_unpublished_scripts = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(refresh_unpublished_scripts)


def test_published_titles_only_keeps_entries_with_video_urls() -> None:
    """Only history rows with a populated YouTube URL should count as published."""
    history = [
        {"title": "Published", "video_url": "https://youtube.test/watch?v=1"},
        {"title": "Draft", "video_url": None},
        {"title": "Blank URL", "video_url": ""},
    ]

    assert refresh_unpublished_scripts.published_titles(history) == {"Published"}


def test_select_unpublished_script_paths_ignores_published_title_matches(tmp_path: Path) -> None:
    """Draft selection should skip scripts already published under the same title."""
    data_dir = tmp_path / "data"
    published_dir = data_dir / "ep1_v2"
    unpublished_dir = data_dir / "ep2_v2"
    published_dir.mkdir(parents=True)
    unpublished_dir.mkdir(parents=True)

    (published_dir / "script.json").write_text(json.dumps({"title": "Already Live"}))
    (unpublished_dir / "script.json").write_text(json.dumps({"title": "Still Draft"}))

    history = [
        {"title": "Already Live", "video_url": "https://youtube.test/watch?v=1"},
        {"title": "Still Draft", "video_url": None},
    ]

    selected = refresh_unpublished_scripts.select_unpublished_script_paths(data_dir, history)

    assert selected == [unpublished_dir / "script.json"]


def test_build_story_package_for_metric_reuses_latest_metric_context() -> None:
    """Metric-targeted story packages should preserve the requested primary series."""
    latest_data = {
        "data": {
            "gas_price": {
                "name": "Regular Gas Price",
                "series_id": "GASREGW",
                "unit": "$/gallon",
                "latest_date": "2026-03-23",
                "latest_value": 3.961,
                "yoy_change": 0.8,
                "yoy_pct": 25.35,
                "prev_year_value": 3.161,
                "score": 45,
                "tags": ["high_public_interest"],
            },
            "cpi_energy": {
                "name": "CPI: Energy",
                "series_id": "CPIENGSL",
                "unit": "index",
                "latest_date": "2026-02-01",
                "latest_value": 300.0,
                "yoy_change": 10.0,
                "yoy_pct": 3.4,
                "prev_year_value": 290.0,
            },
            "cpi": {
                "name": "Consumer Price Index",
                "series_id": "CPIAUCSL",
                "unit": "index",
                "latest_date": "2026-02-01",
                "latest_value": 320.0,
                "yoy_change": 8.0,
                "yoy_pct": 2.6,
                "prev_year_value": 312.0,
            },
            "consumer_confidence": {
                "name": "Consumer Sentiment",
                "series_id": "UMCSENT",
                "unit": "index",
                "latest_date": "2026-03-01",
                "latest_value": 69.0,
                "yoy_change": -2.0,
                "yoy_pct": -2.8,
                "prev_year_value": 71.0,
            },
        }
    }
    ranked_stories = [
        {
            "key": "gas_price",
            "name": "Regular Gas Price",
            "series_id": "GASREGW",
            "unit": "$/gallon",
            "latest_date": "2026-03-23",
            "latest_value": 3.961,
            "yoy_change": 0.8,
            "yoy_pct": 25.35,
            "prev_year_value": 3.161,
            "score": 45,
            "tags": ["high_public_interest"],
        }
    ]

    package = refresh_unpublished_scripts.build_story_package_for_metric(
        latest_data,
        ranked_stories,
        "gas_price",
    )

    assert package["primary"]["key"] == "gas_price"
    assert package["primary"]["latest_value"] == 3.961
    assert [item["name"] for item in package["related"]] == [
        "CPI: Energy",
        "Consumer Price Index",
        "Consumer Sentiment",
    ]


def test_write_script_artifacts_updates_json_and_voiceover_script(tmp_path: Path) -> None:
    """Refreshing a script should keep the JSON and voiceover text in sync."""
    script_dir = tmp_path / "data" / "ep1_v2"
    script_dir.mkdir(parents=True)
    script_path = script_dir / "script.json"

    refresh_unpublished_scripts.write_script_artifacts(
        script_path,
        {
            "title": "Updated Draft",
            "script": "Line one.\nLine two.",
            "primary_metric": {"key": "gas_price"},
        },
    )

    payload = json.loads(script_path.read_text())
    assert payload["title"] == "Updated Draft"
    assert (script_dir / "voiceover_script.txt").read_text() == "Line one.\nLine two.\n"


def test_normalize_plaintext_replaces_curly_punctuation_and_control_bytes() -> None:
    """Voiceover text should be ASCII-safe before it reaches TTS or subtitles."""
    normalized = refresh_unpublished_scripts.normalize_plaintext(
        "America\u2019s outlook\u2014still noisy.\x19"
    )

    assert normalized == "America's outlook-still noisy."
