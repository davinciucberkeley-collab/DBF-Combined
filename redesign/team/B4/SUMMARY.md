# B4 rotor / propeller aero: summary

**CDR fix round, 2026-11-13 (CDR-15; `PROPS.md` §9).** 11×7E added to the trade from APC's PER3 file: cruise pack power
−22.5 % at 16 m/s and −23.3 % at 17 m/s against the 11×5.5MR (177 vs 231 W on B4's model), hover +6.0 %, η 0.61 vs 0.46.
**No 11×7EP (thin-electric pusher) is listed by APC**, so a flight set cannot be bought today; the 11×5.5E / EP pair saves
about 9 %. Second finding: at `THR_MAX` 70 B4's model reaches 24.8 m/s with the MR prop (VH 21.8; F4 carries 21.3):
CR-B4-29. 89 claims; the two by-design fails are unchanged (`CL-B4-RPM-MAX-FULL`, `CL-B4-SF-RPM`).

Status `PROPOSED`, 2026-11-10, re-run at **R4**. Full report: [`PROPS.md`](PROPS.md) (R4 clearance work in §0a
and §3.0). Calculations: `props.py` → `claims.json` (74 claims, 4 planned tests); figures: `figures.py` → `out/`;
data: `data/` (APC PER3 for five props, UIUC for two). R4 inputs: prop plane x −0.0077 (hub x taken straight
from params), `cant_sense_UR` −1 (D-52, now matches F4 and `ASM-B4-WAKE-SENSE`), L/D 6.2, pitot tip x −0.21.
`build_graph.py` shows no B4 drift or error. It does show downstream drift in B3 (`CALC-B3-HOVER`) on
`CL-B4-YAW`, so B3 re-runs. Every claim stays `UNVERIFIED` until the stand runs.

**Decision (unchanged).** Fly the **APC 11×5.5MR / 11×5.5MRP**. The 11×5.5E/EP is the alternate.

## Simulation round (2026-11-10): [`SIMULATION-REPORT.md`](SIMULATION-REPORT.md)

| Result | Hand → sim | Unit | Claim | Status |
|---|---|---|---|---|
| Tube + board Cd on D, hover (SU2 SA, 3 grids, GCI 3.4 %; cylinder validation +0.6 %) | 1.48 → 0.599 | — | `CL-B4-SIM-CD-TUBEFIN` | `MODELLED` |
| Download factor (limit 1.06) | 1.038 → 1.025 | — | `CL-B4-SIM-DOWNLOAD` | `MODELLED` |
| Upper-prop hover thrust / rpm, A3 2.436 kg, split 1.216 | 6.81 / 5 416 → 7.00 / 5 491 | N / rpm | `CL-B4-SIM-T-UPPER`, `-RPM-UPPER` | `MODELLED` |
| T/W at the cap / upper headroom, 680 g pack | 3.40 / 2.78 | — | `CL-B4-SIM-TW-CAP`, `-HEADROOM` | `MODELLED` |
| H-force per prop in the pitch-over (new, to B3) | 0.43 (0.88 at hover thrust) | N | `CL-B4-SIM-H-MAX`, `-H-HOVERT` | `MODELLED` |
| Cruise section Cd vs B1's build-up | 0.995 × | — | `CL-B4-SIM-CD-B1-RATIO` | `CHECKED` |
| Blade to CF tube on the settled CAD | 21.1 (limit 25) `FAIL` | mm | `CL-B4-GAP-TUBE-ENV` | `CHECKED`; CR-B4-25 |

## R4 action item: prop-tip-to-wing clearance

The "≈ 23 mm" figure (wing skin 0.163 m from the canted axis, against R 0.1397 m) **does not reproduce**.
`CALC-B4-TIP-WING` measures the exact 3D distance from every S5010 skin point to the blade's swept volume. It
uses radius R about the 7° axis and E1's envelope, 10 mm forward and 6 mm aft of the hub mid-plane. The nearest
the wing comes to the axis anywhere is 0.1708 m. The points that set the radial minimum lie 35–90 mm behind the
blade, so a radial-only number is not a clearance.

| Clearance (limit 25 mm) | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Blade to wing upper skin, UR/UL (closest at x 0.023, z 0.015 m) | **34.2** (+37 %) | mm | `CL-B4-TIP-WING` | `CHECKED` (E1 CAD probe 34.1–34.2) / `UNVERIFIED` |
| Blade to wing lower skin, LR/LL | 42.2 (+69 %) | mm | `CL-B4-TIP-WING-LOWER` | `MODELLED` |
| Wing upper, symmetric ±10 mm blade / radial inside the KO-PROP band | 33.6 / 31.2 | mm | `-SYM`, `-KO` | `MODELLED` |
| **Blade to CF motor tube (swept volume, CR-E1-46a)** | **21.1 (`FAIL`, −16 %)** | mm | `CL-B4-GAP-TUBE-ENV` | `CHECKED` (= `CL-E1-TIP-GAP-TUBE`) |
| Tube / wing with the mount face 5 mm forward (E1 CR-E1-44) | 26.1 / 35.8 | mm | `CL-B4-GAP-TUBE-FIX5`, `CL-B4-TIP-WING-FIX5` | `MODELLED` |
| Hub mid-plane to the tube face (old metric) / collars | 27.1 / 36.2 | mm | `CL-B4-GAP-TUBE`, `-COLLAR` | `MODELLED` |

**Result:** the wing does not constrain the prop station. The tube does, and A1's CR-D3-26 decision fixes it
(face_ahead 0.0075 m, or 5° cant). See CR-B4-22 (A5) and CR-B4-23 (A1).

## Key numbers (11×5.5MR, 2.6 kg)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover per prop: thrust (÷ cos 7°) / rpm / shaft power / FM | 6.81 / 5 416 / 64.5 / 0.711 | N / rpm / W / — | `CL-B4-HOVER-*`, `CL-B4-FM` | `UNVERIFIED` |
| Cruise per prop (1.03 N, 16 m/s, L/D 6.2): J / η_prop / pack power | 0.578 / 0.443 / 195 (11×4.5MR 239) | — / — / W | `CL-B4-CRUISE-*` | `UNVERIFIED` |
| Full-throttle rpm on a fresh pack / output cap / T/W at the cap | 10 637 / 0.85 / 3.01 | rpm / — / — | `CL-B4-RPM-MAX-FULL` (`FAIL` → cap), `-SPIN-MAX`, `-TW-CAP` | `UNVERIFIED` |
| Download factor, modelled (design value kept) | 1.038 / 1.048 peaked (1.06) | — | `CL-B4-DOWNLOAD`, `-HIGH` | `UNVERIFIED` |
| Hover yaw factor, body axis (reaction + fin), at 7° / half fin force | 1.785 / 1.392 | × reaction torque | `CL-B4-YAW`, `-LOW` | `UNVERIFIED` |
| Yaw moment per N of differential thrust: full / half fin credit | 0.075 / 0.069 (B3 needs 0.048) | m | `CL-B4-K-YAW`, `-LOW` | `UNVERIFIED` |
| Side force on each half-fin, hover / root moment | 0.56 / 0.082 | N / N·m | `CL-B4-SWIRL-FIN`, `-M` | `UNVERIFIED` |
| Elevon tip clear of the hover slipstream / wing-skin wake gap | 61 / 45 | mm | `CL-B4-ELEVON-HOVER`, `CL-B4-WING-GAP` | `UNVERIFIED` |
| Pitot error at (−0.21, −0.046, 0.045), transition / cruise | 1.75 % / 0.30 % (limit 2 %) | % | `CL-B4-PITOT`, `-CRUISE` | `UNVERIFIED` (13 % margin) |
| Cruise drag of the fin hardware, all / not in B1 rev 3 | 0.62 (ΔCD0 0.011) / 0.37 (ΔCD0 0.0064) | N | `CL-B4-ITEMS-DRAG`, `-NOT-B1` | `UNVERIFIED` |
| Vertical tip gap / max descent / BPF hover, at the cap | 94 mm / 1.88 m/s / 181, 311 Hz | — | `CL-B4-GAP-V`, `-DESCENT`, `-BPF` | `UNVERIFIED` |

## Open issues

- **`CL-B4-GAP-TUBE-ENV` fails** until A1 takes CR-E1-44 or a 5° cant. B4 re-runs on the new `x_prop_plane_m`.
- No measured data exist for any MR prop. `T-B4-STAND` settles it. `T-B4-INSTALLED` now also gauges the blade
  against the wing skin and the tube (25 mm printed gauge).
- The fin side force is uncertain by about 2×. B3 sizes on `CL-B4-YAW-LOW` until `T-B4-YAW` runs.
- The blade envelope (+10 / −6 mm) is E1's `ASM-E1-BLADE-ENV` (`UNVERIFIED`). A ±1° cant print error moves the
  wing-side tip by about ±2.1 mm.
- CR-E1-46b (move from `ASM-E1-PACK` to `ASM-E1-PACK-CELLS` + `electrical.r_ext_mohm`) is not done in this pass.
  It shifts the electrical numbers by about +2.5 mΩ.
- Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (R4 rows CR-B4-22 to -24).
