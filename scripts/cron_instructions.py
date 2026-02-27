# scripts/cron_instructions.py
# ─────────────────────────────────────────────
# Instructions for scheduling the Money Map pipeline with cron
# Run this script once to print the cron setup instructions
# ─────────────────────────────────────────────

import os
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.resolve()
PYTHON   = sys.executable
SCRIPT   = REPO_DIR / "scripts" / "orchestrator.py"
LOG_DIR  = REPO_DIR / "output"
LOG_FILE = LOG_DIR / "cron.log"

CRON_LINE = f"0 9 * * 1 {PYTHON} {SCRIPT} >> {LOG_FILE} 2>&1"

print("""
╔══════════════════════════════════════════════════════════════╗
║           THE MONEY MAP — CRON SETUP INSTRUCTIONS           ║
╚══════════════════════════════════════════════════════════════╝

The pipeline is designed to run once per week (Monday at 9 AM).
It will automatically:
  1. Pull fresh FRED economic data
  2. Score and select the most viral story
  3. Write the narration script with Gemini
  4. Generate TTS voiceover (Gemini charon voice)
  5. Render the full 90-second episode video
  6. Generate the thumbnail
  7. Upload to YouTube

─────────────────────────────────────────────
STEP 1: Open your crontab
─────────────────────────────────────────────
  $ crontab -e

─────────────────────────────────────────────
STEP 2: Add this line
─────────────────────────────────────────────
""")

print(f"  {CRON_LINE}")

print("""
─────────────────────────────────────────────
STEP 3: Save and verify
─────────────────────────────────────────────
  $ crontab -l
  # You should see the line above

─────────────────────────────────────────────
STEP 4: Test a manual run first
─────────────────────────────────────────────
""")

print(f"  $ {PYTHON} {SCRIPT} --dry-run")

print("""
─────────────────────────────────────────────
ENVIRONMENT VARIABLES (add to ~/.bashrc or .env)
─────────────────────────────────────────────
  export FRED_API_KEY="your_fred_api_key"
  export GEMINI_API_KEY="your_gemini_api_key"
  export YOUTUBE_CLIENT_SECRETS_FILE="/path/to/client_secrets.json"

─────────────────────────────────────────────
OUTPUT LOCATION
─────────────────────────────────────────────
""")

print(f"  Videos:     {LOG_DIR}/*.mp4")
print(f"  Thumbnails: {LOG_DIR}/*.png")
print(f"  Logs:       {LOG_FILE}")

print("""
─────────────────────────────────────────────
NOTES
─────────────────────────────────────────────
  - First run requires YouTube OAuth2 browser authentication
  - Subsequent runs use stored token.json credentials
  - FRED API is free with no rate limits for this volume
  - Gemini TTS uses ~500 tokens per episode
  - Video rendering takes ~2-5 minutes on a modern CPU
═══════════════════════════════════════════════════════════════
""")