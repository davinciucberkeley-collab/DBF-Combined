# Concept A O4b CG and thrust-margin closure (2026-11-21)

Independent reviewer (opus). I wrote none of T-077 (parts 1-3), T-074, T-080, D-215..D-223. **This is the only repo file I wrote.** I ran no CAD edit, FEA, SITL or landing simulation. Runs, all read-only: `python -I mission_gate_a.py --o4b` (exit 0), `python -I prop_a.py --sched --mass 1.704 / 1.64 / 1.60` (exit 0), and four scratch scripts in the session scratchpad (not in the repo) that import `cad/build_a.py` + `a_model.py` (centroids of every part, the same method as `sitl/cad_mass.py`, which writes `cad_mass.json` and so was **not** run) and `prop_a.py` (T/W, scheduled cap). Housekeeping: my first scratch run wrote `redesign/qp/A/cad/parts.json` (the script changed directory into `cad/`). I moved it to the scratchpad straight away; `git status` is clean.

Limits held, none relaxed: A-P4 band 19-26 mm, hard aft 28.5 mm, SM >= 5 % chord; A-P2 T/W >= 2.0 fresh, >= 1.6 sag; A-P3 window >= +-5 %; A-P16 12.1 A per motor; A-P9 30 deg; RF >= 1.0 with KF 1.725 / KP 2.156 and max(DAF, 1.5), where DAF is 1.97 / 2.23 (D-223); $2,000 total with the crash reserve held (AM-012/013). EST = estimate. "—" = unknown.

## 0. Answers

| # | Question | Answer |
|---|---|---|
| 1 | Are the T-077 numbers right? | **Yes, reproduced.** Basic 1,483.31 g, CG 28.302 mm, SM (40.7 - 28.30)/245 = 5.06 %. Aft trim end 30.12 mm. Pack at -20 mm gives 26.48 mm. MASS-PRED 1.4833 x 1.1174 + 0.032 x 1.47 = **1.7045 kg**. TW-SAG-PRED **1.594**, reproduced only with the **fixed 0.90 cap and no download**. Decided-but-undrawn items: +3.84 mm, giving 32.14 mm (EST). |
| 1 | What sets 26.0, and what governs? | **26.0 mm is the static-margin evidence limit (SM 6.0 %). It is not an elevon-authority limit.** 28.5 mm is the SM 5 % floor (28.45 mm). On the nominal CG, CL-A-CG-HI at 26.0 governs: it is stricter than SM 5 % and stricter than CL-A-CG-TRIM-AFT (nominal <= 26.68 mm). An aft CG *reduces* elevon trim and pitch use (s1). |
| 2 | Levers | Each lever with its mm and g is in s2. Rungs 1-2 cannot close the gap without breaking another limit. Rung 3 can: pack retention, avionics, and moving the whole cage forward relative to the wing. Rung 5 ballast fails A-P3 and A-P2 (40 g: window +3.2 %, fresh 1.91). |
| 3 | T/W sag 1.594 | **The failure is a stale claim, not physics.** D-219 replaced the fixed 0.90 cap with the voltage-scheduled cap. With that cap, sag T/W is 1.884 (1.827 with the 3 % download) at 1.704 kg. **The real mass-dependent failure is A-P3:** with the download, the window is **+4.70 % at 1.704 kg** (fail). It needs predicted mass <= 1.694 kg at derate 0.93, or <= 1.649 kg at the 0.905 bench line. Fresh T/W with the download is 1.969 (s3). |
| 4 | Verdict | **A credible combined fix exists for A-P4 + A-P2 + A-P3 at the design derate 0.93 (EST):** CG **24.7 mm**, SM **6.5 %**, predicted **1.677 kg**, window **+5.50 %** with the download, sag 1.856, fresh 2.001 with the download (2.063 without). **Cost:** the Dec-15 bench pass line rises from 0.905 to **0.920** (0.929 if A-P2 fresh is judged with the download). The fix depends on hub pockets of at least 19 g, which the H-A1/H-A2 FEA must clear. The bridge gets 12 mm longer and must be re-checked. This goes to Dillon as information, not as an option sheet (s4). |

