# B08 — Skeptic review (2026-11-09)

Reviewer role: try to refute the card. The card itself is unchanged. All re-runs were done on a copy of `sizing.py` in the
reviewer's scratchpad, so `sizing.json` here was not overwritten. Corrected scenarios come from a short stdlib script with
the same equations plus the changes listed below.

**Scope note:** the workflow task named the card "FIMI Manta / ZOHD Altus primary, T1 fallback". The card has already
reordered this to **T1-S primary, Altus as the alternative, Manta as backup**. This review checks the card as written,
so the T1-S is the main subject.

## 1. Reproduction
`python -I sizing.py` gives exactly the card's table: T1 0.693 kg, 119 W / 8.0 A hover, 32 W cruise, 24.2 min cruise
after 2 min of hover, 9.0 min hover-only, T/W 2.38. **CHECKED** (arithmetic only).

## 2. Challenges

| # | Claim on the card | Challenge and evidence | Verdict / corrected value |
|---|---|---|---|
| C1 | T1-S is 0.73 × 0.645 m with a listed TOW of 0.60–0.75 kg | Those are the figures for the **older T1 Ranger VTOL** (kiwiquads T1 listing: 730 / 645 mm, 451 g, TOW 600–750 g). The **T1-S** VTOL PNP that the cost line buys is listed at **790 mm span, 715 mm length, flight weight 600–950 g** (rotorama.com T1-S Ranger VTOL PNP, read 2026-11-09; getfpv / RDQ search snippets agree). | **Wrong airframe dimensions.** Use 0.79 × 0.715 m and a listed TOW of 0.60–0.95 kg. The 451 g PNP mass is for the T1, not the T1-S; T1-S PNP ≈ 470–500 g `ESTIMATE`. |
| C2 | "None can take the 0.25 kg growth inside its listed MTOW" | With the T1-S listing (950 g max) the growth case is 0.94–0.97 kg, which is **at** the listed limit rather than clearly over it. | The claim is overstated for the T1-S. Growth is **marginal**, limited by hover T/W (C4) more than by the listing. |
| C3 | Props 6 in (152 mm) `ESTIMATE` | Listings give **3 × 5126 props** (5.1 in, 130 mm), and the T1 listing says 5–6 in is recommended. Disk area falls from 0.0544 to 0.0398 m², and disk loading rises from 125 to about 175 N/m². | **Wrong input.** With D = 0.130 m and nothing else changed, hover becomes 139 W / 9.4 A. |
| C4 | 550 g thrust per FX-1806 2000KV motor on 4S, T/W 2.38 | No maker thrust data. A 1806 at 2000KV on a 5.1 in prop at 4S typically gives 450–520 g static (`ESTIMATE` from generic 1806 / 5 in bench data, `UNVERIFIED`). The T1-S ships **20 A BLHeli_S ESCs** (rotorama), not the card's "FX-25A". | Use **490 g** (`ESTIMATE`): T/W **2.0** at 0.72 kg and **1.5 with +0.25 kg growth (fails the 1.6 gate)**. The thrust-stand test stays first, as the card says. |
| C5 | Hover 119 W from momentum theory, no other losses | On a tilt-tri the downwash of the two front props hits the wing and nacelles in hover. Wing download of 5–15 % of thrust is a standard loss and the card leaves it out. The equal-loading assumption is also optimistic, since the rear rotor of a tricopter usually carries more, and the card's own docstring admits this. A small 5 in prop at low Reynolds number reaches FM 0.5–0.55 at best. | Nominal: m 0.72 kg, D 0.130 m, FM 0.55, η 0.75, download ×1.10 gives **≈ 170 W / 11.5 A**. Pessimistic (FM 0.50, η 0.72, ×1.15, 0.75 kg) gives 220 W / 15 A. **About +40 % over the card.** |
| C6 | 80 % of nominal pack energy usable | A 1500 mAh pack at 7–10 C in hover sags, and the T1-S manual notes the stock setup has **no battery display in flight** (search snippet of the rotorama manual PDF). Until the current sensor is calibrated (ArduPilot forum: low readings are unreliable), 75 % is the safer planning value. | Use 75 %. |
| C7 | Cruise 32 W at 14 m/s, L/D 6 × η 0.5, "calibrated" on the ZOHD Altus | The calibration point is an Altus **maker claim** (70 km/h at 5 A) on a different airframe, with motors stopped but not folded. The T1-S has two exposed nacelles and a stopped rear prop. The calibration is self-consistent (210 W·m/s ÷ 74 W ≈ 2.8), but it is an optimistic maker figure. | Keep L/D 6 as nominal and carry **L/D 5** as the pessimistic case (41 W). |
| C8 | 24 min of cruise after 2 min of hover; 9 min hover-only | Follows from C3–C7. | Nominal **≈ 17 min** cruise and **≈ 6 min** hover-only. Pessimistic **≈ 9 min** cruise and ≈ 4 min hover-only. Still meets the 5 min threshold in every case, and meets 10 min only nominally. The listed "10–15 min flight time" (several retailers) is consistent with this, not with 24 min. A 4S1P 21700 Li-ion pack (as used by the forum T1-S owner) adds ≈ 100 g, takes hover to ≈ 205 W / 14 A (3 C, fine for P45B-class cells) and gives ≈ 60+ min of cruise, but cuts T/W to 1.8. |
| C9 | Transition 12.6 m/s, wing area 0.12 m² | The T1-S wing is larger (790 mm span), so the area is probably ≈ 0.13 m² `ESTIMATE`; wing loading ≈ 5.5 kg/m² and Vs ≈ 9.5 m/s. That is a small change. The wind risk stands: the gust lift ratio is ≈ 0.2 at any of these values. | Little change; the risk is confirmed. |
| C10 | Packed 0.66 × 0.40 × 0.16 m tote; assembled fits on a back seat | The T1-S fuselage plus tail boom is 715 mm long, so a 0.66 m tote is too short. The maker's foam case is included with the F405 + GPS variant (rotorama "included" list). | Packed ≈ **0.75 × 0.42 × 0.18 m** `ESTIMATE` (the maker case). It still fits any car trunk with room to spare, one person, about 2.5 kg with 4 packs. **Transport is the card's strongest point and it holds.** |
| C11 | Cost $1,388.75, reserve $611 | (a) The "T1 Ranger PNP→VTOL conversion kit" spares line is for the **T1**. Whether its motors and servos fit the T1-S (V39 tilt servos, different nacelles) is `UNVERIFIED`. (b) **No spare foam** (wing halves, tail): foam is the part that breaks first in a crash. (c) FAA registration, $5. (d) Shipping of $45 for 3–4 vendors with a ground LiPo shipment is thin. (e) The price of $393.49 at RDQ is a search-result price and its stock is `UNVERIFIED`. RDQ and getfpv refused automated fetches (429/403), so it could not be confirmed. (f) Glue, CA, hinge tape and small hex drivers are partly covered by the $40 hardware line. | Replace the kit line with T1-S-specific spares: 3 × 1806 motors + 2 × V39 servos ≈ $80 `ESTIMATE`. Add a spare wing set + tail ≈ $50 `ESTIMATE` and tools/glue at $20. Shipping $70, FAA $5. Goods $1,228.83 × 1.1025 + $70 + $5 = **$1,429.79**, leaving a **reserve of ≈ $570**. The card's conclusion stands: the plan is well inside $2,000 and a second whole airframe (≈ $434 with tax) is affordable. |
| C12 | Firmware: "official ArduPilot board, community 4.7.1 params settle the question" | The board is confirmed on ardupilot.org (HEEWING F405: V1 has no logging and needs the transitional 4.3.7 bootloader fix; V2 logs to internal flash only, with no SD card; there is no on-board compass, so it needs an external I²C compass). The community thread (discuss.ardupilot.org t/145545) reports that **the factory setup aborted transitions after about 3 s** (the fix was `Q_TRANS_FAIL = 0`) and that tilt endpoints must be bench-set per aircraft to avoid binding. A separate forum report says QLOITER hover "worked on first flights, later all failed" with no resolution found. The thread does not state `Q_FRAME_CLASS` or `Q_TILT_TYPE`; the card's 7 / 2 values stay `UNVERIFIED`. | **Partly confirmed.** ArduPilot support is real, but "settles it" is too strong. Add bench items: transition-fail behaviour, tilt endpoint calibration, external compass orientation. Plan for log size limits on internal flash (V2). |
| C13 | Build 80–100 team-hours, first hover in week 1–2 | Credible for a PNP: no structure is made, and the lead time is US stock. This is the card's real strength against the 12-week window and crash repair (foam + CA, spare airframe in stock). | **Holds** (`ESTIMATE`). |
| C14 | Controls risk | Tilt-tri with vectored yaw on micro servos at 0.7 kg, a 12 m/s transition and the gust ratio of 0.2. The reported factory transition abort and QLOITER failures point to tuning work, not a turnkey aircraft. | Moderate, 3/5. |
| C15 | Capstone content | The card states this itself in risk 2, and the reviewer agrees it is the dominant risk. The team designs almost nothing structural. This is a scope and grading question for the team lead, not a physics question. | Not refuted; flagged. |

