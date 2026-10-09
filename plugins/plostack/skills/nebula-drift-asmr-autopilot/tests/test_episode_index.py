from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_episode_index.py"
SPEC = importlib.util.spec_from_file_location("nebula_episode_index", SCRIPT)
assert SPEC and SPEC.loader
episode_index = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(episode_index)


class EpisodeIndexTests(unittest.TestCase):
    def test_upsert_replaces_record_and_preserves_status_history(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            index = Path(raw) / "episode-index.jsonl"
            first = {
                "episode_id": "episode-1",
                "status": "concept_draft",
                "recorded_at": "t1",
                "image_log_migration": {"candidates": [{"path": "candidate.png"}]},
            }
            second = {"episode_id": "episode-1", "status": "rendered", "recorded_at": "t2"}
            episode_index.upsert_record(index, first)
            episode_index.upsert_record(index, second)
            rows = episode_index.load_index(index)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "rendered")
            self.assertEqual(rows[0]["status_history"], [{"status": "concept_draft", "recorded_at": "t1"}])
            self.assertEqual(rows[0]["image_log_migration"]["candidates"][0]["path"], "candidate.png")

    def test_build_record_uses_relative_paths_and_private_readback(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            episode = root / "episodes" / "20260928_test-scene"
            episode.mkdir(parents=True)
            (episode / "scene-card.json").write_text(
                json.dumps(
                    {
                        "episode_id": "test-scene-20260928",
                        "scene_slug": "test-scene",
                        "concept": {
                            "location": "a quiet test station",
                            "visual_anchor": "a blue window",
                            "quiet_action": "resting",
                            "light_mood": "soft blue",
                        },
                        "assets": {"ambience": [{"role": "station_hum"}]},
                    }
                ),
                encoding="utf-8",
            )
            (episode / "metadata.json").write_text(json.dumps({"title": "Test Station"}), encoding="utf-8")
            (episode / "youtube-upload.json").write_text(
                json.dumps({"video_id": "abc", "privacy_status": "private", "readback_verified": True, "access_token": "do-not-copy"}),
                encoding="utf-8",
            )
            index = root / "episode-index.jsonl"
            record = episode_index.build_record(episode, index)
            self.assertEqual(record["status"], "private_uploaded")
            self.assertEqual(record["source_dir"], "episodes/20260928_test-scene")
            self.assertEqual(record["scene"]["slug"], "test-scene")
            self.assertEqual(record["youtube"], {"video_id": "abc", "url": None, "privacy_status": "private", "publish_at": None, "readback_verified": True})
            self.assertNotIn("access_token", json.dumps(record))


if __name__ == "__main__":
    unittest.main()
