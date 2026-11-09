"""Write team/C6/joint_stacks.json: C6's joint-stack, clamp and bond blocks per interface id, in the
interfaces/SCHEMA.md field names, for the edge owners (D3, D2, D6, E1, F1, F3, D5) to copy into their
interfaces.json. Numbers come from team/C6/claims.json (run joints.py first). Python 3 stdlib.

    python -I redesign/team/C6/joints.py && python -I redesign/team/C6/make_stacks.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}


def o(calc, key, nd=1, k=1.0):
    return round(OUT[calc]["outputs"][key] * k, nd)


ST = ["UR", "UL", "LR", "LL"]
SIDE = {"UR": "R", "LR": "R", "UL": "L", "LL": "L"}
HALF = {"UR": "RU", "LR": "RD", "UL": "LU", "LL": "LD"}
EPOXY = "30 min laminating epoxy + ~5 % colloidal silica (non-sag)"
FOAMEPOXY = "30 min laminating epoxy + glass microballoons (foam-safe; no CA, no solvent glue on XPS)"
PREP_P = "PETG/ASA sanded 120 grit, IPA wipe; CF sanded 120 grit to matte, IPA wipe, gloves"
CURE = "24 h at >= 18 degC before load; parts within 50 mm of a motor: + 4 h at 50 degC post-cure (CR-C6-04)"
stacks = {}

for i, s in enumerate(ST):
    stacks[f"E-FIN-{61 + i}"] = {"joint_stack": {
        "fastener": "M3x8 SHCS ISO 4762 (PRP-005)", "count": 4, "grade": "A2-70",
        "hole": "3.4 mm clearance through plate + canted pads (4.1-4.9 mm stack); drill to the measured motor pattern, "
                "no radial slots", "insert": "none (motor base tapped M3)",
        "engagement_mm": round(OUT["CALC-C6-MOTOR-SCREW"]["input_values"]["Le"] * 1e3, 2), "min_engagement_mm": 3.0,
        "max_engagement_mm": "probed hole depth - 0.5 (T-E1-MOTOR-RM)", "washer_nut": "none",
        "torque": "0.20 N m (4 N on a luggage scale 50 mm out on the key) + Loctite 243 on the screw tip only",
        "tool": "2.5 mm hex key + luggage scale", "access": "from behind the plate (+x), above the tube end",
        "install_order": 3, "removal_order": 1}}
    stacks[f"E-FIN-{5 + i:02d}"] = {"joint_stack": {
        "fastener": "M3x16 SHCS ISO 4762 (FIN-101)", "count": 1, "grade": "A2-70",
        "hole": "3.4 mm clearance through both pinch ears", "insert": "none",
        "engagement_mm": o("CALC-C6-PINCH", "protrusion_m", 1, 1e3),
        "min_engagement_mm": o("CALC-C6-PINCH", "protrusion_need_m", 1, 1e3),
        "washer_nut": "M3 nyloc ISO 10511 + 2 x M3 washer ISO 7089 (nyloc reused <= 3 times)",
        "torque": f"set by T-D3-SLIP (85-100 N at the can); expect ~{o('CALC-C6-PINCH', 'bolt_torque_nm', 2)} N m, "
                  "never above 0.4 N m; no threadlocker",
        "tool": "2.5 mm hex key + 5.5 mm spanner", "access": "outboard side, bolt along x",
        "install_order": 4, "removal_order": 2},
        "clamp": {"bore_mm": 22.3, "part_od_mm": 22.0, "slip_load_n": 94, "sized_by": "D3 (fuse), C6 (stack)"}}

stacks["E-POD-06"] = {"joint_stack": {
    "fastener": "M3x16 SHCS ISO 4762", "count": 1, "grade": "A2-70", "hole": "3.4 mm clearance across the boss",
    "insert": "none", "engagement_mm": "16 - grip - 0.5 (D2 measures)", "min_engagement_mm": 5.0,
    "washer_nut": "M3 nyloc + 1 washer: grip <= 10.5 mm", "torque": "snug, <= 0.3 N m; no threadlocker",
    "tool": "2.5 mm hex key + 5.5 mm spanner", "access": "from +y beside the grip", "install_order": 7,
    "removal_order": 1}}
stacks["E-AVN-01"] = {"joint_stack": {
    "fastener": "M3x10 SHCS ISO 4762", "count": 4, "grade": "A2-70",
    "hole": "board hole with soft-mount grommet", "insert": "M3 x 5.7 brass heat-set in POD-002, hole 4.0 x 6.5 mm",
    "engagement_mm": o("CALC-C6-INSERT", "engage_m", 1, 1e3), "min_engagement_mm": 4.5,
    "washer_nut": "M3 nylon washer under the head", "torque": "0.4 N m max, no threadlocker, paint-pen witness",
    "tool": "2.5 mm hex key", "access": "from above, hatch open", "install_order": 2, "removal_order": 3}}
stacks["E-PWR-03"] = {"joint_stack": {
    "fastener": "M3x10 SHCS ISO 4762 (only if the PDB is a PCB)", "count": 4, "grade": "A2-70",
    "hole": "PCB hole 3.2 mm", "insert": "M3 x 5.7 brass heat-set in POD-002, hole 4.0 x 6.5 mm",
    "engagement_mm": 4.6, "min_engagement_mm": 4.5,
    "washer_nut": "M3 nylon spacer 3 mm under the PCB + nylon washer 0.8 mm", "torque": "0.4 N m max",
    "tool": "2.5 mm hex key", "access": "from above, hatch open", "install_order": 1, "removal_order": 4}}
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
        "tool": "10 mm spanner (field tool, CR-C6-05)", "access": "front", "install_order": 2, "removal_order": 1}}


def bond(adh, area, prep, load, case, by="C6"):
    return {"bond": {"adhesive": adh, "area_mm2": area, "prep": prep, "cure": CURE, "load_n": load,
                     "load_case": case, "sized_by": by}}


tb = OUT["CALC-C6-TUBE-BONDS"]["outputs"]
for i, sd in enumerate(["R", "L"]):
    stacks[f"E-FIN-0{1 + i}"] = bond(EPOXY, round(tb["area_bore_mm2"]), PREP_P,
                                     f"10.4 N m torsion design; RF {tb['rf_tube_block']:.2f} (CL-C6-TUBE-BLOCK-RF)",
                                     "L4 corner")
    stacks[f"E-FIN-{49 + i}"] = bond(EPOXY, round(tb["area_spar_mm2"]), PREP_P,
                                     f"9.7 N m torsion design; RF {tb['rf_block_spar']:.2f} (CL-C6-BLOCK-SPAR-RF)",
                                     "L4 corner", "C4, C6")
    stacks[f"E-FIN-{51 + i}"] = bond(FOAMEPOXY, 6500, "foam dusted off", "secondary: spar carries the block",
                                     "-", "C4")
for i, s in enumerate(ST):
    stacks[f"E-FIN-{13 + i}"] = bond(EPOXY, round(tb["area_collar_mm2"]), PREP_P,
                                     f"11.4 N m design (C1); 20.1 N m on C4's torsion: RF {tb['rf_collar']:.2f} / "
                                     f"{tb['rf_collar_c4']:.2f} (CR-C6-03)", "L4 corner")
    stacks[f"E-FIN-{37 + i}"] = bond(EPOXY, 260, PREP_P, "178 N design; RF %.2f (CL-C6-BRACE-END-RF)"
                                     % OUT["CALC-C6-BRACE"]["outputs"]["rf_end"], "G2")
    stacks[f"E-FIN-{41 + i}"] = bond(EPOXY, 260, PREP_P, "178 N design", "G2")
    stacks[f"E-FIN-{57 + i}"] = bond(EPOXY, 320, PREP_P + "; spar face too",
                                     "178 N pull-off; RF %.2f (CL-C6-ANCHOR-PULL-RF)"
                                     % OUT["CALC-C6-BRACE"]["outputs"]["rf_anchor"], "G2")
    stacks[f"E-FIN-{53 + i}"] = bond(FOAMEPOXY, 6300, "foam dusted off; board edge scuffed",
                                     "RF %.2f at 0.125 MPa (CL-C6-FIN-ROOT-RF)"
                                     % OUT["CALC-C6-FOAM-BONDS"]["outputs"]["rf_root"], "L4 side load", "D3, C6")
    stacks[f"E-GER-0{1 + i}"] = bond(EPOXY, 1100, "board paper scuffed 220 grit, not torn; PETG 120 grit",
                                     "81 N design; RF %.2f at 0.10 MPa (CL-C6-FOOT-SHOE-RF)"
                                     % OUT["CALC-C6-FOAM-BONDS"]["outputs"]["rf_foot"], "L1", "D5, C6")
st = OUT["CALC-C6-STRIP"]["outputs"]
for i, h in enumerate(["RUO", "RUI", "RDO", "RDI", "LUO", "LUI", "LDO", "LDI"]):
    stacks[f"E-FIN-{21 + i}"] = bond(EPOXY, 2640, "strip 120 grit + IPA; paper scuffed 220 grit",
                                     f"shear flow {st['q_npm'] / 1e3:.1f} N/mm: RF {st['rf_face']:.2f} unpinned; "
                                     f"2 mm CF pins every 15 mm: RF {st['rf_pin']:.2f} (CR-C6-02)", "L4")
    stacks[f"E-FIN-{29 + i}"] = bond(EPOXY, 800, PREP_P,
                                     f"{st['F_design_n']:.0f} N design: RF {st['rf_anchor_now']:.2f} as drawn "
                                     f"(200 mm2), {st['rf_anchor_prop']:.2f} with the 40 mm two-face tail (CR-C6-01)",
                                     "L4")

doc = {"_note": "C6 joint stacks / clamp / bond blocks per edge id (interfaces/SCHEMA.md names). Generated by "
                "team/C6/make_stacks.py from team/C6/claims.json. Edge owners copy the block into their "
                "interfaces.json; C6 does not edit other folders. Status PROPOSED.",
       "edges": dict(sorted(stacks.items()))}
(HERE / "joint_stacks.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"joint_stacks.json: {len(stacks)} edges")
