"""
users.py — User management (list, create, soft-delete).

Phase 1 keeps the existing single-tier flow but switches deletion to soft-delete.
RBAC role assignment and team membership management arrive in Phase 2/3.
"""

from fasthtml.common import *

from app import timeutil
from app.db import (
    get_db, get_all_users, get_user_by_id, username_taken, write_audit_log,
)
from app.auth import create_user
from app.session import guard, current_user
from app.components import page_title, nav_bar, alert

ar = APIRouter()


@ar("/users")
def get(session, msg: str = "", msg_kind: str = "warning"):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    db = get_db()
    all_users = get_all_users(db)

    rows = [
        Tr(
            Td(u["id"], cls="nowrap"),
            Td(u["username"]),
            Td(u["created_at"][:16] if u["created_at"] else "—", cls="nowrap"),
            Td(
                Form(
                    Button("🗑️ Delete", cls="secondary outline",
                           style="padding:.25rem .6rem; font-size:.8rem; margin:0",
                           hx_post=f"/users/{u['id']}/delete",
                           hx_confirm=f"Delete user '{u['username']}'?",
                           hx_target="body", hx_push_url="/users"),
                    method="post",
                ) if u["id"] != user["id"] else Span("(you)", style="color:var(--pico-muted-color)"),
                cls="nowrap",
            ),
        )
        for u in all_users
    ]

    return page_title("Users"), nav_bar(user["username"], "users"), Main(
        Div(H2("User Management"), cls="page-header"),
        alert(msg, msg_kind) if msg else "",
        Table(
            Thead(Tr(Th("ID"), Th("Username"), Th("Created"), Th("Actions"))),
            Tbody(*rows),
        ),
        H3("Create New User", style="margin-top:1.5rem"),
        Form(
            Grid(
                Label("Username *", Input(name="username", required=True, placeholder="username")),
                Label("Password *", Input(name="password", type="password",
                      required=True, placeholder="password")),
            ),
            Button("Create User", type="submit"),
            method="post", action="/users/new",
        ),
    )


@ar("/users/new")
async def post(session, username: str, password: str):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    db = get_db()
    uname = username.strip()
    if not uname:
        return RedirectResponse("/users?msg=Username+cannot+be+empty", status_code=303)
    if username_taken(db, uname):
        return RedirectResponse("/users?msg=Username+already+exists", status_code=303)
    uid = create_user(uname, password)
    write_audit_log(user["id"], user["username"], "CREATE", "user", uid, uname,
                    f"Admin created user '{uname}'",
                    new_values={"username": uname})
    return RedirectResponse("/users", status_code=303)


@ar("/users/{uid}/delete")
async def post(session, uid: int):
    redir = guard(session)
    if redir: return redir
    user = current_user(session)
    db = get_db()
    if uid == user["id"]:
        return RedirectResponse("/users?msg=Cannot+delete+yourself", status_code=303)
    # Never let the live-user count reach zero (would expose /setup to anyone).
    if len([u for u in get_all_users(db) if u["id"] != uid]) == 0:
        return RedirectResponse("/users?msg=Cannot+delete+the+last+user", status_code=303)
    target = get_user_by_id(db, uid)
    if target:
        now = timeutil.now_iso()
        db["users"].update(uid, {"deleted_at": now, "deleted_by": user["id"]})
        write_audit_log(user["id"], user["username"], "DELETE", "user", uid,
                        target["username"], f"Deleted user '{target['username']}'",
                        old_values={"deleted_at": None},
                        new_values={"deleted_at": now, "deleted_by": user["id"]})
    return RedirectResponse("/users", status_code=303)
