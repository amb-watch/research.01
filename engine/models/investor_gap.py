"""D5 · Investor gap: the return of the funds (time weighted, TWR) versus the return of the money
invested in them (money weighted, IRR), per fund category, on IZFiA data.

Method (as in "Mind the Gap" studies on aggregate data):
* monthly category return, modified Dietz:
      r_t = (NAV_t − NAV*_{t−1} − F_t) / (NAV*_{t−1} + ½·F_t)
  where F_t is the net flow in the month (assumed mid month) and NAV*_{t−1} is the previous month
  end NAV of the funds assigned to the category **by their classification in month t**, so that a
  fund changing category does not register as a gain or a loss;
* reclassifications R_t = NAV*_{t−1} − NAV_{t−1} enter the IRR as start of month flows (money that
  reached the category without an investor decision);
* investor return: IRR of the flows −NAV_0, −R_t, −F_t, +NAV_T.

Gap = TWR − IRR (percentage points a year). Gap in PLN = how much more investors would hold if
every zloty invested had earned the funds' average annual return (TWR) from the day it was paid in.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import brentq


def bucket_panel(nav: pd.DataFrame, flows: pd.DataFrame, buckets: list[str]) -> pd.DataFrame:
    """Monthly panel per category: nav, nav_prev_aligned, nav_prev_raw, flow, reclass, r.

    nav   : NAV per (month, fund) with columns month, fund, bucket, dedicated, nav
    flows : net flows of non-dedicated funds with columns month, bucket, flow_net
    """
    nav = nav[~nav["dedicated"]].copy()
    months = sorted(set(flows["month"]))
    by_month = {m: g.set_index("fund") for m, g in nav.groupby("month")}
    all_months = sorted(by_month)
    flow = flows.groupby(["month", "bucket"])["flow_net"].sum()

    recs = []
    for m in months:
        i = all_months.index(m)
        if i == 0:
            continue
        cur, prev = by_month[m], by_month[all_months[i - 1]]
        # category used for alignment: the one in month t, or in t−1 if the fund no longer exists
        aligned_bucket = cur["bucket"].reindex(prev.index).fillna(prev["bucket"])
        prev_aligned = prev["nav"].groupby(aligned_bucket).sum()
        prev_raw = prev["nav"].groupby(prev["bucket"]).sum()
        cur_nav = cur["nav"].groupby(cur["bucket"]).sum()
        for b in buckets:
            recs.append({"month": m, "bucket": b, "nav": float(cur_nav.get(b, 0.0)), "nav_prev_aligned": float(prev_aligned.get(b, 0.0)),
                         "nav_prev_raw": float(prev_raw.get(b, 0.0)), "flow": float(flow.get((m, b), 0.0))})
    p = pd.DataFrame(recs)
    p["reclass"] = p["nav_prev_aligned"] - p["nav_prev_raw"]
    p["r"] = (p["nav"] - p["nav_prev_aligned"] - p["flow"]) / (p["nav_prev_aligned"] + 0.5 * p["flow"])
    return p


def _irr_monthly(times: np.ndarray, cfs: np.ndarray) -> float:
    """Monthly IRR of cash flows (convention: money paid into the fund < 0, final value > 0)."""
    T = times.max()
    return brentq(lambda i: float(np.sum(cfs * (1 + i) ** (T - times))), -0.5, 0.5, xtol=1e-12)


@dataclass
class GapResult:
    bucket: str
    start: str
    end: str
    months: int
    twr_ann: float
    irr_ann: float
    gap_pp: float
    gap_pln: float
    avg_nav: float
    net_flows: float
    nav_start: float
    nav_end: float


def investor_gap(panel: pd.DataFrame, bucket: str | None = None, start: str | None = None, end: str | None = None) -> GapResult:
    """Investor gap for one category, or for all categories combined when bucket is None."""
    p = panel if bucket is None else panel[panel["bucket"] == bucket]
    if start:
        p = p[p["month"] >= start]
    if end:
        p = p[p["month"] <= end]
    g = p.groupby("month")[["nav", "nav_prev_aligned", "nav_prev_raw", "flow", "reclass"]].sum().sort_index()
    if bucket is None:
        g["r"] = (g["nav"] - g["nav_prev_aligned"] - g["flow"]) / (g["nav_prev_aligned"] + 0.5 * g["flow"])
    else:
        g["r"] = p.set_index("month")["r"].sort_index()

    n = len(g)
    twr_m = float(np.prod(1 + g["r"].values) ** (1 / n) - 1)
    nav0 = g["nav_prev_raw"].iloc[0]
    t = np.arange(n)
    times = np.concatenate([[0.0], t.astype(float), t + 0.5, [float(n)]])
    cfs = np.concatenate([[-nav0], -g["reclass"].values, -g["flow"].values, [g["nav"].iloc[-1]]])
    irr_m = _irr_monthly(times, cfs)
    fv_twr = float(np.sum(-cfs[:-1] * (1 + twr_m) ** (n - times[:-1])))
    return GapResult(bucket=bucket or "total", start=g.index[0], end=g.index[-1], months=n,
                     twr_ann=(1 + twr_m) ** 12 - 1, irr_ann=(1 + irr_m) ** 12 - 1,
                     gap_pp=((1 + twr_m) ** 12 - (1 + irr_m) ** 12) * 100, gap_pln=fv_twr - float(g["nav"].iloc[-1]),
                     avg_nav=float(g["nav"].mean()), net_flows=float(g["flow"].sum()), nav_start=float(nav0), nav_end=float(g["nav"].iloc[-1]))
