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

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
IN = 0.0254
PROPS = {  # key -> (data file, diameter in, APC rpm-limit constant, mass g, price USD, pusher part exists)
    "11x4.5MR": ("apc_per3_11x45MR.csv", 11.0, 105000, 17.0, 3.83, "MRP"),
    "11x4.7SF": ("apc_per3_11x47SF.csv", 11.0, 65000, 20.0, 3.50, "SFP"),
    "11x5.5MR": ("apc_per3_11x55MR.csv", 11.0, 105000, 17.0, 3.83, "MRP"),
    "11x5.5E": ("apc_per3_11x55E.csv", 11.0, 150000, 23.0, 4.17, "EP"),
    "12x4.5MR": ("apc_per3_12x45MR.csv", 12.0, 105000, 20.0, 4.10, "MRP"),
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
A("ASM-B4-FIN-T", "Fin trailing-edge thickness 10 mm", "blunt fin TE base, two 4.8 mm foam-board layers",
  value=0.010, unit="m", basis="params fins.material and fins.layers; D3 has not drawn the fin yet")
A("ASM-B4-FOOT", "Foot frontal area 30 x 30 mm", "crushable printed foot on each fin TE tip, on the prop axis",
  value=0.0009, unit="m2", basis="D5 has not drawn the foot; 6 g printed PETG cap")
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

A("ASM-B4-CANT", "Proposed motor cant 3 deg", "each motor tilted 3 deg tangentially (about the line from the "
  "aircraft x-axis to the motor) so its thrust adds yaw torque in the sense of its reaction torque", value=3.0,
  unit="deg", basis="B4 proposal; common multirotor practice for yaw authority; D3/F4 decide", status="PROPOSED")

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
          equation="hover: T_h = k_dl m g / 4 -> rpm, P_shaft from Ct, Cp ; FM = T^1.5 / sqrt(2 rho A) / P_shaft ; "
                   "full throttle: (V - rpm/Kv)/R = Q/Kt + I0 (E1 constants, hot winding) ; "
                   "T/W (bus held, no current limit) = 4 T_max / (k_dl m g) ; rpm limit = K / D_in (APC)",
          inputs=dict(E1_MOTOR, v="P:battery.v_nom", v_sag="ASM-B4-VSAG", m=P + "requirements.mtow_gate_kg",
                      k_dl=P + "propulsion.download_factor", g=P + "env.g_ms2", rho=P + "env.rho_kgm3"),
          units={"v": "V", "m": "kg", "rho": "kg/m3"})
def static_points(kv, rm, i0, esc, pack, tcu, v, v_sag, m, k_dl, g, rho):
    mot_hot, _ = _motor(kv, rm, i0, esc, pack, tcu, hot=True)
    mot, esc_w = _motor(kv, rm, i0, esc, pack, tcu, hot=False)
    out = {}
    Th = k_dl * m * g / 4.0
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
            res["tw_unlimited" + tag] = 4 * T / (k_dl * m * g)
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
# ---------------------------------------------------------------- 5. download (installed thrust loss in hover)
def _v_axial(vi, x, R):
    return vi * (1 + x / math.sqrt(x * x + R * R))


def _r_slip(x, R):
    return R / math.sqrt(1 + x / math.sqrt(x * x + R * R))


