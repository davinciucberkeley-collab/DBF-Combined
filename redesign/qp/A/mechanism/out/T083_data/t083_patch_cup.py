"""T-083 one-shot patch: cup CGE-003 for the X2216 on its X-mount (wing.py), lead hole y (common.py PH_Y), lead route start and stock lead
length (electrical.py), assembly plan (X-mount in the cage group). Backups: *_p8_backup.py in this folder.  python -I t083_patch_cup.py"""
import os
CAD = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'cad'))


def sub(path, pairs):
    p = os.path.join(CAD, path)
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        if a not in s:
            raise SystemExit('NOT FOUND in %s: %s' % (path, a[:90]))
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8').write(s)
    print('patched', path, len(pairs))


sub('amodel/common.py', [
    ("PH_Y = 0.0055                               # cup lead hole y (cup frame): collar bore y 3.5..8.0 holds the bend",
     "PH_Y = 0.0180                               # T-083: cup lead hole y (cup frame). The X2216 leads leave the can radially at the base end (SunnySky drawing), so the hole sits\n"
     "                                            # outside the can (r 13.85) after a 4 mm bend: 13.85 + 4 = 17.85 -> 18.0; collar bore y 3.5..20.5 holds the second bend (was 5.5 / 3.5..8.0, MN2212)"),
])

sub('amodel/wing.py', [
    ("CUP_PAT = (0.019, 0.016)                    # MN2212",
     "CUP_PAT = (0.019, 0.016)                    # T-083: no longer drilled (the X2216 sits on its X-mount PRP-006, bolted at r 17 on the diagonals; see propulsion.py). Was: MN2212"),
    ("        cup.prism('X', -0.012, [_rrect_part(0.0035, 0.0165, 0.0165, CUP_R, False, True)], 0.005, name='cup plate cantilever 5.0 mm over the +y 13 mm (T-073 R3fix: the strike S2 row)')",
     "        cup.prism('X', -0.012, [_rrect_part(0.0035, CUP_Y1, 0.0165, CUP_R, False, True)], 0.005, name='cup plate cantilever 5.0 mm over +y 3.5..22.5 (T-073 R3fix: the strike S2 row; T-083: +6 mm for the X2216 lead hole at y 18)')"),
    ("        for sz_ in (1, -1):\n            cup.cylinder('X', (CUP_WEB_X - 0.0001, -CUP_PAT[0] / 2, sz_ * CUP_PAT[1] / 2), CUP_BOSS_X1 - CUP_WEB_X + 0.0001, CUP_BOSS_R, name='screw-head pocket boss r 3.9 mm (T-073 R3fix local bosses; size EST)')\n",
     "        # T-083: the MN2212 screw-head pocket bosses are gone (no motor screws behind the plate)\n"),
    ("        cup.prism('Y', 0.0035 - 0.00005, [w_loop], 0.0053 + 0.00005, name='collar-to-plate web with 1 mm fillets (D-210: the collar only touched the plate along a line)')\n"
     "        cup.prism('Z', -w_zc, [cup_chord_loop(ys=0.0088)], 2 * w_zc, name='cup fillet 1 mm where the web and collar cap end on the plate (D-210)')\n"
     "        for sy_ in (1, -1):\n            for sz_ in (1, -1):\n                cup.cut_cylinder('X', (-0.0126, sy_ * CUP_PAT[0] / 2, sz_ * CUP_PAT[1] / 2), 0.0055, 0.00145, name='motor screw hole M2.5 clearance 2.9 mm (ISO 273 medium; pattern V T-Motor drawing)')\n"
     "        for sz_ in (1, -1):                          # D-197: the y = -9.5 mm screw heads sit in the sleeve wall; print the pocket (was only implied by the seat cut)\n"
     "            cup.cut_cylinder('X', (-0.0072, -CUP_PAT[0] / 2, sz_ * CUP_PAT[1] / 2), 0.0034, 0.00265, name='screw head pocket 5.0 mm in the sleeve wall (D-197, structures/arm_cup_checks.md)')\n"
     "        cup.cut_cylinder('X', (-0.0127, 0.0, 0.0), 0.0063, 0.004, name='motor rear relief 8 mm (EST)')\n",
     "        cup.prism('Y', 0.0035 - 0.00005, [w_loop], CUP_COL_Y1 + 0.0008 - 0.0035 + 0.00005, name='collar-to-plate web with 1 mm fillets (D-210: the collar only touched the plate along a line; T-083: to the longer collar)')\n"
     "        cup.prism('Z', -w_zc, [cup_chord_loop(ys=CUP_COL_Y1 + 0.0008)], 2 * w_zc, name='cup fillet 1 mm where the web and collar cap end on the plate (D-210)')\n"
     "        for k_ in range(4):                          # T-083: X-mount bolt holes, r 17 on the diagonals (M3 clearance 3.4 mm, ISO 273 medium)\n"
     "            a_ = math.radians(45.0 + 90 * k_)\n"
     "            cup.cut_cylinder('X', (-0.0126, 0.017 * math.cos(a_), 0.017 * math.sin(a_)), 0.0060, 0.0017, name='X-mount bolt hole M3 clearance 3.4 mm (T-083)')\n"),
    ("        cup.tube('Y', (0.0, 0.0035, 0.0), 0.0045, 0.0070, ARM_OD / 2 + 0.0001, name='lead collar (D-198, 1.0 mm wall)')\n"
     "        cup.cylinder('Y', (0.0, 0.0080, 0.0), 0.0008, 0.0070, name='lead collar end cap (D-198, 0.8 mm)')",
     "        cup.tube('Y', (0.0, 0.0035, 0.0), CUP_COL_Y1 - 0.0035, 0.0070, ARM_OD / 2 + 0.0001, name='lead collar (D-198, 1.0 mm wall; T-083: to y 20.5 for the lead hole at y 18)')\n"
     "        cup.cylinder('Y', (0.0, CUP_COL_Y1, 0.0), 0.0008, 0.0070, name='lead collar end cap (D-198, 0.8 mm)')"),
    ("CUP_R = 0.006                               # plate corner radius (EST)",
     "CUP_R = 0.006                               # plate corner radius (EST)\n"
     "CUP_Y1 = 0.0225                             # T-083: plate +y edge (was 16.5): lead hole PH_Y 18.0 + 2.4 + 2.1 mm ligament\n"
     "CUP_COL_Y1 = PH_Y + 0.0025                  # T-083: lead collar end (was 8.0 = 5.5 + 2.5)"),
])

