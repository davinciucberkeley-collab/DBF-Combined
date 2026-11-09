# Props and rotor aero (B4)

Status `PROPOSED`, 2026-11-09. Everything below is `UNVERIFIED` until the thrust stand runs (`T-B4-STAND`,
`T-E1-STAND`). Calculations: `team/B4/props.py` → `claims.json` (44 claims), `out/props_results.json`. Figures:
`team/B4/figures.py`. Data: `team/B4/data/` (APC PER3 tables for five props, UIUC measurements for two). Python
standard library only.

**Verdict.** Fly the **APC 11×5.5MR / 11×5.5MRP**, which agrees with E1's CR-E1-06. Compared with the 11×4.5MR it
cuts cruise power by 18 % and costs 3 % in hover. It is the only MR prop in the set that stays under APC's rpm limit
at full throttle on a 14.8 V bus. On a fresh pack it still needs an output cap of about 0.85. Three installation
results matter more than the prop choice:
1. **The elevons are outside the hover slipstream**, so the aircraft has no elevon authority at zero airspeed.
2. **The fins straighten the prop swirl**, which removes about half of the hover yaw authority. A 3° motor cant
   restores it.
3. **The pitot belongs on the pod-nose boom.** With the props at x −0.005 m the prop-induced error at the tip
   (x −0.185 m) is 1.66 % worst case, inside the 2 % limit but no longer under 1 %.

Re-run 2026-11-09 (R2 geometry): motor tube at x 0.045 m, prop plane at x −0.005 m, disc edge 50 mm above the
chord plane (28 mm above the S5010 crest), half-fins 0.275 m chord, pod front at x −0.105 m, pitot tip at x −0.185 m.

## 1. Prop selection

Conditions: 2.6 kg gate, download 1.06 (6.76 N per prop in hover), 16 m/s cruise at L/D 5.6 (1.14 N per prop; params R2),
ρ 1.225 kg/m³. Props are from APC PER3. Electrical power uses E1's motor constants (`ASM-E1-*`: Kv 900, R 86 mΩ,
I0 0.9 A, ESC 10 mΩ + 0.5 W, pack 24 mΩ); E1 owns the electrical numbers.

| Prop | Hover rpm | FM | Hover pack W | Cruise J | η_prop | Cruise pack W | Full-throttle rpm, 14.8 V hot / APC limit | Mass | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **11×5.5MR/MRP** | 5 396 | 0.711 | 343 | 0.573 | **0.465** | **205** | 9 319 / 9 545 (+2 %) | 17 g | `PROPOSED` (selected) |
| 11×4.5MR/MRP | 5 795 | 0.718 | 333 | 0.495 | 0.374 | 249 | 9 778 / 9 545 (**−2 %**) | 17 g | stand A/B only |
| 11×5.5E/EP | 5 808 | 0.696 | 343 | 0.565 | 0.510 | 188 | 9 735 / 13 636 | 23 g | alternate |
| 11×4.7SF | 5 079 | 0.757 | 325 | 0.540 | 0.351 | 268 | 9 019 / **5 909** | 20 g | rejected: SF rpm limit |
| 12×4.5MR | 5 047 | 0.715 | 315 | 0.472 | 0.314 | 297 | 9 087 / 8 750 (−4 %) | 20 g | rejected: cruise, clearance |

- **The 11×4.7SF never flies.** The maker's thrust table was measured on it, but its APC limit (65 000 / D) is
  5 909 rpm and hover alone needs 5 079 rpm (`CL-B4-SF-RPM` `FAIL`).
- **The 11×5.5E** is the most efficient cruise prop: 188 W, against 205 W for the 11×5.5MR. It is 6 g heavier per
  prop, has more rotational inertia (slower thrust response) and a 0.41 in hub. Keep it as the alternate if the
  stand shows the MR worse than predicted.
- **Data trust.** UIUC wind-tunnel measurements of two APC 11 in props match the PER3 cruise efficiency to within
  3.5 % (ratios 0.99 and 1.03, `CL-B4-UIUC-ETA`, `-E`). In static thrust, PER3 over-predicts FM by 4.5 % for both
  props (`CALC-B4-XCHECK`). **Plan hover shaft power about 5 % above the PER3 numbers.**

