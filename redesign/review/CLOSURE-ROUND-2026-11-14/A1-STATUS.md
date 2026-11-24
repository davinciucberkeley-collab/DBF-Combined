# Closure round: A1 status and open requests (resume here)

Written 2026-11-14 when the session hit its usage limit. Decisions applied to params.json: D-160 (A2 re-derived requirements), D-161 (APC 11x5.5E/EP, 73.2 A), D-161c (Kakute H743-Wing + Lua spin cap), D-162 (test order, racetrack), D-163 (allocations power 635 / harness 144), D-164 (cant 10 deg, cg range [0.0430, 0.0501], elevon chamfers), D-165 (gate 2.64 kg, taller foot), D-165b, D-166 (thrust limit 22.1 N). Not yet in CHANGE-LOG.md. Pending A1 trade: turbulator vs D-121 lead x pack (Ovonic 6500 / CNHL 6000 / Gens Ace 6000) after B2. Agents still running at cut-off: C2, C4, C6, D5, D7, D2, F3, F1, B2 (their reports land in this folder). Not started: D3, D1, F2, B1, H1, I2, A2 wording, J6 board, then gates (verify3.sh, closegraph3.sh, assembly_check), STATUS, media, commit, push, republish.


Superseded: D-161 prop (5.5E), D-161b/c (Lua, Kakute), D-170 nose. Current design: X2814 V3 + APC 11x8E/EP, 10 deg cant, 80 A limiter, Q_M_SPIN_MAX 0.81, THR_MAX 41 + FWD_BAT comp, gate 2.70 kg, Gens Ace Shorty 6000 HV pack at -0.0545, CoreWing FC, taller foot, lower turbulator, RW 35046-S tube, face_ahead 4 mm, cheeks 5.5 mm, XT60H, 3 caps/ESC.

