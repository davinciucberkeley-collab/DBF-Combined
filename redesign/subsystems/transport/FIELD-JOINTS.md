# Field joints and disconnects

Status `PROPOSED`, D7 round 3, 2026-11-09. Every joint that is made or broken between the car and the arm check. The
part owners design the joints. D7 owns this list, the order in `CHECKLIST.md` and the time budget (`CL-D7-SETUP-MIN`).
A4 marks these edges `"field_joint": true` (SCHEMA A4 data blocks).

## The rule

K09-L has **no structural field joint**. The wing, fins, tubes, motors, feet and harness travel assembled. A field
joint is allowed only if it is keyed or colour-coded, needs at most the 10 mm prop spanner (D-40), and can be checked
by eye or by hand in under 5 s.

## Joints made at every set-up

| # | Joint | Parts (owner) | Type | Tool | Time s | Foolproofing | Retention / check | Wear item |
|---|---|---|---|---|---|---|---|---|
| 1 | Prop to motor × 4 | `PRP-003-*` + `PRP-004` adapter on `PRP-001-*` (E1) | M6 prop nut, 1.5 N·m; LH thread on the CW motors | 10 mm spanner (`TRN-106`) | 140 | colour dot on each prop and motor; a LH nut does not start on a RH post | firm wrist turn; prop turns freely; nut re-checked after the first hover of the day | spare M6 nuts in the pouch; replace a prop with any nick |
| 2 | Pitot boom into the nose socket | `AVN-005` (F3) in `POD-006` (D2) | keyed 6 mm plug, 35 mm deep, flange ≥ 30 × 30 mm | none | 20 | keyed: fits one way | 2 barbed couplers pushed onto the silicone tubes; tubes not kinked; tip cover off and into the pouch | tube ends: trim 5 mm when loose |
| 3 | Pack into the bay | `PWR-001` (F1) in the pod tray (D2, C3) | 2 straps + stops + trim spacers | none | 40 | trim mark on the tray; leads exit aft | pack does not slide when the aircraft is tipped nose-down by hand | straps: replace if the hook side is lint-filled |
| 4 | Pack plug (the only electrical field disconnect, F2) | `PWR-001` lead ↔ AS150U main disconnect (F1) | AS150U anti-spark pair | none | 15 | polarised housing; TX on first (flight card) | fully seated, no gold visible; FC tones | inspect the pins every 20 matings (`UNVERIFIED` rating) |
| 5 | Hatch | pod hatch (D2) | hook-and-loop tabs | none | in 3 | — | closed flush before the arm check | tabs |

Pack-down reverses the order: **plug first** (4), then the pack (3), boom (2), props (1). The pack goes straight
into its LiPo bag in the battery can.

## Joints made only after damage (not in the set-up time)

| Joint | Parts (owner) | Type | Tool | Time | Spares carried |
|---|---|---|---|---|---|
| Foot insert swap | `GER-002` piston + cartridge + pad in `GER-001` shoe (D5) | snap fit, 2 fingers, colour: orange upper, blue lower | none | 3 min per foot (`CL-D5-REPLACE-TIME`) | 4 + 4 pre-glued inserts, 16 + 16 cartridges, 2 shoes (tote, `TRN-108`) |
| Prop swap | as row 1 | as row 1 | 10 mm spanner | 35 s | 4 spare props in the tray |

## Never broken at the field

Motor bullet connectors, ESC power leads, servo and signal plugs, the FC USB port (workshop only). Every bonded
joint. If one of these needs attention, the day's flying ends.

## Transport-side quick releases (D7)

| Joint | Type | Time s | Check |
|---|---|---|---|
| Lid to base (`E-TRN-10/11/12`) | plug lid + 2 cam-buckle straps | 10 | lid flush, both buckles bitten |
| Aircraft in the cradles (`E-TRN-06…09`) | contact only, no fastening; lid pillars give 5 mm preload | 15 | aircraft does not move when the closed box is tilted 45° |
| Props, boom, pouch in the tray (`E-TRN-16…20`) | foam pockets | 15 | 8 props, boom with tip cover, pouch with spanner |
