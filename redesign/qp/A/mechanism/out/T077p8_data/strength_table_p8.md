Geometry: {'rib': [25.0, 23.0], 'fil_w': 12.0, 'slv_a': 7.3, 'A_fin': 3259.0002616944544, 'A_cen': 3308.728827831719, 'n_ply': 3, 'flange': {'A': 1465.5, 'J': 1489155.9296875037}, 'plate': {'A': 1962.4999999999998, 'J': 2870187.8906250037}, 'sleeve': {'t': 1.15, 'Am': 149.86453793439765, 'Z': 172.77272230501373, 'A': 57.837500000000006}}

| Part | Row | RB | x1.5 | x2.23 | Verdict at x2.23 | Governing case |
|---|---|---|---|---|---|---|
| Bridge CGE-004 16x14 (CF; shortened to x 51.5) | B3 bridge-in-socket bond, axial + torque (integrity class) | 1.85 | 1.23 | 0.83 | integrity class: < 1 | hard 7/7 combo z0.02 mu0.40 |
| Bridge CGE-004 16x14 (CF; shortened to x 51.5) | B1 bridge bending at the socket mouth x 27.5 (350 MPa EST, KF) | 2.29 | 1.52 | 1.03 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C3p flange bond peel from the out-of-plane share (half the hub Mz, Mx; integrity class) | 1.12 | 0.75 | 0.50 | integrity class: < 1 | hard 7/7 combo z0.10 mu0.40 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C1 sleeve: torsion (Bredt, wall 1.15 mm at the flats) + bending (half the hub Mx, Mz at the spar axis), von Mises x KF <= 240 | 2.33 | 1.55 | 1.04 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C3 flange-to-bulkhead bond, polar shear (T_half; flange area 1466 mm2, J 1.49e+06 mm4, r 60.4 mm), epoxy 2.0 | 2.61 | 1.74 | 1.17 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C2 sleeve-to-flange junction (integral, 1.0 mm flange round the sleeve), von Mises x KF | 3.07 | 2.05 | 1.38 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C6 socket boss annulus (OD 20.1 / 16.1) at the socket end x 51.5: bending hypot(My, Mz) + axial, von Mises x KF | 4.17 | 2.78 | 1.87 | PASS | hard 10 wide + drift .5 y z0.10 mu0.30 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C4 centre bulkhead-to-skin tape lap (one bulkhead per side, 8 mm lap; outboard lap only below: the flange slit), epoxy 2.0 | 5.61 | 3.74 | 2.51 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C5 centre bulkhead in-plane shear (0.5 mm CF), S 70 MPa lower bound (EST) | 12.26 | 8.17 | 5.50 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | C7 6061 socket wall bearing under the bridge (6M/(D L^2) + V/(D L), D 16, L 24), bearing yield 386 MPa (ASM / aerospacemetals.com data sheet, typical, e/D 2.0, read 2026-11-21), KF | 23.13 | 15.42 | 10.37 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N4a rib strap laps on the skin (Mz, Fy; one 8 mm lap per strap, 2 straps), epoxy 2.0 | 2.50 | 1.67 | 1.12 | PASS | hard 16 wide + drift .5 y z0.10 mu0.40 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N3 rib-to-bulkhead flox fillet, per flank (My, Fz, rib torsion Mx as a z-couple), L 105.5 mm, width 12 mm (EST), epoxy 2.0 | 3.00 | 2.00 | 1.35 | PASS | hard 16 wide + drift .5 y z0.10 mu0.30 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N5 in-plane plates bonded on the skin, polar group (Mz at the plate centroid; 2 plates, area 1962 mm2 each less the rib notch, J 2.87e+06 mm4) | 5.61 | 3.74 | 2.52 | PASS | hard 10 wide z0.10 mu0.40 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N1 bulkhead-to-skin tape lap (2 bulkheads, 8 mm lap each, q / 2 per bulkhead), epoxy 2.0 MPa | 7.28 | 4.85 | 3.26 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N4b rib strap tension (4 plies 0/90, X 298 MPa, ACP x 0.70), half of w_y per strap | 9.99 | 6.66 | 4.48 | PASS | hard 16 wide + drift .5 y z0.10 mu0.40 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N6 skin + plate in-plane shear at the strap lap line (w_y spread both ways, 2 surfaces, 3-ply skin + 0.5 mm plate), S 70 MPa lower bound (EST) | 14.47 | 9.65 | 6.49 | PASS | hard 16 wide + drift .5 y z0.10 mu0.40 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | N2 bulkhead in-plane shear (2 x 0.5 mm CF), glass +-45 S 70 MPa as the lower bound (EST) | 15.92 | 10.61 | 7.14 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Rib FIN-002 25x23 CF | R1 rib tube at the node exit x 176 (axial Fx, torsion Mx, bending hypot(My, Mz)), CF 350 / 30, KF | 2.94 | 1.96 | 1.32 | PASS | SITL Tb_h5 wide (y drift) z0.10 mu0.40 |
| Rib FIN-002 25x23 CF | R2 rib tube at the root-block mouth x 255, KF | 2.94 | 1.96 | 1.32 | PASS | SITL Tb_h5 wide (y drift) z0.10 mu0.40 |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P6 ring-to-socket junction (16.5 x 29 mm), interlayer 9.5 | 0.82 | 0.54 | 0.37 | **FAIL** | hard 7/7 combo z0.10 mu0.40 |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P8 socket wall, PETG box 29 / bore 25, bending + torsion, interlayer 9.5 | 1.10 | 0.73 | 0.49 | **FAIL** | hard 16 wide + drift .5 y z0.10 mu0.30 |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P7 socket: rib bearing, compression side (PETG 20) | 3.60 | 2.40 | 1.61 | PASS | hard 16 wide + drift .5 y z0.10 mu0.30 |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P7 socket: rib epoxy bond (D25 x 31): shear | 5.40 | 3.60 | 2.42 | PASS | SITL Tb_h5 wide (y drift) z0.10 mu0.40 |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P5 ring epoxy bond on the fin tube (D16 x 60): shear | 7.34 | 4.89 | 3.29 | PASS | hard 16 wide + drift .5 y z0.10 mu0.40 |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | P5 ring bond: bearing, compression side (PETG 20) | 7.95 | 5.30 | 3.57 | PASS | hard 16 wide + drift .5 y z0.10 mu0.30 |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | K1 skin shear at the fin node (T / 2A, all torque in the skin), S 70 MPa | 2.58 | 1.72 | 1.16 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | K2 skin wrinkling, torsion (0.5 (E1 Ef Gf)^(1/3) = 80.83 MPa, EST formula) | 2.96 | 1.97 | 1.33 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | K3 skin shear at the centre bulkheads (T_half / 2A), S 70 MPa | 3.97 | 2.65 | 1.78 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.35 | 2.73 | 1.82 | 1.23 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.285 (clamp node, outboard side, no truss) | 2.73 | 1.82 | 1.23 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.228 | 2.73 | 1.82 | 1.23 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.060 | 2.73 | 1.82 | 1.23 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 foam shear (cell), y 0.040 | 2.73 | 1.82 | 1.23 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.285 (clamp node, outboard side, no truss) | 2.74 | 1.83 | 1.23 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.228 | 2.76 | 1.84 | 1.24 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.060 | 2.76 | 1.84 | 1.24 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.040 | 2.76 | 1.84 | 1.24 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 skin shear+axial interaction, y 0.35 | 2.78 | 1.85 | 1.25 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.285 (clamp node, outboard side, no truss) | 4.41 | 2.94 | 1.98 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.285 (clamp node, outboard side, no truss) | 4.69 | 3.12 | 2.10 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.040 | 4.91 | 3.27 | 2.20 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.228 | 4.91 | 3.27 | 2.20 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.060 | 4.91 | 3.27 | 2.20 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.040 | 5.22 | 3.48 | 2.34 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.228 | 5.22 | 3.48 | 2.34 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.060 | 5.22 | 3.48 | 2.34 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 foam bending + axial, y 0.35 | 6.50 | 4.33 | 2.92 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 cove CF strip, y 0.35 | 6.90 | 4.60 | 3.10 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.35 | 11.32 | 7.55 | 5.08 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.285 (clamp node, outboard side, no truss) | 11.32 | 7.55 | 5.08 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.228 | 11.32 | 7.55 | 5.08 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.060 | 11.32 | 7.55 | 5.08 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P15 spar torsion, y 0.040 | 11.32 | 7.55 | 5.08 | PASS | hard 7/7 combo z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.040 | 20.66 | 13.77 | 9.27 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.228 | 20.66 | 13.77 | 9.27 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.060 | 20.66 | 13.77 | 9.27 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.285 (clamp node, outboard side, no truss) | 30.28 | 20.19 | 13.58 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | P16 spar bending + axial, y 0.35 | 42.57 | 28.38 | 19.09 | PASS | hard 10 wide + drift .5 y z0.10 mu0.40 |

