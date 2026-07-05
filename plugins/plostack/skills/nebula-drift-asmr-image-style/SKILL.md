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

The channel premise: Nebula is a quiet space traveler aboard a spacecraft. The channel contains records from Nebula's journey through planets, moons, nebulae, stations, and unknown regions. Longform sleep videos are one category inside that world.

## Project Paths

- Vault project: `/mnt/data/ObsidianVault/02-Projects/nebula-drift-asmr/`
- Image folder: `/mnt/data/ObsidianVault/02-Projects/nebula-drift-asmr/imgs/`
- Project hub note: `02-Projects/nebula-drift-asmr/Nebula Drift ASMR.md`
- Concept board: `02-Projects/nebula-drift-asmr/nebula-drift-asmr-concepts.md`
- Image log: `02-Projects/nebula-drift-asmr/nebula-drift-asmr-image-log.md`

Use Obsidian CLI for Vault markdown writes where possible. Store generated image files under the `imgs/` folder.

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

## Concept Workflow

Before generating an image:

1. Clarify the episode concept in one sentence.
2. Decide whether this is longform 16:9 or shorts 9:16.
3. Pick a mood: majestic, lonely-safe, dreamy, cold-silent, warm-cabin, alien-ocean, deep-space.
4. Draft the prompt in English.
5. Include a negative/avoid section.
6. Decide target filename before generation.

## Prompt Template

```text
Create a cinematic 16:9 ultra high resolution image for the YouTube channel Nebula Drift ASMR.

World: Nebula is a quiet space traveler recording peaceful sleep/ASMR scenes during a journey across the universe.

Scene: [specific episode scene]

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

## Image Log Rule

After generating or selecting an image, update `nebula-drift-asmr-image-log.md` with:

- date
- concept name
- status: draft, selected, used, rejected
- tool/model if known
- final file path
- prompt
- notes about why it fits or does not fit the channel

## First Canonical Concept

`Saturn Moon Night`

Nebula lands on a frozen moon of Saturn at night. The sky is filled with Saturn and its enormous rings. A small spacecraft or soft landing light may appear in the foreground. The mood is majestic, silent, cold, realistic, fantasy-like, and suitable for sleep music.