## 1. Verification and the A-P4 basis

### 1.1 Numbers reproduced (geometry arithmetic)
- Part table (scratch, `build_a.centroids()` + `a_model.PARTS`): M = 1,483.31 g, CG x = 28.302 mm. This matches `sitl/cad_mass.json` (1.48331 kg, 0.028302 m). Lateral CG is 1.82 mm (limit 5).
- Largest aft moments about the CG (g mm). Fin tubes FIN-001: 7,200 each (27.1 g at x 294). Wing core: 5,866. Root blocks FIN-003: 4,816 each (18.9 g at x 283). Servos: 2,312 each. Ribs: 2,114 each. Elevon balance: 1,827 each. Fairings: 1,774 each. Skin: 1,698. Shoes: 1,228 each.
- Largest forward moments. Pack: -10,071. Motors: -8,294 / -7,449. Hub: -5,332 (61.5 g at x -58.4).
- `mission_gate_a.py --o4b`: "CAD basic 1483.3 g, CG 28.30 mm ... SM 5.06 %", "pack centre at x -20 mm: 26.5 mm, SM 5.8 %", "CG aft limit SM 5 %: 28.45".
- Undrawn decided items, at T-077 P3.5 masses and stations: R2 (-17.91 g at x 92.3, +3 g at 92), R3fix (-11.2 g at -73.6), H743 (+11 g at 60), enlarged root blocks (+12.2 g at 283.1), shoe cups (+7 g at 298.1). Add R4 (-0.08 mm) and the X7 node (+0.2 mm). Result: **1,487.4 g, CG 32.14 mm, SM 3.49 %** (EST). This confirms T-077's "+3.8 mm".
- P6/P8 0.50/0.51 confirmed in `mechanism/out/T064r_landing.md` (1.5 kg, pre-D-223) and in T-080 s3.4.

### 1.2 What the two aft limits are
| Limit | Value | Physics | Source |
|---|---|---|---|
| Hard aft | 28.5 mm (SM 5 % = 28.45) | Static-stability floor. NP 40.7 mm is EST (44.0 inviscid, -3.3 viscous) | BOARD QP-1 C4; MASS-GATE s5 table; `mission_gate_a.py` l.75, l.87 |
| Band top | 26.0 mm (SM 6.0 %) | **An SM band where the transition evidence sits.** QP-3 BOARD s4: "The band is an SM band (6.0-8.4 %, NP 40.7 mm EST), and it is where all transition evidence sits". The 1-point SM buffer (2.45 mm) covers the EST NP. "Why not lower the band: it would accept an untested SM" | `review/QP-3/BOARD.md` l.92-100 |
| Band bottom | 19 mm | **Elevon authority.** Forward CG needs more trim (+3.3 deg cruise, +5.2 deg handover per +3.5 % SM). Pitch use is 0.59 of 0.60 at 19.3 mm | BOARD QP-3 s4; D-195 (3) |

**Elevon authority is not the aft limit.** T-074 check 3 (`T074_check3.md` l.61) at 1.64 kg gives pitch use **0.55 at 19.3 mm, 0.39 at 26.0 mm**, and 0.37 at r 1.51 and 26.0 mm. Moving the CG aft frees authority. The aftmost CG ever run in SITL is 26.0 mm (T-074). The R5 runs reached 23.6 mm (`sitl/jobs_qp5*.txt`, `cg=23.6`). Above 26.0 mm there is **no flight evidence** at all.

**Which limit governs:** CL-A-CG-HI <= 26.0 on the nominal CG. CL-A-CG-TRIM-AFT allows a nominal CG up to 28.5 - 270 x 10 / 1,483 = 26.68 mm, and SM 5 % allows 28.45 mm. Both are looser. Raising 26.0 would be a relaxation. That needs a SITL run above 26 mm plus the measured NP (M5/M6), and it is not proposed here.

