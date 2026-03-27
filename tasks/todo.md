# The Money Map — Task Tracking

## Active Sprint

### [x] Refresh Unpublished Draft Video Scripts
- **Goal**: Update the saved unpublished episode drafts so their scripts and metric facts reflect live data as of 2026-03-27
- **Branch**: `feat/storyboard-timeline-upgrade`
- **Specs**:
  - Refresh only versioned draft episode scripts under `data/ep*_v2/`.
  - Treat a script as already published only when its exact title appears in `data/episode_history.json` with a non-empty `video_url`.
  - Rebuild each unpublished draft from fresh FRED data while preserving its original primary metric/topic.
  - Persist updated `script.json` plus sibling `voiceover_script.txt`, and save a machine-readable refresh report.
- **Steps**:
  - [x] Inspect draft script inventory and current publish history
  - [x] Add a repeatable refresh utility plus deterministic tests
  - [x] Run the refresh against live data and update the affected draft assets
  - [x] Verify the updated scripts, rerun the test suite, and ship the branch
- **Verification**:
  - [x] Baseline `python -m pytest -q` captured (`57 passed`)
  - [x] Targeted pytest slice for unpublished-script refresh logic passes (`python -m pytest -q tests/test_refresh_unpublished_scripts.py`)
  - [x] Full `python -m pytest -q` rerun passes after the refresh (`61 passed`)
  - [x] Refresh report confirms the draft scripts were regenerated from current data (`data/refresh_reports/20260327-114857-unpublished-scripts.json`)
- **Status**: complete
- **Review**: Added `scripts/refresh_unpublished_scripts.py` to refresh versioned unpublished draft scripts in place from a live FRED pull while preserving each draft's primary metric, wrote `tests/test_refresh_unpublished_scripts.py` for draft selection and artifact sync behavior, updated `README.md` with the new operator command, refreshed `data/latest_data.json`, and regenerated the unpublished drafts at `data/ep1_v2/`, `data/ep2_v2/`, `data/ep4_v2/`, and `data/ep5_v2/` plus their sibling `voiceover_script.txt` files. The 2026-03-27 refresh also saved current research dossiers under `data/dossiers/` and the machine-readable summary at `data/refresh_reports/20260327-114857-unpublished-scripts.json`.

### [x] Main Pipeline Storyboard Timeline Upgrade
- **Goal**: Upgrade the main FRED pipeline from section-level timing heuristics to an audio-first storyboard/timeline system that improves visual pacing and sync
- **Branch**: `feat/storyboard-timeline-upgrade`
- **Specs**:
  - Preserve the existing research -> script -> voiceover -> render -> assemble -> upload flow.
  - Add a reusable storyboard/timeline manifest derived from the script and real narration timing.
  - Expand visual planning beyond three coarse b-roll slots into beat-level visual segments.
  - Reuse the narrated-episode pattern where visuals are built to actual audio duration rather than word-count estimates.
  - Extend quality gating so timeline/storyboard defects can block publish.
- **Steps**:
  - [x] Inspect current dirty pipeline diffs and align the write scope
  - [x] Add storyboard planning + timing helpers with deterministic tests
  - [x] Thread storyboard/timeline artifacts through orchestrator, TTS, render, and final assembly
  - [x] Add quality-gate checks for storyboard density and timing coverage
  - [x] Run targeted verification, rerun the repo test suite, and ship the branch
- **Verification**:
  - [x] Baseline `git status --short` captured
  - [x] Baseline `python -m pytest -q` captured with pre-existing collection failure in `tests/test_custom_episode_builder.py`
  - [x] Targeted pytest slices for new storyboard/timeline behavior pass
  - [x] Full `python -m pytest -q` rerun captured and now passes
  - [x] Real pipeline exercise completed via `python scripts/orchestrator.py --step voiceover --no-upload --quality-tier 1080 --force-voiceover --min-words 350`
