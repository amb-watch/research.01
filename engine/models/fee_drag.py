"""D2 · Fees: how much investors in active funds pay each year above the cost of a cheap
alternative in the same asset class (like for like risk).

    annual gap_b = non-dedicated active fund assets_b × (active cost_b − alternative cost_b)

Version 1 assumes active funds do not beat the market before fees on average (zero alpha); version 2
will test this against benchmarks. Absolute return funds are excluded because they have no clear
alternative with the same risk.

Cost assumptions are in % a year, in three scenarios:
* conservative: the lowest plausible active cost and the highest alternative cost (smallest gap);
* base;
* aggressive.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

SCENARIOS = ("conservative", "base", "aggressive")


@dataclass(frozen=True)
class CostAssumption:
    bucket: str
    alternative: str
    active: tuple[float, float, float]  # % a year: conservative, base, aggressive
    alternative_cost: tuple[float, float, float]
    sources: str


ASSUMPTIONS: list[CostAssumption] = [
    CostAssumption("equity", "domestic equity index fund (no FX risk of foreign ETFs)",
                   active=(1.61, 2.13, 2.40), alternative_cost=(0.90, 0.70, 0.30),
                   sources="active: equity fund management fee end 2024 = 1.61% (analizy.pl, 2025-10); equity TER 2023 = 2.13% (analizy.pl, 2024-08); "
                           "Polish equity KID = 2.4% (analizy.pl, 2025-01). alternative: KID inPZU Akcje Polskie 0.7%, PKO Akcji Rynku Polskiego 0.88%, "
                           "inPZU Akcje Rynków Rozwiniętych 0.82% (analizy.pl, 2025-01); 0.30% approximates a low cost UCITS ETF (assumption)."),
    CostAssumption("mixed", "own 60/40 portfolio of equity and bond index funds",
                   active=(1.19, 1.72, 2.00), alternative_cost=(0.90, 0.70, 0.40),
                   sources="active: mixed fund management fee end 2024 = 1.19%; mixed fund ongoing charges = 1.72% (analizy.pl, 2025-10). "
                           "alternative: 60% × ~0.8% (equity index) + 40% × ~0.5% (bond index) ≈ 0.7% (assumption based on index fund KIDs)."),
    CostAssumption("bond", "Treasury bond index fund",
                   active=(0.99, 1.21, 1.53), alternative_cost=(0.63, 0.50, 0.30),
                   sources="active: bond fund management fee end 2024 = 0.99% (analizy.pl, 2025-10); bond TER 2023 = 1.21% (analizy.pl, 2024-08); "
                           "long bond KID = 1.53% (analizy.pl, 2025-01). alternative: KID inPZU Obligacje Polskie Skarbowe 0.63%, mBank Obligacji 0.5%; "
                           "Goldman Sachs Indeks Obligacji TER below 0.5% (analizy.pl)."),
    CostAssumption("short_bond", "lowest cost short term bond and Treasury funds",
                   active=(0.74, 0.88, 0.95), alternative_cost=(0.55, 0.48, 0.30),
                   sources="active: asset weighted average of the 12 largest funds (68.6% of category assets, Oct 2026) = 0.88%; funds with costs taken "
                           "directly from KID (32.6% of assets) = 0.74%; rest of the category at the simple KID average of 1.1% gives 0.95%. "
                           "Table: data/reference/short_term_fund_costs.csv. alternative: KID Erste Dłużny Krótkoterminowy 0.48% (Oct 2026); "
                           "PZU SEJF+ 0.54%; Generali Konserwatywny 0.5% (analizy.pl, 2025-01); 0.30% approximates a short bond ETF (assumption)."),
]


def assumptions_table() -> pd.DataFrame:
    rows = []
    for a in ASSUMPTIONS:
        for i, s in enumerate(SCENARIOS):
            rows.append({"bucket": a.bucket, "scenario": s, "active_cost_pct": a.active[i], "alternative_cost_pct": a.alternative_cost[i],
                         "difference_pp": round(a.active[i] - a.alternative_cost[i], 4)})
    return pd.DataFrame(rows)


def annual_fee_gap(active_aum: pd.Series) -> pd.DataFrame:
    """Annual cost gap (PLN) per category and scenario. active_aum: non-dedicated active fund assets per bucket."""
    t = assumptions_table()
    t["aum_pln"] = t["bucket"].map(active_aum).fillna(0.0)
    t["annual_gap_pln"] = t["aum_pln"] * t["difference_pp"] / 100
    return t


def compound_cost(amount: float, years: int, gross_return_pct: float, cost_high_pct: float, cost_low_pct: float) -> dict:
    """Single investor example: the same investment at two cost levels."""
    fv_high = amount * (1 + (gross_return_pct - cost_high_pct) / 100) ** years
    fv_low = amount * (1 + (gross_return_pct - cost_low_pct) / 100) ** years
    return {"fv_high_cost": fv_high, "fv_low_cost": fv_low, "difference": fv_low - fv_high, "difference_share": (fv_low - fv_high) / fv_low}
