"""amodel/wing.py - LANE A (aero and structure): wing core/section, spar + plugs, elevons, elevon balance, lens caps, mechanical
stops, hinge damper, fins, hub, arms, motor cups, bridge, struts, clamps, pack tray (CGE-008), and their edges + builders
build_wing / build_fins / build_cage. Split from a_model.py; no geometry change.

Lane A edits only this file for those parts. It reads shared constants from common.py (C, B, XH, ELEV_*, COORDS, SPAR_*, HUB, YM,
ZM, R_M, CANT, PHI, YFIN, XFIN_T, FIN_H, FIN_OD/ID, PACK_X, TRIM, TRAY_X1, SERVO_Y, SV_Z1): changing those needs coordination
with lanes B and C. Constants defined HERE are lane A's alone: ELEV_LIM, GAP_Y, PLUG_R, R_IN, HUB_R/X0/X1, ARM_OD/ID, BR_*,
STRUT_*, RIB_*, BAL_*, HINGE_Z, CAP_*, BOSS_*, RHO_PETG, DMP_*, cove XL, core_loop.
"""
from .common import *   # noqa: F401,F403  (shared constants, frames, airfoil helpers, P/E registries)

# ------------------------------------------------------------------ lane A constants (m)
ELEV_LIM = 20.0                             # deg EST (A documents give none): control authority, software limit SERVO5/6
GAP_Y = 0.0005
PLUG_R = 0.0049
R_IN = R_M - 0.245                          # DOC: arm tube 0.245 long
HUB_R, HUB_X0, HUB_X1 = 0.050, -0.105, -0.045      # EST hub disc (envelope of a printed shell; 16 g)
ARM_OD, ARM_ID = 0.012, 0.010               # DOC iteration 2: arms 12x10
BR_OD, BR_ID, BR_X0, BR_X1 = 0.012, 0.010, -0.100, 0.054       # DOC bridge 12x10 (0.16 m in DOC; 0.154 here, ends on the saddle)
STRUT_OD, STRUT_ID = 0.006, 0.0045          # DOC 6x4.5
STRUT_S = (-0.065, 0.0229, 0.0)             # EST start inside the hub
STRUT_E = (0.0500, 0.2850, 0.0)               # EST end in the clamp boss on the spar (DOC: to the spar at y 0.30)
RIB_OD, RIB_ID, RIB_X0 = 0.014, 0.012, 0.0705
RIB_X1 = XFIN_T - FIN_OD / 2                # rib ends on the tube front


def cove_x():
    """Lower end of the slanted core back face (cove for the elevon nose, deflection ELEV_STOP + 2 deg)."""
    t = math.tan(math.radians(ELEV_STOP + 4.0))
    x = XH
    for _ in range(60):
        x = XH - (zu(XH) - zl(x)) * t
    return x


XL = cove_x()


def core_loop():
    up = [(x, zu(x)) for x in XS]                      # LE -> hinge
    lo = [(x, zl(x)) for x in XS if x < XL - 1e-6] + [(XL, zl(XL))]
    return list(reversed(up)) + lo[1:]                 # hinge-top -> LE (aft to fore) then lower LE -> cove foot

# D-187 (FLUTTER.md): elevon mass balance, 10.7 g lead on a 30 mm horn ahead of the hinge, per elevon (EST)
BAL_YC, BAL_W = 0.285, 0.106                # QP-4 FIXES D-187 v2: lead STRIP centre y, length (spanwise y 0.232-0.338; clear of the servo pocket edge y 0.2225 and the elevon tip 0.35)
BAL_ARM_DY = 0.035                          # two horn tabs at BAL_YC +- this
BAL_REACH, BAL_L, BAL_T = 0.020, 0.010, 0.0013        # lead centre 20 mm ahead of the hinge axis; strip 10 x 1.3 mm section x 106 mm = 15.6 g at 11.34 g/cm3 (FIXES.md: fits the section to 2 mm of skin poke, printed lens caps)
BAL_DZ = -0.0060                            # lead centre z below the hinge axis: centres the sweep in the 16.8 mm section; +-20 deg at 30 mm still pokes up to 5.5 mm through both skins (CAD.md QP-4)
BAL_ARM_W, BAL_ARM_T = 0.006, 0.0012        # horn arm (CF-reinforced PETG strip) width, thickness
HINGE_Z = zu(XH)


def _poly_area(l):
    return sum(l[i][0] * l[(i + 1) % len(l)][1] - l[(i + 1) % len(l)][0] * l[i][1] for i in range(len(l))) / 2


def _ccw(l):
    return l if _poly_area(l) > 0 else l[::-1]


def bal_arm_loop():
    xe = XH - BAL_REACH + BAL_L / 2             # aft end of the lead block
    zc = HINGE_Z + BAL_DZ
    zr = HINGE_Z - 0.0035                       # arm root on the elevon nose face (x = XH)
    t = BAL_ARM_T / 2
    return _ccw([(XH - 0.0004, zr + t), (xe, zc + t), (xe, zc - t), (XH - 0.0004, zr - t)])   # 0.4 mm epoxy gap to the elevon nose


def bal_lead_loop():
    xc, zc = XH - BAL_REACH, HINGE_Z + BAL_DZ
    return _ccw([(xc - BAL_L / 2, zc - BAL_T / 2), (xc + BAL_L / 2, zc - BAL_T / 2), (xc + BAL_L / 2, zc + BAL_T / 2),
                 (xc - BAL_L / 2, zc + BAL_T / 2)])


