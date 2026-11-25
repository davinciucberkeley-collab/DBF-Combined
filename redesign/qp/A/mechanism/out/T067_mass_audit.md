# T-067 printed-part mass audit, concept A (2026-11-19)

Task T-067 (R-CAD-05, R-OPT-05). Nothing committed. No CAD source, docs/, CHANGE-LOG, ledger, MASS-GATE.md or `structures/*` edited; the proposed code change (s7) is a diff only, not applied. No simulation run.
**Analysis category: geometry arithmetic** (CAD solid volume by voxelisation of the stub-built CAD shapes) **plus an illustrative / EST print-basis model** (shell + infill). It is not interference, kinematics, rigid-body dynamics, FEA, CFD or flight dynamics.

## 1. Acceptance test (restated from the brief)

(1) For EVERY printed part in the concept A CAD: CAD solid volume vs the listed mass. (2) A print basis per part (perimeters, top/bottom layers, infill, density; all cited, EST where needed) chosen by load, mass computed from volume with the formula shown. (3) Table Part | listed g | CAD solid g | basis | computed g | delta g | source. (4) New CAD basic mass; MASS-GATE s13 flat rule (basic x 1.1174 + 0.032 x 1,470 g) and the itemised rule vs the 1,470 g gate. (5) Proposed code change as a diff, not applied.

## 2. Outcome in one paragraph

Of 42 printed parts (all `PETG (printed)` entries of `a_model.PARTS` except the lead-dominated balance WNG-007), the CAD solid volume x 1.27 g/cm3 is **299.3 g against 112.1 g listed (+187.2 g)**. Parts whose mass is already computed from the drawn volume (bay cover, raceways, conduits, horn, keeper, lens caps, hub) agree with the CAD within 0.1-8 %. The hard-coded entries do not: **FIN-005 1.0 vs 18.4 g, FIN-003 3.2 vs 23.5 g, GER-001 1.4 vs 5.3 g (the F10 numbers, reproduced exactly) and, new here, motor cup 4.3 vs 12.0 g, strut clamp 1.5 vs 9.2 g, bridge saddle 2.0 vs 12.0 g, pack tray 3.8 vs 29.4 g, avionics plate 8.0 vs 23.9 g.** With the print basis in s3 (volume x shell + infill) the printed set is **249.0 g (adopted 250.2 g)**, **+138.1 g** over the listed set. CAD basic mass 1,274.3 g becomes **1,412.4 g**; the flat rule gives **1,625.2 g, 155.2 g over the 1,470 g gate** (itemised 1,633.0 g). With a lighter basis (s5) the excess is still **111.9 g** (flat). The T-068 s11 range of +20 / +45 / +91 g was for three parts; the full printed set is larger. The cause is geometry (solid blocks, plates and sockets drawn in the CAD), not the choice of infill: no basis tried gets near the gate.

## 3. Method and basis

**CAD volume.** `t067_data/t067_mass_audit.py` builds the CAD with `build_a.build_all.build(StubBackend())` (the route of `sitl/cad_mass.py` and `structures/landing_path_a.py volumes()`), takes every body shape of each part (prism, revolve, loft, closed mesh) in the part's own frame, voxelises at pitch h (0.25 mm; hub 0.5 mm, see limits), unions the bodies and subtracts every cut of the part (including cuts placed by another part's seat matrix). Solid mass = N_solid x h^3 x rho. Check: FIN-005 18.39, FIN-003 23.54, GER-001 5.28 g reproduce `T064r_landing.md` s4 (same method) to 0.01 g.

**Density.** rho = 1.27 g/cm3 PETG: Prusament PETG technical data sheet v1.1, 16 Feb 2022, "Density 1.27 g/cm3, ISO 1183" (found by web search 2026-11-19; the PDF itself was not opened here, so treat as search-reported); equals `RHO_PETG` in `amodel/wing.py` (the value every existing CALC part uses). Other PETG brands report 1.27-1.29 (same search): EST +-2 %.

**Shell + infill model (formula).** For each part the print axis z is the grid axis with the smallest occupied extent (part lying flat; EST, orientation not specified anywhere in the repo: "—"). A voxel is *shell* if it is within w = n_per x 0.42 mm of a void in its layer (per-layer 2-D Euclidean distance transform) or within t_tb = n_tb x 0.2 mm of a void along z (binary erosion with a z line); every other solid voxel is *core*.
`m = rho x h^3 x ( N_shell + f_infill x N_core )`. Walls thinner than 2 w (0.6 mm covers, raceways) come out fully solid by construction, as a slicer prints them (EST; a 0.6 mm wall is 1 perimeter plus gap fill).

