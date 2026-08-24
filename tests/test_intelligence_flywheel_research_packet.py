from __future__ import annotations

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "research" / "intelligence_flywheel"
PAGE = ROOT / "docs" / "intelligence-hyperdeflation-flywheel.html"


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")


class IntelligenceFlywheelResearchPacketTests(unittest.TestCase):
    def test_ledgers_have_closed_ids_and_evidence_links(self) -> None:
        sources = json.loads((PACKET / "source_ledger.json").read_text())
        hypotheses = json.loads((PACKET / "hypothesis_ledger.json").read_text())
        experiments = json.loads((PACKET / "experiment_ledger.json").read_text())
        source_ids = {row["id"] for row in sources["sources"]}
        evidence_ids = {row["id"] for row in experiments["experiments"]}
        self.assertEqual(len(source_ids), len(sources["sources"]))
        self.assertEqual(len(evidence_ids), len(experiments["experiments"]))
        for hypothesis in hypotheses["hypotheses"]:
            self.assertTrue(set(hypothesis["source_ids"]) <= source_ids)
            self.assertTrue(set(hypothesis["evidence_ids"]) <= evidence_ids)
            self.assertTrue(hypothesis["assumptions"])
            self.assertTrue(hypothesis["falsifiers"])

    def test_claim_boundary_preserves_every_trust_boundary(self) -> None:
        boundary = (PACKET / "CLAIM_BOUNDARY.md").read_text().lower()
        for phrase in (
            "not claimed",
            "source-to-binary",
            "hermetically attested",
            "submitters",
            "node deployment",
            "objective ethics",
            "no non-tau formal system",
            "reviewed `c4926740",
        ):
            self.assertIn(phrase, boundary)

    def test_research_kernel_status_is_not_fabricated(self) -> None:
        status = json.loads((PACKET / "research_kernel_status.json").read_text())
        blocker = json.loads((PACKET / "handoff_blocker.json").read_text())
        self.assertFalse(status["mcp_run_started"])
        self.assertFalse(status["promotion_invoked"])
        self.assertIn("NOT_MCP_RECEIPT", status["status"])
        self.assertIn("BLOCKED", blocker["status"])
        self.assertIn("fabricate provenance", blocker["reason"].lower())

    def test_page_is_linked_and_contains_evidence_boundary(self) -> None:
        parser = _Parser()
        page = PAGE.read_text()
        parser.feed(page)
        self.assertTrue({"math", "lab", "dividend", "tau", "evidence"} <= parser.ids)
        self.assertIn("https://github.com/IDNI/tau-lang", parser.hrefs)
        self.assertIn("https://github.com/IDNI/tau-testnet", parser.hrefs)
        lower = page.lower()
        self.assertIn("not the alignment theorem", lower)
        self.assertIn("not yet a deployed node", lower)
        self.assertIn("only tau can do this", lower)
        self.assertIn("reviewed binary replay", lower)
        self.assertIn("intelligence-hyperdeflation-flywheel.html", (ROOT / "docs" / "index.html").read_text())
        self.assertIn("intelligence-hyperdeflation-flywheel.html", (ROOT / "docs" / "alignment-theorem-deep-dive.html").read_text())


if __name__ == "__main__":
    unittest.main()
