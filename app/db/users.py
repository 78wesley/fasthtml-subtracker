"""
users.py — User queries (live users only; soft-deleted users are hidden).
"""

from app import timeutil
from app.db.connection import one


def get_user_by_username(db, username: str):
    return one(db, "users", "username = ? AND deleted_at IS NULL", [username])


def get_user_by_id(db, user_id: int):
    return one(db, "users", "id = ? AND deleted_at IS NULL", [user_id])


def get_all_users(db) -> list:
    return list(db["users"].rows_where("deleted_at IS NULL", order_by="id"))


def username_taken(db, username: str) -> bool:
    """True if a live user already holds this username."""
    return one(db, "users", "username = ? AND deleted_at IS NULL", [username]) is not None


def count_super_admins(db) -> int:
    return db.execute(
        "SELECT COUNT(*) FROM users WHERE global_role = 'super_admin' "
        "AND deleted_at IS NULL").fetchone()[0]


def set_global_role(db, user_id: int, role: str) -> None:
    db["users"].update(user_id, {"global_role": role})


def soft_delete_user(db, user_id: int, deleted_by: int) -> None:
    db["users"].update(user_id, {
        "deleted_at": timeutil.now_iso(), "deleted_by": deleted_by})
