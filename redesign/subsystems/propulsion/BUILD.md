# Propulsion stations — build notes for G4

Owner E1. Four stations, same steps each; do the incoming check once on the first set. Station ids, rotation and
adapter thread: UR CW / LH, UL CCW / RH, LR CCW / RH, LL CW / LH (F4 motor map). Prerequisite: D3's mounts
(`FIN-003`) and ESC pads (`FIN-007`) printed in ASA and bonded, cured 24 h + 4 h at 50 °C (fins `BUILD.md`).

## Tools and consumables

| Item | Use |
|---|---|
| 0.1 g scale, calipers, 2 mm drill shank (depth probe), luggage scale | incoming check, torque by force at a lever |
| 2.0 mm and 2.5 mm hex keys, 10 mm spanner (the box-pouch spanner) | adapter screws, motor screws, prop nut |
| Loctite 243 (blue), IPA, paint pen | screw tips only; witness marks |
| Multimeter + bench supply (2.00 A) | 4-wire phase resistance |
| Labels: UR / UL / LR / LL, CW / CCW | every motor, ESC, prop and adapter |

## Steps

| # | Step | Check after the step |
|---|---|---|
| 1 | **Incoming check (`T-E1-MOTOR-RM`)** on one of each: weigh motor, ESC, prop, adapter set; measure motor base bolt pattern, base-hole depth, bell-top thread depth, motor lead length, adapter post length, washer thickness | Record in `team/E1/`; base holes ≥ 4.0 mm deep (`CL-E1-HOLE-DEPTH-MIN`), post ≥ 15.1 mm with the 1.0 mm washer (`CL-E1-NUT-ENGAGE`), bell thread ≥ 2.0 mm. Any miss: stop, tell E1 (fallbacks: 5.0 mm plate, ISO 4035 thin nut) |
| 2 | Phase resistance (4-wire, 2.00 A through two leads) and no-load current at 10.0 V, no prop | R ≈ 86 mΩ, I0 ≈ 0.9 A (± 20 %), smooth spin both directions |
| 3 | Flash each ESC to Bluejay (bidirectional DShot); set direction per station in the configurator; label | ESC beeps on power-up; direction label matches the motor map |
| 4 | **Adapter to motor (`E-PRP-0n`)**, on the bench: set the adapter pilot over the shaft stub, base flat on the bell; 4 × M3×4 with 243 on the tips only, 0.5 N·m (2.0 mm key), cross pattern; LH adapters on UR and LL | Post runs true by eye on a hand spin (no visible wobble at the tip); witness mark on each head |
| 5 | **Motor to mount (`E-FIN-6n`, D3 owns)**: drill the mount pattern to the measured motor (fins `BUILD.md`), then 4 × M3×8 A2, 243 on the tip only (never on the ASA), 0.20 N·m = 4 N on the luggage scale 50 mm out on the 2.5 mm key; leads toward the outboard (ESC) face | Base flat on the canted plate (no light under the boss); screws ≥ 2.5 mm engaged; motor turns freely; witness marks |
| 6 | **ESC on pad (`E-FIN-6n`)**: ESC FET side out, phase end forward (x 0.078), long side along x, on hook-and-loop tape; one 10 mm strap through the two pad slots; heat-shrink not taped over | Tug test 3 N; strap enters both slots beside the ESC (if it bends over the ESC edge, CR-E1-30) |
| 7 | Phase and power solder joints are harness work (F2 `BUILD.md`, `E-HRN-13…20`); E1 checks phase order by a spin test before props | Each motor turns in its station's direction at 5 % throttle |
| 8 | **Props (`E-PRP-0n`, field joint)**: LPAR06E ring in the bore, prop printed face forward, MRP on UR / LL, MR on UL / LR; 1.0 mm washer, nut, 1.5 N·m with the bell held by hand | Post flush with or proud of the nut; nut witness mark; prop direction matches the arrow on its label |
| 9 | Static check per station on the H1 stand before the first hover (`T-E1-STAND`) | Thrust and current inside the `CL-E1-*` bands; no desync on ten 10 → 100 % punches |

## Field (each set-up, 10 mm spanner only)

Fit four props (step 8); check four motor witness lines and four adapter witness marks; tug each ESC. Remove props
for transport and stow each in its tray slot (`E-TRN-17…20`), label to the motor colour.

## Do not

- Put threadlocker on or under a printed ASA/PETG part (stress-cracks it).
- Substitute a 1.6 mm ISO 7089 washer under the prop nut (the nut then sits 0.5 mm off the post end).
- Swap a CW and a CCW prop, or an LH and an RH adapter: the nut on the wrong hand loosens under prop drag.
