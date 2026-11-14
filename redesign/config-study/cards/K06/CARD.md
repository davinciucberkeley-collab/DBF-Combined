# K06 — Scratch-built tilt-tricopter (2 front tilt + 1 fixed rear)

Status: PROPOSED (concept sizing, 2026-11-09). Mission: `REQUIREMENTS.md` §3 default M-A. Numbers come from `sizing.py` → `sizing.json` and `cost.csv`.
Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = not checked against a primary source. `research/*/FINDINGS.md` did not exist when this card was written, so prices come from `docs/research/*` (2026-10/11) plus three checks made 2026-11-09. Every controls-evidence claim is `UNVERIFIED`.

<svg viewBox="0 0 1400 1720" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="30" fill="none" stroke="currentColor" stroke-width="3">
<text x="20" y="40" fill="currentColor" stroke="none" font-size="34">K06 three-view, to scale (units mm, hover configuration, props shown as discs/lines)</text>
<!-- TOP VIEW, origin = root leading edge on centreline -->
<g transform="translate(700,260)">
<text x="-680" y="-170" fill="currentColor" stroke="none">TOP</text>
<polygon points="0,0 650,237 650,437 0,320 -650,437 -650,237"/>
<polygon points="250,305 620,372 620,432 250,365" stroke-dasharray="8 6"/>
<polygon points="-250,305 -620,372 -620,432 -250,365" stroke-dasharray="8 6"/>
<line x1="60" y1="22" x2="60" y2="331" stroke-dasharray="4 6"/><line x1="-60" y1="22" x2="-60" y2="331" stroke-dasharray="4 6"/>
<rect x="-60" y="-163" width="120" height="463" rx="40"/>
<rect x="-11" y="300" width="22" height="317"/>
<rect x="285" y="-80" width="30" height="140"/><rect x="-315" y="-80" width="30" height="140"/>
<circle cx="300" cy="-33" r="140" stroke-dasharray="10 8"/><circle cx="-300" cy="-33" r="140" stroke-dasharray="10 8"/>
<circle cx="0" cy="567" r="140" stroke-dasharray="10 8"/>
<line x1="650" y1="300" x2="650" y2="437" stroke-width="10"/><line x1="-650" y1="300" x2="-650" y2="437" stroke-width="10"/>
<circle cx="0" cy="167" r="12" fill="currentColor"/><text x="20" y="180" fill="currentColor" stroke="none">CG</text>
<line x1="-650" y1="-200" x2="650" y2="-200"/><text x="-110" y="-210" fill="currentColor" stroke="none">span 1300</text>
<text x="330" y="-180" fill="currentColor" stroke="none">tilt motor + 11 in prop</text>
<text x="160" y="600" fill="currentColor" stroke="none">fixed rear motor</text>
<text x="330" y="470" fill="currentColor" stroke="none">elevon</text>
<text x="-640" y="560" fill="currentColor" stroke="none">wing halves 590 + pod 120</text>
<text x="-640" y="600" fill="currentColor" stroke="none">root chord 320, tip 200, LE sweep 20°</text>
<text x="-640" y="640" fill="currentColor" stroke="none">front motors 200 ahead of CG, rear 400 aft</text>
</g>
<!-- FRONT VIEW, ground y=0 -->
<g transform="translate(700,1160)">
<text x="-680" y="-250" fill="currentColor" stroke="none">FRONT</text>
<rect x="-650" y="-135" width="1300" height="35"/>
<rect x="-60" y="-190" width="120" height="110" rx="30"/>
<rect x="645" y="-230" width="10" height="130"/><rect x="-655" y="-230" width="10" height="130"/>
<rect x="285" y="-205" width="30" height="70"/><rect x="-315" y="-205" width="30" height="70"/>
<line x1="160" y1="-215" x2="440" y2="-215" stroke-width="6"/><line x1="-440" y1="-215" x2="-160" y2="-215" stroke-width="6"/>
<line x1="-140" y1="-232" x2="140" y2="-232" stroke-width="6" stroke-dasharray="10 8"/>
<line x1="300" y1="-100" x2="300" y2="0"/><line x1="-300" y1="-100" x2="-300" y2="0"/>
<line x1="-900" y1="0" x2="900" y2="0" stroke-width="1"/>
<text x="460" y="-225" fill="currentColor" stroke="none">prop Ø279</text>
<text x="-640" y="40" fill="currentColor" stroke="none">TPU skid feet under nacelles + tail; ground clearance 100</text>
</g>
<!-- SIDE VIEW, nose left, ground y=0, x origin = root LE -->
<g transform="translate(300,1600)">
<text x="-280" y="-330" fill="currentColor" stroke="none">SIDE</text>
<rect x="-163" y="-190" width="463" height="110" rx="35"/>
<rect x="300" y="-172" width="317" height="22"/>
<polygon points="0,-135 320,-150 320,-160 0,-170"/>
<polygon points="237,-140 437,-140 437,-260 300,-260"/>
<rect x="-48" y="-215" width="30" height="70"/>
<line x1="-173" y1="-225" x2="107" y2="-225" stroke-width="6"/>
<line x1="-130" y1="-320" x2="-130" y2="-40" stroke-dasharray="10 8"/>
<text x="-270" y="-15" fill="currentColor" stroke="none">cruise: front prop tilted 90° forward (dashed)</text>
<rect x="552" y="-220" width="30" height="48"/>
<line x1="427" y1="-230" x2="707" y2="-230" stroke-width="6"/>
<line x1="-33" y1="-135" x2="-33" y2="0"/><line x1="567" y1="-150" x2="567" y2="0"/>
<line x1="-300" y1="0" x2="1000" y2="0" stroke-width="1"/>
<line x1="-163" y1="40" x2="617" y2="40"/><text x="140" y="80" fill="currentColor" stroke="none">pod + boom 780</text>
<text x="640" y="-250" fill="currentColor" stroke="none">rear motor stops in cruise</text>
<text x="460" y="-280" fill="currentColor" stroke="none">tip fin</text>
</g>
<g transform="translate(1000,1680)"><line x1="0" y1="0" x2="200" y2="0" stroke-width="6"/><text x="0" y="-12" fill="currentColor" stroke="none">200 mm</text></g>
</svg>

