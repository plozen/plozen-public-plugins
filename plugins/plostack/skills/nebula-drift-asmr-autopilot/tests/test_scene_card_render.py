#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_video.py"
SPEC = importlib.util.spec_from_file_location("nebula_render_video", SCRIPT)
assert SPEC and SPEC.loader
render_video = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_video)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg is required")
class SceneCardRenderTests(unittest.TestCase):
    def make_asset(self, folder: Path, name: str, lavfi: str, *, audio: bool = False) -> Path:
        path = folder / name
        command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", lavfi]
        if audio:
            command += ["-t", "1", "-c:a", "pcm_s16le", str(path)]
        else:
            command += ["-frames:v", "1", str(path)]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return path

    def test_scene_card_mixes_multiple_ambience_layers_and_records_them(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nebula-scene-card-test-") as raw:
            folder = Path(raw)
            self.make_asset(folder, "scene.png", "color=c=black:s=320x180:d=1")
            self.make_asset(folder, "piano.wav", "sine=frequency=440:sample_rate=48000", audio=True)
            self.make_asset(folder, "campfire.wav", "sine=frequency=110:sample_rate=48000", audio=True)
            self.make_asset(folder, "ship_hum.wav", "sine=frequency=70:sample_rate=48000", audio=True)
            card = folder / "scene-card.json"
            card.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "episode_id": "test-moon-campfire",
                        "concept": {
                            "location": "moon camp",
                            "visual_anchor": "small campfire under Earthrise",
                        },
                        "assets": {
                            "image": "scene.png",
                            "music": ["piano.wav"],
                            "ambience": [
                                {"path": "campfire.wav", "volume": 0.16, "role": "campfire"},
                                {"path": "ship_hum.wav", "volume": 0.04, "role": "spaceship"},
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )
            args = render_video.build_parser().parse_args(
                [
                    "--input-dir",
                    str(folder),
                    "--scene-card",
                    str(card),
                    "--duration",
                    "2",
                    "--width",
                    "320",
                    "--height",
                    "180",
                    "--fps",
                    "1",
                    "--crf",
                    "35",
                ]
            )

            summary = render_video.render(args)

            self.assertEqual(summary["scene_card"]["episode_id"], "test-moon-campfire")
            self.assertEqual(len(summary["inputs"]["ambience"]), 2)
            self.assertEqual(
                [entry["role"] for entry in summary["inputs"]["ambience"]],
                ["campfire", "spaceship"],
            )
            self.assertTrue(Path(summary["output"]["path"]).is_file())
            self.assertGreaterEqual(summary["output"]["audio_duration_seconds"], 1.9)

    def test_scene_card_without_ambience_keeps_music_only_compatibility(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nebula-music-only-test-") as raw:
            folder = Path(raw)
            self.make_asset(folder, "scene.png", "color=c=black:s=320x180:d=1")
            self.make_asset(folder, "piano.wav", "sine=frequency=440:sample_rate=48000", audio=True)
            card = folder / "scene-card.json"
            card.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "episode_id": "test-music-only",
                        "assets": {"image": "scene.png", "music": ["piano.wav"], "ambience": []},
                    }
                ),
                encoding="utf-8",
            )
            args = render_video.build_parser().parse_args(
                [
                    "--input-dir",
                    str(folder),
                    "--scene-card",
                    str(card),
                    "--duration",
                    "2",
                    "--width",
                    "320",
                    "--height",
                    "180",
                    "--fps",
                    "1",
                    "--crf",
                    "35",
                ]
            )

            summary = render_video.render(args)

            self.assertEqual(summary["inputs"]["ambience"], [])
            self.assertTrue(Path(summary["output"]["path"]).is_file())


if __name__ == "__main__":
    unittest.main()
