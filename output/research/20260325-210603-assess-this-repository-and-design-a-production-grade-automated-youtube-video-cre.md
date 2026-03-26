# OpenAI Deep Research Report

        - Generated: 2026-03-25T21:06:03-05:00
        - Goal: Assess this repository and design a production-grade automated YouTube video creation machine with minimal human involvement
        - Prompt model: `gpt-5.4`
        - Research model: `o3-deep-research-2025-06-26`
        - Web tool: `web_search`

        ## Expanded Prompt

        ```text
        The current date is March 25, 2026.

        User goal:
        Assess this repository and design a production-grade automated YouTube video creation machine with minimal human involvement

        Repository:
        - Name: The Money Map
        - Path: /Users/gallagherpropertycompany/Desktop/the-money-map
        - Current positioning: automated macro-data YouTube video pipeline with script, voiceover,
          rendering, thumbnail, and YouTube upload steps.

        Research task:
        1. Assess what is already automated in this repository.
        2. Identify the missing systems required for a genuinely autonomous YouTube channel:
           topic selection, trend/context research, script quality control, asset generation,
           edit QA, upload metadata, scheduling, analytics feedback loops, and cost/reliability guardrails.
        3. Recommend the highest-leverage OpenAI-powered upgrades that fit this codebase right now.
        4. Separate recommendations into:
           - immediate repo-local changes
           - next-step operational automation
           - optional future improvements
        5. Call out where the repo is using older model choices or legacy API patterns.
        6. Return a citation-backed report with concrete implementation guidance, not generic advice.

        Output requirements for the final research report:
        - Start with an executive summary.
        - Include a "Current State" section.
        - Include a "Gaps To Full Automation" section.
        - Include a "Recommended Architecture" section with components and data flow.
        - Include a "Top 5 Repo Changes" section with file-level suggestions where possible.
        - Include a "90-Day Automation Roadmap" section.
        - Include a "Risks and Guardrails" section.
        - Cite all external claims inline.

        Repo context:
        FILE: README.md
                ```text
                # The Money Map 📊

Fully automated YouTube channel that turns Federal Reserve economic data into cinematic, data-driven video content.

## Architecture

```
FRED API → Data Ingestion → Story Discovery → Script Writer → Voiceover (TTS)
                                                    ↓
                              Enhanced Renderer → AI B-Roll → Final Assembly → YouTube
```

## Pipeline Modules

| Module | File | Description |
|--------|------|-------------|
| Data Ingestion | `scripts/data_ingestion.py` | Pulls 34 FRED economic indicators with YoY calculations |
| Story Discovery | `scripts/story_discovery.py` | Scores each metric for viral potential, picks top story |
| Script Writer V1 | `scripts/script_writer.py` | ~250 word scripts (~1:30 videos) |
| Script Writer V2 | `scripts/enhanced_script_writer.py` | ~400-420 word scripts with section markers & b-roll cues |
| Renderer V1 | `scripts/render_pilot.py` | Basic 5fps matplotlib → 30fps video |
| Renderer V2 | `scripts/enhanced_renderer.py` | Cinematic renderer with glowing effects, animated counters, Ken Burns zoom, particle effects |
| Thumbnail V1 | `scripts/thumbnail_gen.py` | Basic stat-focused thumbnails |
| Thumbnail V2 | `scripts/enhanced_thumbnail.py` | High-CTR thumbnails with bold headlines, curiosity gap design |
| Final Assembly | `scripts/final_assembly.py` | Interleaves data-viz with AI b-roll, layers voiceover |
| Custom Narrated Episodes | `scripts/custom_episode_builder.py` | Builds branded section-based narration videos from a JSON episode spec |
| YouTube Upload | `scripts/youtube_uploader.py` | Browser-based upload automation |
| Orchestrator | `scripts/orchestrator.py` | Full pipeline orchestrator |

## Episodes (V2 Enhanced)

| # | Title | Key Metric | Duration |
|---|-------|-----------|----------|
| 1 | Americans Are Going Broke — The Savings Crisis Nobody Talks About | 3.6% savings rate, ▼30.8% YoY | ~2:44 |
| 2 | Mortgage Rates Just Hit 6% — What This Really Means For Home Buyers | 5.98% rate, ▼11.5% YoY | ~2:48 |
| 3 | The U.S. Just Added $2.2 Trillion In Debt — Here's Where It's Going | $37.6T debt, ▲6.1% YoY | ~2:58 |
| 4 | Gas Is Under $3 A Gallon — But That Might Be Bad News | $2.94/gal, ▼6.3% YoY | ~2:50 |
| 5 | GDP Growth Just Collapsed 26% — Is A Recession Coming? | 1.4% growth, ▼26.3% YoY | ~2:42 |

## Tech Stack

- **Data**: FRED API (Federal Reserve Economic Data) — 34 curated series
- **Visualization**: matplotlib (1920x1080, 10fps render → 30fps output)
- **Voiceover**: AI TTS (Gemini, "charon" voice — calm professional male)
- **B-Roll**: AI-generated cinematic video clips (15 clips across 5 episodes)
- **Assembly**: ffmpeg (concatenation, voiceover mixing)
- **Thumbnails**: matplotlib (1280x720, high-CTR design)
- **Scheduling**: Cron (Monday 8AM CST weekly)

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#0A0A0F` | Dark cinematic base |
| Accent Teal | `#00D4AA` | Positive trends, brand |
| Accent Coral | `#FF6B6B` | Emphasis, subtitles |
| Positive | `#22C55E` | Up trends |
| Negative | `#EF4444` | Down trends |

## Setup

```bash
pip install -r requirements.txt
export FRED_API_KEY="your_key_here"
```

## Run

```bash
# Full pipeline for one episode
python scripts/orchestrator.py

# Build a narrated non-FRED episode from a JSON spec
python scripts/custom_episode_builder.py --episode data/cre_balance_sheet_fortress/episode.json

# Just render enhanced episode N
python scripts/enhanced_renderer.py N

# Just generate thumbnail for episode N
python scripts/enhanced_thumbnail.py N

# Full assembly with b-roll interleaving
python scripts/final_assembly.py N
```

Custom narrated episodes write their combined script to `data/<slug>/voiceover_script.txt`,
their final voiceover MP3 to `data/<slug>/voiceover.mp3`, and their final video to
`output/<slug>.mp4`.

## License

MIT

                ```

FILE: config/settings.py
                ```text
                """
The Money Map — Configuration
All API keys and channel settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
FRED_API_KEY = os.environ.get("FRED_API_KEY", "50f1b7098d9ae0eb17d5ec516b6df15e")
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")  # Pending email activation
BLS_API_KEY = os.environ.get("BLS_API_KEY", "")  # Pending email activation
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LUMA_API_KEY = os.environ.get("LUMA_API_KEY", "")

# --- LLM Script Writer ---
SCRIPT_LLM_MODEL = "gpt-5.4"
TARGET_WORD_COUNT = 700  # Target ~4-5 minute videos
SCRIPT_RESPONSE_FORMAT = {
    "type": "json_object"
}

# --- Research & Planning ---
RESEARCH_PROMPT_MODEL = "gpt-5.4"
DEEP_RESEARCH_MODEL = "o3-deep-research"
DEEP_RESEARCH_MAX_TOOL_CALLS = 24
RESEARCH_DOSSIER_MAX_WORDS = 700

# --- B-Roll Settings (Luma Dream Machine) ---
BROLL_ENABLED = True
BROLL_DURATION = 4  # Seconds per b-roll clip

# --- Background Music ---
MUSIC_ENABLED = True

# --- YouTube API (OAuth 2.0) ---
YOUTUBE_CLIENT_SECRET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'client_secret.json'
)
YOUTUBE_TOKEN_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'token.json'
)
YOUTUBE_CATEGORY_ID = "27"  # Education
AUTO_UPLOAD = os.environ.get("AUTO_UPLOAD", "false").lower() == "true"
YOUTUBE_DEFAULT_PRIVACY = os.environ.get("YOUTUBE_DEFAULT_PRIVACY", "private")
YOUTUBE_PUBLISH_OFFSET_DAYS = int(os.environ.get("YOUTUBE_PUBLISH_OFFSET_DAYS", "0"))
YOUTUBE_PROCESSING_TIMEOUT_SECONDS = int(os.environ.get("YOUTUBE_PROCESSING_TIMEOUT_SECONDS", "900"))
YOUTUBE_PROCESSING_POLL_SECONDS = int(os.environ.get("YOUTUBE_PROCESSING_POLL_SECONDS", "12"))

# --- TTS Settings (OpenAI gpt-4o-mini-tts) ---
TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "ash"  # Deep, authoritative — closest match to prior "charon" voice
TTS_INSTRUCTIONS = (
    "Voice Affect: Confident, authoritative data journalist. "
    "Think Bloomberg TV anchor meets accessible YouTuber.\n"
    "Tone: Urgent but measured — convey that this data matters "
    "without being alarmist.\n"
    "Pacing: Moderate pace with deliberate pauses after key statistics. "
    "Speed up slightly during context and background, slow down for the main reveal.\n"
    "Emotion: Genuine surprise at dramatic numbers. Empathy when discussing "
    "consumer impact. Excitement during the hook.\n"
    "Emphasis: Hit numbers hard — pronounce dollar amounts and percentages "
    "with weight. Pause briefly before and after the biggest stat."
)

# --- YouTube Channel ---
YOUTUBE_CHANNEL_NAME = "The Money Map"
YOUTUBE_CHANNEL_ID = ""  # Will be populated after OAuth setup

# --- Content Settings ---
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30
VIDEO_DURATION_TARGET = 270  # Target ~4.5 minutes per video
FONT_FAMILY = "DejaVu Sans"

# --- Color Palette (Dark, Cinematic, Data-Viz Optimized) ---
COLORS = {
    "bg_dark": "#0A0A0F",
    "bg_card": "#12121A",
    "bg_gradient_start": "#0A0A0F",
    "bg_gradient_end": "#1A1A2E",
    "text_primary": "#FFFFFF",
    "text_secondary": "#8B8BA3",
    "text_muted": "#5A5A72",
    "accent_teal": "#00D4AA",
    "accent_blue": "#4A9EFF",
    "accent_coral": "#FF6B6B",
    "accent_amber": "#FFB84D",
    "accent_purple": "#A855F7",
    "accent_green": "#22C55E",
    "grid": "#1E1E2E",
    "border": "#2A2A3E",
    "positive": "#22C55E",
    "negative": "#EF4444",
}

# --- FRED Series Library (curated for viral potential) ---
FRED_SERIES = {
    # Housing & Real Estate
    "median_home_price": {"id": "MSPUS", "name": "Median Home Price", "unit": "$"},
    "mortgage_rate_30yr": {"id": "MORTGAGE30US", "name": "30-Year Mortgage Rate", "unit": "%"},
    "housing_starts": {"id": "HOUST", "name": "Housing Starts", "unit": "thousands"},
    "home_ownership_rate": {"id": "RHORUSQ156N", "name": "Home Ownership Rate", "unit": "%"},
    "case_shiller": {"id": "CSUSHPINSA", "name": "Case-Shiller Home Price Index", "unit": "index"},

    # Inflation & Prices
    "cpi": {"id": "CPIAUCSL", "name": "Consumer Price Index", "unit": "index"},
    "cpi_food": {"id": "CPIUFDSL", "name": "CPI: Food", "unit": "index"},
    "cpi_energy": {"id": "CPIENGSL", "name": "CPI: Energy", "unit": "index"},
    "pce": {"id": "PCEPI", "name": "PCE Price Index", "unit": "index"},
    "gas_price": {"id": "GASREGW", "name": "Regular Gas Price", "unit": "$/gallon"},

    # Labor & Income  
    "unemployment_rate": {"id": "UNRATE", "name": "Unemployment Rate", "unit": "%"},
    "labor_force_participation": {"id": "CIVPART", "name": "Labor Force Participation", "unit": "%"},
    "median_income": {"id": "MEHOINUSA672N", "name": "Median Household Income", "unit": "$"},
    "avg_hourly_earnings": {"id": "CES0500000003", "name": "Avg Hourly Earnings", "unit": "$"},
    "initial_claims": {"id": "ICSA", "name": "Initial Jobless Claims", "unit": "thousands"},
    "job_openings": {"id": "JTSJOL", "name": "Job Openings", "unit": "thousands"},

    # GDP & Economy
    "real_gdp": {"id": "GDPC1", "name": "Real GDP", "unit": "billions $"},
    "gdp_growth": {"id": "A191RL1Q225SBEA", "name": "GDP Growth Rate", "unit": "%"},
    "consumer_spending": {"id": "PCE", "name": "Personal Consumption", "unit": "billions $"},
    "consumer_confidence": {"id": "UMCSENT", "name": "Consumer Sentiment", "unit": "index"},

    # Money & Rates
    "fed_funds_rate": {"id": "FEDFUNDS", "name": "Federal Funds Rate", "unit": "%"},
    "treasury_10yr": {"id": "DGS10", "name": "10-Year Treasury Yield", "unit": "%"},
    "treasury_2yr": {"id": "DGS2", "name": "2-Year Treasury Yield", "unit": "%"},
    "m2_money_supply": {"id": "M2SL", "name": "M2 Money Supply", "unit": "billions $"},
    "national_debt": {"id": "GFDEBTN", "name": "Federal Debt", "unit": "millions $"},

    # Real Estate Specific
    "cre_loan_delinquency": {"id": "DRCRELEXFACBS", "name": "CRE Loan Delinquency Rate", "unit": "%"},
    "rental_vacancy": {"id": "RRVRUSQ156N", "name": "Rental Vacancy Rate", "unit": "%"},
    "rent_cpi": {"id": "CUSR0000SEHA", "name": "CPI: Rent of Primary Residence", "unit": "index"},
    "building_permits": {"id": "PERMIT", "name": "Building Permits", "unit": "thousands"},

    # Debt & Savings
    "personal_savings_rate": {"id": "PSAVERT", "name": "Personal Savings Rate", "unit": "%"},
    "consumer_credit": {"id": "TOTALSL", "name": "Total Consumer Credit", "unit": "millions $"},
    "credit_card_delinquency": {"id": "DRCCLACBS", "name": "Credit Card Delinquency Rate", "unit": "%"},
    "student_loan_debt": {"id": "SLOAS", "name": "Student Loan Debt", "unit": "billions $"},
    "auto_loan_debt": {"id": "MVLOAS", "name": "Motor Vehicle Loans", "unit": "billions $"},
}

# --- Story Templates (narrative frameworks for different data patterns) ---
STORY_TEMPLATES = {
    "surge": "rapid increase in {metric} — what's driving it and what it means for Americans",
    "collapse": "dramatic decline in {metric} — who's being hit hardest",
    "divergence": "{metric_a} and {metric_b} are moving in opposite directions — here's why that's a warning sign",
    "milestone": "{metric} just hit a level not seen since {year} — here's the context",
    "comparison": "comparing {metric} across the last 3 recessions tells a surprising story",
    "acceleration": "{metric} isn't just changing — it's changing faster than ever",
}

                ```

FILE: scripts/orchestrator.py
                ```text
                """
