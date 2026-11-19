"""a_build_steps.py - the build-guide content of concept A, one record per step of a_assembly_plan.STEPS (same ids, same order as the
film stages in showcase/concept-a/render_build_a.py). PURE DATA (no imports): read by
    qp/A/make_build_guide_a.py   -> qp/A/BUILD-GUIDE-A.md  (the written guide, generated so that guide and film never drift)
    showcase/concept-a/render_build_a.py   -> the cards, callouts and fabrication beats of the build film (also runs inside Blender).

Labels: every number is either from the CAD (qp/A/cad/amodel/*.py, part masses from a_model.PARTS), BOM-A.csv, MASS-GATE.md,
review/QP-5/ARMS.md, review/QP-5/HARNESS-ENCLOSED.md, review/QP-4/FIXES2.md, or the K09-L BUILD-GUIDE.md (process practice, such as 24 h epoxy
cures: labelled "K09-L practice"), or it is marked EST. "-" means not in the repo.
Per step:
  id, title            step id of a_assembly_plan and a short title
  line                 the one-line instruction on the film card (<= 100 characters)
  tools                key tools / consumables for the card (<= 80 characters)
  check                the key check for the card (<= 92 characters)
  min                  hands-on time, minutes, EST (machine time such as printing is listed apart, see PRINT)
  cure                 dwell / cure after the step ('' = none)
  need                 extra consumables and tools for the guide (parts come from the plan and BOM-A automatically)
  make                 how to make the part(s) before fitting (guide)
  fit                  how to fit (guide)
  checks               checkpoints: measure, weigh, dry-fit, continuity, polarity (guide)
  safety               safety notes (guide)
  fab                  film make-it beat: dict(kind='tube'|'print'|'core'|'cut'|'lead'|'make'|'fit'|'thread'|'solder', pid, text, dims=[(part id, label)], orient='print orientation')
                       (kind 'thread' / 'solder' is not a separate beat: its text is the banner during the marker step's motion)
  chip                 optional banner dict(kind='thread', text) for the motion phase of a marker step that also has a make-it beat (B0)
  ghost                part ids the film draws see-through (x-ray) from the step card to the end of the step, so that a part hidden inside them
                       (a plug inside the spar) is visible; the moving / fitted parts of the step stay opaque. Restored after the step.
  callouts             film labels with leader lines: (target, label) with target = part id, wire edge id or ('pt', (x, y, z) in m, CAD frame)
  hold                 True = the film shows a checkpoint card after the step; cp = the card text (list of short lines)
"""

# ---------------------------------------------------------------------------------------------------------- common text
SAFETY_ALL = [
    'LiPo: charge, store and carry the pack in the TBS LiPo bag (BOM W03); keep it in the ammo can (W04) when not in use; never charge unattended.',
    'Props OFF whenever the pack is plugged in, until the flight card says otherwise. Every bench power-up with props off first.',
    'CNC router (ShopBot): only after the Jacobs ShopBot training and with the staff rules; dust collection on, eye and ear protection, never reach in while the spindle turns. XPS dust: vacuum, mask.',
    'Hot wire (backup only, D-203): XPS fumes. Cut with extraction or outdoors, never leave the wire powered, lowest current that cuts cleanly (K09-L BUILD-GUIDE Safety).',
    'Epoxy and CA: nitrile gloves, ventilation. No solvent glue and no ordinary CA on XPS (it melts the foam): epoxy or foam-safe CA only, test a drop on an offcut.',
    'Carbon dust: sand cut ends wet or with a mask and a vacuum; carbon dust is conductive, keep it off the electronics.',
    'Soldering only in the Jacobs Electronics Lab (studio 110) with extraction (SCHEDULE-A); heat-shrink with the lab heat gun.',
]

PRINT_RATE = 'EST 14-24 g/h (K09-L G3 PRINT-LIST rows 8, 13, 18)'

# ------------------------------------------------------------------------------------------------------------------ steps
S = []


def step(**kw):
    kw.setdefault('cure', '')
    kw.setdefault('need', [])
    kw.setdefault('make', [])
    kw.setdefault('fit', [])
    kw.setdefault('checks', [])
    kw.setdefault('safety', [])
    kw.setdefault('fab', None)
    kw.setdefault('callouts', [])
    kw.setdefault('ghost', [])
    kw.setdefault('hold', False)
    kw.setdefault('cp', [])
    S.append(kw)


# ============================================================ STAGE 1: wing core and spar
step(id='A1', title='Wing core on the bench',
     line='Machine the S5010 core (245 x 900 mm) on the Jacobs ShopBot CNC router in two halves split at the spar bore, with every pocket and groove; bond the halves; tape both skins.',
     tools='Jacobs ShopBot PRSalpha CNC router, 1/2 in ball-nose and 1/4 in flat end mills (EST), 6 mm registration pins, S5010 gauge (laser), knife, 48 mm tape',
     check='Core straight within 1 mm, no twist (EST); weigh: CAD 100.1 g with skin tape',
     min=600, cure='',
     need=['XPS foam (BOM R01): two slabs at least 960 x 280 x 15 mm (EST: each half is about 12 mm thick plus a skim cut); packing tape for the skin (R01 line, "tape, glue"); foam-safe epoxy for the split line (R05); gauge material: 3 mm ply from the Jacobs laser cutter (EST)',
           'ShopBot time at Jacobs: ASSUMED available for foam (user, 2026-11-16, D-203), not yet confirmed with the staff; book the ShopBot training. CAM toolpaths for concept A are not generated yet: `-` (open item).',
           'Backup (D-203): if Jacobs does not allow foam on the ShopBot, hot-wire the core at workspace W from two laser-cut S5010 templates instead; the gear is not in BOM-A (K09-L lines G11 supply + Ni80 wire $46.01 and H05 bow + template stock $16.54, priced 2026-11-14 in `review/CLOSURE-ROUND-2026-11-14/COST-TRADE.md`): buy it only if the ShopBot is refused.',
           'Calipers, steel rule, 0.1 g scale (BOM G02)'],
     make=['Section: the Selig S5010 coordinates are in `redesign/subsystems/wing/s5010.dat` (published, unscaled, 9.82 % t/c, D-193); scale to chord 0.245 m. Lower the airfoil datum 5.0 mm (D-194) so the 12 mm spar bore sits at mid-thickness: foam above / below the bore 6.3 / 5.6 mm. The split plane is z 0 (the bore axis), so each half is machined from a flat slab. CAM toolpaths are not generated for concept A: `-`.',
           'Each half, side 1 (the flat split face): a 12.7 mm (1/2 in) ball-nose groove 6.35 mm deep along y at x 60 mm, which gives the 12 mm spar 0.35 mm of epoxy clearance (EST). Side 2, after flipping the slab about the two registration pins: the airfoil surface (ball-nose finishing, stepover EST 1 mm so the scallops sand out) and the pockets and slots that open to that skin; hold the part on 2-3 mm tabs at the tips (EST). Cut a scrap half first (EST 1 h) to set feed and speed for XPS.',
           'Bond the halves: lay a 12 mm alignment rod wrapped in packing tape (release) in the lower groove, foam-safe epoxy thin on the split faces, close the upper half on the rod and weight it flat on the bench; pull the rod once cured. The bore is then the one the spar slides into in A2. Glue on the split line is lumped in WNG-001 (EST).',
           'The core ends at the elevon hinge line: the cove foot is at x 179.25 mm, the hinge at x 183.75 mm (CAD `cove_x`, `XH`), so the elevon (stage 5) is the 61.25 mm aft strip, machined in the same job and cut free along the cove line with a knife (EST).',
           'Shop cuts (mark from the CAD; every dimension is in `cad/amodel/wing.py` `build_wing`): spar bore 12 mm along y at x 60 mm, z 0 (the 12 mm tube is bonded in this bore); bridge slot open below x 0-56 mm, |y| <= 6.5 mm; pack tray slot x -10 to 22.5 mm, |y| <= 57 mm, open above; saddle slot x 29.5-71 mm, |y| <= 16.5 mm, open below; strut slots (0.5 mm clear); strut clamp slots y 270.5-309.5 mm; rib saddle slots |y| 349.5-410.5 mm; servo pockets x 124.5-165.5 mm, y 177.5-222.5 mm, open to the upper skin; elevon-tip damper notches at the elevon tip; balance-strip windows y 231-339 mm; phase-lead raceway grooves x 0-22.5 mm, |y| 14-24 mm and the open ditch x 22.5-32 mm; servo-lead drop slot at x 83 mm and a 5 x 3.2 mm groove 3 mm under the upper skin (D-198).',
           'Tape skin: both surfaces, the doublers and a tip-edge layer (CAD part WNG-001 lumps the foam, skin, glue and hinge tape: 100.1 g). Tape hinge and fillets are not drawn.'],
     fit=['Lay the finished core lower surface up on a flat bench, leading edge toward you. Nothing is fitted yet. Never lift a slotted core by its ends: lift with two hands under the root (K09-L SW-07 practice).'],
     checks=['Laser-cut S5010 gauge at three stations: thickness within 0.3 mm of the S5010 (EST tolerance); log the real trailing-edge thickness and the split-line step (sand flush).',
             'Dry-fit the 12 mm spar tube through the bore before taping: it must slide without force. The CAD bore equals the tube OD (12.0 mm); a real foam bore needs a small oversize for the epoxy (EST 0.2 mm): cut a test bore in a scrap first.',
             'Weigh the taped core: CAD 100.1 g (MASS-GATE wing group 191 g EST, D-185). Write the number down; every later step is compared with the CAD mass.'],
     safety=['ShopBot: Jacobs training first, dust collection on, eye and ear protection; never reach in while the spindle turns.'],
     fab=dict(kind='core', pid='WNG-001', text='CNC  ShopBot, S5010 in two halves split at the spar bore, XPS 25 kg/m3, 900 x 245 mm; pockets machined; halves bonded'),
     callouts=[('WNG-001', 'Core: XPS, S5010, chord 245 mm, span 900 mm'),
               (('pt', (0.060, 0.45, 0.0), 'right'), 'Spar bore 12 mm at x 60 mm'),
               (('pt', (0.0, 0.0, -0.002), 'top'), 'Tray slot + bridge slot (shop cuts)')],
     hold=True, cp=['Core straight within 1 mm, no twist.', 'Spar tube slides in the bore without force.', 'Taped core weighs about 100 g (CAD 100.1 g).'])

