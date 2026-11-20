// amb research · Report 01: presentation deck built from report/data.json (python -m engine.report).
//   cd report/deck && npm install && node build_deck.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("./theme");

const DIR = __dirname;
const D = JSON.parse(fs.readFileSync(path.join(DIR, "..", "data.json"), "utf8"));
const OUT = path.join(DIR, "amb_research_report_01.pptx");
const A = (f) => path.join(DIR, "..", "assets", f);

// ---------- amb.watch design tokens ----------
const HEX = { ink: "0A0A0A", ink3: "262626", ink4: "404040", g6: "525252", g5: "737373", g4: "A1A1A1", g3: "D4D4D4", g2: "E5E5E5", g1: "F5F5F5", white: "FFFFFF", blue: "0055FF", blueSoft: "80AAFF" };
const THEME = { name: "amb research", headFontFace: "Switzer", bodyFontFace: "Switzer",
  colors: { dk1: HEX.ink, lt1: HEX.white, dk2: HEX.g6, lt2: HEX.g1, accent1: HEX.blue, accent2: HEX.g5, accent3: HEX.g3, accent4: HEX.ink4, accent5: HEX.g4, accent6: HEX.g2, hlink: HEX.blue, folHlink: HEX.g6 } };
const MONO = "Geist Mono";
const N = (x, d = 1) => Number(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const L = Object.fromEntries(D.levers.map((l) => [l.key, l]));
const T = D.total, HS = D.d1_history_stats, TOR = D.d1_tornado;
const NAMES = { equity: "Equity", mixed: "Mixed", bond: "Bond", short_bond: "Short term bond", absolute_return: "Absolute return", total: "Total" };
const SC = ["conservative", "base", "aggressive"];
const d4b = D.d4_table.find((r) => r.scenario === "base");
const d1b = Object.fromEntries(D.d1_table.filter((r) => r.scenario === "base").map((r) => [r.deposit_type, r]));

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "amb research · Report 01: Money left on the table";
pres.author = "amb research"; pres.company = "amb";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ---------- grid: every content element snaps to these lines ----------
const W = 13.333, M = 0.6, CW = W - 2 * M, GAP = 0.3;
const TOP = 2.3, BOTTOM = 6.65, H = BOTTOM - TOP;           // content band
const COL = (k, of) => (CW - (of - 1) * GAP) / of * k + GAP * (k - 1); // width of k columns in an "of" column grid
const X = (i, of) => M + i * ((CW - (of - 1) * GAP) / of + GAP);      // left edge of column i
const CHART = { x: M, y: TOP, w: COL(7, 12), h: H };
const PX = X(7, 12), PW = COL(5, 12);

pres.defineSlideMaster({
  title: "AMB_DARK", background: { color: HEX.ink },
  objects: [
    { image: { x: M, y: 0.5, w: 0.42, h: 0.42, path: A("logo_white.png") } },
    { text: { text: "amb research", options: { x: M + 0.55, y: 0.52, w: 3, h: 0.38, fontFace: MONO, fontSize: 12, bold: true, color: C.background1, margin: 0, valign: "middle" } } },
    { placeholder: { options: { name: "kicker", type: "body", x: M, y: 1.75, w: 8, h: 0.4, fontFace: MONO, fontSize: 12, color: C.accent5, margin: 0, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.2, w: COL(8, 12), h: 2.75, fontSize: 44, color: C.background1, margin: 0, valign: "top", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 5.1, w: COL(8, 12), h: 1.3, fontSize: 18, color: C.accent5, margin: 0, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "AMB_CONTENT", background: { color: HEX.white }, margin: [0.6, 0.6, 0.8, 0.6],
  objects: [
    { image: { x: M, y: 0.32, w: 0.3, h: 0.3, path: A("logo_black.png") } },
    { text: { text: "amb research", options: { x: M + 0.4, y: 0.32, w: 3, h: 0.3, fontFace: MONO, fontSize: 10, bold: true, color: C.text1, margin: 0, valign: "middle" } } },
    { text: { text: "REPORT 01 · NOVEMBER 2026 · DRAFT 0.2", options: { x: W - M - 5, y: 0.32, w: 5, h: 0.3, fontFace: MONO, fontSize: 10, color: C.accent2, margin: 0, align: "right", valign: "middle" } } },
    { placeholder: { options: { name: "kicker", type: "body", x: M, y: 0.88, w: 9, h: 0.3, fontFace: MONO, fontSize: 11, color: C.accent1, margin: 0, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.18, w: CW, h: 0.95, fontSize: 28, color: C.text1, margin: 0, valign: "top", align: "left" }, text: "" } },
    { placeholder: { options: { name: "source", type: "body", x: M, y: 6.88, w: CW - 0.8, h: 0.4, fontSize: 10, color: C.accent2, margin: 0, valign: "top" }, text: "" } },
  ],
  slideNumber: { x: W - M - 0.6, y: 6.88, w: 0.6, h: 0.3, fontFace: MONO, fontSize: 10, color: HEX.g5, align: "right" },
});

// ---------- components ----------
let n = 0, curSection = "";
function section(t) { pres.addSection({ title: t }); curSection = t; }
function content(kicker, title, source, notes) {
  const s = pres.addSlide({ masterName: "AMB_CONTENT", sectionTitle: curSection });
  s.addText(kicker, { placeholder: "kicker" }); s.addText(title, { placeholder: "title" });
  if (source) s.addText(source, { placeholder: "source" });
  if (notes) s.addNotes(notes);
  n++; return s;
}
function dark(kicker, title, body, mark = "logo_blue.png") {
  const s = pres.addSlide({ masterName: "AMB_DARK", sectionTitle: curSection });
  s.addText(kicker, { placeholder: "kicker" }); s.addText(title, { placeholder: "title" });
  if (body) s.addText(body, { placeholder: "body" });
  if (mark) s.addImage({ path: A(mark), x: 9.3, y: 2.2, w: 3.4, h: 3.4, objectName: `mark-${n}` });
  n++; return s;
}
function divider(kicker, title, body, stats3) {
  const s = dark(kicker, title, body, null);
  stats3.forEach((st, i) => s.addText([{ text: st[0], options: { fontSize: 34, color: i === 0 ? C.accent1 : C.background1, breakLine: true } }, { text: st[1], options: { fontSize: 12, color: C.accent5 } }],
    { x: X(9, 12), y: 1.75 + i * 1.55, w: COL(3, 12), h: 1.35, margin: 0, valign: "top", isTextBox: true, objectName: `div-${n}-${i}` }));
  return s;
}
function panel(s, x, y, w, h, items, name, size = 12.5) {
  const runs = [];
  items.forEach((it, i) => {
    const last = i === items.length - 1;
    if (it.l) runs.push({ text: it.l, options: { fontFace: MONO, fontSize: 10.5, color: C.accent1, breakLine: !last, paraSpaceAfter: 4, paraSpaceBefore: i ? 6 : 0 } });
    else if (it.h) runs.push({ text: it.h, options: { fontSize: size + 1.5, bold: true, color: C.text1, breakLine: !last, paraSpaceAfter: 4 } });
    else if (it.b) runs.push({ text: it.b, options: { fontSize: size, color: C.text2, bullet: { indent: 14 }, breakLine: !last, paraSpaceAfter: 5 } });
    else runs.push({ text: it.p, options: { fontSize: size, color: C.text2, breakLine: !last, paraSpaceAfter: 6 } });
  });
  s.addText(runs, { x, y, w, h, valign: "top", margin: 0, isTextBox: true, objectName: name, lineSpacingMultiple: 1.05 });
}
function stat(s, x, y, w, value, label, color, name, size = 40) {
  s.addText(value, { x, y, w, h: size / 58, fontSize: size, color: color || C.text1, margin: 0, valign: "bottom", isTextBox: true, objectName: name + "-v" });
  s.addText(label, { x, y: y + size / 58 + 0.06, w, h: 0.62, fontSize: 12, color: C.text2, margin: 0, valign: "top", isTextBox: true, objectName: name + "-l" });
}
function card(s, x, y, w, h, num, title, text, name, size = 12.5) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.background2 }, line: { type: "none" }, objectName: name + "-bg" });
  const items = []; if (num) items.push({ l: num }); if (title) items.push({ h: title });
  (Array.isArray(text) ? text : [text]).forEach((t) => items.push(t.startsWith("• ") ? { b: t.slice(2) } : { p: t }));
  panel(s, x + 0.25, y + 0.22, w - 0.5, h - 0.4, items, name, size);
}
function cards(s, list, of, y = TOP, h = H, size = 12.5, name = "c") {
  list.forEach((c, i) => card(s, X(i * (12 / of), 12), y, COL(12 / of, 12), h, c[0], c[1], c[2], `${name}-${n}-${i}`, size));
}
function grid(s, list, cols, rows, size = 12.5) {
  const h = (H - (rows - 1) * GAP) / rows;
  list.forEach((c, i) => card(s, X((i % cols) * (12 / cols), 12), TOP + Math.floor(i / cols) * (h + GAP), COL(12 / cols, 12), h, c[0], c[1], c[2], `g-${n}-${i}`, size));
}
function conclusion(value, sub, items) {
  const s = this;
  stat(s, M, TOP + 0.1, COL(5, 12), value, sub, C.accent1, `end-${n}`, 60);
  panel(s, X(6, 12), TOP + 0.1, COL(6, 12), H - 0.1, items, `end-t-${n}`);
}
const TH = (t, x = {}) => ({ text: t, options: { bold: true, color: HEX.white, fill: { color: HEX.ink }, fontFace: MONO, fontSize: 9.5, valign: "middle", ...x } });
const TD = (t, x = {}) => ({ text: String(t), options: { color: HEX.ink3, fontSize: 11, valign: "middle", ...x } });
const R = { align: "right" };
function table(s, x, y, w, rows, colW, name, rowH = 0.34) { s.addTable(rows, { x, y, w, colW, rowH, border: { type: "solid", pt: 0.75, color: HEX.g2 }, fontFace: "Switzer", margin: [3, 6, 3, 6], objectName: name }); }
const AX = { catAxisLabelColor: HEX.g6, valAxisLabelColor: HEX.g6, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, dataLabelFontFace: "+mn-lt", dataLabelFontSize: 10, dataLabelColor: HEX.ink4,
  valGridLine: { color: HEX.g2, size: 0.75 }, catGridLine: { style: "none" }, titleFontFace: "+mn-lt", titleFontSize: 12, titleColor: HEX.ink, legendFontFace: "+mn-lt", legendFontSize: 10, legendColor: HEX.g6, valAxisLineShow: false };
const end = (kicker, title, value, sub, items) => { const s = content(kicker, title, null); conclusion.call(s, value, sub, items); return s; };

// ======================================================================
section("Introduction");
{ const s = dark("[ REPORT 01 ]", "Money left on the table", "How much Polish households lose each year through the way they save, and how much they could recover without taking on additional risk", null);
  s.addImage({ path: A("logo_blue.png"), x: 8.6, y: 1.35, w: 4.6, h: 4.6, objectName: "cover-mark" });
  s.addText("DRAFT 0.2 · 19 NOVEMBER 2026 · DATA: NBP · GUS · IZFiA · KNF · MF · PFR", { x: M, y: 6.75, w: 9, h: 0.3, fontFace: MONO, fontSize: 10, color: C.accent5, margin: 0, isTextBox: true, objectName: "cover-meta" });
  s.addNotes("Report 01 of the amb research series. Every figure comes from the open source engine (python -m engine.report). This report is not investment advice."); }

{ const s = content("[ 00 · ABOUT THIS REPORT ]", "One question: how much do Polish savers really lose, and where exactly", "This report describes product categories and public data. It is not investment advice.");
  cards(s, [["01 · QUESTION", "What we measure", ["The annual amount, in PLN bn, that Polish households lose compared with a simple, widely available alternative carrying the same level of risk.", "And which of five levers accounts for the largest share of that loss."]],
    ["02 · SCOPE", "Five levers", ["• D1 deposits instead of Treasury bonds", "• D2 fees in investment funds", "• D3 unused IKE and IKZE accounts", "• D4 opting out of PPK", "• D5 buying and selling at the wrong time"]],
    ["03 · METHOD", "Like for like risk", ["We compare only products that are equally safe for the saver. A deposit versus equities is a different choice, not a loss.", "Every figure comes in three scenarios: conservative, base and aggressive."]],
    ["04 · DATA", "Public sources only", ["NBP, GUS, IZFiA, KNF, the Ministry of Finance, PFR and fund KID documents.", "About 93,000 fund asset records, 98 months of flows and 261 months of deposit rates. Code and 29 tests are open source."]]], 4); }

{ const s = content("[ 00 · AGENDA ]", "Structure: findings, method, five levers and synthesis", null);
  grid(s, [["01", "Key findings", "The result, six findings, myth and reality"], ["02", "Method and data", "Principles, formulas, sources and quality controls"], ["03", "D1 · Deposits", `PLN ${N(L.D1.base)} bn a year`],
    ["04", "D4 · PPK", `PLN ${N(L.D4.base)} bn a year`], ["05", "D3 · IKE and IKZE", `PLN ${N(L.D3.base)} bn a year`], ["06", "D2 · Fees", `PLN ${N(L.D2.base)} bn a year`],
    ["07", "D5 · Timing", `PLN ${N(L.D5.base)} bn a year`], ["08", "Synthesis and recommendations", "Three groups of causes, three audiences"], ["09", "Limitations and appendix", "Path to version 1.0, engine outputs"]], 3, 3, 13); }

section("Findings");
{ const s = content("[ 01 · SUMMARY ]", "Polish households leave about PLN 18 bn on the table every year, mostly through idle money", "Source: amb research (python -m engine.report) on data from NBP, GUS, IZFiA, KNF, MF and PFR.");
  stat(s, M, TOP + 0.05, COL(4, 12), `PLN ${N(T.base)} bn`, `a year in the base scenario · range PLN ${N(T.conservative)} bn to ${N(T.aggressive)} bn · about 0.5% of GDP · twice the entire Belka tax take`, C.accent1, "sum-hero", 40);
  panel(s, X(4, 12), TOP + 0.05, COL(8, 12), 2.85, [{ l: "THREE FINDINGS" }, { h: "1. Idle money costs the most" }, { p: `Current accounts pay an average of 0.49% while inflation runs at 3.5%. Moving part of these balances into Treasury bonds is worth about PLN ${N(L.D1.base)} bn a year.` },
    { h: "2. Free public programmes go unused" }, { p: `PPK opt outs and unused IKE and IKZE accounts together cost about PLN ${N(L.D4.base + L.D3.base)} bn a year, with no risk and no effort required to recover it.` },
    { h: "3. Poor market timing costs the least" }, { p: `Fund fees cost about PLN ${N(L.D2.base)} bn and poor timing only about PLN ${N(L.D5.base)} bn a year, less than in the United States.` }], "sum-f", 12.5);
  D.levers.forEach((l, i) => { const x = M + i * ((CW - 4 * 0.25) / 5 + 0.25), w = (CW - 4 * 0.25) / 5;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 5.4, w, h: 1.25, fill: { color: C.background2 }, line: { type: "none" }, objectName: `sl-${i}-bg` });
    s.addText([{ text: l.key, options: { fontFace: MONO, fontSize: 10, color: C.accent1, breakLine: true } }, { text: `PLN ${N(l.base)} bn`, options: { fontSize: 21, color: C.text1, breakLine: true } }, { text: l.label, options: { fontSize: 11, color: C.text2 } }],
      { x: x + 0.18, y: 5.5, w: w - 0.36, h: 1.05, margin: 0, valign: "top", isTextBox: true, objectName: `sl-${i}` }); }); }

