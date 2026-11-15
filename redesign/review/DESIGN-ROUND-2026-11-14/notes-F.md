# Stream F notes (stopped 2026-11-14 at the coordinator's request)

Work stopped before any design change, model run or file edit. These are the findings so far. Nothing here is
`PROPOSED` yet. `EST` marks hand estimates that have not been run in the 3-D model.

## 1. Where `CL-C4-SIM-SEP` stands (read from the repo, nothing re-run)

- **Separation: 0.1445 against 0.20.** Source: `team/C4/claims.sim.json` `CL-C4-SIM-SEP`, from
  `team/C4/sim/out/sim_results.json` `CALC-C4-SIM-MODES`.
- **The lower quarter governs.** First station mode is 240.05 / 234.14 / 231.30 Hz on meshes L1 / L2 / L3; the
  extrapolated value is 228.68 Hz, with order 2.12 and GCI 1.4 %. The upper quarter extrapolates to 235.90 Hz,
  with GCI 1.1 %. The mode is lateral-torsion.
- **Forcing.** `d3.forcing` with `CL-B4-HOVER-RPM` 5 416, `CL-B4-CRUISE-RPM` 5 994 and `CL-B4-RPM-MAX` 9 319 gives:

  | Excitation | Frequency |
  |---|---|
  | 1P hover | 90.3 Hz |
  | 2P hover | 180.5 Hz |
  | 1P cruise | 99.9 Hz |
  | 2P cruise | **199.8 Hz** (governs) |
  | 1P max | 155.3 Hz |

- **Target.** The mode must reach f1 ≥ 1.2 × 199.8 = **239.8 Hz**, which is +4.85 % (matches
  `CL-C4-SIM-LEVER-NEED` 0.0485).
- **No window below 2P cruise.** The mode would have to be above 1.2 × 155.3 = 186.4 Hz and below 0.8 × 180.5 =
  144.4 Hz at the same time. So lowering the mode cannot pass. Only raising it can.
