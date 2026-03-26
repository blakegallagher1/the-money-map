"""
LLM-Powered Script Writer for The Money Map
Replaces template-based scripting with GPT-5.4 for unique,
engaging, longer scripts (~700 words / 4-5 minutes) for all 34 indicators.

Falls back to enhanced_script_writer.py if API call fails.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import OPENAI_API_KEY, SCRIPT_LLM_MODEL, TARGET_WORD_COUNT

# Few-shot example loaded from existing episode
EXAMPLE_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'ep1_v2', 'script.json'
)

SYSTEM_PROMPT = """You are the script writer for "The Money Map" — a weekly YouTube channel that
turns Federal Reserve economic data into cinematic, data-driven video essays.

VOICE & TONE:
- Confident data journalist. Bloomberg TV anchor meets accessible YouTuber.
- Urgent but measured — convey that this data matters without being alarmist.
- Use conversational pauses (ellipses "...") for dramatic effect.
- Pronounce numbers with weight. Pause before and after the biggest stat.
- Genuine surprise at dramatic numbers. Empathy for consumer impact.

NARRATIVE STRUCTURE (8 sections, use these exact markers):

[COLD_OPEN] — 1-2 sentences. Drop the single most dramatic stat. No context. Just the number. (~5 seconds)

[HOOK] — Set the stakes. Why should the viewer care? Personal relevance. "In this episode..." (~15 seconds, ~40 words)

[THE_NUMBER] — Deep dive into the primary metric. Current value, previous year, percentage change, historical context. (~25 seconds, ~65 words)

[CHART_WALK] — Narrate what the viewer sees on the animated chart. Point out trends, inflection points, acceleration. (~30 seconds, ~75 words)

[CONTEXT] — Introduce 2-3 related metrics. Each with current value and YoY change. Explain WHY they matter together. (~35 seconds, ~90 words)

[CONNECTED_DATA] — Meta-analysis. How these metrics reinforce each other. The bigger picture. (~25 seconds, ~65 words)

[INSIGHT] — The "so what" — concrete implications for real Americans. Use specific dollar amounts, relatable scenarios. Historical parallels. (~40 seconds, ~100 words)

[CLOSE] — Subscribe CTA with a forward-looking hook about what to watch next. (~15 seconds, ~40 words)

TOTAL TARGET: {target_words} words (±50 words). This produces a 4-5 minute video.

RULES:
- NEVER use emoji in the script text
- Use "percent" not "%" in spoken script
- Use ellipses "..." for dramatic pauses
- Use specific numbers — never round or approximate
- Reference the actual data values provided
- Each section marker must appear on its own line: [SECTION_NAME]
- Write for spoken delivery — short sentences, natural rhythm
- The channel name is "The Money Map" — use it in the close

You must also generate:
1. A compelling YouTube title (under 70 characters, curiosity-driven)
2. A YouTube description with timestamps and hashtags
3. YouTube tags (15-20 relevant tags)
4. Three b-roll prompts for AI video generation:
   - hook: 4-second cinematic scene matching the hook mood
   - context: 4-second scene illustrating the causal factors
   - insight: 4-second scene showing human impact
   Each prompt should be a detailed, photorealistic scene description for AI video generation.

