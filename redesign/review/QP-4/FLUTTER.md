# QP-4 C1 / C2: wing divergence, flutter and elevon (concept A), 2026-11-15

Script `qp/A/structures/flutter_a.py` (`python -I flutter_a.py`, about 2.5 min, numpy + scipy; output `flutter_run.md`). Labels: `EST` estimate, `CALC` computed here. No git. VD 24 m/s (D-186), rule G8: every speed >= 1.2 VD = **28.8 m/s** (q 508 Pa, rho 1.225). Elevons y 0.04-0.34, +-20 deg (BOARD s3), chord 0.25 c `EST` (a_model.py ELEV_FRAC).

## Verdict

| Item | Speed | x VD | G8 |
|---|---|---|---|
| Torsional divergence (EA at the spar; e/c 0.02 / 0.05 / 0.10) | 286-383 / 181-242 / 128-171 m/s (kd-hi) | > 5 | **PASS** |
| Bending-torsion flutter, fin on the tip, no motor credit | 46 / 49 / 56 (kd / nom / hi) | 1.9-2.3 | **PASS** |
| Same, worst sensitivity (fins off, kd) | 43 | 1.8 | PASS |
| Control reversal (3-D lift, e/c 0.10, kd; the 2-D strip bound is 28 m/s) | 37 | 1.5 | PASS on 3-D, **marginal on the 2-D bound** |
| **Elevon flutter, unbalanced, hinge stiffness K = 0.05-0.2 N m/rad (free play, loose servo)** | **4-9** (read: unstable at any speed) | 0.2-0.4 | **FAIL** |
| Elevon flutter, unbalanced, K = 1 / 5 N m/rad | 43 / 67 | 1.8 / 2.8 | PASS |
| Elevon, balanced 7.1 g at 30 mm (CG on the hinge), K = 0.02 / 0.2 / 5 | 33 / 29 / 55 | 1.4 / 1.2 / 2.3 | PASS (K = 0.2 is on the 28.8 line) |
| Elevon, 1.5 x balance (10.7 g at 30 mm), K = 0.02 / 0.2 / 5 | 40 / 37 / 53 | 1.7 / 1.5 / 2.2 | **PASS, recommended** |

**Only the elevon fails, and only when it is unbalanced and its hinge is soft.** The fix is a mass balance of about 11 g per elevon (22 g for the pair, `EST`) or a measured hinge stiffness >= 1 N m/rad with free play <= 1 deg. Wing flutter and divergence pass with no change; VD 24 and THR_MAX stand.

## Method and limits

1. **GJ** (`GJ_parts`): spar G 2I with the CF corner values of fe_a.py / STRUCTURES s5 (kd 61 / 3 GPa, nom 70 / 3, hi 90 / 4.5, `EST`) plus a Bredt closed box of tape skin, GJ = 4 Am^2 / (perimeter / (G_t t)). Tape: BOPP film E 2.3 GPa machine direction (BOPP patent data found by search 2026-11-15; no figure for packing tape itself), G = E / 2.8 = 0.8 GPa, kd x 0.5, hi 1.0 GPa, t 0.05 mm, one layer per side `EST`. The box runs to the elevon hinge (0.75 c) because the hinge cut opens the aft section in y 0.04-0.34. XPS shear 7 MPa (Ravago XPS LB datasheet, an analog product, not Foamular, searched 2026-11-15) makes the foam a shear web only. Result: GJ elevon zone 4.5 / 5.8 / 8.0 N m2 (kd / nom / hi), full box 5.4 / 7.6 / 10.3.
2. **Divergence**: q_D = (pi/2)^2 GJ / (c^2 e CLa s^2), clamped semispan 0.45 m, CLa 3.7 (qp/A/sitl/a_aero.py). The elastic axis is the spar (x 0.060 m = 0.245 c): foam and tape give almost no bending stiffness, so they do not move it. The AC is at 0.25 c = 0.0613 m, so e is about -0.005 c (EA ahead of the AC): no divergence tendency. Even with the EA 0.10 c aft the speed is 128 m/s at kd.
3. **Flutter**: Ritz modes (3 cantilever bending, 3 torsion) on the 0.45 m semispan; EI of the 12x10 spar; GJ above (full box); masses from the `structures_a.py` / STRUCTURES iteration-2 lists (wing 191 g, CG 0.28 semichord aft of the EA); **fin 59.6 g per tip with its CG 1.6 semichords aft of the EA** (the fin tube sits at x 0.294, behind the 0.245 chord, so the fin is the destabilising mass); strip Theodorsen aerodynamics (2 pi lift, conservative; the 3-D factor 0.59 raises the speeds 20-25 %); k-iteration per mode. The Theodorsen-Garrick T1-T19 forms are checked in the script: steady M_alpha and M_beta against a thin-airfoil integration (1 %), and flap = pitch for c = a = -1 (residual 1e-15). Limits: no 3-D tip loss; root clamped (the soft 9-11 Hz cage modes are not coupled); no slipstream (the prop disks sit 0.04 m off the wing plane, cruise delta-v about 0.2 m/s `EST`); rigid fin and rib; zero structural damping; the plain wing aero is used in the elevon zone. Motors added on the wing (forward mass, optimistic) change nothing below 53 m/s.
4. **Elevon**: 3-DOF section (h, alpha, beta), hinge at 0.50 semichord; elevon 10 g (foam 4.4, tape 2.4, block 3 `EST`), CG 0.35 of its chord aft of the hinge `EST`; f_h 12.4 and f_alpha 43.9 Hz from the modal run (nom). The hinge stiffness K per elevon is unknown: the ES3352HV (stall 1.7-2.4 kgf-cm, REQUIREMENTS-A A-P11, `U`) gives about 4.5 N m/rad if it corrects 3 deg at stall (`EST`) and **zero inside the free-play band**; rod and horn compliance is negligible (a 2 mm CF rod gives about 200 N m/rad). Hence the K sweep. At K 0.05-0.2 the elevon rotation (13-26 Hz) sits on the wing bending mode (12 Hz) and the aft elevon CG drives bending-elevon flutter; the 4-9 m/s values are low-k coalescence and mean "unstable at any speed", not a precise number.
5. **Reversal**: torsion rod with the elevon load (CLd = 2 T10, thin-airfoil flap theory, Cm_d about the EA -0.65 per rad on c, hinge at 0.75 c) and the roll effectiveness integrated to zero. A servo held at K = 5 loses about 7 % of its deflection at 28.8 m/s (aerodynamic hinge stiffness -0.54 N m/rad per elevon at 28.8 m/s, -0.375 at 24, `CALC`); at K = 0.2 it loses 73 %, a second reason the hinge must not be soft.