step(id='A2', title='Spar into the core',
     line='Cut the 12x10 carbon spar to 900 mm; push it through the core bore from the right tip; bond it.',
     tools='tube cutter or saw, sandpaper, epoxy, mixing cups, gloves',
     check='Spar flush with both core tips; weigh the spar: CAD 49.8 g (900 mm)',
     min=60, cure='24 h epoxy cure (K09-L practice)',
     need=['1 x 12x10 CF tube, 1 m (BOM R08, 3 tubes in all); epoxy (BOM R05, bought locally); mixing cups, gloves, IPA, masking tape'],
     make=['Cut the spar to 900 mm (CAD `B`, tube 12x10, part WNG-002, 49.8 g). Cut square (wrap tape round the cut line, cut through the tape, sand the end flat).',
           ],
     fit=['Slide the spar through the bore from the right tip until its ends are flush with both core tips (900 mm spar in a 900 mm span).',
          'Bond rule from the CAD: epoxy over |y| <= 0.20 m only, so the foam shear stays at 58 kPa (FIXES2, MS +0.48). Mix epoxy, wet the bore over the centre 400 mm only, push the spar through, wipe squeeze-out.'],
     checks=['Spar axis parallel to the core leading edge within 1 mm over 900 mm (EST).', 'The spar is 900 mm and the core span is 900 mm: the spar ends are flush with the core tips, within 1 mm (EST).'],
     safety=['Epoxy: gloves. Hold the core by the root while the spar goes in.'],
     fab=dict(kind='tube', pid='WNG-002', text='CUT  12x10 carbon tube to 900 mm  (BOM R08)', dims=[('WNG-002', 'cut 900 mm')]),
     callouts=[('WNG-002', 'Spar: CF 12x10, 900 mm, 49.8 g'),
               (('pt', (0.060, -0.45, 0.0), 'left'), 'Bonded over |y| <= 200 mm only')])

step(id='A3', title='Centre plug in the spar',
     line='Print the centre plug (PETG) and push it up the bore to y 0; bond it. It sits under the bridge saddle.',
     tools='printer (PETG), caliper, epoxy, a stick or dowel for the depth',
     check='Plug centre at y 0 +- 1 mm (EST); plug OD 9.8 mm, 20 mm long; CAD 1.2 g',
     min=20, cure='epoxy: see A5 (cure all five plugs together)',
     need=['PETG (BOM R03). Print file: WNG-003-C.stl (qp/A/drawings/out/stl/, drawing WNG-003.pdf)'],
     make=['Print WNG-003-C: PETG, 0.2 mm layer (G3 class A, K09-L PRINT-LIST): a tube 20 mm long, outside 9.8 mm (CAD radius 4.9 mm), bore 4 mm (CAD radius 2 mm). Mass 1.2 g is the CAD value (wall basis EST). Orientation: axis up (EST). Print time EST about 5 min each (1.2 g at the K09-L print rates).',
           'All five spar plugs (WNG-003-C, WNG-004-R/L, WNG-005-R/L) are the same 9.8 x 20 mm shape, 1.2 g each, at y 0, +-300 and +-380 mm.'],
     fit=['Put a drop of epoxy on the plug, push it up the bore on a dowel marked at the depth. The plug sits under the bridge-saddle clamp (stage 2); it stops the tube from crushing when the clamp is bonded.'],
     checks=['Mark the dowel so the plug centre is y 0 (the wing centre); check with the rule through the root slot.'],
     fab=dict(kind='print', pid='WNG-003-C', orient='tube standing on its end, axis up (EST)', text='PRINT  PETG 0.2 mm  WNG-003-C.stl (qp/A/drawings/out/stl/)'),
     ghost=['WNG-001', 'WNG-002'],
     callouts=[('WNG-003-C', 'Plug inside the spar: 9.8 x 20 mm PETG, 1.2 g, centre y 0')])

step(id='A4', title='Right plugs in the spar',
     line='Push the two right plugs up the bore to y +300 (strut clamp) and y +380 (rib saddle); bond them.',
     tools='dowel marked with both depths, epoxy',
     check='Plugs centred at y 300 and 380 mm +-1 mm; CAD 1.2 g each',
     min=25,
     need=['2 more printed plugs: WNG-004-R, WNG-005-R'],
     make=['Print WNG-004-R and WNG-005-R as A3 (PETG, 0.2 mm, 1.2 g each).'],
     fit=['From the right tip, push each plug on the dowel to its mark: WNG-004-R at y 300 mm (under the right strut clamp), WNG-005-R at y 380 mm (under the right rib saddle). Epoxy, wipe the bore wall.'],
     checks=['Measure each depth from the spar end: the right tip is y 450 mm, so the plugs are 150 mm and 70 mm in.'],
     fab=dict(kind='print', pid='WNG-004-R', orient='tube standing on its end, axis up (EST)', text='PRINT  PETG  WNG-004-R.stl, WNG-005-R.stl (qp/A/drawings/out/stl/)'),
     ghost=['WNG-001', 'WNG-002'],
     callouts=[('WNG-004-R', 'Plug inside the spar, under the strut clamp: y +300'), ('WNG-005-R', 'Plug inside the spar, under the rib saddle: y +380')])

step(id='A5', title='Left plugs in the spar',
     line='Push the two left plugs in from the left tip to y -300 and y -380; bond them. Let the epoxy cure.',
     tools='dowel marked with both depths, epoxy',
     check='Plugs at y -300 and -380 mm +-1 mm; spar still straight; weigh the wing: CAD 155.9 g',
     min=25, cure='24 h epoxy cure (K09-L practice): do not load the spar until cured',
     need=['2 more printed plugs: WNG-004-L, WNG-005-L'],
     make=['Print WNG-004-L and WNG-005-L as A3.'],
     fit=['Same as A4 from the left tip: WNG-004-L at y -300 mm, WNG-005-L at y -380 mm.'],
     checks=['Wing (core + spar + 5 plugs) CAD sum: 100.1 + 49.8 + 5 x 1.2 = 155.9 g. Weigh it; a difference over 10 g means check the tape or the epoxy amount.',
             'Lay the wing leading edge on a straight edge: no bow over 900 mm (EST 1 mm).'],
     fab=dict(kind='print', pid='WNG-004-L', orient='tube standing on its end, axis up (EST)', text='PRINT  PETG  WNG-004-L.stl, WNG-005-L.stl (qp/A/drawings/out/stl/)'),
     ghost=['WNG-001', 'WNG-002'],
     callouts=[('WNG-004-L', 'Plug inside the spar: y -300'), ('WNG-005-L', 'Plug inside the spar: y -380')],
     hold=True, cp=['Wing = core + spar + 5 plugs: CAD 155.9 g.', 'No bow along the 900 mm span.', 'Cure the epoxy 24 h before stage 2.'])

# ============================================================ STAGE 2: cage unit
step(id='B0a', title='Cut the cage tubes (bench)',
     line='Cut two 552.4 mm arm tubes, one 108 mm bridge and two 286.2 mm struts; sand every end square.',
     tools='tube cutter or hacksaw, sanding block, caliper, steel rule',
     check='Arm tubes 552.4 mm +-0.5 (30.6 g each); bridge 108 mm (6.3 g); struts 286.2 mm; ends square',
     min=30,
     need=['2 x 12x10 tubes of BOM R08 for the arm tubes (one per 1 m tube; the bridge comes from the 16x14 fin-tube offcut, D-206); 2 x 6x4.5 struts (R10); 14x12 tube (R09) for the 4 doublers and 3 mm carbon rod (R14, price not found) for the 5 pins'],
     make=['Arm tubes A and B: cut 2 x 552.4 mm (CAD `2 x R_M`; each runs motor cup to motor cup through the hub; 30.6 g each, CALC). Bridge: cut 108 mm (CAD `BR_X1 - BR_X0`, 8.1 g); sand a 0.8 mm x 45 deg chamfer on the outside of the end that goes into the hub, so it seats on the cone in the bore floor (D-207, hub FEA run d209).',
           'Doublers: cut 4 x 21 mm from the 14x12 tube (1.4 g each). Pins: cut 4 x 15-16 mm and 1 x 29 mm from the 3 mm rod (0.17-0.33 g). Struts: cut 2 x 286.2 mm (CAD).',
           'Sand all cut ends wet or with a vacuum (carbon dust). Check each end with a square.'],
     checks=['Weigh the two arm tubes: 61.2 g (CALC from 1.6 g/cm3, EST).', 'Slide a doubler over a scrap piece of arm tube: it must slide by hand (bore 12.2 mm nominal; measure on arrival, EST).'],
     safety=['Carbon dust: mask, wet sanding.'],
     fab=dict(kind='tube', pid='CGE-002-A', text='CUT  2 arm tubes 552.4 mm, bridge 108 mm, 4 doublers 21 mm, 5 pins, 2 struts 286 mm', dims=[('CGE-002-A', 'cut 552.4 mm'), ('CGE-004', 'cut 108 mm')]),
     callouts=[('CGE-002-A', 'Arm tube: one 552.4 mm tube per diagonal, 30.6 g'), ('CGE-004', 'Bridge: 108 mm, 8.1 g, chamfered end')])

step(id='B0b', title='Print the hub',
     line='Print the hub (18.3 g PETG); stand it on the bench, aft face down.',
     tools='printer (PETG), caliper',
     check='Both sleeve bores 12 mm (14 mm over the outer 13 mm), bridge bore 16 mm with a 45 deg cone at its floor (D-206, D-207); hub 18.3 g +-15 %',
     min=15,
     need=['PETG (R03). Print file: CGE-001.stl (qp/A/drawings/out/stl/); print time EST about 1 h at 14-24 g/h'],
     make=['Print CGE-001 (CAD 18.3 g: two 1.5 mm sleeves over s +-24 mm, 38 x 20 x 20 mm centre block on the bridge axis to the tray face with 3 mm edge radii, 2.0 / 1.5 mm fillets where the sleeves meet the block (D-207), 16 mm bridge bore with a 0.8 mm x 45 deg cone at its floor, two strut sockets, tray flange). Orientation `-` (EST: aft face on the bed, sleeve axes tilted, supports inside the bores).',
           'Ream or drill the bores to size if needed: tube bores 12.0 mm, doubler counterbore 14.0 mm, bridge bore 16.0 mm with a 45 deg corner (D-206), lead exit holes 4.8 mm, pin holes 3.0 mm, the two pin access holes from the block front (tube B pins).'],
     checks=['Dry-fit a scrap of tube in each bore; weigh the hub (CAD 18.3 g).', 'The printed hub is the part the glue coupon (COUPON-BOND-D202.md) must clear before the FLIGHT hub is printed.'],
     fab=dict(kind='print', pid='CGE-001', orient='aft face on the bed (EST)', text='PRINT  PETG  CGE-001.stl (qp/A/drawings/out/stl/)'),
     callouts=[('CGE-001', 'Hub: print PETG 18.3 g (CGE-001.stl)')])

