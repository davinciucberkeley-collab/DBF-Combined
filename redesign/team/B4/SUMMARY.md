# B4 rotor / propeller aero: summary

Status `PROPOSED`, 2026-11-09. Full report: [`PROPS.md`](PROPS.md). Calculations: `props.py` → `claims.json`
(38 claims, 4 planned tests); figures: `figures.py` → `out/`; data: `data/` (APC PER3 tables for five props, UIUC
measurements for two). `build_graph.py`: "OK: every stored number re-computes". All claims are `UNVERIFIED` until
the thrust stand runs.

**Decision.** Fly the **APC 11×5.5MR / 11×5.5MRP**, as E1 proposed in CR-E1-06. The 11×5.5E/EP is the alternate.
The 11×4.7SF is rejected because its rpm limit is 5 909 rpm. The 12×4.5MR is rejected on cruise power and rpm.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover per prop: thrust / rpm / shaft power / FM | 6.76 / 5 396 / 63.8 / 0.711 | N / rpm / W / — | `CL-B4-HOVER-*`, `CL-B4-FM` | `UNVERIFIED` |
| Disk loading at the gate | 110 | N/m² | `CL-B4-DL` | `UNVERIFIED` |
| Cruise per prop (1.08 N, 15 m/s): J / η_prop | 0.568 / 0.474 (11×4.5MR: 0.383) | — | `CL-B4-CRUISE-J`, `-ETA` | `UNVERIFIED` |
| Cruise pack power, 4 motors | 181 (11×4.5MR: 219) | W | `CL-B4-CRUISE-W` | `UNVERIFIED` |
| PER3 vs UIUC measured (2 APC 11 in props): cruise η / static FM | ±3.5 % / −4.5 % | — | `CALC-B4-XCHECK` | `CHECKED` against data |
| Full-throttle rpm on a fresh pack, no cap (APC MR limit 9 545) | 10 637 | rpm | `CL-B4-RPM-MAX-FULL` | `FAIL` → output cap 0.85 (`CL-B4-SPIN-MAX`) |
| T/W at the rpm cap, installed | 3.03 | — | `CL-B4-TW-CAP` | `UNVERIFIED` |
| Download factor, modelled (design value kept) | 1.036–1.046 (1.06) | — | `CL-B4-DOWNLOAD` | `UNVERIFIED` |
| Elevon tip clear of the hover slipstream | 26 | mm | `CL-B4-ELEVON-HOVER` | `UNVERIFIED` |
| Hover yaw authority left by fin swirl recovery / with 3° cant | 0.47 / 1.64 | × isolated | `CL-B4-YAW`, `-CANT` | `UNVERIFIED` |
| Pitot error, pod nose tip at x = −0.10 m (worst case) | 0.75 (limit 2) | % | `CL-B4-PITOT` | `UNVERIFIED` |
| Max vertical descent (vortex-ring onset 0.28 v_h) | 1.88 | m/s | `CL-B4-DESCENT` | `UNVERIFIED` |
| Vertical prop tip gap (≥ 25 mm) | 101 | mm | `CL-B4-GAP-V` | `UNVERIFIED` |
| Hover 1P / BPF; BPF at the cap | 90 / 180; 311 | Hz | `CL-B4-BPF`, `-BPF-MAX` | `UNVERIFIED` |

## Findings others depend on

| Finding | Effect | To |
|---|---|---|
| The props sit 0.19 m off the wing plane, and the hover slipstream misses the elevons by 26 mm | No elevon authority at zero airspeed; all hover control comes from the motors | B3, F4, B1 |
| The fin acts as a stator and recovers about half of the prop swirl | Hover yaw (about body x) drops to ≈ 0.47 ×; E1's 0.149 N·m becomes ≈ 0.07 N·m | B3, E1 |
| A 3° tangential motor cant restores yaw authority to 1.6 × for 0.14 % of thrust | Printed mounts with a cant | D3, B3, F4 |
| Both MR props exceed APC's rpm limit at full throttle on a fresh pack | Cap the output at ≈ 0.85 and check with rpm telemetry; T/W stays 3.0 | F4, E1 |
| PER3 over-predicts static FM by about 4.5 % | Hover shaft power about 5 % above the PER3 value | E1, B1 |
| Pitot on the pod nose: under 1 % prop-induced error; the inboard wing LE is worse | `POD-006` mount, tip 80 mm ahead of the pod | D2, F3 |

## Open issues

- No measured data exist for any MR prop: UIUC has none. `T-B4-STAND` (A/B with the 11×4.5MR) settles it.
- The fin-swirl estimate (low-aspect-ratio plate) is uncertain by about 2×. `T-B4-YAW` measures it.
- The download model treats the fin as a flat sheet, but the fin-tube joint is unresolved (P25). Re-run it when D3
  draws the fin.
- In transition the props run at high incidence, and the pitot under-reads at high angle of attack. Neither is
  modelled here: F4 and SITL.
- Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (A1, E1, B1, B3, D2/F3, D3, C4, F4, H1, E3, I1).
