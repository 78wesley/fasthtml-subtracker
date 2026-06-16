"""
styles.py — shadcn/ui theme for SubTracker (matches ui.shadcn.com).

PicoCSS is disabled (fast_app(pico=False)). This implements shadcn's current default
theme: the **neutral** base color with **OKLCH** design tokens and `--radius: 0.625rem`,
exactly as a fresh `shadcn init` emits. Component styling targets the native elements
FastHTML renders (article=Card, .grid=Grid, button, input, table, …). Opacity uses
`color-mix(in oklab, …)`, the same approach Tailwind v4 / shadcn use for `/NN` colors.
Legacy `--pico-*` variables are aliased to shadcn tokens so inline styles keep working.
"""

CSS = """
/* ── shadcn design tokens (neutral, OKLCH) ────────────────────────────────── */
:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);

  /* App-specific semantic colors (shadcn ships none) for status badges/alerts. */
  --success: oklch(0.55 0.14 150);
  --warning: oklch(0.68 0.16 70);
  --info: oklch(0.55 0.16 250);

  /* Legacy aliases so existing inline styles resolve to shadcn tokens. */
  --pico-color: var(--foreground);
  --pico-muted-color: var(--muted-foreground);
  --pico-card-background-color: var(--card);
  --pico-muted-border-color: var(--border);
  --pico-primary: var(--primary);
  --pico-primary-hover: color-mix(in oklab, var(--primary) 88%, transparent);
  --pico-border-radius: var(--radius);
  --pico-font-size: 0.95rem;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.269 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);

  --success: oklch(0.7 0.15 150);
  --warning: oklch(0.8 0.15 80);
  --info: oklch(0.7 0.15 250);
}

/* ── Base ─────────────────────────────────────────────────────────────────── */
* { box-sizing: border-box; }
html { font-size: 100%; }
body {
  margin: 0 auto; max-width: 1200px; padding: 1.25rem;
  background: var(--background); color: var(--foreground);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, "Apple Color Emoji", sans-serif;
  font-size: var(--pico-font-size); line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
main, main.container { display: block; width: 100%; }
h1, h2, h3, h4 { font-weight: 600; line-height: 1.25; letter-spacing: -0.01em; margin: 0 0 .5rem; }
h1 { font-size: 1.6rem; } h2 { font-size: 1.35rem; } h3 { font-size: 1.05rem; }
p { margin: .4rem 0; }
small { font-size: .8rem; }
a { color: var(--foreground); text-decoration: none; }
a:hover { color: var(--primary); }
hr { border: none; border-top: 1px solid var(--border); margin: 1rem 0; }
strong { font-weight: 600; }
::selection { background: color-mix(in oklab, var(--primary) 15%, transparent); }

/* Card = <article>; section-card / cost-card share the look */
article, .section-card, .cost-card {
  background: var(--card); color: var(--card-foreground);
  border: 1px solid var(--border); border-radius: var(--radius);
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.04); padding: 1.5rem; margin-bottom: 1.25rem;
}
article > header { font-weight: 600; margin: -1.5rem -1.5rem 1rem; padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border); }
article > footer { margin: 1rem -1.5rem -1.5rem; padding: 1rem 1.5rem;
  border-top: 1px solid var(--border); }
.section-card h3 { margin-top: 0; }

/* Grid (Pico .grid) → responsive auto-fit columns */
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(0, 1fr)); gap: 1rem; }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }

/* ── Forms ────────────────────────────────────────────────────────────────── */
label { display: block; font-size: .875rem; font-weight: 500; margin: .6rem 0 .3rem; }
input:not([type=checkbox]):not([type=radio]), select, textarea {
  width: 100%; height: 2.4rem; padding: 0 .7rem; margin: .15rem 0 0;
  font-size: .875rem; color: var(--foreground); background: var(--background);
  border: 1px solid var(--input); border-radius: calc(var(--radius) - 2px);
  transition: box-shadow .15s, border-color .15s; appearance: none;
}
textarea { height: auto; padding: .55rem .7rem; line-height: 1.5; }
input:focus, select:focus, textarea:focus {
  outline: none; border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--ring) 45%, transparent);
}
input::placeholder, textarea::placeholder { color: var(--muted-foreground); }
input[type=checkbox] { width: 1rem; height: 1rem; accent-color: var(--primary); vertical-align: middle; }
select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23808080' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right .55rem center; padding-right: 1.8rem;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
button, [role=button], a[role=button], input[type=submit] {
  display: inline-flex; align-items: center; justify-content: center; gap: .4rem;
  height: 2.4rem; padding: 0 1rem; font-size: .875rem; font-weight: 500;
  border-radius: calc(var(--radius) - 2px); border: 1px solid transparent;
  background: var(--primary); color: var(--primary-foreground);
  cursor: pointer; transition: background-color .15s, opacity .15s, border-color .15s;
  text-decoration: none; white-space: nowrap; line-height: 1;
}
button:hover, [role=button]:hover, a[role=button]:hover { background: color-mix(in oklab, var(--primary) 90%, transparent); }
button:focus-visible { outline: none; box-shadow: 0 0 0 3px color-mix(in oklab, var(--ring) 45%, transparent); }
.secondary { background: var(--secondary); color: var(--secondary-foreground); }
.secondary:hover { background: color-mix(in oklab, var(--secondary) 80%, var(--foreground) 6%); }
.outline, .secondary.outline {
  background: var(--background); color: var(--foreground); border: 1px solid var(--border);
}
.outline:hover, .secondary.outline:hover { background: var(--accent); color: var(--accent-foreground); }
.contrast { background: var(--foreground); color: var(--background); }
.btn-danger { background: var(--destructive) !important; color: var(--destructive-foreground) !important; border-color: transparent !important; }
.btn-danger:hover { background: color-mix(in oklab, var(--destructive) 90%, transparent) !important; }

/* ── Tables ───────────────────────────────────────────────────────────────── */
table { width: 100%; border-collapse: collapse; font-size: .875rem; }
thead th { text-align: left; font-weight: 500; color: var(--muted-foreground);
  white-space: nowrap; padding: .55rem .75rem; border-bottom: 1px solid var(--border); }
td { padding: .6rem .75rem; border-bottom: 1px solid var(--border);
  vertical-align: top; overflow-wrap: anywhere; word-break: break-word; max-width: 22rem; }
tbody tr:hover { background: color-mix(in oklab, var(--muted) 50%, transparent); }
td.nowrap, th.nowrap { white-space: nowrap; overflow-wrap: normal; word-break: normal; max-width: none; }
.cell-clip { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* ── Nav ──────────────────────────────────────────────────────────────────── */
nav { display: flex; align-items: center; gap: 1.1rem; padding: .6rem 1rem; flex-wrap: wrap;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); margin-bottom: 1.5rem; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.04); }
nav .brand { font-weight: 700; font-size: 1.05rem; color: var(--foreground); }
nav a { font-size: .875rem; color: var(--muted-foreground); }
nav a:hover { color: var(--foreground); }
nav a.active { color: var(--foreground); font-weight: 600; }
nav .spacer { flex: 1; }
nav .debug-pill { background: color-mix(in oklab, var(--warning) 18%, transparent);
  border: 1px solid color-mix(in oklab, var(--warning) 40%, transparent);
  color: var(--warning); font-size: .72rem; padding: .15rem .55rem; border-radius: 9999px; }
nav .team-switch { margin: 0; }
nav .team-switch select { margin: 0; height: 2rem; padding: 0 1.8rem 0 .6rem; width: auto; font-size: .8rem; }
.theme-toggle { height: 2rem; padding: 0 .6rem; font-size: 1rem; line-height: 1; }
.theme-icon-dark { display: none; }
.dark .theme-icon-dark { display: inline; }
.dark .theme-icon-light { display: none; }

/* ── Badges ───────────────────────────────────────────────────────────────── */
.badge { display: inline-flex; align-items: center; padding: .12rem .55rem; border-radius: 9999px;
  font-size: .72rem; font-weight: 600; border: 1px solid transparent; line-height: 1.4; }
.badge-active   { background: color-mix(in oklab, var(--success) 14%, transparent);     color: var(--success);     border-color: color-mix(in oklab, var(--success) 35%, transparent); }
.badge-inactive { background: color-mix(in oklab, var(--destructive) 12%, transparent); color: var(--destructive); border-color: color-mix(in oklab, var(--destructive) 35%, transparent); }
.badge-warn     { background: color-mix(in oklab, var(--warning) 16%, transparent);     color: var(--warning);     border-color: color-mix(in oklab, var(--warning) 38%, transparent); }
.badge-info     { background: color-mix(in oklab, var(--info) 14%, transparent);        color: var(--info);        border-color: color-mix(in oklab, var(--info) 35%, transparent); }
.badge-role     { background: var(--secondary); color: var(--secondary-foreground); border-color: var(--border); }

/* ── Alerts ───────────────────────────────────────────────────────────────── */
.alert-warning, .alert-error, .alert-success {
  border: 1px solid; border-radius: var(--radius); padding: .75rem 1rem; margin-bottom: 1rem; font-size: .875rem; }
.alert-warning { background: color-mix(in oklab, var(--warning) 12%, transparent); border-color: color-mix(in oklab, var(--warning) 40%, transparent); color: var(--foreground); }
.alert-error   { background: color-mix(in oklab, var(--destructive) 10%, transparent); border-color: color-mix(in oklab, var(--destructive) 40%, transparent); color: var(--destructive); }
.alert-success { background: color-mix(in oklab, var(--success) 12%, transparent); border-color: color-mix(in oklab, var(--success) 40%, transparent); color: var(--foreground); }

/* ── Cost cards ───────────────────────────────────────────────────────────── */
.cost-cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 1.25rem; }
.cost-card { text-align: center; padding: 1.1rem 1rem; }
.cost-card .label { font-size: .72rem; color: var(--muted-foreground); text-transform: uppercase; letter-spacing: .05em; margin-bottom: .25rem; }
.cost-card .amount { font-size: 1.4rem; font-weight: 700; color: var(--foreground); }
.cost-card .sub { font-size: .75rem; color: var(--muted-foreground); margin-top: .2rem; }
@media (max-width: 900px) { .cost-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .cost-cards { grid-template-columns: 1fr; } }

/* ── Charts ───────────────────────────────────────────────────────────────── */
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; }
@media (max-width: 900px) { .charts-grid { grid-template-columns: 1fr; } }
.bar-chart { width: 100%; height: auto; font-size: 11px; }
.bar-chart .bar { fill: var(--primary); transition: fill .15s; }
.bar-chart .bar:hover { fill: color-mix(in oklab, var(--primary) 80%, transparent); }
.bar-chart .axis-label { fill: var(--muted-foreground); }
.bar-chart .grid-line { stroke: var(--border); stroke-width: 1; }
.empty-chart { color: var(--muted-foreground); text-align: center; padding: 2rem 0; }
.hbar-row { display: grid; grid-template-columns: 9rem 1fr 5.5rem; align-items: center; gap: .6rem; margin-bottom: .45rem; font-size: .85rem; }
.hbar-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hbar-track { background: var(--muted); border-radius: 9999px; height: .55rem; overflow: hidden; }
.hbar-fill { background: var(--primary); height: 100%; border-radius: 9999px; }
.hbar-val { text-align: right; color: var(--muted-foreground); }

/* ── Misc layout ──────────────────────────────────────────────────────────── */
.page-header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.page-header h2 { margin: 0; }
.year-bar, .filters { display: flex; gap: 1rem; align-items: flex-end; margin-bottom: 1rem; flex-wrap: wrap; }
.year-bar label, .filters label { margin: 0; font-size: .8rem; }
.year-bar select, .year-bar input, .filters input, .filters select { margin: 0; }
.detail-actions { display: flex; gap: .6rem; flex-wrap: wrap; margin-top: 1rem; }
.upcoming-item { display: flex; justify-content: space-between; align-items: center; padding: .45rem 0; border-bottom: 1px solid var(--border); }
.upcoming-item:last-child { border-bottom: none; }
details summary { cursor: pointer; font-weight: 600; }
pre { font-size: .78rem; white-space: pre-wrap; word-break: break-all;
  background: color-mix(in oklab, var(--muted) 50%, transparent);
  border: 1px solid var(--border); border-radius: calc(var(--radius) - 2px); padding: .6rem .75rem; }

/* ── Action dropdown menu ─────────────────────────────────────────────────── */
.action-menu { position: relative; display: inline-block; }
.action-menu details { margin: 0; }
.action-menu details summary {
  font-weight: 500; font-size: .82rem; margin: 0; padding: .35rem .75rem; list-style: none; cursor: pointer;
  border: 1px solid var(--border); border-radius: calc(var(--radius) - 2px);
  background: var(--background); color: var(--foreground); user-select: none; white-space: nowrap; }
.action-menu details summary::-webkit-details-marker { display: none; }
.action-menu details summary:hover { background: var(--accent); }
.action-menu details[open] summary { border-radius: calc(var(--radius) - 2px) calc(var(--radius) - 2px) 0 0; }
.action-menu .drop-list {
  position: absolute; right: 0; z-index: 200; min-width: 160px;
  background: var(--popover); color: var(--popover-foreground);
  border: 1px solid var(--border); border-top: none;
  border-radius: 0 0 calc(var(--radius) - 2px) calc(var(--radius) - 2px);
  box-shadow: 0 8px 24px rgb(0 0 0 / 0.12); overflow: hidden; padding: .25rem; }
.action-menu .drop-list a, .action-menu .drop-list button {
  display: block; width: 100%; box-sizing: border-box; height: auto; justify-content: flex-start;
  padding: .45rem .6rem; font-size: .84rem; text-decoration: none; color: var(--popover-foreground);
  background: none; border: none; text-align: left; cursor: pointer; margin: 0; border-radius: calc(var(--radius) - 4px); }
.action-menu .drop-list a:hover, .action-menu .drop-list button:hover { background: var(--accent); }
.action-menu .drop-danger { border-top: 1px solid var(--border); margin-top: .25rem; padding-top: .25rem; }
.action-menu .drop-danger button { color: var(--destructive); }
.action-menu .drop-danger button:hover { background: color-mix(in oklab, var(--destructive) 12%, transparent); }
"""
