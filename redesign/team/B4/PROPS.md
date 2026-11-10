# Props and rotor aero (B4)

Status `PROPOSED`, 2026-11-09, re-run at **A1-R3** (CR-A1-29). Everything below is `UNVERIFIED` until the thrust
stand runs (`T-B4-STAND`, `T-B4-INSTALLED`, `T-B4-YAW`). Calculations: `team/B4/props.py` → `claims.json`
(66 claims, 4 planned tests), `out/props_results.json`. Figures: `team/B4/figures.py`. Data: `team/B4/data/` (APC
PER3 tables for five props, UIUC measurements for two). Python standard library only. `props.py` now also reads
D3's `subsystems/fins/params.json` (`P:fin_detail.*`) for the collars, ears, braces and ESC pads.

**Verdict.** Fly the **APC 11×5.5MR / 11×5.5MRP** (unchanged, agrees with E1). At R3 it costs 3 % more hover power
than the 11×4.5MR and saves 19 % in cruise. Five installation results matter more than the prop choice:
1. **The hover-yaw sign was wrong in R0–R2.** The fin's swirl side force acts 0.16 m from the body x-axis and turns
   the airframe *with* the reaction torque. Hover yaw authority is **1.79 ×** the isolated reaction torque at 7°
   cant (1.40 × with half the modelled fin force), not 0.48 ×. Add the cant and the total is 4.5 ×.
2. **The 7° cant (D-27) is more than yaw needs.** With no fin credit at all, 5° meets B3's yaw requirement. At 7°
   the canted disc swings its wing-side edge 13 mm toward the tube: the blade tip passes **27 mm** in front of
   the tube face (limit 25 mm, `CL-B4-GAP-TUBE`).
3. **The cant sense has to match F4's spin map, and D3's print sense is the opposite.** If the mounts are
   printed as D3's `cant_sense_UR +1` with F4's rotations, differential-thrust yaw drops to about zero.
4. **The pitot at R3, tip (−0.195, −0.046, 0.045), reads 1.72 % high in transition** (limit 2 %, margin 14 %).
   Moving it into the left channel costs 0.06 points against the centreline.
5. **The new fin hardware adds 0.64 N of cruise drag** (ΔCD0 0.011; 17 % of cruise drag, 32 W). B1 rev 3
   already carries the braces and station collars. The ears, mount collars and ESC pads (ΔCD0 0.0067) are not
   carried, and the ears alone cost as much as the braces. Hover download is 1.038 (keep 1.06).

## 0. What changed at R3

| Input (params / D3) | R2 | R3 | Effect on B4 numbers |
|---|---|---|---|
| `propulsion.stations.cant_deg` | 3° (B4 assumption) | **7°** (D-27) | hover thrust per prop ÷ cos 7° (+0.75 %); wake leans 6° (0.106 m/m away from the wing, 0.063 m/m inboard); fin incidence down; disc tilts toward the tube |
| `x_prop_plane_m` | −0.005 | **−0.0082** (D-28) | tube 3 mm further behind the disc; hub then moves 4.1 mm toward the wing and 0.3 mm aft along the canted shaft (39 mm stack) |
| `avionics.pitot_tip_xyz_m` | (−0.185, 0, 0.045) | **(−0.195, −0.046, 0.045)** (D-25) | worst error 1.66 → 1.72 % |
| Fin hardware (`fin_detail.*`, CR-D3-15) | not modelled | tube ends at z 0.172; mount collar Ø26 × 12, station collar Ø25.2 × 12, pinch ear 9 × 12 mm, brace ear 10 × 12 mm, brace 10 × 3 × 143 mm, ESC pad 46 × 28 mm at z 0.118 | in the download and a new cruise-drag calc |
| `fins.half_height_m`, top edge | 0.19, flat | **0.21**, top edge from the collar top (z 0.160) at the LE to 0.21 at the TE | fin wetted span 82–89 mm in the wake |
| `fins.layers` | 2 (ASM-B4-FIN-T 10 mm) | 2 × 4.8 mm from params (ASM-B4-FIN-T retired) | base drag 0.041 N |
| `performance.ld_cruise` | 5.6 | **6.9** (D-36) | cruise thrust 1.14 → 0.92 N per prop |
| Half-fin ids | FIN-001-L/R, FIN-002-L/R | **FIN-001-UR/UL/LR/LL** (D-26) | claim `parts` |

