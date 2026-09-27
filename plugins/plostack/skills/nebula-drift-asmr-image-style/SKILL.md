---
name: nebula-drift-asmr-image-style
description: >
  Use when creating or refining Nebula Drift ASMR channel images, prompts,
  filenames, and image-log records.
---

# Nebula Drift ASMR Image Style

Use this skill when the user wants to create, revise, select, or organize images for the Nebula Drift ASMR YouTube channel.

## Purpose

Keep Nebula Drift ASMR images visually consistent as a fantasy sci-fi sleep/ASMR travel-log channel.

The channel premise: Nebula is a quiet space traveler aboard a spacecraft. The channel contains records from Nebula's journey through planets, moons, nebulae, stations, and unknown regions. Longform sleep videos are one category inside that world. Each image is one possible quiet discovery in the world; shared style matters, but plot continuity is optional.

## Project Paths

Canonical asset root for all generated files:

- WSL path for commands: `/home/moon/workspace/plozen-nebula-drift-asmr-assets/`
- Windows Explorer path: `\\wsl.localhost\Ubuntu\home\moon\workspace\plozen-nebula-drift-asmr-assets\`
- Episode directory: `/home/moon/workspace/plozen-nebula-drift-asmr-assets/episodes/YYYYMMDD_<scene-slug>/`
- Candidate images: `<episode-directory>/candidates/`
- Selected render image: `<episode-directory>/render-input/scene.png`
- Episode index: `/home/moon/workspace/plozen-nebula-drift-asmr-assets/episode-index.jsonl`

Use the WSL path with Linux tools. Treat the UNC path as the Windows Explorer view of the same directory. Store generated images, copied audio, Scene Cards, manifests, previews, renders, and other episode deliverables under the episode directory; do not leave final assets only in `$CODEX_HOME/generated_images/`, `/tmp`, the repository, or an old Vault asset folder. Use Obsidian CLI for separate Vault markdown writes where applicable.

## Visual Style Anchors

Always bias toward:

- high-quality 4K cinematic realism
- majestic fantasy sci-fi scale
- sleep-friendly low contrast
- realistic lighting and atmosphere
- quiet solitude, wonder, and safety
- blue, violet, silver, teal, deep black, muted gold accents
- wide 16:9 landscape framing for longform sleep videos
- no text, no watermark, no logo
- no visible face unless the user explicitly requests character art
- Nebula can be implied through a ship, camp, window, footprints, soft light, or point-of-view framing rather than shown directly

Avoid:

- noisy neon cyberpunk clutter
- horror mood
- hard strobe-like highlights
- busy UI overlays
- readable text
- cartoon or toy-like rendering unless explicitly requested
- real person's face or celebrity likeness

## Default Longform Image Pattern

Use one calm, cinematic still image suitable for 30 minute to 1 hour sleep music.

Recommended structure:

1. A clear world location: moon, ringed planet, nebula canyon, alien ocean, space station window, cockpit, campsite.
2. One strong visual anchor: Saturn rings, two moons, a giant nebula, spacecraft window, landing lights.
3. Minimal action: sleeping, watching, drifting, resting, landing, quiet observation.
4. Low visual noise: enough detail to feel premium, not so much that it distracts from sleep.

## World-led Concept Workflow

Before generating an image, use Codex CLI's built-in `image_gen` tool through the system `imagegen` skill as the image backend for this pipeline. This is the Codex-authenticated built-in path and does not require `OPENAI_API_KEY`; the `openai api images.generate` command is only the explicit API/CLI fallback. Do not call Gemini image generation, Gemini image editing, or Gemini image remixing for Nebula visuals; Gemini is reserved for the separate music-generation step.
1. Keep the shared Nebula world and visual style anchors; do not require an episode treatment, previous scene, or plot continuation.
2. If the user supplies a seed, develop it. Otherwise invent a fresh discovery by combining a location, one clear visual anchor, a minimal quiet activity, and sleep-friendly light/mood. Possible seeds include a Moon campfire beneath the stars, a ringed planet with a luminous comet tail or auroral ribbon, an unknown planet's homes or city, an alien ocean, a nebula canyon, or a quiet station window.
3. Extract the concept fields: location, visual anchor, Nebula's implied presence or quiet action, mood/light, and optional sound cues. Keep the idea calm, safe, and free of threat or plot-heavy drama.
4. Decide whether this is longform 16:9 or shorts 9:16; use 16:9 for the sleep-music pipeline.
5. Draft the English image prompt from the concept, then include a negative/avoid section. Request ultra-high-resolution cinematic detail without claiming a native output size the image tool does not provide.
6. Generate three candidates by default for a new concept. Keep the concept, mood, and visual anchor fixed while varying one composition choice at a time; follow an explicit user-provided count when given.
7. Decide target filenames under `<episode-directory>/candidates/` before generation and record the idea seed and concept fields with every image result. After each built-in Codex `image_gen` call, copy the generated file from `$CODEX_HOME/generated_images/` into that candidate folder.
8. Mark every candidate `draft` and pass them to the read-only selection step. Only the selected candidate becomes `<episode-directory>/render-input/scene.png` and changes to `selected`.

## Controlled visual diversity

Keep the Nebula palette, quiet realism, wide composition, and sleep-safe contrast stable, but vary one or more Scene Card dimensions per episode: location, time of day, celestial anchor, foreground scale, atmospheric condition, and implied soundscape. Reject a candidate when its composition, horizon line, dominant color, or visual anchor is too close to recent used images. Do not solve repetition by adding random clutter; change the discovery while preserving calm legibility.

Use the Scene Card's visual anchor as the prompt's primary subject. The image must visibly support the same environment layers as the audio: a campfire should be present when fire sound is used, distant city architecture should be readable when city hum is used, and vegetation or water should be visible when those layers are selected.

## Prompt Template

```text
Create a cinematic 16:9 ultra high resolution image for the YouTube channel Nebula Drift ASMR.

