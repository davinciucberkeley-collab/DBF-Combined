# QP-3 structures, concept A (scaled quad tailsitter), 2026-11-15

Group: structures (C1 loads, C2 wing, C4 arms/fins/vibration, C5 landing, C6 joints). Gate 1.50 kg. Files: `qp/A/structures/` (`structures_a.py` roll-up, `fe_a.py` 3-D beam FE, `landing_a.py` 3-D landing sim, `structures_run.md` full printed tables). Reproduce: `python -I redesign/qp/A/structures/structures_a.py` (about 1 min; numpy, scipy). K09-L files not edited; no git. Labels: `EST` estimate, `V` vendor page, `CALC` computed here, `-` unknown. Design load = limit x 1.5 x 1.15 (CF, metal) and x 1.25 more for printed or bonded (K09-L factors). Allowables are K09-L's (C2/C6), unverified until coupons.

## Verdict

A's structure closes on strength everywhere. Two items are marginal (cage pitch softness, foot side load) and one **fails the 20 % rotor separation: the wing-box (spar/rib) mode near 100 Hz sits on hover 1P at the stiff property corner**, which K09-L's wing also could not clear. It is closed by forced response, which passes at the knock-down and nominal corners and fails at the stiff corner unless every prop is balanced to <= 0.3 g mm. Structure bottom-up is 492 g against 460 g allocated (+32 g; net -11 g on the 1,381 g prediction once growth falls from EST 20 % to CALC 10 %, `EST`). Nothing here moves the gate.

| Area | Result |
|---|---|
| Mass | wing 209 / 220, fins 121 / 70 (**+51**), cage 122 / 135, hardware 40 / 35: **492 / 460** |
| C1 loads | n limit +3.4 / -1.5 governs; the wing cannot reach the 8 m/s gust n (stall-limited 1.98 at 17 m/s) |
| C2 wing | spar 16x14 MS +6.1; foam MS >= +0.5; PASS |
| C4 arms | first arm modes 47-59 Hz (kd); the 87 Hz arm/hub mode at the stiff corner is 17 %: MARGINAL |
| C4 fin | out-of-plane f1 479 (kd) to 555 (hi) Hz, 48 % above cruise 2P: PASS with the 15 mm / 0.1 mm laminate |
| C4 wing box | spar/rib mode 86-118 Hz on hover 1P: **FAIL** on separation; forced response MS +0.2 / +0.2 / **-0.5** (kd / nom / hi, worst of hover and cruise) |
| C5 | tip-over 33.2 deg PASS; worst foot stroke 15.2 of 20 mm PASS; peak 10.8 g PASS; side load 14-19 N MARGINAL |
| C6 | every joint RF >= 1.34; thinnest: foot-shoe bond 1.34, arm socket and saddle bonds 1.55 |

## 1. Minimum structure (what is built)

| Part | Design (CAD numbers) | Source |
|---|---|---|
| Wing | XPS core 30 kg/m3, 9.5 % section 23 mm, b 0.90, c 0.245; spar CF tube 16x14 x 0.90 m at x = 60 mm (0.245 c); 1 layer packing tape per side; PETG plugs in the spar at y = 0, +-0.38; elevons end at \|y\| 0.34 | C2 method, scaled |
| Fins (2) | 0.36 x 0.12 m at y = +-0.38 (outside the prop disk, which ends at y 0.342), x 0.18-0.30; XPS core **15 mm**, CFRP skins **0.1 mm** (BOM R04 changes from 0.2 mm), 0.173 m2; feet at x = 0.30, z = +-0.18 | C4 fin model |
| Fin root | **CF rib tube 14x12 x 0.20 m** from a spar saddle (16 x 30 mm wrap) to a PETG root block on the fin at x 0.24; rib torsion is a deliberate soft root | new |
| Cage | PETG hub at (x -0.075, 0, 0) with the pack tray; **4 arms CF 14x12 x 0.245 m** (radius 0.276, motors at y 0.228 / z 0.156), 25 mm sockets, PETG motor cups; **bridge CF 8x6 x 0.16 m** from hub to spar centre, with a saddle | new |
| Feet | PETG shoe, EVA/PE pad 12 x 15 mm x 30 mm, plateau 30 N per foot, usable stroke 20 mm | `EST` |

