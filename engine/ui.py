"""Terminal output in the amb research style (amb.watch).

Monochrome palette with a single accent (#0055FF), section labels in the site's bracket style,
right aligned numbers and fixed column widths so that every table lines up.
"""

from __future__ import annotations

from typing import Iterable, Sequence

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

ACCENT = "#0055ff"
MUTED = "#737373"
GREY = "#a1a1a1"
WIDTH = 104

console = Console(theme=Theme({"acc": f"bold {ACCENT}", "muted": MUTED, "grey": GREY}), highlight=False, width=WIDTH)


def f(x: float, d: int = 1) -> str:
    """Number in report format: thousands separated by commas, fixed decimals."""
    return f"{x:,.{d}f}"


def banner(title: str, subtitle: str = "") -> None:
    head = Table.grid(expand=True)
    head.add_column(justify="left")
    head.add_column(justify="right")
    head.add_row(Text.assemble((" ◍ ", f"bold white on {ACCENT}"), ("  amb research", "bold")), Text("REPORT 01 · NOVEMBER 2026", style=MUTED))
    body = [head, Text(""), Text(title, style="bold")]
    if subtitle:
        body.append(Text(subtitle, style=MUTED))
    console.print()
    console.print(Panel(Group(*body), box=box.SQUARE, border_style=MUTED, padding=(1, 2), width=WIDTH))


def section(num: str, label: str, title: str) -> None:
    console.print()
    console.print(Text(f"[ {num} · {label.upper()} ]", style="acc"))
    console.print(Text(title, style="bold"))
    console.rule(style=MUTED, characters="─")


def stat(value: str, label: str) -> None:
    console.print(Text.assemble((f"  {value:>16}", f"bold {ACCENT}"), (f"   {label}", MUTED)))


def note(text: str) -> None:
    console.print(Text(f"  {text}", style=MUTED))


def table(columns: Sequence[str], rows: Iterable[Sequence], align: Sequence[str] | None = None, highlight: int | None = None, title: str | None = None) -> None:
    """Results table: uppercase headers, right aligned numbers, base scenario row in the accent colour."""
    tb = Table(box=box.SIMPLE_HEAD, header_style=f"bold {GREY}", show_edge=False, pad_edge=False, expand=False,
               title=title.upper() if title else None, title_style=MUTED, title_justify="left")
    for i, c in enumerate(columns):
        tb.add_column(c.upper(), justify=(align[i] if align else ("left" if i == 0 else "right")), min_width=8 if i else 22, no_wrap=True)
    for j, r in enumerate(rows):
        tb.add_row(*[str(x) for x in r], style=(f"bold {ACCENT}" if j == highlight else None))
    console.print(tb)


def summary(levers: Sequence[tuple[str, float, float, float]], total: tuple[float, float, float]) -> None:
    """All levers with a range bar: solid block is the base scenario, the line runs to the aggressive one."""
    mx = max(l[3] for l in levers)
    tb = Table(box=box.SIMPLE_HEAD, header_style=f"bold {GREY}", show_edge=False, pad_edge=False)
    for c, j, w in [("LEVER", "left", 40), ("CONS.", "right", 6), ("BASE", "right", 6), ("AGGR.", "right", 6), ("", "left", 28)]:
        tb.add_column(c, justify=j, min_width=w, no_wrap=True)
    for name, lo, base, hi in levers:
        a, b, c = (max(1, round(v / mx * 26)) for v in (lo, base, hi))
        bar = Text(" " * (a - 1) + "▏", style=MUTED) + Text("█" * max(1, b - a), style=ACCENT) + Text("─" * max(0, c - b), style=MUTED)
        tb.add_row(name, f(lo), Text(f(base), style="bold"), f(hi), bar)
    tb.add_section()
    tb.add_row(Text("TOTAL, PLN BN A YEAR", style="bold"), *[Text(f(x), style=f"bold {ACCENT}") for x in total], "")
    console.print(Panel(tb, border_style=MUTED, box=box.SQUARE, padding=(1, 2), width=WIDTH,
                        title=Text(" RESULT ", style=f"bold white on {ACCENT}"), title_align="left"))