- **Status**: complete
- **Review**: Added `scripts/storyboard_planner.py` to derive beat-level timelines from ordered script sections plus real voiceover timings, upgraded `scripts/tts_generator.py` to synthesize section-timed narration and persist `data/voiceover_timeline.json`, threaded `data/storyboard_manifest.json` through orchestrator/render/assembly so render scene lengths now follow actual narration instead of word-count heuristics, generalized b-roll planning to multiple storyboard clip slots, and extended the quality gate to require storyboard/timing artifacts. Verification passed with `python -m py_compile scripts/*.py`, a 48-test targeted media pipeline slice, a full `python -m pytest -q` run (`57 passed`), and a real no-upload pipeline build that produced fresh `output/voiceover.wav`, `output/latest_v2_final.mp4`, `output/latest_final.mp4`, `output/thumbnail.png`, `data/voiceover_timeline.json`, `data/storyboard_manifest.json`, and a passing `data/quality_gate.json`.

### [x] Video Quality Upgrade Analysis
- **Goal**: Analyze the current automated pipeline and identify the single highest-impact quality upgrade now that ElevenLabs voiceover and direct YouTube publishing are available
- **Branch**: `main`
- **Steps**:
  - [x] Review current pipeline instructions, memory, and dirty worktree state
  - [x] Trace script, TTS, render, assembly, quality gate, and upload flows
  - [x] Compare current capabilities against the strongest missing quality layer
  - [x] Record the recommendation and supporting code evidence
- **Verification**:
  - [x] Baseline `git status --short` captured
  - [x] Baseline `python -m pytest -q` captured with pre-existing collection failure in `tests/test_custom_episode_builder.py`
  - [x] Core pipeline modules and tests reviewed (`llm_script_writer`, `tts_generator`, `enhanced_renderer`, `final_assembly`, `quality_gate`, `custom_episode_builder`)
- **Status**: complete
- **Review**: The biggest quality bottleneck is no longer voice or publishing infrastructure; it is the lack of a beat-level storyboard and timing system in the main pipeline. The current flow still asks the LLM for only three b-roll prompts, generates only three clips, and assembles them at coarse section boundaries while render timing is estimated from word counts instead of real narration duration. The custom narrated-episode path already proves the better pattern in-repo: generate section audio first, derive exact durations from audio, and build the visual sequence to match that timing. The recommended next upgrade is to port that pattern into the main FRED pipeline as a storyboard/timeline layer that expands each episode into timed visual beats and assembles visuals against actual voiceover timings.

### [ ] OpenAI CUA Skill For Money Map
- **Goal**: Create a repo-local Codex skill that uses the current OpenAI Computer Use Agent workflow to perform browser-driven tasks for `the-money-map`
- **Branch**: `main`
- **Specs**:
  - Build the skill under `.codex/skills/` so it ships with this repo.
  - Ground the skill in current OpenAI docs for the Responses API computer-use flow and safety model.
  - Account for the repo's current `openai==2.16.0` SDK lag by using a raw-response compatibility path instead of relying on generated computer-tool types.
  - Focus the skill on project-relevant browser tasks such as upload/admin workflows, external UI validation, and repeatable operator actions that are difficult to API-automate.
- **Steps**:
  - [x] Gather repo guidance, baseline state, and current OpenAI CUA documentation
  - [x] Scaffold the repo-local skill and agent metadata
  - [x] Implement a reusable helper runner for the CUA loop
  - [x] Add deterministic tests and validate the skill bundle
  - [x] Update repo docs and record final review notes
- **Verification**:
  - [x] Baseline `git status --short` recorded (clean)
  - [x] Baseline test suite run recorded (`python -m pytest`) with pre-existing collection failure in `tests/test_custom_episode_builder.py`
  - [x] `python -m pip_audit -r requirements.txt` recorded before dependency changes
  - [x] `python /Users/gallagherpropertycompany/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/money-map-openai-cua`
  - [x] Targeted pytest slice for the new helper/test coverage passes
  - [x] Repo verification summary recorded, including any remaining unrelated baseline failures
