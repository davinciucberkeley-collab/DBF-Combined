"""B4 rotor / propeller aero: prop selection, hover and cruise operating points, installation effects.

Run:  python -I redesign/team/B4/props.py          -> claims.json + out/props_results.json beside this file
Standard library only. Prop data: APC PER3 files and UIUC measurements copied into data/*.csv (sources in each
file header). Every calculation is a pure function of params.json ids, B4 assumptions (ASM-B4-*) and those data
files, so build_graph.py can re-run it.

Frame (params.json#frame): x aft from the wing LE, y right, z up (cruise attitude). Thrust along -x; the prop
wake travels +x in hover and in cruise.
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/fins/params.json"])  # P:fin_detail.* (D3)
P = "P:"
IN = 0.0254
PROPS = {  # key -> (data file, diameter in, APC rpm-limit constant, mass g, price USD, pusher part exists)
    "11x4.5MR": ("apc_per3_11x45MR.csv", 11.0, 105000, 17.0, 3.83, "MRP"),
    "11x4.7SF": ("apc_per3_11x47SF.csv", 11.0, 65000, 20.0, 3.50, "SFP"),
    "11x5.5MR": ("apc_per3_11x55MR.csv", 11.0, 105000, 17.0, 3.83, "MRP"),
    "11x5.5E": ("apc_per3_11x55E.csv", 11.0, 150000, 23.0, 4.17, "EP"),
    "12x4.5MR": ("apc_per3_12x45MR.csv", 12.0, 105000, 20.0, 4.10, "MRP"),
    # CDR-15 / CDR-AE-08 (2026-11-13): higher-pitch thin electric for the cruise A/B. LP11070E, 0.81 oz, $4.17 (APC
    # product page, read 2026-11-13). No thin-electric pusher 11x7EP is listed by APC (SRC-B4-APC-11X7E): "-".
    "11x7E": ("apc_per3_11x7E.csv", 11.0, 150000, 23.0, 4.17, "-"),
}


# ---------------------------------------------------------------- data
def _load(name):
    rows = []
    with open(HERE / "data" / name, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            rows.append({k: float(v) if v not in ("", None) and k not in ("prop", "kind") else v for k, v in r.items()})
    return rows


DATA = {k: _load(v[0]) for k, v in PROPS.items()}
UIUC = _load("uiuc_measured.csv")
AIRFOIL = HERE.parents[1] / "team" / "B2" / "airfoils" / "s5010.dat"   # B2's checked S5010 coordinates (SRC-S5010)


def _airfoil_surfaces():
    """S5010 upper and lower surfaces as (x/c ascending, z/c) lists, read from B2's Selig-format file."""
    pts = []
    for line in AIRFOIL.read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split()
        if len(f) == 2:
            pts.append((float(f[0]), float(f[1])))
    i_le = min(range(len(pts)), key=lambda k: pts[k][0])
    up = sorted(pts[:i_le + 1])
    lo = sorted(pts[i_le:])
    return up, lo


def _interp(xs, ys, x):
    """Linear interpolation, linear extrapolation beyond the ends."""
    if x <= xs[0]:
        i = 0
    elif x >= xs[-1]:
        i = len(xs) - 2
    else:
        i = max(j for j in range(len(xs) - 1) if xs[j] <= x)
    t = (x - xs[i]) / (xs[i + 1] - xs[i])
    return ys[i] + t * (ys[i + 1] - ys[i])


def coeffs(prop, J, rpm):
    """Ct, Cp at advance ratio J and rpm: linear in J inside each APC rpm table, then linear in rpm (clamped)."""
    tables = sorted({r["rpm"] for r in DATA[prop]})
    rpm_c = min(max(rpm, tables[0]), tables[-1])
    out = []
    for tr in tables:
        rows = [r for r in DATA[prop] if r["rpm"] == tr]
        js = [r["J"] for r in rows]
        out.append((tr, _interp(js, [r["Ct"] for r in rows], J), _interp(js, [r["Cp"] for r in rows], J)))
    rs = [o[0] for o in out]
    return _interp(rs, [o[1] for o in out], rpm_c), _interp(rs, [o[2] for o in out], rpm_c)


def thrust_power(prop, rpm, V, rho):
    D = PROPS[prop][1] * IN
    n = rpm / 60.0
    J = V / (n * D) if n > 0 else 0.0
    ct, cp = coeffs(prop, J, rpm)
    return ct * rho * n * n * D ** 4, cp * rho * n ** 3 * D ** 5, J, ct, cp


def _bisect(f, lo, hi, it=80):
    flo = f(lo)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def rpm_for_thrust(prop, T, V, rho):
    return _bisect(lambda r: thrust_power(prop, r, V, rho)[0] - T, 1500.0, 14000.0)


class Motor:
    """DC motor model: EMF = rpm / Kv, Q = Kt (I - I0), V_term = EMF + I R (R lumps winding, ESC and leads)."""

    def __init__(self, kv, i0, r):
        self.kv, self.i0, self.r = kv, i0, r
        self.kt = 60.0 / (2 * math.pi * kv)

    def current(self, Q):
        return Q / self.kt + self.i0

    def p_in(self, rpm, Q):
        i = self.current(Q)
        return (rpm / self.kv + i * self.r) * i, i

    def full_throttle_rpm(self, prop, V_supply, V_air, rho):
        def f(rpm):
            P_shaft = thrust_power(prop, rpm, V_air, rho)[1]
            Q = P_shaft / (2 * math.pi * rpm / 60.0)
            return (V_supply - rpm / self.kv) / self.r - self.current(Q)
        return _bisect(f, 1500.0, V_supply * self.kv * 0.999)


# ---------------------------------------------------------------- elliptic integrals and vortex rings (stdlib)
def ellip_KE(m):
    a, b, c = 1.0, math.sqrt(max(1.0 - m, 0.0)), math.sqrt(m)
    s, p = 0.5 * c * c, 0.5
    for _ in range(40):
        a, b, c = 0.5 * (a + b), math.sqrt(a * b), 0.5 * (a - b)
        p *= 2.0
        s += p * c * c
        if c < 1e-15:
            break
    K = math.pi / (2 * a)
    return K, K * (1.0 - s)


def ring_ux(a, X, r):
    """Axial velocity per unit circulation of a vortex ring (radius a) at axial offset X and radial distance r."""
    d2 = (a + r) ** 2 + X * X
    m = 4 * a * r / d2
    K, E = ellip_KE(m)
    return 1.0 / (2 * math.pi * math.sqrt(d2)) * (K + (a * a - r * r - X * X) / ((a - r) ** 2 + X * X) * E)


def cylinder_ux(R, gamma, X, r, L, N):
    """Semi-infinite (length L) vortex cylinder, sheet strength gamma, wake along +X from X = 0. Simpson, N even."""
    h = L / N
    s = 0.0
    for k in range(N + 1):
        w = 1 if k in (0, N) else (4 if k % 2 else 2)
        s += w * ring_ux(R, X - k * h, r)
    return gamma * s * h / 3.0


def ring_ur(a, X, r):
    """Radial velocity per unit circulation of the same ring (positive outward). Sign checked by continuity
    (1/r d(r u_r)/dr + du_x/dX = 0, residual < 1e-6) in CALC-B4-PITOT's self-test."""
    d2 = (a + r) ** 2 + X * X
    K, E = ellip_KE(4 * a * r / d2)
    return X / (2 * math.pi * r * math.sqrt(d2)) * (-K + (a * a + r * r + X * X) / ((a - r) ** 2 + X * X) * E)


def cylinder_vel(R, gamma, X, r, L, N):
    """(u_axial, u_radial) of the semi-infinite vortex cylinder, Simpson over N rings (N even)."""
    h = L / N
    sx = sr = 0.0
    for k in range(N + 1):
        w = 1 if k in (0, N) else (4 if k % 2 else 2)
        sx += w * ring_ux(R, X - k * h, r)
        sr += w * ring_ur(R, X - k * h, r)
    return gamma * sx * h / 3.0, gamma * sr * h / 3.0


# ---------------------------------------------------------------- canted-motor geometry (R3: 7 deg cant, D-27)
def thrust_side(y, z, k):
    """Unit (y, z) direction of the canted thrust's side component at a motor at (y, z). F4's map (k = +1,
    subsystems/flight-software/SPEC.md 'Cant sense'): the prop end leans toward the wing plane (|y|/r) and
    outboard (|z|/r). k = -1 is the mirrored spin map (every rotation reversed, cant still with the reaction torque)."""
    r = math.hypot(y, z)
    return k * math.copysign(1.0, y) * abs(z) / r, -k * math.copysign(1.0, z) * abs(y) / r


def wake_axis(y, z, cant, k, V=0.0, v=1.0):
    """Unit wake-axis vector (x, y, z). Hover (V = 0): along the canted shaft, opposite the thrust, so its side
    component is opposite thrust_side. Forward flight: the resultant of V along +x and v along the shaft."""
    s, c = math.sin(math.radians(cant)), math.cos(math.radians(cant))
    ty, tz = thrust_side(y, z, k)
    w = (V + v * c, -v * s * ty, -v * s * tz)
    n = math.sqrt(sum(q * q for q in w))
    return tuple(q / n for q in w)


def hub_centre(x_prop, y, z, cant, k, stack):
    """Prop hub centre: the motor base sits on the canted pads at the axis, the hub is `stack` along the canted
    shaft. R4: x_prop (params, = CL-E1-CAD-HUB-X) is already the hub x on the canted axis (its x projection is
    stack cos(cant), fins params prop_stack_m note), so only y and z move. R3 added stack (1 - cos) = 0.28 mm aft."""
    s = math.sin(math.radians(cant))
    ty, tz = thrust_side(y, z, k)
    return x_prop, y + stack * s * ty, z + stack * s * tz


def wake_centre(x, hub, e):
    """Wake centre-line (y, z) and distance along the axis s at body station x."""
    s_ax = (x - hub[0]) / e[0]
    return hub[1] + s_ax * e[1], hub[2] + s_ax * e[2], s_ax


# ---------------------------------------------------------------- assumptions (B4)
A = kit.assumption
A("ASM-B4-VSAG", "Pack voltage at the end of a flight, loaded", "4S pack at 3.4 V/cell under full-throttle load",
  value=13.6, unit="V", basis="4S 6500 130C late in the flight; same basis as the K09 review section (3.4 V/cell)",
  status="PROPOSED", cites=["SRC-K09-REVIEW"])
A("ASM-B4-CD-TUBE", "Cylinder drag coefficient 1.1", "22 mm tube in the slipstream, Re ~1.3e4 (subcritical)",
  value=1.1, unit="-", basis="Hoerner, Fluid-Dynamic Drag, ch. 3: Cd 1.0-1.2 for 1e4 < Re < 2e5")
A("ASM-B4-PROFILE", "Slipstream peak-to-mean dynamic pressure 1.3", "A real prop loads its outer half: the tube "
  "sees about 1.3 x the mean slipstream dynamic pressure", value=1.3, unit="-",
  basis="typical blade loading peak near 0.75 R; bounds the uniform-disk value from above", status="UNVERIFIED")
A("ASM-B4-FOOT", "Foot frontal area 30 x 30 mm", "crushable printed foot on each fin TE tip, near the prop axis",
  value=0.0009, unit="m2", basis="bounds D5's GER-001 shoe over the 9.6 mm fin TE (subsystems/landing/SPEC.md: "
  "11 x 18 mm cartridge in a sleeve); D5 publishes no frontal area")
A("ASM-B4-CD-STRIP", "Sharp-edged strip and ear drag coefficient 1.2", "10 x 3 mm pultruded CF brace broadside to "
  "the flow with its 10 mm side along x (depth/height 3.3), and the printed collar ears (blunt prisms)", value=1.2,
  unit="-", basis="Hoerner, Fluid-Dynamic Drag, ch. 3, and Delany & Sorensen NACA TN 3038: sharp rectangular "
  "sections at depth/height 3 have Cd 1.1-1.4 (on the height) at Re 1e3-1e4", status="UNVERIFIED")
A("ASM-B4-ESC", "ESC on its pad: 8 mm proud of the board, Cd 0.9", "LANRC 45 A board in heat-shrink with a 10 mm "
  "hook-and-loop strap, on the 1.2 mm PETG pad; frontal = pad height x (pad + ESC), blunt box of length/thickness ~5",
  value=[0.0068, 0.9], unit="m, -", basis="E1 has not published ESC dimensions (PRP-002); typical 45 A BLHeli_S "
  "board 5 mm thick + heat-shrink and strap; Hoerner ch. 3 blunt box", status="UNVERIFIED")
A("ASM-B4-WAKE-SENSE", "Cant sense per F4's motor map (k = +1)", "the side component of each canted thrust points "
  "toward the wing plane and outboard, so each hover wake leans away from the wing and inboard, and each disc's "
  "wing-side edge swings aft toward the tube", value=1, unit="-",
  basis="subsystems/flight-software/SPEC.md motor table and 'Cant sense' (CL-F4-MOTOR-MAP); D3's "
        "fin_detail.mount.cant_sense_UR +1 is the opposite (CR-B4-16)", status="PROPOSED")
A("ASM-B4-MIX", "Shear-layer spreading 0.08", "the slipstream edge mixing layer grows 0.08 m per metre "
  "downstream on each side", value=0.08, unit="-",
  basis="plane mixing layer vorticity thickness growth ~0.16-0.18 dx at velocity ratio 0 (Brown and Roshko 1974); "
        "half toward each side")
A("ASM-B4-PITOT-ERR", "Pitot error limit 2 %", "thrust-dependent airspeed error at the probe tip must stay "
  "within 2 % of true airspeed (a constant bias is removed by ARSPD_RATIO; a thrust-dependent one is not)",
  value=0.02, unit="-", basis="B4 choice; ArduPilot airspeed calibration removes only a constant ratio")
A("ASM-B4-VRS", "Vortex-ring onset at 0.28 v_h", "vortex-ring state begins at a descent rate of about 0.28 times "
  "the hover induced velocity", value=0.28, unit="-",
  basis="Leishman, Principles of Helicopter Aerodynamics 2nd ed., sec. 2.14: VRS boundary from about -0.28 v_h "
        "(onset) to -1.0 v_h; conservative lower edge")
A("ASM-B4-BOOM", "Pitot boom 80 mm ahead of the pod front at z 0.045 m", "plug-in pitot boom on the pod nose, "
  "probe along body x, tip 80 mm ahead of the pod front face, 30 mm above the pod base", value=[0.08, 0.045],
  unit="m", basis="B4 placement (CR-B4-05); D2 draws POD-006; the tip x follows pod.x_le_m if the pod moves",
  status="PROPOSED")
