from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
INDEX = ROOT / "docs" / "index.html"
DEEP_DIVE = ROOT / "docs" / "alignment-theorem-deep-dive.html"
CLAIM_BOUNDARY = ROOT / "docs" / "alignment-theorem-v1-archive-notice.html"
CORRECTIONS = ROOT / "docs" / "V1_TO_V2_CORRECTIONS.md"
AUDIT = ROOT / "research" / "v1" / "ACADEMIC_PAPER_AUDIT.md"
CURRENT_TAU = ROOT / "docs" / "current-tau-net-integration.html"
VERIFICATION_SUMMARY = ROOT / "docs" / "VERIFICATION_SUMMARY.md"


class V1PublicationTests(unittest.TestCase):
    def test_pages_present_full_eetf_vcc_exclusion_mechanism(self) -> None:
        for path in (README, INDEX, DEEP_DIVE, CLAIM_BOUNDARY, CORRECTIONS, AUDIT):
            with self.subTest(path=path):
                text = " ".join(path.read_text().split())
                self.assertIn("exclusion", text.lower())
                self.assertIn("scarcity", text.lower())
        deep_dive = DEEP_DIVE.read_text()
        self.assertIn("EETF-Gated Scarcity-Upside Exclusion Theorem", deep_dive)
        self.assertIn("M(R + L) &gt; G", deep_dive)
        self.assertIn("No tax or balance debit", deep_dive)

    def test_public_wording_does_not_reduce_v1_to_sign_separation(self) -> None:
        for path in (README, INDEX, DEEP_DIVE, CURRENT_TAU, VERIFICATION_SUMMARY):
            with self.subTest(path=path):
                text = path.read_text().lower()
                self.assertNotIn("version 1: sign-separated", text)
                self.assertNotIn("v1 sign-separated", text)
                self.assertNotIn("semantic claim superseded", text)
        index = INDEX.read_text()
        self.assertIn("exclusive scarcity upside", index)
        self.assertIn("does not impose a tax", README.read_text())

    def test_v1_claim_boundary_distinguishes_opportunity_cost_from_debit(self) -> None:
        text = " ".join(CLAIM_BOUNDARY.read_text().split())
        self.assertIn("G &lt; M(R+L)", text)
        self.assertIn("No balance is debited, no tokens are burned, and no confiscation occurs", text)
        self.assertIn("Upside shared by both branches cancels", text)
        self.assertIn("a28695f", text)

    def test_current_tau_page_reports_exact_v1_packet(self) -> None:
        text = CURRENT_TAU.read_text()
        self.assertIn("Scarcity-upside exclusion", text)
        self.assertIn("128 / [0]", text)
        self.assertIn("27 / 27", text)
        self.assertIn("transaction-supplied claims", text)
        self.assertIn("9b191af689ab", text)

    def test_homepage_describes_missed_upside_without_a_debit_display(self) -> None:
        text = INDEX.read_text()
        self.assertIn("not a tax or fine", text)
        self.assertIn("opportunity cost", text)

    def test_no_machine_local_paths_in_new_public_pages(self) -> None:
        for path in (INDEX, DEEP_DIVE, CLAIM_BOUNDARY, CURRENT_TAU):
            text = path.read_text()
            with self.subTest(path=path):
                for forbidden in ("file://", "/tmp/", "/home/", "localhost"):
                    self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