@kit.calc("CALC-B4-DOWNLOAD", title="Hover download on tube, half-fins, feet and the wing beside the disc",
          assumes=["ASM-B4-CD-TUBE", "ASM-B4-PROFILE", "ASM-B4-FIN-T", "ASM-B4-FOOT", "ASM-B4-MIX"],
          cites=["SRC-S5010"],
          equation="v_i = sqrt(T / 2 rho A) ; v(x) = v_i (1 + x / sqrt(x^2 + R^2)) ; r_s = R / sqrt(v/v_i) ; "
                   "D = Cd q d L (tube) + 2 Cf q S (fin) + 0.5 q t h (fin base) + q A (foot) + D_wing ; "
                   "wing: reach(x) = r_s + mix (x - x_p) ; gap(x) = z_m - reach - z_surf(x) (S5010 upper, and lower "
                   "for the lower discs) ; where gap < 0 the wetted strip w = 2 sqrt(reach^2 - (z_m - z_surf)^2) "
                   "carries Cf q/3 (mixing-layer mean of u^2) ; k = 1 + D/T",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "x_mount": P + "propulsion.stations.x_mount_m", "d_tube": P + "fins.tube.od_m",
                  "d_motor": P + "propulsion.motor_diameter_m", "fin_te": P + "fins.te_x_m",
                  "foot_h": P + "cg.foot_height_m", "cd": "ASM-B4-CD-TUBE", "prof": "ASM-B4-PROFILE",
                  "t_fin": "ASM-B4-FIN-T", "a_foot": "ASM-B4-FOOT", "z_m": P + "propulsion.stations.z_m",
                  "c": P + "wing.chord_m", "mix": "ASM-B4-MIX"},
          units={"m": "kg", "D": "m", "x_prop": "m", "x_mount": "m", "d_tube": "m", "d_motor": "m", "fin_te": "m",
                 "z_m": "m", "c": "m"})
def download(m, g, rho, D, x_prop, x_mount, d_tube, d_motor, fin_te, foot_h, cd, prof, t_fin, a_foot, z_m, c, mix):
    R = D / 2
    T = m * g / 4.0
    vi = math.sqrt(T / (2 * rho * math.pi * R * R))
    nu = 1.5e-5
    res = {}
    for tag, pf in (("", 1.0), ("_high", prof)):
        x_t = x_mount - x_prop                         # tube axis behind the disk
        v_t = _v_axial(vi, x_t, R)
        L_t = _r_slip(x_t, R) - d_motor / 2           # inner part shadowed by the motor can
        D_tube = cd * 0.5 * rho * v_t ** 2 * pf * d_tube * L_t
        x_f = 0.5 * ((x_mount + d_tube / 2) + fin_te) - x_prop   # fin mid-chord behind the disk
        v_f = _v_axial(vi, x_f, R)
        h_f = _r_slip(x_f, R)
        c_f = fin_te - (x_mount + d_tube / 2)
        Re = v_f * c_f / nu
        cf = 0.074 / Re ** 0.2
        D_fin = 2 * cf * 0.5 * rho * v_f ** 2 * pf * c_f * h_f
        x_b = fin_te - x_prop
        h_b = _r_slip(x_b, R)
        v_b = _v_axial(vi, x_b, R)
        D_base = 0.5 * 0.5 * rho * v_b ** 2 * pf * t_fin * h_b
        D_foot = 1.0 * 0.5 * rho * (0.5 * v_b) ** 2 * a_foot   # foot sits on the hub axis: hub-wake deficit ~50 %
        D_wing, gap_min, x_gap = _wing_strip(rho, vi, R, x_prop, z_m, c, mix, pf, nu)
        Dt = D_tube + D_fin + D_base + D_foot + D_wing
        res["k" + tag] = 1 + Dt / T
        if not tag:
            up, lo = _airfoil_surfaces()
            z_top = max(z for _, z in up) * c
            res.update({"vi_ms": vi, "tube_n": D_tube, "fin_n": D_fin, "fin_base_n": D_base, "foot_n": D_foot,
                        "wing_n": D_wing, "wing_gap_min_m": gap_min, "wing_gap_min_x_m": x_gap,
                        "disc_edge_over_wing_top_m": z_m - R - z_top,
                        "disc_edge_over_chord_plane_m": z_m - R,
                        "tube_x_behind_disc_m": x_t, "fin_mid_x_behind_disc_m": x_f,
                        "tube_frac_of_disk": d_tube * L_t / (math.pi * R * R)})
    return res


