"""
widgets.py — Small reusable UI widgets.
"""

from fasthtml.common import *


def alert(msg: str, kind: str = "warning") -> Div:
    return Div(msg, cls=f"alert-{kind}")


def badge(text: str, kind: str = "active") -> Span:
    return Span(text, cls=f"badge badge-{kind}")


def status_badge(is_active: int) -> Span:
    return badge("Active", "active") if is_active else badge("Inactive", "inactive")


def action_btn(label: str, href: str = None, cls: str = "secondary",
               hx_post: str = None, hx_confirm: str = None) -> object:
    """Return a small action button, either a link or an HTMX button."""
    btn = Button(label, cls=cls, style="padding:.25rem .6rem; font-size:.8rem; margin:0;")
    if href:
        return A(btn, href=href)
    if hx_post:
        btn.attrs["hx-post"] = hx_post
        btn.attrs["hx-target"] = "body"
        btn.attrs["hx-push-url"] = "true"
        if hx_confirm:
            btn.attrs["hx-confirm"] = hx_confirm
        return btn
    return btn


def action_menu(sub_id: int, name: str) -> Div:
    """Dropdown action menu for the manage table."""
    return Div(
        Details(
            Summary("Actions"),
            Div(
                A("Edit", href=f"/subscriptions/{sub_id}/edit"),
                A("Price Change", href=f"/subscriptions/{sub_id}/price-change"),
                Div(
                    Button("Delete",
                           hx_post=f"/subscriptions/{sub_id}/delete",
                           hx_confirm=f"Delete '{name}'? (soft-delete)",
                           hx_target="body", hx_push_url="true"),
                    cls="drop-danger",
                ),
                cls="drop-list",
            ),
        ),
        cls="action-menu",
    )


def pagination_bar(page: int, total_pages: int, base_url: str) -> Div:
    sep = "&" if "?" in base_url else "?"
    prev_btn = A(Button("← Prev", cls="secondary"),
                 href=f"{base_url}{sep}page={page-1}") if page > 1 else ""
    next_btn = A(Button("Next →", cls="secondary"),
                 href=f"{base_url}{sep}page={page+1}") if page < total_pages else ""
    return Div(prev_btn,
               Span(f" Page {page} of {total_pages} ", style="padding:0 .75rem"),
               next_btn,
               style="display:flex; align-items:center; margin-top:1rem;")
