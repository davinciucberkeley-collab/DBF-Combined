# T-101 reflex-section scout: airfoils to replace the S5010 on concept A

Date checked for every URL: 2026-11-24. Options only; nothing is picked here (the conductor decides).
Format note: the scout template (knowledge/TEMPLATE-approaches.md) does not exist in this repo (knowledge/ is absent), so this follows the brief's field list; the output path is the one the brief named.

## Verdict (one paragraph)
Of the sections checked, only the two Eppler reflexed sections E 230 and E 186 have a positive Cm about c/4 in XFOIL; the Hepperle MH 45/60/61/62/64 series and S5020 are by design near zero or negative (Hepperle: "moment coefficients close to zero"). At Re 2.8e5 XFOIL gives E 230 Cm0 about +0.028 (absolute), E 186 about +0.010. Both have LOWER Clmax than S5010 (E 230 about 0.84 against 1.25 at 2.8e5, XFOIL), which worsens the A-P6 stall claim. No section found gives both Cm0 about +0.037 and Clmax at or above S5010. Cm0 is strongly Re dependent (XFOIL, below) and no wind-tunnel Cm exists for any candidate.

## Method and caveats
- Polars: XFOIL 6.96 runs hosted by airfoiltools.com, Ncrit 9, Re 2e5 and 5e5 (only 2e5 and 5e5 exist between 1e5 and 1e6). Fetched as text from `http://airfoiltools.com/polar/text?polar=xf-<id>-il-<Re>` (ids: mh45, mh60, mh61, mh62, mh64, mh81, e182, e184, e186, e230, s5010, s5020). Values below are read from those tables by me: Cm at CL=0 (interpolated), alpha0L, Clmax, Cd min. All "XFOIL".
- "Re 2.8e5" columns are my linear-in-ln(Re) interpolation between the 2e5 and 5e5 XFOIL runs (weight 0.367 on the 5e5 value). This is an estimate, not a run.
- Geometry (thickness, location, t at 0.25/0.30/0.75 c, camber) computed by me from the downloaded Selig .dat files (linear interpolation of upper/lower surface). Files are in `docs/audits/2026-11-24-T101-reflex-coords/`.
- Wind tunnel: the UIUC low-speed tests measure lift and drag only, no pitching moment (UIUC Vol 1 text: "no pitching moment measurements were taken"; Cm there is computed by Eppler/ISES/XFOIL). So there is no measured Cm for any candidate. Measured CL/Cd exist only for MH 45 (Vol 1, Re 1e5 to 3e5; Selig says the model was too thick, so not reliable) and S5010 (Vol 2, Re 6e4 to 2e5 listed); not extracted into the table (columns did not parse reliably).
- Selig's Vol 2 table lists S5010 camber 2.21 % and Cm c/4 -0.007 (computed, not measured), agreeing with the XFOIL 2e5 value here (-0.007). Our plant uses S5010 Cm0 +0.008. XFOIL at 5e5 gives +0.005. So the plant's absolute +0.008 sits at the high-Re XFOIL end; the absolute-versus-delta question below matters.

## Candidate table (Cm in XFOIL, about c/4, positive = nose-up)
| Section | Cm0 Re 2e5 | Cm0 Re 5e5 | Cm0 Re 2.8e5 (interp. est.) | alpha0L deg (2e5 / 5e5) | Clmax 2e5 / 5e5 | Clmax 2.8e5 (est.) | Cd min 2e5 / 5e5 | Cd min 2.8e5 (est.) |
|---|---|---|---|---|---|---|---|---|
| S5010 (reference) | -0.007 | +0.005 | -0.003 | -1.25 / -0.72 | 1.218 / 1.306 | 1.25 | 0.00975 / 0.00627 | 0.0084 |
| E 230 | +0.021 | +0.041 | +0.028 | +0.31 / +1.19 | 0.817 / 0.887 | 0.84 | 0.00896 / 0.00574 | 0.0078 |
| E 186 | +0.002 | +0.023 | +0.010 | -1.03 / -0.10 | 1.003 / 1.029 | 1.01 | 0.01011 / 0.00665 | 0.0088 |
| E 184 | -0.007 | +0.009 | -0.001 | -0.93 / -0.32 | 0.885 / 0.894 | 0.89 | 0.00926 / 0.00596 | 0.0081 |
| MH 45 | -0.012 | +0.000 | -0.008 | -1.12 / -0.63 | 1.185 / 1.293 | 1.23 | 0.00933 / 0.00592 | 0.0089 |
| MH 60 | -0.014 | -0.002 | -0.010 | -1.20 / -0.70 | 1.155 / 1.246 | 1.19 | 0.00952 / 0.00594 | 0.0089 |
| MH 64 | -0.025 | -0.009 | -0.019 | -1.33 / -0.78 | 1.057 / 1.087 | 1.07 | 0.00845 / 0.00550 | 0.0075 |
| MH 81 | -0.004 | -0.003 | -0.003 | -1.68 / -1.71 | 1.567 / 1.624 | 1.59 | 0.01115 / 0.00774 | 0.0098 |
| S5020 | -0.006 | +0.000 | -0.004 | -1.25 / -1.09 | 1.220 / 1.280 | 1.24 | 0.00942 / 0.00629 | 0.0081 |
| Also run: MH 62 | -0.020 | -0.006 | -0.015 | -1.26 / -0.74 | 1.105 / 1.188 | 1.12 | 0.00898 / 0.00573 | 0.0077 |
| Also run: MH 61 | -0.010 | +0.007 | -0.004 | -0.98 / -0.32 | 1.013 / 1.024 | 1.02 | 0.01001 / 0.00606 | 0.0087 |
| Also run: E 182 | -0.023 | -0.004 | -0.016 | -1.49 / -0.75 | 0.993 / 0.986 | 0.99 | 0.00911 / 0.00598 | 0.0080 |

