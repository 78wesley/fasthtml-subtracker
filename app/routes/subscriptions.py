"""
subscriptions.py — Create / edit / price-change / detail / soft-delete a subscription.

All reads go through the team-scoped get_subscription(db, ctx, ...); all writes are
gated by a permission via require(ctx, ...) and audited with team context.
"""

from datetime import timedelta

from fasthtml.common import *

from app import timeutil
from app.db import (
    get_db, get_subscription, get_active_price, get_price_history,
    get_audit_for_entity, get_categories, delete_price_history_entry, audit,
)
from app.authz import require, writable_team
from app.cost_utils import (
    FREQUENCIES, BASE_UNITS, frequency_label, get_period_cost, next_payment_date,
)
from app.components import (
    page_title, nav_bar, section_card, collapsible_card, alert, badge, status_badge,
    fmt_eur, category_label, subscription_form,
)
from app.styles import PAGE_HEADER, TABLE, INPUT, TEXTAREA, LINK, MUTED_SM, btn

ar = APIRouter()


def _normalise_cadence(frequency: str, interval: int, base_unit: str) -> tuple:
    """Clean a submitted (frequency, interval, base_unit) triple for storage."""
    frequency = frequency if frequency in FREQUENCIES else "monthly"
    if frequency == "custom":
        base_unit_val = base_unit if base_unit in BASE_UNITS else "monthly"
        interval_val = max(1, interval)
    else:
        base_unit_val = None
        interval_val = 1
    return frequency, interval_val, base_unit_val


# ── New subscription ─────────────────────────────────────────────────────────

@ar("/manage/new")
def get(req, session):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.create")): return r
    if not writable_team(ctx):
        return page_title("New Subscription"), nav_bar(ctx, "manage"), Main(
            Div(H2("Add Subscription"), A("← Manage", href="/manage", cls=LINK), cls=PAGE_HEADER),
            alert("Switch to a specific team (not “All teams”) before adding a "
                  "subscription.", "warning"),
        )
    db = get_db()
    return page_title("New Subscription"), nav_bar(ctx, "manage"), Main(
        Div(H2("Add Subscription"), A("← Manage", href="/manage", cls=LINK), cls=PAGE_HEADER),
        subscription_form("/manage/new", btn_label="Create Subscription",
                          categories=get_categories(db, ctx)),
    )


@ar("/manage/new")
async def post(req, session, name: str, amount: float, start_date: str,
               end_date: str = "", frequency: str = "monthly",
               interval: int = 1, base_unit: str = "", notes: str = "",
               is_active: str = "", category: str = ""):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.create")): return r
    if not writable_team(ctx):
        return RedirectResponse("/teams?msg=Switch+to+a+specific+team+first&msg_kind=warning",
                                status_code=303)
    db = get_db()
    now = timeutil.now_iso()
    frequency, interval_val, base_unit_val = _normalise_cadence(frequency, interval, base_unit)
    is_active_val = 1 if is_active == "1" else 0
    category_val = category.strip() or None

    sub_id = db["subscriptions"].insert({
        "team_id": ctx.active_team_id, "created_by": ctx.user["id"],
        "name": name, "amount": amount, "currency": "EUR",
        "category": category_val, "start_date": start_date,
        "end_date": end_date or None, "notes": notes,
        "frequency": frequency, "interval": interval_val, "base_unit": base_unit_val,
        "is_active": is_active_val, "created_at": now, "updated_at": now,
    }).last_pk

    db["subscription_price_history"].insert({
        "subscription_id": sub_id, "amount": amount, "valid_from": start_date,
        "created_at": now, "created_by": ctx.user["id"],
    })

    audit(ctx, "CREATE", "subscription", sub_id, name,
          f"Created '{name}' €{amount}/{frequency}",
          new_values={"name": name, "amount": amount, "category": category_val,
                      "frequency": frequency, "interval": interval_val,
                      "base_unit": base_unit_val, "start_date": start_date})
    return RedirectResponse("/manage", status_code=303)


# ── Edit subscription ────────────────────────────────────────────────────────

