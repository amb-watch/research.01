"""D4 · PPK opt outs.   python -m engine.run_d4"""

from __future__ import annotations

from . import ui
from .data.izfia_parse import PROCESSED
from .models.ppk import Inputs, annual_loss

if __name__ == "__main__":
    t = annual_loss(Inputs())
    PROCESSED.mkdir(parents=True, exist_ok=True)
    t.to_csv(PROCESSED / "d4_ppk.csv", index=False)
    ui.banner("D4 · PPK opt outs")
    ui.table(["scenario", "gross pay", "employer net", "loss per person", "opted out mn", "PLN bn"],
             [[r.scenario, f"{r.gross_pay:,.0f}", f"{r.employer_net_year:,.0f}", f"{r.loss_per_person_year:,.0f}", ui.f(r.opted_out_mn), ui.f(r.annual_loss_pln / 1e9, 2)]
              for r in t.itertuples()], highlight=1)