def _wing_strip(rho, vi, R, x_prop, z_m, c, mix, pf, nu, n=64):
    """Wing beside the disc: the slipstream (plus its mixing layer) reaching the S5010 surface at the fin station.
    Returns (download N for one disc, minimum gap m, x of the minimum gap m). Upper discs see the upper surface,
    lower discs the lower surface; the worse of the two is used for every disc."""
    up, lo = _airfoil_surfaces()
    zu = lambda xc: _interp([p[0] for p in up], [p[1] for p in up], xc) * c
    zl = lambda xc: -_interp([p[0] for p in lo], [p[1] for p in lo], xc) * c    # distance below the chord plane
    D_w, gap_min, x_gap = 0.0, float("inf"), 0.0
    h = c / n
    for k in range(n + 1):
        x = k * h
        xd = x - x_prop
        if xd <= 0:
            continue
        reach = _r_slip(xd, R) + mix * xd
        z_s = max(zu(x / c), zl(x / c))
        gap = (z_m - z_s) - reach
        if gap < gap_min:
            gap_min, x_gap = gap, x
        if gap < 0:
            w = 2 * math.sqrt(max(reach * reach - (z_m - z_s) ** 2, 0.0))
            v = _v_axial(vi, xd, R)
            cf = 0.074 / max(v * max(x, h) / nu, 1e3) ** 0.2
            wk = 0.5 if k in (0, n) else 1.0
            D_w += wk * cf * 0.5 * rho * v * v * pf / 3.0 * w * h
    return D_w, gap_min, x_gap


# ---------------------------------------------------------------- 6. slipstream vs elevons and wing
@kit.calc("CALC-B4-WAKE", title="Slipstream edge versus elevons and wing", assumes=["ASM-B4-MIX"],
          equation="hover: inner edge z = z_m - r_s(x) - mix (x - x_p) ; elevon tip z = c_e sin(delta_max) ; "
                   "cruise: r_s ~ R (lightly loaded) ; gap = edge - surface",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "z_m": P + "propulsion.stations.z_m", "c": P + "wing.chord_m", "tc": P + "wing.t_c",
                  "fe": P + "wing.elevon.chord_frac", "defl": P + "wing.elevon.deflection_deg", "mix": "ASM-B4-MIX"},
          units={"m": "kg", "D": "m", "x_prop": "m", "z_m": "m", "c": "m"})
def wake_vs_surfaces(m, g, rho, D, x_prop, z_m, c, tc, fe, defl, mix):
    R = D / 2
    x_hinge = c * (1 - fe)
    ce = c * fe
    z_elevon = ce * math.sin(math.radians(max(abs(d) for d in defl)))
    out = {}
    for name, x in (("hinge", x_hinge), ("te", c)):
        xd = x - x_prop
        edge_h = z_m - _r_slip(xd, R) - mix * xd
        edge_c = z_m - R - mix * xd
        out[f"hover_edge_z_{name}_m"] = edge_h
        out[f"cruise_edge_z_{name}_m"] = edge_c
    out["elevon_tip_z_max_m"] = z_elevon
    out["hover_gap_elevon_m"] = min(out["hover_edge_z_hinge_m"], out["hover_edge_z_te_m"]) - z_elevon
    out["cruise_gap_elevon_m"] = min(out["cruise_edge_z_hinge_m"], out["cruise_edge_z_te_m"]) - z_elevon
    out["cruise_gap_wing_surface_m"] = (z_m - R - mix * (0.3 * c - x_prop)) - tc * c / 2
    return out


# ---------------------------------------------------------------- 7. pitot placement (actuator-disk vortex cylinders)
def pitot_candidates(pod_x, boom, z_boom, x_prop):
    """name -> (x, y, z) of the probe tip, m. The chosen one is the pod-nose boom (POD-006); the rest bracket it."""
    return {
        "pod_boom": (pod_x - boom, 0.0, z_boom),                  # chosen: = params avionics.pitot_tip_xyz_m
        "pod_face": (pod_x, 0.0, z_boom),                          # no boom: probe flush with the pod front
        "pod_boom_long": (pod_x - boom - 0.10, 0.0, z_boom),       # 100 mm longer boom
        "wing_LE_y0.15": (x_prop - 0.075, 0.15, 0.0),              # 75 mm boom on the inboard wing LE
        "wing_LE_y0.53": (x_prop - 0.075, 0.53, 0.0),              # 75 mm boom on the outboard wing LE
    }


def _induced(pt, disks, R, gamma, L, N):
    u = 0.0
    for (xp, yp, zp) in disks:
        X = pt[0] - xp
        r = math.hypot(pt[1] - yp, pt[2] - zp)
        if r < R and X > 0:
            return float("nan")                    # inside a slipstream
        u += cylinder_ux(R, gamma, X, max(r, 1e-6), L, N)
    return u