{ const s = content("[ 01 · SIX FINDINGS ]", "Six findings worth remembering", "Details and scenarios for every figure follow on later slides.");
  grid(s, [["01", `Deposits: PLN ${N(L.D1.base)} bn`, `PLN 1.1 trn sits in current accounts paying 0.49%. Since 2005, current accounts have beaten inflation in only ${N(HS.current_above_cpi_pct)}% of months.`],
    ["02", `PPK: PLN ${N(L.D4.base)} bn`, "About 2.8 mn eligible employees are outside PPK. Participation is 37.5% in the public sector against 73% in the private sector."],
    ["03", `IKE and IKZE: PLN ${N(L.D3.base)} bn`, "About 1.3 mn IKE accounts for more than 30 mn adults, although early withdrawal costs no more than the ordinary tax."],
    ["04", `Fees: PLN ${N(L.D2.base)} bn`, "Outside equity, low cost index funds barely exist: they hold 0% to 2% of bond and mixed fund assets."],
    ["05", `Timing: PLN ${N(L.D5.base)} bn`, "The investor gap is typically 0.4 to 0.7 pp a year, below about 1.2 pp in the United States. The hypothesis of large timing losses is not supported."],
    ["06", "Myth: 50 versus 9", "The popular estimate of losses on deposits is about five times too high, but it points in the right direction."]], 3, 2); }

{ const s = content("[ 01 · FIVE LEVERS ]", "Deposits account for over half of the loss, and the ranking holds in every scenario", "Source: amb research, data/processed/d1 to d5 output files.");
  const labels = D.levers.map((l) => `${l.key} ${l.label}`);
  s.addChart(pres.charts.BAR, SC.map((k, i) => ({ name: ["Conservative", "Base", "Aggressive"][i], labels, values: D.levers.map((l) => l[k]) })),
    { ...CHART, barDir: "bar", barGrouping: "clustered", barGapWidthPct: 60, chartColors: [HEX.g3, HEX.blue, HEX.g5], catAxisOrientation: "maxMin", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
      showLegend: true, legendPos: "b", showTitle: true, title: "Annual gap versus an alternative with the same risk, PLN bn", valAxisMaxVal: 20, ...AX, objectName: "levers" });
  panel(s, PX, TOP, PW, H, [{ l: "HOW TO READ" }, { p: `The blue bar is the base scenario; grey bars show the conservative and aggressive scenarios. Totals: PLN ${N(T.conservative)} bn, ${N(T.base)} bn and ${N(T.aggressive)} bn a year.` },
    { l: "WHAT STANDS OUT" }, { b: `D1 is the largest lever even in the conservative scenario (PLN ${N(L.D1.conservative)} bn).` }, { b: `D3 and D4, the unused programmes, add up to about PLN ${N(L.D3.base + L.D4.base)} bn.` },
    { b: "D5 is barely visible: poor timing is the smallest problem for Polish savers." }, { l: "IMPLICATION" }, { p: "The biggest gains require no market risk at all, only different decisions about where money sits." }], "levers-t"); }

{ const s = content("[ 01 · MYTH AND REALITY ]", "Deposit losses are real, but about five times smaller than the headlines suggest", "Source: Superbiz (estimate of at least PLN 50 bn based on NBP and PFR data); D1 amb research, base scenario, range PLN 2.8 bn to 18.2 bn.");
  stat(s, M, TOP + 0.1, COL(3, 12), "~PLN 50 bn", "media estimate: entire account balances compared with inflation", C.accent2, "m-a", 32);
  stat(s, X(3, 12), TOP + 0.1, COL(3, 12), `PLN ${N(L.D1.base)} bn`, "amb research: movable money, versus Treasury bonds, after tax", C.accent1, "m-b", 32);
  panel(s, X(7, 12), TOP + 0.1, COL(5, 12), H - 0.1, [{ l: "THREE CORRECTIONS" }, { b: "Count only money that can move. Transaction balances and liquidity buffers stay in the account." },
    { b: "Compare with an alternative of the same risk (COI bonds), not with inflation in the abstract." }, { b: "Apply the Belka tax on both sides of the comparison." },
    { l: "WHY IT MATTERS" }, { p: "We do not claim there is no loss. We measure what can be recovered without taking on more risk, a figure that holds up under scrutiny." }], "m-t");
  [["Entire balances versus inflation", "~PLN 50 bn"], ["Movable share of accounts and deposits", "15% and 70%"], ["Versus COI bonds, after tax", `PLN ${N(L.D1.base)} bn`]].forEach((st, i) => {
    const x = X(i * 2, 12), w = COL(2, 12);
    s.addShape(pres.shapes.RECTANGLE, { x, y: 4.85, w, h: 1.8, fill: { color: i === 2 ? C.accent1 : C.background2 }, line: { type: "none" }, objectName: `ms-${i}-bg` });
    s.addText([{ text: `0${i + 1}`, options: { fontFace: MONO, fontSize: 10, color: i === 2 ? C.background1 : C.accent1, breakLine: true } }, { text: st[0], options: { fontSize: 12, color: i === 2 ? C.background1 : C.text2, breakLine: true } }, { text: st[1], options: { fontSize: 16, bold: true, color: i === 2 ? C.background1 : C.text1 } }],
      { x: x + 0.18, y: 4.97, w: w - 0.36, h: 1.56, margin: 0, valign: "top", isTextBox: true, objectName: `ms-${i}` }); }); }

