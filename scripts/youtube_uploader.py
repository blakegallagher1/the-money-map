# scripts/youtube_uploader.py
# ─────────────────────────────────────────────
# Uploads video + thumbnail to YouTube with optimized metadata
# ─────────────────────────────────────────────

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_CREDENTIALS_FILE

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploader:
    def __init__(self):
        self.youtube = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(YOUTUBE_CREDENTIALS_FILE):
            creds = Credentials.from_authorized_user_file(YOUTUBE_CREDENTIALS_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(YOUTUBE_CREDENTIALS_FILE, "w") as f:
                f.write(creds.to_json())
        return build("youtube", "v3", credentials=creds)

    def upload(self, video_path: str, thumbnail_path: str, script: dict) -> str:
        """
        Upload video + thumbnail to YouTube.
        Returns the YouTube video URL.
        """
        print(f"  Uploading video: {video_path}")

        body = {
            "snippet": {
                "title":       script["title"],
                "description": script["description"],
                "tags":        script["tags"],
                "categoryId":  "25",   # News & Politics
            },
            "status": {
                "privacyStatus": "public",
            },
        }

        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"    Upload progress: {int(status.progress() * 100)}%")

        video_id = response["id"]
        print(f"  Video uploaded: https://youtube.com/watch?v={video_id}")

        # Upload thumbnail
        if os.path.exists(thumbnail_path):
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print(f"  Thumbnail uploaded.")

        return f"https://youtube.com/watch?v={video_id}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python youtube_uploader.py <video_path> <thumbnail_path>")
        sys.exit(1)
    video_path     = sys.argv[1]
    thumbnail_path = sys.argv[2]
    # Minimal test script
    script = {
        "title":       "Test Upload — The Money Map",
        "description": "Test upload.",
        "tags":        ["test", "the money map"],
    }
    uploader = YouTubeUploader()
    url = uploader.upload(video_path, thumbnail_path, script)
    print(f"Video URL: {url}")
