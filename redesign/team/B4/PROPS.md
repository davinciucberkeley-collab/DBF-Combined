# Props and rotor aero (B4)

Status `PROPOSED`, 2026-11-10, re-run at **R4** (prop plane x −0.0077, cant sense −1 per D-52, L/D 6.2, pitot tip
x −0.21). Everything below is `UNVERIFIED` until the thrust stand runs (`T-B4-STAND`, `T-B4-INSTALLED`, `T-B4-YAW`).
Calculations: `team/B4/props.py` → `claims.json` (74 claims, 4 planned tests), `out/props_results.json`. Figures: `team/B4/figures.py`. Data: `team/B4/data/` (APC
PER3 tables for five props, UIUC measurements for two). Python standard library only. `props.py` now also reads
D3's `subsystems/fins/params.json` (`P:fin_detail.*`) for the collars, ears, braces and ESC pads.

**Verdict.** Fly the **APC 11×5.5MR / 11×5.5MRP** (unchanged, agrees with E1). At R3 it costs 3 % more hover power
than the 11×4.5MR and saves 19 % in cruise. Five installation results matter more than the prop choice:
1. **The hover-yaw sign was wrong in R0–R2.** The fin's swirl side force acts 0.16 m from the body x-axis and turns
   the airframe *with* the reaction torque. Hover yaw authority is **1.79 ×** the isolated reaction torque at 7°
   cant (1.40 × with half the modelled fin force), not 0.48 ×. Add the cant and the total is 4.5 ×.