**Slicer defaults (reference, not a source for the loads).** Bambu Studio 0.20 mm Standard as reported by a user on forum.bambulab.com (search result 2026-11-19, unofficial): 2 wall loops, 5 top / 3 bottom layers, 15 % infill. Line width 0.42 mm for a 0.4 mm nozzle (Bambu wiki "line width" page, found by search 2026-11-19, not opened): EST. The repo's own print list already assumes 0.2 mm layer, 0.4 mm nozzle (EST; `redesign/qp/A/mechanism` print-list generator, `Print list (PETG, 0.2 mm layer, 0.4 mm nozzle EST)`). The project has no coupon data: every basis below is **EST**.

| Class | Parts (by load) | Perimeters | Top / bottom layers | Infill | Reason (EST) |
|---|---|---|---|---|---|
| S structural joint | fin root block FIN-003, rib saddle FIN-005, foot shoe GER-001 (landing loads, T064r path checks RF < 1), hub CGE-001, motor cups CGE-003 (thrust, torque), bridge saddle CGE-006, strut clamps CGE-007, spar plugs WNG-003/4/5, horn MEC-004, keeper MEC-008 | 4 (1.68 mm) | 5 / 5 (1.0 mm) | 40 % | bonded / bolted load path, KP 2.156 printed (T064r) |
| M moderate | pack tray CGE-008, avionics plate AVN-001, damper WNG-009/010 | 3 (1.26 mm) | 4 / 4 (0.8 mm) | 25 % | carries masses at 1-2 g, not the primary load path |
| C cover / light | bay cover AVN-008, raceway HRN-003, conduit HRN-004, lens caps WNG-008 | 2 (0.84 mm) | 3 / 3 (0.6 mm) | 10 % | fairings and wire covers |
| Lean (sensitivity only, s5) | S -> 3 perimeters / 4 layers / 25 %; M -> 2 / 3 / 15 %; C unchanged | | | | lower bound of what a normal slicer would accept for these classes, EST |

## 4. Table (per part; all 42 parts in `t067_data/t067_merged.json`)

Source for every row: listed g = `a_model.PARTS` (hard-coded in `amodel/wing.py` l.517-549 or `amodel/electrical.py` l.715-743, or a CALC function of the drawn volume); CAD solid g = `t067_mass_audit.py` voxel volume x 1.27; computed g = shell + infill model, s3. Delta = adopted minus listed (WNG-009 keeps its listed 2.0 g: it includes 12,500 cSt silicone fluid and strips that are not in the CAD, fluid mass "—"; its printed part alone is 1.40 g solid). Voxel pitch 0.25 mm except the hub (0.5 mm). "h-sens" = |computed(0.25) - computed(0.5)|.

| Part (xN) | listed g each | CAD solid g each | basis | computed g each | delta g each | delta g total | h-sens g |
|---|---|---|---|---|---|---|---|
| FIN-003 root block (x2) | 3.20 | 23.54 | S | 18.90 | +15.70 | +31.40 | 0.07 |
| FIN-005 rib saddle (x2) | 1.00 | 18.39 | S | 14.39 | +13.39 | +26.78 | 0.04 |
| GER-001 foot shoe (x4) | 1.40 | 5.28 | S | 4.55 | +3.15 | +12.60 | 0.01 |
| CGE-001 hub (x1) | 18.00 | 17.62 | S | 15.82 | -2.18 | -2.18 | 0.5 mm only |
| CGE-003 motor cup (x4) | 4.30 | 12.04 | S | 9.51 | +5.21 | +20.84 | 0.02 |
| CGE-006 bridge saddle (x1) | 2.00 | 12.04 | S | 9.67 | +7.67 | +7.67 | 0.02 |
| CGE-007 strut clamp (x2) | 1.50 | 9.17 | S | 6.58 | +5.08 | +10.16 | 0.04 |
| CGE-008 pack tray (x1) | 3.80 | 29.41 | M | 25.80 | +22.00 | +22.00 | 3.09 |
| AVN-001 avionics plate (x1) | 8.00 | 23.88 | M | 17.91 | +9.91 | +9.91 | 1.57 |
| AVN-008 bay cover (x1) | 10.40 | 9.59 | C | 9.59 | -0.81 | -0.81 | 0.79 |
| HRN-003 raceway (x2) | 1.71 | 1.43 | C | 1.43 | -0.28 | -0.56 | 0.00 |
| HRN-004 conduit (UR/UL/LR/LL) | 1.05 / 0.77 / 0.97 / 1.25 | 0.98 / 0.72 / 0.90 / 1.22 | C | same (solid) | -0.07 / -0.05 / -0.07 / -0.03 | -0.22 | 0.04-0.12 |
| WNG-003/4/5 spar plug (x5) | 1.20 | 1.60 | S | 1.42 | +0.22 | +1.10 | 0.00 |
| WNG-008 lens cap (x4: RU 3.69, RL 3.74 solid) | 3.80 | 3.69 / 3.74 | C | 3.67 / 3.69 | -0.13 / -0.11 | -0.48 | 0.03-0.08 |
| WNG-009 damper stator (x2) | 2.00 | 1.40 (printed only) | M | 1.40 | 0 (listed kept) | 0 | 0.03 |
| WNG-010 damper rotor (x2) | 0.50 | 0.47 | M | 0.47 | -0.03 | -0.06 | 0.00 |
| MEC-004 horn (x2) | 0.95 | 0.95 | S | 0.95 | 0.00 | 0.00 | 0.00 |
| MEC-008 keeper (x2) | 0.08 | 0.07 | S | 0.07 | -0.01 | -0.02 | 0.01 |
| **Total (42 parts)** | **112.12** | **299.31** | | **249.00** (adopted 250.19) | | **+138.07** | |