## Key numbers (baseline: tricopter, 4S, two vectored tilt servos)

| Item | Value | Basis |
|---|---|---|
| Take-off mass | **2.39 kg** (non-battery 1.54 + 10 % contingency 0.15 + pack 0.45 + growth 0.25) | `sizing.py` build-up, most part masses `ESTIMATE` |
| Span / area / AR | 1.30 m / 0.338 m² / 5.0; MAC 0.265 m | geometry |
| Wing loading / stall / min. transition | 7.1 kg/m² / **11.5 m/s** (CLmax 0.85 `ESTIMATE`) / 15.0 m/s (1.3 Vs) | calc |
| Hover | 380 W, **25.7 A** at 14.8 V; 0.80 kg per motor; disk loading 127 N/m² | X3108S maker table ×1.10 install loss; momentum check with FM·η = 0.495 fitted to the table: 376 W |
| Hover T/W | 1.98 on the table, **1.79 with sag** (gate 1.6); ~0.28 kg headroom past the growth allowance before T/W drops to 1.6 | maker 1,580 g max at 14.8 V, ×0.90 sag `ESTIMATE` |
| Cruise | 15.5 m/s, **L/D ≈ 8.2** (CD0 0.040, e 0.8 `ESTIMATE`), 108 W, 7.3 A; needs ≈ 8,300 rpm vs ≈ 11,300 available | η_prop 0.55 × η_motor+ESC 0.75 `ESTIMATE` |
| Battery | Ovonic 4S 5000 mAh 50C, 74 Wh, 448 g, ×3 | us.ovonicshop.com $48.57, seen 2026-11-09 |
| Endurance | Hover only: 7.5 min. **2 min hover + 2 transitions + 17 min cruise** with 20 % reserve, 80 % usable (passes the threshold and the 10 min objective). A 4S 3300 pack would give 9.7 min. | calc |
| Peak currents | transition 34 A, all motors full 90 A, so the disconnect must carry ≥ 42 A: **AS150U** (an XT90-S at 40 A fails) | D9 |
| Gust | 8 m/s side gust needs about 8° bank in hover | side area 0.07 m² `ESTIMATE` |
| Tilt-servo load | pivot on the thrust line; gyroscopic 0.17 N·m vs 329TG 1.9 N·m at 6 V (11×) | calc, prop inertia `ESTIMATE` |
| **Cost** | **$1,649 total** (goods $1,408 + tax $144 + shipping $97). **Reserve $351.** One bad crash ≈ $340. | `cost.csv` |
| Packed | **one box, 0.88 × 0.50 × 0.39 m**, about 2.4 kg aircraft + 1.4 kg packs + box; longest piece 0.78 m | passes C3 (a)–(c); the 0.50 m width sits exactly at the limit |
| Option K07 (4th rear motor) | 2.57 kg, T/W 2.22 with sag, 362 W hover, 16 min cruise, **+$78** | `sizing.json` |
| Option U05 (one coupled servo) | 2.34 kg. **Not coherent alone:** a fixed-rear tricopter with coupled tilt has no yaw control (unbalanced rear torque, no differential tilt), so it needs a rear yaw servo and saves ≈ $0 | ArduPilot tilt-rotor docs `UNVERIFIED` |