Minor text drift (LOW): MASS-GATE s6 still says "as-built CG outside 20-26 mm", while A-P4 says 19-26 (D-195). Required fix: the conductor aligns the MASS-GATE s6 text.

## 2. Levers in ladder order (geometry arithmetic, EST unless stated)

Sensitivities from the part table. Moving 1 mm forward changes the CG by:
- whole cage (motors, props, adapters, nuts, hub, arms, cups, doublers, pins, conduits; 506.7 g): **-0.342 mm**
- pack group (pack, pad, tray, raceways; 297.4 g): -0.200 mm
- fin group (tubes, blocks, fairings, shoes, pads; 129.8 g): -0.0875 mm
- avionics group (82.3 g after R2): -0.055 mm

The required shift from the 32.14 mm EST state to 26.0 mm is **6.1 mm, or about 9,100 g mm**.

| Rung | Lever | Δ g (basic) | Δ CG mm | Works? | Why / cost | Source |
|---|---|---|---|---|---|---|
| 1 subtract | Elevon lead 12.8 -> 10.0 g per side | -5.6 | -0.52 | Possible, not chosen | Flutter onset falls about 0.54 m/s per g. Half-filled damper: 31.5 m/s -> about 30.0 against 28.8 (linear extrapolation, EST). The undamped case already fails. Needs a flutter re-run. Too small to matter alone | D-195 (5), D-205 (3) |
| 1 | Delete the fin fairings FIN-004 | -16.8 | -3.0 | **No** | Removes fin area that yaw stability (A-P8a) relies on | — |
| 1 | Hardware lump HRD-001, 26 g at x 101 | 0 | ±0.7 (uncertainty) | Not a lever | Its station is a lumped EST. Within ±40 mm of true it moves the CG ±0.7 mm. Weigh-in M5 settles it | `a_model` HRD-001 |
| 2 geometry | Fin tube 16x14 -> 16x15 | -13 | -2.4 | **No** | Z 166 -> 91.5 mm3 (x0.55), so P4 RF falls from 3.91 (1.5 kg, pre-D-223) to about 2.15, before the mass and DAF re-scaling. Fin f1 drops about 15 % against a separation that is already marginal (QP-1 SIZING: 7 % at fixity 0.75). Tube "—" | T064r P4; QP-1 SIZING-A l.67 |
| 2 | Fins 20 mm forward (tube x 294 -> 274, still 8 mm aft of the TE; fins outboard of the elevons) | -2.6 (rib) | **-2.45** | Not enough alone (26.9 after 3a + 3b); not chosen | Moves x_ground and the landing geometry that D-222/D-223 and A-P9 (0.5 deg margin) rest on. The fin yaw arm shortens about 7 % (no SITL). Landing path and fin modes need re-runs | scratch |
| 2 | Pack with the 46 mm side along x | 0 | — | No | Hits the cover at aft trim (T-077 s1) | T-077 s1 |
| 3 rearrange | **3a** Pack 10 mm forward (centre -20) on **two 20 mm straps at about y ±35 mm**, through tray-plate slots outboard of the D-220 collar (collar |y| <= 12) | +3 (strap pair 10 g vs 7 g, EST) | **-1.97** | **Yes** (CAD check needed) | The single central strap had to pass under the bridge inside the collar. Outboard straps never cross the collar, and the leads and balance plug stay at the pack's aft end. Must clear the V struts and raceways under the tray: not checked. Second strap price "—" | T-077 P3.2, P3.6 |
| 3 | 3a': pack forward with the leads re-routed to the front | 0 | -1.82 | Inferior | More exposed lead over the nose | T-077 P3.5 |
| 3 | 3a'': shorter collar | — | -1.8 | No | D-220 needs a 30 mm bond length | D-220 |
| 3 | **3b** Avionics group (FC, ESC, RX, GPS, airspeed, cover, XT60, screws) 15 mm forward, done inside the R2/H743 re-layout already pending | 0 | **-0.83** | **Yes** | With 3a, the pack aft edge at +10 trim is -5.5 mm (after 3c), so the cover front can go from 22.5 to 7.5 mm. Needs a CAD fit on the S5010 upper skin | T-077 P3.4 |
| 3 | **3c** Whole cage + pack **Δ mm forward relative to the wing** (hub, motors, arms, tray, pack all translate; bridge and struts lengthen) | +0.12 per mm (bridge, struts, phase leads) | **-0.56 per mm** | **Yes** | Hub geometry unchanged. Bridge +Δ, already RF 0.86 at DAF 2 (D-221, open). Struts +0.41Δ (Euler -3.4 % at Δ 12, RF 1.10 -> about 1.06 EST). A-P10 cage mode moves down (favourable, EST). Prop plane +Δ forward (NP about -0.1 mm, EST, from the D-195 prop-plane effect). Box x extent 479.4 + Δ, limit 500 | scratch; QP-3 BOARD s4 "cage plane" knob |
| 4 approach | X7 Onyx + CF root blocks instead of enlarged PETG | -4 to -8 | -0.7 to -1.4 | Not shown | Coupons C-1..C-3 and a landing-path run on the D-223 demand. Optional margin | T-080 s3.4 |
| 4 | Onyx shoes | -1 | -0.18 | Marginal | — | T-080 s3.5 |
| 4 | Clamshell root block | about -25 | about -4.3 | "likely no" | 1.15 kN hole bearing | T-068 s6 |
| (mass) | **Hub pockets** (61.5 g solid -> 24-30 g lightened, T-080 EST) | **-31.5 to -37.5** | **+1.8 to +2.2 (aft)** | Needed for A-P3, see s3 | H-A1/H-A2 FEA must size them. The CG cost is paid by a larger Δ in 3c | T-080 s3.1; T-077 P3.6 item 2 |
| 5 add | Nose ballast at x -100 after 3a + 3b: 40 / 60 / 80 g | +40 / +60 / +80 | to 25.96 / 24.34 / 22.76 | **No** | Predicted 1.757 / 1.779 / 1.802 kg. Window +3.19 / +2.55 / +1.93 % and fresh T/W 1.91 / 1.89 / 1.86 (0.93, with download): A-P3 and A-P2 fail. Landing demand +2.5-4.7 %. Bench line 0.964-0.989 | scratch |

