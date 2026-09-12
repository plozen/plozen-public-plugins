---
name: nebula-drift-asmr-pipeline
description: "Create a Nebula Drift ASMR long-form sleep video from a date-folder image and audio assets with FFmpeg, then optionally upload and schedule it on YouTube through OAuth after explicit confirmation. Use when the user asks to render, preview, upload, or schedule a Nebula Drift ASMR sleep-music video."
---

# Nebula Drift ASMR Pipeline

## Scope

This skill handles the first manual-production version of Nebula Drift ASMR:

- one 16:9 still image
- one sleep-music track
- optional spaceship ambience
- a 30-minute to one-hour FFmpeg render
- metadata preparation
- optional YouTube OAuth upload and scheduled publishing

It does not generate images, music, TTS, stories, subtitles, or n8n workflows. Use the existing `nebula-drift-asmr-image-style` skill for image creation and keep user-provided audio as the source of truth.

The current project asset convention is a date folder such as:

`C:\Users\moon\ObsidianVault\02-Projects\nebula-drift-asmr\2026-09-12\`

When running in WSL, the equivalent is normally `/mnt/c/Users/moon/ObsidianVault/02-Projects/nebula-drift-asmr/2026-09-12/`. Prefer an explicit `--input-dir` over guessing a date folder.

## Side-effect policy

Use the stages in order:

1. `preview`: inspect assets and render locally. This has no external side effect.
2. `dry-run`: validate the video, metadata, OAuth-related inputs, and schedule timestamp without contacting YouTube.
3. `upload`: upload as `private` and verify the returned video resource.
4. `schedule`: only after the user explicitly supplies the target time and confirms the external action. The script still uploads as `private` and verifies `status.publishAt` through the API.

Never publish publicly by default. Never put client secrets, access tokens, refresh tokens, or channel identifiers into Vault notes, manifests committed to Git, screenshots, or chat output. Store OAuth material in a local ignored path or a secret manager. YouTube uploads require user OAuth; an API key alone is not sufficient, and service-account authentication is not supported for this user-channel flow. Read [references/youtube-api.md](references/youtube-api.md) before the first authorization.

## Input contract

At the top level of the input folder provide:

- exactly one image: `.png`, `.jpg`, `.jpeg`, or `.webp`
- exactly one music file: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.opus`, or `.aac`
- optionally one ambience file, preferably named with `ambience`, `ambient`, `spaceship`, `engine`, `hum`, or `cabin`

If more than one candidate exists, stop and ask the user to choose with `--image`, `--music`, or `--ambience`; do not guess. Keep renders under a `renders/` subfolder so they cannot be mistaken for source audio.

## Workflow

### 1. Preflight

- Confirm the input folder and selected files exist.
- Run `ffprobe` on each source and reject missing audio/video streams.
- Confirm the target duration, output path, and whether ambience is included.
- For YouTube work, validate metadata with [references/metadata-schema.md](references/metadata-schema.md) before loading any OAuth token.

### 2. Render

Run `scripts/render_video.py`. The default render is a calm static 1920x1080 image with the music looped to the requested duration. If ambience exists, mix it quietly under the music using the requested volume. Apply conservative loudness normalization and encode H.264/AAC in an MP4 suitable for YouTube.

The script must write a sidecar manifest beside the output with source paths, input hashes, output size, duration, and validation results. The manifest must not contain credentials.

### 3. Metadata

Prepare a JSON file with title, description, tags, category, language, and the explicit audience declaration. Start from `references/metadata.example.json`, then adapt the episode idea. Do not invent claims about sounds, locations, or licensing that the supplied assets do not support.

### 4. Upload and schedule

- First run `scripts/youtube_publish.py ... --dry-run`.
- For a live upload, use a dedicated local OAuth token created by `scripts/youtube_auth.py`.
- Default privacy is always `private`.
- A schedule requires an explicit future ISO 8601 timestamp and `--confirm-schedule`.
- After upload, call `videos.list` and verify the returned video ID, `privacyStatus`, and, when requested, `publishAt`. A successful upload without a successful readback is not a completed publish operation.

### 5. Record

After a successful local render, record the render path and manifest in the Nebula project log through the Obsidian CLI. After a live upload, record only non-secret metadata and the YouTube video ID/status; never record OAuth files or tokens. If the upload is not executed, report it as pending rather than implying it was scheduled.

## Commands

```bash
# Render a one-hour preview from the current date folder.
python3 scripts/render_video.py \
  --input-dir /mnt/c/Users/moon/ObsidianVault/02-Projects/nebula-drift-asmr/2026-09-12 \
  --duration 3600

# Validate metadata and schedule inputs without contacting YouTube.
python3 scripts/youtube_publish.py \
  --video /path/to/render.mp4 \
  --metadata /path/to/metadata.json \
  --schedule-at 2026-09-14T22:00:00+09:00 \
  --dry-run

# Live upload and schedule; execute only after explicit user confirmation.
python3 scripts/youtube_publish.py \
  --video /path/to/render.mp4 \
  --metadata /path/to/metadata.json \
  --schedule-at 2026-09-14T22:00:00+09:00 \
  --confirm-schedule
```

## Verification

- Run `python3 /home/moon/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-folder>`.
- Run `python3 -m py_compile scripts/*.py`.
- Render a short fixture with FFmpeg and verify exit code, file size, video/audio streams, resolution, and duration through `ffprobe`.
- Run the YouTube script in `--dry-run` mode with an example metadata file; it must not make a network request.
- During a real upload, verify the API readback. Do not call a real upload merely to test the script.

If FFmpeg or the Google client libraries are unavailable, report the exact missing dependency and stop at the affected stage. Do not silently fall back to browser automation or a public upload.
