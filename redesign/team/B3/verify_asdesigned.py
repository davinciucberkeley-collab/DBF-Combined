"""B3 verification round (V1): the S&C chain re-run on the settled CAD geometry and the A3-R6a mass roll-up.

What changes against the R4 model (sc_analysis.py, which uses the params.json planform):
  fins     as built by subsystems/fins/fusion/fins.py: the laminate starts 0.5 mm aft of the 22 mm tube (x 0.0565,
           not the tube axis 0.045), its top edge slopes from the collar (z 0.1595 at the LE) to the half height at
           x 0.2746 and the tip is cut down to the D5 step (z 0.2005). Half-fin area 0.0455 m2 vs 0.0578 m2 modelled.
           Two brackets: BOARD (laminate only; tube cross-flow drag kept as in R4) and TUBE (the tube sealed to the
           board by the fillet acts as the fin LE from x 0.034 up to the collar; tube drag term dropped).
  elevons  wing/params.json elevon.end_gap_m 1 mm at each panel end: spans [0.071, 0.299] and [0.341, 0.559].
  mass     A3-R6a: basic 2.322 kg, predicted 2.436 kg, CG x 0.0522 / 0.0536 m, z +0.0185 m, inertia (claims).
           The requirements stay at the 2.6 kg gate (CL from the gate mass), as in R4; the predicted mass is a
           second column.
Methods (fidelity justified in SIMULATION-REPORT.md):
  AVL 3.52 on four lattices (coarse/medium/fine/xfine), GCI on the three finest (Celik 2008, unequal ratios).
  Independent checks: a 60-line flat-plate VLM in this file (wing alone: CLa, Xnp), DATCOM-style fin Cn_beta,
  strip-theory roll power. 2-D RANS of the elevon effectiveness in cfd_elevon.py (results read via ASM-B3-V-ETA-*).

Run:  python -I redesign/team/B3/verify_asdesigned.py        (AVL ~5 min the first time, then cached)
      -> claims.verify.json, results/verify.json; then python -I redesign/team/B3/plot_verify.py
"""
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402
import avl_model as AV  # noqa: E402
import flight_models as FM  # noqa: E402
import sc_analysis as SC  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"], out="claims.verify.json")
P = "P:"
LEVELS = ("coarse", "medium", "fine", "xfine")

# ------------------------------------------------------------------------------------------- as-designed geometry
# Read from the CAD module on 2026-11-10 (fins.py geometry(), D3 R4; wing/params.json D1-R1). cad_check() below
# re-reads the CAD and stops the script if any of these moved, so the assumption cannot silently go stale.
FIN_CAD = {"x_le_board": 0.0565, "x_tube_front": 0.034, "z_le_top": 0.1595, "z_collar_bottom": 0.1475,
           "x_sq": 0.2746, "h": 0.21, "z_step": 0.2005, "te": 0.32, "area_half_board": 0.04550}
kit.assumption("ASM-B3-V-FIN-CAD", "As-designed half-fin outline (fins.py R4)",
               "x_le_board, x_tube_front, z_le_top, z_collar_bottom, x_sq, h, z_step, te (m); half-fin board area (m2)",
               basis="subsystems/fins/fusion/fins.py geometry() and half_fin_loop() evaluated on 2026-11-10 "
                     "(verify_asdesigned.cad_check re-reads it on every run)",
               value=FIN_CAD, unit="m", status="PROPOSED")
kit.assumption("ASM-B3-V-ZCG", "A3-R6a CG height", "z of the take-off CG, 550 g pack at -0.022",
               basis="team/A3/rollup/rollup.json cg.cg_m[2] (A3-R6a, 2026-11-10); A3 publishes only the range-use "
                     "claim CL-A3-CG-Z-RANGE (CR-B3-24 asks for a CL-A3-CG-Z in m)", value=0.0185, unit="m",
               status="PROPOSED")
kit.assumption("ASM-B3-V-ELEVON-GAP", "Elevon panel end gap (wing CAD)", "Gap at each end of each elevon panel",
               basis="subsystems/wing/params.json elevon.end_gap_m (D1-R1)", value=0.001, unit="m", status="PROPOSED")


