#!/usr/bin/env python3
"""Generate the two quickstart directory-tree SVGs (replace directory.gif x2).

  - GettingStarted/directory.svg  (the helloworld app layout)
  - Fundamentals/directory.svg    (the generic app layout)

Both are simple filesystem trees. They are redrawn as crisp SVG with folder/file
glyphs and elbow connectors, faithful to the legacy directory.gif structure. The
per-directory meaning is already explained in the page prose, so the tree stays a plain
structural picture. Scope: 4.3.3 only.

Usage:
    python3 tools/diagrams/gen_directory.py

Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

VW = {
    32:352.0, 33:394.0, 34:459.0, 35:818.0, 36:636.0, 37:1076.0, 38:727.0, 39:269.0, 40:454.0, 41:454.0, 42:636.0, 43:818.0,
    44:364.0, 45:454.0, 46:364.0, 47:454.0, 48:636.0, 49:636.0, 50:636.0, 51:636.0, 52:636.0, 53:636.0, 54:636.0, 55:636.0,
    56:636.0, 57:636.0, 58:454.0, 59:454.0, 60:818.0, 61:818.0, 62:818.0, 63:545.0, 64:1000.0, 65:684.0, 66:686.0, 67:698.0,
    68:771.0, 69:632.0, 70:575.0, 71:775.0, 72:751.0, 73:421.0, 74:455.0, 75:693.0, 76:557.0, 77:843.0, 78:748.0, 79:787.0,
    80:603.0, 81:787.0, 82:695.0, 83:684.0, 84:616.0, 85:732.0, 86:684.0, 87:989.0, 88:685.0, 89:615.0, 90:685.0, 91:454.0,
    92:454.0, 93:454.0, 94:818.0, 95:636.0, 96:636.0, 97:601.0, 98:623.0, 99:521.0, 100:623.0, 101:596.0, 102:352.0, 103:623.0,
    104:633.0, 105:274.0, 106:344.0, 107:592.0, 108:274.0, 109:973.0, 110:633.0, 111:607.0, 112:623.0, 113:623.0, 114:427.0, 115:521.0,
    116:394.0, 117:633.0, 118:592.0, 119:818.0, 120:592.0, 121:592.0, 122:525.0, 123:635.0, 124:454.0, 125:635.0, 126:818.0,
}
def text_px(s, fs):
    return sum(VW.get(ord(c), 636.0) for c in s) / 1000.0 * fs

ROW_H = 25
INDENT = 24
LEFT = 16
TOP = 14
NAME_FS = 11.5
ICON_W = 17
STROKE = "#2f2f2f"
FOLDER_FILL = "#f4cd6b"
FOLDER_TAB = "#e0b24e"
FOLDER_STROKE = "#bf8f2a"
FILE_FILL = "#ffffff"
FILE_STROKE = "#8f8f8f"
FOLD_FILL = "#e7e7e7"
LINE = "#9a9a9a"
# folded-corner tint by extension (a faint IDE-ish cue)
EXT_TINT = {".php": "#c9b8ea", ".page": "#b8d0ea", ".tpl": "#b8d0ea", ".xml": "#c8e2c8"}

# (name, type, [children]); type: "dir" | "file"
FUND = ("wwwroot", "dir", [
    ("assets", "dir", []),
    ("protected", "dir", [
        ("pages", "dir", [("Home.page", "file", [])]),
        ("runtime", "dir", []),
    ]),
    ("index.php", "file", []),
])
GS = ("helloworld", "dir", [
    ("assets", "dir", []),
    ("protected", "dir", [
        ("pages", "dir", [("Home.page", "file", []), ("Home.php", "file", [])]),
        ("runtime", "dir", []),
        ("vendor", "dir", []),
    ]),
    ("index.php", "file", []),
])

def flatten(node, depth=0, rows=None):
    if rows is None: rows = []
    name, typ, kids = node
    idx = len(rows)
    rows.append({"name": name, "type": typ, "depth": depth, "kids": []})
    for k in kids:
        cidx = flatten(k, depth + 1, rows)
        rows[idx]["kids"].append(cidx)
    return idx if depth else rows

def folder_glyph(x, ymid):
    y = ymid - 6
    tab = f'<path d="M{x:.1f},{y:.1f} h6 l1.6,2 h-7.6 z" fill="{FOLDER_TAB}" stroke="{FOLDER_STROKE}" stroke-width="0.8"/>'
    body = f'<rect x="{x:.1f}" y="{y+2.4:.1f}" width="{ICON_W}" height="10.4" rx="1.6" fill="{FOLDER_FILL}" stroke="{FOLDER_STROKE}" stroke-width="0.9"/>'
    return "  " + tab + "\n  " + body

def file_glyph(x, ymid, name):
    y = ymid - 7
    w, h, fold = 12.5, 15, 4.2
    ext = name[name.rfind("."):] if "." in name else ""
    tint = EXT_TINT.get(ext, FOLD_FILL)
    body = (f'<path d="M{x:.1f},{y:.1f} h{w-fold:.1f} l{fold:.1f},{fold:.1f} v{h-fold:.1f} h-{w:.1f} z" '
            f'fill="{FILE_FILL}" stroke="{FILE_STROKE}" stroke-width="0.9"/>')
    corner = (f'<path d="M{x+w-fold:.1f},{y:.1f} v{fold:.1f} h{fold:.1f} z" '
              f'fill="{tint}" stroke="{FILE_STROKE}" stroke-width="0.8"/>')
    return "  " + body + "\n  " + corner

def build(root, fname):
    rows = flatten(root)
    n = len(rows)
    # x/y per row
    for i, r in enumerate(rows):
        r["ymid"] = TOP + i * ROW_H + ROW_H / 2
        r["ix"] = LEFT + r["depth"] * INDENT          # icon left
        r["cx"] = r["ix"] + 8                          # vertical-connector x under this folder
        r["tx"] = r["ix"] + ICON_W + 6                 # text left
    W = int(max(r["tx"] + text_px(r["name"], NAME_FS) for r in rows) + LEFT)
    H = TOP + n * ROW_H + 8

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">']
    out.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')

    # connectors first (behind icons)
    for i, r in enumerate(rows):
        if not r["kids"]:
            continue
        last = r["kids"][-1]
        x = r["cx"]
        out.append(f'  <line x1="{x:.1f}" y1="{r["ymid"]+7:.1f}" x2="{x:.1f}" y2="{rows[last]["ymid"]:.1f}" '
                   f'stroke="{LINE}" stroke-width="1"/>')
        for c in r["kids"]:
            cr = rows[c]
            out.append(f'  <line x1="{x:.1f}" y1="{cr["ymid"]:.1f}" x2="{cr["ix"]:.1f}" y2="{cr["ymid"]:.1f}" '
                       f'stroke="{LINE}" stroke-width="1"/>')

    # icons + labels
    for r in rows:
        if r["type"] == "dir":
            out.append(folder_glyph(r["ix"], r["ymid"]))
            fw = ' font-weight="700"' if r["depth"] == 0 else ''
        else:
            out.append(file_glyph(r["ix"], r["ymid"], r["name"]))
            fw = ''
        out.append(f'  <text x="{r["tx"]:.1f}" y="{r["ymid"]:.1f}" font-size="{NAME_FS}" fill="#1a1a1a"{fw} '
                   f'dominant-baseline="central">{esc(r["name"])}</text>')

    out.append('</svg>')
    path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", fname))
    with open(path, "w") as f:
        f.write("\n".join(out))
    print(f"wrote {path}  {W}x{H}")

build(GS, os.path.join("GettingStarted", "directory.svg"))
build(FUND, os.path.join("Fundamentals", "directory.svg"))
