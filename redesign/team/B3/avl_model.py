"""B3 stability and control: AVL 3.52 model of the K09-L quad tailsitter (wing + two fins).

Library used by sc_analysis.py (the proof-chain script) and run_avl_study.py (convergence and option studies).
Every function is a pure function of its arguments: the AVL input text is generated from the arguments, AVL is run
in a temporary folder, and the parsed result is cached in avl/cache/<sha1 of inputs>.json so build_graph.py can
re-run the calculations in milliseconds and without AVL installed. Delete avl/cache/ to force fresh AVL runs.

Frame (redesign/params/params.json#frame, identical to AVL geometry axes): x aft from the wing root LE, y right,
z up in cruise. AVL controls: d1 = "elevator" (both elevons, +TE down), d2 = "aileron" (+ right TE down).
Elevons are two panels per side (inboard and outboard of the fin root) driven together, as in params.json.

What AVL does not model (added by hand in sc_analysis.py with stated assumptions): propeller normal force (Ribner),
motor-tube and motor drag in sideslip, the pod, viscous section drag, stall. Fins are flat plates (foam board).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
AVL_EXE = Path(os.environ.get("AVL_EXE", "C:/Users/dillo/tools/avl/avl352.exe"))
AVL_DIR = HERE / "avl"
CACHE = AVL_DIR / "cache"
NL = chr(10)
AIRFOIL = AVL_DIR / "s5010.dat"           # UIUC coordinate file (copy of team/B2/airfoils/s5010.dat, SRC-B2-S5010-COORD)

# lattice levels for the convergence check: (chordwise vortices, target spanwise spacing m)
LATTICE = {"coarse": (8, 0.025), "medium": (12, 0.0125), "fine": (16, 0.008), "xfine": (18, 0.0076)}   # xfine: AVL NVMAX 5000
DEFAULT_LATTICE = "medium"


# ------------------------------------------------------------------------------------------- geometry text
def _nspan(width, ds):
    return max(1, int(round(width / ds)))


def avl_geometry(g: dict, lattice: str = DEFAULT_LATTICE) -> str:
    """AVL input file text from a geometry dict.

    g keys: b, c, ef (elevon chord fraction), yin [y0,y1], yout [y0,y1], fy (fin station), fh (fin half-height),
            fle, fte (fin LE/TE x), xref, zref, airfoil (True: S5010 camber line), optional: egain (elevon
            gain; 1 = thin-airfoil degrees, eta = physical degrees),
            tipfin {"xle","c","h"} (vertical fins at the wing tips), fin_le_tip (fin LE x at the fin tips; swept LE)
    """
    nc, ds = LATTICE[lattice]
    b2, c = g["b"] / 2, g["c"]
    hinge = 1.0 - g["ef"]
    S = g["b"] * c
    af = f"AFILE\n{AIRFOIL.name}\n" if g.get("airfoil", True) else ""
    text = _wing_text(g, nc, ds, af, hinge, S, lattice)
    # fins: vertical flat plates at y = +/- fy, z = -fh..+fh, break at the wing plane so strip edges align
    fle_tip = g.get("fin_le_tip", g["fle"])
    fins = ["#", "SURFACE", "Fin", f"{max(6, nc - 2)} 1.0", "YDUPLICATE", "0.0"]
    if g.get("fin_sections"):
        # as-designed outline (verify_asdesigned.py): [(z, x_le, chord)] for z >= 0, mirrored to the lower half-fin
        up = sorted(g["fin_sections"])
        secs = [(-z, x, ch) for z, x, ch in reversed(up) if z > 0] + up
        for i, (z, xle, ch) in enumerate(secs):
            n = _nspan(secs[i + 1][0] - z, ds) if i + 1 < len(secs) else 1
            fins += ["SECTION", f"{xle:.5f} {g['fy']:.5f} {z:.5f} {ch:.5f} 0.0  {n} 1.0"]
        return text + "\n".join(fins) + "\n"
    nz = _nspan(g["fh"], ds)
    for z, xle in ((-g["fh"], fle_tip), (0.0, g["fle"]), (g["fh"], fle_tip)):
        fins += ["SECTION", f"{xle:.5f} {g['fy']:.5f} {z:.5f} {g['fte'] - xle:.5f} 0.0  {nz} 1.0"]
    text += "\n".join(fins) + "\n"
    if g.get("tipfin"):
        t = g["tipfin"]
        nzt = _nspan(t["h"], ds)
        tf = ["#", "SURFACE", "Tipfin", f"{max(6, nc - 4)} 1.0", "YDUPLICATE", "0.0"]
        for z in (-t["h"], 0.0, t["h"]):
            tf += ["SECTION", f"{t['xle']:.5f} {b2:.5f} {z:.5f} {t['c']:.5f} 0.0  {nzt} 1.0"]
        text += "\n".join(tf) + "\n"
    return text


def _wing_text(g, nc, ds, af, hinge, S, lattice):
    """Wing surface text. Panels between stations (0, elevon edges, fin root, tip); each elevon panel is bounded by
    control sections and each plain panel by plain sections. Where the two meet, the plain panel gives up 2 mm so
    AVL's linear interpolation of the deflection only acts over a 2 mm strip (gap at the fin root, pod, tip)."""
    b2, c = g["b"] / 2, g["c"]
    ys = sorted({0.0, g["yin"][0], g["yin"][1], g["fy"], g["yout"][0], g["yout"][1], b2})
    elev = [(g["yin"][0], g["yin"][1]), (g["yout"][0], g["yout"][1])]
    panels = [(ys[i], ys[i + 1], any(a - 1e-9 <= ys[i] and ys[i + 1] <= e + 1e-9 for a, e in elev))
              for i in range(len(ys) - 1)]
    secs = []                              # (y, control?)
    for i, (ya, yb, ctrl) in enumerate(panels):
        prev = panels[i - 1][2] if i > 0 else ctrl
        if i == 0:
            secs.append((ya, ctrl))
        elif prev != ctrl:                 # flag changes at ya: plain side gives up 2 mm
            if ctrl:
                secs[-1] = (ya - 0.002, False)
                secs.append((ya, True))
            else:
                secs.append((ya + 0.002, False))
        secs.append((yb, ctrl))
    # drop duplicates (same y, same flag)
    clean = []
    for y, f in secs:
        if clean and abs(clean[-1][0] - y) < 1e-9 and clean[-1][1] == f:
            continue
        clean.append((y, f))
    lines = [f"K09-L quad tailsitter, B3 (team/B3/avl_model.py), lattice {lattice}",
             "0.0                     | Mach",
             "0 0 0.0                 | iYsym iZsym Zsym",
             f"{S:.5f} {c:.5f} {g['b']:.5f}   | Sref Cref Bref",
             f"{g['xref']:.5f} 0.0 {g['zref']:.5f}   | Xref Yref Zref = CG",
             "0.0                     | CDp (not used: AVL gives induced drag only)",
             "#", "SURFACE", "Wing", f"{nc} 1.0", "YDUPLICATE", "0.0", "ANGLE", "0.0"]
    for i, (y, ctrl) in enumerate(clean):
        nxt = clean[i + 1][0] if i + 1 < len(clean) else None
        n = _nspan(nxt - y, ds) if nxt is not None else 1
        lines += ["SECTION", f"0.0 {y:.5f} 0.0 {c:.5f} 0.0  {n} 1.0"]
        if af:
            lines += af.strip().split("\n")
        if ctrl:
            k = g.get("egain", 1.0)
            lines += ["CONTROL", f"elevator {k:.4f} {hinge:.4f} 0 0 0 1.0",
                      "CONTROL", f"aileron {k:.4f} {hinge:.4f} 0 0 0 -1.0"]
    return "\n".join(lines) + "\n"