def cad_check():
    """Re-read the fin outline from the CAD module; raise if FIN_CAD is stale (> 0.5 mm or > 1 % area)."""
    import importlib.util
    red = HERE.parents[1]
    sys.path.insert(0, str(red / "fusion"))
    import k09kit as k9
    spec = importlib.util.spec_from_file_location("fins_cad", red / "subsystems/fins/fusion/fins.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    Pp = k9.load_params()
    co, _ = k9.section(Pp)
    G = m.geometry(Pp, m.load_local(), co)
    lp = m.half_fin_loop(G, True)
    A = 0.5 * sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(lp, lp[1:] + lp[:1]))
    now = {"x_le_board": G["x_le"], "x_tube_front": G["xt"] - G["r_t"], "z_le_top": G["z_le_top"],
           "z_collar_bottom": G["z_sc0"], "x_sq": G["x_sq"], "h": G["h"], "z_step": G["z_step"], "te": G["te"],
           "area_half_board": A}
    bad = {k: (FIN_CAD[k], round(v, 5)) for k, v in now.items()
           if abs(v - FIN_CAD[k]) > (0.01 * FIN_CAD[k] if k == "area_half_board" else 0.0005)}
    if bad:
        raise SystemExit(f"FIN_CAD is stale, update it from the CAD: {bad}")
    return now, lp


def fin_sections(f, mode):
    """AVL fin sections [(z, x_le, chord)] for z >= 0 from the CAD outline. mode BOARD / TUBE (see module doc)."""
    slope = (f["h"] - f["z_le_top"]) / (f["x_sq"] - f["x_le_board"])
    x_at = lambda z: f["x_le_board"] + (z - f["z_le_top"]) / slope   # noqa: E731  LE on the sloped top edge
    te = f["te"]
    if mode == "BOARD":
        secs = [(0.0, f["x_le_board"], te - f["x_le_board"]),
                (f["z_le_top"], f["x_le_board"], te - f["x_le_board"])]
    else:   # tube is the LE up to the collar bottom, collar to the board top
        secs = [(0.0, f["x_tube_front"], te - f["x_tube_front"]),
                (f["z_collar_bottom"], f["x_tube_front"], te - f["x_tube_front"]),
                (f["z_le_top"], f["x_le_board"], te - f["x_le_board"])]
    secs.append((f["z_step"], x_at(f["z_step"]), te - x_at(f["z_step"])))
    # top strip z_step..h, LE on the slope, TE at x_sq (the D5 step); area 0.03 % of S, kept for completeness
    secs.append((f["h"] - 1e-4, x_at(f["h"] - 1e-4), max(f["x_sq"] - x_at(f["h"] - 1e-4), 0.002)))
    return [tuple(round(v, 5) for v in s) for s in secs]


def fin_area(secs):
    return sum(0.5 * (c0 + c1) * (z1 - z0) for (z0, _, c0), (z1, _, c1) in zip(secs, secs[1:]))


def as_built(yin, yout, gap):
    return [yin[0] + gap, yin[1] - gap], [yout[0] + gap, yout[1] - gap]


@contextmanager
def patched_geometry(extra):
    """sc_analysis builds every AVL geometry through SC._g: add the as-designed keys for the duration of a calc."""
    orig = SC._g

    def g(*a, **k):
        d = orig(*a, **k)
        d.update(extra)
        return d
    SC._g = g
    try:
        yield
    finally:
        SC._g = orig