def _rot_pt(p, a_deg):
    a = math.radians(a_deg)
    vx, vz = p[0] - XH, p[1] - HINGE_Z
    return (XH + vx * math.cos(a) + vz * math.sin(a), HINGE_Z - vx * math.sin(a) + vz * math.cos(a))


def _hull(pts):
    pts = sorted(set(pts))
    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def bal_sweep_loop(margin=0.0005):
    """Convex hull of the horn and lead over -ELEV_LIM..+ELEV_LIM (5 deg steps), grown by margin: the pocket cut in the core."""
    pts = []
    for a in range(-int(ELEV_STOP) - 1, int(ELEV_STOP) + 2, 2):      # FIXES2: pocket covers the mechanical stop +1 deg
        for l in (bal_arm_loop(), bal_lead_loop()):
            pts += [_rot_pt(p, a) for p in l]
    for l in (bal_arm_loop(), bal_lead_loop()):          # install path: the elevon with its balance slides in 25 mm from aft (assembly step C2)
        pts += [(q[0] + 0.025, q[1]) for q in l]
    h = _hull(pts)
    cx = sum(p[0] for p in h) / len(h)
    cz = sum(p[1] for p in h) / len(h)
    out = []
    for p in h:
        d = math.hypot(p[0] - cx, p[1] - cz)
        out.append((p[0] + (p[0] - cx) / d * margin, p[1] + (p[1] - cz) / d * margin))
    return _ccw(out)

# ------------------------------------------------------------------ FIXES2: lens caps, mechanical stops, hinge damper
CAP_WALL, CAP_CLR, CAP_SLOPE = 0.0006, 0.0005, 0.20      # printed single wall 0.6 mm (vase-mode print, EST); clearance lead / tab to the cap cavity at the stop >= 0.5 mm; ramp 1:5
CAP_Y0, CAP_Y1 = BAL_YC - BAL_W / 2 - 0.002, BAL_YC + BAL_W / 2 + 0.002
BOSS_S = (0.62, 0.90)                       # stop boss touches the tab face between 55 % and 85 % of the tab length from the root (clear of the lead by >= 0.5 mm)
BOSS_W = 0.006                              # boss width (= tab width)
RHO_PETG = 1.27                             # g/cm3


def _edge_pts(l, step=0.0005):
    out = []
    for i in range(len(l)):
        p, q = l[i], l[(i + 1) % len(l)]
        n = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) / step))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(n)]
    return out


def _skin(side, x):
    return zu(x) if side == 'U' else zl(x)


def _out(side, x, h):                       # z of the point h outside the skin at x
    return _skin(side, x) + h if side == 'U' else _skin(side, x) - h


def _h_of(side, x, z):                      # height of z outside the skin
    return z - zu(x) if side == 'U' else zl(x) - z


def cap_env(side):
    """Height outside the skin needed by the lead strip and tabs over -STOP..+STOP, per 1 mm bin of x."""
    env = {}
    pts0 = _edge_pts(bal_lead_loop()) + _edge_pts(bal_arm_loop())
    for k in range(-42, 43):
        a = ELEV_STOP * k / 42.0
        for p in pts0:
            x, z = _rot_pt(p, a)
            b = int(round(x * 1000))
            env[b] = max(env.get(b, -1.0), _h_of(side, x, z))
    return env


def cap_profile(side):
    """(xs list m, h_out list m): outer lens profile above the skin; inner = h_out - CAP_WALL. Covers the lead sweep + CAP_CLR + wall, and the tab bosses."""
    env = cap_env(side)
    need = {b: h + CAP_CLR for b, h in env.items() if h + CAP_CLR > 0.0002}
    xa, xb = min(need), max(need)
    xb = max(xb, int(round(max(p[0] for p in boss_loop(side)) * 1000)) + 1)       # boss reach on the tab
    bins = list(range(xa - 1, xb + 2))
    ho = [max(need.get(b, 0.0) + CAP_WALL, need.get(b - 1, 0.0) + CAP_WALL, need.get(b + 1, 0.0) + CAP_WALL) if b in need or (b - 1) in need or (b + 1) in need else CAP_WALL for b in bins]
    dx = 0.001
    for _ in range(2):
        for i in range(1, len(ho)):
            ho[i] = max(ho[i], ho[i - 1] - CAP_SLOPE * dx)
        for i in range(len(ho) - 2, -1, -1):
            ho[i] = max(ho[i], ho[i + 1] - CAP_SLOPE * dx)
    xs = [b / 1000.0 for b in bins]
    # ends: ramp down to the skin
    n0 = int(math.ceil(ho[0] / (CAP_SLOPE * dx))); n1 = int(math.ceil(ho[-1] / (CAP_SLOPE * dx)))
    xs = [xs[0] - dx * (n0 - i) for i in range(n0)] + xs + [xs[-1] + dx * (i + 1) for i in range(n1)]
    ho = [ho[0] * (i / float(n0)) for i in range(n0)] + ho + [ho[-1] * (1 - (i + 1) / float(n1)) for i in range(n1)]
    return xs, ho


def cap_loop(side):
    xs, ho = cap_profile(side)
    outer = [(x, _out(side, x, h)) for x, h in zip(xs, ho)]
    inner = [(x, _out(side, x, max(h - CAP_WALL, 0.0))) for x, h in zip(xs, ho)]
    return _ccw(outer + inner[::-1]), outer, inner


def cap_end_loop(side):
    xs, ho = cap_profile(side)
    outer = [(x, _out(side, x, h)) for x, h in zip(xs, ho)]
    base = [(x, _skin(side, x)) for x in xs]
    return _ccw(outer + base[::-1])


