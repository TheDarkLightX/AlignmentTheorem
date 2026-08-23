#!/usr/bin/env python3
"""Validate the hand-authored public pages without mutating them.

This deterministic guard covers accessibility, route integration, claim
boundaries, and the V1 no-debit exclusion interpretation. A failed invariant
stops publication before a stale or misleading page can reach GitHub Pages.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = {
    "index": ROOT / "docs" / "index.html",
    "data_center": ROOT / "docs" / "data-center-social-contract.html",
    "deep_dive": ROOT / "docs" / "alignment-theorem-deep-dive.html",
    "v1_boundary": ROOT / "docs" / "alignment-theorem-v1-archive-notice.html",
    "v1_1": ROOT / "docs" / "v1-1-hyperdeflationary-alignment.html",
    "playbook": ROOT / "docs" / "local-government-policy-playbook.html",
    "current_tau": ROOT / "docs" / "current-tau-net-integration.html",
    "flywheel": ROOT / "docs" / "intelligence-hyperdeflation-flywheel.html",
}
CANONICALS = {
    "index": "https://thedarklightx.github.io/AlignmentTheorem/",
    **{
        name: f"https://thedarklightx.github.io/AlignmentTheorem/{path.name}"
        for name, path in PUBLIC_PAGES.items()
        if name != "index"
    },
}


class _StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.blank_targets_without_noopener: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)
        if tag != "a":
            return
        href = values.get("href")
        if href is not None:
            self.hrefs.append(href)
        if values.get("target") == "_blank":
            rel = set((values.get("rel") or "").split())
            if "noopener" not in rel:
                self.blank_targets_without_noopener.append(href or "<empty>")


def _structure_checks(
    name: str, path: Path, page: str
) -> dict[str, bool]:
    parser = _StructureParser()
    parser.feed(page)
    ids = set(parser.ids)
    local_targets: list[tuple[Path, str]] = []
    same_page_fragments: list[str] = []

    for href in parser.hrefs:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            continue
        if not parsed.path:
            if parsed.fragment:
                same_page_fragments.append(unquote(parsed.fragment))
            continue
        local_targets.append(
            (path.parent / unquote(parsed.path), unquote(parsed.fragment))
        )

    docs_root = (ROOT / "docs").resolve()
    local_targets_stay_public = all(
        target.resolve().is_relative_to(docs_root) for target, _ in local_targets
    )
    local_fragments_resolve = all(
        not fragment or f'id="{fragment}"' in target.read_text()
        for target, fragment in local_targets
        if target.is_file() and target.suffix.lower() == ".html"
    )

    return {
        f"{name} has unique element IDs": len(parser.ids) == len(ids),
        f"{name} has no empty links": all(href and href != "#" for href in parser.hrefs),
        f"{name} same-page fragments resolve": all(
            fragment in ids for fragment in same_page_fragments
        ),
        f"{name} local links stay in public docs": local_targets_stay_public,
        f"{name} local link targets exist": all(
            target.is_file() for target, _ in local_targets
        ),
        f"{name} cross-page fragments resolve": local_fragments_resolve,
        f"{name} blank targets use noopener": not parser.blank_targets_without_noopener,
    }


def _requirements(pages: dict[str, str]) -> dict[str, bool]:
    """Return every named publication invariant and its current status."""
    index = pages["index"]
    essay = pages["data_center"]
    deep_dive = pages["deep_dive"]
    v1_boundary = pages["v1_boundary"]
    v1_1 = pages["v1_1"]
    playbook = pages["playbook"]
    current_tau = pages["current_tau"]

    checks = {
        # Cross-page integration and durable downloads.
        "index links data-center essay": 'href="data-center-social-contract.html"' in index,
        "index features data-center essay": 'class="featured-essay"' in index,
        "index links V1 deep dive": 'href="alignment-theorem-deep-dive.html"' in index,
        "index links V1 boundary": 'href="alignment-theorem-v1-archive-notice.html"' in index,
        "index links original V1 paper": 'href="Alignment_Theorem_V1_Original_2025.pdf"' in index,
        "index links V1.1 paper": 'href="v1-1-hyperdeflationary-alignment.html"' in index,
        "index links V1.1 PDF": 'href="Alignment_Theorem_V1_1_Hyperdeflationary.pdf"' in index,
        "index links V1 boundary PDF": 'href="Alignment_Theorem_Academic.pdf"' in index,
        "index links current Tau matrix": 'href="current-tau-net-integration.html"' in index,
        "index links intelligence flywheel": 'href="intelligence-hyperdeflation-flywheel.html"' in index,
        "index links public playbook": 'href="local-government-policy-playbook.html"' in index,
        "deep dive links intelligence flywheel": 'href="intelligence-hyperdeflation-flywheel.html"' in deep_dive,
        "essay links public playbook": 'href="local-government-policy-playbook.html"' in essay,
        "essay links playbook source": "LOCAL_GOVERNMENT_POLICY_PLAYBOOK.md" in essay,
        # Homepage accessibility and interactive calculator.
        "index skip link": 'class="skip-link"' in index,
        "index main landmark": 'id="main-content"' in index,
        "index accessible scenario controls": '<button type="button" class="scenario-button' in index,
        "index labeled scarcity slider": 'label for="scarcitySlider"' in index,
        "index labeled EETF slider": 'label for="eetfSlider"' in index,
        "index calculator live region": 'aria-live="polite"' in index,
        "index reduced-motion support": "prefers-reduced-motion" in index,
        "index data table scroll region": 'class="table-scroll"' in index,
        # V1 semantics: exclusion with protected upside and no punitive effect.
        "index names missed scarcity upside": "Scarcity Upside Missed Through Exclusion" in index,
        "index has no-debit explanation": "no punitive debit occurs" in index,
        "index renders missed value without minus": " + ' missed'" in index,
        "deep dive states V1 theorem": "EETF-Gated Scarcity-Upside Exclusion Theorem" in deep_dive,
        "deep dive states strict margin": "M(R + L) &gt; G" in deep_dive,
        "deep dive states no balance debit": "No tax or balance debit" in deep_dive,
        "deep dive avoids unconditional scarcity slogan": "Scarcity Drives Ethics" not in deep_dive,
        "V1 boundary retains full mechanism": "EETF, VCC, reward, scarcity, and exclusion" in v1_boundary,
        "V1 boundary states exact finite condition": "G &lt; M(R+L)" in v1_boundary,
        "V1 boundary states no punitive effects": "No tax, fine, burn, confiscation, or balance debit" in v1_boundary,
        "V1 boundary links original paper": "Alignment_Theorem_V1_Original_2025.pdf" in v1_boundary,
        "active V1 pages do not say withdrawn": all(
            "withdrawn" not in page.lower()
            for page in (index, deep_dive, v1_boundary, v1_1)
        ),
        "active V1 pages do not say superseded": all(
            "superseded" not in page.lower()
            for page in (index, deep_dive, v1_boundary, v1_1)
        ),
        "V1.1 uses exclusive-upside model": "scarcity upside available only to the eligible branch" in v1_1.lower(),
        "V1.1 states no punitive debit": "no punitive debit" in v1_1,
        "V1.1 avoids forfeiture model": "forfeit" not in v1_1.lower(),
        # Data-center essay and restored public playbook.
        "essay canonical": 'rel="canonical" href="https://thedarklightx.github.io/AlignmentTheorem/data-center-social-contract.html"' in essay,
        "essay title": "The Data Center Bargain" in essay,
        "essay calculator heading": "Community bargain solvency calculator" in essay,
        "essay Tau section": "Why the full version requires Tau Language" in essay,
        "essay exclusivity claim": "The exclusivity claim is architectural, not mystical" in essay,
        "essay canonical formula R": "R=(G-C)_+" in essay,
        "essay canonical formula d": "d_i=(L_i-B_i)_+" in essay,
        "essay canonical formula h": "h_i=\\max\\{m,d_i\\}" in essay,
        "essay admission condition": "G\\ge C+H(m)" in essay,
        "essay compute condition": "Q\\ge nc" in essay,
        "essay price ratio": "P_{t+1}" in essay,
        "essay skip link": 'class="skip-link"' in essay,
        "essay main landmark": 'id="main-content"' in essay,
        "essay labeled deficits input": 'label for="deficits"' in essay,
        "essay calculator live region": 'aria-live="polite"' in essay,
        "essay reduced-motion support": "prefers-reduced-motion" in essay,
        "playbook is populated": len(playbook) > 10_000,
        "playbook has local enforcement instruments": all(
            phrase in playbook
            for phrase in ("nonperformance consequences", "suspension and clawback")
        ),
        # Current Tau evidence and authority ceiling.
        "current Tau reports three profiles": "Three profiles" in current_tau,
        "current Tau reports native router cases": "27 / 27" in current_tau,
        "current Tau marks supplied facts": "transaction-supplied claims" in current_tau,
    }

    for name, page in pages.items():
        checks[f"{name} has exact canonical URL"] = (
            f'rel="canonical" href="{CANONICALS[name]}"' in page
        )
        checks[f"{name} has no file URI"] = "file://" not in page
        checks[f"{name} has no localhost URL"] = "localhost" not in page
        checks[f"{name} has no machine-local path"] = all(
            value not in page for value in ("/tmp/", "/home/", "/mnt/data")
        )
        checks[f"{name} has no stale feature-branch link"] = (
            "research/compute-dividend-wealth-agent" not in page
        )
        checks.update(_structure_checks(name, PUBLIC_PAGES[name], page))

    return checks


def validate(pages: dict[str, str]) -> None:
    failed = [name for name, ok in _requirements(pages).items() if not ok]
    if failed:
        raise RuntimeError(f"page validation failed: {failed}")


if __name__ == "__main__":
    page_text = {name: path.read_text() for name, path in PUBLIC_PAGES.items()}
    validate(page_text)
    for name, path in PUBLIC_PAGES.items():
        print(f"validated {path.relative_to(ROOT)} ({len(page_text[name])} bytes)")