# ------------------------------------------------------------------------------------------- independent VLM
def flat_vlm(b, c, nx=10, ny=40):
    """Independent check of AVL: planar flat-plate rectangular wing, horseshoe vortices (bound at panel 1/4,
    control point at 3/4), cosine spanwise spacing, Biot-Savart with trailing legs to +infinity. Returns
    CLa (1/rad) and Xnp (m from the LE). Standard library only (Gauss elimination)."""
    import math as m
    ys = [-b / 2 * m.cos(m.pi * j / ny) for j in range(ny + 1)]
    pan = []
    for i in range(nx):
        x0, x1 = c * i / nx, c * (i + 1) / nx
        for j in range(ny):
            ya, yb = ys[j], ys[j + 1]
            pan.append((x0 + 0.25 * (x1 - x0), ya, yb, x0 + 0.75 * (x1 - x0), 0.5 * (ya + yb), (yb - ya)))

    def seg(xp, yp, xa, ya, xb, yb):
        # w (z-velocity per unit circulation) at (xp, yp, 0) from a segment A->B in the z = 0 plane
        r1x, r1y, r2x, r2y = xp - xa, yp - ya, xp - xb, yp - yb
        cz = r1x * r2y - r1y * r2x
        if abs(cz) < 1e-12:
            return 0.0
        r1, r2 = m.hypot(r1x, r1y), m.hypot(r2x, r2y)
        r0x, r0y = xb - xa, yb - ya
        k = (r0x * (r1x / r1 - r2x / r2) + r0y * (r1y / r1 - r2y / r2)) / (4 * m.pi * cz * cz)
        return k * cz

    def semi(xp, yp, xa, ya):
        # semi-infinite leg from (xa, ya) to x = +inf (sign: circulation running aft)
        dy = yp - ya
        if abs(dy) < 1e-12:
            return 0.0
        dx = xp - xa
        return (1 + dx / m.hypot(dx, dy)) / (4 * m.pi * dy)

    N = len(pan)
    A = [[0.0] * N for _ in range(N)]
    for i, (_, _, _, xc, yc, _) in enumerate(pan):
        for j, (xb, ya, yb, _, _, _) in enumerate(pan):
            A[i][j] = -semi(xc, yc, xb, ya) + seg(xc, yc, xb, ya, xb, yb) + semi(xc, yc, xb, yb)
    rhs = [-1.0] * N                     # w = -V alpha with V alpha = 1
    for k in range(N):                   # Gauss elimination with partial pivoting
        p = max(range(k, N), key=lambda r: abs(A[r][k]))
        A[k], A[p], rhs[k], rhs[p] = A[p], A[k], rhs[p], rhs[k]
        for r in range(k + 1, N):
            f = A[r][k] / A[k][k]
            if f:
                for q in range(k, N):
                    A[r][q] -= f * A[k][q]
                rhs[r] -= f * rhs[k]
    G = [0.0] * N
    for k in range(N - 1, -1, -1):
        G[k] = (rhs[k] - sum(A[k][q] * G[q] for q in range(k + 1, N))) / A[k][k]
    L = [abs(g) * p[5] for g, p in zip(G, pan)]
    Ltot = sum(L)
    return {"CLa": 2 * Ltot / (b * c), "xnp": sum(l * p[0] for l, p in zip(L, pan)) / Ltot}


def gci3(f1, f2, f3, r21, r32, Fs=1.25):
    """Celik et al. (2008) with unequal refinement ratios; f1 finest."""
    e21, e32 = f2 - f1, f3 - f2
    if abs(e21) < 1e-12 or abs(e32) < 1e-12 or e32 / e21 <= 0:
        return {"p": None, "f_ext": f1, "gci_pct": 100 * Fs * abs(e21 / f1) if f1 else None,
                "note": "oscillatory or flat: GCI from the fine-medium change with Fs 1.25"}
    s = 1.0
    p = abs(math.log(abs(e32 / e21))) / math.log(r21)
    for _ in range(100):
        p = abs(math.log(abs(e32 / e21)) + math.log((r21 ** p - s) / (r32 ** p - s))) / math.log(r21)
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    return {"p": p, "f_ext": f_ext, "gci_pct": 100 * Fs * abs(e21 / f1) / (r21 ** p - 1)}


def lattice_count(text):
    """Total horseshoe vortices in an AVL input text (sum of Nchord x Nspan over the surfaces)."""
    lines, n, i, nc = text.splitlines(), 0, 0, None
    while i < len(lines):
        if lines[i].strip() == "SURFACE":
            nc = int(lines[i + 2].split()[0])
            dup = any(l.strip() == "YDUPLICATE" for l in lines[i:i + 6])
            k, ns = i + 3, 0
            while k < len(lines) and lines[k].strip() != "SURFACE":
                if lines[k].strip() == "SECTION":
                    ns += int(lines[k + 1].split()[5])
                k += 1
            n += nc * ns * (2 if dup else 1)
            i = k
        else:
            i += 1
    return n


# ------------------------------------------------------------------------------------------- calculations
GEO = SC.GEO
GEOU = SC.GEOU


