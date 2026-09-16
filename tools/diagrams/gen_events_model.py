#!/usr/bin/env python3
"""Generate Fundamentals/events-model.svg — the on / fx / dy event families.

Verified against 4.3.3 (framework/TComponent.php):
  - A method-name prefix selects the mechanism.
  - on…  : per-instance handler list  $this->_e[name]  (getEventHandlers, 1273);
           the onX method must exist or raiseEvent throws component_event_undefined
           (raiseEvent, 1548); handlers run in priority order (TWeakCallableCollection).
  - fx…  : one GLOBAL list per name  self::$_ue[name]  shared by every instance
           (getEventHandlers, 1279); listen() registers an object's fx* methods into it
           (listen, 638); raiseEvent merges global listeners with local (raiseEvent, 1479).
  - dy…  : routed to the object's attached, enabled behaviors via a TCallChain
           (callBehaviorsMethod, 1129 -> getCallChain, 1166); each behavior filters the
           value and calls $chain->dyX() to advance.
  - Unhandled fx/dy call returns $args[0] ?? null (callBehaviorsMethod, 1151).

Scope: 4.3.3 only. Python 3 stdlib only.
Usage: python3 tools/diagrams/gen_events_model.py
"""
import html, os

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
def text_px(s, fs): return sum(VW.get(ord(c), 636.0) for c in s)/1000.0*fs

FONT = "Verdana, 'Segoe UI', -apple-system, sans-serif"
MONO = "'DejaVu Sans Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
ARROW = "#4a4a4a"
INK = "#1a1a1a"

# per-family accent = (light fill, border/ink)
ON = ("#dbe9f6", "#3f6f9f")   # local  — blue
FX = ("#dcecd6", "#4f8140")   # global — green
DY = ("#f6e6c8", "#b07f24")   # behaviors — amber

o = []
def rrect(x, y, w, h, fill, stroke, rx=6, sw=1.1, shadow=True, dash=None):
    sh = ' filter="url(#ds)"' if shadow else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{sh}/>')
def txt(x, y, s, fs=9.0, fill=INK, weight=None, anchor="start", italic=False, family=None):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    fm = f' font-family="{family}"' if family else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it}{fm} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')
def line(x1, y1, x2, y2, stroke=ARROW, sw=1.3, arrow=False, dash=None):
    mk = ' marker-end="url(#arrow)"' if arrow else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{da}{mk}/>')

def wrap(s, fs, maxw):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_px(t, fs) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