World: Nebula is a quiet space traveler recording peaceful sleep/ASMR scenes during a journey across the universe.

Concept: [one fresh, self-contained cosmic discovery]

Location: [moon / ringed planet / unknown planet / alien city / station / nebula / ocean / spacecraft]

Visual anchor: [rings / moons / campfire / alien architecture / giant nebula / spacecraft window / etc.]

Quiet action: [watching / resting / drifting / landing / tending a campfire / observing]

Composition: [wide landscape / first-person window / small ship in foreground / no visible person / etc.]

Mood: majestic, quiet, realistic fantasy sci-fi, sleep-friendly, low contrast, calm wonder.

Visual details: [planet/rings/moons/terrain/ship/light/weather/atmosphere]

Style: high-quality 4K cinematic realism, realistic lighting, detailed but not busy, polished matte-painting realism.

Avoid: no text, no logo, no watermark, no visible face, no horror mood, no harsh neon, no cluttered UI overlays, no real celebrity likeness.
```

## Filename Rule

Use:

`YYYYMMDD_concept_slug_vN.png`

Examples:

- `20260705_saturn_moon_night_v1.png`
- `20260705_alien_ocean_two_moons_v1.png`
- `20260705_deep_space_station_window_v1.png`

## Episode Index Rule

After generating or selecting an image, update the canonical `episode-index.jsonl` through the Nebula pipeline's `update_episode_index.py` helper, and keep the full prompt and candidate details in the episode directory. Record:

- date
- idea source: user-provided seed or model-invented
- concept name, location, and visual anchor
- status: draft, selected, used, rejected
- tool/model if known
- final file path
- prompt
- notes about why it fits or does not fit the channel

## Example Discovery Seeds

- `Moon Camp Stargazing`: a small safe campfire on the Moon, Nebula's ship resting nearby, and an immense quiet star field above.
- `Ringed World Cometfall`: a calm observatory platform beneath enormous rings and a luminous comet tail or auroral ribbon.
- `Unknown City at Blue Hour`: impossible alien homes and towers emerging from a quiet blue-hour landscape, with no visible inhabitants or readable signs.

Use these only as seeds; each request may produce a different location and composition while preserving the shared Nebula world and sleep-friendly visual language.