def avl_mass(m, xcg, zcg, ixx, iyy, izz, ixz, rho, g0) -> str:
    return ("# K09-L point-mass model at the CG (inertias from team/A3 roll-up, scaled to the run mass)\n"
            "Lunit = 1.0 m\nMunit = 1.0 kg\nTunit = 1.0 s\n"
            f"g = {g0:.5f}\nrho = {rho:.4f}\n"
            "#  mass   x     y   z    Ixx   Iyy   Izz   Ixy  Ixz  Iyz\n"
            f"{m:.4f} {xcg:.5f} 0.0 {zcg:.5f} {ixx:.5f} {iyy:.5f} {izz:.5f} 0.0 {ixz:.5f} 0.0\n")


# ------------------------------------------------------------------------------------------- running AVL
_NUM = r"([-+]?[0-9]*\.?[0-9]+(?:[EeDd][-+]?[0-9]+)?)"


def _grab(txt, key):
    m = re.search(rf"(?<![\w']){re.escape(key)}\s*=\s*{_NUM}", txt)
    return float(m.group(1)) if m else None


ST_KEYS = ["Alpha", "Beta", "CLtot", "CDtot", "CDind", "Cmtot", "Cltot", "Cntot", "CYtot", "e",
           "CLa", "CYa", "Cla", "Cma", "Cna", "CLb", "CYb", "Clb", "Cmb", "Cnb",
           "CLp", "CLq", "CLr", "CYp", "CYr", "Clp", "Clq", "Clr", "Cmp", "Cmq", "Cmr", "Cnp", "Cnq", "Cnr",
           "CLd01", "CDd01", "Cmd01", "Cld01", "Cnd01", "CLd02", "CYd02", "Cld02", "Cmd02", "Cnd02", "Xnp"]