@kit.calc("CALC-B4-PITOT", title="Prop-induced airspeed error at pitot candidates", assumes=["ASM-B4-PITOT-ERR"],
          equation="v from T = 2 rho A v (V + v) ; four semi-infinite vortex cylinders, gamma = 2 v ; "
                   "u_x = integral of ring velocities (elliptic K, E) ; error = u_x / V ; "
                   "grid: Simpson N = 100/200/400, wake length 20/40/80 R",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "y_m": P + "propulsion.stations.y_m", "z_m": P + "propulsion.stations.z_m",
                  "ld": P + "performance.ld_cruise", "V": P + "performance.cruise_ms",
                  "Vt": P + "performance.transition_min_ms", "lim": "ASM-B4-PITOT-ERR",
                  "pod_x": P + "pod.x_le_m", "boom": "ASM-B4-BOOM"},
          units={"m": "kg", "D": "m", "x_prop": "m", "y_m": "m", "z_m": "m", "V": "m/s", "Vt": "m/s",
                 "pod_x": "m"})
def pitot(m, g, rho, D, x_prop, y_m, z_m, ld, V, Vt, lim, pod_x, boom):
    R = D / 2
    PITOT_CANDIDATES = pitot_candidates(pod_x, boom[0], boom[1], x_prop)
    A_d = math.pi * R * R
    disks = [(x_prop, sy * y_m, sz * z_m) for sy in (1, -1) for sz in (1, -1)]
    cases = {"cruise": (V, m * g / ld / 4), "transition": (Vt, m * g / 4), "hover": (0.0, m * g / 4)}
    tip = PITOT_CANDIDATES["pod_boom"]
    out = {"tip_x_m": tip[0], "tip_z_m": tip[2], "tip_ahead_of_disc_m": x_prop - tip[0]}
    # self-test: the disk centre of an isolated cylinder sees gamma/2; far downstream inside sees gamma
    out["selftest_centre_over_half_gamma"] = cylinder_ux(R, 1.0, 0.0, 1e-6, 80 * R, 400) / 0.5
    worst = {}
    for case, (Vc, T) in cases.items():
        v = (-Vc + math.sqrt(Vc * Vc + 2 * T / (rho * A_d))) / 2
        gam = 2 * v
        for name, pt in PITOT_CANDIDATES.items():
            levels = [_induced(pt, disks, R, gam, Lr * R, N) for Lr, N in ((20, 100), (40, 200), (80, 400))]
            u = levels[-1]
            out[f"{case}__{name}__u_ms"] = u
            out[f"{case}__{name}__conv"] = abs(levels[-1] - levels[-2]) / (Vc if Vc > 0 else max(abs(u), 1e-9))
            if Vc > 0:
                out[f"{case}__{name}__err"] = u / Vc
                worst[name] = max(worst.get(name, 0.0), abs(u / Vc))
    for name, w in worst.items():
        out[f"worst_err__{name}"] = w
    best = min(worst, key=worst.get)
    out["best_candidate"] = list(PITOT_CANDIDATES).index(best)          # 0 pod_boom ... 4 wing_LE_y0.53
    out["best_worst_err"] = worst[best]
    out["max_conv"] = max(v for k, v in out.items() if k.endswith("__conv") and not k.startswith("hover"))
    return out


# ---------------------------------------------------------------- 8. swirl recovered by the fin (hover yaw authority)
@kit.calc("CALC-B4-SWIRL", title="Fin swirl recovery and hover yaw authority", assumes=["ASM-B4-SPAN-AR"],
          equation="Gamma_s = Q / (rho v_i pi (R^2 - r_h^2)) ; v_t = Gamma_s / r ; alpha = atan(v_t / v_a) ; "
                   "CL = 2 pi AR alpha / (2 + sqrt(AR^2 + 4)) (Helmbold) ; M = CL q c h r_cp ; f = M / Q ; "
                   "yaw per N of differential thrust = (Q/T)(1 - f) + r_arm sin(cant) ; "
                   "half-fin root moment = F (z_m - r_cp - z_root), z_root = mean S5010 surface over the fin chord",
          inputs={"Th": "CL-B4-HOVER-T", "Q": "CL-B4-HOVER-Q", "rho": P + "env.rho_kgm3",
                  "D": P + "propulsion.prop_diameter_m",
                  "d_motor": P + "propulsion.motor_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "x_mount": P + "propulsion.stations.x_mount_m", "d_tube": P + "fins.tube.od_m",
                  "fin_te": P + "fins.te_x_m", "ar_k": "ASM-B4-SPAN-AR",
                  "y_m": P + "propulsion.stations.y_m", "z_m": P + "propulsion.stations.z_m", "cant": "ASM-B4-CANT",
                  "c": P + "wing.chord_m"},
          units={"D": "m", "rho": "kg/m3", "c": "m"})