def boss_loop(side):
    """Stop boss: bottom face coincides with the tab face rotated to the stop angle (+STOP upper / -STOP lower); top buried in the cap wall."""
    a = ELEV_STOP if side == 'U' else -ELEV_STOP
    xr, zr_ = XH - 0.0004, HINGE_Z - 0.0035
    t = BAL_ARM_T / 2
    xe = XH - BAL_REACH + BAL_L / 2
    zc = HINGE_Z + BAL_DZ
    sg = 1 if side == 'U' else -1
    A = (xr, zr_ + sg * t)
    Bp = (xe, zc + sg * t)
    p0 = _rot_pt((A[0] + (Bp[0] - A[0]) * BOSS_S[0], A[1] + (Bp[1] - A[1]) * BOSS_S[0]), a)
    p1 = _rot_pt((A[0] + (Bp[0] - A[0]) * BOSS_S[1], A[1] + (Bp[1] - A[1]) * BOSS_S[1]), a)
    top = lambda p: (p[0], _out(side, p[0], CAP_WALL * 0.5))
    return _ccw([p0, p1, top(p1), top(p0)])


CAP_FL_W, CAP_FL_T = 0.003, 0.0004          # bonding flange: 3 mm wide, 0.4 mm thick on both y sides and the fore end (none at the aft end: it faces the elevon)


def cap_flange_loops(side):
    """(side strip loop along x, fore strip loop) in the XZ plane: thin band on the skin."""
    xs, ho = cap_profile(side)
    band = [(x, _skin(side, x)) for x in xs] + [(x, _out(side, x, CAP_FL_T)) for x in xs[::-1]]
    fore = [(xs[0] - CAP_FL_W, _skin(side, xs[0] - CAP_FL_W)), (xs[0], _skin(side, xs[0])), (xs[0], _out(side, xs[0], CAP_FL_T)), (xs[0] - CAP_FL_W, _out(side, xs[0] - CAP_FL_W, CAP_FL_T))]
    return _ccw(band), _ccw(fore)


def cap_mass_g(side):
    L = cap_loop(side)[0]
    a_arch = abs(_poly_area(L))
    a_end = abs(_poly_area(cap_end_loop(side)))
    ly = CAP_Y1 - CAP_Y0
    vol = a_arch * (ly - 2 * CAP_WALL) + 2 * a_end * CAP_WALL
    bl = boss_loop(side)
    vol += 2 * abs(_poly_area(bl)) * BOSS_W
    fb, ff = cap_flange_loops(side)
    vol += 2 * abs(_poly_area(fb)) * CAP_FL_W + abs(_poly_area(ff)) * (CAP_Y1 - CAP_Y0 + 2 * CAP_FL_W)
    return vol * 1e6 * RHO_PETG


# hinge viscous damper (coaxial shear drum on the hinge axis, in the 22 mm gap between the elevon tip and the fin, fluid 12,500 cSt, mu 12.2 Pa s)
DMP_YE = ELEV_Y1 - GAP_Y                    # elevon tip face y
DMP_R_OUT, DMP_R_BORE, DMP_R_SLV, DMP_T_SLV, DMP_R_PIN, DMP_R_PIN_I = 0.00635, 0.00555, 0.00500, 0.0005, 0.00445, 0.0032
DMP_FLANGE = (DMP_YE, DMP_YE + 0.0010)      # rotor flange disc bonded on the elevon tip face
DMP_SLV = (DMP_YE + 0.0010, DMP_YE + 0.0180)    # rotor sleeve 17 mm
DMP_H0, DMP_H1 = DMP_YE + 0.0012, DMP_YE + 0.0195   # housing tube y range; fin-side end disc is the last 0.8 mm
DMP_MU = 12.2                               # Pa s: 12,500 cSt x 0.974 (Dow PMX-200 / Clearco PSF-12500 data sheets, read 2026-11-15)
DMP_GAP = DMP_R_BORE - (DMP_R_SLV + DMP_T_SLV / 2)
DMP_L_ACT = 0.0160                          # sleeve length inside both gaps (overlap with the pin and bore)
DMP_STATOR_G = round(((math.pi * (DMP_R_OUT ** 2 - DMP_R_BORE ** 2) * (DMP_H1 - DMP_H0) + math.pi * DMP_R_OUT ** 2 * 0.0008 + math.pi * (DMP_R_PIN ** 2 - DMP_R_PIN_I ** 2) * 0.0165) * 1e6 * RHO_PETG)
                     + 2 * math.pi * DMP_R_SLV * DMP_GAP * DMP_L_ACT * 1e6 * 0.974 + 0.4, 1)      # housing + pin + fluid in both gaps + 0.4 g strips (silicone, EST)
DMP_ROTOR_G = round((math.pi * (DMP_R_SLV + DMP_T_SLV / 2) ** 2 - math.pi * (DMP_R_SLV - DMP_T_SLV / 2) ** 2) * 0.0170 * 1e6 * RHO_PETG + math.pi * 0.0056 ** 2 * 0.0010 * 1e6 * RHO_PETG, 1)
DMP_C = 2 * math.pi * DMP_MU * DMP_L_ACT * ((DMP_R_SLV - DMP_T_SLV / 2) ** 3 / (DMP_R_SLV - DMP_T_SLV / 2 - DMP_R_PIN) + (DMP_R_SLV + DMP_T_SLV / 2) ** 3 / DMP_GAP)   # N m s/rad per elevon, 25 C, both gaps



