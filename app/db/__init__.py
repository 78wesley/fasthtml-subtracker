"""
app.db — stable import surface for all data access.

Route modules import from `app.db` so internal file moves stay invisible to handlers.
"""

from app.db.connection import get_db, rows_as_dicts, one
from app.db.schema import init_db, has_any_users
from app.db.users import (
    get_user_by_username, get_user_by_id, get_all_users, username_taken,
)
from app.db.subscriptions import (
    get_subscription, get_active_subscriptions, get_all_subscriptions,
    get_categories, get_active_price, get_price_history, delete_price_history_entry,
)
from app.db.audit import (
    write_audit_log, get_audit_for_entity, get_audit_log,
)

__all__ = [
    "get_db", "rows_as_dicts", "one",
    "init_db", "has_any_users",
    "get_user_by_username", "get_user_by_id", "get_all_users", "username_taken",
    "get_subscription", "get_active_subscriptions", "get_all_subscriptions",
    "get_categories", "get_active_price", "get_price_history",
    "delete_price_history_entry",
    "write_audit_log", "get_audit_for_entity", "get_audit_log",
]
