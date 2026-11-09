# Change requests from the proof-chain tooling (redesign/proofs/)

| # | To | What | Why |
|---|---|---|---|
| 1 | Integrator (`redesign/params/`) | Write each `params.json` leaf as `{"value": …, "unit": "…", "source": "SRC-… or a text basis"}`. Bare values still work. | `build_graph.py` turns every key into a node `P:<dotted.key>`. With a unit it can catch `mm` vs `m` mix-ups, and with a source the chain reaches a datasheet. Without a source the parameter shows as `UNVERIFIED` ("no source"). |
| 2 | Integrator | Keep shared sources (`SRC-…`) and requirements (`R-…` or the config-study ids `C1`…`D11`) in one hand-written `redesign/params/claims.json` (format: `examples/requirements/claims.json`). | One place for ids that every analysis cites, so they are never duplicated. A duplicate id fails the build. |
| 3 | Interface keeper (`redesign/interfaces/`) | None needed now. `interfaces/SCHEMA.md` (`parts[].id`) is already what `build_graph.py` reads. Please keep part ids in that place if the schema changes. | Claims name parts by id. The build warns about ids it cannot find, and the viewer links each id out to the 3-D part. |
| 4 | Aircraft web viewer (`redesign/viewer/`) | Open `index.html#part=<part_id>` focused on that part, and link back to `../proofs/viewer/index.html#node=<id>` for a part's claims (claims about a part are the graph edges of type `about`, in `proofs/out/graph.json`). | Click from a claim to the part and from the part to its claims (advisor lesson 5). Use `build_graph.py --part-link` if you choose another URL. |
| 5 | Analysis and subsystem agents | Emit claims with `proofkit` (see README) and re-run the script after any parameter change. | `build_graph.py` fails on drift, so the stored numbers stay current. |
