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
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".aac"}
AMBIENCE_WORDS = (
    "ambience",
    "ambient",
    "spaceship",
    "engine",
    "hum",
    "cabin",
    "campfire",
    "fire",
    "wind",
    "rain",
    "water",
    "ocean",
    "city",
    "grass",
    "field",
    "alien",
    "soundscape",
    "foley",
)
SCENE_CARD_SCHEMA_VERSION = 1


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


def resolve_scene_asset(raw: str, *, base_dir: Path) -> Path:
    """Resolve a Scene Card asset relative to the card, preserving WSL paths."""

    expanded = os.path.expandvars(os.path.expanduser(str(raw)))
    if re.match(r"^[A-Za-z]:[\\/].*$", expanded):
        return resolve_path(expanded)
    candidate = Path(expanded)
    return (candidate if candidate.is_absolute() else base_dir / candidate).resolve()


def load_scene_card(path: Path) -> dict[str, Any]:
    """Load and validate the non-secret episode contract used by the renderer."""

    if not path.is_file():
        raise RenderError(f"Scene Card not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RenderError(f"Scene Card is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise RenderError("Scene Card root must be a JSON object")
    version = data.get("schema_version", SCENE_CARD_SCHEMA_VERSION)
    if version != SCENE_CARD_SCHEMA_VERSION:
        raise RenderError(
            f"Unsupported Scene Card schema_version={version}; expected {SCENE_CARD_SCHEMA_VERSION}"
        )
    assets = data.get("assets", {})
    if not isinstance(assets, dict):
        raise RenderError("Scene Card assets must be an object")
    for key in ("music", "ambience"):
        if key in assets and not isinstance(assets[key], list):
            raise RenderError(f"Scene Card assets.{key} must be an array")
    return data


def scene_card_assets(path: Path, card: dict[str, Any], default_volume: float) -> dict[str, Any]:
    """Resolve Scene Card asset references into renderer-ready values."""

    assets = card.get("assets", {})
    base_dir = path.parent
    image = assets.get("image")
    music = assets.get("music")
    ambience = assets.get("ambience")
    resolved: dict[str, Any] = {
        "image": str(resolve_scene_asset(image, base_dir=base_dir)) if image else None,
        "music": [str(resolve_scene_asset(item, base_dir=base_dir)) for item in music] if music else None,
        "ambience": None,
    }
    if ambience is not None:
        resolved_ambience: list[dict[str, Any]] = []
        for entry in ambience:
            if isinstance(entry, str):
                raw_path = entry
                volume = default_volume
                role = None
            elif isinstance(entry, dict):
                raw_path = entry.get("path")
                volume = entry.get("volume", default_volume)
                role = entry.get("role")
            else:
                raise RenderError("Each Scene Card ambience entry must be a path or object")
            if not isinstance(raw_path, str) or not raw_path.strip():
                raise RenderError("Each Scene Card ambience entry requires a path")
            if not isinstance(volume, (int, float)) or isinstance(volume, bool) or not 0 <= float(volume) <= 1:
                raise RenderError(f"Invalid ambience volume for {raw_path}: expected a number from 0 to 1")
            resolved_ambience.append(
                {
                    "path": str(resolve_scene_asset(raw_path, base_dir=base_dir)),
                    "volume": float(volume),
                    "role": str(role) if role else Path(raw_path).stem,
                }
            )
        resolved["ambience"] = resolved_ambience
    return resolved


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


def available_video_encoders() -> set[str]:
    """Return video encoder names exposed by the installed FFmpeg build."""

    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-encoders"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RenderError("Could not inspect FFmpeg video encoders")
    return set(re.findall(r"^\s+\S+\s+(\S+)", result.stdout, flags=re.MULTILINE))


def select_video_encoder(requested: str) -> tuple[str, bool]:
    """Select the requested encoder and report whether video encoding is GPU-backed."""

    if requested == "libx264":
        return "libx264", False
    encoders = available_video_encoders()
    if requested == "h264_nvenc":
        if requested not in encoders:
            raise RenderError("Requested h264_nvenc, but this FFmpeg build does not expose NVENC")
        return requested, True
    if requested == "auto":
        if "h264_nvenc" in encoders:
            return "h264_nvenc", True
        return "libx264", False
    raise RenderError(f"Unsupported video encoder: {requested}")


def ffprobe_json(path: Path) -> dict[str, Any]:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height,duration,sample_rate,channels",
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


def choose_music(folder: Path, raw: list[str] | None, candidates: list[Path]) -> list[Path]:
    if raw:
        selected: list[Path] = []
        for raw_path in raw:
            path = explicit_or_single(folder, raw_path, candidates, label="music")
            if path in selected:
                raise RenderError(f"Music was selected more than once: {path.name}")
            selected.append(path)
        return selected
    non_ambience = [
        path for path in candidates if not any(word in path.stem.lower() for word in AMBIENCE_WORDS)
    ]
    if not non_ambience:
        raise RenderError(f"No music found in {folder}; pass --music explicitly.")
    return non_ambience


def choose_ambience_tracks(
    folder: Path,
    raw: list[str | dict[str, Any]] | None,
    candidates: list[Path],
    selected_music: list[Path],
    default_volume: float,
) -> list[dict[str, Any]]:
    """Choose one or more ambience layers, preserving per-track volume and role."""

    available = [path for path in candidates if path not in selected_music]
    if raw is not None:
        selected: list[dict[str, Any]] = []
        seen: set[Path] = set()
        for entry in raw:
            if isinstance(entry, str):
                raw_path = entry
                volume = default_volume
                role = None
            elif isinstance(entry, dict):
                raw_path = entry.get("path")
                volume = entry.get("volume", default_volume)
                role = entry.get("role")
            else:
                raise RenderError("Each ambience entry must be a path or object")
            if not isinstance(raw_path, str) or not raw_path.strip():
                raise RenderError("Each ambience entry requires a path")
            if not isinstance(volume, (int, float)) or isinstance(volume, bool) or not 0 <= float(volume) <= 1:
                raise RenderError(f"Invalid ambience volume for {raw_path}: expected a number from 0 to 1")
            path = resolve_path(raw_path)
            if not path.is_file():
                raise RenderError(f"ambience does not exist: {path}")
            if path in selected_music:
                raise RenderError("Music and ambience must be different files")
            if path in seen:
                raise RenderError(f"Ambience was selected more than once: {path.name}")
            seen.add(path)
            selected.append(
                {
                    "path": path,
                    "volume": float(volume),
                    "role": str(role) if role else path.stem,
                }
            )
        return selected

    preferred = [
        path for path in available if any(word in path.stem.lower() for word in AMBIENCE_WORDS)
    ]
    return [
        {"path": path, "volume": default_volume, "role": path.stem}
        for path in preferred
    ]


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
    parser.add_argument("--scene-card", help="Scene Card JSON; asset paths are relative to the card")
    parser.add_argument("--image", help="Image path; required when the folder has multiple images")
    parser.add_argument(
        "--music",
        action="append",
        help="Music path; repeat to set an explicit order (default: use every non-ambience audio file in filename order)",
    )
    parser.add_argument(
        "--ambience",
        action="append",
        help="Ambience path; repeat for layered environment sounds (default: use all named ambience files)",
    )
    parser.add_argument("--output", help="Output MP4 path; defaults to <input-dir>/renders/<date>_nebula_drift.mp4")
    parser.add_argument("--manifest", help="Manifest path; defaults to output path with .manifest.json")
    parser.add_argument("--duration", type=float, default=3600.0, help="Target duration in seconds (default: 3600)")
    parser.add_argument("--ambience-volume", type=float, default=0.10, help="Default ambience gain from 0 to 1 (default: 0.10)")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--crf", type=int, default=20, help="H.264 quality setting (lower is higher quality)")
    parser.add_argument(
        "--video-encoder",
        choices=("auto", "h264_nvenc", "libx264"),
        default="auto",
        help="Video encoder; auto prefers NVIDIA NVENC and falls back to libx264",
    )
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
    scene_card_path = resolve_path(args.scene_card) if args.scene_card else None
    scene_card = load_scene_card(scene_card_path) if scene_card_path else None
    card_assets = scene_card_assets(scene_card_path, scene_card, args.ambience_volume) if scene_card and scene_card_path else {}

    images = files_with_extensions(input_dir, IMAGE_EXTENSIONS)
    audio = files_with_extensions(input_dir, AUDIO_EXTENSIONS)
    image_raw = args.image or card_assets.get("image")
    music_raw = args.music if args.music is not None else card_assets.get("music")
    ambience_raw = args.ambience if args.ambience is not None else card_assets.get("ambience")
    image = explicit_or_single(input_dir, image_raw, images, label="image")
    music = choose_music(input_dir, music_raw, audio)
    ambience = choose_ambience_tracks(input_dir, ambience_raw, audio, music, args.ambience_volume)

    image_info = validate_input(image, "video")
    music_info = [validate_input(path, "audio") for path in music]
    ambience_info: list[dict[str, Any]] = []
    for track in ambience:
        track_info = validate_input(track["path"], "audio")
        track_info.update({"volume": track["volume"], "role": track["role"]})
        ambience_info.append(track_info)

    date_slug = input_dir.name or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = resolve_path(args.output) if args.output else input_dir / "renders" / f"{date_slug}_nebula_drift.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = resolve_path(args.manifest) if args.manifest else output.with_suffix(".manifest.json")
    manifest.parent.mkdir(parents=True, exist_ok=True)

    video_filter = (
        f"scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
        f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p"
    )
    video_encoder, gpu_video_encoding = select_video_encoder(args.video_encoder)

    # Prepare audio separately from video. FFmpeg's loudnorm filter can emit
    # EINVAL at EOF when it is part of the same long video filtergraph, even
    # after writing a playable but truncated output. Normalizing finite tracks
    # into one exact-duration PCM file gives the final mux step a stable input.
    temp_dir = Path(tempfile.mkdtemp(prefix="nebula-drift-audio-"))
    normalized_audio = temp_dir / "normalized.wav"
    try:
        audio_inputs = []
        for music_path in music:
            audio_inputs += ["-i", str(music_path)]
        for track in ambience:
            audio_inputs += ["-stream_loop", "-1", "-i", str(track["path"])]

        audio_filter_parts = []
        music_labels = []
        for index in range(len(music)):
            label = f"music{index}"
            audio_filter_parts.append(
                f"[{index}:a]aresample=48000,asetpts=N/SR/TB,"
                f"loudnorm=I={args.target_lufs}:TP=-2:LRA=11,"
                f"aresample=48000,asetpts=N/SR/TB[{label}]"
            )
            music_labels.append(label)
        cycle_inputs = "".join(f"[{label}]" for label in music_labels)
        audio_filter_parts.append(
            f"{cycle_inputs}concat=n={len(music_labels)}:v=0:a=1[cycle];"
            f"[cycle]aloop=loop=-1:size=2147483647,atrim=duration={args.duration:.3f},"
            "asetpts=N/SR/TB[musicout]"
        )
        if ambience:
            ambience_labels = []
            for offset, track in enumerate(ambience):
                input_index = len(music) + offset
                label = f"ambience{offset}"
                audio_filter_parts.append(
                    f"[{input_index}:a]aresample=48000,asetpts=N/SR/TB,"
                    f"volume={float(track['volume']):.4f},atrim=duration={args.duration:.3f},"
                    f"asetpts=N/SR/TB[{label}]"
                )
                ambience_labels.append(label)
            ambience_inputs = "".join(f"[{label}]" for label in ambience_labels)
            if len(ambience_labels) == 1:
                audio_filter_parts.append(f"{ambience_inputs}anull[ambience_mix]")
            else:
                audio_filter_parts.append(
                    f"{ambience_inputs}amix=inputs={len(ambience_labels)}:duration=longest:"
                    "dropout_transition=5:normalize=0[ambience_mix]"
                )
            audio_filter_parts.append(
                "[musicout][ambience_mix]amix=inputs=2:duration=first:"
                "dropout_transition=5:normalize=0,asetpts=N/SR/TB[aout]"
            )
        else:
            audio_filter_parts.append("[musicout]anull[aout]")

        audio_command = [
            "ffmpeg",
            "-y",
            *audio_inputs,
            "-filter_complex",
            ";".join(audio_filter_parts),
            "-map",
            "[aout]",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(normalized_audio),
        ]
        run_command(audio_command, label="ffmpeg audio preparation")

        if video_encoder == "h264_nvenc":
            video_codec_options = [
                "-c:v",
                "h264_nvenc",
                "-preset",
                "p5",
                "-rc:v",
                "vbr",
                "-cq:v",
                str(args.crf),
                "-b:v",
                "0",
            ]
        else:
            video_codec_options = [
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                str(args.crf),
            ]
        video_command = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(args.fps),
            "-i",
            str(image),
            "-i",
            str(normalized_audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            video_filter,
            "-t",
            f"{args.duration:.3f}",
            "-r",
            str(args.fps),
            *video_codec_options,
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
        run_command(video_command, label="ffmpeg render")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

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
    audio_stream = next(stream for stream in output_streams if stream.get("codec_type") == "audio")
    if int(video_stream.get("width", 0)) != args.width or int(video_stream.get("height", 0)) != args.height:
        raise RenderError("Rendered resolution does not match the requested dimensions")
    try:
        audio_duration = float(audio_stream["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RenderError("Could not read rendered audio duration") from exc
    if audio_duration < args.duration - 2:
        raise RenderError(f"Rendered audio is too short: {audio_duration:.2f}s < {args.duration:.2f}s")

    manifest_data = {
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target_duration_seconds": args.duration,
        "scene_card": (
            {
                "path": str(scene_card_path),
                "sha256": sha256_file(scene_card_path),
                "episode_id": scene_card.get("episode_id"),
                "concept": scene_card.get("concept", {}),
            }
            if scene_card and scene_card_path
            else None
        ),
        "output": {
            "path": str(output),
            "size_bytes": output.stat().st_size,
            "duration_seconds": output_duration,
            "audio_duration_seconds": audio_duration,
            "width": args.width,
            "height": args.height,
            "video_codec": video_stream.get("codec_name"),
            "video_encoder": video_encoder,
            "gpu_video_encoding": gpu_video_encoding,
        },
        "inputs": {
            "image": image_info,
            "music": music_info,
            "ambience": ambience_info,
        },
        "audio": {
            "ambience_default_volume": args.ambience_volume,
            "ambience_track_count": len(ambience),
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
