from __future__ import annotations

import json
import unittest

from verification.run_lean_compute_dividend import (
    COMPATIBILITY_SHIM_SOURCE,
    EXPECTED_AXIOMS,
    PLACEHOLDER,
    PROOF_FILES,
    PROOF_ROOT,
    REPO_ROOT,
    _bundle_sha256,
    _sha256,
)

RECEIPT = (
    REPO_ROOT
    / "verification"
    / "receipts"
    / "lean_compute_dividend_v4.33.0.json"
)
CHECKER = REPO_ROOT / "verification" / "run_lean_compute_dividend.py"


class ComputeDividendLeanReceiptTests(unittest.TestCase):
    def test_receipt_binds_exact_placeholder_free_sources_and_boundary(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        files = {relative: _sha256(PROOF_ROOT / relative) for relative in PROOF_FILES}
        source = (PROOF_ROOT / "ComputeDividend.lean").read_text()

        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["source_files_sha256"], files)
        self.assertEqual(receipt["source_bundle_sha256"], _bundle_sha256(files))
        self.assertEqual(receipt["checker_sha256"], _sha256(CHECKER))
        self.assertEqual(
            receipt["compatibility_shim_source_sha256"],
            _sha256(COMPATIBILITY_SHIM_SOURCE),
        )
        self.assertEqual(sorted(set(PLACEHOLDER.findall(source))), [])
        self.assertEqual(receipt["placeholders"], [])
        self.assertIn("version 4.33.0", receipt["lean_version"])
        self.assertEqual(receipt["axiom_reports"], EXPECTED_AXIOMS)
        self.assertEqual(receipt["expected_axiom_reports"], EXPECTED_AXIOMS)
        self.assertEqual(receipt["axiom_audit_returncode"], 0)
        self.assertEqual(
            receipt["execution_environment_status"],
            "HOST_KERNEL_LIBRARIES_AND_SANDBOX_NOT_HERMETICALLY_ATTESTED",
        )
        self.assertTrue(receipt["ld_preload"])


if __name__ == "__main__":
    unittest.main()