A("ASM-B4-SPAN-AR", "Fin effective aspect ratio doubles on the wing", "the wing acts as an end plate at the fin "
  "root inside the slipstream", value=2.0, unit="-", basis="image method for a plate ending on a wall")


S = kit.source
S("SRC-B4-APC-PER3", "APC PER3 performance files 11x4.5MR, 11x4.7SF, 11x5.5E, 12x4.5MR", "datasheet",
  url="https://www.apcprop.com/files/PER3_11x45MR.dat", checked="2026-11-09",
  where="tables at 5000-9000 rpm copied into redesign/team/B4/data/apc_per3_*.csv; also PER3_11x47SF.dat, "
        "PER3_11x55E.dat, PER3_12x45MR.dat",
  note="APC blade-element predictions (v2022-0915), not measurements; transcription checked by CALC-B4-DATA")
S("SRC-B4-UIUC", "UIUC Propeller Database vol. 1, APC 11x4.7SF and 11x5.5E", "dataset",
  url="https://m-selig.ae.illinois.edu/props/volume-1/propDB-volume-1.html", checked="2026-11-09",
  where="apcsf_11x4.7_static_pg0526, apcsf_11x4.7_pg0533_6004, apce_11x5.5_static_kt0467, apce_11x5.5_kt0472_6000; "
        "copied into data/uiuc_measured.csv")
S("SRC-B4-APC-RPM", "APC suggested rpm limits", "datasheet", url="https://www.apcprop.com/technical-information/rpm-limits",
  checked="2026-11-09", where="MR 105,000/D(in); SF 65,000/D; Thin Electric 150,000/D")
S("SRC-B4-APC-PRODUCTS", "APC product pages 11x4.5MR and 11x5.5EP", "datasheet",
  url="https://www.apcprop.com/product/11x5-5ep/", checked="2026-11-09",
  where="11x4.5MR LP11045MR 0.60 oz (17 g) $3.83, adapter rings not included; 11x5.5EP LP11055EP 0.81 oz (23 g) "
        "$4.17, reverse rotation, LPAR06E rings included; https://www.apcprop.com/product/11x4-5mr/")
S("SRC-B4-ZHOU-ROTOR", "Zhou, Ning, Hu: rotor-to-rotor interaction of small UAV rotors (ISPIV)", "paper",
  url="https://journals.library.iit.edu/index.php/ISPIV/article/view/39", checked="2026-11-09",
  where="side-by-side rotors at 0.05-1.0 D tip gap: mean thrust within 2 %, thrust fluctuation +240 % and +3 dB at 0.05 D",
  note="abstract and a citing review read; full paper not read", status="UNVERIFIED")


# ---------------------------------------------------------------- 1. data transcription check
S("SRC-B4-APC-11X7E", "APC PER3 performance file 11x7E and product page 11x7E (LP11070E)", "datasheet",
  url="https://www.apcprop.com/files/PER3_11x7E.dat", checked="2026-11-13",
  where="tables at 5000-8000 rpm copied into redesign/team/B4/data/apc_per3_11x7E.csv; product page "
        "https://www.apcprop.com/product/11x7e/ : LP11070E, $4.17, 0.81 oz (23 g), hub 0.80 in x 0.41 in, 1/4 in shaft, "
        "adapter rings LPAR06E. https://www.apcprop.com/product/11x7ep/ returns HTTP 404 and a web search on "
        "2026-11-13 finds no 11x7EP / LP11070EP: the only reverse-rotation 11x7 found is the sport pusher LP11070P "
        "(about 40 g on retailer pages, a different blade)",
  note="APC blade-element predictions (v2022-0915), not measurements; transcription checked by CALC-B4-DATA")
kit.assumption("ASM-B4-AB-HOVER-MAX", "Hover power penalty allowed for a cruise prop", "hover pack power <= 1.10 x the "
               "11x5.5MR (measure M6 of the aero review: above +10 % stay on the MR)",
               basis="review/CDR-2026-11-13/CDR-aero.md 'What the team must measure' M6", value=1.10, unit="-")


@kit.calc("CALC-B4-DATA", title="APC data transcription check", cites=["SRC-B4-APC-PER3"],
          equation="Ct' = T / (rho n^2 D^4) ; Cp' = P / (rho n^3 D^5) from the printed N and W ; "
                   "error = max |Ct'/Ct - 1|, |Cp'/Cp - 1| over rows with Ct, Cp >= 0.02 (4-digit rounding < 0.25 %)",
          inputs={"rho": P + "env.rho_kgm3"}, units={"rho": "kg/m3"})
def data_check(rho):
    worst = 0.0
    rows = 0
    for prop, rs in DATA.items():
        D = PROPS[prop][1] * IN
        for r in rs:
            n = r["rpm"] / 60.0
            ct = r["T_N"] / (rho * n * n * D ** 4)
            cp = r["P_W"] / (rho * n ** 3 * D ** 5)
            if r["Ct"] >= 0.02:
                worst = max(worst, abs(ct / r["Ct"] - 1))
            if r["Cp"] >= 0.02:
                worst = max(worst, abs(cp / r["Cp"] - 1))
            rows += 1
    return {"max_rel_err": worst, "rows": rows}


# ---------------------------------------------------------------- 2. motor constants (E1 owns them; B4 uses them to rank props)
E1_MOTOR = {"kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK",
            "tcu": "ASM-E1-TCOPPER"}


def _motor(kv, rm, i0, esc, pack, tcu, hot=True):
    """E1's constants: winding R at 80 degC (hot) or 25 degC, plus ESC and pack/harness resistance; ESC fixed loss."""
    r = rm * (1 + tcu[0] * (tcu[1] - 25.0)) if hot else rm
    return Motor(kv, i0, r + esc[0] + pack[0]), esc[1]


# ---------------------------------------------------------------- 3. static: hover point, full-throttle rpm per prop
@kit.calc("CALC-B4-STATIC", title="Static operating points, five candidate props", assumes=["ASM-B4-VSAG"],
          cites=["SRC-B4-APC-PER3", "SRC-B4-APC-RPM"],
          equation="hover: T_h = k_dl m g / (4 cos cant) -> rpm, P_shaft from Ct, Cp ; FM = T^1.5 / sqrt(2 rho A) / "
                   "P_shaft ; full throttle: (V - rpm/Kv)/R = Q/Kt + I0 (E1 constants, hot winding) ; "
                   "T/W (bus held, no current limit) = 4 T_max cos cant / (k_dl m g) ; rpm limit = K / D_in (APC)",
          inputs=dict(E1_MOTOR, v="P:battery.v_nom", v_sag="ASM-B4-VSAG", m=P + "requirements.mtow_gate_kg",
                      k_dl=P + "propulsion.download_factor", g=P + "env.g_ms2", rho=P + "env.rho_kgm3",
                      cant=P + "propulsion.stations.cant_deg"),
          units={"v": "V", "m": "kg", "rho": "kg/m3", "cant": "deg"})
def static_points(kv, rm, i0, esc, pack, tcu, v, v_sag, m, k_dl, g, rho, cant):
    mot_hot, _ = _motor(kv, rm, i0, esc, pack, tcu, hot=True)
    mot, esc_w = _motor(kv, rm, i0, esc, pack, tcu, hot=False)
    out = {}
    cc = math.cos(math.radians(cant))                   # canted thrust: only T cos(cant) lifts
    Th = k_dl * m * g / 4.0 / cc
    for prop, (_, d_in, klim, *_rest) in PROPS.items():
        D = d_in * IN
        A_d = math.pi * D * D / 4
        res = {}
        for tag, vs in (("", v), ("_sag", v_sag)):
            rpm = mot_hot.full_throttle_rpm(prop, vs, 0.0, rho)
            T, Pw, *_ = thrust_power(prop, rpm, 0.0, rho)
            res["tmax_n" + tag] = T
            res["rpm_max" + tag] = rpm
            res["i_max_a" + tag] = mot_hot.current(Pw / (2 * math.pi * rpm / 60.0))
            res["tw_unlimited" + tag] = 4 * T * cc / (k_dl * m * g)
        rpm_h = rpm_for_thrust(prop, Th, 0.0, rho)
        _, Ph, *_ = thrust_power(prop, rpm_h, 0.0, rho)
        Pin, Ih = mot.p_in(rpm_h, Ph / (2 * math.pi * rpm_h / 60.0))
        res.update({"hover_rpm": rpm_h, "hover_shaft_w": Ph, "hover_in_w": Pin + esc_w, "hover_i_motor_a": Ih,
                    "hover_fm": Th ** 1.5 / math.sqrt(2 * rho * A_d) / Ph, "disk_loading_npm2": Th / A_d,
                    "hover_torque_nm": Ph / (2 * math.pi * rpm_h / 60.0),
                    "rpm_limit": klim / d_in, "rpm_limit_margin": klim / d_in / res["rpm_max"] - 1,
                    "hover_pack_w": 4 * (Pin + esc_w)})
        for k, val in res.items():
            out[f"{k}__{prop}"] = val
    out["hover_thrust_per_prop_n"] = Th
    return out


# ---------------------------------------------------------------- 4. cruise: lightly loaded operating point
def _cruise(prop, T, V, rho, mot, esc_w=0.0):
    rpm = rpm_for_thrust(prop, T, V, rho)
    Tc, Pw, J, ct, cp = thrust_power(prop, rpm, V, rho)
    Pin, I = mot.p_in(rpm, Pw / (2 * math.pi * rpm / 60.0))
    Pin += esc_w
    return {"rpm": rpm, "J": J, "eta_prop": T * V / Pw, "shaft_w": Pw, "in_w": Pin, "eta_motor": Pw / Pin,
            "eta_total": T * V / Pin}


@kit.calc("CALC-B4-CRUISE", title="Cruise operating point, five props, all four motors running",
          cites=["SRC-B4-APC-PER3"],
          equation="T = m g / (L/D) / 4 ; solve rpm: Ct(J) rho n^2 D^4 = T at V ; eta_p = T V / P_shaft ; "
                   "P_in = (rpm/Kv + I R) I + P_esc (E1 constants, 25 degC winding) ; total = 4 P_in",
          inputs=dict(E1_MOTOR, m=P + "requirements.mtow_gate_kg", ld=P + "performance.ld_cruise",
                      V=P + "performance.cruise_ms", g=P + "env.g_ms2", rho=P + "env.rho_kgm3"),
          units={"m": "kg", "V": "m/s", "rho": "kg/m3"})
def cruise_points(kv, rm, i0, esc, pack, tcu, m, ld, V, g, rho):
    mot, esc_w = _motor(kv, rm, i0, esc, pack, tcu, hot=False)
    T = m * g / ld / 4.0
    out = {"thrust_per_prop_n": T}
    for prop in PROPS:
        cr = _cruise(prop, T, V, rho, mot, esc_w)
        for k, val in cr.items():
            out[f"{k}__{prop}"] = val
        out[f"pack_w__{prop}"] = 4 * cr["in_w"]
        c2 = _cruise(prop, 2 * T, V, rho, mot, esc_w)       # option: two motors stopped (windmill drag not included)
        out[f"pack_w_2motor__{prop}"] = 2 * c2["in_w"]
    return out
# ---------------------------------------------------------------- 4b. CDR-15: 11x7E against the 11x5.5MR (cruise A/B)
def _drag_n(V, m, g, rho, S, cd0, k):
    q = 0.5 * rho * V * V
    cl = m * g / (q * S)
    return q * S * (cd0 + k * cl * cl)


def _level_speed(prop, duty, v_pack, mot, m, g, rho, S, cd0, k):
    """Level speed where four props at motor output `duty` on a v_pack bus give thrust = drag (upper root)."""
    def f(V):
        rpm = mot.full_throttle_rpm(prop, duty * v_pack, V, rho)
        return 4 * thrust_power(prop, rpm, V, rho)[0] - _drag_n(V, m, g, rho, S, cd0, k)
    if f(14.0) <= 0:                 # not enough thrust to hold 14 m/s at this output
        return 14.0
    return _bisect(f, 14.0, 40.0)


@kit.calc("CALC-B4-PROP-AB", title="Prop A/B for the cruise leg: 11x5.5MR, 11x5.5E, 11x7E at 16 and 17 m/s, hover cost, "
          "level speed at the fixed-wing throttle cap (CDR-15, CDR-AE-08)",
          cites=["SRC-B4-APC-PER3", "SRC-B4-APC-11X7E", "SRC-B4-APC-RPM"], assumes=["ASM-B4-AB-HOVER-MAX"],
          equation="CD0 = CL_c / (L/D) - k CL_c^2 at the cruise key, k = 1 / (pi AR e) ; D(V) = q S (CD0 + k CL^2) ; "
                   "T = D / 4 -> rpm, P_shaft (APC), P_in (E1 motor, 25 degC) ; pack = 4 P_in ; hover as CALC-B4-STATIC ; "
                   "level speed: 4 T(rpm(duty x 16.8 V, V), V) = D(V), hot winding ; THR_MAX for V_H: duty with "
                   "V_level = VD / 1.25",
          inputs=dict(E1_MOTOR, m=P + "requirements.mtow_gate_kg", ld=P + "performance.ld_cruise",
                      vc=P + "performance.cruise_ms", g=P + "env.g_ms2", rho=P + "env.rho_kgm3", b=P + "wing.span_m",
                      c=P + "wing.chord_m", e=P + "wing.oswald_e", vd=P + "requirements.vd_ms",
                      k_dl=P + "propulsion.download_factor", cant=P + "propulsion.stations.cant_deg",
                      ocv="ASM-E1-OCV"),
          units={"m": "kg", "vc": "m/s", "rho": "kg/m3", "b": "m", "c": "m", "vd": "m/s", "cant": "deg"})
