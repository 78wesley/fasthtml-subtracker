"""
manage.py — Subscription list (search/filter), CSV export, CSV/bulk import.
"""

import csv
import io
from datetime import date

from fasthtml.common import *
from starlette.responses import Response as StarletteResponse
from starlette.datastructures import UploadFile

from app import timeutil
from app.db import (
    get_db, get_all_subscriptions, get_categories, get_active_price, write_audit_log,
)
from app.session import guard, current_user
from app.cost_utils import FREQUENCIES, BASE_UNITS, frequency_label, get_annual_cost
from app.components import (
    page_title, nav_bar, section_card, alert, badge, status_badge, action_menu,
    fmt_eur, category_label,
)

ar = APIRouter()


# ── Manage list ──────────────────────────────────────────────────────────────

@ar("/manage")
def get(session, q: str = "", status: str = "all", category: str = ""):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    db = get_db()

    all_categories = get_categories(db, user["id"])
    subs = get_all_subscriptions(db, user["id"],
                                 filter_active=status if status != "all" else None,
                                 search=q or None,
                                 category=category or None)
    rows = []
    for s in subs:
        price = get_active_price(db, s["id"], s["amount"])
        notes = s["notes"] or ""
        rows.append(Tr(
            Td(A(s["name"], href=f"/subscriptions/{s['id']}/detail")),
            Td(badge(category_label(s.get("category")), "info"), cls="nowrap"),
            Td(fmt_eur(price), cls="nowrap"),
            Td(frequency_label(s["frequency"], s["interval"] or 1, s.get("base_unit")),
               cls="nowrap"),
            Td(s["start_date"] or "—", cls="nowrap"),
            Td(s["end_date"] or "—", cls="nowrap"),
            Td(status_badge(s["is_active"]), cls="nowrap"),
            Td(Div(notes, cls="cell-clip", title=notes) if notes else "—"),
            Td(action_menu(s["id"], s["name"]), cls="nowrap"),
        ))

    table = (
        Table(
            Thead(Tr(Th("Name"), Th("Category"), Th("Amount"), Th("Frequency"),
                     Th("Start"), Th("End"), Th("Status"), Th("Notes"), Th("Actions"))),
            Tbody(*rows),
        ) if rows else P("No subscriptions found. ", A("Add one →", href="/manage/new"))
    )

    filter_bar = Form(
        Div(
            Label("Search", Input(name="q", value=q, placeholder="Search name…",
                                  style="width:200px")),
            Label("Status", Select(
                Option("All",      value="all",      selected=(status == "all")),
                Option("Active",   value="active",   selected=(status == "active")),
                Option("Inactive", value="inactive", selected=(status == "inactive")),
                name="status", style="width:130px",
            )),
            Label("Category", Select(
                Option("All", value="", selected=(not category)),
                *[Option(c, value=c, selected=(category == c)) for c in all_categories],
                name="category", style="width:160px",
            )),
            Button("Filter", type="submit",
                   style="margin-bottom:0; padding:.4rem 1rem"),
            A(Button("＋ Add", type="button", style="margin-bottom:0; padding:.4rem 1rem"),
              href="/manage/new"),
            A(Button("⬇ CSV", type="button", cls="secondary outline",
                     style="margin-bottom:0; padding:.4rem 1rem"),
              href="/manage/export"),
            A(Button("⬆ Import", type="button", cls="secondary outline",
                     style="margin-bottom:0; padding:.4rem 1rem"),
              href="/manage/import"),
            cls="filters",
        ),
        method="get", action="/manage",
    )

    return page_title("Manage"), nav_bar(user["username"], "manage"), Main(
        Div(H2("Manage Subscriptions"), cls="page-header"),
        filter_bar,
        table,
    )


# ── CSV export ───────────────────────────────────────────────────────────────

@ar("/manage/export")
def get(session):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    db = get_db()
    subs = get_all_subscriptions(db, user["id"])

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID", "Name", "Category", "Active Price (€)", "Currency", "Frequency",
                "Start Date", "End Date", "Active", "Notes", "Annual Cost (€)"])
    for s in subs:
        price = get_active_price(db, s["id"], s["amount"])
        annual = get_annual_cost(price, s["frequency"], s["interval"] or 1, s.get("base_unit"))
        w.writerow([
            s["id"], s["name"], category_label(s.get("category")),
            f"{price:.2f}", s["currency"] or "EUR",
            frequency_label(s["frequency"], s["interval"] or 1, s.get("base_unit")),
            s["start_date"] or "", s["end_date"] or "",
            "Yes" if s["is_active"] else "No",
            s["notes"] or "", f"{annual:.2f}",
        ])

    return StarletteResponse(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=subscriptions.csv"},
    )


