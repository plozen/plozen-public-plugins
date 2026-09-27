# Nebula episode index

`episode-index.jsonl` is the machine-readable registry for the canonical Nebula asset root. It is not a replacement for per-episode provenance files; it is the compact registry used to prevent topic repetition and to find those files.

## Location

Place the file at the root that contains `episodes/` and legacy Nebula run folders:

```text
<asset-root>/episode-index.jsonl
```

Each non-empty line is one JSON object with `schema_version: 1`. Keep one current record per `episode_id`; `scripts/update_episode_index.py` replaces an existing record atomically and preserves prior statuses in `status_history`.

## Required fields

```json
{
  "schema_version": 1,
  "record_type": "episode",
  "episode_id": "20260919-moon-campfire-earthrise",
  "recorded_at": "2026-09-19T00:00:00+00:00",
  "source_kind": "canonical_episode",
  "source_dir": "episodes/20260919_moon-campfire-earthrise",
  "status": "private_uploaded",
  "title": "Moon Camp at Silver Dawn | Sleep Piano & Lunar Ambience",
  "scene": {
    "slug": "moon-campfire",
    "location": "a sheltered moon camp",
    "visual_anchor": "a small campfire beneath Earthrise",
    "quiet_action": "resting beside the fire while the spacecraft cools",
    "light_mood": "deep blue lunar night with warm firelight"
  },
  "dedupe": {
    "keys": ["moon-campfire", "a sheltered moon camp", "campfire"],
    "avoid_by_default": true
  },
  "assets": {
    "scene_card": "episodes/20260919_moon-campfire-earthrise/scene-card.json",
    "selection": "episodes/20260919_moon-campfire-earthrise/selection.json",
    "metadata": "episodes/20260919_moon-campfire-earthrise/metadata.json",
    "render_manifests": [],
    "selected_image": {"path": "render-input/scene.png"},
    "selected_music": []
  },
  "youtube": {
    "video_id": "[non-secret ID]",
    "privacy_status": "private",
    "readback_verified": true
  }
}
```

All asset paths must be relative to the index root. Do not write OAuth files, access tokens, refresh tokens, client secrets, cookies, or channel credentials into the index.

## Statuses

Use these statuses consistently:

- `concept_draft`: concept exists but production has not started.
- `rendered`: local render and validation succeeded.
- `private_uploaded`: YouTube upload succeeded and API readback verified; privacy remains `private`.
- `blocked`: required generation, authorization, or asset dependency prevented progress.
- `aborted`: the run stopped because a constraint or backend requirement failed.
- `unknown`: legacy material lacks enough evidence for a stronger status.

Failed or blocked concepts remain in the index so the next topic-selection pass does not silently repeat them.

## Update points

Write or update a record:

1. immediately after the concept/Scene Card is created (`concept_draft`);
2. after a validated local render (`rendered`);
3. after private YouTube upload and API readback (`private_uploaded`);
4. when a run is blocked or aborted, including a non-secret reason.

The topic selector reads the latest record for every episode, compares `scene.slug`, location, visual anchor, quiet action, and ambience roles, and only then invents a new concept. Vault is a human-readable summary layer; it is not the machine source of truth.
