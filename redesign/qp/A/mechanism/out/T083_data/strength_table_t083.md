# T-083 strength rows at x2.23 (D-223 DAF, KF 1.725, KP 2.156; RF >= 1.0 required for class RF; integrity rows outside the minimum)

Demand: T-083 re-run (t083_demand.py): 1.913 kg simulated (the p6 demand was simulated at 1.64 kg, see T083_report s5), tallied CG 24.41 mm (after the 3 mm cage shift), pad Fp 36 N / 24 mm, 23 cases x zeta 0.02 / 0.05 / 0.10 x mu 0.40 / 0.30.

| Part | Row | class | p8 x2.23 | T-083 all zeta | zeta 0.02 | zeta 0.05 | zeta 0.10 | all zeta, rib 14x12 | zeta 0.02, rib 14x12 | verdict (all zeta, 25x23) |
|---|---|---|---|---|---|---|---|---|---|---|
| Bridge CGE-004 16x14 (CF; shortened to x 51.5) | B3 bridge-in-socket bond, axial + torque (integrity class) | integrity | 0.83 | 0.70 | 0.70 | 1.00 | 0.83 | 0.70 | 0.70 | integrity class: < 1 |
| Bridge CGE-004 16x14 (CF; shortened to x 51.5) | B1 bridge bending at the socket mouth x 27.5 (350 MPa EST, KF) | RF | 1.03 | 0.93 | 1.39 | 1.21 | 0.93 | 0.93 | 1.39 | **FAIL** |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C3p flange bond peel from the out-of-plane share (half the hub Mz, Mx; integrity class) | integrity | 0.50 | 0.46 | 0.53 | 0.58 | 0.46 | 0.46 | 0.53 | integrity class: < 1 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C3 flange-to-bulkhead bond, polar shear (T_half; flange area 1466 mm2, J 1.49e+06 mm4, r 60.4 mm), epoxy 2.0 | RF | 1.17 | 0.66 | 1.16 | 1.18 | 0.66 | 0.66 | 1.16 | **FAIL** |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C1 sleeve: torsion (Bredt, wall 1.15 mm at the flats) + bending (half the hub Mx, Mz at the spar axis), von Mises x KF <= 240 | RF | 1.04 | 0.75 | 1.27 | 1.19 | 0.75 | 0.75 | 1.27 | **FAIL** |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C2 sleeve-to-flange junction (integral, 1.0 mm flange round the sleeve), von Mises x KF | RF | 1.38 | 0.77 | 1.36 | 1.39 | 0.77 | 0.77 | 1.36 | **FAIL** |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C4 centre bulkhead-to-skin tape lap (one bulkhead per side, 8 mm lap; outboard lap only below: the flange slit), epoxy 2.0 | RF | 2.51 | 1.41 | 2.48 | 2.53 | 1.41 | 1.41 | 2.48 | PASS |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C6 socket boss annulus (OD 20.1 / 16.1) at the socket end x 51.5: bending hypot(My, Mz) + axial, von Mises x KF | RF | 1.87 | 1.70 | 2.45 | 2.19 | 1.70 | 1.70 | 2.45 | PASS |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C5 centre bulkhead in-plane shear (0.5 mm CF), S 70 MPa lower bound (EST) | RF | 5.50 | 3.08 | 5.43 | 5.54 | 3.08 | 3.08 | 5.43 | PASS |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C7 6061 socket wall bearing under the bridge (6M/(D L^2) + V/(D L), D 16, L 24), bearing yield 386 MPa (ASM / aerospacemetals.com data sheet, typical, e/D 2.0, read 2026-11-21), KF | RF | 10.37 | 9.39 | 13.98 | 12.20 | 9.39 | 9.39 | 13.98 | PASS |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N3 rib-to-bulkhead flox fillet, per flank (My, Fz, rib torsion Mx as a z-couple), L 105.5 mm, width 12 mm (EST), epoxy 2.0 | RF | 1.35 | 0.83 | 1.58 | 1.41 | 0.83 | 0.74 | 1.23 | **FAIL** |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N4a rib strap laps on the skin (Mz, Fy; one 8 mm lap per strap, 2 straps), epoxy 2.0 | RF | 1.12 | 0.94 | 1.24 | 1.11 | 0.94 | 0.94 | 1.24 | **FAIL** |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N5 in-plane plates bonded on the skin, polar group (Mz at the plate centroid; 2 plates, area 1962 mm2 each less the rib notch, J 2.87e+06 mm4) | RF | 2.52 | 2.11 | 2.84 | 2.53 | 2.11 | - | - | PASS |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N1 bulkhead-to-skin tape lap (2 bulkheads, 8 mm lap each, q / 2 per bulkhead), epoxy 2.0 MPa | RF | 3.26 | 2.14 | 3.71 | 3.28 | 2.14 | 2.14 | 3.71 | PASS |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N4b rib strap tension (4 plies 0/90, X 298 MPa, ACP x 0.70), half of w_y per strap | RF | 4.48 | 3.75 | 4.96 | 4.42 | 3.75 | 3.75 | 4.96 | PASS |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N2 bulkhead in-plane shear (2 x 0.5 mm CF), glass +-45 S 70 MPa as the lower bound (EST) | RF | 7.14 | 4.68 | 8.12 | 7.17 | 4.68 | 4.68 | 8.12 | PASS |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N6 skin + plate in-plane shear at the strap lap line (w_y spread both ways, 2 surfaces, 3-ply skin + 0.5 mm plate), S 70 MPa lower bound (EST) | RF | 6.49 | 5.44 | 7.19 | 6.40 | 5.44 | 5.44 | 7.19 | PASS |
| Rib FIN-002 25x23 CF | R2 rib tube at the root-block mouth x 255, KF | RF | 1.32 | 1.06 | 1.14 | 1.16 | 1.06 | - | - | PASS |
| Rib FIN-002 25x23 CF | R1 rib tube at the node exit x 176 (axial Fx, torsion Mx, bending hypot(My, Mz)), CF 350 / 30, KF | RF | 1.32 | 1.06 | 1.14 | 1.16 | 1.06 | - | - | PASS |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P6 ring-to-socket junction (16.5 x 29 mm), interlayer 9.5 | RF | 0.37 | 0.25 | 0.44 | 0.39 | 0.25 | - | - | **FAIL** |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P8 socket wall, PETG box 29 / bore 25, bending + torsion, interlayer 9.5 | RF | 0.49 | 0.31 | 0.60 | 0.53 | 0.31 | - | - | **FAIL** |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P7 socket: rib bearing, compression side (PETG 20) | RF | 1.61 | 0.99 | 1.90 | 1.67 | 0.99 | - | - | **FAIL** |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P7 socket: rib epoxy bond (D25 x 31): shear | RF | 2.42 | 1.95 | 2.10 | 2.14 | 1.95 | - | - | PASS |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P5 ring bond: bearing, compression side (PETG 20) | RF | 3.57 | 2.34 | 4.56 | 3.96 | 2.34 | - | - | PASS |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P5 ring epoxy bond on the fin tube (D16 x 60): shear | RF | 3.29 | 2.76 | 3.64 | 3.24 | 2.76 | - | - | PASS |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | K1 skin shear at the fin node (T / 2A, all torque in the skin), S 70 MPa | RF | 1.16 | 0.76 | 1.32 | 1.16 | 0.76 | 0.76 | 1.32 | **FAIL** |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | K2 skin wrinkling, torsion (0.5 (E1 Ef Gf)^(1/3) = 80.83 MPa, EST formula) | RF | 1.33 | 0.87 | 1.51 | 1.33 | 0.87 | 0.87 | 1.51 | **FAIL** |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | K3 skin shear at the centre bulkheads (T_half / 2A), S 70 MPa | RF | 1.78 | 1.00 | 1.76 | 1.80 | 1.00 | 1.00 | 1.76 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.35 | RF | 1.23 | 0.80 | 1.39 | 1.23 | 0.80 | 0.80 | 1.39 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.285 (clamp node, outboard side, no truss) | RF | 1.23 | 0.80 | 1.39 | 1.23 | 0.80 | 0.80 | 1.39 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.228 | RF | 1.23 | 0.80 | 1.39 | 1.23 | 0.80 | 0.80 | 1.39 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.060 | RF | 1.23 | 0.80 | 1.39 | 1.23 | 0.80 | 0.80 | 1.39 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.040 | RF | 1.23 | 0.80 | 1.39 | 1.23 | 0.80 | 0.80 | 1.39 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.285 (clamp node, outboard side, no truss) | RF | 1.23 | 0.82 | 1.42 | 1.26 | 0.82 | 0.82 | 1.42 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.228 | RF | 1.24 | 0.82 | 1.42 | 1.26 | 0.82 | 0.82 | 1.42 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.060 | RF | 1.24 | 0.82 | 1.42 | 1.26 | 0.82 | 0.82 | 1.42 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.040 | RF | 1.24 | 0.82 | 1.42 | 1.26 | 0.82 | 0.82 | 1.42 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.35 | RF | 1.25 | 0.82 | 1.42 | 1.26 | 0.82 | 0.82 | 1.42 | **FAIL** |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.285 (clamp node, outboard side, no truss) | RF | 1.98 | 1.66 | 2.63 | 2.15 | 1.66 | 1.66 | 2.63 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.285 (clamp node, outboard side, no truss) | RF | 2.10 | 1.76 | 2.79 | 2.28 | 1.76 | 1.76 | 2.79 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.060 | RF | 2.20 | 1.84 | 2.92 | 2.38 | 1.84 | 1.84 | 2.92 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.228 | RF | 2.20 | 1.84 | 2.92 | 2.38 | 1.84 | 1.84 | 2.92 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.040 | RF | 2.20 | 1.84 | 2.92 | 2.38 | 1.84 | 1.84 | 2.92 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.060 | RF | 2.34 | 1.95 | 3.10 | 2.53 | 1.95 | 1.95 | 3.10 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.228 | RF | 2.34 | 1.95 | 3.10 | 2.53 | 1.95 | 1.95 | 3.10 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.040 | RF | 2.34 | 1.95 | 3.10 | 2.53 | 1.95 | 1.95 | 3.10 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.35 | RF | 2.92 | 2.44 | 3.62 | 3.16 | 2.44 | 2.44 | 3.62 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.35 | RF | 3.10 | 2.59 | 3.84 | 3.35 | 2.59 | 2.59 | 3.84 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.35 | RF | 5.08 | 3.33 | 5.77 | 5.10 | 3.33 | 3.33 | 5.77 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.285 (clamp node, outboard side, no truss) | RF | 5.08 | 3.33 | 5.77 | 5.10 | 3.33 | 3.33 | 5.77 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.228 | RF | 5.08 | 3.33 | 5.77 | 5.10 | 3.33 | 3.33 | 5.77 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.060 | RF | 5.08 | 3.33 | 5.77 | 5.10 | 3.33 | 3.33 | 5.77 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.040 | RF | 5.08 | 3.33 | 5.77 | 5.10 | 3.33 | 3.33 | 5.77 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.228 | RF | 9.27 | 7.81 | 12.42 | 10.13 | 7.81 | 7.81 | 12.42 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.060 | RF | 9.27 | 7.81 | 12.42 | 10.13 | 7.81 | 7.81 | 12.42 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.040 | RF | 9.27 | 7.81 | 12.42 | 10.13 | 7.81 | 7.81 | 12.42 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.285 (clamp node, outboard side, no truss) | RF | 13.58 | 11.37 | 18.03 | 14.72 | 11.37 | 11.37 | 18.03 | PASS |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.35 | RF | 19.09 | 15.99 | 22.20 | 19.77 | 15.99 | 15.99 | 22.20 | PASS |