step(id='B0c', title='Arm tube B through the hub',
     line='Slide arm tube B through its sleeve and the block; bond it over the 48 mm of sleeve.',
     tools='epoxy, mixing stick, wipes, caliper',
     check='Tube centred: 276.2 mm each side of the hub axis (+-0.5)',
     min=20, cure='24 h epoxy cure (K09-L practice) before the pins and the other tube',
     fit=['Dry-fit first. Coat the tube lightly over the middle 60 mm, slide it through its sleeve (it enters from the LL end), centre it 276.2 mm each side. Wipe the squeeze-out from the exit holes.'],
     checks=['Tube B holds LR and UL: its axis is at x +6.5 mm from the hub axis, 34.4 deg from the y axis (CAD).'],
     fab=dict(kind='fit', pid='CGE-002-B', text='FIT  arm tube B through the hub sleeve, epoxy'),
     callouts=[('CGE-002-B', 'Arm tube B: one tube, LR to UL')])

step(id='B0d', title='Pins in tube B',
     line='Push the two 3 mm pins (LR, UL) in along x from the nose side through the block, the sleeve and the tube.',
     tools='epoxy, 3 mm drill bit (clean the holes), wipes',
     check='Pins sit 1.5 mm into the far sleeve wall; CAD 0.17 g each',
     min=20,
     fit=['These two pins lie behind the block, so they go in through 3 mm access holes in the block front face (the CAD note: left open, epoxy-seal them after). Coat each pin, push it in until it stops, wipe.'],
     checks=['Pin ends flush inside the sleeve: not through the tube bore (the bore carries the leads).'],
     fab=dict(kind='fit', pid='CGE-010-LR', text='FIT  2 pins 3 mm x 15 mm, epoxy'),
     callouts=[('CGE-010-LR', 'Pin LR, s +8 mm'), ('CGE-010-UL', 'Pin UL, s -8 mm')])

step(id='B0e', title='Arm tube A through the hub',
     line='Slide arm tube A through its sleeve and the block; bond it.',
     tools='epoxy, wipes, caliper',
     check='Tube centred: 276.2 mm each side of the hub axis; 1.0 mm clear of tube B in x',
     min=20, cure='24 h epoxy cure (K09-L practice)',
     fit=['Same as B0c for tube A (UR and LL); it lies 13 mm ahead of tube B, 1 mm clear of it where the tubes cross.'],
     checks=['Sight along x: the two tubes cross at the hub axis, 34.4 deg to the y axis (mirror images).'],
     fab=dict(kind='fit', pid='CGE-002-A', text='FIT  arm tube A through the hub sleeve, epoxy'),
     callouts=[('CGE-002-A', 'Arm tube A: one tube, UR to LL')])

step(id='B0f', title='Crossing pin and tube A pins',
     line='Push the 29 mm crossing pin and the two tube A pins (UR, LL) in along x from the nose side.',
     tools='epoxy, wipes',
     check='Crossing pin through both tubes and the block; CAD 0.33 g, tube A pins 0.18 g each',
     min=25,
     fit=['The crossing pin (y = z = 0) goes through tube A, the block and tube B; it is flush with the front of the sleeve and ends in the aft sleeve wall. The UR and LL pins are 16 mm, flush with the front of the sleeve. Coat, push in, wipe.'],
     fab=dict(kind='fit', pid='CGE-010-C', text='FIT  crossing pin 3 mm x 29 mm + 2 pins 3 mm x 16 mm, epoxy'),
     callouts=[('CGE-010-C', 'Crossing pin through both tubes'), ('CGE-010-UR', 'Pin UR')])

for _k, (_st, _tb, _s) in enumerate((('UR', 'A', 'UR'), ('LL', 'A', 'LL'), ('LR', 'B', 'LR'), ('UL', 'B', 'UL')), 1):
    step(id='B0g%d' % _k, title='Doubler %s' % _st,
         line='Slide doubler %s over the tube %s end into the sleeve counterbore (s 11 to 32 mm); bond.' % (_st, _tb),
         tools='epoxy, wipes', check='Doubler s 11-32 mm; its 4.8 mm hole lines up with the exit hole; CAD 1.4 g',
         min=15, cure='24 h epoxy cure after the last doubler' if _k == 4 else '',
         fit=['Coat the tube from s 11 to 32 mm, slide the 14x12 doubler on from the %s end until it stops in the sleeve counterbore. Line its 4.8 mm hole up with the hole in the tube (fish wire or a 4.5 mm rod through both); wipe.' % _st],
         checks=['The 4.8 mm hole is open through tube, doubler and sleeve (put the fish wire through).'],
         fab=dict(kind='fit', pid='CGE-009-' + _st, text='FIT  doubler %s over the tube end, epoxy' % _st),
         callouts=[('CGE-009-' + _st, 'Doubler %s: 14x12 carbon, 1.4 g' % _st)])

step(id='B0h', title='Bridge into the boss',
     line='Push the bridge forward into the hub bore from aft until its chamfered end meets the conical floor; bond.',
     tools='epoxy, wipes', check='Bridge end seated on the bore floor cone; 108 mm tube, 8.1 g', min=15, cure='24 h epoxy cure',
     fit=['Coat the first 9 mm of the bridge (the bore depth), push it in from aft until it stops. The tube end is chamfered 0.8 mm x 45 deg to match the cone in the bore floor.'],
     fab=dict(kind='fit', pid='CGE-004', text='FIT  bridge into the hub bore, epoxy'),
     callouts=[('CGE-004', 'Bridge: bonded 9 mm in the hub, seated on the floor')])

for _k, (_st, _tb) in enumerate((('UR', 'A'), ('LL', 'A'), ('LR', 'B'), ('UL', 'B')), 1):
    step(id='B0i%d' % _k, title='Motor cup %s' % _st,
         line='Print the cup; slide it onto the tube %s end (25 mm); bond it, motor axis canted 17 deg.' % _tb,
         tools='printer (PETG), epoxy, protractor', check='Cup 4.3 g; cant 17 deg (D-189) on the cup plate', min=15,
         need=['PETG (R03). Print file: CGE-003-UR/UL/LR/LL.stl (qp/A/drawings/out/stl/)'] if _k == 1 else [],
         make=['Print CGE-003 (4.3 g each, plate flat on the bed, shaft axis up, ARMS.md).'] if _k == 1 else [],
         fit=['Slide the cup on until the tube end meets the plate. Check the cant with a protractor against the CAD drawing; epoxy. The motors go on in B1.'],
         fab=dict(kind='print' if _k == 1 else 'fit', pid='CGE-003-' + _st, orient='plate flat, shaft axis up (ARMS.md)', text='PRINT  PETG  CGE-003-UR/UL/LR/LL.stl x 4 (qp/A/drawings/out/stl/)' if _k == 1 else 'FIT  cup %s on the tube end, epoxy' % _st),
         callouts=[('CGE-003-' + _st, 'Motor cup %s: 4.3 g' % _st)])

for _k, (_s, _n) in enumerate((('R', 'right'), ('L', 'left')), 1):
    step(id='B0j%d' % _k, title='Strut %s' % _n,
         line='Push the %s strut into its hub socket along its own axis; bond.' % _n,
         tools='epoxy, wipes', check='Strut 32 mm deep in the socket; CAD 6.5 g EST', min=10, cure='24 h epoxy cure after the last strut' if _k == 2 else '',
         fit=['Coat the first 30 mm of the strut, push it into the hub strut socket (the socket axis is the strut axis, 66.3 deg to x), wipe. The clamp on the far end goes on in B1.'],
         fab=dict(kind='fit', pid='CGE-005-' + _s, text='FIT  %s strut into the hub socket, epoxy' % _n),
         callouts=[('CGE-005-' + _s, 'Strut %s' % _s)])

step(id='B0k', title='Thread the motor leads (bench)',
     line='Feed each motor\'s 3 leads through cup, tube bore and the 4.8 mm exit hole; lay the free ends flat along the tube.',
     tools='fish wire / thread, 20 AWG wire, tape',
     check='Each bundle comes out of its exit hole at s 18 mm with free ends long enough for the ESC pads',
     min=90, cure='',
     need=['20 AWG silicone wire (W07) for the extensions; heat-shrink (W05); fish wire or a long thread'],
     make=['Phase-lead extensions: each MN2212 has 400 mm of 20 AWG lead (T-Motor page) but the D-202 route to the ESC pads is 0.49-0.51 m (wire_inventory.json), so the stock lead is SHORT: splice an extension of about 0.12-0.15 m onto each of the 12 strands (BOM W07; 30 mm splice overlap, heat-shrink; the CAD lumps the splices in HRN-001). Put the splices outside the tube bore (EST).'],
     fit=['THREAD, on the bench, before the motors go on the cups: push the three leads of each motor from the cup side through the 4.8 mm lead hole, the collar and the tube bore (about 258 mm), out of the 4.8 mm exit hole at s +-18 mm. The exit is on the +t face for the upper arms and the -t face for the lower arms (D-202 CAD note). Keep the bend radius at the collar and at the exit at 4 mm or more. Lay the free ends flat along the tube; they are fished through the hub conduits in B2c.',
          'Use a fish wire pulled through the tube: tape the three lead ends to its tip. The bundle fills 9.7 % of the tube bore (HARNESS-ENCLOSED s2).'],
     checks=['Pull test: the bundle slides freely both ways with two fingers; a tight bundle in a 4 mm bend is a stop.',
             'Weigh the printed parts against the CAD: hub 18.3 g, cup 4.3 g, clamp 1.5 g, saddle 2.0 g, tray 3.8 g (+-15 %, EST).'],
     safety=['Pull wires by the bundle, not by a single strand.'],
     fab=dict(kind='thread', pid='CGE-002-A', text='THREAD  3 leads per motor through the cup collar, the tube bore and the exit hole'),
     chip=dict(kind='thread', text='THREAD  3 leads per motor through the cup collar, the tube bore (258 mm) and the 4.8 mm exit hole'),
     callouts=[('E-HRN-02', 'Motor leads: through the tube bore, out of the exit hole')])

