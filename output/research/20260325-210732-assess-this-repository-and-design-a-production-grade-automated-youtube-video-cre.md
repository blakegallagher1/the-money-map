# OpenAI Deep Research Report

        - Generated: 2026-03-25T21:07:32-05:00
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
**The Money Map** is an automated YouTube channel pipeline that already covers data-driven video creation end-to-end – from pulling U.S. Federal Reserve (FRED) data to uploading a finished video. The repository’s current pipeline uses GPT-based scripts, AI text-to-speech voiceovers, programmatic visualizations, AI-generated b-roll, and automated YouTube uploads. This report finds that while the core automation is in place, several components must be added or improved to achieve a **fully autonomous, production-grade** channel with minimal human input. Key gaps include richer topic selection (beyond the fixed economic indicators), deeper trend research and fact-checking, robust script quality control, and closed-loop learning from YouTube analytics. We recommend an upgraded architecture that integrates OpenAI’s latest models and tools for planning, research, and QA, alongside operational safeguards for reliability and cost control. The report outlines immediate code changes (e.g. updating model APIs, adding error handling), next-step automations (e.g. integrating trending topic signals, analytics feedback loops), and future improvements (e.g. multi-lingual content, adaptive thumbnails). These changes will modernize the codebase (replacing legacy patterns and deprecated models) and elevate The Money Map from an automated pipeline to a self-improving, AI-driven YouTube content engine.  

# Current State  
**Automated Pipeline Overview:** The repository already automates essential steps of video production. The current architecture as described in the README links together modules for data ingestion, story selection, script writing, media generation, and publishing. Specifically:  

