# T-087 rib tube (R15) and hub bars (T1, T11): supply and cost, concept A (O4b), 2026-11-22

Acceptance test (from the brief): rebuild the BOM margin (was +$16.31 of the hard $2,000 incl. the crash reserve) and remove two supply risks without relaxing any limit; `python -I bom_a.py`; `python -I proofs/run_all.py` with the same 8 failing claims and no cost failure; 3-D gates only if geometry changed.
Analysis categories: cost accounting = illustrative; rib screening = hand calculation + FEA-lite (3-D Euler-Bernoulli beam frame, fe_a.py) + rigid-body dynamics (landing_a) + geometry arithmetic (tip-over); no CFD, no flight dynamics.
Backups: `T087_data/` (BOM-A_pre_t087.csv, bom_a_pre_t087.py, wing_pre_t087.py, structures_a_pre_t087.py, cad_mass_pre_t087.json, structures_run_pre_t087.md, params-A_pre_t087.json, claims.a3_program_pre_t087.json, proofs_out_pre_t087/).

## Result
| | Before (T-086) | After (T-087) |
|---|---|---|
| Goods | 1,418.51 | 1,382.41 |
| Shipping (EST) | 67.84 | 63.12 |
| Spend | 1,636.75 | 1,592.23 |
| Crash reserve (definition unchanged) | 346.94 | 346.94 |
| Total | 1,983.69 | 1,939.17 |
| Margin | +16.31 | +60.83 |

Part 1 (R15): no replacement passes; R15 kept, nothing changed. Part 2 (T1, T11): both bars move from Alcobra to Zoro, applied. Margin gain +$44.52 comes only from Part 2.

## Part 1: R15 rib tube 25x23 x 1 m (FIN-002, 2 x 215.5 mm)
Current: Carbonwebshop (EU) 25x23x1000 EUR 45.58 = $50.09 + $25 ship EST, stock not stated.

| Candidate | URL | Date | OD x ID x length | Construction | Stock | Landed price | Checks | Verdict |
|---|---|---|---|---|---|---|---|---|
| RMRC (readymaderc.com) | search / product pages (1 m carbon tubes) | 2026-11-22 | largest plain tube found 16x14; STRIX roll-wrapped nesting pair 16/14 + 14/12 | roll-wrapped | in stock (STRIX) | $37.42 (STRIX pair) | no 24-26 mm OD exists at RMRC | no candidate; shipment would have been free |
| DragonPlate 0.875" ID x 24" (SKU FDPT.875*1.0*24) | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-0875-id-x-24-gloss-finish | 2026-11-22 (page read; cart add did not register) | 25.4 x 22.225 x 609.6 mm, wall 1.59 mm (CAD rib now 25.0 x 23.0, wall 1.0) | roll-wrapped, twill outer ply, UD 0 inner | not stated (processing 2-3 days per dragonplate.com/faq) | $59.65 x 1.1025 = $65.76 + ship: no quote, EST $10.71 = $76.47 (now $80.22); reserve tube term +$10.54 | see below | FAIL (D-185 worse), margin -$6.79 EST, mass +29 g. Rejected |
| DragonPlate 0.875" ID thin wall x 96" | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-0875-id-x-96-thin-wall-gloss-finish | 2026-11-22 | OD 0.94 in (23.9 mm), ID 22.2, 96 in, wall 0.03 in | roll-wrapped | not stated, ships in 7-10 days | $128.02 | rib torsion section modulus 3,124 vs 4,431 mm3 (25x23): 0.70x, so the D-226 node-exit torsion RF 1.20 falls to about 0.84 (hand scaling, EST) | FAIL on arithmetic, price. Rejected |
| DragonPlate 1" ID x 24" | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-1-id-x-24-gloss-finish | 2026-11-22 | OD 1.125 in (28.6), ID 25.4, 24 in | roll-wrapped | not stated | $62.53 | OD 28.6 needs wider fin groove, fairing, root fitting; more mass than the 25.4 case | not run; larger and heavier than the case that already fails |
| Rock West 45355 | https://www.rockwestcomposites.com/45355.html | 2026-11-22 | 25.58 x 22.2 x 1829 mm (1.007 / 0.875 / 72 in) | roll-wrapped fabric | 39 available | $149.99 | wall 1.68 mm, heavier than DragonPlate | cost rejects ($149.99 for 0.43 m used) |
| eBay 25x23 / 24x22 roll-wrapped | ebay.com/itm/154369605514, /134143296862 | 2026-11-22 | - | - | listings ended / 404 | - | - | page not readable or ended; not usable |
| Amazon, HobbyKing, Walmart | not readable (bot pages) | - | - | - | - | - | - | not judged |

