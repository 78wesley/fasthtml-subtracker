"""
schema.py — Idempotent SQLite schema initialisation + RBAC seed.

Create-if-absent for every table, add-column-if-absent for additive changes, so
init_db() is safe to call on every boot. Multi-tenant: subscriptions are owned by
a team; users carry a global role; teams/memberships and a DB-driven role matrix
back the RBAC system. audit_log is intentionally FK-free and denormalised so
entries survive permanent deletion.
"""

from app.db.connection import get_db
from app.db.seed import seed_rbac


def _ensure_columns(db, table: str, cols: dict) -> None:
    existing = db[table].columns_dict
    for name, typ in cols.items():
        if name not in existing:
            db[table].add_column(name, typ)


def init_db():
    db = get_db()
    tables = db.table_names()

    if "users" not in tables:
        db["users"].create({
            "id": int, "username": str, "password_hash": str, "global_role": str,
            "created_at": str, "deleted_at": str, "deleted_by": int,
        }, pk="id", not_null={"username", "password_hash"})
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_live "
                   "ON users(username) WHERE deleted_at IS NULL")
    else:
        _ensure_columns(db, "users", {"global_role": str})

    if "teams" not in tables:
        db["teams"].create({
            "id": int, "name": str, "slug": str, "description": str,
            "created_at": str, "created_by": int,
            "deleted_at": str, "deleted_by": int,
        }, pk="id")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_teams_slug_live "
                   "ON teams(slug) WHERE deleted_at IS NULL")

    if "team_members" not in tables:
        db["team_members"].create({
            "id": int, "team_id": int, "user_id": int, "team_role": str,
            "created_at": str, "created_by": int,
            "deleted_at": str, "deleted_by": int,
        }, pk="id", foreign_keys=[
            ("team_id", "teams", "id"), ("user_id", "users", "id"),
        ])
        # One live membership per (team, user).
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_team_members_live "
                   "ON team_members(team_id, user_id) WHERE deleted_at IS NULL")
        db["team_members"].create_index(["team_id"])
        db["team_members"].create_index(["user_id"])

    if "roles" not in tables:
        db["roles"].create({
            "name": str, "scope": str, "label": str, "is_system": int, "rank": int,
        }, pk="name")

    if "permissions" not in tables:
        db["permissions"].create({"name": str, "label": str, "category": str}, pk="name")

    if "role_permissions" not in tables:
        db["role_permissions"].create(
            {"role_name": str, "permission_name": str},
            pk=("role_name", "permission_name"))
        db["role_permissions"].create_index(["role_name"])

    if "subscriptions" not in tables:
        db["subscriptions"].create({
            "id": int, "team_id": int, "created_by": int, "name": str, "amount": float,
            "currency": str, "category": str, "start_date": str, "end_date": str,
            "notes": str, "frequency": str, "interval": int, "base_unit": str,
            "is_active": int, "created_at": str, "updated_at": str,
            "deleted_at": str, "deleted_by": int,
        }, pk="id", foreign_keys=[
            ("team_id", "teams", "id"), ("created_by", "users", "id"),
        ])
        db["subscriptions"].create_index(["team_id", "deleted_at"])

    if "subscription_price_history" not in tables:
        db["subscription_price_history"].create({
            "id": int, "subscription_id": int, "amount": float,
            "valid_from": str, "created_at": str, "created_by": int,
        }, pk="id", foreign_keys=[
            ("subscription_id", "subscriptions", "id"),
            ("created_by", "users", "id"),
        ])
        db["subscription_price_history"].create_index(["subscription_id"])

    if "audit_log" not in tables:
        # No foreign keys: audit must outlive the entities it references.
        db["audit_log"].create({
            "id": int,
            "actor_user_id": int, "actor_name": str, "actor_global_role": str,
            "team_id": int, "team_name": str,
            "action": str, "entity_type": str, "entity_id": int, "entity_name": str,
            "old_values": str, "new_values": str,
            "description": str, "timestamp": str,
        }, pk="id")
        db["audit_log"].create_index(["entity_type", "entity_id"])
        db["audit_log"].create_index(["actor_user_id"])
        db["audit_log"].create_index(["team_id"])

    seed_rbac(db)
    return db


def has_any_users(db) -> bool:
    """True if at least one live (non-deleted) user exists."""
    return next(db.query(
        "SELECT 1 FROM users WHERE deleted_at IS NULL LIMIT 1"), None) is not None
