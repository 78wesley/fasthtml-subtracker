"""
main.py — Application assembly.

Builds the single FastHTML `app`, registers every route module's APIRouter, and
ensures the schema exists. Importable as `app.main:app` (uvicorn) or via the
top-level `main.py` shim (`python main.py`).

Styling is native shadcn: Tailwind (Play CDN, v3) configured with shadcn's tokens,
plus shadcn's globals.css (tokens + @layer base) in app/styles.py. Components are
styled with shadcn utility class strings (see app/styles.py constants).
"""

from fasthtml.common import *

from app.config import SECRET_KEY
from app.styles import GLOBALS
from app.db import init_db
from app.routes import ALL_ROUTERS
from app.session import load_ctx, SKIP

# Tailwind (Play CDN, v3) configured to consume shadcn's HSL tokens. Opacity
# modifiers (bg-primary/90, hover:bg-muted/50, …) work because the tokens are HSL.
TAILWIND_CONFIG = """
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        border: 'hsl(var(--border))', input: 'hsl(var(--input))', ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))', foreground: 'hsl(var(--foreground))',
        primary: { DEFAULT: 'hsl(var(--primary))', foreground: 'hsl(var(--primary-foreground))' },
        secondary: { DEFAULT: 'hsl(var(--secondary))', foreground: 'hsl(var(--secondary-foreground))' },
        destructive: { DEFAULT: 'hsl(var(--destructive))', foreground: 'hsl(var(--destructive-foreground))' },
        muted: { DEFAULT: 'hsl(var(--muted))', foreground: 'hsl(var(--muted-foreground))' },
        accent: { DEFAULT: 'hsl(var(--accent))', foreground: 'hsl(var(--accent-foreground))' },
        popover: { DEFAULT: 'hsl(var(--popover))', foreground: 'hsl(var(--popover-foreground))' },
        card: { DEFAULT: 'hsl(var(--card))', foreground: 'hsl(var(--card-foreground))' },
        success: 'hsl(var(--success))', warning: 'hsl(var(--warning))', info: 'hsl(var(--info))',
      },
      borderRadius: {
        lg: 'var(--radius)', md: 'calc(var(--radius) - 2px)', sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
}
"""

# Applies the saved/preferred theme to <html> before render (no flash); toggle handler.
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
        Link(rel="stylesheet",
             href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700"
                  "&family=Geist+Mono:wght@400..600&display=swap"),
        Script(src="https://cdn.tailwindcss.com"),
        Script(TAILWIND_CONFIG),
        Style(GLOBALS, type="text/tailwindcss"),
    ),
    before=Beforeware(load_ctx, skip=SKIP),
)

# Register all route modules onto the single app instance.
for _router in ALL_ROUTERS:
    _router.to_app(app)

# Ensure tables exist at startup (idempotent).
init_db()
