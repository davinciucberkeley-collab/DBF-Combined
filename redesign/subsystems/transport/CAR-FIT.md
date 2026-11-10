# Car fit (R-CAR-FIT): measure two cars before freezing

Status `UNVERIFIED`. **No car has been measured yet.** D7 cannot measure a car. The team lead names the two cars
(CR-A1-42, before 15 Dec) and the owners measure them with a tape in about 10 min each. The 0.54 m box and the 1.15 m
span freeze only when both rows below pass. The numbers in the results table are measurements only, never values from
spec sheets.

Box to fit: **1.25 × 0.55 × 0.54 m** (D-31). Fallback: 1.25 × 0.55 × 0.50 m with 56 mm columns and a "MAX DROP 0.15 m" label.

## Decision rule

| Result | Action |
|---|---|
| Both cars pass at 0.54 m | A1 changes `requirements.box_external_m` from `PROPOSED` to frozen; build per `BUILD.md` |
| A car passes only at 0.50 m | Tell A1 (CR-D7-01 fallback): box 0.50 m, `trn.cradle.crush_t_m` 0.056, `requirements.box_drop_m` 0.15, label on the lid; re-run `transport_calc.py` |
| A car fails at 0.50 m | Pick another car. The 1.25 m length is the span plus pads, and only a span change (A1) shortens it |

## How to measure (tape measure, 10 min per car)

| Where | Measure | Pass if (0.54 box) | Pass if (0.50 box) |
|---|---|---|---|
| Back seat, across | door-to-door width at seat-cushion height, doors closed | ≥ 1.27 m | ≥ 1.27 m |
| Back seat, door | clear opening: width at the bottom, height at the narrowest point | both ≥ 0.57 m (box goes in end first) | width ≥ 0.57, height ≥ 0.52 m |
| Back seat, height | seat cushion to headliner at the centre seat | ≥ 0.56 m | ≥ 0.52 m |
| Hatch / trunk | floor length (seats as used), width between wheel arches, opening height | one horizontal pair ≥ 1.27 × 0.57 m and height ≥ 0.56 m | same pair, height ≥ 0.52 m |
| Trunk lid opening | width × height of the opening | the 0.55 × 0.54 end passes, then the box slides in | the 0.55 × 0.50 end passes |

Every dimension includes a 20 mm allowance for handles and straps. A pass on either the back seat or the hatch/trunk is enough.

## Pre-screen (not a measurement)

| Car class | Likely route | Risk to the 0.54 m height |
|---|---|---|
| Compact SUV / hatchback | lengthwise through the hatch with one rear seat folded. Width between the wheel arches is about 1.0 m (dealer figure for a RAV4-class SUV, `UNVERIFIED`), so the box will not go across | low: the cargo opening is well over 0.6 m high |
| Sedan | across the back seat; the trunk opening is usually the limit | medium: measure the rear door opening height and the cushion-to-headliner height |

## Results

| Car (make, model, year, owner) | Location / route | Measured (m) | Pass 0.54 m box | Pass 0.50 m box | Measured by, date |
|---|---|---|---|---|---|
| (car 1, named by the team lead) | | | | | |
| (car 2, named by the team lead) | | | | | |

## Loading the car (round 3)

| Item | Where | How it is held | Why |
|---|---|---|---|
| Box 1.25 × 0.55 × 0.54 m, 5.8 kg | hatch floor lengthwise (seat folded), or across the back seat | a cam strap or the seat belt around the box; never on its end; nothing on the lid | the end-first and lid-down drops are label-only (`SPEC.md`) |
| Battery can (2 packs), 3.3 kg | cabin floor behind a front seat | wedged by the seat; never in a closed trunk in the sun | packs 20–34 °C at flight (flight card, E2/H3); the can contains a pack fire |
| Mat 0.8 × 0.4 m folded, 2.7 kg | flat under the box or on the floor beside it | under the box or wedged | a loose 2.7 kg panel must not slide into the box in a hard stop |
| Tote, 0.6 kg | anywhere in the cabin | — | — |

The car must take all four items at once with the box flat. A hatchback with one rear seat folded does this. In a
sedan with the box across the back seat, the can and the mat go in the front footwell and the trunk.
