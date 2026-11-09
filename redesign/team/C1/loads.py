"""C1 loads engineer: load cases and load distributions for the K09-L quad tailsitter.

Run:  python -I redesign/team/C1/loads.py
Writes claims.json beside this file (proof chain) and the data files in team/C1/data/ that C2-C6, D3, D5 and D7
consume (spanwise wing loads, fin/tube heightwise loads, joint loads, foot loads, envelopes, V-n diagram).

Method (one model for every case):
  * Lumped-mass model of the aircraft at the 2.6 kg gate built from params.json (wing in 5 mm strips, fins and
    tubes discretised, motor stations, pod group). Two growth placements, both run for every case:
      MC-C  the gap from the allocations to the gate sits in the pod (worst for wing root bending),
      MC-P  every item is scaled pro rata to the gate (worst for the motor stations, fins and feet).
  * Each load case = applied loads (aero strips, rotor thrust and torque, ground or hand reactions) plus gravity
    in body axes. Rigid-body accelerations come from the resultant (d'Alembert, quasi-static, no omega^2 terms),
    so every free body is in equilibrium and any cut gives its internal load by summing one side.
  * Cut load = resultant of (applied + gravity + inertia) on the outboard part, at the cut reference point, in the
    aircraft frame (x aft, y right, z up, cruise attitude). It is the load the cut must pass inboard. Limit loads;
    ultimate = 1.5 x limit; joints add the fitting factor (and the printed/bonded factor).
Standard library only. Every calculation is a pure function of the node ids it names.
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ====================================================================== sources and assumptions
kit.source("SRC-C1-FAR23", "14 CFR Part 23 (pre-Amdt 23-64) loads", "standard",
           where="23.321-23.351 flight loads, 23.341 gust formula, 23.473 landing (lift 2/3 W), 23.561 emergency "
                 "landing, 23.619/23.625 special and fitting factors, 23.303 factor of safety 1.5",
           note="Small-aeroplane practice adopted by analogy; there is no certification basis for this UAV.")
kit.source("SRC-C1-PRATT", "Pratt & Walker, NACA Rep. 1206 (1954) gust formula", "paper",
           where="kg = 0.88 mu / (5.3 + mu), mu = 2 (W/S) / (rho c a g)")
kit.source("SRC-C1-THIN-AIRFOIL", "Abbott & von Doenhoff, Theory of Wing Sections, sec. 8.6", "book",
           where="plain-flap thin-airfoil increments dCl/d(delta), dCm/d(delta)")
kit.source("SRC-C1-HOERNER", "Hoerner, Fluid-Dynamic Drag (1965), ch. 3", "book",
           where="flat plate normal to the flow CD ~ 1.17-1.2")

ASM = {}


def asm(id, title, text, basis, value, unit, status="UNVERIFIED", cites=()):
    ASM[id] = value
    kit.assumption(id, title, text, basis, value=value, unit=unit, status=status, cites=cites)


def _b2_spanload(case="CL0.80"):
    """B2's AVL + XFOIL strip loading (team/B2/out/loads_spanwise.json, CR-B2-07): [y_m, cl/CL, cm_c4] rows."""
    p = HERE.parents[0] / "B2" / "out" / "loads_spanwise.json"
    d = json.loads(p.read_text(encoding="utf-8"))["cases"][case]
    return [[round(y, 5), round(r, 5), round(cm, 5)] for y, r, cm in zip(d["y_m"], d["cl_over_CL"], d["cm_c4"])]


asm("ASM-C1-B2-SPANLOAD", "Spanwise lift shape and cm from B2's AVL (trimmed CL 0.80)",
    "Strip lift per unit CL (cl/CL) and section cm about c/4 versus y of the trimmed S5010 wing with fins, props off, "
    "copied from team/B2/out/loads_spanwise.json case CL0.80 (CR-B2-07); replaces Schrenk",
    "B2 AVL 3.52 + XFOIL viscous cm at c 0.30 (AR 3.83); the shape changes < 1 % between CL 0.3 and 1.0 (centroid "
    "0.421-0.423 b/2) and the 0.32 chord (AR 3.59) moves it inboard slightly (conservative). Pod and slipstream "
    "not included (B2 note)", _b2_spanload(), "m,-,-", status="UNVERIFIED", cites=["SRC-B2-AVL", "SRC-B2-XFOIL"])
asm("ASM-C1-CLMIN", "Negative CL limit 0.4", "Most negative CL of the reflexed wing, elevons neutral (magnitude)",
    "B2 CR-B2-07: keep 0.4 (XFOIL section -0.38 at Re 3e5, CL-B2-CLMIN-2D); a larger magnitude raises the negative "
    "stall line, so 0.4 is the conservative pick", 0.4, "-", cites=["SRC-B2-XFOIL"])
asm("ASM-C1-UDE-D-FRAC", "Gust at VD is half the gust at VC", "Derived gust velocity at VD = 0.5 x the VC value",
    "FAR 23.333(c) ratio (25/50 ft/s)", 0.5, "-", status="PROPOSED", cites=["SRC-C1-FAR23"])
asm("ASM-C1-PROP-PITCH", "Prop pitch 5.5 in", "Geometric pitch of the APC 11x5.5MR", "from the prop name (D-05)",
    0.1397, "m", status="PROPOSED", cites=["SRC-APC-11X55MR"])
asm("ASM-C1-VD-FACTOR", "VD = 1.25 x fastest level speed", "Design dive speed = 1.25 x max(VC, VH)",
    "FAR 23.335(b) VD >= 1.25 VC with VC = the highest level speed the aircraft can hold; VH = max(prop pitch speed "
    "at the F4 rpm cap, B1's top level speed)", 1.25, "-", status="PROPOSED", cites=["SRC-C1-FAR23"])
asm("ASM-C1-BELL-INERTIA", "Motor bell inertia 1.5e-5 kg m2", "Rotating bell + magnets of the X3108S about its axis",
    "~40 g ring at r ~ 19 mm", 1.5e-5, "kg m2")
asm("ASM-C1-PITCH-RATE", "Peak body rate 3 rad/s", "Highest body rate during transition or recovery (any axis)",
    "about 2 x the ArduPilot tailsitter rate limits; covers a saturated recovery", 3.0, "rad/s")
asm("ASM-C1-ELEVON-CN", "Elevon panel CN 1.0", "Normal-force coefficient on a fully deflected elevon panel, for hinge/horn sizing",
    "upper bound for a 22 % plain flap at 25 deg; B2 hinge moments from XFOIL supersede", 1.0, "-")
asm("ASM-C1-ADAPTER-MASS", "Prop adapter and nut 5 g", "Mass of one prop adapter and nut", "A3 mass model EST",
    0.005, "kg")
asm("ASM-C1-CRUSH-EFF", "Crush efficiency 0.5", "Energy absorbed / (peak force x stroke) of a foot, foam pad or contact",
    "linear-spring behaviour (worst); a constant-force crush core reaches ~0.8", 0.5, "-")
asm("ASM-C1-LAND-LIFT", "Rotor lift 2/3 W at touchdown", "Thrust still acting at touchdown, fraction of weight",
    "FAR 23.473(b); ArduPilot keeps throttle until the land detector trips", 0.667, "-", status="PROPOSED",
    cites=["SRC-C1-FAR23"])
asm("ASM-C1-FRICTION", "Ground friction 0.5", "Side load / vertical load at a foot", "dry grass / packed dirt",
    0.5, "-")
asm("ASM-C1-CONTACT-STROKE", "Contact stroke 10 mm", "Crush stroke at an unprotected contact (wingtip TE, motor end)",
    "foam/grass contact without a bumper", 0.010, "m")
asm("ASM-C1-CD-PLATE", "Flat-plate CD 1.2", "Broadside drag/normal-force coefficient of the wing or a fin",
    "flat plate normal to the flow", 1.2, "-", status="PROPOSED", cites=["SRC-C1-HOERNER"])
asm("ASM-C1-HANDLING-N", "Handling factor 2", "Ground-handling load factor (lift, carry, set down)",
    "jerk when lifting one-handed or setting down", 2.0, "-", status="PROPOSED")
asm("ASM-C1-CRASH-V", "Crash speed 5 m/s", "Impact speed of the survivable crash for pack retention",
    "A2 R-PACK-RETENTION basis", 5.0, "m/s", status="PROPOSED")
asm("ASM-C1-CRASH-STROKE", "Crash stroke 0.10 m", "Arrest distance in the crash", "A2 R-PACK-RETENTION basis",
    0.10, "m", status="PROPOSED")
asm("ASM-C1-CRADLE-Y", "Cradles at y = +/-0.20 m", "Spar cradle stations in the box", "inboard of the fins, clear of "
    "the pod and servos; D7 sets", 0.20, "m", status="PROPOSED")
asm("ASM-C1-CRADLE-STROKE", "Cradle foam stroke 70 mm", "Usable crush stroke of the cradle/box foam in a drop",
    "CHANGE-LOG D-22: D7 puts >= 70 mm crush foam under the spar cradles (CR-C1-05). Read as usable STROKE; a foam "
    "block bottoms at ~60-70 % strain, so D7 needs ~0.10-0.12 m of block thickness for it", 0.070, "m",
    status="PROPOSED")
asm("ASM-C1-FITTING-FACTOR", "Fitting factor 1.15", "Extra factor on every joint and fitting", "FAR 23.625",
    1.15, "-", status="PROPOSED", cites=["SRC-C1-FAR23"])
asm("ASM-C1-PRINTED-FACTOR", "Printed/bonded factor 1.25", "Extra factor on printed PETG parts and bonds into foam",
    "FAR 23.619 special factor for variable material; C6 may lower it with coupon tests", 1.25, "-")
asm("ASM-C1-PROP-NUT-TORQUE", "Prop nut torque 1.5 N m", "Torque applied to a prop nut at field set-up",
    "hand tightening with a prop wrench; reacted by the mount and tube", 1.5, "N m")
asm("ASM-C1-STRAP-PRELOAD", "Pack strap preload 40 N", "Total pack strap tension after cinching",
    "two-hand cinch of a 20 mm strap", 40.0, "N")

# Inputs every model-based calculation reads (arg -> node id) and their units.
MODEL = {
    "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "m_gate": P + "requirements.mtow_gate_kg",
    "b": P + "wing.span_m", "c": P + "wing.chord_m", "x_spar": P + "wing.spar.x_m",
    "spar_len": P + "wing.spar.length_m", "spar_mpm": P + "wing.spar.mass_per_m_kgm",
    "el_f": P + "wing.elevon.chord_frac", "el_in": P + "wing.elevon.inboard_y_m",
    "el_out": P + "wing.elevon.outboard_y_m", "el_def": P + "wing.elevon.deflection_deg",
    "fin_y": P + "fins.y_m", "fin_hh": P + "fins.half_height_m", "fin_le": P + "fins.le_x_m", "fin_te": P + "fins.te_x_m",
    "fin_am": P + "fins.areal_mass_kgm2", "fin_layers": P + "fins.layers",
    "tube_od": P + "fins.tube.od_m", "tube_len": P + "fins.tube.length_m", "tube_x": P + "fins.tube.x_m",
    "motor_m": P + "propulsion.motor_mass_kg", "motor_len": P + "propulsion.motor_length_m",
    "prop_m": P + "propulsion.prop_mass_kg", "prop_D": P + "propulsion.prop_diameter_m",
    "esc_m": P + "propulsion.esc_mass_kg", "x_mount": P + "propulsion.stations.x_mount_m",
    "x_prop": P + "propulsion.stations.x_prop_plane_m", "st_y": P + "propulsion.stations.y_m",
    "st_z": P + "propulsion.stations.z_m", "pod_size": P + "pod.size_m", "pod_xle": P + "pod.x_le_m",
    "pod_zb": P + "pod.z_base_m", "batt_m": P + "battery.mass_kg", "batt_size": P + "battery.size_m",
    "foot_h": P + "cg.foot_height_m",
    "a_wing": P + "mass.allocation_g.wing", "a_fins": P + "mass.allocation_g.fins", "a_pod": P + "mass.allocation_g.pod",
    "a_landing": P + "mass.allocation_g.landing", "a_power": P + "mass.allocation_g.power",
    "a_avionics": P + "mass.allocation_g.avionics", "a_harness": P + "mass.allocation_g.harness",
    "a_mech": P + "mass.allocation_g.mechanisms",
    "mount_m": "ASM-J1-MOUNT-MASS", "adapter_m": "ASM-C1-ADAPTER-MASS", "pack_x": "CL-A3-PACK-X-REQ",
}
MODEL_UNITS = {
    "g": "m/s2", "rho": "kg/m3", "m_gate": "kg", "b": "m", "c": "m", "x_spar": "m", "spar_len": "m",
    "spar_mpm": "kg/m", "el_in": "m", "el_out": "m", "el_def": "deg", "fin_y": "m", "fin_hh": "m", "fin_le": "m",
    "fin_te": "m", "fin_am": "kg/m2", "tube_od": "m", "tube_len": "m", "tube_x": "m", "motor_m": "kg",
    "motor_len": "m", "prop_m": "kg", "prop_D": "m", "esc_m": "kg", "x_mount": "m", "x_prop": "m", "st_y": "m",
    "st_z": "m", "pod_size": "m", "pod_xle": "m", "pod_zb": "m", "batt_m": "kg", "batt_size": "m", "foot_h": "m",
    "a_wing": "g", "a_fins": "g", "a_pod": "g", "a_landing": "g", "a_power": "g", "a_avionics": "g",
    "a_harness": "g", "a_mech": "g", "mount_m": "kg", "adapter_m": "kg", "pack_x": "m",
}
MODEL_KEYS = list(MODEL)

# ====================================================================== vector helpers


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    return math.sqrt(dot(a, a))


def unit(a):
    n = norm(a)
    return mul(a, 1.0 / n)


def solve3(A, b):
    """Solve a 3x3 linear system by Cramer's rule."""
    def det(M):
        return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    D = det(A)
    out = []
    for k in range(3):
        M = [list(r) for r in A]
        for i in range(3):
            M[i][k] = b[i]
        out.append(det(M) / D)
    return tuple(out)


