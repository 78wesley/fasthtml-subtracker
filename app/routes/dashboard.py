"""
dashboard.py — Spend dashboard: cost cards, monthly chart, breakdowns.
"""

from fasthtml.common import *

from app import timeutil
from app.db import get_db, get_all_subscriptions, get_price_history
from app.authz import require
from app.cost_utils import year_cost_with_price_history, monthly_costs_for_year
from app.components import (
    page_title, nav_bar, section_card, fmt_eur, category_label,
    bar_chart, hbar_breakdown, MONTH_LABELS,
)

ar = APIRouter()


def _year_analytics(db, ctx, year: int) -> dict:
    """
    Spend analytics for `year`, honouring price history and each subscription's
    active window. Returns period_costs, yearly_total, per_sub, per_cat, months.
    """
    subs = get_all_subscriptions(db, ctx)
    per_sub, per_cat, months, yearly_total = [], {}, [0.0] * 12, 0.0

    for s in subs:
        history = get_price_history(db, s["id"])
        sub_year = year_cost_with_price_history(s, history, year)
        if sub_year <= 0:
            continue
        per_sub.append((s["name"], sub_year))
        cat = category_label(s.get("category"))
        per_cat[cat] = round(per_cat.get(cat, 0.0) + sub_year, 2)
        yearly_total += sub_year
        for i, m in enumerate(monthly_costs_for_year(s, history, year)):
            months[i] += m

    yearly_total = round(yearly_total, 2)
    period_costs = {
        "daily":     round(yearly_total / 365.25, 2),
        "weekly":    round(yearly_total / 52.18,  2),
        "monthly":   round(yearly_total / 12,     2),
        "quarterly": round(yearly_total / 4,      2),
        "yearly":    yearly_total,
    }
    return {
        "period_costs": period_costs,
        "yearly_total": yearly_total,
        "per_sub":      per_sub,
        "per_cat":      list(per_cat.items()),
        "months":       [round(m, 2) for m in months],
    }


@ar("/dashboard")
def get(req, session, year: int = None):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.view")): return r
    db = get_db()

    current_year = timeutil.today().year
    year = year or current_year
    year_range = list(range(current_year - 3, current_year + 3))

    data = _year_analytics(db, ctx, year)

    cost_cards = Div(
        *[Div(
            Div(p.capitalize(), cls="label"),
            Div(fmt_eur(data["period_costs"][p]), cls="amount"),
            # Div(f"{year} total ÷ {p}", cls="sub"),
            cls="cost-card",
        ) for p in ["daily", "weekly", "monthly", "quarterly", "yearly"]],
        cls="cost-cards",
    )

    year_bar = Form(
        Div(
            Label("Year", Select(
                *[Option(str(y), value=str(y), selected=(y == year)) for y in year_range],
                name="year",
                onchange="this.form.submit()",
                style="width:100px",
            )),
            Span(f"Total {year}: ", Strong(fmt_eur(data["yearly_total"])),
                 style="align-self:center; color:var(--pico-muted-color); font-size:.9rem;"),
            cls="year-bar",
        ),
        method="get", action="/dashboard",
    )

    monthly_chart = section_card(
        heading=f"Monthly spend in {year}",
        *[bar_chart(MONTH_LABELS, data["months"])],
    )
    breakdown_charts = Div(
        section_card(
            heading=f"Spend by subscription ({year})",
            *[hbar_breakdown(data["per_sub"])],
        ),
        section_card(
            heading=f"Spend by category ({year})",
            *[hbar_breakdown(data["per_cat"])],
        ),
        cls="charts-grid",
    )

    scope_label = ("All teams" if (ctx.view_all and ctx.is_super)
                   else (ctx.active_team_name or "No team"))
    return page_title("Dashboard"), nav_bar(ctx, "dashboard"), Main(
        Div(H2("Dashboard ", Small(f"· {scope_label}", style="color:var(--pico-muted-color)")),
            A("Manage subscriptions →", href="/manage"),
            cls="page-header"),
        year_bar,
        cost_cards,
        monthly_chart,
        breakdown_charts,
    )
