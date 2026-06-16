"""
debug.py — Date/time override tools for testing cost/payment calculations.
Gated on settings.manage (super admin).
"""

from fasthtml.common import *

from app import timeutil
from app.authz import require
from app.components import page_title, nav_bar, alert, badge, section_card
from app.styles import PAGE_HEADER, INPUT, btn

ar = APIRouter()


@ar("/debug")
def get(req, session, msg: str = ""):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "settings.manage")): return r
    debug = timeutil.get_debug_date()
    return page_title("Debug"), nav_bar(ctx, "debug"), Main(
        Div(H2("Debug Tools"), cls=PAGE_HEADER),
        section_card(
            H3("Date Override", cls="mb-2"),
            P("Override the application date for testing. All cost calculations, "
              "next-payment dates, and timestamps will use this date.",
              cls="text-sm text-muted-foreground"),
            P(Strong("Current effective date: "),
              Span(debug or timeutil.today_iso(), cls="font-mono"), " ",
              badge("overridden", "warn") if debug else badge("real clock", "info"),
              cls="my-3"),
            Form(
                Label("Set Debug Date",
                      Input(name="debug_date", type="date",
                            value=debug or timeutil.today_iso(), cls=INPUT),
                      cls="grid gap-1.5 text-sm font-medium"),
                Button("Set Date", type="submit", cls=btn()),
                method="post", action="/debug/set-date", cls="grid gap-3 max-w-xs",
            ),
            Form(
                Button("Reset to Real Clock", cls=btn("outline"), type="submit"),
                method="post", action="/debug/clear-date", cls="mt-3",
            ) if debug else "",
            alert(msg, "success") if msg else "",
        ),
    )


@ar("/debug/set-date")
async def post(req, session, debug_date: str):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "settings.manage")): return r
    timeutil.set_debug_date(debug_date)
    return RedirectResponse(f"/debug?msg=Date+set+to+{debug_date}", status_code=303)


@ar("/debug/clear-date")
async def post(req, session):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "settings.manage")): return r
    timeutil.set_debug_date(None)
    return RedirectResponse("/debug?msg=Date+reset+to+real+clock", status_code=303)
