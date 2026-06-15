"""
debug.py — Date/time override tools for testing cost/payment calculations.
"""

from fasthtml.common import *

from app import timeutil
from app.session import guard, current_user
from app.components import page_title, nav_bar, alert

ar = APIRouter()


@ar("/debug")
def get(session, msg: str = ""):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    debug = timeutil.get_debug_date()
    return page_title("Debug"), nav_bar(user["username"], "debug"), Main(
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
                Button("Reset to Real Clock", cls="secondary outline", type="submit"),
                method="post", action="/debug/clear-date",
            ) if debug else "",
            alert(msg, "success") if msg else "",
            cls="section-card",
        ),
    )


@ar("/debug/set-date")
async def post(session, debug_date: str):
    redir = guard(session)
    if redir: return redir
    timeutil.set_debug_date(debug_date)
    return RedirectResponse(f"/debug?msg=Date+set+to+{debug_date}", status_code=303)


@ar("/debug/clear-date")
async def post(session):
    redir = guard(session)
    if redir: return redir
    timeutil.set_debug_date(None)
    return RedirectResponse("/debug?msg=Date+reset+to+real+clock", status_code=303)