Not printed, listed for completeness: GER-002 foot pad (x4) is EVA/PE foam, listed 0.7 g each, CAD volume 5.40 cm3 each (T064r s4) which implies 0.13 g/cm3 (unsourced, "—"); WNG-007 balance is 12.8 g lead + 0.5 g PETG/CF tabs (lead dominated, kept listed).

Sanity checks on the largest gaps (CAD shapes read from `build_a`):
- Pack tray CGE-008: the CAD draws a 2.0 mm plate 66 x 109 mm (14.5 cm3 = 18.4 g solid) plus two end walls and two lips. The listed 3.8 g ("1.5 mm floor with ribs", QP-4 FIXES) is less than a plain 0.6 mm solid plate of the same area (66 x 109 x 0.6 mm = 4.3 cm3 = 5.5 g). The listed number cannot be printed from this geometry; no ribs or windows are drawn in the CAD.
- Avionics plate AVN-001: the CAD draws the plate (24.7 cm3 before cuts) with 4 lightening windows and 4 nut pockets (QP-4 comment "8 g: 4 lightening windows, now drawn") but the drawn part is 23.9 g solid (17.9 g at 25 % infill), not 8 g.
- Motor cup CGE-003: 12.0 g solid (sleeve 4.9 cm3 + plate 5.3 cm3 + collar and fillets, minus bores), not 4.3 g (QP-4 FIXES 5 -> 4 g, EST, never reconciled with the drawn sleeve).
- Bay cover AVN-008 10.40 g listed vs 9.59 g voxel: the listed value sums boxes and ignores overlaps (`cover_mass_g()`), voxel pitch 0.25 mm on 0.6 mm walls is +-10 %, so treat 0.8 g as inside the discretisation (h-sens 0.79 g).

## 5. New CAD basic mass and mass-gate predictions

Reference now (task brief; T068 s11): CAD basic **1,274.3 g**, flat rule 1,470.94 g, margin -0.94 g; itemised (basic + growth 145.0 + overrun 48.0) 1,467.3 g, margin +2.7 g. Printed set listed 112.12 g.

Flat rule (MASS-GATE s13): `pred = basic x 1.1174 + 0.032 x 1,470 g` (coefficient 1.1174 as stated in MASS-GATE s13; not re-derived here). Itemised rule (`mission_gate_a.py`): `pred = basic + growth + 48 g overrun`, growth 145.0 g (current) plus 20 % (EST maturity) or 10 % (CALC maturity) of the added printed mass; the growth factor is not re-based here (ASM-A3-MGA re-basing is a separate, logged step per T068 s11 item 2).

| Case | Printed set g | Basic g | Flat-rule predicted g | Margin to 1,470 g | Itemised g (20 % / 10 % on the delta) |
|---|---|---|---|---|---|
| As listed (now) | 112.1 | 1,274.3 | 1,470.9 | -0.9 | 1,467.3 (margin +2.7) |
| Lean basis (3 / 4 / 25 %, 2 / 3 / 15 %) | 211.5 | 1,373.6 | 1,581.9 | -111.9 | 1,586.5 / 1,576.6 |
| **Proposed basis (S / M / C, s3)** | **250.2** | **1,412.4** | **1,625.2** | **-155.2** | **1,633.0 / 1,619.2** |
| Solid PETG, CAD as drawn | 299.3 | 1,461.5 | 1,680.1 | -210.1 | 1,691.9 / 1,673.2 |

