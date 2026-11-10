"""Write team/C6/joint_stacks.json: C6's joint-stack, clamp and bond blocks per interface id, in the
interfaces/SCHEMA.md field names, for the edge owners (D3, D2, D6, E1, F1, F3, D5) to copy into their
interfaces.json. Numbers come from team/C6/claims.json (run joints.py first). Python 3 stdlib.
Revision C6-R3: C4 R3 loads read directly (collar max(C1, C4) + brace shear, strip 908 N per face, pins 64 N; CR-C4-23),
D3 R4 geometry (12 mm collar, CR-D3-17), D5 bond 1 350 mm2 (CR-D5-24), F1 power frame on PA66 M3x18 (CR-F1-20,
CR-A4-44), PA66 mast bolt as adopted by D2 (CR-C6-18), D-58 deviations; E-MEC-03/04 and E-PWR-05 withdrawn.

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
fb, pa, pw = out("CALC-C6-FOAM-BONDS"), out("CALC-C6-POD-ALLOW"), out("CALC-C6-PWR-FRAME")
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
    "engagement_mm": 6.0, "min_engagement_mm": 4.0,
    "washer_nut": "M3 PA66 hex nut (2.4 mm) fully on + 2 pitches; grip 10.0 mm as drawn by D2 (<= 11.0), "
                  "6.5 mm counterbore 4.5 deep on +y",
    "torque": "finger tight + 1/4 turn (<= 0.08 N m); the mast is the fuse",
    "tool": "2.5 mm hex key / screwdriver + fingers", "access": "from +y beside the grip", "install_order": 7,
    "removal_order": 1}}
stacks["E-AVN-01"] = {"retention": {
    "type": "CT-GEL-PAD (F3): 2 gel pads, 5 mm, on the scuffed tray; no screws",
    "crash": "secondary retention: one 3 mm tie or 10 mm hook-and-loop strap over the board with 1-2 mm slack so it "
             "does not short the isolation; carries the 10 N crash load if the pads release",
    "prep": "IPA on the tray and the board underside; pads applied at >= 18 degC, pressed 30 s",
    "inspection": "pre-flight: board does not lift with 1 finger; replace pads after a crash"}}
stacks["E-PWR-03"] = {"joint_stack": {
    "fastener": "M3x18 PA66 (nylon) screw; socket head preferred (2.5 mm key, luggage-scale torque), pan head PH1 "
                "accepted (CR-F1-20)", "count": 4,
    "grade": "PA66, natural (insulating beside the bus bars, non-magnetic: GPS 0.138 m)",
    "hole": "3.4 mm clearance in the 2 mm PETG deck (PWR-006) and in the 10 mm nylon spacer (OD 6 / ID 3.2)",
    "insert": "M3 x 5.7 brass heat-set in POD-002 boss, bore 4.0 x 6.5 mm, boss wall >= 1.6 mm (CR-C6-27)",
    "engagement_mm": round(pw["engage_m"] * 1e3, 1), "min_engagement_mm": 4.5,
    "max_engagement_mm": f"5.7 (insert length); tip clears the bore floor by {pw['tip_clear_m'] * 1e3:.1f} mm",
    "washer_nut": "0.5 mm nylon washer under the head; 2.0 mm deck; 10 mm nylon spacer on the boss (stack 12.5 mm)",
    "torque": f"0.08 N m max ({pw['scale_n_at_50mm']:.1f} N on a luggage scale 50 mm out on the key; PH1: fingertips "
              "only, stop when the washer stops turning); no threadlocker on nylon; paint-pen witness. 0.20 N m "
              f"would yield the PA66 shank (install RF {pw['rf_install_at_0p2']:.2f})",
    "tool": "2.5 mm hex key (or PH1) + luggage scale",
    "access": "from above (+z) through the hatch, before the power board is taped on",
    "install_order": 3, "removal_order": 3,
    "load": f"AS150U unplug 50 N at 18 mm, design x 2.16: {pw['tension_design_n']:.0f} N tension per screw "
            f"(RF {pw['rf_tension']:.2f} incl. {pw['preload_n']:.0f} N preload), {pw['shear_design_n']:.0f} N shear "
            f"on the clamp (friction RF {pw['rf_slip']:.2f}; after creep {pw['rf_slip_relaxed']:.2f}, then the "
            f"spacers bear as columns, RF {pw['rf_spacer']:.1f}); insert pull-out RF {pw['rf_pull']:.2f}. Field "
            "rule: thumb on the cradle while unplugging (load stays in the hand)",
    "inspection": "every 10 flights: witness marks unbroken, frame does not rock; re-snug to 0.08 N m"}}
for i, s in enumerate(ST):
    stacks[f"E-PRP-0{1 + i}"] = {"joint_stack": {
        "fastener": "M3x4 SHCS (with the adapter)", "count": 4, "grade": "as supplied",
        "hole": "adapter flange clearance", "insert": "none (bell tapped)", "engagement_mm": 2.5,
        "min_engagement_mm": 2.0, "deviation": "D-58 (a): 2.0 mm granted against the 1.0 d rule, RF 1.70 "
        "(CL-E1-ADAPTER-STRIP), conditional on T-E1-MOTOR-RM measuring >= 2.5 mm of bell thread", "washer_nut": "none", "torque": "0.5 N m + Loctite 243 (maker value wins)",
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
                                     f"{tb['area_collar_mm2'] / (3.14159265 * 22):.0f} mm collar: "
                                     f"{tb['T_collar_design_nm']:.1f} N m design from max(C1 section, C4 FE) = "
                                     f"{tb['T_collar_lim_nm']:.2f} N m limit + {tb['F_brace_design_n']:.0f} N brace "
                                     f"shear, {tb['tau_collar_mpa']:.2f} MPa, RF {tb['rf_collar']:.2f} (needs "
                                     f"{tb['L_collar_req_m'] * 1e3:.1f} mm; 16 mm fallback RF "
                                     f"{tb['rf_collar_alt']:.2f} if T-C6-LAP-PETG < 2.0 MPa)", "L4 / G2")
    stacks[f"E-FIN-{37 + i}"] = bond(EPOXY, 260, PREP_P, f"{br['F_design_n']:.0f} N design; RF {br['rf_end']:.2f} "
                                     "(CL-C6-BRACE-END-RF)", "G2")
    stacks[f"E-FIN-{41 + i}"] = bond(EPOXY, 260, PREP_P, f"{br['F_design_n']:.0f} N design; RF {br['rf_end']:.2f}",
                                     "G2")
    stacks[f"E-FIN-{57 + i}"] = bond(EPOXY, round(br["anchor_area_mm2"]), PREP_P + "; spar face too",
                                     f"{br['F_design_n']:.0f} N pull-off on the 90 deg saddle contact; RF "
                                     f"{br['rf_anchor']:.2f} (CL-C6-ANCHOR-PULL-RF)", "G2")
    stacks[f"E-FIN-{53 + i}"] = bond(FOAMEPOXY, 6300, "foam dusted off; board edges scuffed; fillet leg 15 mm "
                                     "both faces (D-48), stopped over the link notch on the lower roots",
                                     f"12 mm leg RF {fb['rf_root']:.2f}, 15 mm leg RF {fb['rf_root_prop']:.2f} at "
                                     f"0.125 MPa (needs {fb['leg_req_m'] * 1e3:.1f} mm; CL-C6-FIN-ROOT-RF-PROP)",
                                     "L4 side load", "D3, C6")
    stacks[f"E-GER-0{1 + i}"] = bond(EPOXY, round(fb["foot_area_mm2"]),
                                     "board paper scuffed 220 grit, not torn; cut foam edge and CF strip ends IPA; "
                                     "PETG 120 grit", f"{fb['foot_design_n']:.1f} N printed/bonded design; RF "
                                     f"{fb['rf_foot']:.2f} at 0.10 MPa (CL-C6-FOOT-SHOE-RF = CL-D5-BOND-SF)",
                                     "L1 with the C5 biased upper foot", "D5, C6")
    for k, f in enumerate(("O", "I")):
        stacks[f"E-FIN-{21 + 2 * i + k}"] = bond(
            EPOXY, 2640, "strip 120 grit + IPA; paper scuffed 220 grit; pins bonded flush",
            f"C4 FE shear flow {st['q_design_npm'] / 1e3:.2f} N/mm design: paper face alone RF {st['rf_face']:.2f}, "
            f"so 2 mm CF pins through strip-board-board-strip ({st['pin_len_m'] * 1e3:.1f} mm): at 15 mm pitch "
            f"{st['pin_load_n']:.0f} N per pin, RF {st['rf_pin']:.2f}; at 12 mm pitch (CR-C6-25) "
            f"{st['pin_load_prop_n']:.0f} N, RF {st['rf_pin_prop']:.2f}, {st['pins_per_strip_pair_prop']} per pair, "
            "first half a pitch aft of the tail", "L4")
        stacks[f"E-FIN-{29 + 2 * i + k}"] = bond(
            EPOXY, round(2 * 10 * st["embed_m"] * 1e3), PREP_P,
            f"{st['F_design_n']:.0f} N design per strip (CL-C6-STRIP-ANCHOR-F) over 2 faces x 10 x "
            f"{st['embed_m'] * 1e3:.1f} mm: RF {st['rf_anchor']:.2f} (needs {st['L_req_m'] * 1e3:.1f} mm); tail net "
            f"section {st['tail_net_mpa']:.1f} MPa, RF {st['rf_tail_net']:.2f}", "L4")

stacks["E-POD-01"] = bond(FOAMEPOXY, 10014, "tape skin off under the pod; foam and board faces scuffed, dust off",
                          f"C3 interaction R at C6-confirmed allowables (XPS 0.125 MPa tension, 0.10 MPa shear): RF "
                          f"{pa['rf_pod_design']:.2f} design, {pa['rf_pod_crash']:.2f} crash", "L1; 12.75 g crash",
                          "C3, C6 (allowables)")
stacks["E-POD-02"] = bond("30 min epoxy", 13505, "PETG underside 120 grit; board face scuffed 220 grit",
                          f"strap pull flat-wise {pa['board_flat_mpa'] / pa['rf_tray']:.4f} MPa vs {pa['board_flat_mpa']:.2f} MPa: RF {pa['rf_tray']:.2f}; the floor-to-"
                          f"wall corner inside POD-001 under the front strap needs a 6 mm microballoon fillet "
                          f"(RF {pa['rf_floor']:.2f} -> {pa['rf_floor_prop']:.2f}, CR-C6-17)", "C1 crash", "C3, C6")

for i in range(3):
    stacks[f"E-TRN-{13 + i}"] = {"ground_joint": True, "joint_stack": {
        "fastener": "M3x16 SHCS ISO 4762", "count": 2, "grade": "A2-70",
        "hole": "3.4 mm through handle strap, 4 mm Coroplast wall and 3 mm ply backing strip",
        "insert": "none", "engagement_mm": "16 - grip; grip <= 11.0 mm", "min_engagement_mm": 5.0,
        "washer_nut": "M3 x 12 mm fender washer outside; M3 nyloc on the 140 x 30 x 3 mm ply strip inside (TRN-105)",
        "torque": "snug, wall not crushed", "tool": "2.5 mm hex key + 5.5 mm spanner", "access": "nut inside, lid off",
        "install_order": 12, "removal_order": 9,
        "load": "57-59 N per bolt (CL-D7-HANDLE-BOLT-F); confirmed by C6 (CR-D7-10): the ply strip spreads it to "
                "27 kPa on the Coroplast; min engagement = nyloc 4.0 + 2 pitches (D-41), not 3.0"}}

WITHDRAWN = {"E-MEC-03": "servo held in MEC-008 ear slots, no screws (D6 CR-D6-11a); the cover screws are E-MEC-35/36",
             "E-MEC-04": "same as E-MEC-03",
             "E-PWR-05": "bus board on foam tape (F1), retention block owned by power; no C6 stack (CR-A4-44b)"}

doc = {"_note": "C6 joint stacks / clamp / bond / retention blocks per edge id (interfaces/SCHEMA.md names). Generated "
                "by team/C6/make_stacks.py from team/C6/claims.json, revision C6-R3 (params A1-R4). Edge owners copy "
                "the block into their interfaces.json; C6 does not edit other folders. Status PROPOSED.",
       "withdrawn": WITHDRAWN, "edges": dict(sorted(stacks.items()))}
(HERE / "joint_stacks.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"joint_stacks.json: {len(stacks)} edges")