2. **R4: the wing is clear; the tube is not.** Measured exactly in 3D against the blade's swept volume (E1's
   +10 / −6 mm envelope), the blade passes **34.2 mm** from the wing upper skin at the upper stations and 42.2 mm
   from the lower skin at the lower ones (limit 25 mm, `CL-B4-TIP-WING`, `-LOWER`). The "23 mm" radial estimate
   does not reproduce (§3.0). The same exact test gives **21.1 mm to the CF motor tube, a `FAIL`**
   (`CL-B4-GAP-TUBE-ENV`, equal to E1's `CL-E1-TIP-GAP-TUBE`). E1's fix, the mount face 5 mm forward, gives
   26.1 mm (`CL-B4-GAP-TUBE-FIX5`). The 7° cant is still more than yaw needs, and 5° also fixes the tube.
3. **The cant sense has to match F4's spin map, and D3's print sense is the opposite.** If the mounts are
   printed as D3's `cant_sense_UR +1` with F4's rotations, differential-thrust yaw drops to about zero.
4. **The pitot at R4, tip (−0.21, −0.046, 0.045), reads 1.75 % high in transition** (limit 2 %, margin 13 %).
   Moving it into the left channel costs 0.06 points against the centreline.
5. **The new fin hardware adds 0.64 N of cruise drag** (ΔCD0 0.011; 17 % of cruise drag, 32 W). B1 rev 3
   already carries the braces and station collars. The ears, mount collars and ESC pads (ΔCD0 0.0067) are not
   carried, and the ears alone cost as much as the braces. Hover download is 1.038 (keep 1.06).

## 0a. What changed at R4 (action item: prop-tip-to-wing clearance)

| Input / method | R3 | R4 | Effect on B4 numbers |
|---|---|---|---|
| `propulsion.stations.x_prop_plane_m` | −0.0082 | **−0.0077** (D-51, = `CL-E1-CAD-HUB-X`) | hub 0.5 mm closer to the tube and the wing |
| Hub x on the canted axis | x_prop + stack (1 − cos 7°) (0.28 mm aft) | **x_prop** (params already gives the canted-axis hub x) | tube mid-plane gap 27.3 → 27.1 mm |
| `fin_detail.mount.cant_sense_UR` | +1 (opposite of F4) | **−1** (D-52), now the same as `ASM-B4-WAKE-SENSE` | CR-B4-15a closed; B4's numbers were already on this sense |
| Clearance method | hub mid-plane to the tube face, zero-thickness blade | **exact distance from every wing-skin and tube-surface point to the swept volume** (`CALC-B4-TIP-WING`) | adds the wing; the tube falls to 21.1 mm (answers CR-E1-46a) |
| `performance.ld_cruise` | 6.9 | **6.2** | cruise 0.92 → 1.03 N per prop; pack 185 → 195 W |
| `pod.x_le_m` (pitot tip x) | tip −0.195 | tip −0.21 | transition error 1.72 → 1.75 % |

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

Conditions: 2.6 kg gate, download 1.06 and cant 7° (6.81 N per prop in hover), 16 m/s cruise at L/D 6.2 (1.03 N
per prop, R4), ρ 1.225 kg/m³. Props are from APC PER3. Electrical power uses E1's motor constants (`ASM-E1-*`); E1 owns
the electrical numbers.

| Prop | Hover rpm | FM | Hover pack W | Cruise J | η_prop | Cruise pack W | Full-throttle rpm, 14.8 V hot / APC limit | Mass | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **11×5.5MR/MRP** | 5 416 | 0.711 | 346 | 0.578 | **0.443** | **195** | 9 319 / 9 545 (+2 %) | 17 g | `PROPOSED` (selected) |
| 11×4.5MR/MRP | 5 816 | 0.718 | 336 | 0.499 | 0.354 | 239 | 9 778 / 9 545 (**−2 %**) | 17 g | stand A/B only |
| 11×5.5E/EP | 5 830 | 0.696 | 347 | 0.571 | 0.490 | 177 | 9 735 / 13 636 | 23 g | alternate |
| 11×4.7SF | 5 098 | 0.757 | 329 | 0.545 | 0.331 | 256 | 9 019 / **5 909** | 20 g | rejected: SF rpm limit |
| 12×4.5MR | 5 066 | 0.715 | 319 | 0.475 | 0.295 | 286 | 9 087 / 8 750 (−4 %) | 20 g | rejected: cruise, clearance |

- **The 11×4.7SF never flies.** Its APC limit (65 000 / D) is 5 909 rpm and hover alone needs 5 098 rpm
  (`CL-B4-SF-RPM` `FAIL`).
- **The 11×5.5E** is the most efficient cruise prop (177 W against 195 W at R4's L/D 6.2). It is 6 g heavier per prop, has more
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
| Cruise rpm / J / η_prop / shaft power (16 m/s, 1.03 N, L/D 6.2) | 5 946 / 0.578 / 0.443 / 37.1 | rpm / — / — / W | `CL-B4-CRUISE-*` | `UNVERIFIED` |
| Cruise pack power, 4 motors (E1 constants, no fin-hardware drag) | 195 (11×4.5MR: 239) | W | `CL-B4-CRUISE-W`, `-OLD` | `UNVERIFIED` |
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
| **Blade over the tube with the disc canted 7°**: the wing-side edge swings about 15 mm aft | hub mid-plane to the tube face 27.1 mm; **blade swept volume to the tube surface 21.1 mm** (§3.0); collars 36.2 mm (mid-plane); 45.5 mm if mirrored | **`FAIL` by 16 %** (limit 25 mm). E1's mount face +5 mm gives 26.1 mm | `CL-B4-GAP-TUBE-ENV`, `-FIX5`, `CL-B4-GAP-TUBE`, `-COLLAR`, `-TUBE-ALT` |
| **Blade over the wing skin** (upper stations face the cambered upper surface) | **34.2 mm** upper, 42.2 mm lower (exact 3D, E1 envelope); 35.8 mm with the +5 mm fix | meets 25 mm by 37 % | `CL-B4-TIP-WING`, `-LOWER`, `-FIX5` |
| Vortex ring state in vertical descent | v_h 6.71 m/s → onset ≈ 1.9 m/s | descent ≤ 1.5 m/s, landing 0.5 m/s (F4) | `CL-B4-DESCENT` |
| Ground effect at take-off | prop 0.376 m (2.7 R) above ground: +0.9 % | ignore | `CALC-B4-GEOM` |

### 3.0 Blade-tip clearance, exact (R4 action item)

The action item read a 23 mm tip-to-wing gap from a radial-only estimate: wing upper skin about 0.163 m from the
canted shaft axis against a blade radius of 0.1397 m. `CALC-B4-TIP-WING` replaces that estimate with an exact
distance. It samples the S5010 upper and lower skins (B2's coordinates; 0.25 mm in x to x = 0.08 m and 2 mm aft of
that; 1 mm in y over |y − 0.32| ≤ R + 30 mm) and the 22 mm tube surface (0.5 mm × 2.5°). For each point it
measures the distance to the prop's swept volume: radius R about the 7° canted axis, from 10 mm ahead of the hub
mid-plane to 6 mm behind it (`ASM-E1-BLADE-ENV`; the blades cone forward and never reverse). The hub sits at
(−0.0077, 0.3223, 0.1861) m: x from params, y and z moved 37.3 mm × sin 7° along the thrust-side direction (D-52 sense).

| Surface (stations) | Exact gap, E1 envelope | Symmetric ±10 mm | Zero-thickness blade | Radial only, in the KO band | Closest point (x, y, z) m | Limit | Status |
|---|---|---|---|---|---|---|---|
| Wing upper skin (UR, UL) | **34.2 mm** | 33.6 mm | 35.5 mm | 31.2 mm (r 0.171 m) | (0.023, 0.323, 0.015) | 25 mm | `CHECKED` +37 % |
| Wing lower skin (LR, LL) | 42.2 mm | 42.1 mm | 42.4 mm | 42.1 mm | (0.018, 0.322, −0.006) | 25 mm | `MODELLED` +69 % |
| CF motor tube (all four) | **21.1 mm** | 17.2 mm | 27.1 mm (to the face) | — | — | 25 mm | **`FAIL`** −16 % (`CHECKED` vs E1) |
| Tube, mount face 5 mm forward (E1 CR-E1-44) | 26.1 mm | — | — | — | — | 25 mm | `MODELLED` +5 % |
| Wing upper skin, mount face 5 mm forward | 35.8 mm | — | — | — | — | 25 mm | `MODELLED` +43 % |
| Wing upper / tube if the cant sense were mirrored | 51.6 / 37.9 mm | — | — | — | — | — | trade point |

Why the 23 mm figure is not the clearance:
- **No wing point is 0.163 m from the axis.** The least radial distance from the canted UR axis to the S5010 upper
  skin anywhere at the fin station is 0.1708 m, at x 0.045–0.060 m (radial gap 31 mm). A 0.163 m reading needs the
  skin about 8 mm higher than S5010's 9.8 % section, or the hub about 8 mm lower than the params station.
- **Radial distance is not clearance once the point is behind the blade.** At the wing's thickest stations (x 0.06
  to 0.10 m) the skin is 50–90 mm aft of the blade mid-plane, so the blade is 54–91 mm away. The real minimum is
  at x 0.023 m. There the skin is 12 mm behind the mid-plane (6 mm behind the blade's aft face) and 33.6 mm
  outside the tip circle: √(6.2² + 33.6²) = 34.2 mm.
- **A cylinder keep-out (R + 25 mm, ±35 mm) sees the wing at 31.2 mm radial,** so an exact surface test against
  `KO-PROP-UR` passes. A bounding-box test will flag the wing core or tape blocks because the box corners reach
  inside the cylinder (`CL-B4-TIP-WING-KO`).
- **Independent cross-check:** E1's dense-surface CAD probe (`team/E1/prop_clearance.json`) gives 34.1 mm for WNG-003
  (tape doubler block, upper) and 34.2 mm for WNG-001 (core) with the same envelope. That is a different code
  working on the CAD bodies, and it agrees with B4 to 0.1 mm. B4's tube value (21.14 mm) equals E1's
  `CL-E1-TIP-GAP-TUBE` (21.1 mm, analytic) and their probe (21.2 mm).
- Not counted: tape skin and doubler thickness (≈ 0.1–0.3 mm; E1's probe includes them), blade flap beyond E1's
  +10 / −6 mm envelope, and a misprinted cant (±1° moves the wing-side tip about ±2.1 mm in x).

**Consequence.** The wing does not constrain the prop station. The tube does, and only the tube. A1's CR-D3-26
choice (face_ahead 0.0075 m, or a 5° cant) clears it. With the face 5 mm forward the wing gap rises to 35.8 mm.

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