def parse_st(t: str) -> dict:
    d = {k: _grab(t, k) for k in ST_KEYS}
    for name, key in (("elevator", "d1"), ("aileron", "d2")):
        m = re.search(rf"^\s*{name}\s*=\s*{_NUM}", t, re.M)
        d[key] = float(m.group(1)) if m else None
    m = re.search(r"Clb Cnr / Clr Cnb\s*=\s*" + _NUM, t)
    d["spiral"] = float(m.group(1)) if m else None
    return d


def parse_strips(t: str) -> list:
    """Wing strip loading from an FS dump: [(y, chord, cl)] for the right wing (first wing surface)."""
    rows, cur = [], None
    for line in t.splitlines():
        m = re.match(r"\s*Surface #\s*(\d+)\s+(\S+)", line)
        if m:
            cur = (int(m.group(1)), m.group(2))
            continue
        if cur and cur[0] == 1 and re.match(r"\s*\d+\s+[-+0-9.]", line):
            v = line.split()
            try:
                yle, chord, cl = float(v[2]), float(v[4]), float(v[9])
                rows.append((yle, chord, cl))
            except (ValueError, IndexError):
                pass
    return rows


def parse_eig(t: str) -> list:
    ev = []
    for line in t.splitlines():
        if line.strip().startswith("#") or not line.strip():
            continue
        p = line.split()
        if len(p) >= 3:
            try:
                ev.append([float(p[1].replace("D", "E")), float(p[2].replace("D", "E"))])
            except ValueError:
                pass
    return ev


def _key(*parts) -> str:
    h = hashlib.sha1()
    for p in parts:
        h.update(json.dumps(p, sort_keys=True).encode())
    return h.hexdigest()[:20]


def run_case(geom_text: str, case: list, mass_text: str | None = None, want=("st",), tag="") -> dict:
    """Run one AVL operating point. case = list of OPER commands (e.g. ["a a 4", "d1 d1 0"]).
    want: "st" (derivatives), "fs" (strip forces), "eig" (eigenvalues; needs mass_text and an "M" velocity block
    inside case). Returns {"st": {...}, "strips": [...], "eig": [...], "raw_st": text}. Cached."""
    key = _key(geom_text, case, mass_text, list(want), AIRFOIL.read_text() if AIRFOIL.exists() else "")
    cf = CACHE / f"{key}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    if not AVL_EXE.exists():
        raise RuntimeError(f"AVL not found at {AVL_EXE} and no cached result {cf.name}: run on the design machine")
    tmp = Path(tempfile.mkdtemp(prefix="b3avl_"))
    try:
        (tmp / "k.avl").write_text(geom_text)
        if AIRFOIL.exists():
            shutil.copy(AIRFOIL, tmp / AIRFOIL.name)
        cmds = ["LOAD k.avl"]
        if mass_text:
            (tmp / "k.mass").write_text(mass_text)
            cmds += ["MASS k.mass", "MSET 0"]
        cmds += ["OPER"] + case + ["x"]
        if "st" in want:
            cmds += ["st st.txt"]
        if "fs" in want:
            cmds += ["fs fs.txt"]
        cmds += [""]
        if "eig" in want:
            cmds += ["MODE", "N", "W", "k.eig", "", ""]
        cmds += ["QUIT"]
        p = subprocess.run([str(AVL_EXE)], input="\n".join(cmds) + "\n", text=True, capture_output=True,
                           cwd=str(tmp), timeout=3600)
        res = {}
        if "st" in want:
            t = (tmp / "st.txt").read_text()
            res["st"] = parse_st(t)
        if "fs" in want:
            res["strips"] = parse_strips((tmp / "fs.txt").read_text())
        if "eig" in want:
            res["eig"] = parse_eig((tmp / "k.eig").read_text())
        if "st" in want and res["st"].get("CLtot") is None:
            raise RuntimeError("AVL produced no ST output:\n" + p.stdout[-2000:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps(res, indent=0))
    return res


# ------------------------------------------------------------------------------------------- common runs
def geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref, **extra) -> dict:
    g = {"b": b, "c": c, "ef": ef, "yin": list(yin), "yout": list(yout), "fy": fy, "fh": fh, "fle": fle,
         "fte": fte, "xref": xref, "zref": zref, "airfoil": True}
    g.update(extra)
    return g