W, H = 864, 0   # H is computed from the text below
svg = ['__SVG_HEADER__']
svg.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.16"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="''' + ARROW + '''"/>
    </marker>
  </defs>''')
svg.append('__SVG_BG__')
o = svg

# ---- title ----
txt(W/2, 26, "The method-name prefix selects the event mechanism", fs=13, weight=700, fill="#333", anchor="middle")

CW = 268
CENTERS = [148, 432, 716]
CY0, CH = 50, 280

def card(cx, accent, prefix, label, sub):
    x = cx - CW/2
    rrect(x, CY0, CW, CH, "#fff", accent[1], rx=10, sw=1.3)
    rrect(x, CY0, CW, 42, accent[0], accent[1], rx=10, sw=1.3, shadow=False)
    o.append(f'  <rect x="{x:.1f}" y="{CY0+30:.1f}" width="{CW:.1f}" height="12" fill="{accent[0]}"/>')  # square off header bottom
    line(x, CY0+42, x+CW, CY0+42, stroke=accent[1], sw=1.3)
    txt(x+16, CY0+21, prefix + "…", fs=17, weight=700, family=MONO, fill=accent[1])
    txt(x+CW-14, CY0+21, label, fs=10.5, weight=700, fill=accent[1], anchor="end")
    txt(x+16, CY0+34, sub, fs=8.6, italic=True, fill="#666")
    return x

def facts(x, accent, items, y0):
    y = y0
    for s in items:
        o.append(f'  <circle cx="{x+16:.1f}" cy="{y:.1f}" r="2.6" fill="{accent[1]}"/>')
        for i, ln in enumerate(wrap(s, 8.7, CW-40)):
            txt(x+26, y + i*12.5, ln, fs=8.7, fill="#2a2a2a")
        y += 12.5*len(wrap(s, 8.7, CW-40)) + 8

# schematic helpers -----------------------------------------------------------
def objbox(cx, cy, w, h, s, accent, fs=8.8, mono=False, dash=None, fill=None):
    rrect(cx-w/2, cy-h/2, w, h, fill or "#fbfbfa", accent[1], rx=6, sw=1.1, shadow=False, dash=dash)
    txt(cx, cy, s, fs=fs, anchor="middle", family=(MONO if mono else None))

SCH_Y = CY0 + 48       # schematic zone top
SCH_H = 176
FACT_Y = CY0 + 48 + SCH_H + 16

FACTS_ON = [
    "The event exists only when the object defines an onX method.",
    "Handlers attach to that object's own list, $this->_e[name].",
    "raiseEvent calls the handlers in priority order.",
    "raiseEvent on an undefined on-event throws an exception.",
]
FACTS_FX = [
    "Every fx name is a valid event; no method needs to define it.",
    "All objects share one handler list per name, self::$_ue[name].",
    "listen() adds an object's fx methods to those lists.",
    "raiseEvent on any object calls every registered handler.",
    "With no handler, a direct fx call returns its first argument, or null.",
]
FACTS_DY = [
    "Every dy name is a valid event; no method needs to define it.",
    "The call goes to the object's attached, enabled behaviors.",
    "A TCallChain calls those behaviors in priority order.",
    "Each behavior receives the value and calls $chain->dyX() to pass it on.",
    "With no behavior, the call returns its first argument, or null.",
]
def facts_h(items):
    return sum(12.5*len(wrap(t, 8.7, CW-40)) + 8 for t in items)
CH = int(FACT_Y + max(facts_h(FACTS_ON), facts_h(FACTS_FX), facts_h(FACTS_DY)) + 6 - CY0)
H  = CY0 + CH + 16

# ===================== column 1: on — local =====================
x1 = card(CENTERS[0], ON, "on", "local", "an event of one object")
cx = CENTERS[0]
objbox(cx, SCH_Y+46, 190, 26, "component", ON, fs=9.2)
# handler stack
hy = SCH_Y+82
for i, hl in enumerate(["handler 1", "handler 2", "handler 3"]):
    objbox(cx+18, hy+i*20, 118, 16, hl, ON, fs=7.8, fill="#fff")
# raiseEvent arrow down the left of the stack, priority order
line(cx-52, hy-8, cx-52, hy+2*20+8, arrow=True)
txt(cx-58, hy-8, "raiseEvent()", fs=7.6, italic=True, fill="#555", anchor="end")
txt(cx-58, hy+2*20+8, "in priority order", fs=7.2, italic=True, fill="#888", anchor="end")
line(cx+18, SCH_Y+59, cx+18, hy-8, stroke=ON[1], sw=1.0)  # component -> stack
facts(x1, ON, FACTS_ON, FACT_Y)

# ===================== column 2: fx — global =====================
x2 = card(CENTERS[1], FX, "fx", "global", "an event shared by every object")
cx = CENTERS[1]
bar_y = SCH_Y+14
txt(cx, bar_y-7, "one handler list per event name", fs=7.4, italic=True, fill="#888", anchor="middle")
rrect(cx-116, bar_y, 232, 22, FX[0], FX[1], rx=6, sw=1.2, shadow=False)
txt(cx, bar_y+11, "shared registry  \u00b7  self::$_ue[name]", fs=8.4, weight=700, anchor="middle", fill=FX[1])
# one registry -> many objects: "1" at the registry end, a diamond at the object end
oy = SCH_Y+76
line(cx, bar_y+22, cx, oy-12-9, stroke=FX[1], sw=1.0)
txt(cx+6, bar_y+22+8, "1", fs=8.0, weight=700, fill=FX[1])
dy_ = oy-12-5
o.append(f'  <polygon points="{cx:.1f},{dy_-5:.1f} {cx+5:.1f},{dy_:.1f} {cx:.1f},{dy_+5:.1f} {cx-5:.1f},{dy_:.1f}" fill="{FX[1]}"/>')
txt(cx+9, dy_, "many", fs=7.6, italic=True, fill=FX[1])
# object X, drawn as a stack so it reads as many instances
for d in (6, 3):
    rrect(cx-75+d, oy-12+d, 150, 24, "#fbfbfa", FX[1], rx=6, sw=1.0, shadow=False)
objbox(cx, oy, 150, 24, "object X", FX, fs=9.2)
# its fx methods, listed like the on handlers
hy = SCH_Y+112
line(cx, oy+12, cx, hy-8, stroke=FX[1], sw=1.0)
for i, hl in enumerate(["fxMethod 1", "fxMethod 2", "fxMethod 3"]):
    objbox(cx, hy+i*20, 118, 16, hl, FX, fs=7.8, fill="#fff")
txt(cx, SCH_Y+SCH_H-6, "listen() registers each object's fx methods", fs=7.3, italic=True, fill="#888", anchor="middle")
facts(x2, FX, FACTS_FX, FACT_Y)

# ===================== column 3: dy — behaviors =====================
x3 = card(CENTERS[2], DY, "dy", "behaviors", "an event from an object to its behaviors")
cx = CENTERS[2]
lx = cx-66                                   # left stack: component over TCallChain
objbox(lx, SCH_Y+24, 116, 24, "component", DY, fs=9.0)
chy = SCH_Y+70
objbox(lx, chy, 100, 20, "TCallChain", DY, fs=8.2, fill=DY[0])
line(lx, SCH_Y+36, lx, chy-10, arrow=True, stroke=DY[1])
# right: the behaviors, in their own labeled box
bx0, bx1 = cx+2, cx+128
by0, by1 = SCH_Y+6, SCH_Y+156
rrect(bx0, by0, bx1-bx0, by1-by0, "#fbfbfa", DY[1], rx=7, sw=1.0, shadow=False, dash="3,2")
txt((bx0+bx1)/2, by0+11, "Component Behaviors", fs=7.8, weight=700, fill=DY[1], anchor="middle")
bcx = (bx0+bx1)/2
bys = [chy, chy+36, chy+72]
for i, byy in enumerate(bys):
    objbox(bcx, byy, 104, 20, f"behavior {i+1}", DY, fs=7.8, fill="#fff")
    if i:
        line(bcx, bys[i-1]+10, bcx, byy-10, arrow=True, stroke=DY[1], sw=1.1)
line(lx+50, chy, bcx-52, chy, arrow=True, stroke=DY[1], sw=1.1)   # TCallChain -> behavior 1
txt(cx, SCH_Y+SCH_H-6, "$chain->dyX() passes the value to the next behavior", fs=7.3, italic=True, fill="#888", anchor="middle")
facts(x3, DY, FACTS_DY, FACT_Y)

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Fundamentals", "events-model.svg"))
o[0] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">'
o[o.index('__SVG_BG__')] = f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>'
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
