# Change requests from I1 (procurement / BOM)

Numbers from `team/I1/build_bom.py` (claims `CL-I1-…`). Revision I1-R2, 2026-11-09. R1 rows still open are kept; closed ones are listed at the end.

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-I1-13 | E2, F1 (cc A3, A1) | **Pack SKU.** The Ovonic 4S 6500 listing (fetched 2026-11-09) has 12 AWG leads and 680 g per pack, $82.97. Name a SKU with >= 10 AWG leads and <= 658 g, or accept re-leading and the mass. I hold the pack cart until you answer | `CL-F1-PACKLEAD12-RISE` 28.4 K vs 20 K; `CL-A3-GATE-MARGIN-680` -4 g (gate exceeded before overrun) |
| CR-I1-14 | A1 | `params.json#cost`: `spend_baseline_usd` 1 569.03 → **1 579.79**, `spend_pessimistic_usd` 1 680.35 → **1 687.01**, `reserve_pessimistic_usd` 319.65 → **312.99** (sources `CL-I1-SPEND-BASE`, `-PESS`, `CL-I1-RESERVE-PESS`). Also record `reserve_pessimistic_allin_usd` **128.00** (`CL-I1-RESERVE-PESS-ALLIN`) and say whether holding X07 (box and field kit, $118.85) and X08 (airspeed sensor, $66.14) behind a gate is accepted | the expected ≈ $326 is not reachable with the designers' items priced as asked; margin to the $309 crash is only +$3.99; every BOM line bought leaves $128.00 |
| CR-I1-15 | A1 | Decide the next lever if a line above $3.99 appears: borrowing the soldering, meter and hot-wire gear from Jacobs Hall (+$94.82, +$62.54), then SpeedyBee FC (+$21.25). Un-gate X08 (airspeed) if Jacobs lends the electronics bench | `SUMMARY.md` lever table |
| CR-I1-16 | F3, F4 | X08: confirm the first fixed-wing tune can run on the synthetic airspeed estimate; the MS4525DO (`A04`, $59.99 + tax) is bought only when the gate passes | gate X08 |
| CR-I1-17 | D3 (cc C2) | `FIN-006`: stock 20x18 tube is sold by the metre ($20, `D03`), not a $1 share. Can one 1 m length also give C2's six 36 mm spar plugs? Tell me, else C2 needs its own line | `D03` |
| CR-I1-18 | D7, C5 | Reconcile the ground mat: D7 `TRN-104` is a $10 EVA tile, C5 CR-C5-06 asks for a rubber mat on plywood plus 16 spare cartridges per type in the field kit. One mat is carried (`T05`) | `CL-C5-V-PARK-GUST` assumes rubber |
| CR-I1-19 | F2, D6 | Write `parts.csv` with vendor, part number and price for the harness (bullets, servo leads, JST-GH, ties) and the mechanisms (horns, pushrods, clevises, hinge tape). `H01` + `H02` ($36) are my residual estimate | CR-I1-01 stays open for these two |
| CR-I1-20 | D3 | `FIN-003`, `FIN-007` are printed in ASA: confirm 1 kg is the smallest practical spool and that 58 g of ASA is the whole need (`W08`, $24.99) | not in CR-A1-39 |
| CR-I1-21 | H1 | Obtain Jacobs Hall's written yes for the borrow list before 20 Nov; if a line is refused tell me, it becomes a BOM line (prices in `ORDER-PLAN.md`) | `T-I1-BORROW` |
| CR-I1-22 | A2 | Add `CL-I1-GROUNDTEST-BOUGHT` (<= $20) and `CL-I1-RESERVE-PESS-ALLIN` to the verification matrix under `R-BUDGET` and `R-RESERVE`; `T-I1-CONNECTOR-LEADS` verifies the pack SKU | CR-I1-12 follow-up |

## Open from R1 (unchanged)

CR-I1-01 (F2, D1, D6 still owe `parts.csv`; F1, C6, D3, D5, D7 delivered), CR-I1-04 (LANRC listing unconfirmed), CR-I1-07 (D6 servo), CR-I1-08 (C4/H1 bend test by 10 Dec), CR-I1-11 (I2 dates).

## Closed in R2

| # | Closed by |
|---|---|
| CR-I1-02 | accepted D-39; superseded by CR-I1-14 |
| CR-I1-03 | accepted D-39; lever order applied (adapter set gated, airspeed gated last) |
| CR-I1-05 | adapter set gated X05 |
| CR-I1-06 | listing read: XT60 with a TRA adapter, 12 AWG, 680 g → CR-I1-13 |
| CR-I1-09 | F3 CR-F3-06: CoreWing V2 now |
| CR-I1-10 | F1 CR-F1-14: AS150U; `F01` buys the pairs, `H03` cut to $5 |
| CR-I1-12 | A2 forwarded (D-39); extended by CR-I1-22 |
