"""
YouTube API Uploader for The Money Map
Automated video upload via YouTube Data API v3 with OAuth 2.0.

One-time browser auth for consent, then fully automated via refresh token.
Supports upload, thumbnail, and scheduled publishing.
"""
import json
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    YOUTUBE_CLIENT_SECRET_PATH,
    YOUTUBE_TOKEN_PATH,
    YOUTUBE_CATEGORY_ID,
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# YouTube API scopes needed
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

# Retry settings for resumable uploads
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 4, 8]


def _get_authenticated_service():
    """Build an authenticated YouTube API service using OAuth 2.0."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None

    # Load existing token
    if os.path.exists(YOUTUBE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_PATH, SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  Refreshing YouTube OAuth token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(YOUTUBE_CLIENT_SECRET_PATH):
                raise FileNotFoundError(
                    f"YouTube client secret not found at {YOUTUBE_CLIENT_SECRET_PATH}. "
                    f"Download it from Google Cloud Console → APIs & Services → Credentials."
                )
            print("  Starting OAuth flow — a browser window will open...")
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open(YOUTUBE_TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
        print(f"  Token saved to {YOUTUBE_TOKEN_PATH}")

    return build('youtube', 'v3', credentials=creds)


def upload_video(video_path, title, description, tags, thumbnail_path=None,
                 privacy="public", category_id=None, publish_at=None):
    """Upload a video to YouTube with metadata.

    Args:
        video_path: Path to the video file
        title: Video title (max 100 chars)
        description: Video description (max 5000 chars)
        tags: List of tags (max 30)
        thumbnail_path: Optional path to thumbnail image
        privacy: "public", "unlisted", or "private"
        category_id: YouTube category ID (default from settings)
        publish_at: ISO 8601 datetime for scheduled publishing (requires privacy="private")

    Returns:
        dict with video_id and video_url
    """
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    youtube = _get_authenticated_service()

    # Truncate title/description to YouTube limits
    title = title[:100]
    description = description[:5000]
    tags = tags[:30]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id or YOUTUBE_CATEGORY_ID,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    # Scheduled publishing
    if publish_at:
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_at

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"  Uploading: {title}")
    print(f"  File: {video_path} ({os.path.getsize(video_path) / 1024 / 1024:.1f} MB)")

    # Resumable upload with retries
    response = None
    for attempt in range(MAX_RETRIES):
        try:
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"  Upload progress: {progress}%")
            break
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF[attempt]
                print(f"  Upload error: {e}. Retrying in {wait}s...")
                time.sleep(wait)
                response = None
            else:
                raise RuntimeError(f"Upload failed after {MAX_RETRIES} attempts: {e}")

    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  Upload complete: {video_url}")

    # Set thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"  Setting thumbnail: {thumbnail_path}")
            thumb_media = MediaFileUpload(thumbnail_path, mimetype="image/png")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=thumb_media,
            ).execute()
            print("  Thumbnail set successfully")
        except Exception as e:
            print(f"  WARNING: Thumbnail upload failed: {e}")

    return {
        "video_id": video_id,
        "video_url": video_url,
        "title": title,
        "privacy": privacy,
        "publish_at": publish_at,
    }


def schedule_publish(video_id, publish_at):
    """Schedule an already-uploaded private video for future publishing.

    Args:
        video_id: YouTube video ID
        publish_at: ISO 8601 datetime string (e.g. "2026-03-10T14:00:00Z")
    """
    youtube = _get_authenticated_service()

    youtube.videos().update(
        part="status",
        body={
            "id": video_id,
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at,
            },
        },
    ).execute()

    print(f"  Video {video_id} scheduled for {publish_at}")


def main(argv=None):
    """CLI entrypoint for validating auth setup and bootstrapping token."""
    parser = argparse.ArgumentParser(
        description="Validate YouTube uploader credentials and bootstrap OAuth token."
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Only validate paths; do not launch browser OAuth flow.",
    )
    args = parser.parse_args(argv)

    print("YouTube API Uploader — The Money Map")
    print("=" * 40)
    print(f"Client secret: {YOUTUBE_CLIENT_SECRET_PATH}")
    print(f"Token path: {YOUTUBE_TOKEN_PATH}")

    if os.path.exists(YOUTUBE_TOKEN_PATH):
        print("Token exists — ready for automated uploads")
        return 0

    print("No token found — first run will require browser auth")

    if not os.path.exists(YOUTUBE_CLIENT_SECRET_PATH):
        print("\nSETUP INSTRUCTIONS:")
        print("1. Go to Google Cloud Console → APIs & Services → Credentials")
        print("2. Create an OAuth 2.0 Client ID (Desktop application)")
        print("3. Download the client secret JSON")
        print(f"4. Save it to: {YOUTUBE_CLIENT_SECRET_PATH}")
        print("5. Enable YouTube Data API v3 in your project")
        print("6. Run this script again to authenticate")
        return 1

    if args.no_auth:
        print("Auth flow skipped (--no-auth).")
        return 0

    print("Launching OAuth setup now...")
    _get_authenticated_service()
    print("OAuth setup complete — token saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