def prop_ab(kv, rm, i0, esc, pack, tcu, m, ld, vc, g, rho, b, c, e, vd, k_dl, cant, ocv):
    vfull = max(ocv)
    mot, esc_w = _motor(kv, rm, i0, esc, pack, tcu, hot=False)
    mot_hot, _ = _motor(kv, rm, i0, esc, pack, tcu, hot=True)
    S = b * c
    k = 1.0 / (math.pi * (b / c) * e)
    cl_c = m * g / (0.5 * rho * vc * vc * S)
    cd0 = cl_c / ld - k * cl_c * cl_c
    out = {"cd0": cd0, "k": k, "vh_req": vd / 1.25}
    cc = math.cos(math.radians(cant))
    Th = k_dl * m * g / 4.0 / cc
    for prop in ("11x5.5MR", "11x5.5E", "11x7E"):
        tag = prop.replace(".", "").replace("x", "X")
        for V in (16.0, 17.0, 18.0):
            T = _drag_n(V, m, g, rho, S, cd0, k) / 4.0
            cr = _cruise(prop, T, V, rho, mot, esc_w)
            out[f"drag_n_{V:.0f}"] = 4 * T
            out[f"pack_w_{V:.0f}__{tag}"] = 4 * cr["in_w"]
            out[f"eta_{V:.0f}__{tag}"] = cr["eta_prop"]
            out[f"rpm_{V:.0f}__{tag}"] = cr["rpm"]
            out[f"J_{V:.0f}__{tag}"] = cr["J"]
        rpm_h = rpm_for_thrust(prop, Th, 0.0, rho)
        _, Ph, *_ = thrust_power(prop, rpm_h, 0.0, rho)
        Pin, _ih = mot.p_in(rpm_h, Ph / (2 * math.pi * rpm_h / 60.0))
        out[f"hover_pack_w__{tag}"] = 4 * (Pin + esc_w)
        out[f"hover_rpm__{tag}"] = rpm_h
        out[f"v_level_thr70__{tag}"] = _level_speed(prop, 0.704, vfull, mot_hot, m, g, rho, S, cd0, k)
        out[f"thr_for_vh__{tag}"] = _bisect(
            lambda a, prop=prop: _level_speed(prop, a, vfull, mot_hot, m, g, rho, S, cd0, k) - vd / 1.25, 0.30, 0.95)
        rpm_ft = mot_hot.full_throttle_rpm(prop, vfull, 0.0, rho)
        v70 = out[f"v_level_thr70__{tag}"]
        out[f"rpm_level_thr70__{tag}"] = mot_hot.full_throttle_rpm(prop, 0.704 * vfull, v70, rho)
        out[f"rpm_static_thr70__{tag}"] = mot_hot.full_throttle_rpm(prop, 0.704 * vfull, 0.0, rho)
        out[f"rpm_full_fresh__{tag}"] = rpm_ft
        out[f"rpm_limit__{tag}"] = PROPS[prop][2] / PROPS[prop][1]
    for V in (16, 17):
        out[f"ratio_{V}__11X7E_over_MR"] = out[f"pack_w_{V}__11X7E"] / out[f"pack_w_{V}__11X55MR"]
        out[f"ratio_{V}__11X55E_over_MR"] = out[f"pack_w_{V}__11X55E"] / out[f"pack_w_{V}__11X55MR"]
    out["hover_ratio__11X7E_over_MR"] = out["hover_pack_w__11X7E"] / out["hover_pack_w__11X55MR"]
    out["hover_ratio__11X55E_over_MR"] = out["hover_pack_w__11X55E"] / out["hover_pack_w__11X55MR"]
    out["mass_delta_g_4props__11X7E"] = 4 * (PROPS["11x7E"][3] - PROPS["11x5.5MR"][3])
    return out


# ---------------------------------------------------------------- 5. download (installed thrust loss in hover)
def _v_axial(vi, x, R):
    return vi * (1 + x / math.sqrt(x * x + R * R))


def _r_slip(x, R):
    return R / math.sqrt(1 + x / math.sqrt(x * x + R * R))


def _z_surf(c):
    """Worse of the S5010 upper and lower surface heights (m from the chord plane) at body station x."""
    up, lo = _airfoil_surfaces()
    xu, zu = [p[0] for p in up], [p[1] for p in up]
    xl, zl = [p[0] for p in lo], [p[1] for p in lo]

    def f(x):
        xc = min(max(x / c, 0.0), 1.0)
        return max(_interp(xu, zu, xc), -_interp(xl, zl, xc)) * c
    return f


def _fin_top(x, x_mount, fin_te, z_le_top, h_fin):
    """Half-fin top edge (fin_detail.fin.top_edge): straight from the station-collar top at the LE to the TE tip."""
    return z_le_top + (h_fin - z_le_top) * (x - x_mount) / (fin_te - x_mount)


# Geometry keys shared by the download, cruise-items and swirl calculations (D3's R3 fin, subsystems/fins/params.json)
GEO_IN = {"D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
          "x_mount": P + "propulsion.stations.x_mount_m", "y_m": P + "propulsion.stations.y_m",
          "z_m": P + "propulsion.stations.z_m", "cant": P + "propulsion.stations.cant_deg", "k": "ASM-B4-WAKE-SENSE",
          "stack": P + "fin_detail.mount.prop_stack_m", "d_tube": P + "fins.tube.od_m",
          "tube_len": P + "fins.tube.length_m", "d_motor": P + "propulsion.motor_diameter_m",
          "fin_te": P + "fins.te_x_m", "h_fin": P + "fins.half_height_m", "c": P + "wing.chord_m",
          "col_wall": P + "fin_detail.mount.collar_wall_m", "grip": P + "fin_detail.mount.grip_m",
          "m_ear": P + "fin_detail.mount.ear_len_m", "m_ear_h": P + "fin_detail.mount.ear_h_m",
          "sc_h": P + "fin_detail.station_collar.height_m", "sc_gap": P + "fin_detail.station_collar.gap_m",
          "sc_wall": P + "fin_detail.station_collar.ring_wall_m", "sc_ear": P + "fin_detail.station_collar.ear_len_m",
          "br_t": P + "fin_detail.brace.t_m", "br_y": P + "fin_detail.brace.anchor_y_m",
          "anc_proud": P + "fin_detail.anchor.proud_m", "spar_x": P + "wing.spar.x_m",
          "esc_x0": P + "fin_detail.esc_pad.x0_m", "esc_len": P + "fin_detail.esc_pad.len_m",
          "esc_h": P + "fin_detail.esc_pad.h_m", "esc_z": P + "fin_detail.esc_pad.z_m",
          "esc_pad_t": P + "fin_detail.esc_pad.t_m", "esc": "ASM-B4-ESC", "cd": "ASM-B4-CD-TUBE",
          "cd_s": "ASM-B4-CD-STRIP"}
GEO_U = {"D": "m", "x_prop": "m", "x_mount": "m", "y_m": "m", "z_m": "m", "cant": "deg", "stack": "m", "d_tube": "m",
         "tube_len": "m", "d_motor": "m", "fin_te": "m", "h_fin": "m", "c": "m", "col_wall": "m", "grip": "m",
         "m_ear": "m", "m_ear_h": "m", "sc_h": "m", "sc_gap": "m", "sc_wall": "m", "sc_ear": "m", "br_t": "m",
         "br_y": "m", "anc_proud": "m", "spar_x": "m", "esc_x0": "m", "esc_len": "m", "esc_h": "m", "esc_z": "m",
         "esc_pad_t": "m"}


GROUPS = ("tube", "collar_m", "collar_s", "ear", "brace", "esc")


def _items(g):
    """Bluff items on the upper-right station (the others mirror it): list of (group, x, y, z, frontal area m2, Cd).
    Groups: tube (bare 22 mm tube), collar_m / collar_s (mount / station collar, increment over the tube), ear (the
    pinch ear outboard and the brace ear inboard),
    brace (10 x 3 mm strip, area normal to x), esc (ESC + pad, in 10 strips over the pad height)."""
    zs = _z_surf(g["c"])
    out = []
    z_end = g["tube_len"] / 2
    d_mc = g["d_tube"] + 2 * g["col_wall"]
    d_sc = g["d_tube"] + 2 * g["sc_wall"]
    mc = (z_end - g["grip"], z_end)
    sc_top = z_end - g["grip"] - g["sc_gap"]
    sc = (sc_top - g["sc_h"], sc_top)
    z0 = zs(g["x_mount"])
    n = 200
    dz = (z_end - z0) / n
    for i in range(n):
        z = z0 + (i + 0.5) * dz
        out.append(("tube", g["x_mount"], g["y_m"], z, g["d_tube"] * dz, g["cd"]))
        if mc[0] <= z < mc[1]:
            out.append(("collar_m", g["x_mount"], g["y_m"], z, (d_mc - g["d_tube"]) * dz, g["cd"]))
        elif sc[0] <= z < sc[1]:
            out.append(("collar_s", g["x_mount"], g["y_m"], z, (d_sc - g["d_tube"]) * dz, g["cd"]))
    out.append(("ear", g["x_mount"], g["y_m"] + d_mc / 2 + g["m_ear"] / 2, sum(mc) / 2,
                g["m_ear"] * g["m_ear_h"], g["cd_s"]))                                   # pinch ear, outboard
    ear = (g["x_mount"], g["y_m"] - d_sc / 2 - g["sc_ear"] / 2, sum(sc) / 2)            # brace ear, inboard
    out.append(("ear", ear[0], ear[1], ear[2], g["sc_ear"] * g["sc_h"], g["cd_s"]))
    anc = (g["spar_x"], g["br_y"], zs(g["spar_x"]) + g["anc_proud"] / 2)
    L = math.dist(ear, anc)
    perp = math.sqrt(max(1 - ((anc[0] - ear[0]) / L) ** 2, 0.0))
    nb = 100
    for i in range(nb):
        t = (i + 0.5) / nb
        p = [ear[j] + t * (anc[j] - ear[j]) for j in range(3)]
        out.append(("brace", p[0], p[1], p[2], g["br_t"] * L / nb * perp, g["cd_s"]))
    t_esc, cd_esc = g["esc"]
    for i in range(10):
        z = g["esc_z"] - g["esc_h"] / 2 + (i + 0.5) * g["esc_h"] / 10
        out.append(("esc", g["esc_x0"], g["y_m"], z, (g["esc_pad_t"] + t_esc) * g["esc_h"] / 10, cd_esc))
    return out, {"brace_len_m": L, "brace_perp": perp, "z_tube_end": z_end, "sc_top": sc_top}


def _hover_items(g, vi, rho, pf, k):
    """Hover drag (N) per item group on one station's slipstream, wake leaning with sense k."""
    R = g["D"] / 2
    hub = hub_centre(g["x_prop"], g["y_m"], g["z_m"], g["cant"], k, g["stack"])
    e = wake_axis(g["y_m"], g["z_m"], g["cant"], k)
    items, info = _items(g)
    D = dict.fromkeys(GROUPS, 0.0)
    inside = {"brace": 0.0}
    for grp, x, y, z, A_f, cd in items:
        yc, zc, s_ax = wake_centre(x, hub, e)
        if s_ax <= 0:
            continue
        rs = _r_slip(s_ax, R)
        d = math.hypot(y - yc, z - zc)
        if d < rs and d > g["d_motor"] / 2 * rs / R:          # inside the slipstream, outside the motor-can shadow
            v = _v_axial(vi, s_ax, R)
            D[grp] += cd * 0.5 * rho * v * v * pf * A_f
            if grp == "brace":
                inside["brace"] += A_f
    info["brace_frac_in_wake"] = inside["brace"] / (g["br_t"] * info["brace_len_m"] * info["brace_perp"])
    # ESC pad outer edge (wing side) in the leaning slipstream (D3 CL-D3-ESC-WASH uses the untilted axis)
    yc, zc, s_ax = wake_centre(g["esc_x0"] + g["esc_len"], hub, e)
    info["esc_outer_edge_over_rs"] = math.hypot(g["y_m"] - yc, zc - (g["esc_z"] - g["esc_h"] / 2)) / _r_slip(s_ax, R)
    return D, info


@kit.calc("CALC-B4-DOWNLOAD", title="Hover download on tube, collars, braces, ESC pads, half-fins, feet and wing",
          assumes=["ASM-B4-CD-TUBE", "ASM-B4-PROFILE", "ASM-B4-FOOT", "ASM-B4-MIX", "ASM-B4-CD-STRIP", "ASM-B4-ESC",
                   "ASM-B4-WAKE-SENSE"],
          cites=["SRC-S5010"],
          equation="v_i = sqrt(T / 2 rho A) ; v(s) = v_i (1 + s / sqrt(s^2 + R^2)) ; r_s = R / sqrt(v/v_i) ; wake axis "
                   "along the canted shaft from the hub (cant, sense k) ; item drag = Cd q A for every tube, collar, "
                   "ear, brace and ESC element inside r_s and outside the motor-can shadow ; fin: 2 Cf q h_w dx over "
                   "the wetted strip of the half-fin plane (top edge from the station collar to the TE tip) ; base "
                   "0.5 q t h_w (t = board x layers) ; foot q A at half speed ; wing: reach = r_s + mix s, gap = "
                   "z_c - reach - z_surf ; k = 1 + D/T",
          inputs=dict(GEO_IN, m=P + "requirements.mtow_gate_kg", g=P + "env.g_ms2", rho=P + "env.rho_kgm3",
                      foot_h=P + "cg.foot_height_m", prof="ASM-B4-PROFILE", a_foot="ASM-B4-FOOT", mix="ASM-B4-MIX",
                      board_t=P + "fins.board_t_m", layers=P + "fins.layers"),
          units=dict(GEO_U, m="kg", board_t="m"))
def download(m, g, rho, foot_h, prof, a_foot, mix, board_t, layers, **geo):
    G = geo
    R = G["D"] / 2
    T = m * g / 4.0
    vi = math.sqrt(T / (2 * rho * math.pi * R * R))
    nu = 1.5e-5
    zs = _z_surf(G["c"])
    z_le_top = G["tube_len"] / 2 - G["grip"] - G["sc_gap"]
    x0 = G["x_mount"] + G["d_tube"] / 2
    res = {}
    for tag, pf, k in (("", 1.0, G["k"]), ("_high", prof, G["k"]), ("_alt", 1.0, -G["k"])):
        hub = hub_centre(G["x_prop"], G["y_m"], G["z_m"], G["cant"], k, G["stack"])
        e = wake_axis(G["y_m"], G["z_m"], G["cant"], k)
        Di, info = _hover_items(G, vi, rho, pf, k)
        # half-fin skin friction on the wetted strip
        n = 40
        dx = (G["fin_te"] - x0) / n
        D_fin, hw_mid = 0.0, 0.0
        c_f = G["fin_te"] - x0
        for i in range(n):
            x = x0 + (i + 0.5) * dx
            yc, zc, s_ax = wake_centre(x, hub, e)
            rs = _r_slip(s_ax, R)
            off = abs(G["y_m"] - yc)
            if off >= rs:
                continue
            half = math.sqrt(rs * rs - off * off)
            lo = max(zc - half, zs(x))
            hi = min(zc + half, _fin_top(x, G["x_mount"], G["fin_te"], z_le_top, G["h_fin"]))
            hw = max(hi - lo, 0.0)
            v = _v_axial(vi, s_ax, R)
            cf = 0.074 / (v * c_f / nu) ** 0.2
            D_fin += 2 * cf * 0.5 * rho * v * v * pf * hw * dx
            if i == n // 2:
                hw_mid = hw
        # base drag of the blunt fin TE and the foot
        yc, zc, s_ax = wake_centre(G["fin_te"], hub, e)
        rs = _r_slip(s_ax, R)
        off = abs(G["y_m"] - yc)
        half = math.sqrt(max(rs * rs - off * off, 0.0))
        hw_te = max(min(zc + half, G["h_fin"]) - max(zc - half, zs(G["fin_te"])), 0.0)
        v_b = _v_axial(vi, s_ax, R)
        D_base = 0.5 * 0.5 * rho * v_b ** 2 * pf * board_t * layers * hw_te
        d_foot = math.hypot(G["y_m"] - yc, G["h_fin"] - zc)
        v_ft = 0.5 * v_b if d_foot < G["d_motor"] else v_b       # inside the hub-wake deficit near the axis
        D_foot = (1.0 * 0.5 * rho * v_ft ** 2 * a_foot) if d_foot < rs else 0.0
        # wing beside the disc
        D_w, gap_min, x_gap = _wing_strip(rho, vi, R, hub, e, G["c"], mix, pf, nu, zs)
        Dt = sum(Di.values()) + D_fin + D_base + D_foot + D_w
        res["k" + tag] = 1 + Dt / T
        res["wing_gap_min_m" + tag] = gap_min
        if tag == "_alt":
            continue
        for grp, val in Di.items():
            res[f"{grp}_n{tag}"] = val
        if not tag:
            res.update({"vi_ms": vi, "fin_n": D_fin, "fin_base_n": D_base, "foot_n": D_foot, "wing_n": D_w,
                        "wing_gap_min_x_m": x_gap, "fin_wetted_h_mid_m": hw_mid, "fin_wetted_h_te_m": hw_te,
                        "disc_edge_over_chord_plane_m": hub[2] - R, "wake_lean_z_per_m": e[2] / e[0],
                        "wake_lean_y_per_m": e[1] / e[0], "brace_len_m": info["brace_len_m"],
                        "brace_frac_in_wake": info["brace_frac_in_wake"],
                        "esc_outer_edge_over_rs": info["esc_outer_edge_over_rs"],
                        "items_n": sum(Di[q] for q in GROUPS if q != "tube"),
                        "tube_x_behind_disc_m": G["x_mount"] - hub[0]})
    return res


