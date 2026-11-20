"""IZFiA source data: monthly fund assets and net flows by category.

Source: https://www.izfa.pl/raporty (category "Sprzedaż dane", id 25, and "Aktywa dane", id 24).
Each monthly flow file contains flows by fund profile for a single month only, so the history is
assembled from the full archive. Every download is recorded in a manifest with its URL, download
time and SHA-256 checksum.
"""

from __future__ import annotations

import csv
import hashlib
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.izfa.pl"
LIST_URL = BASE + "/raporty?pub_year=All&pub_month=All&field_kategoria_target_id={cat}&page={page}"
CAT_FLOWS = 25
CAT_ASSETS = 24
UA = "Mozilla/5.0 (amb-research)"

ROOT = Path(__file__).resolve().parents[2]
RAW_FLOWS = ROOT / "data" / "raw" / "izfia_flows"
RAW_ASSETS = ROOT / "data" / "raw" / "izfia_assets"

_DATE_PATTERNS = [
    re.compile(r"(?P<y>20\d{2})-?(?P<m>\d{2})-?(?P<d>\d{2})"),  # 20260131, 2018-07-31
    re.compile(r"(?P<d>\d{2})-(?P<m>\d{2})-(?P<y>20\d{2})"),  # 31-05-2018
]


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def month_of(filename: str) -> str | None:
    """Reporting month (YYYY-MM) parsed from an IZFiA file name."""
    name = filename.rsplit("/", 1)[-1]
    for pat in _DATE_PATTERNS:
        m = pat.search(name)
        if m:
            return f"{m['y']}-{m['m']}"
    return None


def crawl_links(cat: int, max_pages: int = 60, pause: float = 0.5) -> list[str]:
    """All data file links in one category of the IZFiA report archive."""
    links: set[str] = set()
    for page in range(max_pages):
        html = fetch(LIST_URL.format(cat=cat, page=page)).decode("utf-8", "replace")
        found = re.findall(r'href="([^"]+\.(?:xlsx?|xlsm))"', html)
        if not found:
            break
        links.update(found)
        time.sleep(pause)
    return sorted(BASE + l if l.startswith("/") else l for l in links)


def pick_monthly_flow_files(links: list[str], since: str = "2018-09") -> dict[str, str]:
    """One flow file per month (consistent format from 2018-09); the latest upload wins on duplicates."""
    out: dict[str, str] = {}
    for url in sorted(links):  # the /files/YYYY-MM/ path grows with the upload date
        name = url.rsplit("/", 1)[-1].lower()
        if "przeplywy" not in name:
            continue
        m = month_of(name)
        if m and m >= since:
            out[m] = url
    return dict(sorted(out.items()))


def pick_asset_files(links: list[str], since: str = "2018-06") -> dict[str, str]:
    """June and December asset files plus the latest one.

    Each file holds about 13 months of fund level NAV, so two files a year give full coverage
    with overlap (the overlap also captures later data revisions).
    """
    by_month: dict[str, str] = {}
    for url in sorted(links):
        name = url.rsplit("/", 1)[-1].lower()
        if "aktywa" not in name or "dane" not in name:
            continue
        m = month_of(name)
        if m and m >= since:
            by_month[m] = url
    latest = max(by_month)
    return {m: u for m, u in sorted(by_month.items()) if m[5:] in ("06", "12") or m == latest}


def download(files: dict[str, str], dest: Path, pause: float = 0.3) -> Path:
    """Downloads missing files and writes a manifest with download time and SHA-256."""
    dest.mkdir(parents=True, exist_ok=True)
    manifest = dest / "_manifest.csv"
    rows = {}
    if manifest.exists():
        with manifest.open() as f:
            rows = {r["month"]: r for r in csv.DictReader(f)}
    for month, url in files.items():
        path = dest / f"{month}_{url.rsplit('/', 1)[-1]}"
        if not path.exists():
            path.write_bytes(fetch(url))
            time.sleep(pause)
            rows[month] = {
                "month": month,
                "url": url,
                "file": path.name,
                "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["month", "url", "file", "downloaded_at", "sha256"])
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: r["month"]))
    return manifest


def download_all() -> None:
    flows = pick_monthly_flow_files(crawl_links(CAT_FLOWS))
    print(f"flows: {len(flows)} months, {min(flows)} to {max(flows)}")
    download(flows, RAW_FLOWS)
    assets = pick_asset_files(crawl_links(CAT_ASSETS))
    print(f"assets: {len(assets)} files, {min(assets)} to {max(assets)}")
    download(assets, RAW_ASSETS)


if __name__ == "__main__":
    download_all()
