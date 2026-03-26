Important caveat first: I can’t directly read `/Users/gallagherpropertycompany/Desktop/the-money-map` from this chat environment, so I can’t honestly tell you “`file X` already does Y” without you pasting the repo tree or key files. If you send `tree -a -L 3`, `package.json`/`pyproject.toml`, and the main app/worker entrypoints, I can turn this into a true repo-specific refactor plan.

With that limitation, here’s the concrete, implementation-oriented blueprint I’d use to turn **this repo** into an automated YouTube video machine.

## 1) What the repo should become

Treat the repo as a **content factory with a strict state machine**, not as “a script that uploads videos.”

Target pipeline:

1. **Topic intake**
2. **Topic scoring / dedupe**
3. **Research packet generation**
4. **Script + storyboard**
5. **Voiceover + assets**
6. **Render**
7. **Policy/quality gate**
8. **Upload + schedule**
9. **Analytics ingest**
10. **Feedback into topic/model/template selection**

If the repo already has any of these, keep them:
- data ingestion / scraping / ETL
- prompt or template management
- image/audio/video transformation utilities
- cron / workers / queues
- a DB / ORM / admin UI

Those are the natural “strengths already present” to reuse. What usually kills YouTube automation projects is not rendering; it’s lack of durable job state, dedupe, policy checks, and feedback loops.

## 2) Missing modules you almost certainly need

Even if the repo already has LLM or media generation pieces, the missing modules for a real YouTube machine are usually these:

### A. `content_jobs` state machine
You need a single source of truth for every video idea.

Suggested states:
- `idea_found`
- `idea_scored`
- `research_locked`
- `script_drafted`
- `script_approved`
- `assets_ready`
- `render_complete`
- `qc_passed`
- `uploaded_private`
- `processing_complete`
- `scheduled`
- `published`
- `analytics_ingested`
- `retired`

Suggested tables:
- `topics`
- `source_packets`
- `scripts`
- `asset_manifests`
- `renders`
- `youtube_publications`
- `video_metrics_daily`
- `policy_audits`
- `experiments`

### B. Topic scorer + novelty guard
Before generating anything, score topic candidates on:
- search/demand signal
- fit to channel thesis
- monetization safety
- freshness / evergreen score
- asset availability
- **novelty vs your previous uploads**

This is how you avoid repetitive, template spam.

### C. Research packet builder
Every video should have a locked packet:
- source URLs
- extracted notes
- claims to verify
- visual asset suggestions
- “original angle” statement
- banned claims / risky claims

### D. Policy guard
Automated checks for:
- semantic similarity to prior scripts/titles/thumbnails
- whether the script is just paraphrased web text
- whether AI disclosure is required
- whether third-party media licensing is missing
- whether the content could look “mass-produced”

### E. YouTube publisher adapter
A dedicated module for:
- OAuth token acquisition/refresh
- resumable uploads
- thumbnail upload
- playlist assignment
- scheduling
- processing-status polling
- analytics pull

### F. Feedback loop
A worker that pulls per-video metrics daily and feeds them back into:
- topic scoring
- title/thumbnail selection
- script length
- intro format
- asset style
- publish timing

## 3) Recommended data flow, end to end

Here’s the flow I’d implement in this repo.

### Step 1: Topic selection
Create a `TopicCandidate` object:
```ts
type TopicCandidate = {
  id: string
  source: 'internal-data' | 'rss' | 'competitor' | 'manual' | 'analytics-gap'
  niche: string
  angle: string
  evidence: string[]
  freshnessScore: number
  evergreenScore: number
  noveltyScore: number
  riskScore: number
  expectedFormat: 'short' | 'long'
}
```

Rules:
- reject if too close to last 20 uploads
- reject if angle can only be executed as slideshow + TTS
- reject if source packet is weak
- rank by `expected_watchtime_gain`, not just click potential

### Step 2: Research packet
Generate and persist:
```json
{
  "topic_id": "...",
  "thesis": "...",
  "supporting_points": ["...", "..."],
  "required_visuals": ["chart", "b-roll", "screen capture"],
  "disallowed_claims": ["guaranteed return", "unverified allegation"],
  "requires_human_review": true
}
```

If the repo already has scraping/data-collection logic, this is where it plugs in.

### Step 3: Script + storyboard
Produce:
- hook variants
- full narration
- shot list
- on-screen text
- CTA
- thumbnail hypotheses