def _wing_strip(rho, vi, R, hub, e, c, mix, pf, nu, zs, n=64):
    """Wing beside the disc: the slipstream (plus its mixing layer) reaching the S5010 surface at the fin station.
    Returns (download N for one disc, minimum gap m, x of the minimum gap m). The worse of the upper and lower
    surfaces is used for every disc (they mirror)."""
    D_w, gap_min, x_gap = 0.0, float("inf"), 0.0
    h = c / n
    for i in range(n + 1):
        x = i * h
        yc, zc, s_ax = wake_centre(x, hub, e)
        if s_ax <= 0:
            continue
        reach = _r_slip(s_ax, R) + mix * s_ax
        z_s = zs(x)
        gap = (zc - z_s) - reach
        if gap < gap_min:
            gap_min, x_gap = gap, x
        if gap < 0:
            w = 2 * math.sqrt(max(reach * reach - (zc - z_s) ** 2, 0.0))
            v = _v_axial(vi, s_ax, R)
            cf = 0.074 / max(v * max(x, h) / nu, 1e3) ** 0.2
            wk = 0.5 if i in (0, n) else 1.0
            D_w += wk * cf * 0.5 * rho * v * v * pf / 3.0 * w * h
    return D_w, gap_min, x_gap


# ---------------------------------------------------------------- 5b. cruise drag of the collars, braces and ESC pads
@kit.calc("CALC-B4-ITEMS-CRUISE", title="Cruise drag of the R3 fin hardware (collars, ears, braces, ESC pads)",
          assumes=["ASM-B4-CD-TUBE", "ASM-B4-CD-STRIP", "ASM-B4-ESC"],
          equation="T = m g / (L/D) / 4 ; v from T = 2 rho A v (V + v) ; inside the slipstream (r < R about the "
                   "x-parallel cruise wake) u = V + v (1 + s / sqrt(s^2 + R^2)), else V ; D = sum Cd 0.5 rho u^2 A "
                   "x 4 stations ; dCD0 = D / (q S), S = b c ; share = D / (m g / (L/D)) ; dP = P_cruise x share",
          inputs=dict(GEO_IN, m=P + "requirements.mtow_gate_kg", g=P + "env.g_ms2", rho=P + "env.rho_kgm3",
                      ld=P + "performance.ld_cruise", V=P + "performance.cruise_ms", b=P + "wing.span_m",
                      Pc="CL-B4-CRUISE-W"),
          units=dict(GEO_U, m="kg", V="m/s", b="m", Pc="W"))
def items_cruise(m, g, rho, ld, V, b, Pc, **geo):
    G = geo
    R = G["D"] / 2
    T = m * g / ld / 4
    v = (-V + math.sqrt(V * V + 2 * T / (rho * math.pi * R * R))) / 2
    hub = hub_centre(G["x_prop"], G["y_m"], G["z_m"], G["cant"], G["k"], G["stack"])
    items, _ = _items(G)
    D = dict.fromkeys(GROUPS, 0.0)
    for grp, x, y, z, A_f, cd in items:
        s_ax = x - hub[0]
        u = V + v * (1 + s_ax / math.sqrt(s_ax * s_ax + R * R)) if math.hypot(y - hub[1], z - hub[2]) < R else V
        D[grp] += 4 * cd * 0.5 * rho * u * u * A_f
    q = 0.5 * rho * V * V
    S = b * G["c"]
    Dn = sum(D[q] for q in GROUPS if q != "tube")
    Dnb = D["collar_m"] + D["ear"] + D["esc"]                # items B1 rev 3 does not carry (ASM-B1-DRAG-ADDONS)
    Dc = m * g / ld
    out = {f"{k}_n": val for k, val in D.items()}
    out.update({"items_n": Dn, "items_dcd0": Dn / (q * S), "items_share_of_cruise_drag": Dn / Dc,
                "items_pack_w": Pc * Dn / Dc, "cruise_drag_n": Dc, "v_induced_ms": v,
                "brace_n_each": D["brace"] / 4, "brace_dcd0": D["brace"] / (q * S),
                "not_in_b1_n": Dnb, "not_in_b1_dcd0": Dnb / (q * S)})
    return out


# ---------------------------------------------------------------- 6. slipstream vs elevons and wing
@kit.calc("CALC-B4-WAKE", title="Slipstream edge versus elevons and wing (canted, leaning hover wake)",
          assumes=["ASM-B4-MIX", "ASM-B4-WAKE-SENSE"],
          equation="hover: inner edge z = z_c(x) - r_s(s) - mix s, wake centre z_c from the hub along the canted "
                   "shaft ; elevon tip z = c_e sin(delta_max) ; cruise: wake along x, r_s ~ R (lightly loaded) ; "
                   "gap = edge - surface ; _alt = mirrored spin map (wake leans toward the wing)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "y_m": P + "propulsion.stations.y_m", "z_m": P + "propulsion.stations.z_m",
                  "cant": P + "propulsion.stations.cant_deg", "k": "ASM-B4-WAKE-SENSE",
                  "stack": P + "fin_detail.mount.prop_stack_m", "c": P + "wing.chord_m", "tc": P + "wing.t_c",
                  "fe": P + "wing.elevon.chord_frac", "defl": P + "wing.elevon.deflection_deg", "mix": "ASM-B4-MIX"},
          units={"m": "kg", "D": "m", "x_prop": "m", "y_m": "m", "z_m": "m", "cant": "deg", "stack": "m", "c": "m"})
def wake_vs_surfaces(m, g, rho, D, x_prop, y_m, z_m, cant, k, stack, c, tc, fe, defl, mix):
    R = D / 2
    x_hinge = c * (1 - fe)
    ce = c * fe
    z_elevon = ce * math.sin(math.radians(max(abs(d) for d in defl)))
    out = {}
    for tag, kk in (("", k), ("_alt", -k)):
        hub = hub_centre(x_prop, y_m, z_m, cant, kk, stack)
        e = wake_axis(y_m, z_m, cant, kk)
        edges = []
        for name, x in (("hinge", x_hinge), ("te", c)):
            yc, zc, s_ax = wake_centre(x, hub, e)
            edge = zc - _r_slip(s_ax, R) - mix * s_ax
            out[f"hover_edge_z_{name}_m{tag}"] = edge
            edges.append(edge)
        out["hover_gap_elevon_m" + tag] = min(edges) - z_elevon
    for name, x in (("hinge", x_hinge), ("te", c)):
        xd = x - x_prop
        out[f"cruise_edge_z_{name}_m"] = z_m - R - mix * xd
    out["elevon_tip_z_max_m"] = z_elevon
    out["cruise_gap_elevon_m"] = min(out["cruise_edge_z_hinge_m"], out["cruise_edge_z_te_m"]) - z_elevon
    out["cruise_gap_wing_surface_m"] = (z_m - R - mix * (0.3 * c - x_prop)) - tc * c / 2
    return out


# ---------------------------------------------------------------- 7. pitot placement (actuator-disk vortex cylinders)
@kit.calc("CALC-B4-PITOT-TIP", title="Pitot tip x station from the pod nose and the boom", assumes=["ASM-B4-BOOM"],
          equation="x_tip = pod.x_le_m - boom", inputs={"pod_x": P + "pod.x_le_m", "boom": "ASM-B4-BOOM"},
          units={"pod_x": "m"}, output="tip_x_m")
def pitot_tip(pod_x, boom):
    return pod_x - boom[0]


def pitot_candidates(tip, pod_x, x_prop):
    """name -> (x, y, z) of the probe tip, m. The chosen one is the pod-nose boom (POD-006) at params
    avionics.pitot_tip_xyz_m; the rest bracket it."""
    x, y, z = tip
    return {
        "pod_boom": (x, y, z),                                     # chosen (D-25): left channel, y -0.046
        "pod_face": (pod_x, y, z),                                 # no boom: probe flush with the pod front
        "pod_boom_long": (x - 0.10, y, z),                         # 100 mm longer boom
        "pod_boom_y0": (x, 0.0, z),                                # R2 position on the centreline
        "wing_LE_y0.15": (x_prop - 0.075, 0.15, 0.0),              # 75 mm boom on the inboard wing LE
        "wing_LE_y0.53": (x_prop - 0.075, 0.53, 0.0),              # 75 mm boom on the outboard wing LE
    }


def _induced_x(pt, disks, R, gamma, L, N):
    """x-component of the velocity induced by the four (leaning) vortex cylinders; nan inside a slipstream."""
    u = 0.0
    for hub, e in disks:
        d = [pt[i] - hub[i] for i in range(3)]
        X = sum(d[i] * e[i] for i in range(3))
        rv = [d[i] - X * e[i] for i in range(3)]
        r = math.sqrt(sum(q * q for q in rv))
        if r < R and X > 0:
            return float("nan")
        ua, ur = cylinder_vel(R, gamma, X, max(r, 1e-6), L, N)
        u += ua * e[0] + (ur * rv[0] / r if r > 1e-6 else 0.0)
    return u


@kit.calc("CALC-B4-PITOT", title="Prop-induced airspeed error at pitot candidates", assumes=["ASM-B4-PITOT-ERR",
          "ASM-B4-WAKE-SENSE"],
          equation="v from T = 2 rho A v (V + v) ; four semi-infinite vortex cylinders, gamma = 2 v, each from its "
                   "canted hub along the resultant of V (+x) and v (canted shaft) ; u = u_axial e + u_radial r_hat "
                   "(elliptic K, E) ; error = u_x / V ; grid: Simpson N = 100/200/400, wake length 20/40/80 R",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "y_m": P + "propulsion.stations.y_m", "z_m": P + "propulsion.stations.z_m",
                  "cant": P + "propulsion.stations.cant_deg", "k": "ASM-B4-WAKE-SENSE",
                  "stack": P + "fin_detail.mount.prop_stack_m",
                  "ld": P + "performance.ld_cruise", "V": P + "performance.cruise_ms",
                  "Vt": P + "performance.transition_min_ms", "lim": "ASM-B4-PITOT-ERR",
                  "pod_x": P + "pod.x_le_m", "tip": P + "avionics.pitot_tip_xyz_m", "tip_x": "CL-B4-PITOT-TIP-X"},
          units={"m": "kg", "D": "m", "x_prop": "m", "y_m": "m", "z_m": "m", "cant": "deg", "stack": "m",
                 "V": "m/s", "Vt": "m/s", "pod_x": "m", "tip": "m", "tip_x": "m"})
def pitot(m, g, rho, D, x_prop, y_m, z_m, cant, k, stack, ld, V, Vt, lim, pod_x, tip, tip_x):
    R = D / 2
    cands = pitot_candidates(tip, pod_x, x_prop)
    A_d = math.pi * R * R
    cases = {"cruise": (V, m * g / ld / 4), "transition": (Vt, m * g / 4), "hover": (0.0, m * g / 4)}
    out = {"tip_x_m": tip[0], "tip_y_m": tip[1], "tip_z_m": tip[2], "tip_ahead_of_disc_m": x_prop - tip[0],
           "tip_x_params_minus_boom_calc_m": tip[0] - tip_x}
    # self-tests: an isolated cylinder's disk centre sees gamma/2; the ring field is divergence-free
    out["selftest_centre_over_half_gamma"] = cylinder_ux(R, 1.0, 0.0, 1e-6, 80 * R, 400) / 0.5
    h, Xt, rt = 1e-5, -0.2, 0.3
    out["selftest_ring_divergence"] = abs(((rt + h) * ring_ur(R, Xt, rt + h) - (rt - h) * ring_ur(R, Xt, rt - h))
                                          / (2 * h) / rt + (ring_ux(R, Xt + h, rt) - ring_ux(R, Xt - h, rt)) / (2 * h))
    worst = {}
    for case, (Vc, T) in cases.items():
        v = (-Vc + math.sqrt(Vc * Vc + 2 * T / (rho * A_d))) / 2
        gam = 2 * v
        disks = []
        for sy in (1, -1):
            for sz in (1, -1):
                yy, zz = sy * y_m, sz * z_m
                disks.append((hub_centre(x_prop, yy, zz, cant, k, stack), wake_axis(yy, zz, cant, k, Vc, v)))
        for name, pt in cands.items():
            levels = [_induced_x(pt, disks, R, gam, Lr * R, N) for Lr, N in ((20, 100), (40, 200), (80, 400))]
            u = levels[-1]
            out[f"{case}__{name}__u_ms"] = u
            out[f"{case}__{name}__conv"] = abs(levels[-1] - levels[-2]) / (Vc if Vc > 0 else max(abs(u), 1e-9))
            if Vc > 0:
                out[f"{case}__{name}__err"] = u / Vc
                worst[name] = max(worst.get(name, 0.0), abs(u / Vc))
    for name, w in worst.items():
        out[f"worst_err__{name}"] = w
    best = min(worst, key=worst.get)
    out["best_candidate"] = list(cands).index(best)          # 0 pod_boom ... 5 wing_LE_y0.53
    out["best_worst_err"] = worst[best]
    out["max_conv"] = max(v for k_, v in out.items() if k_.endswith("__conv") and not k_.startswith("hover"))
    out["pitot_margin"] = 1 - worst["pod_boom"] / lim
    return out