def derivatives(g, alpha_deg=4.0, lattice=DEFAULT_LATTICE, d1=0.0, d2=0.0, beta=0.0):
    case = [f"a a {alpha_deg}", f"b b {beta}", f"d1 d1 {d1}", f"d2 d2 {d2}"]
    return run_case(avl_geometry(g, lattice), case)["st"]


def derivatives_cl(g, CL, lattice=DEFAULT_LATTICE):
    """Stability derivatives at a given CL, elevons neutral."""
    return run_case(avl_geometry(g, lattice), [f"a c {CL}", "b b 0", "d1 d1 0", "d2 d2 0"])["st"]


def trim_sweep(g, cls, cm_t=0.0, lattice=DEFAULT_LATTICE):
    """One AVL session: for each CL, alpha for CL and elevator for Cm = cm_t about Xref (cm_t = -viscous correction
    so that AVL + correction trims to zero). Returns [{CL, alpha, d1, strips [(y, chord, cl)]}] (right wing). Cached."""
    geom = avl_geometry(g, lattice)
    case = {"cls": [round(c, 4) for c in cls], "cm_t": round(cm_t, 6)}
    key = _key(geom, case, "trim_sweep", AIRFOIL.read_text() if AIRFOIL.exists() else "")
    cf = CACHE / f"{key}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    if not AVL_EXE.exists():
        raise RuntimeError(f"AVL not found at {AVL_EXE} and no cached result {cf.name}: run on the design machine")
    tmp = Path(tempfile.mkdtemp(prefix="b3avl_"))
    out = []
    try:
        (tmp / "k.avl").write_text(geom)
        shutil.copy(AIRFOIL, tmp / AIRFOIL.name)
        cmds = ["LOAD k.avl", "OPER"]
        for i, c in enumerate(case["cls"]):
            cmds += [f"a c {c}", f"d1 pm {case['cm_t']}", "d2 d2 0", "b b 0", "x",
                     "ft", f"ft{i}.txt", "fs", f"fs{i}.txt"]
        cmds += ["", "QUIT"]
        subprocess.run([str(AVL_EXE)], input=NL.join(cmds) + NL, text=True, capture_output=True, cwd=str(tmp),
                       timeout=3600)
        for i, c in enumerate(case["cls"]):
            ft = (tmp / f"ft{i}.txt").read_text()
            st = parse_st(ft)
            out.append({"CL": st["CLtot"], "alpha": st["Alpha"], "d1": st["d1"], "CDind": st["CDind"],
                        "strips": parse_strips((tmp / f"fs{i}.txt").read_text())})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps(out, indent=0))
    return out


def trim(g, CL, lattice=DEFAULT_LATTICE, strips=False):
    """Alpha for CL, elevator for Cm = 0 about Xref."""
    case = [f"a c {CL}", "d1 pm 0", "d2 d2 0"]
    r = run_case(avl_geometry(g, lattice), case, want=("st", "fs") if strips else ("st",))
    return r


def modes(g, CL, V, mass_text, lattice=DEFAULT_LATTICE):
    case = [f"a c {CL}", "d1 pm 0", "d2 d2 0", "M", f"V {V}", "D 1.225", "G 9.80665", ""]
    return run_case(avl_geometry(g, lattice), case, mass_text=mass_text, want=("st", "eig"))
