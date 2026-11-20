"""D3 · Unused IKE and IKZE tax shields.   python -m engine.run_d3"""

from __future__ import annotations

from . import ui
from .data.izfia_parse import PROCESSED
from .models.tax_wrappers import Inputs, annual_gap

if __name__ == "__main__":
    t = annual_gap(Inputs())
    PROCESSED.mkdir(parents=True, exist_ok=True)
    t.to_csv(PROCESSED / "d3_tax_wrappers.csv", index=False)
    ui.banner("D3 · Unused IKE and IKZE tax shields")
    ui.table(["scenario", "savings share", "investment share", "savings bn", "investments bn", "total bn"],
             [[r.scenario, f"{r.share_savings:.0%}", f"{r.share_investments:.0%}", ui.f(r.gap_savings_pln / 1e9, 2), ui.f(r.gap_investments_pln / 1e9, 2), ui.f(r.annual_gap_pln / 1e9, 2)]
              for r in t.itertuples()], highlight=1)
