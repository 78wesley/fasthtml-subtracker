"""
main.py — Application assembly.

Builds the single FastHTML `app`, registers every route module's APIRouter, and
ensures the schema exists. Importable as `app.main:app` (uvicorn) or via the
top-level `main.py` shim (`python main.py`).
"""

from fasthtml.common import *

from app.config import SECRET_KEY
from app.styles import CSS
from app.db import init_db
from app.routes import ALL_ROUTERS

app, rt = fast_app(
    secret_key=SECRET_KEY,
    hdrs=(Style(CSS),),
)

# Register all route modules onto the single app instance.
for _router in ALL_ROUTERS:
    _router.to_app(app)

# Ensure tables exist at startup (idempotent).
init_db()