![Cruise pack power against airspeed](out/fig-b4-01-cruise-power.svg)

`FIG B4-01 — Pack power for four motors at 2.6 kg and L/D 5.6, by prop; 11×5.5MR blue, 11×4.5MR ink. Source CALC-B4-CRUISE.`

## 2. Key numbers (selected prop)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover thrust per prop / disk loading | 6.76 / 110 | N / N/m² | `CL-B4-HOVER-T`, `CL-B4-DL` | `UNVERIFIED` |
| Hover rpm / torque / shaft power | 5 396 / 0.113 / 63.8 | rpm / N·m / W | `CL-B4-HOVER-RPM`, `-Q`, `-SHAFT` | `UNVERIFIED` |
| Hover FM (PER3; × 0.955 measured trend) | 0.711 (≈ 0.68) | — | `CL-B4-FM`, `CALC-B4-XCHECK` | `UNVERIFIED` |
| Cruise rpm / J / η_prop / shaft power (16 m/s, 1.14 N) | 6 000 / 0.573 / 0.465 / 39.2 | rpm / — / — / W | `CL-B4-CRUISE-*` | `UNVERIFIED` |
| Cruise pack power, 4 motors (E1 constants) | 205 (11×4.5MR: 249) | W | `CL-B4-CRUISE-W`, `-OLD` | `UNVERIFIED` |
| Full-throttle rpm, 16.8 V fresh, no cap | 10 637 (limit 9 545) | rpm | `CL-B4-RPM-MAX-FULL` | `FAIL` (cap below) |
| Output cap for ≤ 9 350 rpm on a fresh pack | 0.85 | — | `CL-B4-SPIN-MAX` | `UNVERIFIED` |
| T/W at the rpm cap (installed) | 3.03 (≥ 2.0) | — | `CL-B4-TW-CAP` | `UNVERIFIED` |
| Tip Mach hover / at the cap | 0.23 / 0.40 | — | `CL-B4-TIPMACH` | `UNVERIFIED` |

## 3. Installation effects

| Effect | Result | Consequence | Claim |
|---|---|---|---|
| Download: tube 0.114 N, half-fin skin 0.030 N, fin base 0.048 N, foot 0.022 N, wing 0 N per station | k = 1.034 (mean loading), 1.043 (peaked) | **Keep 1.06** until `T-B4-INSTALLED`; release 0.01–0.02 then | `CL-B4-DOWNLOAD`, `-HIGH`, `CL-B4-TUBE-LOAD` |
| Wing beside the disc: disc edge 50 mm above the chord plane, 28 mm above the S5010 crest; the slipstream contracts away from it | closest approach of the mixing-layer edge to the skin 45 mm at x 0.03 m; no wetted strip | The wing adds no modelled download. Entrainment suction on the skin is not modelled; it is one reason to keep 1.06 | `CL-B4-WING-GAP` |
| Hover slipstream edge vs elevon tip at 25° | 33 mm clear (edge z 0.063–0.068 m incl. mixing; elevon tip 0.030 m) | **No blown elevon**: at zero airspeed, pitch, roll and yaw come from the motors only | `CL-B4-ELEVON-HOVER` |
| Cruise slipstream edge vs elevon | tip 5 mm inside the mixing layer at full throw; core increment ≈ 1 m/s | Negligible (+≤ 13 % q locally) | `CL-B4-ELEVON-CRUISE` |
| Half-fin straightens swirl (16.8° swirl at mid-chord, 0.264 m wetted chord behind the tube, 0.104 m wetted span) | side force 0.94 N per half-fin, root moment 0.11 N·m at the wing skin (cp 115 mm above the skin); yaw authority × 0.48 (× 0.74 if half as effective) | Hover yaw (about body x) is weak; E1's 0.149 N·m becomes ≈ 0.07 N·m. C4: the two halves of one fin load the same way | `CL-B4-YAW`, `CL-B4-SWIRL-FIN`, `-M` |
| 3° tangential motor cant | yaw authority 1.65 × isolated (1.17 × even with no reaction torque); thrust cost 0.14 % | **Recommend** printed mounts with 3° cant (minimum 1.3°) | `CL-B4-YAW-CANT` |
| Rotor–rotor: vertical tip gap 0.101 m (0.36 D), lateral 0.361 m, coplanar | mean thrust change < 2 % (rotor-pair data); thrust fluctuation and noise rise | No correction; watch vibration | `CL-B4-GAP-V` |
| Prop–tube: tube face 39 mm (0.14 D) behind the prop plane | steady tube load 0.11–0.15 N; unsteady at blade passing | Do not reduce this gap (D3) | `CALC-B4-GEOM` |
| Vortex ring state in vertical descent | v_h 6.71 m/s → onset ≈ 1.9 m/s | Descent ≤ 1.5 m/s, landing 0.5 m/s (F4) | `CL-B4-DESCENT` |
| Ground effect at take-off | prop plane 0.37 m (2.6 R) above ground: +0.9 % | Ignore | `CALC-B4-GEOM` |

