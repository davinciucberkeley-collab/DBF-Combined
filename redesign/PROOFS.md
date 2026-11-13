# Proof chains (claims map)

Every number in the redesign is meant to be traceable: **requirement ← claim ← calculation ← parameters ← sources**.
The graph has **4,261 nodes and 13,826 links** (2026-11-13), built by `python -I redesign/proofs/build_graph.py`, which
re-runs every calculation and flags any stored number that no longer matches (drift).

**Explore it:** the **Proofs ↗** link in the K09-L Explorer (double-click `00 - OPEN THE K09-L EXPLORER (double-click me).bat`,
or the artifact link), or open `proofs/viewer/index.html`. Search any id, click a node to see its equation, inputs,
outputs and sources, and walk the chain up to the requirement and down to the sources. Filter by status to see
everything still UNVERIFIED.

**Read it as text:** [`proofs/out/CHAIN.md`](proofs/out/CHAIN.md) (large; one section per requirement).

## What the graph contains

| Node type | VERIFIED | CHECKED | PROPOSED | UNVERIFIED | Total |
|---|---|---|---|---|---|
| requirement | 0 | 1 | 1 | 57 | 59 |
| claim | 0 | 87 | 37 | 1576 | 1700 |
| calculation | 0 | 421 | 0 | 0 | 421 |
| parameter | 0 | 63 | 656 | 366 | 1085 |
| source | 0 | 76 | 0 | 101 | 177 |
| assumption | 0 | 0 | 283 | 248 | 531 |
| test | 0 | 0 | 141 | 0 | 141 |
| part | 0 | 0 | 0 | 147 | 147 |

VERIFIED needs a physical test, and nothing has been built yet, so nothing is VERIFIED. CHECKED means re-run and
compared to an independent calculation or simulation. On 2026-11-13 (D-95…D-100) **79 nodes fail on margin: 72 claims and 7 requirements**, down from 90 (79 claims + 11 requirements). Every one is triaged below.

## Triage of every failing claim (2026-11-13, D-95 … D-100)

Before this round the graph had **90 fails: 79 claims and 11 requirements**. Each of the 79 claims is triaged below.
After the round: **72 claims and 7 requirements fail, and each has a reason in this table.** One is new: `CL-H1-MSTIFF-U` (below). Build: 0 drift, 0 errors. `--strict` still
exits 1, because a failed validation pass line or an open structures item is a real FAIL. It is listed, not hidden.

