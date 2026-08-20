from __future__ import annotations

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


class V1_1PublicationTests(unittest.TestCase):
    def test_publication_artifacts_exist_and_pdf_is_rendered(self) -> None:
        # Arrange / Act
        pdf_prefix = PDF.read_bytes()[:5]

        # Assert
        self.assertTrue(PAGE.is_file())
        self.assertGreater(PDF.stat().st_size, 10_000)
        self.assertEqual(pdf_prefix, b"%PDF-")

    def test_live_version_1_pdf_is_an_embedded_withdrawal_notice(self) -> None:
        # Arrange / Act
        notice = ARCHIVE_NOTICE.read_text()
        normalized_notice = " ".join(notice.split())
        pdf_prefix = ACADEMIC_PDF.read_bytes()[:5]

        # Assert
        self.assertIn("universal convergence", normalized_notice)
        self.assertIn(
            "claims in the original Version 1 PDF are withdrawn",
            normalized_notice,
        )
        self.assertIn("M(t)K(t) &gt; B(t)", normalized_notice)
        self.assertIn("a28695f", normalized_notice)
        self.assertEqual(pdf_prefix, b"%PDF-")
        self.assertGreater(ACADEMIC_PDF.stat().st_size, 5_000)

    def test_paper_states_the_exact_margin_and_nonclaims(self) -> None:
        # Arrange / Act
        paper = PAGE.read_text()

        # Assert
        self.assertIn("M(t) K(t) &gt; B(t)", paper)
        self.assertIn("floor(B / K) + 1", paper)
        self.assertIn("does not prove", paper.lower())
        self.assertIn("interpreter replay remains pending", paper.lower())
        self.assertIn("no publication or value-moving authority", paper.lower())

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
