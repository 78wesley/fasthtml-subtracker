"""
audit.py — Snapshot-based audit log: writes and queries.

Audit entries denormalise the actor name, (later) team name, and entity name at
write time, and carry no foreign keys, so they remain accurate and queryable after
the referenced user/team/entity is permanently deleted.
"""

import json

from app import timeutil
from app.db.connection import get_db, rows_as_dicts


def write_audit_log(actor_user_id: int, actor_name: str, action: str,
                    entity_type: str, entity_id: int, entity_name: str,
                    description: str, old_values=None, new_values=None,
                    actor_global_role: str = None,
                    team_id: int = None, team_name: str = None) -> None:
    get_db()["audit_log"].insert({
        "actor_user_id":     actor_user_id,
        "actor_name":        actor_name,
        "actor_global_role": actor_global_role,
        "team_id":           team_id,
        "team_name":         team_name,
        "action":            action,
        "entity_type":       entity_type,
        "entity_id":         entity_id,
        "entity_name":       entity_name,
        "old_values":        json.dumps(old_values) if old_values else None,
        "new_values":        json.dumps(new_values) if new_values else None,
        "description":       description,
        "timestamp":         timeutil.now_iso(),
    })


def get_audit_for_entity(db, entity_id: int, entity_type: str) -> list:
    return rows_as_dicts(db,
        "SELECT * FROM audit_log WHERE entity_id = ? AND entity_type = ? "
        "ORDER BY timestamp DESC",
        [entity_id, entity_type])


def get_audit_log(db, actor_user_id: int, action_filter: str = None,
                  page: int = 1, per_page: int = 25) -> tuple:
    base = "SELECT * FROM audit_log WHERE actor_user_id = ?"
    params = [actor_user_id]
    if action_filter:
        base += " AND action = ?"
        params.append(action_filter)
    total = db.execute(f"SELECT COUNT(*) FROM ({base})", params).fetchone()[0]
    query = base + f" ORDER BY timestamp DESC LIMIT {per_page} OFFSET {(page-1)*per_page}"
    return rows_as_dicts(db, query, params), total