- **Data Ingestion:** A script (`scripts/data_ingestion.py`) fetches ~34 economic indicators from the FRED API, computing year-over-year changes for each ([huggingface.co](https://huggingface.co/spaces/Agents-MCP-Hackathon/consilium_mcp/commit/ce0bf87f809ea4ed1505b42a4f98c1133f705420#:~:text=Image%20azettl%20commited%20on%20Jun,2)). This provides up-to-date macro data (interest rates, prices, GDP, etc.) on a schedule (weekly cron). The use of a curated indicator list means the content is focused on pre-selected metrics.  

- **Story Discovery:** The pipeline automatically selects a video topic from the data. The `scripts/story_discovery.py` module scores each metric’s “viral potential” – likely using delta values (e.g. large YoY changes) – and picks the top story ([huggingface.co](https://huggingface.co/spaces/Agents-MCP-Hackathon/consilium_mcp/commit/ce0bf87f809ea4ed1505b42a4f98c1133f705420#:~:text=Image%20azettl%20commited%20on%20Jun,2)). This ensures each episode covers a timely or notable economic trend (e.g. *“Mortgage Rates Just Hit 6%”*). However, topic selection is currently limited to the FRED metrics and their changes, without incorporating external trend signals or news context.  

- **LLM Script Writing:** The project has an AI-driven scriptwriter. An older template-based script generator exists (`script_writer.py`), but the v2 pipeline uses `scripts/llm_script_writer.py` to produce ~700-word scripts with a defined narrative structure. This module calls an OpenAI GPT model (configured as `GPT-5.4` in settings) to generate a script in **eight labeled sections** (cold open, hook, the number, chart walk, context, etc.), plus a video **title**, **description with timestamps**, **tags**, and even text prompts for **b-roll clips**. The LLM is prompted with the selected data (current value, YoY change) and a “research dossier” to ensure the script is factual and engaging. The output is structured as JSON which the code parses into the final script and metadata. (Notably, the code currently parses JSON from a text response – an area to improve with function calling to avoid errors.)  

- **Research Dossier Generation:** To enrich the script, the pipeline builds a research dossier via `scripts/topic_research.py` (invoked in `orchestrator.step_research`). This likely uses an OpenAI model (notably `RESEARCH_PROMPT_MODEL = "gpt-5.4"` and a special `DEEP_RESEARCH_MODEL = "o3-deep-research"` in settings) to perform web searches or knowledge retrieval. The dossier includes a summary of the topic, an “angle,” novelty insights, potential “watch-outs” (pitfalls to avoid), and a list of source URLs or facts. In essence, this step gives the LLM factual ammo and context, helping reduce hallucination and adding depth (for example, explaining *why* a metric moved or historical context). The dossier content is passed into the script prompt to guide the narrative.  

- **Voiceover (TTS):** The script is converted to speech through an AI text-to-speech model. The code uses OpenAI’s `gpt-4o-mini-tts` model with a configured voice (“ash”) to generate the narration audio (`scripts/tts_generator.py`). The TTS system is prompted with detailed instructions about tone, pacing, and emphasis to match a professional “data journalist” style. It splits the script into chunks to meet the API’s text length limits, generates audio for each chunk, and concatenates them to a final MP3. This yields a consistent voiceover without human recording. (One minor issue: **GPT-4o** is an older model; we’ll address this in upgrades.)  

- **Data Visualization & Rendering:** The visual core of each video is a data-driven chart. Using Matplotlib, the pipeline renders an animated chart of the primary metric over time. The enhanced renderer (`scripts/enhanced_renderer.py`) produces cinematic effects – e.g. smoothing 5fps animations to 30fps, adding glowing highlights, animated counters, and Ken Burns-style panning. The chart visualization corresponds to the script’s “chart walk” section, showing the trend as the voiceover explains it. This is done programmatically and output as a video clip (e.g. 1920x1080, 30fps). The renderer likely also uses cues from the script (section timings or markers) to align visuals with narration segments.  

- **AI B-roll Generation:** To avoid a purely chart-based video, the pipeline integrates AI-generated B-roll clips. Using the Luma Labs “Dream Machine” API (via `scripts/broll_generator.py`), it takes the LLM-provided scene descriptions and generates short cinematic video clips ([apiframe.ai](https://apiframe.ai/ai-video-generation#:~:text=AI%20Video%20Generation%20API%20Image%3A,No%20complexity%2C%20just%20stunning)) ([docs.lumalabs.ai](https://docs.lumalabs.ai/docs/video-generation#:~:text=Video%20Generation%20,Models)). The script typically provides 3 prompts (for the hook, context, and insight sections). For example, a prompt might be *“a busy trading floor with falling stock tickers, cinematic, 4K”* to illustrate a market panic. The orchestrator calls Luma’s API for each prompt and retrieves a video file (each ~4 seconds). These clips are saved and later interleaved with the chart animation to create a more engaging visual narrative. (This is a cutting-edge feature – effectively using generative video as a substitute for stock footage – but it’s also a point of complexity and cost, addressed later.)  

- **Final Assembly:** The `scripts/final_assembly.py` module merges everything using FFmpeg. It takes the core chart animation, inserts the AI B-roll clips at the appropriate timestamps (likely aligning with the [HOOK], [CONTEXT], [INSIGHT] sections in the script), and mixes in the voiceover audio (and background music, if enabled). The result is a single cohesive MP4 file. The assembly step ensures all timing is synced – e.g. pausing the chart animation while a B-roll clip plays full-screen, then returning to the chart. It also likely normalizes audio levels (voice vs. music). By automating FFmpeg composition, the pipeline eliminates manual video editing.  

- **Thumbnail Generation:** The pipeline creates a YouTube thumbnail image via code (`scripts/enhanced_thumbnail.py`). Thumbnails are designed with a “high CTR” style – bold text and graphics highlighting the key stat or provocative title. Currently, Matplotlib is used to generate a 1280x720 image, using the set color palette and possibly including the chart or an illustrative graphic. This is less advanced than using an AI image generator, but it ensures consistency with the video’s data theme. (For instance, Episode 1’s thumbnail shows “3.6%” with a down arrow, hinting at a collapsing savings rate.) Thumbnails are saved as PNG for upload.  

- **YouTube Upload & Scheduling:** Finally, the `scripts/youtube_uploader.py` (and a newer `youtube_api_uploader.py`) handle uploading the video and thumbnail to YouTube via the Data API v3. OAuth2 credentials are stored so the process is headless after first setup. Metadata from the script (title, description, tags) is applied. The pipeline can set the video privacy to “private” or schedule publishing in the future using `publishAt` (configurable via `YOUTUBE_DEFAULT_PRIVACY` and offset days in settings). This means once the pipeline is run, the video can be automatically uploaded and even scheduled without human intervention. Combined with a cron job triggering the script weekly, the channel can consistently post content on a schedule (e.g. every Monday 8AM CST as noted in the README).  

- **Orchestration & Quality Control:** The master orchestrator (`scripts/orchestrator.py`) ties all steps together, with logging at each step. It supports flags like `--no-upload` or `--no-broll` for flexibility. Critically, it includes a **Quality Gate** step (`scripts/quality_gate.py`) before final upload. The quality gate examines the produced script and assets to enforce certain standards. For example, it checks the episode’s title against recent titles (via an `episode_tracker` module) to avoid repeating topics too soon. It may also run an LLM-based check on the script for coherence, length, or adherence to the section structure. If the quality gate fails (low score or a rule triggered), the process can halt or require manual review. This is an important safety net, but details on its criteria are limited. We do see that **previous episode titles** are considered to penalize redundancy, and a report is saved for transparency.  

In summary, the **current system automates a full video production workflow**: data → idea → script → assets → editing → upload. It’s a sophisticated pipeline using AI at multiple points to minimize human work. **Manual involvement is currently minimal**, mainly in: providing API keys, occasionally reviewing quality reports, and maintaining the code/config. However, to become a “genuinely autonomous” YouTube channel, the system needs to broaden how it chooses and researches content, ensure higher content quality consistently, and implement feedback mechanisms to continuously improve with minimal oversight.  

# Gaps To Full Automation  
Despite the impressive automation, several gaps separate the current pipeline from a truly autonomous, self-improving production system:  

- **Topic Selection Limited to Data Changes:** The channel only covers stories that emerge from the fixed set of 34 FRED indicators. This neglects many potential topics that might be trending with audiences. For example, if a major economic event occurs (say, *“Fed introduces a new policy”* or *“Banking crisis unfolds”*), it may not be captured by a YoY change in the preset metrics. A fully autonomous channel should proactively identify **what viewers care about**, not just what data changed. This means integrating external trend signals – e.g. Google Trends, financial news, or YouTube trends in the finance niche – not just internal data signals. By relying solely on numeric thresholds, the channel might miss high-interest topics that don’t show up as outliers in FRED data. In other words, it lacks an AI “content strategist” to ensure relevance. Industry experts suggest using tools or AI to identify **high-potential keywords and trending topics** for YouTube content ([www.upgrowth.in](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=,upload%20via%20Zapier%20or%20TubeBuddy)). The absence of such a system is a key gap – currently, if no FRED metric swings wildly, the pipeline might still choose a relatively mundane topic that isn’t actually in the public discourse.  

- **Shallow Context & Trend Research:** The pipeline’s **research dossier** step is a great idea, but we need to assess its depth and recency. The dossier likely relies on an LLM (possibly with web access) to gather background info and facts. If it’s using a dated model or limited sources, the script might miss crucial context. For example, a video about a low savings rate might lack mentioning recent stimulus ending or credit card debt highs if the research didn’t surface those. A fully autonomous system needs robust “research intelligence” to contextualize the raw data. This means ensuring the LLM can retrieve up-to-date information (e.g. via a web search tool or a vector database of recent news) and that it cites sources or at least provides kernels of facts the script can trust. Right now, the dossier format is largely free-form text in JSON (summary, angle, etc.), which the script uses indirectly. There may be a missed opportunity to directly inject cited facts or even short quotes from sources into the script for credibility. Additionally, it’s unclear if the research step cross-verifies the data – e.g. checking if the FRED values are historically notable or just short-term noise. In short, the research component could be more **data-driven and source-grounded**. Without stronger trend research, the risk is the script sticks to general knowledge the LLM already has (which could be outdated or lack nuance), rather than timely insights.  

- **Script Quality and Fact-Checking:** While the LLM-written scripts are coherent and follow a template, relying on a single-pass GPT generation has risks. One risk is **factual accuracy** – the LLM might fabricate a statistic or misinterpret the data (though the prompt tries to anchor it with numbers). Another risk is **narrative quality** – e.g. the script might be repetitive, too shallow, or not sufficiently engaging. The current quality gate likely checks length and uniqueness, but it may not catch subtle issues like an incorrect historical claim or a section that doesn’t flow well. A production-grade system should have an automated script review. For example, an LLM-based fact-checking pass could verify all numerical claims against the input data or public data sources. Additionally, style and tone compliance can be measured – does the script match the “Bloomberg TV meets YouTuber” voice consistently? Right now, if the LLM veers off-script (e.g. adding an emoji or making an overly sensational claim), it’s unclear if the pipeline would catch it. Improving script QA is essential for trust and brand consistency, especially with minimal human oversight.  

- **Asset Generation Constraints:** The pipeline cleverly uses AI for visuals and sound, but there are practical challenges. The **Luma AI Dream Machine** for b-roll is cutting-edge and may be **slow or costly for regular use**. If the channel scales up to more frequent videos, generating multiple 4-second clips per video could become a bottleneck (both in time and API credits). Additionally, the visual quality or relevance of AI clips can vary – sometimes the clip might not perfectly illustrate the intended concept, and without human review, some clips might feel off-topic or uncanny. The thumbnail generation is currently static (matplotlib-based) and could be missing the human touch of creativity. High performing YouTube thumbnails often include human faces or compelling imagery, not just data graphics. An autonomous system might consider using generative image models (like DALL·E or Midjourney API) to create more eye-catching thumbnail elements (e.g. an illustration of a piggy bank for a savings rate video). Also, **background music** integration is currently simplistic – the backlog notes adding a library of music tracks. Without diverse music, videos might feel monotonous or get flagged by YouTube’s ContentID if the same track is overused. Ensuring variety and rights-safe music is another piece to address. In summary, asset generation works but needs to be **scaled and diversified** to keep content visually engaging long-term.  

- **Edit QA and Video Validation:** Once the video is assembled, there’s minimal verification that the final product is glitch-free. Issues that could occur in automation include: audio-sync problems, sections of silence or black frames if an asset failed to generate, or incorrect durations (e.g. the voiceover is 4:30 but the video runs 4:00 because of a stitching error). A robust system might include a final automated QA pass on the video file – for example, using `ffprobe` to check that audio and video streams lengths match, or even using a computer vision model to ensure there are no blank frames. Currently, aside from the quality_gate (which is more content-focused), there’s no mention of a post-assembly validation. This is a gap, as a truly autonomous pipeline should catch rendering issues automatically.  

- **Upload Metadata & SEO Optimization:** The LLM provides title, description, and tags, which is a great start for metadata. However, it may not be *optimally* tuned for YouTube SEO. The LLM might miss trending keywords that could boost discoverability if it isn’t aware of current search trends. For example, a video on mortgage rates might benefit from tags like “real estate 2026” or currently trending related terms if interest rates are in the news. Right now, metadata is only as good as the prompt and the LLM’s training data. A more autonomous approach would integrate keyword research – e.g., using the YouTube API or third-party tools to find high-search terms to include. Experts note that content visibility on YouTube “depends as much on metadata as on content” ([www.upgrowth.in](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=YouTube%20has%20evolved%20into%20a,The%20challenge)), and that manual SEO optimization per video is time-consuming. The pipeline could automate this by querying for related keywords or using OpenAI to analyze the titles of currently popular videos on similar topics and adjust its own title/description accordingly. This kind of adaptive metadata optimization is not implemented yet, representing a gap in achieving maximum reach without human intervention.  

- **Scheduling & Frequency Adaptation:** The pipeline is set to weekly output via cron. This is fine, but a truly autonomous channel might adapt frequency based on audience demand or content availability. For instance, if multiple metrics are flashing interesting signals, the system could consider producing two videos in a week (one for each story). Conversely, if nothing noteworthy happened, it might skip a week or do a more evergreen explainer to keep the audience engaged. Right now the schedule is rigid. There’s no dynamic decision-making on *when* to publish beyond the fixed cron. Also, scheduling is configured as a static offset (e.g., publish X days after upload). A smarter scheduler could pick the optimal hour based on analytics (when the channel’s audience is usually online) or coordinate with other content (if there were multiple channels or platforms). This kind of nuance is not yet in place.  

- **Analytics Feedback Loop:** Perhaps the biggest missing piece of autonomy is *learning from results*. The system currently does not gather any feedback from how videos perform on YouTube. An ideal autonomous channel would monitor its own analytics – views, watch time, click-through rate (CTR) of thumbnails, audience retention graphs, and even comments – to understand what’s working and what’s not. For example, if videos about consumer debt consistently outperform videos about industrial metrics, the system should notice that trend and adjust its story scoring to favor consumer-focused topics. Or if the audience dips at a certain part of the video consistently, maybe the scripts need to be punchier or shorter. None of this is presently happening. There’s an opportunity to use the YouTube Analytics API and even GPT-driven analysis to close the loop. In fact, some have started using GPT-4 to generate insights from YouTube data automatically ([www.narrative.bi](https://www.narrative.bi/chatgpt/youtube#:~:text=GPT%20Insights%20for%20Youtube%20ChatGPT,Easily%20upload%20your)). Without this feedback loop, the channel is running open-loop – it will continue making videos, but won’t get smarter or correct course if the content misses the mark. In a production-grade scenario, this kind of self-correction is key to long-term success.  

- **Cost & Reliability Guardrails:** The pipeline relies on multiple external APIs (OpenAI, Luma, YouTube, FRED). There are costs associated with these (OpenAI API usage, Luma video generation credits, etc.) and potential failure points (rate limits, service downtime). Currently, there are only basic guardrails. For instance, if the voiceover MP3 was generated in the last 2 hours, it skips regenerating it – a simple cache to save cost if you rerun quickly. Also, the `todo.md` mentions adding retry logic for FRED API calls. But beyond that, there’s no global monitoring of how much the pipeline is spending or any dynamic fallback for cost saving. For example, if OpenAI’s GPT-5.4 is expensive or hits a quota, the system doesn’t automatically switch to a cheaper model or reduce the script length to conserve tokens. Similarly, if Luma API fails to return a clip (which might happen if their service is busy), the current code might just return `None` and proceed, potentially leading to a missing clip in the final video. A robust system would catch that and perhaps fill the gap with a still image or repeat a previous clip, rather than produce a glitch. Another aspect is **model deprecation**: the config is using model names like GPT-5.4 and GPT-4o which could be deprecated soon ([www.pcgamer.com](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=On%20February%2013%2C%202026%2C%20OpenAI,mini)). Without guardrails, a sudden model removal by the provider could break the pipeline. In a human-run scenario, someone would update the code promptly, but in a minimal-human setup, this is a risk to plan for (perhaps by always using an alias or hitting a a proxy that can redirect to available models). Overall, the pipeline would benefit from more resilience – both in handling errors/exceptions gracefully and in managing costs (e.g., not exceeding a monthly budget by scaling back non-critical steps when needed).  

In summary, to reach full autonomy, the channel needs **smarter decision-making (what to cover and when), better information grounding, continuous quality oversight, and adaptive learning**. Additionally, engineering improvements for reliability and maintainability (tests, monitoring, cost control) are required so that the system can run with minimal manual fixes or tweaks.  

# Recommended Architecture  
To transform The Money Map into a truly autonomous video creator, we propose an enhanced architecture with new components for intelligence and feedback. The core idea is to maintain the current pipeline flow (which is effective) but augment it with systems that **plan, learn, and guardrail** the content creation process. Below is the high-level architecture with key components and data flows outlined:

 ([tubechef.ai](https://tubechef.ai/blog/chatgpt-ai-video-tools-complete-workflow#:~:text=,10%20Videos%20in%20One%20Day))**Pipeline with Intelligent Automation:**  
```
Trend Monitor & Planner ─┬─> Data Ingestion (FRED + others) ──> Story Discovery ──> Research & Dossier 
                         |                                       ↓ 
External Trend Signals ──┘                              Script Writing (GPT) ──> Script QA (GPT checks)
                                                            ↓
                    YouTube Analytics <── Feedback Loop ──<  (Script Approved) 
                                                            ↓
         FFmpeg Assembly  <-- Visual Render (Chart + AI B-roll) + Voiceover + Music 
                    ↓ 
      Thumbnail Generation (AI-assisted) 
                    ↓ 
         YouTube Upload & Scheduling (API)
                    ↓ 
           Post-Publish Monitor (Analytics & Comments)
```

**1. Trend Monitor & Topic Planner:** Add an upfront component that runs before Data Ingestion/Story Discovery. This module will use external data to inform what topic to cover. It can pull **Google Trends**, Twitter finance trending topics, or YouTube trending videos in the finance category. It could also utilize tools like VidIQ or simply the YouTube API to see popular search terms related to economics ([www.upgrowth.in](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=,upload%20via%20Zapier%20or%20TubeBuddy)). An OpenAI model can summarize these trend signals and potentially generate a list of candidate topics or angles (for example, “Many people are searching for ‘inflation 2026 forecast’ this week”). These external insights feed into **Story Discovery**: the system can cross-check if any of the trending topics align with the available data. If yes, those get a boost in the scoring. If not, perhaps the pipeline can step slightly outside the strict FRED data list (for instance, if “gold prices” trend and not in FRED, the planner might call a different API or at least mention it in context). Essentially, this component ensures we’re covering stories that have an *audience interest signal*, not just those that are statistically interesting. In practice, this could be implemented as a small service or script that the orchestrator calls at Step 1, which returns either an override “priority topic” or adjusts the scores for story discovery.  

**2. Data Ingestion (Expanded):** Keep the existing FRED ingestion, but consider integrating more data sources (as hinted by placeholders for Census and BLS API in settings). A production system might pull in data from multiple APIs or a data warehouse. For instance, if the trend monitor flags something like “unemployment benefits spike,” but FRED doesn’t capture it well, the system could fetch data from the Department of Labor, etc. Modularizing data ingestion to accept a list of series or even on-the-fly series would make the pipeline more flexible. This could be orchestrated by the planner (which could tell data module: “also fetch this series ID for this episode”). All ingested data goes into a unified structure (like the current `latest_data.json`).  

**3. Story Discovery with Context:** The story selection logic can be enhanced by incorporating context from the Trend Monitor. Instead of purely ranking by YoY change, we introduce factors like “search interest” or “news relevance.” Concretely, `build_story_package` in `story_discovery.py` can be updated to take additional inputs (e.g., trending keywords, or penalize topics covered very recently via episode_tracker). The output remains a `story_pkg` with primary metric and some related metrics, but now more attuned to what people might want to watch. This step might also classify what *type* of story template to use (surge vs collapse vs milestone, etc., which the code already has). With more dynamic input, the discovery becomes both data-driven and audience-driven – a crucial balance for autonomy.  

**4. Research & Dossier (Intelligent Agent):** Upgrade the research step to use an **agentic LLM** with tools (if not already doing so). OpenAI’s functions or a framework like LangChain could enable the LLM to perform live web searches, lookup data, and return a fact-rich dossier. For instance, given the selected topic, the agent could: search news articles about that metric, retrieve 2-3 pertinent facts or quotes (with references), check Wikipedia or official reports for historical context, etc. The result would be a dossier that isn’t just a generic summary, but includes **specific, verifiable details** (including maybe URLs). The script writer can then be prompted to **utilize those specifics** (“According to the Bureau of Labor Statistics, ...”). This can greatly reduce hallucination and increase the informational value of the video. The dossier format can be extended to include a “fact list” or “reference notes” that the script must incorporate. Importantly, this agent should have access to *current* data (maybe via a news API or search engine) so that even if GPT’s base knowledge is outdated on a topic, it can fetch the latest. This aligns with emerging practices of using LLMs for research assistance in content creation ([www.upgrowth.in](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=,upload%20via%20Zapier%20or%20TubeBuddy)) ([www.narrative.bi](https://www.narrative.bi/chatgpt/youtube#:~:text=GPT%20Insights%20for%20Youtube%20ChatGPT,Easily%20upload%20your)).  

**5. Script Writing (GPT-5.2+ with Function Calling):** Keep the structured prompting approach (the eight-section format is working well), but update the model and method. The config should use a currently supported model – e.g. `gpt-5.2` or newer – since GPT-5.4 in config might be a placeholder or an unreleased iteration. Notably, OpenAI is retiring older models in favor of 5.2 by 2026 ([www.pcgamer.com](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=On%20February%2013%2C%202026%2C%20OpenAI,mini)), so switching to `GPT-5.2` ensures continuity. Additionally, leverage the latest API features: we can use the function calling or “OpenAI function” capability to have the API directly return JSON objects. Currently, `llm_script_writer.py` manually parses JSON from the model’s text output. By defining the output schema as a function (with fields like title, description, script, etc. as properties), we can let the model structure the output, reducing risk of formatting errors. The few-shot example can remain to help style, but ensure the prompt clearly instructs the model not to deviate from JSON (the repository already emphasizes this). We should also adjust the prompt to explicitly ask the model to utilize research facts: e.g. “Incorporate at least two specific statistics or facts from the dossier, and avoid any claim not supported by the data or dossier.” This will further improve factual accuracy. The script writer should still produce the same JSON fields (for backward compatibility with downstream steps), just with better quality content.  

**6. Script Quality Assurance (QA) Pass:** Insert a new sub-step after script generation and before voiceover. This QA uses an LLM to double-check the script. For example, a prompt to a smaller/cheaper model (or even the same model if needed) could be: “Review the following script for The Money Map. Ensure it has 8 sections with markers, is under ~750 words, contains no policy-violating language, and that all numerical claims match the provided data. List any issues or confirm it’s good.” The model’s response can be parsed to decide if the script is okay. Specifically, it can check that the script has [COLD_OPEN] through [CLOSE] all present, that each section isn’t empty, etc. It can also be tasked with checking against the input data (we can feed in the primary metric’s actual values for comparison). If any factual discrepancies or format issues are found, the system could either auto-correct (if trivial) or log a failure for a human to review. This QA step serves as a safety net so that the final script doesn’t have obvious flaws that slipped past the initial generation. Essentially, it’s an LLM “proofreader” and fact-checker. This can be implemented in `quality_gate.py` or as a new `script_review.py` module.  

**7. Parallelized Media Generation:** To improve efficiency, the architecture can generate certain assets in parallel once the script is finalized. For example, voiceover generation, chart rendering, and b-roll generation do not depend on each other and can run concurrently. A production system might use background threads or async calls to handle this. Currently, the orchestrator does them sequentially (voiceover then music then render then assembly). We can trigger the chart animation rendering and the b-roll API calls at roughly the same time as the TTS generation, then wait for all to complete. This saves total pipeline time, which is especially important if we scale up video frequency or length. It also better utilizes computational resources (while waiting for the TTS API, the CPU/GPU can be rendering frames, etc.). The orchestrator would need adjustment to manage parallel tasks – perhaps using Python’s `asyncio` or simply threading.  

**8. Enhanced Visuals & Thumbnail Creation:** In the new architecture, the **Visual Renderer** remains largely the same for the chart (since that’s specialized). But we can add an **AI Image generation** step for thumbnails and possibly supplemental visuals. For instance, after script is ready, we could prompt an image model for a thumbnail background: *“an illustrative image of [topic] – e.g. shrinking piggy bank for savings rate – in a cinematic style.”* This image can then be composited with the text and graphics using PIL or OpenCV to produce a thumbnail that’s more eye-catching than a pure matplotlib graph. This could be an optional enhancement (if the image API fails or is too costly, fall back to the existing method). Tools like DALL·E or Stability API can be integrated for this. Additionally, for B-roll, if video generation is too slow, an alternative could be to generate a *still image* and apply Ken Burns effect for a few seconds as pseudo-B-roll. This would be faster and less expensive, while still providing visual variety. The architecture can have a toggle: if Luma API is available and within budget, use it; otherwise, use image-based B-roll (essentially slide dissolves or animated pan on a static AI image).  

**9. Assembly & Editing:** This component remains FFmpeg-based but with more dynamic control. For example, incorporate the ability to adjust segment lengths based on script timing (since now scripts might vary in length). The assembly could be guided by a **timeline** derived from the script JSON. We can calculate, for instance, that [HOOK] is 10 seconds (based on TTS audio length for that section) and ensure a b-roll clip (if available) of ~4s covers part of it. As part of assembly, include an automatic fail-safe: if any expected asset is missing (e.g., a b-roll clip didn’t generate), the assembler can insert a filler (like extend the previous scene or use a backup stock video clip) rather than produce a broken sequence. This way the final video is always complete.  

**10. YouTube Upload & Scheduling:** Continue using the YouTube API for upload, but integrate it with a **content calendar** notion. The architecture can include a simple database or even Google Sheet listing planned videos and their intended publish dates (some workflow from upGrowth suggests using Sheets + Zapier for scheduling ([www.upgrowth.in](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=,upload%20via%20Zapier%20or%20TubeBuddy))). We can have the pipeline write back the video ID and publish date to a log (for tracking). Additionally, incorporate a check after upload: the `_wait_for_processing` in `youtube_api_uploader.py` polls until YouTube has finished processing the video. Once done, we can automatically set the thumbnail (the code already attempts this) and even post a comment or description update if needed (some channels post a pinned comment with key info – could automate that with the LLM too).  

**11. Post-Publish Monitoring:** This is a new feedback component. The system should periodically (say daily or weekly) query the YouTube Analytics API for stats on recent videos. Data like views, impressions, CTR, average view duration, likes, and comments can be collected. Then an OpenAI model can analyze these metrics to provide insights – e.g., “Video A had a high view duration, indicating interest in topic X, whereas Video B’s thumbnail had low CTR, perhaps the title wasn’t compelling.” This analysis could be output to a log or even an email/slack for the human overseer. More autonomously, the system can feed certain metrics back into the **Trend Planner** or **Story Discovery**: for example, boost topics similar to high-performing ones, or avoid ones with poor retention. Over time, this creates a closed-loop learning where the channel’s content strategy evolves based on what the audience responds to ([www.narrative.bi](https://www.narrative.bi/chatgpt/youtube#:~:text=GPT%20Insights%20for%20Youtube%20ChatGPT,Easily%20upload%20your)). Even comment analysis can be done (using GPT to summarize audience feedback sentiment or frequently asked questions, which could inspire future topics).  

**12. System Monitoring & Guardrails:** Architecturally, we add a monitoring layer that tracks runtime, errors, and costs. Each module can log its API usage (e.g., how many tokens the LLM used, how many seconds of TTS generated, etc.). A simple dashboard or report could be generated each run. If certain thresholds are exceeded (say the video took too long to generate or OpenAI billing this month is above X), the system could alert maintainers or adjust settings (like use shorter scripts or disable b-roll temporarily). For reliability, critical failures should trigger fallback behaviors: e.g., if the script LLM fails twice (API error), call the older template script generator as a backup so the episode still gets made (the code already has a fallback to `enhanced_script_writer` if LLM fails). Similarly, if TTS fails, the system might use a secondary TTS service or at least print the script to console so a human could voice it if needed. These guardrails ensure the pipeline doesn’t silently fail – it either recovers or loudly notifies.  

In this recommended architecture, data and control flow together to yield an intelligent content factory. **Data flows** from sources (FRED, trends) into story selection, then into script and media creation, then out to YouTube. **Feedback flows** from YouTube (performance data) back into the planning stage, closing the loop. Throughout, OpenAI’s models are deployed not just for content generation, but for planning, checking, and learning – truly leveraging AI at every stage. The result will be a system that can pick compelling topics, tell accurate and engaging stories, visually illustrate them, and learn from each video to refine its strategy – all with minimal human input.  

# Top 5 Repo Changes (Immediate)  
Below are the five highest-leverage changes to implement **right now** within the repository, focusing on quick wins and upgrades that align with the existing codebase. These are focused on OpenAI-powered enhancements and critical fixes:

**1. Upgrade Model Usage and API Patterns** – *Modernize LLM integration for scriptwriting and research.*  
  - **What:** Update the OpenAI API calls to use the latest stable models and features. In `config/settings.py`, replace `SCRIPT_LLM_MODEL = "gpt-5.4"` with the current model (e.g., `"gpt-5.2"` or whatever OpenAI’s latest GPT model is named). Similarly, update `TTS_MODEL` if `gpt-4o-mini-tts` is deprecated – either use its successor or another service.  
  - **Why:** OpenAI is retiring older model endpoints like GPT-4.0/4.1 and even GPT-5.0 in favor of newer versions ([www.pcgamer.com](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=On%20February%2013%2C%202026%2C%20OpenAI,mini)). Using a deprecated model will soon break the pipeline, so this is urgent. Additionally, newer models often have improved quality or lower cost.  
  - **How:** Modify the settings and any hard-coded model names in the code (e.g., `OpenAI(api_key).responses.create(model="gpt-5.4", ...)` should reflect the new model name). Test the script generation after the switch. Also, adjust prompts to leverage new features: for example, use the `openai.ChatCompletion.create` with function calling to enforce JSON output rather than relying on manual JSON extraction in `llm_script_writer.py`. This means defining a function schema equivalent to the OUTPUT_SCHEMA and calling the model with `functions=[...schema...]` and `function_call={"name": ...}` so the model returns structured data. The change will make the script generation more robust to formatting issues. Ensure to update any error handling around JSON parsing (it may become simpler if the model reliably returns parsed objects).  

**2. Integrate Trending Topic Signals into Story Discovery** – *Make topic selection smarter by adding context from outside the static data.*  
  - **What:** Modify `scripts/story_discovery.py` (specifically the `build_story_package` function) to factor in external trend signals when scoring metrics. This could be as simple as a placeholder where an external “interest score” is added to the metric’s viral score. For instance, if you have a list of trending keywords (fetched via an API or even manually configured) and a metric’s name or tags match one, boost its score.  
  - **Why:** Ensuring the chosen story aligns with viewer interest will improve discoverability ([www.upgrowth.in](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=,upload%20via%20Zapier%20or%20TubeBuddy)). Right now a metric could spike in percentage terms but not matter to lay audiences, which could hurt video performance. Tying story selection to real-world interest (e.g., via Google Trends or social media mentions count) makes the content more relevant and likely to succeed.  
  - **How:** As an immediate solution, you can use OpenAI’s GPT in a quick step to get relevance: feed the list of metric names and a brief summary of recent economic news to a prompt, asking which metric seems most relevant. However, a simpler method: maintain a JSON of “hot topics” (e.g., {“inflation”:5, “mortgage”:3, ...}) updated periodically. Then in `build_story_package`, for each metric, if its name or tags contain a hot keyword, do `score += trend_boost`. Use the existing `tags` field for metrics (the config’s FRED_SERIES might include tags like ["housing", "prices"] etc.). Implementation can be done in a few lines, and the data for trend boost can come from a manual list initially. This is low-hanging fruit that can later be replaced by an automated trend fetcher.  

**3. Enhance the Quality Gate with LLM-based Checks** – *Use an AI reviewer to enforce script quality before proceeding to production.*  
  - **What:** Improve `scripts/quality_gate.py` to perform deeper inspection of the script and metadata. We can call OpenAI (a smaller model like GPT-4 or 3.5 for cost) to review the script JSON. The LLM can check for things like: Are all required sections present and well-developed? Does the script contain any phrases that could be sensitive or misleading? Are the title and description likely to attract viewers (good curiosity gap, no clickbait claims that aren’t addressed)? It can also double-check numbers against the input data (provided we include the data in the prompt).  
  - **Why:** This adds a layer of confidence that the automated content meets quality standards and avoids obvious pitfalls. Human creators often do a review pass – here we replicate that with AI. Given minimal human involvement, an AI second-opinion is valuable for catching issues. This addresses the risk of hallucinations or format errors in the script automatically.  
  - **How:** In `quality_gate.py`, after existing checks (like comparing titles), insert an OpenAI call. For example, compose a prompt: “You are a YouTube content editor. You will be given a proposed video script and its metadata. Analyze it for quality, factual accuracy (given the data), engagement, and adherence to format. Answer with a JSON: {passed: bool, issues: [list of strings]}.” Provide the model the script, title, description, data points, and maybe the dossier summary for context. Parse the output. If `passed` is false or certain severe issues are listed, have the quality gate fail (or mark as needs human review). You might use the function calling approach here too for a structured result. This change primarily involves adding this prompt and logic to consume its result. To keep things efficient, you could use a smaller model (maybe `gpt-3.5-turbo` if available and sufficiently accurate) to reduce cost, since it’s just a check.  

**4. Add Robust Error Handling and Retries** – *Make the pipeline more fault-tolerant to external API hiccups.*  
  - **What:** Implement retry logic and fallback options around key external calls. For instance, in `scripts/data_ingestion.py`, wrap the FRED API fetch in a try-except and retry a couple of times with exponential backoff if it fails (network issues or rate limit). Similarly, in `scripts/broll_generator.py`, if Luma API call returns an error or times out, catch it and return a placeholder (instead of None perhaps create a short black video or skip gracefully). Also, in `scripts/tts_generator.py`, handle the case where OpenAI’s speech API fails mid-way – maybe break the script into smaller parts to retry the failed chunk or use a different voice as backup.  
  - **Why:** This was noted in the backlog (e.g., “Add retry/backoff logic to FRED API calls”), showing it’s a known need. Unhandled exceptions can crash the whole pipeline, requiring a human to rerun it. For production, the system should recover by itself whenever possible. By retrying or degrading functionality (e.g., skip b-roll if service is down), the pipeline can complete the video without manual intervention, perhaps sacrificing some quality but not failing entirely.  
  - **How:** Use Python’s `retry` patterns or simply loops with `time.sleep()`. For example, in `FREDClient.fetch_all()`, if a request fails, log a warning and try again up to 3 times ([www.linkedin.com](https://www.linkedin.com/posts/faris-elshammouty_python-ai-automation-activity-7428891336994488321-AnAZ#:~:text=Faris%20Elshammouty%202w%20I%20built,You%20give%20it%20a%20topic)). For the b-roll, you might implement `generate_broll` to attempt each prompt twice, and if still failing, produce a 4-second static image video (you can generate a solid color background and some text as a last resort). Also ensure the orchestrator doesn’t crash if one step returns an error; instead, handle the error by skipping that step’s output (e.g., if voiceover fails and can’t recover, perhaps halt before upload with a clear error). Logging these incidents to a file or console is important for later debugging.  

**5. Update YouTube Upload Workflow for Automation** – *Make uploads smoother and reduce manual token issues.*  
  - **What:** A few tweaks to the YouTube uploader can enhance automation. First, ensure the OAuth token refresh logic works without user intervention. The current code tries refresh, but in case of failure, it starts a local server for new auth – which is not viable in a headless production run. We should handle token expiry gracefully by catching the exception and perhaps sending an alert to refresh credentials out-of-band, rather than hanging waiting for user auth. Second, automatically set the video’s status after upload according to a schedule. If using `YOUTUBE_PUBLISH_OFFSET_DAYS`, verify that the logic correctly sets the `publishAt` time. If not already, consider adding a default scheduling e.g. every Monday at 8am (the README mentioned that schedule externally). Finally, add some post-upload checks: e.g., verify the video is in the channel (by querying video status) and log the YouTube URL.  
  - **Why:** These changes ensure that the final step – getting the video live – doesn’t become a bottleneck. In a minimal-human setup, we cannot afford the uploader to pause for OAuth input unexpectedly. Also, proper scheduling means the channel stays consistent without manual tweaking.  
  - **How:** In `youtube_api_uploader.py`, inspect the `_get_authenticated_service()` function. It already tries refresh; we can improve it by adding a headless OAuth flow or at least a clear error if token is expired and no refresh token is present (e.g., instruct the maintainer to re-authorize via a script, but not just hanging). For scheduling, if not done, compute `publishAt = now + offset_days` in RFC3339 format and set privacyStatus to “private” with that publish time (the code seems to do this based on `YOUTUBE_PUBLISH_OFFSET_DAYS`). Test this with a dry-run (perhaps with a dummy channel) to ensure scheduling works. Additionally, extend `_wait_for_processing` to catch if processing takes too long or fails, and retry upload if needed (rare but possible). Logging the video URL on success is a nice touch (so it can be easily reviewed).  

By implementing these five changes, the repository will immediately become more robust, current, and aligned with best practices. The model upgrades (Change #1) and QA improvements (Change #3) directly improve content quality and future-proof the AI usage. Trend integration (#2) sets the stage for better topic relevance with minimal effort. Error handling (#4) and upload tweaks (#5) ensure the automation doesn’t break easily in production. All these are relatively contained changes that fit into the existing code structure without a complete rewrite – making them high ROI for the next development sprint.  

# 90-Day Automation Roadmap  
To achieve the vision of a self-running, self-improving YouTube channel, we outline a 90-day roadmap. This plan is divided into three 30-day phases, each with specific goals and deliverables. The focus is on iterative development: solidifying the foundation, then adding intelligence, and finally refining and scaling.  

**Day 0-30: Stabilize and Upgrade the Foundation**  
- *Implement Immediate Code Changes:* Begin by applying the **Top 5 Repo Changes** above. Update the model APIs (switch to GPT-5.2 or latest, update TTS voice if needed) and test the pipeline end-to-end to ensure nothing breaks with the new models. Introduce the improved quality gate LLM check and ensure it passes for recent scripts or identifies any real issues to fix in prompts. Add the error-handling improvements (FRED retries, etc.) and deliberately simulate failures (e.g. disconnect internet for a test run to see if retries work) to validate resiliency.  
- *Testing and CI:* Set up a basic test suite to prevent regressions. For example, write unit tests for `story_discovery` (feed it sample data, ensure it picks expected top story), and for `llm_script_writer` (maybe mock the OpenAI response and test JSON parsing logic). While full integration tests are hard without API calls, you can use dry-run mode with mocks. Additionally, implement continuous integration (GitHub Actions or similar) to run tests and perhaps linting on each commit. This is important for a production system where multiple contributors or updates may occur.  
- *Configure Monitoring:* In this first month, also create simple monitoring hooks. For instance, set up logging to a file (or cloud logging) in the orchestrator for each run, capturing time taken and any warnings/errors. If possible, integrate a notification (like an email or Slack message) when a video is successfully uploaded, including the title and link, or when a run fails. This can be done by calling a webhook or using a service like SendGrid for email. The idea is, by Day 30, you should be able to run the pipeline on schedule and be notified of outcomes without checking manually.  
- *Review Content & Adjust Prompts:* With the new models and quality gate in place, manually review the first few videos produced in this phase. Check if the style and accuracy are on point. Adjust the prompt for script writing as needed (the tone instructions or section guidance) if you notice any issues – e.g., if the new model’s scripts are too long or not hitting the desired tone, fine-tune the prompt or target word count. Also ensure the new metadata (title/description) are appropriate and edit the prompt template if not (maybe the model needs a nudge to include a certain hashtag or CTA).  

**Day 31-60: Integrate Intelligence and Feedback**  
- *Trend Integration System:* In this phase, implement a basic **Trend Monitor** service. This could be a small Python script that uses Google Trends API or YouTube Data API (for trending search queries) to fetch top financial queries weekly. If direct API access is problematic, an alternative is to use an OpenAI function that “scrapes” trends from a news site or Google Trends page (given proper allowances). The output should be a list of keywords or topic phrases with some weight. Integrate this with the pipeline: feed those keywords into `story_discovery` scoring as planned, and also into the LLM prompt for script writing (so it knows what audience angle might be interesting). Test this by comparing topic choices with and without trend input to ensure it’s selecting more relevant stories.  
- *Analytics Feedback Loop:* Start building the analytics ingestion. Register the channel for YouTube Analytics API access. Write a script (`analytics_monitor.py`) that can be run via cron or integrated into the pipeline after upload (maybe the day after upload, since stats on views/CTR need some time). This script should pull data like view count, impressions, CTR, avg view duration for the last video (or last N videos). Store this in a small JSON or database along with video metadata (title, topic). Then integrate an OpenAI analysis: feed the recent videos’ performance into a GPT prompt asking for patterns or suggestions. For example: “Video A (topic X) got 10k views with 5% CTR, Video B (topic Y) got 2k views with 3% CTR. What does this suggest about audience interest?” The model’s output can be logged as a “strategy memo”. This might surface ideas like certain topics resonate more. The plan by Day 60 is to have at least a basic report generated from analytics. The actual *use* of this info can be manual initially (you read it and decide adjustments), but it sets the stage for automation.  
- *Content Strategy Adjustments:* With initial analytics in, consider updating the content plan. Possibly, add a feature in story discovery to **avoid topics that underperformed recently** (similar to how we avoid repeating titles). Conversely, if a certain metric or theme did well, maybe temporarily increase its priority in the scoring. This can be done by maintaining a “recent performance” weight that boosts or penalizes certain metric tags. Implement this carefully to not immediately overfit to a small sample (perhaps require 2-3 data points).  
- *Optional - Audience Interaction:* If time permits in this phase, implement a way to incorporate audience feedback directly. For example, auto-fetch top comments from the last video and use GPT to summarize if viewers are asking questions or suggesting related topics. This summary could be fed to the Trend Monitor or directly to script writer as additional context (“Viewers were particularly interested in how X affects them”). This fosters a feeling of responsiveness. It’s optional, but it can improve engagement if done.  

**Day 61-90: Refine, Scale, and Future-Proof**  
- *Optimize for Efficiency:* In the final stretch, focus on performance and cost optimization to ensure the system can scale. Review where the most time is spent – e.g., if b-roll generation is very slow, consider caching mechanism for clips (if a prompt repeats or if you can reuse certain generic clips like “money printer” often). Also consider parallelization implemented earlier: measure if running TTS + rendering + b-roll concurrently cuts down total time. Aim to reduce the end-to-end runtime so that producing a video takes maybe 30-60 minutes of processing (which allows daily runs if needed).  
- *Cost Management:* Set up cost tracking. OpenAI offers usage APIs or at least usage logs – integrate a small utility to pull monthly token usage and cost, to ensure it’s within budget. If costs are trending high, implement a toggle in config for “cost_savings_mode” which might switch the research to a smaller model or skip b-roll for that run, etc. The idea is to have a knob to dial down features if needed without editing code. By Day 90, you should be confident that the pipeline can run continuously without exorbitant costs or at least will alert you if so.  
- *Robustness Testing:* Conduct scenario tests to validate guardrails. For example, intentionally use a wrong API key for Luma to see if the pipeline still produces a video (it should skip b-roll gracefully). Simulate the OpenAI model failing (maybe by pointing to a dummy local model or turning off internet) to see the fallback script writer kick in. Ensure the quality gate correctly stops a video with issues (maybe create a fake script with a repeated title or a forbidden word to see if it blocks). Over these weeks, iron out any discovered bugs.  
- *Documentation & Handover:* Update the README and documentation to reflect the new features and usage. Document how the trend integration works, any required API keys (e.g. if using Google Trends), and how to interpret the analytics feedback outputs. Since the goal is minimal human involvement, the system should be documented such that if it’s handed to an operator, they only need to monitor high-level dashboards or logs, not tweak the internals frequently. Include instructions on how to update API credentials (for YouTube, OpenAI) when needed, since those expire or rotate.  
- *Future Improvements Planning:* By Day 90, compile insights from this fully running system. For instance, note if the LLM is still occasionally making factual errors or if certain topics are still missed. These can inspire further enhancements, such as fine-tuning a model on past scripts to maintain consistency, or integrating a broader set of data sources. Plan for optional future improvements (some ideas in the next section) and create a backlog so development can continue beyond 90 days, though hopefully by now the channel can run largely on autopilot.  

This 90-day plan ensures that by the end of Q2 2026, **The Money Map** will have evolved from an automated pipeline to an intelligent autonomous content system. Each phase builds upon the last: first solidifying reliability, then adding smarts, then optimizing and future-proofing. Importantly, this roadmap includes testing and monitoring steps to catch issues early – critical when human interaction is minimal. The result will be a channel that not only runs without constant oversight, but also **improves itself** over time by learning from its own data.  

# Risks and Guardrails  
Automating a YouTube channel with AI brings significant benefits, but also risks that must be managed. Below we detail the key risks and the guardrails or mitigations recommended to address them:

- **Content Accuracy and Misinformation:** With GPT generating scripts, there’s a risk of factual errors or exaggerated claims. In the financial domain, even small inaccuracies can hurt credibility or mislead viewers. *Guardrails:* We’ve strengthened the research step to ground the script in real data and sources, and added a QA LLM check to catch inconsistencies. Additionally, it’s wise to implement a **fact-check flag**: if the model is unsure about a fact, it should either double-check via the dossier or not state it. The prompt already says to use specific numbers and not approximate. We can enforce that by scanning the script for phrases like “around X” or “I think” – which shouldn’t appear. In case a factual error slips through, monitoring comments can help (viewers might correct errors, which can be input to the next cycle). In the worst case, an automated system could spread misinformation unknowingly, so as a fail-safe, keeping the videos “unlisted” for an hour after upload could allow an automated fact-check via a secondary service or even a quick human skim before making it public. This gives a small window to catch egregious mistakes.  

- **Sensationalism and Tone Drift:** AI might generate overly sensational titles or script lines in an effort to maximize engagement. While we do want engaging content, there’s a fine line before it becomes clickbait or fear-mongering, especially in economic topics. *Guardrails:* The style instructions in the prompt emphasize “urgent but measured” tone. The quality gate can also be tuned to flag overly sensational language (for example, if the title uses words like “Shocking” or all-caps, we might dial it back). OpenAI’s content guidelines and moderation API can be another layer – e.g., run the final script through the moderation model to ensure it doesn’t contain hate, violence, or other policy-violating content (unlikely in finance, but good practice) ([www.pcgamer.com](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=GPT,one%20which%20can%20remember%20their)). Keeping a human-in-the-loop option is a safeguard: perhaps require manual approval for any video that the quality gate isn’t fully confident about (like if the QA LLM gives it a low score or lists issues). Over time, as the AI proves consistent, this could be relaxed.  

- **Model and API Dependence:** The pipeline heavily relies on external AI services (OpenAI, Luma, etc.). Outages, price changes, or model deprecations can disrupt it. Indeed, OpenAI is phasing out older models around this time ([www.pcgamer.com](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=GPT,capture)). *Guardrails:* Always have a **fallback path**. We have retained the template script writer as a fallback if the LLM fails. Similarly, keep a lightweight offline TTS available (even if lower quality, like Google’s gTTS or an AWS Polly voice) in case OpenAI’s voice API is down. For visuals, if Luma isn’t accessible, default to the chart-only video or use stock footage from a local folder as a backup. It’s also wise to maintain buffer content: maybe pre-render one extra video ahead of time (on a generic topic) that could be published if the pipeline fails one week. This ensures the channel continuity. Also consider containerizing the app with specific versions of dependencies, and updating those regularly, so that you can control the environment. For model deprecations, keeping track of AI news (OpenAI announcements) is important – perhaps ironically, we could use a script to periodically check OpenAI’s updates RSS feed or Twitter for announcements on model changes, and alert the maintainer to upgrade the config.  

- **Cost Overruns:** AI APIs can incur significant costs, especially with high-frequency content. Without oversight, the channel could run up a big bill (e.g., if the research agent goes haywire making many calls, or if a bug causes infinite loop). *Guardrails:* Set usage limits. Use OpenAI’s usage dashboard to set hard limits on monthly spend. In-code, we can implement a simple counter for tokens used per run and abort if it exceeds an absurd number (to catch runaway loops). We also introduced config flags to disable expensive features (`--no-broll`, `--no-music` etc.), which can be triggered by an environment variable “cost_saving_mode”. For example, if the monthly cost is nearing the limit, turn that mode on via an automated flag so subsequent runs use only essential steps. Another approach is scheduling fewer videos (the planner could decide to pause for a week if cost is high – though that’s a last resort). Since the channel’s revenue (if monetized) might offset costs eventually, tracking ROI is important too. In 90 days we might not fully monetize, but longer term, connecting the analytics (views, CPMs) with cost can tell if the operation is sustainable.  

- **Quality Erosion Over Time (Drift):** Models can produce subtly worse outputs if prompts or context shift, and the system could drift into producing low-quality content if not periodically recalibrated. *Guardrail:* Regularly retrain or few-shot update the prompts using the best performing episodes as examples. Essentially, every so often (say monthly), review a successful video’s script and consider adding it (anonymized/generalized) to the few-shot pool or prompt guidelines. This way the model continuously “learns” what good looks like, even as it or the data changes. Also, actively use the analytics feedback to tweak the system – this is a form of **online learning** (though manual at first). The key is not leaving the system completely unchecked for long durations. Having a quarterly review of content quality by a human or an expert would be wise, just to catch any slow decline or needed pivot.  

- **Platform Changes and Compliance:** YouTube might change its API or policies. For instance, if YouTube’s upload API quotas change or if they start flagging AI-generated content. Also, content that skirts too close to sensitive areas (like financial advice claims) could raise compliance issues. *Guardrails:* Stay updated with YouTube’s policy changes – ensure the description or script doesn’t accidentally promise “financial advice” or anything that violates monetization rules. We could incorporate a compliance check in the QA – e.g., flag phrases like “you should invest in…” which might be construed as financial advice. As for API changes, using Google’s official client library (as we are) should shield us from minor changes, but depreciation of any endpoint should be monitored. The task list’s suggestion of Dockerizing the pipeline also helps – you can deploy the same tested setup easily if the environment needs to move (e.g., migrating to a cloud VM or container service to run the cron).  

- **Ethical & Brand Risks:** Since no human is crafting the message, we must ensure the AI doesn’t produce something that a human would know to avoid. For example, inadvertently disrespectful language about a serious economic hardship, or simply an inappropriate joke. The tone instructions aim to avoid that, but AI can be unpredictable. *Guardrails:* Reinforce the **system prompt** with clear don’ts (e.g., “Do not make jokes about tragic situations, maintain professional tone”). Continue using the OpenAI content moderation as a final filter on the script text. Also, maintain an allowlist/denylist in code: certain phrases or topics might be off-limits for the channel’s brand (the quality gate can scan for those). If the channel gains a following, an autonomous system could even face backlash for a misstep that a human might have caught. So, investing in these content guardrails is crucial for brand safety.  

In conclusion, each of these risks can be mitigated with a thoughtful guardrail, many of which we’ve baked into the architecture: multi-layer QA for content, fallback pathways for technical failures, cost monitoring, and periodic human oversight at high level. Running a fully autonomous channel is like running a self-driving car – most of the time it should handle things, but you still want manual override capability and regular maintenance checks ([www.pcgamer.com](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=Late%20last%20year%2C%20OpenAI%20head,models%20most%20people%20use%20today)). By implementing the above measures, The Money Map can safely reap the benefits of automation (consistent output, fast production, data-driven content) while minimizing the downsides. The result will be a reliable, scalable content engine that can operate with confidence and accountability, not just blindly.
## Sources

- [add new research tools · Agents-MCP-Hackathon/consilium_mcp at ce0bf87](https://huggingface.co/spaces/Agents-MCP-Hackathon/consilium_mcp/commit/ce0bf87f809ea4ed1505b42a4f98c1133f705420#:~:text=Image%20azettl%20commited%20on%20Jun,2)
- [Luma API - AI Video Generation API | Dream Machine & Ray3](https://apiframe.ai/ai-video-generation#:~:text=AI%20Video%20Generation%20API%20Image%3A,No%20complexity%2C%20just%20stunning)
- [Video Generation](https://docs.lumalabs.ai/docs/video-generation#:~:text=Video%20Generation%20,Models)
- [Automate YouTube Strategy with GPT-4, VidIQ & Zapier | upGrowth](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=,upload%20via%20Zapier%20or%20TubeBuddy)
- [Automate YouTube Strategy with GPT-4, VidIQ & Zapier | upGrowth](https://www.upgrowth.in/automation/ai-optimised-youtube-strategy-from-content-planning-to-metadata-automation-with-gpt-4-and-vidiq/#:~:text=YouTube%20has%20evolved%20into%20a,The%20challenge)
- [GPT Insights for Youtube](https://www.narrative.bi/chatgpt/youtube#:~:text=GPT%20Insights%20for%20Youtube%20ChatGPT,Easily%20upload%20your)
- [People with AI partners are looking for a 'new home' as OpenAI announces date to switch off 'overly supportive' older models](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=On%20February%2013%2C%202026%2C%20OpenAI,mini)
- [ChatGPT + AI Video Tools: Complete YouTube Automation Workflow | TubeChef Blog | TubeChef](https://tubechef.ai/blog/chatgpt-ai-video-tools-complete-workflow#:~:text=,10%20Videos%20in%20One%20Day)
- [Automated YouTube Content Pipeline Built with Python | Faris Elshammouty posted on the topic | LinkedIn](https://www.linkedin.com/posts/faris-elshammouty_python-ai-automation-activity-7428891336994488321-AnAZ#:~:text=Faris%20Elshammouty%202w%20I%20built,You%20give%20it%20a%20topic)
- [People with AI partners are looking for a 'new home' as OpenAI announces date to switch off 'overly supportive' older models](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=GPT,one%20which%20can%20remember%20their)
- [People with AI partners are looking for a 'new home' as OpenAI announces date to switch off 'overly supportive' older models](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=GPT,capture)
- [People with AI partners are looking for a 'new home' as OpenAI announces date to switch off 'overly supportive' older models](https://www.pcgamer.com/software/ai/people-with-ai-partners-are-looking-for-a-new-home-as-openai-announces-date-to-switch-off-overly-supportive-older-models/#:~:text=Late%20last%20year%2C%20OpenAI%20head,models%20most%20people%20use%20today)