def swirl(Th, Q, rho, D, d_motor, x_prop, x_mount, d_tube, fin_te, ar_k, y_m, z_m, cant, c):
    R = D / 2
    vi = math.sqrt(Th / (2 * rho * math.pi * R * R))
    rh = d_motor / 2
    Gs = Q / (rho * vi * math.pi * (R * R - rh * rh))
    c_f = fin_te - (x_mount + d_tube / 2)
    x_f = 0.5 * ((x_mount + d_tube / 2) + fin_te) - x_prop
    h = _r_slip(x_f, R)
    va = _v_axial(vi, x_f, R)
    r_cp = 0.6 * h
    vt = Gs / r_cp
    alpha = math.atan(vt / va)
    AR = ar_k * h * h / (h * c_f)
    CL = 2 * math.pi * AR * alpha / (2 + math.sqrt(AR * AR + 4))
    q = 0.5 * rho * (va * va + vt * vt)
    M = CL * q * c_f * h * r_cp
    f = min(M / Q, 1.0)
    arm = math.hypot(y_m, z_m)
    k_iso = Q / Th                                       # yaw moment per newton of differential thrust, isolated
    need = max(k_iso - k_iso * (1 - f), 0.0)             # what the fin takes away
    cant_min = math.degrees(math.asin(min(need / arm, 1.0)))
    k_cant = k_iso * (1 - f) + arm * math.sin(math.radians(cant))
    up, lo = _airfoil_surfaces()
    x0, x1 = x_mount + d_tube / 2, fin_te
    zs = [_interp([p[0] for p in up], [p[1] for p in up], (x0 + (x1 - x0) * k / 20) / c) * c for k in range(21)]
    z_root = sum(zs) / len(zs)
    F = CL * q * c_f * h
    return {"half_fin_root_moment_nm": F * (z_m - r_cp - z_root), "half_fin_cp_above_root_m": z_m - r_cp - z_root,
            "half_fin_chord_m": c_f, "half_fin_wetted_span_m": h, "half_fin_aspect_ratio": AR, "swirl_q_pa": q,
            "torque_nm": Q, "swirl_deg": math.degrees(alpha), "fin_side_force_n": CL * q * c_f * h,
            "f_mid": f, "f_low": 0.5 * f, "yaw_authority_factor_mid": 1 - f, "yaw_authority_factor_high": 1 - 0.5 * f,
            "yaw_arm_m": arm, "cant_min_deg": cant_min, "yaw_with_cant_over_isolated": k_cant / k_iso,
            "yaw_with_cant_no_reaction_over_isolated": arm * math.sin(math.radians(cant)) / k_iso,
            "cant_thrust_loss": 1 - math.cos(math.radians(cant))}


# ---------------------------------------------------------------- 9. clearances, VRS, ground effect, noise
@kit.calc("CALC-B4-GEOM", title="Prop spacing, descent limit, ground effect and tones", assumes=["ASM-B4-VRS"],
          equation="gap_v = 2 z_m - D ; gap_l = 2 y_m - D ; v_h = sqrt(k m g / (8 rho A)) ; V_d,max = 0.28 v_h ; "
                   "T_IGE/T = 1 / (1 - (R / 4 h)^2) ; M_tip = pi D n / a ; BPF = 2 n",
          inputs={"D": P + "propulsion.prop_diameter_m", "y_m": P + "propulsion.stations.y_m",
                  "z_m": P + "propulsion.stations.z_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "x_mount": P + "propulsion.stations.x_mount_m", "d_tube": P + "fins.tube.od_m",
                  "fin_te": P + "fins.te_x_m", "foot_h": P + "cg.foot_height_m", "m": P + "requirements.mtow_gate_kg",
                  "k": P + "propulsion.download_factor", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "vrs": "ASM-B4-VRS", "rpm_h": "CL-B4-HOVER-RPM", "rpm_max": "CL-B4-RPM-MAX"},
          units={"D": "m", "y_m": "m", "z_m": "m", "m": "kg"})
