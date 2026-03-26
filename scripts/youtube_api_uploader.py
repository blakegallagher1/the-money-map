"""
YouTube API Uploader for The Money Map
Automated video upload via YouTube Data API v3 with OAuth 2.0.

One-time browser auth for consent, then fully automated via refresh token.
Supports upload, thumbnail, and scheduled publishing.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    YOUTUBE_CLIENT_SECRET_PATH,
    YOUTUBE_TOKEN_PATH,
    YOUTUBE_CATEGORY_ID,
    YOUTUBE_PROCESSING_POLL_SECONDS,
    YOUTUBE_PROCESSING_TIMEOUT_SECONDS,
)

# YouTube API scopes needed
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

# Retry settings for resumable uploads
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 4, 8]
SUCCESS_PROCESSING_STATES = {"success", "processed"}
ERROR_PROCESSING_STATES = {"failed", "terminated", "rejected"}


def _fetch_video_status(youtube, video_id: str) -> dict[str, str | None]:
    """Fetch processing/visibility metadata for a YouTube upload."""
    response = youtube.videos().list(
        part="status,processingDetails",
        id=video_id,
    ).execute()

    items = response.get("items") or []
    if not items:
        raise RuntimeError(f"Uploaded video not found in status check: {video_id}")

    status = items[0].get("status") or {}
    processing = items[0].get("processingDetails") or {}
    upload_status = status.get("uploadStatus")
    processing_status = processing.get("processingStatus")
    return {
        "uploadStatus": upload_status,
        "processingStatus": processing_status,
        "privacyStatus": status.get("privacyStatus"),
        "publishAt": status.get("publishAt"),
    }


def _wait_for_processing(
    youtube,
    video_id: str,
    *,
    timeout_seconds: int = YOUTUBE_PROCESSING_TIMEOUT_SECONDS,
    poll_interval: int = YOUTUBE_PROCESSING_POLL_SECONDS,
) -> dict[str, str | None]:
    """Wait until video processing reaches a terminal state."""
    start = time.time()
    last_printed = None
    while time.time() - start < timeout_seconds:
        status = _fetch_video_status(youtube, video_id)
        key = f"{status['uploadStatus']}/{status['processingStatus']}"
        if key != last_printed:
            print(f"  Processing status: {key}")
            last_printed = key

        processing_status = (status.get("processingStatus") or "").lower()
        upload_status = (status.get("uploadStatus") or "").lower()

        if processing_status in SUCCESS_PROCESSING_STATES:
            return status

        if processing_status in ERROR_PROCESSING_STATES:
            raise RuntimeError(f"Video processing failed (processingStatus={processing_status})")

        if upload_status == "processed" and processing_status in (None, "", "completed"):
            return status

        time.sleep(poll_interval)

    raise TimeoutError(
        f"Video did not finish processing after {timeout_seconds}s: video_id={video_id}"
    )


def _set_thumbnail_if_ready(youtube, video_id: str, thumbnail_path: str | None):
    """Upload thumbnail only after the upload is fully processed."""
    if not (thumbnail_path and os.path.exists(thumbnail_path)):
        return

    from googleapiclient.http import MediaFileUpload

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
        return

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

    from googleapiclient.http import MediaFileUpload

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

    # Ensure the media pipeline has processed the video before downstream steps.
    processing_status = _wait_for_processing(
        youtube,
        video_id,
        timeout_seconds=YOUTUBE_PROCESSING_TIMEOUT_SECONDS,
        poll_interval=YOUTUBE_PROCESSING_POLL_SECONDS,
    )

    _set_thumbnail_if_ready(youtube, video_id, thumbnail_path)

    status_payload = {
        "video_id": video_id,
        "video_url": video_url,
        "title": title,
        "privacy": privacy,
        "publish_at": publish_at,
        "upload_status": processing_status.get("uploadStatus"),
        "processing_status": processing_status.get("processingStatus"),
    }

    status_payload["status_message"] = "processing-complete"

    status_payload["status_details"] = (
        f"uploadStatus={processing_status.get('uploadStatus')}, "
        f"processingStatus={processing_status.get('processingStatus')}, "
        f"publishAt={processing_status.get('publishAt')}"
    )
    return status_payload


def schedule_publish(video_id, publish_at):
    """Schedule an already-uploaded private video for future publishing.

    Args:
        video_id: YouTube video ID
        publish_at: ISO 8601 datetime string (e.g. "2026-03-10T14:00:00Z")
    """
    youtube = _get_authenticated_service()

    response = youtube.videos().update(
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
    return response


if __name__ == "__main__":
    print("YouTube API Uploader — The Money Map")
    print("=" * 40)
    print(f"Client secret: {YOUTUBE_CLIENT_SECRET_PATH}")
    print(f"Token path: {YOUTUBE_TOKEN_PATH}")

    if os.path.exists(YOUTUBE_TOKEN_PATH):
        print("Token exists — ready for automated uploads")
    else:
        print("No token found — first run will require browser auth")

    if not os.path.exists(YOUTUBE_CLIENT_SECRET_PATH):
        print("\nSETUP INSTRUCTIONS:")
        print("1. Go to Google Cloud Console → APIs & Services → Credentials")
        print("2. Create an OAuth 2.0 Client ID (Desktop application)")
        print("3. Download the client secret JSON")
        print(f"4. Save it to: {YOUTUBE_CLIENT_SECRET_PATH}")
        print("5. Enable YouTube Data API v3 in your project")
        print("6. Run this script again to authenticate")