Per group (adopted minus listed, g): fins FIN +58.2 (blocks and saddles), cage CGE +58.5 (cups +20.8, tray +22.0, saddle +7.7, clamps +10.2, hub -2.2), avionics AVN +9.1 (plate +9.9, cover -0.8), landing GER +12.6, wing WNG +0.5, harness HRN -0.8, mechanisms MEC 0.0. Sum +138.1 g. The CAD structure budget lines in MASS-GATE s13 (fins 108.2, cage 131.04, ceiling 494 g) would also change: fins +58.2, cage +58.5, so the s13 structure line (489.72 g, ceiling 494 g) would rise by the printed-part delta that sits in the fins and cage groups, about +117 g (arithmetic on this table; the groups also hold tube and foam items, so the exact new group totals are not itemised here).

The 1,470 g gate is exceeded under every basis in the table, including the lightest one. The T068 s11 rule "decision 2" (gate test not switched to the itemised rule just to pass) is unaffected: both rules fail by more than 100 g.

## 6. What this changes for the recovery round (analysis only, no pick)

- The printed set is the single largest mass lever in the aircraft after the pack. It is 249 g in the CAD as drawn (basis S / M / C), 16 % of the 1,470 g gate mass.
- Infill is a weak lever: moving from the proposed to the lean basis saves 38.7 g (250.2 -> 211.5 g); the remaining 99.3 g over the listed set is geometry that the CAD draws solid (fin root block 50.5 x 23 x 60 mm, rib saddle 41 x 60 x 21 mm, cup sleeve, tray plate). Items on the T068 s11 recovery list (saddle clamshell -14 to -18 g, root block clamshell up to -25 g, lightening of cage/caps/raceway) therefore start from the CAD-solid masses here, not from 1.0 / 3.2 g. Their numbers in T068 s11 were computed against the listed (too low) masses and should be recomputed on this table.
- The CAD fidelity rule (CLAUDE.md: the CAD looks exactly like the aircraft) means the lightening has to be drawn (hollow shells, windows, ribs) before a lower mass can be listed; a listed mass below the drawn volume x basis is not allowed.

## 7. Proposed code change (diff, NOT applied; CAD source is outside this task's edit scope)

Masses are given to `P()` before the shapes exist (`P(...)` at module import, shapes built later by the modules), so volume cannot be read at the `P()` call. Two workable options: (A) a table file generated by the audit script and read by `P()`; (B) a second pass after the build. Option A is the smaller diff and stays deterministic:

```diff
--- a/redesign/qp/A/cad/amodel/common.py
+++ b/redesign/qp/A/cad/amodel/common.py
@@ def P(pid, name, sub, mass_g, material, mob='make', elec=None, cg=None, **flags):
-    PARTS[pid] = dict(id=pid, name=name, subsystem=sub, mass_g=mass_g, material=material, make_or_buy=mob,
+    mass_g = PRINTED_MASS.get(pid, mass_g)      # T-067: printed parts = CAD volume x print basis (printed_mass.json), else the number given
+    PARTS[pid] = dict(id=pid, name=name, subsystem=sub, mass_g=mass_g, material=material, make_or_buy=mob,
                       electrical=elec, cg=cg, **flags)
+
+
+def _load_printed_mass():
+    import json
+    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'printed_mass.json')   # {pid: grams}, written by tools/t067_mass_audit.py --write
+    return json.load(open(p)) if os.path.exists(p) else {}
+
+
+PRINTED_MASS = _load_printed_mass()
```
```diff
--- a/redesign/qp/A/cad/amodel/wing.py        (the hard-coded printed entries keep their listed number as a fallback comment only)
-    P('FIN-003-' + s, 'Fin root block (%s)' % s, 'fins', 3.2, 'PETG (printed)')
+    P('FIN-003-' + s, 'Fin root block (%s)' % s, 'fins', 3.2, 'PETG (printed)')   # T-067: mass from printed_mass.json (CAD volume x basis S)
-    P('FIN-005-' + s, 'Rib saddle on spar (%s)' % s, 'fins', 1.0, 'PETG (printed)')
+    P('FIN-005-' + s, 'Rib saddle on spar (%s)' % s, 'fins', 1.0, 'PETG (printed)')   # same
```
`printed_mass.json` content = the `computed_g` column of `t067_data/t067_merged.json` (adopt_g) for the 42 parts, e.g. `{"FIN-003-R": 18.90, "FIN-005-R": 14.39, "GER-001-UR": 4.55, "CGE-003-UR": 9.51, "CGE-006": 9.67, "CGE-007-R": 6.58, "CGE-008": 25.80, "AVN-001": 17.91, "WNG-003-C": 1.42, ...}`. Consequences to handle when applied (named, not done): `sitl/cad_mass.py` CG and inertias (hub, cups, tray centroid weights change), `proofs/gen_params_a.py` (mass.structure_groups_g), `mission_gate_a.py` hard-coded group sums (fins 116.6, cage 131.04, avionics 103.84), MASS-GATE s13 table, `landing_a.py` mass and CG (M_GATE), T064r allowables if the print basis becomes the CL-A-KP assumption. Alternative (B) keeps the table inside the build: a `Component.mass_g = volume x basis` hook in `fusionkit.Component`, which touches every part and the shop file and is the larger change.

