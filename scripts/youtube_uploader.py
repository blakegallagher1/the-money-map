"""
YouTube Upload Module for The Money Map.
Uses YouTube Studio upload via browser automation.
Handles: video upload, metadata (title, description, tags), thumbnail.
"""
import json
import os
import sys
import subprocess
from datetime import datetime

sys.path.insert(0, '/home/user/workspace/the-money-map')


class YouTubeUploader:
    """Handles uploading videos to The Money Map YouTube channel."""
    
    def __init__(self):
        self.channel_email = "yredstick@gmail.com"
        self.channel_password = "Nola0528!"
        self.channel_name = "The Money Map"
    
    def prepare_upload_package(self, script_data, video_path, thumbnail_path):
        title = script_data['title']
        description = script_data['description']
        tags = script_data.get('tags', [])
        
        if len(title) > 100:
            title = title[:97] + "..."
        
        if len(description) > 5000:
            description = description[:4997] + "..."
        
        package = {
            'title': title,
            'description': description,
            'tags': tags[:30],
            'video_path': os.path.abspath(video_path),
            'thumbnail_path': os.path.abspath(thumbnail_path),
            'category': 'Education',
            'visibility': 'public',
            'language': 'en',
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        }
        
        pkg_path = '/home/user/workspace/the-money-map/data/upload_package.json'
        with open(pkg_path, 'w') as f:
            json.dump(package, f, indent=2)
        
        return package
    
    def get_upload_instructions(self, package):
        tags_str = ', '.join(package['tags'][:15])
        
        instructions = f"""
Upload a video to YouTube Studio for The Money Map channel.

1. Go to https://studio.youtube.com
2. Sign in with: {self.channel_email} / {self.channel_password}
3. Click CREATE → Upload videos
4. Upload: {package['video_path']}
5. Title: {package['title']}
6. Description: {package['description']}
7. Tags: {tags_str}
8. Audience: Not made for kids
9. Visibility: {package['visibility']}
10. Thumbnail: {package['thumbnail_path']}
11. Publish

Return the video URL once published.
"""
        return instructions


def prepare_for_upload():
    script_path = '/home/user/workspace/the-money-map/data/latest_script.json'
    video_path = '/home/user/workspace/the-money-map/output/pilot_episode.mp4'
    thumb_path = '/home/user/workspace/the-money-map/output/thumbnail.png'
    
    with open(script_path) as f:
        script_data = json.load(f)
    
    uploader = YouTubeUploader()
    package = uploader.prepare_upload_package(script_data, video_path, thumb_path)
    instructions = uploader.get_upload_instructions(package)
    
    print("Upload package prepared:")
    print(f"  Title: {package['title']}")
    print(f"  Video: {package['video_path']}")
    print(f"  Thumbnail: {package['thumbnail_path']}")
    print(f"  Tags: {len(package['tags'])}")
    
    return package, instructions


if __name__ == "__main__":
    pkg, instr = prepare_for_upload()
    print(instr)