The Money Map — Full Pipeline Orchestrator (V2)

Enhanced pipeline with LLM scripting, automated quality control, and YouTube
upload policy handling.

Usage:
    python orchestrator.py                      # Full pipeline
    python orchestrator.py --step data            # Run from specific step
    python orchestrator.py --step quality          # Resume from quality check
    python orchestrator.py --dry-run               # Show what would be produced
    python orchestrator.py --script-mode llm       # Use LLM for scripts (default)
    python orchestrator.py --no-upload             # Skip YouTube upload
    python orchestrator.py --no-broll              # Skip b-roll generation
    python orchestrator.py --no-music              # Skip background music
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
OUTPUT_DIR = os.path.join(BASE, 'output')

from config.settings import (  # noqa: E402
    YOUTUBE_DEFAULT_PRIVACY,
    YOUTUBE_PUBLISH_OFFSET_DAYS,
)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")


def step_data():
    log("STEP 1: Fetching fresh economic data from FRED...")
    from scripts.data_ingestion import FREDClient
    client = FREDClient()
    result = client.fetch_all()

    out_path = os.path.join(DATA_DIR, 'latest_data.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)

    log(f"  Fetched {len(result['data'])} indicators")
    return result


def step_story():
    log("STEP 2: Discovering stories...")
    from scripts.story_discovery import build_story_package

    data_path = os.path.join(DATA_DIR, 'latest_data.json')
    pkg = build_story_package(data_path)

    log(f"  Top story: {pkg['primary']['name']}")
    log(f"  YoY change: {pkg['primary']['yoy_pct']:.1f}%")
    log(f"  Score: {pkg['primary']['score']}")
    return pkg


def step_research(story_pkg):
    log("STEP 3: Building research dossier...")
    from scripts.topic_research import generate_research_dossier, save_dossier

    dossier = generate_research_dossier(story_pkg)
    primary_key = story_pkg.get('primary', {}).get('key', 'unknown')
    dossier_json, dossier_md = save_dossier(primary_key, dossier, base_dir=DATA_DIR)

    log(f"  Dossier saved: {dossier_json}")
    log(f"  Published confidence: {dossier.get('confidence', 0):.2f}")

    return {
        "dossier": dossier,
        "dossier_json": dossier_json,
        "dossier_md": dossier_md,
    }


def step_script(story_pkg, script_mode='llm', dossier=None):
    log(f"STEP 4: Writing script (mode: {script_mode})...")

    if script_mode == 'llm':
        from scripts.llm_script_writer import generate_script_with_research
        script_data = generate_script_with_research(story_pkg, dossier=dossier)
    else:
        from scripts.enhanced_script_writer import generate_enhanced_script
        script_data = generate_enhanced_script(story_pkg)

    out_path = os.path.join(DATA_DIR, 'latest_script.json')
    with open(out_path, 'w') as f:
        json.dump(script_data, f, indent=2)

    vo_path = os.path.join(DATA_DIR, 'voiceover_script.txt')
    with open(vo_path, 'w') as f:
        f.write(script_data['script'])

    if dossier:
        log(f"  Title: {script_data['title']}")
        log(f"  Words: {script_data['word_count']}")
        log(f"  Est. duration: ~{script_data['estimated_duration_sec']}s")
        return script_data

    log(f"  Title: {script_data['title']}")
    log(f"  Words: {script_data['word_count']}")
    log(f"  Est. duration: ~{script_data['estimated_duration_sec']}s")
    return script_data


def step_broll(script_data):
    log("STEP 5: Generating b-roll clips via Luma...")
    from scripts.broll_generator import generate_broll

    broll_prompts = script_data.get('broll_prompts', {})
    if not broll_prompts:
        log("  No b-roll prompts found in script — skipping")
        return {}

    broll_dir = os.path.join(OUTPUT_DIR, 'broll_latest')
    results = generate_broll(broll_prompts, broll_dir)

    generated = sum(1 for v in results.values() if v is not None)
    log(f"  B-roll complete: {generated}/{len(results)} clips")
    return results


def step_voiceover():
    log("STEP 6: Voiceover generation...")
    vo_path = os.path.join(OUTPUT_DIR, 'voiceover.mp3')
    script_path = os.path.join(DATA_DIR, 'voiceover_script.txt')

    if os.path.exists(vo_path):
        age_hours = (time.time() - os.path.getmtime(vo_path)) / 3600
        if age_hours < 2:
            log(f"  Using existing voiceover ({age_hours:.1f}h old)")
            return vo_path

    from scripts.tts_generator import generate_voiceover
    log("  Generating voiceover via OpenAI gpt-4o-mini-tts...")
    result_path = generate_voiceover(script_path=script_path, output_path=vo_path)
    log(f"  Voiceover saved: {result_path}")
    return result_path


def step_music(voiceover_path, script_data):
    log("STEP 7: Mixing background music...")
    from scripts.audio_mixer import process_audio

    mixed_path = process_audio(voiceover_path, script_data, OUTPUT_DIR)
    if mixed_path != voiceover_path:
        log(f"  Mixed audio saved: {mixed_path}")
    else:
        log("  No music available — using raw voiceover")

    return mixed_path


def step_render(script_data=None):
    log("STEP 8: Rendering video...")
    if script_data:
        from scripts.enhanced_renderer import render_episode

        script_path = os.path.join(DATA_DIR, 'latest_script.json')
        ep_num = 'latest'
        render_episode(ep_num, script_path, OUTPUT_DIR)
        video_path = os.path.join(OUTPUT_DIR, f'ep{ep_num}_v2_final.mp4')
    else:
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(BASE, 'scripts/render_pilot.py')],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            log(f"  RENDER FAILED: {result.stderr[-500:]}")
            raise RuntimeError(f"Render failed: {result.stderr[-500:]}")
        video_path = os.path.join(OUTPUT_DIR, 'pilot_episode.mp4')

    log(f"  Video: {video_path}")
    return video_path


def step_assemble(dataviz_path, broll_paths, audio_path, script_data):
    log("STEP 9: Final assembly (interleaving b-roll + audio)...")
    from scripts.final_assembly import assemble_episode_dynamic

    output_path = os.path.join(OUTPUT_DIR, 'latest_final.mp4')
    result = assemble_episode_dynamic(
        dataviz_path, broll_paths, audio_path, output_path,
        script_data=script_data,
    )
    log(f"  Final video: {result}")
    return result


def step_thumbnail(script_data=None):
    log("STEP 10: Generating thumbnail...")
    from scripts.enhanced_thumbnail import generate_enhanced_thumbnail

    if script_data is None:
        script_path = os.path.join(DATA_DIR, 'latest_script.json')
        with open(script_path) as f:
            script_data = json.load(f)

    thumb_path = os.path.join(OUTPUT_DIR, 'thumbnail.png')
    generate_enhanced_thumbnail(script_data, thumb_path)
    log(f"  Thumbnail: {thumb_path}")
    return thumb_path