# ── CSV / bulk import ────────────────────────────────────────────────────────

IMPORT_COLUMNS = ["name", "amount", "category", "start_date", "end_date",
                  "frequency", "interval", "base_unit", "notes", "is_active"]

IMPORT_SAMPLE = (
    "name,amount,category,start_date,end_date,frequency,interval,base_unit,notes,is_active\n"
    "Netflix,12.99,Entertainment,2024-01-15,,monthly,,,Standard plan,1\n"
    "Spotify,5.99,Entertainment,2023-06-01,,monthly,,,Student plan,1\n"
    "Domain renewal,15.00,Hosting,2024-03-10,,yearly,,,,1\n"
    "Insurance,90.00,Finance,2024-02-01,,custom,6,monthly,Every 6 months,1\n"
)

_TRUE_VALUES  = {"1", "yes", "true", "y", "active", "on"}
_FALSE_VALUES = {"0", "no", "false", "n", "inactive", "off"}


def _parse_import_csv(text: str) -> tuple:
    """
    Parse pasted/uploaded CSV text into subscription dicts.
    Returns (valid_rows, errors). Only `name` and `amount` are required.
    """
    text = (text or "").strip()
    if not text:
        return [], ["No CSV content provided."]

    try:
        reader = csv.DictReader(io.StringIO(text))
    except Exception as e:
        return [], [f"Could not parse CSV: {e}"]

    if not reader.fieldnames:
        return [], ["CSV has no header row."]

    header_map = {h: (h or "").strip().lower() for h in reader.fieldnames}
    known = set(IMPORT_COLUMNS)
    if not (known & set(header_map.values())):
        return [], [f"No recognised columns found. Expected a header with at "
                    f"least: name, amount. Got: {', '.join(reader.fieldnames)}"]

    today_val = timeutil.today_iso()
    valid, errors = [], []

    def norm(row, key, default=""):
        for raw, low in header_map.items():
            if low == key:
                return (row.get(raw) or "").strip()
        return default

    for i, raw_row in enumerate(reader, start=2):  # row 1 is the header
        name = norm(raw_row, "name")
        if not name:
            errors.append(f"Row {i}: missing name — skipped.")
            continue

        amount_str = norm(raw_row, "amount")
        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Row {i} ('{name}'): invalid amount '{amount_str}' — skipped.")
            continue

        frequency = norm(raw_row, "frequency").lower() or "monthly"
        if frequency not in FREQUENCIES:
            errors.append(f"Row {i} ('{name}'): unknown frequency '{frequency}' "
                          f"(expected one of {', '.join(FREQUENCIES)}) — skipped.")
            continue

        interval_str = norm(raw_row, "interval") or "1"
        try:
            interval = max(1, int(float(interval_str)))
        except ValueError:
            errors.append(f"Row {i} ('{name}'): invalid interval '{interval_str}' — skipped.")
            continue

        base_unit = norm(raw_row, "base_unit").lower() or None
        if frequency == "custom":
            if base_unit not in BASE_UNITS:
                errors.append(f"Row {i} ('{name}'): custom frequency needs base_unit "
                              f"one of {', '.join(BASE_UNITS)} — skipped.")
                continue
        else:
            base_unit = None
            interval = 1

        start_date = norm(raw_row, "start_date") or today_val
        end_date = norm(raw_row, "end_date")
        try:
            date.fromisoformat(start_date)
            if end_date:
                date.fromisoformat(end_date)
        except ValueError:
            errors.append(f"Row {i} ('{name}'): dates must be YYYY-MM-DD — skipped.")
            continue

        is_active_raw = norm(raw_row, "is_active").lower()
        if is_active_raw == "" or is_active_raw in _TRUE_VALUES:
            is_active = 1  # blank defaults to active
        elif is_active_raw in _FALSE_VALUES:
            is_active = 0
        else:
            errors.append(f"Row {i} ('{name}'): invalid is_active '{is_active_raw}' — skipped.")
            continue

        valid.append({
            "name": name,
            "amount": amount,
            "category": norm(raw_row, "category") or None,
            "start_date": start_date,
            "end_date": end_date or None,
            "frequency": frequency,
            "interval": interval,
            "base_unit": base_unit,
            "notes": norm(raw_row, "notes"),
            "is_active": is_active,
        })

    return valid, errors


