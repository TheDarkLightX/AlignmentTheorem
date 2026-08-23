from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "compute_dividend"


class ComputeDividendResearchPacketTests(unittest.TestCase):
    def test_ledgers_have_closed_source_and_evidence_links(self) -> None:
        sources = json.loads((RESEARCH / "source_ledger.json").read_text())
        hypotheses = json.loads((RESEARCH / "hypothesis_ledger.json").read_text())
        experiments = json.loads((RESEARCH / "experiment_ledger.json").read_text())
        source_ids = {row["id"] for row in sources["sources"]}
        evidence_ids = {row["id"] for row in experiments["experiments"]}

        self.assertEqual(len(source_ids), len(sources["sources"]))
        self.assertEqual(len(evidence_ids), len(experiments["experiments"]))
        for hypothesis in hypotheses["hypotheses"]:
            with self.subTest(hypothesis=hypothesis["id"]):
                self.assertTrue(set(hypothesis["source_ids"]) <= source_ids)
                self.assertTrue(set(hypothesis["evidence_ids"]) <= evidence_ids)
                self.assertTrue(hypothesis["assumptions"])
                self.assertTrue(hypothesis["falsifiers"])

    def test_experiment_artifacts_exist_and_are_regular_files(self) -> None:
        experiments = json.loads((RESEARCH / "experiment_ledger.json").read_text())
        for experiment in experiments["experiments"]:
            with self.subTest(experiment=experiment["id"]):
                artifact = ROOT / experiment["artifact"]
                self.assertTrue(artifact.is_file())
                self.assertFalse(artifact.is_symlink())

    def test_research_kernel_unavailability_is_not_labeled_as_receipt(self) -> None:
        status = json.loads((RESEARCH / "research_kernel_status.json").read_text())

        self.assertFalse(status["promotion_invoked"])
        self.assertFalse(status["mcp_run_started"])
        self.assertIn("NOT_MCP_RECEIPT", status["status"])
        self.assertEqual(status["esso_adapter"], "UNAVAILABLE_IN_SESSION")

    def test_tau_boundary_keeps_exact_binary_pending_and_provenance_separate(self) -> None:
        replay = (RESEARCH / "TAU_REPLAY.md").read_text()
        boundary = (RESEARCH / "CLAIM_BOUNDARY.md").read_text()

        self.assertIn(
            "c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa",
            replay,
        )
        self.assertIn("remains absent and pending", replay)
        self.assertIn("produced the reviewed Linux", boundary)
        self.assertIn("not claimed", boundary.lower())

    def test_graph_edges_resolve(self) -> None:
        graph = json.loads((RESEARCH / "graph_ledger.json").read_text())
        node_ids = {node["id"] for node in graph["nodes"]}
        self.assertEqual(len(node_ids), len(graph["nodes"]))
        for edge in graph["edges"]:
            self.assertIn(edge["from"], node_ids)
            self.assertIn(edge["to"], node_ids)


if __name__ == "__main__":
    unittest.main()
