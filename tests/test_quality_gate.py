"""Tests for pre-upload quality gating rules."""

import json
from pathlib import Path

import importlib.util


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "quality_gate.py"
SPEC = importlib.util.spec_from_file_location("quality_gate", MODULE_PATH)
quality_gate = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(quality_gate)
run_quality_gate = quality_gate.run_quality_gate
quality_gate_report_path = quality_gate.quality_gate_report_path


def _write_preupload_reports(tmp_path: Path) -> tuple[Path, Path]:
    loudness_path = tmp_path / "audio_quality_report.json"
    provenance_path = tmp_path / "music_provenance.json"
    loudness_path.write_text(
        json.dumps(
            {
                "metrics": {
                    "integrated_lufs": -15.8,
                    "true_peak_dbtp": -1.3,
                }
            }
        )
    )
    provenance_path.write_text(
        json.dumps(
            {
                "file_path": str(tmp_path / "music_track.wav"),
                "license_id": "voice_only",
                "source": "none",
            }
        )
    )
    return loudness_path, provenance_path


def _write_storyboard_reports(tmp_path: Path) -> tuple[Path, Path]:
    storyboard_path = tmp_path / "storyboard_manifest.json"
    timeline_path = tmp_path / "voiceover_timeline.json"
    storyboard_path.write_text(
        json.dumps(
            {
                "audio_duration_sec": 42.0,
                "beats": [{"id": f"beat_{index}", "duration_sec": 3.5} for index in range(12)],
                "broll_prompts": {"hook_broll_1": "prompt"},
            }
        )
    )
    timeline_path.write_text(
        json.dumps(
            {
                "duration_sec": 42.0,
                "sections": [
                    {"id": section_id, "duration_sec": 5.25}
                    for section_id in (
                        "cold_open",
                        "hook",
                        "the_number",
                        "chart_walk",
                        "context",
                        "connected_data",
                        "insight",
                        "close",
                    )
                ],
            }
        )
    )
    return storyboard_path, timeline_path


def _artifact_bundle(
    voiceover_path: Path | str,
    thumbnail_path: Path | str,
    final_video_path: Path | str,
    script_json_path: Path | str,
    audio_quality_report_path: Path | str,
    music_provenance_path: Path | str,
    storyboard_path: Path | str,
    voiceover_timeline_path: Path | str,
) -> dict:
    return {
        "voiceover_path": voiceover_path,
        "thumbnail_path": thumbnail_path,
        "final_video_path": final_video_path,
        "script_json_path": script_json_path,
        "audio_quality_report_path": audio_quality_report_path,
        "music_provenance_path": music_provenance_path,
        "storyboard_path": storyboard_path,
        "voiceover_timeline_path": voiceover_timeline_path,
    }


def test_quality_gate_requires_core_sections_and_artifacts(tmp_path: Path) -> None:
    """A short or incomplete payload should fail with actionable issues."""
    script = {
        "title": "",
        "description": "A short description.",
        "script": "word " * 120,
        "sections": {
            "cold_open": "",
            "hook": "",
            "the_number": "",
            "chart_walk": "",
            "context": "",
            "connected_data": "",
            "insight": "",
            "close": "",
        },
        "tags": ["economy"],
        "research_dossier": {"disclosed_synthetic_content": True},
    }

    result = run_quality_gate(
        script,
        _artifact_bundle(
            tmp_path / "vo.mp3",
            tmp_path / "thumb.png",
            tmp_path / "vid.mp4",
            tmp_path / "script.json",
            tmp_path / "audio_quality_report.json",
            tmp_path / "music_provenance.json",
            tmp_path / "storyboard_manifest.json",
            tmp_path / "voiceover_timeline.json",
        ),
        strict=True,
    )

    issue_codes = {entry["code"] for entry in result["issues"]}
    assert "missing_title" in issue_codes
    assert "short_script" in issue_codes
    assert "insufficient_tags" in issue_codes
    assert "missing_disclosure" in issue_codes
    assert result["status"] == "fail"


def _required_quality_payload() -> dict:
    return {
        "title": "A robust script with a clear perspective",
        "description": "A detailed economics episode with timestamps.\n\n00:00 intro",
        "script": ("word " * 560).strip(),
        "sections": {
            "cold_open": "x",
            "hook": "x",
            "the_number": "x",
            "chart_walk": "x",
            "context": "x",
            "connected_data": "x",
            "insight": "x",
            "close": "x",
        },
        "script_with_markers": "[COLD_OPEN] x\n[HOOK] y",
        "tags": ["economy", "finance", "money", "market", "inflation", "rates", "mortgage", "housing", "policy", "fed", "data", "personalfinance", "federalreserve"],
        "research_dossier": {"disclosed_synthetic_content": True, "model": "gpt-5.4"},
    }


