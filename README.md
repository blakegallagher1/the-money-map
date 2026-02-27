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

# Just render enhanced episode N
python scripts/enhanced_renderer.py N

# Just generate thumbnail for episode N
python scripts/enhanced_thumbnail.py N

# Full assembly with b-roll interleaving
python scripts/final_assembly.py N
```

## License

MIT
