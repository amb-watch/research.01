"""amb research · Report 01, long form PDF: HTML and CSS rendered by headless Chrome.

    python -m engine.report --quiet      # data and charts first
    python report/pdf/build_pdf.py       # then report/pdf/amb_research_report_01.pdf

Chrome is located through the CHROME_PATH environment variable, the Playwright cache or the
standard macOS and Linux install locations.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
D = json.loads((ROOT / "report" / "data.json").read_text())


def find_chrome() -> str:
    if os.environ.get("CHROME_PATH"):
        return os.environ["CHROME_PATH"]
    for p in sorted((Path.home() / "Library/Caches/ms-playwright").glob("chromium-*/chrome-mac*/*.app/Contents/MacOS/*")):
        return str(p)
    for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"]:
        if Path(p).exists():
            return p
    for name in ["google-chrome", "chromium", "chromium-browser"]:
        if shutil.which(name):
            return shutil.which(name)
    raise SystemExit("Chrome not found: set CHROME_PATH")


n = lambda x, d=1: f"{x:,.{d}f}"  # noqa: E731
L = {l["key"]: l for l in D["levers"]}
T, HS = D["total"], D["d1_history_stats"]
NAMES = {"equity": "Equity", "mixed": "Mixed", "bond": "Bond", "short_bond": "Short term bond", "absolute_return": "Absolute return", "total": "Total"}
S = ["conservative", "base", "aggressive"]

# ------------------------------------------------------------------ building blocks
def chapter(num, kicker, title, lead=""):
    return (f'<section class="chapter"><p class="ch-num">{num}</p><p class="kicker">[ {escape(kicker.upper())} ]</p><h1>{title}</h1>'
            + (f'<p class="lead">{lead}</p>' if lead else "") + "</section>")


def h2(t, k=None):
    return '<div class="h2g">' + (f'<p class="kicker small">[ {escape(k.upper())} ]</p>' if k else "") + f"<h2>{t}</h2></div>"


def p(*ps):
    return "".join(f"<p>{x}</p>" for x in ps)


def ul(*items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


FIG = [0]


def fig(name, caption):
    FIG[0] += 1
    return f'<figure><img src="../charts/{name}.svg"><figcaption>Figure {FIG[0]}. {caption}</figcaption></figure>'


def table(head, rows, align=None, hl=None, cls=""):
    align = align or ["l"] + ["r"] * (len(head) - 1)
    th = "".join(f'<th class="{a}">{escape(h)}</th>' for h, a in zip(head, align))
    tr = "".join("<tr" + (' class="hl"' if i == hl else "") + ">" + "".join(f'<td class="{a}">{c}</td>' for c, a in zip(r, align)) + "</tr>" for i, r in enumerate(rows))
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def stats(*items):
    return '<div class="stats">' + "".join(f'<div class="stat"><p class="v">{v}</p><p class="l">{l}</p></div>' for v, l in items) + "</div>"


def box(title, *ps):
    return f'<div class="box"><p class="kicker small">[ {escape(title.upper())} ]</p>' + "".join(f"<p>{x}</p>" for x in ps) + "</div>"


d1b = {r["deposit_type"]: r for r in D["d1_table"] if r["scenario"] == "base"}
d4 = {r["scenario"]: r for r in D["d4_table"]}
d2b = {r["bucket"]: r for r in D["d2_by_bucket"]}
d2s = {r["bucket"]: r for r in D["d2_split"]["rows"]}
d5 = {r["category"]: r for r in D["d5_table"]}
torn = D["d1_tornado"]

H: list[str] = []
# ------------------------------------------------------------------ cover and contents
H.append(f"""<section class="cover">
<div class="cv-top"><img class="cv-logo" src="../assets/logo_white.png"><span>amb research</span></div>
<img class="cv-mark" src="../assets/logo_blue.png">
<div class="cv-body"><p class="kicker">[ REPORT 01 ]</p>
<h1 class="cv-title">Money left on the table</h1>
<p class="cv-sub">How much Polish households lose each year through the way they save, and how much they could recover without taking on additional risk</p></div>
<div class="cv-foot"><span>DRAFT 0.2 · 19 NOVEMBER 2026</span><span>DATA: NBP · GUS · IZFiA · KNF · MF · PFR</span></div>
</section>""")

toc = [("01", "Key findings"), ("02", "About this report"), ("03", "Methodology"), ("04", "Data and quality controls"), ("05", "D1 · Deposits instead of Treasury bonds"),
       ("06", "D4 · PPK opt outs"), ("07", "D3 · Unused IKE and IKZE"), ("08", "D2 · Fees in investment funds"), ("09", "D5 · Poor timing"),
       ("10", "Synthesis: where the money goes"), ("11", "Recommendations"), ("12", "Limitations and the path to version 1.0"), ("A", "Appendices: engine outputs, glossary, sources")]
H.append('<section class="toc"><p class="kicker">[ CONTENTS ]</p><h1>Contents</h1><ol class="toc-list">'
         + "".join(f'<li><span class="n">{a}</span><span class="t">{b}</span></li>' for a, b in toc) + "</ol>"
         + box("How to read this report",
               "Every lever chapter follows the same structure: context, how the alternative works, method and assumptions, results in three scenarios, sensitivity and conclusions. "
               "Every figure in the text is produced by an open source calculation engine; each chart states its data source and the command that reproduces it.",
               "This report describes product categories and public data. It is not investment advice and does not recommend any specific product.") + "</section>")

# ------------------------------------------------------------------ 01 key findings
H.append(chapter("01", "Key findings", "Polish households leave about PLN 18 bn on the table every year",
                 "The largest losses come from idle money and from public programmes that people do not use. Poor market timing costs the least."))
H.append(stats((f"PLN {n(T['base'])} bn", "a year in the base scenario"), (f"{n(T['conservative'])} to {n(T['aggressive'])}", "PLN bn: range across scenarios"),
               ("about 0.5% of GDP", "and twice the entire Belka tax take (about PLN 9 bn)")))
H.append(p("We estimate how much Polish households lose each year compared with a simple, widely available alternative carrying <b>the same level of risk</b>. "
           "This qualification is central to the analysis. We do not compare a bank deposit with equities, because the difference between them reflects a different choice rather than a loss. "
           "We compare products that are equally safe for the saver, for example a bank account and a Treasury bond.",
           f"The result is about PLN {n(T['base'])} bn a year in the base scenario, within a range of PLN {n(T['conservative'])} bn to PLN {n(T['aggressive'])} bn. "
           "Deposits account for more than half of the total: money held in current accounts that pay an average of 0.49% a year while inflation runs at 3.5%."))
H.append(fig("c01_levers", "Five levers: annual gap versus an alternative with the same risk. Source: amb research."))
H.append(h2("Six findings", "Summary"))
H.append('<ol class="findings">' + "".join(f"<li><b>{a}</b> {b}</li>" for a, b in [
    (f"Deposits are the largest lever at PLN {n(L['D1']['base'])} bn a year.", f"Households hold about PLN 1.1 trn in current accounts at an average rate of 0.49%. Since 2005, current accounts have paid more than inflation in only {n(HS['current_above_cpi_pct'])}% of months."),
    (f"PPK opt outs forgo PLN {n(L['D4']['base'])} bn a year of free money.", "About 2.8 mn eligible employees are outside PPK. Participation is 37.5% in the public sector against 73% in the private sector."),
    (f"IKE and IKZE could legally shelter PLN {n(L['D3']['base'])} bn of tax a year.", "There are about 1.3 mn IKE accounts for more than 30 mn adults, even though early withdrawal from an IKE costs nothing beyond the ordinary tax."),
    (f"Fund fees cost PLN {n(L['D2']['base'])} bn a year above low cost alternatives.", "Outside equity, low cost index funds barely exist: they hold 0% to 2% of bond and mixed fund assets."),
    (f"Poor timing costs the least, about PLN {n(L['D5']['base'])} bn a year.", "The investor gap in equity and mixed funds is typically 0.4 to 0.7 pp a year, below the roughly 1.2 pp reported for the United States. The hypothesis that Polish investors lose heavily on timing is not supported."),
    ("Media estimates overstate the deposit problem, but not its direction.", "The popular claim of PLN 50 bn lost each year compares entire account balances with inflation. A like for like comparison, limited to money that can realistically move and measured after tax, gives about PLN 9 bn."),
]) + "</ol>")
H.append(table(["Lever", "Conservative", "Base", "Aggressive"], [[f"{l['key']} {l['label']}", n(l["conservative"]), f"<b>{n(l['base'])}</b>", n(l["aggressive"])] for l in D["levers"]]
               + [["<b>Total, PLN bn a year</b>", f"<b>{n(T['conservative'])}</b>", f"<b>{n(T['base'])}</b>", f"<b>{n(T['aggressive'])}</b>"]], hl=len(D["levers"])))

# ------------------------------------------------------------------ 02 about
H.append(chapter("02", "About this report", "One question, five levers, public data only"))
H.append(h2("Research question"))
H.append(p("How much do Polish households lose each year, in billions of zloty, compared with a simple and widely available alternative carrying the same level of risk, and which lever accounts for the largest share of that loss?",
           "The question is deliberately narrow. We do not assess whether Poles should invest more in equities, nor do we argue for a particular portfolio. "
           "We ask only about money that could be recovered <i>without changing the risk profile</i>: by moving it into an equally safe product that pays more, costs less or is taxed more favourably."))
H.append(h2("Why it matters"))
H.append(p("Household savings are the largest pool of capital in the Polish economy. Household bank deposits alone exceed PLN 1.5 trn. "
           "Even a small difference in their yield, cost or tax treatment translates into billions of zloty a year that remain with banks, fund managers or the state rather than with savers.",
           "Public debate tends to focus on whether Poles save too little and whether they fear the stock market. This report offers a different perspective: "
           "a larger problem than market risk lies in money that sits idle and in programmes the state already offers but few people use."))
H.append(h2("Five levers"))
H.append(table(["Lever", "What savers do today", "Alternative with the same risk"], [
    ["D1 Deposits", "Hold surplus cash in current accounts or term deposits", "Inflation indexed retail Treasury bonds (COI)"],
    ["D2 Fees", "Buy actively managed investment funds", "A low cost index fund in the same asset class"],
    ["D3 Tax", "Save in an ordinary account and pay the 19% Belka tax", "The same instruments inside IKE or IKZE"],
    ["D4 PPK", "Opt out of the Employee Capital Plans (PPK)", "Remaining in PPK"],
    ["D5 Timing", "Buy and sell funds in response to the market", "The return of the funds at constant exposure"]], align=["l", "l", "l"]))
H.append(h2("What this report is not"))
H.append(ul("It is not investment advice. We describe product categories and aggregate data and do not recommend any specific fund.",
            "It is not an assessment of individual banks or fund managers. Fund names appear only where we show the spread of costs taken from their own documents.",
            "It is not final. This is draft 0.2: three assumptions still need to be anchored in data and several figures need to be confirmed against source files (chapter 12)."))

# ------------------------------------------------------------------ 03 method
H.append(chapter("03", "Methodology", "Like for like risk, three scenarios, no double counting"))
H.append(h2("Principle 1: like for like risk"))
H.append(p("Every loss is measured against an alternative that is at least as safe for the saver. A bank deposit is compared with a Treasury bond, an active bond fund with a bond index fund, and an ordinary account with the same instrument held inside an IKE. "
           "The result therefore measures money that can be recovered without changing the risk profile.",
           "This principle makes our figures lower than popular estimates. That is a deliberate choice: we would rather defend an estimate of at least X than a striking figure that is easy to dispute."))
H.append(h2("Principle 2: three scenarios"))
H.append(p("Each lever has a conservative scenario (the least favourable assumptions), a base scenario and an aggressive scenario (the most favourable). Headlines use the base scenario and always quote the range. "
           "For the key assumptions we also show a sensitivity analysis: how far the result moves when one assumption changes and all others stay at the base scenario."))
H.append(h2("Principle 3: no double counting"))
H.append(p("We add the levers together only because they concern different money or different effects. D1 concerns deposits and D4 wages; D2 and D5 both concern investment funds but measure cost and timing respectively. "
           "D3 starts from the tax paid today rather than after the move into bonds assumed in D1. If the money moved into COI bonds, the IKE shield would be worth more, so this approach is conservative."))
H.append(h2("Principle 4: reproducibility"))
H.append(p("Every figure comes from an open source engine written in Python. Each lever has its own command (python -m engine.run_d1 to run_d5), and the full report, including charts and presentation data, is reproduced by a single command: python -m engine.report. "
           "The logic is covered by 29 unit tests on synthetic data."))
H.append(h2("Formulas"))
H.append(table(["Lever", "Annual gap"], [
    ["D1", "deposits × movable share × (r<sub>COI</sub> − r<sub>deposit</sub>) × (1 − 19%) − cost of early redemptions"],
    ["D2", "assets of active funds × (active cost − alternative cost)"],
    ["D3", "Belka tax on savings × avoidable share + Belka tax on investments × avoidable share"],
    ["D4", "employees outside PPK × (1.5% of pay × 12 × (1 − 12%) × share kept + PLN 240 × share kept)"],
    ["D5", "(TWR − IRR) on monthly net flows; in zloty: value if every payment had grown at the TWR, less the actual value"]], align=["l", "l"]))

# ------------------------------------------------------------------ 04 data
H.append(chapter("04", "Data and quality controls", "All data is public, and every source carries its download date"))
H.append(p("The engine downloads data automatically wherever the source allows and records a manifest with the file URL, download time and SHA-256 checksum. "
           "Where a website is protected by an anti bot challenge (NBP monetary statistics, fund quotes on stooq) we do not circumvent it. "
           "Instead we use other public files or publications citing the data, and flag those items for confirmation."))
H.append(table(["Source", "Content", "Period", "How obtained", "Used in"], [
    ["IZFiA, flow data", "Net flows by fund category", "Sep 2018 to Oct 2026, 98 files", "Automated, 3 file formats", "D5"],
    ["IZFiA, asset data", "NAV of every fund, passive flag", "Dec 2017 to Oct 2026, about 93k rows", "Automated, RawData sheet", "D2, D5"],
    ["NBP, MIR statistics", "Household deposit rates", "Jan 2005 to Sep 2026", "xlsx file from NBP server", "D1"],
    ["NBP (via Parkiet)", "Current and term deposits", "Jun 2026", "Press, to be confirmed", "D1"],
    ["GUS", "Monthly CPI", "1982 to Oct 2026", "CSV file", "D1"],
    ["obligacjeskarbowe.pl", "COI terms and redemption fee", "Nov 2026", "Offer page", "D1"],
    ["Fund KIDs and cost tables", "Ongoing charges of 12 funds", "2021 to 2026", "PDF documents", "D2"],
    ["analizy.pl", "Average costs by category", "2023 to 2025", "Publications", "D2"],
    ["KNF", "Fund manager revenue", "2025", "PDF report", "D2 check"],
    ["Ministry of Finance (via press)", "Belka tax receipts", "2024 to 2026F", "Press, to be confirmed", "D3"],
    ["MRPiPS", "IKE and IKZE limits", "2026", "Official notices", "D3"],
    ["PFR (via analizy.pl), GUS", "PPK participation, wages", "Sep to Oct 2026", "Press, to be confirmed", "D4"]], align=["l", "l", "l", "l", "l"], cls="small"))
H.append(h2("Quality controls"))
H.append(ul("<b>Fund assets.</b> Assets built up from individual funds were compared with the totals published by IZFiA. The median ratio is exactly 1.000, and 56 of 67 months fall within ±1%.",
            "<b>Double counting.</b> The first version of the parser identified funds by name, so name changes between files double counted assets by up to 50%. Switching to the fund code removed the problem. The error was caught precisely by the reconciliation with IZFiA totals.",
            "<b>PPK in fund data.</b> Until March 2021, IZFiA reported PPK funds within Mixed Other and separately thereafter. Both are excluded, because PPK contributions come from payroll rather than investor decisions.",
            "<b>Cross check for D2.</b> Fund managers' revenue from managing funds was PLN 4.69 bn in 2025 (KNF). Our cost gap of PLN 2.2 bn is about half of that amount, so the order of magnitude is consistent."))

# ------------------------------------------------------------------ 05 D1
H.append(chapter("05", "D1 · Deposits", f"Deposits instead of Treasury bonds: PLN {n(L['D1']['base'])} bn a year",
                 "The largest lever in the report. Households hold about PLN 1.1 trn in current accounts paying an average of 0.49% a year."))
H.append(stats(("PLN 1.1 trn", "in household current accounts (June 2026)"), ("0.49%", "average rate on those accounts (September 2026)"), (f"{n(HS['current_above_cpi_pct'])}%", "of months since 2005 in which current accounts beat inflation")))
H.append(h2("Context: two decades of real losses", "5.1"))
H.append(p("According to NBP, in June 2026 households held PLN 1,112.9 bn in current deposits and PLN 400.3 bn in term deposits. The average rate on the stock of current accounts was 0.49% in September 2026 and 2.79% on term deposits. CPI inflation was 3.5% year on year in October 2026.",
           f"This is not a recent anomaly. Between {HS['start']} and {HS['end']} ({HS['months']} months) current accounts paid an average of {n(HS['current_avg'], 2)}%, term deposits {n(HS['term_avg'], 2)}% and inflation averaged {n(HS['cpi_avg'], 2)}%. "
           f"Current accounts paid more than inflation in only {n(HS['current_above_cpi_pct'])}% of months; term deposits did so in {n(HS['term_above_cpi_pct'])}%. "
           f"A zloty held in a current account over the whole period lost about {n(abs(HS['real_current_cum_pct']), 0)}% of its purchasing power after tax."))
H.append(fig("c03_rates_history", "Household deposit rates on the outstanding stock and CPI inflation, January 2005 to September 2026. Source: NBP (MIR), GUS."))
H.append(h2("The alternative: COI Treasury bonds", "5.2"))
H.append(p("Four year COI bonds are retail Treasury bonds issued by the State Treasury. In the November 2026 offer they pay 4.75% in the first year and inflation plus a 1.50% margin in each subsequent year. Interest is paid annually and each bond costs PLN 100.",
           "Their credit risk is that of the State Treasury, no higher than that of a deposit covered by the Bank Guarantee Fund. The difference lies in liquidity: a bond can be redeemed early for PLN 2 per bond (since September 2024), and the money returns within a few days. "
           "COI bonds therefore do not replace a transaction account or a liquidity buffer, which is why the model moves only part of household deposits."))
H.append(fig("c02_rates_now", "Interest rates and inflation today. COI: four year average at 3% inflation in years 2 to 4."))
H.append(h2("Method and assumptions", "5.3"))
H.append(table(["Assumption", "Conservative", "Base", "Aggressive", "Rationale"], [
    ["Inflation in years 2 to 4", "2.0%", "3.0%", "4.0%", "3.5% in October 2026; 2.1% to 4.1% over the past year"],
    ["Share of current accounts that can move", "5%", "15%", "25%", "The rest is transactional money and liquidity buffers"],
    ["Share of term deposits that can move", "50%", "70%", "90%", "Term deposits are already set aside"],
    ["Early redemptions", "30%", "15%", "0%", "PLN 2 per bond, spread over four years"],
    ["Belka tax", "19%", "19%", "19%", "Applied on both sides of the comparison"]], align=["l", "r", "r", "r", "l"], cls="small"))
H.append(h2("Results", "5.4"))
H.append(p(f"In the base scenario, moving 15% of current account balances and 70% of term deposits into COI bonds would give households about PLN {n(L['D1']['base'])} bn a year after tax: "
           f"PLN {n(d1b['current']['gap_bn'])} bn from current accounts and PLN {n(d1b['term']['gap_bn'])} bn from term deposits. "
           f"Each zloty moved out of a current account earns about {n(d1b['current']['gap_after_tax_pp'])} pp a year more after tax; each zloty moved out of a term deposit about {n(d1b['term']['gap_after_tax_pp'])} pp."))
H.append(fig("c05_d1_split", "D1 gap by scenario and deposit type. Source: python -m engine.run_d1."))
H.append(table(["Scenario", "Type", "COI %", "Deposit %", "Gap pp", "Share", "Movable bn", "Gap bn"],
               [[r["scenario"], r["deposit_type"], n(r["coi_rate_pct"], 2), n(r["deposit_rate_pct"], 2), n(r["gap_after_tax_pp"], 2), f"{round(r['movable_share'] * 100)}%", n(r["movable_bn"], 0), n(r["gap_bn"], 2)] for r in D["d1_table"]],
               align=["l", "l", "r", "r", "r", "r", "r", "r"], hl=2, cls="small"))
H.append(h2("Sensitivity: one number drives the result", "5.5"))
H.append(p(f"The most sensitive assumption in the entire report is the share of current account balances that could realistically move. At 5% the D1 result falls to PLN {n(torn['rows'][0]['lo'])} bn; at 25% it rises to PLN {n(torn['rows'][0]['hi'])} bn. "
           "That range is wider than the combined effect of every other assumption. We do not know the size of Polish households' liquidity buffers with precision, which is why this is the first assumption to be anchored before version 1.0, "
           "using the NBP household wealth survey and a survey question on how much people hold above their emergency buffer."))
H.append(fig("c04_d1_tornado", "Range of the D1 result when one assumption changes. Source: amb research."))
H.append(h2("Myth and reality", "5.6"))
H.append(p("Media regularly report that Poles lose at least PLN 50 bn a year by keeping money in banks. That figure compares entire account balances with inflation, including money nobody would sensibly move, and ignores tax. "
           "Our result is about five times smaller because it counts only what can be recovered without changing risk. The direction, however, is right: deposits are the single largest lever in Polish household savings."))
H.append(box("D1 conclusion", f"Idle money is the largest loss in Polish household savings: about PLN {n(L['D1']['base'])} bn a year, and PLN {n(L['D1']['conservative'])} bn even in the conservative scenario. "
             "The barrier is not risk, since the alternative is equally safe, but habit and convenience."))

# ------------------------------------------------------------------ 06 D4
H.append(chapter("06", "D4 · PPK", f"PPK opt outs: PLN {n(L['D4']['base'])} bn a year",
                 "About 2.8 mn eligible employees give up money that employers and the state contribute for free."))
H.append(stats(("63.9%", "overall PPK participation (28 October 2026)"), ("37.5%", "participation in the public sector"), (f"PLN {d4['base']['loss_per_person_year']:,.0f}", "loss per person a year, base scenario")))
H.append(h2("How PPK works", "6.1"))
H.append(p("In the Employee Capital Plans (PPK) the employee contributes 2% of gross pay (0.5% on low incomes) and the employer 1.5%. The state adds a one off welcome payment of PLN 250 and an annual subsidy of PLN 240 when contributions in the year exceed a threshold. "
           "The employer contribution counts as the employee's taxable income.",
           "Participants can withdraw at any time. Before age 60, however, 30% of employer contributions goes to ZUS, state subsidies are forfeited and gains are taxed. "
           "Every four years employers automatically re-enrol those who opted out; the next re-enrolment takes place in 2027."))
H.append(h2("What we count and what we do not", "6.2"))
H.append(p("We count only the money an opted out employee loses unconditionally: the employer contribution after PIT and the state subsidy. The employee's own contribution <b>is not a loss</b>, because it stays in the employee's pocket. "
           "We also allow for part of the participants withdrawing before age 60 and losing part of the employer contributions and the subsidies."))
H.append(fig("c07_d4_waterfall", "Loss per person a year in the base scenario. Source: python -m engine.run_d4."))
H.append(h2("Results", "6.3"))
H.append(table(["Scenario", "Gross pay", "Employer net", "Loss per person", "Opted out", "PLN bn"],
               [[r["scenario"], f"PLN {r['gross_pay']:,.0f}", f"PLN {r['employer_net_year']:,.0f}", f"PLN {r['loss_per_person_year']:,.0f}", f"{n(r['opted_out_mn'])} mn", n(r["loss_bn"], 2)] for r in D["d4_table"]], hl=1))
H.append(p(f"In the base scenario an employee earning PLN 7,400 gross who opted out of PPK loses about PLN {d4['base']['loss_per_person_year']:,.0f} a year. With about 2.8 mn such employees, the total is PLN {n(L['D4']['base'])} bn a year. "
           "The result is robust: each of the four assumptions, varied on its own, keeps it within roughly PLN 2.6 bn to PLN 3.8 bn."))
H.append(h2("The widest gap is in the public sector", "6.4"))
H.append(fig("c06_d4_participation", "PPK participation by sector, October 2026. Source: PFR (as reported by analizy.pl)."))
H.append(p("Participation is 73% in the private sector and 37.5% in the public sector. It exceeds 93% in the largest firms (more than 1,000 employees) and stands at about 34% in firms with 10 to 49 staff. "
           "Paradoxically, the state as an employer is the least successful at persuading its own staff to join its own programme."))
H.append(box("D4 conclusion", "PPK is the easiest money to recover in the entire report: it requires no risk, no knowledge and no effort beyond not opting out. Many people opt out for sound reasons, for example because they need every zloty today. "
             "We therefore treat the total as a cost worth being aware of rather than as a mistake in every case."))

# ------------------------------------------------------------------ 07 D3
H.append(chapter("07", "D3 · IKE and IKZE", f"An unused tax shield: PLN {n(L['D3']['base'])} bn a year",
                 "Legal tax advantaged accounts that few people use, even though early withdrawal from an IKE costs nothing beyond the ordinary tax."))
H.append(stats(("about PLN 9 bn", "Belka tax a year (Ministry of Finance forecast for 2026)"), ("1.32 mn", "IKE accounts (June 2026) for more than 30 mn adults"), ("PLN 28,260", "IKE contribution limit in 2026")))
H.append(h2("How IKE and IKZE work", "7.1"))
H.append(p("The individual retirement account (IKE) exempts gains from the 19% Belka tax if the money is withdrawn after age 60 (or 55 for those entitled to early retirement). An IKE can hold deposits, Treasury bonds, funds and shares. "
           "Its key feature is that early withdrawal simply means paying the Belka tax, exactly as on an ordinary account. For long term money an IKE therefore has practically no tax downside.",
           "The individual retirement security account (IKZE) allows contributions to be deducted from taxable income; withdrawals after age 65 are taxed at a flat 10%. "
           "Contribution limits for 2026 are PLN 28,260 for IKE and PLN 11,304 for IKZE (PLN 16,956 for the self employed)."))
H.append(fig("c08_d3_belka", "Belka tax receipts by source. Source: Ministry of Finance (as reported by PAP and analizy.pl); 2026F = forecast."))
H.append(h2("Method", "7.2"))
H.append(p("We start from the Belka tax actually paid and ask what share of it could be avoided by holding the same savings in IKE or IKZE accounts. We do not count 100%, for two reasons: much of the interest comes from short term money that does not belong in an IKE, and annual limits quickly become binding for larger portfolios.",
           "We omit the IKZE income tax deduction (12% or 32% less the 10% flat tax at withdrawal), which understates the result. Because we start from the tax paid today, D3 does not overlap with D1."))
H.append(h2("Results", "7.3"))
H.append(table(["Scenario", "Savings share", "Investment share", "Savings bn", "Investments bn", "Total bn"],
               [[r["scenario"], f"{round(r['share_savings'] * 100)}%", f"{round(r['share_investments'] * 100)}%", n(r["savings_bn"], 2), n(r["investments_bn"], 2), n(r["total_bn"], 2)] for r in D["d3_table"]], hl=1))
H.append(p(f"In the base scenario 25% of the tax on savings and 40% of the tax on investments could be avoided, or about PLN {n(L['D3']['base'])} bn a year. "
           "As a capacity check, this implies sheltering about PLN 15 bn of gains a year, which under current limits requires several million regular contributors, several times more than today. "
           "That is achievable over the long term, though not from one year to the next."))
H.append(box("D3 conclusion", "The instrument is legal, free and carries no penalty for early withdrawal beyond the ordinary tax. That only about 1.3 mn people use it points to a knowledge problem rather than a supply problem. "
             "The proposed exemption from Belka tax for gains up to PLN 100,000 would narrow this gap from the state's side."))

# ------------------------------------------------------------------ 08 D2
H.append(chapter("08", "D2 · Fees", f"Fees in investment funds: PLN {n(L['D2']['base'])} bn a year",
                 "Outside equity funds, low cost index funds barely exist in Poland."))
H.append(stats(("about PLN 310 bn", "in non-dedicated retail funds (excluding PPK)"), ("0% to 2%", "passive share in bond and mixed funds"), ("0.88%", "average cost of short term bond funds (asset weighted)")))
H.append(h2("The fund market", "8.1"))
H.append(p("Assets of non-dedicated funds (excluding PPK, commodity and private market funds) grew from about PLN 160 bn in 2018 to more than PLN 300 bn in 2026. "
           "Short term bond funds grew fastest; for many savers they serve as an alternative to a term deposit."))
H.append(fig("c09_d2_assets", "Assets of non-dedicated funds by category. Source: IZFiA (RawData), amb research."))
H.append(h2("Passive funds barely exist", "8.2"))
H.append(fig("c10_d2_passive", "Passive funds as a share of assets, October 2026. Source: IZFiA, Passive flag."))
H.append(p(f"In equity funds the passive share is rising quickly, from 6.3% in June to {n(d2s['equity']['passive_share_pct'])}% in October 2026. It is {n(d2s['bond']['passive_share_pct'])}% in bond funds, "
           f"{n(d2s['short_bond']['passive_share_pct'])}% in short term bond funds and zero in mixed funds, even though these categories hold about PLN 250 bn."))
H.append(h2("Costs: a wide spread within one category", "8.3"))
H.append(p("For short term bond funds, the largest category at PLN 129 bn, we checked the costs of the 12 largest funds in their KID documents and cost tables. Together they hold 68.6% of the category, and their asset weighted average cost is 0.88% a year. "
           "For a similar product investors pay between 0.48% and 1.22% a year, a factor of 2.5. On PLN 100,000 the difference is about PLN 700 a year."))
H.append(fig("c11_d2_funds", "Ongoing charges of the 12 largest short term bond funds. Grey: estimated from the management fee. Source: KID documents and TFI cost tables."))
H.append(h2("Method and assumptions", "8.4"))
A = {(r["bucket"], r["scenario"]): r for r in D["d2_assumptions"]}
H.append(table(["Category", "Active cost (c / b / a)", "Alternative cost (c / b / a)", "Base gap, PLN bn"],
               [[NAMES[b], " / ".join(n(A[(b, s)]["active_cost_pct"], 2) for s in S), " / ".join(n(A[(b, s)]["alternative_cost_pct"], 2) for s in S), n(d2b[b]["base"], 2)]
                for b in ["equity", "mixed", "bond", "short_bond"]], cls="small"))
H.append(p("Active costs come from analizy.pl publications (management fees, TER and KID charges) and, for short term bond funds, from our own measurement on KID documents. Alternative costs are those of the cheapest index funds in each asset class. "
           "We assume active funds do not beat the market before fees on average. This is standard in the literature, but for Poland it will be tested in version 2 of the model."))
H.append(h2("Compounding", "8.5"))
H.append(fig("c12_d2_compound", "PLN 100,000 over 30 years: cost of 2.13% (average equity fund, TER 2023) versus 0.70% (index fund)."))
H.append(p("A cost difference of 1.4 pp looks small in any single year, but over 30 years it absorbs a third of the result: PLN 100,000 grows to PLN 625,000 at a cost of 0.70% and to only PLN 416,000 at 2.13%. The difference is PLN 209,000."))
H.append(box("D2 conclusion", f"The cost gap is about PLN {n(L['D2']['base'])} bn a year, within a range of PLN {n(L['D2']['conservative'])} bn to PLN {n(L['D2']['aggressive'])} bn. "
             "The largest opportunity lies not in equity, where passive funds are already growing, but in bond and mixed funds, where low cost products are almost absent."))

# ------------------------------------------------------------------ 09 D5
H.append(chapter("09", "D5 · Timing", f"Poor timing: about PLN {n(L['D5']['base'])} bn a year",
                 "A hypothesis that was not supported: Polish investors lose less on market timing than American investors."))
H.append(stats(("98", "months of flow data (September 2018 to October 2026)"), ("0.4 to 0.7 pp", "typical gap in equity and mixed funds"), ("about 1.2 pp", "the same measure in the United States (Morningstar)")))
H.append(h2("Question and method", "9.1"))
H.append(p("The investor gap is the difference between the return of the funds and the return earned by their clients. A fund may return 9% a year, but if clients buy after rallies and sell after declines, their money earns less. "
           "We measure fund returns with a time weighted return (TWR) and investor returns with a money weighted return (IRR) on the same flows.",
           "Monthly category returns are computed with the modified Dietz method from IZFiA data on assets and net flows. Funds that change category are assigned to their new category in the previous month as well, so a reclassification never registers as a gain or a loss. "
           "Liquidations and mergers are handled so that a payout is not counted as a loss. All of this is covered by unit tests."))
H.append(h2("Investor behaviour", "9.2"))
H.append(fig("c13_d5_flows", "Monthly net flows into equity funds. Source: IZFiA."))
H.append(p("The most visible episode is March 2020: equity funds fell 14.3% and investors withdrew a net PLN 1.1 bn. Funds then gained 11.1% in April and 12.7% in November. Money withdrawn at the bottom missed the recovery. "
           "Such episodes are rare, however: for most of the period flows are stable, and since 2025 they have been clearly positive."))
H.append(fig("c14_d5_index", "Cumulative return by fund category (TWR), August 2018 = 100. Source: IZFiA, amb research."))
H.append(h2("Results", "9.3"))
H.append(table(["Category", "TWR %", "IRR %", "Gap, full period", "Gap, 5y median", "5y range"],
               [[NAMES.get(k, k), n(r["twr_pct"], 2), n(r["irr_pct"], 2), n(r["gap_pp"], 2), n(r["gap_5y_median_pp"], 2), f"{n(r['gap_5y_min_pp'], 2)} to {n(r['gap_5y_max_pp'], 2)}"] for k, r in d5.items()], cls="small"))
H.append(p("The full period result depends on its end points: investors were withdrawing heavily from equities in September 2018, and assets were at their peak in October 2026. We therefore use the median of 39 rolling five year windows as the main measure. "
           "It is 0.65 pp a year in equity and mixed funds, 0.33 pp in bond funds and 0.08 pp in short term bond funds."))
H.append(fig("c15_d5_rolling", "Investor gap in rolling five year windows. Dashed line: the US measure. Source: amb research."))
H.append(h2("Robustness", "9.4"))
H.append(p("Because the data is monthly, we must assume when in the month money arrives. The base case assumes mid month. Assuming month end raises the full period equity gap to 0.44 pp; assuming month start lowers it to minus 0.06 pp. "
           "Mixed funds are stable under every assumption (0.41 to 0.60 pp). For that reason the equity result is always quoted with a range."))
H.append(box("D5 conclusion", f"Poor timing costs about PLN {n(L['D5']['base'])} bn a year, several times less than fees. A limitation: the analysis works at the category level, so it cannot see money switching between funds within a category, for example chasing a fashionable thematic fund. "
             "Version 2 will measure this at the level of individual funds and may reveal a larger gap."))

# ------------------------------------------------------------------ 10 to 12
H.append(chapter("10", "Synthesis", "Three groups of causes: idle money, unused programmes and market costs"))
H.append(fig("c16_groups", "Where the money goes, base scenario. Source: amb research."))
H.append(table(["Group", "Levers", "PLN bn", "Main barrier"], [
    ["Idle money", "D1 deposits", n(L["D1"]["base"]), "Habit and convenience rather than risk"],
    ["Unused programmes", "D3 IKE and IKZE, D4 PPK", n(L["D3"]["base"] + L["D4"]["base"]), "Knowledge of and trust in the programmes"],
    ["Market", "D2 fees, D5 timing", n(L["D2"]["base"] + L["D5"]["base"]), "Cost transparency and a lack of low cost products"]], align=["l", "l", "r", "l"]))
H.append(p("This pattern is the reverse of what most people fear. Fear of the stock market and of poor timing costs the least, while the largest losses arise from decisions that involve no risk at all: where to keep surplus cash, whether to stay in PPK and whether to open an IKE. "
           "That is good news, because these levers are the easiest to change."))

H.append(chapter("11", "Recommendations", "Three audiences, three different levers of change", "Recommendations concern product categories and policy design. They are not investment advice."))
for t, items in [("Households", ["Keep the liquidity buffer in a bank account and hold any surplus above it in State Treasury instruments carrying the same risk.", "Do not opt out of PPK without a specific reason: employer contributions and state subsidies are money without risk.",
                                 "Hold long term savings in an IKE or IKZE. Early withdrawal from an IKE costs no more than the ordinary tax.", "Before buying a fund, check the ongoing charges in its KID and compare them with other funds in the same category."]),
                 ("Industry: banks and fund managers", ["Offer low cost index funds outside equities, where they currently hold 0% to 2% of assets.", "Show costs in zloty on a typical amount, not only as percentages.", "Provide a simple path within banking apps from a current account to Treasury bonds and an IKE."]),
                 ("Government and regulators", ["Raise PPK participation in the public sector, currently 37.5% against 73% in the private sector; the 2027 re-enrolment is a natural opportunity.", "Simplify the IKE and create a single public place to compare fund costs.", "Make financial education in schools cover Treasury bonds, PPK and IKE."])]:
    H.append(h2(t)); H.append(ul(*items))

H.append(chapter("12", "Limitations", "What this draft does not yet know, and how we will address it before version 1.0"))
H.append(table(["Limitation", "Effect", "How we will address it"], [
    ["The movable share of current accounts (D1) is an assumption", "±PLN 3.6 bn", "NBP household wealth survey and a survey question"],
    ["The avoidable share of Belka tax (D3) is an assumption", "PLN 1.7 bn to PLN 4.4 bn", "Distribution of savings by portfolio size"],
    ["Wages of PPK opt outs (D4) are estimated", "PLN 2.6 bn to PLN 3.8 bn", "PFR data on the structure of participants"],
    ["Several figures come from the press (NBP, MF, PFR)", "Risk of an outdated figure", "Source files obtained directly"],
    ["D1 is a valuation as of today", "Unknown for other periods", "Rolling windows on the bond issue archive"],
    ["D2 assumes zero alpha", "May overstate D2", "Net returns versus benchmarks"],
    ["D5 is measured at category level", "Understates D5", "Flows for individual funds"],
    ["General equilibrium effects", "Gap at current behaviour", "Stated in the methodology"]], align=["l", "l", "l"]))
H.append(p("The last point deserves comment. If everyone moved money from accounts into bonds at once, banks would raise deposit rates and the State Treasury would change its issuance terms. "
           "Our figure therefore describes the gap at current behaviour, not an amount everyone could capture simultaneously."))

# ------------------------------------------------------------------ appendices
H.append(chapter("A", "Appendices", "Engine outputs, glossary and sources"))
H.append(h2("A1. Reproducing the results", "Appendix"))
H.append(table(["Command", "What it computes", "Base result"], [
    ["python -m engine.report", "Everything: results, 16 charts and report data", f"PLN {n(T['base'])} bn"],
    ["python -m engine.run_d1", "Deposits versus COI bonds", f"PLN {n(L['D1']['base'])} bn"], ["python -m engine.run_d2", "Cost gap and passive share", f"PLN {n(L['D2']['base'])} bn"],
    ["python -m engine.run_d3", "IKE and IKZE tax shield", f"PLN {n(L['D3']['base'])} bn"], ["python -m engine.run_d4", "Forgone PPK contributions", f"PLN {n(L['D4']['base'])} bn"],
    ["python -m engine.run_d5 [--fresh]", "TWR versus IRR; --fresh downloads IZFiA data again", f"PLN {n(L['D5']['base'])} bn"], ["python -m pytest", "29 unit tests", "all pass"]], align=["l", "l", "r"], cls="mono-first"))
H.append(h2("A2. Glossary"))
H.append(table(["Term", "Meaning"], [
    ["COI", "Four year inflation indexed retail Treasury bonds: a fixed rate in year one, then inflation plus a margin."], ["IKE / IKZE", "Individual retirement account / individual retirement security account: tax advantaged accounts with annual limits."],
    ["PPK", "Employee Capital Plans: contributions from employee, employer and the state."], ["Belka tax", "The 19% flat tax on capital gains and interest."],
    ["KID", "Key information document of a fund, including its ongoing charges."], ["TER", "Total expense ratio: a fund's total costs relative to its assets."],
    ["TWR", "Time weighted return: the fund's return, independent of payments in and out."], ["IRR", "Money weighted return: the return actually earned on investors' money."],
    ["Modified Dietz", "An approximate monthly return when flows occur during the month."], ["Like for like risk", "The report's principle: we compare only products that are at least as safe."]], align=["l", "l"]))
H.append(h2("A3. Sources"))
H.append(ul("IZFiA flow and asset data: izfa.pl/raporty", "NBP MIR interest rate statistics (stopy_proc_pl_srdW.xlsx); deposit volumes as reported by Parkiet", "GUS monthly consumer price indices since 1982",
            "obligacjeskarbowe.pl, four year COI bond offer, November 2026", "KNF, report on the financial situation of fund managers (TFI) in 2025",
            "analizy.pl publications on fund costs, investor returns and PPK", "KID documents and cost tables: PKO TFI, Pekao TFI, Millennium TFI, Erste TFI, ING TFI, PZU TFI",
            "MRPiPS notices on IKE and IKZE limits for 2026; Belka tax receipts: Ministry of Finance as reported by PAP, analizy.pl and xyz.pl"))
H.append('<div class="end"><img src="../assets/logo_black.png"><p class="kicker">[ AMB RESEARCH ]</p><p class="end-t">Less guessing. More understanding.</p><p class="small-grey">amb.watch · Report 01 · draft 0.2</p></div>')

# ------------------------------------------------------------------ style
CSS = """
@font-face { font-family: 'Switzer'; src: local('Switzer Light'), url('../fonts/Switzer-Light.otf'); font-weight: 300; }
@font-face { font-family: 'Switzer'; src: local('Switzer'), url('../fonts/Switzer-Regular.otf'); font-weight: 400; }
@font-face { font-family: 'Switzer'; src: local('Switzer Medium'), url('../fonts/Switzer-Medium.otf'); font-weight: 500; }
@font-face { font-family: 'Switzer'; src: local('Switzer Semibold'), url('../fonts/Switzer-Semibold.otf'); font-weight: 600; }
@font-face { font-family: 'Geist Mono'; src: url('../fonts/GeistMono-Regular.otf'); font-weight: 400; }
@font-face { font-family: 'Geist Mono'; src: url('../fonts/GeistMono-Medium.otf'); font-weight: 500; }
@page { size: A4; margin: 21mm 18mm 19mm 18mm;
  @top-left { content: "amb research"; font: 500 7pt 'Geist Mono'; color: #0a0a0a; }
  @top-right { content: "REPORT 01 · MONEY LEFT ON THE TABLE"; font: 400 7pt 'Geist Mono'; color: #737373; }
  @bottom-left { content: "DRAFT 0.2 · NOVEMBER 2026 · NOT INVESTMENT ADVICE"; font: 400 6.5pt 'Geist Mono'; color: #a1a1a1; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 500 7pt 'Geist Mono'; color: #0a0a0a; } }
@page cover { margin: 0; @top-left { content: none } @top-right { content: none } @bottom-left { content: none } @bottom-right { content: none } }
* { box-sizing: border-box; }
html { font-family: 'Switzer', 'Helvetica Neue', Arial, sans-serif; font-size: 9.6pt; line-height: 1.55; color: #262626; -webkit-print-color-adjust: exact; print-color-adjust: exact; text-align: left; }
body { margin: 0; }
p { margin: 0 0 7pt; orphans: 3; widows: 3; } b { font-weight: 600; color: #0a0a0a; }
.kicker { font-family: 'Geist Mono', monospace; font-weight: 500; font-size: 7.5pt; letter-spacing: .3px; color: #0055ff; text-transform: uppercase; margin: 0 0 4pt; }
.kicker.small { margin-top: 12pt; }
h1 { font-weight: 300; font-size: 25pt; line-height: 1.12; letter-spacing: -.6px; color: #0a0a0a; margin: 0 0 10pt; }
h2 { font-weight: 500; font-size: 12.5pt; line-height: 1.25; color: #0a0a0a; margin: 4pt 0 6pt; }
.h2g { break-inside: avoid; break-after: avoid; }
.lead { font-size: 12pt; line-height: 1.45; font-weight: 300; color: #404040; margin-bottom: 12pt; }
.chapter { break-before: page; padding-top: 4mm; margin-bottom: 8pt; }
.ch-num { font-family: 'Geist Mono', monospace; font-size: 40pt; line-height: 1; color: #e5e5e5; margin: 0 0 8pt; }
figure { margin: 6pt 0 10pt; break-inside: avoid; } figure img { max-width: 100%; max-height: 78mm; width: auto; display: block; }
figcaption { font-family: 'Geist Mono', monospace; font-size: 6.6pt; color: #737373; margin-top: 4pt; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 12pt; font-size: 8.4pt; break-inside: avoid; font-variant-numeric: tabular-nums; }
table.small { font-size: 7.8pt; }
th { background: #0a0a0a; color: #fff; font-family: 'Geist Mono', monospace; font-weight: 500; font-size: 6.6pt; text-transform: uppercase; letter-spacing: .3px; padding: 5pt 6pt; vertical-align: bottom; }
td { padding: 4.5pt 6pt; border-bottom: .6pt solid #e5e5e5; vertical-align: top; }
th.r, td.r { text-align: right; } th.l, td.l { text-align: left; }
tr.hl td { color: #0055ff; font-weight: 600; } tr.hl td b { color: #0055ff; }
table.mono-first td:first-child { font-family: 'Geist Mono', monospace; font-size: 7.6pt; }
ul, ol { margin: 0 0 9pt; padding-left: 14pt; } li { margin-bottom: 4pt; }
.findings li { margin-bottom: 7pt; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10pt; margin: 6pt 0 14pt; break-inside: avoid; }
.stat { background: #f5f5f5; padding: 10pt 11pt; }
.stat .v { font-size: 19pt; font-weight: 300; letter-spacing: -.4px; color: #0055ff; margin: 0 0 3pt; line-height: 1.1; }
.stat .l { font-size: 7.8pt; color: #525252; margin: 0; line-height: 1.35; }
.box { background: #f5f5f5; padding: 10pt 12pt 6pt; margin: 10pt 0 12pt; break-inside: avoid; }
.box .kicker.small { margin-top: 0; }
.cover { page: cover; height: 297mm; width: 210mm; background: #0a0a0a; color: #fff; position: relative; overflow: hidden; }
.cv-top { position: absolute; top: 18mm; left: 18mm; display: flex; align-items: center; gap: 8pt; font: 500 9pt 'Geist Mono'; }
.cv-logo { width: 22pt; height: 22pt; }
.cv-mark { position: absolute; width: 150mm; right: -40mm; top: 62mm; }
.cv-body { position: absolute; left: 18mm; bottom: 46mm; width: 130mm; }
.cv-title { color: #fff; font-size: 40pt; font-weight: 300; letter-spacing: -1.2px; line-height: 1.05; margin-bottom: 14pt; }
.cv-sub { font-size: 12.5pt; font-weight: 300; color: #a1a1a1; line-height: 1.45; }
.cover .kicker { color: #a1a1a1; }
.cv-foot { position: absolute; left: 18mm; right: 18mm; bottom: 16mm; display: flex; justify-content: space-between; font: 400 7pt 'Geist Mono'; color: #737373; }
.toc { break-before: page; }
.toc-list { list-style: none; padding: 0; margin: 10pt 0 20pt; }
.toc-list li { display: grid; grid-template-columns: 26pt 1fr; padding: 7pt 0; border-bottom: .6pt solid #e5e5e5; font-size: 11pt; margin: 0; }
.toc-list .n { font-family: 'Geist Mono', monospace; color: #0055ff; font-size: 9pt; padding-top: 2pt; }
.end { break-before: page; padding-top: 80mm; } .end img { width: 28pt; margin-bottom: 10pt; }
.end-t { font-size: 26pt; font-weight: 300; color: #0a0a0a; letter-spacing: -.6px; line-height: 1.1; }
.small-grey { font: 400 7.5pt 'Geist Mono'; color: #737373; }
sub { font-size: 70%; }
"""

html = f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>amb research · Report 01: Money left on the table</title><style>{CSS}</style></head><body>{"".join(H)}</body></html>'
out_html = HERE / "_report_01.html"
out_html.write_text(html)
out_pdf = HERE / "amb_research_report_01.pdf"
subprocess.run([find_chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files", f"--print-to-pdf={out_pdf}", out_html.as_uri()],
               check=True, capture_output=True, timeout=180)
out_html.unlink()
print("PDF:", out_pdf)
