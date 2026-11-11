"""C5 landing / impact engineer: stance tip-over, landing wind and drift limits, foot drop test, parked-stance
rules and the crash energy path for the K09-L quad tailsitter (fin-tip feet, owner D5).

Run:  python -I redesign/team/C5/landing_calc.py
Writes claims.json beside this file and prints every case table used in LANDING.md.

Frame (README): x aft from the wing root LE, y right, z up in cruise. In the stance the nose points up and the
ground plane is x = chord + foot height. "Narrow axis" = tipping about a pad line parallel to y (the pads at
z = +/-z_pad), rotation about y (Iyy). "Wide axis" = tipping about a pad line parallel to z (pads at y = +/-y_fin),
rotation about z (Izz). +z is the pod side.

Inputs are node ids only: params.json (P:), A3's generated item list (P:a3.rollup.items), D5's foot claims (CL-D5-*),
C1/B1/A3 claims and the assumptions below. Every calculation is a pure function of its inputs.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../A3/rollup/mass_items.json",
                               "../../subsystems/landing/params.json", "../../subsystems/pod/params.json"])
P = "P:"

# ---------------------------------------------------------------- sources and assumptions
kit.source("SRC-C5-UN383", "UN Manual of Tests and Criteria, section 38.3, test T.4 Shock (lithium batteries)",
           "standard", url="https://unece.org/transport/dangerous-goods/rev8-files",
           where="38.3.4.4: small cells and batteries, half-sine 150 gn peak, 6 ms",
           note="every pack shipped as UN3480 must pass T.4; value not yet re-read against the current revision",
           status="UNVERIFIED")

kit.assumption("ASM-C5-TD-DRIFT", "Touchdown drift 0.3 m/s",
               "Horizontal ground speed at touchdown in QLAND / QLOITER with GPS position hold, any direction",
               basis="ArduPilot position hold on a 2-3 kg multirotor typically holds < 0.3 m/s in 5 m/s wind; "
                     "replace with the twin's landing logs (T-C5-DRIFT-LOG)", value=0.3, unit="m/s",
               status="UNVERIFIED")
kit.assumption("ASM-C5-PARK-SF", "Parked-stance factor 1.5",
               "Factor on the overturning moment and on the friction demand before a parked, disarmed aircraft is "
               "allowed to stand", basis="same 1.5 as the structural ultimate factor; the parked case has no "
               "pilot to save it", value=1.5, unit="-", status="PROPOSED")
kit.assumption("ASM-C5-GUST-FACTOR", "Gust factor 1.4 over the mean",
               "Peak gust / 10-min mean wind at 2 m height at RFS in the morning",
               basis="open-terrain gust factors 1.3-1.5 at 2 m; H3 measures it with the handheld anemometer "
                     "(R-WIND-MEASURE)", value=1.4, unit="-", status="UNVERIFIED")
kit.assumption("ASM-C5-CL-FLAT", "Lift coefficient lying flat 0.6",
               "Largest lift coefficient of the wing lying flat on the ground, pod up, any wind direction",
               basis="flat plate at 0 deg with a reflexed section, ground effect and a small nose-up rest angle; "
                     "0.6 is above any value expected for alpha < 5 deg", value=0.6, unit="-", status="UNVERIFIED")
kit.assumption("ASM-C5-PROP-HALF-DEPTH", "Prop blade half-depth 12 mm turned spanwise",
               "Half the z extent of an 11 in prop blade at the hub region when the blade is turned spanwise",
               basis="APC 11x5.5MR hub ~ 10 mm thick, blade chord ~ 25 mm at 5.5 in pitch; measure (H1)",
               value=0.012, unit="m", status="UNVERIFIED")
kit.assumption("ASM-C5-TUBE-CAP", "Tube-end cap 5 mm",
               "The motor mount / end cap stands 5 mm beyond the tube end", basis="A1 envelope note "
               "(transport.envelope_props_off_m: tube ends +/-0.21 plus ~5 mm mount caps)", value=0.005, unit="m",
               status="PROPOSED")
kit.assumption("ASM-C5-PACK-G-MAX", "Pack deceleration limit 100 g",
               "Largest pack deceleration accepted in the survivable crash, applied through foam over the full "
               "fore face (no point load)", basis="UN 38.3 T.4 shock 150 gn on every shipped pack, / 1.5",
               value=100.0, unit="-", status="UNVERIFIED", cites=["SRC-C5-UN383"])
kit.assumption("ASM-C5-NOSE-WALL", "Pod nose wall 2 mm", "Thickness of the pod nose skin ahead of the crush block",
               basis="foam board or printed shell (D2)", value=0.002, unit="m", status="PROPOSED")
kit.assumption("ASM-C5-MU-GRASS", "Pad friction on grass 0.5",
               "Friction coefficient of the neoprene pad on mown RFS grass (parked-stance slide check)",
               basis="C1-R2 value for grass; C1 moved ASM-C1-FRICTION to the mat value 0.7 (CR-C5-09), so the grass "
                     "case carries its own number; H1 spring-scale pull on grass", value=0.5, unit="-",
               status="UNVERIFIED")
kit.assumption("ASM-C5-DROP-GUARD", "Drop-test stroke guard 3 mm",
               "Stroke that must remain unused at the end of the design drop (scatter of the XPS plateau)",
               basis="10 % of the 32 mm stroke", value=0.003, unit="m", status="PROPOSED")


# ---------------------------------------------------------------- helpers (pure)
def _cg(items, drop=(), scale=None, shift=None, add=()):
    """Mass (kg) and CG (x, z) of the A3 item list after edits. items rows: id, subsystem, discipline, mass_g, x, y, z."""
    m = sx = sz = 0.0
    for r in items:
        if r[0] in drop or r[1] in drop:
            continue
        mg, x, z = r[3], r[4], r[6]
        if scale and r[0] in scale:
            mg = mg * scale[r[0]]
        if shift and r[0] in shift:
            x = x + shift[r[0]]
        m += mg
        sx += mg * x
        sz += mg * z
    for mg, x, z in add:
        m += mg
        sx += mg * x
        sz += mg * z
    return m / 1000.0, sx / m, sz / m


def _narrow(z_pad, x_cg, z_cg, ground):
    """Narrow-axis tip-over angles (deg) toward +z (pod side) and -z."""
    h = ground - x_cg
    return math.degrees(math.atan((z_pad - z_cg) / h)), math.degrees(math.atan((z_pad + z_cg) / h)), h


def _v_allow(arm, h, phi_deg, k2, g):
    """Largest horizontal CG speed toward a pad line that does not tip the aircraft over it, when the aircraft
    touches down already tilted phi toward that line (pivot sticks, plastic impact, sink ignored = conservative).
    arm = horizontal CG-to-pad distance upright, h = CG height, k2 = I_cg / m about the tipping axis."""
    phi = math.radians(phi_deg)
    a = arm * math.cos(phi) - h * math.sin(phi)
    if a <= 0:
        return 0.0
    b = arm * math.sin(phi) + h * math.cos(phi)
    R = math.hypot(arm, h)
    return math.sqrt(2 * g * (R - b) * (k2 + R * R)) / b


def _phi_for_v(arm, h, v, k2, g):
    """Tilt toward the pad line at which the drift allowance falls to v (bisection)."""
    lo, hi = 0.0, math.degrees(math.atan(arm / h))
    if _v_allow(arm, h, 0.0, k2, g) < v:
        return 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _v_allow(arm, h, mid, k2, g) >= v:
            lo = mid
        else:
            hi = mid
    return lo


# ---------------------------------------------------------------- 1. CG cases and static tip-over
kit.assumption("ASM-C5-PRE-D47", "Pre-D-47 bay, for the before / after comparison only",
               "Edits that put A3's D-47 item list back to the R4 bay: pack centroid at x_pack, trim kit POD-008 "
               "moved by dx_kit, pitot socket POD-006 by dx_nose. Value [x_pack m, dx_kit m, dx_nose m]",
               basis="D-47 (CR-A3-22, CR-A1-43): pack -0.001 -> -0.022, bay 21 mm forward, nose 15 mm forward. Used only "
                     "for CL-C5-D47-CG-RISE; every flying case uses A3's items as listed",
               value=[-0.001, 0.021, 0.015], unit="m", status="PROPOSED")

STANCE_IN = {"items": P + "a3.rollup.items", "c": P + "wing.chord_m", "foot": P + "cg.foot_height_m",
             "z_fin": P + "fins.half_height_m", "y_fin": P + "fins.y_m", "z_pad": "CL-D5-CONTACT-Z",
             "m_feet": "CL-D5-MASS-TOTAL", "pack_rng": "ASM-A1-PACK-CASES-G",
             "x_t": P + "cg.x_target_m", "x_rng": P + "cg.x_range_m",
             "z_rng": P + "cg.z_range_m", "lam": "ASM-C1-LAND-LIFT",
             "err": P + "requirements.landing_attitude_err_deg", "pre": "ASM-C5-PRE-D47",
             "st47": P + "pack_x_per_pack_m"}


def _pack_id(items):
    """Id of the flight pack row: the one power/energy row (A3 renamed PWR-E01 to PWR-001 at R5)."""
    ids = [r[0] for r in items if r[1] == "power" and r[2] == "energy"]
    if len(ids) != 1:
        raise ValueError("expected one power/energy row in the A3 items, found %r" % ids)
    return ids[0]


def _trim(items, feet, x_goal, pid, scale=1.0):
    """Slide the pack so the CG lands on x_goal. Returns (m, x, z, pack centroid x)."""
    pk_row = [r for r in items if r[0] == pid][0]
    m, x, z = _cg(items, drop=("landing",), add=feet, scale={pid: scale})
    dx = (x_goal - x) * m * 1000.0 / (pk_row[3] * scale)
    m, x, z = _cg(items, drop=("landing",), add=feet, scale={pid: scale}, shift={pid: dx})
    return m, x, z, pk_row[4] + dx


@kit.calc("CALC-C5-STANCE", title="CG cases and static tip-over on the fin-tip feet", inputs=STANCE_IN,
          units={"c": "m", "foot": "m", "z_fin": "m", "y_fin": "m", "z_pad": "m", "m_feet": "g", "pack_rng": "g",
                 "x_t": "m", "x_rng": "m", "z_rng": "m", "err": "deg", "pre": "m", "st47": "m"},
          equation="CG from A3 items (feet replaced by D5's mass at x = c + foot/2) ; flying cases: pack slid until "
                   "x_cg = D-62 target / forward / aft limit (P:cg.*), pack 546 / 550 / 590 g (D-64), and each pack at "
                   "its D-62 flight station (P:pack_x_per_pack_m, D2-R6 / D-64) ; h = c + foot - x_cg ; narrow(+z) = atan((z_pad - z_cg) / h), "
                   "narrow(-z) = atan((z_pad + z_cg) / h) ; wide = atan(y_fin / h) ; residual thrust T = lam W along "
                   "the body: tip at acos(lam z/R) - atan(h/z), R = hypot(z, h) ; lam_max(err) = R cos(err + "
                   "atan(h/z)) / z ; corner bound: x = forward limit, z = top of the z range ; D-47 rise = h(550 g "
                   "station) - h(pre-D-47 bay, ASM-C5-PRE-D47) ; +5 mm allowance: worst station case with h + 5 mm")
def stance(items, c, foot, z_fin, y_fin, z_pad, m_feet, pack_rng, x_t, x_rng, z_rng, lam, err, pre, st47):
    x_fwd, x_aft = x_rng
    ground = c + foot
    feet = [(m_feet / 4.0, c + foot / 2.0, s * z_pad) for s in (1, -1) for _ in (0, 1)]
    pid = _pack_id(items)
    pack = [r for r in items if r[0] == pid][0]
    hi, lo = max(pack_rng) / pack[3], min(pack_rng) / pack[3]
    ml, mh = round(min(pack_rng)), round(max(pack_rng))
    trims = {"B3 target, 550 g": (x_t, 1.0), "B3 target, %d g" % mh: (x_t, hi), "B3 target, %d g" % ml: (x_t, lo),
             "B3 fwd limit, %d g" % mh: (x_fwd, hi), "B3 fwd limit, %d g" % ml: (x_fwd, lo),
             "B3 aft limit, 550 g": (x_aft, 1.0)}
    cases = {"A3 items as listed": _cg(items) + (pack[4],),
             "pre-D-47 bay (pack -0.001), D5 feet":
                 _cg(items, drop=("landing",), add=feet,
                     shift={pid: pre[0] - pack[4], "POD-008": pre[1], "POD-006": pre[2]}) + (pre[0],)}
    for k, (xg, sc) in trims.items():
        cases[k] = _trim(items, feet, xg, pid, sc)
    for key in sorted(st47, key=float):
        mp, xs = float(key), st47[key]
        cases["D-62 station, %d g" % round(mp)] = _cg(items, drop=("landing",), add=feet, scale={pid: mp / pack[3]},
                                                      shift={pid: xs - pack[4]}) + (xs,)
    m0, x0, z0 = _cg(items, drop=("landing", pid), add=feet)
    cases["no pack (parked)"] = (m0, x0, z0, None)
    table = {}
    for k, (m, x, z, xp) in cases.items():
        a1p, a1n, h = _narrow(z_fin, x, z, ground)
        d5p, d5n, _ = _narrow(z_pad, x, z, ground)
        table[k] = {"m_kg": m, "x_m": x, "z_m": z, "h_m": h, "x_pack_m": xp, "a1_narrow_deg": min(a1p, a1n),
                    "d5_narrow_pos_deg": d5p, "d5_narrow_neg_deg": d5n,
                    "wide_deg": math.degrees(math.atan(y_fin / h))}
    flying = [k for k in table if k.startswith(("B3 ", "D-62 "))]
    worst = min(flying, key=lambda k: table[k]["d5_narrow_pos_deg"])
    st_cases = [k for k in table if k.startswith("D-62 ")]
    worst47 = min(st_cases, key=lambda k: table[k]["d5_narrow_pos_deg"])
    corner_h = ground - x_fwd
    corner = math.degrees(math.atan((z_pad - max(z_rng)) / corner_h))
    w47 = table[worst47]
    plus5 = math.degrees(math.atan((z_pad - w47["z_m"]) / (w47["h_m"] + 0.005)))
    r1 = table["B3 target, 550 g"]
    z_arm = z_pad - r1["z_m"]
    R = math.hypot(z_arm, r1["h_m"])
    psi = math.atan(r1["h_m"] / z_arm)
    tip_lam = math.degrees(math.acos(lam * z_arm / R) - psi)
    lam_max = R * math.cos(math.radians(err) + psi) / z_arm
    before = table["pre-D-47 bay (pack -0.001), D5 feet"]
    a3l = before
    post = table[sorted(st_cases, key=lambda k: table[k]["m_kg"])[1]]       # the nominal (middle) pack
    return {"cases": table, "a1_feet_r1_narrow_deg": table[worst]["a1_narrow_deg"],
            "a1_feet_r1_nozcg_deg": math.degrees(math.atan(z_fin / table[worst]["h_m"])),
            "d5_a3_layout_deg": a3l["d5_narrow_pos_deg"], "x_pack_target_m": r1["x_pack_m"],
            "x_pack_light_m": table["B3 target, %d g" % ml]["x_pack_m"],
            "x_pack_heavy_m": table["B3 target, %d g" % mh]["x_pack_m"],
            "d5_r1_narrow_deg": r1["d5_narrow_pos_deg"], "d5_r1_nozcg_deg": math.degrees(math.atan(z_pad / r1["h_m"])),
            "d5_worst_narrow_deg": table[worst]["d5_narrow_pos_deg"], "worst_case": worst,
            "d5_d47_worst_deg": table[worst47]["d5_narrow_pos_deg"], "d47_worst_case": worst47,
            "d47_cg_rise_m": post["h_m"] - before["h_m"],
            "d47_tip_change_deg": post["d5_narrow_pos_deg"] - before["d5_narrow_pos_deg"],
            "d5_corner_deg": corner, "d5_d47_plus5_deg": plus5, "wide_r1_deg": r1["wide_deg"],
            "z_pad_for_33_m": r1["z_m"] + r1["h_m"] * math.tan(math.radians(33.0)),
            "m_r1_kg": r1["m_kg"], "x_r1_m": r1["x_m"], "z_r1_m": r1["z_m"], "h_r1_m": r1["h_m"],
            "m_empty_kg": table["no pack (parked)"]["m_kg"], "z_empty_m": table["no pack (parked)"]["z_m"],
            "h_empty_m": table["no pack (parked)"]["h_m"],
            "tip_with_residual_thrust_deg": tip_lam, "lam_max_for_err": lam_max}


FEET = (["GER-00%d-%s" % (n, s) for n in (1, 2, 4) for s in ("UR", "UL", "LR", "LL")]
        + ["GER-003-UR", "GER-003-UL", "GER-008-LR", "GER-008-LL"])   # GER-003 upper cartridge, GER-008 lower
PADS = [p for p in FEET if p.startswith("GER-004")]

kit.claim("CL-C5-TIPOVER-A1-R1-ZCG", "Tip-over, unsplayed feet (pivot at the fin tip), worst flying CG",
          calc="CALC-C5-STANCE",
          output="a1_feet_r1_narrow_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"),
          note="reference for a first build without D5's splayed pads; do not fly it. The pivot is the 0.21 m fin tip "
               "and the CG sits above the chord plane, so the pod-side arm is 0.21 - z_cg",
          how="Tilting board, feet at the fin tips without splay (first build before D5's pads): angle toward the pod side.")
kit.claim("CL-C5-TIPOVER-A3-LAYOUT", "Tip-over, D5 pads, pre-D-47 bay (pack at -0.001)",
          calc="CALC-C5-STANCE", output="d5_a3_layout_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"),
          parts=PADS,
          note="reference case (A3-R5 before D-47): the CG is aft of B3's range (MASS-CG.md), so it is not a "
               "flying case; the trimmed and D-47 station cases are",
          how="T-C5-TILT-BOARD with the pack at A3's nominal station.")
kit.claim("CL-C5-TIPOVER-R1", "Tip-over, D5 splayed pads, B3 target CG, pod side", calc="CALC-C5-STANCE",
          output="d5_r1_narrow_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"),
          verifies=["R-TIPOVER"], parts=PADS,
          note="pack (550 g) slid until the CG sits on CL-B3-CG-TARGET (CR-B3-11)",
          how="T-C5-TILT-BOARD: built aircraft, pack in at its trimmed station, tipping toward the pod side about "
              "the upper pad edges.")
kit.claim("CL-C5-TIPOVER-WORST", "Tip-over, worst flying CG (D-62 range, pack 546-590 g)", calc="CALC-C5-STANCE",
          output="d5_worst_narrow_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"),
          verifies=["R-TIPOVER"], parts=PADS,
          how="T-C5-TILT-BOARD repeated with the pack slid to the B3 forward-limit mark (and with the heaviest pack).")
kit.claim("CL-C5-TIPOVER-D47", "Tip-over, pack at its D-62 flight station, worst of 546 / 551 / 590 g", calc="CALC-C5-STANCE",
          output="d5_d47_worst_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"),
          verifies=["R-TIPOVER"], parts=PADS,
          note="C5-R6: D-64 packs at their D-62 stations (P:pack_x_per_pack_m, D2-R6: 546 g -0.036, 550 g -0.034, 590 g -0.028) "
               "on A3-R6a's items; the id keeps D47 because others cite it. D-47 / CR-A3-22 raised the CG in the "
               "stance about 5 mm (CL-C5-D47-CG-RISE); the stations are the flight-card marks, not a trim to the B3 target",
          how="T-C5-TILT-BOARD with each weighed pack at its marked station.")
kit.claim("CL-C5-D47-CG-RISE", "CG rise in the stance, pre-D-47 bay to the D-62 551 g station", calc="CALC-C5-STANCE",
          output="d47_cg_rise_m", unit="m",
          note="pre-D-47 bay (pack -0.001) to the 550 g flight station with the bay edits: 5.0 mm at the D-47 station "
               "-0.022, 4.1 mm at the D-59 station -0.018 (C5-R5); CR-A3-22 quoted 5 mm",
          how="T-A3-CG-BALANCE before / after; h = chord + foot - x_cg.")
kit.claim("CL-C5-D47-TIP-CHANGE", "Tip-over change, pre-D-47 bay to the D-62 551 g station (pod side)",
          calc="CALC-C5-STANCE", output="d47_tip_change_deg", unit="deg", how="Geometry; T-C5-TILT-BOARD.")
kit.claim("CL-C5-TIPOVER-STATION-PLUS5", "Tip-over, worst D-62 station with the CG a further 5 mm higher in the stance",
          calc="CALC-C5-STANCE", output="d5_d47_plus5_deg", unit="deg",
          limit=(">=", P + "requirements.tipover_min_deg"), parts=PADS,
          note="allowance check for CR-A3-22 / CR-A1-46: a second 5 mm rise on top of the D-47 one (roll-up "
               "uncertainty, a heavier nose). The CG cannot move ahead of CL-B3-CG-FWD in flight, so "
               "CL-C5-TIPOVER-B3-CORNER stays the bound",
          how="T-C5-TILT-BOARD with the worst pack at its mark and ballast taped to the pod nose.")
kit.claim("CL-C5-TIPOVER-B3-CORNER", "Tip-over at the D-62 forward limit (0.0466) with the z_cg range top (0.025)", calc="CALC-C5-STANCE",
          output="d5_corner_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"), parts=PADS,
          note="C5-R6: x = forward end of P:cg.x_range_m (D-62, 0.0466) and z = top of P:cg.z_range_m (0.025) "
               "together; A3-R6a rolls up z +0.0185 m, so this corner is a bound, not a flying case. Same geometry as "
               "CL-A1-TIPOVER (30.98 deg)",
          how="Tilting board with the pack at the forward-limit mark and z ballast on the pod lid.")
kit.claim("CL-C5-PAD-Z-FOR-33", "Pad pivot z needed for 33 deg at R1 CG", calc="CALC-C5-STANCE",
          output="z_pad_for_33_m", unit="m",
          note="CR-A1-20's 33 deg target with the z offset needs this pivot (D5 has 0.218 m; each mm costs a mm of "
               "box height, 12 mm left). C5 retires the 33 deg target: the landing-heading rule does more (LANDING.md)",
          how="Geometry; compare with CL-D5-CONTACT-Z.")
kit.claim("CL-C5-TIPOVER-WIDE", "Tip-over, wide axis, B3 target CG", calc="CALC-C5-STANCE", output="wide_r1_deg",
          unit="deg", limit=(">=", P + "requirements.tipover_min_deg"), parts=PADS,
          how="T-C5-TILT-BOARD about a fin's pad pair.")
kit.claim("CL-C5-TIP-RESIDUAL-THRUST", "Tip-over with 2/3 W thrust still on", calc="CALC-C5-STANCE",
          output="tip_with_residual_thrust_deg", unit="deg", limit=(">=", P + "requirements.landing_attitude_err_deg"),
          note="thrust along the body axis acts at the pad offset and overturns; the attitude loop is assumed "
               "saturated or spooled down",
          how="T-C5-DRIFT-LOG: time from touchdown to motors at idle in the twin's logs; the lam_max claim bounds it.")
kit.claim("CL-C5-LAM-MAX", "Thrust fraction left at touchdown for a 10 deg error", calc="CALC-C5-STANCE",
          output="lam_max_for_err", unit="-", limit=(">=", "ASM-C1-LAND-LIFT"),
          note="above this fraction an uncorrected 10 deg tilt toward a pad line tips the aircraft",
          how="Twin and aircraft logs: thrust (throttle out) within 0.5 s after the land detector fires.")


# ---------------------------------------------------------------- 2. wind, drift and parked stance
WIND_IN = {"g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "b": P + "wing.span_m", "c": P + "wing.chord_m",
           "foot": P + "cg.foot_height_m", "fin_c": P + "fins.chord_m", "fin_hh": P + "fins.half_height_m",
           "y_fin": P + "fins.y_m", "z_pad": "CL-D5-CONTACT-Z", "cd90": "ASM-B1-CD90",
           "v_card": P + "requirements.wind_limit_ms", "v_gust": P + "requirements.gust_survive_ms",
           "err": P + "requirements.landing_attitude_err_deg", "v_td": "ASM-C5-TD-DRIFT",
           "m": "CL-C5-MASS-R1", "z_cg": "CL-C5-CG-Z-R1", "h": "CL-C5-CG-H-R1", "m_e": "CL-C5-MASS-EMPTY",
           "z_e": "CL-C5-CG-Z-EMPTY", "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ", "m_a3": "CL-A3-MASS-BASIC",
           "mu_pad": "ASM-D5-PAD-MU", "mu_grass": "ASM-C5-MU-GRASS", "sf": "ASM-C5-PARK-SF",
           "gf": "ASM-C5-GUST-FACTOR", "cl_flat": "ASM-C5-CL-FLAT"}


@kit.calc("CALC-C5-WIND", title="Landing lean, drift allowance and parked-stance wind limits", inputs=WIND_IN,
          units={"g": "m/s2", "rho": "kg/m3", "b": "m", "c": "m", "foot": "m", "fin_c": "m", "fin_hh": "m",
                 "y_fin": "m", "z_pad": "m", "v_card": "m/s", "v_gust": "m/s", "err": "deg", "v_td": "m/s",
                 "m": "kg", "z_cg": "m", "h": "m", "m_e": "kg", "z_e": "m", "Iyy": "kg m2", "Izz": "kg m2",
                 "m_a3": "kg"},
          equation="lean = atan(q S CD90 / (m g)), S = b c broadside or 4 fin_c fin_hh span-along-wind ; "
                   "v_allow(phi) = sqrt(2 g (R - b_phi)(k^2 + R^2)) / b_phi, b_phi = z sin phi + h cos phi ; "
                   "delta(v) = beta - phi(v_allow = v) ; beta_req = lean(5) + err + delta(v_td) ; "
                   "V_tip = sqrt(2 m g z_arm / (h_cp rho S CD90)), h_cp = c/2 + foot ; V_slide = sqrt(2 mu m g / (rho S CD90)) ; "
                   "V_park = min(V_tip, V_slide)/sqrt(SF) ; V_lift,flat = sqrt(2 m g / (rho S CL_flat))")
def wind(g, rho, b, c, foot, fin_c, fin_hh, y_fin, z_pad, cd90, v_card, v_gust, err, v_td, m, z_cg, h, m_e, z_e,
         Iyy, Izz, m_a3, mu_pad, mu_grass, sf, gf, cl_flat):
    S = b * c
    S_fin = 2 * fin_c * 2 * fin_hh
    W = m * g

    def lean(V, area, mass):
        return math.degrees(math.atan(0.5 * rho * V * V * area * cd90 / (mass * g)))
    k2y, k2z = Iyy / m_a3, Izz / m_a3
    z_arm = z_pad - z_cg
    beta_n = math.degrees(math.atan(z_arm / h))
    beta_w = math.degrees(math.atan(y_fin / h))
    lean_b5 = lean(v_card, S, m)
    lean_s5 = lean(v_card, S_fin, m)
    phi_n = _phi_for_v(z_arm, h, v_td, k2y, g)          # tilt at which drift allowance = v_td (narrow)
    phi_w = _phi_for_v(y_fin, h, v_td, k2z, g)
    delta_n = beta_n - phi_n
    delta_w = beta_w - phi_w
    # landing wind limits: lean(V) + err + delta <= beta
    def v_limit(area, beta, delta):
        room = math.radians(beta - err - delta)
        return 0.0 if room <= 0 else math.sqrt(math.tan(room) * W / (0.5 * rho * area * cd90))
    h_cp = c / 2 + foot
    v_tip_full = math.sqrt(2 * W * z_arm / (h_cp * rho * S * cd90))
    v_tip_empty = math.sqrt(2 * m_e * g * (z_pad - z_e) / (h_cp * rho * S * cd90))
    v_slide_pad_e = math.sqrt(2 * mu_pad * m_e * g / (rho * S * cd90))
    v_slide_grass_e = math.sqrt(2 * mu_grass * m_e * g / (rho * S * cd90))
    v_slide_grass_f = math.sqrt(2 * mu_grass * W / (rho * S * cd90))
    v_park_gust_mat = min(v_tip_empty, v_slide_pad_e) / math.sqrt(sf)
    v_park_gust_grass = min(v_tip_empty, v_slide_grass_e) / math.sqrt(sf)
    return {"S_m2": S, "S_fin_m2": S_fin, "beta_narrow_deg": beta_n, "beta_wide_deg": beta_w,
            "lean_broadside_5_deg": lean_b5, "lean_spanwise_5_deg": lean_s5,
            "lean_broadside_8_deg": lean(v_gust, S, m), "lean_spanwise_8_deg": lean(v_gust, S_fin, m),
            "v_allow_calm_ms": _v_allow(z_arm, h, err, k2y, g),
            "v_allow_lull_ms": _v_allow(z_arm, h, lean_b5 + err, k2y, g),
            "v_allow_spanwise_ms": _v_allow(y_fin, h, lean_s5 + err, k2z, g),
            "delta_narrow_deg": delta_n, "delta_wide_deg": delta_w,
            "beta_req_broadside_deg": lean_b5 + err + delta_n, "beta_req_spanwise_deg": err + delta_n,
            "v_land_broadside_ms": v_limit(S, beta_n, delta_n), "v_land_spanwise_ms": v_limit(S_fin, beta_w, delta_w),
            "slope_calm_deg": beta_n - err - delta_n,
            "v_tip_parked_full_ms": v_tip_full, "v_tip_parked_empty_ms": v_tip_empty,
            "v_slide_mat_empty_ms": v_slide_pad_e, "v_slide_grass_empty_ms": v_slide_grass_e,
            "v_slide_grass_full_ms": v_slide_grass_f,
            "v_park_gust_mat_ms": v_park_gust_mat, "v_park_gust_grass_ms": v_park_gust_grass,
            "v_park_mean_mat_ms": v_park_gust_mat / gf,
            "v_lift_flat_empty_ms": math.sqrt(2 * m_e * g / (rho * S * cl_flat))}


# scalar claims that carry CALC-C5-STANCE results into CALC-C5-WIND (inputs must be node ids)
kit.claim("CL-C5-MASS-R1", "Flying mass, R1 roll-up with D5 feet, pack trimmed to the B3 target", calc="CALC-C5-STANCE", output="m_r1_kg",
          unit="kg", how="T-A1-WEIGH.")
kit.claim("CL-C5-CG-Z-R1", "CG z above the chord plane, B3 target trim", calc="CALC-C5-STANCE", output="z_r1_m",
          unit="m", how="T-A3-CG-BALANCE in the z direction (aircraft flat, two scales under the fin tips).")
kit.claim("CL-C5-CG-H-R1", "CG height above the pads in the stance", calc="CALC-C5-STANCE", output="h_r1_m",
          unit="m", how="T-A3-CG-BALANCE x position; h = chord + foot - x_cg.")
kit.claim("CL-C5-PACK-X-B3", "Pack centroid station that puts the CG on the B3 target", calc="CALC-C5-STANCE",
          output="x_pack_target_m", unit="m",
          note="C5's own trim of A3's item list (550 g pack); A3 carries -0.001 m as nominal, A3-R3's roll-up needs "
               "-0.015 m for the target (CL-A3-PACK-X-REQ). Sets the room ahead of the pack for the crush block "
               "(CALC-C5-CRASH)",
          how="T-A3-CG-BALANCE: mark the pack station that balances on the target line.")
kit.claim("CL-C5-PACK-X-B3-LIGHT", "Pack station on the D-62 target, 546 g pack", calc="CALC-C5-STANCE",
          output="x_pack_light_m", unit="m", how="As CL-C5-PACK-X-B3 with the weighed pack.")
kit.claim("CL-C5-PACK-X-B3-HEAVY", "Pack station on the D-62 target, 590 g pack", calc="CALC-C5-STANCE",
          output="x_pack_heavy_m", unit="m", how="As CL-C5-PACK-X-B3 with the weighed pack.")
kit.claim("CL-C5-MASS-EMPTY", "Mass with the pack out", calc="CALC-C5-STANCE", output="m_empty_kg", unit="kg",
          how="Weigh without the pack.")
kit.claim("CL-C5-CG-Z-EMPTY", "CG z with the pack out", calc="CALC-C5-STANCE", output="z_empty_m", unit="m",
          how="T-A3-CG-BALANCE without the pack.")

kit.claim("CL-C5-LEAN-5-BROADSIDE", "Hover lean at 5 m/s, wind on the wing face", calc="CALC-C5-WIND",
          output="lean_broadside_5_deg", unit="deg",
          note="at the R1 flying mass (lighter than B1's 2.6 kg gate, so 2-3 deg more lean)",
          how="H2 logs: pitch in QLOITER at a measured 5 m/s.")
kit.claim("CL-C5-LEAN-5-SPANWISE", "Hover lean at 5 m/s, span along the wind", calc="CALC-C5-WIND",
          output="lean_spanwise_5_deg", unit="deg", how="H2 logs: roll in QLOITER with a wingtip into a measured 5 m/s.")
kit.claim("CL-C5-TIPOVER-REQ-BROADSIDE", "Tip-over needed, broadside landing, 5 m/s", calc="CALC-C5-WIND",
          output="beta_req_broadside_deg", unit="deg",
          note="no splay that fits the box reaches it (needs a pivot about 0.04 m further out): broadside landings are limited by "
               "CL-C5-V-LAND-BROADSIDE instead. Lean + 10 deg error + the angle the 0.3 m/s drift needs, all toward one pad line (lull case)",
          how="Compare the tilt-board angle with the logged lean, attitude error and touchdown speed.")
kit.claim("CL-C5-TIPOVER-REQ-SPANWISE", "Tip-over needed on the narrow axis, span-into-wind landing",
          calc="CALC-C5-WIND", output="beta_req_spanwise_deg", unit="deg", limit=("<=", "CL-C5-TIPOVER-R1"),
          verifies=["R-TIPOVER"], how="As above; the lean then acts on the wide axis.")
kit.claim("CL-C5-V-LAND-BROADSIDE", "Wind limit for a broadside fin-tip landing", calc="CALC-C5-WIND",
          output="v_land_broadside_ms", unit="m/s", limit=(">=", P + "requirements.wind_limit_ms"),
          how="Landing practice (H2) with the anemometer; count tip-overs.")
kit.claim("CL-C5-V-LAND-SPANWISE", "Wind limit for a span-into-wind landing", calc="CALC-C5-WIND",
          output="v_land_spanwise_ms", unit="m/s", limit=(">=", P + "requirements.gust_survive_ms"),
          verifies=["R-WIND"], how="Landing practice (H2) with a wingtip into the measured wind.")
kit.claim("CL-C5-DRIFT-ALLOW-CALM", "Touchdown drift allowed, calm, 10 deg error", calc="CALC-C5-WIND",
          output="v_allow_calm_ms", unit="m/s", limit=(">=", "ASM-C5-TD-DRIFT"),
          how="T-C5-DRIFT-LOG: touchdown ground speed from the EKF in 20 landings.")
kit.claim("CL-C5-DRIFT-ALLOW-LULL", "Touchdown drift allowed, 5 m/s lull, broadside", calc="CALC-C5-WIND",
          output="v_allow_lull_ms", unit="m/s",
          note="below the 0.3 m/s touchdown drift: the case behind the flight-card rule 'land span into wind'", how="As CL-C5-DRIFT-ALLOW-CALM.")
kit.claim("CL-C5-DRIFT-ALLOW-SPANWISE", "Touchdown drift allowed, 5 m/s, span into wind", calc="CALC-C5-WIND",
          output="v_allow_spanwise_ms", unit="m/s", limit=(">=", "ASM-C5-TD-DRIFT"), how="As CL-C5-DRIFT-ALLOW-CALM.")
kit.claim("CL-C5-SLOPE-CALM", "Ground slope allowed for a calm landing", calc="CALC-C5-WIND",
          output="slope_calm_deg", unit="deg", limit=(">=", 5.0),
          note="flight card: landing spot level within 5 deg", how="Phone inclinometer on the landing mat.")
kit.claim("CL-C5-V-TIP-PARKED-EMPTY", "Wind that tips the parked aircraft, pack out", calc="CALC-C5-WIND",
          output="v_tip_parked_empty_ms", unit="m/s", how="Fan or measured wind until a pad lifts, pack out.")
kit.claim("CL-C5-V-SLIDE-GRASS-EMPTY", "Wind that slides it on grass, pack out", calc="CALC-C5-WIND",
          output="v_slide_grass_empty_ms", unit="m/s", how="Spring-scale pull of the parked aircraft on RFS grass.")
kit.claim("CL-C5-V-PARK-GUST", "Largest gust to leave it standing (on the mat)", calc="CALC-C5-WIND",
          output="v_park_gust_mat_ms", unit="m/s", limit=(">=", P + "requirements.wind_limit_ms"),
          verifies=["R-WIND"],
          note="pack out governs; factor 1.5 on moment and friction. Below the 5 m/s card on grass: lay it flat",
          how="Handheld anemometer gust reading at the landing mat (H3 flight card).")
kit.claim("CL-C5-V-PARK-GUST-GRASS", "Largest gust to leave it standing on grass", calc="CALC-C5-WIND",
          output="v_park_gust_grass_ms", unit="m/s", how="As CL-C5-V-PARK-GUST, on grass.")
kit.claim("CL-C5-V-LIFT-FLAT", "Wind that lifts it lying flat, pack out", calc="CALC-C5-WIND",
          output="v_lift_flat_empty_ms", unit="m/s", limit=(">=", P + "requirements.gust_survive_ms"),
          how="Never observed in the field log; weight it with the pack bag if the card is exceeded.")


kit.test("T-C5-TILT-BOARD", "Tilt-board tip-over angles",
         verifies=["CL-C5-TIPOVER-R1", "CL-C5-TIPOVER-WORST", "CL-C5-TIPOVER-WIDE", "CL-C5-CG-Z-R1",
                   "CL-C5-CG-H-R1"],
         procedure="Built aircraft, props off, pack in (then pack slid to the forward stop, then pack out), on a "
                   "0.6 x 0.8 m plywood board faced with the landing-mat rubber, a 6 mm stop strip behind the pads "
                   "on the hinge side. Raise the far edge slowly with a phone inclinometer on the board; record the "
                   "angle when the far pads lift. Four directions (+z pod side, -z, +y, -y), 3 times each. Pass: "
                   "pod side >= 30 deg and within 1.5 deg of CL-C5-TIPOVER-R1 (else re-measure the CG z).")
kit.test("T-C5-DRIFT-LOG", "Touchdown drift and spool-down from logs",
         verifies=["CL-C5-DRIFT-ALLOW-CALM", "CL-C5-DRIFT-ALLOW-SPANWISE", "CL-C5-LAM-MAX",
                   "CL-C5-TIP-RESIDUAL-THRUST"],
         procedure="H2: 20 QLAND / QLOITER landings of the twin, then of the aircraft; from the dataflash log take "
                   "the EKF ground speed at first contact (accel spike) and the time from contact to all motors at "
                   "spin-min. Pass: 95th percentile ground speed <= 0.3 m/s; throttle out <= 0.71 hover within 0.5 s "
                   "of contact.")


# ---------------------------------------------------------------- 3. lying flat between flights
@kit.calc("CALC-C5-LAYFLAT", title="Ground contacts and prop clearance lying flat, pod up",
          inputs={"z_pad_out": P + "landing.pad.z_outer_m", "tube_len": P + "fins.tube.length_m",
                  "cap": "ASM-C5-TUBE-CAP", "z_st": P + "propulsion.stations.z_m",
                  "d_mot": P + "propulsion.motor_diameter_m", "D": P + "propulsion.prop_diameter_m",
                  "blade": "ASM-C5-PROP-HALF-DEPTH"},
          units={"z_pad_out": "m", "tube_len": "m", "cap": "m", "z_st": "m", "d_mot": "m", "D": "m", "blade": "m"},
          equation="ground plane = lowest of pad (z_pad_out), tube cap (L/2 + cap), motor can (z_st + d/2) ; "
                   "prop spanwise clearance = ground - (z_st + blade) ; prop blade-down clearance = ground - (z_st + D/2)")
def layflat(z_pad_out, tube_len, cap, z_st, d_mot, D, blade):
    contacts = {"pad": z_pad_out, "tube cap": tube_len / 2 + cap, "motor can": z_st + d_mot / 2}
    ground = max(contacts.values())
    return {"ground_z_m": ground, "contacts": contacts, "prop_spanwise_clear_m": ground - (z_st + blade),
            "prop_down_clear_m": ground - (z_st + D / 2)}


kit.claim("CL-C5-LAYFLAT-PROP-CLEAR", "Lower prop clearance lying flat, blades spanwise", calc="CALC-C5-LAYFLAT",
          output="prop_spanwise_clear_m", unit="m", limit=(">=", 0.005),
          how="Lay the built aircraft pod-up on the mat with both lower props turned spanwise; feeler under the blades.")
kit.claim("CL-C5-LAYFLAT-PROP-DOWN", "Lower prop blade pointing down, lying flat", calc="CALC-C5-LAYFLAT",
          output="prop_down_clear_m", unit="m",
          note="negative: a blade left pointing down carries the aircraft and breaks; turn the lower props spanwise first",
          how="Geometry.")


# ---------------------------------------------------------------- 4. foot drop test
DROP_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "v": P + "requirements.landing_sink_ms",
           "n_max": P + "requirements.landing_n_design", "s40": P + "requirements.foot_crush_stroke_min_m",
           "eta_c1": "ASM-C1-CRUSH-EFF", "lam": "ASM-C1-LAND-LIFT", "F_p": "CL-D5-F-PLATEAU", "F_pk": "CL-D5-F-PEAK",
           "s_av": "CL-D5-STROKE-AVAIL", "L": "CL-D5-CART-LEN", "eps_y": "ASM-D5-YIELD-STRAIN",
           "guard": "ASM-C5-DROP-GUARD", "z_cg": "CL-C5-CG-Z-R1", "z_pad": "CL-D5-CONTACT-Z", "y_fin": P + "fins.y_m",
           "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ", "m_a3": "CL-A3-MASS-BASIC", "set1": "CL-D5-SET-NORMAL",
           "mark": P + "landing.piston.replace_mark_m", "b": P + "wing.span_m", "foot": P + "cg.foot_height_m"}


@kit.calc("CALC-C5-DROP", title="Foot drop test definition and predicted results", inputs=DROP_IN,
          units={"m": "kg", "g": "m/s2", "v": "m/s", "s40": "m", "F_p": "N", "F_pk": "N", "s_av": "m", "L": "m",
                 "guard": "m", "z_cg": "m", "z_pad": "m", "y_fin": "m", "Iyy": "kg m2", "Izz": "kg m2", "m_a3": "kg",
                 "set1": "m", "mark": "m", "b": "m", "foot": "m"},
          equation="h = v^2 / (2 g) ; free drop (no rotor lift): 4 F_p (s - eps L/2) = m g h + m g s ; n = 4 F_pk / (m g) ; "
                   "E_cap = 4 F_p (s_av - eps L/2) ; E_40 = n_max m g eta s40 (the 40 mm / eta 0.5 foot) ; "
                   "one foot first: m_eff = 1 / (1/m + r_z^2/Iyy + r_y^2/Izz), F_p (s1 - eps L/2) = m_eff v^2 / 2 ; "
                   "normal landings per cartridge = mark / set ; wingtip strike roll = atan((foot - s) / (b/2 - y_fin))")
def drop(m, g, v, n_max, s40, eta_c1, lam, F_p, F_pk, s_av, L, eps_y, guard, z_cg, z_pad, y_fin, Iyy, Izz, m_a3, set1,
         mark, b, foot):
    W = m * g
    h = v * v / (2 * g)
    KE = 0.5 * m * v * v
    el = eps_y * L / 2
    s_free = (KE + 4 * F_p * el) / (4 * F_p - W)
    s_design = (KE + 4 * F_p * el) / (4 * F_p - (1 - lam) * W)
    E_cap = 4 * F_p * (s_av - el)
    E_40 = n_max * W * eta_c1 * s40
    k = m / m_a3                                           # scale A3's inertia to the test mass
    m_eff = 1.0 / (1.0 / m + (z_pad - z_cg) ** 2 / (Iyy * k) + y_fin ** 2 / (Izz * k))
    s_one = (0.5 * m_eff * v * v) / F_p + el
    return {"drop_h_m": h, "KE_J": KE, "stroke_free_m": s_free, "stroke_design_m": s_design,
            "stroke_margin_m": (s_av - guard) - s_free, "n_peak": 4 * F_pk / W, "E_cap_J": E_cap, "E_40_J": E_40,
            "m_eff_one_kg": m_eff, "stroke_one_foot_m": s_one, "rig_mass_kg": m / 4,
            "landings_per_cartridge": mark / set1 if set1 > 0 else float("inf"),
            "wingtip_roll_free_deg": math.degrees(math.atan(foot / (b / 2 - y_fin))),
            "wingtip_roll_one_foot_deg": math.degrees(math.atan((foot - s_one) / (b / 2 - y_fin))),
            "wingtip_roll_design_deg": math.degrees(math.atan((foot - s_design) / (b / 2 - y_fin)))}


kit.claim("CL-C5-DROP-HEIGHT", "Free-drop height for 1.5 m/s", calc="CALC-C5-DROP", output="drop_h_m", unit="m",
          how="Release height measured pad-to-floor before each drop.")
kit.claim("CL-C5-DROP-STROKE", "Stroke used in the free drop at the gate mass", calc="CALC-C5-DROP",
          output="stroke_free_m", unit="m", limit=("<=", "CL-D5-STROKE-AVAIL"),
          parts=FEET, note="symmetric hand energy balance (CG on the pad midline); CALC-C5-DROP-DYN supersedes it "
                           "for the real CG (about 19 mm toward the pod-side pair) and for tilted landings",
          how="T-C5-AIRCRAFT-DROP: flange-to-sleeve gap before and after; pass with >= 3 mm left.")
kit.claim("CL-C5-DROP-STROKE-MARGIN", "Stroke left after the free drop, beyond the 3 mm guard", calc="CALC-C5-DROP",
          output="stroke_margin_m", unit="m", limit=(">=", 0.0), parts=FEET, how="As CL-C5-DROP-STROKE.")
kit.claim("CL-C5-DROP-N", "Peak load factor in the drop", calc="CALC-C5-DROP", output="n_peak", unit="-",
          limit=("<=", P + "requirements.landing_n_design"), parts=FEET,
          how="T-C5-AIRCRAFT-DROP: accelerometer at the CG, 1 kHz, 100 Hz low-pass; peak <= 6.0.")
kit.claim("CL-C5-FOOT-ENERGY", "Foot energy capacity at full stroke (four feet)", calc="CALC-C5-DROP",
          output="E_cap_J", unit="J", limit=(">=", "CL-C5-FOOT-ENERGY-40"), parts=FEET,
          note="D5's 32 mm constant-force foot absorbs more than the 40 mm / eta 0.5 foot of the requirement text",
          how="T-D5-COUPON force-stroke record integrated over 32 mm, x 4.")
kit.claim("CL-C5-FOOT-ENERGY-40", "Energy of the 40 mm / eta 0.5 foot at n 6", calc="CALC-C5-DROP",
          output="E_40_J", unit="J", how="Requirement text, R-LANDING-IMPACT.")
kit.claim("CL-C5-DROP-ONE-FOOT", "Stroke when one foot lands first (10 deg pitch + roll)", calc="CALC-C5-DROP",
          output="stroke_one_foot_m", unit="m", limit=("<=", "CL-D5-STROKE-AVAIL"), parts=FEET,
          note="first foot only; the feet that land after the rotation stroke more (CALC-C5-DROP-DYN)",
          how="T-C5-AIRCRAFT-DROP corner drop: stroke of the first foot.")
kit.claim("CL-C5-WINGTIP-ROLL-CRUSHED", "Roll error that grounds the wingtip TE, first foot crushed",
          calc="CALC-C5-DROP", output="wingtip_roll_one_foot_deg", unit="deg",
          note="about 10.7 deg with the feet uncrushed; during a hard landing the first foot crushes and the wingtip "
               "TE corner touches at about 6 deg: protect the corner (CR-C5-04)",
          how="T-C5-AIRCRAFT-DROP roll and corner drops: witness tape on the wingtip TE corners.")
kit.claim("CL-C5-LANDINGS-PER-CARTRIDGE", "Normal 0.5 m/s landings before the replace mark", calc="CALC-C5-DROP",
          output="landings_per_cartridge", unit="-", limit=(">=", 5.0),
          note="FAILS at D5-R4: 1.28 mm permanent set per 0.5 m/s landing (CL-D5-SET-NORMAL) against the replace "
               "mark; D5 owns the fix (CR-D5-21: mark position or a no-set touchdown below CL-D5-V-NO-SET 0.32 m/s)",
          how="H2 records the flange gap after each landing for the first 10 flights.")


# ---------------------------------------------------------------- 4b. planar landing dynamics (pair first)
kit.assumption("ASM-C5-STROKE-PROP", "Proposed foot stroke 38 mm",
               "Flange-to-sleeve gap C5 asks D5 for (CR-C5-10)", basis="worst pad-pair-first landing in "
               "CALC-C5-DROP-DYN plus the 3 mm guard; the 77 mm cartridge has 42 mm of usable crush (0.55 x 77)",
               value=0.038, unit="m", status="PROPOSED")
kit.assumption("ASM-C5-FOOT-PROP", "Proposed foot height 48 mm beyond the TE",
               "cg.foot_height_m C5 asks A1 for (CR-C5-11)", basis="keeps the wing TE >= 10 mm off the ground at "
               "the full 38 mm stroke (C1 D-11 rule)", value=0.048, unit="m", status="PROPOSED")
kit.assumption("ASM-C5-F-PLATEAU-PROP", "Proposed mean cartridge plateau 37.5 N per foot (C5-R3)",
               "Mean of the upper and lower cartridge plateau forces C5 asks D5 for (CR-C5-10 revised)",
               basis="highest mean plateau that keeps the level free drop at n <= 6 with a pre-crushed cartridge "
                     "(4 x 37.5 / (2.6 x 9.807) = 5.88); needed because A3-R3's pitch inertia (0.0300 kg m2, was "
                     "0.0426) lets the second pad pair land harder", value=37.5, unit="N", status="PROPOSED")
kit.assumption("ASM-C5-PRECRUSH-PEAK", "Pre-crushed cartridge: initial peak = plateau",
               "Ratio of the initial crush peak to the plateau after a 2 mm press pre-crush of each cartridge",
               basis="pre-crushing closed-cell foam past its yield strain removes the initial peak (D5 models 1.10 "
                     "uncrushed); 2 mm of the 42 mm usable crush in the 77 mm cartridge is spent, 40 mm left >= 38. "
                     "T-D5-COUPON must show it", value=1.0, unit="-", status="UNVERIFIED")


def _foot_force(s, s_max, F_p, F_pk, s_y, s_av):
    """Crush force of one foot at stroke s (loading if s >= s_max, else elastic unloading). Linear ramp to the
    initial peak F_pk at s_y, plateau F_p, then bottoming (flange on the sleeve) with a stiff 50 F_p / mm spring."""
    def curve(x):
        if x <= s_y:
            return F_pk * x / s_y
        f = F_p
        if x > s_av:
            f += 50.0 * F_p * (x - s_av) / 0.001
        return f
    if s >= s_max:
        return curve(s), s
    k_el = F_pk / s_y
    return max(0.0, curve(s_max) - k_el * (s_max - s)), s_max


def _sim2d(m, I, arms, scales, h, v, tilt_deg, lam, g, F_p, F_pk, s_y, s_av, tip=None, dt=4e-5):
    """Rigid body in a vertical plane: CG height Y, angle th. Two contacts at body points (u = arm, w = -h), each
    two feet (one pad pair or one fin's pair) with plateau F_p x scale. Pads frictionless (cos 10 deg = 0.985
    ignored). Rotor lift lam W at the CG. Start: lowest pad touching, sink v. Returns max stroke per contact,
    peak load factor, lowest height of the optional body point tip = (u, w)."""
    th = math.radians(tilt_deg)

    def wy(u, w, Y, a):
        return Y + u * math.sin(a) + w * math.cos(a)
    Y = -min(wy(a, -h, 0.0, th) for a in arms)
    vY, om = -v, 0.0
    smax = [0.0 for _ in arms]
    peak_n, tip_min, t = 0.0, float("inf"), 0.0
    while t < 0.4:
        Fy, M = 0.0, 0.0
        for i, a in enumerate(arms):
            pen = -wy(a, -h, Y, th)
            if pen > 0:
                f1, smax[i] = _foot_force(pen, smax[i], F_p * scales[i], F_pk * scales[i], s_y, s_av)
                Fy += 2 * f1
                M += (a * math.cos(th) + h * math.sin(th)) * 2 * f1
        peak_n = max(peak_n, Fy / (m * g))
        if tip is not None:
            tip_min = min(tip_min, wy(tip[0], tip[1], Y, th))
        vY += (Fy / m - (1.0 - lam) * g) * dt
        om += (M / I) * dt
        Y += vY * dt
        th += om * dt
        t += dt
        if t > 0.05 and Fy == 0.0 and vY > 0:
            break
    return smax, peak_n, tip_min


DYN_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "v": P + "requirements.landing_sink_ms",
          "lam": "ASM-C1-LAND-LIFT", "F_p": "CL-D5-F-PLATEAU", "F_pk": "CL-D5-F-PEAK", "s_av": "CL-D5-STROKE-AVAIL",
          "L": "CL-D5-CART-LEN", "eps_y": "ASM-D5-YIELD-STRAIN", "guard": "ASM-C5-DROP-GUARD",
          "z_cg": "CL-C5-CG-Z-R1", "h": "CL-C5-CG-H-R1", "z_pad": "CL-D5-CONTACT-Z", "y_fin": P + "fins.y_m",
          "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ", "m_a3": "CL-A3-MASS-BASIC",
          "err": P + "requirements.landing_attitude_err_deg", "b": P + "wing.span_m", "foot": P + "cg.foot_height_m",
          "s_prop": "ASM-C5-STROKE-PROP", "foot_prop": "ASM-C5-FOOT-PROP", "s_hand": "CL-C5-DROP-STROKE",
          "mu_pad": "ASM-D5-PAD-MU", "mu_c1": "ASM-C1-FRICTION", "F_corner": "CL-C1-FOOT-CORNER",
          "F_prop": "ASM-C5-F-PLATEAU-PROP", "pk_prop": "ASM-C5-PRECRUSH-PEAK", "sigma": "ASM-D5-CART-PLATEAU",
          "sec_y": P + "landing.cartridge.section_y_m", "sf_ult": P + "requirements.safety_factor_ult",
          "F_up": "CL-D5-F-PLATEAU-UPPER", "F_lo": "CL-D5-F-PLATEAU-LOWER"}


@kit.calc("CALC-C5-DROP-DYN", title="Planar landing dynamics: level and pad pair first (pitch, roll), current and "
          "proposed foot; foot side load", inputs=DYN_IN,
          units={"m": "kg", "g": "m/s2", "v": "m/s", "F_p": "N", "F_pk": "N", "s_av": "m", "L": "m", "guard": "m",
                 "z_cg": "m", "h": "m", "z_pad": "m", "y_fin": "m", "Iyy": "kg m2", "Izz": "kg m2", "m_a3": "kg",
                 "err": "deg", "b": "m", "foot": "m", "s_prop": "m", "foot_prop": "m", "s_hand": "m", "F_corner": "N",
                 "F_prop": "N", "pk_prop": "-", "sigma": "Pa", "sec_y": "m", "sf_ult": "-",
                 "F_up": "N", "F_lo": "N"},
          equation="m Y'' = sum f_i - (1 - lam) m g ; I th'' = sum f_i x_i ; f_i = 2 x crusher(s_i), s_i = pad "
                   "penetration (ramp to F_pk at eps_y L/2, plateau F_p, no rebound, stiff stop at s_av) ; pitch: "
                   "Iyy, arms z_pad - z_cg and -(z_pad + z_cg) ; roll: Izz, arms +/- y_fin ; tilt scanned -err..+err "
                   "in 1 deg steps, worst kept ; design = sink v with lift lam W, test = free drop ; current = D5 "
                   "as delivered (stroke s_av, plateau F_up upper / F_lo lower, peak F_pk scaled the same) ; proposed = mean plateau F_prop, peak pk_prop F, bias upper "
                   "(pod-side) x b_u, lower x (2 - b_u), b_u in 1.000..1.100 (0.005 steps) minimising the worst pitch "
                   "stroke ; zero-level-moment bias 2 a_- / (a_+ + a_-) reported ; section z = F / (sigma sec_y) ; "
                   "ultimate = sf_ult x upper plateau ; explicit Euler 40 us, governing case re-run at 10 us and at "
                   "0.25 deg tilt steps ; side load = mu_pad F_corner")
def drop_dyn(m, g, v, lam, F_p, F_pk, s_av, L, eps_y, guard, z_cg, h, z_pad, y_fin, Iyy, Izz, m_a3, err, b, foot,
             s_prop, foot_prop, s_hand, mu_pad, mu_c1, F_corner, F_prop, pk_prop, sigma, sec_y, sf_ult, F_up, F_lo):
    k = m / m_a3
    s_y = eps_y * L / 2
    a_p, a_n = z_pad - z_cg, z_pad + z_cg
    pitch, roll = (a_p, -a_n), (y_fin, -y_fin)
    bias0 = (2 * a_n / (a_p + a_n), 2 * a_p / (a_p + a_n))
    tilts = [t for t in range(-int(err), int(err) + 1)]
    Fq, Fqk = F_prop, F_prop * pk_prop

    def worst(arms, I, sc, sav, lam_i, vv, Fa, Fb, tip=None, ts=tilts):
        best = (0.0, 0.0, 0.0, float("inf"))
        for t in ts:
            s, n, tp = _sim2d(m, I, arms, sc, h, vv, t, lam_i, g, Fa, Fb, s_y, sav, tip=tip)
            if max(s) > best[1]:
                best = (t, max(s), n, tp)
        return best
    # proposed bias: minimise the worst pad-pair-first pitch stroke at the design sink
    scan = []
    for i in range(21):
        bu = 1.0 + 0.005 * i
        scan.append((worst(pitch, Iyy * k, (bu, 2 - bu), s_prop, lam, v, Fq, Fqk)[1], bu))
    bu = min(scan)[1]
    bias = (bu, 2 - bu)
    res = {}
    sc_d5 = (F_up / F_p, F_lo / F_p)                       # D5's delivered per-type plateaus about its mean
    for tag, sav, sc, ft, Fa, Fb in (("current", s_av, sc_d5, foot, F_p, F_pk),
                                     ("proposed", s_prop, bias, foot_prop, Fq, Fqk)):
        lv = _sim2d(m, Iyy * k, pitch, sc, h, v, 0.0, lam, g, Fa, Fb, s_y, sav)
        lvf = _sim2d(m, Iyy * k, pitch, sc, h, v, 0.0, 0.0, g, Fa, Fb, s_y, sav)
        pw = worst(pitch, Iyy * k, sc, sav, lam, v, Fa, Fb)
        rw = worst(roll, Izz * k, (1.0, 1.0), sav, lam, v, Fa, Fb, tip=(b / 2, -h + ft))
        res[tag] = {"s_av_m": sav, "usable_m": sav - guard, "scales": list(sc),
                    "level_design_m": max(lv[0]), "level_design_pairs_m": list(lv[0]),
                    "level_free_m": max(lvf[0]), "level_free_n": lvf[1],
                    "pitch_worst_tilt_deg": pw[0], "pitch_design_m": pw[1], "pitch_n": pw[2],
                    "roll_worst_tilt_deg": rw[0], "roll_design_m": rw[1], "roll_n": rw[2],
                    "roll_wingtip_min_m": rw[3], "te_clear_full_stroke_m": ft - sav}
    p = res["proposed"]
    # tilted test drops (free drop, no lift): the height at which the worst pitch case uses the usable stroke
    lo, hi = 0.0, v * v / (2 * g)
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        s, _, _ = _sim2d(m, Iyy * k, pitch, bias, h, math.sqrt(2 * g * mid), p["pitch_worst_tilt_deg"], 0.0, g,
                         Fq, Fqk, s_y, s_prop)
        lo, hi = (mid, hi) if max(s) <= s_prop - guard else (lo, mid)
    # validation: symmetric CG, free level drop vs the hand energy balance (D5's foot); time-step and tilt-step checks
    sym = _sim2d(m, Iyy * k, (z_pad, -z_pad), (1.0, 1.0), h, v, 0.0, 0.0, g, F_p, F_pk, s_y, 1.0)
    fine = _sim2d(m, Iyy * k, pitch, bias, h, v, p["pitch_worst_tilt_deg"], lam, g, Fq, Fqk, s_y, s_prop, dt=1e-5)
    t0 = p["pitch_worst_tilt_deg"]
    fine_t = worst(pitch, Iyy * k, bias, s_prop, lam, v, Fq, Fqk, ts=[t0 + 0.25 * j for j in range(-4, 5)])
    c = res["current"]
    F_up, F_lo = Fq * bias[0], Fq * bias[1]
    return {"cases": res, "bias_upper": bias[0], "bias_lower": bias[1],
            "bias_zero_moment_upper": bias0[0], "bias_scan": [[b_, s_] for s_, b_ in scan],
            "plateau_upper_N": F_up, "plateau_lower_N": F_lo,
            "section_z_upper_m": F_up / (sigma * sec_y), "section_z_lower_m": F_lo / (sigma * sec_y),
            "ult_upper_N": sf_ult * F_up * pk_prop, "pitch_fine_tilt_m": fine_t[1],
            "cur_level_design_m": c["level_design_m"], "cur_pair_design_m": max(c["pitch_design_m"], c["roll_design_m"]),
            "cur_usable_m": c["usable_m"], "cur_pitch_design_m": c["pitch_design_m"],
            "cur_roll_design_m": c["roll_design_m"], "cur_level_free_n": c["level_free_n"],
            "cur_n_tilted": max(c["pitch_n"], c["roll_n"]), "cur_bias_upper": sc_d5[0],
            "prop_level_design_m": p["level_design_m"], "prop_pitch_design_m": max(p["pitch_design_m"], fine_t[1]),
            "prop_roll_design_m": p["roll_design_m"], "prop_level_free_m": p["level_free_m"],
            "prop_level_free_n": p["level_free_n"], "prop_n_tilted": max(p["pitch_n"], p["roll_n"]),
            "prop_usable_m": p["usable_m"], "prop_worst_tilt_deg": p["pitch_worst_tilt_deg"],
            "prop_te_clear_full_m": p["te_clear_full_stroke_m"], "prop_wingtip_min_m": p["roll_wingtip_min_m"],
            "test_tilt_drop_h_m": lo,
            "valid_sym_free_m": max(sym[0]), "valid_hand_free_m": s_hand,
            "dt_check_spread_m": abs(max(fine[0]) - p["pitch_design_m"]),
            "side_load_N": mu_pad * F_corner, "side_load_c1_N": mu_c1 * F_corner}


kit.claim("CL-C5-DYN-USABLE-CUR", "Usable stroke, D5-R4 foot (stroke - 3 mm guard)", calc="CALC-C5-DROP-DYN",
          output="cur_usable_m", unit="m", how="D5 CAD flange gap minus the guard.")
kit.claim("CL-C5-DYN-LEVEL-CUR", "Level 1.5 m/s landing stroke, D5-R4 foot as delivered (per-type plateaus)",
          calc="CALC-C5-DROP-DYN", output="cur_level_design_m", unit="m", limit=("<=", "CL-C5-DYN-USABLE-CUR"),
          parts=FEET,
          note="cross-check of D5's delivered cartridges (U 39.6 / L 35.4 N, bias 1.056) against C5's proposal; no "
               "verifies (CR-A2-21a): the requirement is carried by the -PROP claims, this shows D5 meets them",
          how="T-C5-AIRCRAFT-DROP level drop with lift offload: compare the upper and lower pair flange gaps.")
kit.claim("CL-C5-DYN-PAIR-CUR", "Pad pair first, worst tilt (pitch or roll), D5-R4 foot as delivered",
          calc="CALC-C5-DROP-DYN",
          output="cur_pair_design_m", unit="m", limit=("<=", "CL-C5-DYN-USABLE-CUR"), parts=FEET,
          note="cross-check of D5's delivered cartridges; no verifies (CR-A2-21a). The first pair stops only its "
               "share; the aircraft rotates onto the second pair, which lands harder",
          how="T-C5-AIRCRAFT-DROP tilted drops; the model is validated, not the full design case (no rotor lift).")
kit.claim("CL-C5-DYN-N-CUR", "Peak load factor, level free drop and tilted, D5-R4 foot as delivered",
          calc="CALC-C5-DROP-DYN", output="cur_n_tilted", unit="-",
          limit=("<=", P + "requirements.landing_n_design"), parts=FEET,
          note="tilted design landings; the level free drop is cur_level_free_n", how="As CL-C5-DYN-N-LEVEL.")
kit.claim("CL-C5-DYN-USABLE-PROP", "Usable stroke, proposed foot (38 - 3 mm guard)", calc="CALC-C5-DROP-DYN",
          output="prop_usable_m", unit="m", how="D5 CAD flange gap minus the guard (CR-C5-10).")
kit.claim("CL-C5-DROP-PAIR-PITCH", "Pad pair first in pitch, worst tilt, proposed foot", calc="CALC-C5-DROP-DYN",
          output="prop_pitch_design_m", unit="m", limit=("<=", "CL-C5-DYN-USABLE-PROP"), parts=FEET,
          verifies=["R-LANDING-IMPACT"], how="T-C5-AIRCRAFT-DROP tilted drops validate the model (stroke within 3 mm).")
kit.claim("CL-C5-DROP-PAIR-ROLL", "One fin's pair first in roll, worst tilt, proposed foot", calc="CALC-C5-DROP-DYN",
          output="prop_roll_design_m", unit="m", limit=("<=", "CL-C5-DYN-USABLE-PROP"), parts=FEET,
          verifies=["R-LANDING-IMPACT"], how="As CL-C5-DROP-PAIR-PITCH, roll drops.")
kit.claim("CL-C5-DYN-LEVEL-PROP", "Level 1.5 m/s landing stroke, proposed biased cartridges", calc="CALC-C5-DROP-DYN",
          output="prop_level_design_m", unit="m", limit=("<=", "CL-C5-DYN-USABLE-PROP"), parts=FEET,
          how="T-C5-AIRCRAFT-DROP level drop: both pair gaps equal within 2 mm.")
kit.claim("CL-C5-DYN-LEVEL-FREE-PROP", "Level free drop 0.115 m, proposed foot", calc="CALC-C5-DROP-DYN",
          output="prop_level_free_m", unit="m", limit=("<=", "CL-C5-DYN-USABLE-PROP"), parts=FEET,
          verifies=["R-LANDING-IMPACT"], how="T-C5-AIRCRAFT-DROP level drops (no lift: harder than design).")
kit.claim("CL-C5-DYN-N-LEVEL", "Peak load factor, level free drop, proposed foot", calc="CALC-C5-DROP-DYN",
          output="prop_level_free_n", unit="-", limit=("<=", P + "requirements.landing_n_design"), parts=FEET,
          verifies=["R-LANDING-IMPACT"], how="T-C5-AIRCRAFT-DROP: CG accelerometer, 100 Hz low-pass.")
kit.claim("CL-C5-DYN-N-TILTED", "Peak load factor, tilted landings, proposed foot", calc="CALC-C5-DROP-DYN",
          output="prop_n_tilted", unit="-", limit=("<=", P + "requirements.landing_n_design"), parts=FEET,
          how="As CL-C5-DYN-N-LEVEL, tilted drops.")
kit.claim("CL-C5-TE-CLEAR-PROP", "Wing TE above ground at full stroke, proposed foot", calc="CALC-C5-DROP-DYN",
          output="prop_te_clear_full_m", unit="m", limit=(">=", 0.010), parts=FEET,
          how="Crush one foot to its stop on the bench; feeler under the TE.")
kit.claim("CL-C5-WINGTIP-CLEAR-ROLL", "Lowest wingtip TE height, worst roll landing, proposed foot",
          calc="CALC-C5-DROP-DYN", output="prop_wingtip_min_m", unit="m",
          note="C5-R4 (A3-R5 I_zz 0.165): +2.4 mm, the corner just clears; it was -2.1 mm at R3. Keep the corner cap: when negative, in a roll-first landing at 6-10 deg the wingtip TE corner reaches the ground before the "
               "second fin lands; the 1 g corner cap of CR-C5-04 is the contact point",
          how="T-C5-AIRCRAFT-DROP roll drops: witness tape on the wingtip TE corner.")
kit.claim("CL-C5-TEST-TILT-H", "Free-drop height for the tilted test drops", calc="CALC-C5-DROP-DYN",
          output="test_tilt_drop_h_m", unit="m",
          note="without rotor lift a tilted 0.115 m drop over-strokes; tilted drops are run at this height and "
               "pass when each pair's stroke is within 3 mm of the model",
          how="Release height pad-to-floor.")
kit.claim("CL-C5-DYN-VALID", "Model check: symmetric free level drop vs the hand energy balance",
          calc="CALC-C5-DROP-DYN", output="valid_sym_free_m", unit="m", limit=("<=", "CL-C5-DROP-STROKE"),
          note="the sim spends 0.45 F_p eps L/2 less in the ramp than the hand calculation; it must not exceed it",
          how="Re-run; compare with CL-C5-DROP-STROKE.")
kit.claim("CL-C5-FOOT-SIDE-LOAD", "Foot side load at the pad, mat friction, one foot first", calc="CALC-C5-DROP-DYN",
          output="side_load_N", unit="N", limit=("<=", "CL-C5-FOOT-SIDE-C1"), parts=FEET,
          note="the landing mat and neoprene pad (mu 0.7) raise C1's L4/L5 side load (mu 0.5) by 40 %; C4's fin "
               "face stress scales with it (CR-C5-09)",
          how="T-D5-PAD-MU gives mu; C4's T-C4-FIN-PROOF at 1.5 x this load.")
kit.claim("CL-C5-FOOT-SIDE-C1", "Foot side load in C1 case L4 (C1 friction as carried)", calc="CALC-C5-DROP-DYN",
          output="side_load_c1_N", unit="N", how="C1 LOADS.md case L4.")
kit.claim("CL-C5-CART-BIAS-UPPER", "Cartridge bias, upper (pod-side) feet, proposed", calc="CALC-C5-DROP-DYN",
          output="bias_upper", unit="-",
          note="chosen to minimise the worst pitch pair-first stroke; lower feet get 2 - bias. The zero-level-moment "
               "bias is reported as bias_zero_moment_upper (1.085); D5-R4 delivers 1.056 against the 1.055 optimum",
          how="Coupon plateau ratio of the two marked cartridge types (T-D5-COUPON).")
kit.claim("CL-C5-CART-PLATEAU-UPPER", "Cartridge plateau force, upper feet UR/UL (pre-crushed)",
          calc="CALC-C5-DROP-DYN", output="plateau_upper_N", unit="N", parts=["GER-003-UR", "GER-003-UL"],
          how="T-D5-COUPON: mean force 5-35 mm of a pre-crushed cartridge, +/- 3 %.")
kit.claim("CL-C5-CART-PLATEAU-LOWER", "Cartridge plateau force, lower feet LR/LL (pre-crushed)",
          calc="CALC-C5-DROP-DYN", output="plateau_lower_N", unit="N", parts=["GER-008-LR", "GER-008-LL"],
          how="T-D5-COUPON: mean force 5-35 mm of a pre-crushed cartridge, +/- 3 %.")
kit.claim("CL-C5-CART-SECTION-UPPER", "Cartridge crush section z length, upper feet (y fixed by D5)",
          calc="CALC-C5-DROP-DYN", output="section_z_upper_m", unit="m", parts=["GER-003-UR", "GER-003-UL"],
          note="at D5's 172 kPa XPS plateau and its 11 mm section width; re-cut after the coupon",
          how="Calipers on the cut cartridge.")
kit.claim("CL-C5-CART-SECTION-LOWER", "Cartridge crush section z length, lower feet (y fixed by D5)",
          calc="CALC-C5-DROP-DYN", output="section_z_lower_m", unit="m", parts=["GER-008-LR", "GER-008-LL"],
          how="Calipers on the cut cartridge.")
kit.claim("CL-C5-CART-ULT-UPPER", "Ultimate axial load per upper foot (flange, shoe bond)", calc="CALC-C5-DROP-DYN",
          output="ult_upper_N", unit="N", parts=["GER-001-UR", "GER-001-UL", "GER-002-UR", "GER-002-UL"],
          how="D5 / C6: shoe-bond and flange proof at this load on a coupon fin tip.")


kit.test("T-C5-FOOT-RIG", "Single-foot drop rig", verifies=["CL-C5-DROP-STROKE", "CL-C5-DROP-N"],
         procedure="A foot (shoe bonded on a 2-layer foam-board offcut clamped vertical) under a 0.65 kg sled on two "
                   "guide rods; free drop 0.115 m onto plywood; phone or logger accelerometer on the sled. 3 drops, "
                   "new cartridge each. Pass: stroke <= 35 mm (model 26 mm), sled peak <= 6.0 g (100 Hz filter), no shoe-bond crack. "
                   "With the biased, pre-crushed cartridges (CR-C5-10, R3) use a 0.69 kg sled for an upper-foot "
                   "cartridge and 0.61 kg for a lower one (quarter gate mass x bias). Run before the aircraft drop; "
                   "cheap and repeatable.")
kit.test("T-C5-AIRCRAFT-DROP", "Aircraft drop (= T-C1-FOOT-DROP), proposed foot",
         verifies=["CL-C5-DYN-LEVEL-FREE-PROP", "CL-C5-DYN-N-LEVEL", "CL-C5-DYN-N-TILTED", "CL-C5-DROP-PAIR-PITCH",
                   "CL-C5-DROP-PAIR-ROLL", "CL-C5-DYN-LEVEL-PROP", "CL-C5-WINGTIP-CLEAR-ROLL"],
         procedure="Complete aircraft, props off, LiPo replaced by a sandbag of the weighed pack mass (ballast to "
                   "2.6 kg), FC on a small 2S pack logging IMU at >= 1 kHz. Quick-release hook over plywood. (1) Level, "
                   "0.115 m pad-to-floor, x2, new cartridges each: pass CG peak <= 6.0 g (100 Hz low-pass), every "
                   "stroke <= 35 mm, each pair's stroke within 3 mm of the model (the R3 bias leaves the upper pair "
                   "~3 mm deeper by design). (2) Pitch 4 deg both ways and roll 8 deg, at 0.098 m (CL-C5-TEST-TILT-H): "
                   "pass when each pair's stroke is "
                   "within 3 mm of the model re-run at the measured height and tilt, and the wing TE stays clear except "
                   "the wingtip corner cap. The model then carries the design case (1.5 m/s with 2/3 W lift). After "
                   "every drop: shoe bonds, fin tips, tube block and pod bond checked.")


# ---------------------------------------------------------------- 5. crash energy path: pack nose block
kit.assumption("ASM-C5-SPREADER-T", "Spreader plate 1.5 mm", "Printed PETG plate between the pack fore face and the "
               "crush block, so the block's whole section works", basis="D2 tray practice (1.5 mm stop wall)",
               value=0.0015, unit="m", status="PROPOSED")
CRASH_IN = {"v": "ASM-C1-CRASH-V",
            "g": P + "env.g_ms2", "n_pack": "ASM-C5-PACK-G-MAX", "sigma": "ASM-D5-XPS-PLATEAU",
            "eps_d": "ASM-D5-DENSIFY", "eps_y": "ASM-D5-YIELD-STRAIN", "pack": P + "battery.size_m",
            "bay_w": "CL-D2-BAY-W", "bay_h": "CL-D2-BAY-H", "blk_a": P + "nose_block_l_m",
            "stop": P + "fwd_stop_m", "st": P + "pack_x_per_pack_m",
            "x_pack": "CL-C5-PACK-X-B3", "x_light": "CL-C5-PACK-X-B3-LIGHT", "x_heavy": "CL-C5-PACK-X-B3-HEAVY",
            "t_sp": "ASM-C5-SPREADER-T", "box": P + "requirements.box_external_m",
            "bwall": "ASM-A1-WALL", "env": P + "transport.envelope_props_off_m",
            "x_le": P + "pod.x_le_m", "t_nose": P + "fins.board_t_m", "blk_min": "ASM-A3-NOSE-STACK"}
PACKS = ("546", "551", "590")      # D-64: listing - 5 g, listing, acceptance line; stations from the D2 table in order


@kit.calc("CALC-C5-CRASH", title="Crush block ahead of the pack (5 m/s nose-in), D-62 bay (nose -0.140 m), D-64 packs",
          inputs=CRASH_IN,
          units={"v": "m/s", "g": "m/s2", "sigma": "Pa", "pack": "m", "bay_w": "m",
                 "bay_h": "m", "blk_a": "m", "stop": "m", "st": "m", "x_pack": "m", "x_light": "m", "x_heavy": "m",
                 "t_sp": "m", "box": "m", "bwall": "m", "env": "m", "x_le": "m", "t_nose": "m", "blk_min": "m"},
          equation="per weighed pack mass m (546 / 551 / 590 g, D-64) at its D-62 station x_p (flight-card mark) and "
                   "at the C5 trim to the D-62 target: F = min(n_pack m g, sigma A_bay) ; KE = m v^2 / 2 ; eff = eps_d - "
                   "eps_y / 2 ; nose wall inside face x_n = x_le + t_nose ; block A L_A = nose_block_l_m ; forward stop "
                   "(t_stop, h_stop, w = fwd_stop_m) aft face x_s = x_n + L_A + t_stop ; block B fills x_s .. pack fore face "
                   "behind a t_sp spreader ; capacities add: gap_B needed = t_sp + max(0, KE - F_A eff L_A) / (F eff), "
                   "F_A = min(F, sigma A_stop) ; full-section stop A_stop = A_bay ; D2's stop as drawn A_stop = h_stop w ; "
                   "margin = (x_p - L_pack/2 - x_s) - gap_B needed ; most forward station x_fwd_max = x_p - margin ; "
                   "block A (1 mm epoxy bond since D-47) gets no crush credit ; crush-stack station (A3/A1 nose stack blk_min from the pod LE) x_stack = x_le + blk_min + L_pack/2, stack margin = "
                   "x_stack - x_fwd_max ; extension = max(0, -worst margin) ; box x slack = box_x - 2 wall - "
                   "(envelope_x + extension)")
def crash(v, g, n_pack, sigma, eps_d, eps_y, pack, bay_w, bay_h, blk_a, stop, st, x_pack, x_light,
          x_heavy, t_sp, box, bwall, env, x_le, t_nose, blk_min):
    A_bay = bay_w * bay_h
    face = pack[1] * pack[2]
    eff = eps_d - eps_y / 2
    x_n = x_le + t_nose
    t_stop, h_stop, w_stop = stop
    L_A = blk_a
    stop_aft = x_n + L_A + t_stop
    x_stack = x_le + blk_min + pack[0] / 2                  # A3/A1 nose stack is counted from the pod LE
    trim = {PACKS[0]: x_light, PACKS[1]: x_pack, PACKS[2]: x_heavy}
    keys = sorted(st, key=float)
    if len(keys) != 3 or abs(float(keys[0]) - 546) > 1 or abs(float(keys[2]) - 590) > 1:
        raise ValueError("pack_x_per_pack_m is not the D-64 546 / 550 / 590 g table: %r" % st)
    st = dict(zip(PACKS, (st[k] for k in keys)))           # the 551 g listing flies at the 550 g station
    rows = {}
    for tag in PACKS:
        mp, xs, xt = float(tag) / 1000.0, st[tag], trim[tag]
        F = min(n_pack * mp * g, sigma * A_bay)
        KE = 0.5 * mp * v * v
        A = F / sigma
        sp = t_sp if A > face else 0.0

        def gap_need(A_stop):
            # since D-47 'block A' is a 1 mm epoxy bond line, not XPS: it absorbs nothing (C5-R6; R5 credited it)
            F_A = min(F, sigma * A_stop)
            return sp + max(0.0, KE - F_A * eff * 0.0 * L_A) / (F * eff)
        g_full, g_c3 = gap_need(A_bay), gap_need(h_stop * w_stop)
        gap = (xs - pack[0] / 2) - stop_aft
        gap_t = (xt - pack[0] / 2) - stop_aft
        x_fwd_max = xs - (gap - g_full)
        rows[tag] = {"m_kg": mp, "x_pack_m": xs, "x_pack_trim_m": xt, "F_N": F, "n": F / (mp * g), "stroke_m": KE / F,
                     "L_m": KE / F / eff, "spreader": A > face, "gap_avail_m": gap, "gap_avail_trim_m": gap_t,
                     "gap_need_full_m": g_full, "gap_need_c3_m": g_c3,
                     "room_avail_m": (xs - pack[0] / 2) - x_n, "room_needed_m": L_A + t_stop + g_full,
                     "margin_full_m": gap - g_full, "margin_c3_m": gap - g_c3, "margin_trim_m": gap_t - g_full,
                     "x_fwd_max_m": x_fwd_max, "block_fill_m": gap - t_sp, "stack_margin_m": x_stack - x_fwd_max}
    nom = rows[PACKS[1]]
    worst = min(rows.values(), key=lambda r: r["margin_full_m"])
    worst_c3 = min(rows.values(), key=lambda r: r["margin_c3_m"])
    worst_t = min(rows.values(), key=lambda r: r["margin_trim_m"])
    ext = max(0.0, -worst["margin_full_m"])
    out = {"A_bay_m2": A_bay, "A_pack_face_m2": face, "packs": rows, "x_nose_inner_m": x_n, "x_stop_aft_m": stop_aft,
           "x_stack_m": x_stack, "stack_margin_worst_m": min(r["stack_margin_m"] for r in rows.values()),
           "L_A_m": L_A, "room_needed_nom_m": nom["room_needed_m"], "room_avail_m": nom["room_avail_m"],
           "room_margin_worst_m": worst["margin_full_m"], "room_margin_c3_stop_m": worst_c3["margin_c3_m"],
           "room_margin_trim_worst_m": worst_t["margin_trim_m"],
           "gap_B_nom_m": nom["gap_avail_m"], "block_L_nom_m": nom["L_m"], "n_pack_nom": nom["n"],
           "n_pack_max": max(r["n"] for r in rows.values()),
           "room_ideal_m": 0.5 * v * v / (n_pack * g) / eff,
           "nose_ext_m": ext, "box_x_slack_m": (box[1] - 2 * bwall) - (env[1] + ext)}
    for tag in PACKS:
        out["margin_%s_m" % tag] = rows[tag]["margin_full_m"]
        out["block_L_%s_m" % tag] = rows[tag]["L_m"]
        out["x_fwd_max_%s_m" % tag] = rows[tag]["x_fwd_max_m"]
        out["block_fill_%s_m" % tag] = rows[tag]["block_fill_m"]
    return out


kit.claim("CL-C5-PACK-ROOM-AVAIL", "Room ahead of the 551 g pack at its D-62 station (nose -0.140)",
          calc="CALC-C5-CRASH", output="room_avail_m", unit="m", parts=["POD-001", "POD-008"],
          note="nose wall inside face (x_le + 4.8 mm foam board) to the pack fore face at -0.034 - 0.0675 (D-62, "
               "135 mm pack); holds the 1 mm bond line, the 3 mm forward stop and block B behind it",
          how="Built pod, pack at its marked station: rule from the nose wall inside face to the pack fore face.")
kit.claim("CL-C5-PACK-NOSE-ROOM", "Room the crush blocks need, weighed 551 g pack", calc="CALC-C5-CRASH",
          output="room_needed_nom_m", unit="m", limit=("<=", "CL-C5-PACK-ROOM-AVAIL"), verifies=["R-PACK-RETENTION"],
          parts=["POD-008"],
          note="XPS F-250 over the full bay section; block A ahead of the stop is only a 1 mm bond line, so block B "
               "(behind a 1.5 mm spreader) does the work; the n_pack limit or the section sets the force",
          how="Crush a block coupon (T-D5-COUPON method) to get the force; weigh the pack (E2).")
kit.claim("CL-C5-PACK-ROOM-MARGIN-WORST", "Block B gap margin, worst D-64 pack at its D-62 station", calc="CALC-C5-CRASH",
          output="room_margin_worst_m", unit="m", limit=(">=", 0.0), verifies=["R-PACK-RETENTION"],
          parts=["POD-008"],
          note="D-62 flight-card marks (A1 frame estimate): 546 g at -0.036, 551 g at -0.034, 590 g at -0.028",
          how="As CL-C5-PACK-NOSE-ROOM with the weighed pack at its marked station.")
for _m, _x in (("546", "-0.036"), ("551", "-0.034"), ("590", "-0.028")):
    kit.claim("CL-C5-PACK-ROOM-MARGIN-%s" % _m, "Block B gap margin, %s g pack at its D-62 station %s" % (_m, _x),
              calc="CALC-C5-CRASH", output="margin_%s_m" % _m, unit="m", limit=(">=", 0.0), parts=["POD-008"],
              how="As above.")
kit.claim("CL-C5-PACK-ROOM-MARGIN-TRIM", "Block B gap margin, worst pack trimmed to the D-62 target", calc="CALC-C5-CRASH",
          output="room_margin_trim_worst_m", unit="m", parts=["POD-008"],
          note="cross-check: the pack slid until the CG is on P:cg.x_target_m in A3-R6a's items (D-61 stack shift "
               "not in the items), instead of its D-62 mark",
          how="As above with the pack at its balanced station.")
kit.claim("CL-C5-PACK-ROOM-C3-STOP", "Block B gap margin, worst pack, D2-R5 forward stop as drawn (25 mm tall)",
          calc="CALC-C5-CRASH", output="room_margin_c3_stop_m", unit="m", parts=["POD-002"],
          note="D2-R5 stop 3 x 25 x 54 mm (P:fwd_stop_m); block A is 1 mm, so the stop section hardly matters "
               "(CR-C5-13 withdrawn by C5; C3/D2 close it)",
          how="Geometry of the printed stop (D2 CAD).")
kit.claim("CL-C5-PACK-STACK-MARGIN", "Crush-stack station minus the most forward station that keeps block B, worst pack",
          calc="CALC-C5-CRASH", output="stack_margin_worst_m", unit="m", limit=(">=", 0.0),
          verifies=["R-PACK-RETENTION"], parts=["POD-008"],
          note="the D-62 bay's most forward pack centroid sits on the 34.6 mm nose stack (ASM-A3-NOSE-STACK: bond line, "
               "stop, 24.3 mm block, spreader), about -0.0379 for the 135 mm pack. Negative means a block cut to the "
               "24.3 mm minimum is too short for that pack: its flight-card station must stay aft of "
               "CL-C5-PACK-X-FWD-MAX-<m> (rule S9)",
          how="H3 flight card; rule the pack fore face to the forward stop on the built pod.")
kit.claim("CL-C5-NOSE-EXT", "Further pod nose extension needed beyond D-62 (-0.140 m)", calc="CALC-C5-CRASH",
          output="nose_ext_m", unit="m",
          note="zero when every pack at its D-62 mark keeps block B", how="D2 geometry.")
kit.claim("CL-C5-PACK-CRASH-G", "Largest pack deceleration in its block, 5 m/s nose-in", calc="CALC-C5-CRASH",
          output="n_pack_max", unit="-", limit=("<=", "ASM-C5-PACK-G-MAX"),
          how="Block coupon crush force x section; pack mass weighed (E2).")
kit.claim("CL-C5-BLOCK-L", "Crush block B length (F-250, weighed 551 g pack)", calc="CALC-C5-CRASH",
          output="block_L_nom_m", unit="m", parts=["POD-008"],
          note="D2 reads this in pod_claims.py; D-64 nominal pack 551 g", how="Cut length; rule.")
for _m in PACKS:
    if _m != "551":
        kit.claim("CL-C5-BLOCK-L-%s" % _m, "Crush block B length, %s g pack" % _m, calc="CALC-C5-CRASH",
                  output="block_L_%s_m" % _m, unit="m", parts=["POD-008"], how="Cut length; rule.")
    kit.claim("CL-C5-PACK-X-FWD-MAX-%s" % _m, "Most forward pack centroid station that keeps block B, %s g pack" % _m,
              calc="CALC-C5-CRASH", output="x_fwd_max_%s_m" % _m, unit="m", parts=["POD-008"],
              note="flight-card rule S9 (CR-C5-06, CR-C5-14d): the pack never sits forward of this station; the D-62 "
                   "mark is aft of it by the PACK-ROOM-MARGIN. Includes any fore-aft play of the pack in the bay",
              how="H3 flight card; rule the pack fore face to the forward stop on the built pod.")
    kit.claim("CL-C5-BLOCK-FILL-%s" % _m, "Block B cut length that fills the stop-to-spreader gap, %s g pack at its "
              "D-62 station" % _m, calc="CALC-C5-CRASH", output="block_fill_%s_m" % _m, unit="m", parts=["POD-008"],
              limit=(">=", "CL-C5-BLOCK-L" + ("" if _m == "551" else "-" + _m)),
              note="CR-C5-14c: cut block B to this so the pack has no forward play; it must be at least the block "
                   "length the pack needs",
              how="Cut length; rule; pack seated with no fore-aft play.")
kit.claim("CL-C5-BOX-X-SLACK-NOSE", "Box length slack with the R5 nose", calc="CALC-C5-CRASH",
          output="box_x_slack_m", unit="m", limit=(">=", 0.0), verifies=["R-TRANSPORT"],
          note="the D-62 envelope (0.508 m) holds the 10 mm nose extension and the 48 mm feet",
          how="D7: close the box on the built aircraft.")


if __name__ == "__main__":
    kit.write()
    st = kit.nodes["CALC-C5-STANCE"]["outputs"]
    print("\nCG and tip-over cases (deg):")
    print(f"  {'case':<30} {'m kg':>6} {'x m':>7} {'z m':>7} {'h m':>6} {'A1 feet':>8} {'D5 +z':>6} {'D5 -z':>6} {'wide':>6}")
    for k, r in st["cases"].items():
        print(f"  {k:<30} {r['m_kg']:6.3f} {r['x_m']:7.4f} {r['z_m']:7.4f} {r['h_m']:6.3f} {r['a1_narrow_deg']:8.1f}"
              f" {r['d5_narrow_pos_deg']:6.1f} {r['d5_narrow_neg_deg']:6.1f} {r['wide_deg']:6.1f}")
    for name in ("CALC-C5-STANCE", "CALC-C5-WIND", "CALC-C5-LAYFLAT", "CALC-C5-DROP", "CALC-C5-DROP-DYN", "CALC-C5-CRASH"):
        out = kit.nodes[name]["outputs"]
        print(f"\n{name}:")
        for k, v in out.items():
            if k == "cases":
                continue
            print(f"  {k:<30} {v:.4g}" if isinstance(v, float) else f"  {k:<30} {v}")