## From C6 (C6.md)
- D3: fin_detail.mount.key_w_m 0.003 -> 0.007, key_d_m 0.0025 -> 0.0020 (key_clear 0.0002); rebuild FIN-003/FIN-008; check notch fit.
## From C1 (C1.md, CR-C1-40)
- F4: PTCH2SRV_RMAX_UP 100 -> 35, PTCH2SRV_RMAX_DN 100 -> 20 in K09L.param; fsw.rate_max_fw_degs [150,35,20]; add fsw.rat_vt_degs 30; check Q_ASSIST_ANGLE cannot bypass FW rate clamp at speed (set 0 or show speed-gated); 45 deg turn at 17 m/s needs 23.4 deg/s.
- J6: review re-class to info of CL-C1-N-STALL-LINE-VD, -Q-UP-MAX, -Q-DN-MAX.
## From E2 (E2.md)
- F4: BATT_LOW_MAH 2700 -> 3100 (K09L.param l.304); BATT_CRT_MAH stays 1300.
- H3: flight card 4 "2 600 mAh" -> 3 100; 4b go-around budget 40 s / 336 mAh, then alternate spot.
- A3: CL-A3-PACK-ACCEPT must reach >= 556.0 g (S02/S03 package 560.7) -> closes E2 PACK-LARGEST, SKU-MASS-MARGIN, PACK-MASS.
- A1 notes: battery.mass_kg note acceptance text; goaround_hover_s note "implemented in E2 failsafe_rows()".
- J6: E2 PACK-ACCEPT-KG made info (duplicate of SKU-MASS-MARGIN); pack-trade rows removed (Li-ion, 130C XT60, Admiral 4000, 5000/8000 EST).
## From I1 (I1.md) budget: (a) all-new $2,389.38 (over $389.38); (b) owned TX/charger/meters $2,182.17; with all requests (b) $1,978.76
- D7: box T01+T02+T03+T06 <= $40 incl tax (today $158.69), drop test check. -$118.69
- E2: sign off US Ovonic pair (lead gauge check before order).
- B4/E1: use for B04 11x4.5 x4 or delete (-$16.89); confirm B09 deleted.
- C4: tube 35046-S 48in $167.54 + D08 plug $37.96 = biggest lever; cheaper tube if pass lines allow.
- F3: SpeedyBee F405 Wing vs CoreWing -$23.70 if bdshot/8A BEC/stable Plane hold.
- D1: hot wire from 4S pack, drop bench supply -$10.88 (G11 is $46.01 actually).
- D3/A3: US 19 mm plug tube -$27.25.
- C6 tools: lever-arm torque method instead of K01 -$77.67.
- Tools $507.21 outside: Jacobs Makers Pass tools (memory: Jacobs tools available) -> check which X14 tools Jacobs provides.
- A1: params syncs in I1.md 4.
## From B4 (B4.md, CR-B4-31/32)
- F4: THR_MAX 70 -> 60; Q_ASSIST_ALT 15 -> 0, Q_ASSIST_ANGLE -> 0 (Q_ASSIST_SPEED keeps assist below ~14 m/s; F4 owns safety trade, consistent with C1 request); add fsw keys assist_alt_m, assist_angle_deg; CL-F4-SPIN-MAX -> CL-B4-Q-CAP-VQ (0.852), CL-F4-FW-ACT-MAX -> CL-B4-FW-CAP-VD (0.714); ASM-F4-FW-PASSTHRU pass-through; re-run level speed (THR_MAX 60: 18.25 m/s at 3.6 V/cell vs AIRSPEED_MAX 18, thin); Q_TAILSIT_THR_VT <= THR_MAX.
- D1/A1: elevon TE chamfers next to fin root: inboard panel TE to y 0.28 (20 mm), outboard to y 0.41 (70 mm), from hinge-line ends y 0.30/0.34; new key wing.elevon.te_chamfer_m [0.02, 0.07]; area 17.2 -> 15.5 % S. Copy D6, B2, B3, A5.
- B3: AVL re-run with chamfered panels (trim use ~0.467, roll 183 deg/s, MIX-PITCH ~0.74).
- B1: FW climb at THR_MAX 60.
- A1: propulsion.rpm_max note (in-flight max 9449, static cap 9354, unlimited 10637 not flown -> CL-B4-RPM-UNLIMITED).
- C1/J1: in-flight rpm 9449 (+1 % gyro).
- J6: SF-RPM re-class; D-158 hold point withdrawn.
## From E1 (E1.md rev 10): 0 fails; second bound rejected by maker 11.1 V rows (re-class 6 claims to info; J6 review)
- RISK: with 11x5.5MR at 70.2 A +/-1.1 % the winding current <= 25 A holds only for Rm 85.48-86.30 mOhm (unmeasurable band). 11x5.5E/EP at 73.2 A: band 66.4-108.9, T/W fresh 2.078, worst 1.799, cruise ~-9 %, +24 g, -$12.4, hub +1.5 mm.
- A1 DECISION (D-161, proposed): adopt 11x5.5E/EP at 73.2 A for robustness; find the 24 g by re-deriving the mass gate physically: T/W 2.0 with E/EP allows 2.6*2.078/2.0 = 2.70 kg; landing stroke binds at 2.6 kg -> D5/C5 lengthen foot stroke to carry 2.65 kg at 10 deg; then gate 2.65 (T/W fresh 2.039, worst 1.765). Batch 2: E1 re-run at E/EP; B4 tip gap + E-series rpm limit + THR_MAX; C5/D5 stroke at 2.65; A3 roll-up; H1 stand lines; I1 B03/B04.
- params: performance.full_throttle_current_a note (remove 93 A text); -> 73.2 if E/EP.
- F4: SPEC.md lines 13/47 delete "93 if ..."; H1 T-E1-STAND lines confirmation (>=1330 gf fresh, >=1053 gf @11.9 V); T-E1-MOTOR-RM reject >=131 mOhm; F1 path R allow 10.19 mOhm.
## From B3 (B3.md): all B3 claims pass; transition entry design (window +/-4 %: 1.283-1.397 W)
- Entry: throttle 1.285 x learnt hover theta_h via TX throttle override on a transition switch, 2.0 s QSTABILIZE pre-climb then FBWA; start 50-55 m AGL.
- F4: Q_TAILSIT_RAT_FW 12, Q_TAILSIT_ANGLE 70, Q_TAILSIT_ANG_VT 0 (stated), Q_TRANSITION_MS 11667, Q_A_ANGLE_BOOST 0, Q_M_HOVER_LEARN 2, Q_M_THST_HOVER 0.49 start, Q_THROTTLE_EXPO 0.2, Q_ASSIST_SPEED 14; delete 0.65 fallback text (param, SPEC, TUNING-PLAN); S4c pass lines (B3.md); close entry paths: FBWA only via timed switch, no AUTO forward transitions, battery/fence failsafes from Q mode never pitch over (S8).
- F5: EdgeTX transition switch sequence (throttle override 1.285 theta_h, 67 % stick EST, 2 s timer).
- B1: CALC-B1-PITCHOVER held-throttle rule, T0 = CL-B3-TRANS-T0-HIGH 1.389 W -> CL-B1-TRANS-THRUST ~0.796; altitude change = climb 30-50 m.
- H2/H3: 50-55 m start, transition only by switch, no AUTO forward transitions.
- E1: T/W at 10 deg spare mount = 1.995 < 2.0 (MR) -> with D-161 E/EP recheck.
- A1: D-149 text replaced by entry design; S4c condition retired. J6: review B3 2 and 3.
- NOTE: with D-161 E/EP (more full thrust) the 0.80 fraction side gains margin; B3 re-run its window at E/EP.
## USER 2026-11-14: Buy all new -> I1 column (a): $2,389.38 (+$389.38); with requests +$185.97; tools $507.21 only $0 where Jacobs provides.
## D-161 APPLIED to params (E1 D-161): E/EP, 73.2 A, thrust 1.349, rpm_max 13360, prop 22.96 g, cruise 268 W, alloc prop 486, reserve 150. Propulsion allows gate <= 2.651 kg (2.643 at 10 deg spares).
- D3: fin_detail.mount.prop_stack_m +0.76 mm (10.41 mm hub, M6 thin nut ISO 4035 3.2 mm); re-run 10 deg spare-mount geometry; publish CL-D3-X-PROP.
- I1: B03 -> 6x LP11055E + 6x LP11055EP $4.17 ea ($50.04); delete B04 (-$16.89); add M6 thin nut A4 50-pack $9.59 (Zoro) or in Amazon cart.
- B1/E2: re-run with cruise 268 W, hover 27.6 A/409 W.
- C1: thrust basis 1.349 kg/motor.
- F1: T-F1-SENSOR-CAL +/-1.1 %; path R allow 19.37 mOhm, drop 9.58 %.
- H1: stand pass >= 1316 gf fresh at limiter (pred 1367); >= 1053 gf @11.9 V (pred 1141); phase <= 25 A (24.19); accept motors 77.4-94.6 mOhm @25 C.
- Unknown: E blade coning; envelope carried from MR; measure first station.
## From H2 (H2.md, plan R2): racetrack straight set from wind (0..5 m/s: 300,270,250,220,190,150 m); gate 5 tune: K09-L cannot hand-launch.
- A1 DECISION (D-162): R-TEST-ORDER: gate 5 fixed-wing tune flown from vertical take-off after gates 6-7 (hand-launch tune stays on the twin, DECISION 5.3). Racetrack straight per wind table. Transition start 50 m (fence top 99.5 m, FENCE_MARGIN only notifies).
- A2: CL-C5-LANDINGS-PER-CARTRIDGE limit 5 -> 2 touchdowns per sortie (H2), C5 re-run; A2 requirements.json re-word R-TEST-ORDER and racetrack.
- I2: tight February mornings (F01 0.1, F02 0.7 spare), crew of 4.
- H3: wind-set racetrack straight on flight card.
## From A3 (A3.md closure): harness plugs re-armed (+13.9 g basic); E/EP booked; caps2 + saddles booked. Gate 2.60: margin 19.6 (no lead) FAIL, pack accept 485.6 FAIL; lead D-121 37.9 g.
- D-163 APPLIED: power 635, harness 144, reserve 139 (sum 2461).
- Levers: L6 one cap per ESC (F1 ripple) +14.4 g; L2 through-core block 2 perimeters 10 % gyroid (C4, C2, D3) +15.7 g; L5 spar 880 mm (C2, C5, D1) +15.2 g; L4 Ti screws (C6, I1) +7.2 g +$58.80.
- Forward moves: GPS+mast to nose (F3, D2); servos 50 mm fwd (D6, D1); ESC pads 40 mm fwd (D3, F2): each g.m forward cuts lead 5.5 g.
- Pending: E2 smaller pack at E/EP power; B3 D-121 lead re-derivation + chamfer AVL; C5 gate 2.65 landing.
- F2: republish plug masses in parts.csv; flag 60 mm factory lead assumption.
- A3 next: first-flight mass case in mass_rollup.py; frame_claims.py; mass_budget.json propulsion 462 -> 486.
## From E2 (D-163 pack): at E/EP power min pack 5.8 Ah; BATT_LOW_MAH now 3000 (replaces 3100; F4, H3).
- Gens Ace Redline 4S 6000 130C HV 447/448 +/-10 g, $127.99 ea (+$165.65 for 2): passes 485.6 line (+23.6). LiHV: charge 4.35 V (charger LiHV mode unknown), T-E2-IR <= 4.3 mOhm/cell, hot landing temp exactly 50.0 C (fragile), 17.4 V full: E1/F1/F4 check; pack +4 mm long (C5 stack margin).
- CNHL LiHV 4S 6000 120C EC5 ~479 g (tol unknown) 10 AWG $69.99 ea (+$49.65): fails 485.6 by 3.4 at +/-10; passes if gate 2.65.
- Keep bay 160x52x53; 12 mm foam spacer (book 5 g).
- A1 DECISION PENDING: pack choice depends on gate (C5 2.65), lead (B3), budget.
## From C4 (C4.md): 4 claims re-classed to info (J6); knock-down sep 0.189 -> 0.2045 with cheeks +1.5 mm (R7), +10.1 g, $0.
- D3 R7: fin_detail.mount.cheek_t_m 0.0025 -> 0.0040, cheek_in_t_m 0.0024 -> 0.0039, outward only (inner faces 11.5/12.1 mm); same on 10 deg spares; publish FIN-003 mass/CG (~14.2 g); F2 re-check phase-lead route (outboard cheek face +1.5 mm).
- A1: fins alloc 477 -> 487; tube e/g notes (knock-down gated by CL-C4-SIM-SEP-KNOCK, GT-16 confirmation).
- A2: R-VIBRATION text + cruise re-run trigger 6371 rpm (pending E/EP cruise rpm check).
- H1: GT-16 E >= 78.6, G >= 10.27 GPa; T-C4-MOUNT-STIFF >= 2548 N.m/rad.
- C4 follow-up after D3 R7: ASM-C4-MOUNT-K-ROCK 3100, re-run. ASKED: E/EP rpm re-check + cheaper tube.
- E1 D-161b: voltage-scheduled spin cap min(0.93, 11.2/Vbus) via Lua (F4 implementing).
## From F4 (F4.md, K09L.param F4-R8): no F4 fails. THR_MAX 60 kept (VH), Q_ASSIST_ALT/ANGLE 0 kept (C1 bypass), BATT_FS_LOW_ACT 6, Q_A_ANGLE_BOOST 0, INS_HNTCH_HMNCS 3, BATT_LOW_MAH 3100 (E2 now says 3000 -> F4 update), Q_M_BAT_CURR_MAX 73.2, Q_M_SPIN_MAX held 0.84 (CL-B4-SPIN-LIMITER-LOW fails).
- D-161b blocked on CoreWing F405 (no Lua). A1 DECISION: option C, H7 FC with Lua -> F3 evaluating.
- C1 re-run loads.py; B4 publish VH output 0.611 + sagged level speed claims; F5 transition switch + FW mode latch; H3: "on BATT_LOW in FW select RTL" + other lines; B1 FW climb at 60 %; J1 notch harmonics; J6/B3 accept fence residual (fence breach in hover -> RTL pitches over; bounded 0.848).
- F4 ran git diff --stat read-only (rule slip).
## From F5 (F5.md): transition switch done, SITL logic passes, 0 F5 fails.
- F4 CR-F5-15: FLTMODE1-6 = 17,5,7,18,11,19; RC6/7/10-12_OPTION 0 stated; RC3_MIN 988 / MAX 2012 / DZ 30 / TRIM 988 (do not recalibrate RC3); state Q_THROTTLE_EXPO 0.2, HOVER_LEARN 2, ANGLE_BOOST 0; drop 0.65 comment.
- F4 CR-F5-16: SPEC, TUNING-PLAN step 7, SITL S1b pulses 1167/1295/1423/1556/1684/1817, S4c via transition_sitl.py with pass lines.
- B3: reword ASM-B3-TRANS-REALISE (whole-percent stick); check pre-climb hold up to 2.38 s (climb, w0 ~9.1 m/s) else F5 L06 1.8 s.
- H2/H3 CR-F5-17: theta_h procedure, transition >= 50 m, SB untouched until FW done, switch warnings SA/SC/SD.
- F4 also: BATT_LOW_MAH 3000 (E2 D-163 update).
## From F3 (F3.md): only Holybro Kakute H743-Wing works for option C. +$39.15 (Holybro direct $105, snippet) / +$79.33 (ReadyMadeRC $141.44 in stock). Mass -9.1 g (pess +7.5). Single IMU; servo BEC 6 A vs 5.6 A (7 %). Board on deck seat (left channel) replacing PDB; FC tray retired.
- A1 DECISION D-161c (provisional): option C, Kakute H743-Wing, Lua voltage-scheduled spin cap; CONDITION: F4 proves the Lua cap + hover learning in SITL (scripting runs in SITL) before batch 2b drawing. If it fails -> option A/B.
- F3: update avionics params + avionics.py/avn_data.py. D2: retire FC tray keys, deck seat 45x30x13.5 on 4 gel cubes 7.6 mm, strap, USB-C extender. F2: delete W-PMOD, E-HRN-22/23, re-end E-HRN-24..29 left channel, GPS/airspeed ports, RX full duplex serial, servo V recompute (26 AWG?). F1: delete PWR-003, main path 10 AWG via board pads, servo BEC claim 6 A, BOARD-CHECK step 7. F4: KakuteH7-Wing target, SERIAL port, single IMU offset (-0.038,-0.046,0.050), current scale cal. I1: A01 -> Kakute $115.76/$155.94, withdraw SpeedyBee, avoid lookalike sites. A3: -9.1 g, CG +0.18 x / -0.30 y mm.
## From B3 (D-163): yaw CDMAX 1.494 FAIL at 9 deg w/ E props -> 10 deg 1.618. Turbulator (zigzag upper x/c 0.05) -> lead 0 g, cruise +25 W (+9.7 %) EST, ~1 g; without: lead 35.5 g (42.7 w/ margin). Chamfers AVL OK; fwd CG limit 0.04295.
- D-164 APPLIED: cant 10, cg.x_range [0.0430,0.0501], wing.elevon.te_chamfer_m [0.02,0.07]. Max mass at 10 deg = 2.643 kg (E1).
- D3: face_ahead 14.0 mm (fins params) + C6 key 7x2 + C4 cheeks +1.5 + E hub stack +0.76 mm; publish X-PROP/X-FACE at 10 deg.
- B4, C4, C1, C6, D3 re-run at 10 deg (B4 outboard chamfer up to 96 mm; wake clearance ~+1.8 mm EST).
- F4: Q_M_SPIN_MAX >= 0.90 needed for transition window (now scheduled cap: fresh 0.746 -> check B3 window at fresh pack!).
- PENDING A1 TRADE (turbulator vs lead x pack x gate): A3 mass + E2 mission + B1 cruise drag (dcd +0.0067) + B2 XFOIL tripped.
## From F4 (D-161c, K09L.param R9): Lua spin cap passes SITL (cap tracks 11.2/V, hover learn +3.5 %, alt hold ok, never above cap, fault -> 0.746 + arming refused). Q_M_BAT_VOLT_MAX 16.8 -> 0. BATT_LOW 3000, FLTMODE order, RC3, Kakute settings (BRD_ALT_CONFIG 1, SERIAL6 23, SERIAL3 5, BATT_VOLT_MULT 18.18, AMP_PERVLT 36.6, single IMU INS_POS1 (0.087,-0.046,-0.0315)).
- A1 DECISION D-161c CONFIRMED: Kakute H743-Wing + Lua spin cap. SD card with script = flight item.
- E1: confirm fault value 0.746 (fresh pack single saturated motor > 25 A at >0.720; low pack T/W ~1.13) vs hold-last-good; size frozen-cap (script crash) case.
- B4: CL-B4-SPIN-LIMITER-LOW compare vs scheduled cap at pack state (0.931 @3.60 V/cell vs 0.895).
- B3: transition window with scheduled cap at fresh pack (0.746) and all voltages.
- H3: card line "SPINCAP fault or any Scripting message -> land".
- F1: T-F1-SENSOR-CAL covers voltage too.
## From C1 re-run: all pass except T-CAP -> D-166 APPLIED thrust_limit_per_motor_n 22.1 N.
- B4: re-run RPMFULL on THR_MAX 60, Lua cap, 10 deg, 2.64 kg; flag if > 10 305 rpm.
- C4, C6, D3: re-read C1 data (joints.csv, envelope.json) at 22.03 N.
## From E1 D-165: all pass at 10 deg / 2.64 / 73.2 once D3 writes face_ahead 0.014. MTOW-TW-MAX 2.643. D-165b APPLIED hover 28.4 A / 420 W, cruise 269 W / 18.2 A, thrust 1.350.
- F4: Lua fault value = latched OCV bound min(0.93, 11.2/V_oc_hi), V_oc_hi = min(V_oc_hi, V_f + I_f*0.040); boot/saved Q_M_SPIN_MAX 0.667; asymmetric filter (rise instant, fall filtered); log V_oc_hi; SITL fault after climb; fsw.spin_cap_boot 0.667, fsw.spin_cap_rb_ohm 0.040.
- D3: face_ahead_m 0.014, prop_stack_m 0.03806.
- H2/H3 card: "SPINCAP fault or any Scripting message: QLAND, no go-around, no full-throttle climb".
## From C6 at 10 deg (C6.md 6): R1 7 mm dog RF 1.04 withdrawn; new 10 mm sector dog (arc at r 12.0 mm, r 11.2-12.8, 47.7 deg, centred -x), key_d 2.5 mm, RF 1.612; notch 49.6 deg sector floor 2.7 mm; fins.py code change box->sector; same on spares. Fuse torque 3.71 -> 6.55 N.m (downstream bond RF 5.16).
- A1 DECISION: C1 takes 6.55 N.m and re-runs P1 with all downstream structures (C4 tube/mount, C2 spar) -> CL-C1-P1-FUSE-MATCH; C4 re-run CL-C4-D3-MOUNT-TWIST at 10 deg / 14 mm.
## From C1 (P1 6.55): 0 fails; P1 governs only at the fuse; C2/C4 no new loads. C6 must publish DOG-FUSE-T <= 6.55.
## From D2 (D2.md): Kakute seat (fc_seat_m), FC tray keys RETIRED (delete after F2/F3 stop reading), usb_spot_m, hatch_low(), pack_spacer_m [0,0.139,0.047] (12 mm spacer +5.0 g if D-163 pack). Pod 144.8 g (-2.5). All 44 limited claims pass.
- pod_data.py exit 1 from C6 fastener hook: TRN-102-C not built by transport CAD (D7 running?) -> check in gates.
- F2: stop reading fc_centre_x_m/fc_board_m (FC centre (-0.038,-0.0464)); right-channel JR tie bar still needed?; USB cable off strap slots.
- F1: two deck slots in PWR-006. A3: pod mass/CG. E3: FC temperature at deck station.
- If D-163 pack (139 mm): pod.pack_aft_travel_m 0.014 at -0.036 datum; fwd pack centroid -0.0382 -> -0.0362.
## From D7: box 1.25 x 0.565 x 0.54, box lines $158.69 -> $39.02 (cardboard moving-box panels, tape, paracord, PE foam). D-167 APPLIED box_external, envelope 0.520, box mass 3.48.
- I1: re-price T01 (4 x HD XLBX $3.48), T02 tape $4.30/5.51, T03 delete, T06 Walmart PE foam $11.38/15.96, T04 drop M3 ($12.00); G18 paracord spare 5.2 m.
- C6: delete TRN-102 in fastener_parts.py and E-TRN-13..15 in joint_stacks.json (fixes pod_data.py exit 1).
- J6: deleted handle claims (CL-D7-HANDLE-*).
- CLAUDE.md box text (0.55 x 0.45) vs 0.565 x 0.54: tell the user; height cannot reach 0.45 without re-deriving the 0.3 m drop.
## From F3 (D-161c applied): avionics 52.08 g; allocations APPLIED avionics 53, power 612, harness 142; flight_controller text -> Kakute.
- F2: delete W-PMOD, E-HRN-22/23; re-end cables at F3 points (GPS (-0.0636,-0.0560,0.0473); I2C/airspeed (-0.0636,-0.0365,0.0473), sensor end (-0.0600,-0.0464,0.0256); UART6 (-0.0465,-0.0604,0.0457); USB (-0.0536,-0.0588,0.0477); extender (-0.0380,-0.0617,0.0636); M1-M6 field (-0.0338,-0.0579,0.0452), M1 x -0.0275 then +2.54 mm fwd, rows y -0.06035/-0.05781/-0.05527); airspeed cable ahead of deck front x -0.066; CL-F2-SERVO-V without link drop.
- F1: delete PWR-003 + foam pad + W-PMOD header; cut D2 deck slots; pads BAT-IN +/- (-0.0185,-0.0590/-0.0545,0.0467), BAT-OUT -/+ (-0.0185,-0.0383/-0.0338,0.0467); 10 AWG S-loops; BEC 6 A; BOARD-CHECK.
- F4: ARSPD_BUS 0 -> 2; INS_POS1_Z -0.032.
- D2: ack E-AVN-11; keep z <= 0.050 clear at x -0.076..-0.066.
- E3: CL-E3-FC-PEAK with Kakute 2.83 W. I1: A01 Kakute; spare microSD.
- J6: CL-F3-FC-DISS re-classed info (temp claim replaces).
## From B2: upper trip fails; lower zigzag x/c 0.20 0.7 mm passes; +14 W (+5.3 %) upper bound; stall 12.13, 1.3Vs 15.76; DPROP-DRIFT passes; root bending 10.68 N.m AVL / 11.70 Schrenk (C1/C2).
- D-168 APPLIED wing.turbulator (lower 0.20). D-121 lead retired. Pack provisional: CNHL LiHV 4S 6000 120C EC5 (E2 + A3 to confirm).
- B3 re-read tripped slope from B2 b20 case; B1/E2 +14 W; D1 tape line x 0.064 lower skin vs D-153 doubler; H2 tuft check; A3 tape 5 g, drop lead.
## From F1: L6 NO; caps -> 3 x Rubycon 35PJV560M10X16.5 per ESC (ripple); D-169 APPLIED power 621, r_ext 8.4. CL-F2 DROP-CONT thin 1.95 vs 2.0.
- F2: re-end W-MAIN-1/2 on AVN-001 (0.060/0.080 m, S-loops), fix lap joints off PWR-003, delete W-PMOD/E-HRN-23, drop ASM-F1-PMOD-CONDUCTORS from SERVO-V, 3 caps per ESC legs <= 20 mm, CALC-F2-CAP-RIPPLE winding-current formula.
- A3: retire PWR-A3-CAPS2 (now PWR-009), book PWR-010 +8.8 g x~0.147, S-loops +7.2.
- I1: F07 13 x Rubycon $3.03 ($43.43 incl tax, +$38), 22 wk standard lead -> order early; check maker freq multiplier at 48 kHz (>= 0.86 -> 9 caps).
- F4 Bluejay 48 kHz + BATT cal; E3 ESC losses 48 kHz; D3/D2 cap placement; E1 burst at 17.4 V.
- A1 FIXED: C6 TRN-102 fastener block + E-TRN-13..15 stacks removed (handles retired D-167); transport regenerated; fastener hook OK. Other subsystems' parts/interfaces rewritten by the hook at 17:35 -> gates will show.
- F1 POWER.md / SUMMARY.md still CoreWing (J5 doc cleanup).
## From A3 (D-168 re-book): CNHL 6000 at 2.64: gate margin 96.9 (86.9 heavy) PASS, pack accept 491.9 vs 489 (+2.9 thin) PASS, CG 0.05327 vs 0.0501 aft FAIL (-3.53 mm). Ovonic fails mass; Gens Ace CG -4.49.
- D-170 APPLIED allocations wing 396, fins 487, pod 150, landing 77, power 552 (CNHL pack), harness 146; reserve 219 (needs 214.4).
- D-170 DECISION: pack centroid >= 19 mm forward (to <= -0.055) via bay re-datum + minimal nose extension (D2 working). Then C3 crash block, C5 pack stack margin, D7 box nose gap (fore-aft +up to 19 mm -> box 0.585?, car door >= 0.605), B3 CG/NP.
- L2 lever approved: through-core block 2 perimeters 10 % gyroid (+15.7 g): C4 + C2 confirm, D3 prints.
- Pending: battery.mass_kg 0.479, size [0.139,0.047,0.037] when E2 confirms CNHL.
- mass_budget.json stale -> frame_claims.py in gates.
## From C4 (D-161/D-164 section): with 11x5.5E at 10/14 no cheek passes (page 0.192, knock 0.123 at +1.5). Options: A) prop/rpm cruise <= 6016 rpm (cheeks 4.0/3.9, +11.1 g); B) tube 35045-S +113.7 g, $51-68 (rejected, mass).
- A1 DECISION D-171 (pending E1): higher-pitch APC E prop for cruise <= 6016 rpm; E1 leading; then B4, C4 3-mesh, B3, E2, A3, I1.
- CL-C4-D3-MOUNT-TWIST 0.4045 N.m at 10/14 (C6). All strength margins pass at 22.03 N.
- A2/F4: 2P at full throttle 324.5-342.9 Hz on station mode 335-386 Hz (info) -> notch covers 2P to 343 Hz?
- RW 35046-S 36 in min $118.97 vs 48 in $151.96 (-$33, no spare tube) -> I1 option.
- C4 claims.d3/sim stale until D3 publishes 10/14 + prop picked.
## From E2 (D-168): CNHL 6000 FAILS (12 AWG leads, out of stock). Gens Ace 6000 HV passes all: 462 g worst, 3.97 min (3.59 at 3.70 V), touchdown 1207-1212 vs 1200, hot temp 49.7 C at IR <= 4.2 mOhm/cell. BATT_LOW 2900 / CRT 1200 with Gens Ace. +$165.65. HTRC C150 lists LiHV 1-6S (4.35 V not confirmed).
- A1: pack provisional Gens Ace, but HOLD params until E1 D-171 prop (cruise power changes) and budget closure.
- BUDGET ALARM: all-new est. ~ +$389 - $203 (I1 requests incl box) + Kakute $39-79 + caps $38 + Gens Ace $166 + microSD ~$20 -> roughly +$450 over $2,000. Needs a full I1 budget round with design alternatives after D-171.
## From D5: foot drawn; FLANGE-SF 1.111, TINE 1.212, tip-over 30.58, rim 1.259; mass 79.50 g. D-172 APPLIED landing 80, envelope [1.152,0.520,0.442], tipover note; reserve 216 (vs need 214.4).
- D3: fin step front x 0.2510, |z| 0.2030, depth 7.0 mm. C4: shoe back wall x 0.2512, legs |z| 0.1732, 69 mm. C5: re-run with pads +/-0.221 and lip 78.7 N. A3/B3: CG re-roll. D7: envelope height 0.442 (box slack 73 mm).
## From D2 (D-170): pack to -0.056 needs nose +20 mm (x_le -0.167, size [0.262,0.14,0.07]), pod +9.6 g (154.4), staged overlay team/D2/d170_overlay.json; Ovonic fallback still fits (params swap).
- HELD by A1: CNHL rejected (E2), Gens Ace (448 g) needs >= 26 mm (A3) -> pack choice + budget first, after E1 D-171.
- If applied: pod.pack_x_nominal_m -0.056, pack_aft_travel 0.034, pitot tip x -0.247, pod alloc 155; C3 hatch tab ~2.45 vs 2.5 thin; C5 crush stack (31.0 floor could drop to ~24 mm for a 479 g pack -> nose 7 mm shorter); D7 nose pad -0.1793 box gap; B3 CG/NP; F2 lead +18 mm; H3 spacer.
## From E1 D-171: no 11-in E prop passes with X3108S (torque-limited at 25 A). 11x6E/EP don't exist; 11x7E no EP; 11x8E/EP: cruise 4899 rpm, 205.7 W (-22 %) but T/W 1.844 band edge.
- A1 DECISION D-173 (direction): bigger motor (>= 0.305 N.m continuous) + 11x8E/EP; E1 searching. Knock-ons: maybe drop Lua/Kakute (revert CoreWing), maybe cheap 22x20 tube (C4), smaller/cheaper pack (E2), mount (D3), mass/gate (A3), hover current band (A2), budget (I1).
- 5.5E stays the design of record until D-173 lands.
## D-173 APPLIED: X2814 V3 KV900 + APC 11x8E/EP, limiter 75 A, Q_M_SPIN_MAX fixed 0.81, propulsion 594 g, reserve 108 (need 214) -> pack/gate to close. D-173b: back to CoreWing (Lua/Kakute withdrawn).
- In flight: E1 (switch propulsion.py, gate sweep 75/80/85 A, prop adapter, face_ahead), E2 (lightest/cheapest LiPo at 205+14 W), C4 (cheap 22x20 tube?), F4 (revert Lua, 0.81, 75 A), F3 (revert to CoreWing), C2 (wing).
- Then: A3 re-book + CG (motors forward help aft CG; D-170 nose may be unnecessary), D2 restore FC tray if CoreWing, D3 (mount 19x25 M3, can 36 mm, cheeks/tube per C4, dog per C6 10 mm sector, foot step per D5, face_ahead per E1), B3/B4/B1/C1/C6/F1/F2/I1 re-runs, budget round.
- Superseded: D-161 prop (5.5E) and D-161b/c (Lua, Kakute); D2 D-170 overlay held.
## From E2 D-173 pack: no 4S LiPo passes (>= 5.7 Ah needed; hover sets capacity, BATT_LOW landing need ~1.9 Ah). Lightest pass: Gens Ace Redline Shorty 6000 HV (GEA60004S13S) 410+/-10 g, 98x47x46, $127.99-131.99, 4.66 min, 48.6 C at IR <= 3.8 mOhm/group; BATT_LOW 3000 / CRT 1200. Needs A3 pack line >= 424 g (est. line ~390 after D-173 -> short ~34 g). +$166-174.
- A1 thinking: raise gate (E1 sweep 80/85 A; C5 OK to ~2.84 with new foot; B2 re-derive stall_max from 17 m/s transition; C1/C2 loads) -> gate ~2.68-2.70 closes the Shorty line. Wait for E1 + C4 + A3.
- E1: replace thrust table with X2814/11x8E rows; re-run 17 m/s cruise claim. C5: crush stack with 98 mm pack.
## D-174 APPLIED: limiter 80 A, gate 2.70 kg, pack Gens Ace Shorty 6000 HV (0.414 kg, [0.098,0.047,0.046], 6.0 Ah, 15.2 V, 91.2 Wh), fsw.q_m_spin_max 0.81, hover 29.2 A / 431 W; reserve 162 (power alloc still has old pack -> A3 re-book).
- From E1 rev 12: 0 fails at 75 A; face_ahead 14 -> 4.0 mm recommended, prop_stack 0.0477, mount 4 x M3 on 19/25 mm, plate >= 4.5 mm; motor-screw engagement zero margin (3.0 mm holes); prop adapter M6 post LH on CW motors (UR, LL); E1 re-run at 80 A pending.
- From F4 R10: THR_MAX 42 + FWD_BAT_VOLT compensation (11x8E level speed); Q_M_BAT_VOLT_MAX 16.8/13.2; Lua removed, CoreWing restored; BATT_LOW 3200 (pre-pack). Asked: D-174 (80 A, LiHV, BATT_LOW 3000/1200, THR_MAX 41).
- F1: XT30U pairs at 80 A (40 A per pair) -> asked.
- B3: re-run band edges (fraction 0.788), Q_TAILSIT_THR_VT 55 vs hover ~0.45; B4: confirm 0.429 (CR-F4-54); B1: climb (CR-F4-56).
- J6: deleted F4 SPINCAP claims/tests, CL-F4-FW-RPM-CAP.
## From F4 R11 (D-174): Q_M_BAT_CURR_MAX 80, Q_M_BAT_VOLT_MAX 17.4, FWD_BAT_VOLT_MAX 17.4, THR_MAX 41 (level fresh 21.24-21.53 vs VH 21.76, 1 %), BATT_LOW 3000/CRT 1200, BATT_CAPACITY 5520, BATT_LOW_VOLT 14.4/CRT 14.0, ARM 17.0 (EST, E2 confirm). CL-F4-BATT-LOW fails until E2 re-runs on the Shorty (CR-F4-59). FW climb sagged ~2.9 vs TECS_CLMB_MAX 3 (B1).
- E1: publish T/W at 2.70 kg / 80 A; B3 band edges (fraction ~0.778).
## From F1 D-173: CoreWing restored; XT60H one per ESC (+21.2 g harness, -$1); 3 x Rubycon 35PZJ560M10X15 per ESC (13 x $2.83, 22 wk lead); power non-pack 91.5 g.
- D-175 APPLIED: power alloc 506 (91.5 + Shorty 414), current_max_per_motor 20.0, r_ext 10.3, wire_temp_rise_max 16 K.
- F2: XT60H at pod exits (side-exit fit), restore W-PMOD + E-HRN-22/23, 3 caps per ESC legs <= 20 mm, ripple calc winding current. A3: harness +21.2, power non-pack 91.5, retire PWR-A3-CAPS2. I1: XT60H $8.99; 13 x 35PZJ560M10X15. F4: Bluejay 48 kHz.
- check.py now: pod + avionics FAIL to build (pack_aft_face vs Shorty) -> D2 re-datum (sent). FIN-002 in KO-PROP 24.1 mm -> D3 face_ahead 4 mm (D3 launched).
## From D2 D-174: Shorty re-datum; D-176 APPLIED pack_x_nominal -0.0545, aft_travel 0.010, pod alloc 147. D-170 nose superseded (not needed). POD-013 aft filler; 12 mm spacer not wanted; aft strap -0.045.
- A3 Shorty stations/CG; C3/C5 filler load path (179 N vs 85 N); F1/F2 pack aft face -0.0055, aft strap -0.045; H3 filler pieces, stack blue 8 + white 2; J6 CL-D2-KO-PWR reclass (case U info).
## From C4 D-173: RW tube passes with face_ahead 4.0, cheeks 5.5/5.4, cheek_len 13.5 (sep 0.269 / 0.208 knock); cheap tube fails all. +4.0 g. Notch must track 2P to 265 Hz (A2/F4); VIBE test at full throttle.
## From D3 R8 (Sonnet): mount drawn; cheek inner faces moved to 13.4/14.3 mm (washers at 25 mm pattern) -> C4 MUST RE-CHECK stiffness; plate 0.0200 x 0.0163; FIN-003 16.24 g; fins 479.7 g (L2 block fill 0.449, -13.8 g, pending C4/C2). D-177 APPLIED x_prop -0.01918, x_face 0.0278.
- Launched (Sonnet): E1 propulsion CAD -> X2814 geometry (clears KO-PROP); C6 screw engagement 2.5 mm strip calc.
- Pending: C2 (wing), then grouped re-runs.
## C6: M3 2.5 mm in motor base passes (pull-out 4.12, strike 3.36). D-178 APPLIED requirements.thread_engagement_motor_m3_min_m 0.0025. D3: CL-D3-SCREW-ENGAGE must read it; fins params need the 2 x 0.5 mm washers (C6 STRIP-RF / CANT-ENGAGE still read 3.5 mm).
## E1 (Sonnet): propulsion CAD -> X2814 (KO-PROP cleared); E1 claims at 80 A / 2.70 / 17.4 V: 0 FAIL. A1 kept Q_M_SPIN_MAX 0.81 (tested: winding 46.07 A +8 %, ESC 37.35 +17 %, TW fresh 2.096, worst 1.771). E1 had proposed 0.85 (1 % margin) -> rejected. A1 synced CT-PROP-ADAPTER library spec (3 x M2.5 on 15 mm).
## C6 (Sonnet): E-FIN-61..64 stacks min 2.5 mm; all motor screw claims pass.
- NEXT: wait C2; then grouped re-run batches (Sonnet/Haiku): B1/B2/B3/B4 aero+S&C; C1/C2/C3/C4/C5 structures; E2/F2/F1 elec; A3 mass/CG (check.py total CG 0.058!); H1/H2/H3/I1/I2 programme; D1 wing (chamfers, turbulator, C2 asks).
## From C2: all 5 fails closed. RING-NO-PLUG / RING-ANCHOR / CUTOUT-SENS / FILLET-SENS re-classed (J6); GCI 0.0342 pass (volume percentile). DESIGN D-179: fin root bond-break (release film) from x 0.22 to TE under all 4 roots (D3 key fin_detail.fin.root_fillet.release_x_m 0.22; 4 film bodies 100 x 45 x 0.13 mm; +4.9 g). C2 proposed PTFE tape Uline S-14538 $60 -> A1: find cheaper release film (I1/D3).
- C4: re-check modes/SEP with root bonded only x < 0.22 (open risk; fully free root 150-162 Hz) + D3 R8 cheek inner faces 13.4/14.3; reissue fillet_share_table -> C2 re-run if needed.
- D1: BUILD step 10 note. A1: commit C2 fea split files (c2cl_split_reduce.py, data/c2cl_split.json, out/blk_L{1,2,3}O.json, fea_report.json). C1 wing_spanwise reissue -> C2 FE 4 h (avoid unless loads move > 2 %).