DragonPlate 25.4 x 22.225 trial (wing.py RIB_OD / RIB_ID changed temporarily, `T087_data/wing_trial_dragonplate.py`; structures_a.py M_PRED 1.8796 -> 1.9120 kg, EST from the CAD mass delta; all of it restored from backup afterwards; outputs `structures_run_trial_dragonplate.md`, `modes_trial.txt`, `tipover_t087_trial.txt`, `cad_mass_trial.txt`):
| Check | Baseline (25x23) | Trial (25.4 x 22.225) | Limit | Result |
|---|---|---|---|---|
| CAD basic mass (cad_mass.py) | 1.63298 kg | 1.66206 kg (+29.1 g) | gate 1.50 (already failing, not relaxed) | worse, no gate change |
| Tallied predicted mass | 1.8796 kg | 1.9120 kg (EST scaling) | - | +32 g |
| CG x | 21.95 mm | 24.66 mm | - | moves aft |
| A-P9 tip-over, drawn pads (t084_tipover.py) | 31.00 deg min | 31.24 deg min | >= 30 (target 30.5) | PASS |
| Rib-root RF at x2.23 (structures_a s5 rows, KF 1.725, DAF 2.23, tau 30 MPa EST) | min 1.14 (zeta 0.05, mu 0.4: 1.14; zeta 0.02 1.14) | min 1.66 | >= 1.0 | PASS, better |
| Other landing rows (carried rows s6, not recomputed with the new rib) | PASS zeta <= 0.05, FAIL 0.10 | pad zeta 0.10 still FAIL (A-P5 12.7 g) | - | unchanged; plug and bond rows of FIN-003 / FIN-005 not re-derived for ID 22.225 |
| D-185 coupling, spar-only model, nom (t084_modes_final.py rerun of the baseline reproduces modes_final.txt) | 215.3 Hz, cy 0.52, FAIL | 217.0 Hz, cy 0.54, FAIL | band 94-321 Hz, strong >= 0.5 | slightly worse (cy 0.52 -> 0.54) |
| D-185, D-226 cell nominal, hi corner | 96.2 Hz (0.81 / 0.93) FAIL | 100.2 Hz (0.64 / 0.69) FAIL | same | still FAIL |
| D-185, D-226 cell lower bound, hi corner | none in band, PASS | 96.6 Hz (0.61 / 0.58) in band, FAIL | same | **new FAIL: D-185 gets worse** |
| Cost (R15 plus reserve tube term) | $80.22 + reserve term $55.22 | $76.47 (ship EST) + reserve term $65.76 | margin | -$6.79 EST |

Verdict: R15 stays. The DragonPlate tube is US-sourced and strengthens the rib (rib-root RF 1.14 -> 1.66), but its 29 g of extra mass moves the lower-bound hi corner into the excluded band (D-185 worse, rule stated in the brief), and it costs about $7 more margin with the shipping EST. No CAD, build steps, BOM line or reserve list changed for R15. The supply risk of R15 (Carbonwebshop out-of-stock / $25 ship EST / EU duties) remains and is the largest remaining BOM uncertainty. Option for the team (not applied, would need a decision): accept the D-185 worsening and a rebuilt hub/FIN-003 plug check for a US source, or ask DragonPlate for a custom 25.0 x 23.0 mm roll-wrapped tube (they offer custom sizing, dragonplate.com FAQ; no price).

