"""
Pre-upload quality gate for automated publishing.

The gate checks artifact completeness, script structure, topic novelty, metadata
quality, and optional disclosure requirements. It returns structured issues and a
machine-readable decision (pass/fail).
"""

from __future__ import annotations

from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import json


MAX_TITLE_LENGTH = 100
IDEAL_TITLE_LENGTH = 70
MIN_WORD_COUNT = 520
MAX_TAGS = 30
MIN_TAGS = 10
REQUIRED_MARKERS = {
    "cold_open",
    "hook",
    "the_number",
    "chart_walk",
    "context",
    "connected_data",
    "insight",
    "close",
}


def _ensure_path(value: Any) -> str:
    """Return a non-empty path string."""
    if value is None:
        return ""
    return str(value)


def _path_exists(path: Any) -> bool:
    """Check if a filesystem path exists."""
    return bool(path and Path(str(path)).exists())


def _issue(code: str, severity: str, message: str, **meta: Any) -> dict[str, Any]:
    """Build a normalized issue item."""
    issue = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    issue.update(meta)
    return issue


def _load_json(path: Any) -> dict[str, Any]:
    """Safely load a JSON file."""
    if not _path_exists(path):
        return {}
    try:
        return json.loads(Path(str(path)).read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _check_text(value: str, label: str, required: bool = True) -> list[dict[str, Any]]:
    """Validate required text fields and minimum non-empty content."""
    issues: list[dict[str, Any]] = []
    if not isinstance(value, str) or not value.strip():
        if required:
            issues.append(_issue(f"missing_{label}", "error", f"Missing required {label}."))
        return issues

    if label == "title":
        if len(value) > MAX_TITLE_LENGTH:
            issues.append(
                _issue(
                    "title_too_long",
                    "warning",
                    f"Title exceeds {MAX_TITLE_LENGTH} chars.",
                )
            )
        if len(value) > IDEAL_TITLE_LENGTH:
            issues.append(
                _issue(
                    "title_not_ideal",
                    "warning",
                    f"Title longer than recommended {IDEAL_TITLE_LENGTH} chars.",
                )
            )

    return issues


def _max_similarity(left: str, candidates: list[str]) -> float:
    """Compute maximum normalized similarity against prior titles.

    This is a cheap de-duplication signal to avoid repetitive output.
    """
    best = 0.0
    left_clean = left.lower().strip()
    for candidate in candidates:
        ratio = SequenceMatcher(None, left_clean, candidate.lower().strip()).ratio()
        if ratio > best:
            best = ratio
    return best


def _extract_markers(script_data: dict[str, Any]) -> list[str]:
    """Extract section markers present in the script payload."""
    markers = []
    sections = script_data.get("sections", {})
    if isinstance(sections, dict):
        markers = [name for name in REQUIRED_MARKERS if sections.get(name)]

    if not markers:
        script_with_markers = script_data.get("script_with_markers", "")
        if isinstance(script_with_markers, str):
            for marker in REQUIRED_MARKERS:
                token = f"[{marker.upper()}]"
                if token in script_with_markers:
                    markers.append(marker)

    return markers


def _require_disclosure(dossier: dict[str, Any], tags: list[str]) -> list[dict[str, Any]]:
    """Require synthetic-content disclosure markers when flagged."""
    if not dossier.get("disclosed_synthetic_content"):
        return []

    normalized_tags = {t.lower() for t in tags}
    disclosure_markers = {
        "#synthetic",
        "#ai",
        "#disclosure",
    }
    if not disclosure_markers.intersection(normalized_tags):
        return [
            _issue(
                "missing_disclosure",
                "error",
                "Research dossier flagged synthetic media but tags do not include disclosure markers.",
            )
        ]
    return []


def run_quality_gate(
    script_data: dict[str, Any],
    artifact_paths: dict[str, Any],
    *,
    previous_titles: list[str] | None = None,
    strict: bool = True,
    min_word_count: int | None = None,
) -> dict[str, Any]:
    """Run the publishability checks and return a structured report.

    min_word_count: override default MIN_WORD_COUNT for this run (e.g. shorter legacy scripts).
    """
    issues: list[dict[str, Any]] = []
    word_floor = MIN_WORD_COUNT if min_word_count is None else int(min_word_count)

    title = script_data.get("title", "")
    description = script_data.get("description", "")
    tags = script_data.get("tags", [])
    sections = script_data.get("sections", {})
    script_text = script_data.get("script", "")
    dossier = script_data.get("research_dossier", {}) or {}

    if not isinstance(tags, list):
        tags = []

    issues.extend(_check_text(title, "title"))
    issues.extend(_check_text(description, "description"))
    issues.extend(_check_text(script_text, "script"))

    if not isinstance(sections, dict) or any(not sections.get(sec) for sec in REQUIRED_MARKERS):
        issues.append(
            _issue(
                "missing_sections",
                "error",
                "One or more required script sections are missing.",
                required=list(sorted(REQUIRED_MARKERS)),
            )
        )

    wc = len(script_text.split())
    if wc < word_floor:
        issues.append(
            _issue(
                "short_script",
                "error",
                f"Script is too short ({wc} words; minimum {word_floor}).",
            )
        )

    markers_found = _extract_markers(script_data)
    if len(markers_found) < len(REQUIRED_MARKERS):
        issues.append(
            _issue(
                "missing_markers",
                "warning",
                f"Only {len(markers_found)} of {len(REQUIRED_MARKERS)} script markers found.",
                found=markers_found,
            )
        )

    if len(tags) < MIN_TAGS:
        issues.append(
            _issue(
                "insufficient_tags",
                "warning",
                f"Only {len(tags)} tags provided; target is at least {MIN_TAGS}.",
            )
        )
    if len(tags) > MAX_TAGS:
        issues.append(
            _issue(
                "too_many_tags",
                "warning",
                f"Too many tags ({len(tags)}). YouTube supports up to {MAX_TAGS}.",
            )
        )

    if not _path_exists(artifact_paths.get("voiceover_path")):
        issues.append(_issue("missing_voiceover", "error", "Voiceover file missing."))

    if not _path_exists(artifact_paths.get("thumbnail_path")):
        issues.append(_issue("missing_thumbnail", "error", "Thumbnail file missing."))

    if not _path_exists(artifact_paths.get("final_video_path")):
        issues.append(_issue("missing_final_video", "error", "Final video file missing."))

    if not _path_exists(artifact_paths.get("script_json_path")):
        issues.append(_issue("missing_script_artifact", "error", "Latest script JSON artifact missing."))

    storyboard_path = artifact_paths.get("storyboard_path")
    if not _path_exists(storyboard_path):
        issues.append(
            _issue(
                "missing_storyboard",
                "error",
                "Storyboard manifest is missing.",
            )
        )
    else:
        storyboard = _load_json(storyboard_path)
        beats = storyboard.get("beats", []) if isinstance(storyboard, dict) else []
        if len(beats) < 8:
            issues.append(
                _issue(
                    "thin_storyboard",
                    "warning",
                    f"Storyboard has only {len(beats)} beats; target is at least 8.",
                )
            )

    voiceover_timeline_path = artifact_paths.get("voiceover_timeline_path")
    if not _path_exists(voiceover_timeline_path):
        issues.append(
            _issue(
                "missing_voiceover_timeline",
                "error",
                "Voiceover timing manifest is missing.",
            )
        )
    else:
        voiceover_timeline = _load_json(voiceover_timeline_path)
        total_voiceover_duration = voiceover_timeline.get("duration_sec")
        section_count = len(voiceover_timeline.get("sections", []))
        if total_voiceover_duration in (None, ""):
            issues.append(
                _issue(
                    "missing_voiceover_duration",
                    "error",
                    "Voiceover timing manifest is missing total duration.",
                )
            )
        if section_count < len(REQUIRED_MARKERS):
            issues.append(
                _issue(
                    "incomplete_voiceover_timeline",
                    "error",
                    f"Voiceover timing manifest only covers {section_count} sections.",
                )
            )
        storyboard = _load_json(storyboard_path) if _path_exists(storyboard_path) else {}
        storyboard_duration = storyboard.get("audio_duration_sec")
        if (
            total_voiceover_duration not in (None, "")
            and storyboard_duration not in (None, "")
            and abs(float(total_voiceover_duration) - float(storyboard_duration)) > 1.0
        ):
            issues.append(
                _issue(
                    "storyboard_timing_mismatch",
                    "error",
                    "Storyboard duration diverges from voiceover timing by more than one second.",
                )
            )

    loudness_report_path = artifact_paths.get("audio_quality_report_path")
    if not _path_exists(loudness_report_path):
        issues.append(
            _issue(
                "missing_audio_quality_report",
                "error",
                "Missing LUFS/true-peak report artifact.",
            )
        )
    else:
        loudness = _load_json(loudness_report_path)
        metrics = loudness.get("metrics", {}) if isinstance(loudness, dict) else {}
        if metrics.get("integrated_lufs") in (None, ""):
            issues.append(
                _issue(
                    "missing_lufs_metric",
                    "error",
                    "Audio quality report is missing integrated LUFS metric.",
                )
            )
        if metrics.get("true_peak_dbtp") in (None, ""):
            issues.append(
                _issue(
                    "missing_true_peak_metric",
                    "error",
                    "Audio quality report is missing true-peak metric.",
                )
            )

    provenance_path = artifact_paths.get("music_provenance_path")
    if not _path_exists(provenance_path):
        issues.append(
            _issue(
                "missing_music_provenance",
                "error",
                "Missing music-license provenance tag artifact.",
            )
        )
    else:
        provenance = _load_json(provenance_path)
        if not provenance.get("file_path"):
            issues.append(
                _issue(
                    "missing_music_provenance_file_path",
                    "error",
                    "Music provenance must include file_path.",
                )
            )
        if not provenance.get("license_id"):
            issues.append(
                _issue(
                    "missing_music_provenance_license_id",
                    "error",
                    "Music provenance must include license_id.",
                )
            )
        if not provenance.get("source"):
            issues.append(
                _issue(
                    "missing_music_provenance_source",
                    "error",
                    "Music provenance must include source.",
                )
            )

    # Repetition checks
    previous = previous_titles or []
    if previous:
        similarity = _max_similarity(title, previous)
        if similarity >= 0.78:
            issues.append(
                _issue(
                    "low_novelty",
                    "warning" if strict else "error",
                    "Title is highly similar to recent episodes.",
                    similarity=round(similarity, 3),
                )
            )

    # Disclosure checks (synthetic visuals / realism flags)
    issues.extend(_require_disclosure(dossier, [str(tag) for tag in tags]))

    errors = [issue for issue in issues if issue["severity"] == "error"]
    passed = len(errors) == 0
    status = "pass" if passed else "fail"

    return {
        "status": status,
        "passed": passed,
        "passed_at": datetime.now().isoformat(),
        "checks": {
            "markers": {
                "required": sorted(REQUIRED_MARKERS),
                "found": sorted(markers_found),
            },
            "word_count": wc,
            "min_word_count": word_floor,
            "tag_count": len(tags),
            "has_research_dossier": bool(dossier),
            "has_storyboard": _path_exists(storyboard_path),
            "has_voiceover_timeline": _path_exists(voiceover_timeline_path),
        },
        "issues": issues,
        "strict": strict,
    }


def quality_gate_report_path(result: dict[str, Any], run_dir: str | Path) -> str:
    """Persist the quality gate result for audit and debugging."""
    path = Path(run_dir) / "quality_gate.json"
    path.write_text(json.dumps(result, indent=2))
    return str(path)