## 1. Prop selection

Conditions: 2.6 kg gate, download 1.06 and cant 7° (6.81 N per prop in hover), 16 m/s cruise at L/D 6.9 (0.92 N
per prop), ρ 1.225 kg/m³. Props are from APC PER3. Electrical power uses E1's motor constants (`ASM-E1-*`); E1 owns
the electrical numbers.

| Prop | Hover rpm | FM | Hover pack W | Cruise J | η_prop | Cruise pack W | Full-throttle rpm, 14.8 V hot / APC limit | Mass | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **11×5.5MR/MRP** | 5 416 | 0.711 | 346 | 0.583 | **0.421** | **185** | 9 319 / 9 545 (+2 %) | 17 g | `PROPOSED` (selected) |
| 11×4.5MR/MRP | 5 816 | 0.718 | 336 | 0.503 | 0.333 | 229 | 9 778 / 9 545 (**−2 %**) | 17 g | stand A/B only |
| 11×5.5E/EP | 5 830 | 0.696 | 347 | 0.577 | 0.469 | 167 | 9 735 / 13 636 | 23 g | alternate |
| 11×4.7SF | 5 098 | 0.757 | 329 | 0.549 | 0.312 | 245 | 9 019 / **5 909** | 20 g | rejected: SF rpm limit |
| 12×4.5MR | 5 066 | 0.715 | 319 | 0.478 | 0.275 | 276 | 9 087 / 8 750 (−4 %) | 20 g | rejected: cruise, clearance |

- **The 11×4.7SF never flies.** Its APC limit (65 000 / D) is 5 909 rpm and hover alone needs 5 098 rpm
  (`CL-B4-SF-RPM` `FAIL`).
- **The 11×5.5E** is the most efficient cruise prop (167 W against 185 W). It is 6 g heavier per prop, has more
  rotational inertia and a 0.41 in hub. Keep it as the alternate if the stand shows the MR worse than predicted.
- **Data trust.** UIUC wind-tunnel data for two APC 11 in props sit within ±5 % of the PER3 cruise efficiency
  (ratios 0.95 and 1.05 at R3's lighter cruise thrust, `CL-B4-UIUC-ETA`, `-E`). In static thrust PER3 over-predicts
  FM by 4.5 % for both props (`CALC-B4-XCHECK`). **Plan hover shaft power about 5 % above the PER3 numbers.**

![Cruise pack power against airspeed](out/fig-b4-01-cruise-power.svg)

`FIG B4-01 — Pack power for four motors at 2.6 kg and L/D 6.9, by prop; 11×5.5MR blue, 11×4.5MR ink. Source CALC-B4-CRUISE.`

## 2. Key numbers (selected prop)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover thrust per prop / disk loading (incl. download 1.06 and cos 7°) | 6.81 / 111 | N / N/m² | `CL-B4-HOVER-T`, `CL-B4-DL` | `UNVERIFIED` |
| Hover rpm / torque / shaft power | 5 416 / 0.114 / 64.5 | rpm / N·m / W | `CL-B4-HOVER-RPM`, `-Q`, `-SHAFT` | `UNVERIFIED` |
| Hover FM (PER3; × 0.955 measured trend) | 0.711 (≈ 0.68) | — | `CL-B4-FM`, `CALC-B4-XCHECK` | `UNVERIFIED` |
| Cruise rpm / J / η_prop / shaft power (16 m/s, 0.92 N) | 5 894 / 0.583 / 0.421 / 35.1 | rpm / — / — / W | `CL-B4-CRUISE-*` | `UNVERIFIED` |
| Cruise pack power, 4 motors (E1 constants, no fin-hardware drag) | 185 (11×4.5MR: 229) | W | `CL-B4-CRUISE-W`, `-OLD` | `UNVERIFIED` |
| Full-throttle rpm, 16.8 V fresh, no cap | 10 637 (limit 9 545) | rpm | `CL-B4-RPM-MAX-FULL` | `FAIL` (cap below) |
| Output cap for ≤ 9 350 rpm on a fresh pack | 0.85 | — | `CL-B4-SPIN-MAX` | `UNVERIFIED` |
| T/W at the rpm cap (installed, cos 7°) | 3.01 (≥ 2.0) | — | `CL-B4-TW-CAP` | `UNVERIFIED` |
| Tip Mach hover / at the cap | 0.23 / 0.40 | — | `CL-B4-TIPMACH` | `UNVERIFIED` |

## 3. Installation effects

Model (R3): each wake leaves the canted hub along the shaft. The thrust side component follows F4's map (prop end
toward the wing and outboard, `ASM-B4-WAKE-SENSE`), so each hover wake leans 0.106 m/m away from the wing and
0.063 m/m inboard. Every element of the fin station is tested against the leaning slipstream radius: 200 tube
slices, both collars, both ears, 100 brace segments and 10 ESC strips. Elements in the motor-can shadow are dropped.

