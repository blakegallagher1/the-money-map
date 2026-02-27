# scripts/script_writer.py
# ─────────────────────────────────────────────
# Generates narration scripts from story packages using Gemini
# ─────────────────────────────────────────────

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai
from config.settings import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)


class ScriptWriter:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    # ── Public API ────────────────────────────

    def write_script(self, story_package: dict) -> dict:
        """
        Generate a full narration script from a story package.
        Returns a dict with keys: title, hook, script_text, segments, tags, description.
        """
        item      = story_package["item"]
        related   = story_package.get("related", [])
        category  = story_package.get("category", "Economy")

        # Build the Gemini prompt
        prompt = self._build_prompt(item, related, category)

        response = self.model.generate_content(prompt)
        raw = response.text.strip()

        return self._parse_response(raw, item)

    # ── Internal ──────────────────────────────

    def _build_prompt(self, item: dict, related: list, category: str) -> str:
        related_text = "\n".join(
            f"  - {r['label']}: {r['latest']}{r['unit']} (YoY: {r['yoy_pct']:+.1f}%)"
            for r in related[:4]
        )

        direction = "up" if item.get("yoy_pct", 0) > 0 else "down"
        magnitude = abs(item.get("yoy_pct", 0))

        return f"""You are a financial journalist writing the narration for a short (90-second) YouTube video.

The video is about this economic indicator:
  Indicator:  {item['label']}
  Latest:     {item['latest']}{item['unit']}
  YoY Change: {item['yoy_pct']:+.1f}% ({direction} {magnitude:.1f}%)
  Category:   {category}

Related indicators in the same category:
{related_text if related_text else '  (none available)'}

Write a narration script with EXACTLY this structure:

TITLE: [A punchy, SEO-optimized YouTube title — include the key stat, avoid clickbait]

HOOK: [1–2 sentences, shocking opener that states the key stat immediately]

CONTEXT: [2–3 sentences explaining why this matters to everyday Americans]

RELATED: [1–2 sentences connecting to 1–2 related indicators]

INSIGHT: [2–3 sentences of analysis — what does this mean going forward?]

CLOSE: [1–2 sentences call to action — like & subscribe, comment your thoughts]

TAGS: [10 comma-separated YouTube tags]

DESCRIPTION: [3–4 sentence YouTube video description with key stats]

Rules:
- Write for a general audience, not economists
- Be direct, punchy, and informative
- State exact numbers with units
- Total narration should be 200–280 words
- Do not use emojis in the narration
- Tags should be specific to this story
"""

    def _parse_response(self, raw: str, item: dict) -> dict:
        """
        Parse Gemini's structured response into a dict.
        """
        sections = {"title": "", "hook": "", "context": "", "related": "",
                    "insight": "", "close": "", "tags": [], "description": ""}

        lines = raw.split("\n")
        current_section = None
        buffer = []

        def flush():
            if current_section and buffer:
                text = " ".join(" ".join(buffer).split())
                if current_section == "tags":
                    sections["tags"] = [t.strip() for t in text.split(",")]
                else:
                    sections[current_section] = text

        for line in lines:
            line = line.strip()
            upper = line.upper()
            found = False
            for key in ["TITLE", "HOOK", "CONTEXT", "RELATED", "INSIGHT", "CLOSE", "TAGS", "DESCRIPTION"]:
                if upper.startswith(f"{key}:"):
                    flush()
                    current_section = key.lower()
                    remainder = line[len(key)+1:].strip()
                    buffer = [remainder] if remainder else []
                    found = True
                    break
            if not found and line:
                buffer.append(line)

        flush()

        # Build full script text
        sections["script_text"] = " ".join([
            sections["hook"],
            sections["context"],
            sections["related"],
            sections["insight"],
            sections["close"],
        ])

        # Segment list for video renderer
        sections["segments"] = [
            {"name": "hook",    "text": sections["hook"]},
            {"name": "context", "text": sections["context"]},
            {"name": "related", "text": sections["related"]},
            {"name": "insight", "text": sections["insight"]},
            {"name": "close",   "text": sections["close"]},
        ]

        # Fallback title
        if not sections["title"]:
            sections["title"] = f"{item['label']} Update: {item['yoy_pct']:+.1f}% Year-Over-Year"

        return sections


if __name__ == "__main__":
    import json
    from scripts.data_ingestion import FREDClient
    from scripts.story_discovery import StoryDiscovery

    client = FREDClient()
    data = client.fetch_all()

    discovery = StoryDiscovery(data)
    story = discovery.top_story()

    writer = ScriptWriter()
    script = writer.write_script(story)

    print(f"\nTitle: {script['title']}")
    print(f"\nScript:\n{script['script_text']}")
    print(f"\nTags: {', '.join(script['tags'])}")