@ar("/subscriptions/{sub_id}/edit")
def get(req, session, sub_id: int):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.edit")): return r
    db = get_db()
    sub = get_subscription(db, ctx, sub_id)
    if not sub:
        return RedirectResponse("/manage", status_code=303)
    return page_title(f"Edit {sub['name']}"), nav_bar(ctx, "manage"), Main(
        Div(H2(f"Edit: {sub['name']}"),
            A("← Back", href=f"/subscriptions/{sub_id}/detail", cls=LINK),
            cls=PAGE_HEADER),
        alert("Editing amount here updates the base record only. "
              "Use 💰 Price Change to record a dated price change.", "warning"),
        subscription_form(f"/subscriptions/{sub_id}/edit", sub=sub,
                          btn_label="Update Subscription",
                          categories=get_categories(db, ctx)),
    )


@ar("/subscriptions/{sub_id}/edit")
async def post(req, session, sub_id: int, name: str, amount: float, start_date: str,
               end_date: str = "", frequency: str = "monthly",
               interval: int = 1, base_unit: str = "", notes: str = "",
               is_active: str = "", category: str = ""):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.edit")): return r
    db = get_db()
    sub = get_subscription(db, ctx, sub_id)
    if not sub:
        return RedirectResponse("/manage", status_code=303)

    frequency, interval_val, base_unit_val = _normalise_cadence(frequency, interval, base_unit)
    is_active_val = 1 if is_active == "1" else 0
    category_val = category.strip() or None
    fields = ["name", "amount", "category", "start_date", "end_date",
              "frequency", "interval", "base_unit", "notes", "is_active"]
    old = {k: sub[k] for k in fields}
    new_vals = {"name": name, "amount": amount, "category": category_val,
                "start_date": start_date, "end_date": end_date or None,
                "frequency": frequency, "interval": interval_val,
                "base_unit": base_unit_val, "notes": notes, "is_active": is_active_val}
    changed = {k: v for k, v in new_vals.items() if str(v) != str(old.get(k, ""))}

    db["subscriptions"].update(sub_id, {**new_vals, "updated_at": timeutil.now_iso()})
    audit(ctx, "UPDATE", "subscription", sub_id, name, f"Updated '{name}'",
          old_values={k: old[k] for k in changed}, new_values=changed)
    return RedirectResponse(f"/subscriptions/{sub_id}/detail", status_code=303)


# ── Price change ─────────────────────────────────────────────────────────────

@ar("/subscriptions/{sub_id}/price-change")
def get(req, session, sub_id: int):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.edit")): return r
    db = get_db()
    sub = get_subscription(db, ctx, sub_id)
    if not sub:
        return RedirectResponse("/manage", status_code=303)

    current_price = get_active_price(db, sub_id, sub["amount"])
    return page_title(f"Price Change – {sub['name']}"), nav_bar(ctx, "manage"), Main(
        Div(H2(f"Price Change: {sub['name']}"),
            A("← Back", href=f"/subscriptions/{sub_id}/detail", cls=LINK),
            cls=PAGE_HEADER),
        P("Current active price: ", Strong(fmt_eur(current_price)), cls="text-sm text-muted-foreground"),
        Form(
            Label("New Amount (€) *",
                  Input(name="new_amount", type="number", step="0.01", min="0",
                        required=True, placeholder="e.g. 12.99", cls=INPUT),
                  cls="grid gap-1.5 text-sm font-medium"),
            Label("Valid From *",
                  Input(name="valid_from", type="date", value=timeutil.today_iso(),
                        required=True, cls=INPUT),
                  cls="grid gap-1.5 text-sm font-medium"),
            Label("Notes", Textarea("", name="notes", rows=2, cls=TEXTAREA,
                  placeholder="Optional reason for price change…"),
                  cls="grid gap-1.5 text-sm font-medium"),
            Button("Save Price Change", type="submit", cls=btn()),
            method="post", action=f"/subscriptions/{sub_id}/price-change",
            cls="grid gap-4 max-w-md",
        ),
    )


@ar("/subscriptions/{sub_id}/price-change")
async def post(req, session, sub_id: int, new_amount: float, valid_from: str, notes: str = ""):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.edit")): return r
    db = get_db()
    sub = get_subscription(db, ctx, sub_id)
    if not sub:
        return RedirectResponse("/manage", status_code=303)

    old_amount = get_active_price(db, sub_id, sub["amount"])
    now = timeutil.now_iso()
    is_past = valid_from < timeutil.today_iso()

    db["subscription_price_history"].insert({
        "subscription_id": sub_id, "amount": new_amount,
        "valid_from": valid_from, "created_at": now, "created_by": ctx.user["id"],
    })
    db["subscriptions"].update(sub_id, {"amount": new_amount, "updated_at": now})

    desc = f"Price change '{sub['name']}': {fmt_eur(old_amount)} → {fmt_eur(new_amount)}, effective {valid_from}"
    if is_past:
        desc += " (backdated)"
    if notes:
        desc += f". {notes}"
    audit(ctx, "PRICE_CHANGE", "subscription", sub_id, sub["name"], desc,
          old_values={"amount": old_amount},
          new_values={"amount": new_amount, "valid_from": valid_from, "notes": notes})
    return RedirectResponse(f"/subscriptions/{sub_id}/detail", status_code=303)


