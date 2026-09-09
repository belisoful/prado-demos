#!/usr/bin/env python3
"""Generate quickstart/protected/pages/Advanced/permissions-roles.svg.

A role-hierarchy diagram for TPermissionsManager (RBAC), scoped to 4.2.0+. It shows
roles that contain child roles and permissions, resolved recursively (Editor -> author
-> permissions), a role held by every user (Default), and a super role (Administrator)
that bypasses all permission checks. Roles, permissions, and the super role are drawn
distinctly, with a legend.

Usage:
    python3 tools/diagrams/gen_permissions_roles.py     # writes the SVG in place

Validate by rendering to pixels (see local/quickstart-doc-update-plan-4.3.3.md 4a) and,
because the quickstart runs Mode="Performance", refresh the published copy with a cp
overwrite of quickstart/assets/<hash>/permissions-roles.svg.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

FS = 9.5
CHW = 5.7            # approx char width at FS
NODE_H = 24
ROW = 34            # leaf row pitch
COL_GAP = 40        # horizontal gap between depth columns
PAD = 14            # text padding inside a node
X0 = 14
Y0 = 96             # top of the tree (leaves the legend band above)

ROLE_FILL, ROLE_STROKE = "#d4e3f4", "#3f6fa0"
PERM_FILL, PERM_STROKE = "#e6f2e6", "#5b8c5b"
SUPER_FILL, SUPER_STROKE = "#fbeccb", "#c79a3a"
CONN = "#9aa0a6"
TXT = "#1a1a1a"

def role(name, children, note=None, sup=False):
    return {"name": name, "kind": "super" if sup else "role", "children": children, "note": note}

def perm(name):
    return {"name": name, "kind": "perm", "children": []}

# ---- hierarchy (matches the page's blog example) ----
FOREST = [
    role("Editor", [
        role("author", [perm("post_read"), perm("post_update"), perm("post_new")]),
        perm("post_publish"),
        perm("post_delete"),
    ]),
    role("Default", [perm("register_user"), perm("blog_comment")], note="held by every user"),
    role("Administrator", [], note="bypasses all permission checks", sup=True),
]

def width(node):
    return max(len(node["name"]) * CHW + PAD * 2, 46)

# ---- layout: y by leaf packing, x by per-depth column ----
_y = [Y0]
def layout_y(node, depth, first_of_top):
    node["depth"] = depth
    if node["children"]:
        for i, c in enumerate(node["children"]):
            layout_y(c, depth + 1, False)
        node["y"] = (node["children"][0]["y"] + node["children"][-1]["y"]) / 2
    else:
        node["y"] = _y[0]
        _y[0] += ROW

for i, top in enumerate(FOREST):
    if i:
        _y[0] += 14  # gap between top-level roles
    layout_y(top, 0, True)

# per-depth max width -> column x
def walk(node, acc):
    acc.append(node)
    for c in node["children"]:
        walk(c, acc)
ALL = []
for t in FOREST:
    walk(t, ALL)
maxdepth = max(n["depth"] for n in ALL)
col_w = [0.0] * (maxdepth + 1)
for n in ALL:
    col_w[n["depth"]] = max(col_w[n["depth"]], width(n))
col_x = [X0]
for d in range(1, maxdepth + 1):
    col_x.append(col_x[d - 1] + col_w[d - 1] + COL_GAP)

for n in ALL:
    n["x"] = col_x[n["depth"]]
    n["w"] = width(n)

# canvas size
NOTE_ROOM = 190
W = col_x[maxdepth] + col_w[maxdepth] + NOTE_ROOM
H = max(n["y"] for n in ALL) + NODE_H / 2 + 20

# ---- draw ----
out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" '
           f'font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">')
out.append('''  <defs>
    <filter id="ds" x="-20%" y="-30%" width="140%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.20"/>
    </filter>
  </defs>''')
out.append(f'  <rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#fff"/>')

def node_box(n):
    x, y, w = n["x"], n["y"], n["w"]
    if n["kind"] == "perm":
        fill, stroke, rx = PERM_FILL, PERM_STROKE, NODE_H / 2
    elif n["kind"] == "super":
        fill, stroke, rx = SUPER_FILL, SUPER_STROKE, 6
    else:
        fill, stroke, rx = ROLE_FILL, ROLE_STROKE, 6
    out.append(f'  <rect x="{x:.1f}" y="{y-NODE_H/2:.1f}" width="{w:.1f}" height="{NODE_H}" rx="{rx}" ry="{rx}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="1.1" filter="url(#ds)"/>')
    fw = ' font-weight="600"' if n["kind"] != "perm" else ''
    out.append(f'  <text x="{x+w/2:.1f}" y="{y:.1f}" font-size="{FS}" fill="{TXT}"{fw} text-anchor="middle" '
               f'dominant-baseline="central">{esc(n["name"])}</text>')
    if n.get("note"):
        if n["children"]:  # note below the box, clear of the connectors
            out.append(f'  <text x="{x:.1f}" y="{y+NODE_H/2+10:.1f}" font-size="8.6" fill="#555">{esc(n["note"])}</text>')
        else:              # childless node: note to the right
            out.append(f'  <text x="{x+w+10:.1f}" y="{y:.1f}" font-size="8.6" fill="#555" '
                       f'dominant-baseline="central">{esc(n["note"])}</text>')

# connectors (tree elbows: parent right -> vertical bus -> child left)
for n in ALL:
    if not n["children"]:
        continue
    px = n["x"] + n["w"]
    busx = px + COL_GAP / 2
    for c in n["children"]:
        out.append(f'  <path d="M{px:.1f},{n["y"]:.1f} H{busx:.1f} V{c["y"]:.1f} H{c["x"]:.1f}" '
                   f'fill="none" stroke="{CONN}" stroke-width="1.1"/>')

for n in ALL:
    node_box(n)

# ---- legend (top-left band) ----
lx, ly = 14, 8
out.append(f'  <rect x="{lx}" y="{ly}" width="360" height="60" rx="6" fill="#fbfbf7" stroke="#8a8a8a" stroke-width="1" filter="url(#ds)"/>')
out.append(f'  <text x="{lx+11}" y="{ly+14:.0f}" font-size="10.5" font-weight="600" fill="#333">Legend</text>')
_r1, _r2 = ly + 30, ly + 46
def swatch(x, y, fill, stroke, rx, label):
    out.append(f'  <rect x="{x}" y="{y-5}" width="18" height="10" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="0.9"/>')
    out.append(f'  <text x="{x+25}" y="{y:.0f}" font-size="9.2" fill="#333" dominant-baseline="central">{label}</text>')
swatch(lx + 13, _r1, ROLE_FILL, ROLE_STROKE, 3, "role")
swatch(lx + 120, _r1, PERM_FILL, PERM_STROKE, 5, "permission")
swatch(lx + 13, _r2, SUPER_FILL, SUPER_STROKE, 3, "super role")

out.append('</svg>')

_out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "quickstart", "protected", "pages", "Advanced", "permissions-roles.svg"))
with open(_out, "w") as f:
    f.write("\n".join(out))
print(f"wrote {_out}  {W:.0f}x{H:.0f}")