| Result | Count | Claims |
|---|---|---|
| **Fixed: decision or corrected input** | 8 | `CL-B1V-VS-GATE`, `CL-B2R4-VS-GATE-FWD-ZLO` (D-96: P7 re-derived 12.3 m/s on the integer `AIRSPEED_MIN`; z floor 0.0165 m); `CL-E1-CRUISE-P-55` (D-97: 253 W carried); `CL-F2-MASS` (D-95: harness 142 g); `CL-F3-SERVO-BEC` (D-100: CoreWing 8 A, the value D-74 already relies on); `CL-J1-XT60-CONT-PESS`, `CL-J1-XT60-BURST` (XT60 not fitted, D-32); `CL-J1-TUBE-MODE-SEP` (bare-tube screen superseded by C4's 3-D model) |
| **Decided, owner's one-line edit pending** | 1 | `CL-F2-I2C-LEN` 0.522 m against the 0.5 m rule. D-99 sets the rule to 1.0 m from the bus capacitance (`CL-A1-I2C-CB` 134.6 pF ≤ 200 pF; `CL-A1-I2C-LEN-MAX` 1.21 m). The key lives in `team/F2/harness.py` and `subsystems/harness/params.json`, which F2 owns; it clears when F2 writes 1.0 m |
| **Explained: real shortfall, owned by the structures stream (fin station, STATUS #1, H7)** | 27 | C6 `CL-C6-COLLAR-RF`, `-RF-13MM`, `-RF-15MM`, `-RF-16MM`, `-RF-12MM-COND`, `-COLLAR-L-REQ`, `-STRIP-ANCHOR-RF`, `-STRIP-ANCHOR-RF-EST`, `-STRIP-EMBED-REQ`, `-STRIP-TAIL-NET-RF`, `-STRIP-TAIL-NET-RF-EST`, `-STRIP-PIN-RF`, `-STRIP-PIN-RF-PROP`, `-STRIP-PIN-RF-ALT`, `-STRIP-PIN-RF-EST`, `-STRIP-PIN-PITCH-MAX`, `-PITCH-MAX-ALT`, `-PITCH-MAX-EST`, `-FIN-ROOT-RF`, `-FIN-ROOT-RF-PROP`; D3 `CL-D3-COLLAR-H`, `-COLLAR-H-C6`, `-TAIL-EMBED`, `-ROOT-FILLET-RF-ALLOW`, `-ROOT-LEFF-REQ`; C4 `CL-C4-D3-COLLAR-H-REQ`; H1 `CL-H1-LEVER-NEED9` (the rig tracks the anchor force, and the anchor runs on the 15:1 hole). C1's D-65 torsion (×1.71) outgrew the 13–15 mm collar, the 2.5 mm pins and the 40 mm strip tail. C4 re-solves the set (CR-C6-38), and C6 asks for a 22 mm collar (CR-C6-37, +4.4 g). D-95 keeps that mass available: the 3 g free reserve plus 10.8 g of predicted margin. No collar prints or pin drilling before then. Gates: `T-C6-LAP-PETG`, `T-C6-STRIP-ANCHOR`, `T-C4-FIN-PROOF` |
| **Explained: pod as drawn before the D-69 fixes; C3 has not re-run its FEA on D2-R6** | 13 | `CL-C3-FEA-BOND-R-DESIGN`, `-BOND-R-CRASH` (run with the retired 680 g pack), `-TIED-R-CRASH`, `-AFT-STOP-PEAK`, `-AFT-TRAY-BEND`, `-AFT-PEEL`, `-FWD-PEEL`, `-FWD-BED-PEEL`, `-FWD-TRAY-BEND`, `CL-C3-AFT-STOP-D2`, `-AFT-STOP-REC`, `-BLOCK-A-SHARE`, `-STOP-SECTION-PENALTY`. D-69 drew the strut, flange and brackets (D2-R6), and the recess-corner fillet is CR-C3-17. The numbers are stale until C3 re-runs `pod_fea.py` on D2-R6 with the 590 g bounding pack. Gates: `T-C3-STOP-PUSH`, `T-C3-BOND-COUPON`, `T-C3-POD-PROOF` |
| **Explained: vibration, validated by test plus the rpm notch (R-VIBRATION allows either)** | 13 | D-97 raised the cruise rpm 5 946 → 5 994 (L/D 6.2 → 5.66). That moved C4's worst station separation 0.180 → 0.170 and its mount-stiffness need 2 229 → 2 944 N·m/rad (estimate 1 531: STATUS #9 gets worse; the D3 cheek lever and `T-C4-MOUNT-STIFF` decide). As a result, H1's GT-17 rig uncertainty at the higher pass line reads 10.4 % against 10 % (`CL-H1-MSTIFF-U`): H1 raises the GT-17 load, which has 13 % room (`CL-H1-MSTIFF-LOAD-FRAC`), or reads with a 1 µm gauge. `CL-C2-WING-MODE-SEP` (D-45: notch plus `T-C2-TAP-TEST`); `CL-C4-SIM-SEP`, `CL-C4-D3-SEP-WORST`, `-SEP-BAND` (band rule, by design intent) and `CL-C4-D3-MOUNT-K-REQ` (STATUS #9, `T-C4-MOUNT-STIFF`); `CL-C4-SIM-F1-GCI-LO` (mesh-convergence index, numerical); `CL-C4-D3-SEP-1L` (rejected one-layer option); R1 concept-model claims superseded by `CL-C4-D3-*`: `CL-C4-MESH-CONV`, `-SEP-2L`, `-SEP-1L`, `-SEP-BAND-REC`, `-SEP-BAND-1LB`. Gates: `T-C4-TAP-D3`; hover VIBE < 30 m/s², Clip 0 |
| **Explained: rejected option or sensitivity, expected FAIL** | 4 | `CL-C2-RING-NO-PLUG`, `-RING-ANCHOR` (show the plugs are required; the plug claims carry the load); `CL-C2-FEA-FOAM-FILLET-SENS` (fillet carrying the station loads, sensitivity); `CL-C3-FEA-AFT-HEEL-PEEL` (heel option, not adopted) |
| **Explained: design fixed (D-68), FEA not re-run** | 2 | `CL-C2-FEA-FOAM-CORNER-S1`, `-S3`: pocket corners R 3 mm and beads are drawn; C2 re-runs `fea/` on the revised pocket. Gate: `T-C2-WING-PROOF` |
| **Explained: validation test is the pass line** | 1 | `CL-C4-SIM-FACE-DRAWN` 14.1 vs 10 MPa (estimated allowable): `T-C4-FIN-PROOF` with a strain gauge decides (CR-C4-33) |
| **Explained: landing, operating rule or consumable** | 6 | `CL-C5-V-LAND-BROADSIDE`, `CL-C5-SIM3D-V-BROADSIDE` (4.4 / 4.0 m/s against 5: flight-card rule S1, land with a wingtip into wind, CR-C5-05); `CL-C5-SIM3D-STRIKE-TILT` (by design intent; TPU corner caps take the strike); `CL-C5-LANDINGS-PER-CARTRIDGE` (consumable cartridges: replace at the mark, CR-D5-21); `CL-C5-SIM3D-STROKE` (+0.005 mm on 35 mm at the 2.6 kg gate, 0.1 m/s sink steps; 2.4 mm spare at the predicted mass); `CL-C5-SIM3D-V-SINK-10` (1.1 against 1.2 m/s on the same 0.1 m/s grid). Gates: `T-C5-AIRCRAFT-DROP`, landing practice in measured wind |
| **Explained: protected by the flight software** | 2 | `CL-C1-N-STALL-VD` (a full pull at VD reaches n 5.2 > 3.4: F4 limits pitch rate and elevon in manual modes, CR-C1-08); `CL-B4-RPM-MAX-FULL` (unlimited fresh-pack rpm; the F4 output cap holds 9 350 rpm, `CL-B4-SPIN-MAX`) |
| **Explained: transport box nose stack short; D7 re-lays it** | 3 | `CL-D7-SIDE-CLEAR`, `-NOSE-GAP` 2.95 mm against 10 mm, `-ANTENNA-PAD-GAP` −7.05 mm against 2 mm. D-62 moved the nose 10 mm forward, and the box still has the 3/4 in nose pad (`check.py` warns POD-006 into TRN-001 by 5 mm). A 1/2 in pad (CR-A1-66) gives +6.35 mm, which is not enough for the antenna. D7 needs **+10 mm of inside box length** or the antenna tube trimmed 8 mm (ground item, no flight mass). A box CAD change, specified for D7 |

Requirements that inherit a fail (7): `R-WIND` (C5 broadside), `R-TRANSPORT` (D7 box), `R-STRUCT-MARGIN` (C2 / C6), `R-FIN-TUBE-JOINT` (fin station), `R-VIBRATION` (C2 / C4 modes), `R-PACK-RETENTION` (C3), `R-LANDING-IMPACT` (C5). Each one clears with the rows above.

## Earlier state (2026-11-11, after the harness re-route and the D5-R6 landing parts list; superseded by the triage above)

**The build is clean: 0 drift, 0 errors** (`OK: every stored number re-computes`; two warnings for transport part ids
TRN-102 / TRN-105 not in any `interfaces.json`). Every calculation re-runs to its stored outputs, so all 418
calculations are CHECKED. The rebuild takes about 4.5 min when the C4 FEA cache is warm.

What it took (from 547 build errors: 536 drifted values and 11 script errors):

- every drifted script re-run to a fixed point (the mass chain F2 harness 119.8 g → A3 → A1 → loads, performance,
  thermal, structures), including the C4 fin FEA (`team/C4/sim_fin.py`, cold run about 40 min (2 345 s) with the four parts
  in parallel: `sim/run_part.py stress|modes`, `sim/run_trial.py 0|1`);
- `team/D5/sim/fea_shoe_d5.py`: the leg-to-floor fillet was meshed as an exact arc, which left 8 tangled quads at its
  cusps; SU2 did not converge (6 609 MPa garbage) and the script stored it anyway. The fillet is now 6 chords labelled
  by surface, and a run that does not converge is refused. Shoe FEA re-run: +y 30.5 MPa, +z 38.8 MPa;
- `fusion/skeleton/make_skeleton.py` re-run (the skeleton still carried the D-48 allocations, so A5's cross-check stopped);
- `team/D5/make_interfaces.py` run on D5-R6 (lead decision), so the landing parts list and A3 now carry the real
  69.9 g (A3 retired its +5 g sleeve adder automatically);
- `team/D2/pod_claims.py` cited a requirement that does not exist (`R-TRANSPORT-FIT` → `R-TRANSPORT`).

Real design results the re-runs exposed (claims left failing, no allocation changed):

| Claim | Value vs limit | Margin |
|---|---|---|
| `CL-D5-MASS-TOTAL` / `CL-A3-ALLOC-WORST` landing mass (D5-R6 shoe: 1.2 mm walls, 2.8 mm rim, 25 mm engagement) | 69.9 g vs 48 g allocation | −46 % |
| `CL-A3-CG-X-PRED-RANGE` predicted CG x, 550 g pack at nominal | 52.6 mm vs range 46.6–51.4 mm (1.2 mm aft of the limit) | −51 % (range use 1.51) |
| `CL-A3-CG-X-STATIONS` worst CG x range use over the 546 / 551 / 590 g packs | 1.028 vs 1 | −3 % |
| `CL-A3-GATE-MARGIN-590` gate margin with the 590 g pack (was −9 %) | 67 g vs 100 g | −33 % |
| `CL-A1-PACK-ACCEPT` / `CL-E2-PACK-ACCEPT-KG` heaviest pack the 100 g overrun still covers | 536 g vs 556 g | −4 % |
| `CL-E2-PACK-MASS` 550 g pack carried in the budget vs that acceptance line | 550 g vs 536 g | −3 % |
| `CL-D3-TIP-STEP-MISMATCH` / `CL-D3-TIP-SQUARE` D3 fin tip vs the D5-R6 step | 13 mm vs 0.5 mm; ratio 0.78 vs 1 | fails |
| `CL-C4-SIM-SEP` fin station-mode separation from 1P/2P | 0.181 vs 0.20 | −9 % |
| `CL-C4-SIM-FACE-DRAWN` fin face hot-spot at the drawn D5 shoe, ultimate | 10.3 MPa vs 10 MPa | −3 % |

The mass gate itself still holds: basic 2 374 g, predicted 2 493 g against 2 600 g, gate margin 107 g against the
100 g first-build overrun (+7 %, was +31 %). The harness (120 g basic) stays inside its 123 g allocation.
