"""Tests for pre-upload quality gating rules."""

from pathlib import Path

from scripts.quality_gate import run_quality_gate, quality_gate_report_path


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
        {
            "voiceover_path": tmp_path / "vo.mp3",
            "thumbnail_path": tmp_path / "thumb.png",
            "final_video_path": tmp_path / "vid.mp4",
            "script_json_path": tmp_path / "script.json",
        },
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
    result = run_quality_gate(
        script,
        {
            "voiceover_path": __file__,
            "thumbnail_path": __file__,
            "final_video_path": __file__,
            "script_json_path": __file__,
        },
        strict=False,
    )
    assert "missing_disclosure" in {item["code"] for item in result["issues"]}

    script["tags"].extend(["#ai", "#disclosure"])
    cleared = run_quality_gate(
        script,
        {
            "voiceover_path": __file__,
            "thumbnail_path": __file__,
            "final_video_path": __file__,
            "script_json_path": __file__,
        },
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

    result = run_quality_gate(
        script,
        {
            "voiceover_path": tmp_path / "voiceover.mp3",
            "thumbnail_path": tmp_path / "thumb.png",
            "final_video_path": tmp_path / "video.mp4",
            "script_json_path": tmp_path / "script.json",
        },
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
    result = run_quality_gate(
        script,
        {
            "voiceover_path": tmp_path / "voiceover.mp3",
            "thumbnail_path": tmp_path / "thumb.png",
            "final_video_path": tmp_path / "video.mp4",
            "script_json_path": tmp_path / "script.json",
        },
    )

    report_path = quality_gate_report_path(result, tmp_path)
    assert report_path.endswith("quality_gate.json")