def step_quality(script_data, artifact_paths, strict=True):
    log("STEP 11: Running quality gate...")
    from scripts.episode_tracker import get_recent_titles
    from scripts.quality_gate import quality_gate_report_path, run_quality_gate

    result = run_quality_gate(
        script_data=script_data,
        artifact_paths=artifact_paths,
        previous_titles=get_recent_titles(),
        strict=strict,
    )

    report_path = quality_gate_report_path(result, DATA_DIR)
    log(f"  Quality status: {result['status']} (score={result['check
...[truncated by deep research runner]...
                ```

FILE: scripts/llm_script_writer.py
                ```text
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
from config.settings import (
    OPENAI_API_KEY,
    SCRIPT_LLM_MODEL,
    SCRIPT_RESPONSE_FORMAT,
    TARGET_WORD_COUNT,
)

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


def _build_data_context(story_pkg, dossier):
    """Format the raw data into a clear context block for the LLM."""
    primary = story_pkg['primary']
    related = story_pkg.get('related', [])
    dossier = dossier or {}

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

    lines.extend(
        [
            "",
            "RESEARCH DOSSIER:",
            f"  Summary: {dossier.get('summary', 'No dossier summary provided.')}",
            f"  Angle: {dossier.get('angle', 'No angle provided.')}",
            "  Novelty: "
            f"{dossier.get('novelty', 'No novelty guidance provided.')}",
            "  Watch-outs:",
            *(f"    - {item}" for item in dossier.get("watch_outs", [])),
            "  Source candidates:",
            *(f"    - {item}" for item in dossier.get("source_list", [])),
            "  Hook options:",
            *(f"    - {item}" for item in dossier.get("hook_directions", [])),
            "",
            f"  Dossier confidence: {dossier.get('confidence', 'N/A')}",
        ]
    )

    return "\n".join(lines)


def _extract_json(response_text: str) -> dict:
    """Extract JSON from response output that may include markdown wrappers."""
    clean = response_text.strip()
    if clean.startswith("```"):
        clean = clean.replace("```json", "").replace("```", "").strip()
    start = clean.find("{")
    end = clean.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM response does not contain JSON payload.")
    return json.loads(clean[start:end + 1])


def generate_llm_script(story_pkg, dossier=None):
    """Generate a script using the configured GPT-5 model with structured output."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    data_context = _build_data_context(story_pkg, dossier or {})
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

    response = client.responses.create(
        model=SCRIPT_LLM_MODEL,
        instructions=system,
        input=messages,
...[truncated by deep research runner]...
                ```

FILE: scripts/tts_generator.py
                ```text
                """
The Money Map — TTS Voiceover Generator

Generates voiceover audio using OpenAI's gpt-4o-mini-tts model.
Supports style control via natural language instructions for pacing,
emotion, and emphasis.

Usage:
    from scripts.tts_generator import generate_voiceover
    path = generate_voiceover()  # Uses defaults from settings
"""
import os
import re
import subprocess
import tempfile

from openai import OpenAI

# Allow running from repo root or scripts/
try:
    from config.settings import (
        OPENAI_API_KEY, TTS_MODEL, TTS_VOICE, TTS_INSTRUCTIONS,
    )
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import (
        OPENAI_API_KEY, TTS_MODEL, TTS_VOICE, TTS_INSTRUCTIONS,
    )

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
OUTPUT_DIR = os.path.join(BASE, 'output')

# OpenAI TTS has a 4096 character limit per request
MAX_CHARS_PER_REQUEST = 4096


def _split_script(text, max_chars=MAX_CHARS_PER_REQUEST):
    """Split script into chunks at sentence boundaries, respecting the char limit."""
    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        candidate = (current_chunk + " " + sentence).strip() if current_chunk else sentence
        if len(candidate) <= max_chars:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _concatenate_audio_files(file_paths, output_path):
    """Concatenate multiple MP3 files using ffmpeg."""
    if len(file_paths) == 1:
        os.rename(file_paths[0], output_path)
        return

    list_file = output_path + ".list"
    try:
        with open(list_file, 'w') as f:
            for path in file_paths:
                f.write(f"file '{path}'\n")

        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
             '-i', list_file, '-c', 'copy', output_path],
            capture_output=True, text=True, check=True, timeout=60,
        )
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)


def generate_voiceover(
    script_path=None,
    output_path=None,
    voice=None,
    instructions=None,
):
    """Generate voiceover MP3 from a text script using OpenAI TTS.

    Args:
        script_path: Path to plain-text script. Defaults to data/voiceover_script.txt.
        output_path: Where to save the MP3. Defaults to output/voiceover.mp3.
        voice: OpenAI voice name. Defaults to settings.TTS_VOICE.
        instructions: Style instructions. Defaults to settings.TTS_INSTRUCTIONS.

    Returns:
        str: Absolute path to the generated MP3 file.
    """
    script_path = script_path or os.path.join(DATA_DIR, 'voiceover_script.txt')
    output_path = output_path or os.path.join(OUTPUT_DIR, 'voiceover.mp3')
    voice = voice or TTS_VOICE
    instructions = instructions or TTS_INSTRUCTIONS

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(script_path, 'r') as f:
        script_text = f.read().strip()

    if not script_text:
        raise ValueError(f"Script file is empty: {script_path}")

    client = OpenAI(api_key=OPENAI_API_KEY)
    chunks = _split_script(script_text)

    if len(chunks) == 1:
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=voice,
            input=chunks[0],
            instructions=instructions,
            response_format="mp3",
        )
        response.stream_to_file(output_path)
    else:
        # Multiple chunks — generate each, then concatenate
        temp_files = []
        try:
            for i, chunk in enumerate(chunks):
                temp_path = os.path.join(
                    tempfile.gettempdir(), f"tmm_tts_chunk_{i}.mp3"
                )
                response = client.audio.speech.create(
                    model=TTS_MODEL,
                    voice=voice,
                    input=chunk,
                    instructions=instructions,
                    response_format="mp3",
                )
                response.stream_to_file(temp_path)
                temp_files.append(temp_path)

            _concatenate_audio_files(temp_files, output_path)
        except Exception:
            # Clean up temp files on error
            for path in temp_files:
                if os.path.exists(path):
                    os.remove(path)
            raise

    return os.path.abspath(output_path)


if __name__ == "__main__":
    print("Generating voiceover...")
    path = generate_voiceover()
    print(f"Done: {path}")

                ```

FILE: scripts/youtube_api_uploader.py
                ```text
                """
YouTube API Uploader for The Money Map
Automated video upload via YouTube Data API v3 with OAuth 2.0.

One-time browser auth for consent, then fully automated via refresh token.
Supports upload, thumbnail, and scheduled publishing.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    YOUTUBE_CLIENT_SECRET_PATH,
    YOUTUBE_TOKEN_PATH,
    YOUTUBE_CATEGORY_ID,
    YOUTUBE_PROCESSING_POLL_SECONDS,
    YOUTUBE_PROCESSING_TIMEOUT_SECONDS,
)

# YouTube API scopes needed
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

# Retry settings for resumable uploads
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 4, 8]
SUCCESS_PROCESSING_STATES = {"success", "processed"}
ERROR_PROCESSING_STATES = {"failed", "terminated", "rejected"}


def _fetch_video_status(youtube, video_id: str) -> dict[str, str | None]:
    """Fetch processing/visibility metadata for a YouTube upload."""
    response = youtube.videos().list(
        part="status,processingDetails",
        id=video_id,
    ).execute()

    items = response.get("items") or []
    if not items:
        raise RuntimeError(f"Uploaded video not found in status check: {video_id}")

    status = items[0].get("status") or {}
    processing = items[0].get("processingDetails") or {}
    upload_status = status.get("uploadStatus")
    processing_status = processing.get("processingStatus")
    return {
        "uploadStatus": upload_status,
        "processingStatus": processing_status,
        "privacyStatus": status.get("privacyStatus"),
        "publishAt": status.get("publishAt"),
    }


def _wait_for_processing(
    youtube,
    video_id: str,
    *,
    timeout_seconds: int = YOUTUBE_PROCESSING_TIMEOUT_SECONDS,
    poll_interval: int = YOUTUBE_PROCESSING_POLL_SECONDS,
) -> dict[str, str | None]:
    """Wait until video processing reaches a terminal state."""
    start = time.time()
    last_printed = None
    while time.time() - start < timeout_seconds:
        status = _fetch_video_status(youtube, video_id)
        key = f"{status['uploadStatus']}/{status['processingStatus']}"
        if key != last_printed:
            print(f"  Processing status: {key}")
            last_printed = key

        processing_status = (status.get("processingStatus") or "").lower()
        upload_status = (status.get("uploadStatus") or "").lower()

        if processing_status in SUCCESS_PROCESSING_STATES:
            return status

        if processing_status in ERROR_PROCESSING_STATES:
            raise RuntimeError(f"Video processing failed (processingStatus={processing_status})")

        if upload_status == "processed" and processing_status in (None, "", "completed"):
            return status

        time.sleep(poll_interval)

    raise TimeoutError(
        f"Video did not finish processing after {timeout_seconds}s: video_id={video_id}"
    )


def _set_thumbnail_if_ready(youtube, video_id: str, thumbnail_path: str | None):
    """Upload thumbnail only after the upload is fully processed."""
    if not (thumbnail_path and os.path.exists(thumbnail_path)):
        return

    from googleapiclient.http import MediaFileUpload

    try:
        print(f"  Setting thumbnail: {thumbnail_path}")
        thumb_media = MediaFileUpload(thumbnail_path, mimetype="image/png")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=thumb_media,
        ).execute()
        print("  Thumbnail set successfully")
    except Exception as e:
        print(f"  WARNING: Thumbnail upload failed: {e}")
        return

def _get_authenticated_service():
    """Build an authenticated YouTube API service using OAuth 2.0."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None

    # Load existing token
    if os.path.exists(YOUTUBE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_PATH, SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  Refreshing YouTube OAuth token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(YOUTUBE_CLIENT_SECRET_PATH):
                raise FileNotFoundError(
                    f"YouTube client secret not found at {YOUTUBE_CLIENT_SECRET_PATH}. "
                    f"Download it from Google Cloud Console → APIs & Services → Credentials."
                )
            print("  Starting OAuth flow — a browser window will open...")
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open(YOUTUBE_TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
        print(f"  Token saved to {YOUTUBE_TOKEN_PATH}")

    return build('youtube', 'v3', credentials=creds)


def upload_video(video_path, title, description, tags, thumbnail_path=None,
                 privacy="public", category_id=None, publish_at=None):
    """Upload a video to YouTube with metadata.

    Args:
        video_path: Path to the video file
        title: Video title (max 100 chars)
        description: Video description (max 5000 chars)
        tags: List of tags (max 30)
        thumbnail_path: Optional path to thumbnail image
        privacy: "public", "unlisted", or "private"
        category_id: YouTube category ID (default from settings)
        publish_at: ISO 8601 datetime for scheduled publishing (requires privacy="private")

    Returns:
        dict with video_id and video_url
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    youtube = _get_authenticated_service()

    # Truncate title/description to YouTube limits
    title = title[:100]
    description = description[:5000]
    tags = tags[:30]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id or YOUTUBE_CATEGORY_ID,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    # Scheduled publishing
    if publish_at:
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_at

    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"  Uploading: {title}")
    print(f"  File: {video_path} ({os.path.getsize(video_path) / 1024 / 1024:.1f} MB)")

    # Resumable upload with retries
    response = None
    for attempt in range(MAX_RETRIES):
        try:
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"  Upload progress: {progress}%")
            break
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF[attempt]
                print(f"  Upload error: {e}. Retrying in {wait}s...")
                time.sleep(wait)
                response = None
            else:
                raise RuntimeError(f"Upload failed after {MAX_RETRIES} attempts: {e}")

    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  Upload co
