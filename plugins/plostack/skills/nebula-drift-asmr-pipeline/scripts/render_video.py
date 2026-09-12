#!/usr/bin/env python3
"""Render a Nebula Drift ASMR long-form video with FFmpeg.

The command is intentionally local-only. YouTube credentials are not read here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".aac"}
AMBIENCE_WORDS = ("ambience", "ambient", "spaceship", "engine", "hum", "cabin")
MUSIC_WORDS = ("music", "bgm", "sleep", "track", "song")


class RenderError(RuntimeError):
    """A user-actionable render or input error."""


def resolve_path(raw: str) -> Path:
    """Resolve Linux paths and common Windows paths when running under WSL."""

    expanded = os.path.expandvars(os.path.expanduser(raw))
    windows_match = re.match(r"^([A-Za-z]):[\\/](.*)$", expanded)
    if windows_match:
        drive, rest = windows_match.groups()
        return (Path("/mnt") / drive.lower() / rest.replace("\\", "/")).resolve()
    return Path(expanded).resolve()


def require_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise RenderError(f"Required executable not found: {name}")


def run_command(command: list[str], *, label: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        tail = result.stderr.strip().splitlines()[-12:]
        detail = "\n".join(tail)
        raise RenderError(f"{label} failed (exit={result.returncode}).\n{detail}")
    return result


def ffprobe_json(path: Path) -> dict[str, Any]:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height",
            "-of",
            "json",
            str(path),
        ],
        label=f"ffprobe {path.name}",
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RenderError(f"ffprobe returned invalid JSON for {path.name}") from exc


def input_duration(path: Path) -> float:
    data = ffprobe_json(path)
    try:
        return float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RenderError(f"Could not read duration for {path}") from exc


def stream_types(path: Path) -> set[str]:
    return {str(stream.get("codec_type")) for stream in ffprobe_json(path).get("streams", [])}


def files_with_extensions(folder: Path, extensions: set[str]) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in extensions and not path.name.startswith(".")
    )


def explicit_or_single(
    folder: Path,
    raw: str | None,
    candidates: list[Path],
    *,
    label: str,
) -> Path:
    if raw:
        selected = resolve_path(raw)
        if not selected.is_file():
            raise RenderError(f"{label} does not exist: {selected}")
        return selected
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise RenderError(f"No {label} found in {folder}; pass --{label} explicitly.")
    names = ", ".join(path.name for path in candidates)
    raise RenderError(f"Multiple {label} candidates found ({names}); pass --{label} explicitly.")


def choose_music(folder: Path, raw: str | None, candidates: list[Path]) -> Path:
    if raw:
        return explicit_or_single(folder, raw, candidates, label="music")
    non_ambience = [
        path for path in candidates if not any(word in path.stem.lower() for word in AMBIENCE_WORDS)
    ]
    preferred = [
        path for path in non_ambience if any(word in path.stem.lower() for word in MUSIC_WORDS)
    ]
    if len(preferred) == 1:
        return preferred[0]
    return explicit_or_single(folder, None, non_ambience, label="music")


def choose_ambience(folder: Path, raw: str | None, candidates: list[Path]) -> Path | None:
    if raw:
        return explicit_or_single(folder, raw, candidates, label="ambience")
    preferred = [
        path for path in candidates if any(word in path.stem.lower() for word in AMBIENCE_WORDS)
    ]
    if len(preferred) > 1:
        names = ", ".join(path.name for path in preferred)
        raise RenderError(f"Multiple ambience candidates found ({names}); pass --ambience explicitly.")
    return preferred[0] if preferred else None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_input(path: Path, expected_type: str) -> dict[str, Any]:
    if not path.exists():
        raise RenderError(f"Input does not exist: {path}")
    data = ffprobe_json(path)
    types = {str(stream.get("codec_type")) for stream in data.get("streams", [])}
    if expected_type not in types:
        raise RenderError(f"{path.name} has no {expected_type} stream")
    duration = input_duration(path) if expected_type == "audio" else None
    return {
        "path": str(path),
        "duration_seconds": duration,
        "sha256": sha256_file(path),
        "stream_types": sorted(types),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, help="Folder containing source image/audio assets")
    parser.add_argument("--image", help="Image path; required when the folder has multiple images")
    parser.add_argument("--music", help="Music path; required when the folder has multiple music files")
    parser.add_argument("--ambience", help="Optional spaceship ambience path")
    parser.add_argument("--output", help="Output MP4 path; defaults to <input-dir>/renders/<date>_nebula_drift.mp4")
    parser.add_argument("--manifest", help="Manifest path; defaults to output path with .manifest.json")
    parser.add_argument("--duration", type=float, default=3600.0, help="Target duration in seconds (default: 3600)")
    parser.add_argument("--ambience-volume", type=float, default=0.10, help="Ambience gain from 0 to 1 (default: 0.10)")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--crf", type=int, default=20, help="H.264 quality setting (lower is higher quality)")
    parser.add_argument("--target-lufs", type=float, default=-18.0, help="One-pass loudnorm target (default: -18 LUFS)")
    return parser


def render(args: argparse.Namespace) -> dict[str, Any]:
    require_binary("ffmpeg")
    require_binary("ffprobe")
    if args.duration <= 0 or args.duration > 86400:
        raise RenderError("--duration must be greater than 0 and no more than 86400 seconds")
    if args.ambience_volume < 0 or args.ambience_volume > 1:
        raise RenderError("--ambience-volume must be between 0 and 1")
    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        raise RenderError("--width, --height, and --fps must be positive")

    input_dir = resolve_path(args.input_dir)
    if not input_dir.is_dir():
        raise RenderError(f"Input directory does not exist: {input_dir}")
    images = files_with_extensions(input_dir, IMAGE_EXTENSIONS)
    audio = files_with_extensions(input_dir, AUDIO_EXTENSIONS)
    image = explicit_or_single(input_dir, args.image, images, label="image")
    music = choose_music(input_dir, args.music, audio)
    ambience = choose_ambience(input_dir, args.ambience, audio)
    if ambience and ambience == music:
        raise RenderError("Music and ambience must be different files")

    image_info = validate_input(image, "video")
    music_info = validate_input(music, "audio")
    ambience_info = validate_input(ambience, "audio") if ambience else None

    date_slug = input_dir.name or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = resolve_path(args.output) if args.output else input_dir / "renders" / f"{date_slug}_nebula_drift.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = resolve_path(args.manifest) if args.manifest else output.with_suffix(".manifest.json")
    manifest.parent.mkdir(parents=True, exist_ok=True)

    video_filter = (
        f"scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
        f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p"
    )
    input_args = ["-loop", "1", "-framerate", str(args.fps), "-i", str(image), "-stream_loop", "-1", "-i", str(music)]
    if ambience:
        input_args += ["-stream_loop", "-1", "-i", str(ambience)]

    command = ["ffmpeg", "-y", *input_args]
    if ambience:
        audio_filter = (
            f"[1:a]volume=1.0[music];[2:a]volume={args.ambience_volume:.4f}[ambience];"
            f"[music][ambience]amix=inputs=2:duration=longest:dropout_transition=5:normalize=0,"
            f"loudnorm=I={args.target_lufs}:TP=-2:LRA=11[aout]"
        )
        command += ["-filter_complex", audio_filter, "-map", "0:v:0", "-map", "[aout]"]
    else:
        command += ["-map", "0:v:0", "-map", "1:a:0", "-af", f"loudnorm=I={args.target_lufs}:TP=-2:LRA=11"]
    command += [
        "-vf",
        video_filter,
        "-t",
        f"{args.duration:.3f}",
        "-r",
        str(args.fps),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        str(args.crf),
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        str(output),
    ]
    run_command(command, label="ffmpeg render")

    output_data = ffprobe_json(output)
    output_streams = output_data.get("streams", [])
    output_types = {str(stream.get("codec_type")) for stream in output_streams}
    if not {"video", "audio"}.issubset(output_types):
        raise RenderError(f"Rendered file is missing video/audio streams: {sorted(output_types)}")
    try:
        output_duration = float(output_data["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RenderError("Could not read rendered video duration") from exc
    if output_duration < args.duration - 2:
        raise RenderError(f"Rendered duration is too short: {output_duration:.2f}s < {args.duration:.2f}s")
    video_stream = next(stream for stream in output_streams if stream.get("codec_type") == "video")
    if int(video_stream.get("width", 0)) != args.width or int(video_stream.get("height", 0)) != args.height:
        raise RenderError("Rendered resolution does not match the requested dimensions")

    manifest_data = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target_duration_seconds": args.duration,
        "output": {
            "path": str(output),
            "size_bytes": output.stat().st_size,
            "duration_seconds": output_duration,
            "width": args.width,
            "height": args.height,
            "video_codec": video_stream.get("codec_name"),
        },
        "inputs": {
            "image": image_info,
            "music": music_info,
            "ambience": ambience_info,
        },
        "audio": {
            "ambience_volume": args.ambience_volume if ambience else None,
            "target_lufs": args.target_lufs,
        },
        "verification": {"ffmpeg_exit_code": 0, "ffprobe_streams": sorted(output_types)},
    }
    manifest.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest_data


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = render(args)
    except RenderError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