A regression check to add when applied: for every `PETG (printed)` part, the listed mass must be within +-10 % of the `computed_g` from `t067_mass_audit.py` (about 2 min at 0.25 mm; hub 0.5 mm 30 s).

## 8. Limits, unknowns, caveats

- Print basis, print orientation, line width, infill pattern and the S / M / C assignment are **EST**; no coupon, no slicer run on these parts, no weigh-in ("—"). A real slicer preview of FIN-003, FIN-005, CGE-003 and CGE-008 would replace this model; the repo has no slicer output.
- The voxel model ignores support material, brims, supports and the extra solid a slicer adds near slopes (gives lower mass than a real print by a few percent); real parts are also usually a little heavier from over-extrusion. Not corrected.
- The 0.5 mm hub run (17.62 g solid) is 2.1 % below the listed analytic 18.00 g (`hub_mass_g()`), within pitch error. The 0.25 mm hub run was started three times and did not finish in more than 10 minutes (cause not found; 11 M voxels, dense mesh parity ray cast and per-loft sampling; "—"), so the hub is at 0.5 mm. Voxel pitch sensitivity (computed g, 0.25 vs 0.5 mm) of other parts: <= 0.12 g except tray 3.1 g and avionics plate 1.6 g (thin 2 mm / 5 mm plates: z-sampling of the 0.2 mm layer rule at 0.5 mm); the 0.25 mm numbers are used.
- The CAD shapes are those of the current stub build; they include stand-in solid blocks (e.g. FIN-003, FIN-005, CGE-006/007). If a part will be redrawn hollow, this audit must be rerun; that is the intended use.
- WNG-009 stator: listed 2.0 g includes silicone fluid and preload strips (not in the CAD); kept at 2.0 g. Its printed part alone is 1.40 g.
- The flat-rule coefficient 1.1174 and the 145.0 g growth are taken from MASS-GATE s13 and `mission_gate_a.py` as stated; not re-derived.
- Mass freeze (T068 s11 item 4): the +138 g are not new mass; they are the correction of listed to drawn. They are a correction of the figure, not a design change, and require a decision (recovery round, board) rather than an edit.

## 9. Reproduce / raw data

```
cd redesign/qp/A/mechanism/out/T067_data
python -I t067_mass_audit.py 0.25 WNG FIN GER CGE-003 CGE-006 CGE-007 CGE-008 AVN MEC HRN   # 2 min, run_h025_nohub.txt
python -I t067_mass_audit.py 0.5 CGE-001                                                      # hub, 30 s
python -I t067_mass_audit.py 0.5                                                              # all parts at 0.5 mm: run_h050.txt
T067_LEAN=1 python -I t067_mass_audit.py 0.25 <same prefixes>; T067_LEAN=1 python -I t067_mass_audit.py 0.5 CGE-001
python -I dims.py                                                                             # bounding boxes -> t067_dims.json
python -I t067_table.py                                                                       # merge, gates -> t067_merged.json, t067_table_out.txt
```
Files in `T067_data/`: `t067_mass_audit.py`, `t067_table.py`, `dims.py`, `t067_rows_h0.25_only.json`, `t067_rows_h0.50_all.json`, `t067_rows_h0.25_lean_only.json`, `t067_rows_h0.50_lean_only.json`, `t067_merged.json`, `t067_table_out.txt`, `t067_dims.json`, `run_*.txt`.
