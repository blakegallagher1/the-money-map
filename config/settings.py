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
SUNO_API_KEY = os.environ.get("SUNO_API_KEY", "")  # For AI background music generation

# --- LLM Script Writer ---
SCRIPT_LLM_MODEL = "gpt-5.4"
TARGET_WORD_COUNT = 700  # Target ~4-5 minute videos
RESEARCH_PROMPT_MODEL = "gpt-5.4"
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

# --- TTS Settings (OpenAI gpt-4o-mini-tts) ---
# OpenAI recommends marin/cedar for best quality in the TTS guide.
TTS_MODEL = "gpt-4o-mini-tts-2025-12-15"
TTS_FALLBACK_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "marin"
TTS_FALLBACK_VOICES = ["cedar"]
TTS_INSTRUCTIONS = (
    "Role: Professional macroeconomic narrator for a YouTube briefing.\n"
    "Tone: Confident, credible, and calm. Avoid hype and avoid monotone delivery.\n"
    "Pacing: Baseline pace ~145 words per minute. Slow down 10-15% for key statistics, "
    "year-over-year deltas, and dollar/percent figures.\n"
    "Pauses: Add a short pause after each major claim and a slightly longer pause before the "
    "main takeaway sentence of each section.\n"
    "Emphasis: Clearly stress numeric magnitude words like 'billion', 'percent', "
    "'highest', 'lowest', 'accelerated', and 'slowed'.\n"
    "Prosody: Keep transitions smooth between sections; maintain consistent loudness and tone "
    "from intro through close.\n"
    "Pronunciation: Read symbols naturally (for example '$3.97' as 'three dollars and "
    "ninety-seven cents')."
)

# --- TTS provider (openai | elevenlabs) ---
# ElevenLabs: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "openai").strip().lower()
_vo_norm = os.environ.get("VOICEOVER_NORMALIZE", "true").strip().lower()
VOICEOVER_NORMALIZE = _vo_norm not in ("0", "false", "no", "off")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
ELEVENLABS_MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
# mp3_44100_128 works on free/Creator; wav_44100 requires Pro+ per ElevenLabs API.
ELEVENLABS_OUTPUT_FORMAT = os.environ.get("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128").strip()
ELEVENLABS_API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io").rstrip("/")
ELEVENLABS_MAX_CHARS = int(os.environ.get("ELEVENLABS_MAX_CHARS", "2500"))
ELEVENLABS_STABILITY = float(os.environ.get("ELEVENLABS_STABILITY", "0.5"))
ELEVENLABS_SIMILARITY = float(os.environ.get("ELEVENLABS_SIMILARITY", "0.75"))
ELEVENLABS_STYLE = float(os.environ.get("ELEVENLABS_STYLE", "0.0"))
ELEVENLABS_SPEED = float(os.environ.get("ELEVENLABS_SPEED", "1.0"))
# Omit from API request unless set to auto|on|off. Use "off" if ElevenLabs double-normalizes
# numbers after normalize_for_tts (see ElevenLabs apply_text_normalization docs).
_el_norm = os.environ.get("ELEVENLABS_APPLY_TEXT_NORMALIZATION", "").strip().lower()
ELEVENLABS_APPLY_TEXT_NORMALIZATION = (
    _el_norm if _el_norm in ("auto", "on", "off") else None
)
# Set to e.g. "en" for clearer English normalization on multilingual models (optional).
ELEVENLABS_LANGUAGE_CODE = os.environ.get("ELEVENLABS_LANGUAGE_CODE", "").strip()
TTS_ELEVENLABS_FALLBACK_OPENAI = (
    os.environ.get("TTS_ELEVENLABS_FALLBACK_OPENAI", "false").lower() == "true"
)

# --- YouTube Channel ---
YOUTUBE_CHANNEL_NAME = "Brick & Yield"
YOUTUBE_CHANNEL_ID = "UCoW2hWwjudLNuEAF6CiZvcw"

# --- Content Settings ---
QUALITY_TIERS = {
    "1080": {"width": 1920, "height": 1080, "fps": 30},
    "1440": {"width": 2560, "height": 1440, "fps": 30},
    "2160": {"width": 3840, "height": 2160, "fps": 30},
}
DEFAULT_QUALITY_TIER = os.environ.get("QUALITY_TIER", "1440")
if DEFAULT_QUALITY_TIER not in QUALITY_TIERS:
    DEFAULT_QUALITY_TIER = "1440"

VIDEO_WIDTH = QUALITY_TIERS[DEFAULT_QUALITY_TIER]["width"]
VIDEO_HEIGHT = QUALITY_TIERS[DEFAULT_QUALITY_TIER]["height"]
FPS = QUALITY_TIERS[DEFAULT_QUALITY_TIER]["fps"]
VIDEO_DURATION_TARGET = 270  # Target ~4.5 minutes per video
FONT_FAMILY = "DejaVu Sans"


def get_quality_profile(tier: str | None = None) -> dict:
    """Return normalized render profile for a quality tier."""
    selected = tier or DEFAULT_QUALITY_TIER
    if selected not in QUALITY_TIERS:
        raise ValueError(f"Unknown quality tier '{selected}'. Valid: {sorted(QUALITY_TIERS)}")
    profile = QUALITY_TIERS[selected]
    return {"tier": selected, **profile}

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