Do **not** let the generator output a “read this article aloud” script. YouTube’s monetization policies explicitly call out readings of other materials/news feeds and image slideshows with minimal narrative/commentary as risky or ineligible for monetization if they become repetitive or mass-produced. ([support.google.com](https://support.google.com/youtube/answer/1311392?utm_source=openai))

### Step 4: Asset generation
Build an `AssetManifest`:
- voiceover file
- music bed
- charts/graphs
- stock clips
- screenshots
- captions
- thumbnail layers

Store rights/provenance per asset:
```json
{
  "asset_id": "...",
  "type": "image",
  "source": "internal-chart-generator",
  "license": "owned",
  "attribution_required": false
}
```

### Step 5: Render
Have one renderer interface:
```ts
interface VideoRenderer {
  render(jobId: string, manifestId: string): Promise<RenderResult>
}
```

Then you can swap implementations:
- FFmpeg pipeline
- Remotion
- MoviePy
- After Effects automation
- external render service

### Step 6: QC / policy gate
Before upload, compute:
- duration
- audio loudness
- caption coverage
- title uniqueness
- thumbnail uniqueness
- script similarity to old videos
- disclosure flags
- third-party media risk
- “mass-produced” risk

Fail closed:
- if similarity too high, block
- if source provenance missing, block
- if realistic synthetic media and disclosure unset, block

### Step 7: Upload privately, then schedule
Always upload as `private` first.
Then:
- poll processing
- set thumbnail
- add playlist
- set `publishAt`
- mark scheduled

That gives you a final human or automated QC window.

### Step 8: Analytics ingest
Pull metrics daily into `video_metrics_daily`.

Useful features:
- `views_1d`, `views_7d`, `views_28d`
- `averageViewDuration`
- `estimatedMinutesWatched`
- `likes`, `comments`, `shares`
- `subscribersGained`
- retention breakpoints if you later expand reporting

The YouTube Analytics API’s `reports.query` supports targeted queries over a date range with metrics, dimensions, filters, and sorting, and lets you filter up to 500 video IDs in one request. The API also notes that daily reports can lag for the most recent days, so don’t optimize on “today” data alone. ([developers.google.com](https://developers.google.com/youtube/analytics/reference/reports/query))

### Step 9: Feedback
Use analytics to update:
- which hooks work
- which lengths work
- which visual patterns work
- which publish slots work
- which topics underperform despite high CTR
- which topics drive subs/watch time

That feedback loop is what turns a generator into a machine.

## 4) Official YouTube API integration: the right way

### Auth model
For an internal automation tool, use a **desktop/installed-app** or **server-side web app OAuth 2.0 flow** and store refresh tokens securely. Do **not** try to use service accounts; YouTube Data API does not support them. ([developers.google.com](https://developers.google.com/youtube/v3/guides/auth/installed-apps))

Recommended scopes for this repo’s publisher:
- `youtube.upload` for uploads
- `youtube.force-ssl` if you also want playlist/comment/write operations
- `youtube.readonly` because `reports.query` now requires it
- `yt-analytics.readonly` for analytics reports ([developers.google.com](https://developers.google.com/youtube/v3/docs/playlistItems/insert?utm_source=openai))

### Upload flow
Use **resumable upload**, not one-shot upload, and persist the upload session URL against the job so a worker crash doesn’t waste the upload. YouTube officially documents resumable uploads for reliability, especially on large files or unstable connections. ([developers.google.com](https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol?utm_source=openai))

### Metadata fields to set
At minimum on publish jobs:
- title
- description
- privacy status
- tags/category if relevant
- made-for-kids flag if applicable
- synthetic media disclosure if applicable
- publish time if scheduling

The `video` resource supports `status.selfDeclaredMadeForKids`, `status.containsSyntheticMedia`, and `status.publishAt`; `publishAt` only works for private videos and effectively schedules release. ([developers.google.com](https://developers.google.com/youtube/v3/docs/videos))

### Upload constraints / quotas
As of **December 4, 2025**, a `videos.insert` upload costs about **100 quota units**, and projects typically start with **10,000 units/day**. `thumbnails.set` and `playlistItems.insert` are **50 units** each. That means a full publish flow with upload + thumbnail + playlist + a few status polls is still practical, but you should budget it explicitly. ([developers.google.com](https://developers.google.com/youtube/v3/revision_history))

A rough budget:
- upload: 100
- thumbnail: 50
- playlist insert: 50
- 5 status polls: 5

That’s ~205 units/video, or roughly **48 completed publish jobs/day** on default quota if you did nothing else. ([developers.google.com](https://developers.google.com/youtube/v3/getting-started?utm_source=openai))

### Important gotcha: private-only uploads for unverified projects
If your API project was created **after July 28, 2020** and is still unverified, videos uploaded through `videos.insert` are restricted to **private** until the project passes a compliance audit. If this repo is meant to auto-publish publicly, this is a gating issue from day one. ([developers.google.com](https://developers.google.com/youtube/v3/docs/videos/insert?utm_source=openai))

### If this repo exposes uploads to other users
YouTube’s Required Minimum Functionality says upload-capable API clients must allow users to set title, description, and privacy status, and developer policies require clear identification of write actions and visibility settings. If this repo will be used by a team or clients, build that UI explicitly. ([developers.google.com](https://developers.google.com/youtube/terms/required-minimum-functionality))

## 5) Compliance / policy risks you need to design around

### Synthetic media
YouTube requires disclosure when content is meaningfully altered or synthetically generated **and seems realistic**. Examples that require disclosure include cloned voices, altered real events/places, and realistic synthetic scenes; minor aesthetic edits, captions, upscaling, audio repair, or using AI to help draft a script/title/thumbnail generally do not require disclosure by themselves. The API now exposes `status.containsSyntheticMedia` for this. ([support.google.com](https://support.google.com/youtube/answer/14328491?co=GENIE.Platform%3DDesktop&hl=en))

**Implementation rule:** if your renderer uses cloned voices, realistic AI footage, or photoreal generated scenes, set a `requiresSyntheticDisclosure` flag during QC and refuse upload until it’s mapped to the YouTube metadata.

### Repetitive / mass-produced content
YouTube’s monetization policies now frame this as **inauthentic content**: mass-produced or repetitive videos with little meaningful variation are not eligible for monetization. They specifically call out readings of others’ materials, template-driven near-duplicates, and image slideshows with minimal narrative/commentary as bad patterns. ([support.google.com](https://support.google.com/youtube/answer/1311392?utm_source=openai))

**Implementation rule:** your repo should enforce:
- script similarity threshold
- title similarity threshold
- thumbnail-template variation threshold
- minimum “original commentary” density
- minimum visual novelty per video

### Reused content / copyright
Even if content is “transformed,” copyright still applies, and reused-content monetization reviews are separate from copyright claims. Commentary can help, but it is not a blanket shield. ([support.google.com](https://support.google.com/youtube/answer/1311392?utm_source=openai))

**Implementation rule:** add an `asset_rights` ledger and ban unknown-license media from final renders.

### Financial-content warning
Given the repo name, if this is finance/investing content, add a higher-risk review path for:
- promises of returns
- regulated advice language
- unsupported claims
- thumbnail/title sensationalism

That’s not a YouTube-only issue; it’s broader legal/compliance risk.

## 6) The 5 highest-leverage code changes

### 1. Add a durable `content_jobs` workflow layer
Highest leverage because it makes the whole system restartable, observable, and debuggable.

Build:
- DB tables
- job states
- retry rules
- per-stage artifacts
- failure reasons

Without this, the repo will become a pile of scripts.

### 2. Add a `policy_guard` package before render and before upload
This should check:
- duplicate topics
- repetitive structure
- disclosure needs
- asset rights
- risky claims

This is the single best protection against demonetization and channel-quality drift. ([support.google.com](https://support.google.com/youtube/answer/1311392?utm_source=openai))

### 3. Add a dedicated `youtube_publisher` module
Not scattered API calls.

Responsibilities:
- OAuth bootstrap
- token refresh
- resumable upload
- video metadata mapping
- thumbnail upload
- playlist insert
- schedule publish
- poll processing

Use official APIs only; don’t automate browser clicks for uploads if you can avoid it. The official Data API supports upload, thumbnail set, and playlist insertion directly. ([developers.google.com](https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol?utm_source=openai))

### 4. Add an `analytics_feedback` worker
Pull channel/video metrics nightly and write back into:
- topic ranker weights
- template success rates
- publish-slot recommendations
- title/thumbnail experiments

Use targeted Analytics API queries first; only add the Reporting API if you need bulk historical dumps at scale. The official docs distinguish the Analytics API for targeted queries from the Reporting API for bulk reports. ([developers.google.com](https://developers.google.com/youtube/analytics/reference/reports/query?utm_source=openai))

### 5. Separate “research,” “script,” “assets,” and “render” into explicit interfaces
This lets you swap models/tools without breaking the system.

For example:
```ts
interface TopicSelector {}
interface ResearchBuilder {}
interface ScriptWriter {}
interface AssetBuilder {}
interface Renderer {}
interface Publisher {}
interface MetricsIngestor {}
```

That separation is what makes the repo maintainable once you start experimenting.

## 7) My blunt recommendation

Do **not** optimize first for “fully automatic uploads.”
Optimize first for:

1. good topic selection  
2. strong originality checks  
3. private upload + scheduled publish  
4. daily analytics feedback  
5. only then reduce human review

That sequence is much safer for both channel quality and YouTube compliance.

---

If you want the actual **repo-specific** version, send me one of these:

1. `tree -a -L 3 /Users/gallagherpropertycompany/Desktop/the-money-map`
2. the main manifests (`package.json`, `requirements.txt`, `pyproject.toml`, etc.)
3. the main app/worker entrypoints
4. any existing render/upload scripts

Then I’ll rewrite this as:
- **current strengths already present in your repo**
- **missing modules by filename/folder**
- **exact new files to add**
- **specific refactors**
- **diff-level highest-leverage changes**