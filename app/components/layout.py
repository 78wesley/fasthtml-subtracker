"""
layout.py — Page chrome styled with shadcn utility classes: nav bar, team switcher,
theme toggle, titles, cards, 403 page.
"""

from fasthtml.common import *

from app import timeutil
from app.components.widgets import alert
from app.styles import (
    NAV, NAV_LINK, NAV_LINK_ACTIVE, SELECT_SM, SECTION, PAGE_HEADER, btn, badge_cls,
)


def team_switcher(ctx):
    """Active-team <select> (auto-submits). Super admins also get an 'All teams' option."""
    if not ctx.teams:
        return Span("No team", cls=badge_cls("warn"))
    opts = []
    if ctx.is_super:
        opts.append(Option("🌐 All teams", value="__all__", selected=ctx.view_all))
    for t in ctx.teams:
        opts.append(Option(t["name"], value=str(t["id"]),
                           selected=(not ctx.view_all and t["id"] == ctx.active_team_id)))
    return Form(
        Select(*opts, name="team_id", onchange="this.form.submit()", cls=SELECT_SM + " w-auto"),
        method="post", action="/teams/switch", cls="m-0",
    )


def theme_toggle() -> Button:
    """Light/dark switch — flips the `.dark` class on <html> (see THEME_JS)."""
    return Button(
        Span("🌙", cls="theme-icon-light"), Span("☀️", cls="theme-icon-dark"),
        cls=btn("outline", "icon"), type="button",
        onclick="toggleTheme()", title="Toggle light / dark theme",
        **{"aria-label": "Toggle light / dark theme"},
    )


def nav_bar(ctx, active: str = "") -> Nav:
    debug = timeutil.get_debug_date()
    debug_pill = Span(f"🕐 {debug}", cls=badge_cls("warn")) if debug else ""

    def link(label, href, key, show=True):
        if not show:
            return ""
        return A(label, href=href, cls=NAV_LINK_ACTIVE if key == active else NAV_LINK)

    role_label = ctx.global_role.replace("_", " ").title()
    return Nav(
        A("💳 SubTracker", href="/dashboard", cls="font-bold text-base mr-1"),
        link("Dashboard", "/dashboard", "dashboard", ctx.can("subscriptions.view")),
        link("Manage", "/manage", "manage", ctx.can("subscriptions.view")),
        link("Audit Log", "/audit", "audit"),
        link("Teams", "/teams", "teams", ctx.can("teams.view")),
        link("Deleted", "/admin/deleted", "deleted", ctx.can("records.view_deleted")),
        link("Users", "/users", "users", ctx.can("users.view")),
        link("Roles", "/admin/roles", "roles", ctx.can("settings.manage")),
        link("Debug", "/debug", "debug", ctx.can("settings.manage")),
        debug_pill,
        Div(cls="flex-1"),
        team_switcher(ctx),
        Span(role_label, cls=badge_cls("secondary")),
        Span(f"👤 {ctx.username}", cls="text-sm text-muted-foreground"),
        theme_toggle(),
        A("Logout", href="/logout", cls=NAV_LINK),
        cls=NAV,
    )


def page_title(title: str) -> Title:
    return Title(f"{title} – SubTracker")


def forbidden_page(ctx, missing):
    """Friendly 'not authorized' page shown when a permission check fails."""
    needs = ", ".join(missing) if missing else "additional permissions"
    return page_title("Not allowed"), nav_bar(ctx), Main(
        Div(H2("🚫 Not authorized"), cls=PAGE_HEADER),
        alert(f"You don't have permission to do this (needs: {needs}). "
              "Ask a team admin or super admin for access.", "error"),
        P(A("← Back to dashboard", href="/dashboard")),
    )


def section_card(*children, heading: str = None) -> Div:
    inner = [H3(heading, cls="mb-3")] if heading else []
    inner += list(children)
    return Div(*inner, cls=SECTION)


def collapsible_card(heading: str, *children, open_: bool = False) -> Details:
    return Details(
        Summary(heading, cls="cursor-pointer font-semibold"),
        Div(*children, cls="mt-4"),
        cls=SECTION,
        **({"open": True} if open_ else {}),
    )
