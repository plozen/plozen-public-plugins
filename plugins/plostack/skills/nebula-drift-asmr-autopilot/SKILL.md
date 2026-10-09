---
name: nebula-drift-asmr-autopilot
description: "Create a world-led Nebula Drift ASMR episode: invent a fresh quiet cosmic discovery, generate candidate visuals, collect permissively licensed audio resources, delegate asset selection to a read-only subagent, render a long-form sleep video with FFmpeg, upload it to YouTube as private, and optionally schedule publication after explicit confirmation."
---

# Nebula Drift ASMR Autopilot

## Scope

This skill handles the first autonomous-selection production version of the world-led Nebula Drift ASMR loop:

- the Nebula world premise and one fresh scene concept invented for each episode
- a visual and optional audio mood brief derived from that concept
- three 16:9 still-image candidates generated through Codex CLI's built-in `image_gen` tool via the system `imagegen` skill; Gemini is never used for episode image generation
- one or more fresh piano-led sleep-music tracks generated for every episode in the Google Gemini/Lyria web app through a Playwright/CDP-controlled user-visible Windows Chrome/Edge session; prior audio reuse is prohibited
- a read-only selection subagent that chooses one image and the ordered music set from the prepared candidates
- a Scene Card that binds the location, visual anchor, music brief, and layered environment-sound plan
- a deterministic Scene Card generator that can avoid recent scene slugs while preserving a reproducible seed
- one or more local or permissively licensed ambience layers such as fire, wind, spacecraft hum, distant city, rain, water, or alien vegetation
- a 30-minute to one-hour FFmpeg render
- metadata preparation
- YouTube OAuth upload as `private` with API readback
- optional scheduled publishing

The pipeline does not generate TTS, subtitles, or n8n workflows. For every normal episode run, music must be freshly generated in the Google Gemini/Lyria web UI through a Playwright/CDP-controlled user-visible Windows Chrome/Edge session. Do not use the Gemini API/CLI, project-local audio, permissively licensed audio, or any prior episode track as a fallback. If browser attachment, user authentication, generation, download, or freshness verification fails, record `blocked` and stop before rendering; never silently reuse an old track. Follow `autonomous-ai-agents/browser-auth-workflows`: the user completes login, password, 2FA, CAPTCHA, and consent steps, and credentials must never be recorded. Environment sound remains a separate layered soundscape sourced from project-local, openly licensed, or procedurally generated assets. It must not download arbitrary copyrighted audio or claim a license from an unverified search result. The pipeline does not require a novel, plot continuity, a fixed destination order, or a previous-episode story. Previous assets may guide shared style and prevent accidental repetition, but they do not constrain the next discovery.

## Canonical output root

All generated Nebula assets and deliverables must be created under this root:

- WSL path for commands: `/home/moon/workspace/plozen-nebula-drift-asmr-assets/`
- Windows Explorer path: `\\wsl.localhost\Ubuntu\home\moon\workspace\plozen-nebula-drift-asmr-assets\`

Treat the Windows UNC path as the user-facing equivalent only; pass the WSL path to Linux tools. Create each episode under:

`/home/moon/workspace/plozen-nebula-drift-asmr-assets/episodes/YYYYMMDD_<scene-slug>/`

Use this episode directory for Scene Cards, prompts, Codex image candidates, selected render inputs, music and ambience copies, manifests, metadata, previews, final renders, and upload records. Do not leave a final asset only in the repository, `/tmp`, `$CODEX_HOME/generated_images/`, or the previous ObsidianVault path. Codex built-in `image_gen` outputs must be copied from its default cache into the episode `candidates/` directory before selection.

Prefer an explicit `--input-dir` pointing to the episode's `render-input/` directory over guessing a date folder.

## Episode index and deduplication

The machine-readable source of truth for episode history is `episode-index.jsonl` at the canonical output root. Read it before inventing or accepting a concept; do not rely on directory scanning or ad hoc image logs. The index contains one current non-secret record per `episode_id`, including concept, scene slug, visual anchor, ambience roles, asset links, render status, and private YouTube readback.

- Use `scripts/update_episode_index.py` to create or atomically update records. Keep asset paths relative to the index root.
- Record every concept, including `concept_draft`, `rendered`, `private_uploaded`, `blocked`, and `aborted` attempts. A failed attempt remains part of deduplication history.
- Compare the latest records across scene slug, location, visual anchor, quiet action, light/mood, and ambience roles. Reject a materially repeated concept unless the user explicitly asks for a revision.
- Use `scripts/generate_scene_card.py --history <asset-root>/episode-index.jsonl`; the generator accepts JSON arrays and JSONL records and avoids recorded scene slugs where another library scene is available.
- Vault is a human-readable summary layer only. If Vault sync is unavailable, the local episode index is still mandatory and the run must continue with a pending sync note; never skip the machine record.

Read [references/episode-index.md](references/episode-index.md) before changing the record schema.

## World-led scene loop

Every episode is a self-contained quiet discovery inside the same Nebula world. Continuity means a consistent visual identity, not a continuing plot.

- Keep the core premise: Nebula is a quiet traveler exploring the universe from a spacecraft, planets, moons, stations, and unknown regions.
- Before inventing or accepting a concept, load the latest records from `<asset-root>/episode-index.jsonl` and reject duplicate or near-duplicate scene anchors, locations, and sound-layer combinations.
- If the user gives an idea, develop it. Otherwise invent a fresh, beautiful discovery by combining a location, one strong visual anchor, a minimal quiet activity, and sleep-friendly light/mood. Do not force a sequential destination or ask for a story source first. Suitable directions include a Moon campfire beneath the stars, a ringed planet with a luminous comet tail or auroral ribbon, an unknown planet with impossible homes or city architecture, a nebula canyon, an alien ocean, or a quiet station window.
- Draft a compact concept brief: location, visual anchor, Nebula's implied presence or quiet action, light/mood, and optional sound cues. Keep the scene calm, safe, and visually legible; avoid threat, chase, horror, or plot-heavy drama. Translate the visual mood into a piano-centered audio brief that is beautiful, gentle, serene, warm or ethereal, slow or unhurried, sparse, smooth, and sleep-friendly; do not let a cosmic setting become eerie, ominous, horror-like, or uncanny.
- Hand the visual brief to `nebula-drift-asmr-image-style` and Codex CLI's built-in `image_gen` tool via the system `imagegen` skill; generate three image candidates by default when an image is not already supplied. Keep the concept and style fixed while varying composition. Save candidates under the episode's `candidates/` folder inside the canonical output root as `draft`, pass them to the read-only selection subagent, then copy only the selected image into the episode's `render-input/` directory for rendering and record the concept source, prompts, selection rationale, and statuses in the episode index and per-episode files.
- If an idea is only a draft, label it as draft in the project record. A generated image can be previewed, but it must not silently become the canonical episode asset.

The concept brief is converted into a Scene Card before asset generation. The Scene Card is the single source of truth for the image, music brief, and environment-sound layers; do not independently randomize those assets. TTS narration, subtitles, and a full novel workflow are outside the current loop.

## Scene Card and controlled diversity

Create one JSON Scene Card per episode using `scripts/generate_scene_card.py` and `references/scene-card.example.json` as the contract. Give each episode a reproducible `episode_seed`, a location, one visual anchor, a quiet action, a light/mood, a music brief, and an ordered list of ambience layers with individual volumes and roles. Use a controlled random choice from the world taxonomy, then reject any candidate that is too similar to recent locations, visual anchors, compositions, or sound-layer combinations. Keep the Nebula style anchors fixed while varying the discovery.

The generator writes asset paths as a contract; it does not claim that the files already exist. Every generated or copied asset path in the Scene Card, selection JSON, metadata, manifest, and upload record must resolve under the episode directory in the canonical output root. Generate or collect the named music and ambience files, preserve their provenance, and only then call the renderer.

The same Scene Card must drive the image prompt, music-generation prompt, ambience selection, metadata, and render manifest. Record the card path and hash in the manifest. An episode is not complete when a new image exists; it is complete only when the scene's image, music, and environment layers agree and the final audio has a valid stream. Playback/listening is optional and must not block a user-requested continuation.

## Sleep-music selection criteria

The default instrument is soft felt or acoustic piano. Unless the user explicitly requests another instrument, the selected music should be piano-led: piano should be the principal audible instrument or recurring melodic anchor, with only subtle supporting pad, room tone, or very light texture allowed behind it. Do not deliberately request synth-only drones or generic space pads. The desired audio is beautiful, gentle, serene, and sleep-friendly—not merely "spacey." Prefer warm or ethereal piano harmony, soft melodic motion, sparse arrangement, long gentle decay, slow or unhurried pulse or ambient drift, smooth transitions, restrained dynamics, and no distracting non-piano lead elements. Reject tracks with eerie, ominous, uncanny, suspenseful, horror-like, strongly dissonant, glitchy, whispering, spoken, percussion-forward, beat-driven, bass-heavy, harsh, abrupt, or dramatically swelling qualities when those qualities are observable. Playback/listening is best-effort and must never block the user-requested continuation. If generation succeeded, the artifact downloaded, and `ffprobe` confirms a valid audio stream, continue with `listening_check: skipped_unavailable` and treat the piano/style assessment as provisional. Only a failed generation, failed download, missing/invalid stream, or explicit user rejection blocks the run.

## Autonomous resource collection and delegated selection

When the user asks to run the pipeline end to end, do not pause after image generation for a manual choice.

1. Generate three visual candidates through Codex CLI's built-in `image_gen` tool via the system `imagegen` skill unless the user supplied a usable image. This built-in path uses Codex authentication and does not require `OPENAI_API_KEY`. Copy every candidate from `$CODEX_HOME/generated_images/` into the episode's canonical `candidates/` folder before inspection or selection. Do not use Gemini image generation, Gemini image editing, or Gemini image remixing. Do not substitute the `openai api images.generate` fallback unless the user explicitly chooses the API/CLI fallback. If the built-in Codex image route is unavailable, stop and report the blocker rather than substituting another image backend.
2. Generate at least one fresh piano-led music candidate for this episode in the Google Gemini/Lyria web app using Playwright/CDP attached to the user's visible Windows Chrome/Edge session. Do not use an isolated browser for authenticated work. Preserve the exact music prompt under the episode's `prompts/` directory, download the result into the episode's `render-input/music/` directory, and write a non-secret `music-generation.json` containing the route, prompt path, model/UI label, output path, duration, SHA-256, and generation/download verification. Do not reuse any prior track and do not fall back to the Gemini API/CLI, a project-local track, or a permissively licensed track. If the browser is unavailable, a login/2FA/CAPTCHA wall remains, generation or download fails, or the artifact cannot be verified, write `blocked` and stop before render. Collect the Scene Card's environment layers separately; do not ask the music generator to stand in for fire, wind, city, spacecraft, or alien-vegetation stems.
3. Run `ffprobe` on every music and ambience candidate and record duration, stream presence, generation route/model, usage terms as shown by the UI, attribution text when applicable, hash, role, volume, and whether piano is the principal instrument. Compare every generated music SHA-256 with all prior music hashes in the episode index and reject any collision. Inspect a short preview or otherwise evaluate the audio itself when possible, but do not pause when the environment cannot play or hear the track. After successful generation, download, and stream validation, continue with `listening_check: skipped_unavailable` and a provisional selection. Reject only missing/invalid streams, failed downloads, or explicit user rejection at this gate; never replace a rejected or failed fresh track with an old one.
4. Dispatch one read-only selection subagent with the Scene Card, piano-centered music brief, ambience-layer plan, and candidate files. Ask it to choose exactly one image, an ordered music set, and the ambience layers with per-track volumes and a concise rationale. The subagent must not edit, delete, commit, push, upload, or schedule anything.
5. The main agent verifies the returned paths and licensing, copies only the selected image/audio into a clean render-input folder, and records the selection JSON before rendering.

The user can still override the subagent result, but the default end-to-end path continues automatically through preview, full render, metadata, dry-run, private upload, and API readback. A private upload is part of the normal run when OAuth is available; skip it only when the user requests local-only or dry-run mode. Public visibility and scheduling remain separate explicit-confirmation stages.

## Side-effect policy

Use the stages in order:

1. `preview`: inspect assets and render locally. This has no external side effect.
2. `dry-run`: validate the video, metadata, OAuth-related inputs, and schedule timestamp without contacting YouTube.
3. `upload`: upload as `private` and verify the returned video resource.
4. `schedule`: only after the user explicitly supplies the target time and confirms the external action. The script still uploads as `private` and verifies `status.publishAt` through the API.

Never publish publicly by default. Never put client secrets, access tokens, refresh tokens, or channel identifiers into Vault notes, manifests committed to Git, screenshots, or chat output. Store OAuth material in a local ignored path or a secret manager. YouTube uploads require user OAuth; an API key alone is not sufficient, and service-account authentication is not supported for this user-channel flow. The bundled auth requests `youtube.upload` for upload, `youtube.readonly` for mandatory API readback, and `youtube.force-ssl` for metadata updates. Read [references/youtube-api.md](references/youtube-api.md) before the first authorization.

## Input contract

Concept stage:

- A user idea is optional. If none is supplied, invent a new world-consistent discovery and write a compact concept brief before image generation.
- A story note, episode treatment, previous-episode record, and plot continuity are optional and must never block asset generation.

Render stage:

At the top level of the input folder provide:

- exactly one image: `.png`, `.jpg`, `.jpeg`, or `.webp`, unless the Scene Card names the image explicitly
- one or more music files: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.opus`, or `.aac`
- zero or more ambience files; repeat `--ambience` for layers, or list them in the Scene Card with per-layer `volume` and `role`

