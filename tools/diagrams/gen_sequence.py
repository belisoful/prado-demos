#!/usr/bin/env python3
"""Generate quickstart/protected/pages/GettingStarted/sequence.gif's SVG replacement.

The "Hello World" postback sequence, replacing the legacy sequence.gif and staying
faithful to it while correcting the message names against the 4.3.3 framework and the
demo's own source (Home.php / Home.page):

  - A TButton click is a postback. TPage calls the button's raisePostBackEvent(), the
    button raises its OnClick event, and the page's attached handler buttonClicked()
    runs and sets the button's Text. The page then renders and returns the content.
  - Two lifelines: the Page (TPage) and the Button (TButton). Activation bars mark when
    each object is active. A self-message loop marks work an object does on itself.
  - The handler body ($sender->Text = "Hello World!") is shown in a note, taken verbatim
    from the demo's Home.php.

Usage:
    python3 tools/diagrams/gen_sequence.py    # writes the SVG in place

Validate by rendering to pixels; refresh the Performance-mode published copy with a cp
overwrite of quickstart/assets/<hash>/sequence.svg. Scope: 4.3.3 only.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

# Verdana advance widths per 1000 em (ASCII 32..126), measured from Verdana.ttf.
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

# --- geometry ---
LEFT = 18                  # left margin (where the in/out arrows begin)
PAGE_X = 168               # Page lifeline x
BTN_X = 392                # Button lifeline x
HEAD_W = 104               # header box width
HEAD_H = 30
HEAD_Y = 14
ACT_W = 11                 # activation bar width
STROKE = "#2f2f2f"
PAGE_FILL = "#dbe9f6"      # Page header fill (blue)
BTN_FILL = "#e6dcf2"       # Button header fill (violet)
ACT_PAGE = "#eef5fc"
ACT_BTN = "#f2ecfa"
NOTE_FILL = "#fffdf3"
MSG_FS = 9.6
HEAD_FS = 11.5
LIFE_TOP = HEAD_Y + HEAD_H

def head_cx(x): return x

# message rows (y positions), tuned for even spacing
Y_IN   = 88    # "Button Click" arrives at Page
Y_RPBE = 126   # Page -> Button raisePostBackEvent()
Y_ONCL = 164   # Button self: raises OnClick event
Y_CB   = 214   # Button -> Page buttonClicked()
Y_NOTE = 244   # note: $sender->Text = "Hello World!"
Y_REND = 300   # Page self: render()
Y_OUT  = 340   # Page -> out: Page Content

BOTTOM = Y_OUT + 40
# width fits the Button self-message label (the rightmost element) with an 18px right margin
SELF_W, SELF_LABEL_GAP = 30, 6
W = int(BTN_X + ACT_W/2 + SELF_W + SELF_LABEL_GAP + text_px("raises OnClick event", MSG_FS) + LEFT)
H = BOTTOM

# activation spans
PAGE_ACT_TOP = Y_IN
PAGE_ACT_BOT = Y_OUT
BTN_ACT_TOP = Y_RPBE
BTN_ACT_BOT = Y_CB

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">')
out.append(f'''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.7" dy="1.0" stdDeviation="0.8" flood-color="#000" flood-opacity="0.22"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{STROKE}"/>
    </marker>
  </defs>''')
out.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')

# lifelines (dashed) behind everything
for x in (PAGE_X, BTN_X):
    out.append(f'  <line x1="{x}" y1="{LIFE_TOP}" x2="{x}" y2="{BOTTOM-12}" stroke="#9a9a9a" stroke-width="1" stroke-dasharray="4 3"/>')

# activation bars
def act(x, top, bot, fill):
    out.append(f'  <rect x="{x-ACT_W/2:.1f}" y="{top:.1f}" width="{ACT_W}" height="{bot-top:.1f}" rx="1.5" fill="{fill}" stroke="{STROKE}" stroke-width="1"/>')
act(PAGE_X, PAGE_ACT_TOP, PAGE_ACT_BOT, ACT_PAGE)
act(BTN_X, BTN_ACT_TOP, BTN_ACT_BOT, ACT_BTN)

# header boxes
def header(x, label, fill):
    out.append(f'  <rect x="{x-HEAD_W/2:.1f}" y="{HEAD_Y}" width="{HEAD_W}" height="{HEAD_H}" rx="4" fill="{fill}" stroke="{STROKE}" stroke-width="1.2" filter="url(#ds)"/>')
    out.append(f'  <text x="{x:.1f}" y="{HEAD_Y+HEAD_H/2:.1f}" font-size="{HEAD_FS}" font-weight="700" fill="#1a1a1a" text-anchor="middle" dominant-baseline="central">{esc(label)}</text>')
header(PAGE_X, "Page", PAGE_FILL)
header(BTN_X, "Button", BTN_FILL)

def label(x, y, s, anchor="middle", italic=False, fill="#1a1a1a"):
    st = ' font-style="italic"' if italic else ''
    out.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{MSG_FS}" fill="{fill}" text-anchor="{anchor}"{st}>{esc(s)}</text>')

def h_msg(x1, x2, y, s, dashed=False):
    # horizontal message arrow with a label centered above it
    da = ' stroke-dasharray="5 3"' if dashed else ''
    out.append(f'  <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{STROKE}" stroke-width="1.3"{da} marker-end="url(#arrow)"/>')
    label((x1+x2)/2, y-6, s)

def self_msg(x, y, s):
    # self-call loop on the right side of the activation bar
    xe = x + ACT_W/2
    w, h = SELF_W, 20
    out.append(f'  <path d="M{xe:.1f},{y:.1f} h{w} v{h} h-{w}" fill="none" stroke="{STROKE}" stroke-width="1.3" marker-end="url(#arrow)"/>')
    label(xe + w + 6, y + h/2, s, anchor="start")

# 1. incoming Button Click (postback) from the left into the Page activation
out.append(f'  <line x1="{LEFT:.1f}" y1="{Y_IN:.1f}" x2="{PAGE_X-ACT_W/2:.1f}" y2="{Y_IN:.1f}" stroke="{STROKE}" stroke-width="1.3" marker-end="url(#arrow)"/>')
label(LEFT, Y_IN-6, "Button Click", anchor="start")
label(LEFT+4, Y_IN+11, "(postback)", anchor="start", italic=True, fill="#666")

# 2. Page -> Button raisePostBackEvent()
h_msg(PAGE_X+ACT_W/2, BTN_X-ACT_W/2, Y_RPBE, "raisePostBackEvent()")

# 3. Button self: raises OnClick event
self_msg(BTN_X, Y_ONCL, "raises OnClick event")

# 4. Button -> Page buttonClicked() (the attached handler runs)
h_msg(BTN_X-ACT_W/2, PAGE_X+ACT_W/2, Y_CB, "buttonClicked($sender, $param)")

# 5. note: the handler sets the button caption (verbatim from Home.php)
ntxt = '$sender->Text = "Hello World!";'
nw = text_px(ntxt, MSG_FS) + 20; nh = 22; nx = PAGE_X + ACT_W/2 + 16; ny = Y_NOTE - nh/2
fold = 8
out.append(f'  <line x1="{PAGE_X+ACT_W/2:.1f}" y1="{Y_NOTE:.1f}" x2="{nx:.1f}" y2="{Y_NOTE:.1f}" stroke="#8a8a8a" stroke-width="0.9" stroke-dasharray="2.5 2"/>')
out.append(f'  <path d="M{nx:.1f},{ny:.1f} H{nx+nw-fold:.1f} L{nx+nw:.1f},{ny+fold:.1f} V{ny+nh:.1f} H{nx:.1f} Z" fill="{NOTE_FILL}" stroke="#9a9a8f" stroke-width="0.9" filter="url(#ds)"/>')
out.append(f'  <path d="M{nx+nw-fold:.1f},{ny:.1f} V{ny+fold:.1f} H{nx+nw:.1f}" fill="none" stroke="#9a9a8f" stroke-width="0.9"/>')
label(nx+8, Y_NOTE, ntxt, anchor="start")

# 6. Page self: render()
self_msg(PAGE_X, Y_REND, "render()")

# 7. outgoing Page Content to the left
out.append(f'  <line x1="{PAGE_X-ACT_W/2:.1f}" y1="{Y_OUT:.1f}" x2="{LEFT:.1f}" y2="{Y_OUT:.1f}" stroke="{STROKE}" stroke-width="1.3" marker-end="url(#arrow)"/>')
label(LEFT, Y_OUT-6, "Page Content", anchor="start")
label(LEFT+9, Y_OUT+11, "(updated caption)", anchor="start", italic=True, fill="#666")

out.append('</svg>')

_out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "quickstart", "protected", "pages", "GettingStarted", "sequence.svg"))
with open(_out, "w") as f:
    f.write("\n".join(out))
print(f"wrote {_out}  {W}x{H}")