| Record | Value | Case |
|---|---|---|
| Bridge CGE-004 16x14 (CF; shortened to x 51.5): B2 bridge CF wall bearing stress in the 6061 socket at x2.23 x KF [MPa]; CF bearing allowable "-" (TP-4 coupon) | 37.22 | hard 10 wide + drift .5 y z0.10 mu0.40 |
| Demand record: max fin /My/ into the cell at the rib axis [N m, RB] | 13.29 | hard 7/7 combo z0.10 mu0.40 |
| Demand record: max half-wing /My/ at the spar axis (sleeve / flange torque T_half) [N m, RB] | 8.76 | hard 7/7 combo z0.10 mu0.40 |
| Demand record: max hub /My/ at the spar axis [N m, RB] | 12.83 | SITL Z5_b45 narrow (z drift) z0.10 mu0.30 |
| Demand record: max rib Mx at the node exit x 176 [N m, RB] | 5.14 | SITL Tb_h5 wide (y drift) z0.10 mu0.40 |
| Demand record: max rib My at the node exit x 176 [N m, RB] | 10.01 | hard 16 wide + drift .5 y z0.10 mu0.30 |
| Demand record: max rib Mz at the node exit x 176 [N m, RB] | 10.00 | hard 16 wide + drift .5 y z0.10 mu0.40 |

| Part | min RF at x2.23 (RF class only) |
|---|---|
| Bridge CGE-004 16x14 (CF; shortened to x 51.5) | 1.03 |
| Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem 7.3 mm, bore 12.3, flanges 1.0 mm, bridge socket boss OD 20.1) + bulkheads WNG-013 | 1.04 |
| Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate) | 1.12 |
| Rib FIN-002 25x23 CF | 1.32 |
| Root block FIN-003 (PETG, socket 29 x 29 for the 25 mm rib; drawn block, not the tallied enlargement) | 0.37 |
| Skin WNG-011 + WNG-014: 3 plies 48 g/m2 glass +-45 over |y| 0.052-0.400 | 1.16 |
| Wing section (landing_path_a P15 / P16, 3-ply skin, GJ share; outboard stations unchanged) | 1.23 |
