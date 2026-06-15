"""
styles.py — Application CSS (single source of truth, injected as a <Style> header).
"""

CSS = """
:root { --pico-font-size: 15px; }
body  { max-width: 1200px; margin: 0 auto; padding: 1rem; }

/* Nav */
nav { display:flex; align-items:center; gap:1.5rem; padding:0.75rem 1rem;
      background:var(--pico-card-background-color);
      border-radius:var(--pico-border-radius); margin-bottom:1.5rem;
      border:1px solid var(--pico-muted-border-color); flex-wrap:wrap; }
nav .brand { font-weight:700; font-size:1.1rem; text-decoration:none; color:var(--pico-color); }
nav a      { text-decoration:none; color:var(--pico-muted-color); }
nav a:hover{ color:var(--pico-color); }
nav a.active{ color:var(--pico-primary); font-weight:600; }
nav .spacer{ flex:1; }
nav .debug-pill { background:#fef3c7; border:1px solid #fbbf24; color:#92400e;
                  font-size:0.72rem; padding:0.15rem 0.55rem; border-radius:999px; }
nav .team-switch { margin:0; }
nav .team-switch select { margin:0; padding:0.25rem 1.6rem 0.25rem 0.5rem; height:auto;
                          font-size:0.82rem; width:auto; }

/* Cost cards */
.cost-cards { display:grid; grid-template-columns:repeat(5,1fr); gap:1rem; margin-bottom:1.25rem; }
.cost-card  { background:var(--pico-card-background-color); border:1px solid var(--pico-muted-border-color);
              border-radius:var(--pico-border-radius); padding:1rem; text-align:center; }
.cost-card .label  { font-size:0.72rem; color:var(--pico-muted-color); text-transform:uppercase;
                     letter-spacing:.05em; margin-bottom:.25rem; }
.cost-card .amount { font-size:1.35rem; font-weight:700; color:var(--pico-primary); }
.cost-card .sub    { font-size:0.75rem; color:var(--pico-muted-color); margin-top:.2rem; }
@media (max-width:900px) { .cost-cards { grid-template-columns:repeat(2,1fr); } }
@media (max-width:480px) { .cost-cards { grid-template-columns:1fr; } }

/* Charts */
.charts-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; margin-bottom:1.25rem; }
@media (max-width:900px) { .charts-grid { grid-template-columns:1fr; } }
.bar-chart      { width:100%; height:auto; font-size:11px; }
.bar-chart .bar { fill:var(--pico-primary); transition:fill .15s; }
.bar-chart .bar:hover { fill:var(--pico-primary-hover, #0a84ff); }
.bar-chart .axis-label { fill:var(--pico-muted-color); }
.bar-chart .grid-line  { stroke:var(--pico-muted-border-color); stroke-width:1; }
.empty-chart { color:var(--pico-muted-color); text-align:center; padding:2rem 0; }

/* Horizontal subscription breakdown */
.hbar-row   { display:grid; grid-template-columns:9rem 1fr 5.5rem; align-items:center;
              gap:.6rem; margin-bottom:.45rem; font-size:.85rem; }
.hbar-name  { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.hbar-track { background:var(--pico-muted-border-color); border-radius:999px; height:.7rem; overflow:hidden; }
.hbar-fill  { background:var(--pico-primary); height:100%; border-radius:999px; }
.hbar-val   { text-align:right; color:var(--pico-muted-color); }

/* Year selector */
.year-bar { display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem; flex-wrap:wrap; }
.year-bar label { margin:0; font-size:0.85rem; }
.year-bar select, .year-bar input { margin:0; padding:0.3rem 0.6rem; height:auto; }

/* Filters */
.filters { display:flex; gap:1rem; align-items:flex-end; margin-bottom:1rem; flex-wrap:wrap; }
.filters label { margin:0; font-size:0.85rem; }
.filters input, .filters select { margin:0; padding:0.35rem 0.6rem; height:auto; }

/* Tables — wrap long content, never overflow horizontally */
table { font-size:0.9rem; table-layout:auto; width:100%; }
th    { white-space:nowrap; }
td    { white-space:normal; overflow-wrap:anywhere; word-break:break-word;
        vertical-align:top; max-width:22rem; }
/* Opt-out for short, atomic cells (dates, amounts, status, action menus) */
td.nowrap, th.nowrap { white-space:nowrap; overflow-wrap:normal; word-break:normal; max-width:none; }
/* Clamp very long free-text cells to 2 lines; full text shown via title= tooltip */
.cell-clip { display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
             overflow:hidden; }

/* Badges */
.badge          { display:inline-block; padding:.15rem .5rem; border-radius:999px; font-size:.75rem; font-weight:600; }
.badge-active   { background:#d1fae5; color:#065f46; }
.badge-inactive { background:#fee2e2; color:#991b1b; }
.badge-warn     { background:#fef3c7; color:#92400e; }
.badge-info     { background:#dbeafe; color:#1e40af; }
.badge-role     { background:#ede9fe; color:#5b21b6; }

/* Action dropdown menu (manage table) */
.action-menu { position:relative; display:inline-block; }
.action-menu details { margin:0; }
.action-menu details summary {
  font-weight:500; font-size:.82rem; margin:0;
  padding:.3rem .7rem; list-style:none; cursor:pointer;
  border:1px solid var(--pico-muted-border-color);
  border-radius:var(--pico-border-radius);
  background:var(--pico-card-background-color);
  color:var(--pico-color); user-select:none; white-space:nowrap; }
.action-menu details summary::-webkit-details-marker { display:none; }
.action-menu details[open] summary {
  margin-bottom:0;
  border-radius:var(--pico-border-radius) var(--pico-border-radius) 0 0; }
.action-menu .drop-list {
  position:absolute; right:0; z-index:200; min-width:155px;
  background:var(--pico-card-background-color);
  border:1px solid var(--pico-muted-border-color); border-top:none;
  border-radius:0 0 var(--pico-border-radius) var(--pico-border-radius);
  box-shadow:0 6px 18px rgba(0,0,0,.13); overflow:hidden; }
.action-menu .drop-list a,
.action-menu .drop-list button {
  display:block; width:100%; box-sizing:border-box;
  padding:.48rem .95rem; font-size:.84rem;
  text-decoration:none; color:var(--pico-color);
  background:none; border:none; text-align:left; cursor:pointer; margin:0; }
.action-menu .drop-list a:hover,
.action-menu .drop-list button:hover { background:var(--pico-muted-border-color); }
.action-menu .drop-danger { border-top:1px solid var(--pico-muted-border-color); }
.action-menu .drop-danger button { color:#dc2626; }
.action-menu .drop-danger button:hover { background:#fee2e2; color:#b91c1c; }

/* Detail page action buttons */
.detail-actions { display:flex; gap:.6rem; flex-wrap:wrap; margin-top:.9rem; }
.detail-actions a[role=button], .detail-actions button { margin:0; padding:.45rem 1.1rem; font-size:.88rem; }
.btn-danger { background:#dc2626 !important; border-color:#dc2626 !important; color:#fff !important; }
.btn-danger:hover { background:#b91c1c !important; border-color:#b91c1c !important; }

/* Layout */
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:1.25rem; gap:1rem; flex-wrap:wrap; }
.page-header h2 { margin:0; }

/* Alerts */
.alert-warning { background:#fef3c7; border:1px solid #fbbf24; color:#92400e;
                 padding:.75rem 1rem; border-radius:var(--pico-border-radius); margin-bottom:1rem; }
.alert-error   { background:#fee2e2; border:1px solid #f87171; color:#991b1b;
                 padding:.75rem 1rem; border-radius:var(--pico-border-radius); margin-bottom:1rem; }
.alert-success { background:#d1fae5; border:1px solid #6ee7b7; color:#065f46;
                 padding:.75rem 1rem; border-radius:var(--pico-border-radius); margin-bottom:1rem; }

/* Section cards */
.section-card    { background:var(--pico-card-background-color); border:1px solid var(--pico-muted-border-color);
                   border-radius:var(--pico-border-radius); padding:1.25rem; margin-bottom:1.25rem; }
.section-card h3 { margin-top:0; font-size:1rem; }

/* Collapsible */
details summary { cursor:pointer; font-weight:600; font-size:1rem; margin-bottom:.5rem; }
details[open] summary { margin-bottom:1rem; }

/* Upcoming */
.upcoming-item { display:flex; justify-content:space-between; align-items:center;
                 padding:.4rem 0; border-bottom:1px solid var(--pico-muted-border-color); }
.upcoming-item:last-child { border-bottom:none; }

pre { font-size:.78rem; white-space:pre-wrap; word-break:break-all; }
"""
