#!/usr/bin/env python3
"""Upload a rendered MP4 to YouTube privately and optionally schedule it."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class PublishError(RuntimeError):
    """A user-actionable publish error."""


def path_value(raw: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    windows_match = re.match(r"^([A-Za-z]):[\\/](.*)$", expanded)
    if windows_match:
        drive, rest = windows_match.groups()
        return (Path("/mnt") / drive.lower() / rest.replace("\\", "/")).resolve()
    return Path(expanded).resolve()


def parse_datetime(raw: str) -> datetime:
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise PublishError("--schedule-at must be ISO 8601, for example 2026-09-14T22:00:00+09:00") from exc
    if parsed.tzinfo is None:
        raise PublishError("--schedule-at must include a timezone offset or Z")
    return parsed.astimezone(timezone.utc)


def load_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublishError(f"Metadata file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PublishError(f"Metadata is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PublishError("Metadata root must be a JSON object")
    title = data.get("title")
    description = data.get("description")
    made_for_kids = data.get("made_for_kids")
    if not isinstance(title, str) or not title.strip():
        raise PublishError("Metadata requires a non-empty string: title")
    if len(title) > 100:
        raise PublishError("Metadata title must be 100 characters or fewer")
    if not isinstance(description, str):
        raise PublishError("Metadata requires a string: description")
    if len(description) > 5000:
        raise PublishError("Metadata description must be 5000 characters or fewer")
    if not isinstance(made_for_kids, bool):
        raise PublishError("Metadata requires an explicit boolean: made_for_kids")
    tags = data.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(tag, str) and tag.strip() for tag in tags):
        raise PublishError("Metadata tags must be an array of non-empty strings")
    category_id = str(data.get("category_id", "10"))
    if not category_id.isdigit():
        raise PublishError("Metadata category_id must be a numeric string")
    return {
        "title": title.strip(),
        "description": description,
        "tags": tags,
        "category_id": category_id,
        "language": data.get("language"),
        "made_for_kids": made_for_kids,
    }


def validate_inputs(video: Path, metadata: Path, schedule_at: str | None) -> tuple[dict[str, Any], datetime | None]:
    if not video.is_file():
        raise PublishError(f"Video file not found: {video}")
    if video.suffix.lower() != ".mp4":
        raise PublishError("The publish script expects an MP4 render")
    if video.stat().st_size <= 0:
        raise PublishError("Video file is empty")
    metadata_data = load_metadata(metadata)
    schedule_dt = parse_datetime(schedule_at) if schedule_at else None
    if schedule_dt and schedule_dt <= datetime.now(timezone.utc):
        raise PublishError("--schedule-at must be in the future")
    return metadata_data, schedule_dt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, help="Rendered MP4 path")
    parser.add_argument("--metadata", required=True, help="Metadata JSON path")
    parser.add_argument("--schedule-at", help="Future ISO 8601 publish time")
    parser.add_argument("--token-file", default=os.environ.get("YOUTUBE_TOKEN_FILE", "~/.config/plozen/youtube-oauth.json"))
    parser.add_argument("--dry-run", action="store_true", help="Validate only; never contact YouTube")
    parser.add_argument("--confirm-schedule", action="store_true", help="Acknowledge the external scheduled-publish action")
    return parser


def load_credentials(token_file: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ModuleNotFoundError as exc:
        raise PublishError("Google client libraries are missing; install scripts/requirements.txt") from exc
    if not token_file.is_file():
        raise PublishError(f"OAuth token file not found: {token_file}; run youtube_auth.py first")
    try:
        credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        if not credentials.valid:
            if not credentials.expired or not credentials.refresh_token:
                raise PublishError("OAuth token is invalid or lacks a refresh token; run youtube_auth.py again")
            credentials.refresh(Request())
            token_file.write_text(credentials.to_json() + "\n", encoding="utf-8")
            token_file.chmod(0o600)
        if not credentials.has_scopes(SCOPES):
            raise PublishError("OAuth token does not include the YouTube upload scope; run youtube_auth.py again")
        return credentials
    except PublishError:
        raise
    except Exception as exc:
        raise PublishError(f"Could not load OAuth token ({type(exc).__name__})") from exc


def upload(video: Path, metadata: dict[str, Any], schedule_dt: datetime | None, token_file: Path) -> dict[str, Any]:
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ModuleNotFoundError as exc:
        raise PublishError("Google client libraries are missing; install scripts/requirements.txt") from exc

    credentials = load_credentials(token_file)
    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    snippet: dict[str, Any] = {
        "title": metadata["title"],
        "description": metadata["description"],
        "tags": metadata["tags"],
        "categoryId": metadata["category_id"],
    }
    if metadata.get("language"):
        snippet["defaultLanguage"] = metadata["language"]
        snippet["defaultAudioLanguage"] = metadata["language"]
    status: dict[str, Any] = {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": metadata["made_for_kids"],
    }
    if schedule_dt:
        status["publishAt"] = schedule_dt.isoformat().replace("+00:00", "Z")

    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": snippet, "status": status},
        media_body=MediaFileUpload(str(video), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True),
    )
    response = None
    while response is None:
        try:
            progress, response = request.next_chunk()
        except Exception as exc:
            raise PublishError(f"YouTube upload failed ({type(exc).__name__})") from exc
        if progress is not None:
            print(f"upload_progress={int(progress.progress() * 100)}%", file=sys.stderr)
    video_id = response.get("id") if isinstance(response, dict) else None
    if not video_id:
        raise PublishError("YouTube upload returned no video ID")

    try:
        result = youtube.videos().list(part="snippet,status", id=video_id).execute()
    except Exception as exc:
        raise PublishError(f"Upload succeeded but API readback failed for video ID {video_id} ({type(exc).__name__})") from exc
    items = result.get("items", [])
    if not items:
        raise PublishError(f"Upload returned video ID {video_id}, but the video was not readable back from the API")
    actual_status = items[0].get("status", {})
    if actual_status.get("privacyStatus") != "private":
        raise PublishError(f"Safety check failed for video ID {video_id}: privacy status is not private")
    actual_publish_at = actual_status.get("publishAt")
    if schedule_dt:
        if not actual_publish_at:
            raise PublishError(f"Video ID {video_id} was uploaded but no publishAt was returned")
        actual_dt = parse_datetime(actual_publish_at)
        if abs((actual_dt - schedule_dt).total_seconds()) > 2:
            raise PublishError(f"Video ID {video_id} publishAt does not match the requested schedule")

    return {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "privacy_status": actual_status.get("privacyStatus"),
        "publish_at": actual_publish_at,
        "readback_verified": True,
    }


def main() -> int:
    args = build_parser().parse_args()
    video = path_value(args.video)
    metadata = path_value(args.metadata)
    try:
        metadata_data, schedule_dt = validate_inputs(video, metadata, args.schedule_at)
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "mode": "dry-run",
                        "video": str(video),
                        "video_size_bytes": video.stat().st_size,
                        "metadata_valid": True,
                        "privacy_status": "private",
                        "schedule_at": schedule_dt.isoformat() if schedule_dt else None,
                        "network_contacted": False,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        if schedule_dt and not args.confirm_schedule:
            raise PublishError("A live schedule requires --confirm-schedule")
        result = upload(video, metadata_data, schedule_dt, path_value(args.token_file))
    except PublishError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