step(id='B1', title='Cage unit: motors, props, dock',
     line='Screw the motors on (threadlocker); fit the props; dock the cage unit on the spar from below.',
     tools='hex key, threadlocker, caliper, epoxy (clamps), tape to mark prop direction',
     check='Props: UR + LL = MRP clockwise; UL + LR = MR counter-clockwise (seen from thrust side)',
     min=90, cure='24 h epoxy cure (K09-L practice) of the clamp bonds on the spar',
     need=['4 x MN2212 V2.0 KV780 (BOM P01); APC 9x4.5MR/MRP 4-pack (P02: 2 x MR + 2 x MRP); T-Motor adapters and spinner nuts (in the motor box, BOM P01 note); 16 x M2.5x8 socket-head screws (ARMS.md: M2.5x8 SHCS; no BOM line, check whether the T-Motor box includes them: `-`); threadlocker (W06); epoxy (R05) for the two clamps'],
     make=['Motors: 4 x M2.5x8 per motor into the 19 x 16 mm pattern (T-Motor drawing). Heads sit on the rear face of the cup plate and thread 3.1 mm into the motor base (ARMS.md); use threadlocker and a paint mark (ARMS s4: loosening under 1P is the realistic cup fatigue risk).',
           'Props: fit the adapter on the shaft, the prop on the adapter, the nut on top. Direction: BOM P02: APC 9x4.5MR (standard) turns counter-clockwise and 9x4.5MRP (reverse) clockwise, seen from the thrust side. CAD: UR and LL are MRP (CW), UL and LR are MR (CCW).'],
     fit=['Dock the cured cage unit on the spar from below (30 mm path, CAD): the bridge saddle and strut clamps snap on the spar (clip slots) and the bridge, saddle and struts go into their core slots. Bond the clamps to the spar with epoxy (CAD edges E-CGE: epoxy).',
          'The frame was built, bonded and cured on the bench in B0a-B0k; only the two clamps are bonded to the spar here.'],
     checks=['Prop direction check: motor direction is set in the ESC; with props OFF spin each motor once the ESC is soldered (E6) and swap two phase leads if it is wrong (EST).',
             'Weigh the cage unit (CAD sums, D-202): hub 19.0 + 2 arm tubes 61.2 + 4 doublers 5.6 + 5 pins 1.0 + 4 cups 17.2 + bridge 6.3 + 2 struts 13.0 + 2 clamps 3.0 + saddle 2.0 = 128.3 g without motors and props; motors 260.0 + props 44.2 + adapters 17.2 + spinner nuts 11.6 add 333.0 g, so 461.3 g complete (the tray is a separate step, B3). Accept +-10 % (EST).',
             'Spin each prop by hand: no rub on the arm or the wing.'],
     safety=['Never fit a prop with the pack plugged in.', 'Mark the prop direction on each arm with tape before the unit is docked.'],
     fab=dict(kind='fit', pid='PRP-002-UR', text='FIT  motors on 4 x M2.5x8 + threadlocker  |  props: UR + LL = MRP clockwise, UL + LR = MR counter-clockwise (seen from the thrust side)'),
     callouts=[('PRP-001-UR', 'Motor MN2212 KV780, 65 g'), ('PRP-002-UR', 'MRP: clockwise (UR, LL)'), ('PRP-002-UL', 'MR: counter-clockwise (UL, LR)'),
               ('CGE-007-R', 'Strut clamp snaps on the spar'), ('CGE-006', 'Bridge saddle on the spar')],
     hold=True, cp=['Prop rotation: UR + LL = MRP clockwise; UL + LR = MR counter-clockwise (seen from the thrust side).',
                    'Motor screws: threadlocker and a paint mark.', 'Cage bonds cured 24 h before it takes load.'])

# ============================================================ STAGE 3: saddles, raceways, tray, dampers
step(id='B2', title='Rib saddles on the spar',
     line='Print the two rib saddles; snap them on the spar from below at y +-380 mm, over the plugs.',
     tools='printer (PETG), epoxy, caliper',
     check='Saddle centre at y 380 mm +-1 mm; weigh: CAD 1.0 g each',
     min=20,
     need=['PETG (R03). Print file: FIN-005-R/L.stl (qp/A/drawings/out/stl/)'],
     make=['Print FIN-005-R/L: PETG, 0.2 mm, 1.0 g each. Ring on the spar 60 mm long, 21 mm outside, with a socket 19 x 19 mm facing aft for the rib and a clip slot.'],
     fit=['Spread the clip slot and snap the ring on the spar from below at y +-380 mm; the socket faces aft. Put a drop of epoxy inside. Check it covers the plug (y +-380 mm).'],
     checks=['Socket axis is along x, parallel to the wing chord (square within 1 degree, EST).'],
     fab=dict(kind='print', pid='FIN-005-R', orient='ring axis up, socket side up (EST)', text='PRINT  PETG  FIN-005-R/L.stl x 2 (qp/A/drawings/out/stl/)'),
     callouts=[('FIN-005-R', 'Rib saddle: print PETG 1.0 g'), (('pt', (0.070, 0.38, -0.012), 'top'), 'over plug y 380')])

step(id='B2a', title='Phase-lead raceways',
     line='Print both raceways; lower each into its foam groove from above (before the tray).',
     tools='printer (PETG), bench dry-fit, no glue yet',
     check='Raceway seats in the groove without force; weigh: CAD 1.8 g each',
     min=20,
     need=['PETG (R03; BOM W07 note: the raceway and conduits come from the R03 spool, about 6 g). Print file: HRN-003-R/L.stl (qp/A/drawings/out/stl/)'],
     make=['Print HRN-003-R/L: closed channel, 0.6 mm walls, outer 9.6 x 6.6 mm, interior 8.4 x 5.4 mm, x -58.2 to 22.5 mm (HARNESS-ENCLOSED D-199.1; 1.8 g each). Wall basis is EST (as the bay cover); orientation `-` (EST: flat on its wide side).'],
     fit=['Lower each raceway from above through the slot in the hub pad flange into its foam groove (x 0-22.5 mm, |y| 14-24 mm). Two lanes: y 17 mm (upper-arm bundle) and y 21 mm (lower-arm bundle).'],
     checks=['Dry-fit: the raceway slides into the groove with a 0.2 mm clearance. Do not bond until the leads are threaded (B2c).'],
     fab=dict(kind='print', pid='HRN-003-R', orient='flat on its wide side (EST)', text='PRINT  PETG  HRN-003-R/L.stl x 2 (qp/A/drawings/out/stl/)'),
     callouts=[('HRN-003-R', 'Raceway: 0.6 mm wall, 1.8 g'), ('HRN-003-L', 'Raceway L')])

for _k, (_st, _d) in enumerate((('UR', 'lower from above'), ('UL', 'lower from above'), ('LR', 'raise from below'), ('LL', 'raise from below')), 1):
    step(id='B2b%d' % _k, title='Hub conduit %s' % _st,
         line='Print conduit %s; %s onto its sleeve and its raceway window.' % (_st, _d),
         tools='printer (PETG), caliper', check='Conduit docks over the 4.8 mm exit hole and on the raceway window; CAD 0.8-1.3 g', min=15,
         need=['PETG (R03). Print file: HRN-004-UR/UL/LR/LL.stl x 4 (qp/A/drawings/out/stl/; the four differ)'] if _k == 1 else [],
         make=['Print HRN-004 x 4: 0.6 mm wall tunnel (D-202: chimney over the exit hole, aft run, sideways step, drop / rise column), 0.8-1.3 g each (EST basis).'] if _k == 1 else [],
         fit=['Move the conduit toward the tube along the exit-hole axis (40 mm): its floor hugs the sleeve and its column lands on the raceway wall round the window (x -53 mm). Keep the lead ends out of the way. Bond.'],
         checks=['The conduit mouth lines up with the 4.8 mm exit hole: put the fish wire through it.'],
         fab=dict(kind='print' if _k == 1 else 'fit', pid='HRN-004-' + _st, orient='on its side (EST)', text='PRINT  PETG  HRN-004-UR/UL/LR/LL.stl x 4 (qp/A/drawings/out/stl/)' if _k == 1 else 'FIT  conduit %s on the sleeve, epoxy' % _st),
         callouts=[('HRN-004-' + _st, 'Conduit %s: 0.6 mm wall' % _st)])

step(id='B2c', title='Thread the phase leads to the ditch',
     line='Fish the 12 strand ends through the conduit, raceway and foam ditch; leave them out at x 29 mm.',
     tools='fish wire, tape, 20 AWG wire only if a lead is short',
     check='3 leads per motor, no kink; free ends out at x 29 mm (CAD)',
     min=60, cure='',
     fit=['Feed the free ends of the 12 phase strands (from B0k) through their hub conduit, the raceway and the foam ditch. Fish-thread from the ditch end. The free ends stay out at x 29 mm for the ESC pads (E6).',
          'Bundle path in the CAD: arm bore 264 mm, conduits + raceway 111 mm, ditch 10 mm, then 71-85 mm under the bay cover (HARNESS-ENCLOSED D-199).'],
     checks=['Each motor: three strands, same colour order at both ends (mark each lead with tape).', 'Minimum bend radius 4 mm (HARNESS-ENCLOSED D-199.1).'],
     fab=dict(kind='thread', pid='CGE-001', text='THREAD  3 leads x 4 motors through conduit, raceway, ditch'),
     callouts=[('HRN-003-R', 'Raceway'), ('E-HRN-02', 'Leads threaded through the hub conduit and the raceway')])

step(id='B3', title='Pack tray',
     line='Lower the printed tray into the core slot; bond it to the hub aft face.',
     tools='epoxy, clamps or tape, caliper',
     check='Tray sits flat on the hub pad, raceways not pinched; CAD 3.8 g',
     min=30, cure='1 h to hold, 24 h epoxy cure (K09-L practice)',
     need=['PETG (R03). Print file: CGE-008.stl (qp/A/drawings/out/stl/)'],
     make=['Print CGE-008: one part, 66 x 109 mm plate, 1.5 mm floor with ribs, integral lips at the trim ends: the pack can be placed 6 mm forward to 10 mm aft of nominal (CAD `TRIM_FWD`, `TRIM`); floor basis EST (D-194).'],
     fit=['Lower the tray from above into the core tray slot (x -10 to 22.5 mm). Bond it to the pad flange on the hub aft face (59 mm of bond width after the raceway slots, D-199: open item, coupon not run).'],
     checks=['The raceway must not be pinched: the tray plate underside sits on the raceway top (z 6.0 mm).'],
     fab=dict(kind='print', pid='CGE-008', orient='plate flat on the bed (EST)', text='PRINT  PETG  CGE-008.stl (qp/A/drawings/out/stl/)'),
     callouts=[('CGE-008', 'Pack tray: one printed part, 3.8 g')])

