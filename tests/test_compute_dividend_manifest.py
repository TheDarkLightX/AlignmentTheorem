from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from verification.generate_compute_dividend_manifest import BASE_REVISION, generate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research" / "compute_dividend" / "manifest.json"


class ComputeDividendManifestTests(unittest.TestCase):
    def test_manifest_is_exact_generator_output_and_git_bound(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        revision = manifest["artifact_revision"]

        self.assertEqual(manifest, generate(revision))
        self.assertEqual(manifest["base_revision"], BASE_REVISION)
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE_REVISION, revision],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(ancestor.returncode, 0)

        for relative, expected_hash in manifest["files_sha256"].items():
            with self.subTest(path=relative):
                blob = subprocess.run(
                    ["git", "show", f"{revision}:{relative}"],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                ).stdout
                self.assertEqual(hashlib.sha256(blob).hexdigest(), expected_hash)
                self.assertEqual(blob, (ROOT / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