Rungs 1-2 alone, or 3a + 3b + X7: 32.14 - 1.97 - 0.83 - (0.7..1.4) = **28.6..27.9 mm: fail.** Only 3c closes the gap without mass.

## 3. T/W sag and the mass-dependent checks

### 3.1 Why 1.594 fails, and why it is the wrong test (finding F-1, MAJOR)
`proofs/claims_a1_flight.py` CALC-A-TW-PRED uses `P:prop.spin_cap` = 0.90, a fixed `Q_M_SPIN_MAX` (`params-A.json` prop.spin_cap). **D-219 (AM-009) replaced the fixed cap with a voltage-scheduled cap** (`prop_a.cap_sched`). That cap is 0.904 at 16.8 V and **1.000 (not binding) at the 14.92 V sag state** for 1.60-1.70 kg (`prop_a.py --sched`). It also keeps one motor at <= 12.1 A (A-P16).

Vertical thrust (scratch, `prop_a.tw_state`, derate 1.0, per kg): fresh scheduled 3.721 kgf; sag scheduled 3.451; sag with the fixed 0.90 cap 2.921.

| m kg | derate | download | T/W fresh (sched) | T/W sag (sched) | window | fixed-0.90 sag |
|---|---|---|---|---|---|---|
| 1.704 | 0.93 | none (committed form) | 2.031 | 1.884 | +6.24 % | **1.594** (= proof) |
| 1.704 | 0.93 | 0.97 (plant, D-223) | **1.970** | 1.827 | **+4.70 % FAIL** | 1.546 |
| 1.704 | 0.905 | 0.97 | 1.917 | 1.778 | +3.36 % | 1.505 |
| 1.649 | 0.905 | 0.97 | 1.981 | 1.837 | +5.00 % (the 0.905 line) | 1.555 |
| 1.677 (fix) | 0.93 | 0.97 | 2.001 | 1.856 | +5.50 % | 1.574 (1.620 without download) |