@kit.calc("CALC-B3-V-LATTICE", title="AVL lattice convergence on the as-designed geometry (4 levels, GCI)",
          inputs={**GEO, "fin": "ASM-B3-V-FIN-CAD", "gap": "ASM-B3-V-ELEVON-GAP", "cgf": "CL-A3-CG-X",
                  "zref": "ASM-B3-V-ZCG", "S": "CL-A1-WING-AREA", "m": P + "requirements.mtow_gate_kg",
                  "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "vt": "CL-B3-VT-TRIM"},
          units={**GEOU, "gap": "m", "zref": "m", "S": "m2", "m": "kg", "rho": "kg/m3", "vt": "m/s"},
          cites=["SRC-B3-AVL"],
          equation="AVL at CL(1.3 Vs, gate) about the A3 CG on coarse / medium / fine / xfine lattices; "
                   "GCI (Celik 2008) on (fine, medium, coarse) with r = sqrt(N ratio); xfine as a check")
def lattice(b, c, ef, yin, yout, fy, fh, fle, fte, fin, gap, cgf, zref, S, m, g, rho, vt):
    xref = cgf * c
    yi, yo = as_built(yin, yout, gap)
    geo = AV.geometry_from(b, c, ef, yi, yo, fy, fh, fle, fte, xref, zref, fin_sections=fin_sections(fin, "BOARD"))
    CL = 2 * m * g / (rho * vt * vt * S)
    rows, cnt = {}, {}
    for lv in LEVELS:
        d = AV.derivatives_cl(geo, CL, lv)
        cnt[lv] = lattice_count(AV.avl_geometry(geo, lv))
        rows[lv] = {k: d[k] for k in ("Xnp", "CLa", "Cmd01", "Cld02", "Cnb", "Clb", "Cnr", "Clp", "Alpha")}
    # GCI on coarse / medium / fine (r 1.42 / 1.67 in sqrt(N)); xfine (AVL's 5000-vortex ceiling, r 1.10) is the
    # independent check that the extrapolated value is approached from the right side
    r21 = math.sqrt(cnt["fine"] / cnt["medium"])
    r32 = math.sqrt(cnt["medium"] / cnt["coarse"])
    out = {"N": cnt, "rows": rows, "r21": r21, "r32": r32, "CL": CL}
    for k in ("Xnp", "CLa", "Cmd01", "Cld02", "Cnb"):
        out[f"gci_{k}"] = gci3(rows["fine"][k], rows["medium"][k], rows["coarse"][k], r21, r32)
        fe = out[f"gci_{k}"]["f_ext"]
        out[f"gci_{k}"]["xfine_minus_ext_rel"] = (rows["xfine"][k] - fe) / fe if fe else None
    out["xnp_xfine"] = rows["xfine"]["Xnp"]
    out["xnp_ext"] = out["gci_Xnp"]["f_ext"]
    out["dxnp_fine_xfine_c"] = abs(rows["xfine"]["Xnp"] - rows["fine"]["Xnp"]) / c
    out["cnb_gci_pct"] = out["gci_Cnb"]["gci_pct"]
    out["cnb_spread_abs"] = max(r["Cnb"] for r in rows.values()) - min(r["Cnb"] for r in rows.values())
    return out


kit.claim("CL-B3-V-XNP-LATTICE", "Xnp change fine -> xfine lattice, as designed", calc="CALC-B3-V-LATTICE",
          output="dxnp_fine_xfine_c", unit="-", limit=("<=", 0.005),
          how="Re-run verify_asdesigned.py with avl/cache deleted; four-lattice table in results/verify.json.")
kit.claim("CL-B3-V-CNB-GCI", "Cn_beta (AVL) GCI on the fine lattice, as designed", calc="CALC-B3-V-LATTICE",
          output="cnb_gci_pct", unit="-", limit=("<=", 2.0), how="As CL-B3-V-XNP-LATTICE.")


@kit.calc("CALC-B3-V-HAND", title="Independent checks of AVL: flat-plate VLM, DATCOM fin Cn_beta, strip roll power",
          inputs={"b": P + "wing.span_m", "c": P + "wing.chord_m", "fin": "ASM-B3-V-FIN-CAD",
                  "cgf": "CL-A3-CG-X", "ef": P + "wing.elevon.chord_frac", "yin": P + "wing.elevon.inboard_y_m",
                  "yout": P + "wing.elevon.outboard_y_m", "gap": "ASM-B3-V-ELEVON-GAP", "fy": P + "fins.y_m",
                  "fh": P + "fins.half_height_m", "fle": P + "fins.le_x_m", "fte": P + "fins.te_x_m",
                  "zref": "ASM-B3-V-ZCG"},
          units={"b": "m", "c": "m", "yin": "m", "yout": "m", "gap": "m", "fy": "m", "fh": "m",
                 "fle": "m", "fte": "m", "zref": "m"},
          equation="VLM: horseshoes, 10 x 40 ; fin: dCnb = 2 CLa_v (2 A_h / S) (x_ac,v - x_cg)/b, CLa_v Helmbold on "
                   "AR_v = (2h)^2/(2 A_h) ; Cl_da = 2 CLa_w tau/(S b) sum c y dy, tau = cl_d/cl_a thin airfoil")
def hand(b, c, fin, cgf, ef, yin, yout, gap, fy, fh, fle, fte, zref):
    xcg = cgf * c
    S_ = b * c
    v = flat_vlm(b, c)
    # AVL on the same flat wing (no camber, tiny fin) for an apples-to-apples comparison
    tiny = [(0.0, fte - 0.0005, 0.0004), (0.001, fte - 0.0005, 0.0004)]
    gw = AV.geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, 0.07, 0.0, airfoil=False, fin_sections=tiny)
    dw = AV.derivatives(gw, 4.0, "fine")
    out = {"vlm_CLa": v["CLa"], "vlm_xnp": v["xnp"], "avl_flat_CLa": dw["CLa"], "avl_flat_xnp": dw["Xnp"],
           "xnp_diff_c": (dw["Xnp"] - v["xnp"]) / c, "cla_diff_rel": dw["CLa"] / v["CLa"] - 1}
    AR = b * b / S_
    out["helmbold_CLa"] = 2 * math.pi * AR / (2 + math.sqrt(AR * AR + 4))
    # fin Cn_beta (board outline) by DATCOM-style hand method; x_ac at the quarter chord of each strip
    secs = fin_sections(fin, "BOARD")
    A_h = fin_area(secs)
    xac = sum(0.5 * ((x0 + c0 / 4) * c0 + (x1 + c1 / 4) * c1) * (z1 - z0)
              for (z0, x0, c0), (z1, x1, c1) in zip(secs, secs[1:])) / A_h
    ARv = (2 * fin["h"]) ** 2 / (2 * A_h)
    clav = 2 * math.pi * ARv / (2 + math.sqrt(ARv * ARv + 4))
    out.update({"fin_area_half": A_h, "fin_xac": xac, "fin_ARv": ARv, "fin_CLa": clav,
                "fin_dCnb_hand": 2 * clav * 2 * A_h / S_ * (xac - xcg) / b,
                "fin_area_half_r4": (fte - fle) * fh})
    gf = AV.geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, xcg, zref, fin_sections=secs)
    gn = AV.geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, xcg, zref, fin_sections=tiny)
    d_f, d_n = AV.derivatives(gf, 4.0, "fine"), AV.derivatives(gn, 4.0, "fine")
    out["fin_dCnb_avl"] = d_f["Cnb"] - d_n["Cnb"]
    out["fin_hand_vs_avl"] = out["fin_dCnb_hand"] / out["fin_dCnb_avl"] - 1
    # roll power, strip theory, thin-airfoil tau, wing CLa from AVL
    th = math.acos(1 - 2 * (1 - ef))
    tau = (1 - (th - math.sin(th)) / math.pi)
    yi, yo = as_built(yin, yout, gap)
    integ = sum(0.5 * (y1 * y1 - y0 * y0) for y0, y1 in (yi, yo)) * c
    out["clda_strip_per_deg"] = 2 * d_f["CLa"] * tau * integ / (S_ * b) * math.pi / 180
    out["clda_avl_per_deg"] = abs(d_f["Cld02"])
    out["clda_strip_vs_avl"] = out["clda_strip_per_deg"] / out["clda_avl_per_deg"] - 1
    return out


