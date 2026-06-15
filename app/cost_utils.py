"""
cost_utils.py — Billing frequency helpers, cost normalisation, next-payment dates.

Frequency model
---------------
A subscription's cadence is described by three fields:
    frequency  — one of FREQUENCIES
    interval   — integer N (only meaningful for "custom"; named presets imply 1)
    base_unit  — for "custom" only: the unit the interval counts (BASE_UNITS)

Named presets (daily/weekly/monthly/quarterly/yearly) always mean "every 1 unit".
"custom" means "every <interval> <base_unit>" — e.g. every 6 months, every 2 weeks.
`resolve()` collapses the triple to an (effective_unit, n) pair that the math uses.
"""

import calendar
from datetime import date, timedelta


# ── Frequency model ──────────────────────────────────────────────────────────

FREQUENCIES = ["daily", "weekly", "monthly", "quarterly", "yearly", "custom"]
BASE_UNITS  = ["daily", "weekly", "monthly", "yearly"]

DAYS_PER_UNIT = {
    "daily":     1,
    "weekly":    7,
    "monthly":   30.4375,
    "quarterly": 91.3125,
    "yearly":    365.25,
}

# Output periods used by the cost-breakdown cards (NOT input frequencies).
PERIOD_DIVISORS = {
    "daily":     365.25,
    "weekly":    52.18,
    "monthly":   12,
    "quarterly": 4,
    "yearly":    1,
}

_UNIT_NOUN = {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"}


def resolve(frequency: str, interval: int = 1, base_unit: str = None) -> tuple:
    """Collapse (frequency, interval, base_unit) to an (effective_unit, n) pair."""
    if frequency == "custom":
        unit = base_unit if base_unit in BASE_UNITS else "monthly"
        return unit, max(1, int(interval or 1))
    if frequency not in DAYS_PER_UNIT:
        frequency = "monthly"
    return frequency, 1


# ── Cost normalisation ───────────────────────────────────────────────────────

def get_annual_cost(amount: float, frequency: str, interval: int = 1,
                    base_unit: str = None) -> float:
    unit, n = resolve(frequency, interval, base_unit)
    days_between = DAYS_PER_UNIT[unit] * n
    return round(amount * (365.25 / days_between), 2)


def get_period_cost(amount: float, frequency: str, interval: int,
                    base_unit: str, period: str) -> float:
    return round(get_annual_cost(amount, frequency, interval, base_unit)
                 / PERIOD_DIVISORS[period], 2)


def frequency_label(frequency: str, interval: int = 1, base_unit: str = None) -> str:
    named = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly",
             "quarterly": "Quarterly", "yearly": "Yearly"}
    if frequency != "custom":
        return named.get(frequency, (frequency or "").capitalize())
    unit = base_unit if base_unit in _UNIT_NOUN else "monthly"
    n = max(1, int(interval or 1))
    noun = _UNIT_NOUN[unit]
    return f"Every {noun}" if n == 1 else f"Every {n} {noun}s"


# ── Interval arithmetic (no external deps) ───────────────────────────────────

def _advance(d: date, unit: str, n: int) -> date:
    """Advance a date by n billing units using only stdlib."""
    if unit == "daily":
        return d + timedelta(days=n)
    if unit == "weekly":
        return d + timedelta(weeks=n)
    if unit in ("monthly", "quarterly"):
        months = (1 if unit == "monthly" else 3) * n
        m = d.month - 1 + months
        year = d.year + m // 12
        month = m % 12 + 1
        day = min(d.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
    if unit == "yearly":
        year = d.year + n
        day = min(d.day, calendar.monthrange(year, d.month)[1])
        return date(year, d.month, day)
    raise ValueError(f"Unknown unit: {unit}")


def next_payment_date(start_date_str: str, frequency: str, interval: int,
                      base_unit: str = None, reference: date = None) -> date:
    """Return the next payment date >= reference (defaults to today)."""
    ref = reference or date.today()
    unit, n = resolve(frequency, interval, base_unit)
    d = date.fromisoformat(start_date_str)
    if d >= ref:
        return d
    while d < ref:
        d = _advance(d, unit, n)
    return d


def upcoming_payments(subs: list, price_fn, days: int = 30,
                      reference: date = None) -> list:
    """
    Return [{sub, next_date, amount}] for subscriptions due within `days` of reference.
    price_fn(sub_id, fallback_amount) -> float
    """
    ref = reference or date.today()
    cutoff = ref + timedelta(days=days)
    results = []
    for s in subs:
        if not s.get("start_date"):
            continue
        nd = next_payment_date(s["start_date"], s["frequency"],
                               s.get("interval") or 1, s.get("base_unit"), ref)
        if nd <= cutoff:
            results.append({"sub": s, "next_date": nd,
                            "amount": price_fn(s["id"], s["amount"])})
    results.sort(key=lambda x: x["next_date"])
    return results


# ── Range-aware cost (respects price history mid-period changes) ─────────────

def range_cost_with_price_history(sub: dict, price_history: list,
                                  range_start: date, range_end: date) -> float:
    """
    True cost of a subscription over an inclusive [range_start, range_end] window,
    honouring all price changes and clamping to the subscription's active dates.
    price_history: list of dicts with 'amount' (float) and 'valid_from' (str YYYY-MM-DD).
    """
    sub_start = date.fromisoformat(sub["start_date"]) if sub.get("start_date") else range_start
    sub_end   = date.fromisoformat(sub["end_date"])   if sub.get("end_date")   else range_end

    window_start = max(range_start, sub_start)
    window_end   = min(range_end,   sub_end)

    if window_start > window_end:
        return 0.0

    history_sorted = sorted(price_history, key=lambda h: h["valid_from"])

    def price_at(d: date) -> float:
        active = None
        for h in history_sorted:
            if date.fromisoformat(h["valid_from"]) <= d:
                active = h["amount"]
        return active if active is not None else sub["amount"]

    # Build breakpoints at every price-change boundary inside the window
    breakpoints = [window_start]
    for h in history_sorted:
        vf = date.fromisoformat(h["valid_from"])
        if window_start < vf <= window_end:
            breakpoints.append(vf)
    breakpoints.append(window_end + timedelta(days=1))

    total = 0.0
    for i in range(len(breakpoints) - 1):
        seg_start = breakpoints[i]
        seg_end   = breakpoints[i + 1] - timedelta(days=1)
        days_in_seg = (seg_end - seg_start).days + 1
        daily = get_period_cost(price_at(seg_start), sub["frequency"],
                                sub.get("interval") or 1, sub.get("base_unit"), "daily")
        total += daily * days_in_seg

    return round(total, 2)


def year_cost_with_price_history(sub: dict, price_history: list, year: int) -> float:
    """True cost of a subscription across a calendar year, honouring price changes."""
    return range_cost_with_price_history(sub, price_history,
                                         date(year, 1, 1), date(year, 12, 31))


def monthly_costs_for_year(sub: dict, price_history: list, year: int) -> list:
    """Return a 12-element list of this subscription's cost per month for `year`."""
    out = []
    for month in range(1, 13):
        last_day = calendar.monthrange(year, month)[1]
        out.append(range_cost_with_price_history(
            sub, price_history, date(year, month, 1), date(year, month, last_day)))
    return out