(Cm0 here = Cm at CL=0 from XFOIL; Cm at alpha=0 differs by up to 0.02 because CL is not 0 there. Rounded to 3 decimals.)

## Geometry (computed from the .dat files)
| Section | Max t/c, location | t at 0.25 c | t at 0.30 c | t at 0.40 c | t at 0.75 c | Max camber, location | Coordinates (UIUC Selig format) |
|---|---|---|---|---|---|---|---|
| S5010 | 9.83 % at 0.276 | 9.76 % | 9.79 % | 9.20 % | 3.53 % | 2.20 % at 0.28 | https://m-selig.ae.illinois.edu/ads/coord/s5010.dat |
| E 230 | 9.96 % at 0.293 | 9.87 % | 9.95 % | 9.55 % | 4.64 % | about 0 (0.02 %), reflexed | https://m-selig.ae.illinois.edu/ads/coord/e230.dat |
| E 186 | 10.27 % at 0.310 | 10.06 % | 10.25 % | 9.86 % | 4.28 % | 1.31 % at 0.27 | https://m-selig.ae.illinois.edu/ads/coord/e186.dat |
| E 184 | 8.32 % at 0.321 | 8.13 % | 8.29 % | 8.09 % | 3.40 % | 1.20 % at 0.37 | https://m-selig.ae.illinois.edu/ads/coord/e184.dat |
| MH 45 | 9.85 % at 0.276 | 9.82 % | 9.78 % | 9.14 % | 3.61 % | 1.71 % at 0.32 | https://m-selig.ae.illinois.edu/ads/coord/mh45.dat |
| MH 60 | 10.08 % at 0.277 | 10.04 % | 10.03 % | 9.44 % | 3.85 % | 1.82 % at 0.37 | https://m-selig.ae.illinois.edu/ads/coord/mh60.dat |
| MH 64 | 8.58 % at 0.270 | 8.57 % | 8.53 % | 7.97 % | 3.25 % | 1.49 % at 0.37 | https://m-selig.ae.illinois.edu/ads/coord/mh64.dat |
| MH 81 | 12.99 % at 0.225 | 12.95 % | 12.67 % | 11.43 % | 4.41 % | 3.52 % at 0.23 | https://m-selig.ae.illinois.edu/ads/coord/mh81.dat |
| S5020 | 8.40 % at 0.278 | 8.36 % | 8.36 % | 7.84 % | 2.95 % | 2.62 % at 0.28 | https://m-selig.ae.illinois.edu/ads/coord/s5020.dat |
| MH 62 | 9.29 % at 0.279 | 9.26 % | 9.24 % | 8.67 % | 3.54 % | 1.64 % at 0.37 | https://m-selig.ae.illinois.edu/ads/coord/mh62.dat |
| MH 61 | 10.23 % at 0.278 | 10.11 % | 10.23 % | 9.82 % | 4.12 % | 1.52 % at 0.37 | https://m-selig.ae.illinois.edu/ads/coord/mh61.dat |
| E 182 | 8.47 % at 0.328 | 8.27 % | 8.44 % | 8.21 % | 3.46 % | 1.72 % at 0.37 | https://m-selig.ae.illinois.edu/ads/coord/e182.dat |

The two best-Cm sections (E 230, E 186) have as much or more material at the spar (0.25 to 0.40 c) and at the 0.75 c hinge (4.6 / 4.3 % against S5010 3.5 %) than S5010, so no spar or hinge penalty. MH 81 is 13 % thick (mass/drag cost).

