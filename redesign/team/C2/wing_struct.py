"""C2 wing structures engine (K09-L): section properties, beam-integration deflection and twist of every C1 load
case, a NumPy 3-D Timoshenko frame FE (static cross-check, free-free modes, static aeroelasticity, flutter screen),
a ring-bending model of the spar wall under local bearing, local foam checks, a spar trade, and the sizing data D1
builds from.

Run from the repo root (about 10 s):
    python -I redesign/team/C2/wing_struct.py
    python -I redesign/team/C2/c2_claims.py
    python -I redesign/proofs/build_graph.py

Reads   params/params.json (A1-R2), subsystems/wing/s5010.dat, team/C1/data/{wing_spanwise.csv, mass_model.csv,
        envelope.json}, team/C1/claims.json, team/C4/claims.json, team/B4/claims.json.
Writes  team/C2/params.json (P:c2.* run results + material inputs the proof chain reads), out/results.json,
        data/*.csv, fig/*.svg, sizing.json (for D1).

Frame: params.json#frame (x aft, y right, z up, metres). The beam axis is the spar axis (x 0.080 m); loads from C1
are cut loads on the spar axis at z 0 (the 6.6 mm spar z offset is ignored: < 1 % on every moment).
"""
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import eig, eigh, solve
from scipy.special import hankel2

HERE = Path(__file__).resolve().parent
RD = HERE.parents[1]                       # redesign/
C1D = RD / "team" / "C1" / "data"

# ----------------------------------------------------------------------------------------------- inputs
PARAMS = json.loads((RD / "params" / "params.json").read_text(encoding="utf-8"))


def pv(key):
    d = PARAMS
    for k in key.split("."):
        d = d[k]
    return d["value"] if isinstance(d, dict) and "value" in d else d


def claim_value(folder, cid):
    for n in json.loads((RD / "team" / folder / "claims.json").read_text(encoding="utf-8"))["nodes"]:
        if n["id"] == cid:
            return n["value"]
    raise KeyError(cid)


# Material and modelling inputs. Each becomes P:c2.inputs.<key> in team/C2/params.json; the claims script reads
# them from there. Values are the engineering basis stated in WING-STRUCTURES.md section 2.
MAT = {
    "spar_E_nom_pa": (100e9, "Pa", "ASM-J1-E-TUBE", "UNVERIFIED",
                      "hobby 22 x 20 tube axial modulus, J1/C4 nominal; T-C4-TUBE-BEND measures it"),
    "spar_E_lo_pa": (70e9, "Pa", "ASM-C4-E-TUBE-LO", "UNVERIFIED",
                     "low corner (woven-heavy roll-wrapped); used for every deflection, twist and frequency claim"),
    "spar_G_nom_pa": (5e9, "Pa", "ASM-C4-G-TUBE", "UNVERIFIED", "C4 nominal"),
    "spar_G_lo_pa": (3e9, "Pa", "ASM-C4-G-TUBE-LO", "UNVERIFIED", "pure UD corner"),
    "spar_sigma_allow_pa": (350e6, "Pa", "ASM-C2-SPAR-SIGMA", "UNVERIFIED",
                            "bending (compression side) allowable for an unbranded roll-wrapped tube: ~0.6 x the "
                            "500-600 MPa catalogue compressive strength of standard-modulus roll-wrapped tubes"),
    "spar_tau_allow_pa": (30e6, "Pa", "ASM-C2-SPAR-TAU", "UNVERIFIED",
                          "in-plane shear allowable, matrix-dominated UD lower bound (G12 strength 50-70 MPa x 0.5)"),
    "spar_hoop_allow_pa": (40e6, "Pa", "ASM-C2-SPAR-HOOP", "UNVERIFIED",
                           "transverse (hoop) ring-bending allowable, UD matrix-dominated lower bound; a woven outer "
                           "ply raises it, a split tube lowers it"),
    "xps_E_pa": (10e6, "Pa", "ASM-C2-XPS-E", "UNVERIFIED", "XPS 25-35 kg/m3 modulus 8-15 MPa; T-C2-XPS-COUPON"),
    "xps_G_pa": (4e6, "Pa", "ASM-C2-XPS-G", "UNVERIFIED", "XPS shear modulus 3-6 MPa"),
    "xps_comp_allow_pa": (120e3, "Pa", "ASM-C2-XPS-COMP", "UNVERIFIED",
                          "0.7 x the 172 kPa (25 psi) F-250 rating at 10 % strain or yield (SRC-XPS-F250)"),
    "xps_tens_allow_pa": (150e3, "Pa", "ASM-C2-XPS-TENS", "UNVERIFIED",
                          "XPS tensile/flexural 250-500 kPa at this density, halved for hot-wire surface damage"),
    "xps_shear_allow_pa": (100e3, "Pa", "ASM-C2-XPS-SHEAR", "UNVERIFIED",
                           "XPS shear strength 150-250 kPa (EN 12090 grades near 200 kPa compression), knocked down"),
    "tape_E_pa": (2.0e9, "Pa", "ASM-C2-TAPE", "UNVERIFIED", "BOPP packing-tape film, machine direction"),
    "tape_G_pa": (0.7e9, "Pa", "ASM-C2-TAPE", "UNVERIFIED", "BOPP, E / 2.8"),
    "tape_t_m": (44e-6, "m", "ASM-C2-TAPE", "UNVERIFIED", "40 um film x 1.1 for the 10 % overlap; adhesive not counted"),
    "tape_sigma_allow_pa": (60e6, "Pa", "ASM-C2-TAPE", "UNVERIFIED", "BOPP MD tensile 100-150 MPa, knocked down"),
    "tape_eff": (0.5, "-", "ASM-C2-TAPE-EFF", "UNVERIFIED",
                 "stiffness effectiveness of a tape skin on foam (adhesive creep, wrinkles, overlaps): 50 %"),
    "rear_web_t_m": (0.010, "m", "ASM-C2-REAR-WEB", "UNVERIFIED",
                     "the torsion cell is closed at the hinge line by foam only; an effective 10 mm foam web"),
    "petg_bearing_allow_pa": (20e6, "Pa", "ASM-C4-PETG-BEARING", "UNVERIFIED", "C4's printed PETG bearing allowable"),
    "slot_fill_kgm": (0.015, "kg/m", "team/A3/mass_model.csv", "PROPOSED", "epoxy + microballoon slot fill, A3 15 g"),
    "plug_mass_kg": (0.007, "kg", "C2 estimate", "PROPOSED", "20 mm x 36 mm printed PETG plug, 50 % fill"),
    "anchor_plug_mass_kg": (0.004, "kg", "C2 estimate", "PROPOSED", "20 mm x 20 mm printed PETG plug, 30 % fill"),
    "contact_half_angle_deg": (30.0, "deg", "ASM-C2-CONTACT", "UNVERIFIED",
                               "half-angle of the bore-to-tube contact arc with a 0.15 mm radial bond gap"),
    "cla_2d_per_rad": (5.97, "1/rad", "C2 strip basis", "PROPOSED", "0.95 x 2 pi; strip theory, no downwash (conservative)"),
    "x_sc_aft_m": (0.100, "m", "ASM-C2-XSC", "UNVERIFIED",
                   "pessimistic shear-centre position for divergence (computed 0.08x m; 20 mm aft margin)"),
    "flutter_vmax_factor": (3.0, "-", "C2 choice", "PROPOSED", "flutter sweep to 3 x VD"),
}
M = {k: v[0] for k, v in MAT.items()}

g = pv("env.g_ms2")
rho = pv("env.rho_kgm3")
c = pv("wing.chord_m")
b = pv("wing.span_m")
L_half = b / 2
xs = pv("wing.spar.x_m")
zs = pv("wing.spar.z_m")
D_sp = pv("wing.spar.od_m")
d_sp = pv("wing.spar.id_m")
y_spar_end = pv("wing.spar.length_m") / 2
spar_mpm = pv("wing.spar.mass_per_m_kgm")
rho_core = pv("wing.core.density_kgm3")
tape_areal = pv("wing.skin.areal_mass_kgm2")
x_hinge = c * (1 - pv("wing.elevon.chord_frac"))
y_fin = pv("fins.y_m")
ib = pv("wing.elevon.inboard_y_m")
ob = pv("wing.elevon.outboard_y_m")
VD = claim_value("C1", "CL-C1-VD")
QVD = claim_value("C1", "CL-C1-Q-VD")
SF = pv("requirements.safety_factor_ult")
F_HOVER = claim_value("B4", "CL-B4-HOVER-RPM") / 60.0
F_CRUISE = claim_value("B4", "CL-B4-CRUISE-RPM") / 60.0
FORCING = {"hover 1P": F_HOVER, "hover 2P": 2 * F_HOVER, "cruise 1P": F_CRUISE, "cruise 2P": 2 * F_CRUISE}
SEP_MIN = pv("requirements.vibration_sep_frac")
ETA_EL = claim_value("B2", "CL-B2-ELEVON-ETA")
Y_ANCHOR = 0.242          # D3 brace anchor (subsystems/fins SPEC, CL-D3-BRACE-L); C4 modelled 0.20
Y_CRADLE = 0.20           # ASM-C1-CRADLE-Y


# ----------------------------------------------------------------------------------------------- airfoil
def airfoil():
    pts = []
    for line in (RD / "subsystems" / "wing" / "s5010.dat").read_text().splitlines()[1:]:
        p = line.split()
        if len(p) == 2:
            pts.append((float(p[0]), float(p[1])))
    pts = np.array(pts)
    i_le = int(np.argmin(pts[:, 0]))
    up = pts[:i_le + 1][::-1]          # LE -> TE
    lo = pts[i_le:]
    xg = 0.5 * (1 - np.cos(np.linspace(0, math.pi, 801)))
    zu = np.interp(xg, up[:, 0], up[:, 1])
    zl = np.interp(xg, lo[:, 0], lo[:, 1])
    return xg * c, zu * c, zl * c


XA, ZU, ZL = airfoil()


def thickness_at(x):
    return float(np.interp(x, XA, ZU) - np.interp(x, XA, ZL))


