"""D5 · Investor gap.   python -m engine.run_d5 [--fresh]"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from . import ui
from .data import izfia, izfia_parse
from .data.izfia_parse import BUCKETS, PROCESSED
from .models.investor_gap import bucket_panel, investor_gap


def main(fresh: bool = False) -> pd.DataFrame:
    if fresh:
        izfia.download_all()
    flows, nav = izfia_parse.build(force=fresh)
    panel = bucket_panel(nav, flows, BUCKETS)
    panel.to_csv(PROCESSED / "d5_panel.csv", index=False)
    months = sorted(panel["month"].unique())
    rows = []
    for b in BUCKETS + [None]:
        r = investor_gap(panel, b)
        roll = [investor_gap(panel, b, months[i], months[i + 59]).gap_pp for i in range(len(months) - 59)]
        rows.append({"category": r.bucket, "period": f"{r.start} to {r.end}", "twr_pct": round(r.twr_ann * 100, 2), "irr_pct": round(r.irr_ann * 100, 2),
                     "gap_pp": round(r.gap_pp, 2), "gap_5y_min_pp": round(min(roll), 2), "gap_5y_median_pp": round(float(np.median(roll)), 2),
                     "gap_5y_max_pp": round(max(roll), 2), "gap_pln_bn": round(r.gap_pln / 1e9, 2), "avg_aum_pln_bn": round(r.avg_nav / 1e9, 1),
                     "net_flows_pln_bn": round(r.net_flows / 1e9, 1)})
    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED / "d5_investor_gap.csv", index=False)
    return out


if __name__ == "__main__":
    out = main(fresh="--fresh" in sys.argv)
    ui.banner("D5 · Investor gap", "IZFiA, non-dedicated funds, monthly flows September 2018 to October 2026")
    ui.table(["category", "TWR %", "IRR %", "gap pp", "5y median", "5y range", "gap PLN bn"],
             [[r.category, ui.f(r.twr_pct, 2), ui.f(r.irr_pct, 2), ui.f(r.gap_pp, 2), ui.f(r.gap_5y_median_pp, 2), f"{ui.f(r.gap_5y_min_pp, 2)} to {ui.f(r.gap_5y_max_pp, 2)}", ui.f(r.gap_pln_bn, 2)]
              for r in out.itertuples()])
