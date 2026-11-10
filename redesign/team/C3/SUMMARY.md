# C3 — Pod structures (summary)

Revision **C3-R2**, 2026-11-09, at params A1-R4 (D-47), D2-R5 pod (the D-47 re-lay), C1's latest loads and C6's allowables. Report:
`FUSELAGE-STRUCTURES.md`. Script: `pod_structures.py` (< 1 s) → `claims.json` (34 claims, 10 calcs, 3 planned
tests), `out/results.json`. Proof build: **no C3 errors** (the `stop_wall_h_m` KeyError is fixed). C6's
`CALC-C6-POD-ALLOW` drifts until C6 re-runs (CR-C3-11).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod-to-wing bond interaction, design / 12.75 g crash | 0.87 (L2 pair, narrow) / 0.72 | — | `CL-C3-BOND-R-DESIGN`, `-R-CRASH` | `UNVERIFIED` (+13 % / +28 %) |
| Pod group in the crash (680 g pack) | 0.954 / 119 | kg / N | `CL-C3-POD-GROUP-MASS` | `UNVERIFIED` |
| Aft stop 3.0 mm × 27 mm (tray rear piece, x 0.056) vs 15 MPa / load vs D2 piece bond | 14.0 / 86 vs 417 | MPa / N | `CL-C3-AFT-STOP-D2`, `-BOND` | `UNVERIFIED` (+7 % / +80 %) |
| Forward stop 3.0 × 25 mm: stress / root capacity vs 85 N | 12.9 / 99 | MPa / N | `CL-C3-FWD-STOP-REC`, `-FUSE` | `UNVERIFIED` (+14 % / +16 %) |
| D-47 nose: block A / stack | 1.0 / 8.8 | mm | `CL-C3-NOSE-BLOCK-A`, `-NOSE-STACK` | `MODELLED` |
| Block A share of nose-in energy (≤ 0.10) | 0.041 | — | `CL-C3-BLOCK-A-SHARE` | `UNVERIFIED` (+59 %) |
| Block B cost of a 25 mm stop vs full section (≤ 1 mm) | 0.56 | mm | `CL-C3-STOP-SECTION-PENALTY` | `UNVERIFIED` (+44 %) |
| Guides 1.5 mm, lateral crash | 6.5 | MPa | `CL-C3-GUIDE-D2` | `UNVERIFIED` (+57 %) |
| Tray flat-wise vs C6 50 kPa | 19.3 | kPa | `CL-C3-TRAY-FLAT` | `UNVERIFIED` (+61 %) |
| Floor-wall glue with 6 mm fillet vs C6 100 kPa (without: 110.7) | 49.2 | kPa | `CL-C3-FLOOR-GLUE-FILLET` | `UNVERIFIED` (+51 %) |
| Overhang root face stress, crash / design | 7.7 / 4.4 | MPa | `CL-C3-OVERHANG-CRASH`, `-DESIGN` | `UNVERIFIED` (+23 % / +56 %) |
| Handle design load vs 2 ties | 110 vs 444 | N | `CL-C3-HANDLE-TIES` | `UNVERIFIED` (+75 %) |
| Hatch tab 12 × 40 mm at VD (185 mm hatch) vs 2.5 N/cm² | 2.11 | N/cm² | `CL-C3-HATCH-TAB` | `UNVERIFIED` (+16 %) |
| Pod mass (D2-R5 holds the C3 sizes, Δ 0 g) vs 131 g | 131.0 | g | `CL-C3-POD-MASS-REC` | `UNVERIFIED` (0 %) |
| With a full-section forward stop | 137.3 | g | `CL-C3-POD-MASS-FULL-STOP` | not adopted |

Factors: design = limit × 1.5 × 1.15 × 1.25; crash = C1 ultimate, no further factor. Calculations `CHECKED`;
allowables are estimates (C6), so every margin is `UNVERIFIED` until the tests run.

## Action items closed this round

| Item | Resolution |
|---|---|
| CR-A5-29 / build_graph KeyError `stop_wall_h_m` (all 8 calcs) | Re-pointed: `ASM-C3-STOP-H` ← `fwd_stop_m[1]` (id kept for C5), new `ASM-C3-AFT-STOP-H` ← `aft_stop_m[1]`, hatch ← `pod.size_m[1]` and `pod.x_le_m`. All 10 calcs run |
| CR-A3-22 / D-47 shorter nose block | **Crush path kept**: pack → spreader → block B → stop → nose wall → ground. Block A (1 mm) is unbuildable as XPS; D2-R5 already made it the 1 mm epoxy bond line C3 asked for (CR-C3-08, closed) |
| CR-C5-13 full-section forward stop (+4 g) | **Declined** with the numbers above: 0.56 mm benefit, 6.3 g cost (pod 137.3 vs 131 g). Stop stays 25 × 54 mm, spreader stays full-section |
| CR-C6-16 pod allowables | Read from C6's nodes (`CALC-C3-ALLOW`); board flat-wise 50 kPa, paper 100 kPa; fillet check added |

## Change requests (R2)

`CR-C3-08` block A → bond line (done in D2-R5) · `CR-C3-09` withdrawn (tab passes at C1's q 453 Pa) · `CR-C3-10`
aft stop on the tray rear piece accepted (`CL-C3-AFT-STOP-BOND` +80 %) · `CR-C3-11` C6 re-run · `CR-C3-12` C5 re-run
on the D-47 bay. Overhang and crash checks now use the most forward station that keeps block B (`CL-D2-PACK-X-FWD-MIN`
−0.024 m); a pack flown with block B left out (−0.051) fails the overhang crash check (−19 %): block B is a
no-fly item on the checklist (H3).

## How to verify

| Check | Command or test |
|---|---|
| Re-run claims | `python -I redesign/team/C3/pod_structures.py` then `python -I redesign/proofs/build_graph.py` |
| Allowables | `T-C3-BOND-COUPON`, `T-C3-STOP-PUSH`, C6 `T-C6-BOARD-CORNER` |
| Built pod | `T-C3-POD-PROOF`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-D2-WEIGH` |
