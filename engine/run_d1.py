"""D1 · Deposits versus COI Treasury bonds.   python -m engine.run_d1"""

from __future__ import annotations

from . import ui
from .data.izfia_parse import PROCESSED
from .models.deposits import Inputs, annual_gap


def main():
    t = annual_gap(Inputs())
    PROCESSED.mkdir(parents=True, exist_ok=True)
    t.to_csv(PROCESSED / "d1_deposits.csv", index=False)
    return t


if __name__ == "__main__":
    t = main()
    ui.banner("D1 · Deposits versus COI Treasury bonds")
    ui.table(["scenario", "type", "COI %", "deposit %", "gap pp", "share", "movable bn", "gap bn"],
             [[r.scenario, r.deposit_type, ui.f(r.coi_rate_pct, 2), ui.f(r.deposit_rate_pct, 2), ui.f(r.gap_after_tax_pp, 2), f"{r.movable_share:.0%}",
               ui.f(r.movable_pln / 1e9, 0), ui.f(r.annual_gap_pln / 1e9, 2)] for r in t.itertuples()], highlight=2)
    for s, v in (t.groupby("scenario").annual_gap_pln.sum() / 1e9).reindex(["conservative", "base", "aggressive"]).items():
        ui.stat(f"PLN {ui.f(v)} bn", f"a year, {s} scenario")