def geometry(D, y_m, z_m, x_prop, x_mount, d_tube, fin_te, foot_h, m, k, g, rho, vrs, rpm_h, rpm_max):
    R = D / 2
    vh = math.sqrt(k * m * g / 4 / (2 * rho * math.pi * R * R))
    h = fin_te + foot_h - x_prop
    a = 343.0
    return {"gap_vertical_m": 2 * z_m - D, "gap_vertical_over_D": (2 * z_m - D) / D, "gap_lateral_m": 2 * y_m - D,
            "gap_tube_face_m": (x_mount - d_tube / 2) - x_prop, "gap_tube_over_D": ((x_mount - d_tube / 2) - x_prop) / D,
            "vh_ms": vh, "descent_max_ms": vrs * vh, "prop_height_m": h, "ige_gain": 1 / (1 - (R / (4 * h)) ** 2) - 1,
            "tip_mach_hover": math.pi * D * rpm_h / 60 / a, "tip_mach_max": math.pi * D * rpm_max / 60 / a,
            "bpf_hover_hz": 2 * rpm_h / 60, "one_p_hover_hz": rpm_h / 60, "bpf_max_hz": 2 * rpm_max / 60}


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
                   "T/W at the cap = 4 T(rpm_cap) / (k_dl m g)",
          inputs=dict(E1_MOTOR, ocv="ASM-E1-OCV", m=P + "requirements.mtow_gate_kg",
                      k_dl=P + "propulsion.download_factor", g=P + "env.g_ms2", rho=P + "env.rho_kgm3"),
          units={"m": "kg", "rho": "kg/m3"})
def rpm_full(kv, rm, i0, esc, pack, tcu, ocv, m, k_dl, g, rho):
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
        out["tw_at_cap" + tag] = 4 * t_cap / (k_dl * m * g)
    return out


# ---------------------------------------------------------------- claims
SEL = "11x5.5MR"                                                     # B4 selection (concurs with CR-E1-06)
OLD = "11x4.5MR"
PRP = [f"PRP-003-{s}" for s in ("UR", "UL", "LR", "LL")]          # the four props (A4 interface plan ids)
FINS = ["FIN-001-L", "FIN-001-R", "FIN-002-L", "FIN-002-R"]
c = kit.claim
c("CL-B4-DATA", "APC data copied without error (worst row)", calc="CALC-B4-DATA",
  output="max_rel_err", unit="-", limit=("<=", 0.005),
  how="Re-run props.py; every row's printed N and W reproduce its Ct and Cp within 0.5 % (a typo shows as > 1 %).")
c("CL-B4-HOVER-T", "Hover thrust per prop at the gate incl. download", calc="CALC-B4-STATIC",
  output="hover_thrust_per_prop_n", unit="N", how="= 1.06 x 2.6 kg x g / 4; re-check after T-B4-INSTALLED.")
c("CL-B4-DL", "Disk loading at the gate (11 in)", calc="CALC-B4-STATIC", output=f"disk_loading_npm2__{SEL}",
  unit="N/m2", how="Hand check: 6.76 N / 0.0613 m2.")
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
c("CL-B4-UIUC-ETA", "UIUC-measured over APC-predicted cruise efficiency, 11x4.7SF (data spread)",
  calc="CALC-B4-XCHECK", output="eta_ratio_uiuc_over_apc__11x4.7SF", unit="-",
  how="The 11x5.5MR value comes from T-B4-STAND plus a car-top or flight check; this ratio is the expected spread.")
c("CL-B4-UIUC-ETA-E", "UIUC-measured over APC-predicted cruise efficiency, 11x5.5E", calc="CALC-B4-XCHECK",
  output="eta_ratio_uiuc_over_apc__11x5.5E", unit="-", how="As CL-B4-UIUC-ETA.")