# ---------------------------------------------------------------- 8. fin side force from swirl and cant (hover yaw)
def _fin_swirl(Th, Q, rho, G, ar_k, cant, k, n_x=40, n_z=80):
    """Side force on the upper-right half-fin from the swirl and the leaning canted wake, by area integration.
    Local incidence alpha = atan(v_n / v_a): v_n = swirl normal to the fin (Gamma_s / r, solid-body inside the
    contracted hub) plus the wake's lean across the fin (v_a e_y / e_x). Lift slope: Helmbold on AR = ar_k h_w / c.
    Returns the force, the moment about the body x-axis that adds to the reaction torque (sign-normalised so
    positive = with the prop's reaction torque) and the moment about the motor axis that opposes it."""
    R = G["D"] / 2
    vi = math.sqrt(Th / (2 * rho * math.pi * R * R))
    rh = G["d_motor"] / 2
    Gs = Q / (rho * vi * math.pi * (R * R - rh * rh))
    hub = hub_centre(G["x_prop"], G["y_m"], G["z_m"], cant, k, G["stack"])
    e = wake_axis(G["y_m"], G["z_m"], cant, k)
    zs = _z_surf(G["c"])
    z_le_top = G["tube_len"] / 2 - G["grip"] - G["sc_gap"]
    x0 = G["x_mount"] + G["d_tube"] / 2
    c_f = G["fin_te"] - x0
    dx = c_f / n_x
    cells = []
    hw_sum = 0.0
    for i in range(n_x):
        x = x0 + (i + 0.5) * dx
        yc, zc, s_ax = wake_centre(x, hub, e)
        rs = _r_slip(s_ax, R)
        va = _v_axial(vi, s_ax, R)
        rhc = rh * rs / R
        zb, zt = zs(x), _fin_top(x, G["x_mount"], G["fin_te"], z_le_top, G["h_fin"])
        dz = (zt - zb) / n_z
        hw = 0.0
        for j in range(n_z):
            z = zb + (j + 0.5) * dz
            dn, dh = G["y_m"] - yc, z - zc
            r = math.hypot(dn, dh)
            if r >= rs:
                continue
            hw += dz
            vt = Gs / r if r > rhc else Gs * r / (rhc * rhc)
            vn = k * vt * (-dh) / max(r, 1e-9) + va * e[1] / e[0]      # swirl + lean, along +y (outboard)
            cells.append((x, z, vn, va, dx * dz))
        hw_sum += hw
    h_w = hw_sum / n_x
    AR = ar_k * h_w / c_f
    a_eff = 2 * math.pi * AR / (2 + math.sqrt(AR * AR + 4))
    F = Mb = Ma = Fz = 0.0
    for x, z, vn, va, dA in cells:
        dF = a_eff * math.atan2(vn, va) * 0.5 * rho * (va * va + vn * vn) * dA
        F += dF
        Fz += dF * z
        Mb += k * z * dF                       # about body x, + = same sense as this prop's reaction torque
        Ma += k * (G["z_m"] - z) * dF          # about the motor axis, + = against the reaction torque (recovery)
    z_cp = Fz / F if F else 0.0
    return {"F": F, "M_body": Mb, "M_axis": Ma, "z_cp": z_cp, "h_w": h_w, "AR": AR, "c_f": c_f, "vi": vi,
            "a_eff": a_eff}


@kit.calc("CALC-B4-SWIRL", title="Fin side force from swirl and cant, and hover yaw authority",
          assumes=["ASM-B4-SPAN-AR", "ASM-B4-WAKE-SENSE"],
          equation="Gamma_s = Q / (rho v_i pi (R^2 - r_h^2)) ; v_t = Gamma_s / r ; v_n = v_t (normal part) + v_a "
                   "e_y/e_x (canted wake lean) ; alpha = atan(v_n / v_a) ; dF = a(AR) alpha q dA (Helmbold, "
                   "AR = 2 h_w / c) ; M_body = sum z dF (about the body x-axis) ; yaw factor = 1 + M_body / Q ; "
                   "yaw per N of differential thrust = (Q/T) factor + r_arm sin(cant) ; half-fin root moment = "
                   "F (z_cp - z_root)",
          inputs=dict(GEO_IN, Th="CL-B4-HOVER-T", Q="CL-B4-HOVER-Q", rho=P + "env.rho_kgm3", ar_k="ASM-B4-SPAN-AR"),
          units=dict(GEO_U, rho="kg/m3"))
def swirl(Th, Q, rho, ar_k, **geo):
    G = geo
    cant = G["cant"]
    r = _fin_swirl(Th, Q, rho, G, ar_k, cant, G["k"])
    r0 = _fin_swirl(Th, Q, rho, G, ar_k, 0.0, G["k"])
    r3 = _fin_swirl(Th, Q, rho, G, ar_k, 3.0, G["k"])
    arm = math.hypot(G["y_m"], G["z_m"])
    kq = Q / Th                                       # yaw moment per newton of differential thrust, isolated
    fac = 1 + r["M_body"] / Q
    zs = _z_surf(G["c"])
    x0 = G["x_mount"] + G["d_tube"] / 2
    z_root = sum(zs(x0 + (G["fin_te"] - x0) * i / 20) for i in range(21)) / 21
    out = {"fin_side_force_n": abs(r["F"]), "half_fin_cp_z_m": r["z_cp"],
           "half_fin_cp_above_root_m": r["z_cp"] - z_root,
           "half_fin_root_moment_nm": abs(r["F"]) * (r["z_cp"] - z_root), "half_fin_chord_m": r["c_f"],
           "half_fin_wetted_span_m": r["h_w"], "half_fin_aspect_ratio": r["AR"], "torque_nm": Q,
           "fin_body_moment_nm": r["M_body"], "f_axis_recovery": r["M_axis"] / Q,
           "yaw_authority_factor_mid": fac, "yaw_authority_factor_low": 1 + 0.5 * r["M_body"] / Q,
           "yaw_factor_nocant": 1 + r0["M_body"] / Q, "yaw_factor_cant3": 1 + r3["M_body"] / Q,
           "fin_side_force_nocant_n": abs(r0["F"]), "yaw_arm_m": arm, "kq_iso_m": kq,
           "k_yaw_m": kq * fac + arm * math.sin(math.radians(cant)),
           "k_yaw_low_m": kq * (1 + 0.5 * r["M_body"] / Q) + arm * math.sin(math.radians(cant)),
           "k_yaw_cant3_m": kq * (1 + r3["M_body"] / Q) + arm * math.sin(math.radians(3.0)),
           "k_yaw_nocant_m": kq * (1 + r0["M_body"] / Q),
           "k_yaw_r2_model_m": kq * 0.4796 + arm * math.sin(math.radians(cant)),
           "yaw_with_cant_over_isolated": fac + arm * math.sin(math.radians(cant)) / kq,
           "yaw_with_cant_low_over_isolated": 1 + 0.5 * r["M_body"] / Q + arm * math.sin(math.radians(cant)) / kq,
           "cant_thrust_loss": 1 - math.cos(math.radians(cant))}
    return out


# ---------------------------------------------------------------- 9. clearances, VRS, ground effect, noise
@kit.calc("CALC-B4-GEOM", title="Prop spacing and blade-to-tube gap with the canted discs, descent limit, ground "
          "effect and tones", assumes=["ASM-B4-VRS", "ASM-B4-WAKE-SENSE"],
          equation="hub moved stack sin(cant) along the thrust side ; disc plane normal n = canted shaft ; "
                   "blade x over a point (y, z) = x_hub + (n_y dy + n_z dz) / (-n_x) ; gap = x_face - x_blade over the "
                   "tube and collars inside R ; gap_v = 2 (z_hub - R sqrt(1 - n_z^2)) ; v_h = sqrt(k m g / (8 rho A)) ; "
                   "V_d,max = 0.28 v_h ; T_IGE/T = 1 / (1 - (R / 4 h)^2) ; M_tip = pi D n / a ; BPF = 2 n",
          inputs=dict(GEO_IN, foot_h=P + "cg.foot_height_m", m=P + "requirements.mtow_gate_kg",
                      kdl=P + "propulsion.download_factor", g=P + "env.g_ms2", rho=P + "env.rho_kgm3",
                      vrs="ASM-B4-VRS", rpm_h="CL-B4-HOVER-RPM", rpm_max="CL-B4-RPM-MAX"),
          units=dict(GEO_U, m="kg"))
def geometry(foot_h, m, kdl, g, rho, vrs, rpm_h, rpm_max, **geo):
    G = geo
    D = G["D"]
    R = D / 2
    s, cth = math.sin(math.radians(G["cant"])), math.cos(math.radians(G["cant"]))
    out = {}
    for tag, k in (("", G["k"]), ("_alt", -G["k"])):
        hub = hub_centre(G["x_prop"], G["y_m"], G["z_m"], G["cant"], k, G["stack"])
        ty, tz = thrust_side(G["y_m"], G["z_m"], k)
        n = (-cth, s * ty, s * tz)                          # thrust direction = disc normal
        z_end = G["tube_len"] / 2
        d_mc = G["d_tube"] + 2 * G["col_wall"]
        d_sc = G["d_tube"] + 2 * G["sc_wall"]
        sc_top = z_end - G["grip"] - G["sc_gap"]
        gap_t = gap_c = float("inf")
        for i in range(400):
            z = z_end - i * 0.0005
            dy, dz = G["y_m"] - hub[1], z - hub[2]
            if math.hypot(dy, dz) > R:
                continue
            xb = hub[0] + (n[1] * dy + n[2] * dz) / (-n[0])
            if z >= z_end - G["grip"]:
                gap_c = min(gap_c, G["x_mount"] - d_mc / 2 - xb)
            elif sc_top - G["sc_h"] <= z < sc_top:
                gap_c = min(gap_c, G["x_mount"] - d_sc / 2 - xb)
            else:
                gap_t = min(gap_t, G["x_mount"] - G["d_tube"] / 2 - xb)
        out["gap_tube_face_m" + tag] = gap_t
        out["gap_collar_face_m" + tag] = gap_c
        out["gap_tube_over_D" + tag] = min(gap_t, gap_c) / D
        out["gap_vertical_m" + tag] = 2 * (hub[2] - R * math.sqrt(1 - n[2] ** 2))
    out["gap_vertical_over_D"] = out["gap_vertical_m"] / D
    out["gap_lateral_m"] = 2 * G["y_m"] - D
    out["gap_tube_face_uncanted_m"] = G["x_mount"] - d_mc / 2 - G["x_prop"]
    vh = math.sqrt(kdl * m * g / 4 / (2 * rho * math.pi * R * R))
    h = G["fin_te"] + foot_h - G["x_prop"]
    a = 343.0
    out.update({"vh_ms": vh, "descent_max_ms": vrs * vh, "prop_height_m": h,
                "ige_gain": 1 / (1 - (R / (4 * h)) ** 2) - 1,
                "tip_mach_hover": math.pi * D * rpm_h / 60 / a, "tip_mach_max": math.pi * D * rpm_max / 60 / a,
                "bpf_hover_hz": 2 * rpm_h / 60, "one_p_hover_hz": rpm_h / 60, "bpf_max_hz": 2 * rpm_max / 60})
    return out


# ---------------------------------------------------------------- 9b. exact blade-tip clearance to the wing (R4)
def _vol_gap(p, hub, n, R, fwd, aft):
    """Distance (m) from point p to the prop's swept volume: radius R about the canted axis, axial -fwd..+aft about
    the hub mid-plane (+ = aft, toward the wing). Also returns the axial offset t and the radial distance rr."""
    d = (p[0] - hub[0], p[1] - hub[1], p[2] - hub[2])
    t = -(d[0] * n[0] + d[1] * n[1] + d[2] * n[2])
    rr = math.sqrt(max(0.0, d[0] * d[0] + d[1] * d[1] + d[2] * d[2] - t * t))
    dt = max(0.0, -fwd - t, t - aft)
    return (dt if rr <= R else math.hypot(dt, rr - R)), t, rr


def _wing_points(c, y0, y1, zs_up, zs_lo, dy=0.001):
    """S5010 upper and lower surface points (x, y, z) over y0..y1: 0.25 mm in x to 0.08 m, then 2 mm to the TE."""
    xs = [i * 0.00025 for i in range(321)] + [0.08 + i * 0.002 for i in range(1, int((c - 0.08) / 0.002) + 1)]
    ys = [y0 + j * dy for j in range(int((y1 - y0) / dy) + 1)]
    up = [(x, zs_up(x)) for x in xs]
    lo = [(x, zs_lo(x)) for x in xs]
    return ys, up, lo


@kit.calc("CALC-B4-TIP-WING", title="Exact blade-tip clearance to the wing skin and to the tube, canted disc, blade "
          "envelope (R4)", assumes=["ASM-B4-WAKE-SENSE", "ASM-E1-BLADE-ENV"],
          equation="hub = (x_prop, y + s sin(cant) t_y, z + s sin(cant) t_z) ; n = (-cos, sin t_y, sin t_z) ; for "
                   "every S5010 surface point p (x 0..c, |y - y_m| <= R + 30 mm): t = -(p - hub).n (+ aft), "
                   "rr = |(p - hub) - (-t) n| ; dt = max(0, -fwd - t, t - aft) ; gap = dt if rr <= R else "
                   "hypot(dt, rr - R) ; min over the surface ; upper stations see the upper surface, lower stations "
                   "the lower (mirror) ; same for the tube surface (z 0..L/2) ; keep-out cylinder test = rr - R "
                   "for points with -(10 mm + clr) <= t <= 10 mm + clr",
          inputs={"D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "y_m": P + "propulsion.stations.y_m", "z_m": P + "propulsion.stations.z_m",
                  "cant": P + "propulsion.stations.cant_deg", "k": "ASM-B4-WAKE-SENSE",
                  "stack": P + "fin_detail.mount.prop_stack_m", "c": P + "wing.chord_m", "b": P + "wing.span_m",
                  "env": "ASM-E1-BLADE-ENV", "clr": P + "requirements.prop_clearance_min_m",
                  "x_tube": P + "fins.tube.x_m", "d_tube": P + "fins.tube.od_m", "tube_len": P + "fins.tube.length_m",
                  "y_fin": P + "fins.y_m"},
          units={"D": "m", "x_prop": "m", "y_m": "m", "z_m": "m", "cant": "deg", "stack": "m", "c": "m", "b": "m",
                 "env": "m", "clr": "m", "x_tube": "m", "d_tube": "m", "tube_len": "m", "y_fin": "m"})