If multiple images exist, stop and ask the user to choose with `--image` or name one in the Scene Card; do not guess. Multiple ambience files are allowed and are mixed as layers, either from repeated `--ambience` flags or the Scene Card. By default, every non-ambience music file is included in filename order. Repeat `--music` to set an explicit order or choose a subset. Keep renders under a `renders/` subfolder so they cannot be mistaken for source audio.

## Workflow

### 1. World concept and image brief

- Follow the [world-led scene loop](#world-led-scene-loop).
- Run [autonomous resource collection and delegated selection](#autonomous-resource-collection-and-delegated-selection) unless the user supplied an explicit asset set.
- Confirm that the selected image expresses the chosen discovery concept and is framed for longform sleep use before proceeding to preflight.

### 2. Preflight

- Confirm the input folder and selected files exist.
- Load and validate the Scene Card when supplied.
- Run `ffprobe` on the image, every music file, and every ambience layer; reject missing audio/video streams.
- Require `music.fresh_generation_required=true` and `music.provider=gemini-lyria-playwright`; confirm the selected audio has a fresh Gemini/Lyria browser-generation record, a prompt path, an output hash absent from prior episode music, the ordered playback list, ambience roles, and per-layer volumes.
- Confirm the target duration, output path, and whether the Scene Card's ambience layers are included.
- For YouTube work, validate metadata with [references/metadata-schema.md](references/metadata-schema.md) before loading any OAuth token.

### 3. Render

Run `scripts/render_video.py`. Pass `--scene-card` for the episode contract, or repeat `--ambience` for explicit environment layers. For NVIDIA/WSL production, pass `--video-encoder h264_nvenc` so the render fails rather than silently falling back to CPU; use `--video-encoder auto` only when a portable fallback is intentional. `auto` selects NVIDIA `h264_nvenc` when the installed FFmpeg exposes NVENC and otherwise selects `libx264`; the selected encoder and GPU flag are recorded in the manifest. Audio preparation and loudness filtering remain CPU-side, while H.264 video encoding uses the GPU when NVENC is selected. The default render is a calm static 1920x1080 image with all selected music tracks concatenated in order, then the complete sequence looped to the requested duration. Mix each ambience layer quietly under the music using its Scene Card volume, with the music remaining foreground. Apply conservative loudness normalization, prepare the normalized audio before the video mux, validate both container and audio-stream duration, and encode H.264/AAC in an MP4 suitable for YouTube.

The script must write a sidecar manifest beside the output with source paths, input hashes, output size, duration, and validation results. The manifest must not contain credentials.

### 4. Metadata

Prepare a JSON file with title, description, tags, category, language, and the explicit audience declaration. Start from `references/metadata.example.json`, then adapt the selected discovery concept. Do not invent claims about sounds, locations, or licensing that the supplied assets do not support. Keep download URLs and detailed license evidence in the selection JSON, manifest, and project log rather than in the public YouTube description unless the user explicitly asks for links. Convert the final `tags` array into a matching trailing hashtag line in `description`; retain the raw tags array for YouTube metadata.

- Public titles must not contain episode sequence numbers or labels such as `001`, `002`, or `Episode 3`. Use the world/scene name and listening intent instead. Internal episode IDs may remain in folders, manifests, and Vault logs for traceability.

### 5. Upload and schedule

- First run `scripts/youtube_publish.py ... --dry-run`.
- For a live upload, use a dedicated local OAuth token created by `scripts/youtube_auth.py`; the scripts use Python's standard library and do not require third-party Google packages.
- Default privacy is always `private`.
- In the normal end-to-end run, perform the live private upload immediately after a successful dry-run; do not pause for a second upload confirmation.
- If the OAuth token is missing, invalid, or lacks the required scopes, stop at this stage and report the exact authorization blocker rather than falling back to browser automation or public upload.
- A schedule requires an explicit future ISO 8601 timestamp and `--confirm-schedule`.
- After upload, call `videos.list` and verify the returned video ID, title, description, tags (order-insensitive), category, language, explicit audience declaration, `privacyStatus`, and, when requested, `publishAt`. A successful upload without a successful readback is not a completed publish operation.

### 6. Record

Write the machine record before generation, after rendering, and after every terminal outcome. Use the helper so the JSONL file stays valid and duplicate episode IDs are replaced atomically:

```bash
python3 scripts/update_episode_index.py \
  --index /path/to/asset-root/episode-index.jsonl \
  --episode-dir /path/to/asset-root/episodes/YYYYMMDD_scene-slug \
  --status concept_draft
```

- At concept creation, write `concept_draft` before image or music generation.
- After a validated local render, write `rendered` with the selected image, audio provenance, render path, and manifest.
- After a live private upload and API readback, write `private_uploaded` with only non-secret metadata and the YouTube video ID/status.
- If a dependency or policy stops the run, write `blocked` or `aborted` with a non-secret reason. A failed Gemini/Playwright music generation must remain `blocked`; do not substitute prior audio. If upload is not executed, leave it pending rather than implying it was scheduled.
- After the machine record succeeds, add or update the compact human-readable summary through the Obsidian CLI. Never put OAuth files, access tokens, refresh tokens, or client secrets in the index or Vault.

## Commands

```bash
# Generate a reproducible Scene Card; add --history to avoid recent scene slugs.
python3 scripts/generate_scene_card.py \
  --output /path/to/episode/scene-card.json \
  --seed moon-campfire-test-01 \
  --history /path/to/asset-root/episode-index.jsonl

# Record a concept or terminal episode state without writing secrets.
python3 scripts/update_episode_index.py \
  --index /path/to/asset-root/episode-index.jsonl \
  --episode-dir /path/to/asset-root/episodes/YYYYMMDD_scene-slug \
  --status concept_draft

# Render the episode from its Scene Card and layered audio assets.
python3 scripts/render_video.py \
  --input-dir /path/to/episode \
  --scene-card /path/to/episode/scene-card.json \
  --duration 3600 \
  --video-encoder h264_nvenc

# Validate metadata and schedule inputs without contacting YouTube.
python3 scripts/youtube_publish.py \
  --video /path/to/render.mp4 \
  --metadata /path/to/metadata.json \
  --schedule-at 2026-09-14T22:00:00+09:00 \
  --dry-run

# One-time local OAuth authorization (opens the user-visible browser).
python3 scripts/youtube_auth.py --client-secrets ~/.config/gws/client_secret.json

# Normal end-to-end live upload; always remains private.
python3 scripts/youtube_publish.py \
  --video /path/to/render.mp4 \
  --metadata /path/to/metadata.json

# Optional scheduled publication; execute only after explicit user confirmation.
python3 scripts/youtube_publish.py \
  --video /path/to/render.mp4 \
  --metadata /path/to/metadata.json \
  --schedule-at 2026-09-14T22:00:00+09:00 \
  --confirm-schedule
```

## Verification

- Run `python3 /home/moon/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-folder>`.
- Run `python3 scripts/generate_scene_card.py --output /tmp/scene-card.json --seed verification-seed` twice and confirm the JSON is identical.
- Run the episode-index unit tests and verify every JSONL line has a unique `episode_id`, a recognized `status`, and no credential-like fields.
- Run `python3 -m py_compile scripts/*.py`.
- Render a short fixture with FFmpeg and verify exit code, file size, video/audio streams, resolution, duration, and every ambience layer through the manifest and `ffprobe`.
- Run the YouTube script in `--dry-run` mode with an example metadata file; it must not make a network request.
- During a real upload, verify the API readback. Do not call a real upload merely to test the script.

If FFmpeg or the local OAuth client-secret JSON is unavailable, report the exact missing dependency and stop at the affected stage. Do not silently fall back to browser automation or a public upload.
