"""
audit_routes.py — Audit log viewer (paginated, filterable by action).
"""

from fasthtml.common import *

from app.db import get_db, get_audit_log
from app.session import guard, current_user
from app.components import (
    page_title, nav_bar, alert, badge, pagination_bar, json_pretty,
)

ar = APIRouter()


@ar("/audit")
def get(session, action_filter: str = "", page: int = 1):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    db = get_db()

    entries, total = get_audit_log(db, user["id"],
                                   action_filter=action_filter or None, page=page)
    total_pages = max(1, (total + 24) // 25)
    actions = ["LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE", "PRICE_CHANGE"]

    filter_bar = Form(
        Div(
            Label("Action", Select(
                Option("All Actions", value=""),
                *[Option(a, value=a, selected=(action_filter == a)) for a in actions],
                name="action_filter",
            )),
            Button("Filter", type="submit",
                   style="margin-bottom:0; padding:.4rem 1rem"),
            cls="filters",
        ),
        method="get", action="/audit",
    )

    rows = [
        Tr(
            Td(e["timestamp"][:16], cls="nowrap"),
            Td(badge(e["action"], "active"), cls="nowrap"),
            Td(Div(e["entity_type"]),
               Small(e.get("entity_name") or "", style="color:var(--pico-muted-color)")),
            Td(e["description"]),
            Td(Pre(json_pretty(e["old_values"])) if e["old_values"] else "—"),
            Td(Pre(json_pretty(e["new_values"])) if e["new_values"] else "—"),
        )
        for e in entries
    ]

    return page_title("Audit Log"), nav_bar(user["username"], "audit"), Main(
        Div(H2("Audit Log"), cls="page-header"),
        filter_bar,
        Table(
            Thead(Tr(Th("Time"), Th("Action"), Th("Entity"),
                     Th("Description"), Th("Old"), Th("New"))),
            Tbody(*rows),
        ) if rows else P("No audit entries found."),
        pagination_bar(page, total_pages, f"/audit?action_filter={action_filter}"),
    )
