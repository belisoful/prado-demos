#!/usr/bin/env python3
"""Generate quickstart/protected/pages/Advanced/logging-routes.svg.

Shows the logging fan-out: Prado::log() records a message into the in-memory TLogger, and
at the end of the request the TLogRouter passes the collected messages to each route. Each
route applies its own Levels and Categories filter and sends the messages that pass to its
own destination. The routes run in parallel.

Usage:
    python3 tools/diagrams/gen_logging_routes.py      # writes the SVG in place

Validate by rendering to pixels (see local/quickstart-doc-update-plan-4.3.3.md 4a) and,
because the quickstart runs Mode="Performance", refresh the published copy with a cp
overwrite of quickstart/assets/<hash>/logging-routes.svg.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

FS = 10.5
SUB = 8.6
CHW = 6.2
BLACK = "#2f2f2f"
NOTE = "#555"
SRC_FILL, SRC_STROKE = "#d4e3f4", "#3f6fa0"
LOG_FILL, LOG_STROKE = "#e7eef7", "#3f6fa0"
RTR_FILL, RTR_STROKE = "#cfe0d4", "#3d7a55"
ROUTE_FILL, ROUTE_STROKE = "#eef4fb", "#3f6fa0"
DEST_FILL, DEST_STROKE = "#f4efe2", "#a98a3f"

out = []

def w_of(label, chw=CHW, pad=28, floor=90):
    return max(len(label) * chw + pad, floor)

def node(cx, cy, w, h, label, fill, stroke, sub=None):
    out.append(f'  <rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" ry="8" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="1.2" filter="url(#ds)"/>')
    if sub:
        out.append(f'  <text x="{cx:.1f}" y="{cy-4:.1f}" font-size="{FS}" fill="#1a1a1a" font-weight="600" '
                   f'text-anchor="middle" dominant-baseline="central">{esc(label)}</text>')
        out.append(f'  <text x="{cx:.1f}" y="{cy+9:.1f}" font-size="{SUB}" fill="{NOTE}" '
                   f'text-anchor="middle" dominant-baseline="central">{esc(sub)}</text>')
    else:
        out.append(f'  <text x="{cx:.1f}" y="{cy:.1f}" font-size="{FS}" fill="#1a1a1a" font-weight="600" '
                   f'text-anchor="middle" dominant-baseline="central">{esc(label)}</text>')

def harrow(x1, x2, y):
    out.append(f'  <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{BLACK}" stroke-width="1.4" marker-end="url(#arrow)"/>')

# --- top chain: Prado::log -> TLogger -> TLogRouter ---
NH = 40
chain_y = 60
srcw = w_of("Prado::log()")
logw = w_of("TLogger", floor=120)
rtrw = w_of("TLogRouter", floor=120)

src_cx = 20 + srcw/2
gap = 34
log_cx = src_cx + srcw/2 + gap + logw/2
rtr_cx = log_cx + logw/2 + gap + rtrw/2

# --- routes fan-out: every concrete TLogRoute subclass in 4.3.3 ---
# (class, destination, since)  since is shown as a badge line where it is 4.2.0+.
routes = [
    ("TFileLogRoute", "log file (runtime dir)", None),
    ("TDbLogRoute", "database table", None),
    ("TEmailLogRoute", "email", None),
    ("TBrowserLogRoute", "browser console", None),
    ("TFirebugLogRoute", "Firebug console", None),
    ("TFirePhpLogRoute", "FirePHP console", None),
    ("TSysLogRoute", "system log (syslog)", "since 4.3.0"),
    ("TStdOutLogRoute", "standard output", "since 4.3.0"),
]
RH = 34
ROUTEW = w_of("TBrowserLogRoute", floor=190)
DESTW = w_of("system log (syslog)", floor=150)
row_gap = 12
routes_top = 110
route_cx = rtr_cx
dest_cx = route_cx + ROUTEW/2 + 90 + DESTW/2

W = dest_cx + DESTW/2 + 20
H = routes_top + len(routes) * (RH + row_gap) + 20

out.insert(0, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" '
              f'font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">')
out.append(f'''  <defs>
    <filter id="ds" x="-20%" y="-30%" width="140%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.20"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{BLACK}"/>
    </marker>
  </defs>''')
out.append(f'  <rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#fff"/>')

# top chain arrows
harrow(src_cx + srcw/2, log_cx - logw/2 - 2, chain_y)
harrow(log_cx + logw/2, rtr_cx - rtrw/2 - 2, chain_y)

node(src_cx, chain_y, srcw, NH, "Prado::log()", SRC_FILL, SRC_STROKE)
node(log_cx, chain_y, logw, NH, "TLogger", LOG_FILL, LOG_STROKE, sub="in memory")
node(rtr_cx, chain_y, rtrw, NH, "TLogRouter", RTR_FILL, RTR_STROKE)

# fan-out: TLogRouter branches down a left-side bus, then a stub into each route
rtr_bottom = chain_y + NH/2
row_centers = [routes_top + RH/2 + i * (RH + row_gap) for i in range(len(routes))]
route_left = route_cx - ROUTEW/2

bus_x = route_left - 26
y_junction = rtr_bottom + 8
# trunk from router down and across to the top of the bus (above the route boxes)
out.append(f'  <path d="M{rtr_cx:.1f},{rtr_bottom:.1f} L{rtr_cx:.1f},{y_junction:.1f} L{bus_x:.1f},{y_junction:.1f} '
           f'L{bus_x:.1f},{row_centers[-1]:.1f}" fill="none" stroke="{BLACK}" stroke-width="1.3"/>')
# stub arrows from the bus into each route's left edge
for cy in row_centers:
    out.append(f'  <line x1="{bus_x:.1f}" y1="{cy:.1f}" x2="{route_left-2:.1f}" y2="{cy:.1f}" '
               f'stroke="{BLACK}" stroke-width="1.3" marker-end="url(#arrow)"/>')

# routes and destinations
for (name, dest, since), cy in zip(routes, row_centers):
    node(route_cx, cy, ROUTEW, RH, name, ROUTE_FILL, ROUTE_STROKE, sub=since)
    ax1 = route_cx + ROUTEW/2
    ax2 = dest_cx - DESTW/2 - 2
    harrow(ax1, ax2, cy)
    node(dest_cx, cy, DESTW, RH, dest, DEST_FILL, DEST_STROKE)

# header label over the fan-out column
out.append(f'  <text x="{route_left:.1f}" y="{routes_top-8:.1f}" font-size="9" fill="{NOTE}" '
           f'text-anchor="start" font-style="italic">each route applies its own Levels + Categories filter, then sends &#8212; routes run in parallel</text>')

out.append('</svg>')

_out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "quickstart", "protected", "pages", "Advanced", "logging-routes.svg"))
with open(_out, "w") as f:
    f.write("\n".join(out))
print(f"wrote {_out}  {W:.0f}x{H:.0f}")