# ------------------------------------------------------------------ wing / fins / cage parts
# wing (MASS-GATE 220 allocation; STRUCTURES iteration 2: 191 g)
P('WNG-001', 'Wing core, XPS 25 kg/m3 + tape skin + glue + hinge tape (lumped)', 'wing', 102.0, 'XPS foam 25 kg/m3 + packing tape')   # QP-4 FIXES item 3: 116 - 13.7 (foam 82 g x 5/30) - 0.3 (elevon span moved 10 mm)
P('WNG-002', 'Spar, CF tube 12x10 x 0.90 m', 'wing', round(tube_g(0.90, SPAR_OD, SPAR_ID), 1), 'CFRP tube')
for pid, nm in (('WNG-003-C', 'centre'), ('WNG-004-R', 'right strut'), ('WNG-004-L', 'left strut'),
                ('WNG-005-R', 'right rib'), ('WNG-005-L', 'left rib')):
    P(pid, 'Spar plug (%s clamp)' % nm, 'wing', 1.2, 'PETG (printed)')   # QP-4 FIXES 1.65 -> 1.2 g (1.2 mm wall, EST)
P('WNG-006-R', 'Elevon right', 'wing', 8.0, 'XPS foam + tape')   # 8.5 - 0.73 (foam 4.4 g x 5/30) + 0.26 (10 mm more span)
P('WNG-006-L', 'Elevon left', 'wing', 8.0, 'XPS foam + tape')
for s_ in 'RL':
    P('WNG-007-' + s_, 'Elevon balance (D-187 v2, %s): 15.6 g lead strip 20 mm ahead of the hinge + 2 PETG/CF tabs 0.5 g (caps are separate parts WNG-008)' % s_, 'wing', 16.1, 'lead + PETG/CF')
    for sd in 'UL':      # FIXES2: lens caps with the mechanical stop bosses (mass from the drawn volume, PETG 1.27 g/cm3)
        P('WNG-008-%s%s' % (s_, sd), 'Lens cap + stop bosses (%s, %s skin): wall %.1f mm, >= %.1f mm clearance to the lead at the +-%.0f deg stop' % (s_, 'upper' if sd == 'U' else 'lower', CAP_WALL * 1e3, CAP_CLR * 1e3, ELEV_STOP),
          'wing', round(cap_mass_g(sd), 1), 'PETG (printed)')
    P('WNG-009-' + s_, 'Hinge damper stator (%s): printed housing + pin, 12,500 cSt silicone fluid, 2 silicone preload strips' % s_, 'wing', DMP_STATOR_G, 'PETG + silicone')
    P('WNG-010-' + s_, 'Hinge damper rotor (%s): sleeve + flange bonded on the elevon tip' % s_, 'wing', DMP_ROTOR_G, 'PETG (printed)')
# fins (allocation 70 g; STRUCTURES iteration 2: 119 g)
for s in 'RL':
    P('FIN-001-' + s, 'Fin tube 16x14 x 0.36 m (%s)' % s, 'fins', round(tube_g(0.36, FIN_OD, FIN_ID), 1), 'CFRP tube')
    P('FIN-002-' + s, 'Fin rib tube 14x12 (%s)' % s, 'fins', 14.8, 'CFRP tube')      # DOC 14x12 x 0.227 = 14.8 g
    P('FIN-003-' + s, 'Fin root block (%s)' % s, 'fins', 3.2, 'PETG (printed)')
    P('FIN-004-' + s, 'Fin fairing 3 mm XPS + tape (%s)' % s, 'fins', 8.4, 'XPS foam + tape')
    P('FIN-005-' + s, 'Rib saddle on spar (%s)' % s, 'fins', 1.0, 'PETG (printed)')
# cage (allocation 135; STRUCTURES iteration 2: 122 g)
P('CGE-001', 'Hub disc (printed shell, envelope; QP-4 FIXES: 16 -> 13 g, 2 perimeters, 10 % infill, EST)', 'cage', 13.0, 'PETG (printed)')
for s in ST:
    P('CGE-002-' + s, 'Arm 12x10 x 0.245 (%s)' % s, 'cage', round(tube_g(0.245, ARM_OD, ARM_ID), 1), 'CFRP tube')
    P('CGE-003-' + s, 'Motor cup (%s; QP-4 FIXES 5 -> 4 g, EST, C1 to re-check prop-strike)' % s, 'cage', 4.0, 'PETG (printed)')
P('CGE-004', 'Bridge 12x10', 'cage', round(tube_g(BR_X1 - BR_X0, BR_OD, BR_ID), 1), 'CFRP tube')
for s in 'RL':
    P('CGE-005-' + s, 'V strut 6x4.5 (%s)' % s, 'cage', 6.5, 'CFRP tube')
    P('CGE-007-' + s, 'Strut clamp on spar (%s)' % s, 'cage', 1.5, 'PETG (printed)')
P('CGE-006', 'Bridge saddle on spar', 'cage', 2.0, 'PETG (printed)')
P('CGE-008', 'Pack tray (66 x 109 mm plate, trim slots; 4.0 g at 44 mm scaled by plate area + longer walls, EST)', 'cage', 3.8, 'PETG (printed)')   # QP-4 FIXES 5.3 -> 3.8 g: 1.5 mm floor with ribs, EST