step(id='B4', title='Hinge damper units',
     line='Assemble each damper, fill it with 12,500 cSt silicone, set it in its core notch at the elevon tip.',
     tools='printer, syringe, 12,500 cSt silicone, silicone O-ring / cord, wipes',
     check='Rotor turns with a slow, even drag; no fluid leaks after 10 min; CAD 2.0 g + 0.5 g',
     min=60, cure='',
     need=['Silicone damping fluid 12,500 cSt (BOM R12, EST, about 0.6 g per unit), silicone cord and O-rings (R13), PETG (R03), syringe (EST), paper towels'],
     make=['Print WNG-009-R/L stator (housing OD 12.7 mm, bore 11.1 mm, pin OD 8.9 mm; 2.0 g with fluid) and WNG-010-R/L rotor (sleeve OD 10.0 mm, wall 0.5 mm, 17 mm long, flange 11.2 mm; 0.5 g): PETG (CAD `DMP_*`, FIXES2). The gap each side is 0.30 mm; print fit is the risk: sand the sleeve until it slides.',
           'Fill: put about 0.6 g of silicone fluid (BOM R12) in the housing, push the rotor sleeve in (it displaces the fluid up the gap), seal the end with an O-ring strip.'],
     fit=['Set each damper unit into its core notch at the elevon tip from aft (the notch is open aft; 30 mm travel), before the ribs (C1). Bond the housing in the notch with epoxy; the rotor flange is bonded on the elevon tip face in C2.'],
     checks=['Turn the rotor by hand: smooth, with drag, no stick. EST damping c = 1.03e-3 N m s/rad per elevon (D-188), not testable by hand.', 'Leave the damper upright 10 min on a tissue: no fluid mark.'],
     safety=['Silicone fluid makes floors slippery and ruins epoxy bonds: keep it off bond surfaces (wipe with IPA).'],
     fab=dict(kind='print', pid='WNG-009-R', orient='axis up (EST)', text='PRINT  PETG  WNG-009-R/L, WNG-010-R/L; FILL 12,500 cSt silicone'),
     callouts=[('WNG-009-R', 'Damper stator, fluid filled, 2.0 g'), ('WNG-010-R', 'Rotor: sleeve + flange, 0.5 g'),
               ('WNG-009-L', 'Left damper')],
     hold=True, cp=['Rotor turns with an even drag.', 'No fluid on the bond faces.', 'Tray bond and raceway must be cured before stage 4.'])

# ============================================================ STAGE 4: fin ribs, rib fairings
step(id='C1', title='Fin ribs',
     line='Cut two 14x12 carbon ribs to 215.5 mm; push each in from aft into its saddle socket.',
     tools='tube cutter, sandpaper, epoxy, calipers',
     check='Rib length 215.5 mm (CAD); CAD mass 14.1 g at that length (the CAD part carries 14.8 g)',
     min=45, cure='24 h epoxy cure (K09-L practice)',
     need=['1 x 14x12 CF tube, 1 m (BOM R09: price unverified)'],
     make=['Cut 2 ribs, each 215.5 mm (CAD `RIB_X1 - RIB_X0`: x 70.5 to 286.0 mm). Mass 14.1 g each (D-200: CAD mass and BOM R09 now use the drawn 215.5 mm).'],
     fit=['Slide each rib in from aft through the saddle socket (300 mm path); its far end stops at x 286 mm, where the root block (C5) will take it. Epoxy in the saddle socket.'],
     checks=['Rib axis along x, within 1 degree (EST); the rib ends at the front face of the fin tube: x 286 mm = tube centre 294 mm minus the 8 mm tube radius (CAD `RIB_X1`).'],
     safety=['Carbon dust: wet-sand or vacuum.'],
     fab=dict(kind='tube', pid='FIN-002-R', text='CUT  14x12 carbon tube to 215.5 mm  (BOM R09)', dims=[('FIN-002-R', 'cut 215.5 mm')]),
     callouts=[('FIN-002-R', 'Rib: CF 14x12, cut 215.5 mm'), ('FIN-005-R', 'Rib sits in the saddle socket')])

step(id='C1a', title='Rib fairings',
     line='Cut two XPS blisters (130 to 183.75 mm); bond each over the rib where it leaves the upper skin.',
     tools='knife and sanding block (or the ShopBot with the core job), sandpaper, foam-safe CA or epoxy, tape',
     check='Blister 17 mm wide, 1.5 mm over the tube, blends to the skin; CAD 0.3 g (EST)',
     min=40, cure='CA: minutes; epoxy: 24 h (K09-L practice)',
     need=['XPS offcut (R01); tape (R01); thin CA M5T / foam-safe only (R07) or epoxy'],
     make=['Cut the blister from the foam offcut: 17 mm wide, top 1.5 mm over the tube, x 130 mm to the hinge line (CAD `RIBF_X0`, `RIBF_LOOP`); tape it. The CAD trims it by the core and the rib when built: trim by hand to blend.'],
     fit=['Lower each blister onto the upper skin from above, over the rib; bond with foam-safe CA (CAD edge: CA). The lower skin does not expose the rib.'],
     checks=['Test a drop of CA on an offcut first: no melting of the foam.'],
     fab=dict(kind='cut', pid='FIN-006-R', text='CUT  XPS blister 17 mm wide, x 130 to 183.75 mm; tape it'),
     callouts=[('FIN-006-R', 'Rib fairing: XPS + tape')])

# ============================================================ STAGE 5: elevons, balance, lens caps
step(id='C2', title='Elevons with balance strips',
     line='Cut the elevons; bond a 15.6 g lead strip + 2 tabs on each nose; tape-hinge; push them in.',
     tools='lead sheet 1.3 mm, snips, knife, epoxy, hinge tape, 0.1 g scale',
     check='Lead strip 10 x 1.3 x 106 mm = 15.6 g each; elevon 6.7 g; both strips within 0.3 g',
     min=90, cure='24 h epoxy cure (K09-L practice)',
     need=['Lead sheet 1.3 mm (BOM R11, EST price: fishing / roofing lead); CF/PETG tab strip 6 x 1.2 mm; hinge tape (R05); epoxy (R05)'],
     make=['Elevon: the 61.25 mm aft strip of the S5010 blank, y 40-350 mm (CAD `ELEV_Y0`, `ELEV_Y1`), tape skin; 6.7 g each. A 0.5 mm gap each end (GAP_Y).',
           'Balance: cut a lead strip 10 mm x 106 mm from 1.3 mm sheet (15.6 g at 11.34 g/cm3, D-187 v2), centre y 285 mm (y 232-338 mm). Two tabs (CF-reinforced PETG strips 6 x 1.2 mm) at y 285 +- 35 mm; bond the tab roots to the elevon nose face with a 0.4 mm epoxy gap; bond the strip to the tab ends 20 mm ahead of the hinge axis, 3.3 mm below it (CAD `BAL_REACH`, `BAL_DZ`). Total WNG-007 16.1 g each. Weigh the strip before bonding: 15.6 g +- 0.3 g.'],
     fit=['Push each elevon with its balance horn in from aft (25 mm travel): the horn and strip enter the pocket in the core. Tape-hinge the upper surface after the fit.',
          'The damper rotor flange (WNG-010, from B4) is bonded on the elevon tip face.'],
     checks=['Free swing: deflect the elevon +-21 deg by hand (CAD mechanical stop, ELEV_STOP): nothing touches except the stop bosses (C2a).',
             'Weigh: elevon 6.7 g, balance 16.1 g (CAD). Both elevons within 0.3 g of each other (EST).'],
     safety=['Lead: wash hands after cutting; do not file or sand it dry; no eating at the bench.'],
     fab=dict(kind='lead', pid='WNG-007-R', text='CUT  lead strip 10 x 1.3 x 106 mm = 15.6 g  (D-187 v2), bond to the 2 tabs', dims=[('WNG-007-R', 'strip 106 mm')]),
     callouts=[('WNG-006-R', 'Elevon R: 61.25 mm strip, 6.7 g'), ('WNG-007-R', 'Lead strip 15.6 g, 20 mm ahead of the hinge'),
               ('WNG-010-R', 'Damper rotor flange on the tip')],
     hold=True, cp=['Lead strips 15.6 g each, within 0.3 g.', 'Elevon swings +-21 deg freely.', 'Epoxy cured 24 h.'])

step(id='C2a', title='Upper lens caps',
     line='Print the two upper caps; lower each over the strip window on the upper skin; bond the flange.',
     tools='printer (vase mode), epoxy, tape',
     check='Cap wall 0.6 mm; clearance to the lead at the stop 0.5 mm or more; CAD 3.8 g',
     min=30, cure='24 h epoxy cure (K09-L practice)',
     need=['PETG (R03). Print files: WNG-008-RU.stl, WNG-008-LU.stl (qp/A/drawings/out/stl/)'],
     make=['Print WNG-008-RU / LU: PETG, single 0.6 mm wall, vase mode (CAD says vase-mode print, EST), 3.8 g each; with the two stop bosses and a 3 mm wide, 0.4 mm thick bonding flange.'],
     fit=['Lower the cap onto the upper skin over the strip window (15 mm travel); bond the flange with epoxy; the stop bosses pass through the window to the tab.'],
     checks=['Deflect the elevon to +21 deg: the tab touches the boss (stop), the lead stays 0.5 mm clear of the cap.'],
     fab=dict(kind='print', pid='WNG-008-RU', orient='flange face down on the bed (EST)', text='PRINT  PETG vase mode  WNG-008-RU/LU.stl (qp/A/drawings/out/stl/)'),
     callouts=[('WNG-008-RU', 'Upper lens cap, 0.6 mm wall, 3.8 g')])

step(id='C2b', title='Lower lens caps',
     line='Print the two lower caps; raise each onto the lower skin; bond; check the stops both ways.',
     tools='printer (vase mode), epoxy, tape',
     check='Elevon stops at +-21 deg; CAD 3.8 g each',
     min=30, cure='24 h epoxy cure (K09-L practice)',
     need=['PETG (R03). Print files: WNG-008-RL.stl, WNG-008-LL.stl (qp/A/drawings/out/stl/)'],
     make=['As C2a (lower caps).'],
     fit=['Raise each cap onto the lower skin (15 mm travel); bond the flange.'],
     checks=['Deflect each elevon to both stops: +-21 deg; the servo software limit is +-20 deg (ELEV_LIM), so the mechanical stop is 1 deg beyond it.'],
     fab=dict(kind='print', pid='WNG-008-RL', orient='flange face down on the bed (EST)', text='PRINT  PETG vase mode  WNG-008-RL/LL.stl (qp/A/drawings/out/stl/)'),
     callouts=[('WNG-008-RL', 'Lower lens cap, 3.8 g')],
     hold=True, cp=['Both elevons reach +-21 deg and stop on the bosses.', 'Lead never touches a cap.'])

