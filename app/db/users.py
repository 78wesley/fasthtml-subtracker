"""
users.py — User queries (live users only; soft-deleted users are hidden).
"""

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
