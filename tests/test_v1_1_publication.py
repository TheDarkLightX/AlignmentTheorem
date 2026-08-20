from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PAGE = ROOT / "docs" / "v1-1-hyperdeflationary-alignment.html"
INDEX = ROOT / "docs" / "index.html"
PDF = ROOT / "docs" / "Alignment_Theorem_V1_1_Hyperdeflationary.pdf"


class V1_1PublicationTests(unittest.TestCase):
    def test_publication_artifacts_exist_and_pdf_is_rendered(self) -> None:
        # Arrange / Act
        pdf_prefix = PDF.read_bytes()[:5]

        # Assert
        self.assertTrue(PAGE.is_file())
        self.assertGreater(PDF.stat().st_size, 10_000)
        self.assertEqual(pdf_prefix, b"%PDF-")

    def test_paper_states_the_exact_margin_and_nonclaims(self) -> None:
        # Arrange / Act
        paper = PAGE.read_text()

        # Assert
        self.assertIn("M(t) K(t) &gt; B(t)", paper)
        self.assertIn("floor(B / K) + 1", paper)
        self.assertIn("does not prove", paper.lower())
        self.assertIn("interpreter replay remains pending", paper.lower())

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

    def test_paper_has_no_machine_local_link_or_path(self) -> None:
        # Arrange / Act
        paper = PAGE.read_text()

        # Assert
        forbidden = ("file://", "localhost", "/tmp/", "/home/")
        self.assertFalse(any(value in paper for value in forbidden))
        local_targets = re.findall(r'href="(?!https?://|#)([^"]+)"', paper)
        for target in local_targets:
            self.assertTrue((PAGE.parent / target).is_file(), target)


if __name__ == "__main__":
    unittest.main()