...[truncated by deep research runner]...
                ```

FILE: tasks/todo.md
                ```text
                # The Money Map — Task Tracking

## Active Sprint

### [x] CRE Balance Sheet Narrated Episode
- **Goal**: Produce a finished narrated audio track and video for the supplied CRE script about personal financial statements and risk capacity
- **Branch**: `main`
- **Steps**:
  - [x] Structure the supplied script into reusable source assets and section metadata
  - [x] Implement a custom section-based renderer/assembler for narrated non-FRED episodes
  - [x] Generate voiceover audio and final video exports for this episode
  - [x] Verify artifact integrity and document output paths + durations
- **Verification**:
  - [x] Baseline test suite run recorded (`python -m pytest`)
  - [x] Voiceover audio generated successfully
  - [x] Final video renders successfully
  - [x] `ffprobe` confirms output durations/codecs
- **Status**: complete
- **Review**: Added `scripts/custom_episode_builder.py`, committed the supplied CRE script as `data/cre_balance_sheet_fortress/episode.json`, added a small pytest slice for the builder helpers, and produced `data/cre_balance_sheet_fortress/voiceover.mp3` (~474.55s) plus `output/cre_balance_sheet_fortress.mp4` (1920x1080 H.264/AAC, ~474.57s).

### [x] Video Automation Enhancement (V2 Pipeline)
- **Goal**: Better, longer, higher-quality videos with full automation
- **Branch**: `claude/video-automation-planning-sciHi`
- **Steps**:
  - [x] Phase 1: LLM-powered script writer (`scripts/llm_script_writer.py`) — GPT-5.2
  - [x] Phase 2: Background music mixer (`scripts/audio_mixer.py`) — ffmpeg mixing
  - [x] Phase 3: Automated b-roll via Luma Dream Machine (`scripts/broll_generator.py`)
  - [x] Phase 4: Enhanced renderer with dynamic scene durations (`scripts/enhanced_renderer.py`)
  - [x] Phase 5: YouTube API uploader with OAuth 2.0 (`scripts/youtube_api_uploader.py`)
  - [x] Phase 6: Episode history tracker (`scripts/episode_tracker.py`)
  - [x] Update config/settings.py with all new settings
  - [x] Rewrite orchestrator.py with 11-step V2 pipeline
  - [x] Update final_assembly.py for dynamic segments + mixed audio
  - [x] Update story_discovery.py with recency penalties
  - [x] Clean up hardcoded credentials from youtube_uploader.py and cron_instructions.py
  - [x] Update requirements.txt and .gitignore
- **Verification**:
  - [ ] Pipeline runs end-to-end (`python orchestrator.py --dry-run`)
  - [ ] LLM script generates ~700 word scripts
  - [ ] Background music mixes correctly at -18dB
  - [ ] B-roll clips generate and normalize properly
  - [ ] YouTube OAuth flow works
  - [ ] Episode history tracks and applies recency penalties
- **Status**: review
- **Summary**: Complete V2 pipeline rewrite. 5 new modules, 7 modified files. Videos now target 4-5 minutes with LLM-written scripts, background music, automated Luma b-roll, and YouTube API upload.

---

## Backlog
- [ ] Add pytest suite (data_ingestion, story_discovery, script_writer)
- [ ] Source royalty-free ambient music tracks for assets/music/
- [ ] Set up YouTube OAuth client secret (Google Cloud Console)
- [ ] Set up Luma API key
- [ ] Add retry/backoff logic to FRED API calls
- [ ] Add CI via GitHub Actions (lint + test)
- [ ] Dockerize the pipeline for reproducible runs
- [ ] Add type hints to core modules
- [ ] Multi-metric "mashup" episode type (Phase 7)

## Completed
<!-- Move finished tasks here with date and one-line summary -->

                ```
        ```

        ## Report

        # Executive Summary  
**The Money Map** repository already automates much of the YouTube video production pipeline – from data gathering and script generation to voiceover, visual rendering, thumbnail creation, and uploading. This analysis finds that while the core pipeline is in place, key systems are missing to make the channel truly autonomous. In particular, dynamic topic selection, richer context research, rigorous script quality assurance, and feedback loops for continuous improvement are areas to address. By leveraging advanced OpenAI capabilities (e.g. GPT-based research agents, function-calling for structured outputs, and upgraded models), we can elevate the pipeline to a production-grade, minimal-touch “content machine.” The recommendations below detail immediate code upgrades and longer-term architectural changes – all citation-backed and focused on concrete implementation guidance rather than generic advice.

# Current State  
**Pipeline & Automation:** *The Money Map* pipeline is currently designed as an end-to-end automated system that turns U.S. Federal Reserve (FRED) economic data into a complete YouTube video. The repository’s README outlines a multi-step process from data ingestion to YouTube upload. Key modules include:  

