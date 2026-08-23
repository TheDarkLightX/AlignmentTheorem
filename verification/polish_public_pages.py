#!/usr/bin/env python3
"""Validate the public GitHub Pages for required accessibility, link, and content invariants.

The pages are now hand-authored under a unified design system, so this script
no longer mutates them. It is a deterministic, idempotent guard: it reads the
two public pages, asserts the invariants they must keep, and writes nothing.
Running it twice (or after a commit) therefore never produces a diff, which
keeps the CI "polish is idempotent" step green.

If a required invariant is missing, the script exits non-zero with the list of
failed checks so the regression is caught before publication.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
ESSAY = ROOT / "docs" / "data-center-social-contract.html"


def _requirements(index: str, essay: str) -> dict[str, bool]:
    """Return the named invariants and whether each currently holds."""
    return {
        # Cross-page integration: index must promote the data-center essay.
        "index links data-center essay": 'href="data-center-social-contract.html"' in index,
        "index features data-center essay": 'class="featured-essay"' in index,
        # Version 1.1 / archive artifacts must remain reachable from the index.
        "index links v1.1 paper": 'href="v1-1-hyperdeflationary-alignment.html"' in index,
        "index links v1.1 pdf": 'href="Alignment_Theorem_V1_1_Hyperdeflationary.pdf"' in index,
        "index links academic pdf": 'href="Alignment_Theorem_Academic.pdf"' in index,
        # Accessibility landmarks and controls.
        "index skip link": 'class="skip-link"' in index,
        "index main landmark": 'id="main-content"' in index,
        "index accessible scenario controls": '<button type="button" class="scenario-button' in index,
        "index labeled scarcity slider": 'label for="scarcitySlider"' in index,
        "index labeled eetf slider": 'label for="eetfSlider"' in index,
        "index calculator live region": 'aria-live="polite"' in index,
        "index reduced-motion support": "prefers-reduced-motion" in index,
        # Mobile data table must scroll within a contained region.
        "index data table scroll region": 'class="table-scroll"' in index,
        # Essay canonical URL and deployed link hygiene.
        "essay canonical": 'rel="canonical" href="https://thedarklightx.github.io/AlignmentTheorem/data-center-social-contract.html"' in essay,
        "essay no feature-branch link": "research/compute-dividend-wealth-agent" not in essay,
        "essay no relative research path": "../research/" not in essay,
        # Essay accessibility and calculator controls.
        "essay skip link": 'class="skip-link"' in essay,
        "essay main landmark": 'id="main-content"' in essay,
        "essay labeled deficits input": 'label for="deficits"' in essay,
        "essay calculator live region": 'aria-live="polite"' in essay,
        "essay reduced-motion support": "prefers-reduced-motion" in essay,
        # Required essay content anchors (kept in sync with the publication tests).
        "essay title": "The Data Center Bargain" in essay,
        "essay calculator heading": "Community bargain solvency calculator" in essay,
        "essay tau section": "Why the full version requires Tau Language" in essay,
        "essay exclusivity claim": "The exclusivity claim is architectural, not mystical" in essay,
        "essay playbook link": "LOCAL_GOVERNMENT_POLICY_PLAYBOOK.md" in essay,
        "essay canonical formula R": "R=(G-C)_+" in essay,
        "essay canonical formula d": "d_i=(L_i-B_i)_+" in essay,
        "essay canonical formula h": "h_i=\\max\\{m,d_i\\}" in essay,
        "essay admission condition": "G\\ge C+H(m)" in essay,
        "essay compute condition": "Q\\ge nc" in essay,
        "essay price ratio": "P_{t+1}" in essay,
        # No machine-local references may leak into either public page.
        "index no file uri": "file://" not in index,
        "index no localhost": "localhost" not in index,
        "essay no file uri": "file://" not in essay,
        "essay no localhost": "localhost" not in essay,
        "essay no mnt data": "/mnt/data" not in essay,
    }


def validate(index: str, essay: str) -> None:
    failed = [name for name, ok in _requirements(index, essay).items() if not ok]
    if failed:
        raise RuntimeError(f"page validation failed: {failed}")


if __name__ == "__main__":
    index = INDEX.read_text()
    essay = ESSAY.read_text()
    validate(index, essay)
    print(f"validated {INDEX.relative_to(ROOT)} ({len(index)} bytes)")
    print(f"validated {ESSAY.relative_to(ROOT)} ({len(essay)} bytes)")
