# B4 rotor / propeller aero: summary

Status `PROPOSED`, 2026-11-09, re-run at **A1-R3** (CR-A1-29). Full report: [`PROPS.md`](PROPS.md).
Calculations: `props.py` → `claims.json` (66 claims, 4 planned tests); figures: `figures.py` → `out/`; data:
`data/` (APC PER3 for five props, UIUC for two). R3 inputs: 7° cant, prop plane x −0.0082, pitot tip
(−0.195, −0.046, 0.045), collars, ears, braces and ESC pads from D3's `fin_detail.*`, 0.21 m half-fins, L/D 6.9,
half-fin ids `FIN-001-UR/UL/LR/LL`. `build_graph.py` shows no B4 drift or error. It does show downstream drift
in B3, C4 and E3 on the new B4 values, so those roles re-run. All claims are `UNVERIFIED` until the stand runs.

**Decision (unchanged).** Fly the **APC 11×5.5MR / 11×5.5MRP**. The 11×5.5E/EP is the alternate.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover per prop: thrust (÷ cos 7°) / rpm / shaft power / FM | 6.81 / 5 416 / 64.5 / 0.711 | N / rpm / W / — | `CL-B4-HOVER-*`, `CL-B4-FM` | `UNVERIFIED` |
| Cruise per prop (0.92 N, 16 m/s, L/D 6.9): J / η_prop / pack power | 0.583 / 0.421 / 185 (11×4.5MR 229) | — / — / W | `CL-B4-CRUISE-*` | `UNVERIFIED` |
| Full-throttle rpm on a fresh pack / output cap / T/W at the cap | 10 637 / 0.85 / 3.01 | rpm / — / — | `CL-B4-RPM-MAX-FULL` (`FAIL` → cap), `-SPIN-MAX`, `-TW-CAP` | `UNVERIFIED` |
| Download factor, modelled with the R3 hardware (design value kept) | 1.038 / 1.049 peaked (1.06) | — | `CL-B4-DOWNLOAD`, `-HIGH` | `UNVERIFIED` |
| **Hover yaw factor, body axis (reaction + fin)**, at 7° / half fin force | **1.79 / 1.40** (R2: 0.48) | × reaction torque | `CL-B4-YAW`, `-LOW` | `UNVERIFIED` |
| Yaw moment per N of differential thrust at 7°: full / half / no fin credit | 0.075 / 0.069 / 0.062 (B3 needs 0.048) | m | `CL-B4-K-YAW`, `-LOW` | `UNVERIFIED` |
| Side force on each half-fin, hover, at 7° / root moment | 0.57 / 0.083 (R2: 0.94 / 0.11) | N / N·m | `CL-B4-SWIRL-FIN`, `-M` | `UNVERIFIED` |
| Blade tip over the tube face, canted disc / collars | **27.3** / 36.0 (limit 25; uncanted 40.2) | mm | `CL-B4-GAP-TUBE`, `-COLLAR` | `UNVERIFIED` (9 % margin) |
| Elevon tip clear of the hover slipstream (wake leans away) / if the map were mirrored | 61 / 2.5 | mm | `CL-B4-ELEVON-HOVER`, `-ALT` | `UNVERIFIED` |
| Wing-skin clearance / ESC pad edge in the wake | 45 mm / 0.89 r_s | — | `CL-B4-WING-GAP`, `CL-B4-ESC-WASH` | `UNVERIFIED` |
| **Pitot error at (−0.195, −0.046, 0.045)**, transition / cruise | **1.72 % / 0.27 %** (limit 2 %) | % | `CL-B4-PITOT`, `-CRUISE` | `UNVERIFIED` (14 % margin) |
| Cruise drag of the R3 fin hardware, all / not in B1 rev 3 | 0.64 (ΔCD0 0.011) / 0.39 (ΔCD0 0.0067) | N | `CL-B4-ITEMS-DRAG`, `-NOT-B1` | `UNVERIFIED` |
| Vertical tip gap / max descent / BPF hover, at the cap | 94 mm / 1.88 m/s / 181, 311 Hz | — | `CL-B4-GAP-V`, `-DESCENT`, `-BPF` | `UNVERIFIED` |

## Findings others depend on

| Finding | Effect | To |
|---|---|---|
| R0–R2 had the hover-yaw sign wrong. The fin's swirl side force acts 0.16 m from the body x-axis and adds to the reaction torque, so the factor is 1.79, not 0.48 | B3's yaw authority roughly triples; its cant requirement falls from 6.1° to 2.6° (B3 model, mid) | B3, A1, F4 |
| 5° is the smallest cant that meets B3's yaw need with no fin credit; 7° gives 1.30× with none | A1 may hold 7° or return to 5°: 5° gives +4.3 mm tube gap and half the thrust cost (0.38 % vs 0.75 %) | A1, B3, D3 |
| D3's `cant_sense_UR +1` is the opposite of F4's motor map. Printed that way, the differential-thrust yaw falls to about zero (k −0.003 m) | Swap mounts A and B (D3's own fallback). H1/F4 check the sense on the motor test before the first hover | D3, F4, H1 |
| At 7° the canted disc's wing-side edge swings 13 mm aft. The blade passes 27 mm in front of the tube (0.098 D) | Meets 25 mm. Do not move the prop plane aft; D3 confirms in CAD. Expect a stronger 2P tone | D3, C4, A1 |
| The ears, mount collars and ESC pads add ΔCD0 0.0067 that B1 does not carry; the ears alone cost 0.21 N | B1 adds them. D3 can turn the pinch ear aft and sweep the brace ear along x to save ~0.2 N (≈ 10 W) | B1, D3 |
| Pitot moved to the left channel: 1.72 %; the thrust-dependent part is 0.23 m/s | F3 carries 0.23 m/s in the 0.5 m/s RSS budget | F3, D2 |
| Hover rpm 5 416, thrust 6.81 N, torque 0.114 N·m, cruise rpm 5 894 | C4 (Campbell) and E3 (thermal) re-run | C4, E3, E1 |

## Open issues

- No measured data exist for any MR prop. `T-B4-STAND` (A/B with the 11×4.5MR) settles it.
- The fin side force is uncertain by about 2× (low-AR plate on an end wall, actuator-disk swirl). Until
  `T-B4-YAW` runs, B3 sizes on `CL-B4-YAW-LOW`. `T-B4-YAW` now measures the fin's side force and centre of
  pressure, because a motor-axis torque cell would read only 0.16 (`CL-B4-F-AXIS`).
- The blade-to-tube gap ignores blade thickness and flap, about 1–2 mm at the tip. `T-B4-INSTALLED` measures it.
- ESC dimensions are assumed (`ASM-B4-ESC`). The brace Cd of 1.2 is at the high end (B1 uses 0.8).
- Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (R3 rows CR-B4-13 to CR-B4-21).
