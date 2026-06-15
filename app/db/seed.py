"""
seed.py — Idempotent seeding of the RBAC reference data (roles, permissions,
and the default role→permission matrix). Safe to run on every boot.
"""

from app.rbac import PERMISSIONS, GLOBAL_ROLES, TEAM_ROLES, ROLE_PERMISSIONS


def seed_rbac(db) -> None:
    for name, label, category in PERMISSIONS:
        db["permissions"].upsert({"name": name, "label": label, "category": category}, pk="name")

    for name, label, rank in GLOBAL_ROLES:
        db["roles"].upsert({"name": name, "scope": "global", "label": label,
                            "is_system": 1, "rank": rank}, pk="name")
    for name, label, rank in TEAM_ROLES:
        db["roles"].upsert({"name": name, "scope": "team", "label": label,
                            "is_system": 1, "rank": rank}, pk="name")

    # Ensure each role has at least its default permission set (additive; never
    # strips operator customisations made via the role-matrix editor).
    for role_name, perms in ROLE_PERMISSIONS.items():
        for perm in perms:
            db["role_permissions"].upsert(
                {"role_name": role_name, "permission_name": perm},
                pk=("role_name", "permission_name"))
