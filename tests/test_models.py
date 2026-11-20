import pandas as pd
import pytest

from engine.models import deposits, fee_drag, ppk, tax_wrappers


# ---------------------------------------------------------------- D1 deposits
def test_coi_avg_rate():
    assert deposits.coi_avg_rate(4.75, 1.5, 3.0) == pytest.approx((4.75 + 3 * 4.5) / 4)


def test_deposit_scenarios_ordered():
    t = deposits.annual_gap().groupby("scenario")["annual_gap_pln"].sum()
    assert 0 < t["conservative"] < t["base"] < t["aggressive"]


def test_no_gap_when_deposit_pays_like_coi():
    inp = deposits.Inputs(rate_current=4.0, rate_term=4.0, coi_first_year=4.0, coi_margin=1.0, inflation=(3.0,) * 3, share_redeemed=(0.0,) * 3)
    assert deposits.annual_gap(inp)["annual_gap_pln"].abs().max() == pytest.approx(0)


def test_belka_applied_on_both_sides():
    row = deposits.annual_gap(deposits.Inputs(share_redeemed=(0.0,) * 3)).query("scenario=='base' and deposit_type=='term'").iloc[0]
    assert row.gap_after_tax_pp == pytest.approx((row.coi_rate_pct - row.deposit_rate_pct) * 0.81, abs=1e-3)


# ---------------------------------------------------------------- D2 fees
def test_fee_scenarios_ordered():
    for a in fee_drag.ASSUMPTIONS:
        gaps = [a.active[i] - a.alternative_cost[i] for i in range(3)]
        assert 0 < gaps[0] <= gaps[1] <= gaps[2], a.bucket


def test_fee_gap_scales_with_assets():
    t = fee_drag.annual_fee_gap(pd.Series({"equity": 100e9}))
    row = t[(t.bucket == "equity") & (t.scenario == "base")].iloc[0]
    assert row.annual_gap_pln == pytest.approx(100e9 * row.difference_pp / 100)
    assert t[t.bucket == "mixed"].annual_gap_pln.sum() == 0


def test_compound_cost_example():
    r = fee_drag.compound_cost(100_000, 30, 7.0, 2.0, 0.6)
    assert r["fv_high_cost"] == pytest.approx(100_000 * 1.05 ** 30)
    assert 0.3 < r["difference_share"] < 0.4


# ---------------------------------------------------------------- D3 tax wrappers
def test_tax_gap_is_share_of_belka():
    inp = tax_wrappers.Inputs(belka_savings=10e9, belka_investments=0.0, share_savings=(0.1, 0.2, 0.3))
    assert tax_wrappers.annual_gap(inp).set_index("scenario").loc["base", "annual_gap_pln"] == pytest.approx(2e9)


def test_tax_gap_below_total_belka():
    inp = tax_wrappers.Inputs()
    assert tax_wrappers.annual_gap(inp)["annual_gap_pln"].max() < inp.belka_savings + inp.belka_investments


# ---------------------------------------------------------------- D4 PPK
def test_ppk_per_person_formula():
    inp = ppk.Inputs(gross_pay=(10_000.0,) * 3, employer_share_kept=(1.0,) * 3, state_share_kept=(1.0,) * 3)
    assert ppk.annual_loss(inp).iloc[0].loss_per_person_year == pytest.approx(0.015 * 10_000 * 12 * 0.88 + 240, abs=1)


def test_ppk_scenarios_ordered():
    t = ppk.annual_loss().set_index("scenario")["annual_loss_pln"]
    assert t["conservative"] < t["base"] < t["aggressive"]


def test_own_contribution_not_counted():
    assert "employee_rate" not in ppk.Inputs.__dataclass_fields__
