# The Money Map — Task Tracking

## Active Sprint

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
