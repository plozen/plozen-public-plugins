#!/usr/bin/env python3
"""Create or update the Nebula Drift episode JSONL registry."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
YOUTUBE_FIELDS = ("video_id", "url", "privacy_status", "publish_at", "readback_verified")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _relative_path(value: Any, root: Path) -> Any:
    if not isinstance(value, str) or not value:
        return value
    path = Path(value)
    if not path.is_absolute():
        return value.replace("\\", "/")
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return os.path.relpath(path, root).replace("\\", "/")


def _relative_file(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def load_index(path: Path) -> list[dict[str, Any]]:
    """Read JSONL and collapse duplicate episode IDs to the newest line."""
    if not path.is_file():
        return []
    latest: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict) or not value.get("episode_id"):
            raise ValueError(f"invalid episode record at {path}:{line_number}")
        episode_id = str(value["episode_id"])
        if episode_id not in latest:
            order.append(episode_id)
        latest[episode_id] = value
    return [latest[episode_id] for episode_id in order]


def _safe_youtube(upload: dict[str, Any]) -> dict[str, Any] | None:
    if not any(upload.get(key) is not None for key in YOUTUBE_FIELDS):
        return None
    return {key: upload.get(key) for key in YOUTUBE_FIELDS}


def _scene(card: dict[str, Any]) -> dict[str, Any]:
    concept_value = card.get("concept")
    concept: dict[str, Any] = concept_value if isinstance(concept_value, dict) else {}
    return {
        "slug": card.get("scene_slug"),
        "location": concept.get("location"),
        "visual_anchor": concept.get("visual_anchor"),
        "quiet_action": concept.get("quiet_action"),
        "light_mood": concept.get("light_mood"),
    }


def _selected_image(selection: dict[str, Any], root: Path) -> Any:
    value = selection.get("selected_image")
    if isinstance(value, dict):
        value = copy.deepcopy(value)
        for key in ("path", "render_path"):
            if key in value:
                value[key] = _relative_path(value[key], root)
        return value
    if value:
        return {"path": _relative_path(value, root)}
    return None


def _selected_music(selection: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    values = selection.get("selected_music") or selection.get("ordered_music") or []
    if not isinstance(values, list):
        values = [values]
    result: list[dict[str, Any]] = []
    for value in values:
        if isinstance(value, dict):
            item = copy.deepcopy(value)
            for key in ("path", "render_path"):
                if key in item:
                    item[key] = _relative_path(item[key], root)
            result.append(item)
        elif isinstance(value, str):
            result.append({"path": _relative_path(value, root)})
    return result


def _manifests(episode_dir: Path, root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(episode_dir.rglob("*.manifest.json")):
        data = _load_json(path)
        output_value = data.get("output")
        output: dict[str, Any] = output_value if isinstance(output_value, dict) else {}
        result.append(
            {
                "path": _relative_file(path, root),
                "output_path": _relative_path(output.get("path"), root),
                "duration_seconds": output.get("duration_seconds"),
                "size_bytes": output.get("size_bytes"),
                "verification": data.get("verification"),
            }
        )
    return result


def _derive_status(status_data: dict[str, Any], final_data: dict[str, Any], upload: dict[str, Any], manifests: list[dict[str, Any]]) -> str:
    raw = str(status_data.get("status") or "")
    final = str(final_data.get("status") or "")
    if upload.get("privacy_status") == "private" and (upload.get("readback_verified") is True or upload.get("video_id")):
        return "private_uploaded"
    if raw == "private_upload_verified":
        return "private_uploaded"
    if final == "completed":
        return "completed"
    if raw == "blocked":
        return "blocked"
    if raw.startswith("aborted"):
        return "aborted"
    if any(isinstance(item.get("duration_seconds"), (int, float)) and item["duration_seconds"] >= 1800 for item in manifests):
        return "rendered"
    return raw or "unknown"


def build_record(episode_dir: Path, index_path: Path, status_override: str | None = None) -> dict[str, Any]:
    """Build a non-secret record from one episode directory."""
    root = index_path.resolve().parent
    episode_dir = episode_dir.resolve()
    episode_dir.relative_to(root)

    card_path = episode_dir / "scene-card.json"
    generated_card_path = episode_dir / "scene-card.generated.json"
    card = _load_json(card_path) or _load_json(generated_card_path)
    metadata_path = episode_dir / "metadata.json"
    selection_path = episode_dir / "selection.json"
    status_path = episode_dir / "status.json"
    final_status_path = episode_dir / "final-status.json"
    upload_path = episode_dir / "youtube-upload.json"
    metadata = _load_json(metadata_path)
    selection = _load_json(selection_path)
    status_data = _load_json(status_path)
    final_data = _load_json(final_status_path)
    upload = _load_json(upload_path)
    manifests = _manifests(episode_dir, root)
    scene = _scene(card)
    status = status_override or _derive_status(status_data, final_data, upload, manifests)
    source_dir = _relative_file(episode_dir, root)
    source_kind = "canonical_episode" if episode_dir.parent.name == "episodes" else "legacy_run"
    episode_id = str(card.get("episode_id") or episode_dir.name.lstrip("."))
    roles = []
    for layer in selection.get("ambience") or card.get("assets", {}).get("ambience", []) or []:
        if isinstance(layer, dict) and layer.get("role"):
            roles.append(layer["role"])

    assets: dict[str, Any] = {
        "scene_card": _relative_file(card_path, root) if card_path.is_file() else None,
        "scene_card_generated": _relative_file(generated_card_path, root) if generated_card_path.is_file() else None,
        "metadata": _relative_file(metadata_path, root) if metadata_path.is_file() else None,
        "selection": _relative_file(selection_path, root) if selection_path.is_file() else None,
        "status": _relative_file(status_path, root) if status_path.is_file() else None,
        "final_status": _relative_file(final_status_path, root) if final_status_path.is_file() else None,
        "youtube_upload": _relative_file(upload_path, root) if upload_path.is_file() else None,
        "render_manifests": manifests,
        "selected_image": _selected_image(selection, root),
        "selected_music": _selected_music(selection, root),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "episode",
        "episode_id": episode_id,
        "recorded_at": _now(),
        "source_kind": source_kind,
        "source_dir": source_dir,
        "status": status,
        "status_source": {
            "raw_status": status_data.get("status"),
            "final_status": final_data.get("status"),
            "reason": status_data.get("reason"),
            "next_action": status_data.get("next_action"),
        },
        "title": metadata.get("title"),
        "scene": scene,
        "dedupe": {
            "keys": [value for value in [scene.get("slug"), scene.get("location"), scene.get("visual_anchor"), *roles] if value],
            "avoid_by_default": True,
            "source": "scene-card.json" if card_path.is_file() else ("scene-card.generated.json" if generated_card_path.is_file() else "legacy-filename"),
        },
        "assets": assets,
        "youtube": _safe_youtube(upload),
    }


def upsert_record(index_path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Atomically replace an episode's current record and preserve status history."""
    if not record.get("episode_id"):
        raise ValueError("episode_id is required")
    if not record.get("status"):
        raise ValueError("status is required")
    record = copy.deepcopy(record)
    record.setdefault("schema_version", SCHEMA_VERSION)
    record.setdefault("record_type", "episode")
    record.setdefault("recorded_at", _now())
    records = load_index(index_path)
    existing = next((item for item in records if item.get("episode_id") == record["episode_id"]), None)
    if existing:
        history = list(existing.get("status_history") or [])
        if existing.get("status") != record.get("status"):
            history.append({"status": existing.get("status"), "recorded_at": existing.get("recorded_at")})
        for key in ("episode_date", "image_log_migration"):
            if key not in record and key in existing:
                record[key] = copy.deepcopy(existing[key])
        if history:
            record["status_history"] = history
        records = [item for item in records if item.get("episode_id") != record["episode_id"]]
    records.append(record)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in records)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=index_path.parent, delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.replace(temporary, index_path)
    return record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path, help="episode-index.jsonl path")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--record-json", type=Path, help="record JSON to upsert")
    source.add_argument("--episode-dir", type=Path, help="episode directory to inspect")
    parser.add_argument("--status", help="override the derived status when using --episode-dir")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    index_path = args.index.expanduser().resolve()
    if args.record_json:
        record = _load_json(args.record_json.expanduser().resolve())
    else:
        record = build_record(args.episode_dir.expanduser(), index_path, args.status)
    saved = upsert_record(index_path, record)
    print(json.dumps({"index": str(index_path), "episode_id": saved["episode_id"], "status": saved["status"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