ZERO = (0.0, 0.0, 0.0)
STATIONS = {"UR": (1, 1), "UL": (-1, 1), "LR": (1, -1), "LL": (-1, -1)}      # (side y, side z)
SPIN = {"UR": 1, "LL": 1, "UL": -1, "LR": -1}        # spin sense about +x, diagonal pairs alike (F4 confirms)

# ====================================================================== mass model


def build_items(k, growth="centre", dy_target=0.005):
    """Lumped masses (kg, m) from params. growth: 'centre' (gap to the gate in the pod) or 'prorata'."""
    it = []

    def put(m, r, grp, side=None, st=None, fin=False, transport=True):
        if side is None:
            side = 0 if abs(r[1]) < 1e-12 else (1 if r[1] > 0 else -1)
        it.append({"m": m, "r": r, "grp": grp, "side": side, "st": st, "fin": fin, "transport": transport})

    b, c = k["b"], k["c"]
    n = max(2, int(round(b / dy_target)))
    dy = b / n
    m_spar_tot = k["spar_mpm"] * k["spar_len"]
    m_core = k["a_wing"] / 1000.0 - m_spar_tot
    for i in range(n):
        y = -b / 2 + (i + 0.5) * dy
        put(m_core / n, (0.42 * c, y, 0.0), "wing")
        if abs(y) < k["spar_len"] / 2:
            put(k["spar_mpm"] * dy, (k["x_spar"], y, 0.0), "wing")
    for s in (1, -1):
        put(k["a_mech"] / 2000.0, (0.63 * c, s * k["el_in"][1], 0.0), "mech")
    m_tube = k["spar_mpm"] * k["tube_len"]
    m_board = k["fin_am"] * k["fin_layers"] * (k["fin_te"] - k["fin_le"]) * 2 * k["fin_hh"]
    m_finrem = k["a_fins"] / 2000.0 - m_tube - m_board - 2 * k["mount_m"]
    for s in (1, -1):
        yf = s * k["fin_y"]
        nt = 8
        for j in range(nt):
            z = -k["tube_len"] / 2 + (j + 0.5) * k["tube_len"] / nt
            put(m_tube / nt, (k["tube_x"], yf, z), "tube", side=s, fin=True)
        nx, nz = 4, 8
        for ix in range(nx):
            x = k["fin_le"] + (ix + 0.5) * (k["fin_te"] - k["fin_le"]) / nx
            for iz in range(nz):
                z = -k["fin_hh"] + (iz + 0.5) * 2 * k["fin_hh"] / nz
                put(m_board / (nx * nz), (x, yf, z), "board", side=s, fin=True)
        put(m_finrem, ((k["tube_x"] + k["x_spar"]) / 2, yf, 0.0), "finrem", side=s, fin=True)
        for sz in (1, -1):
            st = [key for key, v in STATIONS.items() if v == (s, sz)][0]
            put(k["a_landing"] / 4000.0, (k["fin_te"] + k["foot_h"] / 2, yf, sz * k["fin_hh"]), "foot", side=s,
                st=st, fin=True)
    for st, (s, sz) in STATIONS.items():
        y, z = s * k["st_y"], sz * k["st_z"]
        put(k["motor_m"], (k["x_mount"] - k["tube_od"] / 2 - k["motor_len"] / 2, y, z), "rotor", side=s, st=st, fin=True)
        put(k["prop_m"] + k["adapter_m"], (k["x_prop"], y, z), "rotor", side=s, st=st, fin=True, transport=False)
        put(k["mount_m"], (k["x_mount"] - 0.005, y, z), "mount", side=s, st=st, fin=True)
        put(k["esc_m"], (k["tube_x"] + 0.04, y, 0.6 * z), "esc", side=s, st=st, fin=True)
    L, Wd, H = k["pod_size"]
    pod_c = (k["pod_xle"] + L / 2, 0.0, k["pod_zb"] + H / 2)
    put(k["a_pod"] / 1000.0, pod_c, "centre")
    put(k["batt_m"], (k["pack_x"], 0.0, k["pod_zb"] + 0.003 + k["batt_size"][2] / 2), "pack", transport=False)
    put(k["a_power"] / 1000.0 - k["batt_m"], (k["pod_xle"] + 0.08, 0.0, 0.03), "centre")
    put(k["a_avionics"] / 1000.0, (k["pod_xle"] + 0.14, 0.0, 0.035), "centre")
    put(k["a_harness"] / 1000.0, pod_c, "centre")
    tot = sum(i["m"] for i in it)
    if growth == "centre":
        put(k["m_gate"] - tot, pod_c, "centre")
    else:
        f = k["m_gate"] / tot
        for i in it:
            i["m"] *= f
    return it


def mass_props(items):
    m = sum(i["m"] for i in items)
    cg = mul((sum(i["m"] * i["r"][0] for i in items), sum(i["m"] * i["r"][1] for i in items),
              sum(i["m"] * i["r"][2] for i in items)), 1.0 / m)
    I = [[0.0] * 3 for _ in range(3)]
    for i in items:
        d = sub(i["r"], cg)
        mm = i["m"]
        I[0][0] += mm * (d[1] ** 2 + d[2] ** 2)
        I[1][1] += mm * (d[0] ** 2 + d[2] ** 2)
        I[2][2] += mm * (d[0] ** 2 + d[1] ** 2)
        I[0][1] -= mm * d[0] * d[1]
        I[0][2] -= mm * d[0] * d[2]
        I[1][2] -= mm * d[1] * d[2]
    I[1][0], I[2][0], I[2][1] = I[0][1], I[0][2], I[1][2]
    return m, cg, I


def m_eff(m, cg, I, r, n):
    """Effective mass of a rigid body at contact point r for a force along unit n."""
    rn = cross(sub(r, cg), n)
    w = solve3(I, rn)
    return 1.0 / (1.0 / m + dot(rn, w))


# ====================================================================== rigid-body solve and cuts


def load(r, F=ZERO, M=ZERO, grp="ext", side=None, st=None, fin=False, kind=""):
    if side is None:
        side = 0 if abs(r[1]) < 1e-12 else (1 if r[1] > 0 else -1)
    return {"r": r, "F": F, "M": M, "grp": grp, "side": side, "st": st, "fin": fin, "kind": kind}


def solve(items, loads, gb):
    """Quasi-static rigid-body accelerations and the list of point loads (applied + gravity + inertia)."""
    m, cg, I = mass_props(items)
    F = mul(gb, m)
    M = ZERO
    for ld in loads:
        F = add(F, ld["F"])
        M = add(M, add(cross(sub(ld["r"], cg), ld["F"]), ld["M"]))
    a = mul(F, 1.0 / m)
    alpha = solve3(I, M)
    pts = []
    for it in items:
        acc = add(a, cross(alpha, sub(it["r"], cg)))
        f = mul(sub(gb, acc), it["m"])
        pts.append({"r": it["r"], "F": f, "M": ZERO, "grp": it["grp"], "side": it["side"], "st": it["st"],
                    "fin": it["fin"]})
    for ld in loads:
        pts.append(ld)
    return pts, {"m": m, "cg": cg, "a": a, "alpha": alpha}


def resultant(pts, P0):
    F, M = ZERO, ZERO
    for p in pts:
        F = add(F, p["F"])
        M = add(M, add(cross(sub(p["r"], P0), p["F"]), p["M"]))
    return F + M


def sweep(pts, key, cuts, ref):
    """Cut loads for the parts with key(p) > cut, for each cut; ref(cut) -> reference point."""
    vals = sorted(((key(p), p) for p in pts if key(p) is not None), key=lambda t: -t[0])
    out = []
    F, RF = ZERO, ZERO
    j = 0
    for cval in sorted(cuts, reverse=True):
        while j < len(vals) and vals[j][0] > cval:
            p = vals[j][1]
            F = add(F, p["F"])
            RF = add(RF, add(cross(p["r"], p["F"]), p["M"]))
            j += 1
        P0 = ref(cval)
        out.append((cval, F + sub(RF, cross(P0, F))))
    out.sort(key=lambda t: t[0])
    return out


# ====================================================================== aero and rotor helpers


def strips(k, dy_target=0.005):
    n = max(2, int(round(k["b"] / dy_target)))
    dy = k["b"] / n
    ys = [-k["b"] / 2 + (i + 0.5) * dy for i in range(n)]
    return ys, dy, [1.0 / n] * n


def _interp(x, xs, fs):
    if x <= xs[0]:
        return fs[0]
    if x >= xs[-1]:
        return fs[-1]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
            return fs[i - 1] + t * (fs[i] - fs[i - 1])
    return fs[-1]


def span_shape(ys, table):
    """Lift weight per strip (sums to 1) and section cm c/4 per strip from B2's strip table [y, cl/CL, cm]."""
    yt = [r[0] for r in table]
    r = [_interp(abs(y), yt, [t[1] for t in table]) for y in ys]
    cm = [_interp(abs(y), yt, [t[2] for t in table]) for y in ys]
    s = sum(r)
    return [x / s for x in r], cm


def flap_increments(el_f):
    """Thin-airfoil plain-flap increments per radian: dCl, dCm_c/4, centre of the increment (fraction of chord)."""
    th = math.acos(2 * el_f - 1)
    dcl = 2 * (math.pi - th + math.sin(th))
    dcm = -0.5 * math.sin(th) * (1 - math.cos(th))
    return dcl, dcm, 0.25 - dcm / dcl


def wing_aero(k, cg, L, D, q, span, elevon=None, el_eff=0.606, dy_target=0.005):
    """Spanwise strips: lift L (N, +z) on B2's AVL shape at c/4 with B2's section cm, drag D (+x) on the same shape;
    optional elevon deltas {side: rad}. trim_lift() then moves the lift chordwise so the aircraft is in pitch trim."""
    ys, dy, _ = strips(k, dy_target)
    w, cms = span_shape(ys, span)
    c = k["c"]
    out = []
    for y, wi, cm in zip(ys, w, cms):
        out.append(load((0.25 * c, y, 0.0), (D * wi, 0.0, L * wi), (0.0, q * c * c * cm * dy, 0.0), grp="wing",
                        kind="lift"))
    if elevon:
        dcl, dcm, xf = flap_increments(k["el_f"])
        for y in ys:
            ay = abs(y)
            if (k["el_in"][0] <= ay <= k["el_in"][1]) or (k["el_out"][0] <= ay <= k["el_out"][1]):
                d = elevon[1 if y > 0 else -1]
                out.append(load((xf * c, y, 0.0), (0.0, 0.0, q * c * dcl * el_eff * d * dy), ZERO, grp="wing",
                                kind="elevon"))
    return out


def trim_lift(loads, cg, xlim):
    """Shift the 'lift' strips chordwise so the pitching moment about the CG is zero (elevon trim)."""
    My, L = 0.0, 0.0
    for ld in loads:
        My += cross(sub(ld["r"], cg), ld["F"])[1] + ld["M"][1]
        if ld["kind"] == "lift":
            L += ld["F"][2]
    if abs(L) < 1e-9:
        return loads
    dx = My / L
    for ld in loads:
        if ld["kind"] == "lift":
            x = min(max(ld["r"][0] + dx, xlim[0]), xlim[1])
            ld["r"] = (x, ld["r"][1], ld["r"][2])
    return loads


def rotor_loads(k, R, thrust, q_body=ZERO):
    out = []
    for st, T in thrust.items():
        s, sz = STATIONS[st]
        frac = max(T, 0.0) / R["T_lim"]
        h = SPIN[st] * R["I_rot"] * R["omega"] * math.sqrt(frac)
        Hv = (h, 0.0, 0.0)
        Mg = mul(cross(q_body, Hv), -1.0)               # d'Alembert gyroscopic moment on the rotor
        M = add((-SPIN[st] * R["Q"] * frac, 0.0, 0.0), Mg)
        out.append(load((k["x_prop"], s * k["st_y"], sz * k["st_z"]), (-T, 0.0, 0.0), M, grp="rotor", side=s,
                        st=st, fin=True, kind="thrust"))
    return out


def trim_split(k, cg, T_tot, other, T_lim):
    """Upper/lower thrust split (per pair) that zeros the pitching moment about the CG."""
    My_o = sum(cross(sub(ld["r"], cg), ld["F"])[1] + ld["M"][1] for ld in other)
    zu, zl = k["st_z"] - cg[2], -k["st_z"] - cg[2]
    TU = (zl * T_tot - My_o) / (zl - zu)
    TU = min(max(TU, 0.0), 2 * T_lim)
    TL = min(max(T_tot - TU, 0.0), 2 * T_lim)
    return {"UR": TU / 2, "UL": TU / 2, "LR": TL / 2, "LL": TL / 2}


# ====================================================================== the small calculations


def _vn(g, rho, m, b, c, clmax, clmin, a, nlim, nneg, Vc, ude_c, ude_d_frac, Vd):
    S = b * c
    W = m * g
    ws = W / S
    mu = 2 * ws / (rho * c * a * g)
    kg = 0.88 * mu / (5.3 + mu)
    Vs = math.sqrt(2 * W / (rho * S * clmax))
    Vsn = math.sqrt(2 * W / (rho * S * clmin))

    def ude(V):
        if V <= Vc:
            return ude_c
        return ude_c + (ude_c * ude_d_frac - ude_c) * (V - Vc) / (Vd - Vc)

    def dn(V):
        return kg * rho * ude(V) * V * a / (2 * ws)

    npk, vpk, nng, vng = -1e9, 0.0, 1e9, 0.0
    N = 400
    for i in range(N + 1):
        V = Vs * 0.5 + (Vd - Vs * 0.5) * i / N
        npos = min((V / Vs) ** 2, 1 + dn(V))
        nn = max(-(V / Vsn) ** 2, 1 - dn(V))
        if npos > npk:
            npk, vpk = npos, V
        if nn < nng:
            nng, vng = nn, V
    return {"S": S, "a3d": a, "mu": mu, "kg": kg, "Vs": Vs, "VA": Vs * math.sqrt(nlim),
            "Vs_neg": Vsn, "VG": Vsn * math.sqrt(abs(nneg)), "n_stall_VD": (Vd / Vs) ** 2,
            "dn_gust_VC": dn(Vc), "n_gust_pos": npk, "V_gust_pos": vpk, "n_gust_neg": nng, "V_gust_neg": vng,
            "n_design_pos": max(nlim, npk), "n_design_neg": min(nneg, nng)}