def test_quality_gate_reports_synthetic_content_tag_requirement(tmp_path: Path) -> None:
    """Synthetic content must be explicitly disclosed using known markers."""
    script = _required_quality_payload()
    loudness_path, provenance_path = _write_preupload_reports(tmp_path)
    storyboard_path, timeline_path = _write_storyboard_reports(tmp_path)
    result = run_quality_gate(
        script,
        _artifact_bundle(
            __file__,
            __file__,
            __file__,
            __file__,
            loudness_path,
            provenance_path,
            storyboard_path,
            timeline_path,
        ),
        strict=False,
    )
    assert "missing_disclosure" in {item["code"] for item in result["issues"]}

    script["tags"].extend(["#ai", "#disclosure"])
    cleared = run_quality_gate(
        script,
        _artifact_bundle(
            __file__,
            __file__,
            __file__,
            __file__,
            loudness_path,
            provenance_path,
            storyboard_path,
            timeline_path,
        ),
        strict=False,
    )
    assert "missing_disclosure" not in {item["code"] for item in cleared["issues"]}


def test_quality_gate_passes_with_complete_bundle(tmp_path: Path) -> None:
    """A fully populated and compliant payload should pass."""
    script = _required_quality_payload()
    script["tags"].extend(["#ai", "#synthetic"])
    (tmp_path / "voiceover.mp3").write_text("audio")
    (tmp_path / "thumb.png").write_text("image")
    (tmp_path / "video.mp4").write_text("mp4")
    (tmp_path / "script.json").write_text("{}")
    loudness_path, provenance_path = _write_preupload_reports(tmp_path)
    storyboard_path, timeline_path = _write_storyboard_reports(tmp_path)

    result = run_quality_gate(
        script,
        _artifact_bundle(
            tmp_path / "voiceover.mp3",
            tmp_path / "thumb.png",
            tmp_path / "video.mp4",
            tmp_path / "script.json",
            loudness_path,
            provenance_path,
            storyboard_path,
            timeline_path,
        ),
        previous_titles=["Old title", "Completely different concept"],
        strict=True,
    )

    assert result["status"] == "pass"
    assert result["passed"]


def test_quality_gate_report_persistence(tmp_path: Path) -> None:
    """The gate report helper should persist a valid JSON artifact."""
    script = _required_quality_payload()
    (tmp_path / "voiceover.mp3").write_text("audio")
    (tmp_path / "thumb.png").write_text("image")
    (tmp_path / "video.mp4").write_text("mp4")
    (tmp_path / "script.json").write_text("{}")
    loudness_path, provenance_path = _write_preupload_reports(tmp_path)
    storyboard_path, timeline_path = _write_storyboard_reports(tmp_path)
    result = run_quality_gate(
        script,
        _artifact_bundle(
            tmp_path / "voiceover.mp3",
            tmp_path / "thumb.png",
            tmp_path / "video.mp4",
            tmp_path / "script.json",
            loudness_path,
            provenance_path,
            storyboard_path,
            timeline_path,
        ),
    )

    report_path = quality_gate_report_path(result, tmp_path)
    assert report_path.endswith("quality_gate.json")


def test_quality_gate_requires_preupload_reports(tmp_path: Path) -> None:
    """Upload block artifacts should fail if report/provenance are missing."""
    script = _required_quality_payload()
    script["tags"].extend(["#ai", "#synthetic"])
    (tmp_path / "voiceover.mp3").write_text("audio")
    (tmp_path / "thumb.png").write_text("image")
    (tmp_path / "video.mp4").write_text("mp4")
    (tmp_path / "script.json").write_text("{}")
    result = run_quality_gate(
        script,
        _artifact_bundle(
            tmp_path / "voiceover.mp3",
            tmp_path / "thumb.png",
            tmp_path / "video.mp4",
            tmp_path / "script.json",
            tmp_path / "missing_audio_quality_report.json",
            tmp_path / "missing_music_provenance.json",
            tmp_path / "missing_storyboard_manifest.json",
            tmp_path / "missing_voiceover_timeline.json",
        ),
    )
    issue_codes = {entry["code"] for entry in result["issues"]}
    assert "missing_audio_quality_report" in issue_codes
    assert "missing_music_provenance" in issue_codes
    assert "missing_storyboard" in issue_codes
    assert "missing_voiceover_timeline" in issue_codes


def test_quality_gate_min_word_count_override(tmp_path: Path) -> None:
    """Per-run min_word_count should relax short_script without changing default."""
    script = _required_quality_payload()
    script["script"] = ("word " * 400).strip()
    script["tags"].extend(["#ai", "#synthetic"])
    (tmp_path / "voiceover.mp3").write_text("audio")
    (tmp_path / "thumb.png").write_text("image")
    (tmp_path / "video.mp4").write_text("mp4")
    (tmp_path / "script.json").write_text("{}")
    loudness_path, provenance_path = _write_preupload_reports(tmp_path)
    storyboard_path, timeline_path = _write_storyboard_reports(tmp_path)
    bundle = _artifact_bundle(
        tmp_path / "voiceover.mp3",
        tmp_path / "thumb.png",
        tmp_path / "video.mp4",
        tmp_path / "script.json",
        loudness_path,
        provenance_path,
        storyboard_path,
        timeline_path,
    )
    strict_fail = run_quality_gate(script, bundle, strict=True)
    assert "short_script" in {i["code"] for i in strict_fail["issues"]}

    relaxed = run_quality_gate(script, bundle, strict=True, min_word_count=350)
    assert "short_script" not in {i["code"] for i in relaxed["issues"]}
    assert relaxed["checks"]["min_word_count"] == 350