c("CL-B4-DOWNLOAD", "Hover download factor (modelled, mean loading)", calc="CALC-B4-DOWNLOAD", output="k", unit="-",
  limit=("<=", P + "propulsion.download_factor"), parts=FINS,
  how="T-B4-INSTALLED: thrust stand with a tube + fin mock-up behind the prop; installed/isolated thrust ratio.")
c("CL-B4-DOWNLOAD-HIGH", "Hover download factor (peaked loading)", calc="CALC-B4-DOWNLOAD", output="k_high", unit="-",
  limit=("<=", P + "propulsion.download_factor"), parts=FINS, how="T-B4-INSTALLED.")
c("CL-B4-ELEVON-HOVER", "Elevons outside the hover slipstream (gap)", calc="CALC-B4-WAKE", output="hover_gap_elevon_m",
  unit="m", limit=(">=", 0.0),
  how="Tufts on the elevons during a tethered hover: they stay still. Consequence: zero elevon authority in hover.")
c("CL-B4-ELEVON-CRUISE", "Elevon tip vs cruise slipstream edge (negative = inside the mixing layer)",
  calc="CALC-B4-WAKE", output="cruise_gap_elevon_m", unit="m", how="Tufts on the elevons in cruise, camera on the fin.")
c("CL-B4-PITOT", "Worst prop-induced airspeed error at the chosen pitot (pod-nose boom, tip 80 mm ahead of the pod)",
  calc="CALC-B4-PITOT", output="worst_err__pod_boom", unit="-", limit=("<=", "ASM-B4-PITOT-ERR"),
  parts=["AVN-005", "POD-006"],
  how="Fly constant GPS-groundspeed legs in calm air at two throttle settings; airspeed must not step with throttle.")
c("CL-B4-PITOT-TIP-X", "Pitot tip x station (pod front - boom; = params avionics.pitot_tip_xyz_m[0])",
  calc="CALC-B4-PITOT", output="tip_x_m", unit="m", parts=["AVN-005", "POD-006"],
  how="Measure the tip from the wing LE on the built airframe with the boom plugged in.")
c("CL-B4-PITOT-FACE", "Prop-induced airspeed error with no boom (probe at the pod front)", calc="CALC-B4-PITOT",
  output="worst_err__pod_face", unit="-", limit=("<=", "ASM-B4-PITOT-ERR"),
  how="Same flight test as CL-B4-PITOT; shows what the boom buys.")
c("CL-B4-PITOT-WING", "Prop-induced airspeed error, inboard wing LE at y = 0.15 m (rejected)", calc="CALC-B4-PITOT",
  output="worst_err__wing_LE_y0.15", unit="-", limit=("<=", "ASM-B4-PITOT-ERR"),
  how="Same flight test; shows why the inboard wing LE is not used.")
c("CL-B4-PITOT-CONV", "Pitot model wake/grid convergence (max change, last two levels)", calc="CALC-B4-PITOT",
  output="max_conv", unit="-", limit=("<=", 0.002),
  how="Re-run: three wake lengths and Simpson grids; change as a fraction of airspeed.")
c("CL-B4-SWIRL-FIN", "Swirl side force on each half-fin in hover (static, mean; same sense on both halves of a fin)",
  calc="CALC-B4-SWIRL", output="fin_side_force_n", unit="N", parts=FINS,
  how="T-B4-YAW: side force on a half-fin mock-up (0.275 m chord) behind the prop at hover thrust, or the "
      "reaction-torque difference divided by the centre-of-pressure radius.")
c("CL-B4-SWIRL-FIN-M", "Swirl bending moment at each half-fin root (wing skin), hover", calc="CALC-B4-SWIRL",
  output="half_fin_root_moment_nm", unit="N*m", parts=FINS, how="As CL-B4-SWIRL-FIN, times the measured cp height.")
c("CL-B4-TUBE-LOAD", "Slipstream drag on each motor tube in hover (mean loading)", calc="CALC-B4-DOWNLOAD",
  output="tube_n", unit="N", parts=FINS, how="T-B4-INSTALLED: thrust with and without the tube.")