## Per-option cost to us (record, not a ranking)
- E 230: Cm0 +0.028 est. at 2.8e5 (XFOIL), strongest positive Cm found. Clmax about 0.84 against 1.25 for S5010 (2D XFOIL, 2.8e5), roughly 0.4 lower. If wing CLmax scales with the 2D ratio (0.75 x 0.84/1.25, my crude scaling, estimate) the wing would stall near CL 0.50, far below the 0.81 the A-P6 claim needs. Cd min about 8 % lower than S5010 (XFOIL). Mass and part count unchanged (same thickness, same spar and elevon layout).
- E 186: Cm0 about +0.010 at 2.8e5 (+0.023 at 5e5); Clmax about 1.01 (about 0.24 lower than S5010); 10.3 % thick.
- E 184: Cm0 about 0; Clmax about 0.89; 8.3 % thick. No trim benefit in XFOIL; listed as the thin Eppler sibling.
- MH 45/60/61/62/64, S5020: Cm0 at or below S5010 (negative to about 0). They are the intended low-Cm flying-wing sections, meant to be used with sweep and twist, which our unswept rectangular wing lacks. Clmax 1.07 to 1.23.
- MH 81: Clmax about 1.59 (higher than S5010, would help A-P6) but Cm0 about -0.003 (no trim benefit), 13 % thick, 3.5 % camber.
- Nothing found has both Cm0 near +0.037 and Clmax at or above S5010.

## Effect on cruise elevon trim (plant line from the brief: 7.29 deg at +0.008, 4.26 at +0.020, 1.74 at +0.030, about 0 at +0.037)
Two readings, both estimates, because the XFOIL S5010 value (-0.003 at 2.8e5) differs from the plant's +0.008. a_aero.py was not read.
- Absolute (use the section's own XFOIL Cm0 in the plant line): E 230 +0.028 gives about 2.2 deg (interpolated); E 186 +0.010 gives about 6.8 deg (near the 7.29 end of the line, rough); others at or above S5010's 7.29.
- Delta (add each section's XFOIL change from S5010 to the plant's +0.008): E 230 +0.031 gives about +0.039, so trim about 0 deg; E 186 +0.013 gives about +0.021, so about 4.0 deg; E 184 +0.002 gives about +0.010, so about 6.8 deg; MH 81, MH 45/60/64, S5020 change is negative or about zero, trim at or above 7.3 deg.
Which reading holds depends on the source of the plant's +0.008 (not checked here).

## Sources opened (all 2026-11-24)
- https://www.mh-aerotools.de/airfoils/foil_flyingwings.htm: Hepperle flying-wing airfoil page (MH 60/61/62/64 published; MH 44/45/46/49 "never intended for publication"; design aim of small Cm c/4; t/c values).
- https://www.mh-aerotools.de/airfoils/flywing1.htm: Hepperle "Flying Wings: Airfoil Design and Selection". An unswept plank needs a positive-Cm reflexed airfoil; the worked example requires Cm +0.025 and concludes "E 186 and E 230 could be used"; no table of values read.
- https://www.mh-aerotools.de/airfoils/index.htm and index_contents.htm: site index only (to find the pages above).
- http://airfoiltools.com/airfoil/details?airfoil=mh45-il: MH 45 details (max thickness 9.8 % at 26.9 %, max camber 1.7 % at 36.6 %; XFOIL polar list Re 5e4 to 5e5). The https form refused the connection; http used.
- http://airfoiltools.com/polar/text?polar=xf-<id>-il-200000 and -500000 for the 12 ids above: XFOIL 6.96 polar tables, Ncrit 9. Source of every Cm, alpha0L, Clmax and Cd min number. (E 325 to E 340 were also run but excluded: their .dat files have a different point order and camber 3.8 to 4.6 %, and the positive Cm is not credible without checking; not evaluated.)
- https://m-selig.ae.illinois.edu/ads/coord/<id>.dat for s5010, mh45, mh60, mh61, mh62, mh64, mh81, e182, e184, e186, e230, s5020: coordinate files saved in docs/audits/2026-11-24-T101-reflex-coords/.
- https://m-selig.web.engr.illinois.edu/uiuc_lsat/Low-Speed-Airfoil-Data-V1.pdf (text extracted): no pitching-moment measurement in the UIUC tunnel; MH 45 tested, model too thick.
- https://m-selig.web.engr.illinois.edu/uiuc_lsat/Low-Speed-Airfoil-Data-V2.pdf: S5010 description (flying-wing section, near-zero moment) and summary table (thickness 9.83 %, camber 2.21 %, Cm c/4 -0.007, computed).
- Fetched but not used: Low-Speed-Airfoil-Data-V3.pdf and V5.pdf (searched for the candidates, no relevant data); V4 returned 404; https://m-selig.ae.illinois.edu/uiuc_lsat/Low-Speed-Airfoil-Data.html returned 404; a web search for measured E 230 / E 186 Cm found none.
