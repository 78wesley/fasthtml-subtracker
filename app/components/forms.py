"""
forms.py — Shared subscription form (new & edit).
"""

from fasthtml.common import *

from app import timeutil
from app.cost_utils import FREQUENCIES, BASE_UNITS, frequency_label


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
        Grid(
            Label("Name *", Input(name="name", value=s.get("name", ""),
                  required=True, placeholder="e.g. Netflix")),
            Label("Amount (€) *", Input(name="amount", type="number", step="0.01",
                  min="0", value=s.get("amount", ""), required=True)),
        ),
        Grid(
            Label("Start Date *", Input(name="start_date", type="date",
                  value=s.get("start_date", today_val), required=True)),
            Label("End Date", Input(name="end_date", type="date",
                  value=s.get("end_date") or "")),
        ),
        Label("Frequency", Select(
            *[Option(freq_option_label(u), value=u, selected=(freq == u))
              for u in FREQUENCIES],
            name="frequency", id="frequency-select",
            onchange="document.getElementById('custom-fields').style.display"
                     " = this.value==='custom' ? 'block' : 'none'",
        )),
        Div(
            Grid(
                Label("Repeat every", Input(name="interval", type="number", min="1",
                      value=interval)),
                Label("Unit", Select(
                    *[Option(u.capitalize(), value=u, selected=(base_unit == u))
                      for u in BASE_UNITS],
                    name="base_unit",
                )),
            ),
            Small("Used only for the Custom frequency — e.g. every 6 months.",
                  style="color:var(--pico-muted-color)"),
            id="custom-fields",
            style=f"display:{'block' if is_custom else 'none'}",
        ),
        Label("Category",
              Input(name="category", value=s.get("category") or "",
                    placeholder="e.g. Entertainment", autocomplete="off",
                    **{"list": "category-options"})),
        Datalist(*[Option(value=c) for c in categories], id="category-options"),
        Label("Notes", Textarea(s.get("notes") or "", name="notes", rows=3,
              placeholder="Optional notes…")),
        Label(
            Input(type="checkbox", name="is_active", value="1",
                  checked=(s.get("is_active", 1) in (1, True, "1"))),
            " Active subscription",
        ),
        Button(btn_label, type="submit"),
        method="post", action=action_url,
    )