sub('amodel/electrical.py', [
    ("    pts = [mworld(st, (-0.0135, PH_Y, 0.0)), mworld(st, (PH_XC, PH_Y, 0.0)), mworld(st, (PH_XC, -0.150, 0.0)),",
     "    # T-083: the X2216 leads leave the can radially (+y, cup frame) LEAD_DX above the base face (start inside the can wall, r 11.5), 4 mm bend into the plate hole at PH_Y\n"
     "    xl = X_MB - LEAD_DX\n"
     "    pts = [mworld(st, (xl, 0.0115, 0.0)), mworld(st, (xl, PH_Y, 0.0)), mworld(st, (PH_XC, PH_Y, 0.0)), mworld(st, (PH_XC, -0.150, 0.0)),"),
    ("    rad = [0.040, 0.040, 0.004, 0.004]" if False else "    rad = [0.004, 0.040, 0.040, 0.004, 0.004]\n    yl = c['yl']",
     "    rad = [0.004, 0.004, 0.040, 0.040, 0.004, 0.004]\n    yl = c['yl']"),
    ("# D-198 bottom-up mass of the lumped harness remainder HRN-001 (replaces the 50.9 g \"110 g allocation less itemised parts\"). The 400 mm stock leads of the\n"
     "# motors are inside the 65 g motor mass (T-Motor page: 55 g without cables, 65 g with), so only the length beyond 0.40 m (+ 30 mm splice overlap) is added.",
     "# D-198 bottom-up mass of the lumped harness remainder HRN-001 (replaces the 50.9 g \"110 g allocation less itemised parts\"). T-083: the X2216 has 100 mm stock\n"
     "# leads (SunnySky drawing), taken to be inside the 67.5 g page mass (EST, not stated), so the length beyond 0.10 m (+ 30 mm splice overlap) is added (was 0.40 m, MN2212)."),
    ("        ext += 3 * max(0.0, _plen(phase_path(st, px, py, ESC_TOP + 0.002)[0]) - 0.40 + 0.030)\n"
     "    return [('phase-lead extensions: 12 strands of 20 AWG, CAD route beyond the 0.40 m stock lead + 30 mm splice (%.2f m)' % ext, round(ext * WIRE_G_PER_M[20], 1)),",
     "        ext += 3 * max(0.0, _plen(phase_path(st, px, py, ESC_TOP + 0.002)[0]) - LEAD_L + 0.030)\n"
     "    return [('phase-lead extensions: 12 strands of 20 AWG, CAD route beyond the 0.10 m X2216 stock lead + 30 mm splice (%.2f m)' % ext, round(ext * WIRE_G_PER_M[20], 1)),"),
])

sub('a_assembly_plan.py', [
    ("['PRP-001-' + s for s in ST] + ['PRP-004-' + s for s in ST]", "['PRP-006-' + s for s in ST] + ['PRP-001-' + s for s in ST] + ['PRP-004-' + s for s in ST]"),
    ("(400 mm stock + extension, EST)", "(100 mm X2216 stock + extension, EST)"),
])