# ----------------------------------------------------------------------------------------------- section
def section(D=D_sp, d=d_sp, with_spar=True, E_s=None, G_s=None, tape_eff=None, foam_only=False):
    """Composite section of the structural box (LE to the hinge line) plus mass of the full chord.
    Returns stiffnesses about the modulus-weighted axes and mass properties per metre."""
    E_s = M["spar_E_nom_pa"] if E_s is None else E_s
    G_s = M["spar_G_nom_pa"] if G_s is None else G_s
    eff = M["tape_eff"] if tape_eff is None else tape_eff
    Ef, Gf, Et, Gt, tt = M["xps_E_pa"], M["xps_G_pa"], M["tape_E_pa"] * eff, M["tape_G_pa"] * eff, M["tape_t_m"]
    if foam_only:
        Et = Gt = 0.0
    xg = np.linspace(0.0, x_hinge, 3001)
    dx = xg[1] - xg[0]
    zu = np.interp(xg, XA, ZU)
    zl = np.interp(xg, XA, ZL)
    t = zu - zl
    zm = 0.5 * (zu + zl)
    # foam strips (minus the spar circle)
    Af = t * dx
    hole = np.zeros_like(xg)
    if with_spar:
        r = D / 2
        inside = np.abs(xg - xs) < r
        hole[inside] = 2 * np.sqrt(r ** 2 - (xg[inside] - xs) ** 2) * dx
    Af_net = Af - hole
    A_f = Af_net.sum()
    # tape: upper and lower arcs LE..hinge
    def arc(zc):
        ds = np.sqrt(np.diff(xg) ** 2 + np.diff(zc) ** 2)
        xm = 0.5 * (xg[1:] + xg[:-1])
        zmid = 0.5 * (zc[1:] + zc[:-1])
        return ds, xm, zmid
    dsu, xu, zuu = arc(zu)
    dsl, xl, zll = arc(zl)
    tape_s = np.concatenate([dsu, dsl])
    tape_x = np.concatenate([xu, xl])
    tape_z = np.concatenate([zuu, zll])
    At = tape_s * tt
    # spar
    A_s = math.pi / 4 * (D ** 2 - d ** 2) if with_spar else 0.0
    I_s = math.pi / 64 * (D ** 4 - d ** 4) if with_spar else 0.0
    J_s = math.pi / 32 * (D ** 4 - d ** 4) if with_spar else 0.0
    # modulus-weighted centroid (foam strips: centroid zm, minus hole at zs)
    EA = Ef * A_f + Et * At.sum() + E_s * A_s
    xn = (Ef * (Af * xg).sum() - Ef * (hole * xg).sum() + Et * (At * tape_x).sum() + E_s * A_s * xs) / EA
    zn = (Ef * (Af * zm).sum() - Ef * (hole * zs).sum() + Et * (At * tape_z).sum() + E_s * A_s * zs) / EA
    # flap (about x axis through zn): sum E (I_own + A dz^2)
    EI_fl = (Ef * ((t ** 3 / 12) * dx + Af * (zm - zn) ** 2).sum()
             - Ef * (hole * (zs - zn) ** 2).sum() - (Ef * math.pi * (D / 2) ** 4 / 4 if with_spar else 0.0)
             + Et * (At * (tape_z - zn) ** 2).sum() + E_s * (I_s + A_s * (zs - zn) ** 2))
    EI_ip = (Ef * (Af_net * (xg - xn) ** 2).sum() + Et * (At * (tape_x - xn) ** 2).sum()
             + E_s * (I_s + A_s * (xs - xn) ** 2))
    # torsion: foam St Venant (thin-strip), tape cell closed by a foam rear web (Bredt), spar tube
    J_f = (t ** 3 / 3 * dx).sum() * 0.85        # 0.85: thick-strip end correction (Roark, t/c ~ 0.1)
    A_enc = (t * dx).sum()
    if foam_only or Gt == 0:
        GJ_cell = 0.0
    else:
        h_rear = thickness_at(x_hinge)
        flex = tape_s.sum() / (Gt * tt) + h_rear / (Gf * M["rear_web_t_m"])
        GJ_cell = 4 * A_enc ** 2 / flex
    GJ_f = Gf * J_f
    GJ_s = G_s * J_s
    GJ = GJ_f + GJ_cell + GJ_s
    k = 5 / 6
    GA_z = k * Gf * A_f + G_s * A_s / 2
    GA_x = k * Gf * A_f + Gt * tt * (dsu.sum() + dsl.sum()) + G_s * A_s / 2
    # flap shear-centre estimate: EI-weighted x of the bending members
    xsc = (E_s * I_s * xs + (EI_fl - E_s * I_s) * xn) / EI_fl if with_spar else xn
    # mass per metre, full chord (core incl. elevon foam, tape over both full surfaces, spar, slot fill)
    xg2 = np.linspace(0, c, 4001)
    dx2 = xg2[1] - xg2[0]
    t2 = np.interp(xg2, XA, ZU) - np.interp(xg2, XA, ZL)
    zm2 = 0.5 * (np.interp(xg2, XA, ZU) + np.interp(xg2, XA, ZL))
    a_core = (t2 * dx2).sum() - (math.pi * (D / 2) ** 2 if with_spar else 0.0)
    m_core = rho_core * a_core
    perim = (np.sqrt(np.diff(xg2) ** 2 + np.diff(np.interp(xg2, XA, ZU)) ** 2).sum()
             + np.sqrt(np.diff(xg2) ** 2 + np.diff(np.interp(xg2, XA, ZL)) ** 2).sum())
    m_tape = tape_areal * perim
    m_spar = (spar_mpm * (D ** 2 - d ** 2) / (D_sp ** 2 - d_sp ** 2) + M["slot_fill_kgm"]) if with_spar else 0.0
    x_core = (rho_core * ((t2 * dx2) * xg2).sum() - (rho_core * math.pi * (D / 2) ** 2 * xs if with_spar else 0)) / m_core
    m_tot = m_core + m_tape + m_spar
    x_cg = (m_core * x_core + m_tape * c * 0.5 + m_spar * xs) / m_tot
    # rotary inertia about the section CG (about y): core strips + tape + spar
    Iy = (rho_core * ((t2 * dx2) * ((xg2 - x_cg) ** 2 + (zm2 - 0) ** 2 + t2 ** 2 / 12)).sum()
          + m_tape * (c ** 2 / 12) + m_spar * (xs - x_cg) ** 2)
    return {"EA": EA, "EI_flap": EI_fl, "EI_inplane": EI_ip, "GJ": GJ, "GJ_foam": GJ_f, "GJ_cell": GJ_cell,
            "GJ_spar": GJ_s, "GA_z": GA_z, "GA_x": GA_x, "xn": xn, "zn": zn, "x_sc": xsc,
            "EI_flap_spar": E_s * I_s, "EI_inplane_spar": E_s * I_s, "A_foam": A_f, "A_enc": A_enc,
            "tape_len": float(dsu.sum() + dsl.sum()), "I_spar": I_s, "J_spar": J_s, "A_spar": A_s,
            "m_per_m": m_tot, "m_core": m_core, "m_tape": m_tape, "m_spar": m_spar, "x_cg": x_cg, "Iy_per_m": Iy,
            "perim": perim, "t_spar": thickness_at(xs)}


# ----------------------------------------------------------------------------------------------- C1 loads
def read_spanwise():
    cases = {}
    with open(C1D / "wing_spanwise.csv", newline="") as f:
        for r in csv.DictReader(f):
            key = (r["case"], r["mass_config"])
            cases.setdefault(key, {"family": r["family"], "rows": []})["rows"].append(
                [float(r[k]) for k in ("y_m", "Fx_N", "Fy_N", "Fz_N", "Mx_Nm", "My_Nm", "Mz_Nm")]
                + [-1.0 if r["y_m"].strip().startswith("-") else 1.0])
    for v in cases.values():
        v["rows"] = np.array(sorted(v["rows"], key=lambda r: r[0]))
    return cases


def side(rows, s):
    """rows of one side, as functions of the outward distance |y| (s=+1 right, -1 left)."""
    sel = rows[rows[:, 7] == s]
    sel = sel[np.argsort(np.abs(sel[:, 0]), kind="stable")]
    _, first = np.unique(np.round(np.abs(sel[:, 0]), 9), return_index=True)
    return sel[np.sort(first)]


def integrate_case(rows, s, sec_fn, step=1):
    """Beam theory on C1's internal loads: curvature = M/EI (+ shear strain V/GA), twist rate = T/GJ.
    Returns |y|, w (flap, up +), u (in-plane, aft +), theta (twist, nose-up +, rad) relative to the centreline."""
    r = side(rows, s)[::step]
    sy = np.abs(r[:, 0])
    Fx, Fz, Mx, My, Mz = r[:, 1], r[:, 3], r[:, 4], r[:, 5], r[:, 6]
    props = [sec_fn(v) for v in sy]
    EIf = np.array([p["EI_flap"] for p in props])
    EIi = np.array([p["EI_inplane"] for p in props])
    GJ = np.array([p["GJ"] for p in props])
    GAz = np.array([p["GA_z"] for p in props])
    GAx = np.array([p["GA_x"] for p in props])
    kap_w = (Mx if s > 0 else -Mx) / EIf
    kap_u = (-Mz if s > 0 else Mz) / EIi
    rate = My / GJ

    def cumtrapz(f):
        out = np.zeros_like(f)
        out[1:] = np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(sy))
        return out
    w = cumtrapz(cumtrapz(kap_w)) + cumtrapz(Fz / GAz)
    u = cumtrapz(cumtrapz(kap_u)) + cumtrapz(Fx / GAx)
    th = cumtrapz(rate)
    return sy, w, u, th


# ----------------------------------------------------------------------------------------------- FE model
def mesh(n_half, extra=()):
    h = L_half / n_half
    must = sorted({0.0, Y_CRADLE, Y_ANCHOR, 0.30, y_fin, y_spar_end, L_half, *extra})
    grid = list(np.linspace(0, L_half, n_half + 1))
    keep = [v for v in grid if all(abs(v - m) > h / 3 for m in must)]
    pos = sorted(set([round(v, 9) for v in keep + must]))
    return np.array(pos)


def timo(EI, GAs, L):
    phi = 12 * EI / (GAs * L ** 2)
    k = EI / ((1 + phi) * L ** 3)
    return k * np.array([[12, 6 * L, -12, 6 * L],
                         [6 * L, (4 + phi) * L ** 2, -6 * L, (2 - phi) * L ** 2],
                         [-12, -6 * L, 12, -6 * L],
                         [6 * L, (2 - phi) * L ** 2, -6 * L, (4 + phi) * L ** 2]])