@kit.calc("CALC-C1-ROTOR", title="Rotor limit loads per motor and design dive speed",
          equation="T_cap = kT_E1 T_h (rpm_cap/rpm_h)^2 ; T_ilim = t_ilim g ; T_lim = max(T_req, T_cap) ; "
                   "rpm_lim = rpm_h sqrt(T_lim / (kT_E1 T_h)) ; Q = kP_E1 Q_h (rpm_lim/rpm_h)^2 ; "
                   "H = (m_p D^2/12 + I_bell) omega ; M_gyro = H q_max ; V_pitch = p rpm_cap/60 ; "
                   "VH = max(V_pitch, VH_B1) ; VD = f_D max(Vc, VH) ; n_hover = n T_lim / (m g)",
          inputs={"T_h": "CL-B4-HOVER-T", "rpm_h": "CL-B4-HOVER-RPM", "Q_h": "CL-B4-HOVER-Q", "kT": "CL-E1-KT",
                  "kP": "CL-E1-KP", "rpm_cap": P + "propulsion.rpm_max", "T_req": P + "requirements.thrust_limit_per_motor_n",
                  "t_ilim": P + "propulsion.thrust_max_per_motor_kg", "g": P + "env.g_ms2",
                  "m_p": P + "propulsion.prop_mass_kg", "D": P + "propulsion.prop_diameter_m",
                  "I_bell": "ASM-C1-BELL-INERTIA", "q_max": "ASM-C1-PITCH-RATE", "pitch": "ASM-C1-PROP-PITCH",
                  "Vc": P + "performance.cruise_ms", "VH_b1": "CL-B1-VMAX", "fD": "ASM-C1-VD-FACTOR",
                  "m": P + "requirements.mtow_gate_kg", "n_mot": P + "propulsion.n_motors"},
          units={"T_h": "N", "rpm_h": "rpm", "Q_h": "N*m", "rpm_cap": "rpm", "T_req": "N", "t_ilim": "kg", "g": "m/s2",
                 "m_p": "kg", "D": "m", "Vc": "m/s", "VH_b1": "m/s", "m": "kg"},
          assumes=["ASM-C1-PROP-PITCH", "ASM-C1-VD-FACTOR", "ASM-C1-PITCH-RATE"], cites=["SRC-C1-FAR23"])
def rotor_calc(T_h, rpm_h, Q_h, kT, kP, rpm_cap, T_req, t_ilim, g, m_p, D, I_bell, q_max, pitch, Vc, VH_b1, fD, m,
               n_mot):
    T_cap = kT * T_h * (rpm_cap / rpm_h) ** 2
    T_lim = max(T_req, T_cap)
    rpm = rpm_h * math.sqrt(T_lim / (kT * T_h))
    omega = rpm * 2 * math.pi / 60
    Q = kP * Q_h * (rpm / rpm_h) ** 2
    I_rot = m_p * D * D / 12 + I_bell
    v_pitch = pitch * rpm_cap / 60
    VH = max(v_pitch, VH_b1)
    Vd = fD * max(Vc, VH)
    return {"T_cap_N": T_cap, "T_ilim_N": t_ilim * g, "T_lim_N": T_lim, "rpm": rpm, "omega": omega, "Q_Nm": Q,
            "I_rot": I_rot, "H_Nms": I_rot * omega, "M_gyro_Nm": I_rot * omega * q_max, "V_pitch_ms": v_pitch,
            "VH_ms": VH, "VD_ms": Vd, "n_hover_max": n_mot * T_lim / (m * g)}


@kit.calc("CALC-C1-VN", title="V-n diagram: manoeuvre and gust envelope",
          equation="Vs = sqrt(2W/(rho S CLmax)); VA = Vs sqrt(n+); a = CL_alpha (B2 AVL); mu = 2(W/S)/(rho c a g); "
                   "kg = 0.88mu/(5.3+mu); dn = kg rho U V a / (2 W/S); n_gust = min(stall line, 1 +/- dn), U = Ude_C to VC "
                   "then linear to f Ude_C at VD; VD = max(VD_req, VD_C1); design n = max(requirement, gust)",
          inputs={"g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "m": P + "requirements.mtow_gate_kg",
                  "b": P + "wing.span_m", "c": P + "wing.chord_m", "clmax": "CL-B2-CLMAX-DESIGN", "clmin": "ASM-C1-CLMIN",
                  "a": "CL-B2-CLA-3D", "nlim": P + "requirements.load_factor_limit_pos",
                  "nneg": P + "requirements.load_factor_limit_neg", "Vc": P + "performance.cruise_ms",
                  "ude_c": P + "requirements.gust_survive_ms", "ude_d_frac": "ASM-C1-UDE-D-FRAC",
                  "Vd_req": P + "requirements.vd_ms", "Vd_c1": "CL-C1-VD"},
          units={"g": "m/s2", "rho": "kg/m3", "m": "kg", "b": "m", "c": "m", "a": "1/rad", "Vc": "m/s", "ude_c": "m/s",
                 "Vd_req": "m/s", "Vd_c1": "m/s"},
          assumes=["ASM-C1-CLMIN", "ASM-C1-UDE-D-FRAC"], cites=["SRC-C1-FAR23", "SRC-C1-PRATT"])
def vn_calc(g, rho, m, b, c, clmax, clmin, a, nlim, nneg, Vc, ude_c, ude_d_frac, Vd_req, Vd_c1):
    Vd = max(Vd_req, Vd_c1)
    out = _vn(g, rho, m, b, c, clmax, clmin, a, nlim, nneg, Vc, ude_c, ude_d_frac, Vd)
    out["VD_env"] = Vd
    out["q_VD_Pa"] = 0.5 * rho * Vd * Vd
    return out


@kit.calc("CALC-C1-LANDING", title="Landing, wingtip strike, tip-over and stance-in-wind loads",
          equation="n_L = v^2/(2 g eta s) + 1 - L/W at s = s_min (requirement) and s = foot height (bound) ; "
                   "s_req = v^2 / (2 g eta (n_target - 1 + L/W)) ; "
                   "F_foot = m_eff v^2/(2 eta s) + (1 - L/W) W/4 with m_eff = 1/(1/m + (r x n).I^-1.(r x n)) ; "
                   "wingtip strike roll = atan(foot / (b/2 - y_fin)) ; foot_req = (b/2 - y_fin) tan(attitude) ; "
                   "tip-over: KE = m g r (1 - cos(phi0 + theta_c)) ; F = KE / (eta s) ; stance wind: q S CD h = W d",
          inputs={**MODEL, "v": P + "requirements.landing_sink_ms", "eta": "ASM-C1-CRUSH-EFF", "lw": "ASM-C1-LAND-LIFT",
                  "n_t": P + "requirements.landing_n_design", "att": P + "requirements.landing_attitude_err_deg",
                  "s_min": P + "requirements.foot_crush_stroke_min_m", "s_c": "ASM-C1-CONTACT-STROKE",
                  "cdp": "ASM-C1-CD-PLATE", "v_gust": P + "requirements.gust_survive_ms",
                  "x_cg_t": P + "cg.x_target_m", "mu": "ASM-C1-FRICTION"},
          units={**MODEL_UNITS, "v": "m/s", "att": "deg", "s_min": "m", "s_c": "m", "v_gust": "m/s", "x_cg_t": "m"},
          assumes=["ASM-C1-CRUSH-EFF", "ASM-C1-LAND-LIFT", "ASM-C1-CONTACT-STROKE"],
          cites=["SRC-C1-FAR23"])
def landing_calc(v, eta, lw, n_t, att, s_min, s_c, cdp, v_gust, x_cg_t, mu, **k):
    return _landing(k, v, eta, lw, n_t, att, s_min, s_c, cdp, v_gust, x_cg_t, mu)


def _landing(k, v, eta, lw, n_t, att, s_min, s_c, cdp, v_gust, x_cg_t, mu, growth="centre"):
    g = k["g"]
    items = build_items(k, growth)
    m, cg, I = mass_props(items)
    W = m * g
    n_smin = v * v / (2 * g * eta * s_min) + 1 - lw
    n_foot = v * v / (2 * g * eta * k["foot_h"]) + 1 - lw
    s_req = v * v / (2 * g * eta * (n_t - 1 + lw))
    xg = k["fin_te"] + k["foot_h"]                          # ground plane in the stance (x)
    nrm = (-1.0, 0.0, 0.0)
    feet = {st: (xg, s * k["fin_y"], sz * k["fin_hh"]) for st, (s, sz) in STATIONS.items()}
    me_level = m / 4
    me_pair_n = m_eff(m, cg, I, (xg, 0.0, k["fin_hh"]), nrm) / 2      # upper pair (narrow axis)
    me_pair_w = m_eff(m, cg, I, (xg, k["fin_y"], 0.0), nrm) / 2       # right pair (wide axis)
    me_corner = m_eff(m, cg, I, feet["UR"], nrm)
    kin = v * v / (2 * eta * s_req)
    grav = (1 - lw) * W / 4
    f = {"level": me_level * kin + grav, "pair_narrow": me_pair_n * kin + grav,
         "pair_wide": me_pair_w * kin + grav, "corner": me_corner * kin + grav}
    f_smin = me_level * v * v / (2 * eta * s_min) + grav
    out_tip = k["b"] / 2 - k["fin_y"]
    tip_angle = math.degrees(math.atan(k["foot_h"] / out_tip))
    foot_req = out_tip * math.tan(math.radians(att))
    tip_req = math.degrees(math.atan(k["fin_hh"] / (k["c"] - x_cg_t + foot_req)))
    me_tip = m_eff(m, cg, I, (k["c"], k["b"] / 2, 0.0), nrm)
    F_tip = 0.5 * me_tip * v * v / (eta * s_c)
    # tip-over about the narrow-axis foot line onto the upper motor-tube ends
    hx, dzc = xg - cg[0], cg[2] - k["fin_hh"]
    r = math.hypot(hx, dzc)
    phi0 = math.atan2(dzc, hx)
    dxc, dzt = xg - k["tube_x"], k["tube_len"] / 2 - k["fin_hh"]
    th_c = math.atan2(dxc, dzt) if dzt > 0 else math.pi / 2
    KE = W * r * (1 - math.cos(phi0 + th_c))
    Ip = I[1][1] + m * r * r
    r_c = math.hypot(dxc, dzt)
    omega = math.sqrt(2 * KE / Ip)
    F_tipover = KE / (eta * s_c)
    # stance in wind, motors off: wing broadside along z, narrow axis
    qg = 0.5 * k["rho"] * v_gust ** 2
    Sw = k["b"] * k["c"]
    Dw = qg * Sw * cdp
    h_d = xg - k["c"] / 2
    d_rest = k["fin_hh"] - abs(cg[2])
    v_tip = math.sqrt(2 * W * d_rest / (h_d * k["rho"] * Sw * cdp))
    return {"m_kg": m, "W_N": W, "n_L_stroke_min": n_smin, "n_L_full_foot": n_foot, "F_foot_stroke_min_N": f_smin,
            "stroke_req_m": s_req,
            "F_foot_level_N": f["level"], "F_foot_pair_narrow_N": f["pair_narrow"],
            "F_foot_pair_wide_N": f["pair_wide"], "F_foot_corner_N": f["corner"],
            "F_foot_max_N": max(f.values()), "F_side_max_N": mu * max(f.values()),
            "m_eff_corner_kg": me_corner, "wingtip_strike_deg": tip_angle, "foot_protrusion_req_m": foot_req,
            "tipover_deg_with_req_foot": tip_req, "m_eff_wingtip_kg": me_tip, "F_wingtip_N": F_tip,
            "tipover_theta_contact_deg": math.degrees(th_c), "tipover_KE_J": KE, "tipover_v_contact_ms": omega * r_c,
            "F_tipover_total_N": F_tipover, "stance_drag_8ms_N": Dw, "stance_tip_wind_ms": v_tip,
            "stance_mu_req_8ms": Dw / W, "n_L_design": n_t}


@kit.calc("CALC-C1-CRASH", title="Crash factor and pack retention load",
          equation="n_c = v^2 / (2 g s) ; F_pack = m_pack_max n_c g (ultimate, emergency)",
          inputs={"v": "ASM-C1-CRASH-V", "s": "ASM-C1-CRASH-STROKE", "g": P + "env.g_ms2",
                  "pack": "ASM-A3-PACK-RANGE", "fc": P + "mass.allocation_g.avionics"},
          units={"v": "m/s", "s": "m", "g": "m/s2", "pack": "g", "fc": "g"}, cites=["SRC-C1-FAR23"])
def crash_calc(v, s, g, pack, fc):
    n = v * v / (2 * g * s)
    return {"n_crash": n, "F_pack_N": max(pack) / 1000.0 * n * g, "F_avionics_N": fc / 1000.0 * n * g}


@kit.calc("CALC-C1-TRANSPORT-N", title="Box drop load factor",
          equation="n_T = 1 + h / (eta s)",
          inputs={"h": P + "requirements.box_drop_m", "eta": "ASM-C1-CRUSH-EFF", "s": "ASM-C1-CRADLE-STROKE"},
          units={"h": "m", "s": "m"})
def transport_n_calc(h, eta, s):
    return {"n_T": 1 + h / (eta * s), "v_impact_ms": math.sqrt(2 * 9.80665 * h)}


# ====================================================================== load cases


