# QP-1 requirements and first tests (A2 / H1), summary

2026-11-14. Files (all `PROPOSED`, nothing built, run or bought): `qp/requirements/REQUIREMENTS-QP.md`, `TEST-PLAN-QP1.md`, `CARRY-OVER.md`. Numbers are `EST` from the restudy candidate B (1.88 kg, 1.40 m span, 4 lift + pusher) unless a source says otherwise.

## Requirements
- 5 USER requirements only: $2,000, 30 Apr 2027, portable / one-piece in a car, 3-D physics, < 25 kg. Everything else is PHYS or DERIVED with its basis.
- All K09-L requirement IDs are carried (about 25), adapted (about 35) or dropped (tailsitter items: elevons, fins, foot, pitch-over, transition switch).
- New: lift-motor-out (hover case declared **not survivable**, 4 fixed rotors), transition at 1.3 Vs with pusher thrust >= 0.25 W, Q_ASSIST window, boom modes >= 20 % from 1P / 2P, gear tip-over >= 30 deg, pusher / parked-prop clearance, energy split (hover 65 %, transition 18 %, cruise 18 %).
- Mission re-derived: hover-mode 3.0 min (kept), cruise **3.6 min** at 15 m/s (213 s, R 39.7 m, far point 190 m inside the 250 m fence).

## Tests (order to buy down risk before the 15 Dec airframe order)
SITL QuadPlane (no spend) -> pack test -> motor/prop bench (pass: >= 0.94 kgf fresh, >= 0.75 kgf at 20 % pack, hover throttle <= 0.625, pusher >= 0.47 kgf) -> CG breadboard and weigh -> boom tap test -> bench electrics and range. Rig is the K09-L H1 stand with a tighter noise line (2 g).

## Carry-over finding
`../firmware/vtol_c0.param`, `check_params.py`, `mission_test.py` and `c0_physics.py` (root, older C0 concept) are already QuadPlane tooling on the same board and are nearer than the tailsitter K09L.param. Tailsitter transition, elevons, transition switch, fin CAD and the 1.25 m box do not carry.

## Open, not decided
1. Span 1.40 m against the 1.25 m box (longer box, split wing, or shorter span); no car has been measured.
2. Q_ASSIST_SPEED rule: C0's (AIRSPEED_MIN - 3, 10.0 m/s) against Vs + 2 (11.6 m/s).
3. FC board: CoreWing F405 Wing V2 (K09-L, C0) against the restudy's SpeedyBee F405 Wing APP.
4. Motor-out layout: confirm the declared non-survivable hover case.
5. Unverified: SITL frame name `quadplane` and the SITL motor-failure parameter name; ArduPilot Q_ASSIST parameter text (docs pages 404 or truncated, only Q_OPTIONS bits read).
