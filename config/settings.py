"""
The Money Map — Configuration
All API keys and channel settings.
"""
import os

# --- API Keys ---
FRED_API_KEY = os.environ.get("FRED_API_KEY", "50f1b7098d9ae0eb17d5ec516b6df15e")
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")  # Pending email activation
BLS_API_KEY = os.environ.get("BLS_API_KEY", "")  # Pending email activation
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

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
VIDEO_DURATION_TARGET = 180  # Target ~3 minutes per video
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
