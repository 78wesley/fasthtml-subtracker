"""
debug.py — Date/time override tools for testing cost/payment calculations.
Gated on settings.manage (super admin).
"""

from fasthtml.common import *

from app import timeutil
from app.authz import require
from app.components import page_title, nav_bar, alert

ar = APIRouter()


@ar("/debug")
def get(req, session, msg: str = ""):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "settings.manage")): return r
    debug = timeutil.get_debug_date()
    return page_title("Debug"), nav_bar(ctx, "debug"), Main(
        Div(H2("Debug Tools"), cls="page-header"),
        Div(
            H3("Date Override"),
            P("Override the application date for testing. All cost calculations, "
              "next-payment dates, and timestamps will use this date."),
            P(Strong("Current effective date: "),
              Span(debug or timeutil.today_iso(), style="font-family:monospace"),
              Span(" (overridden)", cls="badge badge-warn") if debug else
              Span(" (real clock)", cls="badge badge-info")),
            Form(
                Label("Set Debug Date",
                      Input(name="debug_date", type="date",
                            value=debug or timeutil.today_iso())),
                Button("Set Date", type="submit"),
                method="post", action="/debug/set-date",
            ),
            Form(
                Button("Reset to Real Clock", cls="secondary", type="submit"),
                method="post", action="/debug/clear-date",
            ) if debug else "",
            alert(msg, "success") if msg else "",
            cls="section-card",
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