Why arms 14x12 and bridge 8x6 (not 16x14 and 12x10): with stiffer parts the hub-rocking mode sits at 96-130 Hz on hover 1P. Softer parts move every strongly motor-coupled mode below 0.8 x 1P (bridge 8x6: top mode 80 Hz at the stiff corner; 10x8: 87-104 Hz, fails). The price is **hub pitch rotation 2.0 deg at the largest control moment and a cage pitch mode at 40-47 Hz** (FC filter and notch must be set for it; MARGINAL). Tube buy: 16x14 x 1 (spar), **14x12 x 2** ($15.34 each, RMRC listing snippet read 2026-11-15, page not opened), 8x6 x 1 (price `-`); R02's second 16x14 ($27.46) drops out: net about +$3.22 plus the 8x6.

## 2. Mass per part (g)

| Group | Bottom-up | MASS-GATE | Delta | Main items |
|---|---|---|---|---|
| Wing | 209 | 220 | -11 | core 95, spar 68, tape 24, plugs/hinges 14, glue 8 |
| Fins | 121 | 70 | **+51** | skins 28, core 39, 4 feet 16, 2 root blocks 12, 2 rib tubes 26 |
| Cage | 122 | 135 | -13 | arms 64, hub 20, cups 20, bridge 12, epoxy 6 |
| Hardware | 40 | 35 | +5 | `EST` |
| **Total** | **492** | **460** | **+32** | |

The 70 g fin allocation predates the root tie: ribs and blocks (38 g) and the thick core (+26 g over 5 mm) are the overrun. The thick core is what lifts f1 above cruise 2P (a 5 mm core gives 221-253 Hz, on hover 2P). A3 should move 51 g to the fins line and take 13 g from the cage and 11 g from the wing. All `EST`: weigh parts at the first build.

## 3. C1 loads

| Case | Value |
|---|---|
| Vs (CLmax 0.75, 1.50 kg) | 12.07 m/s (REQUIREMENTS-A: 12.19; density or area differs slightly) |
| Gust 8 m/s at VC 17 | n 3.85 by the Pratt formula (Kg 0.613) but stall line 1.98: not reachable |
| Gust 4 m/s at VD 22 | 2.85 (stall line 3.32) |
| Limit n | +3.4 / -1.5 (A-P13), ult +5.1 / -2.25; VA 22.2 |
| Spar root bending | 4.78 N m unrelieved (design), 1.84 relieved |
| Hover 8 m/s gust | wing force 17.2 N, spar root 1.94 N m |
| Largest control pitch moment on the bridge | 2.44 N m (upper pair at the 0.90 cap, 8.8 N each) |
| Prop strike (30 N, `EST`) | arm root 7.4 N m, bridge 4.7 N m (the bridge is the weakest CF part and acts as the fuse) |
| Transport drop 0.3 m | v 2.43 m/s; n = 24 / 17 / 12 / 10 g at cradle stroke 25 / 35 / 50 / 60 mm (eta 0.5); hub and bridge tolerate about 22 g; box cradle `-`, needs >= 40 mm |
| Landing | section 6 |

## 4. C2 wing (ultimate x fitting)

| Check | Stress | Allowable | MS | Result |
|---|---|---|---|---|
| Spar bending (8.2 N m) | 50 MPa | 350 | +6.1 | PASS |
| Spar shear | 1.8 MPa | 30 | +15 | PASS |
| Tip deflection at n 3.4 | 5.7 mm (1.3 % of semispan) | 5 % | | PASS |
| Foam shear around the spar from the bridge torque (2.44 N m) | 65 kPa | 100 | +0.53 | PASS |
| Foam bearing at the fin slot (2 x 20 N side load, 65 x 23 mm) | 57 kPa | 120 | +1.11 | PASS |
| Foam shear, lift into the spar slot | 2.6 kPa | 100 | +37 | PASS |

