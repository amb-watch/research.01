"""D4 · PPK (Employee Capital Plans): what eligible employees who opted out lose each year.

The loss counts only money received for free: the employer's basic contribution (1.5% of gross pay)
and the annual state subsidy (PLN 240). The employee's own 2% contribution is NOT a loss: it stays
in the employee's pocket.

    loss per person = 1.5% × pay × 12 × (1 − PIT) × employer share kept + 240 × state share kept
    annual loss     = employees outside PPK × loss per person

* PIT: the employer contribution is taxable income of the employee (12% in the first bracket);
* "kept": on withdrawal before age 60, 30% of employer contributions goes to ZUS and state
  subsidies are forfeited; the scenarios assume different shares of early withdrawers;
* omitted (all of which would raise the result): the one off PLN 250 welcome payment, voluntary
  extra employer contributions (up to 2.5%), investment returns and PPK fund fees (about 0.5%).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

SCENARIOS = ("conservative", "base", "aggressive")


@dataclass(frozen=True)
class Inputs:
    employer_rate: float = 0.015
    state_subsidy: float = 240.0
    pit: float = 0.12
    # eligible employees outside PPK (million): PFR, about 38% of eligible, "close to 2.8 million" (H1 2026);
    # participation of 63.9% (28 Oct 2026) is measured on active accounts, not people
    opted_out_mn: tuple[float, float, float] = (2.5, 2.8, 3.2)
    # gross monthly pay: median below mean; enterprise sector average Sept 2026 = PLN 9,266
    gross_pay: tuple[float, float, float] = (6_000.0, 7_400.0, 9_266.0)
    employer_share_kept: tuple[float, float, float] = (0.70, 0.85, 1.00)
    state_share_kept: tuple[float, float, float] = (0.0, 0.5, 1.0)


def annual_loss(inp: Inputs = Inputs()) -> pd.DataFrame:
    rows = []
    for i, s in enumerate(SCENARIOS):
        employer_net = inp.employer_rate * inp.gross_pay[i] * 12 * (1 - inp.pit)
        per_person = employer_net * inp.employer_share_kept[i] + inp.state_subsidy * inp.state_share_kept[i]
        rows.append({"scenario": s, "gross_pay": inp.gross_pay[i], "employer_net_year": round(employer_net, 0),
                     "loss_per_person_year": round(per_person, 0), "opted_out_mn": inp.opted_out_mn[i], "annual_loss_pln": per_person * inp.opted_out_mn[i] * 1e6})
    return pd.DataFrame(rows)