# ── Delete a price-history entry ─────────────────────────────────────────────

@ar("/subscriptions/{sub_id}/price-history/{entry_id}/delete")
async def post(req, session, sub_id: int, entry_id: int):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.edit")): return r
    db = get_db()
    sub = get_subscription(db, ctx, sub_id)
    if not sub:
        return RedirectResponse("/manage", status_code=303)

    entries = list(db["subscription_price_history"].rows_where(
        "id = ? AND subscription_id = ?", [entry_id, sub_id]))
    if not entries:
        return RedirectResponse(f"/subscriptions/{sub_id}/detail", status_code=303)

    entry = entries[0]
    delete_price_history_entry(db, entry_id, sub_id)

    new_active = get_active_price(db, sub_id, sub["amount"])
    db["subscriptions"].update(sub_id, {"amount": new_active, "updated_at": timeutil.now_iso()})

    audit(ctx, "DELETE", "subscription_price_history", entry_id, sub["name"],
          f"Deleted price history entry for '{sub['name']}': "
          f"{fmt_eur(entry['amount'])} (valid from {entry['valid_from']})",
          old_values={"amount": entry["amount"], "valid_from": entry["valid_from"]})
    return RedirectResponse(f"/subscriptions/{sub_id}/detail", status_code=303)


# ── Subscription detail ──────────────────────────────────────────────────────