section("Method and data");
{ const s = content("[ 02 · METHODOLOGY ]", "Four principles separate this report from yet another article about saving", "Code: engine/models/ (deposits.py, fee_drag.py, tax_wrappers.py, ppk.py, investor_gap.py).");
  grid(s, [["01 · LIKE FOR LIKE RISK", "Only equally safe products are compared", "A deposit is compared with a Treasury bond, an active bond fund with an index fund, an ordinary account with the same instrument inside an IKE. The result is money recoverable without changing risk."],
    ["02 · THREE SCENARIOS", "Conservative, base and aggressive", "Headlines use the base scenario and always quote the range. For key assumptions we show how far the result moves when one assumption changes and the rest stay at base."],
    ["03 · NO DOUBLE COUNTING", "Levers concern different money", "D1 covers deposits, D4 wages, D2 and D5 funds but different effects. D3 starts from the tax paid today, so it does not overlap with D1 and is conservative."],
    ["04 · REPRODUCIBILITY", "One command, the whole report", "python -m engine.report reproduces every figure, chart and the data behind this deck. Twenty nine unit tests cover the logic of the models."]], 2, 2); }

{ const s = content("[ 02 · FORMULAS ]", "Each lever rests on one simple, transparent formula", "All assumptions and their sources are documented in the engine; outputs in data/processed/.");
  table(s, M, TOP, CW, [[TH("LEVER"), TH("TODAY"), TH("ALTERNATIVE"), TH("ANNUAL GAP"), TH("KEY ASSUMPTION")],
    [TD("D1 Deposits", { bold: true }), TD("Current accounts, term deposits"), TD("COI Treasury bonds"), TD("deposits × movable share × (COI − deposit rate) × 0.81 − redemption cost"), TD("Movable share of current accounts")],
    [TD("D2 Fees", { bold: true }), TD("Active funds"), TD("Index fund"), TD("active fund assets × (active cost − alternative cost)"), TD("Zero alpha before fees")],
    [TD("D3 Tax", { bold: true }), TD("Ordinary account"), TD("IKE or IKZE"), TD("Belka tax × avoidable share"), TD("Share within annual limits")],
    [TD("D4 PPK", { bold: true }), TD("Opting out of PPK"), TD("Staying in PPK"), TD("employees outside PPK × (1.5% of pay × 12 × 0.88 + PLN 240)"), TD("Wages of those who opt out")],
    [TD("D5 Timing", { bold: true }), TD("Investor return (IRR)"), TD("Fund return (TWR)"), TD("TWR − IRR on IZFiA monthly flows"), TD("Timing of flows within a month")]], [1.5, 2.05, 1.8, 4.3, 2.483], "formulas", 0.6);
  panel(s, M, 5.75, CW, 0.9, [{ l: "NOTATION" }, { p: "All rates in % a year. 0.81 = 1 minus the 19% Belka tax. TWR = time weighted return; IRR = money weighted return. Each lever is computed in three scenarios." }], "f-note", 12); }

{ const s = content("[ 02 · DATA ]", "All data is public, and every source carries its download date", "Raw files: data/raw/ (manifests with URL, download time and SHA-256). Items marked as reported by the press are to be confirmed before version 1.0.");
  const r = (a, b, c, d, e) => [TD(a, { bold: true }), TD(b), TD(c), TD(d), TD(e)];
  table(s, M, TOP - 0.05, CW, [[TH("SOURCE"), TH("CONTENT"), TH("PERIOD"), TH("HOW OBTAINED"), TH("USED IN")],
    r("IZFiA, flow data", "Net flows by fund category", "Sep 2018 to Oct 2026 (98 files)", "Automated, 3 formats", "D5"), r("IZFiA, asset data", "NAV of every fund, passive flag", "Dec 2017 to Oct 2026 (~93k rows)", "Automated, RawData", "D2, D5"),
    r("NBP, MIR statistics", "Household deposit rates", "Jan 2005 to Sep 2026", "xlsx from NBP server", "D1"), r("NBP (via Parkiet)", "Current and term deposits", "Jun 2026", "Press, to be confirmed", "D1"),
    r("GUS", "Monthly CPI", "1982 to Oct 2026", "CSV file", "D1"), r("obligacjeskarbowe.pl", "COI terms, redemption fee", "Nov 2026", "Offer page", "D1"),
    r("Fund KIDs, TFI cost tables", "Ongoing charges of 12 funds", "2021 to 2026", "PDF documents", "D2"), r("analizy.pl", "Average costs by category", "2023 to 2025", "Publications", "D2"),
    r("KNF", "Fund manager revenue PLN 4.69 bn", "2025", "PDF report", "D2 check"), r("Ministry of Finance (press)", "Belka tax receipts", "2024 to 2026F", "Press, to be confirmed", "D3"),
    r("MRPiPS", "IKE and IKZE limits", "2026", "Official notices", "D3"), r("PFR (analizy.pl), GUS", "PPK participation, wages", "Sep to Oct 2026", "Press, to be confirmed", "D4")], [2.4, 3.35, 2.6, 2.75, 1.033], "sources", 0.33); }

{ const s = content("[ 02 · DATA QUALITY ]", "Four controls that make the figures trustworthy", "Code: engine/data/izfia_parse.py; reconciliation and checks documented in the PDF report, chapter 4.");
  grid(s, [["01 · FUND ASSETS", "Reconciled with IZFiA totals: median 1.000", "Assets built up from individual funds were compared with the totals IZFiA publishes. 56 of 67 months fall within ±1%."],
    ["02 · DOUBLE COUNTING", "An error found and fixed", "The first version identified funds by name, so name changes between files double counted assets by up to 50%. Switching to the fund code removed the problem."],
    ["03 · PPK IN FUND DATA", "Excluded from the fund analysis", "Until March 2021 IZFiA reported PPK within Mixed Other, separately thereafter. Both are excluded: PPK contributions come from payroll, not from investor decisions."],
    ["04 · CROSS CHECK", "Fund manager revenue versus the cost gap", "Fund managers earned PLN 4.69 bn from managing funds in 2025 (KNF). The D2 cost gap of PLN 2.2 bn is about half of that, a consistent order of magnitude."]], 2, 2); }

// ---------------- D1
section("D1 · Deposits");
divider("[ 03 · D1 · DEPOSITS ]", "Deposits instead of Treasury bonds", `The largest lever: PLN ${N(L.D1.base)} bn a year in the base scenario, within a range of PLN ${N(L.D1.conservative)} bn to ${N(L.D1.aggressive)} bn.`,
  [["PLN 1.1 trn", "in household current accounts"], ["0.49%", "average rate on those accounts"], [`${N(HS.current_above_cpi_pct)}%`, "of months since 2005 in which accounts beat inflation"]]);

{ const h = D.d1_history, lab = h.map((r) => r.month);
  const s = content("[ 03 · D1 · HISTORY ]", `Since 2005, current accounts have paid more than inflation in only ${N(HS.current_above_cpi_pct)}% of months`, `Source: NBP MIR statistics (rates on outstanding stock), ${HS.start} to ${HS.end}; GUS CPI (same month previous year = 100); amb research.`);
  s.addChart(pres.charts.LINE, [{ name: "CPI inflation y/y", labels: lab, values: h.map((r) => r.cpi ?? 0) }, { name: "Term deposits", labels: lab, values: h.map((r) => r.term) }, { name: "Current accounts", labels: lab, values: h.map((r) => r.current) }],
    { ...CHART, chartColors: [HEX.g3, HEX.g5, HEX.blue], lineSize: 2, lineDataSymbol: "none", showLegend: true, legendPos: "b", showTitle: true, title: "Household deposit rates and inflation, % a year", catAxisLabelFrequency: 24, ...AX, objectName: "hist" });
  panel(s, PX, TOP, PW, H, [{ l: `${HS.months} MONTHS OF DATA` }, { p: `Averages: current accounts ${N(HS.current_avg, 2)}%, term deposits ${N(HS.term_avg, 2)}%, inflation ${N(HS.cpi_avg, 2)}%.` },
    { p: `Term deposits beat inflation in ${N(HS.term_above_cpi_pct)}% of months; current accounts in ${N(HS.current_above_cpi_pct)}%.` }, { l: "WHAT IT MEANS" },
    { p: `A zloty held in a current account throughout the period lost about ${N(Math.abs(HS.real_current_cum_pct), 0)}% of its purchasing power after tax.` }, { p: "This is not a recent anomaly but the norm for two decades, interrupted only briefly in 2008 and 2023." }], "hist-t"); }

