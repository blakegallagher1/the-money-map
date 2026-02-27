"""
The Money Map — Cron-Ready Pipeline Instructions

This file contains the instructions the Perplexity Computer cron agent
will follow each week to produce and upload a new episode.

The pipeline runs every Monday at 8:00 AM CST (14:00 UTC).
"""

WEEKLY_PIPELINE_INSTRUCTIONS = """
You are the automated producer for "The Money Map" YouTube channel.
Run the full weekly episode pipeline:

## Step 1: Fetch Fresh Data
```
cd /home/user/workspace/the-money-map
python -c "
from scripts.data_ingestion import FREDClient
import json
client = FREDClient()
result = client.fetch_all()
with open('data/latest_data.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Fetched {len(result[\"data\"])} indicators')
"
```

## Step 2: Discover Story
```
python -c "
from scripts.story_discovery import build_story_package
pkg = build_story_package('data/latest_data.json')
print(f'Top story: {pkg[\"primary\"][\"name\"]}')
print(f'YoY: {pkg[\"primary\"][\"yoy_pct\"]:.1f}%')
"
```

## Step 3: Generate Script
```
python -c "
from scripts.story_discovery import build_story_package
from scripts.script_writer import generate_script
import json
pkg = build_story_package('data/latest_data.json')
script = generate_script(pkg)
with open('data/latest_script.json', 'w') as f:
    json.dump(script, f, indent=2)
with open('data/voiceover_script.txt', 'w') as f:
    f.write(script['script'])
print(f'Title: {script[\"title\"]}')
"
```

## Step 4: Generate Voiceover (Automated)
Voiceover is now generated automatically via OpenAI gpt-4o-mini-tts.
Requires OPENAI_API_KEY environment variable to be set.
```
python -c "
from scripts.tts_generator import generate_voiceover
path = generate_voiceover()
print(f'Voiceover saved: {path}')
"
```

## Step 5: Render Video
```
python scripts/render_pilot.py
```

## Step 6: Generate Thumbnail
```
python -c "
from scripts.thumbnail_gen import generate_thumbnail
import json
with open('data/latest_script.json') as f:
    script = json.load(f)
generate_thumbnail(script, 'output/thumbnail.png')
"
```

## Step 7: Upload to YouTube
- URL: https://studio.youtube.com
- Login: yredstick@gmail.com / Nola0528!
- Upload: output/pilot_episode.mp4
- Title/description from data/latest_script.json
- Thumbnail: output/thumbnail.png
- Not made for kids, Public visibility
- Publish

## Step 8: Notify
Send a notification with the episode title and YouTube link.
"""

if __name__ == "__main__":
    print("The Money Map — Cron Pipeline Instructions")
    print("=" * 50)
    print(WEEKLY_PIPELINE_INSTRUCTIONS)
