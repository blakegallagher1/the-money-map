"""Beat-level storyboard planning for The Money Map episodes."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


SECTION_ORDER = [
    "cold_open",
    "hook",
    "the_number",
    "chart_walk",
    "context",
    "connected_data",
    "insight",
    "close",
]
SCENE_ORDER = ["cold_open", "hook", "chart_walk", "context", "insight", "close"]
SCENE_SECTION_MAP = {
    "cold_open": ["cold_open"],
    "hook": ["hook", "the_number"],
    "chart_walk": ["chart_walk"],
    "context": ["context", "connected_data"],
    "insight": ["insight"],
    "close": ["close"],
}
SECTION_TO_SCENE = {
    section_id: scene_name
    for scene_name, section_ids in SCENE_SECTION_MAP.items()
    for section_id in section_ids
}
BROLL_SECTIONS = {"hook", "context", "insight"}
TARGET_BEAT_WORDS = 22
MAX_BEATS_PER_SECTION = 3


def ordered_section_entries(script_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the ordered non-empty script sections."""
    sections = script_data.get("sections", {}) if isinstance(script_data, dict) else {}
    ordered: list[dict[str, Any]] = []
    for section_id in SECTION_ORDER:
        text = str(sections.get(section_id, "")).strip()
        if not text:
            continue
        ordered.append(
            {
                "id": section_id,
                "text": text,
                "word_count": len(text.split()),
            }
        )
    return ordered


def estimate_section_duration(word_count: int) -> float:
    """Estimate spoken section duration when real audio timing is unavailable."""
    return max(3.0, round(word_count / 2.45, 3))


def split_section_into_beats(text: str, *, target_words: int = TARGET_BEAT_WORDS) -> list[str]:
    """Split section narration into 1-3 readable beat chunks."""
    cleaned = text.strip()
    if not cleaned:
        return []

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", cleaned.replace("...", ". "))
        if sentence.strip()
    ]
    if len(sentences) <= 1:
        return [cleaned]

    beats: list[str] = []
    current: list[str] = []
    current_words = 0
    remaining_slots = MAX_BEATS_PER_SECTION
    for sentence in sentences:
        sentence_words = len(sentence.split())
        candidate_words = current_words + sentence_words
        should_break = (
            current
            and candidate_words > target_words
            and remaining_slots > 1
        )
        if should_break:
            beats.append(" ".join(current).strip())
            remaining_slots -= 1
            current = [sentence]
            current_words = sentence_words
            continue
        current.append(sentence)
        current_words = candidate_words

    if current:
        beats.append(" ".join(current).strip())

    if len(beats) <= MAX_BEATS_PER_SECTION:
        return beats

    merged = beats[: MAX_BEATS_PER_SECTION - 1]
    merged.append(" ".join(beats[MAX_BEATS_PER_SECTION - 1 :]).strip())
    return merged


def _distribute_duration(total_duration: float, weights: list[int]) -> list[float]:
    """Distribute a duration proportionally across weighted beats."""
    if not weights:
        return []
    if len(weights) == 1:
        return [round(total_duration, 3)]

    safe_weights = [max(weight, 1) for weight in weights]
    weight_total = sum(safe_weights)
    cursor = 0.0
    durations: list[float] = []
    for index, weight in enumerate(safe_weights):
        if index == len(safe_weights) - 1:
            durations.append(round(total_duration - cursor, 3))
            break
        duration = round(total_duration * weight / weight_total, 3)
        durations.append(duration)
        cursor += duration
    return durations


def _broll_positions(section_id: str, beat_count: int, duration_sec: float) -> set[int]:
    """Return beat indexes that should use generated b-roll for a section."""
    if section_id not in BROLL_SECTIONS or beat_count <= 0 or duration_sec < 6.0:
        return set()
    if beat_count == 1:
        return {0}
    positions = {0}
    if beat_count >= 3 and duration_sec >= 14.0:
        positions.add(beat_count - 1)
    return positions


def _primary_metric_phrase(primary_metric: dict[str, Any]) -> str:
    """Build a compact metric phrase for prompt grounding."""
    if not primary_metric:
        return "the featured macroeconomic indicator"
    name = str(primary_metric.get("name", "the featured macroeconomic indicator")).strip()
    value = primary_metric.get("latest_value")
    unit = str(primary_metric.get("unit", "")).strip()
    if value is None:
        return name
    return f"{name} at {value} {unit}".strip()


def _compose_broll_prompt(
    section_id: str,
    beat_text: str,
    base_prompt: str,
    primary_metric: dict[str, Any],
) -> str:
    """Compose a beat-specific b-roll prompt from script context."""
    guidance = {
        "hook": "Establish emotional stakes immediately with human-scale context.",
        "context": "Show causal forces, infrastructure, institutions, or market mechanics.",
        "insight": "Show concrete household or investor consequences in the real world.",
    }.get(section_id, "Illustrate the narration with grounded documentary realism.")
    parts = []
    if base_prompt:
        parts.append(base_prompt.rstrip("."))
    parts.append(guidance)
    parts.append(f"Narration beat: {beat_text}")
    parts.append(f"Topic anchor: {_primary_metric_phrase(primary_metric)}.")
    parts.append(
        "Photorealistic documentary cinematography, realistic lighting, 16:9, "
        "no text, no logos, no watermarks, no infographic overlays."
    )
    return " ".join(parts)


