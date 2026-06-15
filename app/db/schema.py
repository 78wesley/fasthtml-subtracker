"""
schema.py — Idempotent SQLite schema initialisation.

Create-if-absent for every table, add-column-if-absent for additive changes, so
init_db() is safe to call on every boot. Phase 1 is single-tenant (subscriptions
owned per user_id); teams/roles arrive in Phase 2. The audit_log is intentionally
foreign-key-free and denormalised so entries survive permanent deletion.
"""

from app.db.connection import get_db


def init_db():
    db = get_db()
    tables = db.table_names()

    if "users" not in tables:
        db["users"].create({
            "id": int, "username": str, "password_hash": str,
            "created_at": str,
            "deleted_at": str, "deleted_by": int,
        }, pk="id", not_null={"username", "password_hash"})
        # Partial-unique: usernames are unique only among LIVE users, so a
        # soft-deleted username can be re-created without a UNIQUE violation.
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_live "
                   "ON users(username) WHERE deleted_at IS NULL")

    if "subscriptions" not in tables:
        db["subscriptions"].create({
            "id": int, "user_id": int, "name": str, "amount": float,
            "currency": str, "category": str, "start_date": str, "end_date": str,
            "notes": str, "frequency": str, "interval": int, "base_unit": str,
            "is_active": int, "created_at": str, "updated_at": str,
            "deleted_at": str, "deleted_by": int,
        }, pk="id", foreign_keys=[("user_id", "users", "id")])
        db["subscriptions"].create_index(["user_id", "deleted_at"])

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

    return db


def has_any_users(db) -> bool:
    """True if at least one live (non-deleted) user exists."""
    return next(db.query(
        "SELECT 1 FROM users WHERE deleted_at IS NULL LIMIT 1"), None) is not None