## Part 2: hub bars T1 and T11
Alcobra ship policy (https://alcobrametals.com/shipping-policy/): UPS live weight rate + $10 fee, one charge per order. Alcobra cart quote: not obtained (add-to-cart needs a cutting-method choice that carries a $25 cutting fee line; no account created, nothing bought), so its shipping stays "—"; bars weigh about 10.6 lb total (EST), so the $10.71 EST was probably low.

| Candidate | URL | Date | Size / temper / length | Stock | Goods | Ship | Landed (before tax) | Verdict |
|---|---|---|---|---|---|---|---|---|
| T1 Alcobra | https://alcobrametals.com/product/2-x-2-1-2-6061t6511/ | 2026-11-22 | 2.00 x 2.50 in 6061-T6511 extruded, 12 in, same tolerance table (2 to under 4 in: +-0.024) | in stock (T-023 note) | $65.56 | shared Alcobra ship, — (EST $10.71) | $65.56 + | replaced |
| T1 Zoro Select 61F2X2.5-12 | https://www.zoro.com/zoro-select-flat-bar-stock-aluminum-25-in-over-w-61f2x25-12/i/G0529051/ | 2026-11-22, page read in the built-in browser | 2 x 2.5 in 6061 T6511 extruded, 12 in +-1 in, width and thickness +-0.024 in, ASTM B221 / AMS-QQ-A-200, yield 40,000 psi typical, no certificate | In Stock, delivery Tue 24 Nov (a Bay Area ZIP) | $43.29 | see below | $43.29 + | ADOPTED |
| T11 Alcobra | https://alcobrametals.com/product/1-x-4-6061t6511/ | 2026-11-21 | 1.00 x 4.00 in 6061-T6511, 12 in price EST ($47.52 = 96 in / 8) | not stated | $47.52 | EST | $47.52 + | replaced |
| T11 Zoro Select 61F1X4-12 | https://www.zoro.com/zoro-select-flat-bar-stock-aluminum-4-in-over-w-61f1x4-12/i/G0792933/ | 2026-11-22, read in the browser | 1 x 4 in 6061 T6511 extruded, 12 in +-1 in, width +-0.034 in, thickness +-0.012 in, same standards | In Stock, delivery on or before 27 Nov | $33.69 | see below | $33.69 + | ADOPTED |
| T1+T11 Zoro order | https://www.zoro.com/cart (guest cart, a Bay Area ZIP) | 2026-11-22 | both bars | - | $76.98 | **$5.99** cart quote as guest; free over $50 after sign-in (not done) | $82.97 before tax | SHIP["Zoro"] = 5.99 |
| T1 Speedy Metals | https://speedymetals.com/p-2363-2-x-2-12-6061-t6511-aluminum-extruded.aspx | 2026-11-22 snippet | shortest length 18 in, $80.80 | - | $80.80 | - | worse | rejected |
| OnlineMetals | onlinemetals.com bar pages | 2026-11-22 | 403 | - | - | - | - | not readable; McMaster / Metals Depot / MidWest not searched further after Zoro read |

Goods change: 65.56 + 47.52 -> 43.29 + 33.69 = -$36.10 x 1.1025 = -$39.80; ship: Alcobra $10.71 line removed, Zoro $5.99 added (-$4.72). Net -$44.52 (= margin +$44.52).

Fit of the CAD blanks to the stock (worst-case tolerance from the Zoro pages):
- CGE-001 hub 59.5 x 107.8 x 49.3 mm in 50.8 x 63.5 mm section: thickness 50.8 - 0.61 = 50.19 (0.89 mm over), width 62.9 (3.4 mm over), length 12 in -1 in = 279 mm (171 mm over). Fits.
- CGE-006 node bbox 100.0 x 119.6 x 20.1 mm (drawings/out/DRAWINGS-A.md) in 25.4 x 101.6 mm: width 101.6 - 0.86 = 100.74 mm (0.74 mm over the part, tight; the earlier BOM text "125 x 102" blank was 0.4 mm wider than the nominal bar and is corrected in the BOM line), thickness 25.1 vs 20.1. Fits, thin margin; machine from the bar faces as supplied.
- FIN-003 blanks (50 x 40 x 25.4 mm, two): came from a 51 mm offcut after two 125 mm blanks (EST). With the +-1 in length tolerance an 11 in bar leaves 29 mm, so the FIN-003 blanks would then come from the second CGE-006 blank's offcut (the spare). Noted in the BOM line; the build step text was not changed.
Temper: Zoro states T6511 (typical yield 40,000 psi, tensile 45,000 psi), same temper and the same extrusion tolerance table as Alcobra. The hub / root-fitting FEA allowable is 6061-T6 yield 240 MPa minimum (en.wikipedia.org/wiki/6061_aluminium_alloy, read 2026-11-20, `T083b_data/t083b_rootblock.py` line 14, secondary source); T6511 is the T6 temper stretched and stress-relieved, so the allowable is unchanged and no FEA rerun is needed. Zoro gives no certificate: test coupons are not part of this decision.
Not done: no account created, nothing bought. The Zoro guest cart still holds the two bars in the browser pane (not purchased). Free shipping needs a sign-in the team must make itself.

## Gate table
| Gate | Command | Result |
|---|---|---|
| BOM | `python -I bom_a.py` (from redesign/qp/A) | total $1,939.17, margin +$60.83 (`T087_data/bom_a_after.txt`) |
| Proof chain | `python -I proofs/run_all.py` | rc 1 as before; the failing-claim list is identical to T-086 (CL-A-MASS-PRED, CL-A-MASS-GATE-ROOM, CL-A-CUTS-REQUIRED, CL-A-HORN-RIB-FOAM-HOLD, CL-A-HORN-RIB-FOAM-STALL, CL-A-ELEVON-TORSION-FOAM, CL-A-HORN-BEARING-STALL, CL-A-LINKAGE-FREEPLAY; 11 ERROR lines, same as before); no cost failure (CL-A-COST-TOTAL 1,939; `T087_data/run_all_after.txt`). Regenerated: params-A.json, proofs/claims.a3_program.json, proofs/out/CHAIN.md, graph.js, graph.json (backups in T087_data) |
| 3-D gates (collide pose 21, 18 linkage poses, a_assembly, wire_inventory, cad_mass, build_a, drawings, build guide) | not run | no geometry changed: the rib trial was restored from backup, `git status` shows only BOM-A.csv, bom_a.py, params-A.json and the regenerated proof files |
| `tools/ledger_audit.py` | not run from this folder (path in the repo root `tools/`) | not checked here |

## Files changed (not committed)
`redesign/qp/A/BOM-A.csv` (T1, T11), `redesign/qp/A/bom_a.py` (SHIP["Zoro"] = 5.99), regenerated `params-A.json`, `proofs/claims.a3_program.json`, `proofs/out/*`.

## Proposed CHANGE-LOG D-235 text
**D-235 T-087 hub-bar vendor and rib-tube sourcing (2026-11-22).** Hub bars T1 (2.00 x 2.50 in) and T11 (1.00 x 4.00 in) move from Alcobra to Zoro Select 61F2X2.5-12 ($43.29) and 61F1X4-12 ($33.69), both 6061 T6511 extruded, in stock, pages read 2026-11-22; Zoro guest cart shipping $5.99 for both (free over $50 after sign-in), SHIP["Zoro"] = 5.99, Alcobra line removed. Same temper and extrusion tolerance table as Alcobra, so the 6061-T6 yield 240 MPa allowable (T-083b, secondary source) stands; CGE-001 fits the stock with 0.89 mm over the thickness at minimum tolerance, CGE-006 with 0.74 mm in the 4 in width (tight), and FIN-003 blanks need the spare blank's offcut if the bar arrives 1 in short. BOM $1,983.69 -> $1,939.17, margin +$16.31 -> +$60.83; proof chain keeps the same 8 failing claims, no cost failure. Rib tube R15 stays at Carbonwebshop: the only US 25-ish mm candidate found, DragonPlate 25.4 x 22.225 x 609.6 mm roll-wrapped ($59.65, shipping unquoted), strengthens the rib (rib-root RF 1.14 -> 1.66, A-P9 31.00 -> 31.24 deg) but adds 29 g and moves the D-226 lower-bound hi corner into the 94-321 Hz band (96.6 Hz, coupling 0.61 / 0.58), so D-185 gets worse, and it costs about $7 more margin (EST). RMRC has no tube above 16x14. Open: R15 supply (EU, $25 ship EST, stock not stated) is now the largest BOM uncertainty; Alcobra shipping was never quoted (no account, no cart quote); Zoro prices and stock are for a Bay Area ZIP on 2026-11-22 and must be reconfirmed at order time.