- **Status**: review
- **Review**: Added the repo-local skill at `.codex/skills/money-map-openai-cua/`, bundled `scripts/run_cua_task.py` as a raw-response OpenAI CUA Playwright harness that matches the current GA docs while working around the repo's `openai==2.16.0` generated-type lag, documented the integration and usage path in `README.md`, added a deterministic pytest slice for the helper, and updated `requirements.txt` plus `.gitignore` for the new workflow. Validation passed via `quick_validate.py`, `python -m pytest tests/test_money_map_openai_cua.py -q`, `python .codex/skills/money-map-openai-cua/scripts/run_cua_task.py --help`, and `python -m pip_audit -r requirements.txt`. Full `python -m pytest` remains blocked by the same pre-existing `tests/test_custom_episode_builder.py` import error recorded at baseline.

### [ ] Imagegen Visual Upgrade
- **Goal**: Replace the weakest slideshow beats in the CRE balance-sheet episode with high-end generated stills and rebuild the video around those visuals
- **Branch**: `main`
- **Steps**:
  - [x] Define a reusable image prompt plan for the episode
  - [x] Generate premium still images with the `imagegen` workflow
  - [x] Integrate the generated stills into the episode builder
  - [x] Rebuild the final episode and verify the upgraded export
- **Verification**:
  - [x] Baseline test suite run recorded (`python -m pytest`)
  - [x] Generated stills are saved locally under stable paths
  - [x] Upgraded final video renders successfully
  - [x] `ffprobe` and spot-check frames confirm the final export
- **Status**: complete
- **Review**: Added `scripts/episode_image_visuals.py` plus `data/cre_balance_sheet_fortress/image_plan.json` for reproducible still generation, moved visual-asset sequencing into `scripts/episode_visual_assets.py`, updated the episode spec to use generated stills, and rebuilt `output/cre_balance_sheet_fortress.mp4` against six locally generated image assets under `output/imagegen/cre_balance_sheet_fortress/`.

### [ ] Sora Generation Via ChatGPT Pro
- **Goal**: Use browser automation against the ChatGPT/Sora web UI so episode visuals can be generated through the user's ChatGPT Pro account instead of the API billing path
- **Branch**: `main`
- **Steps**:
  - [ ] Launch a reusable headed browser session with Playwright interactive
  - [ ] Reach the ChatGPT/Sora generation surface and confirm account access
  - [ ] Submit the episode shot prompts and download completed videos
  - [ ] Rebuild the final episode with the new clips if generation succeeds
- **Verification**:
  - [ ] Browser session reaches the correct Sora UI while signed in
  - [ ] Requested clip jobs are submitted successfully
  - [ ] Downloaded video assets are saved locally
  - [ ] Episode rebuild and artifact checks pass if new clips are produced
- **Status**: superseded
- **Review**: Superseded after the authenticated browser route did not provide a workable current Sora surface for this task; the visual upgrade was completed through the reproducible `imagegen` path instead.

### [ ] CRE Balance Sheet Sora Upgrade
- **Goal**: Improve the narrated CRE balance-sheet video with Sora-generated cinematic section visuals while keeping the existing voiceover and timing intact
- **Branch**: `main`
- **Steps**:
  - [x] Define a reusable Sora shot plan for the episode
  - [x] Add repo-local Sora generation and builder integration paths
  - [x] Generate Sora clips and rebuild the upgraded episode
  - [x] Verify the upgraded export and ship the code path
- **Verification**:
  - [x] Baseline test suite run recorded (`python -m pytest`)
  - [x] Sora clips generated successfully for targeted sections
  - [x] Upgraded final video renders successfully
  - [x] `ffprobe` confirms output durations/codecs
- **Status**: complete
- **Review**: Added `scripts/sora_episode_visuals.py`, wired `scripts/custom_episode_builder.py` to splice section-level Sora b-roll, updated `data/cre_balance_sheet_fortress/episode.json` to reuse the three completed Sora renders across the strongest-fit sections, and rebuilt `output/cre_balance_sheet_fortress.mp4` with subtle motion on non-Sora sections. Full six-shot generation was planned, but live rendering stopped after three successful clips when the OpenAI account hit a Sora billing hard limit.

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
