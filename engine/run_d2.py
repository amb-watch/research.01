"""D2 · Fees in investment funds.   python -m engine.run_d2"""

from __future__ import annotations

import openpyxl
import pandas as pd

from . import ui
from .data import izfia_parse
from .data.izfia_parse import PROCESSED, RAW_ASSETS
from .models.fee_drag import annual_fee_gap, compound_cost


def latest_aum_split() -> tuple[str, pd.DataFrame]:
    """Non-dedicated assets per category, split into active and passive (IZFiA Passive flag, available from 2026)."""
    path = sorted(p for p in RAW_ASSETS.glob("20*") if p.suffix in (".xlsx", ".xlsm"))[-1]
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["RawData"]
    it = ws.iter_rows(values_only=True)
    header = next(it)
    df = pd.DataFrame(list(it), columns=header)
    df["month"] = df["Date"].astype(str).str[:7]
    month = df["month"].max()
    df = df[(df["month"] == month) & (df["Dedicated"] == "Nie")].copy()
    df["bucket"] = df["Profile"].map(izfia_parse.bucket_of)
    df["passive"] = df["Passive"].eq("Tak")
    split = df.groupby(["bucket", "passive"])["NAV"].sum().unstack(fill_value=0.0)
    split.columns = ["passive" if c else "active" for c in split.columns]
    split["passive_share_pct"] = 100 * split["passive"] / split[["active", "passive"]].sum(axis=1)
    return month, split


def main() -> dict:
    month, split = latest_aum_split()
    gaps = annual_fee_gap(split["active"])
    PROCESSED.mkdir(parents=True, exist_ok=True)
    gaps.to_csv(PROCESSED / "d2_fees.csv", index=False)
    summary = gaps.pivot_table(index="bucket", columns="scenario", values="annual_gap_pln", aggfunc="sum")[["conservative", "base", "aggressive"]]
    return {"month": month, "split": split, "summary": summary, "example": compound_cost(100_000, 30, 7.0, 2.13, 0.70)}


if __name__ == "__main__":
    r = main()
    ui.banner("D2 · Fees in investment funds", f"IZFiA, non-dedicated funds, {r['month']}")
    s = r["split"]
    ui.table(["category", "active bn", "passive bn", "passive %"], [[b, ui.f(s.loc[b, "active"] / 1e9), ui.f(s.loc[b, "passive"] / 1e9), ui.f(s.loc[b, "passive_share_pct"])] for b in s.index])
    m = r["summary"] / 1e9
    ui.table(["category", "conservative", "base", "aggressive"], [[b, *[ui.f(m.loc[b, k], 2) for k in m.columns]] for b in m.index], title="Annual cost gap, PLN bn")
    for k in m.columns:
        ui.stat(f"PLN {ui.f(m[k].sum(), 2)} bn", f"a year, {k} scenario")
    e = r["example"]
    ui.note(f"PLN 100,000 over 30 years at 7%: cost 2.13% gives {e['fv_high_cost']:,.0f}, cost 0.70% gives {e['fv_low_cost']:,.0f} (difference {e['difference']:,.0f}).")
