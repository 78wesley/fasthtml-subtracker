"""
auth_routes.py — First-run setup, login, logout.
"""

from fasthtml.common import *

from app.db import init_db, has_any_users, get_user_by_id, get_db
from app.auth import authenticate, create_user
from app.db import write_audit_log
from app.components import page_title, alert

ar = APIRouter()


# ── First-run setup (create initial admin) ───────────────────────────────────

@ar("/setup")
def get(session, error: str = ""):
    db = init_db()
    if has_any_users(db):
        return RedirectResponse("/login", status_code=303)
    return page_title("Setup"), Titled("Welcome to SubTracker",
        Card(
            H2("Create your admin account", style="margin-top:0"),
            alert(error, "error") if error else "",
            P("No users exist yet. Create the first account to get started."),
            Form(
                Label("Username", Input(name="username", required=True,
                      placeholder="admin", autofocus=True)),
                Label("Password", Input(type="password", name="password",
                      required=True, placeholder="choose a password")),
                Label("Confirm Password", Input(type="password", name="password2",
                      required=True, placeholder="repeat password")),
                Button("Create Account", type="submit", style="width:100%"),
                method="post", action="/setup",
            ),
            style="max-width:400px; margin:4rem auto;",
        )
    )


@ar("/setup")
async def post(session, username: str, password: str, password2: str):
    db = init_db()
    if has_any_users(db):
        return RedirectResponse("/login", status_code=303)
    if not username.strip():
        return RedirectResponse("/setup?error=Username+cannot+be+empty", status_code=303)
    if password != password2:
        return RedirectResponse("/setup?error=Passwords+do+not+match", status_code=303)
    if len(password) < 6:
        return RedirectResponse("/setup?error=Password+must+be+at+least+6+characters", status_code=303)
    uname = username.strip()
    uid = create_user(uname, password)
    write_audit_log(uid, uname, "CREATE", "user", uid, uname,
                    f"Admin account '{uname}' created during setup")
    session["user_id"] = uid
    return RedirectResponse("/dashboard", status_code=303)


# ── Login / Logout ───────────────────────────────────────────────────────────

@ar("/")
def get(session):
    return RedirectResponse("/dashboard", status_code=303)


@ar("/login")
def get(session, error: str = ""):
    db = init_db()
    if not has_any_users(db):
        return RedirectResponse("/setup", status_code=303)
    return page_title("Login"), Titled("SubTracker",
        Card(
            H2("Sign In", style="margin-top:0"),
            alert(error, "error") if error else "",
            Form(
                Label("Username", Input(name="username", required=True,
                      placeholder="username", autofocus=True)),
                Label("Password", Input(type="password", name="password",
                      required=True, placeholder="password")),
                Button("Sign In", type="submit", style="width:100%"),
                method="post", action="/login",
            ),
            style="max-width:380px; margin:4rem auto;",
        )
    )


@ar("/login")
async def post(session, username: str, password: str):
    user = authenticate(username, password)
    if not user:
        return RedirectResponse("/login?error=Invalid+username+or+password", status_code=303)
    session["user_id"] = user["id"]
    write_audit_log(user["id"], user["username"], "LOGIN", "user", user["id"],
                    user["username"], f"User '{username}' logged in")
    return RedirectResponse("/dashboard", status_code=303)


@ar("/logout")
def get(session):
    uid = session.get("user_id")
    if uid:
        u = get_user_by_id(get_db(), uid)
        if u:
            write_audit_log(uid, u["username"], "LOGOUT", "user", uid, u["username"],
                            f"User '{u['username']}' logged out")
    session.clear()
    return RedirectResponse("/login", status_code=303)
