from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "docs" / "data-center-social-contract.html"
PUBLIC_PLAYBOOK = ROOT / "docs" / "local-government-policy-playbook.html"
INDEX = ROOT / "docs" / "index.html"
PLAYBOOK = (
    ROOT
    / "research"
    / "data_center_social_contract"
    / "LOCAL_GOVERNMENT_POLICY_PLAYBOOK.md"
)
TAU_GATE = (
    ROOT
    / "tau"
    / "data_center_social_contract"
    / "data_center_admission_gate.tau"
)

OBLIGATIONS = (
    "policy_root_ok",
    "project_identity_authenticated",
    "local_consent_authenticated",
    "incremental_energy_costs_reserved",
    "reliability_curtailment_plan_ok",
    "water_emissions_land_limits_ok",
    "decommissioning_bond_funded",
    "no_harm_compensation_funded",
    "universal_dividend_compute_floor_funded",
    "public_audit_receipt_current",
)


class DataCenterPolicyPublicationTests(unittest.TestCase):
    def test_public_blog_is_complete_and_links_research(self) -> None:
        text = BLOG.read_text()
        self.assertIn("The Data Center Bargain", text)
        self.assertIn("Community bargain solvency calculator", text)
        self.assertIn("Why the full version requires Tau Language", text)
        self.assertIn("The exclusivity claim is architectural, not mystical", text)
        self.assertIn("LOCAL_GOVERNMENT_POLICY_PLAYBOOK.md", text)
        self.assertIn("United States Data Center Energy Usage Report: 2025 Update", text)
        self.assertIn("ferc-launches-aggressive-targeted-action", text)
        self.assertIn("github.com/IDNI/tau-lang", text)
        self.assertNotIn("file://", text)
        self.assertNotIn("/mnt/data", text)
        self.assertNotIn("localhost", text)

    def test_blog_contains_exact_alignment_theorem_boundaries(self) -> None:
        text = BLOG.read_text()
        for formula_fragment in (
            "R=(G-C)_+",
            "d_i=(L_i-B_i)_+",
            "h_i=\\max\\{m,d_i\\}",
            "G\\ge C+H(m)",
            "Q\\ge nc",
            "P_{t+1}",
        ):
            with self.subTest(fragment=formula_fragment):
                self.assertIn(formula_fragment, text)
        self.assertIn("Tau does not authenticate the facts", text)
        self.assertIn("Native replay remains pending", text)
        self.assertIn("not production authority", text)

    def test_playbook_has_local_instruments_and_model_resolution(self) -> None:
        text = PLAYBOOK.read_text()
        for phrase in (
            "conditional-use permit",
            "growth pays for growth",
            "performance bond",
            "community-benefit agreement",
            "universal resident benefit plus targeted no-harm top-ups",
            "Model local resolution",
            "Recommended adoption sequence",
            "Tau-ready local approval structure",
            "not jurisdiction-specific legal advice",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        numbered_policies = re.findall(r"^## (\d+)\.", text, flags=re.MULTILINE)
        self.assertEqual(numbered_policies, [str(index) for index in range(1, 15)])

    def test_static_playbook_is_publishable_and_linked_from_index(self) -> None:
        page = PUBLIC_PLAYBOOK.read_text()
        index = INDEX.read_text()
        self.assertIn("Local Data-Center Policy Playbook", page)
        self.assertIn("The fourteen-part local package", page)
        self.assertIn("Make growth pay for growth", page)
        self.assertIn("not jurisdiction-specific legal advice", page)
        self.assertIn('href="local-government-policy-playbook.html"', index)
        for forbidden in ("file://", "/tmp/", "/home/", "localhost"):
            self.assertNotIn(forbidden, page)

    def test_public_explanation_matches_the_actual_tau_gate(self) -> None:
        blog = BLOG.read_text()
        playbook = PLAYBOOK.read_text()
        gate = TAU_GATE.read_text()
        for obligation in OBLIGATIONS:
            with self.subTest(obligation=obligation):
                self.assertIn(obligation, blog)
                self.assertIn(obligation, playbook)
                self.assertIn(obligation, gate)
        self.assertEqual(gate.count("&"), len(OBLIGATIONS) - 1)


if __name__ == "__main__":
    unittest.main()
