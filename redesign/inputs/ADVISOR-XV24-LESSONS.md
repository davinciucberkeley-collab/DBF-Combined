# Lessons from the advisor's XV-24 "Kestrel" run (VECTOR site)

Source: https://vector-vtol-lab-c71a.dpm5970.chatgpt.site/ (viewer, gear study, engineering handoff, read 2026-11-09).
A separate AI-agent run (ChatGPT/Codex, CadQuery + OCCT + Three.js) on a ~2 m uncrewed VTOL with tilting nacelles.
It is a different aircraft; we take its methods and lessons, not its numbers.

## What it achieved
- A 4,146-part solid-CAD inventory down to fasteners, bushings, pins, cotters, wiring and the ground tools needed
  for service, shown in a Three.js viewer with modes: whole aircraft / inside & wiring / structure / exploded,
  a part browser, click-to-inspect and double-click-to-focus.
- One solid inventory meant to drive the viewer, BOM, STEP/STL exports, flat profiles, wire cuts and instructions.
- Real joint stacks for each connection: mating parts, fits, grip length, useful thread engagement (with minimum
  acceptance values), positive retention (shoulders, crosspins, cotters instead of grub screws), tool access and
  removal order. Example: nose gear service sequence with named tools and pull distances.
- Wiring treated as a physical installation: supports, chafe protection, bend radii, strain relief, connector
  access, isolation, slack across moving joints. "A drawn line between electrical nodes is not an installation."
- An honest status vocabulary: proposal → generated geometry → passed check → physical qualification. Missing
  and failed parts stay in the inventory and are shown as missing.

## Where it went wrong (avoid)
- **It never produced a complete aircraft.** Whole assembly HOLD (51 of 147 nose-gear members), no accepted mass.
- **Mass blew up:** 3 kg target → 6 kg → a partial inventory of 10.84 kg. Detail without a mass budget kills a VTOL.
- **Verification became the product:** sealed receipts, SHA256 chains, kernel-level B-rep validity proofs, CPU-time
  "authorizations". The user complained nothing visible had changed for a day.
- Monolithic long CAD builds that time out and lose state; geometry-kernel defects (non-manifold unions, 0.001 mm
  gaps) consumed the effort.
- Over-detailed parts (custom turned 17-4PH pins, machined 6061 beams) where a student team would buy hardware.

## What our redesign adopts
1. **Status per item** (use exactly these words): `PROPOSED`, `MODELLED` (in Fusion script), `CHECKED` (passes
   check.py / calc), `VERIFIED` (bench/physical evidence). Missing parts are listed, never silently dropped.
2. **Joint-stack table for every fastened interface** in `interfaces.json` / SPEC.md: fastener (size × length,
   grade), clearance/tap hole, useful thread engagement, insert type (heat-set, T-nut, nylock), torque or
   "snug + threadlocker", tool, access direction, install and removal order.
3. **Wiring as installation:** route, support points, bend radius, chafe protection, strain relief, disconnect at
   every removable joint (wing for transport), slack across moving surfaces.
4. **One inventory drives everything:** Fusion scripts + params.json → parts.csv/BOM → renders → build manual →
   viewer. Ground tools/fixtures are listed but never counted in flying mass.
5. **Viewer modes** for our web views: whole aircraft / inside & wiring / structure / exploded, click a part to see
   its part id, mass, status, interfaces and the proof-chain claims that depend on it.
6. **Proportionate verification:** checks a student can rerun in seconds (check.py, merge_check.py, calc scripts),
   not kernel-level certification. Visible, complete increments beat partial perfect subassemblies.
7. **Mass discipline first:** every subsystem reports against MASS-CG.md; the 7.75 kg limit is a hard gate.
