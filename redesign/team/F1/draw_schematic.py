"""One-page power schematic (SVG, design-system wiring style) drawn from claims.json and params.json.

Run after power.py:  python -I redesign/team/F1/draw_schematic.py   -> redesign/team/F1/power-schematic.svg
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CL = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}
W = CL["CALC-F1-WIRES"]["outputs"]

# light-theme token values (design-system/tokens.css, blender-style.json wire colours)
FG, FG2, FG3, LINE2, PANEL = "#121619", "#4B5563", "#6B7280", "#CBD2DB", "#FFFFFF"
RED, BLACK, SIG, DATA = "#D83A30", "#303030", "#C9A800", "#9AA4B1"
SUB = {"PWR": "#E0613A", "PRP": "#D45C8E", "AVN": "#5DB24D", "HRN": "#D9A91E", "MEC": "#7F8C9E"}
SANS = "'IBM Plex Sans', system-ui, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, monospace"

out = []


def box(x, y, w, h, sub, pid, name, lines=()):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{PANEL}" stroke="{LINE2}" stroke-width="1"/>')
    out.append(f'<rect x="{x + 8}" y="{y + 8}" width="10" height="10" fill="{SUB[sub]}"/>')
    out.append(f'<text x="{x + 24}" y="{y + 17}" font-family="{MONO}" font-size="12" fill="{FG3}">{pid}</text>')
    out.append(f'<text x="{x + 8}" y="{y + 36}" font-family="{SANS}" font-size="12" font-weight="500" fill="{FG}">{name}</text>')
    for i, t in enumerate(lines):
        out.append(f'<text x="{x + 8}" y="{y + 54 + 16 * i}" font-family="{MONO}" font-size="11" fill="{FG2}">{t}</text>')


def pair(x1, y1, x2, y2, label=None, lx=None, ly=None, bend=None):
    """+/- pair: red over black, 4 px apart. bend = x of the vertical leg for an L-route."""
    vertical = x1 == x2
    for col, dy in ((RED, -3), (BLACK, 3)):
        if bend is None and vertical:
            pts = f"{x1 + dy},{y1} {x2 + dy},{y2}"
        elif bend is None:
            pts = f"{x1},{y1 + dy} {x2},{y2 + dy}"
        else:
            pts = f"{x1},{y1 + dy} {bend + dy},{y1 + dy} {bend + dy},{y2 + dy} {x2},{y2 + dy}"
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round"/>')
    if label:
        out.append(f'<text x="{lx}" y="{ly}" font-family="{MONO}" font-size="11" fill="{FG2}" text-anchor="middle">{label}</text>')


def sig(pts, label=None, lx=None, ly=None, data=False):
    dash = ' stroke-dasharray="6 4"' if data else ""
    col = DATA if data else SIG
    out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.25"{dash}/>')
    if label:
        out.append(f'<text x="{lx}" y="{ly}" font-family="{MONO}" font-size="11" fill="{FG2}" text-anchor="middle">{label}</text>')


def disconnect(x, y, iface, conn):
    """gap with two half-circles at a removable joint"""
    out.append(f'<path d="M{x - 10},{y - 9} a9,9 0 0,1 0,18" fill="none" stroke="{FG}" stroke-width="1.5"/>')
    out.append(f'<path d="M{x + 10},{y - 9} a9,9 0 0,0 0,18" fill="none" stroke="{FG}" stroke-width="1.5"/>')
    out.append(f'<text x="{x}" y="{y - 18}" font-family="{MONO}" font-size="11" fill="{FG}" text-anchor="middle">{iface}</text>')
    out.append(f'<text x="{x}" y="{y + 30}" font-family="{MONO}" font-size="11" fill="{FG2}" text-anchor="middle">{conn}</text>')


def fuse(x, y, label):
    """vertical fuse symbol centred on (x, y)"""
    out.append(f'<rect x="{x - 8}" y="{y - 16}" width="16" height="32" rx="2" fill="{PANEL}" stroke="{FG}" stroke-width="1.25"/>')
    out.append(f'<line x1="{x}" y1="{y - 16}" x2="{x}" y2="{y + 16}" stroke="{FG}" stroke-width="1"/>')
    out.append(f'<text x="{x + 16}" y="{y + 4}" font-family="{MONO}" font-size="11" fill="{FG2}">{label}</text>')


def cap(x, y):
    out.append(f'<line x1="{x}" y1="{y - 3}" x2="{x}" y2="{y + 9}" stroke="{FG}" stroke-width="1"/>')
    out.append(f'<line x1="{x - 7}" y1="{y + 9}" x2="{x + 7}" y2="{y + 9}" stroke="{FG}" stroke-width="1.5"/>')
    out.append(f'<line x1="{x - 7}" y1="{y + 13}" x2="{x + 7}" y2="{y + 13}" stroke="{FG}" stroke-width="1.5"/>')


LEN = [CL["CALC-F1-WIRES"]["input_values"][k] for k in ("l_ur", "l_ul", "l_lr", "l_ll")]
r = lambda k, d=1: f"{W[k]:.{d}f}"  # noqa: E731
i_cont = CL["CL-F1-I-CONT"]["value"]

# --- pack and disconnect
box(20, 150, 150, 112, "PWR", "PWR-001", "Flight pack 4S 6500",
    ["14.8 V nom", f"cont {i_cont:.1f} A", "peak 120 A &lt; 5 s"])
PL = CL["CALC-F1-PACKLEAD"]["outputs"]
pair(170, 206, 242, 206)
out.append(f'<text x="206" y="290" font-family="{MONO}" font-size="11" fill="{FG2}" text-anchor="middle">'
           f'pack lead {PL["lead_awg"]} AWG · +{PL["lead_rise_c"]:.1f} °C</text>')
disconnect(252, 206, "E-HRN-10", "AS150U")
pair(262, 206, 280, 206)
box(280, 150, 130, 112, "PWR", "PWR-002", "Disconnect",
    ["anti-spark 15 Ω", "70 A / 140 A", f"t95 {CL['CL-F1-PRECHARGE-T95']['value']:.0f} ms"])
# --- main path to power board
pair(410, 206, 540, 206, f"{W['main_awg']} AWG ≤ 50 mm", 475, 190)
out.append(f'<text x="475" y="236" font-family="{MONO}" font-size="11" fill="{FG2}" text-anchor="middle">+{r('main_rise_c')} °C</text>')
box(540, 150, 150, 112, "PWR", "PWR-003", "Power board",
    ["CoreWing PDB", "90 A / 215 A pk", "FC BEC 5 V"])
pair(690, 206, 760, 206, f"{W['main_awg']} AWG", 725, 190)
box(760, 150, 110, 112, "PWR", "PWR-004", "Bus board", ["2 × 8 AWG bars", "4 ESC + fuse"])

# --- ESC leads (four)
esc = [("PRP-002-UR", "ESC upper R"), ("PRP-002-UL", "ESC upper L"),
       ("PRP-002-LR", "ESC lower R"), ("PRP-002-LL", "ESC lower L")]
for k, (pid, name) in enumerate(esc):
    y = 40 + k * 110
    pair(870, 206, 1010, y + 46, bend=900 + k * 14)
    cap(990, y + 58)
    box(1010, y, 150, 92, "PRP", pid, name, ["45 A (55 A 10 s)", "+680 µF at pads"])
    sig(f"1190,{y + 70} 1160,{y + 70}")
out.append(f'<text x="955" y="28" font-family="{MONO}" font-size="11" fill="{FG2}" text-anchor="middle">'
           f'{W["esc_awg"]} AWG · {min(LEN):.2f}–{max(LEN):.2f} m · +{r("esc_rise_c")} °C</text>')
out.append(f'<text x="1085" y="478" font-family="{MONO}" font-size="11" fill="{FG3}" text-anchor="middle">'
           f'to motor: 3 × 3.5 mm bullet</text>')

# --- UBEC branch
pair(815, 262, 815, 364)
fuse(815, 380, "5 A")
pair(815, 396, 815, 430)
box(740, 430, 150, 100, "PWR", "PWR-005", "UBEC 6 V 8 A",
    [f"req ≥ {CL['CL-F1-SERVO-BEC-REQ']['value']:.1f} A", f"{W['feed_awg']} AWG feed"])
pair(740, 500, 610, 500, f"{W['bus_awg']} AWG", 675, 488)
box(460, 450, 150, 92, "MEC", "MEC servos", "2 × elevon servo",
    [f"stall {CL['CL-F1-SERVO-STALL-BUS']['value']:.1f} A both", "6 V"])

# --- avionics
box(240, 330, 170, 92, "AVN", "AVN-001", "Flight controller",
    ["BATT_MONITOR 4", "Q_M_BAT_CURR_MAX 100"])
sig("615,262 615,300 325,300 325,330", "GH-6 · V, I, 5 V · no Vx", 470, 294, data=True)
sig("410,400 430,400 430,560 1190,560 1190,110", "DShot ×4", 1120, 552)
sig("325,422 325,496 460,496", "PWM ×2", 392, 488)

# --- frame
body = "\n".join(out)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 580" width="1200" height="580" '
       f'role="img" aria-label="K09-L power distribution schematic">\n{body}\n</svg>\n')
(HERE / "power-schematic.svg").write_text(svg, encoding="utf-8")
print("wrote", HERE / "power-schematic.svg")