kit.claim("CL-B3-V-VLM-XNP", "AVL vs independent VLM, flat wing Xnp difference", calc="CALC-B3-V-HAND",
          output="xnp_diff_c", unit="-", limit=("<=", 0.01),
          how="Re-run verify_asdesigned.py; flat_vlm() is independent code (horseshoe VLM, standard library).")
kit.claim("CL-B3-V-FIN-HAND", "Fin Cn_beta: DATCOM-style hand calc vs AVL (relative)", calc="CALC-B3-V-HAND",
          output="fin_hand_vs_avl", unit="-", how="As CL-B3-V-VLM-XNP.")


V_SM_GRID = [0.05, 0.06, 0.07, 0.08]
VIN = {**SC.CS_IN, "fin": "ASM-B3-V-FIN-CAD", "gap": "ASM-B3-V-ELEVON-GAP", "sm_min": P + "requirements.static_margin_min",
       "travel": P + "wing.elevon.deflection_deg", "tfrac": P + "requirements.elevon_trim_travel_max",
       "kslop": "ASM-B3-SLOP-TRIM-FRAC", "zcg": "ASM-B3-V-ZCG", "m_pred": "CL-A3-MASS-PREDICTED",
       "cgf": "CL-A3-CG-X", "x_a3_pred": "CL-A3-CG-X-PRED", "CLa": "CL-B3-CLA", "n": P + "propulsion.n_motors",
       "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
       "cna": "ASM-B3-PROP-CNA", "up": "ASM-B3-UPWASH", "pod": P + "pod.size_m", "kpod": "ASM-B3-POD-K"}
VU = {**SC.CS_U, "gap": "m", "travel": "deg", "zcg": "m", "m_pred": "kg", "x_a3_pred": "m", "D": "m",
      "x_prop": "m", "pod": "m"}
VIN.pop("xnp_a")
VIN.pop("xnp")


