# The Money Map 📊

**Fully automated YouTube channel that produces weekly data-driven economic analysis videos.**

The Money Map pulls real-time economic data from the Federal Reserve (FRED), discovers the most compelling story, writes a narration script, generates AI voiceover, renders animated data visualization videos, and uploads to YouTube — all on autopilot.

## How It Works

```
FRED API → Story Discovery → Script Writer → TTS Voiceover → Video Renderer → YouTube Upload
```

Each week, the pipeline:

1. **Fetches fresh data** from 34 curated FRED economic indicators (housing, inflation, employment, GDP, debt, etc.)
2. **Scores stories** by viral potential — magnitude of change, public interest, consumer pain points, data freshness
3. **Writes a narration script** with a Hook → Context → Related Indicators → Insight → Close structure
4. **Generates AI voiceover** using Gemini TTS (charon voice)
5. **Renders animated data visualizations** — title card, stat callout, animated line chart, comparison dashboard, closing
6. **Generates a clickbait-resistant thumbnail** with the key stat and YoY change
7. **Uploads to YouTube** with optimized title, description, and tags

## Architecture

```
the-money-map/
├── config/
│   └── settings.py          # API keys, 34 FRED series, color palette, story templates
├── scripts/
│   ├── data_ingestion.py    # FREDClient — fetches all 34 indicators with YoY calculations
│   ├── story_discovery.py   # Scores stories by viral potential, finds related indicators
│   ├── script_writer.py     # Generates narration scripts from story packages
│   ├── episode_renderer.py  # Generalized renderer — produces any episode from a story key
│   ├── thumbnail_gen.py     # Generates thumbnails with key stat and YoY change
│   ├── youtube_uploader.py  # Uploads video + thumbnail to YouTube with metadata
│   ├── orchestrator.py      # Full pipeline — runs weekly on cron
│   └── cron_instructions.py # How to schedule the pipeline
└── requirements.txt
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys
Edit `config/settings.py` and fill in:
- `FRED_API_KEY` — get free at https://fred.stlouisfed.org/docs/api/api_key.html
- `GEMINI_API_KEY` — get at https://aistudio.google.com/
- `YOUTUBE_CLIENT_SECRETS_FILE` — path to OAuth2 client_secrets.json from Google Cloud Console

### 3. Run the full pipeline
```bash
python scripts/orchestrator.py
```

### 4. Render a specific episode
```bash
python scripts/episode_renderer.py --story MORTGAGE_RATE_30Y
```

### 5. Schedule weekly runs
```bash
python scripts/cron_instructions.py
```

## Output

Each run produces:
- `output/episode_YYYYMMDD_HHMMSS.mp4` — the rendered video
- `output/thumbnail_YYYYMMDD_HHMMSS.png` — the thumbnail
- Uploaded to YouTube automatically

## Economic Indicators Tracked

| Category | Indicators |
|----------|------------|
| Housing | Mortgage rates (30Y, 15Y), home sales, housing starts, Case-Shiller HPI |
| Inflation | CPI, Core CPI, PCE, PPI |
| Employment | Unemployment rate, nonfarm payrolls, job openings, quits rate |
| GDP | Real GDP, GDP growth rate, GDP per capita |
| Consumer | Retail sales, consumer sentiment, credit card delinquencies |
| Debt | Federal debt, household debt, student loans |
| Banking | Fed funds rate, M2 money supply, 10Y treasury yield |
| Business | ISM manufacturing, durable goods orders |

## License

MIT