# ------------------------------------------------------------------ wing / fins / cage edges
# wing
E('E-WNG-01', 'WNG-002', 'WNG-001', EPX, 'wing', 'spar bonded in its bore; build rule: bond over |y| <= 0.20 m (FIXES2: 0.15 m gave foam shear 78 kPa, MS +0.11 at the board allowable 103 kPa scale; 0.20 m gives 58 kPa, MS +0.48)')
for pid in ('WNG-003-C', 'WNG-004-R', 'WNG-004-L', 'WNG-005-R', 'WNG-005-L'):
    E(en('WNG'), pid, 'WNG-002', EPX, 'wing', 'plug in the spar bore under a clamp (C2 rule)')
for s in 'RL':
    E('E-WNG-1' + ('0' if s == 'R' else '1'), 'WNG-006-' + s, 'WNG-001', 'CT-TAPE-HINGE', 'wing', 'tape hinge, upper surface',
      motion=dict(axis='Y', range_deg=[-ELEV_POSE, ELEV_POSE]))
for s in 'RL':
    E('E-WNG-2' + ('0' if s == 'R' else '1'), 'WNG-007-' + s, 'WNG-006-' + s, EPX, 'wing', 'balance horn root bonded to the elevon nose face (D-187)')
    for k_, sd in enumerate('UL'):
        E('E-WNG-3%d%s' % (k_, s), 'WNG-008-%s%s' % (s, sd), 'WNG-001', EPX, 'wing', 'lens cap flange bonded on the tape skin over the strip window; the stop bosses pass through the window to the tab (FIXES2)')
    E('E-WNG-4' + s, 'WNG-009-' + s, 'WNG-001', EPX, 'wing', 'damper housing bonded in the core notch at the elevon tip, axis on the hinge line (FIXES2)')
    E('E-WNG-5' + s, 'WNG-010-' + s, 'WNG-006-' + s, EPX, 'wing', 'damper rotor flange bonded on the elevon tip face (FIXES2)')
    E('E-WNG-6' + s, 'WNG-010-' + s, 'WNG-009-' + s, EPX, 'wing', 'rotor sleeve in the fluid-filled annulus of the stator, 0.30 mm gaps, not bonded (modelled as a bonded contact so the sequence check sees support; FIXES2)')
# fins
for s in 'RL':
    E(en('FIN'), 'FIN-003-' + s, 'FIN-001-' + s, EPX, 'fins', 'root block wraps the tube')
    E(en('FIN'), 'FIN-003-' + s, 'FIN-002-' + s, EPX, 'fins', 'rib end in the block socket')
    E(en('FIN'), 'FIN-002-' + s, 'FIN-005-' + s, EPX, 'fins', 'rib start in the saddle socket')
    E(en('FIN'), 'FIN-005-' + s, 'WNG-002', EPX, 'fins', 'saddle wraps the spar (60 mm)')
    E(en('FIN'), 'FIN-004-' + s, 'FIN-001-' + s, CA, 'fins', 'fairing in the tube slot (foam-safe CA)')
    E(en('FIN'), 'FIN-004-' + s, 'FIN-002-' + s, CA, 'fins', 'fairing round the rib')
# cage
for s in ST:
    E(en('CGE'), 'CGE-002-' + s, 'CGE-001', EPX, 'cage', 'arm in hub socket')
    E(en('CGE'), 'CGE-002-' + s, 'CGE-003-' + s, EPX, 'cage', 'arm end in cup sleeve (25 mm)')
E(en('CGE'), 'CGE-004', 'CGE-001', EPX, 'cage', 'bridge in hub')
E(en('CGE'), 'CGE-004', 'CGE-006', EPX, 'cage', 'bridge end in saddle boss')
E(en('CGE'), 'CGE-006', 'WNG-002', EPX, 'cage', 'saddle wraps the spar (30 mm)')
for s in 'RL':
    E(en('CGE'), 'CGE-005-' + s, 'CGE-001', EPX, 'cage', 'strut in hub')
    E(en('CGE'), 'CGE-005-' + s, 'CGE-007-' + s, EPX, 'cage', 'strut end in clamp boss')
    E(en('CGE'), 'CGE-007-' + s, 'WNG-002', EPX, 'cage', 'clamp wraps the spar')
E(en('CGE'), 'CGE-008', 'CGE-001', EPX, 'cage', 'pack tray bonded to the hub aft face and seated in the core tray slot')


