# config/settings.py
# ─────────────────────────────────────────────
# Central configuration for The Money Map pipeline
# ─────────────────────────────────────────────

import os

# ── API Keys ──────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_CREDENTIALS_FILE = os.getenv("YOUTUBE_CREDENTIALS_FILE", "token.json")

# ── Output ────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Video Dimensions ──────────────────────────
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# ── Brand Colors ──────────────────────────────
COLOR_BG        = "#0A0E1A"   # deep navy background
COLOR_ACCENT    = "#00D4FF"   # electric cyan
COLOR_POSITIVE  = "#00FF88"   # green for good news
COLOR_NEGATIVE  = "#FF4444"   # red for bad news
COLOR_NEUTRAL   = "#FFB800"   # amber for neutral
COLOR_TEXT      = "#FFFFFF"   # white text
COLOR_SUBTEXT   = "#8892A4"   # muted subtext
COLOR_GRID      = "#1A2035"   # subtle grid lines

# ── TTS Voice ─────────────────────────────────
TTS_VOICE = "charon"   # Gemini TTS voice

# ── FRED Series IDs ───────────────────────────
# 34 curated economic indicators
FRED_SERIES = {
    # Housing
    "MORTGAGE_RATE_30Y":     {"series_id": "MORTGAGE30US",  "label": "30-Year Mortgage Rate",         "unit": "%",  "category": "Housing"},
    "MORTGAGE_RATE_15Y":     {"series_id": "MORTGAGE15US",  "label": "15-Year Mortgage Rate",         "unit": "%",  "category": "Housing"},
    "HOME_SALES_EXISTING":   {"series_id": "EXHOSLUSM495S", "label": "Existing Home Sales",           "unit": "M",  "category": "Housing"},
    "HOME_SALES_NEW":        {"series_id": "HSN1F",         "label": "New Home Sales",                "unit": "K",  "category": "Housing"},
    "HOUSING_STARTS":        {"series_id": "HOUST",         "label": "Housing Starts",                "unit": "K",  "category": "Housing"},
    "CASE_SHILLER_HPI":      {"series_id": "CSUSHPISA",     "label": "Case-Shiller Home Price Index", "unit": "",   "category": "Housing"},
    # Inflation
    "CPI_ALL":               {"series_id": "CPIAUCSL",      "label": "CPI (All Items)",               "unit": "",   "category": "Inflation"},
    "CPI_CORE":              {"series_id": "CPILFESL",      "label": "Core CPI",                      "unit": "",   "category": "Inflation"},
    "PCE":                   {"series_id": "PCE",           "label": "Personal Consumption Expenditures","unit": "B", "category": "Inflation"},
    "PPI_ALL":               {"series_id": "PPIACO",        "label": "PPI (All Commodities)",         "unit": "",   "category": "Inflation"},
    # Employment
    "UNEMPLOYMENT_RATE":     {"series_id": "UNRATE",        "label": "Unemployment Rate",             "unit": "%",  "category": "Employment"},
    "NONFARM_PAYROLLS":      {"series_id": "PAYEMS",        "label": "Nonfarm Payrolls",              "unit": "K",  "category": "Employment"},
    "JOB_OPENINGS":          {"series_id": "JTSJOL",        "label": "Job Openings",                  "unit": "K",  "category": "Employment"},
    "QUITS_RATE":            {"series_id": "JTSQUR",        "label": "Quits Rate",                    "unit": "%",  "category": "Employment"},
    # GDP
    "REAL_GDP":              {"series_id": "GDPC1",         "label": "Real GDP",                      "unit": "B",  "category": "GDP"},
    "GDP_GROWTH":            {"series_id": "A191RL1Q225SBEA","label": "Real GDP Growth Rate",         "unit": "%",  "category": "GDP"},
    "GDP_PER_CAPITA":        {"series_id": "A939RX0Q048SBEA","label": "Real GDP Per Capita",          "unit": "$",  "category": "GDP"},
    # Consumer
    "RETAIL_SALES":          {"series_id": "RSAFS",         "label": "Retail Sales",                  "unit": "M",  "category": "Consumer"},
    "CONSUMER_SENTIMENT":    {"series_id": "UMCSENT",       "label": "Consumer Sentiment",            "unit": "",   "category": "Consumer"},
    "CREDIT_CARD_DELINQ":    {"series_id": "DRCCLACBS",     "label": "Credit Card Delinquency Rate",  "unit": "%",  "category": "Consumer"},
    "PERSONAL_SAVINGS":      {"series_id": "PSAVERT",       "label": "Personal Savings Rate",         "unit": "%",  "category": "Consumer"},
    # Debt
    "FEDERAL_DEBT":          {"series_id": "GFDEBTN",       "label": "Federal Debt",                  "unit": "M",  "category": "Debt"},
    "HOUSEHOLD_DEBT":        {"series_id": "HDTGPDUSQ163N", "label": "Household Debt to GDP",         "unit": "%",  "category": "Debt"},
    "STUDENT_LOANS":         {"series_id": "SLOAS",         "label": "Student Loan Debt",             "unit": "M",  "category": "Debt"},
    # Banking
    "FED_FUNDS_RATE":        {"series_id": "FEDFUNDS",      "label": "Federal Funds Rate",            "unit": "%",  "category": "Banking"},
    "M2_MONEY_SUPPLY":       {"series_id": "M2SL",          "label": "M2 Money Supply",               "unit": "B",  "category": "Banking"},
    "TREASURY_10Y":          {"series_id": "GS10",          "label": "10-Year Treasury Yield",        "unit": "%",  "category": "Banking"},
    "TREASURY_2Y":           {"series_id": "GS2",           "label": "2-Year Treasury Yield",         "unit": "%",  "category": "Banking"},
    "YIELD_CURVE":           {"series_id": "T10Y2Y",        "label": "10Y-2Y Yield Curve Spread",     "unit": "%",  "category": "Banking"},
    # Business
    "ISM_MANUFACTURING":     {"series_id": "MANEMP",        "label": "Manufacturing Employment",      "unit": "K",  "category": "Business"},
    "DURABLE_GOODS":         {"series_id": "DGORDER",       "label": "Durable Goods Orders",          "unit": "M",  "category": "Business"},
    "INDUSTRIAL_PRODUCTION": {"series_id": "INDPRO",        "label": "Industrial Production Index",   "unit": "",   "category": "Business"},
    # Market
    "SP500":                 {"series_id": "SP500",         "label": "S&P 500",                       "unit": "",   "category": "Market"},
    "WILSHIRE5000":          {"series_id": "WILL5000PR",    "label": "Wilshire 5000",                 "unit": "",   "category": "Market"},
}

# ── Story Score Weights ────────────────────────
STORY_WEIGHTS = {
    "magnitude":       0.35,   # how big is the YoY change?
    "public_interest": 0.25,   # does it affect everyday Americans?
    "pain_point":      0.20,   # does it hurt people's wallets?
    "freshness":       0.20,   # how recent is the data?
}

# Public interest scores by category (0–1)
PUBLIC_INTEREST = {
    "Housing":    0.95,
    "Inflation":  0.90,
    "Employment": 0.85,
    "Consumer":   0.80,
    "Debt":       0.75,
    "Banking":    0.70,
    "GDP":        0.65,
    "Business":   0.60,
    "Market":     0.55,
}

# Pain point scores by category (0–1)
PAIN_POINT = {
    "Housing":    1.00,
    "Inflation":  0.95,
    "Employment": 0.90,
    "Consumer":   0.85,
    "Debt":       0.80,
    "Banking":    0.60,
    "GDP":        0.40,
    "Business":   0.35,
    "Market":     0.30,
}
