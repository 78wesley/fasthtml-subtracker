"""
app.components — stable import surface for all shared UI primitives.
"""

from app.components.fmt import (
    MONTH_LABELS, fmt_eur, category_label, truncate, json_pretty,
)
from app.components.widgets import (
    alert, badge, status_badge, action_btn, action_menu, pagination_bar,
)
from app.components.layout import (
    nav_bar, page_title, section_card, collapsible_card, team_switcher, forbidden_page,
)
from app.components.charts import bar_chart, hbar_breakdown
from app.components.forms import subscription_form

__all__ = [
    "MONTH_LABELS", "fmt_eur", "category_label", "truncate", "json_pretty",
    "alert", "badge", "status_badge", "action_btn", "action_menu", "pagination_bar",
    "nav_bar", "page_title", "section_card", "collapsible_card",
    "bar_chart", "hbar_breakdown", "subscription_form",
]