## Transport and assembly
Box layout: the two wing halves (each 0.59 × 0.45 m with its nacelle, props off) lie stacked; the pod+boom sits on top; packs travel separately in the ammo can. In the field: slide each half onto the 22 mm carbon joiner, fit one nylon M5 thumbscrew, plug an XT60 (front ESC power) and one 6-pin plug (ESC signal, tilt servo, elevon), fit 3 props. That is **5 field joints, one person, about 8 min** `ESTIMATE`. The XT60 on each half carries 8 A in hover and 30 A peak at full throttle; check it for heat on the bench.

## Build (Jacobs Hall processes)
Hot-wire XPS cores with printed root and tip templates (10 h). Tape skin, elevons and foam-board fins (8 h). Glue in the spar sockets (3 h). Printed PETG pod (about 30 h of unattended printing, 12 h hands-on). **Tilt nacelles: 6 mm shaft in two flanged bearings, servo horn link, expect three print iterations (25 h).** Boom and rear mount (4 h). Wiring (15 h). ArduPilot setup and failsafes (25 h). Bench tests (15 h). Total **about 120 person-hours** `ESTIMATE`: 4–5 weeks for 3–4 students, then 3–4 weeks of hover and transition tuning. Crash repair: recut a wing half in 4 h, reprint a nacelle overnight. Long-lead parts are the carbon tubes (overseas) and the CoreWing FC (on backorder); a Kakute H743-Wing at $107 is the fallback.

## Controls
ArduPilot Plane with `Q_ENABLE 1`, `Q_FRAME_CLASS 7` (Tri), `Q_TILT_ENABLE 1`, `Q_TILT_TYPE 2` (vectored yaw: hover yaw comes from differential front tilt), `Q_TILT_MASK 3`, tilt servos on `SERVOn_FUNCTION` 75/76, elevons on 77/78, `Q_TILT_RATE_UP/DN`, `Q_TILT_MAX`, airspeed sensor, `Q_ASSIST_SPEED` ≈ `AIRSPEED_MIN` − 3. The rear motor stops in fixed-wing flight. The lineage is the E-flite Convergence and HEEWING T1 parameter sets `UNVERIFIED`. **The screening's `Q_TILT_TYPE 1` binary retract idea does not work on K06 as drawn:** binary tilt gives no vectored yaw, so it needs either a rear yaw servo or the K07 fourth motor (a front-tilt quad that yaws on motor torque). **K07 with one coupled binary servo is the coherent low-risk variant** (+$78, T/W 2.22).

## Top 3 risks
1. **No redundancy in hover.** Losing the rear motor or ESC, or a stripped tilt servo, means a crash (the same holds for K07). Mitigations: a 200-cycle tilt bench test, spare servos and motors, hover tests below 3 m.
2. **Tilt and transition tuning on a one-off airframe.** Pitch trim changes as the rear motor spools down; the nose rears up in the forward transition; the vectored-yaw gains need tuning. Few scratch-built tilt-tris have documented ArduPilot logs `UNVERIFIED`. This is probably 3–4 weeks of the 12.
3. **Hover/cruise prop compromise and mass growth.** The 4.5 in pitch prop needs about 74 % of available rpm at 15.5 m/s, and the cruise efficiency is only an estimate. T/W reaches 1.6 if the aircraft ends up about 0.28 kg over this build-up plus growth allowance (D14 gate).

## First prototype test
**Tilt-nacelle bench rig** (SCREENING §5, about $10 extra, 1 day). Mount one complete printed nacelle (329TG, bearings, X3108S, 11 in prop) on the thrust stand. Command 0→90° tilts at 800 g thrust for 200 cycles. Pass if: hinge slop < 1°, servo case < 60 °C, thrust within 5 % of the table, no change in rpm or current at angles in between. Then do a tethered QHOVER of the complete airframe at 2.4 kg before any transition.