# ------------------------------------------------------------------ geometry builders
def build_wing(ctx):
    core = ctx.part('WNG-001', rgb=(0.85, 0.85, 0.80))
    core.loft('Y', [(-B / 2, core_loop()), (B / 2, core_loop())], smooth=False, name='core box')
    spar = ctx.part('WNG-002', rgb=(0.1, 0.1, 0.1))
    spar.tube('Y', (SPAR_X, -B / 2, 0.0), B, SPAR_OD / 2, SPAR_ID / 2, name='spar tube')
    for pid, y in (('WNG-003-C', 0.0), ('WNG-004-R', 0.30), ('WNG-004-L', -0.30), ('WNG-005-R', YFIN), ('WNG-005-L', -YFIN)):
        pl = ctx.part(pid, rgb=(0.9, 0.9, 0.9))
        pl.tube('Y', (SPAR_X, y - 0.010, 0.0), 0.020, PLUG_R, 0.002, name='plug')
    ev = ctx.part('WNG-006-R', rgb=(0.95, 0.5, 0.1))
    k9.elevon(ev, COORDS, C, 1 - ELEV_FRAC, ELEV_Y0, ELEV_Y1, gap=GAP_Y)
    ctx.mirror('WNG-006-R', 'WNG-006-L', plane='XZ')
    bw = ctx.part('WNG-007-R', rgb=(0.35, 0.35, 0.4))
    for dy_ in (-BAL_ARM_DY, BAL_ARM_DY):
        bw.prism('Y', BAL_YC + dy_ - BAL_ARM_W / 2, [bal_arm_loop()], BAL_ARM_W, name='balance horn tab')
    bw.prism('Y', BAL_YC - BAL_W / 2, [bal_lead_loop()], BAL_W, name='balance lead block')
    ctx.mirror('WNG-007-R', 'WNG-007-L', plane='XZ')
    for sd in 'UL':                                       # FIXES2: lens caps with stop bosses (right side; left by mirror)
        cp = ctx.part('WNG-008-R' + sd, rgb=(0.8, 0.8, 0.85))
        wl = CAP_WALL
        cp.prism('Y', CAP_Y0 + wl, [cap_loop(sd)[0]], CAP_Y1 - CAP_Y0 - 2 * wl, name='lens cap arch')
        cp.prism('Y', CAP_Y0, [cap_end_loop(sd)], wl, name='lens cap end wall')
        cp.prism('Y', CAP_Y1 - wl, [cap_end_loop(sd)], wl, name='lens cap end wall')
        for dy_ in (-BAL_ARM_DY, BAL_ARM_DY):
            cp.prism('Y', BAL_YC + dy_ - BOSS_W / 2, [boss_loop(sd)], BOSS_W, name='mechanical stop boss')
        fb_, ff_ = cap_flange_loops(sd)
        cp.prism('Y', CAP_Y0 - CAP_FL_W, [fb_], CAP_FL_W, name='cap bonding flange')
        cp.prism('Y', CAP_Y1, [fb_], CAP_FL_W, name='cap bonding flange')
        cp.prism('Y', CAP_Y0 - CAP_FL_W, [ff_], CAP_Y1 - CAP_Y0 + 2 * CAP_FL_W, name='cap bonding flange (fore)')
        ctx.mirror('WNG-008-R' + sd, 'WNG-008-L' + sd, plane='XZ')
    for sd in 'UL':                                       # core pockets for the bosses (grown 0.3 mm) so they sit in air
        for sy in (1, -1):
            for dy_ in (-BAL_ARM_DY, BAL_ARM_DY):
                yc_ = sy * (BAL_YC + dy_)
                bl = boss_loop(sd)
                cx_ = sum(p[0] for p in bl) / 4.0
                cz_ = sum(p[1] for p in bl) / 4.0
                gl = [(p[0] + (p[0] - cx_) / math.hypot(p[0] - cx_, p[1] - cz_) * 0.0003, p[1] + (p[1] - cz_) / math.hypot(p[0] - cx_, p[1] - cz_) * 0.0003) for p in bl]
                core.cut_prism('Y', yc_ - BOSS_W / 2 - 0.0003, [_ccw(gl)], BOSS_W + 0.0006, name='stop boss pocket')
    ro = ctx.part('WNG-010-R', rgb=(0.9, 0.6, 0.2))        # hinge damper: rotor sleeve + flange on the elevon tip, stator housing in a core notch
    ro.tube('Y', (XH, DMP_SLV[0], HINGE_Z), DMP_SLV[1] - DMP_SLV[0], DMP_R_SLV + DMP_T_SLV / 2, DMP_R_SLV - DMP_T_SLV / 2, name='damper rotor sleeve')
    ro.cylinder('Y', (XH, DMP_FLANGE[0], HINGE_Z), DMP_FLANGE[1] - DMP_FLANGE[0], 0.0056, name='damper rotor flange')
    ctx.mirror('WNG-010-R', 'WNG-010-L', plane='XZ')
    st = ctx.part('WNG-009-R', rgb=(0.5, 0.6, 0.7))
    st.tube('Y', (XH, DMP_H0, HINGE_Z), DMP_H1 - DMP_H0, DMP_R_OUT, DMP_R_BORE, name='damper housing')
    st.cylinder('Y', (XH, DMP_H1 - 0.0008, HINGE_Z), 0.0008, DMP_R_OUT, name='damper end disc')
    st.tube('Y', (XH, DMP_H1 - 0.0008, HINGE_Z), -0.0165, DMP_R_PIN, DMP_R_PIN_I, name='damper stator pin')
    ctx.mirror('WNG-009-R', 'WNG-009-L', plane='XZ')
    for sy in (1, -1):                                    # notch in the core for the housing and flange (the core ends at the hinge x = XH here)
        ya, yb = sorted((sy * (DMP_YE - 0.0003), sy * (DMP_H1 + 0.0004)))
        core.cut_box((XH - DMP_R_OUT - 0.0004, ya, HINGE_Z - DMP_R_OUT - 0.0004), (XH + 0.001, yb, HINGE_Z + 0.001), name='elevon-tip damper notch')
    for sy in (1, -1):                                    # pocket for the balance horn and lead over the full elevon travel
        ya, yb = sorted((sy * (BAL_YC - BAL_W / 2 - 0.001), sy * (BAL_YC + BAL_W / 2 + 0.001)))
        core.cut_prism('Y', ya, [bal_sweep_loop()], yb - ya, name='elevon balance pocket (strip window)')
    for sy in (1, -1):                                    # servo pocket open to the upper skin (arm sweep too)
        y0, y1 = sorted((sy * SERVO_Y - 0.0225, sy * SERVO_Y + 0.0225))
        core.cut_box((0.1245, y0, SV_Z1), (0.1655, y1, 0.020), name='servo pocket')
    core.cut_box((0.0, -0.0065, -0.05), (0.056, 0.0065, 0.0075), name='bridge slot (open below)')
    core.cut_box((-0.010, -0.0555, 0.0055), (0.0225, 0.0555, 0.050), name='pack tray slot (open above)')
    core.cut_box((0.0295, -0.0165, -0.05), (0.0710, 0.0165, 0.0115), name='saddle slot (open below)')
    core.cut_box((0.0335, 0.2705, -0.05), (0.0710, 0.3095, 0.0075), name='clamp slot R (open below)')
    core.cut_box((0.0335, -0.3095, -0.05), (0.0710, -0.2705, 0.0075), name='clamp slot L (open below)')
    for sg in (1, -1):
        y0, y1 = sorted((sg * (YFIN - 0.0305), sg * (YFIN + 0.0305)))
        core.cut_box((0.0485, y0, -0.05), (0.0910, y1, 0.0115), name='rib saddle slot (open below)')
        d = (STRUT_E[0] - STRUT_S[0], STRUT_E[1] - STRUT_S[1])
        L_ = math.hypot(*d)
        ux, uy = d[0] / L_, d[1] / L_
        nx, ny = -uy * 0.0050, ux * 0.0050
        p0 = (-0.012, STRUT_S[1] + (-0.012 - STRUT_S[0]) / ux * uy)
        p1 = (STRUT_E[0], STRUT_E[1])
        loop = [(p0[0] + nx, sg * (p0[1] + ny)), (p1[0] + nx, sg * (p1[1] + ny)), (p1[0] - nx, sg * (p1[1] - ny)),
                (p0[0] - nx, sg * (p0[1] - ny))]
        core.cut_prism('Z', -0.05, [loop], 0.055, name='strut slot (open below, 0.5 mm clear)')
    guests = ['WNG-002', 'CGE-004', 'CGE-005-R', 'CGE-005-L', 'CGE-006', 'CGE-007-R', 'CGE-007-L', 'FIN-002-R', 'FIN-002-L',
              'FIN-005-R', 'FIN-005-L', 'AVN-006', 'MEC-001-R', 'MEC-001-L', 'CGE-008']
    for g in guests:
        ctx.seat('WNG-001', g, 'groove / bore / pocket cut in the core for ' + g, shop=True)