def build_cases(k, X, items, growth, dy=0.005):
    """Every load case for one mass configuration. X holds the derived scalars (n, V, rotor, landing)."""
    g = k["g"]
    m, cg, I = mass_props(items)
    W = m * g
    S = k["b"] * k["c"]
    AR = k["b"] ** 2 / S
    R = X["rotor"]
    T_lim = R["T_lim_N"]
    Rr = {"T_lim": T_lim, "Q": R["Q_Nm"], "I_rot": R["I_rot"], "omega": R["omega"]}
    q_max = X["q_max"]
    cl_c = W / (0.5 * k["rho"] * X["Vc"] ** 2 * S)
    cd0 = cl_c / X["ld"] - cl_c ** 2 / (math.pi * X["e"] * AR)
    xlim = (0.0, k["c"])
    cases = []

    def drag(V, L):
        qq = 0.5 * k["rho"] * V * V
        cl = L / (qq * S)
        return qq * S * (cd0 + cl * cl / (math.pi * X["e"] * AR))

    def flight(cid, title, n, V, elevon=None):
        qq = 0.5 * k["rho"] * V * V
        L = n * W
        D = drag(V, L)
        lds = wing_aero(k, cg, L, D, qq, X["span"], elevon, X["el_eff"], dy)
        lds += rotor_loads(k, Rr, {st: D / 4 for st in STATIONS})
        trim_lift(lds, cg, xlim)
        cases.append({"id": cid, "family": "flight", "title": title, "gb": (0.0, 0.0, -g), "loads": lds,
                      "info": {"n": n, "V_ms": V, "L_N": L, "D_N": D}})

    nP, nN = X["n_pos"], X["n_neg"]
    flight("F1-PULLUP-VD", "Symmetric pull-up, n+ at VD", nP, X["VD"])
    flight("F2-PULLUP-VA", "Symmetric pull-up, n+ at VA", nP, X["VA"])
    flight("F3-PUSH-VD", "Symmetric push-over, n- at VD", nN, X["VD"])
    flight("F4-GUST-POS", "Vertical gust, peak positive n", X["n_gust_pos"], X["V_gust_pos"])
    flight("F5-GUST-NEG", "Vertical gust, peak negative n", X["n_gust_neg"], X["V_gust_neg"])
    dl = math.radians(X["el_def"])
    flight("F6-ROLL-VD", "Full roll elevon at VD, n = 1", 1.0, X["VD"], {1: dl, -1: -dl})
    flight("F7-ROLLPULL-VD", "Rolling pull-up, 2/3 n+ with full roll elevon", 2.0 / 3.0 * nP, X["VD"], {1: dl, -1: -dl})
    flight("F8-CRUISE", "Cruise 1 g at VC (reference, deflection)", 1.0, X["Vc"])

    hov = (g, 0.0, 0.0)

    def hover(cid, title, thrust, gb=hov, extra=(), q_body=ZERO, info=None):
        lds = list(extra) + rotor_loads(k, Rr, thrust, q_body)
        cases.append({"id": cid, "family": "hover", "title": title, "gb": gb, "loads": lds, "info": info or {}})

    hover("H1-HOVER", "Hover 1 g, pitch-trimmed split", trim_split(k, cg, W, [], T_lim), info={"T_tot_N": W})
    hover("H2-MAX-THRUST", "All four motors at T_lim", {st: T_lim for st in STATIONS}, info={"T_tot_N": 4 * T_lim})
    hover("H3-PITCH-UPPER", "Upper pair T_lim, lower pair off (+ gyro)", {"UR": T_lim, "UL": T_lim, "LR": 0, "LL": 0},
          q_body=(0.0, -q_max, 0.0))
    hover("H4-PITCH-LOWER", "Lower pair T_lim, upper pair off (+ gyro)", {"UR": 0, "UL": 0, "LR": T_lim, "LL": T_lim},
          q_body=(0.0, q_max, 0.0))
    hover("H5-SIDE-RIGHT", "Right pair T_lim, left pair off", {"UR": T_lim, "LR": T_lim, "UL": 0, "LL": 0},
          q_body=(0.0, 0.0, q_max))
    hover("H6-DIAG-A", "Diagonal UR+LL at T_lim, others off (yaw)", {"UR": T_lim, "LL": T_lim, "UL": 0, "LR": 0},
          q_body=(q_max, 0.0, 0.0))
    hover("H7-DIAG-B", "Diagonal UL+LR at T_lim, others off (yaw)", {"UL": T_lim, "LR": T_lim, "UR": 0, "LL": 0},
          q_body=(-q_max, 0.0, 0.0))
    # hover in the 8 m/s gust: broadside on the wing (z) and on the fins (y)
    qg = 0.5 * k["rho"] * X["v_gust"] ** 2
    ys, _, _ = strips(k, dy)
    Nw = qg * S * X["cdp"]
    wind_w = [load((k["c"] / 2, y, 0.0), (0.0, 0.0, -Nw / len(ys)), grp="wing", kind="wind") for y in ys]
    th = math.asin(min(1.0, Nw / W))
    gb = (g * math.cos(th), 0.0, g * math.sin(th))
    hover("H8-GUST-WING", "Hover, 8 m/s gust broadside on the wing", trim_split(k, cg, W * math.cos(th), wind_w, T_lim),
          gb=gb, extra=wind_w, info={"N_N": Nw, "lean_deg": math.degrees(th)})
    board = [it for it in items if it["grp"] == "board"]
    Af = 2 * (k["fin_te"] - k["fin_le"]) * 2 * k["fin_hh"]
    Nf = qg * Af * X["cdp"]
    wind_f = [load(it["r"], (0.0, -Nf / len(board), 0.0), grp="board", side=it["side"], fin=True, kind="wind")
              for it in board]
    th = math.asin(min(1.0, Nf / W))
    gb = (g * math.cos(th), g * math.sin(th), 0.0)
    hover("H9-GUST-FINS", "Hover, 8 m/s gust broadside on the fins", trim_split(k, cg, W * math.cos(th), wind_f, T_lim),
          gb=gb, extra=wind_f, info={"N_N": Nf, "lean_deg": math.degrees(th)})

    def trans(cid, title, theta_deg, V, thrust, q_body, trim):
        th = math.radians(theta_deg)
        qq = 0.5 * k["rho"] * V * V
        L = qq * S * X["clmax"]
        D = drag(V, L)
        lds = wing_aero(k, cg, L, D, qq, X["span"], dy_target=dy)
        lds += rotor_loads(k, Rr, thrust, q_body)
        if trim:
            trim_lift(lds, cg, xlim)
        cases.append({"id": cid, "family": "transition", "title": title,
                      "gb": (g * math.sin(th), 0.0, -g * math.cos(th)), "loads": lds,
                      "info": {"theta_deg": theta_deg, "V_ms": V, "L_N": L, "D_N": D}})

    trans("T1-TRANSITION", "Transition at 45 deg, CLmax at 1.3 Vs, all motors T_lim", 45.0, X["V_tr"],
          {st: T_lim for st in STATIONS}, ZERO, True)
    trans("T2-FLARE-UPPER", "Back-transition flare at 30 deg, CLmax at VC, upper pair T_lim", 30.0, X["Vc"],
          {"UR": T_lim, "UL": T_lim, "LR": 0, "LL": 0}, (0.0, -q_max, 0.0), False)
    trans("T3-FLARE-LOWER", "Back-transition flare at 30 deg, CLmax at VC, lower pair T_lim", 30.0, X["Vc"],
          {"UR": 0, "UL": 0, "LR": T_lim, "LL": T_lim}, (0.0, q_max, 0.0), False)

    LD = X["landing"]
    lift_t = X["lw"] * W

    def land(cid, title, feet_f, gb=hov, family="landing", info=None):
        lds = rotor_loads(k, Rr, {st: lift_t / 4 for st in STATIONS})
        xg = k["fin_te"] + k["foot_h"]
        for st, F in feet_f.items():
            s, sz = STATIONS[st]
            lds.append(load((xg, s * k["fin_y"], sz * k["fin_hh"]), F, grp="foot", side=s, st=st, fin=True,
                            kind="ground"))
        cases.append({"id": cid, "family": family, "title": title, "gb": gb, "loads": lds, "info": info or {}})

    a = math.radians(X["att"])
    Fl, Fn, Fw, Fc, mu = LD["F_foot_level_N"], LD["F_foot_pair_narrow_N"], LD["F_foot_pair_wide_N"], \
        LD["F_foot_corner_N"], X["mu"]
    land("L1-LEVEL", "Level landing on four feet", {st: (-Fl, 0.0, 0.0) for st in STATIONS},
         info={"F_foot_N": Fl})
    land("L2-PAIR-NARROW", "Upper foot pair first, 10 deg pitch error", {"UR": (-Fn, 0.0, 0.0), "UL": (-Fn, 0.0, 0.0)},
         gb=(g * math.cos(a), 0.0, g * math.sin(a)), info={"F_foot_N": Fn})
    land("L3-PAIR-WIDE", "Right foot pair first, 10 deg roll error", {"UR": (-Fw, 0.0, 0.0), "LR": (-Fw, 0.0, 0.0)},
         gb=(g * math.cos(a), g * math.sin(a), 0.0), info={"F_foot_N": Fw})
    land("L4-CORNER-SIDE-Y", "One foot (UR) first + friction across the fin (y)", {"UR": (-Fc, -mu * Fc, 0.0)},
         gb=(g * math.cos(a), g * math.sin(a), 0.0), info={"F_foot_N": Fc})
    land("L5-CORNER-SIDE-Z", "One foot (UR) first + friction along the fin (z)", {"UR": (-Fc, 0.0, -mu * Fc)},
         gb=(g * math.cos(a), 0.0, g * math.sin(a)), info={"F_foot_N": Fc})
    # damage-tolerance cases (reported, not in the sizing envelope)
    lds = rotor_loads(k, Rr, {st: lift_t / 4 for st in STATIONS})
    lds.append(load((k["c"], k["b"] / 2, 0.0), (-LD["F_wingtip_N"], 0.0, 0.0), grp="wing", kind="ground"))
    cases.append({"id": "L6-WINGTIP-STRIKE", "family": "damage", "title": "Wingtip TE strikes first (roll error > strike angle)",
                  "gb": (g * math.cos(a), g * math.sin(a), 0.0), "loads": lds, "info": {"F_N": LD["F_wingtip_N"]}})
    thc = math.radians(LD["tipover_theta_contact_deg"])
    nrm = (-math.cos(thc), 0.0, -math.sin(thc))
    Ft = LD["F_tipover_total_N"] / 2
    lds = [load((k["tube_x"], s * k["fin_y"], k["tube_len"] / 2), mul(nrm, Ft), grp="tube", side=s, fin=True,
                st=("UR" if s > 0 else "UL"), kind="ground") for s in (1, -1)]
    cases.append({"id": "L7-TIPOVER", "family": "damage", "title": "Tip-over onto the upper motor-tube ends",
                  "gb": (g * math.cos(thc), 0.0, g * math.sin(thc)), "loads": lds,
                  "info": {"F_total_N": 2 * Ft, "theta_deg": math.degrees(thc)}})

    nh = X["n_h"]
    L_, Wd, H = k["pod_size"]
    pod_c = (k["pod_xle"] + L_ / 2, 0.0, k["pod_zb"] + H / 2)
    cases.append({"id": "G1-POD-LIFT", "family": "ground", "title": "Lifted by the pod, handling factor",
                  "gb": (0.0, 0.0, -g), "loads": [load(pod_c, (0.0, 0.0, nh * W), grp="centre", kind="hand")],
                  "info": {"n": nh}})
    hand = (k["tube_x"], k["fin_y"], k["tube_len"] / 2)
    gdir = unit(sub(cg, hand))
    cases.append({"id": "G2-HANG-MOTOR", "family": "ground", "title": "Carried by one upper motor tube end (UR)",
                  "gb": mul(gdir, g), "loads": [load(hand, mul(gdir, -nh * W), grp="tube", side=1, fin=True, st="UR",
                                                     kind="hand")], "info": {"n": nh}})
    # set down flat (lower surface down): the lowest points are the lower motor cans (z -0.19), the lower tube
    # ends (z -0.21) and the lower feet (z -0.19). The pair of contacts that brackets the CG in x carries it.
    xm = k["x_mount"] - k["tube_od"] / 2 - k["motor_len"]
    xt, xf = k["tube_x"], k["fin_te"] + k["foot_h"]
    if cg[0] < xt:
        (xa, za, ga), (xb, zb, gb_) = (xm, -k["st_z"], "rotor"), (xt, -k["tube_len"] / 2, "tube")
    else:
        (xa, za, ga), (xb, zb, gb_) = (xt, -k["tube_len"] / 2, "tube"), (xf, -k["fin_hh"], "foot")
    Ra = nh * W * (xb - cg[0]) / (xb - xa) / 2
    Rb = nh * W / 2 - Ra
    sup = []
    for s in (1, -1):
        st = "LR" if s > 0 else "LL"
        sup.append(load((xa, s * k["fin_y"], za), (0.0, 0.0, Ra), grp=ga, side=s, fin=True, st=st, kind="ground"))
        sup.append(load((xb, s * k["fin_y"], zb), (0.0, 0.0, Rb), grp=gb_, side=s, fin=True, st=st, kind="ground"))
    cases.append({"id": "G3-BENCH", "family": "ground", "title": "Set down flat on the lower motors / tube ends / feet",
                  "gb": (0.0, 0.0, -g), "loads": sup,
                  "info": {"n": nh, "support_a": ga, "R_a_N": Ra, "support_b": gb_, "R_b_N": Rb}})

    nT = X["n_T"]
    W_T = sum(i["m"] for i in items if i["transport"]) * g
    for ax, name in ((0, "X"), (1, "Y"), (2, "Z")):
        e = [0.0, 0.0, 0.0]
        e[ax] = 1.0
        e = tuple(e)
        lds = [load((k["x_spar"], s * X["y_cr"], 0.0), mul(e, nT * W_T / 2), grp="wing", kind="cradle") for s in (1, -1)]
        cases.append({"id": f"X{ax + 1}-DROP-{name}", "family": "transport",
                      "title": f"Box drop, n_T along {name.lower()}, reacted at the spar cradles",
                      "gb": mul(e, -g), "loads": lds, "info": {"n_T": nT, "m_transport_kg": W_T / g}})
    return cases


ENVELOPE_FAMILIES = ("flight", "hover", "transition", "landing", "ground")


