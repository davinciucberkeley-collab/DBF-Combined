# B4 rotor / propeller aero: summary

Status `PROPOSED`, 2026-11-09. Full report: [`PROPS.md`](PROPS.md). Calculations: `props.py` → `claims.json`
(44 claims, 4 planned tests); figures: `figures.py` → `out/`; data: `data/` (APC PER3 tables for five props, UIUC
measurements for two; S5010 section read from `team/B2/airfoils/`). Re-run 2026-11-09 at R2 geometry (motor tube at
x 0.045 m, prop plane at x −0.005 m, half-fins 0.275 m, cruise 16 m/s at L/D 5.6, pitot tip at x −0.185 m):
`build_graph.py` reports no B4 drift or error. The build as a whole still fails on drift in A5, B1, B2, B3, C1, E1
and J1. All claims are `UNVERIFIED` until the thrust stand runs.

**Decision.** Fly the **APC 11×5.5MR / 11×5.5MRP**, as E1 proposed in CR-E1-06. The 11×5.5E/EP is the alternate.
The 11×4.7SF is rejected because its rpm limit is 5 909 rpm. The 12×4.5MR is rejected on cruise power and rpm.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover per prop: thrust / rpm / shaft power / FM | 6.76 / 5 396 / 63.8 / 0.711 | N / rpm / W / — | `CL-B4-HOVER-*`, `CL-B4-FM` | `UNVERIFIED` |
| Disk loading at the gate | 110 | N/m² | `CL-B4-DL` | `UNVERIFIED` |
| Cruise per prop (1.14 N, 16 m/s): J / η_prop | 0.573 / 0.465 (11×4.5MR: 0.374) | — | `CL-B4-CRUISE-J`, `-ETA` | `UNVERIFIED` |
| Cruise pack power, 4 motors | 205 (11×4.5MR: 249) | W | `CL-B4-CRUISE-W` | `UNVERIFIED` |
| PER3 vs UIUC measured (2 APC 11 in props): cruise η / static FM | ±3.5 % / −4.5 % | — | `CALC-B4-XCHECK` | `CHECKED` against data |
| Full-throttle rpm on a fresh pack, no cap (APC MR limit 9 545) | 10 637 | rpm | `CL-B4-RPM-MAX-FULL` | `FAIL` → output cap 0.85 (`CL-B4-SPIN-MAX`) |
| T/W at the rpm cap, installed | 3.03 | — | `CL-B4-TW-CAP` | `UNVERIFIED` |
| Download factor, modelled (design value kept) | 1.034–1.043 (1.06) | — | `CL-B4-DOWNLOAD`, `-HIGH` | `UNVERIFIED` |
| Slipstream clearance to the wing skin (disc edge 28 mm above the S5010 crest) | 45 (wing download 0) | mm | `CL-B4-WING-GAP` | `UNVERIFIED` |
| Swirl on each half-fin in hover: side force / root moment | 0.94 / 0.11 | N / N·m | `CL-B4-SWIRL-FIN`, `-M` | `UNVERIFIED` |
| Slipstream drag on each motor tube in hover | 0.11 (0.15 peaked) | N | `CL-B4-TUBE-LOAD` | `UNVERIFIED` |
| Elevon tip clear of the hover slipstream | 33 | mm | `CL-B4-ELEVON-HOVER` | `UNVERIFIED` |
| Hover yaw authority left by fin swirl recovery / with 3° cant | 0.48 / 1.65 | × isolated | `CL-B4-YAW`, `-CANT` | `UNVERIFIED` |
| Pitot error, boom tip at x = −0.185 m (worst case, transition) | 1.66 (limit 2; was 0.75 at R0 geometry) | % | `CL-B4-PITOT` | `UNVERIFIED` |
| Max vertical descent (vortex-ring onset 0.28 v_h) | 1.88 | m/s | `CL-B4-DESCENT` | `UNVERIFIED` |
| Vertical prop tip gap (≥ 25 mm) | 101 | mm | `CL-B4-GAP-V` | `UNVERIFIED` |
| Hover 1P / BPF; BPF at the cap | 90 / 180; 311 | Hz | `CL-B4-BPF`, `-BPF-MAX` | `UNVERIFIED` |

## Findings others depend on

| Finding | Effect | To |
|---|---|---|
| The props sit 0.19 m off the wing plane, and the hover slipstream misses the elevons by 33 mm and the wing skin by 45 mm | No elevon authority at zero airspeed; all hover control comes from the motors | B3, F4, B1 |
| The fin acts as a stator and recovers about half of the prop swirl | Hover yaw (about body x) drops to ≈ 0.48 ×; E1's 0.149 N·m becomes ≈ 0.07 N·m | B3, E1 |
| A 3° tangential motor cant restores yaw authority to 1.6 × for 0.14 % of thrust | Printed mounts with a cant | D3, B3, F4 |
| Each half-fin carries 0.94 N of swirl side force (0.11 N·m at the skin); both halves of one fin push the same way | Fin-to-tube and fin-to-skin bonds, saddle | C4, D3 |
| Both MR props exceed APC's rpm limit at full throttle on a fresh pack | Cap the output at ≈ 0.85 and check with rpm telemetry; T/W stays 3.0 | F4, E1 |
| PER3 over-predicts static FM by about 4.5 % | Hover shaft power about 5 % above the PER3 value | E1, B1 |
| Pitot boom on the pod nose: 1.66 % worst case with the props at x −0.005 (the tip is near the peak of the props' upstream field, about 0.25 m ahead of them); a longer boom does not help below about 0.6 m | Keep the 80 mm boom (`POD-006`); thrust-dependent part 0.21 m/s | D2, F3, A1 |

## Open issues

- No measured data exist for any MR prop: UIUC has none. `T-B4-STAND` (A/B with the 11×4.5MR) settles it.
- The fin-swirl estimate (low-aspect-ratio plate) is uncertain by about 2×. `T-B4-YAW` measures it.
- The download model treats the half-fin as a flat sheet and does not model entrainment suction on the wing skin
  28 mm below the disc edge. Hold 1.06 until `T-B4-INSTALLED` (now with a wing strip). Re-run when D3 draws the
  fin-tube joint and the saddle.
- The pitot margin fell from 63 % to 17 % with the R2 geometry. If the pod moves to x −0.125 (D-17), the tip moves to
  −0.205 and the error rises to about 1.7 %. Still inside 2 %.
- In transition the props run at high incidence, and the pitot under-reads at high angle of attack. Neither is
  modelled here: F4 and SITL.
- Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (A1, E1, B1, B3, D2/F3, D3, C4, F4, H1, E3, I1).
