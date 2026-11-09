# Change requests from the aircraft web viewer (redesign/viewer/)

| # | To | What | Why |
|---|---|---|---|
| 1 | Proof-chain tooling (`redesign/proofs/`) | In `proofs/examples/*/claims.json`, name the example parts by the ids of the generic test aircraft (`FUS-001`, `WNG-003`, ...; see `redesign/interfaces/example-output/interfaces.json`) instead of `EX-FUS-001`, and drop the `EX-PWR-*` / `EX-HRN-*` parts it does not have. | The viewer links a part to the claims about it by part id. For the demo, `build_data.py --examples` strips an `EX-` prefix and warns about 9 ids that match nothing. With matching ids the strip can go. |
| 2 | Interface keeper (`redesign/interfaces/SCHEMA.md`) | Add an optional part field `structural: true/false` (load-carrying). | The Structure mode shows load-carrying parts. Without the field the viewer infers it: not electrical, and at least one mechanical edge that is not a hinge. That is wrong for e.g. a cosmetic fairing that is bolted on. |
| 3 | Interface keeper | State in SCHEMA.md which side of a `hinged` edge moves (the viewer assumes `part_a` turns about the joint). | The part panel has a deflection slider for hinged surfaces. |
| 4 | Integrator (`redesign/params/`) | Write `redesign/params/mass_budget.json` (`limit_g`, `allocations_g`, `cg_x_m`) as `interfaces/SCHEMA.md` proposes. | The Mass / CG overlay draws the CG target band and the allocation table from it. Until then the real aircraft shows mass and CG without a target. |
