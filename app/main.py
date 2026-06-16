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
from app.session import load_ctx, SKIP

# Tailwind (Play CDN) configured with the shadcn design tokens. Preflight is off so
# it never clobbers the base element styling defined in styles.py (which also makes
# the page look correct before/independently of the CDN finishing).
TAILWIND_CONFIG = """
tailwind.config = {
  darkMode: 'class',
  corePlugins: { preflight: false },
  theme: { extend: {
    colors: {
      border: 'var(--border)', input: 'var(--input)', ring: 'var(--ring)',
      background: 'var(--background)', foreground: 'var(--foreground)',
      primary: { DEFAULT: 'var(--primary)', foreground: 'var(--primary-foreground)' },
      secondary: { DEFAULT: 'var(--secondary)', foreground: 'var(--secondary-foreground)' },
      destructive: { DEFAULT: 'var(--destructive)', foreground: 'var(--destructive-foreground)' },
      muted: { DEFAULT: 'var(--muted)', foreground: 'var(--muted-foreground)' },
      accent: { DEFAULT: 'var(--accent)', foreground: 'var(--accent-foreground)' },
      card: { DEFAULT: 'var(--card)', foreground: 'var(--card-foreground)' },
      popover: { DEFAULT: 'var(--popover)', foreground: 'var(--popover-foreground)' },
    },
    borderRadius: { lg: 'var(--radius)', md: 'calc(var(--radius) - 2px)', sm: 'calc(var(--radius) - 4px)' },
  } }
}
"""

# Applies the saved/preferred theme to <html> before the body renders (no flash),
# and defines the nav toggle handler. shadcn dark mode = a `.dark` class on <html>.
THEME_JS = """
(function () {
  try {
    var t = localStorage.getItem('theme');
    if (t === 'dark' || (t === null && window.matchMedia &&
        matchMedia('(prefers-color-scheme: dark)').matches))
      document.documentElement.classList.add('dark');
  } catch (e) {}
})();
function toggleTheme() {
  var dark = document.documentElement.classList.toggle('dark');
  try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) {}
}
"""

app, rt = fast_app(
    secret_key=SECRET_KEY,
    pico=False,
    hdrs=(
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Script(THEME_JS),
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700" "&family=Geist+Mono:wght@400..600&display=swap"),
        Script(src="https://cdn.tailwindcss.com"),
        Script(TAILWIND_CONFIG),
        Style(CSS),
    ),
    before=Beforeware(load_ctx, skip=SKIP),
)

# Register all route modules onto the single app instance.
for _router in ALL_ROUTERS:
    _router.to_app(app)

# Ensure tables exist at startup (idempotent).
init_db()