# ============================================================ STAGE 6: fins
step(id='C3', title='Fin fairing, right',
     line='Machine a 3 mm XPS fairing 360 mm long on the ShopBot (hot wire as the backup); tape it; slide it on from outboard; bond with foam-safe CA.',
     tools='ShopBot (face an XPS slab to 3 mm, then profile; backup: hot wire), tape, sandpaper, foam-safe CA',
     check='Fairing 3 mm thick, 360 mm tall, 4 mm elliptical leading edge; CAD 8.4 g',
     min=35, cure='',
     need=['XPS (R01), tape (R01), CA (R07, foam-safe only)'],
     make=['Cut a 3 mm XPS fairing 360 mm tall (CAD `2 x FIN_H`): elliptical leading edge 4 mm long x 3 mm thick, straight sides, ending at the tube axis; tape it (8.4 g each). A rib groove runs across it (0.5 mm clearance) for the 14 mm rib.'],
     fit=['Slide the right fairing on from outboard (40 mm); it sits in the tube slot and round the rib. Bond with foam-safe CA.'],
     checks=['Fairing is vertical and flush with the tube front (x 294 mm tube centre, tube radius 8 mm).'],
     fab=dict(kind='cut', pid='FIN-004-R', text='CUT  XPS 3 mm thick, 360 mm tall, elliptical nose; tape both faces', dims=[('FIN-004-R', 'cut 360 mm')]),
     callouts=[('FIN-004-R', 'Fairing R: XPS 3 mm + tape, 8.4 g')])

step(id='C4', title='Fin fairing, left',
     line='Same as C3 for the left fin: slide the fairing on from outboard.',
     tools='as C3',
     check='Fairings match: both 8.4 g within 0.3 g',
     min=25,
     make=['As C3.'], fit=['Slide the left fairing on from outboard (40 mm); bond with foam-safe CA.'],
     checks=['Compare the two fairings side by side and on the scale (8.4 g CAD).'],
     callouts=[('FIN-004-L', 'Fairing L')])

step(id='C5', title='Fin root blocks',
     line='Print two root blocks; push each on the rib end from aft; it takes the fin tube in C6.',
     tools='printer (PETG), epoxy, caliper',
     check='Block bore 16 mm for the tube; rib socket 19 x 19 mm; CAD 3.2 g',
     min=30, cure='24 h epoxy cure (K09-L practice)',
     need=['PETG (R03). Print file: FIN-003-R/L.stl x 2 (qp/A/drawings/out/stl/)'],
     make=['Print FIN-003-R/L: tube ring 60 mm long, outside 23 mm, bore 16 mm, plus a 19 x 19 mm rib socket (CAD `build_fins`), 3.2 g each. Orientation: ring axis up (EST).'],
     fit=['Push each block on the rib end from aft (60 mm path), tube hole vertical; epoxy in the socket.'],
     checks=['Tube bore vertical within 1 degree (EST): drop a straight 16 mm rod through it.', 'The block sits on the fin plane y 380 mm +-1 mm.'],
     fab=dict(kind='print', pid='FIN-003-R', orient='tube-ring axis up (EST)', text='PRINT  PETG  FIN-003-R/L.stl x 2 (qp/A/drawings/out/stl/)'),
     callouts=[('FIN-003-R', 'Root block: tube bore 16 mm, rib socket'), ('FIN-002-R', 'Rib end')])

step(id='C6', title='Fin tubes',
     line='Cut two 16x14 fin tubes to 360 mm; drop each through its block; bond; keep them vertical.',
     tools='tube cutter, epoxy, square / plumb, calipers',
     check='Tube 360 mm, centre at x 294 mm, y +-380 mm; vertical within 1 degree; CAD 27.1 g each',
     min=60, cure='24 h epoxy cure (K09-L practice)',
     need=['1 x 16x14 CF tube, 1 m (BOM R02): 2 x 0.36 m = 0.72 m'],
     make=['Cut 2 tubes, each 360 mm (CAD FIN_H 0.18 m: z -180 to +180 mm; 27.1 g each).'],
     fit=['Drop each tube down through its block (500 mm start, 360 mm tube): centred on z 0, 180 mm each side. Epoxy the block ring.'],
     checks=['Plumb: tube vertical in the wing plane (nose view) and in the side view within 1 degree (EST).',
             'Equal height each side: tube ends at z +-180 mm +-1 mm.'],
     safety=['The tube ends are sharp: cap them with tape until the feet are on.'],
     fab=dict(kind='tube', pid='FIN-001-R', text='CUT  16x14 carbon tube to 360 mm  (BOM R02)', dims=[('FIN-001-R', 'cut 360 mm')]),
     callouts=[('FIN-001-R', 'Fin tube R: CF 16x14, 360 mm, 27.1 g'), ('FIN-001-L', 'Fin tube L')],
     hold=True, cp=['Fin tubes 360 mm, centred, vertical within 1 degree.', 'Weigh the half-built wing: about 790 g (CAD running total).'])

# ============================================================ STAGE 7: landing feet
step(id='C7', title='Upper shoes',
     line='Print four foot shoes; slide the two upper ones on the top tube ends from above and bond.',
     tools='printer (PETG), epoxy',
     check='Shoe plate faces aft; ring on the tube; CAD 1.4 g',
     min=20, cure='24 h epoxy cure (K09-L practice)',
     need=['PETG (R03). Print file: GER-001-UR/UL/LR/LL.stl x 4 (qp/A/drawings/out/stl/)'],
     make=['Print GER-001 UR/UL/LR/LL: PETG, 1.4 g each; ring 12 mm tall on the tube, plate 5.5 x 21 x 15 mm facing aft for the pad (CAD).'],
     fit=['Slide the upper shoes on the upper tube ends (30 mm, from above), plate aft; epoxy.'],
     checks=['The four shoe plates are in one plane, 337.5 mm aft of the wing leading edge (CAD ground plane).'],
     fab=dict(kind='print', pid='GER-001-UR', orient='shoe ring axis up (EST)', text='PRINT  PETG  GER-001-UR/UL/LR/LL.stl x 4 (qp/A/drawings/out/stl/)'),
     callouts=[('GER-001-UR', 'Shoe: PETG 1.4 g')])

step(id='C8', title='Lower shoes',
     line='Raise the two lower shoes onto the bottom tube ends from below and bond.',
     tools='epoxy', check='All four plates coplanar within 1 mm (EST)',
     min=20, cure='24 h epoxy cure (K09-L practice)',
     make=['As C7.'], fit=['Raise the lower shoes on the lower tube ends (30 mm, from below); epoxy.'],
     checks=['Stand the aircraft on the four shoe plates on a flat bench: no rocking (EST 1 mm).'],
     callouts=[('GER-001-LR', 'Lower shoe')])

step(id='C9', title='Foot pads',
     line='Cut four EVA/PE pads 12 x 15 x 30 mm; slide each on from aft onto its shoe plate and press on.',
     tools='knife, double-sided tape (CAD: pad PSA)',
     check='Pad 12 x 15 x 30 mm, flat; weigh: CAD 0.7 g each',
     min=20, cure='24 h cure (EST)',
     need=['EVA/PE foam, 12 x 15 mm section (BOM R03 line text names "foot pads"; no separate foam line: `-`)'],
     make=['Cut 4 pads 12 x 15 mm, 30 mm long (CAD `GER-002`), flat ends.'],
     fit=['Slide each pad on from aft (30 mm travel) onto the shoe plate and press it on: the CAD pad is stuck with its own pressure-sensitive adhesive (edge E-GER: pad PSA on the shoe plate). Use double-sided tape if the foam has no adhesive back (EST).'],
     checks=['Standing check: aircraft stands on 4 pads, upright, wing vertical (this is the take-off pose).'],
     callouts=[('GER-002-UR', 'Foot pad: EVA/PE 12 x 15 x 30 mm')],
     hold=True, cp=['Aircraft stands on its four pads without rocking.', 'Feet cured before the aircraft is stood up.'])

# ============================================================ STAGE 8: servos, linkage
step(id='D1', title='Servos in their pockets',
     line='Drop the two EMAX ES3054HV servos into the core pockets from above; fix them.',
     tools='servo tester, screwdriver, foam-safe CA or epoxy dab',
     check='Servo 28.4 x 26.7 x 13.0 mm (servodatabase); weigh: 20.5 g each',
     min=30,
     need=['3 x EMAX ES3054HV (BOM M01: 2 + 1 spare)'],
     make=['Test each servo on the servo tester before it goes in.'],
     fit=['Drop each servo into its pocket (core, x 124.5-165.5 mm, y +-200 mm) 30 mm from above and bond it in the pocket with a little epoxy (CAD edge E-MEC: epoxy, `servo in its pocket`). Keep epoxy off the case seam and the output shaft.'],
     checks=['The pocket is open to the upper skin, so the arm can sweep +-20 deg (CAD).'],
     callouts=[('MEC-001-R', 'Servo ES3054HV, 20.5 g')])

step(id='D0', title='Thread the servo leads',
     line='Fish each servo lead along its foam groove, 3 mm under the skin, to the slit at x 83 mm.',
     tools='fish wire, tape',
     check='Free end out of the slit at x 83 mm, |y| 24 mm (CAD)',
     min=30,
     fit=['Feed each servo 3-wire lead from the pocket along its foam groove (3 mm under the upper skin, aft of the spar) to the slit at x 83 mm, |y| 24 mm. Free end stays out for the FC pads (E3b).'],
     checks=['Lead 250 mm routed (CAD E-HRN-07 / 08); wire inside the groove, nothing under the skin tape.'],
     fab=dict(kind='thread', pid='MEC-001-R', text='THREAD  servo lead in the foam groove'),
     callouts=[('E-HRN-07', 'Servo lead R in its groove'), ('E-HRN-08', 'Servo lead L')])

step(id='D2', title='Servo arms',
     line='Drill the arm hole 1.3 mm at 8.5 mm; centre each servo with the tester; press the arm on the spline so it sits level.',
     tools='servo tester, 1.3 mm drill, calipers',
     check='Arm hole 1.3 mm, 8.5 mm from the shaft (CAD D-212 rev 3; window 7.8-8.97 mm); arm 1.0 g',
     min=20,
     make=['Drill the arm hole with a 1.3 mm drill at 8.5 mm from the spline centre (the ES3054HV arm hole row is not published: if a stock hole lies 7.8-8.97 mm from the centre and is 1.25-1.35 mm, use it and re-solve the linkage with its radius; a 1.3 mm hole on 1.2 mm wire is 0.1 mm clearance, D-212 rev 3).',
           'Measure the output boss height: if the arm does not sit on the case top, the arm-top height (CAD 8.70 mm above the datum) changes and the horn hole and keeper heights follow it: update electrical.py ARM_Z0 and re-print the horn and keeper.',
           'Centre the servo with the tester at 1500 us (standard servo pulse, EST).'],
     fit=['Press the arm on the 23-tooth output spline 15 mm from above (CAD: EMAX ES3054HV, 23T spline, RMRC page 85975). The arm points inboard at centre. The screw goes in after the pushrod and keeper (step D2a).'],
     checks=['Arm hole radius 8.5 mm (D-212 rev 2), hole 1.3 mm (rev 3).'],
     callouts=[('MEC-002-R', 'Servo arm: hole 1.3 mm at 8.5 mm')])

