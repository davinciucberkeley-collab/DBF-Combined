# T-086 cost-trim study (AM-020), concept A (O4b) BOM, 2026-11-22

Analysis category: illustrative (cost accounting; no geometry, no physics). Prices read 2026-11-22 unless marked.
Backups: `T086_data/BOM-A.csv`, `T086_data/bom_a.py` (bom_a.py not changed). Proof-chain output after: `T086_data/run_all_after.txt`.

## Result
| | Before | After |
|---|---|---|
| Goods | 1,432.50 | 1,418.51 |
| Spend | 1,652.17 | 1,636.75 |
| Crash reserve (definition unchanged) | 346.94 | 346.94 |
| Total | 1,999.12 | 1,983.69 |
| Margin | +0.88 | +16.31 |

The goal of >= $50 margin is NOT reached with levers 1-3: +$15.43 applied. The lever-4 proposals below add roughly $70-90 (EST) if the team accepts them.
Several fetches were blocked (Amazon "access restricted" bot page, Zoro 403, eBay 403, RDQ 429 / no rates, RMRC policy pages 404). They were not bypassed, so those lines stay unverified.

## Trade table
| Line | Current vendor / price / ship | Alternative | URL | Date | Saving incl. tax (+ship) | Same spec | Applied | Risk |
|---|---|---|---|---|---|---|---|---|
| M01 | RMRC 3 x $13.99 (1 spare) | qty 2, no BOM spare (lever 2, AM-019 logic; no decision requires a servo spare; reserve() still prices one servo) | https://www.readymaderc.com/products/details/85975-emax-es3054-hv-high-voltage-17g-metal-gear-digital-servo | 2026-11-15 page, unchanged | $15.42 | yes (same part) | YES | A servo failure before first flight grounds the aircraft until a reorder (schedule, not money). Revert: qty 3, spares 1 |
| T1 | Alcobra 2.00x2.50x12 in 6061-T6511 $65.56 | Zoro Select 2 x 2-1/2 in, 1 ft flat, snippet price $41.99, snippet says T6511 | https://www.zoro.com/zoro-select-flat-al-6061-2-x-2-12-in-1-ft-61f2x25-12/i/G0529051 (403, page NOT read) | 2026-11-22 snippet only | up to $25.98 before Zoro ship (—) | unverified (temper, tolerance, extruded or not) | no | Do not buy from a snippet; page must be read in an ordinary browser |
| T11 | Alcobra 1.00x4.00x12 in 6061-T6511 $47.52 (EST length mapping) | Zoro Select 1 x 4 in, 1 ft flat 61F1X4-12, snippet $28.99, temper not stated | https://www.zoro.com/zoro-select-flat-stock-al-6061-1-x-4-in-1-ft-61f1x4-12/i/G0792933 (not read) | 2026-11-22 snippet | up to $20.50 before ship | unverified (plain 6061 vs T6511) | no | same |
| T1+T11 ship | SHIP["Alcobra"] $10.71 EST | would drop if both bars move; Zoro ship — | - | - | $10.71 | - | no | see Alcobra finding |
| T1 alt | Speedy Metals 2x2.5 6061-T6511 | shortest length 18 in, $80.80 (snippet) | https://speedymetals.com/p-2363-2-x-2-12-6061-t6511-aluminum-extruded.aspx | 2026-11-22 | negative | no (18 in) | no | worse than Alcobra |
| R15 | Carbonwebshop 25x23x1000 EUR 45.58 = $50.09 + $25.00 ship EST | US-shipped 25x23 x 1 m roll-wrapped: eBay listings exist (e.g. https://ebay.com/itm/324236157445, 403, seller and price not read); Robozar and aryabot (India), UAV Garage (AU) | - | 2026-11-22 | — | cannot confirm | no | Search snippets say the Carbonwebshop page shows out of stock; the page read shows only an Add to cart button (stock not stated). The $25 ship is an EST, not a quote (EU to US, duties not stated). Largest cost and schedule uncertainty in the BOM |
| T3 | Wicks 3 yd 1080 $6.46 (48 in stock, read) + Wicks ship $10.71 EST | Aircraft Spruce 1080-50 (1.45 oz, 50 in; US price not read; free ship only over $350) | https://www.aircraftspruce.com/catalog/pnpages/1080-50.php | 2026-11-22 | — | likely yes | no | No free-ship gain. US Composites has no 1080 (lightest 3 oz): https://www.uscomposites.com/prices.html |
| T3 alt | Fiberglass Supply 1080 1.4 oz x 38 in | $7.26/yd snippet | https://fiberglasssupply.com/style-1080-1-4-oz-x-38in-plain-weave-e-glass/ | 2026-11-22 | none | NO (38 in, 1.4 oz) | no | lever 4 |
| W01 | RDQ 2 x $54.99 + RDQ ship $10.71 EST | RMRC has no 4S 2800 mAh pack on the first search page (450...3300 mAh; Gens Ace 3300 mAh 45C $62.99, mass not listed) | https://www.readymaderc.com/products/details/86401-gens-ace-3300mah-4s-45c-14-8v-g-tech-lipo-battery-pack-with-ec3 | 2026-11-22 | would remove the $10.71 line | NO | no | different pack = lever 4 (mass, C rate, size). RDQ policy page lists no rates or threshold, so the EST stays |
| RMRC lines | SHIP RMRC = 0 | RMRC free-shipping rule is "5 % of order" per review/QP-1/COST.md; policy URLs 404 on 2026-11-22, not re-read | - | - | - | - | no | keep RMRC as the consolidation hub |
| T4/T12 | US Composites 635 kit $20.20 + flock $4.90, one ship line | already one shipment | https://www.uscomposites.com/prices.html | 2026-11-22 | 0 | - | no | kit price reconfirmed ($20.20 for 16+8 oz) |
| T7/T8 | 2 pad foams $23.79 + $24.69 | buy one | - | - | $26 if one dropped | - | no | TP-3 compares foam candidates (TEST-PLAN-O4B.md): a decision requires them. Test-plan call |
| W07 | 20 AWG 8 x 1 m $7.92 | 6 x 1 m $5.94 | https://www.readymaderc.com/products/details/premium-silicone-wire-20ga-red-1m | 2026-11-15 | $2.18 | yes | no | 5.40 m needed from 12 strands; 6 m leaves 0.6 m. Too little gain for a short-strand risk |
| Jacobs $0 | T1/T11 bar, PETG, foam, wood | docs/reference/jacobs-equipment.md lists machines only; "Material costs ... not on the page"; X7 filament believed free (EST, Dillon 2026-11-20) | - | - | - | - | no | no line is supported as $0 by the document; nothing applied |

### Finding that works against the margin (not applied, flagged)
Alcobra shipping policy (https://alcobrametals.com/shipping-policy/, read 2026-11-22): live UPS rate by weight and size, one charge per order, plus a flat $10 packaging fee; free pick-up only within 150 miles of Spokane. The two bars weigh about 5.9 lb (2.0x2.5x12 in) and 4.7 lb (1x4x12 in) (EST from 6061 density 0.0975 lb/in3), so the real shipping is likely above the $10.71 in SHIP["Alcobra"] (UPS quote: —). Get a cart quote before the margin is relied on. This is a second reason to move the bars to a vendor whose page can be read.

## Lever-4 proposals (not applied; EST incl. 10.25 % tax, before shipping effects)
| # | Change | Saving EST | Re-checks required |
|---|---|---|---|
| L4-1 | Hub bars T1/T11 from Zoro (or any vendor with a readable page showing 6061-T6511) | $20-45 plus the Alcobra ship line | Page read for temper and tolerance; CGE-001 / CGE-006 blank sizes vs cross-section tolerance; hub FEA only if the temper is not T6511 |
| L4-2 | Rib tube R15 25x23 replaced by a stock US tube (e.g. 24 or 26 mm roll-wrapped at RMRC/Amazon) or built up from R09 14x12 | about $80 (50.09 x 1.1025 + $25 ship) plus a reserve drop of about $55 | FIN-002 geometry, fin FEA (structures_a), spar / fin mode (T-084, T-085), collision and assembly gates, mass |
| L4-3 | R09 14x12 tube bought only for 4 hub doublers (84 mm, $15.36): cut doublers from an offcut of another tube or print them | $16.9 plus reserve drop $16.9 | doubler fit and FEA, parts list |
| L4-4 | One pad foam (T7 or T8) instead of two | $26 | TP-3 / TP-9 plan (test-plan owner) |
| L4-5 | W01 pack from RMRC if a 4S 2.6-3.0 Ah pack of equal mass appears | $10.71 ship line | mass, cruise time, tray fit, CAD pack envelope |
| L4-6 | 1080 cloth shipped with another group | $10.71 | glass-skin mass, wet-out coupon |
| L4-7 | Materials from Jacobs at $0 once Jacobs confirms (PETG/PLA, foam sheet, aluminium offcut) | up to about $100 (R03 12.99, R01 45, bars 113.08) | Jacobs must confirm; PLA vs PETG needs the printed-part checks |

Reaching +$50 needs at least L4-2, or L4-1 plus L4-4.

## Verification
- `python -I bom_a.py`: total $1,983.69, margin +$16.31 (was $1,999.12, +$0.88). Reserve $346.94 unchanged.
- `python -I proofs/run_all.py` (rc 1 as before, known fails): the same 8 failing claims (CL-A-MASS-PRED, CL-A-MASS-GATE-ROOM, CL-A-CUTS-REQUIRED, CL-A-HORN-RIB-FOAM-HOLD, CL-A-HORN-RIB-FOAM-STALL, CL-A-ELEVON-TORSION-FOAM, CL-A-HORN-BEARING-STALL, CL-A-LINKAGE-FREEPLAY); no cost failure. Regenerated outputs changed only in cost values and M01 qty (`params-A.json`, `proofs/claims.a3_program.json`, `proofs/out/*`).
- `parts_links_a.py` does not exist; no part-number text changed. No geometry changed: no CAD or 3-D gates run. Not committed.

## Proposed CHANGE-LOG D-234 text
**D-234 T-086 cost-trim study (2026-11-22).** Levers 1-3 applied in order. One change survives: M01 servo qty 3 -> 2, spare dropped (AM-019 logic: the crash reserve already carries one servo; no decision requires a servo spare). BOM $1,999.12 -> $1,983.69, margin +$0.88 -> +$16.31; reserve definition (AM-018) and SHIP table unchanged; proof chain keeps the same 8 failing claims, no cost failure. No substitute with proven same spec was found: Zoro bar prices (T1 $41.99, T11 $28.99, search snippets) could not be read (403); RDQ, Alcobra, Wicks and Carbonwebshop give no firm rates; Jacobs has no documented material supply. Open risks: Alcobra ships by UPS weight plus a $10 fee (EST $10.71 probably low); Carbonwebshop R15 may be out of stock and its $25 shipping is an EST. Lever-4 proposals (hub bar vendor, rib tube, R09 doublers, one pad foam, pack source, cloth) are in `redesign/qp/A/mechanism/out/T086_report.md`; reaching +$50 needs at least L4-2, or L4-1 plus L4-4.