**Altus / Manta (brief):** The Altus's 315 W / 21 A hover at 304 N/m² with 5 in tri-blades is plausible. The Manta's 95 min
is not credible (the card already says so); the 3S Li-ion at 1.7 C is fine, but T/W 1.95 → 1.37 with growth fails. No
change to their ranking.

## 3. Numbers the reviewer believes (T1-S primary, corrected)

| Quantity | Card | Corrected (nominal / pessimistic) |
|---|---|---|
| Span × length | 0.73 × 0.645 m | **0.79 × 0.715 m** (listing) |
| TOW | 0.69 kg | **0.72 kg** / 0.75 kg (listed 0.60–0.95) |
| Props | 6 in | **5.1 in (5126)** (listing) |
| Disk loading | 125 N/m² | ≈ 177 / 185 N/m² |
| Hover power / current | 119 W / 8.0 A | **≈ 170 W / 11.5 A** / 220 W / 15 A |
| Hover T/W (with +0.25 kg) | 2.38 (1.75) | **≈ 2.0 (1.5, fails 1.6)** `ESTIMATE` |
| Cruise power | 32 W | 33 W / 41 W |
| Cruise after 2 min hover | 24 min | **≈ 17 min** / 9 min (4S 1500) |
| Hover-only | 9 min | **≈ 6 min** / 4 min |
| Total spend / reserve | $1,388.75 / $611 | **≈ $1,430 / ≈ $570** |
| Packed | 0.66 × 0.40 × 0.16 m | **≈ 0.75 × 0.42 × 0.18 m** (maker foam case) |
| Build effort | 80–100 h | 80–100 h (holds) |
| Build difficulty / controls risk | — | 1 / 5 and 3 / 5 |