def assemble_K(ys, sec_fn):
    n = len(ys)
    K = np.zeros((6 * n, 6 * n))
    for e in range(n - 1):
        L = ys[e + 1] - ys[e]
        p = sec_fn(abs(0.5 * (ys[e] + ys[e + 1])))
        i, j = 6 * e, 6 * (e + 1)
        # axial uy (1), torsion ry (4)
        for dof, kk in ((1, p["EA"] / L), (4, p["GJ"] / L)):
            K[i + dof, i + dof] += kk
            K[j + dof, j + dof] += kk
            K[i + dof, j + dof] -= kk
            K[j + dof, i + dof] -= kk
        # flap: v = uz (2), theta = rx (3) with duz/dy = rx
        kf = timo(p["EI_flap"], p["GA_z"], L)
        idx = [i + 2, i + 3, j + 2, j + 3]
        K[np.ix_(idx, idx)] += kf
        # in-plane: v = ux (0), theta = -rz (5)
        ki = timo(p["EI_inplane"], p["GA_x"], L)
        T = np.diag([1, -1, 1, -1])
        idx = [i + 0, i + 5, j + 0, j + 5]
        K[np.ix_(idx, idx)] += T @ ki @ T
    return K


def skew(r):
    return np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])


def rigid_mass(m, r, J=None):
    """6x6 mass of a rigid item with mass m at offset r from the node, own inertia J (3x3) about its CG."""
    T = np.hstack([np.eye(3), -skew(r)])
    Mm = m * T.T @ T
    if J is not None:
        Mm[3:, 3:] += J
    return Mm


