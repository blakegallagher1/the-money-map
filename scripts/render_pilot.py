# scripts/render_pilot.py
# ─────────────────────────────────────────────
# Render the PILOT episode for The Money Map
# Hard-coded to 30-Year Mortgage Rate story
# ─────────────────────────────────────────────

import os
import sys
import datetime
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import OUTPUT_DIR, GEMINI_API_KEY, TTS_VOICE
from scripts.video_renderer import (
    build_title_card, build_stat_callout, build_chart_clip,
    build_comparison_dashboard, build_closing_card
)

import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

# ── Pilot story data (hard-coded for demo) ────

STORY = {
    "key": "MORTGAGE_RATE_30Y",
    "item": {
        "label":        "30-Year Mortgage Rate",
        "latest":       6.81,
        "unit":         "%",
        "yoy_pct":      -3.8,
        "yoy_change":   -0.27,
        "category":     "Housing",
        "dates":        ["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01",
                         "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01",
                         "2023-09-01", "2023-10-01", "2023-11-01", "2023-12-01",
                         "2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01",
                         "2024-05-01", "2024-06-01", "2024-07-01", "2024-08-01",
                         "2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01"],
        "values":       [6.27, 6.65, 6.73, 6.79, 6.79, 6.71, 6.81, 7.09,
                         7.20, 7.79, 7.44, 6.95, 6.62, 6.90, 6.87, 7.17,
                         7.22, 7.03, 6.78, 6.50, 6.20, 6.72, 6.81, 6.97],
    },
    "related": [
        {"key": "MORTGAGE_RATE_15Y", "label": "15-Year Mortgage Rate", "latest": 6.10, "unit": "%", "yoy_pct": -4.2},
        {"key": "HOME_SALES_EXISTING", "label": "Existing Home Sales",  "latest": 3.96, "unit": "M", "yoy_pct": +2.9},
        {"key": "HOUSING_STARTS",     "label": "Housing Starts",        "latest": 1354, "unit": "K", "yoy_pct": -4.1},
    ],
    "score": 87.4,
    "category": "Housing",
}

SCRIPT = {
    "title": "Mortgage Rates Hit 6.81%: Is Housing Finally Cooling Down?",
    "hook":    "Mortgage rates are sitting at 6.81 percent — still more than double the lows we saw in 2021.",
    "context": "For the average American buying a 400-thousand-dollar home, that means monthly payments are roughly 800 dollars higher than they were just three years ago. The Fed has paused rate hikes, but the housing market hasn't caught its breath yet.",
    "related": "Meanwhile, 15-year mortgage rates are at 6.10 percent. Existing home sales inched up 2.9 percent year-over-year to 3.96 million — but housing starts fell 4.1 percent, meaning builders aren't keeping pace with demand.",
    "insight":  "With rates above 6.5 percent, affordability remains near historic lows. Economists expect gradual rate relief in 2025, but a true housing recovery requires rates closer to 5 percent. Until then, the lock-in effect keeps inventory tight.",
    "close":   "That's your Money Map for this week. If you want to understand where the economy is actually heading, hit subscribe — we drop new data every week.",
    "script_text": "",
    "tags": ["mortgage rates 2024", "housing market update", "30 year mortgage", "fed rate decision",
             "housing affordability", "real estate 2024", "interest rates", "home prices",
             "the money map", "economic data"],
    "description": "Mortgage rates are at 6.81% — more than double the 2021 lows. We break down what this means for homebuyers, the housing market, and when rates might finally come down. Data sourced directly from the Federal Reserve (FRED).",
    "segments": [
        {"name": "hook",    "text": "Mortgage rates are sitting at 6.81 percent — still more than double the lows we saw in 2021."},
        {"name": "context", "text": "For the average American buying a 400-thousand-dollar home, that means monthly payments are roughly 800 dollars higher than they were just three years ago. The Fed has paused rate hikes, but the housing market hasn't caught its breath yet."},
        {"name": "related", "text": "Meanwhile, 15-year mortgage rates are at 6.10 percent. Existing home sales inched up 2.9 percent year-over-year to 3.96 million — but housing starts fell 4.1 percent, meaning builders aren't keeping pace with demand."},
        {"name": "insight",  "text": "With rates above 6.5 percent, affordability remains near historic lows. Economists expect gradual rate relief in 2025, but a true housing recovery requires rates closer to 5 percent. Until then, the lock-in effect keeps inventory tight."},
        {"name": "close",   "text": "That's your Money Map for this week. If you want to understand where the economy is actually heading, hit subscribe — we drop new data every week."},
    ],
}

# Assemble full script text
SCRIPT["script_text"] = " ".join(s["text"] for s in SCRIPT["segments"])


# ── TTS ───────────────────────────────────────

def generate_tts(text: str, out_path: str) -> str:
    """Generate TTS audio using Gemini and save as MP3 to out_path."""
    import wave, struct

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

    # Save as WAV then convert path (MoviePy reads WAV fine)
    wav_path = out_path.replace(".mp3", ".wav")
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # 16-bit
        wf.setframerate(24000)
        wf.writeframes(audio_data)

    return wav_path


# ── Main render ───────────────────────────────

def render_pilot():
    from moviepy.editor import concatenate_videoclips, AudioFileClip, CompositeVideoClip

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(OUTPUT_DIR, f"pilot_{timestamp}.mp4")
    audio_path = os.path.join(OUTPUT_DIR, f"pilot_audio_{timestamp}.mp3")

    print("=" * 60)
    print("  THE MONEY MAP — PILOT RENDER")
    print("=" * 60)

    # ── 1. TTS ────────────────────────────────
    print("\n[1/4] Generating TTS voiceover...")
    audio_file = generate_tts(SCRIPT["script_text"], audio_path)
    print(f"  Audio saved to {audio_file}")

    # ── 2. Build video scenes ─────────────────
    print("\n[2/4] Building video scenes...")
    item = STORY["item"]

    title_clip = build_title_card(
        title=SCRIPT["title"],
        indicator_label=item["label"],
        latest_value=f"{item['latest']}{item['unit']}",
        yoy_pct=item["yoy_pct"],
        duration=4.0,
    )
    stat_clip = build_stat_callout(
        label=item["label"],
        value=f"{item['latest']}{item['unit']}",
        yoy_pct=item["yoy_pct"],
        context_text=SCRIPT["hook"] + " " + SCRIPT["context"],
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
        related=STORY["related"],
        duration=6.0,
    )
    closing_clip = build_closing_card(duration=4.0)
    print("  Scenes built.")

    # ── 3. Assemble with audio ─────────────────
    print("\n[3/4] Assembling video with voiceover...")
    video = concatenate_videoclips(
        [title_clip, stat_clip, chart_clip, dashboard_clip, closing_clip],
        method="compose"
    )
    audio = AudioFileClip(audio_file)
    # Trim or pad video to match audio length
    if audio.duration > video.duration:
        from moviepy.editor import ColorClip
        pad = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                        color=hex_to_rgb(COLOR_BG),
                        duration=audio.duration - video.duration)
        video = concatenate_videoclips([video, pad])
    else:
        audio = audio.subclip(0, video.duration)
    video = video.set_audio(audio)
    print("  Assembly complete.")

    # ── 4. Export ─────────────────────────────
    print(f"\n[4/4] Exporting to {video_path}...")
    video.write_videofile(
        video_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=os.path.join(OUTPUT_DIR, "temp_audio.m4a"),
        remove_temp=True,
        logger=None,
    )
    print(f"\n✓ Pilot video saved to:\n  {video_path}")
    return video_path


if __name__ == "__main__":
    render_pilot()
