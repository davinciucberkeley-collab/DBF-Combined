# Change requests from I1 (procurement / BOM)

Numbers from `team/I1/build_bom.py` (claims `CL-I1-…`). Revision I1-R1, 2026-11-09.

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-I1-01 | F1, F2, D1, D2, D3, D5, D6, D7 | Write `subsystems/<key>/parts.csv` with vendor, part number and price for every bought part; F1/F2 itemise the $124.01 wiring/hardware kit (connectors, wire by gauge, UBEC, epoxy, screws) | only `propulsion` has a `parts.csv`; the BOM carries the kit as one `EST` lump (`H01`, `H02`) |
| CR-I1-02 | A1 | `params.json#cost`: `spend_baseline_usd` 1 576.78 → **1 569.03**, `spend_pessimistic_usd` 1 678.58 → **1 680.35**, `reserve_pessimistic_usd` 321.42 → **319.65**, source `CL-I1-SPEND-PESS` / `CL-I1-RESERVE-PESS`; then re-run `frame_claims.py` (or retire `CL-A1-RESERVE` in favour of `CL-I1-RESERVE-PESS`) | margin to the $309 crash is +$10.65 and depends on deferring the second ESC pack (X01) |
| CR-I1-03 | A1 | Decide the lever if a new pessimistic line above $10.65 appears: defer the airspeed sensor (+$66.14, DECISION 5.1) or fall back to the SpeedyBee FC (+$21.25) | the gate has almost no slack |
| CR-I1-04 | E1 | `PRP-002`: buy 1 LANRC 4-pack now (4 fitted, no spare); the second pack is gated X01. LANRC ASIN B0D2HS4Y4J is unconfirmed (503, no US 4-pack page): tell me if you can read it. Fallback Tekko32 F4 45A AM32 +$60 for four, backorder to Dec 2026 | keeps the reserve >= $309 (CR-E1-12 asked 4 + 4) |
| CR-I1-05 | E1 | `PRP-004` Small Parts CNC set is out of stock; I buy it in December if listed, else the adapters in the motor boxes. Tell H1 the stand uses the box adapters | CR-E1-20 |
| CR-I1-06 | E2, A3 | Ovonic listing title says "XT60 to TRA plug": confirm the pack connector is XT60 when ordering; I weigh both packs and give masses to E2 (`pack_log.csv`) and A3 | `SRC-I1-OVONIC` |
| CR-I1-07 | D6 | Pick the elevon servo (>= 3.04 kgf·cm, 6–8.4 V, mass, price). `M01` carries 2 × EMAX ES3005HV $19.99 as a placeholder; the 12 g ES08MA II (~2 kgf·cm) is too weak | `CL-I1-SPEND-PESS` carries $39.98 |
| CR-I1-08 | C4, H1 | Bend-test the Aloft tube (`W03`) by **10 Dec** and tell me pass/fail: pass → December tubes from Aloft ($24, US stock); fail or no result → overseas $28.32, ~14 days | the tube SKU is the critical path for the 19 Jan build start |
| CR-I1-09 | F3 | Confirm a stable ArduPilot Plane tailsitter build for the CoreWing F405 Wing V2 before 20 Nov, else name the board (SpeedyBee F405 Wing $47.99 saves $21.25). Airspeed `A04` is ordered 15 Dec | I do not order the FC before this |
| CR-I1-10 | F1 | Say whether the main disconnect is XT60 (re-termination `H03`, $16.54, drops out) or AS150U | `params.json#electrical.main_disconnect` |
| CR-I1-11 | I2 | Dates: early order 20 Nov (arrival ~1 Dec), tube decision 10 Dec, December order 15 Dec (arrival by ~29 Dec), build start 19 Jan, store pick-up in January | `ORDER-PLAN.md` |
| CR-I1-12 | A2 | Point `R-BUDGET` and `R-RESERVE` at `CL-I1-SPEND-PESS`, `CL-I1-RESERVE-PESS`, `CL-I1-RESERVE-BASE` | verification matrix lists `team/I1/BOM.csv` as the artefact |
