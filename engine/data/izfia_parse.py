"""Parses raw IZFiA files into two tables:

* net flows of non-dedicated funds per (month, category), from the "Sprzedaż dane" files;
* NAV per (month, fund), from the RawData sheet of the "Aktywa dane" files.

Categories (`bucket`) are deliberately coarse because IZFiA changed its classification several
times (for example Money_Market became Bond_Short_Term in 2019, and PPK target date funds were
reported separately only from 2021-04).
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import openpyxl
import pandas as pd

from .izfia import RAW_ASSETS, RAW_FLOWS, ROOT

PROCESSED = ROOT / "data" / "processed"

BUCKETS = ["equity", "mixed", "bond", "short_bond", "absolute_return"]
EXCLUDED = "excluded"


def bucket_of(profile: str) -> str:
    """Maps an IZFiA fund profile (any naming convention) to a stable category.

    Excluded: PPK and other target date funds (payroll contributions, not investor decisions),
    Mixed Other (held PPK funds until 2021-03), commodities, crypto and private market funds.
    """
    p = re.sub(r"[\s_]+", "_", str(profile).strip().lower())
    if "target_date" in p or "ppk" in p or p.startswith("mixed_other"):
        return EXCLUDED
    if p.startswith("equity"):
        return "equity"
    if p.startswith("mixed"):
        return "mixed"
    if "short_term" in p or p.startswith("money_market"):
        return "short_bond"
    if p.startswith("bond"):
        return "bond"
    if p.startswith("absolute"):
        return "absolute_return"
    return EXCLUDED


# ---------------------------------------------------------------- flows


def _rows(ws):
    return list(ws.iter_rows(values_only=True))


def _parse_flows_v1(wb) -> list[tuple[str, float]]:
    """2018-09 to 2019-03: sheet "niededykowane", columns Profile | In | Out | Net."""
    out = []
    for r in _rows(wb["niededykowane"])[2:]:
        name = r[0]
        if name is None or str(name).startswith("Suma"):
            break  # a bond subcategory breakdown follows the first table and would double count
        out.append((str(name), float(r[3])))
    return out


def _parse_flows_v2(wb) -> list[tuple[str, float]]:
    """2019-04 to 2021-03: sheet "02P", blocks All | Non-dedicated | Dedicated."""
    rows = _rows(wb["02P"])
    labels, hdr = rows[0], rows[1]
    nets = [i for i, h in enumerate(hdr) if "FlowNet" in str(h)]
    assert len(nets) == 3, hdr
    # block labels are centred above their columns: check the second block is non-dedicated
    assert any("Niededyk" in str(labels[i]) for i in range(nets[0] + 1, nets[1] + 1)), labels
    out = []
    for r in rows[2:]:
        name = r[0]
        if name is None or str(name).startswith("Suma"):
            break
        out.append((str(name), float(r[nets[1]])))
    return out


def _parse_flows_v3(wb) -> list[tuple[str, float]]:
    """2021-04 onwards: sheet "04T", long format Date | Profile | Dedicated | NAV | In | Out | Net."""
    rows = _rows(wb["04T"])
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Date")
    hdr = rows[hi]
    assert hdr[1] == "Profile" and hdr[2] == "Dedykowane" and hdr[6] == "FlowNet", hdr
    return [(str(r[1]), float(r[6])) for r in rows[hi + 1:] if r and r[1] and r[2] == "Nie"]


def parse_flow_file(path: Path) -> list[tuple[str, float]]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    names = wb.sheetnames
    if "04T" in names:
        return _parse_flows_v3(wb)
    if "02P" in names:
        return _parse_flows_v2(wb)
    if "niededykowane" in names:
        return _parse_flows_v1(wb)
    raise ValueError(f"Unknown flow file format: {path.name} {names}")


def load_flows(raw_dir: Path = RAW_FLOWS) -> pd.DataFrame:
    """Net flows of non-dedicated funds: month, profile, bucket, flow_net (PLN)."""
    with (raw_dir / "_manifest.csv").open() as f:
        manifest = list(csv.DictReader(f))
    recs = []
    for m in manifest:
        for profile, net in parse_flow_file(raw_dir / m["file"]):
            recs.append({"month": m["month"], "profile": profile, "bucket": bucket_of(profile), "flow_net": net})
    return pd.DataFrame(recs)


# ---------------------------------------------------------------- NAV


def parse_rawdata(path: Path) -> pd.DataFrame:
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["RawData"]
    it = ws.iter_rows(values_only=True)
    hdr = next(it)
    idx = {h: i for i, h in enumerate(hdr)}
    need = ["Date", "Fund_Code", "Fund Name", "NAV", "Profile", "Dedicated", "Type"]
    missing = [c for c in need if c not in idx]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")
    recs = [{c: r[idx[c]] for c in need} for r in it if r[idx["Fund_Code"]] is not None]
    df = pd.DataFrame(recs)
    df["month"] = pd.to_datetime(df["Date"].astype(str).str[:10]).dt.strftime("%Y-%m")
    df["NAV"] = pd.to_numeric(df["NAV"], errors="coerce").fillna(0.0)
    return df.drop(columns="Date")


def load_nav(raw_dir: Path = RAW_ASSETS) -> pd.DataFrame:
    """NAV per (month, fund) from all files; on overlaps the newer file wins (data revisions)."""
    with (raw_dir / "_manifest.csv").open() as f:
        manifest = sorted(csv.DictReader(f), key=lambda m: m["month"])
    df = pd.concat([parse_rawdata(raw_dir / m["file"]).assign(file_month=m["month"]) for m in manifest], ignore_index=True)
    # The key is Fund_Code: unique within a month and stable across files. Fund names change between
    # files (rebranding, typos); a name based key double counted assets on overlaps by up to 50%.
    df["fund"] = df["Fund_Code"].astype(str).str.strip()
    df = df.sort_values("file_month").drop_duplicates(["month", "fund"], keep="last")
    df["bucket"] = df["Profile"].map(bucket_of)
    df["dedicated"] = df["Dedicated"].astype(str).str.strip().str.lower().isin(["tak", "yes", "true"])
    return df.rename(columns={"Fund Name": "fund_name", "Fund_Code": "fund_code", "Profile": "profile", "Type": "type", "NAV": "nav"})[
        ["month", "fund", "fund_code", "fund_name", "profile", "bucket", "type", "dedicated", "nav", "file_month"]]


def build(force: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Builds and caches both tables in data/processed/."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    fp, np_ = PROCESSED / "izfia_flows.csv.gz", PROCESSED / "izfia_nav_fund.csv.gz"
    if force or not fp.exists():
        load_flows().to_csv(fp, index=False)
    if force or not np_.exists():
        load_nav().to_csv(np_, index=False)
    flows, nav = pd.read_csv(fp), pd.read_csv(np_)
    nav["dedicated"] = nav["dedicated"].astype(bool)
    return flows, nav


if __name__ == "__main__":
    flows, nav = build(force=True)
    print("flows", flows.shape, flows["month"].min(), "to", flows["month"].max())
    print("nav  ", nav.shape, nav["month"].min(), "to", nav["month"].max())