def sg_(s):
    return 1 if s == 'R' else -1


def build_fins(ctx):
    t = ctx.part('FIN-001-R', rgb=(0.1, 0.1, 0.1))
    t.tube('Z', (XFIN_T, YFIN, -FIN_H), 2 * FIN_H, FIN_OD / 2, FIN_ID / 2, name='fin tube')
    ctx.mirror('FIN-001-R', 'FIN-001-L', plane='XZ')
    r = ctx.part('FIN-002-R', rgb=(0.1, 0.1, 0.1))
    r.tube('X', (RIB_X0, YFIN, 0.0), RIB_X1 - RIB_X0, RIB_OD / 2, RIB_ID / 2, name='rib tube')
    ctx.mirror('FIN-002-R', 'FIN-002-L', plane='XZ')
    b = ctx.part('FIN-003-R', rgb=(0.9, 0.9, 0.9))
    b.tube('Z', (XFIN_T, YFIN, -0.03), 0.06, 0.0115, FIN_OD / 2, name='root block ring')
    b.box((0.2550, YFIN - 0.0095, -0.0095), (RIB_X1, YFIN + 0.0095, 0.0095), name='root block rib socket')
    ctx.mirror('FIN-003-R', 'FIN-003-L', plane='XZ')
    f = ctx.part('FIN-004-R', rgb=(0.95, 0.95, 0.8))
    f.box((XH + 0.0003, YFIN - 0.0015, -FIN_H), (XFIN_T, YFIN + 0.0015, FIN_H), name='fairing')
    ctx.mirror('FIN-004-R', 'FIN-004-L', plane='XZ')
    sdl = ctx.part('FIN-005-R', rgb=(0.9, 0.9, 0.9))
    sdl.tube('Y', (SPAR_X, YFIN - 0.030, 0.0), 0.060, 0.0105, SPAR_OD / 2, name='rib saddle ring')
    sdl.box((0.0665, YFIN - 0.0095, -0.0095), (0.0905, YFIN + 0.0095, 0.0095), name='rib saddle socket')
    sdl.cut_box((SPAR_X - 0.0065, YFIN - 0.031, 0.0), (SPAR_X + 0.0065, YFIN + 0.031, 0.012), name='clip slot')
    ctx.mirror('FIN-005-R', 'FIN-005-L', plane='XZ')
    for s in 'RL':
        for g, note in (('FIN-001-' + s, 'tube slot'), ('FIN-003-' + s, 'block notch')):
            ctx.seat('FIN-004-' + s, g, 'fairing ' + note)
        ctx.components['FIN-004-' + s].cut_cylinder('X', (XH, sg_(s) * YFIN, 0.0), XFIN_T - XH, 0.0075, name='rib groove (0.5 mm clearance)')
        ctx.seat('FIN-003-' + s, 'FIN-001-' + s, 'block bore on the tube')
        ctx.seat('FIN-003-' + s, 'FIN-002-' + s, 'block rib socket')
        ctx.seat('FIN-005-' + s, 'WNG-002', 'saddle bore on the spar')
        ctx.seat('FIN-005-' + s, 'FIN-002-' + s, 'saddle rib socket')
    for st in ST:
        ctx.seat('FIN-004-' + ('R' if ST[st][0] > 0 else 'L'), 'GER-001-' + st, 'fairing notch for the shoe')