@kit.calc("CALC-B3-V-CG", title="NP and CG limits on the as-designed geometry; A3-R6a CG against them",
          inputs=VIN, units=VU, assumes=["ASM-B3-CLMAX-FLAP", "ASM-B3-PROP-CNA"], cites=["SRC-B3-AVL"],
          equation="as CALC-B3-AVL-LONG, -NP, -CG-LIMITS (sc_analysis.py) with the CAD fins and elevon spans, "
                   "zref = A3 z ; at the gate mass and at A3's predicted mass ; margins = limit - A3 CG")
def cg_v(b, c, ef, yin, yout, fy, fh, fle, fte, zref, dcm, eta, tab, m, g, rho, S, lo, li, va, slop, vmax, fin, gap,
         sm_min, travel, tfrac, kslop, zcg, m_pred, cgf, x_a3_pred, CLa, n, D, x_prop, cna, up, pod, kpod):
    x_a3 = cgf * c
    yi, yo = as_built(yin, yout, gap)
    secs = fin_sections(fin, "BOARD")
    geo = AV.geometry_from(b, c, ef, yi, yo, fy, fh, fle, fte, 0.0529, zcg, fin_sections=secs)
    d = AV.derivatives(geo, 4.0, "fine")
    xnp_a = d["Xnp"]
    npv = SC.neutral_point(xnp_a, d["CLa"], n, D, x_prop, S, c, b, cna, up, pod, kpod)
    out = {"x_a3": x_a3, "xnp_aero": xnp_a, "xnp": npv["xnp"], "CLa": d["CLa"], "Cmd": d["Cmd01"], "Cld": d["Cld02"]}
    grid0 = SC.SM_GRID
    SC.SM_GRID = V_SM_GRID       # bracket the R4 crossing (SM 0.063) only: 4 AVL trim sweeps per mass instead of 12
    with patched_geometry({"fin_sections": secs}):
      try:
        for tag, mm in (("gate", m), ("pred", m_pred)):
            r = SC.cg_limits(b, c, ef, yi, yo, fy, fh, fle, fte, zcg, xnp_a, npv["xnp"], dcm, eta, tab, mm, g, rho,
                            S, lo, li, va, slop, vmax, sm_min, travel, tfrac, kslop)
            out[f"x_fwd_{tag}"], out[f"x_aft_{tag}"], out[f"width_{tag}"] = r["x_fwd"], r["x_aft"], r["width"]
            out[f"binding_{tag}"], out[f"x_target_{tag}"] = r["binding"], r["x_target"]
            out[f"table_{tag}"] = r["table"]
            out[f"sm_fwd_{tag}"] = r["sm_fwd"]
      finally:
        SC.SM_GRID = grid0
    if not (V_SM_GRID[0] < out["sm_fwd_gate"] < V_SM_GRID[-1]):
        raise RuntimeError("forward-limit crossing outside V_SM_GRID: widen it")
    out["a3_fwd_margin"] = x_a3 - out["x_fwd_gate"]
    out["a3_aft_margin"] = out["x_aft_gate"] - x_a3
    out["a3pred_fwd_margin"] = x_a3_pred - out["x_fwd_pred"]
    out["a3pred_aft_margin"] = out["x_aft_pred"] - x_a3_pred
    out["sm_a3"] = (npv["xnp"] - x_a3) / c
    out["sm_a3_pred"] = (npv["xnp"] - x_a3_pred) / c
    return out


kit.claim("CL-B3-V-XNP-AERO", "Neutral point, wing and fins (AVL fine), as designed", calc="CALC-B3-V-CG",
          output="xnp_aero", unit="m", how="As CL-B3-XNP-AERO; lattice study CALC-B3-V-LATTICE.")
kit.claim("CL-B3-V-XNP", "Neutral point, whole aircraft, as designed", calc="CALC-B3-V-CG", output="xnp", unit="m",
          how="T-B3-TWIN-NP (FBWA glides at two pack positions).")
kit.claim("CL-B3-V-CG-FWD", "Forward CG limit, as designed, gate mass", calc="CALC-B3-V-CG", output="x_fwd_gate",
          unit="m", how="T-B3-CG-BALANCE + twin slow flight at the forward mark.")
kit.claim("CL-B3-V-CG-AFT", "Aft CG limit, as designed", calc="CALC-B3-V-CG", output="x_aft_gate", unit="m",
          how="T-B3-CG-BALANCE.")
kit.claim("CL-B3-V-CG-WIDTH", "CG range width, as designed, gate mass", calc="CALC-B3-V-CG", output="width_gate",
          unit="m", limit=(">=", 0.004), how="Follows from the two limits.")
