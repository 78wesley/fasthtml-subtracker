"""
main.py — Thin entrypoint shim.

The application now lives in the `app/` package. This shim keeps `python main.py`
working (and gives uvicorn a `main:app` target with live reload).

    python main.py                 # run with live reload
    uvicorn app.main:app --reload  # equivalent
"""

from fasthtml.common import serve

from app.main import app  # noqa: F401  (exposes `app` for `serve()` / uvicorn)
from app.config import PORT

if __name__ == "__main__":
    serve(port=PORT)
