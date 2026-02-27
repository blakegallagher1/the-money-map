# scripts/episode_renderer.py
# ─────────────────────────────────────────────
# Generalized renderer — produces any episode from a story key
# Usage: python scripts/episode_renderer.py [--story STORY_KEY]
# ─────────────────────────────────────────────

import os
import sys
import argparse
import datetime
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import OUTPUT_DIR, GEMINI_API_KEY, TTS_VOICE, VIDEO_WIDTH, VIDEO_HEIGHT, FPS
from scripts.video_renderer import (
    build_title_card, build_stat_callout, build_chart_clip,
    build_comparison_dashboard, build_closing_card, hex_to_rgb, COLOR_BG
)
from scripts.data_ingestion import FREDClient
from scripts.story_discovery import StoryDiscovery
from scripts.script_writer import ScriptWriter

import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)


class EpisodeRenderer:
    def __init__(self):
        self.fred_client  = FREDClient()
        self.writer       = ScriptWriter()

    # ── Public API ────────────────────────────

    def render(self, story_key: str = None) -> str:
        """
        Full pipeline: fetch data → discover/pick story → write script → TTS → render → save.
        If story_key is None, auto-selects the top story.
        Returns path to output video.
        """
        print("=" * 60)
        print(f"  THE MONEY MAP — Episode Renderer")
        print("=" * 60)

        # 1. Fetch data
        print("\n[1/5] Fetching FRED data...")
        fred_data = self.fred_client.fetch_all()

        # 2. Discover story
        print("\n[2/5] Discovering story...")
        discovery = StoryDiscovery(fred_data)
        if story_key:
            story = discovery.story_for_key(story_key)
            if not story:
                raise ValueError(f"Story key '{story_key}' not found in FRED data.")
        else:
            story = discovery.top_story()
        print(f"  Story: {story['item']['label']}  (score={story['score']:.1f})")

        # 3. Write script
        print("\n[3/5] Writing script with Gemini...")
        script = self.writer.write_script(story)
        print(f"  Title: {script['title']}")

        # 4. TTS
        print("\n[4/5] Generating TTS voiceover...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join(OUTPUT_DIR, f"episode_audio_{timestamp}.mp3")
        audio_file = self._generate_tts(script["script_text"], audio_path)
        print(f"  Audio: {audio_file}")

        # 5. Render
        print("\n[5/5] Rendering video...")
        video_path = self._render_video(story, script, audio_file, timestamp)
        print(f"\n✓ Episode saved to:\n  {video_path}")
        return video_path

    # ── TTS ───────────────────────────────────

    def _generate_tts(self, text: str, out_path: str) -> str:
        """Generate TTS with Gemini, save as WAV."""
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=genai.types.GenerateContentConfig(
                speech_config=genai.types.SpeechConfig(
                    voice_config=genai.types.VoiceConfig(
                        prebuilt_voice_config=genai.types.PrebuiltVoiceConfig(
                            voice_name=TTS_VOICE,
                        )
                    )
                )
            ),
        )
        audio_data = b""
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                audio_data += part.inline_data.data

        wav_path = out_path.replace(".mp3", ".wav")
        with wave.open(wav_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)
        return wav_path

    # ── Video assembly ────────────────────────

    def _render_video(self, story: dict, script: dict, audio_file: str, timestamp: str) -> str:
        from moviepy.editor import concatenate_videoclips, AudioFileClip, ColorClip

        item    = story["item"]
        related = story.get("related", [])

        # Build scenes
        title_clip = build_title_card(
            title=script["title"],
            indicator_label=item["label"],
            latest_value=f"{item['latest']}{item['unit']}",
            yoy_pct=item["yoy_pct"],
            duration=4.0,
        )
        stat_clip = build_stat_callout(
            label=item["label"],
            value=f"{item['latest']}{item['unit']}",
            yoy_pct=item["yoy_pct"],
            context_text=script["hook"] + " " + script["context"],
            duration=6.0,
        )
        chart_clip = build_chart_clip(
            dates=item["dates"],
            values=item["values"],
            label=item["label"],
            unit=item["unit"],
            yoy_pct=item["yoy_pct"],
            duration=10.0,
        )
        dashboard_clip = build_comparison_dashboard(
            main_item=item,
            related=related,
            duration=6.0,
        )
        closing_clip = build_closing_card(duration=4.0)

        # Concatenate
        video = concatenate_videoclips(
            [title_clip, stat_clip, chart_clip, dashboard_clip, closing_clip],
            method="compose"
        )

        # Attach audio
        audio = AudioFileClip(audio_file)
        if audio.duration > video.duration:
            pad = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=hex_to_rgb(COLOR_BG),
                duration=audio.duration - video.duration
            )
            video = concatenate_videoclips([video, pad])
        else:
            audio = audio.subclip(0, video.duration)
        video = video.set_audio(audio)

        # Export
        video_path = os.path.join(OUTPUT_DIR, f"episode_{timestamp}.mp4")
        video.write_videofile(
            video_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(OUTPUT_DIR, "temp_audio.m4a"),
            remove_temp=True,
            logger=None,
        )
        return video_path


# ── CLI ───────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render a Money Map episode")
    parser.add_argument(
        "--story", type=str, default=None,
        help="FRED story key (e.g. MORTGAGE_RATE_30Y). Omit to auto-select top story."
    )
    args = parser.parse_args()

    renderer = EpisodeRenderer()
    out_path = renderer.render(story_key=args.story)
    print(f"\nDone! Video: {out_path}")
