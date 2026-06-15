"""
session.py — Session/auth gate helpers shared by all routes.
"""

from starlette.responses import RedirectResponse

from app.db import get_db, get_user_by_id, init_db, has_any_users


def current_user(session: dict):
    uid = session.get("user_id")
    return get_user_by_id(get_db(), uid) if uid else None


def require_login(session: dict):
    """Return a redirect if not logged in, else None."""
    if not session.get("user_id"):
        return RedirectResponse("/login", status_code=303)
    return None


def guard(session: dict):
    """Combined guard: redirect to setup if no users, login if not authenticated."""
    db = init_db()
    if not has_any_users(db):
        return RedirectResponse("/setup", status_code=303)
    return require_login(session)
