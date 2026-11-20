"""D3 · Unused IKE and IKZE tax shields.

The model starts from the Belka tax (19%) actually paid and asks what share of it could be avoided
legally by holding *the same* savings and investments inside IKE or IKZE accounts (the same
instruments: deposits and Treasury bonds in a bank or bond IKE, funds and shares in a fund or
brokerage IKE).

    gap = Belka on savings × avoidable share_savings + Belka on investments × avoidable share_investments

Why this does not double count D1: the reference point is the Belka tax paid today (on deposit
interest). If the money moved into COI bonds (D1), tax on the higher interest would be larger, so
starting from today understates D3; the estimate is conservative and separate from D1.

The avoidable share reflects that (1) short term and liquidity money does not belong in IKE,
(2) annual limits (IKE PLN 28,260 and IKZE PLN 11,304 in 2026) bind for larger portfolios, and
(3) gains already inside IKE and IKZE are not in the tax receipts at all.
A key feature of IKE: early withdrawal simply means paying the Belka tax, as on an ordinary account,
so for long term money IKE has practically no tax downside.

Omitted (which understates the result): the IKZE PIT deduction (12% or 32%, less a 10% flat tax at withdrawal).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

SCENARIOS = ("conservative", "base", "aggressive")


@dataclass(frozen=True)
class Inputs:
    # Belka tax receipts, PLN: Ministry of Finance 2026 forecast (as reported); 2025 outturn: 5.7 + 3.6 bn
    belka_savings: float = 5.1e9
    belka_investments: float = 3.9e9
    share_savings: tuple[float, float, float] = (0.15, 0.25, 0.40)
    share_investments: tuple[float, float, float] = (0.25, 0.40, 0.60)


def annual_gap(inp: Inputs = Inputs()) -> pd.DataFrame:
    rows = []
    for i, s in enumerate(SCENARIOS):
        sav, inv = inp.belka_savings * inp.share_savings[i], inp.belka_investments * inp.share_investments[i]
        rows.append({"scenario": s, "share_savings": inp.share_savings[i], "share_investments": inp.share_investments[i],
                     "gap_savings_pln": sav, "gap_investments_pln": inv, "annual_gap_pln": sav + inv})
    return pd.DataFrame(rows)
