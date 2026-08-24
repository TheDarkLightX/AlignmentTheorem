from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
TOOLCHAINS = ROOT / "TOOLCHAINS.md"
PAGE = ROOT / "docs" / "v1-1-hyperdeflationary-alignment.html"
INDEX = ROOT / "docs" / "index.html"
PDF = ROOT / "docs" / "Alignment_Theorem_V1_1_Hyperdeflationary.pdf"
ARCHIVE_NOTICE = ROOT / "docs" / "alignment-theorem-v1-archive-notice.html"
ACADEMIC_PDF = ROOT / "docs" / "Alignment_Theorem_Academic.pdf"
ORIGINAL_V1_PDF = ROOT / "docs" / "Alignment_Theorem_V1_Original_2025.pdf"
V1_1_MODEL = ROOT / "verification" / "alignment_v1_1_model.py"
V1_1_LEAN = ROOT / "proofs" / "v1_1" / "AlignmentTheoremV1_1.lean"


class V1_1PublicationTests(unittest.TestCase):
    def test_publication_artifacts_exist_and_pdf_is_rendered(self) -> None:
        # Arrange / Act
        pdf_prefix = PDF.read_bytes()[:5]

        # Assert
        self.assertTrue(PAGE.is_file())
        self.assertGreater(PDF.stat().st_size, 10_000)
        self.assertEqual(pdf_prefix, b"%PDF-")

    def test_live_version_1_pdf_is_an_embedded_claim_boundary(self) -> None:
        # Arrange / Act
        notice = ARCHIVE_NOTICE.read_text()
        normalized_notice = " ".join(notice.split())
        normalized_notice_lower = normalized_notice.lower()
        pdf_prefix = ACADEMIC_PDF.read_bytes()[:5]

        # Assert
        self.assertIn("core mechanism is retained", normalized_notice_lower)
        self.assertIn("not a tax or fine", normalized_notice_lower)
        self.assertIn("G &lt; M(R+L)", normalized_notice)
        self.assertIn("M(t)K(t) &gt; B(t)", normalized_notice)
        self.assertIn("a28695f", normalized_notice)
        self.assertEqual(pdf_prefix, b"%PDF-")
        self.assertGreater(ACADEMIC_PDF.stat().st_size, 5_000)
        self.assertEqual(
            hashlib.sha256(ORIGINAL_V1_PDF.read_bytes()).hexdigest(),
            "f5dca5a1e7bcd069441f16410664cdecac3eeebe4a5af8f128dd0efa7043c8bc",
        )
        self.assertIn("Alignment_Theorem_V1_Original_2025.pdf", notice)

    def test_paper_states_the_exact_margin_and_nonclaims(self) -> None:
        # Arrange / Act
        paper = PAGE.read_text()

        # Assert
        self.assertIn("M(t) K(t) &gt; B(t)", paper)
        self.assertIn("floor(B / K) + 1", paper)
        self.assertIn("does not prove", paper.lower())
        self.assertIn("local tau build pinned to a specific source commit matched", paper.lower())
        self.assertIn("review of the compiled binary and public-node deployment remain pending", paper.lower())
        self.assertIn("no publication or value-moving authority", paper.lower())

    def test_active_v1_1_surfaces_use_the_no_debit_exclusion_model(self) -> None:
        for path in (V1_1_MODEL, V1_1_LEAN, PAGE):
            with self.subTest(path=path):
                text = path.read_text().lower()
                self.assertNotIn("forfeit", text)
                self.assertNotIn("punitive penalty", text)
                self.assertTrue(
                    any(
                        phrase in text
                        for phrase in ("no debit", "no-debit", "no punitive debit")
                    )
                )

    def test_public_pages_link_to_version_1_1_artifacts(self) -> None:
        # Arrange
        readme = README.read_text()
        index = INDEX.read_text()

        # Act / Assert
        for relative in (
            "docs/v1-1-hyperdeflationary-alignment.html",
            "docs/Alignment_Theorem_V1_1_Hyperdeflationary.pdf",
        ):
            self.assertIn(relative, readme)
            self.assertTrue((ROOT / relative).is_file())
        self.assertIn('href="v1-1-hyperdeflationary-alignment.html"', index)
        self.assertIn(
            'href="Alignment_Theorem_V1_1_Hyperdeflationary.pdf"', index
        )
        self.assertIn('href="Alignment_Theorem_Academic.pdf"', index)

    def test_paper_has_no_machine_local_link_or_path(self) -> None:
        # Arrange / Act
        paper = PAGE.read_text()

        # Assert
        forbidden = ("file://", "localhost", "/tmp/", "/home/")
        self.assertFalse(any(value in paper for value in forbidden))
        local_targets = re.findall(r'href="(?!https?://|#)([^"]+)"', paper)
        for target in local_targets:
            self.assertTrue((PAGE.parent / target).is_file(), target)

    def test_tau_replay_docs_separate_binary_checks_from_build_provenance(self) -> None:
        # Arrange / Act
        toolchains = " ".join(TOOLCHAINS.read_text().split())

        # Assert
        self.assertIn("does not rebuild the executable", toolchains)
        self.assertIn("immutable image digest", toolchains)
        self.assertIn("do not edit the accepted hash solely", toolchains)
        self.assertIn("capture_tau_v1_1_candidate.py", toolchains)
        self.assertIn("promotion_eligible", toolchains)


if __name__ == "__main__":
    unittest.main()