def tip_wing(D, x_prop, y_m, z_m, cant, k, stack, c, b, env, clr, x_tube, d_tube, tube_len, y_fin):
    R = D / 2
    fwd, aft = env
    sym = 0.010                                            # A1's symmetric keep-out half-thickness (KO-PROP)
    s, co = math.sin(math.radians(cant)), math.cos(math.radians(cant))
    up, lo = _airfoil_surfaces()
    xu, zu = [q[0] for q in up], [q[1] for q in up]
    xl, zl = [q[0] for q in lo], [q[1] for q in lo]
    zs_up = lambda x: _interp(xu, zu, min(max(x / c, 0.0), 1.0)) * c
    zs_lo = lambda x: -_interp(xl, zl, min(max(x / c, 0.0), 1.0)) * c     # lower surface, mirrored to +z
    y0, y1 = max(y_m - R - 0.03, 0.0), min(y_m + R + 0.03, b / 2)
    ys, pu, pl = _wing_points(c, y0, y1, zs_up, zs_lo)
    out = {}
    for tag, kk in (("", k), ("_alt", -k)):
        hub = hub_centre(x_prop, y_m, z_m, cant, kk, stack)
        ty, tz = thrust_side(y_m, z_m, kk)
        n = (-co, s * ty, s * tz)
        for st, prof in (("upper", pu), ("lower", pl)):     # UR/UL face the upper skin; LR/LL (mirror) the lower
            best = {"env": (9.0, None), "sym": (9.0, None), "mid": (9.0, None), "ko": (9.0, None)}
            for y in ys:
                for x, z in prof:
                    p = (x, y, z)
                    g_e, t, rr = _vol_gap(p, hub, n, R, fwd, aft)
                    if g_e < best["env"][0]:
                        best["env"] = (g_e, (x, y, z, t, rr))
                    g_s = _vol_gap(p, hub, n, R, sym, sym)[0]
                    if g_s < best["sym"][0]:
                        best["sym"] = (g_s, (x, y, z, t, rr))
                    g_m = math.hypot(t, rr - R) if rr > R else abs(t)   # zero-thickness tip circle / disc
                    if g_m < best["mid"][0]:
                        best["mid"] = (g_m, (x, y, z, t, rr))
                    if -(sym + clr) <= t <= sym + clr and rr - R < best["ko"][0]:
                        best["ko"] = (rr - R, (x, y, z, t, rr))
            pre = f"wing_{st}"
            out[f"{pre}_gap_env_m{tag}"] = best["env"][0]
            out[f"{pre}_gap_sym_m{tag}"] = best["sym"][0]
            out[f"{pre}_gap_midplane_m{tag}"] = best["mid"][0]
            out[f"{pre}_ko_radial_gap_m{tag}"] = best["ko"][0]
            if tag == "":
                x, y, z, t, rr = best["env"][1]
                out[f"{pre}_closest_xyz_m"] = [round(x, 4), round(y, 4), round(z, 4)]
                out[f"{pre}_closest_axial_m"] = t
                out[f"{pre}_closest_radial_m"] = rr
                x, y, z, t, rr = best["ko"][1]
                out[f"{pre}_ko_point_xyz_m"] = [round(x, 4), round(y, 4), round(z, 4)]
                out[f"{pre}_ko_point_axial_m"] = t
                out[f"{pre}_ko_point_radial_m"] = rr
        # bare 22 mm CF tube (z 0..L/2), same envelope: restates CL-B4-GAP-TUBE against ASM-E1-BLADE-ENV (CR-E1-46a)
        g_t = g_ts = 9.0
        for i in range(int(tube_len / 2 / 0.0005) + 1):
            z = i * 0.0005
            for j in range(144):
                ph = 2 * math.pi * j / 144
                p = (x_tube + d_tube / 2 * math.cos(ph), y_fin + d_tube / 2 * math.sin(ph), z)
                g_t = min(g_t, _vol_gap(p, hub, n, R, fwd, aft)[0])
                g_ts = min(g_ts, _vol_gap(p, hub, n, R, sym, sym)[0])
        out["tube_gap_env_m" + tag] = g_t
        out["tube_gap_sym_m" + tag] = g_ts
        out["hub_xyz_m" + tag] = [round(q, 5) for q in hub]
        if tag == "":                                      # trade point: E1's CR-E1-44 fix, mount face 5 mm forward
            hub5 = (hub[0] - 0.005, hub[1], hub[2])
            out["tube_gap_env_fix5_m"] = min(
                _vol_gap((x_tube + d_tube / 2 * math.cos(2 * math.pi * j / 144),
                          y_fin + d_tube / 2 * math.sin(2 * math.pi * j / 144), i * 0.0005), hub5, n, R, fwd, aft)[0]
                for i in range(int(tube_len / 2 / 0.0005) + 1) for j in range(144))
            out["wing_upper_gap_env_fix5_m"] = min(_vol_gap((x, y, z), hub5, n, R, fwd, aft)[0]
                                                  for y in ys for x, z in pu)
    out["wing_gap_env_min_m"] = min(out["wing_upper_gap_env_m"], out["wing_lower_gap_env_m"])
    out["wing_ko_radial_min_m"] = min(out["wing_upper_ko_radial_gap_m"], out["wing_lower_ko_radial_gap_m"])
    return out


# ---------------------------------------------------------------- 10. cross-check against UIUC measurements
def _uiuc(prop, kind):
    return [r for r in UIUC if r["prop"] == prop and r["kind"] == kind]


