"""
charts.py — Inline SVG / CSS charts, styled with shadcn token utilities
(fill-primary / stroke-border / fill-muted-foreground).
"""

from fasthtml.common import *
from fasthtml.svg import Svg, Rect, Line, Text


def bar_chart(labels: list, values: list, *, height: int = 220,
              fmt=lambda v: f"€{v:,.0f}") -> object:
    """Responsive vertical bar chart rendered as inline SVG."""
    if not values or max(values) <= 0:
        return P("No data for this period.", cls="text-muted-foreground text-center py-8")

    n = len(values)
    W, H = 640, height
    pad_l, pad_r, pad_t, pad_b = 48, 12, 12, 28
    plot_w = W - pad_l - pad_r
    plot_h = H - pad_t - pad_b
    vmax = max(values)
    slot = plot_w / n
    bar_w = slot * 0.62

    elems = []
    for i in range(5):
        frac = i / 4
        y = pad_t + plot_h * (1 - frac)
        elems.append(Line(x1=pad_l, y1=y, x2=W - pad_r, y2=y, cls="stroke-border"))
        elems.append(Text(fmt(vmax * frac), x=pad_l - 6, y=y + 3,
                           text_anchor="end", cls="fill-muted-foreground text-[11px]"))

    for i, (lab, val) in enumerate(zip(labels, values)):
        bh = (val / vmax) * plot_h if vmax else 0
        x = pad_l + slot * i + (slot - bar_w) / 2
        y = pad_t + (plot_h - bh)
        elems.append(Rect(x=x, y=y, width=bar_w, height=bh, rx=4,
                          cls="fill-primary transition-[fill] hover:fill-primary/80",
                          title=f"{lab}: {fmt(val)}"))
        elems.append(Text(lab, x=x + bar_w / 2, y=H - pad_b + 16,
                          text_anchor="middle", cls="fill-muted-foreground text-[11px]"))

    return Svg(*elems, viewBox=f"0 0 {W} {H}", cls="w-full h-auto",
               preserveAspectRatio="xMidYMid meet", role="img")


def hbar_breakdown(items: list, *, fmt=lambda v: f"€{v:,.2f}") -> object:
    """Horizontal bar breakdown from [(label, value)], sorted desc by value."""
    items = [(lab, v) for lab, v in items if v > 0]
    if not items:
        return P("No active subscriptions in this year.",
                 cls="text-muted-foreground text-center py-8")
    items.sort(key=lambda t: t[1], reverse=True)
    vmax = items[0][1]
    rows = []
    for lab, val in items:
        pct = (val / vmax) * 100 if vmax else 0
        rows.append(Div(
            Span(lab, cls="break-words leading-snug", title=lab),
            Div(Div(cls="bg-primary h-full rounded-full", style=f"width:{pct:.1f}%"),
                cls="bg-muted rounded-full h-2 overflow-hidden"),
            Span(fmt(val), cls="text-right text-muted-foreground"),
            cls="grid grid-cols-[11rem_1fr_5.5rem] items-center gap-2 mb-2 text-sm",
        ))
    return Div(*rows)