def joint_defs(k, items):
    """Named cuts: (id, structure, predicate on a point load, reference point, member axis for bending)."""
    L_, Wd, H = k["pod_size"]
    pod_c = (k["pod_xle"] + L_ / 2, 0.0, k["pod_zb"])
    pack = [i for i in items if i["grp"] == "pack"][0]
    J = []
    for s, sn in ((1, "R"), (-1, "L")):
        J.append((f"J-FIN-{sn}", "fin group to wing (saddle + fin root)",
                  lambda p, s=s: p["fin"] and p["side"] == s, (k["x_spar"], s * k["fin_y"], 0.0), None))
    for st, (s, sz) in STATIONS.items():
        y, z = s * k["st_y"], sz * k["st_z"]
        J.append((f"J-FINHALF-{st}", "fin + tube section at the wing plane",
                  lambda p, s=s, sz=sz: p["fin"] and p["side"] == s and p["r"][2] * sz > 1e-9,
                  (k["tube_x"], s * k["fin_y"], 0.0), "z"))
        J.append((f"J-MOTOR-{st}", "motor to mount (mount face)",
                  lambda p, st=st: p["grp"] == "rotor" and p["st"] == st, (k["x_mount"], y, z), "x"))
        J.append((f"J-MOUNT-{st}", "mount to tube (tube axis)",
                  lambda p, st=st: p["grp"] in ("rotor", "mount") and p["st"] == st, (k["tube_x"], y, z), "z"))
        J.append((f"J-FOOT-{st}", "foot to fin TE tip",
                  lambda p, st=st: p["grp"] == "foot" and p["st"] == st, (k["fin_te"], y, sz * k["fin_hh"]), None))
    J.append(("J-POD", "pod group to wing (bond + strap)", lambda p: p["grp"] in ("centre", "pack"), pod_c, None))
    J.append(("J-PACK", "pack to tray (strap)", lambda p: p["grp"] == "pack", pack["r"], None))
    J.append(("J-SPAR-ROOT", "spar at the centreline (right half)", lambda p: p["r"][1] > 1e-9,
              (k["x_spar"], 0.0, 0.0), "y"))
    return J


def bend(v, axis):
    M = v[3:]
    if axis == "x":
        return math.hypot(M[1], M[2])
    if axis == "y":
        return math.hypot(M[0], M[2])
    if axis == "z":
        return math.hypot(M[0], M[1])
    return norm(M)


def run_all(k, X, dy=0.005, detail=False):
    """Run every case on both mass configurations; return envelopes (and full tables when detail)."""
    res = {"joints": [], "wing": [], "fin": [], "cases": [], "residual": 0.0}
    ycuts_base = [i * dy for i in range(int(round(k["b"] / 2 / dy)) + 1)]
    for growth, mc in (("centre", "MC-C"), ("prorata", "MC-P")):
        items = build_items(k, growth, dy)
        eps = 1e-6
        extra = [k["fin_y"] - eps, k["fin_y"] + eps, k["el_in"][1] - eps, k["el_in"][1] + eps]
        ycuts = sorted(set(ycuts_base + [e for e in extra if 0 <= e <= k["b"] / 2]))
        zcuts = sorted(set([i * 0.0105 for i in range(21)] + [k["st_z"] - eps, k["st_z"] + eps,
                                                              0.6 * k["st_z"] - eps, 0.6 * k["st_z"] + eps]))
        zcuts = [z for z in zcuts if 0 <= z <= k["tube_len"] / 2]
        J = joint_defs(k, items)
        items_t = [i for i in items if i["transport"]]
        for case in build_cases(k, X, items, growth, dy):
            pts, info = solve(items_t if case["family"] == "transport" else items, case["loads"], case["gb"])
            tot = resultant(pts, info["cg"])
            res["residual"] = max(res["residual"], max(abs(v) for v in tot))
            res["cases"].append({"case": case["id"], "mc": mc, "family": case["family"], "title": case["title"],
                                 "a_ms2": info["a"], "alpha_rads2": info["alpha"], "cg_m": info["cg"],
                                 "gb_ms2": case["gb"], **{kk: vv for kk, vv in case["info"].items()}})
            for jid, struct, pred, P0, axis in J:
                v = resultant([p for p in pts if pred(p)], P0)
                res["joints"].append((case["id"], mc, case["family"], jid, v, bend(v, axis)))
            xs = k["x_spar"]
            for side in (1, -1):
                for yc, v in sweep(pts, lambda p, side=side: p["r"][1] * side, ycuts,
                                   lambda yc, side=side: (xs, side * yc, 0.0)):
                    res["wing"].append((case["id"], mc, case["family"], side * yc if side > 0 else -yc, side, v))
                if True:
                    for sz in (1, -1):
                        for zc, v in sweep(pts, lambda p, side=side, sz=sz: (p["r"][2] * sz) if (p["fin"] and p["side"] == side) else None,
                                           zcuts, lambda zc, side=side, sz=sz: (k["tube_x"], side * k["fin_y"], sz * zc)):
                            res["fin"].append((case["id"], mc, case["family"], side, sz, zc, v))
    return res


def jclass(jid):
    """Fold mirror-image joints into one class (the structure is symmetric left/right and nearly up/down)."""
    for c in ("J-FINHALF", "J-FIN", "J-MOTOR", "J-MOUNT", "J-FOOT"):
        if jid.startswith(c + "-"):
            return c
    return jid


TRANSPORT_KEYS = ("WING:Mb", "WING:My", "J-FIN:F", "J-FIN:M", "J-FINHALF:F", "J-FINHALF:Mb",
                  "J-MOUNT:F", "J-MOUNT:M", "J-MOTOR:F", "J-POD:F", "J-POD:M")


def envelope_scalars(res, fam=ENVELOPE_FAMILIES, skip_cases=()):
    """Peak limit values per joint class and section, with the governing case."""
    out = {}

    def keep(key, val, case):
        if key not in out or val > out[key][0]:
            out[key] = (val, case)

    for case, mc, family, jid, v, mb in res["joints"]:
        if family not in fam or case in skip_cases:
            continue
        jid = jclass(jid)
        keep(jid + ":F", norm(v[:3]), case)
        keep(jid + ":M", norm(v[3:]), case)
        keep(jid + ":Mb", mb, case)
        for i, cname in enumerate(("Fx", "Fy", "Fz", "Mx", "My", "Mz")):
            keep(f"{jid}:{cname}", abs(v[i]), case)
    for case, mc, family, y, side, v in res["wing"]:
        if family not in fam or case in skip_cases:
            continue
        keep("WING:Mb", math.hypot(v[3], v[5]), case)
        keep("WING:Mx", abs(v[3]), case)
        keep("WING:Mz", abs(v[5]), case)
        keep("WING:My", abs(v[4]), case)
        keep("WING:Vz", abs(v[2]), case)
        keep("WING:Vx", abs(v[0]), case)
    for case, mc, family, side, sz, zc, v in res["fin"]:
        if family not in fam or case in skip_cases:
            continue
        keep("FIN:Mb", math.hypot(v[3], v[4]), case)
        keep("FIN:Mz", abs(v[5]), case)
    return out


def derived(k, kx):
    """Scalars the cases need, gathered from the other claims (passed in kx)."""
    return {"rotor": kx["rotor"], "q_max": kx["q_max"], "Vc": kx["Vc"], "ld": kx["ld"], "e": kx["e"],
            "span": kx["span"], "el_eff": kx["el_eff"], "el_def": k["el_def"][1], "n_pos": kx["n_pos"],
            "n_neg": kx["n_neg"], "VD": kx["VD"], "VA": kx["VA"], "n_gust_pos": kx["n_gust_pos"],
            "V_gust_pos": kx["V_gust_pos"], "n_gust_neg": kx["n_gust_neg"], "V_gust_neg": kx["V_gust_neg"],
            "v_gust": kx["v_gust"], "cdp": kx["cdp"], "clmax": kx["clmax"], "V_tr": kx["V_tr"],
            "landing": kx["landing"], "lw": kx["lw"], "att": kx["att"], "mu": kx["mu"], "n_h": kx["n_h"],
            "n_T": kx["n_T"], "y_cr": kx["y_cr"]}


ENV_INPUTS = {
    **MODEL,
    "T_lim": "CL-C1-T-LIMIT", "Q": "CL-C1-MOTOR-TORQUE", "H": "CL-C1-ROTOR-H", "omega_lim": "CL-C1-ROTOR-OMEGA",
    "q_max": "ASM-C1-PITCH-RATE", "Vc": P + "performance.cruise_ms", "ld": P + "performance.ld_cruise",
    "e": P + "wing.oswald_e", "span": "ASM-C1-B2-SPANLOAD", "el_eff": "CL-B2-ELEVON-ETA",
    "n_pos": "CL-C1-N-LIMIT-POS", "n_neg": "CL-C1-N-LIMIT-NEG", "VD": "CL-C1-VD-ENV", "VA": "CL-C1-VA",
    "n_gp": "CL-C1-GUST-N-POS", "V_gp": "CL-C1-GUST-V-POS", "n_gn": "CL-C1-GUST-N-NEG", "V_gn": "CL-C1-GUST-V-NEG",
    "v_gust": P + "requirements.gust_survive_ms", "cdp": "ASM-C1-CD-PLATE", "clmax": "CL-B2-CLMAX-DESIGN",
    "V_tr": "CL-A1-TRANSITION-GATE", "F_lvl": "CL-C1-FOOT-LEVEL", "F_pn": "CL-C1-FOOT-PAIR-NARROW",
    "F_pw": "CL-C1-FOOT-PAIR-WIDE", "F_cor": "CL-C1-FOOT-CORNER", "F_tip": "CL-C1-WINGTIP-FORCE",
    "th_to": "CL-C1-TIPOVER-ANGLE-CONTACT", "F_to": "CL-C1-TIPOVER-FORCE", "lw": "ASM-C1-LAND-LIFT",
    "att": P + "requirements.landing_attitude_err_deg", "mu": "ASM-C1-FRICTION", "n_h": "ASM-C1-HANDLING-N", "n_T": "CL-C1-TRANSPORT-N",
    "y_cr": "ASM-C1-CRADLE-Y", "h_drop": P + "requirements.box_drop_m", "s_cr": "ASM-C1-CRADLE-STROKE",
    "eta": "ASM-C1-CRUSH-EFF", "sf": P + "requirements.safety_factor_ult",
    "kfit": "ASM-C1-FITTING-FACTOR", "kprint": "ASM-C1-PRINTED-FACTOR",
}
ENV_UNITS = {**MODEL_UNITS, "Vc": "m/s", "VD": "m/s", "VA": "m/s", "V_gp": "m/s", "V_gn": "m/s", "v_gust": "m/s",
             "V_tr": "m/s", "att": "deg", "y_cr": "m", "h_drop": "m", "s_cr": "m", "T_lim": "N", "F_lvl": "N", "F_pn": "N",
             "F_pw": "N", "F_cor": "N", "F_tip": "N", "F_to": "N", "th_to": "deg"}


def kit_stroke(kw):
    return kw["s_cr"]


def pack_inputs(kw):
    """Split the flat calc arguments into the model dict k and the derived-scalar dict X."""
    k = {kk: kw[kk] for kk in MODEL_KEYS}
    kx = {
        "rotor": {"T_lim_N": kw["T_lim"], "Q_Nm": kw["Q"], "I_rot": kw["H"] / kw["omega_lim"], "omega": kw["omega_lim"]},
        "q_max": kw["q_max"], "Vc": kw["Vc"], "ld": kw["ld"], "e": kw["e"], "span": kw["span"], "el_eff": kw["el_eff"],
        "n_pos": kw["n_pos"], "n_neg": kw["n_neg"], "VD": kw["VD"], "VA": kw["VA"], "n_gust_pos": kw["n_gp"],
        "V_gust_pos": kw["V_gp"], "n_gust_neg": kw["n_gn"], "V_gust_neg": kw["V_gn"], "v_gust": kw["v_gust"],
        "cdp": kw["cdp"], "clmax": kw["clmax"], "V_tr": kw["V_tr"],
        "landing": {"F_foot_level_N": kw["F_lvl"], "F_foot_pair_narrow_N": kw["F_pn"], "F_foot_pair_wide_N": kw["F_pw"],
                    "F_foot_corner_N": kw["F_cor"], "F_wingtip_N": kw["F_tip"], "tipover_theta_contact_deg": kw["th_to"],
                    "F_tipover_total_N": kw["F_to"]},
        "lw": kw["lw"], "att": kw["att"], "mu": kw["mu"], "n_h": kw["n_h"], "n_T": kw["n_T"], "y_cr": kw["y_cr"],
    }
    return k, derived(k, kx)


@kit.calc("CALC-C1-ENVELOPE", title="Load envelope over every case and both mass configurations",
          equation="per case: a = F/m, alpha = I^-1 M_cg ; cut load = sum over the outboard part of (applied + m (g - a - "
                   "alpha x r)) ; envelope = max over cases F, H, T, L1-L5, G and mass configs MC-C, MC-P ; ultimate = "
                   "SF x limit ; joints x fitting factor ; transport n_allow = n_T x min(envelope / transport) ; "
                   "s_req = h / (eta (n_allow - 1))",
          inputs=ENV_INPUTS, units=ENV_UNITS,
          assumes=["ASM-C1-B2-SPANLOAD", "ASM-C1-CD-PLATE", "ASM-C1-HANDLING-N", "ASM-C1-CRADLE-Y"],
          cites=["SRC-B2-AVL", "SRC-C1-THIN-AIRFOIL", "SRC-C1-FAR23"])