def build_cage(ctx):
    hub = ctx.part('CGE-001', rgb=(0.9, 0.9, 0.9))
    hub.cylinder('X', (HUB_X0, 0.0, 0.0), HUB_X1 - HUB_X0, HUB_R, name='hub disc')
    for st in ST:
        arm = ctx.part('CGE-002-' + st, at=HUB, rotate=('X', PHI[st]), rgb=(0.1, 0.1, 0.1))
        arm.tube('Y', (0.0, R_IN, 0.0), R_M - R_IN, ARM_OD / 2, ARM_ID / 2, name='arm tube')
        cup = ctx.part('CGE-003-' + st, at=station(st), rotate=mrot(st), rgb=(0.9, 0.9, 0.9))
        cup.box((-0.012, -0.0165, -0.0165), (-0.007, 0.0165, 0.0165), name='cup motor plate')
        cup.tube('Y', (0.0, -0.025, 0.0), 0.0285, 0.0095, ARM_OD / 2, name='cup arm sleeve')
        cup.cut_cylinder('X', (-0.0125, 0.0, 0.0135), 0.006, 0.003, name='lead hole')
        ctx.seat('CGE-003-' + st, 'CGE-002-' + st, 'arm socket')
        ctx.seat('CGE-001', 'CGE-002-' + st, 'arm socket in the hub')
    br = ctx.part('CGE-004', rgb=(0.1, 0.1, 0.1))
    br.tube('X', (BR_X0, 0.0, 0.0), BR_X1 - BR_X0, BR_OD / 2, BR_ID / 2, name='bridge tube')
    ctx.seat('CGE-001', 'CGE-004', 'bridge socket in the hub')
    d = (STRUT_E[0] - STRUT_S[0], STRUT_E[1] - STRUT_S[1])
    L = math.hypot(*d)
    ang = math.degrees(math.atan2(d[1], d[0]))
    for s, sg in (('R', 1), ('L', -1)):
        st_ = ctx.part('CGE-005-' + s, at=(STRUT_S[0], sg * STRUT_S[1], 0.0), rotate=('Z', sg * ang), rgb=(0.1, 0.1, 0.1))
        st_.tube('X', (0.0, 0.0, 0.0), L, STRUT_OD / 2, STRUT_ID / 2, name='strut tube')
        ctx.seat('CGE-001', 'CGE-005-' + s, 'strut socket in the hub')
        ctx.components['WNG-001'].cut(fk.Shape('revolve', 'strut groove (0.5 mm per side clearance)', axis='X', center=(0.0, 0.0, 0.0),
                                               profile=[(0.0, 0.0), (L + 0.002, 0.0), (L + 0.002, STRUT_OD / 2 + 0.0005),
                                                        (0.0, STRUT_OD / 2 + 0.0005)]), st_.matrix(), 'strut groove, bonded slip fit clearance EST')
        ctx.seat('CGE-007-' + s, 'CGE-005-' + s, 'strut socket in the clamp')
        ctx.seat('CGE-007-' + s, 'WNG-002', 'clamp bore on the spar')
    sd = ctx.part('CGE-006', rgb=(0.9, 0.9, 0.9))
    sd.tube('Y', (SPAR_X, -0.015, 0.0), 0.030, 0.0105, SPAR_OD / 2, name='saddle ring')
    sd.box((0.030, -0.0085, -0.0085), (0.0535, 0.0085, 0.0085), name='saddle bridge socket')
    sd.cut_box((SPAR_X - 0.0065, -0.016, 0.0), (SPAR_X + 0.0065, 0.016, 0.012), name='clip slot')
    ctx.seat('CGE-006', 'WNG-002', 'saddle bore on the spar')
    ctx.seat('CGE-006', 'CGE-004', 'saddle bridge socket')
    cl = ctx.part('CGE-007-R', rgb=(0.9, 0.9, 0.9))
    cl.tube('Y', (SPAR_X, 0.292, 0.0), 0.016, 0.0095, SPAR_OD / 2, name='clamp ring')
    cl.box((0.034, 0.272, -0.0055), (0.0535, 0.300, 0.0055), name='clamp strut socket')
    cl.cut_box((SPAR_X - 0.0065, 0.291, 0.0), (SPAR_X + 0.0065, 0.309, 0.012), name='clip slot')
    ctx.mirror('CGE-007-R', 'CGE-007-L', plane='XZ')
    tr = ctx.part('CGE-008', rgb=(0.9, 0.9, 0.9))
    tr.box((-0.045, -0.0545, 0.006), (TRAY_X1, 0.0545, 0.008), name='tray plate')
    tr.box((PACK_X[0] - TRIM, 0.0525, 0.008), (PACK_X[1] + TRIM, 0.0545, 0.030), name='tray end wall R')
    tr.box((PACK_X[0] - TRIM, -0.0545, 0.008), (PACK_X[1] + TRIM, -0.0525, 0.030), name='tray end wall L')
    tr.box((PACK_X[0] - 0.002, -0.0545, 0.008), (PACK_X[0], 0.0545, 0.020), name='tray front lip')
    tr.box((PACK_X[1], -0.0545, 0.008), (PACK_X[1] + 0.002, 0.0545, 0.018), name='tray rear lip')
    for xl in (PACK_X[0] - 0.001, PACK_X[1] + 0.001):          # trim slots: the M3 lip bolts slide +-TRIM (lips re-bolt with the pack)
        for sy_ in (1, -1):
            tr.cut_box((xl - TRIM - 0.0017, sy_ * 0.040 - 0.0017, 0.005), (xl + TRIM + 0.0017, sy_ * 0.040 + 0.0017, 0.009), name='trim slot')
