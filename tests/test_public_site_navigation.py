from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
DATA_CENTER = ROOT / "docs" / "data-center-social-contract.html"
V11 = ROOT / "docs" / "v1-1-hyperdeflationary-alignment.html"
DEEP_DIVE = ROOT / "docs" / "alignment-theorem-deep-dive.html"


class PublicSiteNavigationTests(unittest.TestCase):
    def test_homepage_routes_to_every_public_essay(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        for target in (
            "data-center-social-contract.html",
            "v1-1-hyperdeflationary-alignment.html",
            "alignment-theorem-deep-dive.html",
            "Alignment_Theorem_V2.pdf",
        ):
            with self.subTest(target=target):
                self.assertIn(f'href="{target}"', html)

        self.assertTrue(DATA_CENTER.is_file())
        self.assertTrue(V11.is_file())
        self.assertTrue(DEEP_DIVE.is_file())

    def test_homepage_has_accessibility_and_responsive_guards(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        required = (
            'class="skip-link"',
            'href="#main"',
            'id="main"',
            'aria-label="Primary navigation"',
            'aria-current="page"',
            ':focus-visible',
            'prefers-reduced-motion: reduce',
            '@media (max-width: 680px)',
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, html)

    def test_homepage_has_complete_metadata_and_no_dead_fragment_links(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('<meta name="description"', html)
        self.assertIn('<meta name="viewport"', html)
        self.assertIn('<meta property="og:title"', html)
        self.assertNotIn('href="#"', html)

        fragment_links = set(re.findall(r'href="#([A-Za-z][A-Za-z0-9_-]*)"', html))
        element_ids = set(re.findall(r'\bid="([A-Za-z][A-Za-z0-9_-]*)"', html))
        self.assertLessEqual(fragment_links, element_ids)

    def test_data_center_essay_retains_interactive_and_claim_boundary_sections(self) -> None:
        html = DATA_CENTER.read_text(encoding="utf-8")
        required = (
            "The Data Center Bargain",
            "community-solvency",
            "Why Tau",
            "not production-ready",
            "H(m)",
        )
        normalized = html.lower()
        self.assertIn("data center bargain", normalized)
        self.assertIn("tau", normalized)
        self.assertIn("calculator", normalized)
        self.assertIn("claim boundary", normalized)
        self.assertIn("h(m)", normalized)


if __name__ == "__main__":
    unittest.main()
