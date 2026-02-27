# scripts/orchestrator.py
# ─────────────────────────────────────────────
# Full pipeline — orchestrates the weekly Money Map episode
# Run manually or via cron
# ─────────────────────────────────────────────

import os
import sys
import datetime
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import OUTPUT_DIR, GEMINI_API_KEY, TTS_VOICE, VIDEO_WIDTH, VIDEO_HEIGHT, FPS
from scripts.data_ingestion import FREDClient
from scripts.story_discovery import StoryDiscovery
from scripts.script_writer import ScriptWriter
from scripts.episode_renderer import EpisodeRenderer
from scripts.thumbnail_gen import generate_thumbnail
from scripts.youtube_uploader import YouTubeUploader


class MoneyMapOrchestrator:
    def __init__(self):
        self.fred_client = FREDClient()
        self.discovery   = None
        self.writer      = ScriptWriter()
        self.renderer    = EpisodeRenderer()
        self.uploader    = YouTubeUploader()

    def run(self, story_key: str = None, dry_run: bool = False) -> dict:
        """
        Full pipeline run.
        story_key: optional override to force a specific indicator
        dry_run:   if True, skip YouTube upload
        Returns a summary dict.
        """
        print("=" * 60)
        print("  THE MONEY MAP — Weekly Pipeline")
        print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        summary = {
            "run_at":       datetime.datetime.now().isoformat(),
            "story_key":    None,
            "story_label":  None,
            "story_score":  None,
            "video_title":  None,
            "video_path":   None,
            "thumbnail_path": None,
            "youtube_url":  None,
            "status":       "started",
            "error":        None,
        }

        try:
            # ── Step 1: Fetch data ─────────────────
            print("\n[STEP 1/6] Fetching FRED data...")
            fred_data = self.fred_client.fetch_all()
            print(f"  Fetched {len(fred_data)} indicators.")

            # ── Step 2: Discover story ─────────────
            print("\n[STEP 2/6] Discovering story...")
            self.discovery = StoryDiscovery(fred_data)
            if story_key:
                story = self.discovery.story_for_key(story_key)
                if not story:
                    raise ValueError(f"Story key not found: {story_key}")
            else:
                story = self.discovery.top_story()

            summary["story_key"]   = story["key"]
            summary["story_label"] = story["item"]["label"]
            summary["story_score"] = story["score"]
            print(f"  Story: {story['item']['label']}  (score={story['score']:.1f})")

            # ── Step 3: Write script ───────────────
            print("\n[STEP 3/6] Writing script...")
            script = self.writer.write_script(story)
            summary["video_title"] = script["title"]
            print(f"  Title: {script['title']}")

            # ── Step 4: Generate voiceover ─────────
            print("\n[STEP 4/6] Generating TTS voiceover...")
            timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path  = os.path.join(OUTPUT_DIR, f"audio_{timestamp}.mp3")
            audio_file  = self.renderer._generate_tts(script["script_text"], audio_path)
            print(f"  Audio: {audio_file}")

            # ── Step 5: Render video + thumbnail ───
            print("\n[STEP 5/6] Rendering episode video...")
            video_path = self.renderer._render_video(story, script, audio_file, timestamp)
            summary["video_path"] = video_path
            print(f"  Video: {video_path}")

            print("  Generating thumbnail...")
            thumb_path = os.path.join(OUTPUT_DIR, f"thumbnail_{timestamp}.png")
            generate_thumbnail(
                title=script["title"],
                indicator_label=story["item"]["label"],
                latest_value=f"{story['item']['latest']}{story['item']['unit']}",
                yoy_pct=story["item"]["yoy_pct"],
                out_path=thumb_path,
            )
            summary["thumbnail_path"] = thumb_path

            # ── Step 6: Upload to YouTube ──────────
            if dry_run:
                print("\n[STEP 6/6] Dry run — skipping YouTube upload.")
                summary["youtube_url"] = "(dry run — not uploaded)"
            else:
                print("\n[STEP 6/6] Uploading to YouTube...")
                yt_url = self.uploader.upload(video_path, thumb_path, script)
                summary["youtube_url"] = yt_url
                print(f"  YouTube URL: {yt_url}")

            summary["status"] = "success"

        except Exception as e:
            summary["status"] = "error"
            summary["error"]  = str(e)
            print(f"\n[ERROR] Pipeline failed: {e}")
            traceback.print_exc()

        # ── Print summary ──────────────────────────
        print("\n" + "=" * 60)
        print("  PIPELINE SUMMARY")
        print("=" * 60)
        for k, v in summary.items():
            print(f"  {k:20s}: {v}")

        return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Money Map pipeline")
    parser.add_argument("--story",   type=str,  default=None,  help="Force a specific story key")
    parser.add_argument("--dry-run", action="store_true",      help="Skip YouTube upload")
    args = parser.parse_args()

    orch = MoneyMapOrchestrator()
    result = orch.run(story_key=args.story, dry_run=args.dry_run)

    if result["status"] == "error":
        sys.exit(1)