Arms and motors load no foam: the cage hangs on the spar through the bridge saddle, and the fins load the spar through the CF ribs. Saddle pockets need R >= 3 mm corners (C6 rule from K09-L's CR-C2-11 failure). The spar needs PETG plugs under every clamp (C2: the unplugged ring failed by 20x).

## 5. C4 modes, forced response, mounts

Rotor orders (`prop_a.py`, 1.50 kg, derate 0.93): hover 6,272 rpm = 105 Hz 1P, 209 Hz 2P; 1.381 kg 6,018 rpm; 8 m/s lean 7,150 rpm. **Cruise 9,700 rpm (162 / 323 Hz) is an estimate** (APC static table only; band 8,900-10,500 rpm). FE: 3-D Euler beam frame, free-free, three property corners (kd: CF E 61 GPa, PETG 1.6; nom 70 / 2.1; hi 90 / 2.4; fin skin x 0.87 / 1 / 1.1). The design is soft: every motor-coupled mode sits below hover 1P, because no stiffness reachable at this size clears hover 2P and cruise 2P together.

| Group | Modes kd / nom / hi (Hz) | Worst separation (hover, hover light, cruise) | Result |
|---|---|---|---|
| Arm first modes (thrust and in-plane) | 47-59 / 51-63 / 57-72 | 44 / 40 / 32 % | PASS |
| Arm / hub / bridge coupled | 72-79 / 76-85 / 87-96 | 21-29 / 15-24 / 4-17 % | kd PASS, nom MARGINAL, **hi FAIL (bridge 96 Hz, 4 %)** |
| Fin out-of-plane | 479-486 / 514-521 / 543-555 | 48 / 59 / 68 % | PASS |
| Wing box (spar + rib), weakly coupled | 86-97, 207 / 92-104, 221 / 104-118, 251 | 0-3 % worst | **FAIL**, closed below |
| Arm second family | 589-700 | > 80 % | PASS |

Forced response (C2 CR-C2-16 method; worst-phase modal sum; U 1.0 g mm per rotor `EST`, an ISO G16 prop alone is 0.27 g mm; 2P axial ripple 5 % of thrust `EST`; damping 1 % `EST`); acceleration at the FC against 30 m/s2:

| Corner | Hover 1P | Hover 2P | Cruise 1P | Cruise 2P | MS (worst) |
|---|---|---|---|---|---|
| kd | 14.9 | 2.9 | 24.4 | 0.4 | +0.2 |
| nom | 17.5 | 3.0 | 25.2 | 0.4 | +0.2 |
| hi | **63.9** | 3.0 | 27.1 | 0.4 | **-0.5** |

Closure: at the stiff corner the 104 Hz wing-box mode lands on hover 1P. New requirement from this round: **balance every prop with its motor to <= 0.3 g mm** (hi hover 1P then drops to about 19 m/s2), read IMU VIBE in the first tethered hover (< 30 m/s2), and tap-test the built wing for the 90-120 Hz mode before the cage is fitted. Fin tip acceleration at 1P is 28-53 m/s2 (information; the fin stress there is small against its allowable).

Mount stiffness and strength:

| Item | Value | MS | Result |
|---|---|---|---|
| Arm root bending at the cap thrust (2.17 N m) | 30 MPa vs 350 | +10.6 | PASS |
| Arm, prop strike 7.4 N m | 103 MPa | +2.4 | PASS |
| Bridge 8x6, prop strike 4.7 N m | 235 MPa | +0.49 | PASS |
| Bridge, control pitch moment 2.44 N m | 122 MPa | +1.86 | PASS |
| Bridge, pack + hub at 12 g crash (A-P5) | 231 MPa | +0.51 | PASS |
| Arm tip stiffness / deflection at the cap | 12.2 N/mm, 0.72 mm | | info |
| Bridge buckling | P_cr 1.3 kN vs 20 N | +37 | PASS |
| Hub pitch rotation at the largest control moment | 2.0 deg | | **MARGINAL** (soft mount) |
| Rib torsion, one foot (2.7 N m) | 5.9 deg, foot 19 mm sideways, shear 18.8 of 30 MPa | RF 1.60 | **MARGINAL** stiffness |

## 6. C5 landing

Static: CG 25.2 mm aft of the LE, feet at x 0.30 / y +-0.38 / z +-0.18, CG 0.275 m above them: tip-over narrow axis **33.2 deg** (limit 30; sizing 33.2), wide axis 54.1 deg; parked tip-wind 7.4 m/s (below the 8 m/s gust: crew catches or lays it down, A-P9); restoring / overturning 2.21 at 5 m/s. Inertia about the CG 0.056 / 0.025 / 0.062 kg m2.

`landing_a.py` is the physics of K09-L `team/C5/sim/landing_sim3d.py` rebuilt standalone for A (its inputs are K09-L proof-chain nodes): 6 dof, four elasto-plastic feet, mu 0.40, lift 2/3 W to 0.3 s then 0, 1.50 kg. Attitude error 10 deg and sink 1.2 / 0.5 m/s are K09-L's, since REQUIREMENTS-A gives only 12 g on 6 mm. The 6 mm crush of SIZING-A is replaced by 20 mm usable at a 30 N plateau per foot.

| Case | Stroke (mm of 20) | Set (mm) | Foot peak (N) | Side (N) | End tilt (deg) |
|---|---|---|---|---|---|
| hard 1.2 m/s level | 8.3 | 6.8 | 40 | 0 | 0.0 |
| hard, 10 deg narrow | 13.9 | 12.4 | 40 | 14 | 1.8 |
| hard, 10 deg wide | 8.2 | 6.7 | 45 | 18 | 0.1 |
| hard, 10 narrow + 0.5 m/s drift | **15.2** | 13.7 | 40 | 16 | 2.1 |
| hard, 10 wide + drift | 11.1 | 9.6 | 47 | 19 | 0.4 |
| normal 0.5 m/s, 10 wide + drift | 5.8 | 4.3 | 40 | 16 | 0.3 |
| hard, 1.381 kg, 10 narrow | 12.9 | 11.4 | 40 | 14 | 1.6 |

Worst stroke 15.2 of 20 mm (margin 32 %): PASS. Peak foot-load factor 10.8 g < 12 (A-P5): PASS. No tip-over. Pad life: normal landings set 0.8-4.3 mm, a hard landing up to 13.7 mm; replace at 10 mm cumulative set and after any hard landing. **Side load 14-19 N per foot against a mass-scaled K09-L cap of about 14 N: MARGINAL**; pad face mu <= 0.3 brings it to about 15 N. Plateau (0.17 MPa), stroke and set are `EST`: drop-test five pad coupons before bonding.

## 7. C6 joints (RF = allowable / design stress)

| Joint | RF | Result |
|---|---|---|
| Motor, 4 x M3x8: tension (thrust, strike) | > 90 | PASS |
| Motor thread strip, 2.5 mm engagement | 40 | PASS |
| Arm in hub / cup socket, 25 mm, strike couple 330 N | 1.55 | PASS (20 mm would give 1.24) |
| Arm socket, thrust | 4.40 | PASS |
| PETG socket wall bearing | 4.72 | PASS |
| Bridge saddle on spar, 2.4 N m | 4.59 | PASS |
| Bridge into hub (strike) | 1.55 | PASS |
| Rib 14x12 root bending, both feet 40 N | 3.49 | PASS |
| Rib saddle on spar (7.2 N m couple) | 1.55 | PASS |
| Rib torsion, one foot | 1.60 | PASS |
| Fin root block bonds (skins, 60 mm rib embed) | > 29 | PASS |
| Fin skin bending / wrinkling | 13.5 / 3.4 | PASS |
| Foot shoe bond to foam, 52 N on 1,500 mm2 | 1.34 | PASS (0.1 MPa foam-bond allowable) |
| Pack tray bond at 12 g | 17 | PASS |

Bond areas: arm sockets 25 mm deep x 14 mm; saddles 30 mm wide, full wrap on the 16 mm spar; fin root blocks 60 x 40 mm both faces; foot shoe 25 x 30 mm both faces. One 30 min laminating epoxy, 120 grit + IPA, bond gap 0.1-0.3 mm (C6 rules).

## 8. Design numbers for CAD (mm)

Spar 16x14 CF x 900 at x 60, z 0; hub (-75, 0, 0); arm tubes 14x12 x 245 to motors at (-75, +-228, +-156); bridge 8x6 x 160 from hub to (60, 0, 0); fins at y +-380, x 180-300, z +-180, core 15, skin 0.1; rib 14x12 x 200 from (60, +-380, 0) to (240, +-380, 0); wing slot for the fin 65 x 23; elevon end at \|y\| 340; feet at x 300; pad 12 x 15 x 30, stroke 20; CG 25.2 aft of the LE; pocket corner radius >= 3; socket depth 25; spar plugs at y 0, +-380.

## 9. Open items and tests

1. Tap-test the built wing (90-120 Hz) and fins (expect about 480 Hz); balance props to <= 0.3 g mm; first tethered hover logs IMU VIBE (< 30 m/s2).
2. Measure cruise rpm (bench M1 + audio FFT): if cruise 2P is 350 Hz instead of 323, the fin margin falls from 48 % to about 37 % (still pass).
3. Bench the cage pitch mode (40-47 Hz) and set the FC filter and notch before hover. If the 2 deg hub rotation upsets rate control, stiffen the bridge to 10x8; the arm/hub mode then reaches 87-104 Hz and the hover 1P separation is lost at the stiff corner.
4. Foot pad coupon drop (plateau, 20 mm stroke, set per hit); side-load cap and pad mu <= 0.3.
5. All allowables are K09-L values and tube E (nom 70, hi 90 GPa) is `EST`: three-point bend one arm tube and the spar.
6. A3: move 51 g to fins, take 13 g from cage and 11 g from wing. A2: BOM R02 / R04 changes (14x12 x2, 8x6 x1 price `-`, 0.1 mm CFRP price `-`). A 12.7 % thick fin costs cruise drag (`-` not computed).


---

# Iteration 2 (A1 request: all modes clear at nominal, knock-down and stiff corners, no balancing credit, structure <= 460 g, US-stock fin materials)

Files: `qp/A/structures/iter2_run.py` (mass, modes, forced response, cage rotation), `iter2_margins.py` (strength), `iter2_eval.py`, `fe_a.py` (now parametric; `fe_a_iter1.py` keeps iteration 1), outputs `iter2_run.md`, `iter2_margins.md`. Reproduce: `python -I redesign/qp/A/structures/iter2_run.py` and `iter2_margins.py`. No git. Same labels and design factors as above.

## Verdict

| Request | Result |
|---|---|
| (1) wing-box mode off hover 1P | **Done for every motor-coupled mode, not literally for every mode.** Spar 16x14 -> 12x10 puts all strongly coupled modes (coupling >= 0.5) below 83 Hz at all three corners (highest 64 / 68 / **78 Hz**, limit 83.3). A 0.9 m spar always has bending modes in 83-420 Hz (free-free sequence 1 : 2.8 : 5.4 : 8.9); up to four per corner remain in band with coupling 0.1-0.4 (13 % of an arm mode or less): spar 215 / 230 / 261 Hz (kd / nom / hi, coupling 0.4) and bridge 349-407 Hz (0.1-0.2) |
| (2) bridge and arm / hub modes | Fixed: arm / hub mode no longer in band (arms 12x10; first arm modes 37-57 Hz, all arm-coupled modes <= 78 Hz); the 96 Hz bridge mode is gone |
| (3) cage pitch softness | Fixed: static pitch **0.50-0.58 deg** at 2.44 N m (was 2.0), yaw about the thrust axis 0.26-0.29 deg at 0.35 N m. **Correction to iteration 1:** the "cage pitch mode 40-47 Hz" there was the arm family; the cage rocked at 5-28 Hz. Now the lowest cage-coupled modes are 9 / 9 / 11 Hz (bridge 62 %, coupling 2.3, spar bending with the cage) and still inside the rate-loop band: **MARGINAL**, set the gyro filter and notch for it |
| (4) fin without CFRP sheet | CF strips on foam fail the bond (below). **Fin = 16x14 CF tube at the aft edge + 3 mm XPS fairing + tape**, all US stock. Fin f1 432 / 463 / 525 Hz (kd / nom / hi, limit 420: kd margin only 3 %) |
| Mass <= 460 g | **Not met: 473 g (+13).** Wing 191, fins 119, cage 122, hardware 40 |
| No balancing credit | Met: forced response with U = 1.0 g mm per rotor, MS +0.63 / +0.67 / +0.66 (FC accel 18.4 / 17.9 / 18.0 vs 30 m/s2) |

## What changed

| Part | Iteration 1 | Iteration 2 | Why |
|---|---|---|---|
| Spar | CF 16x14 | **CF 12x10** x 0.90 m | hover-1P wing-box mode moved from 86-118 Hz to <= 78 Hz coupled; MS +2.7, deflection 3.2 % of semispan (limit 5 %) |
| Arms | 14x12 | **12x10** x 0.245 m | arm / hub mode below 83 Hz at the stiff corner (87 -> 78) |
| Bridge | 8x6 single | **12x10 single (0.16 m) + 2 struts 6x4.5 x 0.33 m** to the spar at y +-0.30 | single 12x10 gives pitch (0.5 deg); the V gives roll / yaw; V alone left pitch at 22 deg and direct motor-to-spar braces put 100-180 Hz arm modes in band (forced response 100+ m/s2) |
| Ribs | 14x12 x 0.20 | 14x12 x 0.227 (fin tube now at x 0.294) | torsion RF 1.60 kept; 12x10 ribs would give RF 1.14 and 9.8 deg twist |
| Fin | 15 mm XPS + 0.1 mm CFRP skins | **16x14 CF tube (aft edge, foot on its end)** + 3 mm XPS + tape | no US-stock thin CFRP |
| Saddles | 30 mm | rib saddles 60 mm wide | bond RF 1.34 on the 12 mm spar |

Fin materials tried, with US stock checked 2026-11-15 (RMRC pages read unless noted): (a) CF strips 5x1 mm on 10 mm XPS (RMRC, in stock, $2.84; https://www.readymaderc.com/products/details/85955-carbon-fiber-flat-strip-5mm-x-1mm-1m-1000mm-long): stiffness passes (f1 486 Hz) but the strip-to-foam shear flow is 0.31-0.61 MPa against a 0.1 MPa foam bond: **FAIL**, the face skin must span the chord. (b) Wet-layup carbon cloth: lightest US-stock 3K plain is 193 gsm (US Composites and others, search snippet only), both faces about 57 g: fins reach about 131 g. (c) CFRP plate: thinnest US item found is Rock West 1/64 in twill, 12 x 12 (about 0.4 mm), about 100 g of skin: no. (d) The CFRP sheet at 0.1 mm stays as the 458-466 g option if A2 can source it (lead time > 4 weeks).

## Rotor bands and rpm source

Hover 6,018 rpm (1.381 kg) / 6,272 (1.50 kg) / 7,151 (8 m/s lean, 1.3 W): `qp/A/prop_a.py` hover() at derate 0.93, lean scaled by sqrt(1.3): 1P 100-119 Hz, 2P 201-238 Hz. Cruise 8,900-10,500 rpm is an **estimate** (the 4.5 in pitch gives 17 m/s at 8,923 rpm; J0 0.47 assumed; the APC file has no V > 0 data): 1P 148-175 Hz, 2P 297-350 Hz. Rule: f <= band_low / 1.2 or f >= 1.2 x band_high for all four bands, which excludes **83-420 Hz**. Corners as above (kd CF E 61 GPa, nom 70, hi 90; PETG 1.6 / 2.1 / 2.4).

## Every mode against the bands (coupling = mass-normalised |phi| summed at the four motors; arm modes 2.7-3.4; full list in `iter2_run.md`)

| Group | kd (Hz) | nom (Hz) | hi (Hz) | vs bands |
|---|---|---|---|---|
| Cage and wing flex, coupled 0.7-2.8 | 9, 14, 18, 27, 50 | 9, 15, 18, 28, 54 | 11, 17, 21, 33, 61 | below 83: pass (in the rate-loop band) |
| Arm modes, coupled 1.3-3.4 | 30, 37, 37, 38, 39, 44, 46, 64 | 32, 40, 40, 42, 47, 48, 68 | 36, 45, 45, 46, 48, 53, 56, 78 | pass; highest 64 / 68 / 78 vs 83.3 (margin 30 / 22 / **7 %**) |
| Fin tube out-of-plane (coupling 0.0) | 432 | 463 | 525 | pass (limit 420; kd margin 3 %) |
| Coupled modes above the bands | >= 448 | >= 480 | >= 582 | pass |
| **In band, weak coupling** | 215 (0.4); 349, 360, 361 (0.1) | 230 (0.4); 369 (0.2); 382, 387 (0.1) | 261 (0.4); 407 (0.1) | **not clear**; closed by the forced response below |

Forced response (C2 method; worst-phase modal sum; U 1.0 g mm per rotor `EST`, an ISO G16 prop alone is 0.27; 2P ripple 5 % of thrust `EST`; damping 1 % `EST`; worst of six rpm points 6,018 / 6,272 / 7,151 / 8,900 / 9,700 / 10,500): FC acceleration 18.4 / 17.9 / 18.0 m/s2 vs 30, MS +0.63 / +0.67 / +0.66. Iteration 1 was 63.9 m/s2 at the stiff corner.

## Strength margins (design = limit x 1.5 x 1.15; x 1.25 more for printed or bonded; K09-L allowables)

| Item | Load | Design stress (MPa) | Allowable | MS | Result |
|---|---|---|---|---|---|
| Spar 12x10 root bending | 4.78 N m | 93.9 | 350 | +2.73 | PASS |
| Spar shear | 25 N | 2.5 | 30 | +11 | PASS |
| Spar tip deflection, n 3.4 | | 14.4 mm = 3.2 % | 5 % | | PASS |
| Arm 12x10 bending at the cap thrust | 2.17 N m | 42.5 | 350 | +7.2 | PASS |
| Arm, prop strike 30 N | 7.4 N m | 144.9 | 350 | +1.41 | PASS |
| Bridge 12x10, prop strike / pack 12 g crash / control pitch | 4.7 / 4.6 / 2.44 N m | 91.9 / 90.3 / 47.9 | 350 | +2.8 / +2.9 / +6.3 | PASS |
| V strut 6x4.5 buckling (axial 19 N) | | P_cr 276 N vs 33 N | | +7.4 | PASS |
| Rib 14x12 bending, both feet 40 N x 0.234 m | 9.4 N m | 130.8 | 350 | +1.68 | PASS |
| Rib torsion, one foot | 2.7 N m | 18.8 | 30 | +0.60 | PASS (twist 5.9 deg: MARGINAL stiffness as before) |
| Fin tube bending, side load / foot load | 3.6 / 7.6 N m | 37.3 / 78.8 | 350 | +8.4 / +3.4 | PASS |
| Arm in socket (25 mm), strike couple 296 N | | 1.4 | 2.0 (bond) | +0.48 | PASS |
| Bridge in hub (25 mm), strike | 188 N | 0.9 | 2.0 | +1.32 | PASS |
| Bridge saddle (30 mm wrap), 2.44 N m | | 0.8 | 2.0 | +1.58 | PASS |
| Rib saddle (60 mm wrap), 9.4 N m | 783 N | 1.5 | 2.0 | +0.34 | PASS (thinnest bond) |
| Foot shoe on the tube end; fin root block on the tube | 52 / 130 N | 0.1 / 0.3 | 2.0 | +21 / +6.2 | PASS |

Landing, tip-over (33.2 deg), foot design, motor screws and feet are unchanged from iteration 1 (the foot now sits on a CF tube end instead of foam: the shoe bond is on CF, MS +21 instead of RF 1.34). Foam bearing and shear numbers of section 4 are unchanged except that the arm-side saddle torque acts on a 12 mm spar (foam shear 65 -> 116 kPa at r 6 mm over the 0.2 m zone: MS -0.14, **FAIL**; bonding the spar to the foam over |y| <= 0.15 m instead gives 77 kPa, MS +0.30: a build rule, adopted).

## Mass vs allocation (g)

| Group | Iter 2 | Iter 1 | MASS-GATE |
|---|---|---|---|
| Wing | 191 | 209 | 220 |
| Fins | 119 | 121 | 70 |
| Cage | 122 | 122 | 135 |
| Hardware | 40 | 40 | 35 |
| **Total** | **473** | 492 | **460** |

The fin line (2 tubes 54, ribs 30, fairing 8, tape 10, shoes 10, blocks 8) is 49 g over its 70 g allocation and is why the total is 13 g over. Levers if A1 wants 460: ribs 12x10 (-4.5 g, RF 1.14, 9.8 deg twist), hardware EST 40 -> 36 (needs a counted fastener list), hub 16 -> 14. Together about 10 g: not enough on its own. The 0.1 mm CFRP-sheet fin (if sourced) is 466 g; CF strips would be 458 g but fail the bond.

## BOM changes (RMRC unless stated; prices and stock read 2026-11-15; `bom_a.py` not edited)

| Line | Change | Price | Source |
|---|---|---|---|
| R02 | 2 x 16x14 ($54.92) -> **1 x 16x14** (fin tubes, 0.72 m) | $27.46 | existing line, https://www.readymaderc.com/products/details/86475-carbon-fiber-tube-16mm-x-14mm-1m-long |
| new | **3 x 12x10** tube (spar 0.90, arms 0.98, bridge 0.16) | 3 x $12.26 in stock | https://www.readymaderc.com/products/details/carbon-fiber-tube-12mm-x-10mm-1m-long |
| new | **1 x 14x12** tube (ribs 0.454 m) | $15.34, search snippet, page not opened | https://www.readymaderc.com/products/details/carbon-fiber-tube-14mm-x-12mm-1m-long |
| new | **1 x 6x4.5** tube (V struts 0.66 m) | $4.40 in stock | https://www.readymaderc.com/products/details/carbon-fiber-tube-6mm-x-4-5mm-1m-long |
| R04 | CFRP sheet 0.2 mm ($40 EST): **removed** | -$40.00 | no US stock |
| R01 | XPS fairing 3 mm, tape skins, EVA pads inside the existing foam / tape line | `-` | not re-read |

Net about **-$10.94** before tax (tubes $83.98 vs R02 $54.92 plus R04 $40.00). No 10x8 or 8x6 tube is needed any more.

## Open after iteration 2

1. Mass 473 g vs 460: 13 g over (fin line). A1 decides between the 12x10 ribs, a counted hardware list, or sourcing the CFRP sheet.
2. Up to four weakly coupled modes per corner stay in 83-420 Hz (spar 215-261 Hz at coupling 0.4; bridge 349-407 Hz at 0.1-0.2). A physical 0.9 m spar cannot avoid them; tap-test the built wing and read IMU VIBE in the first tethered hover.
3. Highest arm mode at the stiff corner 78 Hz vs 83.3 (7 %); fin f1 432 Hz vs 420 at kd (3 %). Both rest on the estimated cruise rpm and on tube E; bend-test one 12x10 and one 16x14 tube.
4. Cage-coupled modes at 9-11 Hz are inside the rate-loop band; filter / notch setting is a flight-controls item.
5. All allowables are `EST`; the spar must be bonded to the foam over |y| <= 0.15 m (foam shear at the bridge torque).
