#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_scene_card.py"
SPEC = importlib.util.spec_from_file_location("nebula_scene_card_generator", SCRIPT)
assert SPEC and SPEC.loader
scene_generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scene_generator)


class SceneCardGeneratorTests(unittest.TestCase):
    def test_same_seed_is_reproducible(self) -> None:
        first = scene_generator.build_scene_card("fixed-seed")
        second = scene_generator.build_scene_card("fixed-seed")
        self.assertEqual(first, second)

    def test_recent_scene_is_avoided_when_other_scenes_exist(self) -> None:
        recent = scene_generator.build_scene_card("fixed-seed")
        next_card = scene_generator.build_scene_card("fixed-seed", recent_cards=[recent])
        self.assertNotEqual(next_card["scene_slug"], recent["scene_slug"])

    def test_card_contains_layered_soundscape_and_asset_contract(self) -> None:
        card = scene_generator.build_scene_card("soundscape-seed")
        self.assertGreaterEqual(len(card["assets"]["ambience"]), 2)
        self.assertTrue(all("path" in layer and "volume" in layer and "role" in layer for layer in card["assets"]["ambience"]))
        self.assertIn("image_prompt", card["concept"])
        self.assertIn("brief", card["music"])

    def test_episode_index_jsonl_is_accepted_as_history(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "episode-index.jsonl"
            path.write_text(
                json.dumps({"episode_id": "old", "scene": {"slug": "moon-campfire"}}) + "\n",
                encoding="utf-8",
            )
            cards = scene_generator.load_recent_cards(path)
            self.assertEqual(cards, [{"scene_slug": "moon-campfire"}])


if __name__ == "__main__":
    unittest.main()