RESPOND WITH VALID JSON ONLY. No markdown, no code fences. Use this exact structure:
{output_schema}
"""

OUTPUT_SCHEMA = """{
  "title": "string — YouTube title, under 70 chars",
  "description": "string — YouTube description with timestamps and hashtags",
  "tags": ["string array — 15-20 YouTube tags"],
  "script_with_markers": "string — full script with [SECTION] markers",
  "script": "string — clean script without section markers",
  "sections": {
    "cold_open": "string",
    "hook": "string",
    "the_number": "string",
    "chart_walk": "string",
    "context": "string",
    "connected_data": "string",
    "insight": "string",
    "close": "string"
  },
  "broll_prompts": {
    "hook": "string — detailed AI video generation prompt",
    "context": "string — detailed AI video generation prompt",
    "insight": "string — detailed AI video generation prompt"
  },
  "word_count": "integer",
  "estimated_duration_sec": "integer"
}"""


def _load_example_script():
    """Load an existing episode script as a few-shot example."""
    try:
        with open(EXAMPLE_SCRIPT_PATH) as f:
            example = json.load(f)
        return json.dumps(example, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _build_data_context(story_pkg):
    """Format the raw data into a clear context block for the LLM."""
    primary = story_pkg['primary']
    related = story_pkg.get('related', [])

    lines = [
        "PRIMARY METRIC:",
        f"  Name: {primary['name']}",
        f"  Key: {primary['key']}",
        f"  Current Value: {primary['latest_value']} {primary['unit']}",
        f"  Previous Year Value: {primary['prev_year_value']} {primary['unit']}",
        f"  YoY Change: {primary.get('yoy_change', 'N/A')}",
        f"  YoY Percent Change: {primary['yoy_pct']:.2f}%",
        f"  Latest Date: {primary['latest_date']}",
        f"  Score: {primary.get('score', 'N/A')}",
        f"  Tags: {', '.join(primary.get('tags', []))}",
        "",
        "RELATED METRICS:"
    ]

    for i, r in enumerate(related[:3], 1):
        lines.extend([
            f"  {i}. {r['name']}",
            f"     Current Value: {r['latest_value']} {r.get('unit', '')}",
            f"     YoY Change: {r.get('yoy_pct', 'N/A')}%",
            f"     Latest Date: {r.get('latest_date', 'N/A')}",
        ])

    return "\n".join(lines)


def generate_llm_script(story_pkg):
    """Generate a script using the configured GPT-5 model with structured output."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    data_context = _build_data_context(story_pkg)
    example_script = _load_example_script()

    system = SYSTEM_PROMPT.format(
        target_words=TARGET_WORD_COUNT,
        output_schema=OUTPUT_SCHEMA
    )

    user_message = f"Write a Money Map episode script for this economic data:\n\n{data_context}"

    if example_script:
        user_message += (
            f"\n\nHere is an example of a completed episode script for reference "
            f"(match this style and JSON structure):\n{example_script}"
        )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model=SCRIPT_LLM_MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    script_data = json.loads(raw)

    # Validate required fields
    required_keys = ['title', 'script', 'sections', 'broll_prompts']
    for key in required_keys:
        if key not in script_data:
            raise ValueError(f"LLM response missing required key: {key}")

    required_sections = ['cold_open', 'hook', 'the_number', 'chart_walk',
                         'context', 'connected_data', 'insight', 'close']
    for sec in required_sections:
        if sec not in script_data.get('sections', {}):
            raise ValueError(f"LLM response missing section: {sec}")

    for broll_key in ['hook', 'context', 'insight']:
        if broll_key not in script_data.get('broll_prompts', {}):
            raise ValueError(f"LLM response missing broll_prompt: {broll_key}")

    # Compute word count and duration if not provided
    clean_script = script_data['script']
    word_count = len(clean_script.split())
    script_data['word_count'] = word_count
    script_data['estimated_duration_sec'] = int(word_count / 2.5)

    # Add primary metric metadata (matches enhanced_script_writer output format)
    primary = story_pkg['primary']
    script_data['primary_metric'] = {
        "key": primary['key'],
        "name": primary['name'],
        "series_id": primary['series_id'],
        "unit": primary['unit'],
        "latest_value": primary['latest_value'],
        "latest_date": primary['latest_date'],
        "yoy_change": primary.get('yoy_change'),
        "yoy_pct": primary['yoy_pct'],
        "prev_year_value": primary['prev_year_value'],
        "score": primary.get('score'),
        "tags": primary.get('tags', []),
    }

    # Generate script_with_markers if not provided
    if 'script_with_markers' not in script_data:
        sections = script_data['sections']
        script_data['script_with_markers'] = "\n\n".join(
            f"[{sec.upper()}]\n{sections[sec]}"
            for sec in required_sections
        )

    # Generate description if not provided
    if 'description' not in script_data:
        yoy = primary['yoy_pct']
        direction = "dropped" if yoy < 0 else "risen"
        script_data['description'] = (
            f"📊 {primary['name']} just {direction} {abs(yoy):.1f}% year-over-year.\n\n"
            f"In this episode of The Money Map, we break down what's really happening.\n\n"
            f"All data sourced from FRED (Federal Reserve Economic Data).\n\n"
            f"🔔 Subscribe for weekly data-driven economic analysis.\n\n"
            f"#economy #data #finance #themoneymap #economics #personalfinance"
        )

    # Generate tags if not provided
    if 'tags' not in script_data:
        script_data['tags'] = [
            "economy", "economics", "data", "finance", "money",
            primary['name'].lower().replace(" ", ""),
            "federal reserve", "FRED data", "personal finance",
            "economic analysis", "the money map", "data visualization",
            "economic data", "recession", "inflation", "interest rates"
        ]

    return script_data


def generate_script(story_pkg):
    """Main entry point — tries LLM, falls back to template writer."""
    try:
        print(f"  Using LLM script writer ({SCRIPT_LLM_MODEL})...")
        result = generate_llm_script(story_pkg)
        print(f"  LLM script generated: {result['word_count']} words, "
              f"~{result['estimated_duration_sec']}s")
        return result
    except Exception as e:
        print(f"  LLM script writer failed: {e}")
        print("  Falling back to template script writer...")
        from scripts.enhanced_script_writer import generate_enhanced_script
        return generate_enhanced_script(story_pkg)


if __name__ == "__main__":
    from scripts.story_discovery import build_story_package
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data', 'latest_data.json'
    )
    pkg = build_story_package(data_path)
    result = generate_script(pkg)
    print(f"\nTitle: {result['title']}")
    print(f"Words: {result['word_count']}")
    print(f"Duration: ~{result['estimated_duration_sec']}s")
    print(f"\nSections:")
    for k, v in result['sections'].items():
        wc = len(v.split())
        print(f"  {k}: {wc} words")
    print(f"\nB-roll prompts:")
    for k, v in result['broll_prompts'].items():
        print(f"  {k}: {v[:80]}...")
