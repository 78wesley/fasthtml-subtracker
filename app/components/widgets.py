"""
widgets.py — Small reusable UI widgets, styled with shadcn utility classes.
"""

from fasthtml.common import *

from app.styles import btn, badge_cls, ALERT

# shadcn DropdownMenu content + item recipes.
_MENU = ("absolute right-0 z-50 mt-1 min-w-[11rem] overflow-hidden rounded-md border "
         "bg-popover p-1 text-popover-foreground shadow-md")
_MENU_ITEM = ("flex w-full items-center rounded-sm px-2 py-1.5 text-sm cursor-pointer "
              "select-none transition-colors hover:bg-accent hover:text-accent-foreground "
              "border-0 bg-transparent text-left")
_MENU_ITEM_DANGER = ("flex w-full items-center rounded-sm px-2 py-1.5 text-sm cursor-pointer "
                     "select-none transition-colors text-destructive hover:bg-destructive/10 "
                     "border-0 bg-transparent text-left")
_SUMMARY = (btn("outline", "sm") + " list-none marker:hidden "
            "[&::-webkit-details-marker]:hidden")


def alert(msg: str, kind: str = "warning") -> Div:
    return Div(msg, cls=ALERT.get(kind, ALERT["warning"]))


def badge(text: str, kind: str = "default") -> Span:
    return Span(text, cls=badge_cls(kind))


def status_badge(is_active: int) -> Span:
    return badge("Active", "active") if is_active else badge("Inactive", "inactive")


def action_btn(label: str, href: str = None, variant: str = "outline",
               hx_post: str = None, hx_confirm: str = None) -> object:
    """A small (sm) shadcn button, either a link or an HTMX button."""
    cls = btn(variant, "sm")
    if href:
        return A(label, href=href, role="button", cls=cls)
    btn_el = Button(label, cls=cls)
    if hx_post:
        btn_el.attrs["hx-post"] = hx_post
        btn_el.attrs["hx-target"] = "body"
        btn_el.attrs["hx-push-url"] = "true"
        if hx_confirm:
            btn_el.attrs["hx-confirm"] = hx_confirm
    return btn_el


def action_menu(sub_id: int, name: str) -> Div:
    """shadcn-style dropdown menu (built on <details>) for the manage table."""
    return Div(
        Details(
            Summary("Actions", cls=_SUMMARY),
            Div(
                A("Edit", href=f"/subscriptions/{sub_id}/edit", cls=_MENU_ITEM),
                A("Price Change", href=f"/subscriptions/{sub_id}/price-change", cls=_MENU_ITEM),
                Button("Delete", cls=_MENU_ITEM_DANGER,
                       hx_post=f"/subscriptions/{sub_id}/delete",
                       hx_confirm=f"Delete '{name}'? (soft-delete)",
                       hx_target="body", hx_push_url="true"),
                cls=_MENU,
            ),
            cls="relative inline-block",
        ),
        cls="relative inline-block",
    )


def pagination_bar(page: int, total_pages: int, base_url: str) -> Div:
    sep = "&" if "?" in base_url else "?"
    prev_btn = (A("← Prev", href=f"{base_url}{sep}page={page-1}", role="button",
                  cls=btn("outline", "sm")) if page > 1 else "")
    next_btn = (A("Next →", href=f"{base_url}{sep}page={page+1}", role="button",
                  cls=btn("outline", "sm")) if page < total_pages else "")
    return Div(prev_btn,
               Span(f"Page {page} of {total_pages}", cls="text-sm text-muted-foreground px-3"),
               next_btn,
               cls="flex items-center gap-2 mt-4")
