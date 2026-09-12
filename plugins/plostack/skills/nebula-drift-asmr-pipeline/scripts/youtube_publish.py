#!/usr/bin/env python3
"""Upload a rendered MP4 to YouTube privately and optionally schedule it."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


YOUTUBE_API = "https://www.googleapis.com/youtube/v3"
YOUTUBE_UPLOAD_API = "https://www.googleapis.com/upload/youtube/v3/videos"
UPLOAD_CHUNK_SIZE = 8 * 1024 * 1024
REQUIRED_SCOPES = {
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
}


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


def request_json(
    method: str,
    url: str,
    *,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[dict[str, Any], Any]:
    request_headers = {"User-Agent": "nebula-drift-asmr-pipeline/1.0", **(headers or {})}
    if token:
        request_headers["Authorization"] = f"Bearer {token}"
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            decoded = json.loads(raw.decode("utf-8")) if raw else {}
            return decoded if isinstance(decoded, dict) else {}, response
    except urllib.error.HTTPError as exc:
        raise PublishError(f"YouTube API request failed (HTTP {exc.code})") from exc
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise PublishError(f"YouTube API request failed ({type(exc).__name__})") from exc


def load_token(token_file: Path) -> dict[str, Any]:
    try:
        data = json.loads(token_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublishError(f"OAuth token file not found: {token_file}; run youtube_auth.py first") from exc
    except json.JSONDecodeError as exc:
        raise PublishError(f"OAuth token file is not valid JSON: {token_file}") from exc
    if not isinstance(data, dict) or not data.get("access_token") or not data.get("refresh_token"):
        raise PublishError("OAuth token file lacks the required access_token/refresh_token fields")
    scope = str(data.get("scope", ""))
    missing_scopes = REQUIRED_SCOPES - set(scope.split())
    if missing_scopes:
        raise PublishError("OAuth token lacks required YouTube upload/readback scopes; run youtube_auth.py again")
    return data


def token_expired(token: dict[str, Any]) -> bool:
    try:
        expires_at = float(token.get("expires_at", 0))
    except (TypeError, ValueError):
        return True
    return expires_at <= time.time() + 60


def refresh_token(token_file: Path, token: dict[str, Any]) -> dict[str, Any]:
    token_uri = token.get("token_uri", "https://oauth2.googleapis.com/token")
    payload = urllib.parse.urlencode(
        {
            "client_id": token.get("client_id", ""),
            "client_secret": token.get("client_secret", ""),
            "refresh_token": token["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        str(token_uri),
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "nebula-drift-asmr-pipeline/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            refreshed = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise PublishError(f"OAuth token refresh failed ({type(exc).__name__})") from exc
    if not isinstance(refreshed, dict) or not refreshed.get("access_token"):
        raise PublishError("OAuth refresh response did not include an access token")
    updated = {**token, **refreshed, "expires_at": int(time.time()) + int(refreshed.get("expires_in", 3600))}
    token_file.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    token_file.chmod(0o600)
    return updated


def load_access_token(token_file: Path) -> tuple[dict[str, Any], str]:
    token = load_token(token_file)
    if token_expired(token):
        token = refresh_token(token_file, token)
    return token, str(token["access_token"])


def start_resumable_upload(token: str, video: Path, body: dict[str, Any]) -> str:
    params = urllib.parse.urlencode({"uploadType": "resumable", "part": "snippet,status"})
    request = urllib.request.Request(
        f"{YOUTUBE_UPLOAD_API}?{params}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(video.stat().st_size),
            "User-Agent": "nebula-drift-asmr-pipeline/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            location = response.headers.get("Location")
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise PublishError(f"Could not initialize YouTube resumable upload ({type(exc).__name__})") from exc
    if not location:
        raise PublishError("YouTube did not return a resumable upload URL")
    return location


def upload_bytes(token: str, upload_url: str, video: Path) -> dict[str, Any]:
    total = video.stat().st_size
    offset = 0
    with video.open("rb") as handle:
        while offset < total:
            handle.seek(offset)
            chunk = handle.read(UPLOAD_CHUNK_SIZE)
            if not chunk:
                raise PublishError("Video ended before the resumable upload completed")
            end = offset + len(chunk) - 1
            request = urllib.request.Request(
                upload_url,
                data=chunk,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {offset}-{end}/{total}",
                    "Content-Type": "video/mp4",
                    "User-Agent": "nebula-drift-asmr-pipeline/1.0",
                },
                method="PUT",
            )
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    raw = response.read()
                    if response.status in (200, 201):
                        result = json.loads(raw.decode("utf-8"))
                        if not isinstance(result, dict):
                            raise PublishError("YouTube upload returned an invalid response")
                        return result
                    if response.status == 308:
                        server_range = response.headers.get("Range")
                        offset = int(server_range.rsplit("-", 1)[-1]) + 1 if server_range else end + 1
                        continue
                    raise PublishError(f"Unexpected YouTube upload response (HTTP {response.status})")
            except urllib.error.HTTPError as exc:
                if exc.code == 308:
                    server_range = exc.headers.get("Range")
                    offset = int(server_range.rsplit("-", 1)[-1]) + 1 if server_range else end + 1
                    continue
                raise PublishError(f"YouTube media upload failed (HTTP {exc.code})") from exc
            except (urllib.error.URLError, json.JSONDecodeError) as exc:
                raise PublishError(f"YouTube media upload failed ({type(exc).__name__})") from exc
            print(f"upload_progress={int((offset / total) * 100)}%", file=sys.stderr)
    raise PublishError("YouTube upload ended without a final response")


def verify_metadata_readback(
    video_id: str,
    snippet: dict[str, Any],
    status: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    if snippet.get("title") != metadata["title"]:
        raise PublishError(f"Video ID {video_id} title does not match the requested metadata")
    if snippet.get("description") != metadata["description"]:
        raise PublishError(f"Video ID {video_id} description does not match the requested metadata")

    actual_tags = snippet.get("tags", [])
    expected_tags = metadata["tags"]
    if (
        not isinstance(actual_tags, list)
        or len(actual_tags) != len(expected_tags)
        or set(actual_tags) != set(expected_tags)
    ):
        raise PublishError(f"Video ID {video_id} tags do not match the requested metadata")
    if str(snippet.get("categoryId")) != metadata["category_id"]:
        raise PublishError(f"Video ID {video_id} category does not match the requested metadata")

    language = metadata.get("language")
    if language and (
        snippet.get("defaultLanguage") != language
        or snippet.get("defaultAudioLanguage") != language
    ):
        raise PublishError(f"Video ID {video_id} language does not match the requested metadata")
    if status.get("selfDeclaredMadeForKids") is not metadata["made_for_kids"]:
        raise PublishError(f"Video ID {video_id} audience declaration does not match the requested metadata")


def upload(video: Path, metadata: dict[str, Any], schedule_dt: datetime | None, token_file: Path) -> dict[str, Any]:
    token_data, access_token = load_access_token(token_file)
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
    response = upload_bytes(access_token, start_resumable_upload(access_token, video, {"snippet": snippet, "status": status}), video)
    video_id = response.get("id") if isinstance(response, dict) else None
    if not video_id:
        raise PublishError("YouTube upload returned no video ID")
    try:
        result, _ = request_json(
            "GET",
            f"{YOUTUBE_API}/videos?{urllib.parse.urlencode({'part': 'snippet,status', 'id': video_id})}",
            token=access_token,
        )
    except PublishError as exc:
        raise PublishError(f"Upload succeeded but API readback failed for video ID {video_id}") from exc
    items = result.get("items", [])
    if not items:
        raise PublishError(f"Upload returned video ID {video_id}, but the video was not readable back from the API")
    actual_snippet = items[0].get("snippet", {})
    actual_status = items[0].get("status", {})
    if not isinstance(actual_snippet, dict) or not isinstance(actual_status, dict):
        raise PublishError(f"Video ID {video_id} returned incomplete metadata during API readback")
    verify_metadata_readback(video_id, actual_snippet, actual_status, metadata)
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
