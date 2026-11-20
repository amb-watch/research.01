"""D1 · Deposits versus inflation indexed retail Treasury bonds (COI), at like for like risk.

Version 1 is a valuation as of today, over the next four years:

    annual gap = Σ_type  deposits_type × movable share_type × (r_COI − r_deposit) × (1 − Belka tax)
                 − cost of early redemptions

* r_COI: average annual coupon of the four year COI bond in the current offer,
  (first year rate + 3 × (inflation + margin)) / 4, interest paid annually without compounding;
* r_deposit: average rate on the outstanding stock of household deposits (NBP MIR statistics), held
  constant (a simplification: in a low inflation scenario deposit rates would also fall);
* the 19% Belka tax applies on both sides, so the after tax gap is 0.81 × the gross gap;
* early redemption costs PLN 2 per PLN 100 bond (since 2024-09), spread over four years, for an
  assumed share of investors.

The movable share is the most sensitive assumption in the report: most current account balances
are transactional money and liquidity buffers that will not move into four year bonds.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

SCENARIOS = ("conservative", "base", "aggressive")
BELKA = 0.19


@dataclass(frozen=True)
class Inputs:
    # household deposits, PLN (NBP, June 2026, as reported by Parkiet)
    current_accounts: float = 1_112.9e9
    term_deposits: float = 400.3e9
    # rates on the outstanding stock, % (NBP MIR, September 2026)
    rate_current: float = 0.49
    rate_term: float = 2.79
    # COI offer (obligacjeskarbowe.pl, November 2026)
    coi_first_year: float = 4.75
    coi_margin: float = 1.50
    coi_redemption_fee_pct: float = 2.0  # PLN 2 per PLN 100
    # scenarios: conservative, base, aggressive
    inflation: tuple[float, float, float] = (2.0, 3.0, 4.0)  # average CPI in years 2 to 4; Oct 2026: 3.5% y/y
    share_current: tuple[float, float, float] = (0.05, 0.15, 0.25)
    share_term: tuple[float, float, float] = (0.50, 0.70, 0.90)
    share_redeemed: tuple[float, float, float] = (0.30, 0.15, 0.0)


def coi_avg_rate(first_year: float, margin: float, inflation: float) -> float:
    """Average annual coupon of a four year COI bond (% before tax)."""
    return (first_year + 3 * (inflation + margin)) / 4


def annual_gap(inp: Inputs = Inputs()) -> pd.DataFrame:
    rows = []
    for i, s in enumerate(SCENARIOS):
        r_coi = coi_avg_rate(inp.coi_first_year, inp.coi_margin, inp.inflation[i])
        redemption_cost = inp.share_redeemed[i] * inp.coi_redemption_fee_pct / 4  # pp a year
        for kind, stock, r_dep, share in [("current", inp.current_accounts, inp.rate_current, inp.share_current[i]),
                                          ("term", inp.term_deposits, inp.rate_term, inp.share_term[i])]:
            gap_pp = (r_coi - r_dep) * (1 - BELKA) - redemption_cost
            amount = stock * share
            rows.append({"scenario": s, "deposit_type": kind, "coi_rate_pct": round(r_coi, 3), "deposit_rate_pct": r_dep,
                         "gap_after_tax_pp": round(gap_pp, 3), "movable_share": share, "movable_pln": amount, "annual_gap_pln": amount * gap_pp / 100})
    return pd.DataFrame(rows)