Mass ceilings at the predicted mass (scheduled cap):

| Check | derate 0.93, no download | 0.93, download | 0.905, download |
|---|---|---|---|
| A-P2 fresh 2.0 | 1.730 kg | 1.678 | 1.633 |
| A-P2 sag 1.6 | 2.006 | 1.946 | 1.894 |
| A-P3 window +-5 % | 1.747 | **1.694** | **1.649** |

- **F-1 (MAJOR):** CL-A-TW-SAG-PRED, CL-A-WINDOW-PRED and CL-A-WINDOW-MASS still test the pre-D-219 fixed cap. They report a failing sag (1.594) that does not exist under O4b. They also report the window in the no-download form, which hides the real failure. **Required fix (conductor, proofs + params):** re-base CALC-A-TW-* on `prop_a.cap_sched`, apply the 0.97 download that D-223 says governs, and re-word the A-P1/A-P2 text "with Q_M_SPIN_MAX 0.90" to follow D-219.
- **F-2 (MAJOR):** at the present prediction (1.704 kg), **A-P3 fails** in the plant convention that D-223 adopted: +4.70 % at derate 0.93, +3.36 % at 0.905. The 0.905 pass line (TEST-PLAN TP-1, D-223 item 2) was derived at **1.649 kg**: 1.649 / (3.4513 x 0.97) x 1.47 / 0.80 = 0.905. **The pass line has to follow the predicted mass.** At 1.704 kg it is 0.935, which is above the design EST 0.93. Required fix: TEST-PLAN TP-1 states its line as a function of the predicted mass and is re-issued with the final number.
- **F-3 (MAJOR, open convention):** the record reports A-P2 fresh T/W **without** the download (T-074: 2.10; proofs). If the D-223 reasoning (the plant applies the download, so the check must hold in flight) applies to A-P2 as well, then fresh 2.0 needs derate **0.914 even at 1.649 kg**. That is stricter than the 0.905 line D-223 accepted. Required fix: an opus ruling on whether A-P2 is judged with the download. The verdict below gives both forms.
- Cruise (mass-dependent, `mission_gate_a.py` formulas with the 2,800 mAh pack): 279 s at 1.704 kg and about 289 s at 1.677 kg, against 204.6 s required. Passes. The proof CL-A-CRUISE-AVAIL (173.5 s) still uses the old 2,300 mAh pack and is stale. Same F-1 fix.

### 3.2 What restores the margins
- **Mass is the only lever inside budget.** The margin is $42.49 (T-082). Already-priced alternatives do not help. 10x4.5 props give at most +0.8 % at A-P16 (D-217 F-1). Smaller packs fail cruise: 2,300 mAh gives about 191 s at 1.65 kg against 204.6 s (scratch, `mission_gate_a.py` formulas). A 2,500 mAh pack would pass cruise (about 233 s), but its mass and price are "—" and it is not priced. Buying any new pack or prop eats the $42 margin.
- **Hub pockets (-31.5..-37.5 g, T-080 EST) are the mass lever that counts.** Every gram costs 0.058 mm of aft CG, because the pockets sit at the most forward heavy part. That is the coupling with the CG fix: pockets and the cage shift Δ have to be sized together.
- Information only, not used in the verdict: CALC-A-MASS-PRED applies the uniform 1.1174 growth factor to the pack (270 g). ASM-A3-MGA books packs at 0 % growth and datasheet/CAD items at 5 %. The itemised maturity rule on the present CAD gives 1.666 kg against 1.704 kg (scratch). Re-basing the method is a conductor/opus call. Both mass claims stay required (D-208).

## 4. Verdict and the combined fix

