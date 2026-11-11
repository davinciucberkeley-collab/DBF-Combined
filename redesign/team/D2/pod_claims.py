"""D2 pod designer (revision D2-R6, params A1-R5: D-62 bay re-lay, D-64 pack, D-69 C3 fixes): claims other roles build on (pack bay and stations, crush-block
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


def _left_ch_hits(ctx, box):
    """pod bodies whose bounding box enters the left-channel volume F1 asked D2 to keep free (CR-F1-26)."""
    x0, x1, z0, z1 = box
    n = 0
    for c in ctx.components.values():
        for sh in c.shapes:
            pts = [c.to_world(q) for q in sh.points()]
            lo = [min(q[i] for q in pts) for i in range(3)]
            hi = [max(q[i] for q in pts) for i in range(3)]
            ylo, yhi = -0.0652, -0.0275                 # left channel (wall inner face to guide outer face)
            if min(hi[0], x1) - max(lo[0], x0) > 1e-4 and min(hi[1], yhi) - max(lo[1], ylo) > 1e-4 and \
                    min(hi[2], z1) - max(lo[2], z0) > 1e-4:
                n += 1
    return n


def _cad_readouts():
    import pod_data as pdm
    ctx, _P, _Lc, G, _src = pdm.build_pod()
    return [round(v, 7) for v in (G["overhang_clr"], G["ant_a_pack_clr"], G["ant_b_pack_clr"], min(G["gps_clr"].values()),
                                  G["ch_h"], G["cross_gap"], G["cross_h"], G["tray_front_area"] + G["fs_flange_bond"],
                                  G["tray_rear_area"], G["strut_rib_l"], G["strut_clear_skin"], G["bracket_area"],
                                  G["fs_flange_bond"], G["pdb_pad"][0], G["pdb_pad"][1], G["ant_b_tip_x"],
                                  _left_ch_hits(ctx, G["left_ch_clear"]))]


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
kit.assumption("ASM-D2-STOP-T", "Aft stop wall thickness", "Printed aft stop on the tray rear piece (R5, D-47), the pack's aft stop",
               basis="C3 CR-C3-01 (3.0 mm, 2 mm root fillet), adopted at R3", value=_lv("aft_stop_m")[0], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-FWD-STOP", "Nose-wall bond line (was block A), forward stop thickness", "The printed forward-stop T "
               "(backstop of the crush block) sits on a 1 mm epoxy line on the nose wall inside face; the stop face follows the nose",
               basis="CHANGE-LOG D-47 (block A deleted, nose skin to stop face 8.8 mm), D-62 (stop face -0.1312 at x_le -0.140), "
                     "C3 CR-C3-01 (3.0 mm), D-69 (T with a flange under the floor)",
               value=[_lv("nose_block_l_m"), _lv("fwd_stop_m")[0]], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-AFT-STOP-X", "Aft stop face x", "Face of the aft stop the spacers bear on",
               basis="CHANGE-LOG D-62 / CR-A1-62: aft stop = datum -0.032 + L/2 (0.0675, D-64 pack) + pod.pack_aft_travel_m 0.012 = 0.0475; "
                     "A1's text says 0.050, the same sum with the retired 0.140 pack (CR-D2-24)", value=_lv("aft_stop_x_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-PACK-AFT", "Pack aft face, datum and no-spacer", "Aft face for the datum centroid "
               "pod.pack_x_nominal_m -0.032 (12 mm stack, CAD) and with no spacer on the aft stop (centroid -0.020, D-62)",
               basis="CHANGE-LOG D-62, team/A1/CHANGE-REQUESTS.md#CR-A1-62", value=list(_lv("pack_aft_face_m")), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-PACK-STATIONS", "Pack centroid stations for the 546 g, 590 g and 550 g packs", "A1's D-62 frame-estimate "
               "stations for the D-64 cases (listing -5 g, acceptance line, nominal); the CAD pack sits at the datum; the flight card "
               "takes A3's live stations (CR-A3-27)",
               basis="CHANGE-LOG D-62, D-64; team/A1 CALC-A1-PACK-CASES; subsystems/pod/params.json pack_x_per_pack_m",
               value=[_lv("pack_x_per_pack_m")["546"], _lv("pack_x_per_pack_m")["590"], _lv("pack_x_per_pack_m")["550"]], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-STACK-BLOCK-A1", "Crush block length A1 uses for the crush-stack limit", "Block length behind which A1 "
               "puts the most forward centroid -0.0379 (D-62)", basis="CHANGE-LOG D-62 (crush block >= 24.3 mm, the D-47 / D-59 "
               "503 g value); C5's 550 g class value is CL-C5-BLOCK-L", value=0.0243, unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-UNPLUG-M", "AS150U unplug moment at the PDB bosses, design", "50 N unplug at 18 mm above the boss tops",
               basis="team/C6/CHANGE-REQUESTS.md#CR-C6-27, team/C6/JOINTS.md E-PWR-03 (1.94 N m design)", value=1.94, unit="N m", cites=SRC_POD)
kit.assumption("ASM-D2-PLATE-PEEL", "Flat-wise allowable of a rigid PETG pad on the foam-board paper face", "Peel / flat-wise "
               "tension the plate bond may carry under a local moment", basis="team/C6/CHANGE-REQUESTS.md#CR-C6-27 (0.05 MPa)",
               value=50000.0, unit="Pa", status="UNVERIFIED", cites=SRC_POD)
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
kit.assumption("ASM-D2-PART-MASSES", "Pod part masses from the CAD", "Declared masses of POD-001 ... POD-010 (g), body volumes x densities",
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
               "height (m); tray front-piece solid area + stop-T flange under the floor (forward stop), tray rear-piece net area (m2); "
               "R6: strut rib free length, rib underside to wing skin (m), wall-bracket flange area per side (m2), stop-T flange "
               "area under the floor (m2), PDB pad length x and width y (m), antenna B tube end x (m), pod bodies inside F1's "
               "left-channel volume (-)]. Item 0 is the most aft pack face (no spacer) ahead of the recess end",
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
@kit.calc("CALC-D2-BAY", equation="x_fs = pod LE + t + bond line + t_fs (forward stop aft face); nose to stop = x_fs - pod LE; bay L = x_as - x_fs; H = (base + H - t) - (base + t + floor stack); "
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
            "nose_in": xn, "nose_block": l_a, "x_fs": x_fs, "nose_to_stop": x_fs - x_le, "block_area": bw * (zh - (z_base + t + sec[0])) - sec[1] * sec[2], "travel": x_as - x_fs - pack[0], "pack_z": zp + pack[2] / 2}


@kit.calc("CALC-D2-STATION", equation="most forward centroid that keeps C5's block B = x_fs + t_sp + L_B + L_pack/2 ; station range = "
          "aft reach - that ; spacer sum >= range",
          inputs={"x_fs": "CL-D2-FWD-STOP-X", "t_sp": "ASM-D2-SPREADER-T", "LB": "CL-C5-BLOCK-L", "pack": P + "battery.size_m",
                  "reach": "CL-D2-AFT-REACH", "sp": "ASM-D2-SPACERS"})
def station(x_fs, t_sp, LB, pack, reach, sp):
    x_min = x_fs + t_sp + LB + pack[0] / 2
    return {"x_fwd_min": x_min, "range": reach - x_min, "spacer_sum": sum(sp)}


@kit.calc("CALC-D2-FWD-ROOM", equation="forward trim room at the nominal station = nominal centroid - most forward centroid with block B",
          inputs={"x_nom": "CL-D2-PACK-X-NOM", "x_min": "CL-D2-PACK-X-FWD-MIN"})
def fwd_room(x_nom, x_min):
    return {"room": x_nom - x_min}


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
    return {"front_n": g[7] * tau, "rear_n": g[8] * tau}


@kit.calc("CALC-D2-PACK-STATIONS", equation="per pack m (546 g, 590 g acceptance line, 550 g): spacer = round_2mm(x_as - (x_target + L_pack/2)); "
          "x = x_as - spacer - L_pack/2; block B = (x - L_pack/2 - t_sp) - x_fs; block B min = CL-C5-BLOCK-L x m / m_nom (crush energy ~ m)",
          inputs={"x_fs": "CL-D2-FWD-STOP-X", "x_as": "ASM-D2-AFT-STOP-X", "t_sp": "ASM-D2-SPREADER-T", "LB": "CL-C5-BLOCK-L",
                  "pack": P + "battery.size_m", "m_nom": P + "battery.mass_kg", "rng": "ASM-A1-PACK-CASES-G", "st": "ASM-D2-PACK-STATIONS",
                  "sp": "ASM-D2-SPACERS"})
def pack_stations(x_fs, x_as, t_sp, LB, pack, m_nom, rng, st, sp):
    step = min(sp)
    out = {}
    for tag, m, x_t in (("light", min(rng), st[0]), ("heavy", max(rng), st[1]), ("mid", m_nom * 1000, st[2])):
        s = max(0.0, round((x_as - (x_t + pack[0] / 2)) / step) * step)
        x = x_as - s - pack[0] / 2
        out.update({"spacer_" + tag: s, "x_" + tag: x, "block_" + tag: (x - pack[0] / 2 - t_sp) - x_fs,
                    "block_min_" + tag: LB * m / (m_nom * 1000), "dx_" + tag: x - x_t})
    return out


@kit.calc("CALC-D2-STACK", equation="pack on the crush stack: x = x_fs + L_B + t_sp + L_pack/2 ; gap to the aft stop = x_as - "
          "(x + L_pack/2) ; spacer that fits = floor(gap / step) x step ; play = gap - spacer ; same with C5's block",
          inputs={"x_fs": "CL-D2-FWD-STOP-X", "LA": "ASM-D2-STACK-BLOCK-A1", "LB": "CL-C5-BLOCK-L", "t_sp": "ASM-D2-SPREADER-T",
                  "pack": P + "battery.size_m", "x_as": "ASM-D2-AFT-STOP-X", "sp": "ASM-D2-SPACERS"})
def stack(x_fs, LA, LB, t_sp, pack, x_as, sp):
    step = min(sp)
    out = {}
    for tag, L_b in (("a1", LA), ("c5", LB)):
        x = x_fs + L_b + t_sp + pack[0] / 2
        gap = x_as - (x + pack[0] / 2)
        n = math.floor(gap / step + 1e-9)
        out.update({"x_" + tag: x, "gap_" + tag: gap, "spacer_" + tag: n * step, "play_" + tag: gap - n * step})
    return out


@kit.calc("CALC-D2-R6-GEOM", equation="read-outs of pod.py#layout() for the D-69 fixes: strut rib free length = bridge front - pad back; "
          "rib to skin = rib underside - max wing surface under it; bracket flange area per side; stop-T flange area under the floor; "
          "antenna B tube end x; pod bodies in the left-channel volume (CR-F1-26)", inputs={"g": "ASM-D2-GEOM-CAD"})
def r6_geom(g):
    return {"rib_l": g[9], "rib_skin": g[10], "bracket": g[11], "flange": g[12], "ant_b_x": g[15], "left_hits": g[16]}


@kit.calc("CALC-D2-PDB-PAD", equation="flat-wise moment capacity of the ribbed PDB plate (rigid pad) = sigma x b x L^2 / 6 ; "
          "RF = capacity / unplug moment", inputs={"g": "ASM-D2-GEOM-CAD", "s": "ASM-D2-PLATE-PEEL", "m": "ASM-D2-UNPLUG-M"})
def pdb_pad(g, s, m):
    cap = s * g[14] * g[13] ** 2 / 6
    return {"m_cap": cap, "rf": cap / m}


@kit.calc("CALC-D2-STRAPS", equation="capacity = n straps x installed loop capacity", inputs={"n": "ASM-D2-N-STRAPS", "cap": "ASM-D2-STRAP-CAP"})
def straps(n, cap):
    return {"capacity_n": n * cap}


@kit.calc("CALC-D2-POD-CRASH", equation="F = (pod + avionics + power - nominal pack + acceptance-line pack) x n_crash x g",
          inputs={"pod": P + "mass.allocation_g.pod", "avn": P + "mass.allocation_g.avionics", "pwr": P + "mass.allocation_g.power",
                  "pack_nom": P + "battery.mass_kg", "pack_rng": "ASM-A1-PACK-CASES-G", "n": "CL-C1-CRASH-N", "g": P + "env.g_ms2"})
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
          note="D-62: forward stop face -0.1312, 135 mm pack; the pack never flies here (the crush block is ahead of it)")
kit.claim("CL-D2-PACK-X-NOM", "Pack centroid at the bay datum, CAD (aft face 0.0355, 12 mm stack blue + yellow)", calc="CALC-D2-BAY", output="pack_x_nom",
          unit="m", limit=("<=", P + "pod.pack_x_nominal_m"), verifies=["R-CG-RANGE"], parts=PODP + ["POD-008", "POD-009", "POD-010"],
          how="Pack strapped with its block, spreader and spacer; measure the centre mark from the wing LE.",
          note="D-62 / CR-A1-62: pod.pack_x_nominal_m -0.032 m (was -0.022, D-47)")
kit.claim("CL-D2-PACK-X-NOSPACER", "Pack centroid with no spacer, on the aft stop (aft face 0.0475)", calc="CALC-D2-BAY", output="pack_x_hvy",
          unit="m", parts=PODP + ["POD-009", "POD-010"], how="As CL-D2-PACK-X-NOM with no spacer.",
          note="D-62: datum + pod.pack_aft_travel_m = -0.020; no D-64 case flies here (590 g uses 8 mm)")
kit.claim("CL-D2-PACK-X-HEAVY", "Pack centroid, 590 g acceptance-line station (8 mm blue)", calc="CALC-D2-PACK-STATIONS", output="x_heavy",
          unit="m", verifies=["R-CG-RANGE"], parts=PODP + ["POD-008", "POD-009", "POD-010"], how="As CL-D2-PACK-X-NOM with the blue 8 mm spacer.",
          note="A1 D-62 frame estimate -0.028 (was the 680 g -0.010 station, retired at D-64)")
kit.claim("CL-D2-PACK-X-LIGHT", "Pack centroid, 546 g station (16 mm: white + green + blue)", calc="CALC-D2-PACK-STATIONS", output="x_light",
          unit="m", verifies=["R-CG-RANGE"], parts=PODP + ["POD-008", "POD-009", "POD-010"],
          how="As CL-D2-PACK-X-NOM with the 2 + 6 + 8 mm spacers.",
          note="A1 D-62 frame estimate -0.036 (the 503 g listing is retired, D-64)")
kit.claim("CL-D2-PACK-X-550", "Pack centroid, 550 g station (14 mm: green + blue)", calc="CALC-D2-PACK-STATIONS", output="x_mid",
          unit="m", verifies=["R-CG-RANGE"], parts=PODP + ["POD-008", "POD-009", "POD-010"],
          how="As CL-D2-PACK-X-NOM with the 6 + 8 mm spacers.",
          note="A1 D-62 frame estimate -0.034; the CAD keeps the pack at the -0.032 datum with 12 mm; the card takes A3's station")
kit.claim("CL-D2-PACK-X-STACK", "Pack centroid on the crush stack with A1's 24.3 mm block (135 mm pack)", calc="CALC-D2-STACK", output="x_a1",
          unit="m", parts=PODP + ["POD-009", "POD-010"], how="Block cut to 24.3 mm, spreader, pack pushed forward: centre mark from the wing LE.",
          note="D-62 quotes -0.0379; for a 550 g class pack C5's block is 25.7 mm (CL-D2-PACK-X-STACK-C5)")
kit.claim("CL-D2-PACK-X-STACK-C5", "Pack centroid on the crush stack with C5's block for the 550 g class", calc="CALC-D2-STACK", output="x_c5",
          unit="m", verifies=["R-PACK-RETENTION"], parts=PODP + ["POD-009", "POD-010"], how="As CL-D2-PACK-X-STACK with the block cut to CL-C5-BLOCK-L.")
kit.claim("CL-D2-STACK-GAP", "Gap between the pack on A1's crush stack and the aft stop", calc="CALC-D2-STACK", output="gap_a1", unit="m",
          parts=["POD-008", "POD-002"], how="Feeler / calipers between the pack aft face and the aft stop with the 24.3 mm block.")
kit.claim("CL-D2-STACK-SPACER", "Spacer stack that fits behind the pack on A1's crush stack", calc="CALC-D2-STACK", output="spacer_a1",
          unit="m", parts=["POD-008"], how="Stack the spacers into the gap.")
kit.claim("CL-D2-STACK-PLAY", "Fore-aft play left on A1's crush stack with the 2 mm spacer grid", calc="CALC-D2-STACK", output="play_a1",
          unit="m", parts=["POD-008", "POD-009"], how="Push the pack fore and aft by hand with the block and spacers fitted; the block is cut "
          "this much longer so the play is zero in flight (C5 CR-C5-14 c).",
          note="the flown stations (A3) have 0 play: the block is cut per pack to fill the stop-to-spreader gap")
kit.claim("CL-D2-BLOCK-B-550", "Crush block length at the 550 g flight station", calc="CALC-D2-PACK-STATIONS", output="block_mid", unit="m",
          limit=(">=", "CL-D2-BLOCK-MIN-550"), verifies=["R-PACK-RETENTION"], parts=["POD-009"], how="Cut length for the 550 g pack; rule.")
kit.claim("CL-D2-BLOCK-MIN-550", "Crush block B minimum for the 550 g pack (C5's length)", calc="CALC-D2-PACK-STATIONS",
          output="block_min_mid", unit="m", parts=["POD-009"], how="C5's CL-C5-BLOCK-L.")
kit.claim("CL-D2-SPACER-LIGHT", "Aft spacer stack for the 546 g pack", calc="CALC-D2-PACK-STATIONS", output="spacer_light", unit="m",
          parts=["POD-008"], how="Stack on the pack label; calipers.")
kit.claim("CL-D2-SPACER-HEAVY", "Aft spacer stack for the 590 g acceptance-line pack", calc="CALC-D2-PACK-STATIONS", output="spacer_heavy", unit="m",
          parts=["POD-008"], how="Blue 8 mm spacer; calipers.")
kit.claim("CL-D2-BLOCK-MIN-LIGHT", "Crush block B minimum for the 546 g pack (scaled from C5's 550 g length)", calc="CALC-D2-PACK-STATIONS",
          output="block_min_light", unit="m", parts=["POD-009"], how="C5 confirms per pack mass (CR-D2-10).",
          note="scaling with pack mass is D2's estimate (UNVERIFIED until C5 publishes CL-C5-BLOCK-L per mass)")
kit.claim("CL-D2-BLOCK-MIN-HEAVY", "Crush block B minimum for the 590 g pack (scaled from C5's 550 g length)", calc="CALC-D2-PACK-STATIONS",
          output="block_min_heavy", unit="m", parts=["POD-009"], how="C5 confirms per pack mass (CR-D2-10).")
kit.claim("CL-D2-BLOCK-B-LIGHT", "Crush block length at the 546 g station", calc="CALC-D2-PACK-STATIONS", output="block_light", unit="m",
          limit=(">=", "CL-D2-BLOCK-MIN-LIGHT"), verifies=["R-PACK-RETENTION"], parts=["POD-009"], how="Cut length for the 546 g pack; rule.")
kit.claim("CL-D2-BLOCK-B-HEAVY", "Crush block length at the 590 g station", calc="CALC-D2-PACK-STATIONS", output="block_heavy", unit="m",
          limit=(">=", "CL-D2-BLOCK-MIN-HEAVY"), verifies=["R-PACK-RETENTION"], parts=["POD-009"], how="Cut length for the 590 g pack; rule.")
kit.claim("CL-D2-PACK-FWD-ROOM", "Forward trim room at the nominal station with C5's block B", calc="CALC-D2-FWD-ROOM", output="room",
          unit="m", verifies=["R-CG-RANGE"], parts=["POD-009"], how="Block cut to CL-C5-BLOCK-L: pack slides this far forward of nominal.",
          note="room ahead of the -0.032 datum with C5's 25.7 mm block (D-62 quotes the -0.0379 limit with 24.3 mm)")
kit.claim("CL-D2-AFT-REACH", "Most aft pack centroid the bay allows (no spacer)", calc="CALC-D2-BAY", output="aft_reach", unit="m",
          limit=(">=", "CL-D2-PACK-X-HEAVY"), verifies=["R-CG-RANGE"], parts=["POD-002"],
          how="Pack against the aft stop with no spacer: centre mark from the wing LE.",
          note="D-62: the aft stop is 12 mm (pod.pack_aft_travel_m) behind the datum pack's aft face: -0.020")
kit.claim("CL-D2-SPACER-NOM", "Aft spacer stack at the bay datum, CAD (blue 8 + yellow 4 mm)", calc="CALC-D2-BAY", output="spacer_nom", unit="m", parts=["POD-008"],
          how="Spacer thickness fitted behind the nominal pack.")
kit.claim("CL-D2-BLOCK-B-NOM", "Crush block length at the nominal station (forward stop to spreader)", calc="CALC-D2-BAY", output="block_nom",
          unit="m", limit=(">=", "CL-C5-BLOCK-L"), verifies=["R-PACK-RETENTION"], parts=["POD-009"],
          how="Cut length of the block for a 550 g pack; rule.")
kit.claim("CL-D2-BLOCK-SECTION", "Crush block B section (52 mm x tray top to hatch, less the vent groove)", calc="CALC-D2-BAY",
          output="block_area", unit="m2", parts=["POD-009"], how="Calipers on the cut block.",
          note="C5 uses bay W x bay H (pad top to hatch) for A_bay; the block stands on the tray, 2.5 mm lower than the pack")
kit.claim("CL-D2-NOSE-INNER", "Nose wall inside face x", calc="CALC-D2-BAY", output="nose_in", unit="m",
          parts=["POD-001"], how="Built pod: rule from the wing LE to the nose wall inside face.",
          note="foam-board nose wall 4.8 mm (C5 assumes 2 mm, ASM-C5-NOSE-WALL)")
kit.claim("CL-D2-FWD-STOP-X", "Forward stop aft face x (crush block backstop)", calc="CALC-D2-BAY", output="x_fs", unit="m",
          parts=["POD-002"], how="Built pod: rule from the wing LE to the forward stop aft face.",
          note="D-62: -0.1312 (was -0.1212); derived from the nose (x_le + wall + bond line + stop)")
kit.claim("CL-D2-NOSE-BLOCK-L", "Nose wall to forward stop bond line (XPS block A deleted, D-47)", calc="CALC-D2-BAY", output="nose_block",
          unit="m", parts=["POD-001", "POD-002"], how="Feeler gauge before bonding: stop fore face 1 mm off the nose wall; fill with microballoon epoxy.")
kit.claim("CL-D2-NOSE-TO-STOP", "Nose skin to forward stop face (A1's 'nose block')", calc="CALC-D2-BAY", output="nose_to_stop", unit="m",
          limit=("<=", 0.00885), parts=["POD-001", "POD-002"], how="Rule from the nose skin to the stop face through the hatch.",
          note="D-47 / D-62: 8.8 mm (limit 8.8 mm + 0.05 mm rounding)")
kit.claim("CL-D2-PACK-TRAVEL", "Stop-to-stop room beyond the pack length (block B + spreader + spacers)", calc="CALC-D2-BAY", output="travel",
          unit="m", verifies=["R-CG-RANGE"], parts=PODP + ["POD-008", "POD-009", "POD-010"],
          how="Slide the real pack from the forward stop to the aft stop (block and spacers out); record the travel.")
kit.claim("CL-D2-PACK-Z", "Pack centroid height", calc="CALC-D2-BAY", output="pack_z", unit="m", parts=PODP,
          how="Measure pad top above the chord line + half the pack height.")
kit.claim("CL-D2-PACK-X-FWD-MIN", "Most forward pack centroid that keeps C5's crush block B", calc="CALC-D2-STATION", output="x_fwd_min",
          unit="m", limit=("<=", "CL-D2-PACK-X-NOM"), verifies=["R-PACK-RETENTION"], parts=["POD-009"],
          how="Pack strapped with a block cut to CL-C5-BLOCK-L: centre mark from the wing LE.")
kit.claim("CL-D2-SPACER-SUM", "Aft spacer set total", calc="CALC-D2-STATION", output="spacer_sum", unit="m",
          limit=(">=", "CL-D2-STATION-RANGE"), verifies=["R-CG-RANGE"], parts=["POD-008"], how="Stack the spacers; calipers.",
          note="D-62 set 2 / 4 / 6 / 8 mm, colour-coded (white / yellow / green / blue)")
kit.claim("CL-D2-STATION-RANGE", "Pack station range inside the bay (forward minimum to aft reach)", calc="CALC-D2-STATION", output="range",
          unit="m", parts=["POD-008"], how="As CL-D2-AFT-REACH and CL-D2-PACK-X-FWD-MIN.")
kit.claim("CL-D2-OVERHANG-CLR", "Most aft pack face (no spacer) ahead of the recess end", calc="CALC-D2-CAD",
          output="overhang_clr", unit="m", limit=(">=", 0.0), parts=["POD-002", "POD-004"],
          how="Pack against the aft stop: the pack sits wholly on the tray, nothing over the spar slot.",
          note="D-62: aft face <= 0.0475, recess end 0.065")
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
kit.claim("CL-D2-CROSS-H", "Crossing height: foot bridge top to deck underside", calc="CALC-D2-CAD", output="cross_h", unit="m",
          limit=(">=", 0.026), parts=["POD-007", "POD-001"], how="Rule before the deck goes on.", note="F2 CR-F2-03 (c): 26 mm")
kit.claim("CL-D2-FWD-STOP-BOND", "Tray front piece + stop-T flange bond (forward stop), shear capacity", calc="CALC-D2-POD-BONDS",
          output="front_n", unit="N", limit=(">=", "CL-C1-PACK-CRASH-LOAD"), verifies=["R-PACK-RETENTION"], parts=["POD-002", "POD-001"],
          how="T-C3-STOP-PUSH on the built tray: 100 N on the stop; the tray does not peel.",
          note="D-69: the stop is a T, flange bonded under the floor (9 x 54 mm) and backed by the nose wall through the 1 mm epoxy line; "
               "peel at the root is C3's CL-C3-FEA-FWD-BED-PEEL (re-run on R6)")
kit.claim("CL-D2-AFT-STOP-BOND", "Tray rear piece bond, shear capacity (read-out only)", calc="CALC-D2-POD-BONDS",
          output="rear_n", unit="N", parts=["POD-002", "POD-001"],
          how="Covered by T-C3-STOP-PUSH (tray pieces bonded to board offcuts, CR-C3-20).",
          note="RETIRED as the aft-stop check (D-69, CR-C3-18): it does not see the root moment; the strut (CL-D2-STRUT-*) "
               "and C3's CL-C3-FEA-AFT-PROP-PEEL cover the stop. Kept as a read-out until C3 drops CL-C3-AFT-STOP-BOND")
kit.claim("CL-D2-STRUT-RIB-L", "Aft-stop strut rib free length (pad back face to foot-bridge front)", calc="CALC-D2-R6-GEOM", output="rib_l",
          unit="m", parts=["POD-007"], how="Rule on the printed handle; the pad sits on the stop back face with the bedding.",
          note="D-69 sized 14 mm at the D-59 stop (0.060); the D-62 stop at 0.0475 makes it 24.5 mm: C3 re-checks (CR-D2-25)")
kit.claim("CL-D2-STRUT-SKIN-CLR", "Strut rib underside to the wing skin", calc="CALC-D2-R6-GEOM", output="rib_skin", unit="m",
          limit=(">=", 0.002), parts=["POD-007", "POD-002"], how="Feeler under each rib with the handle bonded.")
kit.claim("CL-D2-BRACKET-AREA", "Handle-foot wall-bracket flange bonded to the side wall, per side", calc="CALC-D2-R6-GEOM", output="bracket",
          unit="m2", limit=(">=", 0.001), verifies=["R-STRUCT-MARGIN"], parts=["POD-007", "POD-001"],
          how="Measure the flange; witness the epoxy squeeze-out all round; T-C3-POD-PROOF + 200 N on the brackets.",
          note="C3 CR-C3-16: >= 1 000 mm2 per side (CL-C3-FEA-SADDLE-BOND-AREA 1 996 mm2 total)")
kit.claim("CL-D2-FWD-FLANGE-AREA", "Forward-stop T flange bonded under the floor", calc="CALC-D2-R6-GEOM", output="flange", unit="m2",
          parts=["POD-002", "POD-001"], how="Calipers on the flange; squeeze-out along both edges.",
          note="C3 CR-C3-15: 12 mm flange; 9 x 54 mm of it is under the floor (the other 3 mm is under the stop upright)")
kit.claim("CL-D2-PDB-PAD-M", "PDB plate flat-wise moment capacity (ribbed plate as a rigid pad)", calc="CALC-D2-PDB-PAD", output="m_cap",
          unit="N m", limit=(">=", "ASM-D2-UNPLUG-M"), verifies=["R-JOINT-STACK"], parts=["POD-002", "POD-001"],
          how="T-C6-INSERT on a bonded plate: record the plate-peel load; field rule thumb on the cradle while unplugging.",
          note="C6 CR-C6-27 option: plate 84 x 36.7 mm with a 1.2 x 3 mm rib along each boss row, 0.05 MPa flat-wise")
kit.claim("CL-D2-ANT-B-TIP-X", "Antenna B tube end x (ahead of the nose)", calc="CALC-D2-R6-GEOM", output="ant_b_x", unit="m",
          limit=(">=", -0.150), verifies=["R-TRANSPORT-FIT"], parts=["POD-001"], how="Rule from the wing LE to the tube end.",
          note="D7 CR-D7-23 at D-62: x >= -0.150 (10 mm ahead of the nose)")
kit.claim("CL-D2-LEFT-CH-CLEAR", "Pod bodies inside F1's left-channel volume ahead of the deck (x -0.063 ... -0.053, z 0.031 ... 0.070)",
          calc="CALC-D2-R6-GEOM", output="left_hits", unit="-", limit=("<=", 0), parts=["POD-002", "POD-003"],
          how="Look down the left channel with the hatch off: nothing of the pod above the plate in that span.",
          note="F1 CR-F1-26: held until F3 measures the CoreWing PDB")
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
          verifies=["R-AIRSPEED"], parts=["POD-006"], how="F3 cuts the boom to this length; check the tip at x -0.220 m with the boom seated.",
          note="D-62: the socket moved 10 mm forward with the nose; boom AVN-005 unchanged, tip -0.220")
kit.claim("CL-D2-PITOT-SOCKET", "Pitot socket depth", calc="CALC-D2-PITOT", output="socket_depth", unit="m", parts=["POD-006"],
          how="Depth gauge in the bore.")
kit.claim("CL-D2-MASS", "Pod subsystem mass (CAD estimate)", calc="CALC-D2-MASS", output="mass_g", unit="g",
          limit=("<=", P + "mass.allocation_g.pod"), verifies=["R-MASS-ALLOC"], parts=sorted(_MASSES),
          how="T-D2-WEIGH: weigh every pod part before bonding; update interfaces.json.",
          note="D-63 allocation 146 g (was 131, D-48): C3's fixes + the D-62 nose")

# ---------------------------------------------------------------- tests (planned)
kit.test("T-D2-WEIGH", "Weigh every pod part before assembly", verifies=["CL-D2-MASS"],
         procedure="0.1 g scale; each printed part, board piece and XPS block; record in subsystems/pod/parts.csv")
kit.test("T-D2-FIT", "Real pack fit", verifies=["CL-D2-BAY-L", "CL-D2-BAY-W", "CL-D2-BAY-H", "CL-D2-PACK-TRAVEL", "CL-D2-AFT-REACH",
                                                 "CL-D2-OVERHANG-CLR", "CL-D2-PACK-X-NOM", "CL-D2-PACK-X-LIGHT", "CL-D2-PACK-X-STACK",
                                                 "CL-D2-STACK-PLAY", "CL-D2-STRUT-SKIN-CLR", "CL-D2-LEFT-CH-CLEAR"],
         procedure="Both packs weighed and labelled with their spacer stack (A3's station on the day): in through the hatch, "
                   "strapped at their station, block cut for the pack and spreader fitted (no play), leads over the aft stop "
                   "to the AS150U park, hatch closes; centre mark measured from the wing LE; once on the crush stack with a 24.3 mm "
                   "block to record CL-D2-PACK-X-STACK and the play")
kit.test("T-D2-STRAP-PULL", "Strap loop pull test", verifies=["CL-D2-STRAP-CAP"],
         procedure="Spring scale, one installed loop on a tray offcut, 170 N for 10 s; no slip, no tear at the slot")
kit.test("T-D2-HANDLE-PULL", "Handle proof load on the built wing", verifies=["CL-D2-TIE-CAP"],
         procedure="Wing supported at the spar ends; 12 kg on the grip for 10 s; feet stay on the spar, ties do not slip")

if __name__ == "__main__":
    kit.write()
