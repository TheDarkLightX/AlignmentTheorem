import unittest
from fractions import Fraction

from verification.data_center_social_contract import (
    DATA_CENTER_OBLIGATION_NAMES,
    DataCenterObligations,
    HouseholdImpact,
    PriceFactors,
    data_center_admits,
    minimal_hybrid_requirement_atoms,
    minimal_hybrid_transfers,
    minimal_uniform_requirement_atoms,
    project_cash_contract_feasible,
    tau_truth_rows,
    transfers_satisfy_floor_and_no_harm,
    universal_base_plus_topups_identity_atoms,
)


class DataCenterSocialContractTests(unittest.TestCase):
    @staticmethod
    def impacts() -> tuple[HouseholdImpact, ...]:
        return (
            HouseholdImpact("a", 10, 0, 0),
            HouseholdImpact("b", 10, 7, 2),
            HouseholdImpact("c", 10, 3, 1),
        )

    def test_hybrid_is_pointwise_minimal_and_funded_at_exact_threshold(self) -> None:
        rows = self.impacts()
        transfers = minimal_hybrid_transfers(rows, universal_floor_atoms=2)
        self.assertEqual(transfers, (2, 5, 2))
        self.assertTrue(
            transfers_satisfy_floor_and_no_harm(
                rows, transfers, universal_floor_atoms=2
            )
        )
        self.assertEqual(
            minimal_hybrid_requirement_atoms(rows, universal_floor_atoms=2), 9
        )
        self.assertFalse(
            project_cash_contract_feasible(
                rows, distributable_cash_atoms=8, universal_floor_atoms=2
            )
        )
        self.assertTrue(
            project_cash_contract_feasible(
                rows, distributable_cash_atoms=9, universal_floor_atoms=2
            )
        )

    def test_hybrid_is_cheaper_than_uniform_when_deficits_are_heterogeneous(self) -> None:
        rows = self.impacts()
        self.assertEqual(
            minimal_hybrid_requirement_atoms(rows, universal_floor_atoms=2), 9
        )
        self.assertEqual(
            minimal_uniform_requirement_atoms(rows, universal_floor_atoms=2), 15
        )

    def test_universal_base_plus_targeted_topup_identity(self) -> None:
        left, right = universal_base_plus_topups_identity_atoms(
            self.impacts(), universal_floor_atoms=2
        )
        self.assertEqual((left, right), (9, 9))

    def test_floor_alone_can_be_funded_but_fail_no_harm(self) -> None:
        rows = (HouseholdImpact("a", 10, 2, 0),)
        self.assertFalse(
            transfers_satisfy_floor_and_no_harm(
                rows, (1,), universal_floor_atoms=1
            )
        )

    def test_tau_gate_is_complete_conjunction(self) -> None:
        rows = tau_truth_rows()
        self.assertEqual(len(rows), 1024)
        accepted = []
        for index, row in enumerate(rows):
            obligations = DataCenterObligations(
                **dict(zip(DATA_CENTER_OBLIGATION_NAMES, row))
            )
            if data_center_admits(obligations):
                accepted.append(index)
        self.assertEqual(accepted, [0])

    def test_intelligence_improvement_is_not_by_itself_a_price_theorem(self) -> None:
        no_diffusion = PriceFactors(Fraction(1), Fraction(1), Fraction(1))
        offset = PriceFactors(Fraction(2), Fraction(4, 3), Fraction(3, 2))
        clean = PriceFactors(Fraction(2), Fraction(1), Fraction(1))
        self.assertFalse(no_diffusion.is_deflationary)
        self.assertFalse(offset.is_deflationary)
        self.assertTrue(clean.is_deflationary)
        self.assertEqual(clean.price_ratio, Fraction(1, 2))

    def test_invalid_types_fail_closed(self) -> None:
        with self.assertRaises(TypeError):
            HouseholdImpact("a", 1, 1, True)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