@ar("/subscriptions/{sub_id}/detail")
def get(req, session, sub_id: int):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.view")): return r
    db = get_db()
    sub = get_subscription(db, ctx, sub_id)
    if not sub:
        return RedirectResponse("/manage", status_code=303)

    today = timeutil.today()
    active_price = get_active_price(db, sub_id, sub["amount"])
    history = get_price_history(db, sub_id)
    audit_entries = get_audit_for_entity(db, sub_id, "subscription")
    freq_lbl = frequency_label(sub["frequency"], sub["interval"] or 1, sub.get("base_unit"))

    can_edit = ctx.can("subscriptions.edit")
    can_delete = ctx.can("subscriptions.delete")
    actions = []
    if can_edit:
        actions += [
            A("✏️ Edit", href=f"/subscriptions/{sub_id}/edit", role="button", cls=btn("outline")),
            A("💰 Price Change", href=f"/subscriptions/{sub_id}/price-change",
              role="button", cls=btn("outline")),
        ]
    if can_delete:
        actions.append(Button("🗑️ Delete",
                       hx_post=f"/subscriptions/{sub_id}/delete",
                       hx_confirm=f"Delete '{sub['name']}'? (soft-delete)",
                       hx_target="body", hx_push_url="true", cls=btn("destructive")))

    def kv(label, value):
        return Div(Div(label, cls="text-xs text-muted-foreground mb-0.5"), Div(value))

    info = section_card(
        H3(sub["name"]),
        Div(
            kv("Amount", Strong(fmt_eur(active_price))),
            kv("Frequency", freq_lbl),
            kv("Start Date", sub["start_date"] or "—"),
            kv("End Date", sub["end_date"] or "—"),
            kv("Status", status_badge(sub["is_active"])),
            kv("Category", badge(category_label(sub.get("category")), "info")),
            kv("Currency", sub["currency"] or "EUR"),
            cls="grid grid-cols-2 sm:grid-cols-3 gap-4 my-4",
        ),
        Div(Div("Notes", cls="text-xs text-muted-foreground mb-0.5"), Div(sub["notes"] or "—")),
        Div(*actions, cls="flex gap-2 flex-wrap mt-4") if actions else "",
    )

    costs = section_card(
        Table(
            Thead(Tr(*[Th(p.capitalize())
                       for p in ["daily", "weekly", "monthly", "quarterly", "yearly"]])),
            Tbody(Tr(*[Td(fmt_eur(get_period_cost(
                              active_price, sub["frequency"], sub["interval"] or 1,
                              sub.get("base_unit"), p)), cls="nowrap")
                       for p in ["daily", "weekly", "monthly", "quarterly", "yearly"]])),
            cls=TABLE,
        ),
        heading="Cost Breakdown (active price)",
    )

    price_rows = [
        Tr(
            Td(fmt_eur(h["amount"]), cls="nowrap"),
            Td(h["valid_from"], cls="nowrap"),
            Td(h.get("username") or "—"),
            Td(h["created_at"][:16], cls="nowrap"),
            Td(Form(
                Button("🗑️ Delete", cls=btn("outline", "sm"),
                       hx_post=f"/subscriptions/{sub_id}/price-history/{h['id']}/delete",
                       hx_confirm=f"Delete price entry {fmt_eur(h['amount'])} from {h['valid_from']}?",
                       hx_target="body", hx_push_url="true"),
                method="post", cls="m-0",
            ) if can_edit else "", cls="nowrap"),
        )
        for h in history
    ]
    price_hist = section_card(
        heading="Price History",
        *([Table(
            Thead(Tr(Th("Amount"), Th("Valid From"), Th("Added By"), Th("Added At"), Th(""))),
            Tbody(*price_rows), cls=TABLE,
        )] if price_rows else [P("No price history yet.", cls=MUTED_SM)]),
    )

    upcoming = []
    if sub.get("start_date") and sub["is_active"]:
        d = next_payment_date(sub["start_date"], sub["frequency"],
                              sub["interval"] or 1, sub.get("base_unit"), today)
        for _ in range(6):
            price_on_day = get_active_price(db, sub_id, sub["amount"], d.isoformat())
            days_from_now = (d - today).days
            label = "today" if days_from_now == 0 else (
                f"in {days_from_now} day{'s' if days_from_now != 1 else ''}"
                if days_from_now > 0 else f"{-days_from_now}d ago"
            )
            upcoming.append(Div(
                Span(d.isoformat()),
                Span(Span(label, cls="text-muted-foreground text-sm mr-2"),
                     Strong(fmt_eur(price_on_day))),
                cls="flex justify-between items-center py-2 border-b last:border-0",
            ))
            d = next_payment_date(sub["start_date"], sub["frequency"],
                                  sub["interval"] or 1, sub.get("base_unit"),
                                  d + timedelta(days=1))

    next_payments = section_card(
        heading="Next Expected Payments",
        *(upcoming if upcoming else [P("Subscription is inactive or has no start date.")]),
    )

    audit_rows = [
        Tr(Td(a["timestamp"][:16], cls="nowrap"), Td(a["action"], cls="nowrap"),
           Td(a["description"]))
        for a in audit_entries
    ]
    # Audit history is hidden from roles without audit access (e.g. viewers).
    audit_section = collapsible_card(
        f"Audit Log ({len(audit_entries)} entries)",
        Table(
            Thead(Tr(Th("Time"), Th("Action"), Th("Description"))),
            Tbody(*audit_rows), cls=TABLE,
        ) if audit_rows else P("No audit entries.", cls=MUTED_SM),
    ) if ctx.can("audit.view") else ""

    return page_title(sub["name"]), nav_bar(ctx, "manage"), Main(
        Div(H2(sub["name"]), A("← Manage", href="/manage", cls=LINK), cls=PAGE_HEADER),
        info, costs, price_hist, next_payments, audit_section,
    )


# ── Soft-delete a subscription ───────────────────────────────────────────────

@ar("/subscriptions/{sub_id}/delete")
async def post(req, session, sub_id: int):
    ctx = req.scope["ctx"]
    if (r := require(ctx, "subscriptions.delete")): return r
    db = get_db()
    sub = get_subscription(db, ctx, sub_id)
    if not sub:
        return RedirectResponse("/manage", status_code=303)

    now = timeutil.now_iso()
    db["subscriptions"].update(sub_id, {
        "deleted_at": now, "deleted_by": ctx.user["id"], "updated_at": now,
    })
    audit(ctx, "DELETE", "subscription", sub_id, sub["name"],
          f"Soft-deleted '{sub['name']}'",
          old_values={"deleted_at": None},
          new_values={"deleted_at": now, "deleted_by": ctx.user["id"]})
    return RedirectResponse("/manage", status_code=303)