## Design fixes, mass, cost

| Fix | Mass | Notes |
|---|---|---|
| Elevon mass balance: lead or tungsten 10.7 g per elevon on a 30 mm horn ahead of the hinge (1.5 x the CG-on-hinge amount); 7.1 g at 45 mm if the wing is thick enough | **+21 g for both** (wing 191 -> 212 g, structure 473 -> 494 g against the 460 g gate; A3 carries it, `EST`) | the one item that fails; about $3 `EST` |
| Lighter elevon (balsa or 2 mm foam) | about -2 g each | balance mass scales with elevon mass x CG offset |
| Hinge stiffness: servo on the horn, 2 mm CF rod, horn >= 12 mm, free play <= 1 deg | 0 | measure K (coupon test step 5); at K >= 1 N m/rad the unbalanced elevon passes at 1.8 VD |
| Wing spar position, torsion tape | 0 | not needed: flutter speed barely changes with GJ (2 to 8 N m2: 50 to 49 m/s) because the fin mass, not the torsion stiffness, is the limit |
| If the balance is rejected | | VD 24 / THR_MAX stay only if K >= 1 N m/rad is measured; K < 0.5 needs the balance |

## Torsion coupon test (about $5 of XPS, 20 min)

1. Cut a **300 mm** wing section of the real core (0.245 c, 23 mm) with the 12x10 spar bonded as built, one tape layer per side, plywood or PETG end caps bonded to the spar plugs, and the **elevon cut and hinge slot** as in y 0.04-0.34 (box open aft of 0.75 c). Make a second coupon without the spar (foam and tape only) to separate GJ_box from GJ_spar.
2. Clamp one end in a vise (cap, not the spar); bond a 250 mm stiff arm (CF or wood) at the free end, perpendicular to the chord.
3. Hang 100 / 200 / 300 g on the arm tip (T = 0.25 / 0.49 / 0.74 N m). Read the twist with a phone inclinometer on the tip cap, or the arm-tip deflection with a ruler. Prediction at 300 g: nom GJ 5.8 N m2 gives 2.2 deg (9.5 mm); kd 4.5 gives 2.9 deg; hi 8.0 gives 1.6 deg. GJ = T L / theta with L 0.30 m, slope of the three points; unload and repeat after 10 min for tape creep.
4. Pass: measured GJ >= 2 N m2 (flutter 50 m/s at 2) and divergence needs only > 0.2 N m2 even at e/c 0.10. A value far under kd 4.5 points to a bad tape bond or wrinkling, not a flutter problem.
5. **Elevon test on the built wing (more important):** servo powered and holding, push the trailing edge with a spring scale 30 mm behind the hinge and read the deflection: K = F r^2 / x per elevon. Require K >= 1 N m/rad and total free play <= 1 deg (0.5 mm at the trailing edge, 0.03 m arm). Tap-test for f_h about 12 Hz and f_alpha about 44 Hz.

## Open

1. K, elevon mass and elevon CG are `EST`; K decides between "balance required" and "pass unbalanced". Measure before the elevons are glued.
2. Cruise 1P of 120-130 Hz (7,300-7,600 rpm, BOARD item 1) is above every flutter frequency here (14-47 Hz); no coupling expected.
3. A tap or ground-vibration test with the fin on one tip checks the 12 / 44 Hz modes this result rests on.
