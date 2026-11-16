# Real content copied from redesign/site/app.html (read 2026-11-16).
MASS = [("propulsion",353),("power",279),("wing",222),("cage",119),("fins",110),("avionics",65),
        ("mechanisms",48),("harness",33),("assembly",26),("wiring",14),("landing",8.4)]
PHASES = [
 ("01","Re-study and selection","done","Re-study 2026-11-14, QP-1 sizing of A, B, T, D2; J6 board picks A","D-182"),
 ("02","Sizing and SITL","done","QP-2: wind, bench plan, baseline","D-183, D-184"),
 ("03","Pre-order validation","done","QP-3: SITL flight, structures, cost and schedule, CAD through the 3-D gates","D-185, D-186"),
 ("04","Fixes and board re-sit","done","QP-4: elevon balance and hinge damper, caps and stops. Order 1 YES, main order NOT YET","D-187, D-188"),
 ("05","Claims and real-shape CAD","done","QP-5: claims cleared, CAD to vendor geometry, analyses on it, hub walls, arms and motor cups","D-189 to D-197"),
 ("06","Enclosed wiring","partial","C8: phase leads enclosed from motor to ESC; exposed wire 9.09 to 0.87 strand-m; pitot tube run not designed","D-199"),
 ("07","Order 1 and bench","todo","Bench kit early December: thrust, current, yaw (M1 to M4), elevon coupon, weigh-in","by 4 Dec"),
 ("08","Main order","todo","Gates G1 to G9 (QP-4 board s4); latest safe date 28 Dec","28 Dec"),
 ("09","Build and tethered hover","todo","January to February; lifeboat (ZOHD Altus) if no tethered hover","15 Feb 2027"),
 ("10","Flight test","todo","Transition round trip and the mission profile","30 Apr 2027"),
]
STATE = {"done":"Done","partial":"Partial","todo":"Not started"}
ISSUES = [
 ("1","Exposed wiring (hard constraint C8)","After D-199, 0.87 strand-m are still outside the skin (was 9.09; 0.60 without the vendor pack leads). Left: vendor pack leads and battery tail to the cover slot, short RX / airspeed / servo lead stubs, and the pitot silicone tube, not designed (0.45 m, needs a foam groove across the spar).","harness, CAD","CLAUDE.md C8; HARNESS-ENCLOSED.md s5","Open"),
 ("2","Hub arm-socket wall","2.0 mm over the 12 mm mouth: the rough hoop check passes only with a 12 mm bearing patch (MS +0.05; -0.47 at 6 mm).","structures, bench","ASM-A-HUB-WALL, D-196; qp5_checks.md s2","Unverified"),
 ("3","Mass has about 4 g of room","Predicted 1,455.6 g against the 1.46 kg target (weigh-in gate 1.47 kg) after D-198; the estimated cuts must prove real at the weigh-in.","mass (A3)","CL-A-MASS-PRED, CL-A-CUTS-REQUIRED; MASS-GATE.md s11","Unverified"),
 ("4","Elevon flutter","Cleared only with the silicone-fluid hinge damper (lowest onset 38.5 m/s hot against the 28.8 m/s line); the coupon must show K >= 2, free play <= 0.5 deg, damping >= 1 %.","structures (C1, C2)","G8, D-188; flutter_d195.md","Unverified"),
 ("5","Gusty hover heading","Excursion 25.4 deg in one of seven turbulence seeds (8.5 to 14.0 deg in the rest); flown with the pilot holding heading.","flight controls","A-P8a; QP-5/ANALYSES.md","Marginal"),
]
BOM = [
 ("P01","T-Motor MN2212 V2.0 KV780 (4 + 1 spare)","propulsion","T-Motor",5,46.90,"V","Order 1","2026-11-14"),
 ("P02","APC 9x4.5MR 4-pack (2 standard + 2 reverse rotation)","propulsion","RMRC",1,9.40,"V","Order 1","2026-11-14"),
 ("P04","SpeedyBee BLS 35A Mini V2 4-in-1 ESC 20x20 (DShot300/600)","propulsion","RMRC",1,45.66,"V","Order 1","2026-11-14"),
 ("W01","Tattu 2300 mAh 4S 75C XT60 270 g (2 flight packs)","power","RMRC",2,37.09,"V","Order 1","2026-11-14"),
 ("W02","ToolkitRC M6AC charger","power","RMRC",1,63.71,"V","Order 1","2026-11-14"),
 ("W03","TBS LiPo bag","power","RMRC",2,7.61,"V","Order 1","2026-11-14"),
 ("W04","Metal ammo can (pack storage)","power","Local",1,13.99,"V","Order 1","2026-11-14"),
 ("W05","Wire 14 AWG silicone, XT60 5-pair, heat shrink","power","RMRC",1,19.94,"V","Order 1","2026-11-15"),
 ("W06","Threadlocker","power","Local",1,6.00,"EST","Order 1","-"),
 ("W07","Wire 20 AWG silicone: phase-lead extension","power","RMRC",1,3.96,"V","Main","2026-11-15"),
 ("W08","Battery strap 20 x 300 mm (2 pcs)","power","RMRC",1,1.99,"V","Main","2026-11-15"),
 ("W09","Anti-slip pad: silicone rubber sheet 1 mm","power","Amazon",1,2.00,"EST","Main","-"),
]
GROUPS = [("propulsion",319.24),("avionics",304.07),("airframe",273.36),("power",221.59),("ground test",217.46),("mechanisms",56.18)]
def money(x): return "${:,.2f}".format(x)
