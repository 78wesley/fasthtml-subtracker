"""
forms.py — Shared subscription form (new & edit), styled with shadcn utilities.
"""

from fasthtml.common import *

from app import timeutil
from app.components.widgets import select_menu
from app.cost_utils import FREQUENCIES, BASE_UNITS, frequency_label
from app.styles import INPUT, TEXTAREA, LABEL, FIELD, btn


def _field(label, control):
    return Div(Label(label, cls=LABEL), control, cls=FIELD)


def subscription_form(action_url: str, sub: dict = None, btn_label: str = "Save",
                      categories: list = None) -> Form:
    s = sub or {}
    today_val = timeutil.today_iso()
    categories = categories or []

    freq = s.get("frequency", "monthly")
    is_custom = (freq == "custom")
    base_unit = s.get("base_unit") or "monthly"
    interval = s.get("interval") or 1

    def freq_option_label(u):
        return "Custom…" if u == "custom" else frequency_label(u)

    return Form(
        Div(
            _field("Name *", Input(name="name", value=s.get("name", ""),
                   required=True, placeholder="e.g. Netflix", cls=INPUT)),
            _field("Amount (€) *", Input(name="amount", type="number", step="0.01",
                   min="0", value=s.get("amount", ""), required=True, cls=INPUT)),
            cls="grid gap-4 sm:grid-cols-2",
        ),
        Div(
            _field("Start Date *", Input(name="start_date", type="date",
                   value=s.get("start_date", today_val), required=True, cls=INPUT)),
            _field("End Date", Input(name="end_date", type="date",
                   value=s.get("end_date") or "", cls=INPUT)),
            cls="grid gap-4 sm:grid-cols-2",
        ),
        _field("Frequency", select_menu(
            "frequency", [(u, freq_option_label(u)) for u in FREQUENCIES],
            value=freq, width="w-full",
            onchange="document.getElementById('custom-fields').style.display"
                     " = this.value==='custom' ? 'block' : 'none'",
        )),
        Div(
            Div(
                _field("Repeat every", Input(name="interval", type="number", min="1",
                       value=interval, cls=INPUT)),
                _field("Unit", select_menu(
                    "base_unit", [(u, u.capitalize()) for u in BASE_UNITS],
                    value=base_unit, width="w-full")),
                cls="grid gap-4 sm:grid-cols-2",
            ),
            P("Used only for the Custom frequency — e.g. every 6 months.",
              cls="text-sm text-muted-foreground mt-1.5"),
            id="custom-fields", style=f"display:{'block' if is_custom else 'none'}",
        ),
        _field("Category", Input(name="category", value=s.get("category") or "",
               placeholder="e.g. Entertainment", autocomplete="off", cls=INPUT,
               **{"list": "category-options"})),
        Datalist(*[Option(value=c) for c in categories], id="category-options"),
        _field("Notes", Textarea(s.get("notes") or "", name="notes", rows=3,
               placeholder="Optional notes…", cls=TEXTAREA)),
        Label(
            Input(type="checkbox", name="is_active", value="1",
                  checked=(s.get("is_active", 1) in (1, True, "1")),
                  cls="h-4 w-4 rounded border-input", style="accent-color:hsl(var(--primary))"),
            "Active subscription",
            cls="flex items-center gap-2 text-sm font-medium",
        ),
        Button(btn_label, type="submit", cls=btn()),
        method="post", action=action_url, cls="grid gap-4 max-w-2xl",
    )
