"""Write team/C6/joint_stacks.json: C6's joint-stack, clamp and bond blocks per interface id, in the
interfaces/SCHEMA.md field names, for the edge owners (D3, D2, D6, E1, F1, F3, D5) to copy into their
interfaces.json. Numbers come from team/C6/claims.json (run joints.py first). Python 3 stdlib.
Revision C6-R2: R3 geometry merged (collar 16 mm, 40 mm two-face tail, pinned strips, canted 4.5 mm motor plate,
7 deg side load), FC on gel pads, PDB on inserts, GPS mast bolt non-magnetic.

    python -I redesign/team/C6/joints.py && python -I redesign/team/C6/make_stacks.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
NODES = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}


def out(calc):
    return NODES[calc]["outputs"]


def o(calc, key, nd=1, k=1.0):
    return round(out(calc)[key] * k, nd)


ST = ["UR", "UL", "LR", "LL"]
HALF_D3 = {"UR": "RU", "LR": "RD", "UL": "LU", "LL": "LD"}            # D3's current edge part ids (pre D-26 rename)
EPOXY = "30 min laminating epoxy + ~5 % colloidal silica (non-sag)"
FOAMEPOXY = "30 min laminating epoxy + glass microballoons (foam-safe; no CA, no solvent glue on XPS)"
PREP_P = "PETG/ASA sanded 120 grit, IPA wipe; CF sanded 120 grit to matte, IPA wipe, gloves"
CURE = "24 h at >= 18 degC before load; parts within 50 mm of a motor: + 4 h at 50 degC post-cure (CR-C6-04)"
ms, cs, ms_side = out("CALC-C6-MOTOR-SCREW"), out("CALC-C6-CANT-SEAT"), out("CALC-C6-MOUNT-SIDE")
tb, st, br = out("CALC-C6-TUBE-BONDS"), out("CALC-C6-STRIP"), out("CALC-C6-BRACE")
fb, pa = out("CALC-C6-FOAM-BONDS"), out("CALC-C6-POD-ALLOW")
stacks = {}

for i, s in enumerate(ST):
    stacks[f"E-FIN-{61 + i}"] = {"joint_stack": {
        "fastener": "M3x8 SHCS ISO 4762 (PRP-005)", "count": 4, "grade": "A2-70",
        "hole": "3.4 mm drilled square to the canted 4.5 mm plate face (holes parallel to the motor axis) on the "
                "measured motor pattern, motor as template; no radial slots",
        "insert": "none (motor base tapped M3)",
        "engagement_mm": round(cs["engage_m"] * 1e3, 2), "min_engagement_mm": 3.0,
        "max_engagement_mm": "probed hole depth - 0.5 (T-E1-MOTOR-RM)", "washer_nut": "none (head bears flat on "
                                                                                       "the canted back face)",
        "torque": "0.20 N m (4 N on a luggage scale 50 mm out on the key) + Loctite 243 on the screw tip only",
        "tool": "2.5 mm hex key + luggage scale", "access": "from behind the plate (+x), above the tube end",
        "install_order": 3, "removal_order": 1,
        "load": f"{ms['tension_n']:.0f} N design per screw incl. the 7 deg side moment "
                f"{ms['M_side_ult_nm']:.2f} N m ult; preload {ms['preload_n']:.0f} N (RF {ms['rf_sep']:.2f}); "
                f"head 22.7 MPa on ASA (RF {ms['rf_head']:.2f})"}}
    stacks[f"E-FIN-{5 + i:02d}"] = {"joint_stack": {
        "fastener": "M3x16 SHCS ISO 4762 (FIN-101)", "count": 1, "grade": "A2-70",
        "hole": "3.4 mm clearance through both pinch ears", "insert": "none",
        "engagement_mm": o("CALC-C6-PINCH", "protrusion_m", 1, 1e3),
        "min_engagement_mm": o("CALC-C6-PINCH", "protrusion_need_m", 1, 1e3),
        "washer_nut": "M3 nyloc ISO 10511 + 2 x M3 washer ISO 7089 (nyloc reused <= 3 times)",
        "torque": f"set by T-D3-SLIP (85-100 N at the can); expect ~{o('CALC-C6-PINCH', 'bolt_torque_nm', 2)} N m, "
                  "never above 0.4 N m; no threadlocker",
        "tool": "2.5 mm hex key + 5.5 mm spanner", "access": "outboard side, bolt along x",
        "install_order": 4, "removal_order": 2,
        "load": f"7 deg side force {ms_side['side_lim_n']:.2f} N limit: tube torsion {ms_side['mz_lim_nm']:.3f} N m "
                f"(slip RF {ms_side['rf_slip_torsion']:.1f}), along the tube {ms_side['fax_lim_n']:.2f} N (RF "
                f"{ms_side['rf_slip_axial']:.0f}); prop-nut 3.23 N m design, bearing RF "
                f"{o('CALC-C6-PINCH', 'rf_rock', 2)}"},
        "clamp": {"bore_mm": 22.3, "part_od_mm": 22.0, "slip_load_n": 94, "sized_by": "D3 (fuse), C6 (stack)"}}

stacks["E-POD-06"] = {"joint_stack": {
    "fastener": "M3x16 PA66 (nylon) cheese-head screw: non-magnetic near the compass (CR-F3-03)", "count": 1,
    "grade": "PA66", "hole": "3.4 mm clearance across the socket boss and the mast base", "insert": "none",
    "engagement_mm": "16 - grip (D2 measures)", "min_engagement_mm": 4.0,
    "washer_nut": "M3 PA66 hex nut fully on + 2 pitches: grip <= 11.0 mm", "torque": "finger tight + 1/4 turn "
                                                                                       "(~0.1 N m); the mast is the fuse",
    "tool": "2.5 mm hex key / screwdriver + fingers", "access": "from +y beside the grip", "install_order": 7,
    "removal_order": 1}}
stacks["E-AVN-01"] = {"retention": {
    "type": "CT-GEL-PAD (F3): 2 gel pads, 5 mm, on the scuffed tray; no screws",
    "crash": "secondary retention: one 3 mm tie or 10 mm hook-and-loop strap over the board with 1-2 mm slack so it "
             "does not short the isolation; carries the 10 N crash load if the pads release",
    "prep": "IPA on the tray and the board underside; pads applied at >= 18 degC, pressed 30 s",
    "inspection": "pre-flight: board does not lift with 1 finger; replace pads after a crash"}}
stacks["E-PWR-03"] = {"joint_stack": {
    "fastener": "M3x10 SHCS ISO 4762 (bus PDB, F1)", "count": 4, "grade": "A2-70 (>= 0.10 m from the GPS mast, F1)",
    "hole": "PCB hole 3.2 mm", "insert": "M3 x 5.7 brass heat-set in POD-002, hole 4.0 x 6.5 mm, boss wall >= 1.6 mm",
    "engagement_mm": o("CALC-C6-INSERT", "engage_m", 1, 1e3), "min_engagement_mm": 4.5,
    "washer_nut": "2 mm nylon spacer under the PCB + 0.8 mm nylon washer under the head (stack 4.4 mm)",
    "torque": "0.4 N m max, no threadlocker, paint-pen witness", "tool": "2.5 mm hex key",
    "access": "from above, hatch open", "install_order": 1, "removal_order": 4}}
for i, s in enumerate(["L", "R"]):
    stacks[f"E-MEC-0{3 + i}"] = {"joint_stack": {
        "fastener": "servo's own M2 self-tapping screws", "count": 2, "grade": "as supplied",
        "hole": "1.6 mm pilot in printed (or ply) ear bosses of MEC-008, >= 5 mm deep; never into foam",
        "insert": "none", "engagement_mm": 4.0, "min_engagement_mm": 4.0, "washer_nut": "servo rubber grommets",
        "torque": "snug, head seated; no threadlocker", "tool": "Phillips #1", "access": "pocket opening, cover off",
        "install_order": 2, "removal_order": 1}}
for i, s in enumerate(ST):
    stacks[f"E-PRP-0{1 + i}"] = {"joint_stack": {
        "fastener": "M3x4 SHCS (with the adapter)", "count": 4, "grade": "as supplied",
        "hole": "adapter flange clearance", "insert": "none (bell tapped)", "engagement_mm": "E1 measures",
        "min_engagement_mm": 3.0, "washer_nut": "none", "torque": "0.5 N m + Loctite 243 (maker value wins)",
        "tool": "2.5 mm hex key", "access": "front of the bell, prop off", "install_order": 1, "removal_order": 9}}
    stacks[f"E-PRP-0{5 + i}"] = {"field_joint": True, "joint_stack": {
        "fastener": "M6x1 nut ISO 4032 on the adapter post (LH thread on CW motors)", "count": 1, "grade": "8",
        "hole": "prop hub 1/4 in on the LPAR06E ring", "insert": "none",
        "engagement_mm": "post - hub - washer, measured (E1: 0.1 mm past the nut)", "min_engagement_mm": 5.2,
        "washer_nut": "M6 washer 1.0 mm", "torque": "1.5 N m, bell held by hand (ASM-C1-PROP-NUT-TORQUE)",
        "tool": "10 mm spanner (the single field tool, D-40)", "access": "front", "install_order": 2,
        "removal_order": 1}}


def bond(adh, area, prep, load, case, by="C6"):
    return {"bond": {"adhesive": adh, "area_mm2": area, "prep": prep, "cure": CURE, "load_n": load,
                     "load_case": case, "sized_by": by}}


for i, sd in enumerate(["R", "L"]):
    stacks[f"E-FIN-0{1 + i}"] = bond(EPOXY, round(tb["area_bore_mm2"]), PREP_P,
                                     f"{tb['T_tb_design_nm']:.1f} N m torsion design; RF {tb['rf_tube_block']:.2f} "
                                     "(CL-C6-TUBE-BLOCK-RF)", "L4 corner")
    stacks[f"E-FIN-{49 + i}"] = bond(EPOXY, round(tb["area_spar_mm2"]), PREP_P,
                                     f"{tb['T_bs_design_nm']:.1f} N m torsion design; RF {tb['rf_block_spar']:.2f} "
                                     "(CL-C6-BLOCK-SPAR-RF)", "L4 corner", "C4, C6")
    stacks[f"E-FIN-{51 + i}"] = bond(FOAMEPOXY, 6500, "foam dusted off", "secondary: spar carries the block",
                                     "-", "C4")
for i, s in enumerate(ST):
    h = HALF_D3[s]
    stacks[f"E-FIN-{13 + i}"] = bond(EPOXY, round(tb["area_collar_mm2"]), PREP_P,
                                     f"16 mm collar: {tb['T_c4_design_nm']:.1f} N m (C4 9.3 N m limit) + "
                                     f"{tb['F_brace_design_n']:.0f} N brace shear, {tb['tau_collar_c4_mpa']:.2f} MPa, "
                                     f"RF {tb['rf_collar_c4']:.2f}; C1 torsion RF {tb['rf_collar']:.2f}", "L4 / G2")
    stacks[f"E-FIN-{37 + i}"] = bond(EPOXY, 260, PREP_P, f"{br['F_design_n']:.0f} N design; RF {br['rf_end']:.2f} "
                                     "(CL-C6-BRACE-END-RF)", "G2")
    stacks[f"E-FIN-{41 + i}"] = bond(EPOXY, 260, PREP_P, f"{br['F_design_n']:.0f} N design; RF {br['rf_end']:.2f}",
                                     "G2")
    stacks[f"E-FIN-{57 + i}"] = bond(EPOXY, round(br["anchor_area_mm2"]), PREP_P + "; spar face too",
                                     f"{br['F_design_n']:.0f} N pull-off on the 90 deg saddle contact; RF "
                                     f"{br['rf_anchor']:.2f} (CL-C6-ANCHOR-PULL-RF)", "G2")
    stacks[f"E-FIN-{53 + i}"] = bond(FOAMEPOXY, 6300, "foam dusted off; board edges scuffed",
                                     f"RF {fb['rf_root']:.2f} at 0.125 MPa (CL-C6-FIN-ROOT-RF)", "L4 side load",
                                     "D3, C6")
    stacks[f"E-GER-0{1 + i}"] = bond(EPOXY, 1100, "board paper scuffed 220 grit, not torn; PETG 120 grit",
                                     f"81 N design; RF {fb['rf_foot']:.2f} at 0.10 MPa (CL-C6-FOOT-SHOE-RF)", "L1",
                                     "D5, C6")
    for k, f in enumerate(("O", "I")):
        stacks[f"E-FIN-{21 + 2 * i + k}"] = bond(
            EPOXY, 2640, "strip 120 grit + IPA; paper scuffed 220 grit; pins bonded flush",
            f"shear flow {st['q_npm'] / 1e3:.2f} N/mm: paper face alone RF {st['rf_face']:.2f}, so 2 mm CF pins "
            f"every 15 mm through strip-board-board-strip ({st['pin_len_m'] * 1e3:.1f} mm, "
            f"{st['pins_per_strip_pair']} per pair, first half a pitch aft of the tail): {st['pin_load_n']:.0f} N per "
            f"pin, RF {st['rf_pin']:.2f} (CL-C6-STRIP-PIN-RF)", "L4")
        stacks[f"E-FIN-{29 + 2 * i + k}"] = bond(
            EPOXY, 800, PREP_P, f"{st['F_design_n']:.0f} N design over 2 faces x 10 x 40 mm: RF {st['rf_anchor']:.2f} "
            f"(needs {st['L_req_m'] * 1e3:.1f} mm, CL-C6-STRIP-EMBED-REQ)", "L4")

stacks["E-POD-01"] = bond(FOAMEPOXY, 10014, "tape skin off under the pod; foam and board faces scuffed, dust off",
                          f"C3 interaction R at C6-confirmed allowables (XPS 0.125 MPa tension, 0.10 MPa shear): RF "
                          f"{pa['rf_pod_design']:.2f} design, {pa['rf_pod_crash']:.2f} crash", "L1; 12.75 g crash",
                          "C3, C6 (allowables)")
stacks["E-POD-02"] = bond("30 min epoxy", 13505, "PETG underside 120 grit; board face scuffed 220 grit",
                          f"strap pull flat-wise {pa['board_flat_mpa'] / pa['rf_tray']:.4f} MPa vs {pa['board_flat_mpa']:.2f} MPa: RF {pa['rf_tray']:.2f}; the floor-to-"
                          f"wall corner inside POD-001 under the front strap needs a 6 mm microballoon fillet "
                          f"(RF {pa['rf_floor']:.2f} -> {pa['rf_floor_prop']:.2f}, CR-C6-17)", "C1 crash", "C3, C6")

doc = {"_note": "C6 joint stacks / clamp / bond / retention blocks per edge id (interfaces/SCHEMA.md names). Generated "
                "by team/C6/make_stacks.py from team/C6/claims.json, revision C6-R2 (params A1-R3). Edge owners copy "
                "the block into their interfaces.json; C6 does not edit other folders. Status PROPOSED.",
       "edges": dict(sorted(stacks.items()))}
(HERE / "joint_stacks.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"joint_stacks.json: {len(stacks)} edges")
