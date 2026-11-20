"""amb research · Report 01: one command from source data to results, charts and report data.

    python -m engine.report            # terminal output, 16 charts and report/data.json
    python -m engine.report --quiet    # without terminal output
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

from . import charts as ch
from . import ui
from .data.izfia_parse import BUCKETS, PROCESSED, build as build_izfia
from .data.public import GUS_CPI, NBP_MIR
from .models import deposits, fee_drag, ppk, tax_wrappers
from .models.investor_gap import investor_gap
from .run_d2 import latest_aum_split
from .run_d5 import main as run_d5

ROOT = Path(__file__).resolve().parents[1]
S = ["conservative", "base", "aggressive"]
NAMES = {"equity": "Equity", "mixed": "Mixed", "bond": "Bond", "short_bond": "Short term bond", "absolute_return": "Absolute return", "total": "Total"}
LEVERS = {"D1": "Deposits instead of Treasury bonds", "D2": "Fees in investment funds", "D3": "Unused IKE and IKZE", "D4": "PPK opt outs", "D5": "Poor timing"}
n = ch.num


# ------------------------------------------------------------------ inputs
def nbp_history() -> pd.DataFrame:
    """Household deposit rates on the outstanding stock (NBP MIR) joined with CPI y/y (GUS)."""
    R = list(openpyxl.load_workbook(NBP_MIR, read_only=True, data_only=True)["1 OPS_PLN"].iter_rows(values_only=True))
    dates = [d for d in R[1][6:] if hasattr(d, "year")]
    df = pd.DataFrame({"month": [d.strftime("%Y-%m") for d in dates], "current": R[2][6:6 + len(dates)], "term": R[5][6:6 + len(dates)]}).dropna()
    df[["current", "term"]] = df[["current", "term"]].astype(float) * 100
    cpi = pd.read_csv(GUS_CPI, sep=";", encoding="cp1250", decimal=",")
    cpi = cpi[cpi.iloc[:, 2].astype(str).str.contains("Analogiczny miesiąc", na=False)].dropna(subset=[cpi.columns[5]])
    cpi["month"] = cpi.iloc[:, 3].astype(int).astype(str) + "-" + cpi.iloc[:, 4].astype(int).map("{:02d}".format)
    cpi["cpi"] = cpi.iloc[:, 5].astype(float) - 100
    return df.merge(cpi[["month", "cpi"]], on="month", how="left")


def collect() -> dict:
    D: dict = {}
    # D1
    inp = deposits.Inputs()
    d1 = deposits.annual_gap(inp)
    D["d1_table"] = d1.assign(movable_bn=d1.movable_pln / 1e9, gap_bn=d1.annual_gap_pln / 1e9).drop(columns=["movable_pln", "annual_gap_pln"]).round(3).to_dict("records")
    d1s = d1.groupby("scenario").annual_gap_pln.sum().reindex(S) / 1e9
    base_of = lambda i: deposits.annual_gap(i).query("scenario=='base'").annual_gap_pln.sum() / 1e9  # noqa: E731
    torn = []
    for field, label in [("share_current", "Share of current accounts (5% to 25%)"), ("inflation", "Inflation in years 2 to 4 (2% to 4%)"),
                         ("share_term", "Share of term deposits (50% to 90%)"), ("share_redeemed", "Early redemptions (30% to 0%)")]:
        v = getattr(inp, field)
        a, b = base_of(replace(inp, **{field: (v[0],) * 3})), base_of(replace(inp, **{field: (v[2],) * 3}))
        torn.append({"label": label, "lo": round(min(a, b), 2), "hi": round(max(a, b), 2)})
    D["d1_tornado"] = {"base": round(base_of(inp), 2), "rows": torn}
    D["d1_rates"] = {"Current accounts": inp.rate_current, "Term deposits": inp.rate_term, "CPI, Oct 2026": 3.5, "COI, 4 year average": round(deposits.coi_avg_rate(4.75, 1.5, 3.0), 2)}
    h = nbp_history()
    D["d1_history"] = h.round(2).to_dict("records")
    hh = h.dropna(subset=["cpi"])
    D["d1_history_stats"] = {"start": hh.month.min(), "end": hh.month.max(), "months": int(len(hh)),
                             "current_above_cpi_pct": round(float((hh.current > hh.cpi).mean() * 100), 1), "term_above_cpi_pct": round(float((hh.term > hh.cpi).mean() * 100), 1),
                             "current_avg": round(float(hh.current.mean()), 2), "term_avg": round(float(hh.term.mean()), 2), "cpi_avg": round(float(hh.cpi.mean()), 2),
                             "real_current_cum_pct": round(float((np.prod((1 + hh.current / 1200 * 0.81) / (1 + hh.cpi / 1200)) - 1) * 100), 1)}
    # D2
    month, split = latest_aum_split()
    gaps = fee_drag.annual_fee_gap(split["active"])
    d2s = gaps.groupby("scenario").annual_gap_pln.sum().reindex(S) / 1e9
    D["d2_split"] = {"month": month, "rows": [{"bucket": b, "active_bn": round(split.loc[b, "active"] / 1e9, 1), "passive_bn": round(split.loc[b, "passive"] / 1e9, 1),
                                                "passive_share_pct": round(split.loc[b, "passive_share_pct"], 1)} for b in ["equity", "bond", "short_bond", "mixed"]]}
    D["d2_by_bucket"] = gaps.pivot_table(index="bucket", columns="scenario", values="annual_gap_pln").div(1e9).round(2)[S].reset_index().to_dict("records")
    D["d2_assumptions"] = fee_drag.assumptions_table().to_dict("records")
    D["d2_funds"] = pd.read_csv(ROOT / "data/reference/short_term_fund_costs.csv").sort_values("cost_pct")[["fund", "cost_pct", "basis", "data_year"]].to_dict("records")
    D["d2_compound"] = [{"year": y, "high": round(100_000 * (1 + (7.0 - 2.13) / 100) ** y), "low": round(100_000 * (1 + (7.0 - 0.70) / 100) ** y)} for y in range(31)]
    flows, nav = build_izfia()
    navb = nav[~nav.dedicated & nav.bucket.isin(BUCKETS)].groupby(["month", "bucket"]).nav.sum().unstack().fillna(0) / 1e9
    D["d2_assets_history"] = navb[navb.index >= "2018-08"].round(2).reset_index().to_dict("records")
    # D3
    d3 = tax_wrappers.annual_gap(tax_wrappers.Inputs())
    d3s = d3.set_index("scenario").annual_gap_pln.reindex(S) / 1e9
    D["d3_belka"] = [{"year": "2024", "savings": 7.3, "investments": 3.2}, {"year": "2025", "savings": 5.7, "investments": 3.6}, {"year": "2026F", "savings": 5.1, "investments": 3.9}]
    D["d3_table"] = d3.assign(savings_bn=d3.gap_savings_pln / 1e9, investments_bn=d3.gap_investments_pln / 1e9, total_bn=d3.annual_gap_pln / 1e9)[
        ["scenario", "share_savings", "share_investments", "savings_bn", "investments_bn", "total_bn"]].round(2).to_dict("records")
    # D4
    d4 = ppk.annual_loss(ppk.Inputs())
    d4s = d4.set_index("scenario").annual_loss_pln.reindex(S) / 1e9
    D["d4_table"] = d4.assign(loss_bn=d4.annual_loss_pln / 1e9).drop(columns="annual_loss_pln").round(2).to_dict("records")
    # D5
    res = run_d5()
    panel = pd.read_csv(PROCESSED / "d5_panel.csv")
    months = sorted(panel.month.unique())
    D["d5_table"] = res.to_dict("records")
    eq = panel[panel.bucket == "equity"].sort_values("month")
    D["d5_equity_flows"] = [{"month": m, "flow_bn": round(fl / 1e9, 3), "r_pct": round(r * 100, 2)} for m, fl, r in zip(eq.month, eq.flow, eq.r)]
    D["d5_index"] = {"months": months, **{b: list(np.round(100 * np.cumprod(1 + panel[panel.bucket == b].sort_values("month").r.values), 2)) for b in BUCKETS}}
    D["d5_rolling"] = [{"end": months[i + 59], **{b: round(investor_gap(panel, b, months[i], months[i + 59]).gap_pp, 2) for b in ["equity", "mixed", "bond"]}} for i in range(len(months) - 59)]
    d5_base = res.set_index("category").loc[BUCKETS, "gap_pln_bn"].clip(lower=0).sum() / (len(months) / 12)
    series = {"D1": d1s, "D4": d4s, "D3": d3s, "D2": d2s, "D5": pd.Series([0.3, round(float(d5_base), 2), 0.5], index=S)}
    D["levers"] = [{"key": k, "label": LEVERS[k], **{s: round(float(v[s]), 2) for s in S}} for k, v in series.items()]
    D["total"] = {s: round(sum(float(v[s]) for v in series.values()), 1) for s in S}
    return D


# ------------------------------------------------------------------ charts
def make_charts(D: dict) -> list[str]:
    plt, out = ch.plt, []
    L = D["levers"][::-1]
    f, ax = ch.fig(7.2, 3.4, "Five levers · PLN bn a year", "Annual gap versus an alternative with the same risk")
    for i, l in enumerate(L):
        ax.barh(i, l["base"], color=ch.BLUE, height=0.5, zorder=3)
        ax.plot([l["conservative"], l["aggressive"]], [i, i], color=ch.INK, lw=1.2, zorder=4)
        for x in (l["conservative"], l["aggressive"]):
            ax.plot([x, x], [i - 0.12, i + 0.12], color=ch.INK, lw=1.2, zorder=4)
        ax.text(l["aggressive"] + 0.35, i, f"{n(l['base'])}  ({n(l['conservative'])} to {n(l['aggressive'])})", va="center", fontsize=8.5)
    ax.set_yticks(range(len(L)), [f"{l['key']}  {l['label']}" for l in L]); ax.grid(axis="y", visible=False); ax.set_xlim(0, 24)
    ch.source(ax, "Bar: base scenario · line: conservative to aggressive · source: amb research", -0.16)
    out.append(ch.save(f, "c01_levers").name)

    R = D["d1_rates"]
    f, ax = ch.fig(6.4, 3.2, "D1 · Deposits", "Interest rates and inflation, % a year")
    bars = ax.bar(list(R), list(R.values()), color=[ch.G4, ch.G4, ch.G3, ch.BLUE], width=0.55, zorder=3)
    for b, v in zip(bars, R.values()):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{n(v, 2)}%", ha="center", fontsize=9)
    ax.grid(axis="x", visible=False)
    ch.source(ax, "NBP MIR Sep 2026 (outstanding stock), GUS CPI Oct 2026, obligacjeskarbowe.pl Nov 2026 (base CPI 3%)", -0.14)
    out.append(ch.save(f, "c02_rates_now").name)

    h = pd.DataFrame(D["d1_history"]); h["d"] = pd.to_datetime(h.month)
    f, ax = ch.fig(7.2, 3.3, "D1 · History", "Household deposit rates and inflation, % a year")
    ax.fill_between(h.d, h.cpi, color=ch.G2, zorder=2, label="CPI inflation y/y")
    ax.plot(h.d, h.term, color=ch.G5, lw=1.4, zorder=3, label="Term deposits")
    ax.plot(h.d, h.current, color=ch.BLUE, lw=1.8, zorder=4, label="Current accounts")
    ax.legend(loc="upper left", ncol=3)
    ch.source(ax, "NBP MIR statistics (rates on outstanding stock), Jan 2005 to Sep 2026; GUS CPI, same month previous year = 100", -0.12)
    out.append(ch.save(f, "c03_rates_history").name)

    t = D["d1_tornado"]; rows = t["rows"][::-1]
    f, ax = ch.fig(7.2, 2.9, "D1 · Sensitivity", "Range of the D1 result when one assumption changes, PLN bn a year")
    for i, r in enumerate(rows):
        ax.barh(i, r["hi"] - r["lo"], left=r["lo"], color=ch.BLUE, height=0.5, zorder=3)
        ax.text(r["lo"] - 0.15, i, n(r["lo"]), ha="right", va="center", fontsize=8.5)
        ax.text(r["hi"] + 0.15, i, n(r["hi"]), ha="left", va="center", fontsize=8.5)
    ax.axvline(t["base"], color=ch.INK, lw=1, zorder=4); ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.text(t["base"] + 0.1, len(rows) - 0.45, f"base {n(t['base'])}", fontsize=8)
    ax.set_yticks(range(len(rows)), [r["label"] for r in rows]); ax.set_xlim(3, 15); ax.grid(axis="y", visible=False)
    ch.source(ax, "amb research; all other assumptions at the base scenario", -0.16)
    out.append(ch.save(f, "c04_d1_tornado").name)

    tb = pd.DataFrame(D["d1_table"]); piv = tb.pivot(index="scenario", columns="deposit_type", values="gap_bn").reindex(S)
    f, ax = ch.fig(6.4, 3.0, "D1 · Result", "Annual gap by scenario and deposit type, PLN bn")
    ax.bar(S, piv["current"], color=ch.BLUE, width=0.5, label="Current accounts", zorder=3)
    ax.bar(S, piv["term"], bottom=piv["current"], color=ch.G4, width=0.5, label="Term deposits", zorder=3, edgecolor="white", linewidth=1)
    for i, s in enumerate(S):
        ax.text(i, piv.loc[s].sum() + 0.3, n(piv.loc[s].sum()), ha="center", fontsize=9, fontweight="medium")
    ax.legend(loc="upper left"); ax.grid(axis="x", visible=False)
    ch.source(ax, "python -m engine.run_d1 → data/processed/d1_deposits.csv", -0.14)
    out.append(ch.save(f, "c05_d1_split").name)

    f, ax = ch.fig(5.2, 3.0, "D4 · PPK", "PPK participation, Oct 2026, %")
    vals = {"Private sector": 73.04, "Total": 63.9, "Public sector": 37.53}
    bars = ax.bar(list(vals), list(vals.values()), color=[ch.G4, ch.G3, ch.BLUE], width=0.55, zorder=3)
    for b, v in zip(bars, vals.values()):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{n(v)}%", ha="center", fontsize=9)
    ax.set_ylim(0, 100); ax.grid(axis="x", visible=False)
    ch.source(ax, "PFR, PPK register, 28 Oct 2026 (as reported by analizy.pl)", -0.14)
    out.append(ch.save(f, "c06_d4_participation").name)

    steps = [("Employer\ncontribution", 1332), ("PIT 12%", -160), ("Withdrawals\nbefore 60", -176), ("State\nsubsidy", 120)]
    f, ax = ch.fig(6.0, 3.0, "D4 · Per person", "Loss per person a year, base scenario, PLN")
    run = 0
    for i, (lab, v) in enumerate(steps):
        ax.bar(i, abs(v), bottom=run if v >= 0 else run + v, color=ch.BLUE if v > 0 else ch.G3, width=0.55, zorder=3)
        ax.text(i, run + max(v, 0) + 25, (f"+{v:,}" if v > 0 and i else f"{v:,}"), ha="center", fontsize=8.5)
        run += v
    ax.bar(len(steps), run, color=ch.INK, width=0.55, zorder=3); ax.text(len(steps), run + 25, f"{run:,}", ha="center", fontsize=9, fontweight="medium")
    ax.set_xticks(range(len(steps) + 1), [s[0] for s in steps] + ["Loss per\nperson"]); ax.grid(axis="x", visible=False); ax.set_ylim(0, 1600)
    ch.source(ax, "Gross pay PLN 7,400 · 85% of employer contributions kept · 50% of subsidies · python -m engine.run_d4", -0.22)
    out.append(ch.save(f, "c07_d4_waterfall").name)

    B = D["d3_belka"]
    f, ax = ch.fig(5.6, 3.0, "D3 · IKE and IKZE", "Belka tax receipts, PLN bn")
    xs = [b["year"] for b in B]
    ax.bar(xs, [b["savings"] for b in B], color=ch.BLUE, width=0.5, label="Interest on savings", zorder=3)
    ax.bar(xs, [b["investments"] for b in B], bottom=[b["savings"] for b in B], color=ch.G4, width=0.5, label="Investment gains", zorder=3, edgecolor="white", linewidth=1)
    for i, b in enumerate(B):
        ax.text(i, b["savings"] + b["investments"] + 0.2, n(b["savings"] + b["investments"]), ha="center", fontsize=9)
    ax.legend(loc="upper right"); ax.grid(axis="x", visible=False); ax.set_ylim(0, 12.5)
    ch.source(ax, "Ministry of Finance (as reported by PAP and analizy.pl); 2026F = forecast", -0.14)
    out.append(ch.save(f, "c08_d3_belka").name)

    A = pd.DataFrame(D["d2_assets_history"]); A["d"] = pd.to_datetime(A.month)
    f, ax = ch.fig(7.2, 3.3, "D2 · Fund market", "Assets of non-dedicated funds (excluding PPK), PLN bn")
    order = ["short_bond", "bond", "equity", "mixed", "absolute_return"]
    ax.stackplot(A.d, *[A[b] for b in order], colors=[ch.BLUE, ch.BLUE_SOFT, ch.INK4, ch.G4, ch.G3], labels=[NAMES[b] for b in order], edgecolor="white", linewidth=0.4)
    ax.legend(loc="upper left", ncol=3)
    ch.source(ax, "IZFiA RawData (NAV of every fund), Aug 2018 to Oct 2026; amb research", -0.12)
    out.append(ch.save(f, "c09_d2_assets").name)

    sp = D["d2_split"]["rows"]
    f, ax = ch.fig(6.0, 2.6, "D2 · Passive funds", "Passive funds as a share of assets, Oct 2026, %")
    yy = np.arange(len(sp))[::-1]
    ax.barh(yy, [100] * len(sp), color=ch.G1, height=0.55, zorder=2)
    ax.barh(yy, [r["passive_share_pct"] for r in sp], color=ch.BLUE, height=0.55, zorder=3)
    for yv, r in zip(yy, sp):
        ax.text(r["passive_share_pct"] + 1.5, yv, f"{n(r['passive_share_pct'])}%   (PLN {n(r['active_bn'] + r['passive_bn'], 0)} bn of assets)", va="center", fontsize=8.5)
    ax.set_yticks(yy, [NAMES[r["bucket"]] for r in sp]); ax.set_xlim(0, 100); ax.grid(False)
    ch.source(ax, "IZFiA, Passive flag, Oct 2026, non-dedicated funds", -0.18)
    out.append(ch.save(f, "c10_d2_passive").name)

    F = D["d2_funds"]
    f, ax = ch.fig(6.8, 4.0, "D2 · Costs", "Short term bond funds: annual ongoing charges, %")
    yy = np.arange(len(F))[::-1]
    ax.barh(yy, [x["cost_pct"] for x in F], color=[ch.G4 if x["basis"].startswith("estimate") else ch.BLUE for x in F], height=0.6, zorder=3)
    for yv, x in zip(yy, F):
        ax.text(x["cost_pct"] + 0.02, yv, f"{n(x['cost_pct'], 2)}%", va="center", fontsize=8)
    ax.axvline(0.88, color=ch.INK, lw=1, ls=(0, (3, 2))); ax.text(0.9, -0.9, "asset weighted average 0.88%", fontsize=7.5)
    ax.set_yticks(yy, [x["fund"] for x in F], fontsize=8); ax.set_xlim(0, 1.45); ax.grid(axis="y", visible=False)
    ch.source(ax, "KID documents and TFI cost tables, 2021 to 2026 · grey: estimated from the management fee", -0.1)
    out.append(ch.save(f, "c11_d2_funds").name)

    P = pd.DataFrame(D["d2_compound"])
    f, ax = ch.fig(6.4, 3.1, "D2 · Compounding", "PLN 100,000 at 7% a year before costs, PLN thousand")
    ax.plot(P.year, P.low / 1000, color=ch.BLUE, lw=2, label="Cost 0.70% (index fund)")
    ax.plot(P.year, P.high / 1000, color=ch.G4, lw=2, label="Cost 2.13% (average equity fund)")
    ax.fill_between(P.year, P.high / 1000, P.low / 1000, color=ch.BLUE, alpha=0.08)
    ax.text(19, 420, "PLN 209,000 difference\nafter 30 years", fontsize=9, color=ch.BLUE, ha="right")
    ax.legend(loc="upper left"); ax.set_xlabel("years")
    ch.source(ax, "engine/models/fee_drag.py · active cost: equity fund TER 2023 (analizy.pl)", -0.2)
    out.append(ch.save(f, "c12_d2_compound").name)

    E = pd.DataFrame(D["d5_equity_flows"]); E["d"] = pd.to_datetime(E.month)
    f, ax = ch.fig(7.2, 3.1, "D5 · Behaviour", "Equity funds: monthly net flows, PLN bn")
    ax.bar(E.d, E.flow_bn, width=22, color=[ch.BLUE if v >= 0 else ch.G4 for v in E.flow_bn], zorder=3)
    i20 = E.index[E.month == "2020-03"][0]
    ax.annotate("Mar 2020: PLN 1.1 bn out\nas funds fell 14.3%", (E.d[i20], E.flow_bn[i20]), xytext=(E.d[i20] + pd.Timedelta(days=200), -1.25), fontsize=8, arrowprops=dict(arrowstyle="-", color=ch.G5, lw=0.8))
    ax.axhline(0, color=ch.G5, lw=0.8)
    ch.source(ax, "IZFiA, net flows of non-dedicated funds, Sep 2018 to Oct 2026", -0.12)
    out.append(ch.save(f, "c13_d5_flows").name)

    I = D["d5_index"]; dts = pd.to_datetime(I["months"])
    f, ax = ch.fig(7.2, 3.2, "D5 · Returns", "Cumulative return by fund category (TWR), Aug 2018 = 100")
    for b, (c, lw) in {"equity": (ch.BLUE, 2), "mixed": (ch.INK4, 1.4), "bond": (ch.G4, 1.4), "short_bond": (ch.BLUE_SOFT, 1.4), "absolute_return": (ch.G3, 1.4)}.items():
        ax.plot(dts, I[b], color=c, lw=lw, label=NAMES[b])
    ax.axhline(100, color=ch.G5, lw=0.8); ax.legend(loc="upper left", ncol=3)
    ch.source(ax, "IZFiA; modified Dietz with reclassification alignment (engine/models/investor_gap.py)", -0.12)
    out.append(ch.save(f, "c14_d5_index").name)

    Rl = pd.DataFrame(D["d5_rolling"]); Rl["d"] = pd.to_datetime(Rl.end)
    f, ax = ch.fig(7.2, 3.0, "D5 · Investor gap", "Investor gap in rolling five year windows, pp a year (window end)")
    ax.plot(Rl.d, Rl.equity, color=ch.BLUE, lw=2, label="Equity"); ax.plot(Rl.d, Rl.mixed, color=ch.INK4, lw=1.5, label="Mixed"); ax.plot(Rl.d, Rl.bond, color=ch.G4, lw=1.5, label="Bond")
    ax.axhline(1.2, color=ch.G5, lw=0.8, ls=(0, (3, 2))); ax.text(Rl.d.iloc[0], 1.24, "United States, Morningstar: about 1.2 pp", fontsize=7.5, color=ch.G5)
    ax.legend(loc="upper right", ncol=3); ax.set_ylim(-0.2, 2.1)
    ch.source(ax, "IZFiA; 39 five year windows; amb research (python -m engine.run_d5)", -0.14)
    out.append(ch.save(f, "c15_d5_rolling").name)

    Lv = {l["key"]: l["base"] for l in D["levers"]}
    groups = [("Idle money\n(D1)", Lv["D1"]), ("Unused programmes\n(D3 + D4)", Lv["D3"] + Lv["D4"]), ("Market\n(D2 + D5)", Lv["D2"] + Lv["D5"])]
    f, ax = ch.fig(5.6, 3.0, "Synthesis", "Where the money goes, PLN bn a year, base scenario")
    bars = ax.bar([g[0] for g in groups], [g[1] for g in groups], color=[ch.INK, ch.BLUE, ch.G4], width=0.55, zorder=3)
    for b, g in zip(bars, groups):
        ax.text(b.get_x() + b.get_width() / 2, g[1] + 0.2, f"PLN {n(g[1])} bn", ha="center", fontsize=9, fontweight="medium")
    ax.grid(axis="x", visible=False); ax.set_ylim(0, 11)
    ch.source(ax, f"Total: PLN {n(D['total']['base'])} bn a year · amb research", -0.2)
    out.append(ch.save(f, "c16_groups").name)
    return out


# ------------------------------------------------------------------ terminal
def print_report(D: dict, files: list[str]) -> None:
    ui.banner("Money left on the table", "How much Polish households lose each year through the way they save · data: NBP, GUS, IZFiA, KNF, MF, PFR")
    ui.summary([(f"{l['key']}  {l['label']}", l["conservative"], l["base"], l["aggressive"]) for l in D["levers"]], tuple(D["total"][s] for s in S))

    ui.section("01", "D1 · Deposits", "Deposits instead of inflation indexed Treasury bonds")
    ui.table(["scenario", "type", "COI %", "deposit %", "gap pp", "share", "movable bn", "gap bn"],
             [[r["scenario"], r["deposit_type"], n(r["coi_rate_pct"], 2), n(r["deposit_rate_pct"], 2), n(r["gap_after_tax_pp"], 2), f"{r['movable_share']:.0%}", n(r["movable_bn"], 0), n(r["gap_bn"], 2)] for r in D["d1_table"]], highlight=2)
    hs = D["d1_history_stats"]
    ui.note(f"{hs['start']} to {hs['end']}: current accounts beat inflation in {n(hs['current_above_cpi_pct'])}% of months, term deposits in {n(hs['term_above_cpi_pct'])}%.")
    ui.table(["assumption", "low", "high"], [[r["label"], n(r["lo"]), n(r["hi"])] for r in D["d1_tornado"]["rows"]], title="Sensitivity, PLN bn")

    ui.section("02", "D2 · Fees", "Fees in investment funds versus a low cost alternative")
    ui.table(["category", "active bn", "passive bn", "passive %"], [[NAMES[r["bucket"]], n(r["active_bn"]), n(r["passive_bn"]), n(r["passive_share_pct"])] for r in D["d2_split"]["rows"]])
    ui.table(["category", "conservative", "base", "aggressive"], [[NAMES[r["bucket"]], n(r["conservative"], 2), n(r["base"], 2), n(r["aggressive"], 2)] for r in D["d2_by_bucket"]], title="Annual cost gap, PLN bn")

    ui.section("03", "D3 · IKE and IKZE", "Belka tax that could be avoided legally")
    ui.table(["scenario", "savings share", "investment share", "savings bn", "investments bn", "total bn"],
             [[r["scenario"], f"{r['share_savings']:.0%}", f"{r['share_investments']:.0%}", n(r["savings_bn"], 2), n(r["investments_bn"], 2), n(r["total_bn"], 2)] for r in D["d3_table"]], highlight=1)

    ui.section("04", "D4 · PPK", "Employer contributions and state subsidies forgone")
    ui.table(["scenario", "gross pay", "employer net", "loss per person", "opted out mn", "PLN bn"],
             [[r["scenario"], f"{r['gross_pay']:,.0f}", f"{r['employer_net_year']:,.0f}", f"{r['loss_per_person_year']:,.0f}", n(r["opted_out_mn"]), n(r["loss_bn"], 2)] for r in D["d4_table"]], highlight=1)

    ui.section("05", "D5 · Investor gap", "Fund returns (TWR) versus investor returns (IRR)")
    ui.table(["category", "TWR %", "IRR %", "gap pp", "5y median", "5y range"],
             [[NAMES.get(r["category"], r["category"]), n(r["twr_pct"], 2), n(r["irr_pct"], 2), n(r["gap_pp"], 2), n(r["gap_5y_median_pp"], 2), f"{n(r['gap_5y_min_pp'], 2)} to {n(r['gap_5y_max_pp'], 2)}"] for r in D["d5_table"]])

    ui.section("06", "Output", f"{len(files)} charts in report/charts, report data in report/data.json")
    ui.stat(f"PLN {n(D['total']['base'])} bn", f"a year in the base scenario · range {n(D['total']['conservative'])} to {n(D['total']['aggressive'])}")
    ui.console.print()


def main(quiet: bool = False) -> dict:
    D = collect()
    files = make_charts(D)
    (ROOT / "report" / "data.json").write_text(json.dumps(D, ensure_ascii=False, indent=1, default=str))
    if not quiet:
        print_report(D, files)
    return D


if __name__ == "__main__":
    main(quiet="--quiet" in sys.argv)
