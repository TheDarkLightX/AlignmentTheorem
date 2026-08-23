from __future__ import annotations

import json
import sys
import unittest

from verification.run_compute_dividend_campaign import (
    LEAN_RECEIPT,
    MODEL,
    MODEL_TEST,
    REPO_ROOT,
    TAU_GENERATOR,
    TAU_TEST,
    _sha256,
    run,
)

RECEIPT = (
    REPO_ROOT / "verification" / "receipts" / "compute_dividend_campaign.json"
)
CHECKER = REPO_ROOT / "verification" / "run_compute_dividend_campaign.py"


class ComputeDividendCampaignReceiptTests(unittest.TestCase):
    def test_receipt_is_source_bound_and_recomputes_exactly(self) -> None:
        stored = json.loads(RECEIPT.read_text())
        rerun = run()

        self.assertTrue(stored["passed"])
        self.assertEqual(stored, rerun)
        self.assertEqual(
            stored["python_version"],
            f"{sys.version_info.major}.{sys.version_info.minor}",
        )
        self.assertEqual(stored["checker_sha256"], _sha256(CHECKER))
        self.assertEqual(
            stored["bound_files_sha256"],
            {
                "verification/compute_dividend_model.py": _sha256(MODEL),
                "tests/test_compute_dividend_model.py": _sha256(MODEL_TEST),
                "tests/test_tau_compute_dividend.py": _sha256(TAU_TEST),
                "verification/generate_tau_compute_dividend_packets.py": _sha256(
                    TAU_GENERATOR
                ),
                "verification/receipts/lean_compute_dividend_v4.33.0.json": _sha256(
                    LEAN_RECEIPT
                ),
            },
        )
        self.assertEqual(stored["allocation_campaign"]["cases"], 10_836)
        self.assertEqual(stored["allocation_campaign"]["mismatches"], [])
        self.assertEqual(stored["progressive_transfer_campaign"]["cases"], 1_024)
        self.assertEqual(stored["progressive_transfer_campaign"]["mismatches"], [])
        self.assertEqual(
            stored["tau_interpreter_replay_status"],
            "PENDING_REVIEWED_BINARY_c4926740",
        )


if __name__ == "__main__":
    unittest.main()