| Part | T-083 all zeta | zeta 0.02 | zeta 0.05 | zeta 0.10 | all zeta, rib 14x12 | zeta 0.02, rib 14x12 |
|---|---|---|---|---|---|---|
| Bridge CGE-004 16x14 (CF; shortened to x 51.5) | 0.93 | 1.39 | 1.21 | 0.93 | 0.93 | 1.39 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | 0.66 | 1.16 | 1.18 | 0.66 | 0.66 | 1.16 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | 0.83 | 1.24 | 1.11 | 0.83 | 0.74 | 1.23 |
| Rib FIN-002 25x23 CF | 1.06 | 1.14 | 1.16 | 1.06 | nan | nan |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | 0.25 | 0.44 | 0.39 | 0.25 | nan | nan |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | 0.76 | 1.32 | 1.16 | 0.76 | 0.76 | 1.32 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | 0.80 | 1.39 | 1.23 | 0.80 | 0.80 | 1.39 |

| Record (RB) | p8 | T-083 all | zeta 0.02 | zeta 0.10 | case (all) |
|---|---|---|---|---|---|
| Bridge CGE-004 16x14 (CF; shortened to x 51.5): B2 bridge CF wall bearing stress in the 6061 socket at x2.23 x KF [MPa]; CF bearing allowable "-" (TP-4 coupon) | 37.22 | 41.12 | 27.61 | 41.12 | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Demand record: max fin |My| into the cell at the rib axis [N m, RB] | 13.29 | 20.26 | 11.69 | 20.26 | hard 7/7 combo z0.10 mu0.30 |
| Demand record: max half-wing |My| at the spar axis (sleeve / flange torque T_half) [N m, RB] | 8.76 | 15.62 | 8.87 | 15.62 | hard 7/7 combo z0.10 mu0.30 |
| Demand record: max hub |My| at the spar axis [N m, RB] | 12.83 | 14.57 | 12.05 | 14.57 | SITL Z5_b45 narrow (z drift) z0.10 mu0.30 |
| Demand record: max rib Mx at the node exit x 176 [N m, RB] | 5.14 | 6.38 | 5.94 | 6.38 | SITL Tb_h5 wide (y drift) z0.10 mu0.40 |
| Demand record: max rib My at the node exit x 176 [N m, RB] | 10.01 | 18.15 | 9.84 | 18.15 | hard 7/7 combo z0.10 mu0.30 |
| Demand record: max rib Mz at the node exit x 176 [N m, RB] | 10.00 | 11.93 | 9.03 | 11.93 | hard 16 wide + drift .5 y z0.10 mu0.40 |
