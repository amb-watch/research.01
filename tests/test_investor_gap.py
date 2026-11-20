import numpy as np
import pandas as pd
import pytest

from engine.data.izfia_parse import bucket_of
from engine.models.investor_gap import bucket_panel, investor_gap


def _simulate(returns, flows, bucket="equity", nav0=100.0):
    """One fund, flows in the middle of the month (consistent with the Dietz assumption)."""
    nav_rows, flow_rows = [], []
    months = pd.period_range("2020-01", periods=len(returns) + 1, freq="M").astype(str)
    v = nav0
    nav_rows.append({"month": months[0], "fund": "F1", "bucket": bucket, "dedicated": False, "nav": v})
    for m, r, f in zip(months[1:], returns, flows):
        v = v * (1 + r) + f * (1 + 0.5 * r)
        nav_rows.append({"month": m, "fund": "F1", "bucket": bucket, "dedicated": False, "nav": v})
        flow_rows.append({"month": m, "bucket": bucket, "flow_net": f})
    return pd.DataFrame(nav_rows), pd.DataFrame(flow_rows)


def test_dietz_recovers_returns():
    rets = [0.02, -0.05, 0.03, 0.01]
    nav, flows = _simulate(rets, [10, -5, 20, 0])
    assert np.allclose(bucket_panel(nav, flows, ["equity"])["r"].values, rets)


def test_no_flows_means_no_gap():
    rets = np.random.default_rng(0).normal(0.005, 0.04, 60)
    nav, flows = _simulate(rets, np.zeros(60))
    res = investor_gap(bucket_panel(nav, flows, ["equity"]), "equity")
    assert res.gap_pp == pytest.approx(0, abs=1e-6)
    assert res.gap_pln == pytest.approx(0, abs=1e-6)


def test_buying_high_selling_low_gives_positive_gap():
    # a rally followed by a sell off: investors buy near the top and sell near the bottom
    rets = [0.05] * 12 + [-0.04] * 12 + [0.03] * 12
    flows = [0] * 8 + [30] * 4 + [0] * 8 + [-20] * 4 + [0] * 12
    nav, fl = _simulate(rets, flows)
    res = investor_gap(bucket_panel(nav, fl, ["equity"]), "equity")
    assert res.gap_pp > 1
    assert res.gap_pln > 0


def test_reclassification_is_not_a_return():
    # fund F2 moves from "bond" to "equity" in February with no change in value
    nav = pd.DataFrame([
        {"month": "2020-01", "fund": "F1", "bucket": "equity", "dedicated": False, "nav": 100.0},
        {"month": "2020-01", "fund": "F2", "bucket": "bond", "dedicated": False, "nav": 50.0},
        {"month": "2020-02", "fund": "F1", "bucket": "equity", "dedicated": False, "nav": 101.0},
        {"month": "2020-02", "fund": "F2", "bucket": "equity", "dedicated": False, "nav": 50.5},
    ])
    flows = pd.DataFrame([{"month": "2020-02", "bucket": "equity", "flow_net": 0.0}])
    p = bucket_panel(nav, flows, ["equity", "bond"]).set_index("bucket")
    assert p.loc["equity", "r"] == pytest.approx(0.01)
    assert p.loc["equity", "reclass"] == pytest.approx(50.0)


def test_liquidated_fund_outflow_is_not_a_loss():
    # F2 is liquidated: its value is paid out as a redemption (negative flow)
    nav = pd.DataFrame([
        {"month": "2020-01", "fund": "F1", "bucket": "equity", "dedicated": False, "nav": 100.0},
        {"month": "2020-01", "fund": "F2", "bucket": "equity", "dedicated": False, "nav": 20.0},
        {"month": "2020-02", "fund": "F1", "bucket": "equity", "dedicated": False, "nav": 100.0},
    ])
    flows = pd.DataFrame([{"month": "2020-02", "bucket": "equity", "flow_net": -20.0}])
    assert bucket_panel(nav, flows, ["equity"])["r"].iloc[0] == pytest.approx(0.0)


@pytest.mark.parametrize("profile,bucket", [
    ("Equity (Universal i Index)", "equity"), ("Equity_Small&medium_cap", "equity"), ("Mixed Stable Growth", "mixed"),
    ("Mixed Other", "excluded"), ("Target Date PPK", "excluded"), ("Target_Date_Other_2040", "excluded"),
    ("Money_Market_PLN", "short_bond"), ("BOND_Short_Term_Universal_PLN", "short_bond"), ("Bond no base currency", "bond"),
    ("Absolute Return", "absolute_return"), ("Other (Private Equity, Securitized, Real Estate)", "excluded"), ("Commodity", "excluded"),
])
def test_bucket_mapping(profile, bucket):
    assert bucket_of(profile) == bucket