def build_storyboard(
    script_data: dict[str, Any],
    voiceover_timeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a beat-level storyboard from script sections and voice timing."""
    ordered_sections = ordered_section_entries(script_data)
    timeline_sections = {
        str(section.get("id")): section
        for section in (voiceover_timeline or {}).get("sections", [])
        if isinstance(section, dict) and section.get("id")
    }
    primary_metric = script_data.get("primary_metric", {}) or {}
    base_prompts = script_data.get("broll_prompts", {}) or {}

    section_entries: list[dict[str, Any]] = []
    cursor = 0.0
    for section in ordered_sections:
        timeline = timeline_sections.get(section["id"], {})
        duration_sec = float(
            timeline.get("duration_sec")
            or estimate_section_duration(section["word_count"])
        )
        entry = {
            **section,
            "duration_sec": round(duration_sec, 3),
            "start_sec": round(cursor, 3),
            "end_sec": round(cursor + duration_sec, 3),
            "scene_name": SECTION_TO_SCENE[section["id"]],
        }
        cursor += duration_sec
        section_entries.append(entry)

    scene_durations = {
        scene_name: round(
            sum(
                section["duration_sec"]
                for section in section_entries
                if section["id"] in section_ids
            ),
            3,
        )
        for scene_name, section_ids in SCENE_SECTION_MAP.items()
    }
    scene_ranges: dict[str, dict[str, float]] = {}
    scene_cursor = 0.0
    for scene_name in SCENE_ORDER:
        duration_sec = scene_durations.get(scene_name, 0.0)
        scene_ranges[scene_name] = {
            "start_sec": round(scene_cursor, 3),
            "end_sec": round(scene_cursor + duration_sec, 3),
        }
        scene_cursor += duration_sec

    scene_section_offsets: dict[str, float] = {}
    per_scene_cursor = {scene_name: 0.0 for scene_name in SCENE_ORDER}
    for section in section_entries:
        scene_name = section["scene_name"]
        scene_section_offsets[section["id"]] = per_scene_cursor[scene_name]
        per_scene_cursor[scene_name] += section["duration_sec"]

    beats: list[dict[str, Any]] = []
    broll_prompts: dict[str, str] = {}
    for section in section_entries:
        beat_texts = split_section_into_beats(section["text"])
        weights = [len(text.split()) for text in beat_texts]
        beat_durations = _distribute_duration(section["duration_sec"], weights)
        section_broll_positions = _broll_positions(
            section["id"], len(beat_texts), section["duration_sec"]
        )
        section_offset = 0.0
        broll_index = 0
        for beat_index, beat_text in enumerate(beat_texts):
            duration_sec = beat_durations[beat_index]
            beat_start = round(section["start_sec"] + section_offset, 3)
            beat_end = round(beat_start + duration_sec, 3)
            dataviz_start = round(
                scene_ranges[section["scene_name"]]["start_sec"]
                + scene_section_offsets[section["id"]]
                + section_offset,
                3,
            )
            dataviz_end = round(dataviz_start + duration_sec, 3)
            visual_type = "dataviz"
            asset_key = None
            if beat_index in section_broll_positions:
                visual_type = "broll"
                broll_index += 1
                asset_key = f"{section['id']}_broll_{broll_index}"
                base_prompt = str(
                    base_prompts.get(section["id"])
                    or base_prompts.get("hook" if section["id"] == "the_number" else section["id"])
                    or base_prompts.get("context" if section["id"] == "connected_data" else section["id"])
                    or ""
                )
                broll_prompts[asset_key] = _compose_broll_prompt(
                    section["id"],
                    beat_text,
                    base_prompt=base_prompt,
                    primary_metric=primary_metric,
                )
            beats.append(
                {
                    "id": f"{section['id']}_beat_{beat_index + 1}",
                    "section_id": section["id"],
                    "scene_name": section["scene_name"],
                    "text": beat_text,
                    "word_count": len(beat_text.split()),
                    "start_sec": beat_start,
                    "end_sec": beat_end,
                    "duration_sec": round(duration_sec, 3),
                    "dataviz_start_sec": dataviz_start,
                    "dataviz_end_sec": dataviz_end,
                    "visual_type": visual_type,
                    "asset_key": asset_key,
                }
            )
            section_offset += duration_sec

    total_duration = round(section_entries[-1]["end_sec"] if section_entries else 0.0, 3)
    return {
        "generated_at": datetime.now().isoformat(),
        "audio_duration_sec": total_duration,
        "section_count": len(section_entries),
        "beat_count": len(beats),
        "scene_count": len(SCENE_ORDER),
        "scene_order": SCENE_ORDER,
        "scene_durations": scene_durations,
        "scene_ranges": scene_ranges,
        "sections": section_entries,
        "beats": beats,
        "broll_prompts": broll_prompts,
    }


def save_storyboard(storyboard: dict[str, Any], path: str | Path) -> str:
    """Persist storyboard JSON and return the output path."""
    out_path = Path(path)
    out_path.write_text(json.dumps(storyboard, indent=2))
    return str(out_path)


def main() -> None:
    """Build a storyboard manifest from script and optional timing artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", required=True, help="Path to the script JSON file")
    parser.add_argument(
        "--voiceover-timeline",
        default=None,
        help="Optional voiceover timeline JSON path for exact section timings.",
    )
    parser.add_argument("--out", required=True, help="Path to write storyboard JSON")
    args = parser.parse_args()

    script_data = json.loads(Path(args.script).read_text())
    voiceover_timeline = (
        json.loads(Path(args.voiceover_timeline).read_text())
        if args.voiceover_timeline
        else None
    )
    storyboard = build_storyboard(script_data, voiceover_timeline=voiceover_timeline)
    save_storyboard(storyboard, args.out)


if __name__ == "__main__":
    main()