kit.claim("CL-B3-V-CG-A3-FWD", "A3-R6a CG (550 g pack, -0.022) aft of the forward limit", calc="CALC-B3-V-CG",
          output="a3_fwd_margin", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE"],
          how="H1 balance of the built aircraft (T-B3-CG-BALANCE).")
kit.claim("CL-B3-V-CG-A3-AFT", "A3-R6a CG (550 g pack, -0.022) ahead of the aft limit", calc="CALC-B3-V-CG",
          output="a3_aft_margin", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE", "R-STATIC-MARGIN"],
          how="H1 balance of the built aircraft (T-B3-CG-BALANCE).")
kit.claim("CL-B3-V-CG-A3PRED-AFT", "A3 predicted CG (with growth) ahead of the aft limit at the predicted mass",
          calc="CALC-B3-V-CG", output="a3pred_aft_margin", unit="m", limit=(">=", 0.0),
          how="H1 balance of the built aircraft; growth lands aft (A3 CL-A3-CG-X-PRED).")
kit.claim("CL-B3-V-SM-A3", "Static margin at the A3-R6a CG, as designed", calc="CALC-B3-V-CG", output="sm_a3",
          unit="-", limit=(">=", P + "requirements.static_margin_min"), verifies=["R-STATIC-MARGIN"],
          how="T-B3-TWIN-NP.")


LIN = {**SC.LATIN, "fin": "ASM-B3-V-FIN-CAD", "gap": "ASM-B3-V-ELEVON-GAP", "x_aft": "CL-B3-V-CG-AFT",
       "zcg": "ASM-B3-V-ZCG", "vt": "CL-B3-VT-TRIM", "cgf": "CL-A3-CG-X", "vc": P + "performance.cruise_ms"}
LU = {**SC.LATU, "gap": "m", "x_aft": "m", "zcg": "m", "vt": "m/s", "vc": "m/s"}


@kit.calc("CALC-B3-V-LATDIR", title="Directional stability with the as-designed fins (R-DIRECTIONAL)",
          inputs=LIN, units=LU, assumes=["ASM-B3-PROP-CNA", "ASM-B3-CD-CYL", "ASM-B3-POD-K-YAW"],
          cites=["SRC-B3-AVL", "SRC-B3-RIBNER", "SRC-B3-MUNK"],
          equation="as CALC-B3-LATDIR (sc_analysis.lat_terms) with the CAD fin outline: BOARD (tube drag kept) and "
                   "TUBE (tube as fin LE, tube drag term removed); 1.3 Vs at the aft limit and cruise at the A3 CG")
def latdir_v(fin, gap, x_aft, zcg, vt, cgf, vc, **kw):
    x_a3 = cgf * kw["c"]
    q = lambda V: 0.5 * kw["rho"] * V * V   # noqa: E731
    W = kw["m"] * kw["g"]
    kw = dict(kw)
    kw["zref"] = zcg
    kw["yin"], kw["yout"] = as_built(kw["yin"], kw["yout"], gap)
    out = {}
    for mode in ("BOARD", "TUBE"):
        with patched_geometry({"fin_sections": fin_sections(fin, mode)}):
            a = SC.lat_terms(x_aft, W / (q(vt) * kw["S"]), **kw)
            cr = SC.lat_terms(x_a3, W / (q(vc) * kw["S"]), **kw)
        if mode == "TUBE":   # the tube is now part of the fin: drop its cross-flow drag term (motor cans stay)
            tube = [(2 * kw["cd"] * kw["tube_od"] * kw["tube_l"], kw["x_tube"])]
            a["Cnb"] -= FM.drag_items_dCnb(tube, x_aft, kw["S"], kw["b"])
            cr["Cnb"] -= FM.drag_items_dCnb(tube, x_a3, kw["S"], kw["b"])
        k = mode.lower()
        out[f"Cnb_{k}"], out[f"Cnb_avl_{k}"] = a["Cnb"], a["Cnb_avl"]
        out[f"Cnb_cruise_{k}"] = cr["Cnb"]
        out[f"Clb_{k}"], out[f"Cnr_{k}"] = a["Clb"], a["Cnr"]
        if mode == "BOARD":
            out.update({"Cnb_props": a["Cnb_props"], "Cnb_tubes": a["Cnb_tubes"], "Cnb_pod": a["Cnb_pod"]})
    return out


kit.claim("CL-B3-V-CNB", "Cn_beta at 1.3 Vs, aft limit, as-designed fins (board only)", calc="CALC-B3-V-LATDIR",
          output="Cnb_board", unit="1/rad", limit=(">=", P + "requirements.cnbeta_min"), verifies=["R-DIRECTIONAL"],
          assumes=["ASM-B3-PROP-CNA"], how="T-B3-YAW-DOUBLET at the aft mark, 1.3 Vs.")