def envelope_calc(**kw):
    k, X = pack_inputs(kw)
    res = run_all(k, X)
    env = envelope_scalars(res)
    trn = envelope_scalars(res, fam=("transport",))
    sf = kw["sf"]
    # transport allowance: every resultant the drop produces must stay inside the other limit cases
    ratios = [(env[key][0] / trn[key][0], key) for key in TRANSPORT_KEYS if trn[key][0] > 1e-9]
    rmin, rkey = min(ratios)
    n_allow = kw["n_T"] * rmin
    s_req = kw["h_drop"] / (kw["eta"] * max(n_allow - 1, 1e-6))
    nog = envelope_scalars(res, fam=("flight", "hover", "transition", "landing"))
    o = {"residual_N": res["residual"]}
    for key, name in (("WING:Mb", "spar_Mb"), ("WING:Mx", "spar_Mx"), ("WING:Mz", "spar_Mz"), ("WING:My", "wing_T"),
                      ("WING:Vz", "wing_Vz"), ("WING:Vx", "wing_Vx"), ("J-FIN:F", "finjoint_F"),
                      ("J-FIN:M", "finjoint_M"), ("FIN:Mb", "finhalf_Mb"), ("FIN:Mz", "finhalf_T"),
                      ("J-MOUNT:F", "mount_F"), ("J-MOUNT:M", "mount_M"), ("J-MOTOR:F", "motor_F"),
                      ("J-MOTOR:M", "motor_M"), ("J-POD:F", "pod_F"), ("J-POD:M", "pod_M"), ("J-PACK:F", "pack_F"),
                      ("J-FOOT:F", "foot_F")):
        v, c = env[key]
        o[name + "_lim"] = v
        o[name + "_ult"] = v * sf
        o[name + "_case"] = c
    o["finjoint_F_design"] = o["finjoint_F_ult"] * kw["kfit"] * kw["kprint"]
    o["finjoint_M_design"] = o["finjoint_M_ult"] * kw["kfit"] * kw["kprint"]
    o["mount_F_design"] = o["mount_F_ult"] * kw["kfit"] * kw["kprint"]
    o["mount_M_design"] = o["mount_M_ult"] * kw["kfit"] * kw["kprint"]
    o["pod_F_design"] = o["pod_F_ult"] * kw["kfit"] * kw["kprint"]
    o["finjoint_M_nohandling_lim"] = nog["J-FIN:M"][0]
    o["finjoint_M_nohandling_case"] = nog["J-FIN:M"][1]
    o["finhalf_Mb_nohandling_lim"] = nog["FIN:Mb"][0]
    o["finhalf_Mb_nohandling_case"] = nog["FIN:Mb"][1]
    o["n_T_allow"] = n_allow
    o["h_drop_allow_m"] = kw["eta"] * kit_stroke(kw) * (n_allow - 1)
    o["n_T_governing"] = rkey
    o["cradle_stroke_req_m"] = s_req
    return o


# ====================================================================== claims
# rotor
kit.claim("CL-C1-T-CAP", "Peak static thrust per motor at the F4 rpm cap", calc="CALC-C1-ROTOR", output="T_cap_N",
          unit="N", limit=("<=", P + "requirements.thrust_limit_per_motor_n"), verifies=["R-LOADS"], parts=[],
          how="T-C1-THRUST-FRESH: thrust stand on a 16.8 V pack with the F4 output cap; peak thrust <= the requirement.",
          note="The 100 A pack-current limiter is filtered (seconds), so a step to full throttle reaches the rpm cap "
               "before it acts: the limiter does not bound an instantaneous structural load (CR-C1-12).")
kit.claim("CL-C1-T-ILIM", "Thrust per motor held by the 100 A limiter (steady)", calc="CALC-C1-ROTOR",
          output="T_ilim_N", unit="N", how="E1 CL-E1-ILIM-TW-FRESH; stand with the limiter active.")
kit.claim("CL-C1-T-LIMIT", "Limit thrust per motor used for every load case", calc="CALC-C1-ROTOR", output="T_lim_N",
          unit="N", verifies=["R-LOADS"], parts=[],
          how="= max(requirements.thrust_limit_per_motor_n, CL-C1-T-CAP); T-C1-THRUST-FRESH confirms.",
          note="Every rotor, mount, fin and in-plane spar load scales with it.")
kit.claim("CL-C1-MOTOR-TORQUE", "Motor reaction torque at T_lim", calc="CALC-C1-ROTOR", output="Q_Nm", unit="N m",
          how="Thrust stand with a torque cell (T-B4-STAND) at T_lim.")
kit.claim("CL-C1-ROTOR-H", "Rotor angular momentum at T_lim", calc="CALC-C1-ROTOR", output="H_Nms", unit="N m s",
          how="Prop and bell inertia by bifilar swing; rpm from the stand.")
kit.claim("CL-C1-ROTOR-OMEGA", "Rotor speed at T_lim", calc="CALC-C1-ROTOR", output="omega", unit="rad/s",
          how="Optical tachometer or rpm telemetry on the thrust stand.")
kit.claim("CL-C1-GYRO-MOMENT", "Gyroscopic moment per rotor at q_max", calc="CALC-C1-ROTOR", output="M_gyro_Nm",
          unit="N m", how="Calculated; check q_max against flight logs (RATE.*) after the first transitions.")
kit.claim("CL-C1-VH", "Highest level speed used for VD", calc="CALC-C1-ROTOR", output="VH_ms", unit="m/s",
          how="Level full-throttle pass with airspeed logging on the twin; B1 re-runs CL-B1-VMAX with the 11x5.5MR.",
          note="max(prop pitch speed at the 9 350 rpm cap, B1's top speed with the 11x4.5MR); B1's 11x5.5MR value "
               "replaces it (CR-C1-14).")
kit.claim("CL-C1-VD", "Design dive speed VD, re-derived at VC 16 m/s", calc="CALC-C1-ROTOR", output="VD_ms",
          unit="m/s", limit=("<=", P + "requirements.vd_ms"), verifies=["R-LOADS"],
          how="Flight logs: airspeed never exceeds VD; F4 sets ARSPD_FBW_MAX and the fixed-wing THR_MAX below it.",
          note="1.25 x VH: VC 16 m/s does not govern; the 11x5.5MR at the rpm cap does. A FAIL here means "
               "requirements.vd_ms is below the derived value (CR-C1-13); the envelope runs at the larger one.")
kit.claim("CL-C1-HOVER-N-MAX", "Hover load factor at full thrust", calc="CALC-C1-ROTOR", output="n_hover_max",
          unit="-", how="Thrust stand x 4 / weighed mass.")
# V-n
kit.claim("CL-C1-VD-ENV", "Dive speed the envelope runs at", calc="CALC-C1-VN", output="VD_env", unit="m/s",
          how="= max(requirements.vd_ms, CL-C1-VD).")
kit.claim("CL-C1-Q-VD", "Dynamic pressure at the envelope VD", calc="CALC-C1-VN", output="q_VD_Pa", unit="Pa",
          how="0.5 rho VD^2; B2/D6 size the elevon hinge and servo at it (CR-C1-15).")
kit.claim("CL-C1-VS", "Stall speed at the gate, trimmed CLmax (B2)", calc="CALC-C1-VN", output="Vs", unit="m/s",
          how="Same as CL-A1-STALL-GATE; slow-flight stall T-B2-STALL.")
kit.claim("CL-C1-VA", "Manoeuvre speed VA", calc="CALC-C1-VN", output="VA", unit="m/s",
          how="Vs sqrt(n+) with B2's trimmed CLmax; moves with T-B2-STALL.")
kit.claim("CL-C1-N-LIMIT-POS", "Design limit load factor, positive", calc="CALC-C1-VN", output="n_design_pos",
          unit="-", limit=("<=", P + "requirements.load_factor_limit_pos"), verifies=["R-LOADS"],
          how="Wing proof load test (T-C1-WING-PROOF) at this n x the gate weight; flight logs: IMU n stays below it.",
          note="= max(requirement, gust peak); a FAIL means the gust exceeds requirements.load_factor_limit_pos.")
kit.claim("CL-C1-N-LIMIT-NEG", "Design limit load factor, negative", calc="CALC-C1-VN", output="n_design_neg",
          unit="-", limit=(">=", P + "requirements.load_factor_limit_neg"), verifies=["R-LOADS"],
          how="As the positive case, inverted.")
kit.claim("CL-C1-GUST-N-POS", "Peak positive gust load factor", calc="CALC-C1-VN", output="n_gust_pos", unit="-",
          limit=("<=", P + "requirements.load_factor_limit_pos"), verifies=["R-LOADS"],
          how="B2's CL_alpha and trimmed CLmax; the gust line is stall-limited below the peak speed.")
kit.claim("CL-C1-GUST-V-POS", "Speed of the positive gust peak", calc="CALC-C1-VN", output="V_gust_pos", unit="m/s",
          how="Calculated.")
kit.claim("CL-C1-GUST-N-NEG", "Peak negative gust load factor", calc="CALC-C1-VN", output="n_gust_neg", unit="-",
          limit=(">=", P + "requirements.load_factor_limit_neg"), how="Calculated.")
kit.claim("CL-C1-GUST-V-NEG", "Speed of the negative gust peak", calc="CALC-C1-VN", output="V_gust_neg", unit="m/s",
          how="Calculated.")
kit.claim("CL-C1-N-STALL-VD", "Stall-line load factor at VD", calc="CALC-C1-VN", output="n_stall_VD", unit="-",
          limit=("<=", "CL-C1-N-LIMIT-POS"),
          how="F4: limit pitch rate / elevon in manual modes so a full pull at VD cannot reach the stall line.",
          note="Above VA a full elevon pull can exceed the design n; the flight software must prevent it (CR-C1-08).")
# landing and ground
kit.claim("CL-C1-N-LAND-STROKE-MIN", "Landing factor at the minimum foot stroke (40 mm requirement)",
          calc="CALC-C1-LANDING", output="n_L_stroke_min", unit="-", limit=("<=", P + "requirements.landing_n_design"),
          verifies=["R-LANDING-IMPACT"], parts=[],
          how="Drop test T-C1-FOOT-DROP: 0.115 m free drop (1.5 m/s) on the feet with an accelerometer at the CG.",
          note="Replaces CL-C1-N-LAND-NOW (10 mm foot, retired). Rigid airframe, crush efficiency 0.5.")
kit.claim("CL-C1-N-LAND-FULL-FOOT", "Landing factor if the whole 45 mm foot crushes (bound)", calc="CALC-C1-LANDING",
          output="n_L_full_foot", unit="-",
          how="Lower bound: a printed foot cannot crush to zero height; the drop test decides.")
kit.claim("CL-C1-FOOT-STROKE-REQ", "Foot crush stroke required for n_L 6", calc="CALC-C1-LANDING",
          output="stroke_req_m", unit="m", limit=("<=", P + "requirements.foot_crush_stroke_min_m"), how="C5/D5 design the foot to this stroke; drop test T-C1-FOOT-DROP confirms n <= 6.")
kit.claim("CL-C1-FOOT-LEVEL", "Foot load, level landing (limit)", calc="CALC-C1-LANDING", output="F_foot_level_N",
          unit="N", how="Drop test with load cell / accelerometer.")
kit.claim("CL-C1-FOOT-PAIR-NARROW", "Foot load, pair first, narrow axis", calc="CALC-C1-LANDING",
          output="F_foot_pair_narrow_N", unit="N", how="Drop test tilted 10 deg in pitch.")
kit.claim("CL-C1-FOOT-PAIR-WIDE", "Foot load, pair first, wide axis", calc="CALC-C1-LANDING",
          output="F_foot_pair_wide_N", unit="N", how="Drop test tilted 10 deg in roll (after the wingtip fix).")
kit.claim("CL-C1-FOOT-CORNER", "Foot load, one foot first", calc="CALC-C1-LANDING", output="F_foot_corner_N",
          unit="N", how="Drop test tilted 10 deg in pitch and roll.")
kit.claim("CL-C1-FOOT-MAX", "Peak foot load (limit)", calc="CALC-C1-LANDING", output="F_foot_max_N", unit="N",
          how="Envelope of the four foot cases.")
kit.claim("CL-C1-WINGTIP-STRIKE-ANGLE", "Roll error that puts the wingtip down", calc="CALC-C1-LANDING",
          output="wingtip_strike_deg", unit="deg", limit=(">=", P + "requirements.landing_attitude_err_deg"),
          verifies=["R-LANDING-IMPACT"],
          how="Stand the aircraft on its feet and tilt it about the right foot pair until the wingtip TE touches.",
          note="With 10 mm feet the wing TE tip is the first contact for any roll error above this angle (CR-C1-01).")
kit.claim("CL-C1-FOOT-PROTRUSION-REQ", "Foot protrusion beyond the TE required", calc="CALC-C1-LANDING",
          output="foot_protrusion_req_m", unit="m",
          how="D5: foot bottom this far beyond the wing TE; check with the tilt test above.")
kit.claim("CL-C1-TIPOVER-WITH-FOOT", "Narrow-axis tip-over with the longer foot", calc="CALC-C1-LANDING",
          output="tipover_deg_with_req_foot", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"),
          verifies=["R-TIPOVER"], how="Tilt-table test after the foot change (H1 tip-over board).")
kit.claim("CL-C1-WINGTIP-FORCE", "Wingtip strike force (damage case)", calc="CALC-C1-LANDING", output="F_wingtip_N",
          unit="N", how="Not a sizing case once the feet protrude; kept for C2 damage tolerance.")
kit.claim("CL-C1-TIPOVER-ANGLE-CONTACT", "Tip-over rotation at tube-end contact", calc="CALC-C1-LANDING",
          output="tipover_theta_contact_deg", unit="deg", how="Geometry from params.json.")
kit.claim("CL-C1-TIPOVER-ENERGY", "Tip-over impact energy", calc="CALC-C1-LANDING", output="tipover_KE_J", unit="J",
          how="Tip-over board test (H1): drop from the balance point onto foam; bumper must absorb this.")
kit.claim("CL-C1-TIPOVER-FORCE", "Tip-over impact force, two tube ends", calc="CALC-C1-LANDING",
          output="F_tipover_total_N", unit="N", how="Damage-tolerance case; falls with bumper stroke (CR-C1-03).")
kit.claim("CL-C1-STANCE-TIP-WIND", "Wind that tips the parked aircraft", calc="CALC-C1-LANDING",
          output="stance_tip_wind_ms", unit="m/s", limit=(">=", P + "requirements.gust_survive_ms"),
          how="Parked on its feet, motors off: fan or measured wind until a foot lifts.")
kit.claim("CL-C1-STANCE-MU-REQ", "Friction needed to stand in 8 m/s", calc="CALC-C1-LANDING",
          output="stance_mu_req_8ms", unit="-", limit=("<=", "ASM-C1-FRICTION"),
          how="Pull test of a foot on the RFS grass with a spring scale.",
          note="Above the friction available the parked aircraft slides before it tips: feet need spikes or a "
               "rubber pad, or it is laid flat between flights (CR-C1-02).")
