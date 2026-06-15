"""
subscriptions.py — Subscription and price-history queries.

All read helpers exclude soft-deleted rows (deleted_at IS NULL) by default.
Phase 1 scopes by user_id; Phase 2 swaps this for team scoping.
"""

from app import timeutil
from app.db.connection import get_db, rows_as_dicts, one


# ── Subscription queries ─────────────────────────────────────────────────────

def get_subscription(db, sub_id: int, user_id: int):
    return one(db, "subscriptions",
               "id = ? AND user_id = ? AND deleted_at IS NULL", [sub_id, user_id])


def get_active_subscriptions(db, user_id: int) -> list:
    today = timeutil.today_iso()
    return rows_as_dicts(db,
        "SELECT * FROM subscriptions WHERE user_id = ? AND deleted_at IS NULL "
        "AND is_active = 1 AND (end_date IS NULL OR end_date >= ?)",
        [user_id, today])


def get_all_subscriptions(db, user_id: int, filter_active: str = None,
                          search: str = None, category: str = None) -> list:
    query = "SELECT * FROM subscriptions WHERE user_id = ? AND deleted_at IS NULL"
    params = [user_id]
    if filter_active == "active":
        query += " AND is_active = 1"
    elif filter_active == "inactive":
        query += " AND is_active = 0"
    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")
    if category:
        query += " AND COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') = ?"
        params.append(category)
    query += " ORDER BY name ASC"
    return rows_as_dicts(db, query, params)


def get_categories(db, user_id: int) -> list:
    """Distinct non-empty category names for a user, alphabetically sorted."""
    rows = rows_as_dicts(db,
        "SELECT DISTINCT TRIM(category) AS c FROM subscriptions "
        "WHERE user_id = ? AND deleted_at IS NULL "
        "AND category IS NOT NULL AND TRIM(category) != '' "
        "ORDER BY c COLLATE NOCASE ASC",
        [user_id])
    return [r["c"] for r in rows]


# ── Price history queries ────────────────────────────────────────────────────

def get_active_price(db, subscription_id: int, amount_fallback: float,
                     reference_date: str = None) -> float:
    ref = reference_date or timeutil.today_iso()
    row = db.execute(
        "SELECT amount FROM subscription_price_history "
        "WHERE subscription_id = ? AND valid_from <= ? "
        "ORDER BY valid_from DESC, id DESC LIMIT 1",
        [subscription_id, ref]
    ).fetchone()
    return row[0] if row else amount_fallback


def get_price_history(db, subscription_id: int) -> list:
    return rows_as_dicts(db,
        "SELECT sph.id, sph.subscription_id, sph.amount, sph.valid_from, "
        "       sph.created_at, sph.created_by, u.username "
        "FROM subscription_price_history sph "
        "LEFT JOIN users u ON u.id = sph.created_by "
        "WHERE sph.subscription_id = ? ORDER BY sph.valid_from ASC, sph.id ASC",
        [subscription_id])


def delete_price_history_entry(db, entry_id: int, subscription_id: int) -> bool:
    """Delete a single price-history row; returns True if it existed."""
    rows = list(db["subscription_price_history"].rows_where(
        "id = ? AND subscription_id = ?", [entry_id, subscription_id]))
    if not rows:
        return False
    db["subscription_price_history"].delete(entry_id)
    return True