kit.claim("CL-B3-V-CNB-TUBE", "Cn_beta at 1.3 Vs, aft limit, tube credited as fin LE", calc="CALC-B3-V-LATDIR",
          output="Cnb_tube", unit="1/rad", limit=(">=", P + "requirements.cnbeta_min"),
          how="As CL-B3-V-CNB; the bracket's upper end.")
kit.claim("CL-B3-V-CNB-CRUISE", "Cn_beta at cruise, A3 CG, as-designed fins (board only)", calc="CALC-B3-V-LATDIR",
          output="Cnb_cruise_board", unit="1/rad", limit=(">=", P + "requirements.cnbeta_min"),
          how="As CL-B3-V-CNB at 16 m/s.")


@kit.calc("CALC-B3-V-STALL", title="Trimmed stall and 1.3 Vs on the as-designed geometry at the A3 CG",
          inputs={**SC.CS_IN, "fin": "ASM-B3-V-FIN-CAD", "gap": "ASM-B3-V-ELEVON-GAP", "zcg": "ASM-B3-V-ZCG",
                  "cgf": "CL-A3-CG-X", "xnp_v": "CL-B3-V-XNP", "xnp_av": "CL-B3-V-XNP-AERO", "x_fwd_v": "CL-B3-V-CG-FWD",
                  "k": P + "requirements.transition_factor", "m_pred": "CL-A3-MASS-PREDICTED"},
          units={**SC.CS_U, "gap": "m", "zcg": "m", "xnp_v": "m", "xnp_av": "m", "x_fwd_v": "m", "m_pred": "kg"},
          assumes=["ASM-B3-CLMAX-FLAP"], cites=["SRC-B3-AVL"],
          equation="critical section (sc_analysis) with Xnp_aero shifted to the as-designed Xnp ; Vs at the gate "
                   "and predicted mass ; Vt = k Vs at the as-designed forward limit")
def stall_v(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, lo, li, va, slop,
            vmax, fin, gap, zcg, cgf, xnp_v, xnp_av, x_fwd_v, k, m_pred):
    x_a3 = cgf * c
    yi, yo = as_built(yin, yout, gap)
    geo = dict(zip(SC.GKEYS, (b, c, ef, yi, yo, fy, fh, fle, fte)))
    e_st = SC.eff_mech(vmax, lo, li, va)
    dx = xnp_av - xnp_v          # AVL has no props or pod: shift the reference so AVL sees the whole-aircraft SM
    out = {}
    with patched_geometry({"fin_sections": fin_sections(fin, "BOARD")}):
        for tag, x in (("a3", x_a3), ("fwd", x_fwd_v)):
            r = SC.critical_section(geo, x + dx, zcg, eta, dcm, tab, eff=e_st)
            out[f"clmax_{tag}"], out[f"delta_{tag}"] = r["CLmax"], r["delta"]
            out[f"vs_{tag}"] = FM.stall_speed(m, g, rho, S, r["CLmax"])
            out[f"vs_{tag}_pred"] = FM.stall_speed(m_pred, g, rho, S, r["CLmax"])
    out["vt_fwd"] = k * out["vs_fwd"]
    return out


kit.claim("CL-B3-V-VS-A3", "Trimmed stall speed at the gate, A3 CG, as designed", calc="CALC-B3-V-STALL",
          output="vs_a3", unit="m/s", limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="Slow-flight stall at the gate mass (H2).")
kit.claim("CL-B3-V-VT", "1.3 Vs at the as-designed forward limit, gate mass", calc="CALC-B3-V-STALL",
          output="vt_fwd", unit="m/s", limit=("<=", P + "performance.cruise_ms"), verifies=["R-TRANSITION"],
          how="F4 ARSPD_FBW_MIN >= this; first-transition log (H2).")


def main():
    now, loop = cad_check()
    res = kit.write()
    out = {}
    data = json.loads((HERE / "claims.verify.json").read_text())
    for nd in data["nodes"]:
        if nd.get("type") == "calculation":
            out[nd["id"]] = nd.get("outputs")
    out["cad_now"] = now
    out["cad_loop"] = [[round(x, 5), round(z, 5)] for x, z in loop]
    out["fin_sections_board"] = fin_sections(FIN_CAD, "BOARD")
    out["fin_sections_tube"] = fin_sections(FIN_CAD, "TUBE")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "verify.json").write_text(json.dumps(out, indent=1, default=str))
    return res


if __name__ == "__main__":
    main()
