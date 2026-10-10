"""Release archive reproducibility and integrity tests (stdlib only)."""
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_release import build, verify


class ReleasePackagingTests(unittest.TestCase):
    COMMIT = "f" * 40
    CI = "https://github.com/seydivakkas/MinimalAdam/actions/runs/37999395061"

    def test_release_contains_all_files_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            archive, manifest, sums = build(ROOT, Path(td), "0.6.1", self.COMMIT, self.CI)
            verify(archive, manifest, sums)
            meta = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(meta["source_commit"], self.COMMIT)
            self.assertIn("editor/offline.html", meta["files"])
            self.assertIn("minimaladam/SKILL.md", meta["files"])
            self.assertIn("LICENSE", meta["files"])
            self.assertGreater(meta["file_count"], 100)
            with zipfile.ZipFile(archive) as zf:
                self.assertIn("MinimalAdam/RELEASE_MANIFEST.json", zf.namelist())
                self.assertNotIn("MinimalAdam/.git/config", zf.namelist())

    def test_byte_for_byte_reproducible_archive(self):
        with tempfile.TemporaryDirectory() as td:
            a = build(ROOT, Path(td) / "a", "0.6.1", self.COMMIT, self.CI)
            b = build(ROOT, Path(td) / "b", "0.6.1", self.COMMIT, self.CI)
            for left, right in zip(a, b):
                self.assertEqual(hashlib.sha256(left.read_bytes()).digest(),
                                 hashlib.sha256(right.read_bytes()).digest())

    def test_reject_invalid_commit(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "Git SHA"):
                build(ROOT, Path(td), "0.6.1", "unknown", self.CI)


if __name__ == "__main__":
    unittest.main()