def import_page(user, *, result=None):
    """Render the import form, optionally with a result summary panel."""
    result_panel = ""
    if result is not None:
        imported, errors = result
        blocks = []
        if imported:
            blocks.append(alert(f"✅ Imported {imported} "
                                f"subscription{'s' if imported != 1 else ''}.", "success"))
        elif not errors:
            blocks.append(alert("Nothing to import.", "warning"))
        if errors:
            blocks.append(Div(
                P(Strong(f"{len(errors)} row{'s' if len(errors) != 1 else ''} skipped:")),
                Ul(*[Li(e) for e in errors]),
                cls="alert-warning",
            ))
        result_panel = Div(*blocks)

    return page_title("Import"), nav_bar(user["username"], "manage"), Main(
        Div(H2("Import Subscriptions"), A("← Manage", href="/manage"), cls="page-header"),
        result_panel,
        section_card(
            Form(
                Label("CSV file",
                      Input(type="file", name="file", accept=".csv,text/csv")),
                Label("…or paste CSV here",
                      Textarea("", name="csv_text", rows=8,
                               placeholder=IMPORT_SAMPLE)),
                Button("Import", type="submit"),
                method="post", action="/manage/import",
                enctype="multipart/form-data",
            ),
            heading="Upload or paste CSV",
        ),
        section_card(
            P("The first row must be a header. Recognised columns "
              "(only ", Strong("name"), " and ", Strong("amount"),
              " are required):"),
            Ul(
                Li(Strong("name"), " — subscription name"),
                Li(Strong("amount"), " — price per billing period, e.g. 12.99"),
                Li(Strong("category"), " — optional, e.g. Entertainment"),
                Li(Strong("start_date"), " — YYYY-MM-DD, defaults to today"),
                Li(Strong("end_date"), " — YYYY-MM-DD, optional"),
                Li(Strong("frequency"), f" — one of: {', '.join(FREQUENCIES)} (default monthly)"),
                Li(Strong("interval"), " — for custom only: bill every N units (default 1)"),
                Li(Strong("base_unit"), f" — for custom only: one of {', '.join(BASE_UNITS)}"),
                Li(Strong("notes"), " — optional free text"),
                Li(Strong("is_active"), " — 1/yes/true or 0/no/false (default active)"),
            ),
            P(Small("Column order doesn't matter; unknown columns are ignored. "
                    "Invalid rows are skipped and reported — valid rows still import.")),
            P(Strong("Example:")),
            Pre(IMPORT_SAMPLE),
            heading="Format",
        ),
    )


@ar("/manage/import")
def get(session):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    return import_page(user)


@ar("/manage/import")
async def post(session, csv_text: str = "", file: UploadFile = None):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    db = get_db()

    # Prefer an uploaded file; fall back to pasted text.
    text = ""
    if file is not None and getattr(file, "filename", ""):
        text = (await file.read()).decode("utf-8", errors="replace")
    if not text.strip():
        text = csv_text

    rows, errors = _parse_import_csv(text)

    imported = 0
    for r in rows:
        now = timeutil.now_iso()
        sub_id = db["subscriptions"].insert({
            "user_id": user["id"], "name": r["name"], "amount": r["amount"],
            "currency": "EUR", "category": r["category"],
            "start_date": r["start_date"], "end_date": r["end_date"],
            "notes": r["notes"], "frequency": r["frequency"],
            "interval": r["interval"], "base_unit": r["base_unit"],
            "is_active": r["is_active"], "created_at": now, "updated_at": now,
        }).last_pk
        db["subscription_price_history"].insert({
            "subscription_id": sub_id, "amount": r["amount"],
            "valid_from": r["start_date"], "created_at": now, "created_by": user["id"],
        })
        write_audit_log(user["id"], user["username"], "CREATE", "subscription",
                        sub_id, r["name"],
                        f"Imported '{r['name']}' €{r['amount']}/{r['frequency']}",
                        new_values={"name": r["name"], "amount": r["amount"],
                                    "category": r["category"], "frequency": r["frequency"],
                                    "interval": r["interval"], "base_unit": r["base_unit"],
                                    "start_date": r["start_date"]})
        imported += 1

    return import_page(user, result=(imported, errors))
