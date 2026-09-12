---
name: nebula-drift-asmr-pipeline
description: "Create a story-led Nebula Drift ASMR episode: derive the scene and media brief from an episode treatment, generate or select the 16:9 image, render a long-form sleep video from audio assets with FFmpeg, and optionally upload or schedule it on YouTube after explicit confirmation."
---

# Nebula Drift ASMR Pipeline

## Scope

This skill handles the first manual-production version of the story-led Nebula Drift ASMR loop:

- a concise episode treatment or story seed that preserves continuity with the previous episode
- a visual and audio brief derived from that story source
- one 16:9 still image, generated through `nebula-drift-asmr-image-style` and the built-in image generation tool when needed
- one or more sleep-music tracks, played in order and looped as a sequence
- optional spaceship ambience
- a 30-minute to one-hour FFmpeg render
- metadata preparation
- optional YouTube OAuth upload and scheduled publishing

Music remains user-provided or explicitly selected. This skill does not generate music, TTS, subtitles, or n8n workflows. Full novel writing is a separate later capability; the current loop still requires a short, engaging episode treatment as its creative source of truth.

The current project asset convention is a date folder such as:

`C:\Users\moon\ObsidianVault\02-Projects\nebula-drift-asmr\2026-09-12\`

When running in WSL, the equivalent is normally `/mnt/c/Users/moon/ObsidianVault/02-Projects/nebula-drift-asmr/2026-09-12/`. Prefer an explicit `--input-dir` over guessing a date folder.

## Story-first loop

Every episode starts with the narrative source, even when the final format is only image plus sleep music.

- Read the Nebula project note, the previous episode record, and any user-provided story material before choosing the next location or scene.
- Create or use a concise episode treatment: continuity from the previous episode, current waypoint, scene, emotional movement, and a quiet ending suitable for sleep content.
- Derive two briefs from the treatment: a visual brief for the image and an audio brief for music/ambience. Do not add a location, object, or mood that the story does not support.
- Hand the visual brief to `nebula-drift-asmr-image-style`; generate three image candidates by default with the built-in image tool when an image is not already supplied. Save candidates under the project `imgs/` folder as `draft`, let the user select one, then copy only the selected image into an episode-specific date-folder input directory for rendering and record the treatment source, prompts, and statuses in the image log.
- If the treatment is only a draft, label it as draft in the project record. A generated image can be previewed, but it must not silently become the canonical episode asset.

The story treatment is the minimum current input. TTS narration and a full novel workflow can be added later without removing this continuity layer.

## Side-effect policy

Use the stages in order:

1. `preview`: inspect assets and render locally. This has no external side effect.
2. `dry-run`: validate the video, metadata, OAuth-related inputs, and schedule timestamp without contacting YouTube.
3. `upload`: upload as `private` and verify the returned video resource.
4. `schedule`: only after the user explicitly supplies the target time and confirms the external action. The script still uploads as `private` and verifies `status.publishAt` through the API.

Never publish publicly by default. Never put client secrets, access tokens, refresh tokens, or channel identifiers into Vault notes, manifests committed to Git, screenshots, or chat output. Store OAuth material in a local ignored path or a secret manager. YouTube uploads require user OAuth; an API key alone is not sufficient, and service-account authentication is not supported for this user-channel flow. The bundled auth requests `youtube.upload` for upload and `youtube.readonly` for the mandatory API readback. Read [references/youtube-api.md](references/youtube-api.md) before the first authorization.

## Input contract

Story stage:

- Use an existing episode treatment/story note or draft one from the current canon before asset generation.
- The treatment may be supplied in the request or kept in the Nebula project notes; it must identify the episode and its continuity link.

Render stage:

At the top level of the input folder provide:

- exactly one image: `.png`, `.jpg`, `.jpeg`, or `.webp`
- one or more music files: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.opus`, or `.aac`
- optionally one ambience file, preferably named with `ambience`, `ambient`, `spaceship`, `engine`, `hum`, or `cabin`

If multiple images or ambience files exist, stop and ask the user to choose with `--image` or `--ambience`; do not guess. By default, every non-ambience music file is included in filename order. Repeat `--music` to set an explicit order or choose a subset. Keep renders under a `renders/` subfolder so they cannot be mistaken for source audio.

## Workflow

### 1. Story and image brief

- Follow the [story-first loop](#story-first-loop).
- Confirm that the user-selected image expresses the episode treatment and is framed for longform sleep use before proceeding to preflight.

### 2. Preflight

- Confirm the input folder and selected files exist.
- Run `ffprobe` on each source and reject missing audio/video streams.
- Confirm the target duration, output path, and whether ambience is included.
- For YouTube work, validate metadata with [references/metadata-schema.md](references/metadata-schema.md) before loading any OAuth token.

### 3. Render

Run `scripts/render_video.py`. The default render is a calm static 1920x1080 image with all selected music tracks concatenated in order, then the complete sequence looped to the requested duration. If ambience exists, mix it quietly under the music using the requested volume. Apply conservative loudness normalization and encode H.264/AAC in an MP4 suitable for YouTube.

The script must write a sidecar manifest beside the output with source paths, input hashes, output size, duration, and validation results. The manifest must not contain credentials.

### 4. Metadata

Prepare a JSON file with title, description, tags, category, language, and the explicit audience declaration. Start from `references/metadata.example.json`, then adapt the episode idea. Do not invent claims about sounds, locations, or licensing that the supplied assets do not support.

### 5. Upload and schedule

- First run `scripts/youtube_publish.py ... --dry-run`.
- For a live upload, use a dedicated local OAuth token created by `scripts/youtube_auth.py`; the scripts use Python's standard library and do not require third-party Google packages.
- Default privacy is always `private`.
- A schedule requires an explicit future ISO 8601 timestamp and `--confirm-schedule`.
- After upload, call `videos.list` and verify the returned video ID, title, description, tags (order-insensitive), category, language, explicit audience declaration, `privacyStatus`, and, when requested, `publishAt`. A successful upload without a successful readback is not a completed publish operation.

### 6. Record

After a successful local render, record the episode treatment reference, render path, and manifest in the Nebula project log through the Obsidian CLI. After a live upload, record only non-secret metadata and the YouTube video ID/status; never record OAuth files or tokens. If the upload is not executed, report it as pending rather than implying it was scheduled.

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

# One-time local OAuth authorization (opens the user-visible browser).
python3 scripts/youtube_auth.py --client-secrets ~/.config/gws/client_secret.json

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

If FFmpeg or the local OAuth client-secret JSON is unavailable, report the exact missing dependency and stop at the affected stage. Do not silently fall back to browser automation or a public upload.
