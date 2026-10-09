#!/usr/bin/env python3
"""Create a reproducible, world-consistent Nebula Drift Scene Card."""

from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCENE_LIBRARY: tuple[dict[str, Any], ...] = (
    {
        "slug": "moon-campfire",
        "location": "a sheltered moon camp",
        "visual_anchors": ("a small campfire beneath Earthrise", "a warm fire beside a resting lander"),
        "quiet_actions": ("resting beside the fire while the spacecraft cools", "watching sparks rise into the black sky"),
        "light_moods": ("deep blue lunar night with warm firelight", "silver dawn with a quiet amber glow"),
        "music_brief": "soft felt piano, sparse warm harmony, slow unhurried pulse, instrumental, sleep-friendly",
        "ambience": (
            {"path": "ambience/campfire.wav", "volume": 0.16, "role": "campfire"},
            {"path": "ambience/spaceship_hum.wav", "volume": 0.04, "role": "spaceship"},
            {"path": "ambience/lunar_wind.wav", "volume": 0.03, "role": "wind"},
        ),
    },
    {
        "slug": "blue-hour-alien-city",
        "location": "a quiet alien city at blue hour",
        "visual_anchors": ("distant towers beneath two moons", "empty curved streets reflecting violet light"),
        "quiet_actions": ("observing the city from a silent landing platform", "drifting above the rooftops in a parked shuttle"),
        "light_moods": ("soft blue hour with muted violet windows", "cool twilight under a faint ringed planet"),
        "music_brief": "gentle felt piano with a barely audible warm pad, sparse, slow, no percussion or vocals",
        "ambience": (
            {"path": "ambience/distant_city_hum.wav", "volume": 0.06, "role": "distant_city"},
            {"path": "ambience/alien_wind.wav", "volume": 0.035, "role": "alien_wind"},
            {"path": "ambience/spaceship_hum.wav", "volume": 0.025, "role": "spaceship"},
        ),
    },
    {
        "slug": "bioluminescent-grassland",
        "location": "a bioluminescent alien grassland",
        "visual_anchors": ("glowing seed heads moving under two moons", "a luminous meadow around a quiet survey beacon"),
        "quiet_actions": ("walking slowly through the glowing grass", "watching the plants ripple in a warm night breeze"),
        "light_moods": ("deep teal night with soft green points of light", "violet dusk fading into a star field"),
        "music_brief": "warm sparse piano with long decay, gentle ambient support, serene and unhurried, instrumental",
        "ambience": (
            {"path": "ambience/alien_wind.wav", "volume": 0.055, "role": "alien_wind"},
            {"path": "ambience/alien_grass.wav", "volume": 0.07, "role": "alien_grass"},
            {"path": "ambience/soft_plant_chimes.wav", "volume": 0.025, "role": "plant_chimes"},
        ),
    },
    {
        "slug": "ringed-world-observatory",
        "location": "a small observatory on a ringed world",
        "visual_anchors": ("enormous rings crossing a dark sky", "a quiet observatory window beneath an auroral ribbon"),
        "quiet_actions": ("recording the slow movement of the rings", "resting beside the observation glass"),
        "light_moods": ("muted gold aurora over deep indigo terrain", "silver night with a soft teal horizon"),
        "music_brief": "slow acoustic piano, spacious harmony, very light atmospheric pad, no beat, no dramatic swell",
        "ambience": (
            {"path": "ambience/observatory_hum.wav", "volume": 0.045, "role": "observatory"},
            {"path": "ambience/distant_wind.wav", "volume": 0.035, "role": "wind"},
            {"path": "ambience/low_aurora_tone.wav", "volume": 0.02, "role": "aurora"},
        ),
    },
    {
        "slug": "alien-ocean-window",
        "location": "a quiet alien ocean beneath a spacecraft window",
        "visual_anchors": ("bioluminescent waves under a crescent moon", "a calm ocean reflecting a giant nebula"),
        "quiet_actions": ("watching the tide move beneath the ship", "listening from the observation cabin while the vessel drifts"),
        "light_moods": ("dark cobalt water with gentle cyan glow", "soft dawn over a lavender alien sea"),
        "music_brief": "minimal felt piano, warm open intervals, slow ambient drift, beautiful and sleep-friendly",
        "ambience": (
            {"path": "ambience/alien_ocean.wav", "volume": 0.09, "role": "alien_ocean"},
            {"path": "ambience/spaceship_hum.wav", "volume": 0.035, "role": "spaceship"},
            {"path": "ambience/soft_wind.wav", "volume": 0.025, "role": "wind"},
        ),
    },
    {
        "slug": "nebula-canyon",
        "location": "a calm canyon inside a luminous nebula",
        "visual_anchors": ("violet dust clouds between tall mineral cliffs", "a small landing light beneath a slow aurora"),
        "quiet_actions": ("resting after a quiet landing", "watching dust drift through the canyon light"),
        "light_moods": ("muted violet and silver with no harsh highlights", "deep blue shadow and soft rose nebula light"),
        "music_brief": "soft piano with long gentle decay, sparse harmony, subtle warm texture, no vocals or percussion",
        "ambience": (
            {"path": "ambience/canyon_wind.wav", "volume": 0.045, "role": "canyon_wind"},
            {"path": "ambience/ship_landing_hum.wav", "volume": 0.035, "role": "ship_landing"},
            {"path": "ambience/distant_resonance.wav", "volume": 0.02, "role": "distant_resonance"},
        ),
    },
)


