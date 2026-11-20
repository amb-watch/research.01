"""Charts in the amb research style (matplotlib): Switzer and Geist Mono, black, greys and #0055FF.

Every chart is saved as SVG (for the PDF report) and PNG (for the README and previews) in report/charts/.
Fonts are loaded from report/fonts/ when present and fall back to the system sans serif otherwise.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "report" / "fonts"
OUT = ROOT / "report" / "charts"

INK, INK4, G6, G5, G4, G3, G2, G1 = "#0a0a0a", "#404040", "#525252", "#737373", "#a1a1a1", "#d4d4d4", "#e5e5e5", "#f5f5f5"
BLUE, BLUE_SOFT = "#0055ff", "#80aaff"

for font in FONTS.glob("*.otf"):
    fm.fontManager.addfont(str(font))
_names = {f.name for f in fm.fontManager.ttflist}
SANS = "Switzer" if "Switzer" in _names else "DejaVu Sans"
MONO = "Geist Mono" if "Geist Mono" in _names else "DejaVu Sans Mono"

plt.rcParams.update({
    "font.family": SANS, "font.size": 9.5, "text.color": INK,
    "axes.edgecolor": G3, "axes.labelcolor": G6, "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": G2, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "xtick.color": G6, "ytick.color": G6, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "xtick.major.size": 0, "ytick.major.size": 0,
    "legend.frameon": False, "legend.fontsize": 8.5, "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.08, "svg.fonttype": "none",
})

fmt = lambda d=1: FuncFormatter(lambda x, _: f"{x:,.{d}f}")  # noqa: E731
num = lambda x, d=1: f"{x:,.{d}f}"  # noqa: E731


def fig(w: float = 7.2, h: float = 3.6, kicker: str | None = None, title: str | None = None):
    f, ax = plt.subplots(figsize=(w, h))
    if kicker:
        f.text(0.0, 1.16, kicker.upper(), fontfamily=MONO, fontsize=7.5, color=BLUE, fontweight="medium", transform=ax.transAxes)
    if title:
        f.text(0.0, 1.04, title, fontsize=11, color=INK, transform=ax.transAxes, va="bottom")
    return f, ax


def source(ax, text: str, y: float = -0.2):
    ax.text(0.0, y, text, transform=ax.transAxes, fontfamily=MONO, fontsize=6.5, color=G5, va="top")


def save(f, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    f.savefig(OUT / f"{name}.svg")
    f.savefig(OUT / f"{name}.png", dpi=170)
    plt.close(f)
    return OUT / f"{name}.svg"