c("CL-B4-WING-GAP", "Hover slipstream (incl. mixing layer) clearance to the wing surface at the fin station",
  calc="CALC-B4-DOWNLOAD", output="wing_gap_min_m", unit="m", limit=(">=", 0.0), parts=FINS,
  how="T-B4-INSTALLED with a wing-section strip at the right height; tufts on the wing beside the fin in a "
      "tethered hover stay still.")
c("CL-B4-YAW", "Hover yaw authority left by fin swirl recovery (fraction of isolated)", calc="CALC-B4-SWIRL",
  output="yaw_authority_factor_mid", unit="-",
  how="T-B4-YAW: reaction torque on the stand with and without a fin mock-up; tethered hover yaw step.")
c("CL-B4-YAW-CANT", "Hover yaw authority with 3 deg motor cant (fraction of isolated, untilted)",
  calc="CALC-B4-SWIRL", output="yaw_with_cant_over_isolated", unit="-", limit=(">=", 1.0), assumes=["ASM-B4-CANT"],
  how="T-B4-YAW then a tethered-hover yaw step with the canted mounts.")
c("CL-B4-DESCENT", "Maximum vertical descent rate (vortex-ring margin)", calc="CALC-B4-GEOM", output="descent_max_ms",
  unit="m/s", how="F4 sets Q_WP_SPEED_DN and Q_LAND_SPEED below this; watch for thrust oscillation in descent tests.")
c("CL-B4-GAP-V", "Vertical prop-to-prop tip gap", calc="CALC-B4-GEOM", output="gap_vertical_m", unit="m",
  limit=(">=", P + "requirements.prop_clearance_min_m"), verifies=["R-PROP-CLEAR"], parts=PRP,
  cites=["SRC-B4-ZHOU-ROTOR"], how="Measure on the built airframe with props fitted. 0.36 D tip gap: mean thrust "
  "change < 2 % per the cited rotor-pair data.")
c("CL-B4-BPF", "Hover blade-passing frequency (vibration input to C4)", calc="CALC-B4-GEOM", output="bpf_hover_hz",
  unit="Hz", how="FFT of the FC IMU log in hover (ArduPilot batch sampler).")
c("CL-B4-BPF-MAX", "Blade-passing frequency at full throttle (14.8 V)", calc="CALC-B4-GEOM", output="bpf_max_hz",
  unit="Hz", how="From rpm on the stand.")
c("CL-B4-TIPMACH", "Tip Mach number at full throttle", calc="CALC-B4-GEOM", output="tip_mach_max", unit="-",
  limit=("<=", 0.5), how="From rpm on the stand.")

kit.test("T-B4-STAND", "Isolated static thrust A/B: 11x5.5MR and 11x4.5MR on one X3108S",
         verifies=["CL-B4-FM", "CL-B4-HOVER-SHAFT", "CL-B4-RPM-MAX", "CL-B4-HOVER-Q", "CL-B4-FM-OLD"], state="planned",
         procedure="H1 stand (shared with T-E1-STAND), 14.8 V, 10 % throttle steps; log thrust, torque, rpm, V, A.")
kit.test("T-B4-INSTALLED", "Installed thrust with tube, half-fin and wing-strip mock-up",
         verifies=["CL-B4-DOWNLOAD", "CL-B4-TUBE-LOAD", "CL-B4-WING-GAP"], state="planned",
         procedure="Same stand; 22 mm tube with its face 39 mm behind the prop plane, a 0.275 m-chord foam-board "
                   "half-fin behind it and a 0.32 m S5010 wing strip whose upper surface sits 28 mm below the disc "
                   "edge (LE 5 mm behind the prop plane); compare thrust at equal rpm with and without; repeat with "
                   "the fin, then the strip, removed.")
kit.test("T-B4-YAW", "Fin swirl effect on reaction torque", verifies=["CL-B4-YAW"], state="planned",
         procedure="Stand with torque cell: reaction torque at hover thrust with and without the fin mock-up.")
kit.test("T-B4-CRUISE", "Cruise prop check, car-top or flight", verifies=["CL-B4-CRUISE-ETA", "CL-B4-CRUISE-W"],
         state="planned", procedure="Car-top rig at performance.cruise_ms (GPS) or logged level cruise on the twin: rpm, current, "
                                    "voltage; compare with CALC-B4-CRUISE.")


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