![Side view at the fin station with the hover slipstream](out/fig-b4-02-slipstream.svg)

`FIG B4-02 — Side view at y = 0.32 m, 1 m = 850 px. S5010 section, motor tube at x 0.045 m and half-fins (grey). Blue: hover slipstream edge (solid: momentum theory; dashed: with the mixing layer). Orange: elevon at ±25° and the pitot boom (at y = 0, projected). Source CALC-B4-WAKE, CALC-B4-PITOT.`

## 4. Pitot placement

Model: four semi-infinite vortex cylinders (actuator disks, Γ = 2v), ring velocities from elliptic integrals, three
wake lengths and grids (convergence 0.02 % of V, self-test 0.9999). The error is the axial induced velocity at the
probe tip divided by airspeed, for cruise (16 m/s, 1.14 N), transition (15.5 m/s at full hover thrust, the worst
case) and hover. Prop planes at x −0.005 m; the tip of the chosen boom follows `pod.x_le_m` − 0.08 m (`ASM-B4-BOOM`).

| Probe tip (x, y, z) m | Cruise | Transition | Hover induced | Verdict |
|---|---|---|---|---|
| **Pod-nose boom (−0.185, 0, 0.045)**, 180 mm ahead of the discs | 0.31 % | **1.66 %** | 0.71 m/s | **use** (`POD-006`, 80 mm ahead of the pod front; margin 17 % on the 2 % limit) |
| Pod front, no boom (−0.105, 0, 0.045) | 0.23 % | 1.20 % | 0.51 m/s | less prop error, but the pod's own stagnation field sits on the probe: reject |
| Boom 100 mm longer (−0.285, 0, 0.045) | 0.32 % | 1.71 % | 0.73 m/s | no gain |
| Inboard wing LE (−0.08, 0.15, 0) | 0.33 % | 1.78 % | 0.76 m/s | marginal; also in the wing's own upwash |
| Outboard wing LE (−0.08, 0.53, 0) | 0.22 % | 1.17 % | 0.50 m/s | acceptable; long tube run, tip-strike exposure |

The error does not fall as the boom gets longer. Upstream of the discs the props act like sinks 0.35 m off the pod
axis, so the axial induced velocity on the axis peaks about 0.25 m ahead of the prop planes. Transition error along
the pod axis: tip x −0.105 m 1.20 %, −0.15 m 1.52 %, −0.185 m 1.66 %, −0.25 m 1.74 %, −0.30 m 1.69 %, −0.40 m 1.48 %,
−0.50 m 1.23 %, −0.70 m 0.83 %. A boom long enough to beat the 80 mm one would be about 0.6 m, which is not worth it
in a one-piece box. About 0.31 % of the error is constant at cruise thrust and ARSPD_RATIO removes it. The
thrust-dependent part is 1.35 % (0.21 m/s at 15.5 m/s), well inside `airspeed_err_max_ms` 1.0 m/s.

Limits of the model: axial inflow only. In transition, the body angle of attack reaches tens of degrees and a pitot
on the body x-axis under-reads (cosine error, then stall of the probe above about 20°). Use airspeed for gain
scheduling only after the transition is nearly complete (F4).