- **Data Ingestion:** A script fetches ~34 curated economic indicators from the FRED API and computes year-over-year changes for context (e.g. personal savings rate, mortgage rates) – providing the raw material for each video’s story.  
- **Story Discovery:** An automated ranking selects the “most viral” metric as the video’s topic. Currently this is based on factors like the magnitude of change (especially YoY%) which proxies for newsworthiness. (E.g. a plunging savings rate or a spike in debt might score highest.) This step ensures each episode centers on a timely data story without manual topic input.  
- **Script Generation:** A *Large Language Model* (LLM) writes the video script. In the latest pipeline version, the repository uses an OpenAI GPT model (`gpt-5.4` as per settings) to produce ~700-word scripts following a defined structure – from a “[COLD_OPEN]” hook to the “[CLOSE]” call-to-action. The LLM is guided by a system prompt that enforces the channel’s voice and an 8-section format. It also generates a video title, description (with timestamps), and tags in JSON format. This is a major upgrade from earlier template-based scripts, resulting in more engaging, varied narration.  
- **Research Dossier:** To enrich the script, the pipeline can compile a research dossier on the chosen topic using an LLM agent with web access. The `o3-deep-research` model (OpenAI’s tool-using agent) is configured to perform up to 24 tool calls, likely doing web searches and reading articles to gather context. This produces a summary, angle, and list of relevant facts or sources, which feed into the script prompt. Using such an agent aligns with OpenAI’s 2025-era “Responses API” that lets models call tools for richer, up-to-date context ([openai.com](https://openai.com/index/new-tools-and-features-in-the-responses-api/#:~:text=window%29,more%20contextually%20rich%20and%20relevant)). This means the script isn’t written in a vacuum – it’s informed by current events and background info around the data, all done autonomously by the AI.  
- **Voiceover (TTS):** The finalized script is converted to spoken narration using an AI text-to-speech model. The repo uses an OpenAI voice model (`gpt-4o-mini-tts`, voice “ash”) to generate a male, authoritative voiceover. The code splits the script into chunks (to avoid API limits ~4096 chars) and streams the audio to an MP3 file. OpenAI’s recently opened voice capabilities (from late 2024) mean high-quality, human-like narration can be generated on the fly ([www.axios.com](https://www.axios.com/2024/10/01/chatgpt-developers-ai-voice-engine#:~:text=OpenAI%20is%20giving%20other%20developers,order%20for%20400%20chocolate%20covered)). This eliminates the need for a human voice actor while maintaining a professional tone.  
- **Data Visualization Renderer:** Economic data is turned into cinematic charts and animations. The V2 renderer uses Matplotlib to create 1080p visualizations (with custom colors, glowing effects, animated counters, etc.), outputting a base video of the chart. It can adjust scene timing to align with the script’s narration of the data (“chart walk”). Essentially, this module ensures the core data is visualized clearly and dramatically, forming the backbone of the video visuals.  
- **AI B-Roll Generation:** Beyond charts, the pipeline adds variety with cutaway “B-roll” clips generated by an AI video model (via Luma’s Dream Machine API). The script provides three textual prompts (for hook, context, insight segments), and each prompt yields a ~4-second synthetic video clip (e.g. a shot of worried shoppers for an inflation story) that gets inserted to keep viewers engaged. This replaces the manual process of finding stock footage. It’s noteworthy that generative video AI is an evolving tech – OpenAI’s own foray (code-named *Sora* for text-to-video) is on the horizon ([www.techradar.com](https://www.techradar.com/computing/artificial-intelligence/sora-2-is-coming-but-it-will-have-to-dazzle-viewers-to-beat-googles-veo-3-model#:~:text=2025,raised%20the%20bar%20by%20incorporating)) – but the current system relies on Luma’s service to achieve similar results.  
- **Music and Audio Mixing:** The pipeline supports background music mixing. A library of royalty-free tracks (or AI-generated music) can be added under the narration at a subtle volume. The current codebase has a mixer that will duck volumes appropriately. However, it appears this is not fully utilized yet (the team noted needing to source music tracks). For now, videos may go out with voiceover only, but the code is ready to add music for a more polished output when assets are provided.  
- **Thumbnail Generation:** An automated thumbnail creator produces a 1280x720 image highlighting the video’s key stat and title. The V2 thumbnail script uses Matplotlib and a bold design (dark background, large text) aiming for a high click-through-rate (CTR). While not as flashy as human-designed thumbnails, it ensures every video has a consistent, on-brand thumbnail without manual design work.  
- **Assembly & Upload:** Finally, the pipeline assembles all components into the final video. Using FFmpeg, it concatenates the chart video with B-roll clips, overlays the voiceover (and music), and outputs a finished MP4. The `youtube_api_uploader.py` then handles uploading the video and thumbnail via YouTube’s Data API. It sets metadata (title, description, tags) from the LLM output and can even schedule the video as private or public based on config. OAuth2 credentials are used so this can run headless. With this, the video is live on the channel – theoretically, no human needed to hit “Publish.”  

**Scheduling & Trigger:** Currently, new videos are triggered by a cron job (e.g. every Monday 8AM per README). This means the whole pipeline can run on a schedule to maintain a consistent upload cadence. All required API keys (FRED, OpenAI, etc.) and settings are configured in environment variables, so the process can run automatically on a server each week. The result is a *faceless*, AI-driven YouTube channel that produces data-driven news content regularly without on-camera presenters. This approach epitomizes the emerging trend of automated content creation – using AI for scripting, narration, and visuals so that daily uploads are possible “without burnout” ([www.yourautomatedlife.com](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=platforms%20like%20ChatGPT%2C%20Fliki%2C%20and,enabling%20daily%20uploads%20without%20burnout)).

**Existing Quality Controls:** The repo does include some quality and safety checks. A “quality gate” step runs after rendering, intended to prevent subpar videos from publishing. This likely checks for issues like duplicate topics (the code tracks recent video titles to avoid repeating a story too soon) and possibly script coherence or length. If the quality gate fails (score below threshold or a flagged issue), the pipeline can stop before uploading. Additionally, the script generator has instructions to avoid certain pitfalls (e.g. “no emoji, don’t be alarmist”) and uses a JSON format to enforce all needed fields (title, tags, etc.). However, as we’ll see, these measures could be expanded further for a truly production-grade system.

# Gaps To Full Automation  
Despite the impressive automation already in place, there are several gaps preventing this from being a **genuinely autonomous YouTube channel**. Achieving full production-grade automation means addressing the following areas that currently require either manual effort or risk compromising quality:

- **🔍 Topic Selection & Trend Relevance:** Right now, topic selection is based purely on internal data changes (e.g. the biggest % drop among tracked metrics). This misses external context – for example, a moderate change in unemployment might actually be more newsworthy this week if it’s in headlines, compared to a larger change in a obscure metric. The system lacks integration with trend data (Google Trends, news headlines, social media) to ensure chosen topics align with what the audience cares about *today*. An autonomous channel needs to “sense” what’s trending to maximize relevance, not just pick metrics in a vacuum. Incorporating a trend check or news scan would fill this gap.

- **📑 Contextual Research Depth:** While a research dossier is generated, we need to confirm its robustness. Does the LLM agent find the latest credible facts and nuances for the story? Are multiple sources cross-checked? Without human researchers, the pipeline must ensure the context it provides (for script writing) is accurate and up-to-date. A potential gap is factual accuracy – the LLM might produce an angle or cite “sources” that sound plausible but are not verified. A truly autonomous system should include fact-checking (for instance, confirming any cited stats from the dossier against reputable sources) and possibly deeper research on *why* the metric moved (e.g. policy changes, events) so the script has real substance. In short, the research agent needs oversight or improvement to guarantee quality research comparable to a human researcher.

- **✍️ Script Quality Control:** The current LLM script generator produces structured output, but there’s minimal automated QA on the script text itself. Issues like hallucinated data (e.g. the LLM mis-stating a number), off-tone language, or repetition might slip through. For example, if the model ignored the “no emoji” rule or overshot the length, would the system catch it? There is a **quality gate**, but it appears basic (e.g. checking similarity to recent titles). Industry best practices for AI-generated content recommend rigorous checks – style adherence, factual accuracy, proper formatting, and originality ([oleno.ai](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=,test%2C%20and%20stop%20infinite%20loops)). The pipeline currently doesn’t verify that every figure in the script matches the actual data, nor that the script meets style guidelines beyond what the prompt enforced. To be production-grade, we need automated script QA: a “second-pass” LLM or rule-based checker that ensures the script is publish-ready (no policy violations, no glaring errors). Without such checks, a fully autonomous channel risks publishing a video with a mistake or something off-brand that a human would normally catch.

- **🎥 Asset Generation & Visual Quality:** The visual pipeline (charts + AI b-roll) works, but there are areas to improve for a polished, television-quality output. For instance, the **B-roll generation** might produce irrelevant or low-quality clips if the AI prompt is ambiguous – currently there’s no review of the generated clips’ relevance. Likewise, the **thumbnail generation** is automated but might be lacking in the kind of creativity/human touch that drives high click-through rates (e.g. emotionally resonant images or clever design). A fully autonomous system might incorporate more advanced generative visuals (like using a dedicated image AI for thumbnails to create a compelling scene, not just a chart) and have a way to ensure they meet quality standards (perhaps an AI vision model to detect if the thumbnail is visually appealing and legible). Right now, these creative decisions are rule-based and could be enhanced with AI or templates to reach human-designer level effectiveness.

- **✅ Edit & Output Verification:** In a manual workflow, an editor would watch the final video to ensure everything looks and sounds right (no glitches, audio in sync, etc.). In our pipeline, there’s no explicit automated verification of the final video. Potential issues like a segment of silence, a misaligned clip, or incorrect duration could go unnoticed. An autonomous setup should include an **edit QA** step – for example, programmatically checking the final video’s properties (duration matches sum of segment durations, audio peak levels are within range, etc.), and even using speech-to-text on the final audio to ensure it matches the script. Currently, if an assembly error occurred (say a clip missing), the pipeline might not catch it unless FFmpeg errors out. Introducing automated video QA would add confidence that the published video is glitch-free.

- **📣 Upload Metadata & SEO Optimization:** The LLM generates title, description, and tags, which is great automation. However, it’s unclear if the metadata is optimized for YouTube’s search and discovery. A human YouTube strategist might perform keyword research, craft a description with a strong hook and relevant links, and choose tags based on SEO tools. The gap here is the **finesse in metadata** – ensuring the title is not just under 70 characters, but really clickable; ensuring the description contains relevant keywords and maybe references to sources or related videos; and that tags target what viewers might search. The LLM does a decent job, but it might not know the *exact* trending keywords. For full autonomy, we could integrate keyword optimization (perhaps using an SEO API or prompting GPT with trending keyword data). Also, scheduling is handled via config (publish offset days), but there’s no dynamic logic (e.g. “post at the statistically best time for our channel”). That’s a minor gap – currently solved by a fixed cron time – but for completeness, an advanced system might adapt upload timing based on audience analytics.

- **📊 Analytics Feedback Loop:** One of the biggest missing pieces is what happens *after* upload. A human channel manager would monitor YouTube Analytics to see how each video performs – which topics get views or new subscribers, where audience retention drops off, etc. This feedback is crucial to refine content strategy. In the current setup, there’s no mechanism to learn from the results. A fully autonomous channel should at least log key performance metrics (views, watch time, click-through rate) for each video and feed that into future decisions. For example, if videos about consumer debt consistently outperform videos about housing data, the system might bias the story selection towards debt-related metrics or adjust the script tone accordingly. The gap is that without an analytics integration, the pipeline is “flying blind” – it can’t adapt or improve its content strategy over time. Automating performance tracking (e.g. via YouTube API or scraping analytics) and using that data to inform the pipeline is essential for a truly smart autonomous system ([www.yourautomatedlife.com](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=Once%20your%20uploads%20are%20in,reports%20automatically%20every%2024%20hours)).

- **💰 Cost & Reliability Guardrails:** Lastly, running a complex AI-driven pipeline introduces cost and reliability concerns that aren’t fully addressed. Each video triggers multiple OpenAI API calls (research agent, script writing, TTS voice) and possibly image/video generation calls – all of which can incur significant costs or rate limits over time. There’s a risk of runaway costs if something goes into a loop or if usage scales up (say daily videos) without monitoring. Currently, there’s no mentioned budget limit or usage tracking in the code. Similarly, reliability: what if an API fails (FRED downtime, OpenAI outage) or returns bad data? The pipeline should fail gracefully or retry, rather than produce a broken episode. We see some retry logic (e.g. YouTube upload has retries, and the script generator will fall back to a template if the LLM fails), but other parts could use hardening. Truly autonomous operation requires **guardrails**: e.g. a way to abort or switch to a cheaper model if OpenAI costs in a month exceed X, notifications if a run fails, and fallback behaviors (perhaps “skip B-roll generation this time” if the AI video service is down, etc.). At present, many of these guardrails are not implemented, which means a human still needs to oversee the process to some extent (defeating the goal of minimal involvement). For instance, one of the frequently asked questions in automation is how to handle API quotas and limits so the system doesn’t break unexpectedly ([www.yourautomatedlife.com](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=,automate%20my%20YouTube%20content%20creation)) – these considerations will need to be built into the next iteration.

In summary, the current codebase achieves automated video production, but to go **from automated to autonomous**, it needs improvements in decision-making (what to create and why), quality assurance (ensuring each video is as good as a human-produced one), and learning (getting better with each video). The following sections propose an architecture and specific changes to bridge these gaps.

# Recommended Architecture  
To transform the existing pipeline into a **production-grade automated YouTube machine**, we propose a modular architecture with new components for intelligence and oversight. Below is the recommended system architecture, with data flow between components:

1. **Trending Topic Scanner** – *New Module*: This component runs before data story selection. It can use external signals (Google Trends, news APIs, social media sentiment) to identify what economic or financial topics are gaining attention in the moment. Implementation could involve querying trending keywords in the finance category or scraping headlines of major financial news sites daily. An OpenAI LLM could assist by summarizing “what people are worried or curious about this week” based on news ([openai.com](https://openai.com/index/new-tools-and-features-in-the-responses-api/#:~:text=With%20built,Today)). The output is a set of hot topics or relevant angles (e.g. “inflation spike”, “mortgage crisis”, “debt ceiling debate”). This ensures the system’s content decisions are grounded in current zeitgeist, not just historical data changes.  

2. **Data Ingestion & Metric Update** – *Existing Module*: Continue to pull FRED (and potentially other data sources like Census, BLS once API keys are enabled) to get the latest values for our library of indicators. This populates a data store (JSON) with current values and YoY changes. No major change here except possibly broadening data sources for more story options in the future.

3. **Topic Selection Engine** – *Enhanced Module*: Combine the outputs of the trend scanner and data ingestion to choose a video topic. This could be a scoring system where each metric’s data “surprise” (e.g. large change or record level) is weighted by its current trend relevance. For example, if “unemployment” had a moderate change but unemployment is all over the news, it might win over a larger change in a niche metric. Implementation: augment `story_discovery.py` to call an OpenAI function that takes the list of candidate metrics (with their latest data) and a summary of trending topics, and returns the best story candidate with reasoning. This leverages AI to mimic an editorial meeting – balancing *what’s important (data)* with *what’s interesting (trends)*. The result is a “Story Package” containing the primary metric and possibly a couple of related metrics to mention for context (the current system already picks related metrics for context; we keep that).

4. **Research & Context Dossier** – *Expanded Module*: Using the selected story, an LLM agent (with tools) compiles a concise dossier of facts, context, and references. We retain the `generate_research_dossier` step but bolster it. The agent should answer: *Why is this metric changing? Who is affected? What historical context or expert opinions are there?* It can perform web searches, read relevant articles, and even fetch a statistic or quote that might enrich the video. The output dossier (in JSON or Markdown) contains: a summary of the situation, key points to include, potential pitfalls or “watch-outs” (e.g. avoid false causation), and a list of trustworthy sources or data points. This dossier feeds the script writer. By formalizing this step, we ensure the script has a factual backbone. (In practice, this might involve using OpenAI’s tool-using models with a defined chain-of-thought for say up to 10 searches/articles, then summarizing findings into the structured dossier.)

5. **Script Writing with QA Loop** – *Enhanced Module*: The LLM script writer uses the data and dossier to draft the narrative (as it does now), but we add a **QA loop** before finalizing the script. The initial draft from `GPT-5.4` (or an updated model) will be parsed and then evaluated by a secondary process. This could be another LLM prompt: e.g. “Review the following script for any factual errors or sections that are unclear or off-tone. List any issues and suggested fixes.” The model or a rule-based system checks that all numbers in the script match the data (we can automatically cross-verify numeric values against the data JSON), that the tone matches our guidelines (no sensationalism beyond what’s intended), and that the length/structure is within bounds. If issues are found, the script can either be auto-edited or the LLM can be asked to revise (e.g. provide corrected sentences). Only once the script passes the QA checks do we proceed. This **quality gate** could assign a score to the script (as mentioned, e.g. 0-100) based on a rubric of checks ([oleno.ai](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=,test%2C%20and%20stop%20infinite%20loops)), requiring a passing score to continue. Internally, this might live in `scripts/quality_gate.py` and use both deterministic checks and GPT-based evaluation for things like coherence or engagement level.

6. **Text-to-Speech Voiceover** – *Existing Module*: Use the AI voice to convert the final script to audio. This remains largely the same, but we might consider upgrading the voice model if newer, more natural-sounding voices are available. By 2026, OpenAI and others have released even more advanced TTS (for example, OpenAI’s voice cloning tech was in testing ([cincodias.elpais.com](https://cincodias.elpais.com/smartlife/lifestyle/2025-03-21/openai-nuevos-modelos-voz-transcripcion.html#:~:text=2025,a%20sus%20predecesores%20Whisper%2C%20destacando))). We should monitor available voices and possibly allow multiple voice options (to avoid every video sounding exactly the same, we could have a small range of voices or tones and let the script choose one that fits the episode mood). This adds variety and a human touch. The TTS module should also handle prosody instructions; our current system already passes a detailed style instruction string. No major architecture change here, just ensure it’s robust (with fallback: if TTS API fails, maybe use a secondary service or cached voice clips).

7. **Visualization Renderer** – *Existing Module*: Continue to generate the core chart animation for the data. We should ensure this module can take dynamic input on how long to make the chart segment. The script might dictate timing (e.g. if the “[CHART_WALK]” section is longer, the animation should be longer). The enhanced renderer already handles dynamic scene timing to some extent. In the future, we might integrate more sophisticated visualization (e.g. automatically highlight the specific data point being talked about, or show annotations on the chart for key events the script mentions). For now, the architecture keeps this as is, with potential to incorporate templates for multi-metric visuals (if we ever do a “comparison of 3 metrics” episode, the renderer would need templates to show multiple lines on one chart, etc.).

8. **AI B-Roll Generator** – *Existing Module*: Keep using the Luma API (or alternatives) to generate illustrative footage for abstract concepts. To improve this component’s reliability in the architecture, consider a validation step for B-roll. For example, after generation, run a quick computer vision caption or classifier on the clip to see if it matches the intended prompt (e.g. if we prompted “crowded shopping mall economic anxiety” and the AI produced something weird, the system could flag or regenerate). This ensures the visuals align with the story. Also, architecturally, we keep this separate from the main render to maintain flexibility – in case a future OpenAI video model (like *Sora*) becomes available, we could swap out the Luma API for our own generative model calls. It’s a pluggable component: as AI video tech evolves, the pipeline can adopt new tools without affecting other parts.

9. **Audio Mixing** – *Existing Module*: Blend voiceover with background music. The architecture should include a library of pre-vetted music tracks (or an AI music generator component) to lay under the narration. Music adds emotional tone – e.g. subtle tense music for a dire economic warning, or upbeat tone for a positive trend. We’d maintain a collection of license-free tracks categorized by mood. The system can pick a track based on the episode’s sentiment (the script or dossier could tag the story as “urgent”, “cautionary”, “optimistic”, etc.). The audio mixer then normalizes levels (keeping music ~-18 dB under voice, for instance). This component ensures the final audio is rich and not monotonous. It’s largely in place (the code supports it), but the architecture now formalizes using it systematically. If no music is desired or available, it can gracefully skip or default to silence – but ideally we integrate it for every video.

10. **Final Video Assembly** – *Existing Module*: Using FFmpeg or a video editing library, compose the final video from the chart animation, B-roll clips, and the mixed audio. The architecture should allow dynamic sequencing: e.g. insert B-roll at specific timestamps corresponding to script sections. The current `final_assembly.py` does interleave b-roll with data-viz; we will continue that, ensuring that if the script sections change length, the assembly code can adjust clip placement accordingly. We may also consider adding **branding elements** at this stage – e.g. an intro or outro card, a watermark logo, or auto-generated subtitles (for accessibility). Subtitles could be created by transcribing the voiceover (speech-to-text) and then hardcoding or uploading to YouTube. This is an optional addition but worth including in the architecture for completeness (since YouTube can auto-caption, it’s lower priority, but having our own ensures accuracy especially for technical terms). The assembly step outputs the final MP4 ready for upload.

11. **YouTube Upload & Scheduling** – *Existing Module*: The uploader will use YouTube’s API to upload the video, set it to the proper privacy setting (e.g. private if scheduling in future), apply the title/description/tags, upload the thumbnail, and schedule publishing as configured. In the improved architecture, this module could be extended to handle multiple videos in a queue (if we ever batch-produce or maintain an upload calendar). For now, it handles one video at a time. We should ensure it captures the returned video ID and maybe stores it along with the topic/date somewhere (to feed the analytics module later). Architecture-wise, this is the point where the content leaves our system to the platform.

12. **Analytics & Feedback Loop** – *New Module*: After upload, a new component will periodically pull performance data for published videos. Using the YouTube Analytics API (or even simpler, the Data API for basic stats), this module can fetch metrics like views, likes, watch time, retention graphs, subscriber gain, etc. We can schedule it to run daily or a few days after each video goes live. The data is then logged and **analyzed, possibly by an LLM**, to discern patterns. For example, we could prompt GPT with a summary of the last 5 videos’ topics and stats: “Analyze which video performed best and why. Consider title appeal, topic interest, audience retention. Provide suggestions for future topics or improvements.” This turns raw analytics into actionable insights automatically ([www.yourautomatedlife.com](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=Once%20your%20uploads%20are%20in,reports%20automatically%20every%2024%20hours)) ([www.yourautomatedlife.com](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=Go%20beyond%20basic%20reports%20by,subscription%20trends%20in%20real%20time)). The insights can be fed back into the Topic Scanner or Script Writer – effectively closing the loop. Over time, the system “learns” what content resonates with viewers (maybe the AI finds that videos with certain keywords in the title get above-average click-through, or that viewers drop off during heavy jargon sections – it can recommend avoiding those). This feedback mechanism is key for continuous improvement without a human strategist.  

13. **Monitoring & Control Panel** – *New/Optional:* For a production system, we should have a monitoring dashboard or at least logs that are human-readable. This isn’t a content module per se, but important architecturally. It would aggregate logs from each step (data fetched, topic picked, any warnings in quality gate, video uploaded link, performance metrics collected). It could be as simple as a Slack/Email notification after each run (“Video X uploaded, awaiting QA approval” or “Quality gate failed, needs attention”) or a full internal web dashboard tracking the pipeline status and upcoming schedule. This ensures that minimal human *involvement* doesn’t mean no human *oversight*. A stakeholder could glance at the dashboard to ensure all systems are healthy and intervene only when needed (e.g. if the quality gate flags something or if performance drops unexpectedly and the AI suggestions need review).

In this architecture, data and control flow in a loop: **Trend & data input → content creation pipeline → YouTube output → performance data → back to input.** The content creation itself is multi-stage, each with its own AI assist and validation. By designing components this way, we achieve a resilient system where each part does a specific job and can be improved or replaced independently. For example, if a better script-writing model comes out, we swap that in without overhauling research or assembly. Or if a new data source is added (say international economic data), the earlier stages can handle multiple sources. The modular design also means issues can be isolated – e.g. if B-roll generation fails, the system could still publish a video (with just charts) rather than abort the entire run. Similarly, the quality gate can intercept problems at the script stage, saving costs by not going through rendering/upload if content wasn’t up to par.

This proposed architecture extends the repo’s current design by adding the “brain” (trends + feedback) and the “safety net” (QA + monitoring) around the existing automated pipeline. It ensures the channel not only runs with minimal human input, but also can adapt and maintain quality standards expected from a professional channel.

# Top 5 Repo Changes (Immediate)  
Based on the gaps and the new architecture, here are the top five high-leverage changes to implement **immediately in the repository**. These focus on modifications or additions to the codebase that can be done in the short term to dramatically improve autonomy and quality:

1. **Upgrade LLM Model Usage and API Calls** – *Files: `config/settings.py`, `scripts/llm_script_writer.py`*: Update the code to use the latest OpenAI models and more robust API patterns. The repository currently references `GPT-5.4` and uses the Responses API with `client.responses.create`. Verify if a newer model (e.g., a GPT-5.x or GPT-6 if available) offers better output or lower cost. Adjust `SCRIPT_LLM_MODEL` in settings to the new model name. Additionally, refactor the script generation to use **function calling** for structured output instead of relying purely on prompt formatting. OpenAI introduced function calling in 2023 to enforce JSON outputs from the model – by defining a function schema, the model can return well-structured JSON reliably ([openai.com](https://openai.com/index/new-tools-and-features-in-the-responses-api/#:~:text=window%29,more%20contextually%20rich%20and%20relevant)). Implement this in `llm_script_writer.py`: define the output schema as a function or use OpenAI’s `functions=[…]` parameter with the schema (title, description, tags, etc.) as fields. This will eliminate the need for `_extract_json` and reduce the chance of formatting errors. Also, ensure we handle the system vs user prompt with the latest API (the code still uses a custom `OpenAI` client; if OpenAI’s Python SDK has changed, align with the new method calls). By upgrading the model and call method, we aim for more reliable and possibly faster script generation.  

2. **Integrate Trend Data into Story Discovery** – *Files: `scripts/story_discovery.py`, possibly new script e.g. `trend_helper.py`*: Modify the story selection logic to account for trending topics. For a quick win, use an external signal like Google Trends API or a news keyword search. For example, in `build_story_package()` (story discovery), after scoring by YoY change, adjust the scores: for each top candidate metric, query if that metric (or its theme) has been in the news in the last week (this could be a simple web search count or using an AI to judge). Concretely, you could call the OpenAI LLM with a prompt: “Here is a list of metrics and their one-sentence description. Which one do you think is most interesting to the general public *right now*, and why?” letting it incorporate its knowledge of recent events. Alternatively, integrate a small function to query Google Trends for the metric’s name (e.g. “unemployment rate”) and get a popularity index. This numeric trend score can be added to the metric’s viral score. If implementing directly, use the `pytrends` Python library to get a relative search interest for the past 7 days for each term. Then, in code, do something like: `score = normalized_yoy_change + w * trend_score`. Tune the weight `w` so that a trending topic can outweigh a slightly bigger YOY change for a dull topic. This change will ensure the selected story each week isn’t just data-driven but audience-driven. It might require new API credentials (for Google Trends or news API) – add those to `config/settings.py`. This is an immediate change that can yield more relevant content. *Example Implementation Detail:* Suppose “inflation” and “money supply” are two metrics close in YOY score; if Google Trends shows “inflation” is spiking in search or news mentions, the code should choose inflation as the episode topic.

3. **Enhance Script Quality Gate – Data Accuracy & Style Checks** – *Files: `scripts/quality_gate.py`, `scripts/llm_script_writer.py`*: Strengthen the quality checking before a video is finalized. First, implement a **data validation check**: after script generation, parse the script text for any numbers (regex for sequences of digits, or use the structured JSON already containing key values) and verify each against the actual data. If the script says “savings rate fell to 3%” but data shows 4%, that’s a red flag – adjust or re-prompt the LLM with the correct value. This can be done by passing the primary metric’s actual value into the prompt explicitly (the current system does, but double-check the LLM didn’t ad-lib something else). Add a function in `quality_gate.py` to compare `script_data['sections']` content against `story_pkg` values. Next, add **style and consistency checks**: e.g., ensure the script contains all 8 section markers and that each section has content (no section accidentally empty), and that the word count is within, say, 50 words of the target (the LLM already aims for ~700, but double-check). Also, leverage an LLM to do a quick qualitative review. For example, prompt: “Analyze the script for The Money Map episode and respond with any issues in tone, clarity, or factual consistency.” The response can be parsed for issues. If any major issues arise (model says “the script exaggerates a fact” or “contains a confusing point”), have the pipeline either auto-correct or halt for manual review depending on severity. We can quantify these checks into a score. For instance, assign points for each quality criterion met (correct data, no repeated sentences, presence of CTA, etc.), and require a minimum score (e.g. 85/100) to pass ([oleno.ai](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=,test%2C%20and%20stop%20infinite%20loops)). Document these rules in the project (maybe update `README` quality section) so it’s clear. This change will prevent flawed scripts from proceeding to production, increasing reliability.  

4. **Implement Background Music Automation** – *Files: `scripts/audio_mixer.py`, `config/settings.py`, plus asset folder*: Activate and enhance the background music feature for improved video quality. Currently, the code has flags `MUSIC_ENABLED` and a function to mix audio, but likely lacks actual music files. As an immediate step, integrate a small set of royalty-free music tracks into the project (e.g., add an `assets/music/` directory with a few .mp3 files of varying moods). Update `audio_mixer.process_audio()` to randomly select an appropriate track (or one based on the episode tone if we pass in a “mood” parameter). For now, even a random selection from 2-3 tracks adds variety. Mix the chosen track under the voiceover at a low volume (already -18 dB as mentioned). Ensure the mixer also trims or loops the music to match the voiceover length. This change is low-effort (just a matter of adding files and tweaking the mixer logic) but high impact in making the video sound more professional. In the future, we could use an AI music generator, but immediately we can manually pick a few decent background tracks and automate their use. Don’t forget to update documentation about how to add new music. As part of this change, test the final assembly to ensure the music doesn’t overpower speech and that encoding (stereo sound) is correct. Viewers will immediately notice the improvement in quality when videos have background music for atmosphere.

5. **Robust Error Handling & Logging** – *Files: `scripts/orchestrator.py`, `scripts/data_ingestion.py`, etc.*: Introduce a more robust error-handling approach across the pipeline to account for failures without human intervention. For example, in `data_ingestion.py`, add retry with exponential backoff for API calls to FRED (network issues or rate limits shouldn’t crash the whole run – try 3 times before giving up, and log if failed). In `orchestrator.py`, wrap each step call in try/except and on exception, log an informative message with the step name and error. This way, if one component fails, the orchestrator could either skip to the upload (maybe uploading last successful video) or exit gracefully. Additionally, implement logging to file: instead of just `print()`, use Python’s `logging` module to write logs to `logs/pipeline.log` with timestamps. This log will feed into the monitoring. Include in logs: key decisions (which metric chosen, title generated), lengths of script, any quality gate scores, etc. Also, add a summary at the end: e.g. “[Pipeline] Episode complete: Title…, Duration…, Status: Uploaded/Skipped.” This change will not be directly visible to viewers but is crucial for maintainability. It allows developers to review what happened in each run, and if something goes wrong at 3 AM, the log might save the day. In terms of guardrails: we should also add a simple **OpenAI API usage log** – the OpenAI client can often return token usage in responses; capture that and accumulate a counter of total tokens (and roughly dollars spent) per run and per month. Even just logging “Script GPT tokens: X (~$Y), Research GPT tokens: Z (~$W)” will raise awareness of usage. If we see anomalies (like one script run used 10x tokens due to retries or a loop), that flags a problem. We can set a soft limit (warn if a single episode uses > certain tokens). These defensive coding practices ensure the pipeline doesn’t silently fail or overspend. They directly address reliability and cost concerns by making the system “self-aware” of its health and resource use ([www.yourautomatedlife.com](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=,automate%20my%20YouTube%20content%20creation)).

By implementing these five changes, the repository will immediately become more resilient and intelligent. We’ll have up-to-date AI models giving better output, smarter topic choices using real-world context, no more obvious script errors, improved video audio quality, and clear logs/handling of any hiccups. These are mostly “local” changes to the repo (not requiring large external systems) and lay the groundwork for the next steps in automation.

# 90-Day Automation Roadmap  
To achieve a **fully autonomous channel** in production, we propose a 90-day roadmap split into three phases. Each phase builds on the last, addressing progressively higher-level automation tasks and incorporating improvements:

**Month 1: Stabilize and Upgrade the Pipeline (Days 0-30)**  
- *Implement Quick Wins:* Apply the Top 5 Repo Changes above. Upgrade the LLM model and API usage, add trend-based topic scoring, strengthen the quality gate, integrate background music, and bolster error handling/logging. These should be completed in the first few weeks as they are mostly self-contained code changes.  
- *Testing & Validation:* After these changes, run the pipeline end-to-end multiple times (e.g., simulate weekly episodes) in a staging environment. Verify that each step works with the new changes – the LLM returns valid JSON (thanks to function calling), the trend integration indeed picks appropriate topics, and the quality gate doesn’t produce false positives or negatives. Adjust parameters as needed (for example, tuning the trend weight or QA threshold score). Aim to have a “feature freeze” by day 30 where the pipeline runs smoothly with all new enhancements.  
- *Documentation & Config:* Update the README and any internal docs to reflect the new usage (e.g., mention any new environment variables or dependencies like a Google Trends API key). Ensure that **all API keys** (FRED, OpenAI, YouTube, etc.) are loaded via environment or a secure store – no keys in code. Document how one would set up and run the pipeline now. This is important as we move to more autonomous operation that others (or a server) might run without manual tweaks.

**Month 2: Operational Automation and Scaling (Days 31-60)**  
- *Deploy and Schedule:* Set up the pipeline to run on a reliable host (cloud VM or server) on a schedule. If currently on a personal machine with cron, migrate to a cloud environment or a container orchestration (Docker + cron job, or a scheduled GitHub Action, etc.). This ensures the pipeline can run uninterrupted even if the developer’s machine is off. Use Docker if possible (as noted in backlog) to encapsulate dependencies and ease deployment. By mid-month 2, the channel should be publishing new videos regularly with minimal human input.  
- *Analytics Feedback Integration:* Begin building the analytics feedback loop. In this phase, focus on data collection: use YouTube’s API to automatically retrieve metrics for each video after, say, 48 hours of posting. Store this in a simple database or even a CSV/JSON file. Gather data like views, likes, average view duration, audience retention (if accessible via API or YouTube Studio export), etc. Also track which metric/topic the video was about, and the title used. By day 60, have a script (maybe `scripts/analytics_collector.py`) that can be run via cron daily to update these stats.  
- *Basic Feedback Analysis:* Implement a basic analysis of the collected data. For instance, compute averages and identify outliers: did one video perform 2x better in views? Did one have a particularly high drop-off at 30 seconds? At this point, integrate a simple rule or AI analysis: e.g., if a video underperforms significantly, log a note “Topic X didn’t do well – consider reducing frequency of similar topics.” Conversely, flag successful topics. This doesn’t yet feed back into content creation, but sets the stage for it.  
- *Quality & Compliance Review:* As videos go out, monitor them for any issues we didn’t catch. This month, manually review at least a couple of outputs thoroughly (listen to the voiceover, watch the visuals) to ensure the new automated pieces (like trend logic or QA changes) are functioning as intended in production. This is the safety net before we completely “trust” the system. Also, ensure no YouTube policies are inadvertently violated – e.g., the description and tags are appropriate, content isn’t being flagged. So far so good if our quality gate is working, but a quick human audit early on can save headaches.

**Month 3: Intelligent Refinement and Future-Proofing (Days 61-90)**  
- *Closed-Loop Content Optimization:* Now use the analytics insights to influence the pipeline automatically. For example, integrate with the topic selection: if our data shows “debt-related videos got +30% views on average,” incorporate a bias to pick debt topics slightly more often (provided the data supports it) or spin the angle that way. This could be done by updating the story discovery to reference a simple profile of past performance – essentially a machine learning light touch. Alternatively, use an LLM to generate suggestions: “Given the last 8 videos and their performance, suggest what topic to cover next or how to angle it.” This might yield creative ideas like focusing on a contrast if viewers liked a certain style. Implement these as small adjustments rather than sweeping changes; we still need to ensure the content stays data-driven and factual.  
- *Multi-Metric Episodes & New Formats:* By this time, all single-metric episodes are running smoothly. We can experiment with the content format to keep the channel growing. One idea (from the backlog) is multi-metric “mashup” episodes or special topics. Implement the capability to handle a “theme” that isn’t just one FRED series but a concept (e.g. “Recession Indicators – 5 metrics flashing red”). This may involve writing a new script template or prompt for multiple metrics and adjusting the renderer for multiple charts or a composite visualization. Month 3 is a good time to prototype this because the base pipeline is stable. Start with one special episode in addition to regular ones to test flexibility.  
- *Explore Advanced AI Tools:* Evaluate any new AI offerings that emerged or became stable by 2026. For example, if OpenAI’s *Sora 2* text-to-video is available in beta, test it for generating short B-roll clips or even data-driven animations. Similarly, consider using DALL·E 3 or other image AIs for more dynamic thumbnail images (e.g., generate an image of a piggy bank breaking for a savings rate video, which might attract more clicks than a plain chart). Be cautious and evaluate on a separate branch – only integrate if it genuinely improves content and is reliable. The goal is to keep the pipeline at the cutting edge of what’s possible, giving the channel a competitive advantage.  
- *Final Review & Documentation:* By day 90, conduct a comprehensive review of the system. Compile performance trends from since the improvements – is the channel growing in views/subscribers as expected? Note any failures or human interventions that occurred and address their root causes. Write an internal report or documentation updates covering the entire automated system architecture, so that future maintainers (or a scale-up team) can understand the design. At this point, the YouTube channel should be running with minimal oversight, and the focus can shift to incremental improvements or scaling to multiple channels if desired.

This 90-day roadmap ensures that we don’t just implement features, but also validate and iterate on them. It front-loads the critical fixes (Month 1), establishes a reliable operation and data collection (Month 2), and then uses that data to truly make the system smart (Month 3). By the end of this period, The Money Map would function as a self-driving YouTube channel – choosing timely topics, producing quality videos, learning from feedback, and requiring only occasional check-ins.

# Risks and Guardrails  
Building an autonomous content pipeline comes with risks that must be managed through proper guardrails. Below we outline the key risks and the measures (existing or recommended) to mitigate them, ensuring the system remains reliable, ethical, and effective:

- **Risk: Misinformation or Data Errors** – *Guardrail: Multi-layer Quality Assurance*. The worst-case scenario is the channel publishes a video with incorrect information (e.g. a wrong statistic or misleading claim), which could damage credibility or even violate platform policies. To guard against this, the pipeline should enforce strict data validation and factual checks as described. We’ve enhanced the quality gate to verify numbers against sources and can even require that the research dossier provide citations for any non-obvious facts. An additional guardrail could be to use OpenAI’s content moderation or a custom “fact-check prompt” on the script. For example, ask the LLM: “Are all statements in this script supported by the data provided?” and only proceed if the answer is yes. Moreover, any time the LLM research provides a fact (like “Inflation is at a 40-year high”), we should have it include a reference (source link or report) in the dossier so we can double-check it. By treating accuracy as non-negotiable – even if it means occasionally not uploading that week – we maintain trust. Encoding such rules in the QA gate (e.g. block if script claims a ranking like “highest ever” without proof) ensures consistency ([oleno.ai](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=,on%20accuracy%20and%20invented%20links)).

- **Risk: Low-Quality or Repetitive Content (Algorithm Penalties)** – *Guardrail: Content Diversity & Policy Compliance*. YouTube’s algorithm (and viewers) can penalize channels that churn out repetitive, low-value content (the so-called “cash cow” automation channels often faced demonetization) ([www.opodab.com](https://www.opodab.com/2025/07/youtube-automation-truth-content-system-guide.html#:~:text=Content%20System%20www,million%20dollar%20businesses%20on)). To avoid this, our pipeline must maintain a high quality bar and variety in content. The topic rotation (with trend integration and avoidance of repeats) helps keep content fresh. We should also enforce a rule that not every video is doom-and-gloom – mix in positive or neutral stories to avoid a monotone theme that might turn off viewers. From a policy standpoint, ensure the content doesn’t veer into sensitive areas without care; for instance, economic data can intersect with political topics – the script should stay factual and not insert personal opinions or policy stances that could be contentious. The style guide given to the LLM (urgent but measured, not alarmist) is a good safeguard here. We can expand the guardrail by having the LLM critique: “Does this script contain any sensational or unsupported claims?” and remove them. We should also monitor audience feedback: if comments indicate a particular approach is irritating (“this sounds like clickbait”), adjust the prompts/strategy. Essentially, keep the content valuable – **the AI should be directed to prioritize insight and clarity over hype**. That way, the channel grows organically and stays in good standing with YouTube’s quality standards (no reuse or duplication concerns since everything is original each time).

- **Risk: Over-reliance on External Services** – *Guardrail: Redundancy and Fallbacks*. The pipeline depends on several external APIs (OpenAI, FRED, Luma, YouTube). Any of these could have outages or changes. We must prepare fallback paths. For data: if FRED API fails one week, maybe use a cached copy of last week’s data or an alternate source (e.g. an archived CSV) to at least allow the script to comment “data for X is not updated this week” rather than failing completely. For OpenAI: maintain a fallback script generator (the repo’s older `enhanced_script_writer.py` with templated sections can serve as a backup if the LLM API is down or too expensive). It won’t be as polished, but it ensures continuity. Similarly, if the TTS fails, we could have a backup voice (perhaps a local TTS engine or a different cloud TTS like AWS Polly) – the voice might change slightly, but better than no video. We should implement logic in each AI call wrapper to catch exceptions and either retry on a different service or switch to a simplified path. Redundancy is key. Additionally, monitor API usage and quotas: for example, the YouTube Data API has quotas – if we ever scale to multiple uploads, we need to ensure we don’t exceed them (the FAQ in automation guides highlight managing API quotas ([www.yourautomatedlife.com](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=,automate%20my%20YouTube%20content%20creation))). We might need to request quota increases or rate-limit certain calls (like not pulling analytics too frequently). Logging usage, as mentioned, will help spot potential overuse before it becomes a failure.

- **Risk: Cost Overruns** – *Guardrail: Budget Management*. Automation is great, but it can rack up costs if not monitored (OpenAI API costs, Luma credits, etc.). To control this, implement a simple budget checker. For instance, decide on a monthly OpenAI token budget (e.g. $50). The code can track each call’s cost; store a small file with cumulative usage. If a certain threshold is crossed, the system could send an alert to the team and optionally scale back usage (perhaps switch the research agent to a smaller model or reduce the frequency of videos until the next period). For LLM usage, also consider using fine-tuned or local models for less critical tasks. By 2026, there may be open-source models that, while not as powerful as GPT-5, are sufficient for some tasks (like first-pass proofreading). Using them could cut costs. The repository can incorporate a hybrid approach: use OpenAI for the heavy creative tasks (script writing, complex research), but maybe use a cheaper model or service for straightforward tasks (like formatting the description or summarizing analytics). That said, given we target minimal human involvement, we prefer to keep things automated rather than asking a human “approve additional budget”. So the system should manage itself within limits. Another guardrail: if certain features are expensive (e.g. the AI video generation if billed per second of video), allow an option to disable or downscale them if cost becomes an issue (the orchestrator flags `--no-broll`, `--no-music` already exist, so we can trigger those programmatically if needed).

- **Risk: Technical Glitches & Pipeline Drift** – *Guardrail: Monitoring & Alerts*. Even with testing, things can go wrong in production: e.g., an API response format changes and our parser breaks, or a new data series is added that doesn’t fit our code’s assumptions. To catch these, implement monitoring. As described in the architecture, a simple dashboard or even automated emails can inform maintainers of each run’s outcome. For critical failures (any exception that stops the pipeline), set up an immediate alert (using a service like SendGrid to email an error report or a message to a Slack channel). This way, if the pipeline stops, it won’t go unnoticed for long. Additionally, periodically audit the content being produced – maybe once a quarter, a human should watch a video and skim a script to ensure quality hasn’t degraded. It’s possible that iterative changes or model updates subtly shift the tone or quality over time (“pipeline drift”). Regular check-ins guard against that. In terms of version control, tag stable versions of the pipeline and use a staging environment for big changes once it’s running autonomously – treat it like production code. Finally, maintain backups of important outputs (like the final videos or at least the scripts) in case something needs to be rolled back. Having the last N scripts in a `data/archive` can help if we need to compare and see if the style is changing undesirably.

- **Risk: Ethical and Legal Considerations** – *Guardrail: Policy Compliance*. Although this is a data channel, we must still ensure compliance with YouTube’s and general content rules. For example, avoid using any non-approved data or copyrighted content. Our assets are AI-generated or public domain (FRED data is public), so that’s good. Keep an eye on music licensing if we add tracks – only use royalty-free or properly licensed tracks to avoid copyright strikes. For AI-generated assets, current regulations require no attribution, but if that changes, be ready to comply (e.g. if YouTube or laws start requiring labeling of AI-generated content, we should adapt the description to disclose it). Also consider accessibility: providing captions, as mentioned, or descriptions for visually impaired if possible, to be inclusive. As a financial data channel, there’s a duty to not give financial *advice*. Our scripts seem informational, but as a guardrail, maybe include a brief disclaimer in the description (e.g. “This video is generated from public data for informational purposes”). This was not in the original scope but is a prudent addition in fully automated content to cover liability.

In conclusion, by embedding these guardrails, we can significantly reduce the risks associated with a self-driving content pipeline. The goal is a system that is **self-correcting and failsafe** – if something is off, it catches itself or at least signals for help. The balance is between full automation and controlled automation: we want minimal routine involvement, but we also want the ability to intervene if needed. By treating quality and reliability as “code” – with clear rules and automated checks – we ensure The Money Map channel maintains high standards as it operates autonomously ([oleno.ai](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=Key%20Takeaways%3A)). With these safeguards, the channel can confidently grow, leveraging AI to inform and engage viewers without stepping into the pitfalls that early automated channels faced.
## Sources

- [New tools and features in the Responses API | OpenAI](https://openai.com/index/new-tools-and-features-in-the-responses-api/#:~:text=window%29,more%20contextually%20rich%20and%20relevant)
- [OpenAI opens its speech AI engine to developers](https://www.axios.com/2024/10/01/chatgpt-developers-ai-voice-engine#:~:text=OpenAI%20is%20giving%20other%20developers,order%20for%20400%20chocolate%20covered)
- [2025-07-24 | Sora 2 is coming, but it will have to dazzle viewers to beat Google's Veo 3 model](https://www.techradar.com/computing/artificial-intelligence/sora-2-is-coming-but-it-will-have-to-dazzle-viewers-to-beat-googles-veo-3-model#:~:text=2025,raised%20the%20bar%20by%20incorporating)
- [Ultimate Guide to YouTube Content Automation 2026 - Your Automated Life - AI Automation Tools, Passive Income Systems and Tools](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=platforms%20like%20ChatGPT%2C%20Fliki%2C%20and,enabling%20daily%20uploads%20without%20burnout)
- [Build an Automated QA-Gate: 50+ Quality Checks for](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=,test%2C%20and%20stop%20infinite%20loops)
- [Ultimate Guide to YouTube Content Automation 2026 - Your Automated Life - AI Automation Tools, Passive Income Systems and Tools](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=Once%20your%20uploads%20are%20in,reports%20automatically%20every%2024%20hours)
- [Ultimate Guide to YouTube Content Automation 2026 - Your Automated Life - AI Automation Tools, Passive Income Systems and Tools](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=,automate%20my%20YouTube%20content%20creation)
- [New tools and features in the Responses API | OpenAI](https://openai.com/index/new-tools-and-features-in-the-responses-api/#:~:text=With%20built,Today)
- [2025-03-21 | OpenAI revoluciona el mundo del audio con nuevos modelos de voz y transcripción](https://cincodias.elpais.com/smartlife/lifestyle/2025-03-21/openai-nuevos-modelos-voz-transcripcion.html#:~:text=2025,a%20sus%20predecesores%20Whisper%2C%20destacando)
- [Ultimate Guide to YouTube Content Automation 2026 - Your Automated Life - AI Automation Tools, Passive Income Systems and Tools](https://www.yourautomatedlife.com/ultimate-guide-youtube-content-automation#:~:text=Go%20beyond%20basic%20reports%20by,subscription%20trends%20in%20real%20time)
- [Build an Automated QA-Gate: 50+ Quality Checks for](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=,on%20accuracy%20and%20invented%20links)
- [The Truth About YouTube Automation: A Creator's Guide to Building a Real Content System](https://www.opodab.com/2025/07/youtube-automation-truth-content-system-guide.html#:~:text=Content%20System%20www,million%20dollar%20businesses%20on)
- [Build an Automated QA-Gate: 50+ Quality Checks for](https://oleno.ai/blog/build-an-automated-qa-gate-50-quality-checks-for-content-pipelines/#:~:text=Key%20Takeaways%3A)
