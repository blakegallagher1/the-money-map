"""Tests for quality-tier profile resolution."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.py"
SPEC = importlib.util.spec_from_file_location("settings", MODULE_PATH)
settings = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(settings)


def test_get_quality_profile_returns_expected_1440_defaults() -> None:
    """1440 tier should resolve to 2560x1440 at 30fps."""
    profile = settings.get_quality_profile("1440")
    assert profile["width"] == 2560
    assert profile["height"] == 1440
    assert profile["fps"] == 30


def test_get_quality_profile_rejects_unknown_tier() -> None:
    """Unknown quality tier should raise a clear error."""
    try:
        settings.get_quality_profile("9999")
    except ValueError as exc:
        assert "Unknown quality tier" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported quality tier")
