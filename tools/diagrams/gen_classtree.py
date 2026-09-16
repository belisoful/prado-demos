#!/usr/bin/env python3
"""Generate Fundamentals/classtree.svg — a class inheritance tree of major PRADO classes.

Replaces the legacy classtree.gif. Every edge is a real `extends` relation verified
against the 4.3.3 framework (vendor/pradosoft/prado/framework), correcting the legacy
diagram, which was stale:
  - TApplication extends TComponent directly (not TApplicationComponent).
  - TSqliteCache is gone; the cache base module is the abstract TCache.
  - TBaseValidator extends TLabel (not TWebControl).
  - TTemplateControl reaches TControl through TCompositeControl.
  - THttpRequest/THttpSession extend TApplicationComponent (they implement IModule but do
    not extend TModule); the TModule examples shown are real subclasses.

Drawn as an indented tree so the deep validator chain stays legible at page width.
Scope: 4.3.3 only. Requires: Python 3 standard library only.

Usage:
    python3 tools/diagrams/gen_classtree.py
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

FONT = "Verdana, 'Segoe UI', -apple-system, sans-serif"
LEFT, TOP = 16, 16   # top padding equals left padding; TComponent + legend both start here
ROW_H, INDENT, BOX_H = 28, 22, 22
NAME_FS, PAD = 10.5, 9
LINE = "#9aa0a6"
CAT = {   # fill, stroke
    "core":  ("#eef1f5", "#7a8a9a"),
    "ctrl":  ("#dbe9f6", "#4a78a8"),
    "valid": ("#f6e6c8", "#b8862a"),
    "data":  ("#dcecd6", "#5a8f45"),
    "mod":   ("#e7ddf2", "#7a4fb5"),
    "svc":   ("#d6ecec", "#2f8f8f"),
}
LEG = [("core", "core / base"), ("ctrl", "controls"), ("valid", "validators"),
       ("data", "data-bound"), ("mod", "modules"), ("svc", "services")]

# (name, category, [children]) — every edge verified as a real `extends` in 4.3.3
TREE = ("TComponent", "core", [
    ("TApplicationComponent", "core", [
        ("TControl", "ctrl", [
            ("TWebControl", "ctrl", [
                ("TLabel", "ctrl", [
                    ("TBaseValidator", "valid", [
                        ("TRequiredFieldValidator", "valid", []),
                        ("TCompareValidator", "valid", []),
                        ("TRegularExpressionValidator", "valid", [
                            ("TEmailAddressValidator", "valid", []),
                        ]),
                        ("TCustomValidator", "valid", []),
                    ]),
                ]),
                ("TPanel", "ctrl", []),
                ("TTextBox", "ctrl", []),
                ("TButton", "ctrl", []),
                ("TDataBoundControl", "data", [
                    ("TListControl", "data", [
                        ("TListBox", "data", []),
                        ("TCheckBoxList", "data", []),
                    ]),
                    ("TRepeater", "data", []),
                    ("TBaseDataList", "data", [
                        ("TDataList", "data", []),
                        ("TDataGrid", "data", []),
                    ]),
                ]),
            ]),
            ("TCompositeControl", "ctrl", [
                ("TTemplateControl", "ctrl", [
                    ("TPage", "ctrl", []),
                ]),
            ]),
        ]),
        ("TModule", "mod", [
            ("THttpResponse", "mod", []),
            ("TErrorHandler", "mod", []),
            ("TCache", "mod", []),
            ("TUserManager", "mod", []),
            ("TAuthManager", "mod", []),
        ]),
        ("TService", "svc", [
            ("TPageService", "svc", []),
        ]),
    ]),
    ("TApplication", "core", []),
    ("TList", "core", []),
    ("TMap", "core", []),
])

# flatten pre-order
rows = []
def walk(node, depth, parent):
    name, cat, kids = node
    idx = len(rows)
    rows.append({"name": name, "cat": cat, "depth": depth, "parent": parent, "kids": []})
    if parent is not None:
        rows[parent]["kids"].append(idx)
    for k in kids:
        walk(k, depth + 1, idx)
walk(TREE, 0, None)

for i, r in enumerate(rows):
    r["x"] = LEFT + r["depth"] * INDENT
    r["w"] = text_px(r["name"], NAME_FS) + 2 * PAD
    r["top"] = TOP + i * ROW_H
    r["mid"] = r["top"] + BOX_H / 2
    r["cx"] = r["x"] + 11                      # connector rail x under this node

content_right = round(max(r["x"] + r["w"] for r in rows))   # rightmost content, on an integer
W = content_right + TOP                                     # right padding == top padding == TOP, exactly
H = TOP + len(rows) * ROW_H + 8

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
out.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')

# connectors (behind boxes)
for r in rows:
    if not r["kids"]:
        continue
    last = rows[r["kids"][-1]]
    out.append(f'  <line x1="{r["cx"]:.1f}" y1="{r["top"]+BOX_H:.1f}" x2="{r["cx"]:.1f}" y2="{last["mid"]:.1f}" stroke="{LINE}" stroke-width="1"/>')
    for c in r["kids"]:
        cr = rows[c]
        out.append(f'  <line x1="{r["cx"]:.1f}" y1="{cr["mid"]:.1f}" x2="{cr["x"]:.1f}" y2="{cr["mid"]:.1f}" stroke="{LINE}" stroke-width="1"/>')

# node boxes
for r in rows:
    fill, stroke = CAT[r["cat"]]
    sw = 1.6 if r["depth"] == 0 else 1.1
    out.append(f'  <rect x="{r["x"]:.1f}" y="{r["top"]:.1f}" width="{r["w"]:.1f}" height="{BOX_H}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    fw = ' font-weight="700"' if r["depth"] == 0 else ''
    out.append(f'  <text x="{r["x"]+r["w"]/2:.1f}" y="{r["mid"]:.1f}" font-size="{NAME_FS}"{fw} fill="#1a1a1a" text-anchor="middle" dominant-baseline="central">{esc(r["name"])}</text>')

# legend, enclosed in a box with equal padding on all sides; right-aligned (margin = LEFT),
# its top aligned with TComponent's top
title_w = text_px("Class Categories", 9)
item_w = 22 + max(text_px(label, 8.6) for _, label in LEG)
lpad = 12                                           # roomier left/right padding
vtop, vbot = 12, 9                                  # top padding (−1) and bottom padding
box_w = max(title_w, item_w) + 2 * lpad
title_off = vtop
item0_off = title_off + 17
box_h = item0_off + (len(LEG) - 1) * 14 + 5 + vbot  # last swatch bottom + bottom pad
box_x = content_right - box_w                       # right edge aligned with the rightmost class box
box_y = TOP                                         # top aligned with TComponent
lcx = box_x + box_w / 2
out.append(f'  <rect x="{box_x:.1f}" y="{box_y}" width="{box_w:.1f}" height="{box_h:.1f}" rx="6" fill="#fbfbf9" stroke="#c4c4c4" stroke-width="1"/>')
out.append(f'  <text x="{lcx:.1f}" y="{box_y+title_off:.1f}" font-size="9" font-weight="700" fill="#444" text-anchor="middle" dominant-baseline="central">Class Categories</text>')
for i, (cat, label) in enumerate(LEG):
    yy = box_y + item0_off + i * 14
    fill, stroke = CAT[cat]
    out.append(f'  <rect x="{box_x+lpad:.1f}" y="{yy-5:.1f}" width="16" height="10" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
    out.append(f'  <text x="{box_x+lpad+22:.1f}" y="{yy:.1f}" font-size="8.6" fill="#555" dominant-baseline="central">{esc(label)}</text>')

out.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Fundamentals", "classtree.svg"))
with open(path, "w") as f:
    f.write("\n".join(out))
print(f"wrote {path}  {W}x{H}")