def read_mass_items(config="MC-P"):
    items = []
    with open(C1D / "mass_model.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["mass_config"] != config or r["group"] in ("TOTAL",):
                continue
            items.append({"group": r["group"], "station": r["station"], "m": float(r["mass_kg"]),
                          "x": float(r["x_m"]), "y": float(r["y_m"]), "z": float(r["z_m"])})
    return items


def item_inertia(it):
    m, gp = it["m"], it["group"]
    if gp == "tube":
        Lt = pv("fins.tube.length_m")
        return np.diag([m * Lt ** 2 / 12, m * Lt ** 2 / 12, 0.0])
    if gp == "board":
        h, cc = 2 * pv("fins.half_height_m"), pv("fins.chord_m")
        return np.diag([m * h ** 2 / 12, m * (h ** 2 + cc ** 2) / 12, m * cc ** 2 / 12])
    if gp == "pack":
        lx, ly, lz = 0.16, 0.052, 0.053
    elif gp == "centre":
        lx, ly, lz = 0.20, 0.10, 0.07
    else:
        return None
    return np.diag([m * (ly ** 2 + lz ** 2) / 12, m * (lx ** 2 + lz ** 2) / 12, m * (lx ** 2 + ly ** 2) / 12])


STATION_GROUPS = {"mount", "rotor"}      # C4 convention: motor + prop + mount body


def assemble_M(ys, sec_fn, config="MC-P", full=True, wing_scale=None):
    """Lumped rigid-item mass matrix. The distributed wing (section mass, strip by strip) is scaled so that each
    half equals C1's wing group mass for the configuration (loads and modes on one mass basis)."""
    n = len(ys)
    Mg = np.zeros((6 * n, 6 * n))
    items = read_mass_items(config)
    wing_half = sum(it["m"] for it in items if it["group"] == "wing") / 2
    # distributed wing strips, 2 mm
    edges = np.linspace(0, L_half, 288)
    strips = []
    for a, bb in zip(edges[:-1], edges[1:]):
        ym = 0.5 * (a + bb)
        p = sec_fn(ym)
        strips.append((ym, p["m_per_m"] * (bb - a), p["x_cg"], p["Iy_per_m"] * (bb - a), bb - a))
    m_raw = sum(s[1] for s in strips)
    scale = wing_half / m_raw if wing_scale is None else wing_scale
    sides = (1, -1) if full else (1,)
    station_idx = []
    for s in sides:
        for ym, ms, xc, Iy, dy in strips:
            y = s * ym
            node = int(np.argmin(np.abs(ys - y)))
            r = np.array([xc - xs, y - ys[node], 0.0])
            J = np.diag([ms * scale * dy ** 2 / 12, Iy * scale, ms * scale * dy ** 2 / 12])
            Mg[6 * node:6 * node + 6, 6 * node:6 * node + 6] += rigid_mass(ms * scale, r, J)
    for it in items:
        if it["group"] == "wing":
            continue
        if not full and it["y"] < -1e-6:
            continue
        if not full and abs(it["y"]) < 1e-6:
            continue                       # centre items sit on the clamped root
        node = int(np.argmin(np.abs(ys - it["y"])))
        r = np.array([it["x"] - xs, it["y"] - ys[node], it["z"] - 0.0])
        Mg[6 * node:6 * node + 6, 6 * node:6 * node + 6] += rigid_mass(it["m"], r, item_inertia(it))
        if it["group"] in STATION_GROUPS:
            station_idx.append((node, it))
    return Mg, station_idx, scale


def station_ke_fraction(phi, Mg, ys, station_idx):
    tot = phi @ Mg @ phi
    ke = 0.0
    for node, it in station_idx:
        Mi = rigid_mass(it["m"], np.array([it["x"] - xs, it["y"] - ys[node], it["z"]]), item_inertia(it))
        v = phi[6 * node:6 * node + 6]
        ke += v @ Mi @ v
    return ke / tot


def classify(phi, K, ys):
    n = len(ys)
    parts = {"flap": [2, 3], "in-plane": [0, 5], "torsion": [4], "axial": [1]}
    e = {}
    for k_, dofs in parts.items():
        mask = np.zeros(6 * n, bool)
        for i in range(n):
            for d_ in dofs:
                mask[6 * i + d_] = True
        ph = np.where(mask, phi, 0)
        e[k_] = float(ph @ K @ ph)
    tot = sum(max(v, 0) for v in e.values())
    frac = {k_: max(v, 0) / tot for k_, v in e.items()}
    # symmetry from the dominant translation at +/- the fin station
    i_r = int(np.argmin(np.abs(ys - y_fin)))
    i_l = int(np.argmin(np.abs(ys + y_fin)))
    dom = max(frac, key=frac.get)
    d_ = {"flap": 2, "in-plane": 0, "torsion": 4, "axial": 1}[dom]
    a, bb = phi[6 * i_r + d_], phi[6 * i_l + d_]
    sym = "sym" if a * bb > 0 else "antisym"
    if dom == "axial":
        sym = "antisym" if a * bb > 0 else "sym"
    return dom, sym, frac


def modal(n_half, sec_fn, config="MC-P", nmodes=30):
    ys_r = mesh(n_half)
    ys = np.concatenate([-ys_r[:0:-1], ys_r])
    K = assemble_K(ys, sec_fn)
    Mg, st, _ = assemble_M(ys, sec_fn, config)
    w2, V = eigh(K, Mg)
    f = np.sqrt(np.clip(w2, 0, None)) / (2 * math.pi)
    out = []
    for i in range(len(f)):
        if f[i] < 2.0:
            continue
        phi = V[:, i]
        dom, sym, frac = classify(phi, K, ys)
        out.append({"f_hz": float(f[i]), "type": dom, "sym": sym, "energy": frac,
                    "station_ke": float(station_ke_fraction(phi, Mg, ys, st))})
        if len(out) >= nmodes:
            break
    n_rigid = int((f < 2.0).sum())
    return out, n_rigid


def separation(f):
    return min(abs(f / fp - 1) for fp in FORCING.values())


# ---- static FE on the right half, clamped at the centreline, loaded by C1's strip loads
def nodal_loads_from_cuts(rows, ys):
    r = side(rows, 1)
    n = len(ys)
    Fv = np.zeros(6 * n)
    P = np.array([[xs, v, 0.0] for v in r[:, 0]])
    Fc, Mc = r[:, 1:4], r[:, 4:7]
    for i in range(len(r)):
        if i + 1 < len(r):
            F_ext = Fc[i] - Fc[i + 1]
            M_ext = Mc[i] - (Mc[i + 1] + np.cross(P[i + 1] - P[i], Fc[i + 1]))
            y_app = 0.5 * (r[i, 0] + r[i + 1, 0])
        else:
            F_ext, M_ext, y_app = Fc[i], Mc[i], r[i, 0]
        node = int(np.argmin(np.abs(ys - y_app)))
        arm = P[i] - np.array([xs, ys[node], 0.0])
        Fv[6 * node:6 * node + 3] += F_ext
        Fv[6 * node + 3:6 * node + 6] += M_ext + np.cross(arm, F_ext)
    return Fv


def static_fe(rows, n_half, sec_fn):
    ys = mesh(n_half)
    K = assemble_K(ys, sec_fn)
    F = nodal_loads_from_cuts(rows, ys)
    free = np.arange(6, 6 * len(ys))
    u = np.zeros(6 * len(ys))
    u[free] = solve(K[np.ix_(free, free)], F[free], assume_a="sym")
    return ys, u


# ---- static aeroelasticity on the clamped half wing (torsion + flap, strip theory)
def aero_matrices(ys, x_sc):
    """A: aerodynamic stiffness per unit q (forces from twist); B: forces per unit q per rad of elevon.
    Lift acts at c/4 (x 0.080); moment about the beam axis at x_sc."""
    n = len(ys)
    A = np.zeros((6 * n, 6 * n))
    Bv = np.zeros(6 * n)
    cla = M["cla_2d_per_rad"]
    E = pv("wing.elevon.chord_frac")
    thf = math.acos(2 * E - 1)
    cld = 2 * (math.pi - thf + math.sin(thf)) * ETA_EL
    cmd = -0.5 * math.sin(thf) * (1 - math.cos(thf)) * ETA_EL
    edges = 0.5 * (ys[1:] + ys[:-1])
    widths = np.diff(np.concatenate([[ys[0]], edges, [ys[-1]]]))
    e_arm = x_sc - 0.25 * c                  # lift ahead of the axis by e_arm -> nose-up moment = L * e_arm
    for i, y in enumerate(ys):
        w = widths[i]
        on = (ib[0] <= y <= ib[1]) or (ob[0] <= y <= ob[1])
        # twist ry (nose-up) -> lift Fz and moment My about the axis
        A[6 * i + 2, 6 * i + 4] += cla * c * w
        A[6 * i + 4, 6 * i + 4] += cla * c * w * e_arm
        if on:
            Bv[6 * i + 2] += cld * c * w
            Bv[6 * i + 4] += cld * c * w * e_arm + cmd * c * c * w
    return A, Bv, widths


def aeroelastic(n_half, sec_fn, x_sc):
    ys = mesh(n_half)
    K = assemble_K(ys, sec_fn)
    A, Bv, widths = aero_matrices(ys, x_sc)
    free = np.arange(6, 6 * len(ys))
    Kf, Af, Bf = K[np.ix_(free, free)], A[np.ix_(free, free)], Bv[free]
    # divergence: K x = q A x
    lam = eig(Af, Kf, right=False)
    lam = lam[np.isfinite(lam)]
    lam_r = [1 / l.real for l in lam if l.real > 1e-12 and abs(l.imag) < 1e-6 * abs(l.real) + 1e-12]
    q_div = min(lam_r) if lam_r else float("inf")
    # roll moment per rad of antisymmetric elevon, held root
    def roll(q):
        x = solve(Kf - q * Af, q * Bf)
        u = np.zeros(6 * len(ys))
        u[free] = x
        lift = q * (A @ u)[2::6] + q * Bv[2::6]
        return float((lift * ys).sum())
    r0 = roll(1.0)
    qs = np.linspace(1, 60000, 600)
    vals = [roll(q) / (q * r0) for q in qs]
    q_rev = float("inf")
    for a, bb, va, vb in zip(qs[:-1], qs[1:], vals[:-1], vals[1:]):
        if va > 0 >= vb:
            q_rev = a + (bb - a) * va / (va - vb)
            break
    eff_vd = roll(QVD) / (QVD * r0)
    return {"q_div": q_div, "q_rev": q_rev, "eff_vd": eff_vd}


# ---- flutter screen (modal p-k, strip Theodorsen, clamped half wing)
def theodorsen(k):
    if k < 1e-6:
        return 1.0 + 0j
    H1, H0 = hankel2(1, k), hankel2(0, k)
    return H1 / (H1 + 1j * H0)


def flutter(n_half, sec_fn, nm=6, config="MC-P"):
    ys = mesh(n_half)
    K = assemble_K(ys, sec_fn)
    Mg, _, _ = assemble_M(ys, sec_fn, config, full=False)
    free = np.arange(6, 6 * len(ys))
    Kf, Mf = K[np.ix_(free, free)], Mg[np.ix_(free, free)]
    w2, V = eigh(Kf, Mf)
    Phi = V[:, :nm]
    wn = np.sqrt(w2[:nm])
    Kg = Phi.T @ Kf @ Phi
    Mgm = Phi.T @ Mf @ Phi
    n = len(ys)
    full = np.zeros((6 * n, nm))
    full[free] = Phi
    Pz, Pr = full[2::6], full[4::6]
    edges = 0.5 * (ys[1:] + ys[:-1])
    widths = np.diff(np.concatenate([[ys[0]], edges, [ys[-1]]]))
    bs = c / 2
    a = (xs - c / 2) / bs

    def Q(omega, V_):
        k = omega * bs / V_
        C = theodorsen(k)
        iw = 1j * omega
        # per unit span: L (up) and M (nose-up) from h (down) and alpha
        Lh = math.pi * rho * bs ** 2 * (-omega ** 2) + 2 * math.pi * rho * V_ * bs * C * iw
        La = (math.pi * rho * bs ** 2 * (V_ * iw + bs * a * omega ** 2)
              + 2 * math.pi * rho * V_ * bs * C * (V_ + bs * (0.5 - a) * iw))
        Mh = (math.pi * rho * bs ** 2 * (bs * a * (-omega ** 2))
              + 2 * math.pi * rho * V_ * bs ** 2 * (a + 0.5) * C * iw)
        Ma = (math.pi * rho * bs ** 2 * (-V_ * bs * (0.5 - a) * iw + bs ** 2 * (1 / 8 + a ** 2) * omega ** 2)
              + 2 * math.pi * rho * V_ * bs ** 2 * (a + 0.5) * C * (V_ + bs * (0.5 - a) * iw))
        # h = -uz, alpha = ry; Fz = L, My = M
        Hz = -Pz
        Qm = np.zeros((nm, nm), complex)
        for i in range(n):
            w = widths[i]
            hz, ar = Hz[i], Pr[i]
            Lrow = Lh * hz + La * ar
            Mrow = Mh * hz + Ma * ar
            Qm += w * (np.outer(Pz[i], Lrow) + np.outer(Pr[i], Mrow))
        return Qm

    Vmax = M["flutter_vmax_factor"] * VD
    Vs = np.linspace(2.0, Vmax, 120)
    tracks = []
    for j in range(nm):
        om = wn[j]
        track = []
        for V_ in Vs:
            for _ in range(60):
                A_ = np.linalg.solve(Mgm, Kg - Q(om, V_))
                ev = np.linalg.eigvals(-A_.astype(complex))
                p = np.sqrt(ev)
                p = np.where(p.imag < 0, -p, p)
                jj = int(np.argmin(np.abs(p.imag - om)))
                new = abs(p[jj].imag)
                if abs(new - om) < 1e-6 * max(om, 1):
                    om = new
                    break
                om = 0.5 * (om + new)
            track.append((V_, float(p[jj].real), float(om)))
        tracks.append(track)
    vf = float("inf")
    for tr in tracks:
        for (v1, s1, _), (v2, s2, o2) in zip(tr[:-1], tr[1:]):
            if s1 <= 0 and s2 > 1e-4 * o2:
                vf = min(vf, v1 + (v2 - v1) * (-s1) / (s2 - s1))
                break
    gmin = min(-2 * s / max(o, 1e-9) for tr in tracks for (_, s, o) in tr)
    return {"V_flutter": vf, "V_max_swept": float(Vmax), "f_modes_hz": [float(x / 2 / math.pi) for x in wn],
            "min_damping_g": float(gmin)}


# ----------------------------------------------------------------------------------------------- ring model
def ring_moment(P_line, beta_deg, R, n=4001):
    """Thin ring (mean radius R) loaded by a cosine bearing pressure over |phi| <= beta with resultant P_line
    (N per metre of tube) and reacted by the beam shear flow q = P sin(phi)/(pi R). Returns max |M| (N m / m)
    and the hoop force at that point. Redundants M0, N0 at the top cut from Castigliano (bending energy)."""
    beta = math.radians(beta_deg)
    ph = np.linspace(0, math.pi, n)
    dph = ph[1] - ph[0]
    # half-ring loads on [0, pi]: pressure (inward) on [0, beta], shear on [0, pi]
    p0 = P_line / (2 * R * (beta / 2 + math.sin(2 * beta) / 4))     # int_{-b}^{b} p0 cos^2 R dphi = P
    pres = np.where(ph <= beta, p0 * np.cos(ph), 0.0)
    q = P_line * np.sin(ph) / (math.pi * R)
    pos = np.stack([R * np.sin(ph), R * np.cos(ph)], 1)              # (y, z)
    rhat = pos / R
    that = np.stack([np.cos(ph), -np.sin(ph)], 1)
    F = (-pres[:, None] * rhat - q[:, None] * that) * R * dph        # force on each element (y, z)
    Mst = np.zeros(n)
    Nst = np.zeros(n)
    for k in range(1, n):
        d = pos[:k] - pos[k]
        Mst[k] = (d[:, 0] * F[:k, 1] - d[:, 1] * F[:k, 0]).sum()
        Nst[k] = F[:k].sum(0) @ that[k]                                   # tangential force passed (approx hoop)
    g1 = np.ones(n)
    g2 = -R * (1 - np.cos(ph))
    A_ = np.array([[(g1 * g1).sum(), (g1 * g2).sum()], [(g2 * g1).sum(), (g2 * g2).sum()]])
    rhs = -np.array([(Mst * g1).sum(), (Mst * g2).sum()])
    M0, N0 = np.linalg.solve(A_, rhs)
    Mtot = Mst + M0 * g1 + N0 * g2
    i = int(np.argmax(np.abs(Mtot)))
    return float(abs(Mtot[i])), float(Nst[i] + N0 * np.cos(ph[i])), float(math.degrees(ph[i]))


def ring_check(P_line, beta_deg, D=D_sp, d=d_sp):
    R = (D + d) / 4
    t = (D - d) / 2
    Mr, Nr, at = ring_moment(P_line, beta_deg, R)
    return {"M_Nm_per_m": Mr, "sigma_pa": 6 * Mr / t ** 2 + abs(Nr) / t, "at_deg": at}


def ring_validation():
    """Two opposed point loads on a ring: M_max = P R / pi (Roark table 9.2 case 1). Model: loads at the top and
    the bottom, emulated by a narrow contact (beta 1 deg) top and a narrow bottom reaction instead of the shear."""
    R, P = 0.0105, 1000.0
    beta = math.radians(1.0)
    n = 20001
    ph = np.linspace(0, math.pi, n)
    dph = ph[1] - ph[0]
    p0 = P / (2 * R * (beta / 2 + math.sin(2 * beta) / 4))
    pres = np.where(ph <= beta, p0 * np.cos(ph), 0.0) + np.where(ph >= math.pi - beta, p0 * np.cos(math.pi - ph), 0.0)
    pos = np.stack([R * np.sin(ph), R * np.cos(ph)], 1)
    F = -pres[:, None] * (pos / R) * R * dph
    cum = np.cumsum(F[::-1], 0)
    Mst = np.zeros(n)
    for k in range(1, n, 50):
        d = pos[:k] - pos[k]
        Mst[k] = (d[:, 0] * F[:k, 1] - d[:, 1] * F[:k, 0]).sum()
    ks = np.arange(1, n, 50)
    phk = ph[ks]
    Mk = Mst[ks]
    g1 = np.ones_like(phk)
    g2 = -R * (1 - np.cos(phk))
    A_ = np.array([[(g1 * g1).sum(), (g1 * g2).sum()], [(g2 * g1).sum(), (g2 * g2).sum()]])
    M0, N0 = np.linalg.solve(A_, -np.array([(Mk * g1).sum(), (Mk * g2).sum()]))
    Mt = Mk + M0 * g1 + N0 * g2
    del cum
    return float(np.abs(Mt).max()), P * R / math.pi


# ----------------------------------------------------------------------------------------------- main run
def sec_factory(E_s=None, G_s=None, D=D_sp, d=d_sp, tape_eff=None):
    with_ = section(D=D, d=d, with_spar=True, E_s=E_s, G_s=G_s, tape_eff=tape_eff)
    without = section(D=D, d=d, with_spar=False, E_s=E_s, G_s=G_s, tape_eff=tape_eff)
    return lambda y: with_ if abs(y) < y_spar_end else without


def svg_envelope(path, sy, wenv, thenv, uenv):
    W, H, x0, x1, y0, y1 = 1200, 420, 90, 1100, 30, 360
    def X(v):
        return x0 + (x1 - x0) * v / L_half
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    panels = [("flap w, mm", wenv * 1000, "#1F5FC7"), ("in-plane u, mm", uenv * 1000, "#4B5563"),
              ("twist, deg", np.degrees(thenv), "#C2540A")]
    ph = (y1 - y0) / 3
    for k, (lab, v, col) in enumerate(panels):
        top = y0 + k * ph + 8
        bot = y0 + (k + 1) * ph - 14
        vmax = max(float(np.max(v)), 1e-9) * 1.15
        out.append(f'<line x1="{x0}" y1="{bot:.1f}" x2="{x1}" y2="{bot:.1f}" stroke="#9AA4B1" stroke-width="1"/>')
        out.append(f'<text x="{x0 - 8}" y="{top + 10:.1f}" text-anchor="end" fill="#6B7280" '
                   f'font-family="IBM Plex Mono, monospace" font-size="12">{vmax / 1.15:.2f}</text>')
        out.append(f'<text x="{x0 + 6}" y="{top + 10:.1f}" fill="#4B5563" font-family="IBM Plex Sans, sans-serif" '
                   f'font-size="12">{lab}</text>')
        pts = " ".join(f"{X(a):.1f},{bot - (bot - top) * bb / vmax:.1f}" for a, bb in zip(sy, v))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.5"/>')
    for yy, lab in ((Y_CRADLE, "cradle"), (Y_ANCHOR, "anchor"), (y_fin, "fin"), (y_spar_end, "spar end")):
        out.append(f'<line x1="{X(yy):.1f}" y1="{y0}" x2="{X(yy):.1f}" y2="{y1}" stroke="#CBD2DB" '
                   f'stroke-width="0.75" stroke-dasharray="6 4"/>')
        out.append(f'<text x="{X(yy):.1f}" y="{y1 + 16}" text-anchor="middle" fill="#6B7280" '
                   f'font-family="IBM Plex Mono, monospace" font-size="11">{lab}</text>')
    for v in np.arange(0, 0.6, 0.1):
        out.append(f'<text x="{X(v):.1f}" y="{y1 + 34}" text-anchor="middle" fill="#6B7280" '
                   f'font-family="IBM Plex Mono, monospace" font-size="12">{v:.1f}</text>')
    out.append(f'<text x="{x1}" y="{y1 + 52}" text-anchor="end" fill="#6B7280" '
               f'font-family="IBM Plex Mono, monospace" font-size="11">|y|, m</text></svg>')
    path.write_text("\n".join(out), encoding="utf-8")


def svg_modes(path, modes):
    W, H, x0, x1, y0 = 1200, 300, 90, 1100, 40
    fmax = 400.0
    def X(f):
        return x0 + (x1 - x0) * f / fmax
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    for name, fp in FORCING.items():
        a, bb = X(fp * (1 - SEP_MIN)), X(fp * (1 + SEP_MIN))
        out.append(f'<rect x="{a:.1f}" y="{y0}" width="{bb - a:.1f}" height="150" fill="#E2E6EC" opacity="0.6"/>')
        out.append(f'<line x1="{X(fp):.1f}" y1="{y0}" x2="{X(fp):.1f}" y2="{y0 + 150}" stroke="#9AA4B1" stroke-width="1"/>')
        out.append(f'<text x="{X(fp):.1f}" y="{y0 - 8 + (12 if "cruise" in name else 0)}" text-anchor="middle" '
                   f'fill="#6B7280" font-family="IBM Plex Mono, monospace" font-size="11">{name}</text>')
    for k, m in enumerate(modes):
        if m["f_hz"] > fmax:
            continue
        col = "#C2540A" if (m["station_ke"] >= 0.10 and separation(m["f_hz"]) < SEP_MIN) else "#1F5FC7"
        yy = y0 + 20 + 22 * (k % 6)
        out.append(f'<circle cx="{X(m["f_hz"]):.1f}" cy="{yy}" r="5" fill="{col}"/>')
        out.append(f'<text x="{X(m["f_hz"]) + 9:.1f}" y="{yy + 4}" fill="#121619" '
                   f'font-family="IBM Plex Mono, monospace" font-size="11">{m["f_hz"]:.0f} Hz {m["type"]} {m["sym"]}</text>')
    for f in range(0, int(fmax) + 1, 50):
        out.append(f'<text x="{X(f):.1f}" y="{y0 + 172}" text-anchor="middle" fill="#6B7280" '
                   f'font-family="IBM Plex Mono, monospace" font-size="12">{f}</text>')
    out.append(f'<line x1="{x0}" y1="{y0 + 155}" x2="{x1}" y2="{y0 + 155}" stroke="#9AA4B1" stroke-width="1"/>')
    out.append(f'<text x="{x1}" y="{y0 + 190}" text-anchor="end" fill="#6B7280" '
               f'font-family="IBM Plex Mono, monospace" font-size="11">Hz; grey = within 20 % of a rotor order</text></svg>')
    path.write_text("\n".join(out), encoding="utf-8")


def main():
    res = {"inputs": {k: v[0] for k, v in MAT.items()}}
    sec_nom = sec_factory()
    sec_lo = sec_factory(E_s=M["spar_E_lo_pa"], G_s=M["spar_G_lo_pa"])
    s_nom = section()
    s_lo = section(E_s=M["spar_E_lo_pa"], G_s=M["spar_G_lo_pa"])
    s_tip = section(with_spar=False)
    res["section_nominal"] = {k: v for k, v in s_nom.items()}
    res["section_low"] = {k: v for k, v in s_lo.items()}
    res["section_tip"] = {k: v for k, v in s_tip.items()}

    # ---- mass of the wing structure (physical, before the C1 scaling)
    half_with = y_spar_end
    m_core = s_nom["m_core"] * half_with * 2 + s_tip["m_core"] * (L_half - half_with) * 2
    m_tape = s_nom["m_tape"] * b
    m_spar = spar_mpm * 2 * y_spar_end
    m_fill = M["slot_fill_kgm"] * 2 * y_spar_end
    m_plugs = 2 * M["plug_mass_kg"] + 4 * M["anchor_plug_mass_kg"]
    res["mass"] = {"core_kg": m_core, "tape_kg": m_tape, "spar_kg": m_spar, "slot_fill_kg": m_fill,
                   "plugs_kg": m_plugs, "total_kg": m_core + m_tape + m_spar + m_fill + m_plugs,
                   "allocation_kg": pv("mass.allocation_g.wing") / 1000}

    # ---- beam integration of every C1 case (low-corner stiffness), envelopes
    cases = read_spanwise()
    rows_out = []
    env = {}
    fam_env = ("flight", "hover", "transition", "landing", "ground")
    sy_ref = None
    w_env = th_env = u_env = None
    for (cid, mc), v in cases.items():
        for s in (1, -1):
            sy, w, u, th = integrate_case(v["rows"], s, sec_lo)
            if sy_ref is None:
                sy_ref = sy
                w_env = np.zeros_like(sy)
                u_env = np.zeros_like(sy)
                th_env = np.zeros_like(sy)
            rec = {"case": cid, "mc": mc, "family": v["family"], "side": "R" if s > 0 else "L",
                   "w_tip_m": float(w[-1]), "u_tip_m": float(u[-1]), "th_max_rad": float(th[np.argmax(np.abs(th))]),
                   "w_max_abs": float(np.abs(w).max()), "w_fin_m": float(np.interp(y_fin, sy, w)),
                   "u_max_abs": float(np.abs(u).max()), "th_tip_rad": float(th[-1])}
            rows_out.append(rec)
            if v["family"] in fam_env:
                w_env = np.maximum(w_env, np.abs(np.interp(sy_ref, sy, w)))
                u_env = np.maximum(u_env, np.abs(np.interp(sy_ref, sy, u)))
                th_env = np.maximum(th_env, np.abs(np.interp(sy_ref, sy, th)))
    def worst(key, fams):
        r = max((x for x in rows_out if x["family"] in fams), key=lambda x: abs(x[key]))
        return {"value": abs(r[key]), "case": f'{r["case"]}/{r["mc"]}/{r["side"]}'}
    env["w_tip_envelope"] = worst("w_tip_m", fam_env)
    env["w_tip_flight"] = worst("w_tip_m", ("flight",))
    env["w_max_envelope"] = worst("w_max_abs", fam_env)
    env["u_max_envelope"] = worst("u_max_abs", fam_env)
    env["twist_envelope"] = worst("th_max_rad", fam_env)
    env["twist_flight"] = worst("th_max_rad", ("flight",))
    env["w_tip_transport"] = worst("w_tip_m", ("transport",))
    res["deflection"] = env
    # symmetry check of the sign conventions: F1 left vs right tip deflection
    f1 = [r for r in rows_out if r["case"] == "F1-PULLUP-VD" and r["mc"] == "MC-P"]
    res["check_symmetry_F1"] = {"right_mm": f1[0]["w_tip_m"] * 1000, "left_mm": f1[1]["w_tip_m"] * 1000}
    # integration step convergence on F1 (5, 10, 20 mm)
    conv_int = []
    for step in (4, 2, 1):
        sy, w, u, th = integrate_case(cases[("F1-PULLUP-VD", "MC-P")]["rows"], 1, sec_lo, step=step)
        conv_int.append({"dy_mm": 5 * step, "w_tip_mm": float(w[-1] * 1000)})
    res["conv_integration"] = conv_int
    with open(HERE / "data" / "deflection_cases.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        wr.writeheader()
        wr.writerows(rows_out)
    with open(HERE / "data" / "deflection_envelope.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["y_abs_m", "w_env_mm", "u_env_mm", "twist_env_deg"])
        for a, bb, cc, dd in zip(sy_ref, w_env, u_env, th_env):
            wr.writerow([f"{a:.4f}", f"{bb * 1000:.3f}", f"{cc * 1000:.3f}", f"{math.degrees(dd):.4f}"])
    svg_envelope(HERE / "fig" / "C2-01-deflection-envelope.svg", sy_ref, w_env, th_env, u_env)

    # ---- spar stress along the span (spar alone carries all bending: bounding)
    wenv_rows = list(csv.DictReader(open(C1D / "wing_envelope.csv", newline="")))
    I_s, r_o = s_nom["I_spar"], D_sp / 2
    sig = []
    for r in wenv_rows:
        y = float(r["y_m"])
        if y > y_spar_end:
            continue
        sig.append((y, float(r["Mbend_Nm_ultimate"]) * r_o / I_s, r["Mbend_Nm_max_case"]))
    smax = max(sig, key=lambda t: t[1])
    res["spar_stress"] = {"sigma_ult_max_pa": smax[1], "y_m": smax[0], "case": smax[2],
                          "Mb_ult_root_Nm": claim_value("C1", "CL-C1-SPAR-MB-ULT")}
    # composite share check at the root: fraction of flap / in-plane bending the spar takes
    res["spar_share"] = {"flap": s_nom["EI_flap_spar"] / s_nom["EI_flap"],
                         "inplane": s_nom["EI_inplane_spar"] / s_nom["EI_inplane"],
                         "torsion": s_nom["GJ_spar"] / s_nom["GJ"]}

    # ---- skin and foam stresses (composite, ultimate) at the root, worst components
    Mx_u = max(abs(float(wenv_rows[0]["Mx_Nm_max_limit"])), abs(float(wenv_rows[0]["Mx_Nm_min_limit"]))) * SF
    Mz_u = max(abs(float(wenv_rows[0]["Mz_Nm_max_limit"])), abs(float(wenv_rows[0]["Mz_Nm_min_limit"]))) * SF
    sn = section(tape_eff=1.0)   # full tape stiffness: upper bound on tape stress
    dz = max(np.max(ZU) - sn["zn"], sn["zn"] - np.min(ZL))
    dxm = max(sn["xn"], x_hinge - sn["xn"])
    Et, Ef = M["tape_E_pa"], M["xps_E_pa"]
    kf, ki = Mx_u / sn["EI_flap"], Mz_u / sn["EI_inplane"]
    res["skin_foam_root"] = {"tape_sigma_ult_pa": Et * (kf * dz + ki * dxm), "foam_sigma_ult_pa": Ef * (kf * dz + ki * dxm),
                             "Mx_ult": Mx_u, "Mz_ult": Mz_u}

    # ---- tip foam outboard of the spar end (flight + landing envelope at y 0.50) and the L6 damage case
    r50 = min(wenv_rows, key=lambda r: abs(float(r["y_m"]) - y_spar_end))
    Mx50 = max(abs(float(r50["Mx_Nm_max_limit"])), abs(float(r50["Mx_Nm_min_limit"]))) * SF
    Mz50 = max(abs(float(r50["Mz_Nm_max_limit"])), abs(float(r50["Mz_Nm_min_limit"]))) * SF
    st = section(with_spar=False, tape_eff=1.0)
    dzt = max(np.max(ZU) - st["zn"], st["zn"] - np.min(ZL))
    dxt = max(st["xn"], x_hinge - st["xn"])
    sig_t = Et * (Mx50 / st["EI_flap"] * dzt + Mz50 / st["EI_inplane"] * dxt)
    sig_f = Ef * (Mx50 / st["EI_flap"] * dzt + Mz50 / st["EI_inplane"] * dxt)
    l6 = cases[("L6-WINGTIP-STRIKE", "MC-P")]["rows"]
    r6 = [r for r in l6 if abs(abs(r[0]) - y_spar_end) < 1e-6]
    m6 = max(math.hypot(r[4], r[6]) for r in r6) if r6 else 0.0
    res["tip_foam"] = {"Mx_ult": Mx50, "Mz_ult": Mz50, "tape_sigma_ult_pa": sig_t, "foam_sigma_ult_pa": sig_f,
                       "L6_M_at_spar_end_Nm": m6,
                       "L6_tape_sigma_pa": Et * m6 / min(st["EI_flap"], st["EI_inplane"]) * max(dzt, dxt)}

    # ---- chordwise bending of the core aft of the spar under the elevon/section pressure at VD (CN 1)
    p = QVD * 1.0 * SF
    chord_checks = []
    for x in np.linspace(xs + 0.01, x_hinge - 0.01, 8):
        Mp = p * (c - x) ** 2 / 2            # per metre of span, about the station x
        Vp = p * (c - x)
        h = thickness_at(x)
        chord_checks.append({"x_m": float(x), "h_m": h, "tape_sigma_pa": Mp / (h * M["tape_t_m"]),
                             "foam_only_sigma_pa": 6 * Mp / h ** 2, "foam_shear_pa": 1.5 * Vp / h})
    res["chordwise"] = {"p_ult_pa": p, "worst_tape": max(chord_checks, key=lambda d: d["tape_sigma_pa"]),
                        "worst_foam_only": max(chord_checks, key=lambda d: d["foam_only_sigma_pa"]),
                        "stations": chord_checks}

    # ---- spar-to-core shear transfer (distributed air load into the spar)
    worst_q = 0.0
    for (cid, mc), v in cases.items():
        if v["family"] != "flight":
            continue
        r = side(v["rows"], 1)
        sy = np.abs(r[:, 0])
        mask = (np.abs(sy - y_fin) > 0.02) & (np.abs(sy - 0.30) > 0.02) & (sy < y_spar_end - 0.02) & (sy > 0.06)
        dF = np.abs(np.gradient(r[:, 3], sy))[mask]
        worst_q = max(worst_q, float(dF.max()))
    res["spar_bond"] = {"q_z_max_Npm": worst_q, "tau_ult_pa": worst_q * SF / (math.pi * D_sp / 2)}

    # ---- local spar wall at the block and at the brace anchor (ring model), plug
    Mv, Mex = ring_validation()
    res["ring_validation"] = {"model_Nm": Mv, "roark_Nm": Mex, "err": abs(Mv / Mex - 1)}
    F_couple = claim_value("C4", "CL-C4-SPAR-COUPLE")                 # design (ult x fitting x printed)
    W_bore = pv("fins.y_m") * 0 + 0.036                              # C4 block spar-bore length
    w_peak = 4 * F_couple / W_bore                                   # triangular half-distribution peak, N/m
    beta = M["contact_half_angle_deg"]
    rb = ring_check(w_peak, beta)
    rb60 = ring_check(w_peak, 60.0)
    F_brace = 142.0 * 0 + json_brace()                               # C4 design strut load
    w_anchor = F_brace / 0.016                                       # 16 mm saddle along the spar (D3 pocket)
    ra = ring_check(w_anchor, beta)
    plug_bear = w_peak / (d_sp)
    res["local_spar"] = {"F_couple_N": F_couple, "bore_len_m": W_bore, "w_peak_Npm": w_peak,
                         "ring_no_plug_sigma_pa": rb["sigma_pa"], "ring_no_plug_sigma_60_pa": rb60["sigma_pa"],
                         "plug_bearing_pa": plug_bear, "F_brace_N": F_brace, "w_anchor_Npm": w_anchor,
                         "ring_anchor_sigma_pa": ra["sigma_pa"]}

    # ---- transport cradle pad and pod bond on the wing side
    x3 = cases[("X3-DROP-Z", "MC-P")]["rows"]
    r3 = side(x3, 1)
    i0 = int(np.argmin(np.abs(np.abs(r3[:, 0]) - Y_CRADLE)))
    R_cr = abs(r3[i0 - 1, 3] - r3[i0, 3])
    res["cradle"] = {"R_limit_N": R_cr, "area_req_m2": R_cr * SF / M["xps_comp_allow_pa"]}
    Fpod = claim_value("C1", "CL-C1-POD-F-ULT") * 1.15 * 1.25
    res["pod"] = {"F_design_N": Fpod, "tau_pa": Fpod / (pv("pod.size_m")[0] * pv("pod.size_m")[1])}

    # ---- FE: static cross-check vs integration, mesh convergence (right half, clamped)
    conv = []
    for nh in (6, 12, 24, 48, 96):
        out = {"n_half": nh}
        for cid in ("F1-PULLUP-VD", "L1-LEVEL", "F7-ROLLPULL-VD"):
            ys, u = static_fe(cases[(cid, "MC-P")]["rows"], nh, sec_lo)
            out[cid] = {"w_tip_mm": float(u[-6 + 2] * 1000), "u_tip_mm": float(u[-6 + 0] * 1000),
                        "th_tip_deg": float(math.degrees(u[-6 + 4]))}
        conv.append(out)
    res["fe_static_conv"] = conv
    ref = {}
    for cid in ("F1-PULLUP-VD", "L1-LEVEL", "F7-ROLLPULL-VD"):
        sy, w, u, th = integrate_case(cases[(cid, "MC-P")]["rows"], 1, sec_lo)
        ref[cid] = {"w_tip_mm": float(w[-1] * 1000), "u_tip_mm": float(u[-1] * 1000),
                    "th_tip_deg": float(math.degrees(th[-1]))}
    res["integration_ref"] = ref
    fin = conv[-1]
    res["fe_vs_integration"] = {
        "F1_w_err": abs(fin["F1-PULLUP-VD"]["w_tip_mm"] / ref["F1-PULLUP-VD"]["w_tip_mm"] - 1),
        "L1_u_err": abs(fin["L1-LEVEL"]["u_tip_mm"] / ref["L1-LEVEL"]["u_tip_mm"] - 1),
        "F7_th_err": abs(fin["F7-ROLLPULL-VD"]["th_tip_deg"] / ref["F7-ROLLPULL-VD"]["th_tip_deg"] - 1)}
    # hand check: uniform-load cantilever from the F1 root moment, spar EI only
    Mr = float(side(cases[("F1-PULLUP-VD", "MC-P")]["rows"], 1)[0, 4])
    res["hand_w_tip_F1_mm"] = {"uniform_load_mm": Mr * L_half ** 2 / (4 * s_lo["EI_flap"]) * 1000,
                                "tip_load_mm": Mr * L_half ** 2 / (3 * s_lo["EI_flap"]) * 1000}

    # ---- modes: convergence on the low corner, then the four stiffness corners
    mc = []
    for nh in (6, 12, 24, 48, 96):
        mods, nr = modal(nh, sec_lo)
        mc.append({"n_half": nh, "n_rigid": nr, "f_hz": [m["f_hz"] for m in mods[:6]]})
    res["modal_conv"] = mc
    corners = {}
    for name, (E_, G_) in {"E70-G3": (70e9, 3e9), "E70-G5": (70e9, 5e9), "E100-G3": (100e9, 3e9),
                           "E100-G5": (100e9, 5e9)}.items():
        for teff in (0.5, 0.0, 1.0):
            mods, _ = modal(48, sec_factory(E_s=E_, G_s=G_, tape_eff=teff))
            for mcfg in ():
                pass
            corners[f"{name}-tape{teff}"] = mods
    res["modes"] = corners
    def worst_in(keys):
        w_ = None
        for key in keys:
            for m in corners[key]:
                if m["station_ke"] < 0.10 or m["f_hz"] > 1.2 * max(FORCING.values()):
                    continue
                sp = separation(m["f_hz"])
                if w_ is None or sp < w_["sep"]:
                    w_ = {"sep": sp, "corner": key, **m}
        return w_
    res["mode_sep_worst"] = worst_in(["E100-G5-tape0.5"])           # nominal stiffness
    res["mode_sep_worst_all"] = worst_in(list(corners))             # any stiffness corner
    res["station_modes_nominal"] = [dict(m, sep=separation(m["f_hz"])) for m in corners["E100-G5-tape0.5"]
                                    if m["station_ke"] >= 0.10 and m["f_hz"] < 400]
    nominal_modes = corners["E100-G5-tape0.5"]
    svg_modes(HERE / "fig" / "C2-02-wing-modes.svg", nominal_modes)
    # MC-C mass configuration at the low corner (lighter: frequencies up)
    mods_c, _ = modal(48, sec_lo, config="MC-C")
    res["modes_MC_C"] = mods_c

    # ---- aeroelastic statics and flutter (low corner, pessimistic shear centre for divergence)
    ae_conv = []
    for nh in (12, 24, 48):
        ae_conv.append({"n_half": nh, **aeroelastic(nh, sec_lo, s_lo["x_sc"])})
    res["aeroelastic_conv"] = ae_conv
    ae = aeroelastic(48, sec_lo, s_lo["x_sc"])
    ae_aft = aeroelastic(48, sec_lo, M["x_sc_aft_m"])
    sec_spar_only = sec_factory(E_s=M["spar_E_lo_pa"], G_s=M["spar_G_lo_pa"], tape_eff=0.0)
    ae_bound = aeroelastic(48, sec_spar_only, M["x_sc_aft_m"])
    res["aeroelastic"] = {
        "V_rev_ms": math.sqrt(2 * ae["q_rev"] / rho), "eff_vd": ae["eff_vd"],
        "V_div_ms": math.sqrt(2 * ae["q_div"] / rho) if math.isfinite(ae["q_div"]) else float("inf"),
        "V_div_aft_ms": math.sqrt(2 * ae_aft["q_div"] / rho) if math.isfinite(ae_aft["q_div"]) else float("inf"),
        "V_rev_bound_ms": math.sqrt(2 * ae_bound["q_rev"] / rho),
        "V_div_bound_ms": math.sqrt(2 * ae_bound["q_div"] / rho) if math.isfinite(ae_bound["q_div"]) else float("inf"),
        "eff_vd_bound": ae_bound["eff_vd"], "x_sc_m": s_lo["x_sc"]}
    fl = [{"n_half": nh, **flutter(nh, sec_lo)} for nh in (12, 24)]
    res["flutter_conv"] = fl
    res["flutter"] = fl[-1]

    # ---- spar trade (same loads)
    trade = []
    Mb = claim_value("C1", "CL-C1-SPAR-MB-ULT")
    for (Do, Di) in ((0.016, 0.014), (0.018, 0.016), (0.020, 0.018), (0.022, 0.020), (0.025, 0.023)):
        Is = math.pi / 64 * (Do ** 4 - Di ** 4)
        sf = sec_factory(E_s=M["spar_E_lo_pa"], G_s=M["spar_G_lo_pa"], D=Do, d=Di)
        mods, _ = modal(24, sf)
        sy, w, u, th = integrate_case(cases[("G2-HANG-MOTOR", "MC-P")]["rows"], 1, sf)
        cover = (thickness_at(xs) - Do) / 2
        sep = min((separation(m["f_hz"]) for m in mods if m["station_ke"] >= 0.1 and m["f_hz"] < 400), default=9)
        trade.append({"tube_mm": f"{Do * 1000:.0f}x{Di * 1000:.0f}",
                      "mass_g": 1550 * math.pi / 4 * (Do ** 2 - Di ** 2) * 1000 * 2 * y_spar_end,
                      "sigma_ult_mpa": Mb * Do / 2 / Is / 1e6, "w_tip_G2_mm": float(abs(w[-1]) * 1000),
                      "f1_hz": mods[0]["f_hz"], "f1_type": mods[0]["type"], "cover_mm": cover * 1000,
                      "min_sep_station_modes": sep})
    res["spar_trade"] = trade
    (HERE / "out" / "results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    write_params(res)
    write_sizing(res)
    report(res)


def json_brace():
    """C4 design brace load (CALC-C4-STATIC-1L output strut_comp_design_n)."""
    for n in json.loads((RD / "team" / "C4" / "claims.json").read_text(encoding="utf-8"))["nodes"]:
        if n.get("type") == "calculation" and "strut_comp_design_n" in n.get("outputs", {}):
            return float(n["outputs"]["strut_comp_design_n"])
    return 142.0


def write_params(res):
    def P(v, unit, note, source="team/C2/wing_struct.py", status="CHECKED"):
        return {"value": round(float(v), 6) if isinstance(v, (int, float)) else v, "unit": unit, "source": source,
                "status": status, "note": note}
    sn, sl = res["section_nominal"], res["section_low"]
    dfl = res["deflection"]
    ae, fl = res["aeroelastic"], res["flutter"]
    ws = res["mode_sep_worst"]
    conv = res["modal_conv"]
    fconv = max(abs(a / b_ - 1) for a, b_ in zip(conv[-2]["f_hz"][:4], conv[-1]["f_hz"][:4]))
    sconv = res["fe_static_conv"]
    sc = max(abs(sconv[-2][k]["w_tip_mm"] / sconv[-1][k]["w_tip_mm"] - 1) for k in ("F1-PULLUP-VD",))
    out = {"_note": "Written by team/C2/wing_struct.py. Do not edit by hand: change MAT in the script or "
                    "params/params.json, re-run it, then team/C2/c2_claims.py.",
           "c2": {"inputs": {k: {"value": v[0], "unit": v[1], "source": v[2], "status": v[3], "note": v[4]}
                             for k, v in MAT.items()},
                  "section": {
                      "EI_flap_lo": P(sl["EI_flap"], "N m2", "flap EI, spar E 70 GPa, tape 50 %"),
                      "EI_inplane_lo": P(sl["EI_inplane"], "N m2", "in-plane EI about the modulus-weighted x"),
                      "GJ_lo": P(sl["GJ"], "N m2", "foam + tape cell + spar, spar G 3 GPa"),
                      "GJ_spar_lo": P(sl["GJ_spar"], "N m2", "spar alone, G 3 GPa"),
                      "I_spar": P(sn["I_spar"], "m4", "pi/64 (D^4 - d^4)"),
                      "J_spar": P(sn["J_spar"], "m4", "pi/32 (D^4 - d^4)"),
                      "spar_share_flap": P(res["spar_share"]["flap"], "-", "spar EI / section EI, flap"),
                      "spar_share_inplane": P(res["spar_share"]["inplane"], "-", "spar EI / section EI, in-plane"),
                      "x_sc": P(sl["x_sc"], "m", "flap shear-centre estimate"),
                      "t_at_spar": P(sn["t_spar"], "m", "section thickness at the spar station"),
                      "tip_EI_flap": P(res["section_tip"]["EI_flap"], "N m2", "foam + tape outboard of the spar")},
                  "fe": {
                      "w_tip_env_m": P(dfl["w_tip_envelope"]["value"], "m", "max flap tip deflection, envelope "
                                       "cases, limit, low corner: " + dfl["w_tip_envelope"]["case"]),
                      "w_tip_flight_m": P(dfl["w_tip_flight"]["value"], "m", "flight cases only: " +
                                          dfl["w_tip_flight"]["case"]),
                      "w_max_env_m": P(dfl["w_max_envelope"]["value"], "m", "max |w| anywhere: " + dfl["w_max_envelope"]["case"]),
                      "u_max_env_m": P(dfl["u_max_envelope"]["value"], "m", "max in-plane |u|: " + dfl["u_max_envelope"]["case"]),
                      "twist_env_rad": P(dfl["twist_envelope"]["value"], "rad", "max twist: " + dfl["twist_envelope"]["case"]),
                      "twist_flight_rad": P(dfl["twist_flight"]["value"], "rad", "max twist, flight: " + dfl["twist_flight"]["case"]),
                      "spar_sigma_ult_max_pa": P(res["spar_stress"]["sigma_ult_max_pa"], "Pa",
                                                 f'spar alone, envelope Mbend ultimate, y {res["spar_stress"]["y_m"]:.3f} m'),
                      "tape_sigma_root_ult_pa": P(res["skin_foam_root"]["tape_sigma_ult_pa"], "Pa", "tape at full stiffness, root, Mx and Mz ult combined"),
                      "foam_sigma_root_ult_pa": P(res["skin_foam_root"]["foam_sigma_ult_pa"], "Pa", "foam fibre stress, root, ult"),
                      "tip_foam_sigma_ult_pa": P(res["tip_foam"]["foam_sigma_ult_pa"], "Pa", "foam outboard of the spar end, ult"),
                      "tip_tape_sigma_ult_pa": P(res["tip_foam"]["tape_sigma_ult_pa"], "Pa", "tape outboard of the spar end, ult"),
                      "chord_tape_sigma_ult_pa": P(res["chordwise"]["worst_tape"]["tape_sigma_pa"], "Pa",
                                                   "chordwise bending of the core aft of the spar, CN 1 at q_VD, ult, tape faces"),
                      "chord_foam_only_sigma_ult_pa": P(res["chordwise"]["worst_foam_only"]["foam_only_sigma_pa"], "Pa",
                                                        "same, bare foam (no tape)"),
                      "spar_bond_tau_ult_pa": P(res["spar_bond"]["tau_ult_pa"], "Pa", "air load into the spar through the slot bond"),
                      "ring_no_plug_sigma_pa": P(res["local_spar"]["ring_no_plug_sigma_pa"], "Pa",
                                                 "spar wall ring bending at the block bore end, no plug, design load"),
                      "plug_bearing_pa": P(res["local_spar"]["plug_bearing_pa"], "Pa", "plug bearing with the plug fitted, design"),
                      "ring_anchor_sigma_pa": P(res["local_spar"]["ring_anchor_sigma_pa"], "Pa",
                                                "spar wall ring bending under the brace anchor saddle, design, no plug"),
                      "cradle_area_req_m2": P(res["cradle"]["area_req_m2"], "m2", "foam pad area per cradle, X3 drop x 1.5"),
                      "pod_tau_pa": P(res["pod"]["tau_pa"], "Pa", "pod bond shear on the wing foam, design"),
                      "mode_sep_worst": P(ws["sep"], "-", f'worst separation of a station-participating wing mode '
                                          f'({ws["f_hz"]:.1f} Hz {ws["type"]} {ws["sym"]}, corner {ws["corner"]})'),
                      "mode_worst_f_hz": P(ws["f_hz"], "Hz", "frequency of that mode"),
                      "mode_sep_worst_all": P(res["mode_sep_worst_all"]["sep"], "-", "same over all 12 stiffness corners ("
                                              f'{res["mode_sep_worst_all"]["f_hz"]:.1f} Hz, {res["mode_sep_worst_all"]["corner"]})'),
                      "f_torsion_anti_hz": P(res["modes"]["E70-G3-tape0.5"][0]["f_hz"], "Hz", "first wing mode, low corner: antisymmetric torsion (fin stations rocking)"),
                      "f_torsion_sym_hz": P(res["modes"]["E70-G3-tape0.5"][1]["f_hz"], "Hz", "second wing mode, low corner: symmetric torsion"),
                      "V_rev_ms": P(ae["V_rev_ms"], "m/s", "roll reversal, strip theory, low corner"),
                      "V_rev_bound_ms": P(ae["V_rev_bound_ms"], "m/s", "roll reversal, spar-only GJ bound"),
                      "eff_vd": P(ae["eff_vd"], "-", "elevon roll effectiveness at VD (rigid = 1)"),
                      "V_div_bound_ms": P(ae["V_div_bound_ms"], "m/s", "divergence, spar-only GJ, shear centre 20 mm aft"),
                      "V_flutter_ms": P(fl["V_flutter"] if math.isfinite(fl["V_flutter"]) else fl["V_max_swept"], "m/s",
                                        "flutter screen (modal p-k, 6 modes): no crossing up to this speed"
                                        if not math.isfinite(fl["V_flutter"]) else "flutter screen crossing"),
                      "mesh_conv_freq": P(fconv, "-", "max change of the first 4 frequencies, 48 -> 96 elements per half"),
                      "mesh_conv_static": P(sc, "-", "F1 tip deflection change, 48 -> 96 elements per half"),
                      "fe_vs_integration": P(max(res["fe_vs_integration"].values()), "-",
                                             "FE (96/half) vs beam integration, F1 w, L1 u, F7 twist"),
                      "ring_validation_err": P(res["ring_validation"]["err"], "-", "ring model vs Roark two-point-load ring, P R / pi"),
                      "F_brace_design_N": P(res["local_spar"]["F_brace_N"], "N", "C4 design brace load (CALC-C4-STATIC-1L)", source="team/C4/claims.json"),
                      "anchor_plug_bearing_pa": P(res["local_spar"]["w_anchor_Npm"] / d_sp, "Pa", "anchor plug bearing, design"),
                      "twist_flight_deg": P(math.degrees(res["deflection"]["twist_flight"]["value"]), "deg", "max twist, flight, limit, low corner"),
                      "wing_mass_kg": P(res["mass"]["total_kg"], "kg", "core + tape + spar + slot fill + 2 plugs")}}}
    (HERE / "params.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


def write_sizing(res):
    sn = res["section_nominal"]
    t_sp = sn["t_spar"]
    zu = float(np.interp(xs, XA, ZU))
    zl = float(np.interp(xs, XA, ZL))
    sizing = {
        "_note": "C2 sizing outputs for D1 (wing CAD) and D3/D7 where marked. Written by team/C2/wing_struct.py. "
                 "Frame: params.json#frame, metres. Status PROPOSED until D1 models it and H1 proof-tests it.",
        "spar": {"part": "WNG-002", "tube": "CF 22 x 20 x 1000 mm, roll-wrapped, unspliced", "x_m": xs, "z_m": zs,
                 "y_m": [-y_spar_end, y_spar_end], "foam_cover_upper_mm": round((zu - zs - D_sp / 2) * 1000, 2),
                 "foam_cover_lower_mm": round((zs - D_sp / 2 - zl) * 1000, 2),
                 "slot": "22.4 mm wide (0.2 mm per side bond line), cut from the lower surface to z_s + 11.2 mm, "
                         "bottom rounded r 11.2 mm; slot foam strip re-bonded as the cap",
                 "bond": "30-min epoxy + glass microballoons (1:1 by volume), full wet-out of the slot; cure 24 h before tape",
                 "abrade": "sand the tube 120 grit, wipe with IPA"},
        "plugs": {"what": "internal plug, printed PETG 19.8 mm dia x 36 mm, 4 perimeters 50 % gyroid, bonded with "
                          "thickened epoxy", "y_m": [-y_fin, y_fin], "why": "spar wall ring bending under the "
                          "through-core block bore (CR-C4-02)", "install": "push in from the spar end with a marked "
                          "dowel to |y| = 0.32 m before the spar goes into the slot", "mass_g_each": M["plug_mass_kg"] * 1000,
                  "anchor_plugs": {"what": "printed PETG plug 19.8 mm dia x 20 mm, 30 % fill, bonded", "y_m": [-Y_ANCHOR, Y_ANCHOR],
                                   "per_anchor": "one under each brace saddle, upper and lower braces share it (|y| 0.242)",
                                   "why": "ring bending under the 146 N design saddle load exceeds the hoop allowable without it",
                                   "order": "push the anchor plug (0.242) in first, then the block plug (0.32)", "mass_g_each": M["anchor_plug_mass_kg"] * 1000}},
        "skin": {"part": "WNG-003", "layup": "1 layer packing tape each side, spanwise strips, 10 % overlap, "
                                            "wrapped 15 mm round the LE; tape continuous over the spar slot and the "
                                            "block pockets", "required_for": "chordwise bending aft of the spar "
                                            "(bare foam MS < tape MS), torsion cell, handling",
                 "doublers": "one extra chordwise tape band 60 mm wide over each block pocket and each servo pocket edge"},
        "core": {"part": "WNG-001", "material": "XPS F-250, one piece", "ribs": "none: the core is the rib; the "
                 "blocks FIN-004-L/R are the hard points at |y| 0.32",
                 "pockets": "block pocket full depth at |y| 0.32 (C4/D3 size), brace anchor pockets 20 x 16 mm to the "
                            "spar at |y| 0.242, servo pockets aft of x 0.12 m only",
                 "keep_out": "no cut deeper than 50 % of the local thickness between x 0.06 and 0.10 m except the "
                             "spar slot and block pockets"},
        "tip": {"unspanned_m": round(L_half - y_spar_end, 3), "edge": "wingtip edge tape 2 layers (damage fuse; "
                "L6 tip strike breaks the tip outboard of the spar, repair = re-cut and glue)"},
        "transport_cradle": {"y_m": [-Y_CRADLE, Y_CRADLE], "pad_area_min_m2": round(res["cradle"]["area_req_m2"], 5),
                             "pad_min_mm": "40 x 40 under the spar line (D7)"},
        "pod": {"bond": "epoxy to bare foam (remove tape in the footprint, sand); not onto tape"},
        "mass_g": {k: round(v * 1000, 1) for k, v in res["mass"].items()},
    }
    (HERE / "sizing.json").write_text(json.dumps(sizing, indent=1) + "\n", encoding="utf-8")


def report(res):
    pr = print
    sl = res["section_low"]
    pr(f'section (low corner): EI flap {sl["EI_flap"]:.1f}  EI in-plane {sl["EI_inplane"]:.1f}  GJ {sl["GJ"]:.1f} '
       f'(foam {sl["GJ_foam"]:.1f} cell {sl["GJ_cell"]:.1f} spar {sl["GJ_spar"]:.1f}) N m2; GAz {sl["GA_z"]:.0f} '
       f'GAx {sl["GA_x"]:.0f} N; xn {sl["xn"]:.4f} x_sc {sl["x_sc"]:.4f} t_spar {sl["t_spar"] * 1000:.1f} mm')
    pr("spar share", {k: round(v, 3) for k, v in res["spar_share"].items()})
    pr("mass", {k: round(v * 1000, 1) for k, v in res["mass"].items()})
    pr("deflection", {k: (round(v["value"] * 1000, 2) if "rad" not in k and "twist" not in k else
                          round(math.degrees(v["value"]), 3), v["case"]) for k, v in res["deflection"].items()})
    pr("symmetry F1", res["check_symmetry_F1"], "int conv", res["conv_integration"])
    pr("spar stress", res["spar_stress"])
    pr("skin/foam root", res["skin_foam_root"])
    pr("tip", res["tip_foam"])
    pr("chordwise", res["chordwise"]["worst_tape"], res["chordwise"]["worst_foam_only"])
    pr("bond", res["spar_bond"], "ring val", res["ring_validation"])
    pr("local", res["local_spar"])
    pr("cradle", res["cradle"], "pod", res["pod"])
    pr("FE static conv", json.dumps(res["fe_static_conv"]))
    pr("integration ref", res["integration_ref"], "FE vs int", res["fe_vs_integration"], "hand F1", res["hand_w_tip_F1_mm"])
    pr("modal conv", json.dumps(res["modal_conv"]))
    for k, mods in res["modes"].items():
        pr(k, [(round(m["f_hz"], 1), m["type"][:4], m["sym"][:4], round(m["station_ke"], 2)) for m in mods[:6]])
    pr("MC-C", [(round(m["f_hz"], 1), m["type"][:4], m["sym"][:4]) for m in res["modes_MC_C"][:6]])
    pr("worst sep", res["mode_sep_worst"], res["mode_sep_worst_all"])
    pr("aeroelastic", res["aeroelastic"], res["aeroelastic_conv"])
    pr("flutter", res["flutter_conv"])
    for t in res["spar_trade"]:
        pr(t)


if __name__ == "__main__":
    main()