- **Two ways to move the rpm (stream A's call).**
  - Raise the mode above the forcing, as above.
  - Lower the cruise rpm. A cruise rpm of 5 718 or less (228.7 / 1.2 × 30) puts 2P cruise at or below 190.6 Hz,
    and then 2P hover at 180.5 Hz → 228.7 / 180.5 − 1 = 0.267, which passes. `EST` from the formula. It is not a
    structural fix and needs stream A.

## 2. Lever table already in the repo (S1, CDR-19)

Source: `team/C4/claims.sim.json` `CL-C4-SIM-LEVER-*`. Each lever is applied one at a time, lower quarter, mesh L2.

| Lever | Separation | Mass |
|---|---|---|
| Brace 10 × 3 | 0.158 | +9 g |
| 10 g less at each station | 0.181 | −40 g |
| Mount rocking stiffness × 1.5 | 0.155 | — |
| Tube at 90 / 4.6 GPa | 0.126 | — |
| **Tube G 8 GPa at E 100 GPa** | **0.215** (passes) | — |
| Brace 10 × 3 with the 90 / 4.6 tube | 0.139 | — |

Tube shear modulus G is the dominant lever. Raising G from 5 to 8 GPa gives +6.1 % in f1.

## 3. Options looked at (none run in 3-D yet)

### a. Stiffer tube at the same 22 mm OD

This is the best candidate. Catalogue search was done by a subagent, all pages checked 2026-11-14. Rock West E and G
are the CLT values printed on each product page, in psi, and Rock West does not guarantee them.

| Part | Size | Construction | E | G | Mass | Price |
|---|---|---|---|---|---|---|
| **Rock West 35046-S** https://www.rockwestcomposites.com/35046-s.html | 0.875 × 0.750 in = 22.23 × 19.05 mm | filament wound ±15 / hoop / ±45 / ±15 | 13.08 Msi = 90.2 GPa | **2.979 Msi = 20.5 GPa** | 0.105 lb/ft = 0.156 kg/m | $32.99 per 12 in, 3 ft minimum, $20 cut charge, **backorder** |
| Rock West 35045-S https://www.rockwestcomposites.com/35045-s.html | 22.23 × 15.88 mm | — | 72.3 GPa (fails E ≥ 90) | 25.0 GPa | 0.289 kg/m | $49.99 per ft |
| Rock West 46728 "Torsion" https://www.rockwestcomposites.com/46728.html | 22.23 × 19.05 mm | — | 28.8 GPa (fails E) | 25.2 GPa | — | 60 in for $121.99 |
| Rock West 46727 "Torsion" https://www.rockwestcomposites.com/46727.html | — | — | 25.1 GPa (fails E) | 29.7 GPa | — | $142.99 |
| Rock West 45405 https://www.rockwestcomposites.com/45405.html | 22.23 × 15.88 mm | 0° plies | 89.7 GPa | 13.6 GPa | 0.289 kg/m | 72 in for $188.99 |
| ECF https://ecfibreglasssupplies.co.uk/carbon-fibre-tube-22mm-19mm | 22 × 19 mm | roll-wrapped twill | E not published (page gives EI 0.54 kN·m², i.e. about 106 GPa `EST`) | G not published | 0.14 kg/m | 1 000 mm for £24.00 ex VAT |
| R&G 22 × 18 via Lindinger https://lindinger.at/en/SUPPLIES-MISC/BUILDING-MATERIALS/Rods-Tubes-Solid-Strips-Panels/Tubes/R-G-VEC-PIPE-22-18MM-1M-WRAPPED/96336 | 22 × 18 mm | wound, vinyl ester | not published | not published | — | €43.80 |

Parts and sources that do not help:

- Easy Composites has no 22 mm OD tube in its metric range.
- Easy Composites' 90 / 4.6 GPa source pages now return 404.
- Rock West PBRT-2022 (pullbraided) returns 404.
- DragonPlate has no 22 mm tube.

Rock West 35046-S needs to be judged on four points:

- **Stiffness.** G 20.5 GPa is far above the 7.3 GPa S1 estimated as needed, and E sits at 90 GPa. It should pass
  well, but this is `EST` until the 3-D model is run (step 4).
- **Fit.** The OD is 0.23 mm over 22 mm and the wall is 1.59 mm. Every printed bore is 22.3 mm (bond gap 0.15 mm,
  `fin_detail.bond_gap_m`), so this tube leaves about 0.04 mm radial gap. Either sand the tube or open the bores
  in the fins CAD.
- **Mass.** Two 344 mm tubes weigh 2 × 0.344 × 0.156 = 107.3 g, against 70.2 g for the 22 × 20 at 0.102 kg/m
  (`wing.spar.mass_per_m_kgm`). That is **+37 g**. The A3 margin is +98 g (`RULES.md`).
- **Cost.** Three feet comes to about $99 plus the $20 cut charge, `EST`.

The models read the fin tube's mass per metre from the wing-spar key (`GEOM["mu"]` in `fin_structures_d3.py`), so
a different fin tube needs its own fin key.

### b. Thicker wall at 22 mm OD, same material (E 100 / G 5 GPa)

All figures are `EST` from π/4(OD⁴ − ID⁴).

| Tube | EI and GJ | Mass |
|---|---|---|
| 22 × 19 | +40 % | +16 g per tube |
| 22 × 18 | +74 % | +32 g per tube |

The in-house tube (`tube_equiv`) is a square bar, so a run must also scale `mu`.

### c. Shorter station arm

`fin_detail.mount.face_ahead_m` is 7.5 mm. The prop-gap ratio `CL-D3-PROP-GAP` is 1.138 against 1.0, which allows
about −5.4 mm. That cut would reduce the station's inertia about the tube axis:

- now: about 2.19e-4 kg·m², `EST` from `model_cfg` parts
- after −5 mm: about 1.81e-4 kg·m² (−17 %)

That is +10 % in f1 for pure torsion, but the mode is coupled lateral-torsion, so the real gain is less. It also has
side effects:

- It moves the prop plane `propulsion.stations.x_prop_plane_m`, which is shared and belongs to stream A / E1.
- The tip gap and the prop-gap ratio approach their limits.
- The CG moves aft by about 0.9 mm, `EST`.
- The mount stiffness geometry changes.

It was not run.

### d. Mount or fin stiffening

S1 measured a mount rocking stiffness × 1.5 at +0.9 % and a 10 × 3 brace at +1.2 %. Neither is enough alone.

### e. Notch filter

A notch is a mitigation only and does not change the mode.

## 4. Next step the restructured round should take

Run the 3-D model on the lower quarter at mesh L2 with E 90.2 / G 20.5 GPa, OD 22.23 mm, ID 19.05 mm and mu
0.156 kg/m. If it passes, run all three meshes on both quarters (`team/C4/sim/run_modes_side.py`). The cache sits in
`team/C4/sim/out/cache`, and each L2 run takes about 45–150 s (cache `_wall_s`).

## Scratch scripts

None were written. No background `sim_fin.py` run was started.
