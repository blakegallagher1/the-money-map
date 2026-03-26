"""Tests for topic research dossier generation and persistence."""

from pathlib import Path

from scripts import topic_research


def test_extract_json_supports_code_fence_wrapping() -> None:
    """The parser should handle JSON embedded in Markdown fences."""
    response_text = """
```json
{\n  \"summary\": \"A test topic\"\n}
```"""
    payload = topic_research._extract_json(response_text)
    assert payload == {"summary": "A test topic"}


def test_generate_research_dossier_falls_back_when_model_output_invalid(monkeypatch, tmp_path: Path) -> None:
    """Invalid model output should not crash generation; fallback dossier must be returned."""
    story_pkg = {
        "primary": {
            "name": "Home Price Index",
            "key": "home_price",
            "yoy_pct": 2.3,
            "latest_value": 123,
            "unit": "index",
        },
        "related": [],
    }

    class BadClient:
        class responses:  # noqa: N801
            @staticmethod
            def create(*_, **__):
                class Resp:
                    output_text = "not-json"

                return Resp()

    class ClientFactory:
        def __new__(cls):
            return BadClient()

    monkeypatch.setattr(topic_research, "OpenAI", ClientFactory)
    dossier = topic_research.generate_research_dossier(story_pkg, model="test-model", max_tokens=100)

    assert dossier["summary"].startswith("The selected signal is Home Price Index")
    assert dossier["model"] == "fallback"
    assert "source_list" in dossier


def test_generate_research_dossier_and_save_dossier(tmp_path: Path) -> None:
    """The dossier artifact writer should persist markdown and JSON payloads."""
    story = {
        "primary": {
            "name": "Inflation",
            "yoy_pct": 4.0,
            "key": "cpi",
            "latest_value": 321,
            "unit": "index",
        },
        "related": [],
    }

    class GoodClient:
        class responses:  # noqa: N801
            @staticmethod
            def create(*_, **__):
                class Resp:
                    output_text = (
                        '{"summary":"Balanced macro cycle",'
                        '"angle":"Unexpected demand resilience",'
                        '"watch_outs":["none"],'
                        '"source_list":["FRED", "BLS"],'
                        '"novelty":"Use a new angle",'
                        '"disclosed_synthetic_content":false,'
                        '"title_variants":["A","B","C"],'
                        '"hook_directions":["Hook1","Hook2","Hook3"],'
                        '"confidence":0.91}'
                    )

                return Resp()

    class ClientFactory:
        def __new__(cls):
            return GoodClient()

    topic_research.OpenAI = ClientFactory
    dossier = topic_research.generate_research_dossier(story, model="test-model", max_tokens=100)
    json_path, md_path = topic_research.save_dossier("cpi", dossier, base_dir=tmp_path)

    assert Path(json_path).exists()
    assert Path(md_path).exists()
    assert dossier["model"] == "test-model"
    assert dossier["confidence"] == 0.91
