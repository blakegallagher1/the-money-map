# The Money Map 📊

Fully automated YouTube channel that turns Federal Reserve economic data into cinematic, data-driven video content.

## Architecture

```
FRED API → Data Ingestion → Story Discovery → Script Writer → Voiceover (TTS)
                                                    ↓
                               Storyboard Timeline → Enhanced Renderer → AI B-Roll
                                                    ↓
                                   Final Assembly → Quality Gate → YouTube
```

## Pipeline Modules

| Module | File | Description |
|--------|------|-------------|
| Data Ingestion | `scripts/data_ingestion.py` | Pulls 34 FRED economic indicators with YoY calculations |
| Story Discovery | `scripts/story_discovery.py` | Scores each metric for viral potential, picks top story |
| Script Writer V1 | `scripts/script_writer.py` | ~250 word scripts (~1:30 videos) |
| Script Writer V2 | `scripts/enhanced_script_writer.py` | ~400-420 word scripts with section markers & b-roll cues |
| Storyboard Planner | `scripts/storyboard_planner.py` | Builds beat-level storyboard timelines from script sections and real narration timing |
| Renderer V1 | `scripts/render_pilot.py` | Basic 5fps matplotlib → 30fps video |
| Renderer V2 | `scripts/enhanced_renderer.py` | Cinematic renderer with glowing effects, animated counters, Ken Burns zoom, particle effects |
| Thumbnail V1 | `scripts/thumbnail_gen.py` | Basic stat-focused thumbnails |
| Thumbnail V2 | `scripts/enhanced_thumbnail.py` | High-CTR thumbnails with bold headlines, curiosity gap design |
| Final Assembly | `scripts/final_assembly.py` | Interleaves data-viz with AI b-roll, layers voiceover |
| Custom Narrated Episodes | `scripts/custom_episode_builder.py` | Builds branded section-based narration videos from a JSON episode spec |
| Episode Image Visuals | `scripts/episode_image_visuals.py` | Generates reusable still-image visuals from an episode image plan |
| Sora Episode Visuals | `scripts/sora_episode_visuals.py` | Generates Sora clips from a shot plan and drops them into narrated episodes |
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
- **Voiceover**: ElevenLabs / OpenAI TTS with section-timed narration manifests
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

If you want to use the repo-local OpenAI Computer Use helper, install Chromium for
Playwright as well:

```bash
python -m playwright install chromium
```

## Run

```bash
# Full pipeline for one episode
python scripts/orchestrator.py

# Build a narrated non-FRED episode from a JSON spec
python scripts/custom_episode_builder.py --episode data/cre_balance_sheet_fortress/episode.json

# Generate still-image visuals for a narrated episode, then rebuild with those visuals
python scripts/episode_image_visuals.py --plan data/cre_balance_sheet_fortress/image_plan.json
python scripts/custom_episode_builder.py --episode data/cre_balance_sheet_fortress/episode.json

# Generate Sora clips for a narrated episode, then rebuild with those visuals
python scripts/sora_episode_visuals.py --plan data/cre_balance_sheet_fortress/sora_shots.json
python scripts/custom_episode_builder.py --episode data/cre_balance_sheet_fortress/episode.json

# Refresh unpublished versioned draft scripts from live FRED data
python scripts/refresh_unpublished_scripts.py

# Just render enhanced episode N
python scripts/enhanced_renderer.py N

# Just generate thumbnail for episode N
python scripts/enhanced_thumbnail.py N

# Full assembly with b-roll interleaving
python scripts/final_assembly.py N
```

## Repo-Local Skill

This repo now includes a project-scoped Codex skill at
`.codex/skills/money-map-openai-cua/` for browser-only operator tasks that are a
bad fit for the deterministic pipeline scripts. The bundled helper uses the
current OpenAI computer-use loop with a repo-local Playwright harness and writes
screenshots plus raw response JSON to `output/cua/`.

```bash
python .codex/skills/money-map-openai-cua/scripts/run_cua_task.py \
  --task "Upload the finished episode draft in YouTube Studio, then stop before publish." \
  --start-url "https://studio.youtube.com" \
  --allow-domain "studio.youtube.com"
```

Custom narrated episodes write their combined script to `data/<slug>/voiceover_script.txt`,
their final voiceover MP3 to `data/<slug>/voiceover.mp3`, and their final video to
`output/<slug>.mp4`. Generated still-image visuals land under `output/imagegen/<slug>/`.

Main pipeline runs now also emit:

- `data/voiceover_timeline.json` — exact per-section narration timings from the synthesized voiceover
- `data/storyboard_manifest.json` — beat-level visual plan with scene durations and b-roll slots
- `data/quality_gate.json` — publishability report including storyboard/timeline checks

Draft script refresh runs also emit:

- `data/refresh_reports/<timestamp>-unpublished-scripts.json` — machine-readable summary of which draft scripts were regenerated and which current metric values were written

## License

MIT
