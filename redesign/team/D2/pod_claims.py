"""D2 pod designer (revision D2-R4, params A1-R3): claims other roles build on (pack bay and stations, crush-block
geometry for C5, pack and pod retention, carry point, recess for D1, pitot boom, antenna and GPS clearances, pod mass).

Run:  python -I redesign/team/D2/pod_data.py   (CAD masses -> interfaces.json)
      python -I redesign/team/D2/pod_claims.py  then  python -I redesign/proofs/build_graph.py
Pod-only design numbers come from subsystems/pod/params.json and the CAD roll-up (team/D2/pod_data.py); they enter
the graph as ASM-D2-* assumptions written when this script runs, so the calculations stay pure functions of node
ids. The geometry formulas are the same as subsystems/pod/fusion/pod.py#layout() (pod_selfcheck.py compares them).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(REDESIGN / "proofs"))
sys.path.insert(0, str(REDESIGN / "fusion"))
sys.path.insert(0, str(HERE))
import proofkit as pk  # noqa: E402
import k09kit as k9    # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
POD = REDESIGN / "subsystems" / "pod"
_L = json.loads((POD / "params.json").read_text(encoding="utf-8"))
_lv = lambda k: _L[k]["value"]
_IF = json.loads((POD / "interfaces.json").read_text(encoding="utf-8"))
_MASSES = {p["id"]: p["mass_g"] for p in _IF["parts"]}
_PP = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))
SRC_POD = ["SRC-K09-CARD"]


def _cad_readouts():
    import pod_data as pdm
    _ctx, _P, _Lc, G, _src = pdm.build_pod()
    return [round(v, 7) for v in (G["overhang_clr"], G["ant_a_pack_clr"], G["ant_b_pack_clr"], min(G["gps_clr"].values()),
                                  G["ch_h"], G["cross_gap"], G["cross_h"], G["tray_front_area"])]


_GEO = _cad_readouts()

# ---------------------------------------------------------------- assumptions (pod-local numbers, D2 choices and adopted requests)
kit.assumption("ASM-D2-POD-WIDTH", "Pod outside width", "Pod outside width that holds the 52 mm bay and two 37.7 mm side channels",
               basis="params.json pod.size_m[1] (D-25 adopted CR-D2-01)", value=_PP["pod"]["size_m"]["value"][1], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-BAY-W", "Pack bay width between the guides", "Inside width of the bay", basis="E2 CR-E2-02 minimum, D2 uses it exactly",
               value=_lv("bay_min_m")[1], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-FLOOR-STACK", "Tray floor + EVA pad under the pack", "Height from the foam-board floor top to the pack underside",
               basis="subsystems/pod/params.json tray_floor_t_m + pad_t_m (R3: 2.5 mm pads lift the pack over the wing surface aft of the recess)",
               value=_lv("tray_floor_t_m") + _lv("pad_t_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-SLOT-WALL", "Foam between the pod recess and the spar slot", "Recess ends this far ahead of the spar-slot front face",
               basis="subsystems/pod/params.json slot_wall_m; D1 confirms on the first core (CR-D2-04)", value=_lv("slot_wall_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-STOP-T", "Aft stop wall thickness", "Printed aft stop on the handle bridge, the pack's aft stop",
               basis="C3 CR-C3-01 (3.0 mm, 2 mm root fillet), adopted at R3", value=_lv("aft_stop_m")[0], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-FWD-STOP", "Nose block A length, forward stop thickness", "Fixed XPS block behind the nose wall, then the "
               "printed forward stop (backstop of the crush block); the stop face follows the nose (R4)",
               basis="CHANGE-LOG D-25 (block A 7.0 mm, stop face -0.1002 at x_le -0.115), C3 CR-C3-01 (3.0 mm)",
               value=[_lv("nose_block_l_m"), _lv("fwd_stop_m")[0]], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-AFT-STOP-X", "Aft stop face x", "Face of the aft stop the spacers bear on",
               basis="subsystems/pod/params.json aft_stop_x_m: A1's 0.073 heavy-pack aft face + 4 mm", value=_lv("aft_stop_x_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-PACK-AFT", "Pack aft face, nominal and 680 g", "A1's stations: aft face for the nominal centroid x -0.001 and with a 680 g pack",
               basis="team/A1/CHANGE-REQUESTS.md#CR-A1-27 (D-24, D-25)", value=list(_lv("pack_aft_face_m")), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-SPREADER-T", "Spreader on the pack fore face", "Printed PETG plate between the pack and the crush block",
               basis="C5 CR-C5-02 / ASM-C5-SPREADER-T", value=_lv("spreader_t_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-BLOCK-SEC", "Crush block section inputs", "Tray floor thickness under the block, vent groove width x depth in its top",
               basis="subsystems/pod/params.json tray_floor_t_m, block_groove_m (vent path over the pack, CR-E3-03)",
               value=[_lv("tray_floor_t_m")] + list(_lv("block_groove_m")), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-SPACERS", "Aft spacer set", "Printed U-spacers behind the pack (2 mm steps)", basis="subsystems/pod/params.json spacer_set_m",
               value=list(_lv("spacer_set_m")), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-STRAP-CAP", "Installed strap loop capacity", "Breaking load of one 20 mm hook-and-loop battery strap loop as installed (two legs)",
               basis="ESTIMATE for rubber-backed RC battery straps; T-D2-STRAP-PULL pulls one loop to 2 x 85 N", value=100.0, unit="N",
               status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-N-STRAPS", "Pack straps", "Straps holding the pack in z and y", basis="D2 design", value=2, unit="-", cites=SRC_POD)
kit.assumption("ASM-D2-TIE-CAP", "Spar tie capacity", "Rated tensile strength of one 7.6 mm heavy-duty nylon cable tie (50 lb class)",
               basis="catalogue class value 50 lbf = 222 N; T-D2-HANDLE-PULL proof-loads the handle", value=222.0, unit="N",
               status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-N-TIES", "Spar ties", "One tie per handle foot", basis="D2 design", value=2, unit="-", cites=SRC_POD)
kit.assumption("ASM-D2-ULT", "Ultimate factor", "Ultimate = 1.5 x limit for handling loads", basis="C1 LOADS.md convention (limit x 1.5)",
               value=1.5, unit="-", cites=SRC_POD)
kit.assumption("ASM-D2-POD-M-ULT", "Pod-to-wing moment, ultimate", "Pitching moment at the pod bond in the L1 landing, ultimate",
               basis="team/C1/LOADS.md joint table row 'Pod -> wing (C3)': 2.0 N m limit, 3.0 N m ultimate", value=3.0, unit="N m", cites=SRC_POD)
kit.assumption("ASM-D2-XPS-ALLOW", "XPS bond allowable (tension)", "Allowable tensile stress at an epoxy-to-XPS F-250 bond line, foam failure",
               basis="ESTIMATE, conservative for 25 psi XPS (compressive 172 kPa); C6 owns it (CR-C3-05), T-D2-BOND-PULL", value=100000.0,
               unit="Pa", status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-PART-MASSES", "Pod part masses from the CAD", "Declared masses of POD-001 ... POD-008 (g), body volumes x densities",
               basis="team/D2/pod_data.py from subsystems/pod/fusion/pod.py; foam board areal mass and PETG fill are estimates; weigh (T-D2-WEIGH)",
               value=[_MASSES[k] for k in sorted(_MASSES)], unit="g", status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-PITOT-Y", "Pitot boom lateral station", "Boom on the left side-channel centre, beside the pack",
               basis="params.json avionics.pitot_tip_xyz_m[1] (D-25 adopted CR-D2-03)", value=_PP["avionics"]["pitot_tip_xyz_m"]["value"][1],
               unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-SOCKET", "Pitot socket length inside / collar outside", "Socket depth behind the nose wall and collar ahead of it",
               basis="subsystems/pod/params.json socket_m", value=[_lv("socket_m")[2], _lv("socket_m")[3]], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-GEOM-CAD", "Pod CAD geometry read-outs", "Values the CAD layout computes from the wing section and pod params: "
               "[pad-to-wing clearance over the overhang, antenna A element to pack, antenna B element to pack, GPS to the nearest "
               "power item (PDB / AS150U park / UBEC) (m); wire-channel height under the pack, crossing gap leg-to-aft-wall, crossing "
               "height (m); tray front-piece area (m2)]",
               basis="subsystems/pod/fusion/pod.py#layout() via team/D2/pod_data.py (S5010 section, pod params)", value=_GEO, unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-MAST-BOLT", "GPS mast screw: length, grip", "PA66 M3x16 screw length and clamped grip (counterbored boss, no washer)",
               basis="C6 CR-C6-18 (PA66 screw + nut, grip <= 11.0 mm); subsystems/pod/params.json socket_boss_m", value=[0.016, 0.010],
               unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-PAPER-SHEAR", "Epoxy on foam-board paper face, shear allowable", "PETG epoxied to the scuffed paper face",
               basis="C6 CR-C6-16 (100 kPa, halved from 200); subsystems/pod/params.json paper_shear_pa", value=_lv("paper_shear_pa"),
               unit="Pa", status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-F2-ROUTE", "F2 routing minima in the pod", "Wire channel under the pack (height), crossing gap behind the aft stop",
               basis="team/F2/CHANGE-REQUESTS.md#CR-F2-03 (d) 10 x 3 mm, (c) >= 6.7 mm", value=[0.003, 0.0067], unit="m", cites=SRC_POD)


def _section(coords):
    return [tuple(p) for p in coords]


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-D2-BAY", equation="x_fs = pod LE + t + block A + t_fs (forward stop aft face); bay L = x_as - x_fs; H = (base + H - t) - (base + t + floor stack); "
          "x_nose_in = pod LE + t; nose block = (x_fs - t_fs) - x_nose_in; centroid against the forward stop = x_fs + L_pack/2 ; "
          "nominal / heavy centroid = aft face - L_pack/2 ; spacer = x_as - aft face ; block B (nominal) = (aft_nom - L_pack - t_sp) - x_fs ; block section = bw (zh - tray top) - groove ; "
          "aft reach = x_as - L_pack/2 ; travel = bay L - L_pack",
          inputs={"x_le": P + "pod.x_le_m", "size": P + "pod.size_m", "z_base": P + "pod.z_base_m", "t": P + "fins.board_t_m",
                  "fs": "ASM-D2-FWD-STOP", "x_as": "ASM-D2-AFT-STOP-X", "aft": "ASM-D2-PACK-AFT", "t_sp": "ASM-D2-SPREADER-T",
                  "stack": "ASM-D2-FLOOR-STACK", "bw": "ASM-D2-BAY-W", "pack": P + "battery.size_m", "sec": "ASM-D2-BLOCK-SEC"})
def bay(x_le, size, z_base, t, fs, x_as, aft, t_sp, stack, bw, pack, sec):
    l_a, t_fs = fs
    xn = x_le + t
    x_fs = xn + l_a + t_fs
    zh = z_base + size[2] - t
    zp = z_base + t + stack
    return {"bay_l": x_as - x_fs, "bay_w": bw, "bay_h": zh - zp, "pack_x_fwd": x_fs + pack[0] / 2,
            "pack_x_nom": aft[0] - pack[0] / 2, "pack_x_hvy": aft[1] - pack[0] / 2, "aft_reach": x_as - pack[0] / 2,
            "spacer_nom": x_as - aft[0], "spacer_hvy": x_as - aft[1], "block_nom": (aft[0] - pack[0] - t_sp) - x_fs,
            "nose_in": xn, "nose_block": l_a, "x_fs": x_fs, "block_area": bw * (zh - (z_base + t + sec[0])) - sec[1] * sec[2], "travel": x_as - x_fs - pack[0], "pack_z": zp + pack[2] / 2}


@kit.calc("CALC-D2-STATION", equation="most forward centroid that keeps C5's block B = x_fs + t_sp + L_B + L_pack/2 ; station range = "
          "aft reach - that ; spacer sum >= range",
          inputs={"x_fs": "CL-D2-FWD-STOP-X", "t_sp": "ASM-D2-SPREADER-T", "LB": "CL-C5-BLOCK-L", "pack": P + "battery.size_m",
                  "reach": "CL-D2-AFT-REACH", "sp": "ASM-D2-SPACERS"})
def station(x_fs, t_sp, LB, pack, reach, sp):
    x_min = x_fs + t_sp + LB + pack[0] / 2
    return {"x_fwd_min": x_min, "range": reach - x_min, "spacer_sum": sum(sp)}


@kit.calc("CALC-D2-RECESS", equation="x0: upper surface z(x) = pod base; depth = z(x_end) - base, x_end = spar x - r - wall; "
          "foam under = base - lower surface z(x_end)",
          inputs={"sec": "ASM-A5-SECTION", "c": P + "wing.chord_m", "z_base": P + "pod.z_base_m", "xs": P + "wing.spar.x_m",
                  "od": P + "wing.spar.od_m", "wall": "ASM-D2-SLOT-WALL"})
def recess(sec, c, z_base, xs, od, wall):
    co = _section(sec)
    zu = lambda x: k9.surface_z(co, c, x / c, "upper")
    lo, hi = 0.0, xs
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if zu(mid) < z_base else (lo, mid)
    x1 = xs - od / 2 - wall
    return {"x0": (lo + hi) / 2, "x1": x1, "depth": zu(x1) - z_base,
            "foam_under": z_base - k9.surface_z(co, c, x1 / c, "lower")}


@kit.calc("CALC-D2-CAD", equation="read-outs of pod.py#layout(): pad clearance, antenna A / B to pack, GPS to nearest power item, "
          "wire channel and crossing (F2)", inputs={"g": "ASM-D2-GEOM-CAD"})
def cad(g):
    return {"overhang_clr": g[0], "ant_a": g[1], "ant_b": g[2], "gps": g[3], "ch_h": g[4], "cross_gap": g[5], "cross_h": g[6]}


@kit.calc("CALC-D2-POD-BONDS", equation="capacity = bonded area x epoxy-on-paper shear allowable",
          inputs={"g": "ASM-D2-GEOM-CAD", "tau": "ASM-D2-PAPER-SHEAR"})
def pod_bonds(g, tau):
    return {"front_n": g[7] * tau}


@kit.calc("CALC-D2-NOSE-EXT", equation="block B for mass m: L_B(m) = CL-C5-BLOCK-L x m / m_nom (crush energy ~ m); forward stop face "
          "needed = x_station - L_pack/2 - t_sp - L_B(m); nose extension = x_fs - that (>0: the nose must move forward by this)",
          inputs={"x_fs": "CL-D2-FWD-STOP-X", "t_sp": "ASM-D2-SPREADER-T", "LB": "CL-C5-BLOCK-L", "pack": P + "battery.size_m",
                  "m_nom": P + "battery.mass_kg", "rng": "ASM-A3-PACK-RANGE", "x550": "CL-C5-PACK-X-B3", "x503": "CL-C5-PACK-X-B3-LIGHT"})
def nose_ext(x_fs, t_sp, LB, pack, m_nom, rng, x550, x503):
    need = lambda x, m: x_fs - (x - pack[0] / 2 - t_sp - LB * m / (m_nom * 1000))
    return {"ext_nom": need(x550, m_nom * 1000), "ext_light": need(x503, min(rng))}


@kit.calc("CALC-D2-STRAPS", equation="capacity = n straps x installed loop capacity", inputs={"n": "ASM-D2-N-STRAPS", "cap": "ASM-D2-STRAP-CAP"})
def straps(n, cap):
    return {"capacity_n": n * cap}


@kit.calc("CALC-D2-POD-CRASH", equation="F = (pod + avionics + power - nominal pack + heaviest pack listing) x n_crash x g",
          inputs={"pod": P + "mass.allocation_g.pod", "avn": P + "mass.allocation_g.avionics", "pwr": P + "mass.allocation_g.power",
                  "pack_nom": P + "battery.mass_kg", "pack_rng": "ASM-A3-PACK-RANGE", "n": "CL-C1-CRASH-N", "g": P + "env.g_ms2"})
def pod_crash(pod, avn, pwr, pack_nom, pack_rng, n, g):
    m_g = pod + avn + pwr - pack_nom * 1000 + max(pack_rng)
    return {"mass_g": m_g, "force_n": m_g / 1000 * n * g}


@kit.calc("CALC-D2-TIES", equation="capacity = n ties x tie rating", inputs={"n": "ASM-D2-N-TIES", "cap": "ASM-D2-TIE-CAP"})
def ties(n, cap):
    return {"capacity_n": n * cap}


@kit.calc("CALC-D2-HANDLE", equation="F_ult = gate mass x g x handling factor x ultimate factor",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "nh": "ASM-C1-HANDLING-N", "u": "ASM-D2-ULT"})
def handle(m, g, nh, u):
    return {"force_ult_n": m * g * nh * u}


@kit.calc("CALC-D2-PITOT", equation="boom length = socket inner end - tip x; exposed = pod LE - collar - tip x",
          inputs={"tip": P + "avionics.pitot_tip_xyz_m", "x_le": P + "pod.x_le_m", "t": P + "fins.board_t_m", "sock": "ASM-D2-SOCKET"})
def pitot(tip, x_le, t, sock):
    inner = x_le + t + sock[0]
    return {"boom_len": inner - tip[0], "exposed": (x_le - sock[1]) - tip[0], "socket_depth": inner - (x_le - sock[1])}


@kit.calc("CALC-D2-MAST-BOLT", equation="past the grip = screw length - grip ; C6 E-POD-06 min engagement 4.0 mm (PA66 nut fully on + 2 pitches)",
          inputs={"b": "ASM-D2-MAST-BOLT"})
def mast_bolt(b):
    return {"past": b[0] - b[1], "grip": b[1]}


@kit.calc("CALC-D2-MASS", equation="pod mass = sum of the CAD part masses", inputs={"parts": "ASM-D2-PART-MASSES"})
def mass(parts):
    return {"mass_g": sum(parts)}


# ---------------------------------------------------------------- claims
PODP = ["POD-001", "POD-002"]
kit.claim("CL-D2-BAY-L", "Pack bay inside length (forward stop to aft stop)", calc="CALC-D2-BAY", output="bay_l", unit="m",
          limit=(">=", 0.160), verifies=["R-BATT-HANDLING"], parts=PODP + ["POD-007"], cites=SRC_POD,
          how="Measure forward stop to aft stop inside the built pod; drop the real pack in with the block and spacers out.",
          note="E2 CR-E2-02 minimum 0.160 m")
kit.claim("CL-D2-BAY-W", "Pack bay inside width (between the guides)", calc="CALC-D2-BAY", output="bay_w", unit="m",
          limit=(">=", 0.052), verifies=["R-BATT-HANDLING"], parts=PODP, how="Calipers between the guides.")
kit.claim("CL-D2-BAY-H", "Pack bay inside height (pad top to hatch underside)", calc="CALC-D2-BAY", output="bay_h", unit="m",
          limit=(">=", 0.053), verifies=["R-BATT-HANDLING"], parts=PODP + ["POD-003"],
          how="Close the hatch over the strapped pack with the balance lead parked: no bulge.")
kit.claim("CL-D2-PACK-X-FWD", "Pack centroid if it sat against the forward stop (block out)", calc="CALC-D2-BAY", output="pack_x_fwd", unit="m",
          parts=PODP, how="Mark the pack centre; measure from the wing LE with the pack against the forward stop.",
          note="R3: the forward stop aft face (x -0.1002) is unchanged, so this reference is unchanged; the pack never flies here (the crush block is ahead of it)")
kit.claim("CL-D2-PACK-X-NOM", "Pack centroid, nominal station (aft face 0.069, 8 mm spacer)", calc="CALC-D2-BAY", output="pack_x_nom", unit="m",
          parts=PODP + ["POD-008"], how="Pack strapped with its block and spacer; measure the centre mark from the wing LE.",
          note="CR-A1-27: x -0.001 m")
kit.claim("CL-D2-PACK-X-HEAVY", "Pack centroid, 680 g station (aft face 0.073, 4 mm spacer)", calc="CALC-D2-BAY", output="pack_x_hvy",
          unit="m", parts=PODP + ["POD-008"], how="As CL-D2-PACK-X-NOM with the 4 mm spacer.")
kit.claim("CL-D2-AFT-REACH", "Most aft pack centroid the bay allows (no spacer)", calc="CALC-D2-BAY", output="aft_reach", unit="m",
          limit=(">=", "CL-C5-PACK-X-B3-HEAVY"), verifies=["R-CG-RANGE"], parts=["POD-007"],
          how="Pack against the aft stop with no spacer: centre mark from the wing LE.",
          note="also >= A1's 680 g station (CL-D2-PACK-X-HEAVY) by 4 mm")
kit.claim("CL-D2-SPACER-NOM", "Aft spacer at the nominal station", calc="CALC-D2-BAY", output="spacer_nom", unit="m", parts=["POD-008"],
          how="Spacer thickness fitted behind the nominal pack.")
kit.claim("CL-D2-BLOCK-B-NOM", "Crush block length at the nominal station (forward stop to spreader)", calc="CALC-D2-BAY", output="block_nom",
          unit="m", limit=(">=", "CL-C5-BLOCK-L"), verifies=["R-PACK-RETENTION"], parts=["POD-008"],
          how="Cut length of the block for a 550 g pack; rule.")
kit.claim("CL-D2-BLOCK-SECTION", "Crush block B section (52 mm x tray top to hatch, less the vent groove)", calc="CALC-D2-BAY",
          output="block_area", unit="m2", parts=["POD-008"], how="Calipers on the cut block.",
          note="C5 uses bay W x bay H (pad top to hatch) for A_bay; the block stands on the tray, 2.5 mm lower than the pack")
kit.claim("CL-D2-NOSE-INNER", "Nose wall inside face x (front of the fixed nose block)", calc="CALC-D2-BAY", output="nose_in", unit="m",
          parts=["POD-001"], how="Built pod: rule from the wing LE to the nose wall inside face.",
          note="foam-board nose wall 4.8 mm (C5 assumes 2 mm, ASM-C5-NOSE-WALL)")
kit.claim("CL-D2-FWD-STOP-X", "Forward stop aft face x (crush block backstop)", calc="CALC-D2-BAY", output="x_fs", unit="m",
          parts=["POD-002"], how="Built pod: rule from the wing LE to the forward stop aft face.",
          note="R4: derived from the nose (x_le + wall + block A + stop), so the bay follows pod.x_le_m (CR-D2-16)")
kit.claim("CL-D2-NOSE-BLOCK-L", "Fixed XPS nose block length (block A)", calc="CALC-D2-BAY", output="nose_block", unit="m", parts=["POD-001"],
          how="Cut length; rule.")
kit.claim("CL-D2-PACK-TRAVEL", "Stop-to-stop room beyond the pack length (block B + spreader + spacers)", calc="CALC-D2-BAY", output="travel",
          unit="m", verifies=["R-CG-RANGE"], parts=PODP + ["POD-007", "POD-008"],
          how="Slide the real pack from the forward stop to the aft stop (block and spacers out); record the travel.")
kit.claim("CL-D2-PACK-Z", "Pack centroid height", calc="CALC-D2-BAY", output="pack_z", unit="m", parts=PODP,
          how="Measure pad top above the chord line + half the pack height.")
kit.claim("CL-D2-PACK-X-FWD-MIN", "Most forward pack centroid that keeps C5's crush block B", calc="CALC-D2-STATION", output="x_fwd_min",
          unit="m", limit=("<=", "CL-D2-PACK-X-NOM"), verifies=["R-PACK-RETENTION"], parts=["POD-008"],
          how="Pack strapped with a block cut to CL-C5-BLOCK-L: centre mark from the wing LE.",
          note="any trim forward of this needs the pod nose (or the whole pod group) forward by the same amount (CR-C5-12 is A1's call)")
kit.claim("CL-D2-SPACER-SUM", "Aft spacer set total", calc="CALC-D2-STATION", output="spacer_sum", unit="m",
          limit=(">=", "CL-D2-STATION-RANGE"), verifies=["R-CG-RANGE"], parts=["POD-008"], how="Stack the spacers; calipers.")
kit.claim("CL-D2-STATION-RANGE", "Pack station range inside the bay (forward minimum to aft reach)", calc="CALC-D2-STATION", output="range",
          unit="m", parts=["POD-008"], how="As CL-D2-AFT-REACH and CL-D2-PACK-X-FWD-MIN.")
kit.claim("CL-D2-OVERHANG-CLR", "Pack underside above the wing surface where it overhangs the recess end", calc="CALC-D2-CAD",
          output="overhang_clr", unit="m", limit=(">=", 0.0005), parts=["POD-004", "POD-007"],
          how="Pack strapped at the 0.077 aft face: feeler gauge between the pack and the wing over the spar slot.")
kit.claim("CL-D2-ANT-A-CLR", "Antenna A (hatch tube) element base to the pack", calc="CALC-D2-CAD", output="ant_a", unit="m",
          limit=(">=", "CL-F5-ANT-CLEAR"), verifies=["R-RC-LINK"], parts=["POD-003"], how="Rule from the tube top to the pack top edge.")
kit.claim("CL-D2-ANT-B-CLR", "Antenna B (nose tube) element base to the pack fore face", calc="CALC-D2-CAD", output="ant_b", unit="m",
          limit=(">=", "CL-F5-ANT-CLEAR"), verifies=["R-RC-LINK"], parts=["POD-001"], how="Rule from the nose skin to the pack fore face.")
kit.claim("CL-D2-GPS-CLR", "GPS to the nearest power item (PDB, AS150U park, UBEC zone)", calc="CALC-D2-CAD", output="gps", unit="m",
          limit=(">=", P + "requirements.gps_mast_clearance_m"), verifies=["R-COMPASS"], parts=["POD-005", "POD-002"],
          how="Rule from the GPS puck centre to the PDB, the parked AS150U and the UBEC as installed.")
kit.claim("CL-D2-MAST-BOLT-PAST", "GPS mast screw length past the grip", calc="CALC-D2-MAST-BOLT", output="past", unit="m",
          limit=(">=", 0.004), verifies=["R-JOINT-STACK"], parts=["POD-005", "POD-007"],
          how="Assembled: PA66 nut fully on with >= 2 pitches showing; grip measured with calipers (<= 11.0 mm).",
          note="C6 CR-C6-18 min engagement 4.0 mm")
kit.claim("CL-D2-FLOOR-CH-H", "Wire channel under the pack: foam-board floor to pack underside", calc="CALC-D2-CAD", output="ch_h",
          unit="m", limit=(">=", 0.003), parts=["POD-002", "POD-004"],
          how="Pack strapped: a 3 mm drill shank slides through the channel under the pack.", note="F2 CR-F2-03 (d): 10 x 3 mm")
kit.claim("CL-D2-CROSS-GAP", "Crossing behind the aft stop: handle-leg aft face to aft-wall inside face", calc="CALC-D2-CAD",
          output="cross_gap", unit="m", limit=(">=", 0.0067), parts=["POD-007", "POD-001"],
          how="Calipers between each leg and the aft wall before the deck goes on.", note="F2 CR-F2-03 (c): >= 6.7 mm")
kit.claim("CL-D2-CROSS-H", "Crossing height: stop bridge top to deck underside", calc="CALC-D2-CAD", output="cross_h", unit="m",
          limit=(">=", 0.026), parts=["POD-007", "POD-001"], how="Rule before the deck goes on.", note="F2 CR-F2-03 (c): 26 mm")
kit.claim("CL-D2-FWD-STOP-BOND", "Tray front piece bond (carries the forward stop), shear capacity", calc="CALC-D2-POD-BONDS",
          output="front_n", unit="N", limit=(">=", "CL-C1-PACK-CRASH-LOAD"), verifies=["R-PACK-RETENTION"], parts=["POD-002", "POD-001"],
          how="T-C3-STOP-PUSH on the built tray: 100 N on the stop; the stop breaks off (C3 fuse), the tray does not peel.",
          note="R4 splits the tray at the wire channel; the front piece is solid so its bond (> ~100 N stop break load) outlasts the stop")
kit.claim("CL-D2-NOSE-EXT-NOM", "Nose extension needed to fly a 550 g pack at C5's B3-target station with block B", calc="CALC-D2-NOSE-EXT",
          output="ext_nom", unit="m", verifies=["R-CG-RANGE"], parts=["POD-001", "POD-002"],
          how="python -I redesign/team/D2/pod_station_options.py (CAD rebuilt at each extension).",
          note="> 0: the pack cannot reach the station today (CR-D2-16 asks A1 for x_le -0.127)")
kit.claim("CL-D2-NOSE-EXT-LIGHT", "Nose extension needed to fly a 503 g pack at C5's light station with block B", calc="CALC-D2-NOSE-EXT",
          output="ext_light", unit="m", verifies=["R-CG-RANGE"], parts=["POD-001", "POD-002"],
          how="As CL-D2-NOSE-EXT-NOM.", note="block B scaled with pack mass (UNVERIFIED, C5 to confirm)")
kit.claim("CL-D2-RECESS-X0", "Pod recess start (upper surface at the pod base)", calc="CALC-D2-RECESS", output="x0", unit="m",
          parts=["POD-001"], how="Template on the hot-wired core; the recess floor meets the skin here.")
kit.claim("CL-D2-RECESS-DEPTH", "Pod recess depth at its aft end (D1 cuts)", calc="CALC-D2-RECESS", output="depth", unit="m",
          parts=["POD-001"], how="Depth gauge at the recess aft end before bonding.")
kit.claim("CL-D2-RECESS-FOAM", "Foam left under the recess at its aft end", calc="CALC-D2-RECESS", output="foam_under", unit="m",
          limit=(">=", 0.015), parts=["POD-001"], how="Calipers through the core at the recess end.",
          note="15 mm keeps the root section stiffer than the outboard core at the tubes (~27 mm thick)")
kit.claim("CL-D2-STRAP-CAP", "Pack strap capacity (2 straps)", calc="CALC-D2-STRAPS", output="capacity_n", unit="N",
          limit=(">=", "CL-C1-PACK-CRASH-LOAD"), verifies=["R-PACK-RETENTION"], parts=["POD-004", "POD-002"],
          how="T-D2-STRAP-PULL: one installed loop pulled to 2 x 85 N without slip or tear.")
kit.claim("CL-D2-POD-CRASH-F", "Pod group crash load (pod, heaviest pack, avionics, power), ultimate", calc="CALC-D2-POD-CRASH",
          output="force_n", unit="N", parts=["POD-001", "POD-007"], how="Recompute from weighed masses.")
kit.claim("CL-D2-HANDLE-F-ULT", "Carry handle load, lifting at 2 g, ultimate", calc="CALC-D2-HANDLE", output="force_ult_n", unit="N",
          parts=["POD-007"], how="Covered by T-D2-HANDLE-PULL (120 N > this).")
kit.claim("CL-D2-TIE-CAP", "Spar ties: carry-handle capacity (handling)", calc="CALC-D2-TIES", output="capacity_n", unit="N",
          limit=(">=", "CL-D2-HANDLE-F-ULT"), verifies=["R-STRUCT-MARGIN"], parts=["POD-007"],
          how="T-D2-HANDLE-PULL: 120 N on the handle grip for 10 s, no tie slip, no foot lift.",
          note="CR-C3-04: handling (G1) only; the crash path is straps -> tray -> floor -> bond (C3 claims)")
kit.claim("CL-D2-PITOT-BOOM-L", "Pitot boom length (socket inner end to tip)", calc="CALC-D2-PITOT", output="boom_len", unit="m",
          verifies=["R-AIRSPEED"], parts=["POD-006"], how="F3 cuts the boom to this length; check the tip at x -0.195 m with the boom seated.")
kit.claim("CL-D2-PITOT-SOCKET", "Pitot socket depth", calc="CALC-D2-PITOT", output="socket_depth", unit="m", parts=["POD-006"],
          how="Depth gauge in the bore.")
kit.claim("CL-D2-MASS", "Pod subsystem mass (CAD estimate)", calc="CALC-D2-MASS", output="mass_g", unit="g",
          limit=("<=", P + "mass.allocation_g.pod"), verifies=["R-MASS-ALLOC"], parts=sorted(_MASSES),
          how="T-D2-WEIGH: weigh every pod part before bonding; update interfaces.json.",
          note="over the 122 g allocation: CR-D2-09 (rev. R4) asks A1 for 128 g (131 g with CR-D2-16)")

# ---------------------------------------------------------------- tests (planned)
kit.test("T-D2-WEIGH", "Weigh every pod part before assembly", verifies=["CL-D2-MASS"],
         procedure="0.1 g scale; each printed part, board piece and XPS block; record in subsystems/pod/parts.csv")
kit.test("T-D2-FIT", "Real pack fit", verifies=["CL-D2-BAY-L", "CL-D2-BAY-W", "CL-D2-BAY-H", "CL-D2-PACK-TRAVEL", "CL-D2-AFT-REACH",
                                                 "CL-D2-OVERHANG-CLR", "CL-D2-PACK-X-NOM"],
         procedure="Both packs: in through the hatch, tucked under the deck, strapped at the nominal and the aft-reach stations, "
                   "block and spacer fitted, leads over the aft stop to the AS150U park, hatch closes; feeler gauge under the overhang")
kit.test("T-D2-STRAP-PULL", "Strap loop pull test", verifies=["CL-D2-STRAP-CAP"],
         procedure="Spring scale, one installed loop on a tray offcut, 170 N for 10 s; no slip, no tear at the slot")
kit.test("T-D2-HANDLE-PULL", "Handle proof load on the built wing", verifies=["CL-D2-TIE-CAP"],
         procedure="Wing supported at the spar ends; 12 kg on the grip for 10 s; feet stay on the spar, ties do not slip")

if __name__ == "__main__":
    kit.write()
