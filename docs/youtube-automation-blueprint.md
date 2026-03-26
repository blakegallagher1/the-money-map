# YouTube Automation Blueprint

Updated: 2026-03-25

## Objective

Turn `the-money-map` from a strong semi-automated video pipeline into a genuinely automated YouTube publishing system that can:

1. detect promising topics,
2. research them with current web context,
3. write differentiated scripts and metadata,
4. generate visuals and narration,
5. run policy and quality gates,
6. publish or schedule uploads safely, and
7. learn from channel performance.

## Current State

The repo already covers a meaningful portion of the production path:

- FRED ingestion and story selection exist.
- Script generation exists.
- OpenAI TTS exists.
- Render, thumbnail, assembly, and upload code exist.
- Episode history tracking exists.
- The repo now includes a reusable OpenAI deep-research runner at `scripts/openai_deep_research.py`.

The missing piece is the closed automation loop. Right now the project can produce videos, but it does not yet behave like a channel operator.

## What Is Missing

The highest-leverage gap is a "channel brain" layer between story discovery and final publish.

Without that layer, the repo still lacks:

- current-event and audience-context research,
- title and package iteration,
- automated policy/quality checks before upload,
- upload scheduling and processing-state orchestration,
- analytics-driven topic feedback,
- originality controls to avoid repetitive or low-differentiation output.

## Platform Constraints

These YouTube platform details matter for the design:

- Uploading, updating, or deleting videos requires OAuth 2.0 authorization through the YouTube Data API, not just an API key. See the [YouTube Data API reference](https://developers.google.com/youtube/v3/docs).
- Google documents that uploads from unverified API projects created after July 28, 2020 are restricted to private mode until the project passes an audit. See the [video resource docs](https://developers.google.com/youtube/v3/docs/videos) and the [upload guide](https://developers.google.com/youtube/v3/guides/uploading_a_video).
- Scheduled publishing relies on `status.publishAt`, and Google states it can only be set on videos that are private and have never been published. See the [video resource docs](https://developers.google.com/youtube/v3/docs/videos).
- Google’s implementation guides recommend checking `processingDetails.processingStatus` after upload before downstream actions depend on a finished asset. See the [videos implementation guide](https://developers.google.com/youtube/v3/guides/implementation/videos).
- YouTube monetization policy explicitly warns against mass-produced or repetitive content, including image slideshows with minimal narrative or educational value. See [YouTube channel monetization policies](https://support.google.com/youtube/answer/1311392).
- YouTube requires creators to disclose meaningfully altered or synthetic realistic content through the altered-content flow. See [Disclosing use of altered or synthetic content](https://support.google.com/youtube/answer/14328491).

## Recommended Architecture

### 1. Topic Scout

Keep the existing FRED-based story discovery, but add a second signal layer:

- web-backed macro context,
- seasonal and event context,
- prior channel performance,
- novelty scoring against recently published episodes.

Model:

- `gpt-5.4` for ranking, synthesis, and routing.

### 2. Research Dossier

Before script generation, generate a structured topic dossier that answers:

- Why this topic matters right now
- What recent developments changed the story
- What the viewer takeaway should be
- Which angles are overused versus differentiated
- What supporting examples and citations should appear in the script

Models:

- `gpt-5.4` to rewrite the research brief or compress repo/story context
- `o3-deep-research-2025-06-26` for long-form external research when you want
  the highest quality

Repo path:

- Extend `scripts/openai_deep_research.py` into a story-level dossier generator
- Save artifacts under `data/<episode_slug>/research.md` and `data/<episode_slug>/research.json`

### 3. Script + Metadata Pack

Replace "script only" generation with a full package:

- spoken script,
- title options,
- description,
- tags,
- thumbnail text angles,
- b-roll plan,
- disclosure flags,
- source list.

Model:

- `gpt-5.4` with structured outputs via the Responses API.

### 4. Asset Planner

Turn the section plan into a deterministic visual schedule:

- chart segments,
- Sora clips,
- image generations,
- stock-footage fallback,
- on-screen text constraints,
- disclosure overlays when needed.

This should produce a machine-readable asset manifest, not just prompts.

### 5. Quality Gate

Add a hard pre-publish gate that blocks upload when:

- the episode is too similar to prior uploads,
- citations are missing,
- the metadata overpromises versus the script,
- the video lacks enough original narration/commentary,
- AI disclosure is required but not set,
- processing or thumbnail generation failed.

### 6. Publisher + Scheduler

After upload:

- poll processing status,
- set thumbnail only when the upload is ready,
- optionally schedule via `publishAt`,
- record the upload URL and publish state,
- keep private by default until all gates pass.

### 7. Feedback Loop

Ingest channel performance and feed it back into topic and packaging decisions:

- views,
- click-through rate,
- average view duration,
- retention drop-off points,
- subscribers gained,
- comments/themes.

Use that signal to change story scoring, script structure, title style, and visual pacing.

## Top 5 Immediate Repo Changes

1. Add `step_research()` to `scripts/orchestrator.py` before `step_script()`.
   The script writer should consume a research dossier rather than only a `story_pkg`.

2. Move `scripts/llm_script_writer.py` from Chat Completions to the Responses API.
   The repo now points at `gpt-5.4`, but the writer still uses the older chat-completions surface. Migrate to structured outputs and keep the research dossier in-context.

3. Add `scripts/quality_gate.py`.
   It should validate originality, citation presence, disclosure requirements, metadata alignment, and required artifacts before upload.

4. Extend `scripts/youtube_api_uploader.py` into a publish controller.
   Add processing-status polling, scheduled publish support, and a private-by-default flow until the quality gate passes.

5. Extend `scripts/episode_tracker.py` into a real feedback store.
   Store post-publish analytics and use them in `story_discovery.py` to avoid repetitive or low-performing episode formats.

## Build Order

1. Wire research dossiers into the orchestrator.
2. Upgrade script generation to Responses API structured outputs.
3. Add the quality gate.
4. Harden YouTube upload and scheduling.
5. Add analytics ingestion and feedback-driven scoring.
6. Only then fully automate public publishing.

## Operational Guardrails

- Keep uploads private by default until the automated gate is proven stable.
- Maintain a source ledger for every claim used in narration.
- Add a repetition detector against recent scripts, titles, and thumbnails.
- Require explicit altered/synthetic-content flags when visuals are realistic enough to trigger YouTube disclosure rules.
- Add cost ceilings for research, image generation, video generation, and retries.
- Preserve a human review option for public publish, especially while the channel is still building a monetizable content pattern.

## The Short Version

The repo does not need a wholesale rebuild. It needs one new control plane:

`topic -> research dossier -> script pack -> asset manifest -> quality gate -> upload/schedule -> analytics feedback`

The single most important addition is the research-and-feedback loop. That is the step that turns this from "a pipeline that can make videos" into "a channel system that can operate itself."