## 5. Noise and vibration inputs

| Item | Hover | Full throttle (cap) | Use |
|---|---|---|---|
| 1P (shaft) | 90 Hz | 156 Hz | C4: tube and mount first modes outside 80–330 Hz |
| BPF (2-blade) | 180 Hz | 311 Hz | F4: ESC-rpm harmonic notch; tonal noise |
| Tip Mach | 0.23 | 0.40 | Low; no compressibility correction |

SPL is not estimated: no validated model for this installation. Measure it at 10 m on the twin (phone meter, A-weighted)
if a site limit is ever imposed.

## 6. Assumptions

| Id | Value | Basis | Status |
|---|---|---|---|
| `ASM-B4-VSAG` | 13.6 V | 3.4 V/cell loaded, end of flight | `PROPOSED` |
| `ASM-B4-CD-TUBE` | 1.1 | cylinder, Re ≈ 1.3e4 (Hoerner) | `PROPOSED` |
| `ASM-B4-PROFILE` | 1.3 | peak/mean slipstream q | `UNVERIFIED` |
| `ASM-B4-FIN-T` / `-FOOT` | 10 mm / 900 mm² | fin and foot not drawn yet | `PROPOSED` |
| `ASM-B4-MIX` | 0.08 | mixing-layer spread per side (Brown and Roshko) | `PROPOSED` |
| `ASM-B4-VRS` | 0.28 v_h | VRS onset (Leishman) | `PROPOSED` |
| `ASM-B4-SPAN-AR` | 2 | wing as end plate for the fin | `PROPOSED` |
| `ASM-B4-PITOT-ERR` | 2 % | thrust-dependent airspeed error limit | `PROPOSED` |
| `ASM-B4-CANT` | 3° | B4 proposal | `PROPOSED` |
| `ASM-B4-BOOM` | 80 mm, z 0.045 m | pitot boom ahead of the pod front | `PROPOSED` |

## 7. How to verify

| Test | What it checks | Owner |
|---|---|---|
| `T-B4-STAND` | A/B of 11×5.5MR and 11×4.5MR: thrust, torque and rpm at 10 % steps, 14.8 V and a fresh pack; FM, rpm at the cap | H1 (shared with `T-E1-STAND`) |
| `T-B4-INSTALLED` | Same stand with a 22 mm tube (face 39 mm behind the prop), a 0.275 m-chord foam-board half-fin and a 0.32 m S5010 wing strip 28 mm below the disc edge: installed/isolated thrust → download, then strip and fin removed in turn | H1 |
| `T-B4-YAW` | Reaction torque with and without the half-fin mock-up → swirl recovery fraction and half-fin side force | H1 |
| `T-B4-CRUISE` | Car-top rig at 16 m/s, or a logged twin cruise: rpm, current, voltage against `CALC-B4-CRUISE` | H1 / H2 |
| Pitot | Constant-groundspeed legs in calm air at two throttles: airspeed must not step with throttle | H2 |

Re-run everything: `python -I redesign/team/B4/props.py`, `python -I redesign/team/B4/figures.py`, then
`python -I redesign/proofs/build_graph.py` (result 2026-11-09 after the R2 re-run: no B4 drift or error; the build still fails on other roles' drift: A5, B1, B2, B3, C1, E1, J1).

## Sources

APC PER3 files ([11×4.5MR](https://www.apcprop.com/files/PER3_11x45MR.dat), 11×5.5MR, 11×5.5E, 11×4.7SF,
12×4.5MR), [APC rpm limits](https://www.apcprop.com/technical-information/rpm-limits), APC product pages
([11×4.5MR](https://www.apcprop.com/product/11x4-5mr/), [11×5.5EP](https://www.apcprop.com/product/11x5-5ep/)),
[UIUC Propeller Database vol. 1](https://m-selig.ae.illinois.edu/props/volume-1/propDB-volume-1.html), rotor-pair
interaction: [Zhou, Ning, Hu (ISPIV)](https://journals.library.iit.edu/index.php/ISPIV/article/view/39) (abstract
only, `UNVERIFIED`). All read 2026-11-09.
