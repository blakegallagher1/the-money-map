"""Tests for YouTube uploader CLI auth bootstrap behavior."""

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "youtube_api_uploader.py"
SPEC = importlib.util.spec_from_file_location("youtube_api_uploader", MODULE_PATH)
youtube_api_uploader = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(youtube_api_uploader)


def test_main_launches_oauth_when_token_missing(monkeypatch) -> None:
    """Missing token with available client secret should start OAuth flow."""
    calls = {"auth": 0}

    def fake_exists(path: str) -> bool:
        if path == youtube_api_uploader.YOUTUBE_TOKEN_PATH:
            return False
        if path == youtube_api_uploader.YOUTUBE_CLIENT_SECRET_PATH:
            return True
        return False

    def fake_auth() -> None:
        calls["auth"] += 1

    monkeypatch.setattr(youtube_api_uploader.os.path, "exists", fake_exists)
    monkeypatch.setattr(youtube_api_uploader, "_get_authenticated_service", fake_auth)

    exit_code = youtube_api_uploader.main([])
    assert exit_code == 0
    assert calls["auth"] == 1


def test_main_fails_when_client_secret_missing(monkeypatch) -> None:
    """Missing client secret should return setup error code without OAuth."""
    calls = {"auth": 0}

    def fake_exists(path: str) -> bool:
        if path == youtube_api_uploader.YOUTUBE_TOKEN_PATH:
            return False
        if path == youtube_api_uploader.YOUTUBE_CLIENT_SECRET_PATH:
            return False
        return False

    def fake_auth() -> None:
        calls["auth"] += 1

    monkeypatch.setattr(youtube_api_uploader.os.path, "exists", fake_exists)
    monkeypatch.setattr(youtube_api_uploader, "_get_authenticated_service", fake_auth)

    exit_code = youtube_api_uploader.main([])
    assert exit_code == 1
    assert calls["auth"] == 0