step(id='D2a', title='Z-bend keepers and arm screws',
     line='Lay the printed keeper on the arm over the Z-bend; fit the M2 x 8 screw through keeper and arm into the output shaft; snug, threadlocker.',
     tools='small screwdriver, threadlocker',
     check='Rod free to swing under the keeper bridge; it cannot lift more than 0.3 mm; arm cannot be pulled off',
     min=15,
     need=['M2 x 8 pan screws (R05 stock screws, local)'],
     make=['Print 2 Z-bend keepers (CAD MEC-008, PETG, 0.08 g each, drawing MEC-008): flat, bridge face down.'],
     fit=['Keeper spacer on the arm top, its bridge over the Z-bend leg and bend (CAD MEC-008: spacer 1.5 mm, bridge 0.8 mm, bridge underside 0.3 mm above the rod top resting on the arm); M2 x 8 pan screw (CAD HWC-002) through keeper and arm into the shaft; a little threadlocker (W06).'],
     checks=['Feeler 0.3 mm between rod top and bridge with the rod resting on the arm; the rod swings +-25 deg about the leg without touching the spacer.', 'Arm cannot be pulled off.', 'Keeper retorque and inspection (review r3 m-4; the keeper is a 2.3 mm printed PETG stack clamped by one M2 screw and held against rotation by clamp friction only, creep and preload loss "-"): after the first full-travel run (step D5b) and after the stall test re-snug the M2 screw and look for a crack or white stress line at the bridge root (spacer end); repeat at every preflight. Hand check: bridge stress 19.5 of 20 MPa EST at the 51 N stall case (linkage_loads_check.py keeper_bridge_MEC008), so a cracked or loose keeper is replaced, not repaired.'],
     callouts=[('MEC-008-R', 'Z-bend keeper'), ('HWC-002-R', 'M2 x 8 arm screw')])

step(id='D3', title='Horns on the elevons',
     line='Cut a 2.2 mm slot through each elevon, push the printed horn rib down into it and bond it; tape over the slot.',
     tools='slot guide, 2 mm saw / hot wire, 1.1 mm drill, epoxy, 0.1 g scale',
     check='Horn hole directly above the hinge line (x 183.75 mm), 9.155 mm up from the hinge axis (CAD D-212 rev 3); printed horn 0.95 g',
     min=40, cure='24 h epoxy cure (K09-L practice)',
     need=['Printed horn MEC-004 x 2 (R03 PETG)'],
     make=['Print 2 horns (CAD MEC-004, drawing MEC-004): LYING FLAT, 2 mm thick, so the blade and rib bend in the layer plane (D-212 rev 3, review M-3); hole printed 0.9 mm, then reamed with a 1.1 mm drill (0.1 mm on the 1.0 mm clevis pin).',
           'Cut the slot through the full elevon depth at the horn station (y = 191.5 mm from the centreline), 2.2 mm wide, from 2.4 to 55.1 mm aft of the hinge line (CAD cut on WNG-006): use a printed or ply slot guide.'],
     fit=['Push the horn rib down into the slot from above (15 mm travel) until the blade base sits on the upper skin and the rib bottom is 0.2 mm inside the lower skin; fill the slot with epoxy (both faces wetted, CAD edge E-MEC: rib bonded in its slot). Tape over the slot on both skins with a 60 x 40 mm patch of the skin tape after the cure, the upper patch slit for the blade.'],
     checks=['Hole centre directly above the hinge line and 9.155 mm up from the hinge axis (CALC, D-212 rev 3): lay the pushrod across; it must run level and parallel to the chord at neutral.', 'The clevis cheeks slide over the blade and pivot freely (fit check of the printed 2 mm blade in the 2.2 mm cheek gap, review m-5).'],
     callouts=[('MEC-004-R', 'Control horn: blade + rib, hole 9.155 mm above the hinge line')])

step(id='D4', title='Pushrods',
     line='Bend-test one rod; Z-bend the 1.2 mm rod into the 1.3 mm arm hole; set the clevis cheeks over the horn blade.',
     tools='Z-bend pliers, small pliers, calipers, 7.9 kg weight or spring scale',
     check='Pushrod 0.97 g; rod test at 91 N passed; clevis cheeks straddle the horn blade',
     min=40,
     need=['M02 linkage set: pushrods, clevises (its horns are not used)'],
     make=['Receipt test (D-212 rev 3, review M-1): form a Z-bend on a spare M02 rod, hold the leg in a 2 mm plate with a 1.3 mm hole and load the rod along its axis with 91 N for 10 s (= 1.5 x the 51 N stall force x 1.9 / 1.6: the Z-bend leg sees an eccentricity of 1.9 mm when the rod is lifted against the keeper, 1.6 mm when it rests on the plate, so the plate test is raised 19 % instead of shimming the rod, review r3 m-3; load computed in linkage_loads_check.py receipt_test_load_N): pass = no permanent set over 0.2 mm at the far end. If it sets, use ASTM A228 music wire 1.2 mm for both rods and repeat.'],
     fit=['Z-bend the 1.2 mm rod into the arm tip hole (CAD: L-end leg down through the 1.3 mm arm hole, the rod lying on the arm top; held down by the keeper, step D2a) and set the clevis over the horn blade, cheeks either side (CAD: clevis on the horn hole, horizontal pin; 10 mm). The pin follows in D5.'],
     checks=['Elevon neutral with servo centred: straight edge on the elevon and the core.'],
     callouts=[('MEC-003-R', 'Pushrod 1.2 mm, Z-bend + clevis')])

step(id='D5', title='Clevis pin, right',
     line='Press the 1.0 x 4.4 mm clevis pin through the cheeks and the horn hole from outboard.',
     tools='tweezers, small pliers',
     check='Pin flush, free to pivot; CAD 0.03 g',
     min=15,
     fit=['Press the pin in along y from outboard (6 mm).'],
     checks=['Pin cannot fall out; the clevis moves freely.'],
     callouts=[('MEC-005-R', 'Clevis pin 1.0 x 4.4 mm')])

step(id='D5b', title='Clevis pin, left',
     line='Press the left clevis pin in along y from outboard; run each elevon through its full travel.',
     tools='tweezers, servo tester',
     check='Both elevons move +-20 deg smoothly, equal throw',
     min=10,
     fit=['Press the pin in along y from outboard (6 mm).'],
     checks=['With the servo tester, each elevon goes +-20 deg without binding; both match within 1 degree (EST).', 'Free play at the trailing edge, servo powered at neutral: record the BUILT value (dial gauge, +-0.05 mm at the trailing edge). Basis: flutter (review r3 m-7): the limit is the 1 deg guide of SERVO.md s4, and the CAD budget is 1.28 deg from the hole clearances; servo gear backlash and the clevis cheek holes are not in that budget ("-"), so the measured value is expected to be above it. The hinge damper makes flutter independent of stiffness (FIXES2 s1), but a nonlinear free-play limit cycle is not covered by that linear sweep: a built value above 1 deg is reported as a FAIL of CL-A-LINKAGE-FREEPLAY, not waived (D-212 rev 3 open item).', 'Bench stall test (D-212 rev 3, review r3 M-1; claim CL-A-HORN-STALL-BENCH, test T-A-HORN-RIB; EST criteria): with the servo at 7.2 V, temporarily set the endpoint past the stop and drive each elevon into its +21 deg stop for 5 s (the 51 N stall case). Pass: no crack in horn, rib, slot tape or stop; hole elongation <= 0.1 mm (a 1.2 mm pin gauge must not enter the 1.1 mm hole); trailing-edge set < 0.5 deg. Record what yields first. A failed bench test is a stop: the fallback is the CF torsion tube of the trade table (docs/engineering-decisions.md, D-212 rev 3 row J).', 'Set the endpoints so neither servo reaches the 21 deg stop (no stall current at full stick); the endpoint is +-20 deg. This stops a SERVO-driven stall only: with the built free play (budget 1.28 deg) the surface can still touch the 21 deg stop under a reversed aerodynamic load, which is a hold-level load (17 N), not the 51 N stall (review r3 m-7). If the measured free play exceeds 1 deg, set the endpoints to +-19 deg.', 'Re-snug both Z-bend keeper screws and inspect each keeper bridge for cracks after the stall test (review r3 m-4); this is also a preflight item (keeper screw snug, bridge intact, rod lifts no more than 0.3 mm).'],
     callouts=[('MEC-005-L', 'Clevis pin L')],
     hold=True, cp=['Elevons move +-20 deg, no binding, no rub on the caps.', 'Servo arm screws snug.', 'Weigh: tubes and linkage mass match the CAD.'])

# ============================================================ STAGE 9: avionics
step(id='E1', title='Pitot probe',
     line='Slide the pitot (EST 160 mm) into its groove in the left leading edge from the front; bond it.',
     tools='caliper',
     check='Pitot EST 160 x 3 mm with its plastic block (RMRC publishes no size); weigh: CAD 5.0 g',
     min=20,
     need=['RMRC MS4525 airspeed + pitot (BOM V05)'],
     make=['Measure the pitot and the airspeed board from V05 on arrival: probe length and OD, the plastic attachment block and where its two barbs are, the board size and its port and plug positions (CAD EST: 160 x 3 mm probe from x -130 mm, block 8 x 9 x 6 mm, barbs 4.4 mm apart on its rear face; board 15 x 15 mm, ports facing forward). If they differ, update electrical.py PIT_* / AS_* before cutting.',
           'Cut in the core (D-208, from above): the probe groove at y -420 with a 9 x 7 mm nose channel for the block; the line pocket behind the probe and over the spar; the board pocket at x 69-84 mm (aft of the spar); the I2C lead groove at x 95 mm from the left plate window to the board (deep under the servo-lead groove, shallow over the fin rib tube).'],
     fit=['Slide it in from the front (250 mm path) into its groove in the leading edge at y -420 mm, 40 mm outboard of the left fin plane and 110 mm outboard of the prop discs (EST: outside the rotor wash), block last; bond it with epoxy (CAD edge: epoxy). Fill the nose channel ahead of the block with foam and epoxy.'],
     checks=['Probe points straight ahead (along x), within 2 degrees (EST).'],
     callouts=[('AVN-006', 'Pitot probe, brass, 5.0 g')])