| Effect | Result | Consequence | Claim |
|---|---|---|---|
| Download per station: tube 0.116 N, mount + station collars 0.005, ears 0.015, brace 0.009 (51 % of its length in the wake), ESC 0.012, fin skin 0.023, fin base 0.041, foot 0.022, wing 0 | k = **1.038** (mean), 1.049 (peaked loading); 1.055 if the spin map were mirrored | **Keep 1.06** until `T-B4-INSTALLED`. The R3 hardware adds 0.004 to k | `CL-B4-DOWNLOAD`, `-HIGH`, `CL-B4-ITEMS-HOVER`, `CL-B4-TUBE-LOAD`, `CL-B4-BRACE-HOVER` |
| Wing beside the disc (disc edge 46 mm above the chord plane after the 4 mm hub shift) | mixing-layer edge 45 mm off the skin at x 0.015 (32 mm if mirrored) | no wing download modelled; entrainment suction not modelled | `CL-B4-WING-GAP`, `-ALT` |
| Hover slipstream vs elevon tip at 25° | **61 mm** clear (was 33: the wake leans away); **2.5 mm** if the spin map were mirrored | no blown elevon in hover; do not mirror the map | `CL-B4-ELEVON-HOVER`, `-ALT` |
| ESC pad in the leaning wake | outer (wing-side) edge at 0.89 r_s | still inside the slipstream; 11 % margin (D3's untilted check reads 0.87 R) | `CL-B4-ESC-WASH` |
| Cruise slipstream vs elevon | tip 6 mm inside the mixing layer at full throw | negligible | `CL-B4-ELEVON-CRUISE` |
| Rotor–rotor: vertical tip gap 94 mm (0.34 D, canted discs), lateral 0.361 m | mean thrust change < 2 % (rotor-pair data) | no correction; watch vibration | `CL-B4-GAP-V` |
| **Blade over the tube with the disc canted 7°**: the wing-side edge swings 13 mm aft | tube face **27.3 mm** at the tip (uncanted 40.2), collars 36.0 mm; 45.7 mm if mirrored | **meets 25 mm by 9 %**; below the 0.14 D (39 mm) B4 asked for in CR-B4-04 | `CL-B4-GAP-TUBE`, `-COLLAR`, `-TUBE-ALT` |
| Vortex ring state in vertical descent | v_h 6.71 m/s → onset ≈ 1.9 m/s | descent ≤ 1.5 m/s, landing 0.5 m/s (F4) | `CL-B4-DESCENT` |
| Ground effect at take-off | prop 0.376 m (2.7 R) above ground: +0.9 % | ignore | `CALC-B4-GEOM` |

![Side view at the fin station with the hover slipstream](out/fig-b4-02-slipstream.svg)

`FIG B4-02 — Side view at y = 0.32 m, 1 m = 850 px. S5010 section, motor tube at x 0.045 m and half-fins (grey). Black: canted discs. Blue: leaning hover slipstream edge (solid: momentum theory; dashed: with the mixing layer). Orange: elevon at ±25° and the pitot boom (y = −0.046, projected). Source CALC-B4-WAKE, CALC-B4-PITOT.`

### 3.1 Hover yaw: the fin helps, it does not hurt

R0–R2 treated the half-fin as a stator. It takes swirl out of the wake, so the moment it makes about the **motor**
axis opposes the reaction torque (factor 0.48). Hover yaw is a rotation about the **body** x-axis. The fin force
acts at z_cp = 0.158 m from that axis, on the wing side of the motor axis. At the upper-right station (F4: CW from
the nose, reaction −x) the swirl below the motor axis blows outboard and pushes the fin +y at z > 0. The moment
about the body axis is −z F_y, which is negative, the same sense as the reaction torque. The same holds at all four
stations. In trimmed hover the four fin forces cancel. Under a yaw command the fin forces of the loaded pair grow
and add to the reaction torque. This is the same effect as slipstream swirl on a conventional fin.

The cant's wake lean crosses the fin at 3.6°, against the swirl. The cant therefore *lowers* the fin force:

| Cant | Fin side force per half-fin | Yaw factor (reaction + fin) | Yaw moment per N differential, full / half fin / no fin credit | vs B3's need 0.0477 m (half fin) |
|---|---|---|---|---|
| 0° | 1.35 N | 2.77 | 0.046 / 0.032 / 0.017 m | 0.66 × |
| 3° | 1.11 N | 2.54 | 0.062 / 0.049 / 0.036 m | 1.03 × |
| 5° | 0.82 N | 2.15 | 0.068 / 0.059 / 0.049 m | 1.23 × |
| **7° (R3)** | **0.57 N** | **1.79** (`CL-B4-YAW`) | **0.075 / 0.069 / 0.062 m** (`CL-B4-K-YAW`, `-LOW`) | 1.44 × |
| −7° (printed the wrong way round) | 1.43 N | 2.54 | −0.003 / −0.016 m | **no yaw** |

B3's need is k = M_yaw,need / (4 dT) = 0.387 / (4 × 2.03) = 0.0477 m (`CALC-B3-HOVER`). Three things follow:
- **7° works with no fin credit at all** (1.30 ×). 5° is the smallest cant that does (1.03 ×). It keeps 31.6 mm
  at the tube and halves the cant's thrust cost (0.38 % against 0.75 %).
- **The fin swirl force at 7° is 0.57 N per half-fin** (root moment 0.083 N·m), down from 0.94 N at R2. C4's fin
  loads go down. If the mounts are printed with the wrong sense, the force rises to 1.43 N.
- **A motor-axis torque cell sees the wrong number.** With the fin on the same cell it reads a "recovery" of only
  0.16 (`CL-B4-F-AXIS`). `T-B4-YAW` now measures the fin's side force and centre of pressure on a separate cell.

Uncertainty: the lift slope uses Helmbold's formula on a plate with an end wall (AR 0.63). The swirl is the
actuator-disk value, Γ = Q / (ρ v_i π (R² − r_h²)). The fin force could be about 2× high or low. B3 should size the
cant on `CL-B4-YAW-LOW` (1.40) until `T-B4-YAW` runs.

## 4. Pitot placement

Model: four semi-infinite vortex cylinders (actuator disks, Γ = 2v). Each starts at its canted hub and runs along
the resultant of V (+x) and v (canted shaft). Ring velocities, axial *and radial*, come from elliptic integrals. A
continuity self-test of the radial formula gives a residual of 0. Three wake lengths and grids converge to 0.01 % of
V. The error is the x-component of the induced velocity at the probe tip divided by airspeed, for cruise (16 m/s,
0.92 N), transition (15.6 m/s at full hover thrust, the worst case) and hover. Prop planes are at x −0.0082 m.

| Probe tip (x, y, z) m | Cruise | Transition | Hover induced | Verdict |
|---|---|---|---|---|
| **Pod-nose boom, left channel (−0.195, −0.046, 0.045)**, 187 mm ahead of the discs | 0.27 % | **1.72 %** | 0.74 m/s | **use** (`POD-006`; margin 14 % on the 2 % limit) |
| Same boom on the centreline (−0.195, 0, 0.045) | 0.26 % | 1.66 % | 0.71 m/s | comparison: the channel costs 0.06 points |
| Pod front, no boom (−0.115, −0.046, 0.045) | 0.21 % | 1.33 % | 0.57 m/s | the pod's own stagnation field sits on the probe: reject |
| Boom 100 mm longer (−0.295, −0.046, 0.045) | 0.27 % | 1.71 % | 0.74 m/s | no gain |
| Inboard wing LE (−0.083, 0.15, 0) | 0.28 % | 1.79 % | 0.77 m/s | marginal; also in the wing's upwash |
| Outboard wing LE (−0.083, 0.53, 0) | 0.19 % | 1.23 % | 0.54 m/s | acceptable; long tube run, tip-strike exposure |

The error does not fall as the boom gets longer: the axial induced velocity on the pod axis peaks about 0.25 m
ahead of the discs. About 0.27 % of the error is constant at cruise thrust, and ARSPD_RATIO removes it. The
thrust-dependent part is 1.45 % (0.23 m/s at 15.6 m/s), inside F3's 0.5 m/s budget (`airspeed_err_max_ms`). F3
should carry 0.23 m/s, not 0.21. The model covers axial inflow only. In transition the body angle of attack reaches
tens of degrees and the probe under-reads (F4: no gain scheduling during the pitch-over).

## 5. Cruise drag of the R3 fin hardware (CR-D3-15)

Freestream q 157 Pa. Items inside the cruise slipstream see V + v(1 + s/√(s² + R²)), with v = 0.38 m/s. The sum
covers 4 stations.

| Item | Size (each) | Cd (basis) | Cruise drag, 4 stations | In B1 rev 3? |
|---|---|---|---|---|
| Braces | 10 × 3 mm, 143 mm, 3 mm across the flow | 1.2 (`ASM-B4-CD-STRIP`; B1 uses 0.8) | 0.219 N | yes |
| Station collars | Ø25.2 × 12 mm (increment over the tube) | 1.1 | 0.038 N | yes |
| Mount collars | Ø26 × 12 mm (increment) | 1.1 | 0.036 N | **no** |
| Ears (pinch 9 × 12, brace 10 × 12 mm) | 228 mm² per station | 1.2 | **0.215 N** | **no** |
| ESC + pad | 8 × 28 mm frontal | 0.9 (`ASM-B4-ESC`) | 0.136 N | **no** |
| **Total** | | | **0.64 N** (ΔCD0 0.0111, 17 % of 3.70 N, ≈ 32 W) | not carried: **0.39 N, ΔCD0 0.0067** (`CL-B4-ITEMS-NOT-B1`) |

The bare tubes (2.43 N with Cd 1.1 unfaired) belong to B1, who fairs them with the fin. The cheap wins are on
the ears. Turning the pinch ear aft into the fin plane (slit on the trailing side) and sweeping the brace ear
along x would put both in the tube's wake and save most of 0.2 N (≈ 10 W).

## 6. Noise and vibration inputs

| Item | Hover | Full throttle (cap) | Use |
|---|---|---|---|
| 1P (shaft) | 90 Hz | 156 Hz | C4: tube and mount first modes outside 80–330 Hz |
| BPF (2-blade) | 181 Hz | 311 Hz | F4: ESC-rpm harmonic notch; tonal noise. The blade passes 27 mm over the tube: expect a stronger 2P tone than at R2 |
| Tip Mach | 0.23 | 0.40 | low; no compressibility correction |

SPL is not estimated: there is no validated model for this installation. If a site limit is ever imposed, measure
it at 10 m on the twin.

## 7. Assumptions

| Id | Value | Basis | Status |
|---|---|---|---|
| `ASM-B4-VSAG` | 13.6 V | 3.4 V/cell loaded, end of flight | `PROPOSED` |
| `ASM-B4-CD-TUBE` | 1.1 | cylinder, Re ≈ 1.3e4 (Hoerner); conservative with the fin as a splitter plate | `PROPOSED` |
| `ASM-B4-CD-STRIP` | 1.2 | sharp rectangles d/h ≈ 3 (Hoerner; Delany and Sorensen) | `UNVERIFIED` |
| `ASM-B4-ESC` | 6.8 mm proud, Cd 0.9 | E1 publishes no ESC size | `UNVERIFIED` |
| `ASM-B4-WAKE-SENSE` | k = +1 | F4's motor table and cant sense | `PROPOSED` |
| `ASM-B4-PROFILE` | 1.3 | peak/mean slipstream q | `UNVERIFIED` |
| `ASM-B4-FOOT` | 900 mm² | bounds D5's shoe | `PROPOSED` |
| `ASM-B4-MIX` | 0.08 | mixing-layer spread per side (Brown and Roshko) | `PROPOSED` |
| `ASM-B4-VRS` | 0.28 v_h | VRS onset (Leishman) | `PROPOSED` |
| `ASM-B4-SPAN-AR` | 2 | wing as end plate for the fin | `PROPOSED` |
| `ASM-B4-PITOT-ERR` | 2 % | thrust-dependent airspeed error limit | `PROPOSED` |
| `ASM-B4-BOOM` | 80 mm, z 0.045 m | pitot boom ahead of the pod front | `PROPOSED` |

Retired at R3: `ASM-B4-CANT` (now `P:propulsion.stations.cant_deg`), `ASM-B4-FIN-T` (now board × layers).

## 8. How to verify

| Test | What it checks | Owner |
|---|---|---|
| `T-B4-STAND` | A/B of 11×5.5MR and 11×4.5MR: thrust, torque and rpm at 10 % steps, 14.8 V and a fresh pack; FM, rpm at the cap | H1 (shared with `T-E1-STAND`) |
| `T-B4-INSTALLED` | 7° canted mount on a tube cut to the R3 end, both collars with ears, one brace strip, ESC dummy, two-layer 0.21 m half-fin with the R3 top edge, S5010 strip. Blade-tip gap over the tube by hand first; installed/isolated thrust; brace and ESC, then fin, then strip removed in turn | H1 |
| `T-B4-YAW` | fin side force and centre of pressure on its own cell, reaction torque, with the 7° and the 0° mount → body-axis yaw factor = 1 + F z_cp / Q | H1 |
| `T-B4-CRUISE` | car-top rig at 16 m/s, or a logged twin cruise, against `CALC-B4-CRUISE` (and the item drag) | H1 / H2 |
| Cant sense | before the first hover: in the motor test, each motor's thrust side load must turn the frame the same way as its reaction torque | H1 / F4 |
| Pitot | constant-groundspeed legs in calm air at two throttles: airspeed must not step with throttle | H2 |

Re-run everything: `python -I redesign/team/B4/props.py`, `python -I redesign/team/B4/figures.py`, then
`python -I redesign/proofs/build_graph.py`.

## Sources

APC PER3 files ([11×4.5MR](https://www.apcprop.com/files/PER3_11x45MR.dat), 11×5.5MR, 11×5.5E, 11×4.7SF,
12×4.5MR), [APC rpm limits](https://www.apcprop.com/technical-information/rpm-limits), APC product pages
([11×4.5MR](https://www.apcprop.com/product/11x4-5mr/), [11×5.5EP](https://www.apcprop.com/product/11x5-5ep/)),
[UIUC Propeller Database vol. 1](https://m-selig.ae.illinois.edu/props/volume-1/propDB-volume-1.html), rotor-pair
interaction: [Zhou, Ning, Hu (ISPIV)](https://journals.library.iit.edu/index.php/ISPIV/article/view/39) (abstract
only, `UNVERIFIED`). Drag of rectangular sections: Hoerner, *Fluid-Dynamic Drag* ch. 3; Delany and Sorensen, NACA
TN 3038. All read 2026-11-09.