**Bottom line:** The concept survives review. It is cheap, transportable, fast to fly and well inside the budget. The card
overstates hover efficiency by about 40 % (wrong prop size, wrong airframe variant, no wing download) and overstates
endurance by about 30 %. It also uses T1 dimensions for a T1-S purchase. None of this changes the go/no-go. The thrust-stand
pass criterion should change to "hover current within ±25 % of **11.5 A**".

## Sources (read 2026-11-09)
- T1-S VTOL PNP specs: https://www.rotorama.com/product/heewing-t1-s-ranger-vtol-pnp-se-stabilizaci (manufacturer distributor)
- T1 (non-S) VTOL specs, 451 g / TOW 600–750 g, 35 min max cruise claim: https://kiwiquads.co.nz/product/hee-wing-t1-ranger-vtol-fixed-wing-730mm-pnp
- T1-S price $393.49 (search snippet only, fetch blocked): https://www.racedayquads.com/products/heewing-t1-s-vtol-ranger-fpv-airplane-w-f405-stabilizer-gps-pnp
- HEEWING F405 board doc: https://ardupilot.org/plane/docs/common-heewingf405.html
- T1-S on Plane 4.7.1 (transition abort, tilt endpoints): https://discuss.ardupilot.org/t/heewing-t-1-s-vtol-on-4-7-1-parameters/145545 (forum, not manufacturer)
- T1-S manual (no in-flight battery display; text only partly readable): https://www.rotorama.com/assets/docs/f165155da636ec7130ee3b50ab8d926f/42985-1/heewing-t1-s-vtol-pnp-manual-en.pdf
