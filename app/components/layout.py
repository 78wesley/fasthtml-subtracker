"""
layout.py — Page chrome styled with shadcn utility classes: nav bar, team switcher,
theme toggle, titles, cards, 403 page.
"""

from fasthtml.common import *

from app import timeutil
from app.components.widgets import alert, dropdown_menu, menu_item_cls
from app.styles import (
    NAV, NAV_LINK, NAV_LINK_ACTIVE, SECTION, PAGE_HEADER, btn, badge_cls,
)


def team_switcher(ctx):
    """
    Active-team picker as a shadcn DropdownMenu (matching the Manage Actions menu).
    Super admins also get an 'All teams' option. Only rendered when there's an actual
    choice (>1 option); with a single team the name is shown as plain text instead.
    """
    if not ctx.teams:
        return Span("No team", cls=badge_cls("warn"))
    options = []  # (value, label, is_selected)
    if ctx.is_super:
        options.append(("__all__", "🌐 All teams", ctx.view_all))
    for t in ctx.teams:
        options.append((str(t["id"]), t["name"],
                        (not ctx.view_all and t["id"] == ctx.active_team_id)))
    if len(options) <= 1:
        return Span(ctx.active_team_name or ctx.teams[0]["name"],
                    cls="text-sm text-muted-foreground")

    current = next((lbl for _, lbl, sel in options if sel), options[0][1])
    items = [
        Form(
            Button(lbl, type="submit", name="team_id", value=val,
                   cls=menu_item_cls(active=sel)),
            method="post", action="/teams/switch", cls="m-0",
        )
        for val, lbl, sel in options
    ]
    return dropdown_menu(current, *items)


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
        link("Audit Log", "/audit", "audit", ctx.can("audit.view")),
        link("Teams", "/teams", "teams", ctx.can("teams.manage")),
        link("Deleted", "/admin/deleted", "deleted", ctx.can("records.view_deleted")),
        link("Users", "/users", "users", ctx.can("users.view")),
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