{ const Rt = D.d1_rates, lab = Object.keys(Rt);
  const s = content("[ 03 · D1 · TODAY ]", "Current accounts pay 0.49%, while a Treasury bond with the same risk pays about 4.6% a year", "Source: NBP MIR (outstanding stock), Sep 2026; GUS CPI, Oct 2026; obligacjeskarbowe.pl, COI offer Nov 2026: 4.75% in year one, then inflation plus 1.5% (base inflation 3%).");
  s.addChart(pres.charts.BAR, [{ name: "% a year", labels: lab, values: lab.map((k) => Rt[k]) }], { ...CHART, barDir: "col", barGapWidthPct: 70, chartColors: [HEX.blue], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.00"%"', showLegend: false, showTitle: true, title: "Interest rates and inflation, % a year", valAxisMinVal: 0, valAxisMaxVal: 5, ...AX, objectName: "rates" });
  panel(s, PX, TOP, PW, H, [{ l: "AFTER TAX DIFFERENCE" }, { h: `Current account to COI: about ${N(d1b.current.gap_after_tax_pp)} pp a year` }, { p: "On every PLN 10,000 moved out of a current account, about PLN 320 a year more after tax." },
    { h: `Term deposit to COI: about ${N(d1b.term.gap_after_tax_pp)} pp a year` }, { p: "On every PLN 10,000, about PLN 140 a year more after tax." }, { l: "NOTE" },
    { p: "COI pays a fixed rate only in the first year; years two to four depend on inflation. The scenarios assume 2%, 3% and 4%." }], "rates-t"); }

{ const s = content("[ 03 · D1 · THE ALTERNATIVE ]", "COI bonds: State Treasury risk, inflation protection and limited liquidity", "Source: obligacjeskarbowe.pl, COI offer and early redemption terms (Nov 2026); Bank Guarantee Fund (BFG).");
  cards(s, [["01 · HOW IT WORKS", "COI mechanics", ["• Four year bond priced at PLN 100", "• 4.75% in year one (November 2026 offer)", "• Years two to four: inflation plus a 1.50% margin", "• Interest paid annually", "• 19% Belka tax on interest"]],
    ["02 · RISK", "The same shelf as a deposit", ["The issuer is the State Treasury. Credit risk is no higher than that of a deposit covered by the Bank Guarantee Fund.", "From year two the coupon rises with inflation, which protects real value."]],
    ["03 · CONSTRAINT", "Liquidity", ["Early redemption costs PLN 2 per PLN 100 bond (since September 2024), and the money returns within a few days.", "COI bonds therefore do not replace a transaction account or a liquidity buffer, which is why the model moves only part of deposits."]]], 3); }

{ const s = content("[ 03 · D1 · ASSUMPTIONS ]", "Five assumptions in three scenarios, from cautious to optimistic", "Model: engine/models/deposits.py. CPI was 3.5% year on year in October 2026 and ranged from 2.1% to 4.1% over the past year.");
  table(s, M, TOP, CW, [[TH("ASSUMPTION"), TH("CONSERVATIVE", R), TH("BASE", R), TH("AGGRESSIVE", R), TH("RATIONALE")],
    [TD("Inflation in years 2 to 4"), TD("2.0%", R), TD("3.0%", { ...R, bold: true }), TD("4.0%", R), TD("Currently 3.5%; 2.1% to 4.1% over the past year")],
    [TD("Movable share of current accounts"), TD("5%", R), TD("15%", { ...R, bold: true }), TD("25%", R), TD("The rest is transactional money and buffers")],
    [TD("Movable share of term deposits"), TD("50%", R), TD("70%", { ...R, bold: true }), TD("90%", R), TD("Term deposits are already set aside")],
    [TD("Early redemptions"), TD("30%", R), TD("15%", { ...R, bold: true }), TD("0%", R), TD("PLN 2 per bond, spread over four years")],
    [TD("Belka tax"), TD("19%", R), TD("19%", { ...R, bold: true }), TD("19%", R), TD("Applied on both sides of the comparison")]], [3.6, 1.6, 1.4, 1.5, 4.033], "d1a", 0.52);
  panel(s, M, 5.65, CW, 1.0, [{ l: "FORMULA" }, { p: "gap = deposits × movable share × (r COI − r deposit) × (1 − 19%) − redemption cost;   r COI = (4.75% + 3 × (inflation + 1.5%)) / 4" }], "d1f", 12); }

{ const s = content("[ 03 · D1 · ENGINE OUTPUT ]", `PLN ${N(L.D1.base)} bn a year in the base case: most of it from current accounts, the rest from term deposits`, "Output: python -m engine.run_d1 → data/processed/d1_deposits.csv.");
  const piv = { current: {}, term: {} }; D.d1_table.forEach((r) => (piv[r.deposit_type][r.scenario] = r.gap_bn));
  s.addChart(pres.charts.BAR, [{ name: "Current accounts", labels: SC, values: SC.map((k) => piv.current[k]) }, { name: "Term deposits", labels: SC, values: SC.map((k) => piv.term[k]) }],
    { x: M, y: TOP, w: COL(5, 12), h: H, barDir: "col", barGrouping: "stacked", barGapWidthPct: 60, chartColors: [HEX.blue, HEX.g4], showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "0.0", showLegend: true, legendPos: "b", showTitle: true, title: "D1 gap by scenario, PLN bn", ...AX, dataLabelColor: HEX.white, objectName: "d1s" });
  const rows = [[TH("SCENARIO"), TH("TYPE"), TH("COI", R), TH("DEP.", R), TH("GAP PP", R), TH("SHARE", R), TH("PLN BN", R)]];
  D.d1_table.forEach((r) => { const o = r.scenario === "base" ? { bold: true, color: HEX.blue } : {};
    rows.push([TD(r.scenario, o), TD(r.deposit_type, o), TD(N(r.coi_rate_pct, 2), { ...R, ...o }), TD(N(r.deposit_rate_pct, 2), { ...R, ...o }), TD(N(r.gap_after_tax_pp, 2), { ...R, ...o }), TD(`${Math.round(r.movable_share * 100)}%`, { ...R, ...o }), TD(N(r.gap_bn, 2), { ...R, ...o })]); });
  table(s, X(5, 12), TOP, COL(7, 12), rows, [1.45, 0.95, 0.75, 0.75, 0.9, 0.75, 0.825], "d1t", 0.4);
  panel(s, X(5, 12), 5.35, COL(7, 12), 1.3, [{ l: "TAKEAWAY" }, { p: `Even the conservative case, with 5% of current accounts and 50% of term deposits, yields PLN ${N(L.D1.conservative)} bn a year: more than the entire fund cost gap in the base case.` }], "d1r", 12.5); }

{ const lab = TOR.rows.map((r) => r.label);
  const s = content("[ 03 · D1 · SENSITIVITY ]", "The single most important assumption: how much of current account money can realistically move", "amb research: one assumption varied at a time, all others at the base scenario.");
  s.addChart(pres.charts.BAR, [{ name: "Low", labels: lab, values: TOR.rows.map((r) => r.lo) }, { name: "Range", labels: lab, values: TOR.rows.map((r) => +(r.hi - r.lo).toFixed(2)) }],
    { ...CHART, barDir: "bar", barGrouping: "stacked", barGapWidthPct: 50, chartColors: [HEX.white, HEX.blue], catAxisOrientation: "maxMin", showValue: false, showLegend: false, showTitle: true, title: "Range of the D1 result, PLN bn a year", valAxisMinVal: 0, valAxisMaxVal: 14, ...AX, objectName: "tor" });
  const rows = [[TH("ASSUMPTION"), TH("LOW", R), TH("HIGH", R), TH("RANGE", R)]];
  TOR.rows.forEach((r) => rows.push([TD(r.label), TD(N(r.lo), R), TD(N(r.hi), R), TD(N(r.hi - r.lo), { ...R, bold: true })]));
  table(s, PX, TOP, PW, rows, [2.4, 0.6, 0.6, 0.683], "tort", 0.42);
  panel(s, PX, 4.6, PW, 2.05, [{ l: "ANCHOR BEFORE VERSION 1.0" }, { p: `The movable share of current accounts shifts the result by PLN ${N(TOR.rows[0].hi - TOR.rows[0].lo)} bn, more than all other assumptions combined.` }, { p: "It will be anchored in the NBP household wealth survey and a survey question on money held above the emergency buffer." }], "tor-t", 12); }

end("[ 03 · D1 · CONCLUSION ]", "Idle money is the largest loss in Polish household savings", `PLN ${N(L.D1.base)} bn`, `a year in the base scenario · range PLN ${N(L.D1.conservative)} bn to ${N(L.D1.aggressive)} bn`,
  [{ l: "BARRIER" }, { h: "Habit and convenience, not risk" }, { p: "The alternative is equally safe, yet most surplus cash sits in accounts paying 0.49%." }, { l: "WHO SHOULD ACT" },
    { b: "Households: separate the liquidity buffer from the surplus." }, { b: "Banks: offer a simple path from the account to Treasury bonds within the app." }, { b: "Government: use retail bonds as a vehicle for financial education." }]);

// ---------------- D4
section("D4 · PPK");
divider("[ 04 · D4 · PPK ]", "Opting out of PPK", `About 2.8 mn eligible employees give up money from employers and the state: PLN ${N(L.D4.base)} bn a year in the base scenario.`,
  [["63.9%", "overall PPK participation (28 Oct 2026)"], ["37.5%", "participation in the public sector"], [`PLN ${N(d4b.loss_per_person_year, 0)}`, "loss per person a year, base scenario"]]);

{ const s = content("[ 04 · D4 · MECHANICS ]", "PPK means 1.5% of pay from the employer plus state subsidies, all forfeited on opting out", "Source: PPK Act, mojeppk.pl; automatic re-enrolment every four years, next in 2027.");
  cards(s, [["01 · CONTRIBUTIONS", "Who pays what", ["• Employee: 2% of gross pay (0.5% on low incomes)", "• Employer: 1.5% of gross pay", "• State: PLN 250 at the start and PLN 240 a year", "The employer contribution counts as the employee's taxable income."]],
    ["02 · WITHDRAWAL", "Leaving early", ["Before age 60, 30% of employer contributions goes to ZUS, state subsidies are forfeited and gains are taxed.", "The employee's own contributions are always returned in full."]],
    ["03 · WHAT WE COUNT", "Only the free money", ["The employer contribution after PIT and the state subsidy. The employee's own contribution is not a loss, because it stays in the employee's pocket.", "We allow for part of the participants withdrawing before age 60."]]], 3); }

{ const s = content("[ 04 · D4 · PER PERSON ]", `An employee earning PLN 7,400 gross who opts out loses about PLN ${N(d4b.loss_per_person_year, 0)} a year`, "amb research (python -m engine.run_d4): gross pay PLN 7,400, 85% of employer contributions kept, 50% of subsidies.");
  const lab = ["Employer contribution", "PIT 12%", "Withdrawals before 60", "State subsidy", "Loss per person"];
  s.addChart(pres.charts.BAR, [{ name: "Base", labels: lab, values: [0, 1172, 996, 996, 0] }, { name: "PLN", labels: lab, values: [1332, 160, 176, 120, 1116] }],
    { ...CHART, barDir: "col", barGrouping: "stacked", barGapWidthPct: 50, chartColors: [HEX.white, HEX.blue], showValue: false, showLegend: false, showTitle: true, title: "From employer contribution to loss per person, PLN a year", valAxisMinVal: 0, valAxisMaxVal: 1500, ...AX, objectName: "wf" });
  const rows = [[TH("STEP"), TH("CALCULATION"), TH("PLN", R)]];
  [["Employer contribution", "1.5% × 7,400 × 12", "1,332"], ["PIT 12%", "employee's income", "−160"], ["Withdrawals before 60", "× 85%", "−176"], ["State subsidy", "PLN 240 × 50%", "+120"], ["Loss per person", "a year, base", "1,116"]]
    .forEach((r, i) => rows.push([TD(r[0], { bold: i === 4 }), TD(r[1]), TD(r[2], { ...R, bold: i === 4, color: i === 4 ? HEX.blue : HEX.ink3 })]));
  table(s, PX, TOP, PW, rows, [1.75, 1.75, 0.783], "wft", 0.42);
  panel(s, PX, 4.95, PW, 1.7, [{ l: "READING THE CHART" }, { p: "Blue bars show what the employee gains or loses at each step. The final bar is the net annual loss used in the model." }], "wf-t", 12); }

{ const s = content("[ 04 · D4 · ENGINE OUTPUT ]", `PLN ${N(L.D4.base)} bn a year, and the result is robust to every assumption`, "Output: python -m engine.run_d4 → data/processed/d4_ppk.csv.");
  const rows = [[TH("SCENARIO"), TH("GROSS PAY", R), TH("EMPLOYER NET", R), TH("LOSS PER PERSON", R), TH("OPTED OUT", R), TH("PLN BN", R)]];
  D.d4_table.forEach((r) => { const o = r.scenario === "base" ? { bold: true, color: HEX.blue } : {};
    rows.push([TD(r.scenario, o), TD(`PLN ${N(r.gross_pay, 0)}`, { ...R, ...o }), TD(`PLN ${N(r.employer_net_year, 0)}`, { ...R, ...o }), TD(`PLN ${N(r.loss_per_person_year, 0)}`, { ...R, ...o }), TD(`${N(r.opted_out_mn)} mn`, { ...R, ...o }), TD(N(r.loss_bn, 2), { ...R, ...o })]); });
  table(s, M, TOP, CW, rows, [2.4, 2.0, 2.2, 2.2, 1.8, 1.533], "d4t", 0.48);
  cards(s, [["WAGES OF THOSE WHO OPT OUT", null, "Base PLN 7,400, about 80% of the enterprise sector average (PLN 9,266 in Sep 2026). A range of PLN 6,000 to 9,266 gives PLN 2.6 bn to 3.8 bn."],
    ["NUMBER OUTSIDE PPK", null, "Base 2.8 mn (PFR: about 38% of eligible). The ratio counts accounts rather than people and only firms running PPK, so the result is likely understated."],
    ["WHAT WE OMIT", null, "The PLN 250 welcome payment, voluntary employer top ups and investment returns on contributions. Each of these would raise the gap."]], 3, 4.5, 2.15, 12); }

{ const s = content("[ 04 · D4 · PUBLIC SECTOR ]", "The state as an employer is the least successful at enrolling staff in its own programme", "Source: PFR, PPK register, 28 Oct 2026 (as reported by analizy.pl).");
  s.addChart(pres.charts.BAR, [{ name: "Participation, %", labels: ["Firms 1,000+", "Private sector", "Total", "Public sector", "Firms 10 to 49"], values: [93.03, 73.04, 63.9, 37.53, 33.83] }],
    { ...CHART, barDir: "col", barGapWidthPct: 60, chartColors: [HEX.blue], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', showLegend: false, showTitle: true, title: "PPK participation, Oct 2026, %", valAxisMinVal: 0, valAxisMaxVal: 100, ...AX, objectName: "part" });
  panel(s, PX, TOP, PW, H, [{ l: "WHAT STANDS OUT" }, { p: "Large private firms exceed 93% participation. The public sector and small firms sit between 34% and 38%." }, { l: "WHY IT MATTERS" },
    { p: "The 35 pp gap between the private and public sectors is the simplest lever to pull in the entire programme." }, { l: "RE-ENROLMENT 2027" }, { p: "The next automatic re-enrolment in 2027 is a natural moment for an information campaign across the public administration." }], "part-t"); }

end("[ 04 · D4 · CONCLUSION ]", "PPK is the easiest money to recover in the entire report", `PLN ${N(L.D4.base)} bn`, `a year · range PLN ${N(L.D4.conservative)} bn to ${N(L.D4.aggressive)} bn · about PLN 1,100 per person`,
  [{ l: "BARRIER" }, { h: "Knowledge of and trust in the programme" }, { p: "It requires no risk, knowledge or effort beyond not opting out." }, { l: "A FAIR CAVEAT" },
    { p: "Many people opt out for sound reasons, for example because they need every zloty today. The total is therefore a cost worth being aware of, not a mistake in every case." }]);

// ---------------- D3
section("D3 · IKE and IKZE");
divider("[ 05 · D3 · IKE AND IKZE ]", "An unused tax shield", `PLN ${N(L.D3.base)} bn a year of Belka tax that could be avoided legally through IKE and IKZE accounts.`,
  [["~PLN 9 bn", "Belka tax a year (2026 forecast)"], ["1.32 mn", "IKE accounts for more than 30 mn adults"], ["PLN 0", "extra penalty for early IKE withdrawal"]]);

{ const s = content("[ 05 · D3 · MECHANICS ]", "IKE removes the Belka tax, IKZE lowers income tax, and early IKE withdrawal costs nothing extra", "Source: IKE and IKZE Act; limits: MRPiPS notices of November 2025.");
  cards(s, [["01 · IKE", "Individual retirement account", ["• Gains exempt from the 19% Belka tax on withdrawal after 60 (55 with early retirement rights)", "• Can hold deposits, Treasury bonds, funds and shares", "• 2026 contribution limit: PLN 28,260", "Early withdrawal means paying the Belka tax as on an ordinary account, so long term money faces no tax downside."]],
    ["02 · IKZE", "Individual retirement security account", ["• Contributions deductible from taxable income (12% or 32%)", "• Flat 10% tax on withdrawal after 65", "• 2026 limit: PLN 11,304 (PLN 16,956 for the self employed)", "The model ignores the IKZE income tax relief, so D3 is understated."]]], 2); }

{ const B = D.d3_belka;
  const s = content("[ 05 · D3 · BELKA TAX ]", "Poles pay about PLN 9 bn of Belka tax a year, most of it on interest", "Source: Ministry of Finance (as reported by PAP and analizy.pl); 2026F = forecast.");
  s.addChart(pres.charts.BAR, [{ name: "Interest on savings", labels: B.map((b) => b.year), values: B.map((b) => b.savings) }, { name: "Investment gains", labels: B.map((b) => b.year), values: B.map((b) => b.investments) }],
    { ...CHART, barDir: "col", barGrouping: "stacked", barGapWidthPct: 60, chartColors: [HEX.blue, HEX.g4], showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "0.0", showLegend: true, legendPos: "b", showTitle: true, title: "Belka tax receipts, PLN bn", valAxisMinVal: 0, ...AX, dataLabelColor: HEX.white, objectName: "belka" });
  panel(s, PX, TOP, PW, H, [{ l: "WHAT STANDS OUT" }, { p: "Receipts fell from a record of about PLN 10.5 bn in 2024 to about PLN 9 bn forecast for 2026, mainly because deposit rates declined." },
    { p: "The share from investments is rising, from PLN 3.2 bn to PLN 3.9 bn." }, { l: "WHY IT MATTERS FOR D3" }, { p: "The more savings move from deposits into investment instruments, the more valuable the IKE tax shield becomes." }], "belka-t"); }

{ const s = content("[ 05 · D3 · ENGINE OUTPUT ]", `PLN ${N(L.D3.base)} bn a year in the base case: 25% of the tax on savings and 40% of the tax on investments`, "Output: python -m engine.run_d3 → data/processed/d3_tax_wrappers.csv.");
  const rows = [[TH("SCENARIO"), TH("SAVINGS SHARE", R), TH("INVESTMENT SHARE", R), TH("SAVINGS BN", R), TH("INVESTMENTS BN", R), TH("TOTAL BN", R)]];
  D.d3_table.forEach((r) => { const o = r.scenario === "base" ? { bold: true, color: HEX.blue } : {};
    rows.push([TD(r.scenario, o), TD(`${Math.round(r.share_savings * 100)}%`, { ...R, ...o }), TD(`${Math.round(r.share_investments * 100)}%`, { ...R, ...o }), TD(N(r.savings_bn, 2), { ...R, ...o }), TD(N(r.investments_bn, 2), { ...R, ...o }), TD(N(r.total_bn, 2), { ...R, ...o })]); });
  table(s, M, TOP, CW, rows, [2.4, 2.0, 2.2, 2.0, 1.9, 1.633], "d3t", 0.48);
  cards(s, [["WHY NOT 100%", null, "Short term money does not belong in an IKE, and annual limits quickly become binding for larger portfolios."],
    ["CAPACITY CHECK", null, "The base case shelters about PLN 15 bn of gains a year, which under current limits requires several million regular contributors."],
    ["NO DOUBLE COUNTING", null, "We start from the tax paid today rather than after a move into COI bonds (D1). This approach is conservative."]], 3, 4.5, 2.15, 12); }

end("[ 05 · D3 · CONCLUSION ]", "The tool is legal and free, yet few use it: the barrier is knowledge", `PLN ${N(L.D3.base)} bn`, `a year · range PLN ${N(L.D3.conservative)} bn to ${N(L.D3.aggressive)} bn`,
  [{ l: "BARRIER" }, { h: "Awareness that IKE carries no penalty" }, { p: "Many people believe an IKE locks money away until retirement. In practice, early withdrawal costs exactly the ordinary tax." },
    { l: "POLICY CONTEXT" }, { p: "The proposed exemption from Belka tax for gains up to PLN 100,000 would narrow this gap from the state's side." }]);

// ---------------- D2
section("D2 · Fees");
divider("[ 06 · D2 · FEES ]", "Fees in investment funds", `PLN ${N(L.D2.base)} bn a year above the cost of a low cost alternative in the same asset class.`,
  [["~PLN 310 bn", "in non-dedicated retail funds"], ["0% to 2%", "passive share in bond and mixed funds"], ["0.88%", "average cost of short term bond funds"]]);

{ const AH = D.d2_assets_history, lab = AH.map((r) => r.month), order = ["short_bond", "bond", "equity", "mixed", "absolute_return"];
  const s = content("[ 06 · D2 · MARKET ]", "Fund assets have doubled since 2018, with short term bond funds growing fastest", "Source: IZFiA RawData (NAV of every fund), Aug 2018 to Oct 2026, excluding PPK, commodity and private market funds; amb research.");
  s.addChart(pres.charts.AREA, order.map((b) => ({ name: NAMES[b], labels: lab, values: AH.map((r) => r[b]) })),
    { ...CHART, barGrouping: "stacked", chartColors: [HEX.blue, HEX.blueSoft, HEX.ink4, HEX.g4, HEX.g3], showLegend: true, legendPos: "b", showTitle: true, title: "Assets of non-dedicated funds, PLN bn", catAxisLabelFrequency: 12, ...AX, objectName: "assets" });
  panel(s, PX, TOP, PW, H, [{ l: "WHAT STANDS OUT" }, { p: "From about PLN 160 bn in 2018 to more than PLN 300 bn in 2026. The 2022 dip reflects outflows and the repricing of bonds." },
    { p: "Short term bond funds grew fastest and now hold about PLN 129 bn; for many savers they replace a term deposit." }, { l: "WHY IT MATTERS FOR D2" }, { p: "The larger the category, the more each 0.1 pp of cost difference is worth in zloty." }], "assets-t"); }

{ const sp = D.d2_split.rows;
  const s = content("[ 06 · D2 · PASSIVE FUNDS ]", "Outside equity, low cost index funds barely exist in Poland", "Source: IZFiA, assets of non-dedicated funds with the Passive flag, Oct 2026, excluding PPK.");
  s.addChart(pres.charts.BAR, [{ name: "Passive share, %", labels: sp.map((r) => NAMES[r.bucket]), values: sp.map((r) => r.passive_share_pct) }],
    { x: M, y: TOP, w: COL(6, 12), h: H, barDir: "bar", barGapWidthPct: 60, chartColors: [HEX.blue], catAxisOrientation: "maxMin", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', showLegend: false, showTitle: true, title: "Passive funds as a share of assets, Oct 2026, %", valAxisMinVal: 0, valAxisMaxVal: 15, ...AX, objectName: "passive" });
  const rows = [[TH("CATEGORY"), TH("ACTIVE", R), TH("PASSIVE", R), TH("PASSIVE %", R)]];
  sp.forEach((r) => rows.push([TD(NAMES[r.bucket]), TD(`PLN ${N(r.active_bn)} bn`, R), TD(`PLN ${N(r.passive_bn)} bn`, R), TD(N(r.passive_share_pct), { ...R, bold: true })]));
  table(s, X(6, 12), TOP, COL(6, 12), rows, [1.85, 1.45, 1.45, 1.167], "pt", 0.42);
  panel(s, X(6, 12), 4.55, COL(6, 12), 2.1, [{ l: "WHAT STANDS OUT" }, { p: "In equity funds the passive share is rising fast, from 6.3% in June to 10.1% in October 2026. Bond and mixed funds, which together hold about PLN 250 bn, have almost none." }], "pass-t"); }

{ const F = D.d2_funds;
  const s = content("[ 06 · D2 · FUND COSTS ]", "Within one category, one fund charges 2.5 times as much as another each year", "Source: KID documents and TFI cost tables (2021 to 2026; data/reference/short_term_fund_costs.csv). Pekao Spokojna Inwestycja and Pekao Konserwatywny: estimated from the management fee.");
  s.addChart(pres.charts.BAR, [{ name: "Ongoing charges, %", labels: F.map((f) => f.fund), values: F.map((f) => f.cost_pct) }],
    { x: M, y: TOP, w: COL(8, 12), h: H, barDir: "bar", barGapWidthPct: 40, chartColors: [HEX.blue], catAxisOrientation: "maxMin", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.00"%"', showLegend: false, showTitle: true, title: "Short term bond funds: annual ongoing charges, %", valAxisMinVal: 0, valAxisMaxVal: 1.5, ...AX, catAxisLabelFontSize: 9, objectName: "funds" });
  stat(s, X(8, 12), TOP, COL(4, 12), "0.88%", "asset weighted average of 12 funds holding 68.6% of the category (PLN 129 bn)", C.accent1, "fs", 36);
  panel(s, X(8, 12), 3.75, COL(4, 12), 2.9, [{ l: "WHAT STANDS OUT" }, { p: "For a similar product investors pay from about 0.5% to about 1.2% a year. On PLN 100,000 that is about PLN 700 a year." }, { l: "NOTE" }, { p: "This is not a recommendation of any fund. It shows the spread of costs taken from the managers' own documents." }], "f-t", 12); }

{ const Aq = Object.fromEntries(D.d2_assumptions.map((r) => [`${r.bucket}|${r.scenario}`, r]));
  const s = content("[ 06 · D2 · ASSUMPTIONS ]", "Active costs and alternative costs: every figure has a source", "Sources: analizy.pl (management fees, TER and KID charges, 2023 to 2025); own KID measurement for short term bond funds; model: engine/models/fee_drag.py.");
  const alt = { equity: "Domestic equity index fund", mixed: "60/40 portfolio of index funds", bond: "Treasury bond index fund", short_bond: "Lowest cost short term funds" };
  const gb = Object.fromEntries(D.d2_by_bucket.map((r) => [r.bucket, r]));
  const rows = [[TH("CATEGORY"), TH("ACTIVE C / B / A", R), TH("ALTERNATIVE C / B / A", R), TH("ALTERNATIVE"), TH("BASE GAP, BN", R)]];
  ["equity", "mixed", "bond", "short_bond"].forEach((b) => rows.push([TD(NAMES[b], { bold: true }), TD(SC.map((k) => N(Aq[`${b}|${k}`].active_cost_pct, 2)).join(" / "), R),
    TD(SC.map((k) => N(Aq[`${b}|${k}`].alternative_cost_pct, 2)).join(" / "), R), TD(alt[b]), TD(N(gb[b].base, 2), { ...R, bold: true })]));
  rows.push([TD("Total", { bold: true }), TD(""), TD(""), TD(""), TD(N(L.D2.base, 2), { ...R, bold: true, color: HEX.blue })]);
  table(s, M, TOP, CW, rows, [2.2, 2.6, 2.6, 3.0, 1.733], "d2a", 0.5);
  panel(s, M, 5.6, CW, 1.05, [{ l: "KEY ASSUMPTION" }, { p: "On average, active funds do not beat the market before fees (zero alpha). This is standard in the literature; for Poland it will be tested in version 2 by comparing net returns with benchmarks." }], "d2a-t", 12); }

{ const P = D.d2_compound;
  const s = content("[ 06 · D2 · COMPOUNDING ]", "Over 30 years, a cost difference of 1.4 pp absorbs a third of the result", "amb research (fee_drag.compound_cost): PLN 100,000 at 7% a year before costs; 2.13% = equity fund TER 2023 (analizy.pl), 0.70% = index fund.");
  s.addChart(pres.charts.LINE, [{ name: "Cost 0.70% (index fund)", labels: P.map((p) => String(p.year)), values: P.map((p) => +(p.low / 1000).toFixed(1)) }, { name: "Cost 2.13% (active fund)", labels: P.map((p) => String(p.year)), values: P.map((p) => +(p.high / 1000).toFixed(1)) }],
    { ...CHART, chartColors: [HEX.blue, HEX.g4], lineSize: 2, lineDataSymbol: "none", showLegend: true, legendPos: "b", showTitle: true, title: "Value of PLN 100,000, PLN thousand, years 0 to 30", catAxisLabelFrequency: 5, valAxisMinVal: 0, ...AX, objectName: "comp" });
  stat(s, PX, TOP, PW, "PLN 209,000", "difference after 30 years: PLN 625,000 versus PLN 416,000", C.accent1, "cs", 36);
  panel(s, PX, 3.75, PW, 2.9, [{ l: "WHY IT MATTERS" }, { p: "A cost gap looks small in any single year but works like compound interest in reverse." }, { p: `Across the market this amounts to about PLN ${N(L.D2.base)} bn a year. As a check, fund managers earned PLN 4.69 bn from managing funds in 2025 (KNF).` }], "comp-t"); }

end("[ 06 · D2 · CONCLUSION ]", "The largest opportunity lies not in equity, but in bond and mixed funds", `PLN ${N(L.D2.base)} bn`, `a year · range PLN ${N(L.D2.conservative)} bn to ${N(L.D2.aggressive)} bn`,
  [{ l: "BARRIER" }, { h: "A lack of low cost products and of cost transparency" }, { p: "Passive funds are already growing in equity. In bond and mixed funds, which hold about PLN 250 bn, low cost options are almost absent." },
    { l: "WHAT WOULD HELP" }, { b: "Bond index funds and 60/40 portfolios built from index funds." }, { b: "Costs shown in zloty on a typical amount." }]);

// ---------------- D5
section("D5 · Timing");
divider("[ 07 · D5 · TIMING ]", "Buying and selling at the wrong time", `A hypothesis that was not supported: about PLN ${N(L.D5.base)} bn a year, less than in the United States.`,
  [["98", "months of flow data (Sep 2018 to Oct 2026)"], ["0.4 to 0.7 pp", "typical gap in equity and mixed funds"], ["~1.2 pp", "the same measure in the US (Morningstar)"]]);

{ const s = content("[ 07 · D5 · METHOD ]", "The investor gap: fund returns (TWR) versus the returns on investors' money (IRR)", "Model: engine/models/investor_gap.py; tests: tests/test_investor_gap.py.");
  cards(s, [["01 · QUESTION", "What we measure", ["A fund may return 9% a year, but if clients buy after rallies and sell after declines, their money earns less.", "The difference between the two returns is the investor gap."]],
    ["02 · METHOD", "TWR, IRR and Dietz", ["• TWR: time weighted, the fund's return", "• IRR: money weighted, the investors' return", "• Monthly returns: modified Dietz on IZFiA assets and net flows"]],
    ["03 · PITFALLS", "What the model handles", ["• Funds changing category never register a gain or loss", "• Liquidations and mergers are not counted as losses", "• PPK is excluded from the analysis", "All of this is covered by unit tests."]]], 3); }

{ const E = D.d5_equity_flows;
  const s = content("[ 07 · D5 · BEHAVIOUR ]", "Investors pulled money out of equity funds at the worst moment, but such episodes are rare", "Source: IZFiA, net flows of non-dedicated equity funds (excluding PPK), Sep 2018 to Oct 2026.");
  s.addChart(pres.charts.BAR, [{ name: "Net flows, PLN bn", labels: E.map((e) => e.month), values: E.map((e) => e.flow_bn) }],
    { ...CHART, barDir: "col", barGapWidthPct: 30, chartColors: [HEX.blue], showValue: false, showLegend: false, showTitle: true, title: "Equity funds: monthly net flows, PLN bn", catAxisLabelFrequency: 12, ...AX, objectName: "flows" });
  panel(s, PX, TOP, PW, H, [{ l: "CASE: THE 2020 CRASH" }, { p: "March 2020: equity funds fell 14.3% and investors withdrew a net PLN 1.1 bn. Funds then gained 11.1% in April and 12.7% in November. Money withdrawn at the bottom missed the recovery." },
    { l: "WHAT IT MEANS" }, { p: "Such episodes are costly but rare. For most of the period flows were stable, and since 2025 they have been clearly positive." }], "flows-t"); }

{ const I = D.d5_index, b5 = ["equity", "mixed", "bond", "short_bond", "absolute_return"], last = (b) => I[b][I[b].length - 1], twr = (b) => D.d5_table.find((r) => r.category === b).twr_pct;
  const s = content("[ 07 · D5 · RETURNS ]", "Equity funds have doubled since 2018, while bond and mixed funds gained 30% to 45%", "Source: IZFiA; modified Dietz with reclassification alignment; amb research.");
  s.addChart(pres.charts.LINE, b5.map((b) => ({ name: NAMES[b], labels: I.months, values: I[b] })), { ...CHART, chartColors: [HEX.blue, HEX.ink4, HEX.g4, HEX.blueSoft, HEX.g3], lineSize: 2, lineDataSymbol: "none", showLegend: true, legendPos: "b", showTitle: true, title: "Cumulative return by fund category (TWR), Aug 2018 = 100", catAxisLabelFrequency: 12, ...AX, objectName: "idx" });
  panel(s, PX, TOP, PW, H, [{ l: "FUND RETURNS, SEP 2018 TO OCT 2026" }, ...b5.map((b) => ({ p: `${NAMES[b]}: ${N(last(b), 0)} (${N(twr(b), 2)}% a year)` })), { l: "NOTE" }, { p: "These are fund returns after costs. Investor returns (IRR) follow on the next slide." }], "idx-t"); }

{ const s = content("[ 07 · D5 · ENGINE OUTPUT ]", "At category level the investor gap is small, and close to zero in short term bond funds", "Output: python -m engine.run_d5 → data/processed/d5_investor_gap.csv. 5y = 39 rolling five year windows.");
  const rows = [[TH("CATEGORY"), TH("TWR %", R), TH("IRR %", R), TH("GAP, FULL PERIOD", R), TH("GAP, 5Y MEDIAN", R), TH("5Y RANGE", R), TH("AVG ASSETS, BN", R)]];
  D.d5_table.forEach((r) => rows.push([TD(NAMES[r.category] || r.category, { bold: r.category === "total" }), TD(N(r.twr_pct, 2), R), TD(N(r.irr_pct, 2), R), TD(N(r.gap_pp, 2), R),
    TD(N(r.gap_5y_median_pp, 2), { ...R, bold: true }), TD(`${N(r.gap_5y_min_pp, 2)} to ${N(r.gap_5y_max_pp, 2)}`, R), TD(N(r.avg_aum_pln_bn, 1), R)]));
  table(s, M, TOP, CW, rows, [2.6, 1.3, 1.3, 1.85, 1.85, 1.75, 1.483], "d5t", 0.44);
  panel(s, M, 5.55, CW, 1.1, [{ l: "HOW TO READ" }, { p: "The full period result depends on its end points (heavy outflows in September 2018, peak assets in October 2026), so the main measure is the median of five year windows. The total row reflects the category mix rather than timing." }], "d5r-t", 12); }

{ const Rl = D.d5_rolling;
  const s = content("[ 07 · D5 · GAP OVER TIME ]", "The equity gap varies with the period, while the mixed fund gap holds steady at about 0.6 to 0.7 pp", "Source: IZFiA; 39 five year windows (window end on the axis); US: Morningstar Mind the Gap, as reported by analizy.pl.");
  s.addChart(pres.charts.LINE, ["equity", "mixed", "bond"].map((b) => ({ name: NAMES[b], labels: Rl.map((r) => r.end), values: Rl.map((r) => r[b]) })),
    { ...CHART, chartColors: [HEX.blue, HEX.ink4, HEX.g4], lineSize: 2, lineDataSymbol: "none", showLegend: true, legendPos: "b", showTitle: true, title: "Investor gap in five year windows, pp a year", catAxisLabelFrequency: 6, valAxisMinVal: -0.2, valAxisMaxVal: 2, ...AX, objectName: "roll" });
  panel(s, PX, TOP, PW, H, [{ l: "ROBUSTNESS" }, { p: "With monthly data we assume flows arrive mid month. Assuming month end, the full period equity gap is 0.44 pp; assuming month start, minus 0.06 pp." },
    { p: "Mixed funds are stable under every assumption (0.41 to 0.60 pp), so the equity result is always quoted with a range." }, { l: "BENCHMARK" }, { p: "The same measure in the United States is about 1.2 pp a year." }], "roll-t"); }

end("[ 07 · D5 · CONCLUSION ]", "Poor timing costs several times less than fees", `~PLN ${N(L.D5.base)} bn`, "a year · about PLN 3.3 bn over eight years in categories with a positive gap",
  [{ l: "HYPOTHESIS H5" }, { h: "Not supported" }, { p: "We expected Polish investors to lose heavily on timing. The data shows they lose less than American investors." },
    { l: "LIMITATION" }, { p: "The analysis works at category level and cannot see switching between funds within a category, such as chasing a fashionable thematic fund. Version 2 will measure this fund by fund." }]);

// ---------------- Synthesis
section("Synthesis");
dark("[ 08 · SYNTHESIS ]", "The largest losses come from money that sits idle", "The reverse of what most people fear: fear of the stock market costs less than unused bonds, PPK and IKE.");

{ const idle = L.D1.base, prog = L.D3.base + L.D4.base, mkt = L.D2.base + L.D5.base;
  const s = content("[ 08 · THREE GROUPS ]", "Three groups of causes: idle money, unused programmes and market costs", `Source: amb research, base scenario; total PLN ${N(T.base)} bn a year.`);
  s.addChart(pres.charts.BAR, [{ name: "PLN bn a year", labels: ["Idle money (D1)", "Programmes (D3 + D4)", "Market (D2 + D5)"], values: [+idle.toFixed(2), +prog.toFixed(2), +mkt.toFixed(2)] }],
    { x: M, y: TOP, w: COL(5, 12), h: H, barDir: "col", barGapWidthPct: 50, chartColors: [HEX.blue], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", showLegend: false, showTitle: true, title: "PLN bn a year, base scenario", valAxisMinVal: 0, ...AX, objectName: "groups" });
  const h = (H - 2 * GAP) / 3;
  [["01 · IDLE MONEY", "Deposits instead of Treasury bonds", "Habit and convenience rather than risk."], ["02 · UNUSED PROGRAMMES", "PPK, IKE and IKZE", "Knowledge of and trust in state programmes."], ["03 · MARKET", "Fees and poor timing", "Cost transparency and a lack of low cost products."]]
    .forEach((c, i) => card(s, X(5, 12), TOP + i * (h + GAP), COL(7, 12), h, c[0], c[1], c[2], `grp-${i}`, 12.5)); }

{ const s = content("[ 08 · WHAT IT MEANS ]", "The good news: the largest levers are the easiest to change", null);
  cards(s, [["01", "No market risk required", ["Moving surplus cash into Treasury bonds, staying in PPK and opening an IKE leave the saver's risk profile unchanged.", `Together they are worth about PLN ${N(L.D1.base + L.D3.base + L.D4.base)} bn a year.`]],
    ["02", "No market expertise required", ["There is no need to pick shares or forecast markets. It is enough to know that these products exist and how they work.", "This gives financial education a direct, measurable effect."]],
    ["03", "Immediate impact", ["Every zloty moved from a current account into COI bonds earns about 3.2 pp a year more after tax from the first year.", "There is no need to wait decades, as with fund costs."]]], 3); }

{ const s = content("[ 08 · RECOMMENDATIONS · HOUSEHOLDS ]", "Households: deal with idle money first, then with costs", "Recommendations concern product categories. This report is not investment advice.");
  cards(s, [["01", "Buffer and surplus", "Keep the liquidity buffer in the bank and hold the surplus above it in State Treasury instruments carrying the same risk."], ["02", "Stay in PPK", "Do not opt out without a specific reason: employer contributions and state subsidies are money without risk."],
    ["03", "Use IKE or IKZE", "Hold long term savings inside an IKE or IKZE. Early IKE withdrawal costs no more than the ordinary tax."], ["04", "Read the KID", "Before buying a fund, check its ongoing charges in the KID and compare them with funds in the same category."]], 4); }

{ const s = content("[ 08 · RECOMMENDATIONS · INDUSTRY AND GOVERNMENT ]", "Industry and government: low cost products where they are missing, and better use of existing programmes", "Recommendations to be refined once the key assumptions are anchored (version 1.0).");
  cards(s, [["INDUSTRY: BANKS AND FUND MANAGERS", "Low cost products and transparency", ["• Index funds outside equity: today 0% to 2% of bond and mixed fund assets", "• Costs shown in zloty on a typical amount, not only as percentages", "• A simple path within the app from the account to Treasury bonds and an IKE"]],
    ["GOVERNMENT AND REGULATORS", "Programmes that already exist", ["• PPK in the public sector: 37.5% participation against 73% in the private sector; the 2027 re-enrolment is an opportunity", "• A simpler IKE and a single public place to compare fund costs", "• Financial education in schools covering Treasury bonds, PPK and IKE"]]], 2); }

// ---------------- Limitations
section("Limitations");
{ const s = content("[ 09 · LIMITATIONS ]", "What this draft does not yet know, and how we will address it before version 1.0", "Full methodology and limitations: PDF report, chapter 12.");
  const r = (a, b, c) => [TD(a, { bold: true }), TD(b), TD(c)];
  table(s, M, TOP, CW, [[TH("LIMITATION"), TH("EFFECT ON THE RESULT"), TH("HOW WE WILL ADDRESS IT")],
    r("The movable share of current accounts (D1) is an assumption", "±PLN 3.6 bn around the base case", "NBP wealth survey and a survey question"), r("The avoidable share of Belka tax (D3) is an assumption", "PLN 1.7 bn to 4.4 bn", "Distribution of savings by portfolio size"),
    r("Wages of PPK opt outs (D4) are estimated", "PLN 2.6 bn to 3.8 bn", "PFR data on participant structure"), r("Several figures come from the press (NBP, MF, PFR)", "Risk of an outdated figure", "Source files obtained directly"),
    r("D1 is a valuation as of today", "Unknown for other periods", "Rolling windows on the bond issue archive"), r("D2 assumes zero alpha", "May overstate D2", "Net returns versus benchmarks"),
    r("D5 is measured at category level", "Understates D5", "Flows for individual funds"), r("General equilibrium effects", "Gap at current behaviour", "Stated in the methodology")], [4.6, 3.3, 4.233], "lim", 0.46); }

{ const s = content("[ 09 · PATH TO VERSION 1.0 ]", "Three steps to version 1.0 and two publications", "amb research · Report 01 · draft 0.2 · 19 November 2026");
  cards(s, [["STEP 1", "Anchor the assumptions", "NBP household wealth survey and an anonymous survey: how much people hold above their buffer, whether they use IKE and PPK, and what they believe they pay for funds."],
    ["STEP 2", "Data straight from source", "Deposits from NBP, Belka tax from the Ministry of Finance and PPK participation from the PFR bulletin instead of the press, each with download date and checksum."],
    ["STEP 3", "Version 2 models", "D1 on historical windows, D2 with net returns against benchmarks, and D5 at the level of individual funds."]], 3, TOP, 3.1);
  panel(s, M, 5.7, CW, 0.95, [{ l: "PUBLICATION PLAN" }, { p: "First: the investor gap (D5) as a standalone note with a link to the survey. Second: the full report on amb.watch, with the code, the PDF and the methodology." }], "pub", 12.5); }

// ---------------- Appendix
section("Appendix");
{ const s = content("[ A1 · ENGINE OUTPUTS ]", "Every figure in this report comes from a single command", "Repository: engine/ (Python), tests/ (29 tests), data/processed/ (CSV outputs), report/ (charts, PDF and this deck).");
  const r = (a, b, c, d) => [TD(a, { fontFace: MONO, fontSize: 10 }), TD(b), TD(c), TD(d, { ...R, bold: true })];
  table(s, M, TOP, CW, [[TH("COMMAND"), TH("WHAT IT COMPUTES"), TH("OUTPUT FILE"), TH("BASE RESULT", R)],
    r("python -m engine.report", "Everything: results, 16 charts, data", "report/data.json, report/charts/", `PLN ${N(T.base)} bn`), r("python -m engine.run_d1", "Deposits versus COI", "d1_deposits.csv", `PLN ${N(L.D1.base)} bn`),
    r("python -m engine.run_d2", "Cost gap, passive share", "d2_fees.csv", `PLN ${N(L.D2.base)} bn`), r("python -m engine.run_d3", "IKE and IKZE tax shield", "d3_tax_wrappers.csv", `PLN ${N(L.D3.base)} bn`),
    r("python -m engine.run_d4", "Forgone PPK contributions", "d4_ppk.csv", `PLN ${N(L.D4.base)} bn`), r("python -m engine.run_d5", "TWR versus IRR, 5y windows", "d5_investor_gap.csv", `PLN ${N(L.D5.base)} bn`),
    r("python report/pdf/build_pdf.py", "Long form PDF report", "report/pdf/*.pdf", "28 pages"), r("python -m pytest", "Unit tests", "tests/", "29 / 29")], [3.6, 3.4, 3.4, 1.733], "annex", 0.44); }

{ const s = content("[ A2 · ARCHITECTURE ]", "An open Python engine: data, models, outputs and report", "Stack: Python, pandas, numpy, scipy, openpyxl, matplotlib, rich and pytest; deck built with pptxgenjs.");
  const mods = [["engine/data/izfia.py", "Downloads the IZFiA archive with a manifest: URL, date, SHA-256."], ["engine/data/izfia_parse.py", "Three file formats, stable categories, PPK excluded."],
    ["engine/models/investor_gap.py", "Dietz with reclassification alignment, IRR, gap in PLN."], ["engine/models/fee_drag.py", "Cost assumptions with sources, cost gap, compounding."],
    ["engine/models/deposits.py", "Deposits versus COI, Belka on both sides, redemptions."], ["engine/models/tax_wrappers.py", "IKE and IKZE shield from the tax paid today."],
    ["engine/models/ppk.py", "Employer contributions after PIT and state subsidies."], ["engine/report.py · ui.py · charts.py", "One command: terminal output in the amb style and 16 charts."]];
  const h = (H - 3 * GAP) / 4;
  mods.forEach((m, i) => { const x = X((i % 2) * 6, 12), y = TOP + Math.floor(i / 2) * (h + GAP), w = COL(6, 12);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.background2 }, line: { type: "none" }, objectName: `ar-${i}-bg` });
    s.addText([{ text: m[0], options: { fontFace: MONO, fontSize: 11, color: C.accent1, breakLine: true } }, { text: m[1], options: { fontSize: 12.5, color: C.text2 } }], { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: h - 0.3, margin: 0, valign: "top", isTextBox: true, objectName: `ar-${i}` }); }); }

{ const s = content("[ A3 · GLOSSARY ]", "Ten terms used throughout the report", null);
  table(s, M, TOP, CW, [[TH("TERM"), TH("MEANING")], [TD("COI", { bold: true }), TD("Four year inflation indexed retail Treasury bonds: a fixed rate in year one, then inflation plus a margin.")],
    [TD("IKE / IKZE", { bold: true }), TD("Individual retirement account / individual retirement security account: tax advantaged accounts with annual limits.")], [TD("PPK", { bold: true }), TD("Employee Capital Plans: contributions from the employee, the employer and the state.")],
    [TD("Belka tax", { bold: true }), TD("The 19% flat tax on capital gains and interest.")], [TD("KID", { bold: true }), TD("Key information document of a fund, including its ongoing charges.")],
    [TD("TER", { bold: true }), TD("Total expense ratio: a fund's total costs relative to its assets.")], [TD("TWR", { bold: true }), TD("Time weighted return: the fund's return, independent of payments in and out.")],
    [TD("IRR", { bold: true }), TD("Money weighted return: the return actually earned on investors' money.")], [TD("Modified Dietz", { bold: true }), TD("An approximate monthly return when flows occur during the month.")],
    [TD("Like for like risk", { bold: true }), TD("The report's principle: we compare only products that are at least as safe.")]], [2.6, 9.533], "gloss", 0.39); }

{ const s = content("[ A4 · SOURCES ]", "Full list of sources", "Download dates and checksums: data/raw/*/_manifest.csv.");
  panel(s, M, TOP, CW, H, [{ b: "IZFiA flow and asset data: izfa.pl/raporty" }, { b: "NBP MIR interest rate statistics (stopy_proc_pl_srdW.xlsx); deposit volumes as reported by Parkiet" },
    { b: "GUS monthly consumer price indices since 1982" }, { b: "obligacjeskarbowe.pl, four year COI bond offer, November 2026" }, { b: "KNF, report on the financial situation of fund managers (TFI) in 2025" },
    { b: "analizy.pl publications on fund costs (KID, TER, management fees), investor returns and PPK" }, { b: "KID documents and cost tables: PKO TFI, Pekao TFI, Millennium TFI, Erste TFI, ING TFI, PZU TFI" },
    { b: "MRPiPS notices on IKE and IKZE limits for 2026; Belka tax receipts: Ministry of Finance as reported by PAP, analizy.pl and xyz.pl" }], "srcs", 13); }

dark("[ AMB RESEARCH ]", "Less guessing. More understanding.", "amb.watch · Report 01: Money left on the table · draft 0.2", "logo_white.png");

(async () => { await pres.writeFile({ fileName: OUT }); await applyTheme(OUT, THEME); console.log("OK", OUT, "slides:", n); })();