kit.claim("CL-C1-CRASH-N", "Crash deceleration (ultimate)", calc="CALC-C1-CRASH", output="n_crash", unit="-",
          limit=(">=", P + "requirements.crash_decel_g"), verifies=["R-PACK-RETENTION"],
          how="Pack strap pull test (C3) at F_pack in each axis.")
kit.claim("CL-C1-PACK-CRASH-LOAD", "Pack retention load (ultimate)", calc="CALC-C1-CRASH", output="F_pack_N",
          unit="N", verifies=["R-PACK-RETENTION"], how="Pull test of the strapped 680 g pack dummy in x, y and z.")
kit.claim("CL-C1-TRANSPORT-N", "Box drop load factor (cradle stroke as assumed)", calc="CALC-C1-TRANSPORT-N",
          output="n_T", unit="-", limit=("<=", "CL-C1-TRANSPORT-N-ALLOW"),
          how="Drop the loaded box 0.3 m with an accelerometer on the spar.")
# envelope
for out, cid, title, unit_, how in (
        ("spar_Mb_ult", "CL-C1-SPAR-MB-ULT", "Spar bending moment, ultimate", "N m",
         "C2 sizes the spar; wing proof test at limit (T-C1-WING-PROOF)."),
        ("spar_Mx_ult", "CL-C1-SPAR-MX-ULT", "Spar flap bending, ultimate", "N m", "As above."),
        ("spar_Mz_ult", "CL-C1-SPAR-MZ-ULT", "Spar in-plane bending, ultimate", "N m",
         "As above; in-plane load from the motor thrust at the fins."),
        ("wing_T_ult", "CL-C1-WING-TORSION-ULT", "Wing torsion about the spar, ultimate", "N m",
         "C2: foam core + skin torsion; twist test at limit."),
        ("wing_Vz_ult", "CL-C1-WING-SHEAR-ULT", "Wing shear (z), ultimate", "N", "C2: spar slot bond shear."),
        ("finjoint_F_ult", "CL-C1-FINJOINT-F-ULT", "Fin-group-to-wing force, ultimate", "N",
         "C4/C6 size the saddle and fin root; proof load at the motor stations."),
        ("finjoint_M_ult", "CL-C1-FINJOINT-M-ULT", "Fin-group-to-wing moment, ultimate", "N m", "As above."),
        ("finjoint_M_design", "CL-C1-FINJOINT-M-DESIGN", "Fin joint design moment (fitting, printed)", "N m",
         "C6 sizes the printed/bonded saddle to this value."),
        ("finhalf_Mb_ult", "CL-C1-FINHALF-MB-ULT", "Fin + tube bending at the wing plane, ultimate", "N m",
         "C4 splits between tube and fin board; tube proof hang test."),
        ("mount_F_ult", "CL-C1-MOUNT-F-ULT", "Mount-to-tube force, ultimate", "N", "C4/C6: mount clamp proof load."),
        ("mount_M_ult", "CL-C1-MOUNT-M-ULT", "Mount-to-tube moment, ultimate", "N m", "As above."),
        ("motor_F_ult", "CL-C1-MOTOR-F-ULT", "Motor-to-mount force, ultimate", "N", "C6: M3 screw sizing."),
        ("pod_F_ult", "CL-C1-POD-F-ULT", "Pod-to-wing force, flight/ground, ultimate", "N",
         "C3: pod bond and strap; crash is separate (CL-C1-PACK-CRASH-LOAD)."),
        ("foot_F_ult", "CL-C1-FOOT-F-ULT", "Foot-to-fin force, ultimate", "N", "C5: foot bond; drop test."),
        ("n_T_allow", "CL-C1-TRANSPORT-N-ALLOW", "Box drop factor the airframe tolerates", "-",
         "Calculated: the drop must not exceed any flight/landing/handling limit load."),
        ("finjoint_M_nohandling_lim", "CL-C1-FINJOINT-M-FLIGHT-LIM", "Fin joint moment without handling cases, limit",
         "N m", "Applies only if lifting by a motor tube is ruled out by a handle and a label (CR-C1-04)."),
        ("h_drop_allow_m", "CL-C1-DROP-HEIGHT-ALLOW", "Box drop height the assumed cradle foam allows", "m",
         "Box drop test with accelerometer; D7 label 'do not drop'."),
        ("cradle_stroke_req_m", "CL-C1-CRADLE-STROKE-REQ", "Cradle foam stroke required (0.3 m drop)", "m",
         "D7 sizes the cradle foam; box drop test with accelerometer."),
        ("residual_N", "CL-C1-EQUILIBRIUM-RESIDUAL", "Largest free-body residual (all cases)", "N or N m",
         "Self-check: every case is in equilibrium.")):
    kw_ = {}
    if cid == "CL-C1-EQUILIBRIUM-RESIDUAL":
        kw_["limit"] = ("<=", 1e-6)
    kit.claim(cid, title, calc="CALC-C1-ENVELOPE", output=out, unit=unit_, how=how,
              verifies=["R-LOADS"] if cid != "CL-C1-EQUILIBRIUM-RESIDUAL" else [], **kw_)

kit.test("T-C1-WING-PROOF", "Wing proof load at limit", verifies=["CL-C1-SPAR-MB-ULT", "CL-C1-N-LIMIT-POS"],
         procedure="Support at the pod, sandbag the wing to the F1 spanwise shear (data/wing_spanwise.csv) at limit; "
                   "no permanent set after unloading; tip deflection logged.")
kit.test("T-C1-FOOT-DROP", "Foot drop test at 1.5 m/s", verifies=["CL-C1-N-LAND-STROKE-MIN", "CL-C1-FOOT-STROKE-REQ"],
         procedure="0.115 m free drop of the aircraft (or a 2.6 kg dummy on one fin) onto its feet, accelerometer at the "
                   "CG; level and 10 deg tilted; n <= 6.")
kit.test("T-C1-THRUST-FRESH", "Max thrust on a fresh pack", verifies=["CL-C1-T-CAP", "CL-C1-T-LIMIT"],
         procedure="H1 thrust stand, one station, 11x5.5MR, 16.8 V pack, F4 output cap and 100 A limiter as flown: step to full throttle, record peak thrust, torque and rpm.")
kit.test("T-C1-STATION-PROOF", "Motor-station proof load", verifies=["CL-C1-MOUNT-F-ULT", "CL-C1-FINHALF-MB-ULT"],
         procedure="Hang the limit mount load from each motor mount in -x and y with the wing supported at the spar.")


# ====================================================================== export (data files and figures)


def _model_args():
    vals = {}
    for arg, ref in ENV_INPUTS.items():
        vals[arg] = kit.value(ref)
    return vals


