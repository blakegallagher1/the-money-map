"""Tests for beat-level storyboard planning."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "storyboard_planner.py"
SPEC = importlib.util.spec_from_file_location("storyboard_planner", MODULE_PATH)
storyboard_planner = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(storyboard_planner)


def _script_payload() -> dict:
    return {
        "sections": {
            "cold_open": "Debt just hit a new high.",
            "hook": "The debt story matters because rates are still elevated. That changes the bill taxpayers carry.",
            "the_number": "Federal debt now stands at 37 point 6 trillion dollars. One year ago it was 35 point 5 trillion dollars.",
            "chart_walk": "Watch the line bend higher after the pandemic. The slope steepens again as borrowing costs stay high.",
            "context": "The ten-year yield is elevated. Growth is slowing. The Fed has less room to cut without consequences.",
            "connected_data": "These pressures reinforce each other and make the debt load harder to finance.",
            "insight": "For households and investors, that means more federal revenue diverted to interest instead of productive uses. It also means less policy flexibility in the next slowdown.",
            "close": "Subscribe for the next data-driven briefing.",
        },
        "broll_prompts": {
            "hook": "Moody dusk shot of the Capitol under gathering storm clouds.",
            "context": "Institutional finance desks, treasury screens, and government buildings.",
            "insight": "American households and investors absorbing higher financing pressure.",
        },
        "primary_metric": {
            "name": "Federal Debt",
            "latest_value": 37.6,
            "unit": "trillion dollars",
        },
    }


def test_build_storyboard_uses_voiceover_durations_and_plans_broll() -> None:
    """Storyboard should aggregate scene timings from exact section durations."""
    timeline = {
        "sections": [
            {"id": "cold_open", "duration_sec": 4.0},
            {"id": "hook", "duration_sec": 10.0},
            {"id": "the_number", "duration_sec": 11.0},
            {"id": "chart_walk", "duration_sec": 12.0},
            {"id": "context", "duration_sec": 10.0},
            {"id": "connected_data", "duration_sec": 7.0},
            {"id": "insight", "duration_sec": 14.0},
            {"id": "close", "duration_sec": 5.0},
        ]
    }

    storyboard = storyboard_planner.build_storyboard(
        _script_payload(),
        voiceover_timeline=timeline,
    )

    assert storyboard["scene_durations"]["hook"] == 21.0
    assert storyboard["scene_durations"]["context"] == 17.0
    assert storyboard["audio_duration_sec"] == 73.0
    assert storyboard["beat_count"] >= 8
    assert len(storyboard["broll_prompts"]) >= 3
    assert any(beat["visual_type"] == "broll" for beat in storyboard["beats"])


def test_ordered_section_entries_preserve_required_section_order() -> None:
    """Ordered section extraction should follow the canonical pipeline sequence."""
    ordered = storyboard_planner.ordered_section_entries(_script_payload())
    assert [entry["id"] for entry in ordered] == storyboard_planner.SECTION_ORDER
