"""Other public sources: NBP interest rate statistics (MIR) and GUS monthly CPI.

Both files are downloaded as published; the GUS file name changes with each monthly release,
so its link is read from the GUS page first.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .izfia import ROOT, fetch

NBP_MIR_URL = "https://static.nbp.pl/dane/statystyka/inne/stopy_proc_pl_srdW.xlsx"
GUS_CPI_PAGE = ("https://stat.gov.pl/obszary-tematyczne/ceny-handel/wskazniki-cen/wskazniki-cen-towarow-i-uslug-konsumpcyjnych-pot-inflacja-/"
                "miesieczne-wskazniki-cen-towarow-i-uslug-konsumpcyjnych-od-1982-roku/")

NBP_MIR = ROOT / "data" / "raw" / "nbp" / "stopy_proc_pl_srdW.xlsx"
GUS_CPI = ROOT / "data" / "raw" / "gus_cpi" / "cpi_monthly.csv"


def _save(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def download_nbp() -> Path:
    print("NBP MIR:", _save(NBP_MIR, fetch(NBP_MIR_URL))[:12])
    return NBP_MIR


def download_gus() -> Path:
    html = fetch(GUS_CPI_PAGE).decode("utf-8", "replace")
    link = re.search(r'href="([^"]+\.csv)"', html)
    if not link:
        raise RuntimeError("GUS CPI csv link not found on the source page")
    print("GUS CPI:", _save(GUS_CPI, fetch("https://stat.gov.pl" + link.group(1)))[:12])
    return GUS_CPI


if __name__ == "__main__":
    download_nbp()
    download_gus()