def write_data(outdir):
    kw = _model_args()
    k, X = pack_inputs(kw)
    res = run_all(k, X, detail=True)
    sf = kw["sf"]
    outdir.mkdir(parents=True, exist_ok=True)
    comps = ["Fx_N", "Fy_N", "Fz_N", "Mx_Nm", "My_Nm", "Mz_Nm"]
    with open(outdir / "wing_spanwise.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "mass_config", "family", "y_m"] + comps + ["Mbend_Nm"])
        for case, mc, fam, y, side, v in res["wing"]:
            w.writerow([case, mc, fam, f"{y:.6f}"] + [f"{x:.4f}" for x in v] + [f"{math.hypot(v[3], v[5]):.4f}"])
    with open(outdir / "fin_heightwise.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "mass_config", "family", "side", "half", "z_cut_m"] + comps + ["Mbend_Nm"])
        for case, mc, fam, side, sz, zc, v in res["fin"]:
            w.writerow([case, mc, fam, "R" if side > 0 else "L", "upper" if sz > 0 else "lower", f"{sz * zc:.6f}"]
                       + [f"{x:.4f}" for x in v] + [f"{math.hypot(v[3], v[4]):.4f}"])
    with open(outdir / "joints.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "mass_config", "family", "joint"] + comps + ["F_res_N", "M_res_Nm", "Mbend_Nm"])
        for case, mc, fam, jid, v, mb in res["joints"]:
            w.writerow([case, mc, fam, jid] + [f"{x:.4f}" for x in v]
                       + [f"{norm(v[:3]):.4f}", f"{norm(v[3:]):.4f}", f"{mb:.4f}"])
    # envelopes
    env = {}
    for case, mc, fam, jid0, v, mb in res["joints"]:
        if fam not in ENVELOPE_FAMILIES:
            continue
        jid = jclass(jid0)
        e = env.setdefault(jid, {"F_res_N": (0, ""), "M_res_Nm": (0, ""), "Mbend_Nm": (0, ""),
                                 **{c: (0, "") for c in comps}})
        for name, val in (("F_res_N", norm(v[:3])), ("M_res_Nm", norm(v[3:])), ("Mbend_Nm", mb),
                          *[(c, abs(v[i])) for i, c in enumerate(comps)]):
            if val > e[name][0]:
                e[name] = (val, f"{case}/{mc}/{jid0}")
    kf, kp = kw["kfit"], kw["kprint"]
    jenv = {}
    for jid, e in env.items():
        jenv[jid] = {name: {"limit": round(v, 4), "ultimate": round(v * sf, 4),
                            "joint_design": round(v * sf * kf, 4), "printed_bonded_design": round(v * sf * kf * kp, 4),
                            "case": c} for name, (v, c) in e.items()}
    wenv = {}
    for case, mc, fam, y, side, v in res["wing"]:
        if fam not in ENVELOPE_FAMILIES:
            continue
        key = f"{abs(y):.6f}"
        if y < 0 or (side < 0):
            v = (v[0], -v[1], v[2], -v[3], v[4], -v[5])          # mirror the left half onto the right
        e = wenv.setdefault(key, {})
        for i, c in enumerate(comps):
            mx, mn = e.get(c + "_max", (-1e9, "")), e.get(c + "_min", (1e9, ""))
            if v[i] > mx[0]:
                e[c + "_max"] = (v[i], case)
            if v[i] < mn[0]:
                e[c + "_min"] = (v[i], case)
        mb = math.hypot(v[3], v[5])
        if mb > e.get("Mbend_Nm_max", (-1, ""))[0]:
            e["Mbend_Nm_max"] = (mb, case)
    with open(outdir / "wing_envelope.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        cols = [c + s for c in comps for s in ("_max", "_min")] + ["Mbend_Nm_max"]
        w.writerow(["y_m"] + [h for c in cols for h in (c + "_limit", c + "_case")] + ["Mbend_Nm_ultimate"])
        for key in sorted(wenv, key=float):
            e = wenv[key]
            w.writerow([key] + [x for c in cols for x in (f"{e[c][0]:.4f}", e[c][1])] + [f"{e['Mbend_Nm_max'][0] * sf:.4f}"])
    fenv = {}
    for case, mc, fam, side, sz, zc, v in res["fin"]:
        if fam not in ENVELOPE_FAMILIES:
            continue
        key = f"{zc:.6f}"
        e = fenv.setdefault(key, {})
        for name, val in (("Mbend_Nm", math.hypot(v[3], v[4])), ("Mz_torsion_Nm", abs(v[5])),
                          ("Fx_N", abs(v[0])), ("Fy_N", abs(v[1])), ("Fz_axial_N", abs(v[2]))):
            if val > e.get(name, (-1, ""))[0]:
                e[name] = (val, f"{case}/{mc}/{'R' if side > 0 else 'L'}{'U' if sz > 0 else 'L'}")
    with open(outdir / "fin_envelope.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        names = ["Mbend_Nm", "Mz_torsion_Nm", "Fx_N", "Fy_N", "Fz_axial_N"]
        w.writerow(["z_from_wing_m"] + [h for n in names for h in (n + "_limit", n + "_case")]
                   + [n + "_ultimate" for n in names])
        for key in sorted(fenv, key=float):
            e = fenv[key]
            w.writerow([key] + [x for n in names for x in (f"{e[n][0]:.4f}", e[n][1])]
                       + [f"{e[n][0] * sf:.4f}" for n in names])
    # feet
    feet = []
    for case, mc, fam, jid, v, mb in res["joints"]:
        if jid.startswith("J-FOOT-"):
            feet.append((case, mc, fam, jid[7:], v))
    with open(outdir / "feet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "mass_config", "family", "foot", "Fx_N", "Fy_N", "Fz_N", "Mx_Nm", "My_Nm", "Mz_Nm"])
        for case, mc, fam, ft, v in feet:
            w.writerow([case, mc, fam, ft] + [f"{x:.4f}" for x in v])
    # cases
    with open(outdir / "cases.json", "w", encoding="utf-8") as f:
        json.dump({"note": "Rigid-body state per case and mass configuration (aircraft frame, SI). Loads are limit.",
                   "cases": res["cases"]}, f, indent=1, default=lambda o: list(o))
    ld = kit.value("CL-C1-FOOT-MAX")
    other = {
        "factors": {"safety_factor_ultimate": sf, "fitting_factor": kf, "printed_bonded_factor": kp,
                    "crash": "ultimate as given (emergency case, no further factor)"},
        "landing": {kid: kit.value(kid) for kid in ("CL-C1-N-LAND-STROKE-MIN", "CL-C1-N-LAND-FULL-FOOT", "CL-C1-FOOT-STROKE-REQ", "CL-C1-FOOT-LEVEL",
                                                     "CL-C1-FOOT-PAIR-NARROW", "CL-C1-FOOT-PAIR-WIDE",
                                                     "CL-C1-FOOT-CORNER", "CL-C1-FOOT-MAX")},
        "foot_side_load_limit_N": kit.value("ASM-C1-FRICTION") * ld,
        "crash_ultimate": {"n": kit.value("CL-C1-CRASH-N"), "pack_N_any_axis": kit.value("CL-C1-PACK-CRASH-LOAD"),
                           "avionics_N_any_axis": kit._run("CALC-C1-CRASH")["F_avionics_N"]},
        "assembly": {"prop_nut_torque_Nm_about_shaft": kit.value("ASM-C1-PROP-NUT-TORQUE"),
                     "pack_strap_preload_N": kit.value("ASM-C1-STRAP-PRELOAD")},
        "elevon_panel_limit_load_per_m_N": 0.5 * kw["rho"] * kw["VD"] ** 2 * k["el_f"] * k["c"] * kit.value("ASM-C1-ELEVON-CN"),
        "elevon_panel_limit_pressure_Pa": 0.5 * kw["rho"] * kw["VD"] ** 2 * kit.value("ASM-C1-ELEVON-CN"),
        "rotor_per_motor": {"T_lim_N": kw["T_lim"], "Q_Nm": kw["Q"], "M_gyro_Nm": kit.value("CL-C1-GYRO-MOMENT")},
        "transport": {"n_T": kw["n_T"], "n_T_allow": kit.value("CL-C1-TRANSPORT-N-ALLOW"),
                      "cradle_stroke_req_m": kit.value("CL-C1-CRADLE-STROKE-REQ")},
    }
    with open(outdir / "envelope.json", "w", encoding="utf-8") as f:
        json.dump({"note": "Limit-load envelopes over cases F1-F8, H1-H9, T1-T3, L1-L5, G1-G3 and both mass configs. "
                           "ultimate = 1.5 x limit; joint_design = x fitting factor; printed_bonded_design = x printed factor. "
                           "Damage (L6, L7), transport (X1-X3) and crash are reported separately.",
                   "joints": jenv, "other": other}, f, indent=1)
    write_mass_csv(outdir, k)
    return res, k, X, kw, wenv, fenv, jenv


def write_mass_csv(outdir, k):
    with open(outdir / "mass_model.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mass_config", "group", "station", "n_items", "mass_kg", "x_m", "y_m", "z_m"])
        for growth, mc in (("centre", "MC-C"), ("prorata", "MC-P")):
            items = build_items(k, growth)
            grp = {}
            for i in items:
                key = (i["grp"], i["st"] or ("R" if i["side"] > 0 else "L" if i["side"] < 0 else "C"))
                grp.setdefault(key, []).append(i)
            for (g_, st), lst in sorted(grp.items()):
                m = sum(i["m"] for i in lst)
                c = [sum(i["m"] * i["r"][a] for i in lst) / m for a in range(3)]
                w.writerow([mc, g_, st, len(lst), f"{m:.5f}"] + [f"{x:.4f}" for x in c])
            m, cg, I = mass_props(items)
            w.writerow([mc, "TOTAL", "", len(items), f"{m:.5f}"] + [f"{x:.4f}" for x in cg])


def convergence(k, X):
    rows = []
    for dy in (0.01, 0.005, 0.0025):
        items = build_items(k, "centre", dy)
        case = [c for c in build_cases(k, X, items, "centre", dy) if c["id"] == "F1-PULLUP-VD"][0]
        pts, info = solve(items, case["loads"], case["gb"])
        v = resultant([p for p in pts if p["r"][1] > 1e-9], (k["x_spar"], 0.0, 0.0))
        rows.append((dy, v[3], math.hypot(v[3], v[5])))
    return rows


def hand_check(k, X):
    """Independent root flap moment for F8 (1 g cruise), MC-C: lift moment with B2's own half-span centroid (from
    loads_spanwise.json, not from the strip model) minus the right-half weight moment."""
    items = build_items(k, "centre")
    m, cg, I = mass_props(items)
    W = m * k["g"]
    p = HERE.parents[0] / "B2" / "out" / "loads_spanwise.json"
    ybar = json.loads(p.read_text(encoding="utf-8"))["cases"]["CL0.30"]["ybar_m"]
    M_lift = W / 2 * ybar
    M_wt = sum(i["m"] * k["g"] * i["r"][1] for i in items if i["r"][1] > 0)
    return M_lift - M_wt


def svg_figures(outdir, k, X, kw, wenv):
    sf = kw["sf"]
    ink, ink2, ink3, line3, acc = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#1F5FC7"
    font = "font-family=\"IBM Plex Mono, monospace\" font-size=\"12\""
    # --- V-n diagram
    vn = vn_calc(kw["g"], kw["rho"], kw["m_gate"], kw["b"], kw["c"], kw["clmax"], kit.value("ASM-C1-CLMIN"),
                 kit.value("CL-B2-CLA-3D"), kit.value(P + "requirements.load_factor_limit_pos"),
                 kit.value(P + "requirements.load_factor_limit_neg"), kw["Vc"], kw["v_gust"],
                 kit.value("ASM-C1-UDE-D-FRAC"), kw["VD"], kw["VD"])
    Wd, Hd, L, T, Rm, B = 1200, 560, 80, 30, 40, 60
    vmax, nmin, nmax = math.ceil(kw["VD"] + 2), -2.0, 4.0

    def X_(v):
        return L + (Wd - L - Rm) * v / vmax

    def Y_(n):
        return T + (Hd - T - B) * (nmax - n) / (nmax - nmin)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Hd}" width="{Wd}" height="{Hd}">']
    for n in range(int(nmin), int(nmax) + 1):
        s.append(f'<line x1="{L}" y1="{Y_(n):.1f}" x2="{Wd - Rm}" y2="{Y_(n):.1f}" stroke="#E3E7ED" stroke-width="1"/>')
        s.append(f'<text x="{L - 10}" y="{Y_(n) + 4:.1f}" text-anchor="end" fill="{ink3}" {font}>{n}</text>')
    for v in range(0, vmax + 1, 5):
        s.append(f'<text x="{X_(v):.1f}" y="{Hd - B + 20}" text-anchor="middle" fill="{ink3}" {font}>{v}</text>')
    s.append(f'<line x1="{L}" y1="{Y_(0):.1f}" x2="{Wd - Rm}" y2="{Y_(0):.1f}" stroke="{line3}" stroke-width="1"/>')
    s.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{Hd - B}" stroke="{line3}" stroke-width="1"/>')
    s.append(f'<text x="{(Wd + L) / 2}" y="{Hd - 12}" text-anchor="middle" fill="{ink2}" {font}>airspeed m/s (EAS)</text>')
    s.append(f'<text x="20" y="{(Hd) / 2}" fill="{ink2}" {font} transform="rotate(-90 20 {Hd / 2})" text-anchor="middle">load factor n</text>')
    # manoeuvre envelope
    nP, nN = kit.value("CL-C1-N-LIMIT-POS"), kit.value("CL-C1-N-LIMIT-NEG")
    pts = []
    Vs = vn["Vs"]
    for i in range(0, 101):
        v = Vs + (vn["VA"] - Vs) * i / 100
        pts.append((v, (v / Vs) ** 2))
    pts += [(kw["VD"], nP), (kw["VD"], nN)]
    neg = []
    for i in range(0, 101):
        v = Vs + (vn["VG"] - Vs) * i / 100
        neg.append((v, -(v / vn["Vs_neg"]) ** 2))
    pts += [(vn["VG"], nN)] + neg[::-1]
    d = " ".join(f"{'M' if i == 0 else 'L'}{X_(v):.1f},{Y_(n):.1f}" for i, (v, n) in enumerate(pts))
    s.append(f'<path d="{d} Z" fill="#E6EEFB" fill-opacity="0.6" stroke="{acc}" stroke-width="1.5"/>')
    # stall lines extended (dashed) and gust lines
    st = " ".join(f"{'M' if i == 0 else 'L'}{X_(v):.1f},{Y_(min((v / Vs) ** 2, nmax)):.1f}"
                  for i, v in enumerate([Vs * 0.0 + Vs + (kw['VD'] - Vs) * j / 60 for j in range(61)]))
    s.append(f'<path d="{st}" fill="none" stroke="{ink3}" stroke-width="0.75" stroke-dasharray="6 4"/>')
    a, kg, ws = vn["a3d"], vn["kg"], kw["m_gate"] * kw["g"] / (kw["b"] * kw["c"])
    Uc, Ud = kw["v_gust"], kw["v_gust"] * kit.value("ASM-C1-UDE-D-FRAC")
    for sign in (1, -1):
        for U, Vend in ((Uc, kw["Vc"]), (Ud, kw["VD"])):
            n_end = 1 + sign * kg * kw["rho"] * U * Vend * a / (2 * ws)
            s.append(f'<line x1="{X_(0):.1f}" y1="{Y_(1):.1f}" x2="{X_(Vend):.1f}" y2="{Y_(n_end):.1f}" stroke="{ink2}" '
                     f'stroke-width="0.75"/>')
    for v, n, lab in ((vn["Vs"], 1, "Vs"), (vn["VA"], nP, "VA"), (kw["Vc"], 0, "VC"), (kw["VD"], 0, "VD")):
        s.append(f'<line x1="{X_(v):.1f}" y1="{Y_(nmin):.1f}" x2="{X_(v):.1f}" y2="{Y_(nmax):.1f}" stroke="{line3}" '
                 f'stroke-width="0.75" stroke-dasharray="6 4"/>')
        s.append(f'<text x="{X_(v) + 4:.1f}" y="{T + 14}" fill="{ink}" {font}>{lab} {v:.1f}</text>')
    s.append(f'<circle cx="{X_(vn["V_gust_pos"]):.1f}" cy="{Y_(vn["n_gust_pos"]):.1f}" r="5" fill="#C2540A"/>')
    s.append(f'<text x="{X_(vn["V_gust_pos"]) - 8:.1f}" y="{Y_(vn["n_gust_pos"]) + 20:.1f}" text-anchor="end" fill="{ink}" {font}>'
             f'gust peak n {vn["n_gust_pos"]:.2f}</text>')
    s.append(f'<text x="{X_(kw["VD"]) - 6:.1f}" y="{Y_(nP) - 8:.1f}" text-anchor="end" fill="{acc}" {font}>n+ {nP:.2f}</text>')
    s.append(f'<text x="{X_(kw["VD"]) - 6:.1f}" y="{Y_(nN) + 18:.1f}" text-anchor="end" fill="{acc}" {font}>n- {nN:.2f}</text>')
    s.append("</svg>")
    (outdir / "vn-diagram.svg").write_text("\n".join(s), encoding="utf-8")
    # --- wing spanwise envelope (ultimate), right half
    ys = sorted((float(kk) for kk in wenv if float(kk) >= 0))
    series = [("Mbend_Nm_max", "spar bending (resultant)", ink), ("Mx_Nm", "flap Mx", acc),
              ("Mz_Nm", "in-plane Mz", "#C2540A"), ("My_Nm", "torsion My", ink3)]

    def val(e, key):
        if key == "Mbend_Nm_max":
            return e[key][0]
        return max(abs(e[key + "_max"][0]), abs(e[key + "_min"][0]))

    vmaxm = max(val(wenv[f"{y:.6f}"], "Mbend_Nm_max") for y in ys) * sf
    top = math.ceil(vmaxm / 2) * 2
    Wd, Hd = 1200, 460
    L, T, Rm, B = 80, 30, 220, 60

    def XX(y):
        return L + (Wd - L - Rm) * y / (k["b"] / 2)

    def YY(v):
        return T + (Hd - T - B) * (top - v) / top

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Hd}" width="{Wd}" height="{Hd}">']
    for v in range(0, int(top) + 1, 2):
        s.append(f'<line x1="{L}" y1="{YY(v):.1f}" x2="{Wd - Rm}" y2="{YY(v):.1f}" stroke="#E3E7ED" stroke-width="1"/>')
        s.append(f'<text x="{L - 10}" y="{YY(v) + 4:.1f}" text-anchor="end" fill="{ink3}" {font}>{v}</text>')
    for i in range(0, 7):
        y = 0.1 * i
        if y <= k["b"] / 2 + 1e-9:
            s.append(f'<text x="{XX(y):.1f}" y="{Hd - B + 20}" text-anchor="middle" fill="{ink3}" {font}>{y:.1f}</text>')
    s.append(f'<line x1="{L}" y1="{YY(0):.1f}" x2="{Wd - Rm}" y2="{YY(0):.1f}" stroke="{line3}"/>')
    s.append(f'<line x1="{XX(k["fin_y"]):.1f}" y1="{T}" x2="{XX(k["fin_y"]):.1f}" y2="{Hd - B}" stroke="{line3}" '
             f'stroke-dasharray="6 4" stroke-width="0.75"/>')
    s.append(f'<text x="{XX(k["fin_y"]) + 4:.1f}" y="{T + 12}" fill="{ink2}" {font}>fin y {k["fin_y"]:.2f}</text>')
    s.append(f'<text x="{(Wd - Rm + L) / 2}" y="{Hd - 12}" text-anchor="middle" fill="{ink2}" {font}>span station y m</text>')
    s.append(f'<text x="20" y="{Hd / 2}" fill="{ink2}" {font} transform="rotate(-90 20 {Hd / 2})" text-anchor="middle">ultimate moment N·m</text>')
    for j, (key, lab, col) in enumerate(series):
        d = " ".join(f"{'M' if i == 0 else 'L'}{XX(y):.1f},{YY(val(wenv[f'{y:.6f}'], key) * sf):.1f}"
                     for i, y in enumerate(ys))
        wdt = 2 if j == 0 else 1.5
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{wdt}"/>')
        y_lab = T + 20 + 22 * j
        s.append(f'<line x1="{Wd - Rm + 20}" y1="{y_lab - 4}" x2="{Wd - Rm + 44}" y2="{y_lab - 4}" stroke="{col}" stroke-width="{wdt}"/>')
        s.append(f'<text x="{Wd - Rm + 50}" y="{y_lab}" fill="{ink}" {font}>{lab}</text>')
    s.append("</svg>")
    (outdir / "wing-envelope.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    kit.write()
    out = HERE / "data"
    res, k, X, kw, wenv, fenv, jenv = write_data(out)
    svg_figures(out, k, X, kw, wenv)
    conv = convergence(k, X)
    hc = hand_check(k, X)
    f8 = [v for case, mc, fam, y, side, v in res["wing"] if case == "F8-CRUISE" and mc == "MC-C" and side > 0 and abs(y) < 1e-12][0]
    rep = {"strip_convergence_F1_root": [{"dy_m": d, "Mx_Nm": mx, "Mbend_Nm": mb} for d, mx, mb in conv],
           "hand_check_F8_root_Mx": {"hand_Nm": hc, "model_Nm": f8[3], "diff_frac": (f8[3] - hc) / hc},
           "equilibrium_residual_max": res["residual"]}
    (out / "checks.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))