def _recent_slugs(recent_cards: Iterable[dict[str, Any]]) -> set[str]:
    return {
        str(card.get("scene_slug"))
        for card in recent_cards
        if isinstance(card, dict) and card.get("scene_slug")
    }


def build_scene_card(seed: str, recent_cards: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
    """Build the same Scene Card for the same seed unless recent scenes exclude it."""

    if not isinstance(seed, str) or not seed.strip():
        raise ValueError("seed must be a non-empty string")
    rng = random.Random(seed)
    recent = _recent_slugs(recent_cards)
    available = [scene for scene in SCENE_LIBRARY if scene["slug"] not in recent]
    choices = available or list(SCENE_LIBRARY)
    scene = rng.choice(choices)
    anchor = rng.choice(scene["visual_anchors"])
    action = rng.choice(scene["quiet_actions"])
    light_mood = rng.choice(scene["light_moods"])
    episode_id = f"{scene['slug']}-{seed[:8]}"
    image_prompt = (
        "Create a cinematic 16:9 ultra high resolution image for Nebula Drift ASMR. "
        "Nebula is a quiet space traveler recording a peaceful sleep scene. "
        f"Location: {scene['location']}. Visual anchor: {anchor}. "
        f"Quiet action: {action}. Light and mood: {light_mood}. "
        "Use realistic fantasy sci-fi scale, low contrast, blue/violet/silver/muted-gold palette, "
        "quiet solitude and safe wonder. No text, logo, watermark, visible face, horror, harsh neon, or clutter."
    )
    return {
        "schema_version": 1,
        "episode_id": episode_id,
        "episode_seed": seed,
        "scene_slug": scene["slug"],
        "concept": {
            "location": scene["location"],
            "visual_anchor": anchor,
            "quiet_action": action,
            "light_mood": light_mood,
            "image_prompt": image_prompt,
        },
        "music": {
            "provider": "gemini-lyria-playwright",
            "fresh_generation_required": True,
            "brief": scene["music_brief"],
        },
        "assets": {
            "image": "scene.png",
            "music": ["music/music_candidate_01.mp3"],
            "ambience": [dict(layer) for layer in scene["ambience"]],
        },
        "provenance": {
            "environment_sound_policy": "record source URL, license or generation record, and SHA-256 for every layer",
            "music_policy": "generate fresh music in the Google Gemini/Lyria web UI through a user-visible Windows Chrome/Edge Playwright/CDP session; record the prompt, output format, usage terms, and SHA-256 before rendering; never reuse prior audio",
        },
    }


def load_recent_cards(path: Path) -> list[dict[str, Any]]:
    """Load JSON history or the canonical JSONL episode index."""
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError:
        data = [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(data, dict):
        data = data.get("episodes", [data])
    if not isinstance(data, list):
        raise ValueError("history must be a JSON array, JSONL records, or an object with an episodes array")
    cards: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        scene_value = item.get("scene")
        scene: dict[str, Any] = scene_value if isinstance(scene_value, dict) else {}
        slug = item.get("scene_slug") or scene.get("slug")
        if slug:
            cards.append({"scene_slug": slug})
    return cards


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Scene Card JSON output path")
    parser.add_argument("--seed", help="Reproducible scene seed; generated when omitted")
    parser.add_argument("--history", help="Optional JSON history used to avoid recent scene slugs")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    seed = args.seed or f"{datetime.now(timezone.utc).isoformat()}-{uuid.uuid4().hex[:8]}"
    history = load_recent_cards(Path(args.history).expanduser().resolve()) if args.history else []
    card = build_scene_card(seed, history)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "episode_id": card["episode_id"], "scene_slug": card["scene_slug"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
