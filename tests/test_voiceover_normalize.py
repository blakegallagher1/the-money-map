"""Tests for TTS-oriented voiceover text normalization."""

from scripts.voiceover_normalize import normalize_for_tts


def test_gas_price_per_gallon_rounds_to_cents() -> None:
    out = normalize_for_tts("The average was $3.961 per gallon.")
    assert "three dollars and ninety-six cents per gallon" in out
    assert "$" not in out


def test_spelled_dollars_no_dollar_sign() -> None:
    """LLM scripts often write '3.961 dollars' instead of '$3.961'."""
    out = normalize_for_tts("Regular gas is 3.961 dollars per gallon nationally.")
    assert "three dollars and ninety-six cents per gallon" in out.lower()
    assert "3.961" not in out


def test_spelled_subdollar_tenths() -> None:
    """0.8 dollars -> eighty cents (tenths of a dollar)."""
    out = normalize_for_tts("That's an increase of 0.8 dollars per gallon.")
    assert "eighty cents per gallon" in out


def test_spelled_integer_dollars() -> None:
    out = normalize_for_tts("Gas is back near 4 dollars.")
    assert "four dollars" in out


def test_percent_word_not_symbol() -> None:
    out = normalize_for_tts("Up 25.35 percent in one year.")
    assert "twenty-five point thirty-five percent" in out
    assert "25.35" not in out


def test_subdollar_is_cents_not_zero_point_dollars() -> None:
    out = normalize_for_tts("An increase of $0.08 per gallon.")
    assert "eight cents per gallon" in out
    assert "$" not in out


def test_slash_date_us_style() -> None:
    out = normalize_for_tts("As of 3-23, prices rose.")
    assert "March" in out
    assert "twenty-third" in out


def test_iso_date() -> None:
    out = normalize_for_tts("Released 2026-03-27.")
    assert "March" in out and "twenty-seventh" in out


def test_trillion_macro() -> None:
    out = normalize_for_tts("Debt hit $2.2 trillion.")
    assert "two point two trillion dollars" in out


def test_percent() -> None:
    out = normalize_for_tts("Inflation at 6.1%.")
    assert "six point one percent" in out


def test_comma_thousands() -> None:
    out = normalize_for_tts("Revenue was $1,234.50.")
    assert "thirty-four dollars and fifty cents" in out
    assert "$" not in out


def test_whole_dollars_no_cents() -> None:
    out = normalize_for_tts("Fee is $5.00 flat.")
    assert "five dollars" in out
    assert "$" not in out


def test_empty_passthrough() -> None:
    assert normalize_for_tts("") == ""
