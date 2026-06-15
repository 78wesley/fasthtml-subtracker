"""
layout.py — Page chrome: nav bar, titles, section cards.
"""

from fasthtml.common import *

from app import timeutil


def nav_bar(username: str, active: str = "") -> Nav:
    debug = timeutil.get_debug_date()
    debug_pill = Span(f"🕐 Debug date: {debug}", cls="debug-pill") if debug else ""

    def link(label, href, key):
        return A(label, href=href, cls="active" if key == active else None)

    return Nav(
        A("💳 SubTracker", href="/dashboard", cls="brand"),
        link("Dashboard", "/dashboard", "dashboard"),
        link("Manage", "/manage", "manage"),
        link("Audit Log", "/audit", "audit"),
        link("Users", "/users", "users"),
        link("Debug", "/debug", "debug"),
        debug_pill,
        Div(cls="spacer"),
        Span(f"👤 {username}", style="color:var(--pico-muted-color); font-size:.85rem;"),
        A("Logout", href="/logout"),
    )


def page_title(title: str) -> Title:
    return Title(f"{title} – SubTracker")


def section_card(*children, heading: str = None) -> Div:
    inner = [H3(heading)] if heading else []
    inner += list(children)
    return Div(*inner, cls="section-card")


def collapsible_card(heading: str, *children, open_: bool = False) -> Details:
    return Details(
        Summary(heading),
        *children,
        cls="section-card",
        **({"open": True} if open_ else {}),
    )