**Combined fix (S\*):** 3a + 3b + 3c with **Δ = 12 mm** + hub pockets -34 g (T-080 mid EST), on top of every decided-but-undrawn item (scratch `plan.py`, EST):

| State | basic g | CG mm | SM % | pred kg | window (0.93, dl) | T/W fresh (0.93, dl / none) | T/W sag (sched, dl) | bench line |
|---|---|---|---|---|---|---|---|---|
| CAD as drawn | 1,483.3 | 28.30 | 5.06 | 1.704 | +4.70 % | 1.969 / 2.031 | 1.827 | 0.936 |
| + undrawn decided items | 1,487.4 | 32.14 | 3.49 | 1.709 | +4.57 % | 1.964 | 1.822 | 0.938 |
| + 3a + 3b | 1,490.4 | 29.34 | 4.64 | 1.712 | +4.47 % | 1.960 | 1.818 | 0.940 |
| + 3c Δ 12, no pockets | 1,493.0 | 22.57 | 7.40 | 1.715 | +4.39 % FAIL | 1.957 | 1.815 | 0.941 |
| **S\*: + 3c Δ 12 + pockets -34 g** | **1,459.0** | **24.74** | **6.52** | **1.677** | **+5.50 %** | **2.001 / 2.063** | **1.856** | **0.920** |
| S\* + X7 root blocks -6 g (optional) | 1,453.0 | 23.67 | 6.95 | 1.671 | +5.70 % | 2.009 | 1.864 | 0.917 |

S\* checks:
- CL-A-CG-HI: 24.74 <= 26.0, a margin of 1.26 mm. That margin absorbs error in the +3.8 mm EST tally.
- Trim ends: 23.6 / 26.6 mm (>= 19 / <= 28.5). The pack keeps its 6 mm of forward travel (-1.1 mm) as the weigh-in knob.
- SM 6.5 %, inside the evidence band.
- Box x extent about 491 mm against 500.
- The stale fixed-0.90 sag claim also passes without the download (1.620).

Sensitivity:
- With Δ = 10 mm the CG is 25.84 mm. That margin is too thin, so Δ = 12.
- The pockets must deliver **at least 19 g** for the window at 0.93 with the download (at least 13 g if the X7 blocks are adopted).

**Verdict:** O4b *can* meet A-P4 and A-P2 (sag and fresh) together, plus A-P3 at the design derate 0.93 with the download. It does so by rearranging (rung 3) plus the hub pockets. No ballast is used and no limit is relaxed. The fix has three conditions:

1. **The hub pockets must pass H-A1/H-A2** (FEA not run; D-220 hub sized on Mz 17.51 N m).
2. **The bridge, now 12 mm longer, must pass.** It is already RF 0.86 at DAF 2 at the saddle end (D-221, open on T-076c D-1). The moment arm grows about 11 % (EST), giving about 0.77 before D-1. The fallback is an 18x16 bridge (Z x1.29, +2 g EST, collar bore 18 mm; wall 3 mm, EST).
3. **The Dec-15 bench line becomes 0.920** (0.929 if F-3 rules the download into A-P2), up from 0.905. The prop must come within 1 % of the EST derate instead of 2.7 %.

This is not a relaxation, but it raises the go/no-go risk. **For Dillon (information, no money):** "The CG fix keeps the aircraft and budget as approved. Its consequence is that the December thrust test must show at least 92 % of the catalogue thrust, not 90.5 %." If the bench lands at 0.905-0.920, the escalation path is more mass removal: X7 blocks, the elevon-lead flutter re-run, the growth-method ruling (s3.2), or a lighter pack (price "—").

## 5. Findings