step(id='E2', title='Avionics plate',
     line='Print the plate; seat four M2 thin nuts in the hex pockets; place it on the skin over the spar.',
     tools='printer (PETG), M2 thin nuts (DIN 439), tweezers',
     check='Plate 110 mm wide, nuts seated flush; CAD 8.0 g + 0.41 g',
     min=25,
     need=['PETG (R03). Print file: AVN-001.stl (qp/A/drawings/out/stl/); 4 x M2 thin nuts DIN 439 1.2 mm (R05 stock hardware)'],
     make=['Print AVN-001: PETG, lightening windows, 4 hex pockets 4.2 mm across, 2.2 mm clearance holes (CAD).'],
     fit=['Press the nuts into the hex pockets, then set the plate on the skin (20 mm from above) and bond it with foam-safe CA (CAD edge: CA, plate base follows the upper skin). The FC 20 x 20 mm M2 pattern is centred on the spar (x 60 mm): the FC sits on the wing centre, not on the cage hub (SITL follow-up).'],
     checks=['Nuts flush; the plate lies flat on the skin.'],
     fab=dict(kind='print', pid='AVN-001', orient='plate flat on the bed (EST)', text='PRINT  PETG  AVN-001.stl (qp/A/drawings/out/stl/)'),
     callouts=[('AVN-001', 'Plate: print PETG 8.0 g'), ('HWC-003', 'M2 thin nuts in hex pockets')])

step(id='E3', title='ESC, FC, RX, GPS, airspeed',
     line='Stick the FC on four 3 mm foam-tape pads; put the ESC, RX and GPS on the plate and the airspeed board in its left-wing-tip pocket.',
     tools='foam tape (VHB-class), tweezers, 0.1 g scale',
     check='FC on 4 pads (hard mount, 20 x 20 mm); weigh: FC 17.0 g, ESC 20.0 g, RX 4.6 g, GPS 13.5 g',
     min=40,
     need=['Kakute F405 Wing Mini (V03), SpeedyBee BLS 35A 4-in-1 ESC (P04), RP3 V2 (V02), TBS M10Q GPS (V04), MS4525 board (V05)'],
     make=['Flash and set up in the Electronics Lab first: firmware, parameters (Q_TAILSIT etc.). Parameter file `qp/A/A.param`. Not covered here: `-`.'],
     fit=['Press the FC on the four pads; set the ESC, RX and GPS on the plate in their CAD places (GPS y 27.5-52.5 mm, RX y -52.5 to -39.5 mm); foam-tape the airspeed board in its pocket at x 69-84 mm, y -427.5 to -412.5 mm, ports facing forward (D-208).'],
     checks=['Arrow on the FC points aft (AHRS_ORIENTATION 0, CAD note).', 'GPS has sky view.'],
     callouts=[('AVN-002', 'FC Kakute F405 Wing Mini'), ('PRP-003', 'ESC 4-in-1'), ('AVN-004', 'GPS + compass'), ('AVN-003', 'RX RP3')])

step(id='E3a', title='FC screws',
     line='Four M2 x 25 screws down through the FC stack into the plate nuts.',
     tools='small screwdriver', check='Screws snug; FC does not rock',
     min=15,
     fit=['Four M2 x 25 pan screws through the stack into the nuts (20 mm).'],
     checks=['Snug only; the foam pads still isolate vibration.'],
     callouts=[('HWC-001', 'M2 x 25 screws')])

step(id='E3d', title='Pitot lines',
     line='Push the two short silicone lines on the pitot barbs and on the airspeed board ports; tape the pockets closed.',
     tools='scissors, hinge tape', check='Blow gently into the pitot tip: the airspeed reading rises; no kink in either line', min=25,
     need=['RMRC tubing 2 / 4 mm: about 0.5 m comes in V05'],
     make=['Cut two lines of 36 mm (CAD route, AVN-009-T / -S) plus 5 mm each for trimming.'],
     fit=['Push each line 4 mm onto its barb on the probe block, bend it up and aft over the spar and push it 4 mm onto its board port: P1 total, P2 static (ARSPD_TUBE_ORDR 2 makes a swap harmless). Both lines lie in the pocket under the skin line; tape the pocket and the board pocket closed.',
          'Exposed: none (the lines and the board are in the core under tape).'],
     checks=['Bends are tight (4 mm radius, about 1 x the tube OD, EST: the vendor gives no minimum): look for a flattened bend; the blow test must still read.'],
     callouts=[('AVN-009-T', 'Pitot line, total, 36 mm'), ('AVN-009-S', 'Pitot line, static, 36 mm')])

step(id='E3b', title='Solder the signal wiring',
     line='Solder the ESC signal ribbon, servo leads, RX, GPS and airspeed leads to the FC.',
     tools='soldering station (Jacobs EL), heat-shrink, multimeter',
     check='Continuity on every joint; no short to neighbour pads',
     min=120, cure='',
     need=['Jacobs Electronics Lab soldering station + multimeter + extraction'],
     fit=['LAY: ESC signal ribbon to the FC, servo leads to FC pads S5 / S6, RX CRSF lead, GPS and airspeed leads (JST plugs on the sensor boards). D-208: the airspeed I2C lead (about 0.5 m) is threaded first: from the board pocket along its groove at x 95 mm to the slot under the left plate window, up through the window, along the plate (taped, about 70 mm in the open) to the cover notch and the FC I2C pad.'],
     checks=['Continuity each joint; no short between neighbour pads; lead colours as the CAD.'],
     safety=['Soldering only in the Jacobs Electronics Lab.'],
     fab=dict(kind='solder', pid='AVN-002', text='SOLDER  ESC ribbon, servo leads S5/S6, RX, GPS, airspeed'),
     callouts=[('E-HRN-06', 'ESC signal ribbon'), ('E-HRN-07', 'Servo lead R to pad S5'), ('E-HRN-09', 'RX lead'), ('E-HRN-10', 'GPS lead')],
     hold=True, cp=['Continuity on every solder joint.', 'No short between neighbour pads.', 'Boards secure; FC arrow aft.'])

# ============================================================ STAGE 10: pack, power, cover
step(id='E3c', title='Anti-slip pad',
     line='Stick the 100 x 30 x 1 mm silicone pad on the tray floor.', tools='knife, scissors',
     check='Pad 100 x 30 x 1.0 mm; CAD 3.5 g (EST)', min=5,
     need=['Silicone rubber sheet 1 mm (BOM W09, EST)'],
     make=['Cut 100 x 30 mm from the 1 mm sheet.'], fit=['Stick on the tray floor (10 mm from above).'],
     callouts=[('PWR-003', 'Anti-slip pad, 1 mm')])

step(id='E4', title='Flight pack in the tray',
     line='Lay the Tattu 2300 4S pack in the tray against the lip; the strap goes on next.',
     tools='0.1 g scale, TBS LiPo bag',
     check='Pack 105 x 35 x 29 mm, 270 g; no swelling or dents; resting near 15.2 V (4 x 3.8 V, EST)',
     min=10,
     need=['Tattu 2300 4S (BOM W01)'],
     fit=['Lay the pack on the anti-slip pad, between the tray lips (30 mm from above). The strap (E5) holds it. Fore-aft trim (6 mm forward to 10 mm aft) is set later at the CG check.'],
     checks=['Pack not swollen, no damage; storage voltage 3.8 V per cell (EST).'],
     safety=['Pack stays unplugged.'],
     callouts=[('PWR-001', 'Pack Tattu 2300 4S, 270 g')])

step(id='E4a', title='XT60 female',
     line='Plug the XT60 female with its tail onto the pack lead XT60 male; tape it on the skin.',
     tools='soldering (tail to ESC after), heat-shrink', check='Polarity: red to +, black to -',
     min=20,
     need=['XT60, 14 AWG wire (BOM W05)'],
     fit=['Plug the XT60 female on the pack lead XT60 male from aft (15 mm); the XT60 pair stays outboard of the pack end (y 55.75-71.25 mm) so you can unplug it in the field; foam-tape it to the skin and tie it (CAD edge E-HRN-21). The tail is soldered to the ESC pads in E6.'],
     checks=['Check polarity with a multimeter: pack + to ESC BAT +.'],
     callouts=[('HRN-002', 'XT60 female + 14 AWG tail')])

step(id='E4b', title='Pack leads and balance lead',
     line='Tape the pack power leads and the balance lead along the skin; balance plug on the pack top.',
     tools='tape', check='Leads under tape, not pinched', min=20,
     fit=['Vendor leads taped to the skin along their route.'],
     checks=['No tension on the connectors.'],
     callouts=[('E-HRN-13', 'Pack power leads'), ('E-HRN-14', 'Balance lead')])

step(id='E5', title='Pack strap',
     line='Thread the strap under the bridge tube and close it over the pack.',
     tools='none', check='Pack does not move when you shake the aircraft', min=10,
     fit=['Thread the 20 x 300 mm strap by hand: over the pack top, outside the tray end walls, under the tray plate and under the 16 mm bridge tube (D-206) (CAD edge E-PWR: buckle strap). Buckle it over the pack. The CAD thickness 1.6 mm is EST.'],
     checks=['Strap tight: pack does not move.'],
     callouts=[('PWR-002', 'Pack strap 20 x 300 mm')])

step(id='E6', title='Solder phase leads and battery tail',
     line='Solder the battery tail to the ESC BAT pads and the 12 phase leads to the motor pads; heat-shrink.',
     tools='soldering station (Jacobs EL), heat-shrink, multimeter',
     check='Continuity pad to motor winding; no short between phases; props OFF', min=150,
     fit=['LAY: battery tail to the ESC BAT pads and the 12 phase leads (free ends from B0 / B2c) to the ESC motor pads; heat-shrink.'],
     checks=['Continuity each phase to the winding; no short.', 'First power-up: props OFF, pack plugged for the first time.'],
     safety=['Pack stays unplugged until every joint is checked.'],
     fab=dict(kind='solder', pid='PRP-003', text='SOLDER  tail to BAT pads, 12 phase leads to motor pads'),
     callouts=[('E-HRN-12', 'Battery tail to BAT pads'), ('E-HRN-02', 'Phase leads to motor pads')],
     hold=True, cp=['Continuity each phase; no short between phases.', 'Props OFF for every power-up.'])

step(id='E7', title='Bay cover',
     line='Print the bay cover; lower it over the FC stack and ESC; foam tape and two ties.',
     tools='printer, foam tape, ties', check='Cover fits; leads drop into the notches; CAD 9.6 g', min=20,
     need=['PETG (R03). Print file: AVN-008.stl (qp/A/drawings/out/stl/)'],
     make=['Print AVN-008: 0.6 mm hood, x 22.5-126.5 mm, |y| <= 26.5 mm.'],
     fit=['Lower the cover (40 mm) onto the plate; leads drop into the notches; tape and tie.'],
     checks=['Final weigh-in: gate 1.47 kg (D-190); CG 19-26 mm aft of the LE.'],
     fab=dict(kind='print', pid='AVN-008', orient='roof up, open side down (EST)', text='PRINT  PETG  AVN-008.stl (qp/A/drawings/out/stl/)'),
     callouts=[('AVN-008', 'Bay cover: 0.6 mm PETG, 9.6 g')],
     hold=True, cp=['Weigh-in: gate 1.47 kg.', 'CG 19-26 mm aft of the leading edge.'])

BY_ID = {s['id']: s for s in S}
