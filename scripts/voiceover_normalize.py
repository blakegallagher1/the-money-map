"""
Normalize economics / data scripts for natural TTS delivery.

Applied to plain-text voiceover before synthesis so ElevenLabs/OpenAI read
prices, small deltas, and dates the way a human anchor would—not as digit
strings or "zero point eight dollars".

See normalize_for_tts() for the rule set.
"""

from __future__ import annotations

import re
from typing import Callable

from num2words import num2words

_MONTHS = (
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def _expand_year(y: int) -> str:
    if y < 100:
        y += 2000 if y < 70 else 1900
    return num2words(y)


def _replace_slash_dates(text: str) -> str:
    """3/23, 03/23/2026, 12-5-24 -> March twenty-third (comma year optional)."""

    def repl(m: re.Match[str]) -> str:
        a, b, c = m.group(1), m.group(2), m.group(3)
        if c is not None:
            month_s, day_s, year_s = a, b, c
        else:
            month_s, day_s = a, b
            year_s = None
        try:
            month = int(month_s)
            day = int(day_s)
        except ValueError:
            return m.group(0)
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return m.group(0)
        spoken = f"{_MONTHS[month]} {num2words(day, to='ordinal')}"
        if year_s is not None:
            try:
                y = int(year_s)
            except ValueError:
                return m.group(0)
            spoken = f"{spoken}, {_expand_year(y)}"
        return spoken

    # MM/DD or MM-DD with optional /YYYY or /YY (also 4-digit year)
    pattern = r"(?<![\d.])(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?(?![\d])"
    return re.sub(pattern, repl, text)


def _dollars_and_cents(whole: int, cents: int, *, force_cents_only: bool = False) -> str:
    if force_cents_only or (whole == 0 and cents > 0):
        if cents == 1:
            return "one cent"
        return f"{num2words(cents)} cents"
    if cents == 0:
        if whole == 1:
            return "one dollar"
        return f"{num2words(whole)} dollars"
    cword = "one cent" if cents == 1 else f"{num2words(cents)} cents"
    if whole == 0:
        return cword
    dword = "one dollar" if whole == 1 else f"{num2words(whole)} dollars"
    return f"{dword} and {cword}"


def _spell_money_value(whole: int, frac_digits: str | None) -> str | None:
    """
    Convert integer + fractional string (after '.') to spoken dollars/cents.
    Gas-style three decimal places: round fractional part to whole cents.
    """
    if frac_digits is None or frac_digits == "":
        return _dollars_and_cents(whole, 0)

    if len(frac_digits) >= 3:
        val = float(f"{whole}.{frac_digits}")
        c = int(round((val - whole) * 100))
        if c >= 100:
            whole += c // 100
            c = c % 100
        return _dollars_and_cents(whole, c)

    if len(frac_digits) == 1:
        # One decimal place = tenths of a dollar ($37.6 -> sixty cents)
        tenths = int(frac_digits)
        return _dollars_and_cents(whole, tenths * 10)

    # Two fractional digits = cents ($1.23, $0.08)
    cents = int(frac_digits)
    if whole == 0 and cents < 100:
        return _dollars_and_cents(0, cents, force_cents_only=True)
    return _dollars_and_cents(whole, cents)


def _spell_numeric_for_percent(body: str) -> str:
    """25.35 -> twenty-five point thirty-five (for 'percent' phrases)."""
    if "." in body:
        ip, fp = body.split(".", 1)
        if not ip.isdigit() or not fp.isdigit():
            return body
        tail = num2words(int(fp))
        return f"{num2words(int(ip))} point {tail}"
    if body.isdigit():
        return num2words(int(body))
    return body


def _replace_spelled_dollar_amounts(text: str) -> str:
    """
    Scripts often omit '$' and write '3.961 dollars per gallon' or '0.8 dollars'.
    Those never hit the $-currency rule; expand them here.
    Order: three-decimal, two-decimal, sub-dollar 0.xx, then integer dollars.
    """

    def repl_three(m: re.Match[str]) -> str:
        whole = int(m.group(1).replace(",", ""))
        frac = m.group(2)
        tail = m.group(3) or ""
        spoken = _spell_money_value(whole, frac)
        if not spoken:
            return m.group(0)
        return f"{spoken}{tail}"

    text = re.sub(
        r"\b(\d{1,3}(?:,\d{3})*)\.(\d{3})\s+dollars(\s+per\s+gallon)?\b",
        repl_three,
        text,
        flags=re.IGNORECASE,
    )

    def repl_two(m: re.Match[str]) -> str:
        whole = int(m.group(1).replace(",", ""))
        frac = m.group(2)
        tail = m.group(3) or ""
        spoken = _spell_money_value(whole, frac)
        if not spoken:
            return m.group(0)
        return f"{spoken}{tail}"

    text = re.sub(
        r"\b(\d{1,3}(?:,\d{3})*)\.(\d{2})\s+dollars(\s+per\s+gallon)?\b",
        repl_two,
        text,
        flags=re.IGNORECASE,
    )

    def repl_zero(m: re.Match[str]) -> str:
        digits = m.group(1)
        tail = m.group(2) or ""
        if len(digits) == 1:
            cents = int(digits) * 10
        else:
            cents = int(digits)
        if cents <= 0 or cents >= 100:
            return m.group(0)
        spoken = _dollars_and_cents(0, cents, force_cents_only=True)
        return f"{spoken}{tail}"

    text = re.sub(
        r"\b0\.(\d{1,2})\s+dollars(\s+per\s+gallon)?\b",
        repl_zero,
        text,
        flags=re.IGNORECASE,
    )

    def repl_int(m: re.Match[str]) -> str:
        whole = int(m.group(1).replace(",", ""))
        tail = m.group(2) or ""
        spoken = _dollars_and_cents(whole, 0)
        return f"{spoken}{tail}"

    text = re.sub(
        r"\b(\d{1,3}(?:,\d{3})*)\s+dollars(\s+per\s+gallon)?\b",
        repl_int,
        text,
        flags=re.IGNORECASE,
    )
    return text


def _replace_percent_words(text: str) -> str:
    """25.35 percent -> twenty-five point thirty-five percent (word 'percent', not %)."""

    def repl(m: re.Match[str]) -> str:
        body = m.group(1)
        if not re.match(r"^\d+(?:\.\d{1,3})?$", body):
            return m.group(0)
        return f"{_spell_numeric_for_percent(body)} percent"

    return re.sub(
        r"\b(\d+(?:\.\d{1,3})?)\s+percent\b",
        repl,
        text,
        flags=re.IGNORECASE,
    )


def _replace_currency_amounts(text: str) -> str:
    """
    $3.961, $0.08, $37.6 trillion, $1,234.56
    """

    def repl(m: re.Match[str]) -> str:
        raw_whole = m.group(1).replace(",", "")
        frac = m.group(2)  # includes dot or None
        scale = m.group(3)
        per_gallon = "per gallon" in m.group(0).lower()
        try:
            whole = int(raw_whole)
        except ValueError:
            return m.group(0)

        frac_digits = frac[1:] if frac else None

        if scale:
            # Macro amounts: $37.6 trillion -> "thirty-seven point six trillion dollars"
            if frac_digits:
                dec_part = frac_digits.rstrip("0") or ""
                if dec_part == "":
                    amount = num2words(whole)
                else:
                    whole_w = num2words(whole)
                    tail = num2words(int(dec_part))
                    amount = f"{whole_w} point {tail}"
            else:
                amount = num2words(whole)
            out = f"{amount} {scale} dollars"
            if per_gallon:
                out = f"{out} per gallon"
            return out

        spoken = _spell_money_value(whole, frac_digits)
        if spoken is None:
            return m.group(0)
        if per_gallon:
            return f"{spoken} per gallon"
        return spoken

    # Optional scale or per gallon (case-insensitive)
    pattern = (
        r"\$(\d{1,3}(?:,\d{3})*|\d+)"
        r"(\.\d{1,4})?"
        r"(?:\s+(trillion|billion|million|thousand))?"
        r"(?:\s*(?:/\s*)?per\s+gallon)?"
    )
    return re.sub(pattern, repl, text, flags=re.IGNORECASE)


def _replace_iso_dates(text: str) -> str:
    """2026-03-27 -> March twenty-seventh, twenty twenty-six"""

    def repl(m: re.Match[str]) -> str:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (1 <= mo <= 12 and 1 <= d <= 31):
            return m.group(0)
        return f"{_MONTHS[mo]} {num2words(d, to='ordinal')}, {_expand_year(y)}"

    return re.sub(r"\b(20\d{2})-(\d{2})-(\d{2})\b", repl, text)


def _replace_percent_spoken(text: str) -> str:
    """
    Optional: 6.1% -> six point one percent (reduces 'digit by digit' reads).
    Skip if already contains 'percent' nearby (heuristic: simple % only).
    """

    def repl(m: re.Match[str]) -> str:
        body = m.group(1)
        if "." in body:
            ip, fp = body.split(".", 1)
            if not ip.isdigit() or not fp.isdigit():
                return m.group(0)
            tail = num2words(int(fp))
            return f"{num2words(int(ip))} point {tail} percent"
        if not body.isdigit():
            return m.group(0)
        return f"{num2words(int(body))} percent"

    return re.sub(r"(?<!\d)(\d+(?:\.\d+)?)%", repl, text)


def normalize_for_tts(text: str) -> str:
    """
    Apply all normalization rules. Order is chosen to avoid cross-pattern clashes.

    Rules:
    - Slash / dash calendar dates -> month + ordinal day (+ year)
    - ISO dates YYYY-MM-DD
    - Plain-text money: ``3.961 dollars``, ``0.8 dollars per gallon``, ``4 dollars``
    - Currency: $ with optional trillion/billion/million/thousand or per gallon
    - Sub-dollar amounts ($0.08) -> N cents (via currency rule)
    - ``12.5 percent`` (word) and ``6.1%`` -> spoken
    """
    if not text or not text.strip():
        return text

    steps: list[Callable[[str], str]] = [
        _replace_iso_dates,
        _replace_slash_dates,
        _replace_spelled_dollar_amounts,
        _replace_currency_amounts,
        _replace_percent_words,
        _replace_percent_spoken,
    ]
    out = text
    for fn in steps:
        out = fn(out)
    return out