| ID | Severity | Finding | Evidence | Required fix |
|---|---|---|---|---|
| F-1 | MAJOR | T/W and window claims use the superseded fixed 0.90 cap and the 2,300 mAh pack | `claims_a1_flight.py` l.153-200; `params-A.json` prop.spin_cap 0.9; D-219 | Re-base on `cap_sched` and the 0.97 download; update A-P1/A-P2 text (conductor) |
| F-2 | MAJOR | A-P3 fails at 1.704 kg in the D-223 convention (+4.70 %); the 0.905 line belongs to 1.649 kg | s3.1 table | Mass to <= 1.694 kg (S\*); TP-1 line follows the predicted mass |
| F-3 | MAJOR | Download convention on A-P2 fresh is unresolved; with the download, 0.905 is already short (0.914 needed at 1.649 kg) | s3.1 | Opus ruling |
| F-4 | MAJOR | CG 28.3 mm as drawn, about 32.1 mm EST with decided items: A-P4 fails; rungs 1-2 cannot close it | s1.1, s2 | Implement S\* (s6) |
| F-5 | MINOR | `mission_gate_a.py` roll-up rows (1.466 kg) and the default path are stale (T-077 says so as well) | `mission_gate_a.py` l.29-37 | Re-base on the CAD part table |
| F-6 | LOW | MASS-GATE s6 band text 20-26 vs A-P4 19-26 | MASS-GATE l.73 | Align the text |

## 6. Implementation scope (sonnet implementer; gates once at the end)

1. **CAD 3c.** `amodel/common.py`: set `HUB` x -0.069 -> **-0.081**. Every hub-referenced item follows: motors, arms, sleeves, pins, cups, doublers, conduits, raceway front (`RW_DX`), tray face `HUB_X1` -0.045 -> -0.057, tray, collar. Bridge `BR_X0` follows the bore and `BR_X1` stays at the saddle, so the bridge gets 12 mm longer. Struts are recomputed. The tray's aft end leaves 12 mm of the core slot: fill the slot or keep the tray length, and record which.
2. **CAD 3a.** Set `PACK_X` to the new centre: -20 relative to the tray, -32 mm absolute = (-0.0485, -0.0155). Replace PWR-002 with **two 20 mm straps at about y ±35 mm** through tray-plate slots. Check against CGE-005 struts and HRN-003 raceways. Keep the lead exit at the pack aft end. Update BOM W08 to qty 2 (>= 385 mm each, price "—").
3. **CAD 3b (with R2/H743).** Draw the R2 bosses and the Kakute H743-Wing with the avionics group 15 mm forward (cover front 22.5 -> 7.5 mm). Check the cover against the pack at +10 trim (aft edge -5.5 mm).
4. **Wiring.** E-HRN-13 grows by about 7 mm per strand (pack exit -22 mm, XT60 -15 mm) to about 124.5 mm EST. List it under the exposed-wire rule. The W10 extension (55 mm stock) still covers it.
5. **Hub pockets.** Do not draw them until H-A1/H-A2 size them. Until then, carry them as an EST mass line, labelled EST. Hold the threshold at >= 19 g.
6. **Gates:** build_a, collide pose 21, linkage poses, assembly, wire_inventory, `cad_mass.py`, `mission_gate_a.py --o4b`, proofs, drawings. Acceptance: CG <= 25.0 mm with the undrawn items drawn or tallied, SM >= 6 %, CG-TRIM-AFT <= 28.5, box x <= 500 mm.
7. **Separate analysis tasks (not the implementer's):**
   - H-A1/H-A2 with pockets at the new position
   - bridge at L + 12 under T-076c D-1, with the 18x16 fallback
   - strut buckling
   - landing path and A-P9 at the predicted mass, new CG and Iyy (+2.5 % EST)
   - A-P10 modes
   - proofs re-base (F-1)
   - TP-1 line (F-2)
   - F-3 ruling

## 7. Limits of this review
- All CG and mass deltas are point-mass geometry arithmetic on EST stations. The undrawn-item tally is T-077's EST. Pocket mass is T-080's EST.
- Thrust uses the `prop_a.py` model (APC static rows, derate 0.93 EST, I0 0.5 A EST).
- No collision check of the strap slots, the forward avionics or the 12 mm cage shift. No structural check of the longer bridge or of the pockets.
- The NP effect of the prop plane is a scaled estimate.
- Second-strap price, X7 charge and lighter-pack data are "—".