@kit.calc("CALC-B4-XCHECK", title="UIUC-measured cross-check of the APC predictions", cites=["SRC-B4-UIUC"],
          equation="static: Ct_UIUC / Ct_APC and Cp_UIUC / Cp_APC at J = 0, top measured rpm ; FM ratio = "
                   "(Ct ratio)^1.5 / Cp ratio ; cruise: solve Ct_UIUC(J) rho n^2 D^4 = T at V ; eta = T V / P",
          inputs={"m": P + "requirements.mtow_gate_kg", "ld": P + "performance.ld_cruise",
                  "V": P + "performance.cruise_ms", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3"},
          units={"m": "kg", "V": "m/s", "rho": "kg/m3"})
def uiuc_xcheck(m, ld, V, g, rho):
    out = {}
    Tc = m * g / ld / 4
    for prop in ("11x4.7SF", "11x5.5E"):
        st = max(_uiuc(prop, "static"), key=lambda r: r["x"])
        ct0, cp0 = coeffs(prop, 0.0, st["x"])
        out[f"ct_ratio_static__{prop}"] = st["Ct"] / ct0
        out[f"cp_ratio_static__{prop}"] = st["Cp"] / cp0
        out[f"fm_ratio_static__{prop}"] = (st["Ct"] / ct0) ** 1.5 / (st["Cp"] / cp0)
        tun = _uiuc(prop, "tunnel")
        js, cts, cps = [r["J"] for r in tun], [r["Ct"] for r in tun], [r["Cp"] for r in tun]
        D = PROPS[prop][1] * IN

        def g2(rpm):
            n = rpm / 60
            return _interp(js, cts, V / (n * D)) * rho * n * n * D ** 4 - Tc
        rpm_c = _bisect(g2, 3000.0, 14000.0)
        n = rpm_c / 60
        J = V / (n * D)
        Pw = _interp(js, cps, J) * rho * n ** 3 * D ** 5
        apc = _cruise(prop, Tc, V, rho, Motor(900.0, 0.0, 0.0))
        out[f"J_uiuc__{prop}"] = J
        out[f"eta_prop_uiuc__{prop}"] = Tc * V / Pw
        out[f"eta_prop_apc__{prop}"] = apc["eta_prop"]
        out[f"eta_ratio_uiuc_over_apc__{prop}"] = (Tc * V / Pw) / apc["eta_prop"]
    return out
# ---------------------------------------------------------------- 11. worst-case rpm against the APC limit
@kit.calc("CALC-B4-RPMFULL", title="Unlimited full-throttle rpm on a fresh pack and the output cap that respects the APC limit",
          cites=["SRC-B4-APC-RPM"],
          equation="(V - rpm/Kv)/R = Q(rpm)/Kt + I0, cold winding (lowest R, highest rpm), V = max OCV ; "
                   "cap: find V_eff giving rpm = 0.98 x 105000/D_in ; duty = V_eff / V_ocv,max ; "
                   "T/W at the cap = 4 T(rpm_cap) cos cant / (k_dl m g)",
          inputs=dict(E1_MOTOR, ocv="ASM-E1-OCV", m=P + "requirements.mtow_gate_kg",
                      k_dl=P + "propulsion.download_factor", g=P + "env.g_ms2", rho=P + "env.rho_kgm3",
                      cant=P + "propulsion.stations.cant_deg"),
          units={"m": "kg", "rho": "kg/m3", "cant": "deg"})
def rpm_full(kv, rm, i0, esc, pack, tcu, ocv, m, k_dl, g, rho, cant):
    mot, _ = _motor(kv, rm, i0, esc, pack, tcu, hot=False)
    out = {}
    for prop in ("11x5.5MR", "11x4.5MR"):
        rpm = mot.full_throttle_rpm(prop, max(ocv), 0.0, rho)
        cap = 0.98 * PROPS[prop][2] / PROPS[prop][1]
        v_eff = _bisect(lambda vv: mot.full_throttle_rpm(prop, vv, 0.0, rho) - cap, 6.0, max(ocv))
        t_cap = thrust_power(prop, cap, 0.0, rho)[0]
        tag = "" if prop == "11x5.5MR" else "__11x4.5MR"
        out["rpm" + tag] = rpm
        out["rpm_cap" + tag] = cap
        out["spin_max_duty" + tag] = v_eff / max(ocv)
        out["tw_at_cap" + tag] = 4 * t_cap * math.cos(math.radians(cant)) / (k_dl * m * g)
        out["t_cap_n" + tag] = t_cap
    return out


# ---------------------------------------------------------------- claims
SEL = "11x5.5MR"                                                     # B4 selection (concurs with CR-E1-06)
OLD = "11x4.5MR"
PRP = [f"PRP-003-{s}" for s in ("UR", "UL", "LR", "LL")]          # the four props (A4 interface plan ids)
FINS = [f"FIN-001-{s}" for s in ("UR", "UL", "LR", "LL")]       # half-fins (CHANGE-LOG D-26 codes)
c = kit.claim
c("CL-B4-DATA", "APC data copied without error (worst row)", calc="CALC-B4-DATA",
  output="max_rel_err", unit="-", limit=("<=", 0.005),
  how="Re-run props.py; every row's printed N and W reproduce its Ct and Cp within 0.5 % (a typo shows as > 1 %).")
c("CL-B4-HOVER-T", "Hover thrust per prop at the gate incl. download", calc="CALC-B4-STATIC",
  output="hover_thrust_per_prop_n", unit="N",
  how="= 1.06 x 2.6 kg x g / (4 cos 7 deg): the canted thrust lifts with cos(cant); re-check after T-B4-INSTALLED.")
c("CL-B4-DL", "Disk loading at the gate (11 in)", calc="CALC-B4-STATIC", output=f"disk_loading_npm2__{SEL}",
  unit="N/m2", how="Hand check: 6.81 N / 0.0613 m2.")
c("CL-B4-HOVER-RPM", "Hover rpm, 11x5.5MR", calc="CALC-B4-STATIC", output=f"hover_rpm__{SEL}", unit="rpm",
  parts=PRP, how="Log rpm (Bluejay bidirectional DShot telemetry) in a tethered hover at 2.6 kg.")
c("CL-B4-HOVER-Q", "Prop torque at hover, 11x5.5MR (reaction torque for yaw)", calc="CALC-B4-STATIC",
  output=f"hover_torque_nm__{SEL}", unit="N*m", parts=PRP, how="T-B4-STAND torque cell at 0.69 kgf.")
c("CL-B4-FM", "Hover figure of merit, 11x5.5MR (APC data)", calc="CALC-B4-STATIC", output=f"hover_fm__{SEL}",
  unit="-", parts=PRP, how="T-B4-STAND: FM from measured thrust and shaft power (rpm x torque) at 0.69 kgf.")
c("CL-B4-FM-OLD", "Hover figure of merit, 11x4.5MR (APC data)", calc="CALC-B4-STATIC", output=f"hover_fm__{OLD}",
  unit="-", how="T-B4-STAND A/B with the 11x4.5MR.")
c("CL-B4-HOVER-SHAFT", "Hover shaft power per motor, 11x5.5MR", calc="CALC-B4-STATIC",
  output=f"hover_shaft_w__{SEL}", unit="W", parts=PRP, how="T-B4-STAND: rpm x torque at 0.69 kgf.")
c("CL-B4-RPM-MAX", "Full-throttle rpm, 11x5.5MR, 14.8 V bus, hot winding", calc="CALC-B4-STATIC",
  output=f"rpm_max__{SEL}", unit="rpm", parts=PRP, limit=("<=", 105000 / 11.0), cites=["SRC-B4-APC-RPM"],
  how="T-B4-STAND at 14.8 V full throttle with rpm telemetry; must stay below the APC MR limit 9 545 rpm.")
c("CL-B4-RPM-MAX-FULL", "Full-throttle rpm, 11x5.5MR, 16.8 V fresh pack (unlimited)", calc="CALC-B4-RPMFULL",
  output="rpm", unit="rpm", parts=PRP, limit=("<=", 105000 / 11.0), cites=["SRC-B4-APC-RPM"],
  how="T-B4-STAND on a fully charged pack. Expected to FAIL unlimited: F4 caps the output (CL-B4-SPIN-MAX).")
c("CL-B4-SPIN-MAX", "Motor output cap that holds 11x5.5MR rpm at 98 % of the APC limit, fresh pack", calc="CALC-B4-RPMFULL",
  output="spin_max_duty", unit="-", parts=PRP,
  how="Stand on a 16.8 V pack: at this output fraction rpm <= 9 350; F4 sets Q_M_SPIN_MAX (or the ESC limit) to it.")
c("CL-B4-TW-CAP", "T/W at the rpm cap (11x5.5MR, installed, bus able to reach the cap)", calc="CALC-B4-RPMFULL",
  output="tw_at_cap", unit="-", limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"], parts=PRP,
  how="T-B4-STAND: thrust at 9 350 rpm >= 1.40 kgf.")
c("CL-B4-SF-RPM", "11x4.7SF rpm-limit margin at full throttle (negative = over limit)", calc="CALC-B4-STATIC",
  output="rpm_limit_margin__11x4.7SF", unit="-", limit=(">=", 0.0), cites=["SRC-B4-APC-RPM"],
  how="APC SF limit 65 000/11 = 5 909 rpm against full-throttle rpm. FAILS by design: the reason the SF is rejected.")
c("CL-B4-CRUISE-ETA", "Cruise prop efficiency, 11x5.5MR, cruise speed and thrust (params)", calc="CALC-B4-CRUISE",
  output=f"eta_prop__{SEL}", unit="-", parts=PRP,
  how="Logged cruise: shaft power from ESC rpm and motor model vs drag x V; or a car-top test at cruise speed.")
c("CL-B4-CRUISE-ETA-OLD", "Cruise prop efficiency, 11x4.5MR, cruise speed and thrust (params)", calc="CALC-B4-CRUISE",
  output=f"eta_prop__{OLD}", unit="-", how="As CL-B4-CRUISE-ETA.")
c("CL-B4-CRUISE-J", "Cruise advance ratio, 11x5.5MR", calc="CALC-B4-CRUISE", output=f"J__{SEL}", unit="-",
  how="J = V / (n D) from logged rpm and airspeed.")
c("CL-B4-CRUISE-RPM", "Cruise rpm, 11x5.5MR", calc="CALC-B4-CRUISE", output=f"rpm__{SEL}", unit="rpm", parts=PRP,
  how="ESC rpm telemetry in steady cruise.")
c("CL-B4-CRUISE-SHAFT", "Cruise shaft power per motor, 11x5.5MR", calc="CALC-B4-CRUISE", output=f"shaft_w__{SEL}",
  unit="W", parts=PRP, how="Logged cruise: rpm and current with E1's motor constants.")
c("CL-B4-CRUISE-W", "Cruise pack power, 11x5.5MR, 4 motors (E1 motor constants)", calc="CALC-B4-CRUISE",
  output=f"pack_w__{SEL}", unit="W", parts=PRP, how="Log pack power in steady level cruise at performance.cruise_ms, 2.6 kg.")
c("CL-B4-CRUISE-W-OLD", "Cruise pack power, 11x4.5MR, 4 motors (E1 motor constants)", calc="CALC-B4-CRUISE",
  output=f"pack_w__{OLD}", unit="W", how="As CL-B4-CRUISE-W.")
c("CL-B4-HOVER-W", "Hover pack power at the gate, 11x5.5MR (E1 motor constants)", calc="CALC-B4-STATIC",
  output=f"hover_pack_w__{SEL}", unit="W", parts=PRP, how="Log pack power in a 60 s tethered hover at 2.6 kg.")
c("CL-B4-HOVER-W-OLD", "Hover pack power at the gate, 11x4.5MR (E1 motor constants)", calc="CALC-B4-STATIC",
  output=f"hover_pack_w__{OLD}", unit="W", how="As CL-B4-HOVER-W.")
# CDR-15 / CDR-AE-08: cruise prop A/B (APC PER3 predictions, uncalibrated; the stand and a cruise leg decide, M6)
c("CL-B4-AB-CRUISE-W-MR-17", "Cruise pack power at 17 m/s (B6 baseline speed), 11x5.5MR, 4 motors", calc="CALC-B4-PROP-AB",
  output="pack_w_17__11X55MR", unit="W", parts=PRP,
  how="T-B1-CRUISE-POWER leg at 17 m/s; E1's own figure for 17 m/s is 283 W (D-96).")
c("CL-B4-AB-CRUISE-W-11X7E-16", "Cruise pack power at 16 m/s, 11x7E, 4 motors", calc="CALC-B4-PROP-AB",
  output="pack_w_16__11X7E", unit="W", how="GT-02 static A/B, then a cruise leg on the twin (M6).")
c("CL-B4-AB-CRUISE-W-11X7E-17", "Cruise pack power at 17 m/s, 11x7E, 4 motors", calc="CALC-B4-PROP-AB",
  output="pack_w_17__11X7E", unit="W", how="As CL-B4-AB-CRUISE-W-11X7E-16.")
c("CL-B4-AB-CRUISE-RATIO-16", "Cruise pack power, 11x7E over 11x5.5MR, 16 m/s", calc="CALC-B4-PROP-AB",
  output="ratio_16__11X7E_over_MR", unit="-", how="Ratio of logged cruise power in the A/B legs.")
c("CL-B4-AB-CRUISE-RATIO-17", "Cruise pack power, 11x7E over 11x5.5MR, 17 m/s", calc="CALC-B4-PROP-AB",
  output="ratio_17__11X7E_over_MR", unit="-", how="As CL-B4-AB-CRUISE-RATIO-16.")
c("CL-B4-AB-CRUISE-RATIO-E-17", "Cruise pack power, 11x5.5E over 11x5.5MR, 17 m/s", calc="CALC-B4-PROP-AB",
  output="ratio_17__11X55E_over_MR", unit="-", how="As CL-B4-AB-CRUISE-RATIO-16.")
c("CL-B4-AB-ETA-11X7E-17", "Cruise prop efficiency at 17 m/s, 11x7E", calc="CALC-B4-PROP-AB", output="eta_17__11X7E",
  unit="-", how="As CL-B4-CRUISE-ETA.")
c("CL-B4-AB-ETA-MR-17", "Cruise prop efficiency at 17 m/s, 11x5.5MR", calc="CALC-B4-PROP-AB", output="eta_17__11X55MR",
  unit="-", how="As CL-B4-CRUISE-ETA.")
c("CL-B4-AB-HOVER-RATIO", "Hover pack power, 11x7E over 11x5.5MR, gate mass", calc="CALC-B4-PROP-AB",
  output="hover_ratio__11X7E_over_MR", unit="-", limit=("<=", "ASM-B4-AB-HOVER-MAX"),
  how="GT-02: pack power at 0.69 kgf per prop, both props on the same motor and supply.")
c("CL-B4-AB-THR-VH-11X7E", "Motor output that reaches VH 21.8 m/s in level flight with the 11x7E, fresh pack "
  "(THR_MAX would be set to this)", calc="CALC-B4-PROP-AB", output="thr_for_vh__11X7E", unit="-",
  how="FBWB full-throttle level leg with the 11x7E fitted (TUNING-PLAN step 6c) before THR_MAX is frozen.")
c("CL-B4-AB-VLEVEL-MR-70", "Level speed at fixed-wing output 0.704, fresh pack, 11x5.5MR (B4 motor and prop model; "
  "F4 carries 21.3 m/s from B1)", calc="CALC-B4-PROP-AB", output="v_level_thr70__11X55MR", unit="m/s",
  how="TUNING-PLAN step 6c.")
c("CL-B4-AB-THR-VH-MR", "Motor output that reaches VH 21.8 m/s in level flight with the 11x5.5MR, fresh pack "
  "(B4 motor and prop model: the prop unloads in flight, so rpm at a fixed output is higher than on the stand)",
  calc="CALC-B4-PROP-AB", output="thr_for_vh__11X55MR", unit="-",
  how="TUNING-PLAN step 6c (FBWB full-throttle level leg, THR_MAX downward only): airspeed <= 21.8 m/s decides "
      "THR_MAX. F4's CL-F4-VLEVEL-VH scales B1's speed with the static rpm (ASM-F4-RPM-LIN); this claim is the "
      "second model and reads lower (CR-B4-20 to F4, B1).")
c("CL-B4-AB-RPM-LEVEL-MR-70", "In-flight rpm at fixed-wing output 0.704 and the level speed it reaches, 11x5.5MR, "
  "fresh pack", calc="CALC-B4-PROP-AB", output="rpm_level_thr70__11X55MR", unit="rpm",
  limit=("<=", 105000 / 11.0), cites=["SRC-B4-APC-RPM"], how="ESC rpm telemetry in the step-6c leg.")
c("CL-B4-AB-VLEVEL-11X7E-70", "Level speed at fixed-wing output 0.704, fresh pack, 11x7E (THR_MAX 70 kept)",
  calc="CALC-B4-PROP-AB", output="v_level_thr70__11X7E", unit="m/s",
  how="Information: above VH 21.8 m/s, so THR_MAX must drop to CL-B4-AB-THR-VH-11X7E if the 11x7E is flown.")
c("CL-B4-AB-RPM-FULL-11X7E", "Full-throttle rpm, 11x7E, 16.8 V fresh pack (unlimited), against the thin-electric limit",
  calc="CALC-B4-PROP-AB", output="rpm_full_fresh__11X7E", unit="rpm", limit=("<=", 150000 / 11.0),
  cites=["SRC-B4-APC-RPM"], how="GT-02 with rpm telemetry on a full pack.")
c("CL-B4-UIUC-ETA", "UIUC-measured over APC-predicted cruise efficiency, 11x4.7SF (data spread)",
  calc="CALC-B4-XCHECK", output="eta_ratio_uiuc_over_apc__11x4.7SF", unit="-",
  how="The 11x5.5MR value comes from T-B4-STAND plus a car-top or flight check; this ratio is the expected spread.")
c("CL-B4-UIUC-ETA-E", "UIUC-measured over APC-predicted cruise efficiency, 11x5.5E", calc="CALC-B4-XCHECK",
  output="eta_ratio_uiuc_over_apc__11x5.5E", unit="-", how="As CL-B4-UIUC-ETA.")
c("CL-B4-DOWNLOAD", "Hover download factor (modelled, mean loading, R3 fin hardware)", calc="CALC-B4-DOWNLOAD",
  output="k", unit="-", limit=("<=", P + "propulsion.download_factor"), parts=FINS,
  how="T-B4-INSTALLED: thrust stand with the canted mount, tube, collars, brace, ESC dummy and half-fin behind the "
      "prop; installed/isolated thrust ratio at equal rpm.")
c("CL-B4-DOWNLOAD-HIGH", "Hover download factor (peaked loading)", calc="CALC-B4-DOWNLOAD", output="k_high", unit="-",
  limit=("<=", P + "propulsion.download_factor"), parts=FINS, how="T-B4-INSTALLED.")
c("CL-B4-ITEMS-HOVER", "Hover download of collars, ears, brace and ESC pad, one station (mean loading)",
  calc="CALC-B4-DOWNLOAD", output="items_n", unit="N", parts=FINS,
  how="T-B4-INSTALLED: thrust with and without the collars, brace strip and ESC dummy.")
c("CL-B4-BRACE-HOVER", "Slipstream drag on one brace in hover (mean loading; load case for C4)",
  calc="CALC-B4-DOWNLOAD", output="brace_n", unit="N", parts=FINS,
  how="T-B4-INSTALLED with the brace strip on a 2-axis load cell, or by difference.")
c("CL-B4-ESC-WASH", "ESC pad outer (wing-side) edge / slipstream radius, leaning hover wake", calc="CALC-B4-DOWNLOAD",
  output="esc_outer_edge_over_rs", unit="-", limit=("<=", 1.0), parts=["FIN-007-UR"],
  how="Tufts on the pad edge in a tethered hover; E3's ESC temperature log.")
c("CL-B4-ITEMS-DRAG", "Cruise drag of collars, ears, braces and ESC pads, 4 stations (B4 coefficients)",
  calc="CALC-B4-ITEMS-CRUISE", output="items_n", unit="N", parts=FINS,
  how="T-B4-CRUISE: logged cruise power with and without brace fairings, or a car-top drag rig on one fin.")
c("CL-B4-ITEMS-DCD0", "Cruise CD0 increment of the R3 fin hardware (on S = b c)", calc="CALC-B4-ITEMS-CRUISE",
  output="items_dcd0", unit="-", how="As CL-B4-ITEMS-DRAG.")
c("CL-B4-ITEMS-NOT-B1", "Cruise CD0 of the items B1 rev 3 does not carry (mount collars, ears, ESC pads)",
  calc="CALC-B4-ITEMS-CRUISE", output="not_in_b1_dcd0", unit="-", how="As CL-B4-ITEMS-DRAG.")
c("CL-B4-ITEMS-PACK-W", "Cruise pack power for the R3 fin hardware (share of CL-B4-CRUISE-W)",
  calc="CALC-B4-ITEMS-CRUISE", output="items_pack_w", unit="W", how="As CL-B4-ITEMS-DRAG.")
c("CL-B4-ELEVON-HOVER", "Elevons outside the hover slipstream (gap; wake leaning per F4's spin map)",
  calc="CALC-B4-WAKE", output="hover_gap_elevon_m", unit="m", limit=(">=", 0.0), assumes=["ASM-B4-WAKE-SENSE"],
  how="Tufts on the elevons during a tethered hover: they stay still. Consequence: zero elevon authority in hover.")
c("CL-B4-ELEVON-HOVER-ALT", "Elevon gap to the hover slipstream if the spin map were mirrored (wake leans to the wing)",
  calc="CALC-B4-WAKE", output="hover_gap_elevon_m_alt", unit="m", limit=(">=", 0.0),
  how="Only if F4 mirrors the map; same tuft test.")
c("CL-B4-ELEVON-CRUISE", "Elevon tip vs cruise slipstream edge (negative = inside the mixing layer)",
  calc="CALC-B4-WAKE", output="cruise_gap_elevon_m", unit="m", how="Tufts on the elevons in cruise, camera on the fin.")
c("CL-B4-PITOT", "Worst prop-induced airspeed error at the chosen pitot (pod-nose boom, left channel)",
  calc="CALC-B4-PITOT", output="worst_err__pod_boom", unit="-", limit=("<=", "ASM-B4-PITOT-ERR"),
  parts=["AVN-005", "POD-006"],
  how="Fly constant GPS-groundspeed legs in calm air at two throttle settings; airspeed must not step with throttle.")
c("CL-B4-PITOT-TIP-X", "Pitot tip x station (pod front - boom; = params avionics.pitot_tip_xyz_m[0])",
  calc="CALC-B4-PITOT-TIP", output="tip_x_m", unit="m", parts=["AVN-005", "POD-006"],
  how="Measure the tip from the wing LE on the built airframe with the boom plugged in.")
c("CL-B4-PITOT-CRUISE", "Prop-induced airspeed error at the chosen pitot in cruise", calc="CALC-B4-PITOT",
  output="cruise__pod_boom__err", unit="-", limit=("<=", "ASM-B4-PITOT-ERR"), parts=["AVN-005", "POD-006"],
  how="As CL-B4-PITOT.")
c("CL-B4-PITOT-Y0", "Prop-induced airspeed error with the boom on the centreline (R2 position, comparison)",
  calc="CALC-B4-PITOT", output="worst_err__pod_boom_y0", unit="-", how="Comparison only.")
c("CL-B4-PITOT-FACE", "Prop-induced airspeed error with no boom (probe at the pod front)", calc="CALC-B4-PITOT",
  output="worst_err__pod_face", unit="-", limit=("<=", "ASM-B4-PITOT-ERR"),
  how="Same flight test as CL-B4-PITOT; shows what the boom buys.")
c("CL-B4-PITOT-WING", "Prop-induced airspeed error, inboard wing LE at y = 0.15 m (rejected)", calc="CALC-B4-PITOT",
  output="worst_err__wing_LE_y0.15", unit="-", limit=("<=", "ASM-B4-PITOT-ERR"),
  how="Same flight test; shows why the inboard wing LE is not used.")
c("CL-B4-PITOT-CONV", "Pitot model wake/grid convergence (max change, last two levels)", calc="CALC-B4-PITOT",
  output="max_conv", unit="-", limit=("<=", 0.002),
  how="Re-run: three wake lengths and Simpson grids; change as a fraction of airspeed.")
c("CL-B4-SWIRL-FIN", "Side force on each half-fin in hover from swirl and the canted wake (same sense on both halves "
  "of a fin)", calc="CALC-B4-SWIRL", output="fin_side_force_n", unit="N", parts=FINS,
  how="T-B4-YAW: side force on a half-fin mock-up (0.264 m wetted chord, R3 top edge) on its own load cell behind "
      "the canted prop at hover thrust.")
c("CL-B4-SWIRL-FIN-M", "Swirl bending moment at each half-fin root (wing skin), hover", calc="CALC-B4-SWIRL",
  output="half_fin_root_moment_nm", unit="N*m", parts=FINS, how="As CL-B4-SWIRL-FIN, times the measured cp height.")
c("CL-B4-TUBE-LOAD", "Slipstream drag on each bare motor tube in hover (mean loading)", calc="CALC-B4-DOWNLOAD",
  output="tube_n", unit="N", parts=FINS, how="T-B4-INSTALLED: thrust with and without the tube.")
c("CL-B4-WING-GAP", "Hover slipstream (incl. mixing layer) clearance to the wing surface at the fin station",
  calc="CALC-B4-DOWNLOAD", output="wing_gap_min_m", unit="m", limit=(">=", 0.0), parts=FINS,
  how="T-B4-INSTALLED with a wing-section strip at the right height; tufts on the wing beside the fin in a "
      "tethered hover stay still.")
c("CL-B4-WING-GAP-ALT", "Wing-surface clearance if the spin map were mirrored (wake leans to the wing)",
  calc="CALC-B4-DOWNLOAD", output="wing_gap_min_m_alt", unit="m", limit=(">=", 0.0), how="As CL-B4-WING-GAP.")
c("CL-B4-YAW", "Hover yaw authority factor: (reaction torque + fin side-force moment about the body x-axis) / "
  "reaction torque, at the params cant", calc="CALC-B4-SWIRL", output="yaw_authority_factor_mid", unit="-",
  how="T-B4-YAW: fin side force and its centre of pressure on the stand; then a tethered-hover yaw step.",
  note="R3: the fin side force acts 0.1-0.2 m from the body x-axis and turns the airframe WITH the reaction torque. "
       "R0-R2 counted only its moment about the motor axis (0.48), which is the wrong axis for body yaw.")
c("CL-B4-YAW-LOW", "Hover yaw authority factor with half the modelled fin force (sizing value)", calc="CALC-B4-SWIRL",
  output="yaw_authority_factor_low", unit="-", limit=(">=", 1.0), how="As CL-B4-YAW.")
c("CL-B4-YAW-NOCANT", "Hover yaw authority factor with an uncanted motor (the cant's wake lean opposes the swirl)",
  calc="CALC-B4-SWIRL", output="yaw_factor_nocant", unit="-", how="T-B4-YAW with the 0 deg mount.")
c("CL-B4-K-YAW", "Yaw moment per newton of differential thrust, params cant (reaction x factor + r sin cant)",
  calc="CALC-B4-SWIRL", output="k_yaw_m", unit="m",
  how="Tethered-hover yaw step: yaw acceleration x Ixx / differential thrust.")
c("CL-B4-K-YAW-LOW", "Yaw moment per newton of differential thrust, half fin force (sizing value)",
  calc="CALC-B4-SWIRL", output="k_yaw_low_m", unit="m", how="As CL-B4-K-YAW.")
c("CL-B4-K-YAW-3DEG", "Yaw moment per newton of differential thrust at a 3 deg cant (trade point)",
  calc="CALC-B4-SWIRL", output="k_yaw_cant3_m", unit="m", how="As CL-B4-K-YAW with the 3 deg mounts.")
c("CL-B4-F-AXIS", "Fin moment about the motor axis / reaction torque (what a motor-axis torque cell with the fin on it "
  "reads as 'recovery')", calc="CALC-B4-SWIRL", output="f_axis_recovery", unit="-",
  how="T-B4-YAW: reaction torque with and without the fin on the same cell.")
c("CL-B4-YAW-CANT", "Hover yaw authority with the params motor cant (fraction of isolated, uncanted)",
  calc="CALC-B4-SWIRL", output="yaw_with_cant_over_isolated", unit="-", limit=(">=", 1.0),
  how="T-B4-YAW then a tethered-hover yaw step with the canted mounts.")
c("CL-B4-YAW-CANT-LOW", "Hover yaw authority with the params cant and half the fin force (fraction of isolated)",
  calc="CALC-B4-SWIRL", output="yaw_with_cant_low_over_isolated", unit="-", limit=(">=", 1.0),
  how="As CL-B4-YAW-CANT.")
c("CL-B4-CANT-LOSS", "Hover thrust lost to the cant (1 - cos cant)", calc="CALC-B4-SWIRL", output="cant_thrust_loss",
  unit="-", how="Geometry; included in CL-B4-HOVER-T.")
c("CL-B4-DESCENT", "Maximum vertical descent rate (vortex-ring margin)", calc="CALC-B4-GEOM", output="descent_max_ms",
  unit="m/s", how="F4 sets Q_WP_SPEED_DN and Q_LAND_SPEED below this; watch for thrust oscillation in descent tests.")
c("CL-B4-GAP-V", "Vertical prop-to-prop tip gap (canted discs)", calc="CALC-B4-GEOM", output="gap_vertical_m",
  unit="m", limit=(">=", P + "requirements.prop_clearance_min_m"), verifies=["R-PROP-CLEAR"], parts=PRP,
  cites=["SRC-B4-ZHOU-ROTOR"], how="Measure on the built airframe with props fitted. About 0.33 D tip gap: mean "
  "thrust change < 2 % per the cited rotor-pair data.")
c("CL-B4-TIP-WING", "Blade swept volume (E1 envelope +10/-6 mm) to the wing upper skin, upper stations, exact 3D",
  calc="CALC-B4-TIP-WING", output="wing_upper_gap_env_m", unit="m",
  limit=(">=", P + "requirements.prop_clearance_min_m"), verifies=["R-PROP-CLEAR"], parts=PRP + ["WNG-001", "WNG-003"],
  note="R4 action item: the 23 mm figure (0.163 m radial vs R 0.1397) does not reproduce. The least radial distance "
       "from the canted UR axis to the S5010 upper skin anywhere at the fin station is 0.171 m, and the point that "
       "sets it lies 35-50 mm behind the blade, so a radial-only number is not a clearance. The true minimum is at "
       "x 0.023, 0.6 mm aft of the 6 mm blade envelope's reach in x; agrees with E1's CAD probe (WNG-003 34.1 mm)",
  how="Built airframe, props fitted: turn the blade through the wing-side position and pass a printed 25 mm gauge "
      "between the blade tip and the wing upper skin at y 0.32 (T-B4-INSTALLED; same gauge as CL-E1-TIP-GAP-TUBE).")
c("CL-B4-TIP-WING-LOWER", "Blade swept volume (E1 envelope) to the wing lower skin, lower stations, exact 3D",
  calc="CALC-B4-TIP-WING", output="wing_lower_gap_env_m", unit="m",
  limit=(">=", P + "requirements.prop_clearance_min_m"), verifies=["R-PROP-CLEAR"], parts=PRP + ["WNG-001", "WNG-003"],
  how="As CL-B4-TIP-WING at LR / LL.")
c("CL-B4-TIP-WING-SYM", "Blade swept volume (A1's symmetric +/-10 mm) to the wing upper skin, exact 3D",
  calc="CALC-B4-TIP-WING", output="wing_upper_gap_sym_m", unit="m",
  limit=(">=", P + "requirements.prop_clearance_min_m"), how="As CL-B4-TIP-WING.")
c("CL-B4-TIP-WING-KO", "Radial clearance of the wing upper skin inside the KO-PROP axial band (what a cylinder "
  "keep-out test of R + 25 mm, half 35 mm, sees)", calc="CALC-B4-TIP-WING", output="wing_upper_ko_radial_gap_m",
  unit="m", limit=(">=", P + "requirements.prop_clearance_min_m"),
  how="For A5: the exact surface test (check.py) against the KO-PROP-UR cylinder must give this, not a box hit.")
c("CL-B4-TIP-WING-ALT", "Blade to wing upper skin if the cant sense were mirrored (R3 print)", calc="CALC-B4-TIP-WING",
  output="wing_upper_gap_env_m_alt", unit="m", how="Trade point only.")
c("CL-B4-GAP-TUBE-ENV", "Blade swept volume (E1 envelope) to the bare CF motor tube surface, exact 3D (CR-E1-46a)",
  calc="CALC-B4-TIP-WING", output="tube_gap_env_m", unit="m",
  limit=(">=", P + "requirements.prop_clearance_min_m"), verifies=["R-PROP-CLEAR"], parts=PRP + FINS,
  note="the R4 controlling prop clearance. CL-B4-GAP-TUBE is the hub mid-plane to the tube face (zero-thickness "
       "blade); the blade's aft face is 6 mm behind it. Same value as E1's CL-E1-TIP-GAP-TUBE (independent code)",
  how="Printed 25 mm gauge between the blade trailing face at the tip and the tube, blade over the wing-side "
      "position (T-B4-INSTALLED, T-E1-MOTOR-RM).")
c("CL-B4-GAP-TUBE-FIX5", "Blade to tube with the mount face 5 mm forward (E1 CR-E1-44, face_ahead 0.0075)",
  calc="CALC-B4-TIP-WING", output="tube_gap_env_fix5_m", unit="m",
  limit=(">=", P + "requirements.prop_clearance_min_m"), how="As CL-B4-GAP-TUBE-ENV on the R5 mount.")
c("CL-B4-TIP-WING-FIX5", "Blade to wing upper skin with the mount face 5 mm forward", calc="CALC-B4-TIP-WING",
  output="wing_upper_gap_env_fix5_m", unit="m", limit=(">=", P + "requirements.prop_clearance_min_m"),
  how="As CL-B4-TIP-WING on the R5 mount.")
c("CL-B4-GAP-TUBE", "Blade-to-tube axial gap, hub mid-plane (zero-thickness blade) over the bare tube face",
  calc="CALC-B4-GEOM",
  output="gap_tube_face_m", unit="m", limit=(">=", P + "requirements.prop_clearance_min_m"),
  verifies=["R-PROP-CLEAR"], parts=PRP + FINS,
  how="On the built airframe: ruler from the blade tip, turned over the tube, to the tube face.")
c("CL-B4-GAP-COLLAR", "Blade-to-collar axial gap, canted disc (minimum)", calc="CALC-B4-GEOM",
  output="gap_collar_face_m", unit="m", limit=(">=", P + "requirements.prop_clearance_min_m"),
  verifies=["R-PROP-CLEAR"], parts=PRP + FINS, how="As CL-B4-GAP-TUBE at the collars.")
c("CL-B4-GAP-TUBE-ALT", "Blade-to-tube gap if the spin map were mirrored (disc edge swings away from the tube)",
  calc="CALC-B4-GEOM", output="gap_tube_face_m_alt", unit="m", how="Trade point only.")
c("CL-B4-BPF", "Hover blade-passing frequency (vibration input to C4)", calc="CALC-B4-GEOM", output="bpf_hover_hz",
  unit="Hz", how="FFT of the FC IMU log in hover (ArduPilot batch sampler).")
c("CL-B4-BPF-MAX", "Blade-passing frequency at full throttle (14.8 V)", calc="CALC-B4-GEOM", output="bpf_max_hz",
  unit="Hz", how="From rpm on the stand.")
c("CL-B4-TIPMACH", "Tip Mach number at full throttle", calc="CALC-B4-GEOM", output="tip_mach_max", unit="-",
  limit=("<=", 0.5), how="From rpm on the stand.")

kit.test("T-B4-STAND", "Isolated static thrust A/B: 11x5.5MR and 11x4.5MR on one X3108S",
         verifies=["CL-B4-FM", "CL-B4-HOVER-SHAFT", "CL-B4-RPM-MAX", "CL-B4-HOVER-Q", "CL-B4-FM-OLD"], state="planned",
         procedure="H1 stand (shared with T-E1-STAND), 14.8 V, 10 % throttle steps; log thrust, torque, rpm, V, A.")
kit.test("T-B4-INSTALLED", "Installed thrust with the R3 fin station mock-up and a wing strip",
         verifies=["CL-B4-DOWNLOAD", "CL-B4-TUBE-LOAD", "CL-B4-WING-GAP", "CL-B4-ITEMS-HOVER", "CL-B4-GAP-TUBE",
                   "CL-B4-GAP-TUBE-ENV", "CL-B4-TIP-WING"],
         state="planned",
         procedure="Same stand; the printed 7 deg canted mount on a 22 mm tube cut to the R3 end (0.172 m from the "
                   "chord plane), mount and station collars with their ears, one 10 x 3 mm brace strip to a dummy "
                   "anchor, an ESC dummy (8 x 28 x 46 mm) on the pad station, a two-layer 0.21 m half-fin with the "
                   "R3 top edge, and a 0.32 m S5010 wing strip at the right offset; measure the blade-tip gap over "
                   "the tube by hand first; compare thrust at equal rpm with and without; repeat with the brace and "
                   "ESC removed, then the fin, then the strip.")
kit.test("T-B4-YAW", "Fin side force and yaw moment from swirl and cant",
         verifies=["CL-B4-YAW", "CL-B4-SWIRL-FIN", "CL-B4-F-AXIS"], state="planned",
         procedure="Stand with torque cell and the 7 deg canted mount; the half-fin mock-up on its own side-force "
                   "cell (two load points give the centre of pressure); at hover thrust record reaction torque and "
                   "fin side force, then with the 0 deg mount. Body-axis yaw factor = 1 + F z_cp / Q.")
kit.test("T-B4-CRUISE", "Cruise prop check, car-top or flight", verifies=["CL-B4-CRUISE-ETA", "CL-B4-CRUISE-W"],
         state="planned", procedure="Car-top rig at performance.cruise_ms (GPS) or logged level cruise on the twin: "
                                    "rpm, current, voltage; compare with CALC-B4-CRUISE.")


def _write_results():
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    res = {}
    for nid, n in kit.nodes.items():
        if n["type"] == "calculation":
            res[nid] = n.get("outputs")
    (out / "props_results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    kit.write()
    _write_results()
