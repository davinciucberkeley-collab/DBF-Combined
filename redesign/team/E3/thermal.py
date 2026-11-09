"""E3 thermal engineer: motor, motor-mount, ESC, pack and flight-controller temperatures across the K09-L mission,
the field-ambient ceiling (R-THERMAL / P19) and the operating rules that follow from it.

Run:  python -I redesign/team/E3/thermal.py        -> claims.json beside this file, results printed
Then: python -I redesign/proofs/build_graph.py      -> confirms nothing drifted

Method (one paragraph). Lumped-capacitance (RC) networks integrated in time over E2's mission phase tables
(`CL-E2-BUDGET-PESS-TABLE` / `-BASE-TABLE`). Per motor station the bus power of each phase is turned into an
operating point with E1's motor constants (Kv, R_m(T), I0, ESC 10 mOhm + 0.5 W) and a torque law Q = c n^2 scaled
from B4's hover and cruise points with E1's calibration factor kP; the copper resistance follows the winding
temperature. Motor: one node (winding + stator + base), conductance 1/R_th to ambient (E1's 1.0 K/W nominal,
1.5 K/W design). The printed mount sees the motor base, taken equal to the motor node (conservative). ESC: one node
on its fin pad, flat-plate forced convection (Incropera eq. 7.30) at the local slipstream velocity of B4's momentum
model (`_v_axial`) times a tube-wake / fin-boundary-layer factor, plus radiation; the pad side is adiabatic. Pod:
three nodes (pack, flight controller, pod air) with I^2 R pack heat from E2's currents and cell resistance, wall
conduction and, with the recommended vents, ram-air exchange in cruise. Every temperature is checked against its
rating; the field-ambient ceiling is the ambient at which the first part reaches its rating (bisection). Checks:
time-step convergence (3 levels), steady hover vs the hand value loss x R_th, adiabatic pack vs E2's `CL-E2-PACK-T-END`.
R2 (2026-11-09): ESC pad moved to D3's layout, strap area, 15-30 degC ambient sweep, GT-04 pass lines for H1.
Python 3 standard library only.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
SIGMA = 5.670e-8

# ---------------------------------------------------------------- sources
kit.source("SRC-E3-INCROPERA", "Incropera, DeWitt et al., Fundamentals of Heat and Mass Transfer, 6th ed.", kind="book",
           url="https://www.wiley.com/en-us/Fundamentals+of+Heat+and+Mass+Transfer%2C+6th+Edition-p-9780471457282",
           where="eq. 7.30 laminar flat plate Nu = 0.664 Re^0.5 Pr^1/3; eq. 9.27 natural convection; Table A.4 air at "
                 "300 K (nu 15.89e-6 m2/s, k 0.0263 W/m K, Pr 0.707); Table 1.1 film-coefficient ranges")
kit.source("SRC-E3-PETG-TDS", "Prusament PETG technical data sheet (HDT 68 degC at 0.45 and 1.8 MPa)", kind="web",
           url="https://prusament.com/materials/petg/",
           where="HDT 68 degC (ISO 75, 0.45 MPa); value carried from the previous design's materials research "
                 "(docs/research/thermal.md section 4, read 2026-10-25); not re-opened by E3",
           status="UNVERIFIED")
kit.source("SRC-E3-ASA-TDS", "Prusament ASA technical data sheet v1.1 (May 2024)", kind="web",
           url="https://storage.googleapis.com/prusa3d-content-prod-14e8-wordpress-prusament-prod/2024/05/e6cbbc16-tds_prusament-asa_2024_it.pdf",
           where="HDT 93 degC at 0.45 MPa (ISO 75), from the search snippet of the Italian TDS 2026-11-09; other ASA "
                 "brands 100-101 degC", status="UNVERIFIED")
kit.source("SRC-E3-EFM8BB2", "Silicon Labs EFM8BB21F16G-C-QFN20 (BLHeli_S ESC MCU) temperature grade", kind="web",
           url="https://www.silabs.com/mcu/8-bit/efm8-busy-bee/device.efm8bb21f16g-qfn20",
           checked="2026-11-09",
           where="'G' grade -40 to +85 degC operating (Silicon Labs device page; Arrow, Farnell listings agree). The "
                 "LANRC 45 A ESC publishes no temperature rating")
kit.source("SRC-E3-STM32F405", "STM32F405RGT6 ambient rating -40 to +85 degC (6-suffix)", kind="web",
           url="https://hken.rs-online.com/web/p/microcontrollers/7468217",
           where="checked 2026-11-02 for the previous design (docs/research/thermal.md section 4); the F405 wing "
                 "boards on the shortlist use this part. IMU ICM-42688-P is rated to +85 degC too", status="UNVERIFIED")
kit.source("SRC-E3-LIPO-RATING", "LiPo discharge temperature rating 60 degC (hobby pack norm)", kind="web",
           url="https://www.ovonicshop.com/pages/lipo-battery-guide",
           where="hobby LiPo makers state discharge -20 to +60 degC and advise landing below ~50 degC for life; Ovonic "
                 "page not opened (rate-limited); confirm on the pack label/manual on arrival", status="UNVERIFIED")

# ---------------------------------------------------------------- assumptions
A = kit.assumption
A("ASM-E3-AIR", "Air properties at 300 K", "kinematic viscosity, conductivity, Prandtl number used in every film coefficient",
  basis="Incropera Table A.4; within +-6 % from 10 to 40 degC, so held constant", value=[15.89e-6, 0.0263, 0.707],
  unit="m2/s,W/m K,-", cites=["SRC-E3-INCROPERA"])
A("ASM-E3-MOTOR-CP", "Motor specific heat 540 J/kg K", "one lumped node of 81 g: copper ~20 g, laminations ~25 g, "
  "aluminium bell and base ~20 g, magnets and shaft ~16 g", basis="mass-weighted c_p (Cu 385, Fe 450, Al 900, NdFeB 440, "
  "steel 470) = 520-560", value=540.0, unit="J/kg K", status="UNVERIFIED")
A("ASM-E3-RTH-DESIGN", "Motor thermal resistance 1.5 K/W (design)", "winding-to-ambient resistance in its own prop wash "
  "used for the design case; E1's 1.0 K/W is the nominal case", basis="E1 back-solved 0.83 K/W from the maker's 94 degC "
  "at the 30 A row, a test that was probably not steady, so the true value is higher; an outer-surface-only "
  "correlation (rotating bell, no internal ventilation) gives ~3 K/W, a bound. 1.5 x nominal until T-E3-MOTOR-TAU",
  value=1.5, unit="K/W", status="UNVERIFIED", cites=["SRC-E1-X3108S-DATA"])
A("ASM-E3-ESC", "ESC body 45 x 20 x 6 mm, 11 g, 700 J/kg K", "LANRC 45 A in heat-shrink, strapped flat on the fin pad, "
  "FET side out; the pad face is adiabatic (foam board); the leads' fin effect is ignored (conservative)",
  basis="typical 45 A BLHeli_S 2-6S board size (LANRC publishes no drawing); mass from E1's 11 g with leads "
        "(ASM-E1-PART-MASS); c_p FR4 + copper + parts. Measure on arrival", value=[0.045, 0.020, 0.006, 0.011, 700.0],
  unit="m,m,m,kg,J/kg K", status="UNVERIFIED")
A("ASM-E3-ESC-PAD", "ESC pad centre at x 0.101 m, 0.072 m from the motor axis (D3 layout)", "pad FIN-007 on the "
  "half-fin face from x 0.078 to 0.124 m, centre |z| 0.118 m (72 mm toward the wing from the motor axis), ESC long "
  "side along x; the 20 mm wide ESC spans 62-82 mm from the axis",
  basis="subsystems/fins/params.json fin_detail.esc_pad (x0 0.078, len 0.046, z 0.118; D3 R2, CL-D3-ESC-WASH), which "
        "replaces E3's R1 proposal (x 0.10, 60 mm). Inside the contracted slipstream, clear of the hub wake (r < 30 mm)",
  value=[0.101, 0.072], unit="m,m", status="PROPOSED")
A("ASM-E3-ESC-STRAP", "Hook-and-loop strap covers 320 mm2 of the ESC's exposed faces", "one 10 mm strap through the two "
  "pad slots wraps the ESC once: it covers 10 mm x (20 + 2 x 6) mm of the FET face and sides, which then reject no "
  "heat (conservative)", basis="fins BUILD.md / params fin_detail.esc_pad.slot_m (10 mm strap); ESC 45 x 20 x 6 "
  "(ASM-E3-ESC): exposed 1 680 mm2 -> 1 360 mm2 (-19 %)", value=0.00032, unit="m2", status="PROPOSED")
A("ASM-E3-WAKE", "Local-velocity factor at the ESC 0.7 nominal / 0.5 design", "velocity over the ESC = factor x the "
  "slipstream (hover) or free-stream (cruise) velocity, for the motor-tube wake and the fin boundary layer",
  basis="the pad is 2.5 tube diameters behind the 22 mm tube, on its wake centreline; a cylinder wake keeps a 0.3-0.5 "
        "velocity deficit there; the 6 mm ESC sits inside a 3-6 mm fin boundary layer. Measure with a hot-wire or "
        "the ESC temperature on the stand (T-E3-ESC-PAD)", value=[0.7, 0.5], unit="-", status="UNVERIFIED")
A("ASM-E3-EMISS", "Emissivity 0.9, still-air film 8 W/m2 K", "heat-shrink, solder mask, anodised and painted surfaces; "
  "natural convection on small parts with no flow", basis="Incropera Table 1.1 (free convection, gases 2-25); "
  "radiation linearised at the part temperature", value=[0.9, 8.0], unit="-,W/m2 K", cites=["SRC-E3-INCROPERA"])
A("ASM-E3-PACK", "Pack c_p 1 000 J/kg K, cell R 5 mOhm design, R(T) x 1.5 per 15 K below 25 degC",
  "pack heat = I^2 x cells x R_cell(T); R_cell = 4 mOhm nominal (E2), 5 mOhm design (E2's T-E2-IR acceptance limit); "
  "R(T) = R25 x 1.5^((25 - T)/15) below 25 degC, R25 above (no credit for warm cells)",
  basis="E2 ASM-E2-R-CELL, ASM-E2-COLD-R and T-E2-IR pass value; c_p as E2 (LiPo 1 000-1 100)", value=[1000.0, 0.005],
  unit="J/kg K,ohm", status="UNVERIFIED", cites=["SRC-OVONIC-4S6500"])
A("ASM-E3-FC", "Flight controller 2.0 W, 50 x 36 mm, 20 J/K", "FC board dissipation: MCU, IMU/baro, OSD and its 5 V "
  "regulator (servo BEC in a separate UBEC); board both faces exchange with the pod air",
  basis="previous design itemisation 2.0 W (docs/research/thermal.md section 2); F405 wing boards 50-54 x 32-36 mm; "
        "F3 replaces with the bench current", value=[2.0, 0.050, 0.036, 20.0], unit="W,m,m,J/K", status="UNVERIFIED")
A("ASM-E3-POD", "Pod shell and vents", "shell foam board 5 mm, k 0.035 W/m K, the face on the wing adiabatic; pod air "
  "10 J/K; recommended vents: inlet 15 x 30 mm at the pod nose and an equal exit at the rear, internal velocity "
  "0.25 x airspeed in cruise, no vent flow credited in hover",
  basis="foam board k 0.03-0.04; vent sizing as the previous design (docs/research/thermal.md 6.4); 0.25 for inlet "
        "and internal losses EST", value=[0.005, 0.035, 10.0, 0.00045, 0.25], unit="m,W/m K,J/K,m2,-",
  status="PROPOSED")
A("ASM-E3-PROFILE", "Mission order and hover split", "chronological order of E2's phases: ground, climb, first hover "
  "(half of the hover row), forward transition, cruise, back-transition, second hover, descent; motors off on the "
  "ground; climb, hover, transitions and descent use the static prop law; the abuse case adds 30 s at the 100 A "
  "limiter after the first hover", basis="mission profile params.json#mission.profile; E2 ASM-E2-PROFILE; E1 CR-E1-10 "
  "(full throttle <= 30 s)", value=[0.5, 30.0], unit="-,s")
A("ASM-E3-LIMITS", "Temperature limits", "motor winding/stator 80; PETG mount HDT 68; ASA mount HDT 93; ESC 85; pack "
  "60 rating and 50 at landing for life; FC 85 degC",
  basis="motor: previous test-plan abort value (SunnySky publishes none; the maker's own test reached 94 degC); "
        "PETG and ASA: TDS HDT at 0.45 MPa; ESC: EFM8BB21 G-grade MCU; pack: hobby LiPo rating (E2 uses 50 at "
        "landing); FC: STM32F405 and IMU rating", value=[80.0, 68.0, 93.0, 85.0, 60.0, 50.0, 85.0], unit="degC",
  status="UNVERIFIED", cites=["SRC-E3-PETG-TDS", "SRC-E3-ASA-TDS", "SRC-E3-EFM8BB2", "SRC-E3-LIPO-RATING",
                              "SRC-E3-STM32F405"])
A("ASM-E3-SUN", "Morning sun 700 W/m2, absorptivity 0.9 dark / 0.3 white, outside film 20 W/m2 K, 600 s soak",
  "parked aircraft at set-up, sun on the pod top", basis="clear April morning 09-10 h; Incropera Table 1.1; "
  "five-minute set-up plus waiting", value=[700.0, 0.9, 0.3, 20.0, 600.0], unit="W/m2,-,-,W/m2 K,s", status="UNVERIFIED")

A("ASM-E3-AMB-SWEEP", "Ambient sweep 15, 20, 25, 30 degC", "field ambients at which every temperature is reported "
  "for the mission table; the pack starts at ambient (E2's >= 20 degC warm-up rule is not modelled, so the 15 degC row "
  "is a cold-pack row)", basis="E3 task scope 2026-11-09 (15-30 degC); params env.ambient_design_c is [10, 30] and "
  "its cold end stays in CL-E3-PACK-RISE-COLD", value=[15.0, 20.0, 25.0, 30.0], unit="degC", status="PROPOSED")
A("ASM-E3-GT04", "H1 GT-04 stand sequence", "one station on the stand with the ESC on the half-fin mock-up: 120 s at "
  "690 gf hover thrust, 10 s at the 25 A limiter share, 60 s at hover thrust, then stop; no forward flow",
  basis="team/H1/GROUND-TEST-PLAN.md GT-04 step 1 (CR-H1-06)", value=[120.0, 6.77, 10.0, 60.0], unit="s,N,s,s",
  status="PROPOSED")

# ---------------------------------------------------------------- model helpers (pure functions)
LIM_KEYS = ["motor", "petg", "asa", "esc", "pack", "pack_life", "fc"]


def film(v, L, air):
    """Laminar flat-plate average film coefficient (Incropera eq. 7.30)."""
    nu, k, pr = air
    re = max(v, 1e-6) * L / nu
    return 0.664 * re ** 0.5 * pr ** (1 / 3) * k / L


def h_rad(T_c, eps):
    T = T_c + 273.15
    return 4 * eps * SIGMA * T ** 3


def motor_point(pb, c, kv, rm25, a_cu, i0, resc, pfix, tw):
    """Operating point at bus power pb (W) per station, torque law Q = c n^2 (n in rpm)."""
    kt = 60 / (2 * math.pi * kv)
    rm = rm25 * (1 + a_cu * (tw - 25))

    def bus(n):
        im = c * n * n / kt + i0
        e = n / kv
        return im * (e + im * rm) + im * im * resc + pfix, im, e

    lo, hi = 0.0, 30000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if bus(mid)[0] < pb:
            lo = mid
        else:
            hi = mid
    _, im, e = bus(lo)
    return {"n": lo, "im": im, "loss_m": im * im * rm + i0 * e, "loss_e": im * im * resc + pfix}


def build_phases(table, avn_w, split, i_lim, v_nom, t_abuse, hover_only_s=None, abuse=False):
    """Chronological phase list: (name, seconds, bus W per motor or None, regime, pack A)."""
    r = {row[0]: row for row in table}
    def m(row):
        return (row[2] - avn_w) / 4

    hov = r["hover (mission)"]
    if hover_only_s is not None:
        return [("ground", r["ground, armed checks"][1], None, "off", r["ground, armed checks"][3]),
                ("hover-only sortie", hover_only_s, m(hov), "static", hov[3])]
    ph = [("ground", r["ground, armed checks"][1], None, "off", r["ground, armed checks"][3]),
          ("climb", r["climb 0-50 m"][1], m(r["climb 0-50 m"]), "static", r["climb 0-50 m"][3]),
          ("hover 1", hov[1] * split, m(hov), "static", hov[3])]
    if abuse:
        ph.append(("limiter", t_abuse, i_lim * v_nom, "static", 4 * i_lim))
    ph += [("transition fwd", r["transition forward"][1], m(r["transition forward"]), "static", r["transition forward"][3]),
           ("cruise", r["cruise"][1], m(r["cruise"]), "cruise", r["cruise"][3]),
           ("back-transition", r["back-transition"][1], m(r["back-transition"]), "static", r["back-transition"][3]),
           ("hover 2", hov[1] * (1 - split), m(hov), "static", hov[3]),
           ("descent", r["descent 50-0 m"][1], m(r["descent 50-0 m"]), "static", r["descent 50-0 m"][3])]
    return ph


def simulate(amb, phases, k, rth, wake, r_cell, vented, dt=0.5, pack_start=None, adiabatic_pack=False,
             pack_r_const=None):
    """Integrate all nodes over the phase list. k: shared constants. Returns peaks and end values (degC)."""
    air, eps, h_nat = k["air"], k["eps"], k["h_nat"]
    L, W, t, m_esc, cp_esc = k["esc"]
    a_esc = L * W + 2 * L * t + 2 * W * t - k["strap"]
    c_esc = m_esc * cp_esc
    c_mot = k["m_motor"] * k["cp_motor"]
    pk_, pw, ph_ = k["pack_size"]
    a_pack = 2 * (pk_ * pw + pk_ * ph_ + pw * ph_) - pk_ * pw          # tray face excluded
    c_pack = k["m_pack"] * k["cp_pack"]
    q_fc, fl, fw, c_fc = k["fc"]
    a_fc = 2 * fl * fw
    sl, sw, sh = k["pod_size"]
    a_shell = 2 * (sl * sh + sw * sh) + sl * sw                           # bottom on the wing excluded
    t_w, k_w, c_air, a_vent, f_vent = k["pod"]
    T = {"mot": amb, "esc": amb, "fc": amb, "air": amb,
         "pack": amb if pack_start is None else pack_start}
    peak = dict(T)
    peak_t = {key: 0.0 for key in T}
    time = 0.0
    log = []
    for name, dur, pb, regime, i_pack in phases:
        if pb is not None:
            c = k["c_static"] if regime == "static" else k["c_cruise"]
            pts = [motor_point(pb, c, k["kv"], k["rm"], k["a_cu"], k["i0"], k["resc"], k["pfix"], tw)
                   for tw in (25.0, 125.0)]
            n = pts[0]["n"]
            if regime == "static":
                thrust = k["kT"] * k["T_h"] * (n / k["n_h"]) ** 2
                vi = math.sqrt(thrust / (2 * k["rho"] * math.pi * k["R"] ** 2))
                x = k["x_pad"] - k["x_prop"]
                v_loc = vi * (1 + x / math.sqrt(x * x + k["R"] ** 2))
                v_air = 0.0
            else:
                v_loc = k["V_c"]
                v_air = k["V_c"]
            g_mot = 1.0 / rth
        else:
            pts, v_loc, v_air, g_mot = None, 0.0, 0.0, 0.04
        steps = max(1, int(round(dur / dt)))
        h = dur / steps
        for _ in range(steps):
            if pts:
                f = (T["mot"] - 25.0) / 100.0
                q_m = pts[0]["loss_m"] + f * (pts[1]["loss_m"] - pts[0]["loss_m"])
                q_e = pts[0]["loss_e"] + f * (pts[1]["loss_e"] - pts[0]["loss_e"])
                h_e = film(wake * v_loc, L, air) + h_rad(T["esc"], eps)
            else:
                q_m = 0.0
                q_e = k["pfix"]
                h_e = h_nat + h_rad(T["esc"], eps)
            # pod: pack heat, harness heat in the pod, conductances
            if pack_r_const is not None:
                rc = pack_r_const
            else:
                rc = r_cell * (k["cold"] ** ((25.0 - T["pack"]) / 15.0) if T["pack"] < 25.0 else 1.0)
            q_pack = i_pack ** 2 * k["cells"] * rc
            q_ext = i_pack ** 2 * k["r_ext"]
            h_out = (film(v_air, sl, air) if v_air > 0 else h_nat) + h_rad(amb, eps)
            g_wall = a_shell / (t_w / k_w + 1.0 / h_out)
            v_in = f_vent * v_air if vented else 0.0
            g_vent = 1.2 * v_in * a_vent * 1005.0
            h_in_p = (film(v_in, pk_, air) if v_in > 0 else h_nat) + h_rad(T["pack"], eps)
            h_in_f = (film(v_in, fl, air) if v_in > 0 else h_nat) + h_rad(T["fc"], eps)
            g_pa = 0.0 if adiabatic_pack else h_in_p * a_pack
            g_fa = h_in_f * a_fc
            d = {
                "mot": (q_m - g_mot * (T["mot"] - amb)) / c_mot,
                "esc": (q_e - h_e * a_esc * (T["esc"] - amb)) / c_esc,
                "pack": (q_pack - g_pa * (T["pack"] - T["air"])) / c_pack,
                "fc": (q_fc - g_fa * (T["fc"] - T["air"])) / c_fc,
                "air": (q_ext + g_pa * (T["pack"] - T["air"]) + g_fa * (T["fc"] - T["air"])
                        - (g_wall + g_vent) * (T["air"] - amb)) / c_air,
            }
            # the pod-air node is fast: relax it implicitly to keep the explicit step stable
            g_air = g_pa + g_fa + g_wall + g_vent
            T_air_eq = (q_ext + g_pa * T["pack"] + g_fa * T["fc"] + (g_wall + g_vent) * amb) / g_air
            for key in ("mot", "esc", "pack", "fc"):
                T[key] += h * d[key]
            T["air"] = T_air_eq + (T["air"] - T_air_eq) * math.exp(-h * g_air / c_air)
            time += h
            for key in T:
                if T[key] > peak[key]:
                    peak[key], peak_t[key] = T[key], time
        log.append((name, round(time, 1), {kk: round(vv, 2) for kk, vv in T.items()},
                    None if not pts else {"rpm": round(pts[0]["n"]), "I_m_A": round(pts[0]["im"], 2),
                                          "loss_motor_W": round(pts[0]["loss_m"], 2),
                                          "loss_esc_W": round(pts[0]["loss_e"], 2), "v_local_ms": round(v_loc, 2)}))
    return {"peak": peak, "peak_t": peak_t, "end": dict(T), "log": log}


def consts(rho, D, x_prop, x_pad_r, strap, kv, rm, i0, esc, tcu, kP, kT, T_h, Q_h, n_h, n_c, P_c, V_c, m_motor, cp_motor,
           esc_geom, air, emiss, pack, cells, m_pack, pack_size, cold, r_ext, fc, pod, pod_size):
    return {"rho": rho, "R": D / 2, "x_prop": x_prop, "x_pad": x_pad_r[0], "strap": strap, "kv": kv, "rm": rm, "i0": i0,
            "resc": esc[0], "pfix": esc[1], "a_cu": tcu[0], "kT": kT, "T_h": T_h, "n_h": n_h,
            "c_static": kP * Q_h / n_h ** 2,
            "c_cruise": kP * (P_c / (2 * math.pi * n_c / 60)) / n_c ** 2, "V_c": V_c,
            "m_motor": m_motor, "cp_motor": cp_motor, "esc": esc_geom, "air": air, "eps": emiss[0],
            "h_nat": emiss[1], "cp_pack": pack[0], "cells": cells, "m_pack": m_pack, "pack_size": pack_size,
            "cold": cold, "r_ext": r_ext, "fc": fc, "pod": pod, "pod_size": pod_size}


def limits_dict(lim):
    return dict(zip(LIM_KEYS, lim))


def worst(res):
    p = res["peak"]
    return {"motor": p["mot"], "petg": p["mot"], "asa": p["mot"], "esc": p["esc"], "pack": p["pack"],
            "pack_life": res["end"]["pack"], "fc": p["fc"]}


def ceiling(run, lim, key):
    """Highest ambient (degC) at which part `key` stays at its limit; run(amb) -> worst()."""
    lo, hi = -20.0, 80.0
    if run(hi)[key] <= lim[key]:
        return hi
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if run(mid)[key] <= lim[key]:
            lo = mid
        else:
            hi = mid
    return lo


COMMON = {"rho": P + "env.rho_kgm3", "D": P + "propulsion.prop_diameter_m",
          "x_prop": P + "propulsion.stations.x_prop_plane_m", "x_pad_r": "ASM-E3-ESC-PAD", "strap": "ASM-E3-ESC-STRAP",
          "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "tcu": "ASM-E1-TCOPPER",
          "kP": "CL-E1-KP", "kT": "CL-E1-KT", "T_h": "CL-B4-HOVER-T", "Q_h": "CL-B4-HOVER-Q", "n_h": "CL-B4-HOVER-RPM",
          "n_c": "CL-B4-CRUISE-RPM", "P_c": "CL-B4-CRUISE-SHAFT", "V_c": P + "performance.cruise_ms",
          "m_motor": P + "propulsion.motor_mass_kg", "cp_motor": "ASM-E3-MOTOR-CP", "esc_geom": "ASM-E3-ESC",
          "air": "ASM-E3-AIR", "emiss": "ASM-E3-EMISS", "pack": "ASM-E3-PACK", "cells": P + "battery.cells_s",
          "m_pack": P + "battery.mass_kg", "pack_size": P + "battery.size_m", "cold": "ASM-E2-COLD-R",
          "r_ext": "ASM-E2-R-EXT", "fc": "ASM-E3-FC", "pod": "ASM-E3-POD", "pod_size": P + "pod.size_m"}
CU = {"rho": "kg/m3", "D": "m", "x_prop": "m", "V_c": "m/s", "m_motor": "kg", "m_pack": "kg", "pack_size": "m",
      "pod_size": "m"}
CASE = {"pess": "CL-E2-BUDGET-PESS-TABLE", "base": "CL-E2-BUDGET-BASE-TABLE", "avn": "ASM-E2-AVIONICS-W",
        "rth_nom": "ASM-E1-RTH", "rth_des": "ASM-E3-RTH-DESIGN", "wake": "ASM-E3-WAKE", "r_nom": "ASM-E2-R-CELL",
        "prof": "ASM-E3-PROFILE", "i_lim": "CL-E1-ILIM-I", "v_nom": P + "battery.v_nom", "lim": "ASM-E3-LIMITS",
        "amb_range": P + "env.ambient_design_c", "t_hov_only": "CL-E2-HOVER-ONLY-MIN-PESS"}
CASE_U = {"v_nom": "V", "amb_range": "degC", "t_hov_only": "min"}
ASSUMES = ["ASM-E3-AIR", "ASM-E3-MOTOR-CP", "ASM-E3-RTH-DESIGN", "ASM-E3-ESC", "ASM-E3-ESC-PAD", "ASM-E3-ESC-STRAP", "ASM-E3-WAKE",
           "ASM-E3-EMISS", "ASM-E3-PACK", "ASM-E3-FC", "ASM-E3-POD", "ASM-E3-PROFILE", "ASM-E3-LIMITS",
           "ASM-E1-RTH", "ASM-E1-RM", "ASM-E1-I0", "ASM-E1-ESC", "ASM-E2-R-CELL", "ASM-E2-COLD-R"]


def setup(kw):
    case_keys = set(CASE)
    k = consts(**{a: kw[a] for a in kw if a not in case_keys})
    c = {a: kw[a] for a in kw if a in case_keys}
    lim = limits_dict(c["lim"])
    split, t_abuse = c["prof"]
    design = dict(table=c["pess"], rth=c["rth_des"], wake=c["wake"][1], r_cell=kw["pack"][1])
    nominal = dict(table=c["base"], rth=c["rth_nom"], wake=c["wake"][0], r_cell=c["r_nom"])
    return k, c, lim, split, t_abuse, design, nominal


def run_case(k, c, case, amb, split, t_abuse, vented=True, abuse=False, hover_only=False, dt=0.5):
    ph = build_phases(case["table"], c["avn"], split, c["i_lim"], c["v_nom"], t_abuse,
                      hover_only_s=c["t_hov_only"] * 60 if hover_only else None, abuse=abuse)
    return simulate(amb, ph, k, case["rth"], case["wake"], case["r_cell"], vented, dt=dt)


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-E3-MISSION", title="Mission temperatures at the top of the design ambient (30 degC)",
          equation="per node C dT/dt = Q(t, T) - sum G (T - T_neighbour) ; Q_motor = I_m^2 R_m(T) + I0 n/Kv, "
                   "Q_esc = I_m^2 R_esc + P_fix with I_m from P_bus = I_m (n/Kv + I_m R_m) + Q_esc and Q = kP Q_B4 "
                   "(n/n_B4)^2 ; ESC h = 0.664 Re^0.5 Pr^1/3 k/L at f_wake v(x), v(x) = v_i (1 + x/sqrt(x^2+R^2)) + "
                   "4 eps sigma T^3 ; pack Q = I^2 N R_cell(T) ; explicit Euler dt 0.5 s, pod air relaxed exactly",
          inputs={**COMMON, **CASE}, units={**CU, **CASE_U}, assumes=ASSUMES,
          cites=["SRC-E3-INCROPERA"])
def mission(**kw):
    k, c, lim, split, t_abuse, design, nominal = setup(kw)
    amb = c["amb_range"][1]
    out = {}
    for tag, case in (("des", design), ("nom", nominal)):
        r = run_case(k, c, case, amb, split, t_abuse)
        out[f"motor_peak_{tag}_c"] = r["peak"]["mot"]
        out[f"esc_peak_{tag}_c"] = r["peak"]["esc"]
        out[f"pack_end_{tag}_c"] = r["end"]["pack"]
        out[f"fc_peak_{tag}_c"] = r["peak"]["fc"]
        if tag == "des":
            out["phase_log_des"] = [[n, t, T, op] for n, t, T, op in r["log"]]
    r = run_case(k, c, design, amb, split, t_abuse, vented=False)
    out["fc_peak_sealed_des_c"] = r["peak"]["fc"]
    out["pack_end_sealed_des_c"] = r["end"]["pack"]
    r = run_case(k, c, design, amb, split, t_abuse, abuse=True)
    out["motor_peak_abuse_des_c"] = r["peak"]["mot"]
    out["esc_peak_abuse_des_c"] = r["peak"]["esc"]
    r = run_case(k, c, design, amb, split, t_abuse, hover_only=True, vented=False)
    out["motor_peak_hoveronly_des_c"] = r["peak"]["mot"]
    out["esc_peak_hoveronly_des_c"] = r["peak"]["esc"]
    out["fc_peak_hoveronly_des_c"] = r["peak"]["fc"]
    out["pack_end_hoveronly_des_c"] = r["end"]["pack"]
    # cold morning (bottom of the range): pack start at ambient as E2's case, then E2's rule (>= 20 degC)
    amb_lo = c["amb_range"][0]
    r = run_case(k, c, design, amb_lo, split, t_abuse)
    out["pack_rise_cold_des_k"] = r["end"]["pack"] - amb_lo
    # pad inside the slipstream: contracted radius at the pad minus (pad radius + half ESC width)
    x = k["x_pad"] - k["x_prop"]
    r_s = k["R"] / math.sqrt(1 + x / math.sqrt(x * x + k["R"] ** 2))
    out["pad_r_margin_m"] = r_s - (kw["x_pad_r"][1] + k["esc"][1] / 2)
    out["pad_hub_margin_m"] = (kw["x_pad_r"][1] - k["esc"][1] / 2) - 0.03
    # hover operating point (design) for the loss cross-check with E1 CR-E1-10
    hov = [row for row in c["pess"] if row[0] == "hover (mission)"][0]
    pt = motor_point((hov[2] - c["avn"]) / 4, k["c_static"], k["kv"], k["rm"], k["a_cu"], k["i0"], k["resc"],
                     k["pfix"], 70.0)
    out["hover_loss_motor_des_w"], out["hover_loss_esc_des_w"], out["hover_im_des_a"] = pt["loss_m"], pt["loss_e"], pt["im"]
    hovb = [row for row in c["base"] if row[0] == "hover (mission)"][0]
    pt = motor_point((hovb[2] - c["avn"]) / 4, k["c_static"], k["kv"], k["rm"], k["a_cu"], k["i0"], k["resc"],
                     k["pfix"], 50.0)
    out["hover_loss_motor_nom_w"], out["hover_loss_esc_nom_w"] = pt["loss_m"], pt["loss_e"]
    pt = motor_point(c["i_lim"] * c["v_nom"], k["c_static"], k["kv"], k["rm"], k["a_cu"], k["i0"], k["resc"],
                     k["pfix"], 80.0)
    out["limiter_loss_motor_w"], out["limiter_loss_esc_w"], out["limiter_im_a"] = pt["loss_m"], pt["loss_e"], pt["im"]
    return out


@kit.calc("CALC-E3-CEILING", title="Field-ambient ceiling per part (design case, mission and hover-only sortie)",
          equation="T_amb,max(part) = max T_amb such that peak T_part(T_amb) <= limit (bisection on the full model) ; "
                   "ceiling = min over parts ; pack starts at ambient",
          inputs={**COMMON, **CASE}, units={**CU, **CASE_U}, assumes=ASSUMES)
def ceilings(**kw):
    k, c, lim, split, t_abuse, design, nominal = setup(kw)
    out = {}
    runs = {
        "mission_des": lambda a: worst(run_case(k, c, design, a, split, t_abuse, dt=1.0)),
        "mission_nom": lambda a: worst(run_case(k, c, nominal, a, split, t_abuse, dt=1.0)),
        "hoveronly_des": lambda a: worst(run_case(k, c, design, a, split, t_abuse, hover_only=True, vented=False,
                                                  dt=1.0)),
        "abuse_des": lambda a: worst(run_case(k, c, design, a, split, t_abuse, abuse=True, dt=1.0)),
    }
    for rn, fn in runs.items():
        for key in ("motor", "petg", "asa", "esc", "pack", "pack_life", "fc"):
            out[f"{rn}__{key}"] = ceiling(fn, lim, key)
        parts = ("motor", "asa", "esc", "pack", "fc")          # ASA mount = recommended build
        out[f"{rn}__min_asa_c"] = min(out[f"{rn}__{p}"] for p in parts)
        out[f"{rn}__min_petg_c"] = min(out[f"{rn}__{p}"] for p in parts + ("petg",))
    return out


@kit.calc("CALC-E3-CHECKS", title="Model checks: time-step convergence, steady hover vs hand value, pack vs E2",
          equation="convergence: peaks at dt 1.0 / 0.5 / 0.25 s ; steady: T_mot - T_amb -> Q_m R_th after 15 tau ; "
                   "pack: adiabatic, R x 1.0 at 30 degC and x 1.5 at 10 degC, E2 phase order -> E2's dT",
          inputs={**COMMON, **CASE, "e2_t_end": "CL-E2-PACK-T-END"}, units={**CU, **CASE_U, "e2_t_end": "degC"},
          assumes=ASSUMES)
def checks(**kw):
    e2 = kw.pop("e2_t_end")
    k, c, lim, split, t_abuse, design, nominal = setup(kw)
    amb = c["amb_range"][1]
    peaks = []
    for dt in (1.0, 0.5, 0.25):
        r = run_case(k, c, design, amb, split, t_abuse, dt=dt)
        peaks.append([r["peak"]["mot"], r["peak"]["esc"], r["end"]["pack"], r["peak"]["fc"]])
    conv = max(abs(a - b) for a, b in zip(peaks[1], peaks[2]))
    # steady hover: 15 time constants of continuous design hover
    hov = [row for row in c["pess"] if row[0] == "hover (mission)"][0]
    pb = (hov[2] - c["avn"]) / 4
    long = [("hover", 15 * k["m_motor"] * k["cp_motor"] * design["rth"], pb, "static", hov[3])]
    r = simulate(amb, long, k, design["rth"], design["wake"], design["r_cell"], True)
    tw = r["end"]["mot"]
    pt = motor_point(pb, k["c_static"], k["kv"], k["rm"], k["a_cu"], k["i0"], k["resc"], k["pfix"], tw)
    hand = pt["loss_m"] * design["rth"]
    steady_err = (tw - amb) - hand
    # E2 replication: adiabatic pack, E2's own (table) order, constant R, c 1000
    ph = [(row[0], row[1], None, "off", row[3]) for row in c["pess"]]
    rr = simulate(amb, ph, k, design["rth"], design["wake"], c["r_nom"], False, adiabatic_pack=True,
                  pack_r_const=c["r_nom"])
    e2_err = rr["end"]["pack"] - e2
    return {"dt_conv_k": conv, "peaks_dt_1_05_025": peaks, "steady_hover_rise_k": tw - amb,
            "steady_hand_k": hand, "steady_err_k": steady_err, "pack_vs_e2_k": e2_err,
            "motor_steady_hover_des_c": tw}


@kit.calc("CALC-E3-SUN", title="Pre-flight sun soak of the pack in the pod",
          equation="T_sol-air - T_amb = alpha G / h_o ; Q = G_top (T_sa - T_amb), G_top = A_top / (t/k + 1/h_o) ; "
                   "dT_pack <= Q t / (m c) (all of it reaching the pack: upper bound)",
          inputs={"sun": "ASM-E3-SUN", "pod": "ASM-E3-POD", "pod_size": P + "pod.size_m", "m": P + "battery.mass_kg",
                  "pack": "ASM-E3-PACK"}, units={"pod_size": "m", "m": "kg"}, assumes=["ASM-E3-SUN", "ASM-E3-POD"])
def sun(sun, pod, pod_size, m, pack):
    g, a_dark, a_white, ho, t = sun
    a_top = pod_size[0] * pod_size[1]
    g_top = a_top / (pod[0] / pod[1] + 1 / ho)
    out = {}
    for tag, a in (("dark", a_dark), ("white", a_white)):
        dts = a * g / ho
        out[f"skin_rise_{tag}_k"] = dts
        out[f"pack_rise_{tag}_k"] = g_top * dts * t / (m * pack[0])
    return out


@kit.calc("CALC-E3-OPS", title="Operating limits: full-throttle burst length and pack start temperature (design, 30 degC)",
          equation="burst: max t such that peak T_motor <= 80 degC and T_esc <= 85 degC with t s at the limiter after "
                   "the first hover ; pack: max T_start such that T_pack(landing) <= 50 degC (bisection)",
          inputs={**COMMON, **CASE}, units={**CU, **CASE_U}, assumes=ASSUMES)
def ops(**kw):
    k, c, lim, split, t_abuse, design, nominal = setup(kw)
    amb = c["amb_range"][1]

    def burst_ok(t):
        ph = build_phases(design["table"], c["avn"], split, c["i_lim"], c["v_nom"], t, abuse=True)
        r = simulate(amb, ph, k, design["rth"], design["wake"], design["r_cell"], True, dt=0.25)
        return r["peak"]["mot"] <= lim["motor"] and r["peak"]["esc"] <= lim["esc"]
    lo, hi = 0.0, 120.0
    for _ in range(25):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if burst_ok(mid) else (lo, mid)
    burst = lo
    ph = build_phases(design["table"], c["avn"], split, c["i_lim"], c["v_nom"], t_abuse)
    lo, hi = amb - 20.0, 60.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        r = simulate(amb, ph, k, design["rth"], design["wake"], design["r_cell"], True, dt=1.0, pack_start=mid)
        lo, hi = (mid, hi) if r["end"]["pack"] <= lim["pack_life"] else (lo, mid)
    return {"burst_max_s": burst, "pack_start_max_c": lo}


@kit.calc("CALC-E3-SWEEP", title="Mission temperatures across the 15-30 degC field ambient (design and nominal)",
          equation="as CALC-E3-MISSION, repeated at each ambient of ASM-E3-AMB-SWEEP ; rows [T_amb, motor peak, ESC "
                   "peak, pack at landing, FC peak, pod-air peak] in degC",
          inputs={**COMMON, **CASE, "sweep": "ASM-E3-AMB-SWEEP"}, units={**CU, **CASE_U, "sweep": "degC"},
          assumes=ASSUMES + ["ASM-E3-AMB-SWEEP"])
def sweep(**kw):
    amb_list = kw.pop("sweep")
    k, c, lim, split, t_abuse, design, nominal = setup(kw)
    out = {}
    for tag, case in (("des", design), ("nom", nominal)):
        rows = []
        for amb in amb_list:
            r = run_case(k, c, case, amb, split, t_abuse)
            rows.append([amb, r["peak"]["mot"], r["peak"]["esc"], r["end"]["pack"], r["peak"]["fc"], r["peak"]["air"]])
        out[f"rows_{tag}"] = rows
        out[f"motor_rise_spread_{tag}_k"] = (rows[-1][1] - rows[-1][0]) - (rows[0][1] - rows[0][0])
        out[f"esc_rise_spread_{tag}_k"] = (rows[-1][2] - rows[-1][0]) - (rows[0][2] - rows[0][0])
    # the 15 degC morning with E2's rule applied: pack warmed to 20 degC before take-off
    amb0 = amb_list[0]
    ph = build_phases(design["table"], c["avn"], split, c["i_lim"], c["v_nom"], t_abuse)
    r = simulate(amb0, ph, k, design["rth"], design["wake"], design["r_cell"], True, pack_start=20.0)
    out["pack_end_15_warmed_des_c"] = r["end"]["pack"]
    return out


@kit.calc("CALC-E3-GT04", title="Predicted rises for the H1 GT-04 stand sequence (CR-H1-06)",
          equation="rpm from thrust n = n_B4 sqrt(T / (kT T_B4)) ; bus power from the motor model at 25 degC ; RC "
                   "network of CALC-E3-MISSION with the static slipstream, sequence ASM-E3-GT04 ; rise = T - T_amb at "
                   "stop (what the IR reads) ; scaled-to-30 degC = T_meas - T_amb,test + 30",
          inputs={**COMMON, **CASE, "gt": "ASM-E3-GT04"}, units={**CU, **CASE_U}, assumes=ASSUMES + ["ASM-E3-GT04"])
def gt04(**kw):
    gt = kw.pop("gt")
    t1, thrust, t2, t3 = gt
    k, c, lim, split, t_abuse, design, nominal = setup(kw)
    n = k["n_h"] * math.sqrt(thrust / (k["kT"] * k["T_h"]))
    kt = 60 / (2 * math.pi * k["kv"])
    im = k["c_static"] * n * n / kt + k["i0"]
    pb = im * (n / k["kv"] + im * k["rm"]) + im * im * k["resc"] + k["pfix"]
    ph = [("hover", t1, pb, "static", 0.0), ("limiter", t2, c["i_lim"] * c["v_nom"], "static", 0.0),
          ("hover", t3, pb, "static", 0.0)]
    out = {"hover_bus_w": pb}
    amb = 20.0
    for tag, case in (("des", design), ("nom", nominal)):
        r = simulate(amb, ph, k, case["rth"], case["wake"], case["r_cell"], True, dt=0.25)
        out[f"motor_rise_{tag}_k"] = r["end"]["mot"] - amb
        out[f"esc_rise_{tag}_k"] = r["end"]["esc"] - amb
        out[f"esc_peak_rise_{tag}_k"] = r["peak"]["esc"] - amb
        out[f"motor_peak_rise_{tag}_k"] = r["peak"]["mot"] - amb
    return out


# ---------------------------------------------------------------- claims
TH = "Thermocouple (K type) on the part, mission flown or run on the stand at the stated power, log every 5 s; "
kit.claim("CL-E3-MOTOR-PEAK", "Motor (winding/stator) peak, design mission at 30 degC", calc="CALC-E3-MISSION",
          output="motor_peak_des_c", unit="degC", limit=("<=", 80.0), verifies=["R-THERMAL"],
          parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL"],
          how=TH + "T-E3-MOTOR-TAU fits R_th and tau on the stand; T-E3-MISSION reads the can by IR within 30 s of landing.")
kit.claim("CL-E3-MOUNT-PETG", "Motor base on a PETG mount vs HDT 68 - 10 K, design mission at 30 degC",
          calc="CALC-E3-MISSION", output="motor_peak_des_c", unit="degC", limit=("<=", 58.0), verifies=["R-THERMAL"],
          parts=["FIN-003-UR", "FIN-003-UL", "FIN-003-LR", "FIN-003-LL"],
          how="T-E3-MOTOR-TAU: thermocouple between motor base and mount; peak after 90 s hover power + 20 s "
              "transition power from 30 degC must stay < 58 degC (10 K below HDT) for PETG to be accepted.",
          note="10 K below HDT for screw preload and creep under vibration. Fails: the printed motor mount is ASA (HDT 93) or PA-CF, not PETG (CR-E3-01)")
kit.claim("CL-E3-MOUNT-ASA", "Motor base on an ASA mount vs HDT 93 - 10 K, hover-only sortie at 30 degC",
          calc="CALC-E3-MISSION", output="motor_peak_hoveronly_des_c", unit="degC", limit=("<=", 83.0),
          verifies=["R-THERMAL"], parts=["FIN-003-UR", "FIN-003-UL", "FIN-003-LR", "FIN-003-LL"],
          how="As CL-E3-MOUNT-PETG, continuous hover power until steady; mount shows no sag or loss of screw preload.")
kit.claim("CL-E3-ESC-PEAK", "ESC peak on its fin pad, design mission at 30 degC", calc="CALC-E3-MISSION",
          output="esc_peak_des_c", unit="degC", limit=("<=", 85.0), verifies=["R-THERMAL"],
          parts=["PRP-002-UR", "PRP-002-UL", "PRP-002-LR", "PRP-002-LL"],
          how="T-E3-ESC-PAD: thermocouple under the heat-shrink on the FET side, ESC on a fin-pad mock-up behind a "
              "22 mm tube on the thrust stand, hover power 10 min then 30 s at the limiter.")
kit.claim("CL-E3-ESC-ABUSE", "ESC peak with 30 s at the 100 A limiter after the first hover, design, 30 degC",
          calc="CALC-E3-MISSION", output="esc_peak_abuse_des_c", unit="degC", limit=("<=", 85.0),
          verifies=["R-THERMAL"], parts=["PRP-002-UR", "PRP-002-UL", "PRP-002-LR", "PRP-002-LL"],
          how="T-E3-ESC-PAD, the 30 s limiter step.")
kit.claim("CL-E3-MOTOR-ABUSE", "Motor peak with 30 s at the 100 A limiter after the first hover, design, 30 degC",
          calc="CALC-E3-MISSION", output="motor_peak_abuse_des_c", unit="degC", parts=["PRP-001-UR", "FIN-003-UR"],
          how="T-E3-MOTOR-TAU limiter step.",
          note="above the 80 degC winding limit: sustained full throttle is limited by CL-E3-BURST-MAX, not by ambient")
kit.claim("CL-E3-BURST-MAX", "Longest continuous run at the 100 A limiter after the first hover, design, 30 degC",
          calc="CALC-E3-OPS", output="burst_max_s", unit="s", limit=(">=", 10.0), verifies=["R-THERMAL"],
          parts=["PRP-001-UR", "PRP-002-UR", "FIN-003-UR"],
          how="T-E3-MOTOR-TAU limiter step: time from hover-steady to 80 degC stator.",
          note="limit 10 s = a climb-out or gust recovery (E3 choice); flight card: no full throttle longer than this")
kit.claim("CL-E3-PACK-START-MAX", "Highest pack temperature at take-off for <= 50 degC at landing, design, 30 degC",
          calc="CALC-E3-OPS", output="pack_start_max_c", unit="degC", limit=(">=", 30.0), parts=["PWR-001"],
          how="IR thermometer on the pack before it goes in the pod; log it on the flight card.")
kit.claim("CL-E3-PACK-END", "Pack at landing, design mission at 30 degC (5 mOhm/cell, vented pod)",
          calc="CALC-E3-MISSION", output="pack_end_des_c", unit="degC", limit=("<=", 50.0), verifies=["R-THERMAL"],
          parts=["PWR-001"], how="T-E2-MISSION-LOG: IR thermometer on the pack's largest face within 60 s of landing.")
kit.claim("CL-E3-PACK-RISE-COLD", "Pack self-heating over the design mission on a 10 degC morning",
          calc="CALC-E3-MISSION", output="pack_rise_cold_des_k", unit="K", parts=["PWR-001"],
          how="T-E2-MISSION-LOG on a cold morning: pack temperature at take-off and at landing.",
          note="E2's adiabatic 22.9 K (CR-E2-07) less the pod losses and the R(T) drop as the pack warms")
kit.claim("CL-E3-FC-PEAK", "Flight controller peak, design mission at 30 degC, vented pod", calc="CALC-E3-MISSION",
          output="fc_peak_des_c", unit="degC", limit=("<=", 85.0), verifies=["R-THERMAL"], parts=["AVN-001"],
          how="ArduPilot logs the IMU temperature (IMU.T); fly the mission and read the peak.")
kit.claim("CL-E3-FC-HOVERONLY", "Flight controller peak, design hover-only sortie at 30 degC (no ram air)",
          calc="CALC-E3-MISSION", output="fc_peak_hoveronly_des_c", unit="degC", limit=("<=", 85.0),
          verifies=["R-THERMAL"], parts=["AVN-001"], how="IMU.T in the logs of the tethered and hover-only flights.")
kit.claim("CL-E3-ESC-PAD-IN-WASH", "ESC pad inside the contracted slipstream (radial margin)", calc="CALC-E3-MISSION",
          output="pad_r_margin_m", unit="m", limit=(">=", 0.0), parts=["FIN-007-UR", "FIN-007-UL", "FIN-007-LR",
                                                                        "FIN-007-LL"],
          how="Tuft or ribbon on the pad on the thrust stand at hover power: it streams aft and does not flap.")
kit.claim("CL-E3-HOVER-LOSS", "Motor loss per station in the design hover (5 m/s wind, pessimistic)",
          calc="CALC-E3-MISSION", output="hover_loss_motor_des_w", unit="W", parts=["PRP-001-UR"],
          how="T-E1-STAND: input power minus shaft power (thrust stand torque x rpm) at hover thrust.",
          note="E1 CR-E1-10 gives 20.7-22.8 W at the calm gate hover; this includes E2's 1.10 wind factor")
kit.claim("CL-E3-LIMITER-LOSS", "Motor loss per station at the 100 A limiter", calc="CALC-E3-MISSION",
          output="limiter_loss_motor_w", unit="W", parts=["PRP-001-UR"],
          how="T-E1-STAND at 24.8 A battery current.", note="E1 CR-E1-10: 79-86 W")
kit.claim("CL-E3-CEIL-MISSION", "Field-ambient ceiling, full mission, design case, ASA mounts", calc="CALC-E3-CEILING",
          output="mission_des__min_asa_c", unit="degC", limit=(">=", 30.0),
          verifies=["R-THERMAL"], parts=["PRP-001-UR", "PRP-002-UR", "PWR-001", "AVN-001"],
          how="Replace ASM-E3-RTH-DESIGN, ASM-E3-WAKE and ASM-E3-PACK with the T-E3-* and T-E2-IR results and re-run; "
              "the ceiling is then MODELLED on measured inputs.",
          note="limit 30 degC = upper end of params env.ambient_design_c [10, 30]")
kit.claim("CL-E3-CEIL-MISSION-PETG", "Field-ambient ceiling, full mission, design case, PETG mounts",
          calc="CALC-E3-CEILING", output="mission_des__min_petg_c", unit="degC", how="As CL-E3-CEIL-MISSION.")
kit.claim("CL-E3-CEIL-HOVERONLY", "Field-ambient ceiling, hover-only sortie to the 20 % line, design, ASA mounts",
          calc="CALC-E3-CEILING", output="hoveronly_des__min_asa_c", unit="degC", verifies=["R-THERMAL"],
          parts=["PRP-001-UR", "PRP-002-UR", "PWR-001", "AVN-001"],
          how="Tethered-hover test (H2): thermocouples on one motor base and one ESC, IMU.T, pack IR at landing.")
kit.claim("CL-E3-CEIL-PACK-LIFE", "Ambient at which the pack lands at 50 degC (design mission)", calc="CALC-E3-CEILING",
          output="mission_des__pack_life", unit="degC", parts=["PWR-001"],
          how="Pack IR at landing on the warmest test morning; the flight card start-temperature rule follows.")
kit.claim("CL-E3-DT-CONV", "Time-step convergence: largest peak change between dt 0.5 and 0.25 s", calc="CALC-E3-CHECKS",
          output="dt_conv_k", unit="K", limit=("<=", 0.2), how="Re-run this script; CALC-E3-CHECKS prints the three levels.")
kit.claim("CL-E3-STEADY-CHECK", "Steady hover rise minus the hand value loss x R_th", calc="CALC-E3-CHECKS",
          output="steady_err_k", unit="K", how="Hand: Q_m(T) x R_th from motor_point at the final winding temperature.")
kit.claim("CL-E3-PACK-VS-E2", "Adiabatic pack replication minus E2's CL-E2-PACK-T-END", calc="CALC-E3-CHECKS",
          output="pack_vs_e2_k", unit="K", how="Same inputs as CALC-E2-HEAT (hot case): the two must agree within 0.1 K.")
kit.claim("CL-E3-MOTOR-STEADY", "Motor steady temperature in continuous design hover at 30 degC", calc="CALC-E3-CHECKS",
          output="motor_steady_hover_des_c", unit="degC", limit=("<=", 93.0), parts=["PRP-001-UR", "FIN-003-UR"],
          how="T-E3-MOTOR-TAU run to steady state (10 min).")
kit.claim("CL-E3-SUN-PACK", "Pack rise from a 10 min sun soak at set-up, dark pod skin (upper bound)",
          calc="CALC-E3-SUN", output="pack_rise_dark_k", unit="K", parts=["PWR-001", "POD-001"],
          how="IR thermometer on the pod skin and the pack after 10 min of morning sun, dark vs white tape.")

kit.claim("CL-E3-SWEEP-DES", "Mission temperatures at 15/20/25/30 degC ambient, design case (rows: T_amb, motor, ESC, "
          "pack at landing, FC, pod air; degC)", calc="CALC-E3-SWEEP", output="rows_des", unit="degC",
          verifies=["R-THERMAL"], parts=["PRP-001-UR", "PRP-002-UR", "PWR-001", "AVN-001"],
          how="T-E3-MISSION at whatever ambient the test mornings give; compare with the row re-run at that ambient.")
kit.claim("CL-E3-SWEEP-NOM", "Mission temperatures at 15/20/25/30 degC ambient, nominal case", calc="CALC-E3-SWEEP",
          output="rows_nom", unit="degC", parts=["PRP-001-UR", "PRP-002-UR", "PWR-001", "AVN-001"],
          how="As CL-E3-SWEEP-DES.")
kit.claim("CL-E3-RISE-AMB-INDEP", "Change of the motor rise above ambient between 15 and 30 degC, design (scaling check)",
          calc="CALC-E3-SWEEP", output="motor_rise_spread_des_k", unit="K", limit=("<=", 2.0),
          how="Two GT-04 runs on mornings 10 K apart give the same rise within the IR accuracy.",
          note="small: the rise is nearly independent of ambient, so a stand reading scales to 30 degC by adding (30 - T_amb)")
kit.claim("CL-E3-GT04-ESC-RISE", "ESC case rise at the end of the GT-04 sequence, design case (pass line for H1)",
          calc="CALC-E3-GT04", output="esc_rise_des_k", unit="K", limit=("<=", 40.0),
          parts=["PRP-002-UR"], verifies=["R-THERMAL"],
          how="GT-04 (H1): IR on the ESC FET side within 10 s of stop; pass if the rise is <= this value (design "
              "inputs are then conservative); any reading scaled to 30 degC must be <= 70 degC.",
          note="limit 40 K = 85 degC MCU rating - 30 degC - 15 K for case-to-die and IR error")
kit.claim("CL-E3-GT04-MOTOR-RISE", "Motor can rise at the end of the GT-04 sequence, design case", calc="CALC-E3-GT04",
          output="motor_rise_des_k", unit="K", limit=("<=", 50.0), parts=["PRP-001-UR"],
          how="GT-04: thermocouple on the can during the run; pass if the rise is <= this value.",
          note="limit 50 K = H1's GT-04 line (80 degC at 30 degC)")
kit.claim("CL-E3-ESC-PAD-PETG", "ESC (and its pad) peak vs PETG HDT 68 - 10 K, design mission at 30 degC",
          calc="CALC-E3-MISSION", output="esc_peak_des_c", unit="degC", limit=("<=", 58.0),
          parts=["FIN-007-UR", "FIN-007-UL", "FIN-007-LR", "FIN-007-LL"],
          how="T-E3-ESC-PAD: thermocouple between the hook-and-loop and the pad face; pad < 58 degC from 30 degC.",
          note="conservative: pad taken at the ESC temperature (the hook-and-loop between them insulates). "
               "Fails: print the four pads in ASA with the motor mounts (CR-E3-01), no mass or cost change")
kit.claim("CL-E3-PACK-15-WARMED", "Pack at landing on a 15 degC morning, pack warmed to 20 degC before take-off, design",
          calc="CALC-E3-SWEEP", output="pack_end_15_warmed_des_c", unit="degC", limit=("<=", 50.0), parts=["PWR-001"],
          how="T-E2-MISSION-LOG on a cool morning.")

# ---------------------------------------------------------------- tests
kit.test("T-E3-MOTOR-TAU", "Motor thermal resistance and time constant on the thrust stand",
         verifies=["CL-E3-MOTOR-PEAK", "CL-E3-MOUNT-PETG", "CL-E3-MOUNT-ASA", "CL-E3-MOTOR-ABUSE", "CL-E3-MOTOR-STEADY",
                   "CL-E3-GT04-MOTOR-RISE", "CL-E3-BURST-MAX"],
         procedure="One station on the H1 stand with the real printed mount, 11x5.5MR, 14.8 V. K-type thermocouples on "
                   "the stator (through the base vent), between base and mount, and on the bell (IR). From ambient: hover "
                   "power (~100 W bus) for 10 min, log every 5 s; fit T = T_inf - (T_inf - T_0) e^(-t/tau): R_th = "
                   "(T_inf - T_amb) / loss, loss = P_in - torque x omega. Then 30 s at 24.8 A. Pass: R_th <= 1.5 K/W, "
                   "base < 58 degC at hover power from 30 degC (PETG) or < 83 degC (ASA).")
kit.test("T-E3-ESC-PAD", "ESC on a fin-pad mock-up in the slipstream",
         verifies=["CL-E3-ESC-PEAK", "CL-E3-ESC-ABUSE", "CL-E3-ESC-PAD-IN-WASH", "CL-E3-ESC-PAD-PETG",
                   "CL-E3-GT04-ESC-RISE"],
         procedure="Foam-board half-fin with a 22 mm tube LE behind the stand prop; ESC strapped on the pad at x 0.101 m, "
                   "0.072 m from the axis, FET side out; thermocouple under the heat-shrink on the FETs. Hover power 10 min, "
                   "then 30 s at the limiter. Tuft on the pad. Back-solve the wake factor: f = (h_meas / h_model)^2. "
                   "Pass: <= 70 degC steady at hover power from 30 degC (15 K below the MCU rating).")
kit.test("T-E3-MISSION", "Temperatures after the first full missions",
         verifies=["CL-E3-MOTOR-PEAK", "CL-E3-ESC-PEAK", "CL-E3-PACK-END", "CL-E3-FC-PEAK", "CL-E3-CEIL-MISSION"],
         procedure="Field ambient from the handheld anemometer/thermometer at take-off; IR on the four motor cans, ESCs "
                   "and the pack within 60 s of landing; IMU.T and BAT current from the log. Compare with the model re-run "
                   "at the measured ambient: within +-8 K, else update ASM-E3-RTH-DESIGN / ASM-E3-WAKE.")

if __name__ == "__main__":
    import json
    kit.write()
    m = kit.nodes["CALC-E3-MISSION"]["outputs"]
    c = kit.nodes["CALC-E3-CEILING"]["outputs"]
    ch = kit.nodes["CALC-E3-CHECKS"]["outputs"]
    s = kit.nodes["CALC-E3-SUN"]["outputs"]
    o = kit.nodes["CALC-E3-OPS"]["outputs"]
    sw = kit.nodes["CALC-E3-SWEEP"]["outputs"]
    g4 = kit.nodes["CALC-E3-GT04"]["outputs"]
    res = {"mission": m, "ceiling": c, "checks": ch, "sun": s, "ops": o, "sweep": sw, "gt04": g4}
    (HERE / "thermal_results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print("\nphase log (design, 30 degC):")
    for row in m["phase_log_des"]:
        print("  ", row)
    print("\nmission outputs:")
    for kk, vv in m.items():
        if kk != "phase_log_des":
            print(f"   {kk:32s} {vv:8.2f}")
    print("\nceilings (degC):")
    for kk, vv in c.items():
        print(f"   {kk:32s} {vv:8.1f}")
    print("\nchecks:", {kk: vv for kk, vv in ch.items() if kk != "peaks_dt_1_05_025"})
    print("   peaks dt 1/0.5/0.25:", ch["peaks_dt_1_05_025"])
    print("sun:", s)
    print("ops:", o)
    print("\nsweep (T_amb, motor, ESC, pack end, FC, pod air):")
    for tag in ("des", "nom"):
        for row in sw[f"rows_{tag}"]:
            print(f"   {tag} " + "  ".join(f"{v:6.1f}" for v in row))
    print("   ", {kk: vv for kk, vv in sw.items() if not kk.startswith("rows")})
    print("gt04:", g4)
