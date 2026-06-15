"""
authz.py — Per-route authorization gate.

Pair with the Beforeware (which loads ctx + authenticates): each protected handler
calls `require(ctx, "perm", ...)` and returns the result if non-None.
"""

from app.components.layout import forbidden_page


def require(ctx, *perms):
    """Return a 'forbidden' page if ctx lacks ANY of `perms`, else None."""
    missing = [p for p in perms if not ctx.can(p)]
    return forbidden_page(ctx, missing) if missing else None


def writable_team(ctx) -> bool:
    """
    True only when there is exactly one unambiguous team to write into. Blocks
    creating rows while teamless (would orphan the row) or while a super admin is
    in cross-team 'view all' mode (would silently file into an arbitrary team).
    """
    return ctx.active_team_id is not None and not (ctx.view_all and ctx.is_super)
