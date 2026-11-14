# A1 hand-off: team-lead actions and the pod-station rule

Status: `PROPOSED`, A1, 2026-11-10 (pack thresholds at D-64; first written 2026-11-09, closes CR-A1-21 on A1's side). This is the A1 draft of the team-lead section
for `redesign/HANDOFF.md` (README: A1 owns it, written last). Numbers come from
`python -I redesign/team/A1/frame_claims.py` (`CALC-A1-POD-RULE`) and A3's roll-up (`CALC-A3-CG`).

## 1. Team-lead actions (people with hands and software, not agents)

| # | Action | Who | When | Done when | Feeds |
|---|---|---|---|---|---|
| L1 | Run **BuildAll** once in Fusion 360 on the K09-L skeleton | one teammate with a Fusion licence, named by the team lead | after A5 reports the skeleton moved to R1 (CR-A1-12: tubes at x 0.045, half-fins, through-core block, 45 mm feet, pod at the station in force) | A5 has the run summary text, a screenshot of the assembly and the Fusion build number | A5 (CR-A5-08): `fusion_backend.py` `UNVERIFIED-IN-FUSION` → `CHECKED` |
| L2 | Weigh and measure the **first flight pack** on arrival | E2 or whoever receives the order (I1) | the day it arrives (order ~20 Nov) | mass (1 g scale), L × W × H (mm), resting voltage per cell entered in `team/E2/pack_log.csv`; E2 re-runs `energy_claims.py` | `T-E2-WEIGH` → `CL-E2-PACK-MASS`; A3 replaces the 550 g line; CG and gate re-run |
| L3 | Weigh the **first carbon tube** on arrival (spar 22×20×1000 `WNG-E03`; motor tubes when they come) | same | the day it arrives | mass (1 g scale) and length to A3 | `T-A3-WEIGH-PARTS`; spar line 102 g is `CALC` |

How to run L1: `redesign/fusion/README.md` steps 1–6 (UTILITIES > ADD-INS > Scripts and Add-Ins, add the folder
`redesign/fusion/BuildAll`, Run; `TARGET` stays `auto`). Any line marked FAIL or ERROR in the summary goes to A5
unchanged. Do not fix geometry in Fusion by hand.

### What the weights decide (act on these the same day)

| Measured | Threshold | Meaning | Action |
|---|---|---|---|
| Pack mass | 546–556 g (Ovonic 120C EC5 listing 551 ± 5 g, D-64) | as carried | none; log it in `team/E2/pack_log.csv` |
| Pack mass | 557–592 g | still under the D-64 acceptance line `CL-A1-PACK-ACCEPT` (592.6 g: the 100 g first-build overrun stays covered); CG moves forward about 0.03 mm per gram, re-trimmed by the spacer station (A3 re-runs) | A3 re-runs; station from the roll-up |
| Pack mass | > 592.6 g | the overrun is no longer covered (gate margin < 100 g after growth) | return the pack or A1 picks a mass lever (D3's fins levers, harness return) before the build; also check the 10 AWG leads (12 AWG → stop, E2 / F1) |
| Pack length | > 135 mm (+3 mm tolerance) | the crush-stack room shrinks by half the excess (most forward centroid −0.0379 m at 135 mm) | D2 and A1 re-check the pod station |
| Spar mass | > 112 g (CALC 102 g + 10 % growth) | growth beyond what the wing allocation carries | A3 moves the wing line to `WEIGHED`; any excess comes from A1's reserve (50 g cover) |

## 2. Pod station: the D-17 rule (closed by D-24, kept for the record)

**Outcome (A1-R3, CHANGE-LOG D-24):** B3 published the R1 range, 0.050–0.055 m (`CL-B3-CG-FWD` 0.0499,
`CL-B3-CG-AFT` 0.0553, target 0.0526). The pack-centred CG 0.0515 m is inside it, so neither part of the rule fires:
the pod stays at the D-08 layout, the pack's nominal centroid moves to x −0.001 m (4 mm aft of the old pod centre),
and the −0.125 m fallback, `CALC-A1-POD-RULE` and the `ASM-A1-POD-*` assumptions are retired (replaced by
`CALC-A1-CG-RANGE`). The preview below was wrong about the mechanism: at R1 the forward limit is set by elevon
trim (≤ 12.5° at CLmax), not by static margin, and it moved 10 mm aft. The pod nose shell alone later grew 10 mm
to −0.115 m for the crush block (D-25); that is not a station move.

### The rule as it stood at A1-R2

D-17 held the pod nose at x = −0.105 m until B3 re-derived the CG range at R1 geometry (CR-A1-10), and moved it to
−0.125 m "if the re-derived aft limit is < 0.051 m". The 0.051 m was A3's pack-centred CG at the time. With the
A3-R3 roll-up it was 0.0519 m, and A3 had shown (CR-A3-11) that the held station failed for a second reason: the
pack could not reach the then CG target inside the nose wall. The rule was re-stated in two parts, each a claim:

| Part | The pod moves to −0.125 m when | Claim (value today) | Today, on B3's stored (R0) range |
|---|---|---|---|
| 1 | B3's R1 aft limit `CL-B3-CG-AFT` < the CG with the pack centred at −0.105 m | `CL-A1-POD-TRIGGER` = **0.0519 m** | 0.0491 < 0.0519 → fires |
| 2 | the pack must sit further ahead of the pod centre than the nose wall allows to reach `CL-B3-CG-TARGET` | `CL-A1-POD-HELD-ROOM` = **−2.2 mm** (needs 29.2 mm, room 27.0 mm with a 3 mm wall) | fires (`FAIL`) |

Both parts read B3's claims directly, so they recompute the moment B3 re-runs `sc_analysis.py` at R1. A1 acts
then, not before (no station moves twice).

### The fallback station is feasible on every check A1 can run now

| Check at x_le −0.125 m, pack centred | Value | Limit | Status |
|---|---|---|---|
| CG x, pack centred (`CL-A1-POD-ALT-AFT`) | 0.0448 m | ≤ 0.0491 m (aft) | `UNVERIFIED` (+9 %, R0 range) |
| Margin to the forward limit (`CL-A1-POD-ALT-FWD`) | +5.0 mm | ≥ 0 (0.0397 m) | `UNVERIFIED` |
| Forward pack slide inside a 3 mm nose wall (`CL-A1-POD-ALT-PACK-ROOM`) | 27 mm (aft 27 mm) | ≥ 0 | `MODELLED` |
| Box slack along the chord, pitot off (`CL-A1-POD-ALT-BOX`) | 10 mm (30 mm today) | ≥ 0 | `MODELLED` |
| Pitot static error (B4) | about 1.7 % | ≤ 2 % | `UNVERIFIED` (B4) |

The pod group (pod, power, avionics: 763 g, `ASM-A1-POD-GROUP`) moves the CG 0.36 mm per mm; 20 mm forward gives
−7.1 mm. The heavy 680 g pack then sits at the forward limit and is slid aft, which the 27 mm aft room allows.

### Preview of B3's R1 re-run (not B3's result)

The proof build re-runs B3's stored functions with R1 parameters. `CALC-B3-NP.xnp` re-runs to 0.0674 m (stored
0.0641), which with SM 5 % at c 0.32 gives an aft limit near **0.0514 m**. That is above the literal 0.051 m of D-17
but below 0.0519 m, so part 1 would still fire by about 0.5 mm, and part 2 fires on any target near mid-range.
This is a preview: B3's script is being edited (two calcs do not run in the build) and the CG limits there do not
yet run. **A1 does not move the pod on the preview.** Expected outcome: the pod moves to −0.125 m when B3 publishes.

### Interim until B3 publishes (answers CR-A3-11)

A3 carries the pack **26 mm** ahead of the pod centre (A3 option a: 3 mm nose wall, CG 0.0448 m, inside the R0
range). Option (b), pod to −0.110 m, is not taken: if the rule fires the pod goes to −0.125 m in one move. D2 draws
the pod nose and tray so the station is a single parameter (`pod.x_le_m`); D3, D1 and C3 do not freeze anything
that depends on the pod station.

### When B3 publishes, A1 does this (one sitting)

1. Re-run `frame_claims.py`; read `CL-A1-POD-TRIGGER` against the new `CL-B3-CG-AFT` and `CL-A1-POD-HELD-ROOM`.
2. If either part fires: `params.json` `pod.x_le_m` −0.105 → −0.125, `avionics.pitot_tip_xyz_m` x −0.185 →
   −0.205, `transport.envelope_props_off_m` 0.47 → 0.49; CHANGE-LOG entry closing D-17; CR to A3 (pack centred),
   A5 (skeleton), D2, B4 (pitot), D7 (box), A4 (interface plan).
3. If neither fires: D-17 closes with the pod held and the pack at A3's `CL-A3-PACK-X-REQ`.
4. `python -I redesign/proofs/build_graph.py`; update `README.md` stations and this file.
