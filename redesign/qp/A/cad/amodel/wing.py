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
# LEGACY D-193 hub constants (R_IN .. HUB_SPOKE_D): superseded by the D-202 hub below; kept only so structures/fea_arm.py (the D-201 FEA of the old hub) still imports. Not used by the CAD.
R_IN = R_M - 0.245                          # DOC: arm tube 0.245 long (D-193 four separate arms)
HUB_X0, HUB_X1 = -0.102, -0.045             # D-193 hub x range; HUB_X1 (aft face = tray face, x -0.045) is still the aft face of the D-202 hub
HUB_W = 0.0008                              # EST printed wall = 2 perimeters at 0.4 mm (the QP-4 FIXES basis of the 13 g hub); at 1.2 mm (3 perimeters) the drawn hub is 19.1 g
HUB_SOCK_W = 0.002                          # D-196: arm-socket boss wall 2.0 mm (5 perimeters); 0.8 mm failed the hoop check (structures/qp5_checks.md s2, MS -0.58)
HUB_RB = 0.006 + HUB_SOCK_W                 # arm-socket boss outer radius over the mouth zone (8.0 mm)
HUB_MOUTH = 0.012                           # D-196: 2.0 mm wall over the outer 12 mm of the socket (the bearing patch of qp5_checks s2); deeper the boss steps to the 0.8 mm wall
HUB_RBI = 0.006 + HUB_W                     # arm-socket boss outer radius inboard of the mouth zone (6.8 mm)
HUB_SLV_W = 0.0012                          # D-196: bridge-sleeve wall 1.2 mm (3 perimeters), structures/qp5_checks.md s2b
HUB_RS = 0.006 + HUB_SLV_W                  # bridge-sleeve outer radius (7.2 mm)
HUB_SOCK = 0.025                            # arm socket depth 25 mm (STRUCTURES iter 2 iter2_margins.py assumes 25 mm; the old disc gave 18.8 mm)
HUB_ARM_R0 = R_IN - 0.002                   # arm socket floor (2 mm)
HUB_ARM_R1 = R_IN + HUB_SOCK                # open mouth of the arm socket (r 56.2 mm)
HUB_SPOKE_D = 0.022                         # radial web depth along x (sleeve to socket), one wall (HUB_W) thick
HUB_STRUT_S = (-0.017, 0.032)               # strut socket: from 17 mm behind the strut end (web to the bridge sleeve) to 32 mm ahead (30 mm socket)
PACK_XL_, PACK_ZL_ = 0.0015, 0.009 + 0.0230   # lead exit x and z (= electrical.PACK_XL, PACK_ZL; keep equal)
CUP_PAT = (0.019, 0.016)                    # MN2212 mounting pattern 19 mm (along the arm, y) x 16 mm (z): retailers list 16x19 and 19x25 (getfpv MN2212 V2.0 page, search 2026-11-15; T-Motor drawing: 4-M2.5 on 19 x 16 (read 2026-11-15); cup holes M2.5 clearance 2.9 mm, D-194)
CUP_R = 0.006                               # plate corner radius (EST)
CUP_FIL = 0.001                             # D-210: fillet on the cup's sleeve-to-plate junction (the FEA's S2 / S3 hotspot was the sharp corner)


def cup_fillet_loops(xf=-0.007, ro=0.0096, rho=CUP_FIL, ys=0.0035, e=0.00005, n=12):
    """D-210 fillet prisms for the motor cup (cup frame: plate rear face x = xf, sleeve r ro about y, sleeve end y = ys).
    Returns (along, chord, zc): two (x, z) loops for the fillets along the arm (z > 0, z < 0) and one (x, y) loop for the fillet
    where the sleeve end meets the plate (extruded along z over |z| <= zc). Each loop reaches e = 0.05 mm into the plate and the
    sleeve (D-198: no coincident faces). Same geometry as structures/fea_arm.py _cup (OpenCASCADE fillet)."""
    cx = xf + rho
    cz = math.sqrt((ro + rho) ** 2 - cx ** 2)
    t2 = (cx * ro / (ro + rho), cz * ro / (ro + rho))
    a0 = math.atan2(t2[1] - cz, t2[0] - cx); a1 = math.pi
    if a1 - a0 > math.pi:
        a1 -= 2 * math.pi
    arc = [(cx + rho * math.cos(a0 + (a1 - a0) * k / n), cz + rho * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
    zi = math.sqrt((ro - e) ** 2 - (xf - e) ** 2)
    ti = math.atan2(t2[1], t2[0]); t0 = math.atan2(zi, xf - e)
    inner = [((ro - e) * math.cos(t0 + (ti - t0) * k / n), (ro - e) * math.sin(t0 + (ti - t0) * k / n)) for k in range(n + 1)]
    up = [(xf - e, cz)] + [(xf - e, zi)] + inner[1:] + arc
    down = [(x, -z) for x, z in reversed(up)]
    return up, down, cup_chord_loop(xf, ys, rho, e, n), math.sqrt(ro ** 2 - xf ** 2)


def cup_chord_loop(xf=-0.007, ys=0.0035, rho=CUP_FIL, e=0.00005, n=12):
    """(x, y) loop of a 1 mm fillet between an end face y = ys (material below, x > xf) and the plate rear face x = xf (extrude along z)."""
    cx = xf + rho
    return [(xf - e, ys - e), (cx, ys - e)] + [(cx + rho * math.cos(-math.pi / 2 - (math.pi / 2) * k / n),
                                               ys + rho + rho * math.sin(-math.pi / 2 - (math.pi / 2) * k / n)) for k in range(n + 1)] + [(xf - e, ys + rho)]


def cup_web_loop(xf=-0.007, rc=0.0070, rho=CUP_FIL, e=0.00005, n=12):
    """D-210: (x, z) loop of the web that joins the lead collar (r rc, tangent to the plate face x = xf) to the plate: the cusp between
    them filled, with a fillet of radius rho on each side (the bare tangent line was a knife-edge joint; FEA d210 peak). Extrude along y
    over the collar and its end cap. Returns (loop, z of the web edge at x = xf + rho / 2)."""
    cx = xf + rho
    cz = math.sqrt((rc + rho) ** 2 - cx ** 2)
    a_t2 = math.atan2(-cz, -cx)                                   # from the fillet centre towards the collar axis
    arc = [(cx + rho * math.cos(math.pi + (a_t2 + 2 * math.pi - math.pi) * k / n), cz + rho * math.sin(math.pi + (a_t2 + 2 * math.pi - math.pi) * k / n)) for k in range(n + 1)]
    th = math.atan2(arc[-1][1], arc[-1][0])
    circ = [((rc - e) * math.cos(th + (2 * math.pi - 2 * th) * k / (2 * n)), (rc - e) * math.sin(th + (2 * math.pi - 2 * th) * k / (2 * n))) for k in range(2 * n + 1)]
    low = [(x, -z) for x, z in reversed(arc)]
    loop = [(xf - e, cz)] + arc + circ[1:-1] + low + [(xf - e, -cz)]
    return loop, cz - math.sqrt(rho ** 2 - (rho / 2) ** 2)
ARM_OD, ARM_ID = 0.012, 0.010               # DOC iteration 2: arms 12x10
BR_OD, BR_ID, BR_X1 = 0.016, 0.014, 0.054       # D-206: bridge 16x14 (was 12x10): torsion (structures/bridge_torsion_d206.md); cut from the R02 16x14 fin-tube offcut
BR_RO, BR_RI = BR_OD / 2, BR_ID / 2
BR_Z = -0.002                               # D-206: bridge axis 2 mm below the hub axis, so the 16 mm tube top stays tangent to the tray plate underside (z 6.0)
BORE_X0 = HUB[0] + 0.015                    # bridge bore floor 15 mm aft of the hub axis; floor corner a 45 deg cone matching the tube's BR_CHAMFER (D-207, FEA run d209)
BR_X0 = BORE_X0                             # D-207: the bridge seats on the bore floor, its chamfer on the conical corner (a 1 mm gap, FEA d208, doubled the peak at the tube end edge). D-202 note: D-202: the bridge starts 15 mm aft of the hub axis (x -0.060), bonded in the 12 mm boss bore; it no longer passes through the hub centre (was -0.100)
STRUT_OD, STRUT_ID = 0.006, 0.0040          # T-071 / T-073 / T-076 / D-219: strut 6x4.0 (was DOC 6x4.5; Euler pinned RF 0.93 -> 1.10, T071_wing_skin.md l.72); availability and price "-"
STRUT_S = (-0.065, 0.0229, 0.0)             # EST start inside the hub
STRUT_E = (0.0500, 0.2850, 0.0)               # EST end in the clamp boss on the spar (DOC: to the spar at y 0.30)
RIB_OD, RIB_ID, RIB_X0 = 0.014, 0.012, 0.0705
RIB_X1 = XFIN_T - FIN_OD / 2                # rib ends on the tube front


def cove_x():
    """Lower end of the slanted core back face (cove for the elevon nose, deflection ELEV_STOP + 6 deg)."""
    t = math.tan(math.radians(ELEV_STOP + 6.0))        # D-194: +4 -> +6 deg (the S5010 core grazed the elevon nose by 0.08 mm at +21 deg)
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
BAL_REACH, BAL_L, BAL_T = 0.020, 0.010, 0.0013 * 12.8 / 15.6   # D-205: lead fallback 15.6 -> 12.8 g (D-195 fallback, flutter case F); was 1.3 mm. Lead centre 20 mm ahead of the hinge axis; strip 10 x 1.3 mm section x 106 mm = 15.6 g at 11.34 g/cm3 (FIXES.md: fits the section to 2 mm of skin poke, printed lens caps)
BAL_DZ = -0.0033                            # lead centre z below the hinge axis: D-193 S5010 (8.6 mm deep at the hinge): -3.3 mm balances the +-21 deg sweep so lead pokes ~3.0 mm through BOTH skins (was -6.0 mm in the 16.8 mm placeholder section; at -6.0 on S5010 the lower cap would poke 5.7 mm)
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
CAP_WALL, CAP_CLR, CAP_SLOPE = 0.0006, 0.00052, 0.20      # printed single wall 0.6 mm (vase-mode print, EST); clearance lead / tab to the cap cavity at the stop >= 0.5 mm; ramp 1:5
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
    xb = max(xb, int(round(max(p[0] for p in boss_loop(side, buried=False)) * 1000)) + 1)       # boss reach on the tab
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
    # D-194: the aft ramp must not run on over the elevon nose (the cap is fixed on the core; at the stop and in the static check the ramp end hung 0.45 mm
    # into the elevon, lower side x 185 vs hinge 183.75): cut the shell 4.0 mm ahead of the hinge line: the elevon's lower nose corner (9 mm below the hinge axis) swings 3.2 mm
    # forward at +21 deg and grazed the cap end by 0.22 mm at a 0.6 mm cut. Nothing needed is lost (lead / tab envelope ends at x 172, boss reach 176.4).
    xcut = XH - 0.0040
    if xs[-1] > xcut:
        k = max(i for i, x in enumerate(xs) if x <= xcut)
        hcut = ho[k] + (ho[k + 1] - ho[k]) * (xcut - xs[k]) / (xs[k + 1] - xs[k])
        xs, ho = xs[:k + 1] + [xcut], ho[:k + 1] + [hcut]
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


def boss_loop(side, buried=True):
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
    xs_, ho_ = cap_profile(side) if buried else ([0.0, 1.0], [CAP_WALL, CAP_WALL])   # buried=False: x reach only (cap_profile asks)

    def h_at(x):                                # cap outer height above the skin at x (linear between profile stations)
        for i in range(len(xs_) - 1):
            if min(xs_[i], xs_[i + 1]) <= x <= max(xs_[i], xs_[i + 1]):
                f = (x - xs_[i]) / ((xs_[i + 1] - xs_[i]) or 1.0)
                return ho_[i] + f * (ho_[i + 1] - ho_[i])
        return ho_[0] if abs(x - xs_[0]) < abs(x - xs_[-1]) else ho_[-1]
    top = lambda p: (p[0], _out(side, p[0], max(h_at(p[0]) - CAP_WALL * 0.5, CAP_WALL * 0.5)))   # D-208: up into the cap wall (was 0.3 mm over the skin: the bosses floated)
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



# ------------------------------------------------------------------ D-193 hub (CGE-001) and cup geometry helpers
def _ut(phi_deg):
    a = math.radians(phi_deg)
    return (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))


def _round_boss(r0, r1, R, c, plane_pts):
    """Sections of a round boss of radius R: axis in a plane normal to the loft axis, c = loft-axis coordinate of the boss axis.
    plane_pts(a, w) -> (u, v) of the rectangle corner at axial position a and half width w. 13 sections, 15 deg apart."""
    secs = []
    for k in range(13):
        th = math.radians(-90 + 15 * k)
        hw = max(R * math.cos(th), 0.0003)
        secs.append((c + R * math.sin(th), [plane_pts(r0, -hw), plane_pts(r1, -hw), plane_pts(r1, hw), plane_pts(r0, hw)]))
    return secs


def _strut_dir():
    d = (STRUT_E[0] - STRUT_S[0], STRUT_E[1] - STRUT_S[1])
    L_ = math.hypot(*d)
    return d[0] / L_, d[1] / L_


def hub_strut_pt(sg, a, w):
    """Point (x, y) of the strut socket frame: a along the strut axis from its inner end, w across (sg = +1 right, -1 left)."""
    ux, uy = _strut_dir()
    uy *= sg
    return (STRUT_S[0] + a * ux - w * uy, sg * STRUT_S[1] + a * uy + w * ux)


def hub_strut_boss(sg):
    R = STRUT_OD / 2 + HUB_W
    return _round_boss(-0.002, HUB_STRUT_S[1], R, 0.0, lambda a, w: hub_strut_pt(sg, a, w)), R


def hub_strut_web(sg):
    return [hub_strut_pt(sg, HUB_STRUT_S[0], -0.003), hub_strut_pt(sg, -0.0015, -0.003), hub_strut_pt(sg, -0.0015, 0.003), hub_strut_pt(sg, HUB_STRUT_S[0], 0.003)]


HUB_PAD = ((HUB_X1 - 0.0012, -(PADN_Y[0] - 0.0002), 0.003), (HUB_X1, PADN_Y[0] - 0.0002, 0.011))   # D-208: the flange stops inboard of the raceway notches (|y| 13.6); its outer tabs (|y| 24.4..40) were cut free by the full-height notches and floated (STL islands)

# ------------------------------------------------------------------ D-202 hub (CGE-001), continuous arm tubes (CGE-002-A/B), doublers (CGE-009), pins (CGE-010)
# All from qp/A/structures/fea_hub.py GEO (the FEA that decided D-202) unless marked. Tube frame: origin on the tube axis at the hub plane (x = TUBE_X[T]), local Y = u (tube axis, +s
# toward UR for tube A, toward LR for tube B), local Z = t = x_hat cross u (tangential face), local X = world x.
TUBE_RO, TUBE_RI = ARM_OD / 2, ARM_ID / 2   # 12 x 10 carbon tube
TUBE_HL = R_M                               # tube half length: from the hub axis to the motor cup end (DOC radius 0.2762): each tube is 2 x R_M = 0.5524 m (CALC)
SLV_L = 0.024                               # printed sleeve over s = -24..+24 mm (FEA L_SLV)
SLV_WALL = 0.0015                           # sleeve wall 1.5 mm (FEA SLV_W of the it3 / pins runs)
DBL_T = 0.001                               # doubler wall (14 x 12 carbon tube over the 12 mm tube)
DBL_RO, DBL_RI = TUBE_RO + DBL_T, TUBE_RO + 0.0001   # doubler 14 mm OD; bore 12.2 mm: 0.1 mm epoxy gap round the 12 mm tube (as the cup sleeve, D-198: no coincident cylinder faces)
DBL_S0, DBL_S1 = 0.011, 0.025               # doubler s range per side (FEA DBL_S0 / DBL_S1)
SLV_R = TUBE_RO + DBL_T + SLV_WALL          # sleeve outer radius 8.5 mm (FEA: ro + SLV_W + DBL_T); bore = tube OD for |s| < 11, doubler OD for 11..24
CB, R_CB = 0.010, 0.003                     # centre block half width / height 10 mm; 3 mm radii on its four x-parallel edges
BLK_AFT = HUB_X1 - HUB[0] - (TUBE_DX + TUBE_RO + SLV_WALL)   # D-207: the centre block runs aft to the tray face (no separate bridge boss): the bridge bore goes into the block; this removes the boss/block junction that could not be filleted (the boss r 9.5 left 0.5 mm of block face) and puts sleeve B well inside the block (10 mm)
BLK_X = (-(TUBE_DX + TUBE_RO + SLV_WALL), TUBE_DX + TUBE_RO + SLV_WALL + BLK_AFT)   # block x range relative to HUB_x: -14.0 .. +24.0 mm (to the tray face)
BLK_Z = BR_Z                                # D-207: block centred on the bridge axis (z -2 mm) so the bridge boss sits 0.5 mm inside it all round
R_BR = 0.0095                               # D-207: bridge boss radius 9.5 mm about the bridge axis (1.5 mm wall round the 16 mm bore, as the sleeves; D-206: 10.0, tangent to the block sides)
HOLE_S, HOLE_R = 0.018, 0.0024              # phase-lead exit 4.8 mm at s = +-18 mm (FEA S_HOLE, HOLE_R)
PIN_D, PIN_S = 0.003, 0.008                 # 3 mm carbon pins along x: at the crossing (y = z = 0) and one per tube at s = +-8 mm
# Pin insertion (CAD interpretation, D-202): all pins go in along +x from the nose side. A pin of tube A (UR, LL) and the crossing pin are flush with the sleeve front surface (x_A - 8.5 mm),
# so their holes are open there (pin 16 mm; crossing pin 29 mm = the 28 mm block span + 1 mm, ends buried in the aft sleeve wall). The tube B pins (LR, UL) lie behind the block, so the hub
# carries a 3 mm access hole from the block front face to the pin (open, epoxy-sealed after bonding, not drawn); the pin itself is the specified 15 mm. FEA (fea_hub.py) did not model these holes.
PIN_X0 = {st: TUBE_X[TUBE_OF[st]] - (SLV_R if TUBE_OF[st] == 'A' else TUBE_RO + SLV_WALL) for st in ST}
PIN_L = {st: TUBE_X[TUBE_OF[st]] + TUBE_RO + SLV_WALL - PIN_X0[st] for st in ST}
PINC_X0 = TUBE_X['A'] - SLV_R               # crossing pin front end (m)
BR_CHAMFER = 0.0008                         # bridge tube end: 0.8 mm x 45 deg outside chamfer (wall 1.0 mm: 0.2 mm flat left); the bridge seats on the bore floor in a matching 45 deg conical corner (D-207, hub FEA run d209)
SLV_N = 31                                  # loft sections of a sleeve (6 deg steps)
# station -> (tube, s sign) and the tube-frame placement
STN_S = {'UR': 1, 'LL': -1, 'LR': 1, 'UL': -1}
      # tray pad flange on the aft face (tray plate z 6..8 mm lands on it)


def _yz_ut(phi_deg, y, z):
    """World (y, z) -> tube coordinates (u along the tube, t tangential), tube direction phi_deg from +y."""
    a = math.radians(phi_deg)
    return y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a)


def _ut_yz(phi_deg, u, t):
    a = math.radians(phi_deg)
    return u * math.cos(a) - t * math.sin(a), u * math.sin(a) + t * math.cos(a)


def hub_core_volume_m3(h=0.00025):
    """Drawn volume (m3) of the D-202 hub core: centre block (rounded edges) + two sleeves + bridge boss, minus the tube bores (12 mm; 14 mm over the doublers), the bridge bore with its
    45 deg conical corner, the five 3 mm pins and the four 4.8 mm lead exits. Integrated on a regular grid of pitch h (0.25 mm; error well under 0.1 g); the strut sockets, webs and the
    tray pad are added analytically in hub_mass_g."""
    import numpy as np
    x0, x1 = HUB[0] + BLK_X[0] - 0.001, HUB_X1 + 0.001
    ext = 0.026                                # |y|, |z| of the sleeves reach 24.6 / 20.6 mm
    xs = np.arange(x0 + h / 2, x1, h)
    ys = np.arange(-ext + h / 2, ext, h)
    Y, Z = np.meshgrid(ys, ys, indexing='ij')
    tot = 0.0
    for x in xs:
        dx_rel = x - HUB[0]
        inside = np.zeros(Y.shape, dtype=bool)
        # centre block with rounded x-parallel edges
        if BLK_X[0] <= dx_rel <= BLK_X[1]:
            ay, az = np.abs(Y), np.abs(Z - BLK_Z)
            cy, cz = np.maximum(ay - (CB - R_CB), 0.0), np.maximum(az - (CB - R_CB), 0.0)
            inside |= (ay <= CB) & (az <= CB) & (cy * cy + cz * cz <= R_CB * R_CB)
        # bridge boss
        if BLK_X[1] - 0.0005 <= dx_rel <= HUB_X1 - HUB[0]:
            inside |= (Y * Y + (Z - BR_Z) ** 2 <= R_BR * R_BR)
        sub = np.zeros(Y.shape, dtype=bool)
        for T in 'AB':
            xt, phi = TUBE_X[T], TUBE_PHI[T]
            U, Tt = _yz_ut(phi, Y, Z)
            d2 = Tt * Tt + (x - xt) ** 2
            inside |= (np.abs(U) <= SLV_L) & (d2 <= SLV_R ** 2)
            sub |= d2 <= TUBE_RO ** 2
            sub |= (np.abs(U) >= DBL_S0) & (np.abs(U) <= DBL_S1) & (d2 <= DBL_RO ** 2)
            for st in ST:
                if TUBE_OF[st] != T:
                    continue
                sg = STN_S[st]
                for sp in (HOLE_S,):                       # lead exit hole: along t on the SIG side, from the bore out through the sleeve
                    sub |= ((U - sg * sp) ** 2 + (x - xt) ** 2 <= HOLE_R ** 2) & (Tt * SIG[st] > 0.0055)
                x_hi = xt + TUBE_RO + SLV_WALL
                x_lo = PIN_X0[st] if T == 'A' else HUB[0] + BLK_X[0] - 0.0015      # tube B pins: access hole from the block front face
                sub |= ((U - sg * PIN_S) ** 2 + Tt * Tt <= (PIN_D / 2) ** 2) & (x >= x_lo) & (x <= x_hi)
        sub |= (Y * Y + Z * Z <= (PIN_D / 2) ** 2) & (x >= PINC_X0) & (x <= HUB[0] + BLK_X[1])
        if dx_rel >= BORE_X0 - HUB[0]:
            q_ = dx_rel - (BORE_X0 - HUB[0])
            rr = BR_RO if q_ >= BR_CHAMFER else BR_RO - BR_CHAMFER + q_   # D-207 conical floor corner
            sub |= (Y * Y + (Z - BR_Z) ** 2 <= rr * rr)
        tot += float(np.count_nonzero(inside & ~sub)) * h ** 3
    return tot


_HUB_OUTER = []


def hub_outer():
    """Outer hub body mesh (verts, tris, OCC volumes with and without the junction fillets); built once per process (cached on disk)."""
    if not _HUB_OUTER:
        from . import hub_body
        _HUB_OUTER.append(hub_body.hub_outer_mesh(hub_body.cad_params()))
    return _HUB_OUTER[0]


_HUB_VOL = []


def hub_mass_g():
    """Mass of the drawn D-202 hub: core volume by hub_core_volume_m3 (block + sleeves + boss minus bores, pins, lead exits) plus the junction fillet material (D-207, OCC: filleted minus sharp body, hub_body.py) plus the strut sockets, strut webs and tray pad flange as drawn
    (analytic, overlaps with the core ignored, < 0.2 g), PETG 1.27 g/cm3 solid wall. Drawn-volume mass; the FEA solid (fea_hub.py, no strut sockets or pad) is 16.70 g."""
    if not _HUB_VOL:
        _HUB_VOL.append(hub_core_volume_m3())
    r_ = hub_outer()
    v = _HUB_VOL[0] + (r_['vol_fillet_mm3'] - r_['vol_sharp_mm3']) * 1e-9      # D-207: junction fillet material (OCC volume with fillets minus the same body without)
    Rs = STRUT_OD / 2 + HUB_W
    ls = HUB_STRUT_S[1] + 0.002
    v += 2 * (math.pi * Rs ** 2 * ls - math.pi * (STRUT_OD / 2) ** 2 * HUB_STRUT_S[1] + HUB_W * 0.006 * (-HUB_STRUT_S[0] - 0.0015))
    v += (HUB_PAD[1][0] - HUB_PAD[0][0]) * (HUB_PAD[1][1] - HUB_PAD[0][1]) * (HUB_PAD[1][2] - HUB_PAD[0][2])
    return v * 1e6 * RHO_PETG


def _rrect(hy, hz, r, n=6):
    """Rounded-rectangle loop in (y, z), half sizes hy, hz, corner radius r."""
    out = []
    for cy, cz, a0 in ((hy - r, hz - r, 0.0), (-hy + r, hz - r, 90.0), (-hy + r, -hz + r, 180.0), (hy - r, -hz + r, 270.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return out


# D-194 rib fairing: with the datum 5 mm lower the 14 mm rib (axis z 0) stays inside both skins to x 0.135 and then rises out of the upper skin (zu < 7 mm,
# 6.2 mm proud at the hinge x 0.184); the lower skin never exposes it. Blister 17 mm wide, top 1.5 mm over the tube, from x 0.130 to the hinge,
# trimmed by the core and the rib when built. Outboard of the elevon (y 0.35) so no clearance issue. Basis: structures keep the 14x12 rib (STRUCTURES-R), so it is faired not shrunk.
RIBF_X0 = 0.130
RIBF_LOOP = [(YFIN + dy, z) for dy, z in ((-0.0085, 0.0005), (0.0085, 0.0005), (0.0085, 0.0030), (0.0065, 0.0065), (0.0035, 0.0084),
                                          (-0.0035, 0.0084), (-0.0065, 0.0065), (-0.0085, 0.0030))]


def fin_fairing_loop():
    """XPS fairing section (x, y): elliptical leading edge 4 mm long x 3 mm thick, straight sides, ends at the tube axis (hidden by the tube)."""
    x0, a, b = XH + 0.0003, 0.004, 0.0015
    el = [(x0 + a + a * math.cos(math.radians(th)), b * math.sin(math.radians(th))) for th in range(100, 261, 10)]
    return [(XFIN_T, b), (x0 + a, b)] + el + [(x0 + a, -b), (XFIN_T, -b)]



# ------------------------------------------------------------------ T-077 R1'' pack tray CGE-008 (T-073 / T-076 passing variant, RDQ 2,800 mAh pack 107 x 33 x 46 mm)
# One source for the drawn solids (TRAY_ADD, disjoint boxes) and the window cuts (TRAY_CUT, each fully inside one added box), so build and mass use the same numbers.
# R1'': plate 1.2 mm with windows + ribs + 2.0 mm root pad at the hub, end walls 2.0 mm with 3 windows (T-076 t076_step4.py: "30 % windows"; here the drawn fraction is
# printed by tray_stats()), 2 lip tabs 40 x 2.0 mm per lip (y 7..47 and -47..-7). Rib width 2.0 mm (T-073 used 1.2 mm ribs at 50 % windows; the drawn windows are 54 %, wider ribs
# keep the area: EST, not re-checked by the T-073 hand calc). Orientation: plate flat on the bed (z up in the CAD), tabs and walls rise in z (interlayer allowable, T-073).
TRAY_PLATE_T = 0.0012                       # R1'' thin plate: top z 8.0 (pad / pack floor unchanged), bottom z 6.8
TRAY_RIB = 0.002                            # rib / rim width (EST)
TRAY_ROOT_X1 = -0.035                       # solid 2.0 mm root pad x -45..-35 (R1'' "2.0 mm root pad" over the hub flange end)
TRAY_YB = (0.0142, 0.0238)                  # solid band over the phase-lead raceway footprint (the raceway is bonded to the plate underside, common.RW_YO)
TRAY_YL = 0.0394                            # longitudinal rib in the outboard zone
TRAY_NB = 3                                 # window bays along x
TRAY_WN_X = (-0.024, -0.008, 0.008)         # end wall window centres x (EST)
TRAY_WN_W, TRAY_WN_Z = 0.010, (0.0110, 0.0240)


def _tray_solids():
    x0, x1 = -0.045, TRAY_X1
    zb, zt = 0.008 - TRAY_PLATE_T, 0.008
    yo = TRAY_YO
    add, cut = [], []
    add.append(((x0, -yo, zb), (x1, yo, zt), 'tray plate 1.2 mm (R1'')'))
    add.append(((x0, -yo, 0.006), (TRAY_ROOT_X1, yo, zb), 'root pad under the plate (2.0 mm total)'))
    add.append(((TRAY_ROOT_X1, -TRAY_RIB / 2, 0.006), (x1, TRAY_RIB / 2, zb), 'centre rib under the plate, tangent to the bridge tube (z 6.0)'))
    xs = [TRAY_ROOT_X1 + TRAY_RIB]
    bw = ((x1 - TRAY_RIB) - xs[0] - (TRAY_NB - 1) * TRAY_RIB) / TRAY_NB
    xl = xs[0]
    bays = []
    for k in range(TRAY_NB):
        bays.append((xl, xl + bw))
        xl += bw + TRAY_RIB
    yz = [(TRAY_RIB / 2 + TRAY_RIB / 2, TRAY_YB[0]),                                  # inner zone |y| 2.0 .. 14.2
          (TRAY_YB[1], TRAY_YL - TRAY_RIB / 2), (TRAY_YL + TRAY_RIB / 2, TRAY_YO - TRAY_RIB)]  # outer zones 23.8 .. 38.4 and 40.4 .. 54.0
    for sy in (1, -1):
        for (xa, xb) in bays:
            for (ya, yb) in yz:
                lo, hi = sorted((sy * ya, sy * yb))
                cut.append(((xa, lo, zb - 0.0001), (xb, hi, zt + 0.0001), 'plate window'))
    # end walls (2.0 mm, z 8..wall top) with three windows each
    wx0, wx1 = PACK_X[0] - TRIM_FWD, PACK_X[1] + TRIM
    for sy in (1, -1):
        lo, hi = sorted((sy * TRAY_YI, sy * TRAY_YO))
        add.append(((wx0, lo, zt), (wx1, hi, TRAY_WALL_TOP), 'tray end wall %s' % ('R' if sy > 0 else 'L')))
        for xc in TRAY_WN_X:
            cut.append(((xc - TRAY_WN_W / 2, lo - 0.0001, TRAY_WN_Z[0]), (xc + TRAY_WN_W / 2, hi + 0.0001, TRAY_WN_Z[1]), 'end wall window'))
    # lips: two tabs 40 x 2.0 mm per lip
    for (xa, xb, zh, nm) in ((wx0 - 0.002, wx0, 0.020, 'front'), (wx1, wx1 + 0.002, 0.018, 'rear')):
        for sy in (1, -1):
            lo, hi = sorted((sy * 0.007, sy * 0.047))
            add.append(((xa, lo, zt), (xb, hi, zh), 'tray %s lip tab' % nm))
    return add, cut


TRAY_ADD, TRAY_CUT = _tray_solids()


def _bv(lo, hi):
    return (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2])


def tray_volume_m3():
    """Solid volume of the drawn tray: added boxes minus the through-windows (windows lie inside one added box; the clip of the 0.1 mm overcut is removed)."""
    v = sum(_bv(lo, hi) for lo, hi, _ in TRAY_ADD)
    for lo, hi, nm in TRAY_CUT:
        lo2 = (lo[0], lo[1], lo[2] + 0.0001) if nm == 'plate window' else (lo[0], lo[1] + 0.0001, lo[2])
        hi2 = (hi[0], hi[1], hi[2] - 0.0001) if nm == 'plate window' else (hi[0], hi[1] - 0.0001, hi[2])
        v -= _bv(lo2, hi2)
    return v


def tray_stats():
    pl = [a for a in TRAY_ADD if a[2].startswith('tray plate')][0]
    pa = (pl[1][0] - pl[0][0]) * (pl[1][1] - pl[0][1])
    wa = sum((hi[0] - lo[0]) * (hi[1] - lo[1]) for lo, hi, nm in TRAY_CUT if nm == 'plate window')
    return dict(plate_area_mm2=pa * 1e6, window_area_mm2=wa * 1e6, window_frac=wa / pa, solid_cm3=tray_volume_m3() * 1e6)

# ------------------------------------------------------------------ wing / fins / cage parts
# wing (MASS-GATE 220 allocation; STRUCTURES iteration 2: 191 g)
P('WNG-001', 'Wing core, XPS 25 kg/m3 + tape skin + glue + hinge tape (lumped)', 'wing', 100.1, 'XPS foam 25 kg/m3 + packing tape')   # QP-4 FIXES item 3: 116 - 13.7 (foam 82 g x 5/30) - 0.3 (elevon span moved 10 mm); D-193 S5010: core section area 3457 -> 3372 mm2 (CALC from core_loop, hinge-forward part) = -85 mm2 x 0.90 m x 25 kg/m3 = -1.9 g
P('WNG-002', 'Spar, CF tube 12x10 x 0.90 m', 'wing', round(tube_g(0.90, SPAR_OD, SPAR_ID), 1), 'CFRP tube')
for pid, nm in (('WNG-003-C', 'centre'), ('WNG-004-R', 'right strut'), ('WNG-004-L', 'left strut'),
                ('WNG-005-R', 'right rib'), ('WNG-005-L', 'left rib')):
    P(pid, 'Spar plug (%s clamp)' % nm, 'wing', 1.2, 'PETG (printed)')   # QP-4 FIXES 1.65 -> 1.2 g (1.2 mm wall, EST)
P('WNG-006-R', 'Elevon right', 'wing', 6.7, 'XPS foam + tape')   # 8.5 - 0.73 (foam 4.4 g x 5/30) + 0.26 (10 mm more span); D-193 S5010: aft-section area 410 -> 247 mm2 (CALC) x 0.309 m x 25 kg/m3 = -1.26 g per elevon
P('WNG-006-L', 'Elevon left', 'wing', 6.7, 'XPS foam + tape')
for s_ in 'RL':
    P('WNG-007-' + s_, 'Elevon balance (D-187 v2, D-205 %s): 12.8 g lead strip 20 mm ahead of the hinge (10 x 1.07 mm x 106 mm; D-195 fallback) + 2 PETG/CF tabs 0.5 g (caps are separate parts WNG-008)' % s_, 'wing', 13.3, 'lead + PETG/CF')
    for sd in 'UL':      # FIXES2: lens caps with the mechanical stop bosses (mass from the drawn volume, PETG 1.27 g/cm3)
        P('WNG-008-%s%s' % (s_, sd), 'Lens cap + stop bosses (%s, %s skin): wall %.1f mm, >= %.1f mm clearance to the lead at the +-%.0f deg stop' % (s_, 'upper' if sd == 'U' else 'lower', CAP_WALL * 1e3, CAP_CLR * 1e3, ELEV_STOP),
          'wing', round(cap_mass_g(sd), 1), 'PETG (printed)')
    P('WNG-009-' + s_, 'Hinge damper stator (%s): printed housing + pin, 12,500 cSt silicone fluid, 2 silicone preload strips' % s_, 'wing', DMP_STATOR_G, 'PETG + silicone')
    P('WNG-010-' + s_, 'Hinge damper rotor (%s): sleeve + flange bonded on the elevon tip' % s_, 'wing', DMP_ROTOR_G, 'PETG (printed)')
# fins (allocation 70 g; STRUCTURES iteration 2: 119 g)
for s in 'RL':
    P('FIN-001-' + s, 'Fin tube 16x14 x 0.36 m (%s)' % s, 'fins', round(tube_g(0.36, FIN_OD, FIN_ID), 1), 'CFRP tube')
    P('FIN-002-' + s, 'Fin rib tube 14x12 (%s)' % s, 'fins', round(tube_g(RIB_X1 - RIB_X0, RIB_OD, RIB_ID), 1), 'CFRP tube')      # D-200: mass from the drawn length (215.5 mm; was 14.8 g for the DOC 0.227 m)
    P('FIN-003-' + s, 'Fin root block (%s)' % s, 'fins', 3.2, 'PETG (printed)')
    P('FIN-004-' + s, 'Fin fairing 3 mm XPS + tape (%s)' % s, 'fins', 8.4, 'XPS foam + tape')
    P('FIN-005-' + s, 'Rib saddle on spar (%s)' % s, 'fins', 1.0, 'PETG (printed)')
    P('FIN-006-' + s, 'Rib fairing, upper (%s): XPS + tape blister over the 14 mm rib where the S5010 skin is thinner than the tube (D-194); mass EST' % s, 'fins', 0.3, 'XPS foam + tape')
# cage (allocation 135; STRUCTURES iteration 2: 122 g)
P('CGE-001', 'Hub (printed PETG, D-202: 1.5 mm sleeves over s +-24 mm of both arm tubes, 38 x 20 x 20 mm centre block on the bridge axis, running aft to the tray face (no separate boss), 3 mm edge radii, junction fillets 2.0 mm (sleeve B / block) and 1.5 mm (sleeve A / block) as in the FEA (D-207; outer body is the OpenCASCADE mesh of hub_body.py), 2 strut sockets, tray flange; mass = drawn volume x 1.27)', 'cage', round(hub_mass_g(), 1), 'PETG (printed)')
for t_ in 'AB':
    P('CGE-002-' + t_, 'Arm tube %s 12x10 x %.4f m, ONE continuous tube from motor cup to motor cup through the hub (D-202; %s)' % (t_, 2 * TUBE_HL, 'UR + LL' if t_ == 'A' else 'LR + UL'), 'cage', round(tube_g(2 * TUBE_HL, ARM_OD, ARM_ID), 1), 'CFRP tube')
for s in ST:
    P('CGE-003-' + s, 'Motor cup (%s; QP-4 FIXES 5 -> 4 g, EST, +0.3 g lead collar and hole D-198)' % s, 'cage', 4.3, 'PETG (printed)')
    P('CGE-009-' + s, 'Doubler 14x12 x %.0f mm (%s), carbon tube sleeve bonded over the arm tube at s %.0f..%.0f mm (D-202)' % ((DBL_S1 - DBL_S0) * 1e3, s, DBL_S0 * 1e3, DBL_S1 * 1e3), 'cage', round(tube_g(DBL_S1 - DBL_S0, 2 * DBL_RO, 2 * TUBE_RO), 1), 'CFRP tube')
    P('CGE-010-' + s, 'Pin 3 mm carbon rod x %.0f mm (%s) through the arm tube and its sleeve at s %+.0f mm (D-202)' % (PIN_L[s] * 1e3, s, STN_S[s] * PIN_S * 1e3), 'cage', round(math.pi / 4 * PIN_D ** 2 * PIN_L[s] * 1600 * 1000, 2), 'CFRP rod')
P('CGE-010-C', 'Crossing pin 3 mm carbon rod x %.0f mm through both arm tubes and the hub block (D-202)' % ((HUB[0] + BLK_X[1] - PINC_X0) * 1e3), 'cage', round(math.pi / 4 * PIN_D ** 2 * (HUB[0] + BLK_X[1] - PINC_X0) * 1600 * 1000, 2), 'CFRP rod')
P('CGE-004', 'Bridge 16x14 (D-206, torsion; axis z -2 mm; D-202: starts 15 mm aft of the hub axis, bored into the boss)', 'cage', round(tube_g(BR_X1 - BR_X0, BR_OD, BR_ID), 1), 'CFRP tube')
for s in 'RL':
    P('CGE-005-' + s, 'V strut 6x4.0 (%s), T-077 (D-219)' % s, 'cage', round(tube_g(math.hypot(STRUT_E[0] - STRUT_S[0], STRUT_E[1] - STRUT_S[1]), STRUT_OD, STRUT_ID), 1), 'CFRP tube')   # T-077: from the drawn length x section x 1600 kg/m3 (STRUCTURES); was 6.5 g listed for 6x4.5
    P('CGE-007-' + s, 'Strut clamp on spar (%s)' % s, 'cage', 1.5, 'PETG (printed)')
P('CGE-006', 'Bridge saddle on spar', 'cage', 2.0, 'PETG (printed)')
P('CGE-008', 'Pack tray R1'' (T-077: 1.2 mm windowed plate on a 2.0 mm root pad + ribs, 2.0 mm end walls with windows, two 40 x 2.0 mm tabs per lip; mass = drawn solid volume x 1.27, T-067 basis M applied by printed_mass.json when present)', 'cage', round(tray_volume_m3() * 1e6 * RHO_PETG, 1), 'PETG (printed)')   # T-077: from the drawn volume (solid); was 3.8 g EST

# ------------------------------------------------------------------ wing / fins / cage edges
# wing
E('E-WNG-01', 'WNG-002', 'WNG-001', EPX, 'wing', 'spar bonded in its bore; build rule: bond over |y| <= 0.20 m (FIXES2: 0.15 m gave foam shear 78 kPa, MS +0.11 at the board allowable 103 kPa scale; 0.20 m gives 58 kPa, MS +0.48)')
for pid in ('WNG-003-C', 'WNG-004-R', 'WNG-004-L', 'WNG-005-R', 'WNG-005-L'):
    E(en('WNG'), pid, 'WNG-002', EPX, 'wing', 'plug in the spar bore under a clamp (C2 rule)')
for s in 'RL':
    E('E-WNG-1' + ('0' if s == 'R' else '1'), 'WNG-006-' + s, 'WNG-001', 'CT-TAPE-HINGE', 'wing', 'tape hinge, upper surface; tape film not drawn (product and thickness "—", BOM R05; T-022 Q2)',
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
    E(en('FIN'), 'FIN-006-' + s, 'FIN-002-' + s, CA, 'fins', 'rib fairing over the rib top (foam-safe CA), sits on the core skin')
    E(en('FIN'), 'FIN-006-' + s, 'WNG-001', CA, 'fins', 'rib fairing bonded on the upper skin')
# cage
for t_ in 'AB':
    E(en('CGE'), 'CGE-002-' + t_, 'CGE-001', EPX, 'cage', 'tube through the two sleeves and the centre block, bonded over s +-24 mm (D-202)')
for s in ST:
    E(en('CGE'), 'CGE-002-' + TUBE_OF[s], 'CGE-003-' + s, EPX, 'cage', 'tube end in cup sleeve (25 mm)')
    E(en('CGE'), 'CGE-009-' + s, 'CGE-002-' + TUBE_OF[s], EPX, 'cage', 'doubler bonded over the tube, s 11..32 mm (D-202)')
    E(en('CGE'), 'CGE-009-' + s, 'CGE-001', EPX, 'cage', 'doubler in the sleeve bore (D-202)')
    E(en('CGE'), 'CGE-010-' + s, 'CGE-002-' + TUBE_OF[s], EPX, 'cage', 'pin through the tube wall, bonded (D-202)')
    E(en('CGE'), 'CGE-010-' + s, 'CGE-001', EPX, 'cage', 'pin ends in the sleeve walls (D-202)')
for t_ in 'AB':
    E(en('CGE'), 'CGE-010-C', 'CGE-002-' + t_, EPX, 'cage', 'crossing pin through the tube, bonded (D-202)')
E(en('CGE'), 'CGE-010-C', 'CGE-001', EPX, 'cage', 'crossing pin through the centre block (D-202)')
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
    core.cut_box((0.0, -(BR_RO + 0.0005), -0.05), (0.056, BR_RO + 0.0005, 0.0075), name='bridge slot (open below; D-206 16 mm bridge)')
    core.cut_box((-0.010, -0.0585, 0.0055), (0.0225, 0.0585, 0.060), name='pack tray slot (open above; T-077 y +-58.5 clears the 20 mm strap, outer face 57.6, over the whole trim travel)')
    core.cut_box((0.0295, -0.0165, -0.05), (0.0710, 0.0165, 0.0115), name='saddle slot (open below)')
    for sy in (1, -1):                                    # D-199: raceway groove under the tray slot, then the open ditch under the bay cover
        ya, yb = sorted((sy * (RW_YO[0] - 0.0002), sy * (RW_YO[1] + 0.0002)))
        core.cut_box((0.0, ya, RW_ZO[0] - 0.0002), (RW_X1 + 0.0001, yb, RW_ZO[1] + 0.0002), name='phase-lead raceway groove (D-199)')
        ya, yb = sorted((sy * RW_YI[0], sy * RW_YI[1]))
        core.cut_box((RW_X1, ya, RW_ZI[0]), (DITCH_X1, yb, 0.0140), name='phase-lead ditch, open top under the bay cover (D-199)')
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
    guests = ['HWC-001', 'HWC-003', 'WNG-002', 'CGE-004', 'CGE-005-R', 'CGE-005-L', 'CGE-006', 'CGE-007-R', 'CGE-007-L', 'FIN-002-R', 'FIN-002-L',
              'FIN-005-R', 'FIN-005-L', 'AVN-006', 'MEC-001-R', 'MEC-001-L', 'CGE-008', 'HRN-003-R', 'HRN-003-L']
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
    f.prism('Z', -FIN_H, [[(x_, YFIN + y_) for x_, y_ in fin_fairing_loop()]], 2 * FIN_H, name='fairing')
    ctx.mirror('FIN-004-R', 'FIN-004-L', plane='XZ')
    rf = ctx.part('FIN-006-R', rgb=(0.95, 0.95, 0.8))
    rf.prism('X', RIBF_X0, [RIBF_LOOP], XH - RIBF_X0, name='rib fairing blister')
    ctx.mirror('FIN-006-R', 'FIN-006-L', plane='XZ')
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
        ctx.seat('FIN-006-' + s, 'FIN-002-' + s, 'rib groove')
        ctx.seat('FIN-006-' + s, 'WNG-001', 'blister trimmed to the skin (sits on it)')
    for st in ST:
        ctx.seat('FIN-004-' + ('R' if ST[st][0] > 0 else 'L'), 'GER-001-' + st, 'fairing notch for the shoe')


def _tube_cyl(axis, c, a0, a1, r):
    """Solid cylinder along `axis` from a0 to a1 (that coordinate) about the line through c (the other two coordinates)."""
    k = 'XYZ'.index(axis)
    cc = list(c)
    cc[k] = a0
    return fk.Shape('revolve', None, axis=axis, center=tuple(cc), profile=[(0.0, 0.0), (a1 - a0, 0.0), (a1 - a0, r), (0.0, r)])


def hub_sleeve_secs(T):
    """Loft sections (along x) of the printed sleeve round tube T: a cylinder of radius SLV_R and length 2 x SLV_L about the tube axis, as rectangles in the tube (u, t) plane."""
    xt, phi = TUBE_X[T], TUBE_PHI[T]
    secs = []
    for k in range(SLV_N + 1):
        th = math.radians(-90 + 180.0 * k / SLV_N)
        w = max(SLV_R * math.cos(th), 0.0003)
        secs.append((xt + SLV_R * math.sin(th), [_ut_yz(phi, -SLV_L, -w), _ut_yz(phi, SLV_L, -w), _ut_yz(phi, SLV_L, w), _ut_yz(phi, -SLV_L, w)]))
    return secs


def build_cage(ctx):
    hub = ctx.part('CGE-001', rgb=(0.9, 0.9, 0.9))
    # D-207: the outer body (centre block with its 3 mm edge radii + both sleeves + the 2.0 / 1.5 mm junction fillets) is ONE mesh body from the OpenCASCADE geometry of fea_hub.staged_fillet
    # (amodel/hub_body.py, cached in hub_body_cache.npz): the fusionkit prism / loft kinds cannot fillet. Every bore, pin hole, lead exit and the bridge bore are still cut below.
    r_ = hub_outer()
    hub.mesh(r_['verts'], r_['tris'], name='hub outer body: centre block 38 x 20 x 20 mm on the bridge axis to the tray face, 3 mm edge radii, sleeves r 8.5 mm over s +-24 mm, junction fillets 2.0 / 1.5 mm (OpenCASCADE, = FEA geometry; D-202, D-207)')
    hub.box(HUB_PAD[0], HUB_PAD[1], name='hub tray pad flange (D-208: inboard of the raceway notches, |y| <= 13.6)')
    for sy_ in (1, -1):                          # D-199: the raceway notches also clear the hub body beside the flange (the UR / UL conduits pass here)
        ya_, yb_ = sorted((sy_ * PADN_Y[0], sy_ * PADN_Y[1]))
        hub.cut_box((PADN_X[0], ya_, PADN_Z[0]), (PADN_X[1], yb_, PADN_Z[1]), name='raceway notch beside the tray pad flange (D-199)')
    # bridge bore: 12 mm from x = HUB_x + 15 mm to the aft face, 45 deg conical corner at the floor (matches the chamfered bridge end); explicit cut, not a seat (a seat would fill the chamfer)
    hub.cut(fk.Shape('revolve', 'bridge bore 16 mm, floor corner a 0.8 mm x 45 deg cone matching the bridge chamfer (D-207)', axis='X', center=(BORE_X0, 0.0, BR_Z),
                     profile=[(0.0, 0.0), (0.0, BR_RO - BR_CHAMFER), (BR_CHAMFER, BR_RO)]
                     + [(HUB_X1 - BORE_X0 + 0.001, BR_RO), (HUB_X1 - BORE_X0 + 0.001, 0.0)]), None, 'bridge bore D-202')
    tubes = {}
    for T in 'AB':
        tube = ctx.part('CGE-002-' + T, at=(TUBE_X[T], 0.0, 0.0), rotate=('X', TUBE_PHI[T]), rgb=(0.1, 0.1, 0.1))
        tube.tube('Y', (0.0, -TUBE_HL, 0.0), 2 * TUBE_HL, TUBE_RO, TUBE_RI, name='arm tube (one continuous tube, motor cup to motor cup)')
        tubes[T] = tube
    for st in ST:
        T, sg, sig = TUBE_OF[st], STN_S[st], SIG[st]
        tube = tubes[T]
        hs = sg * HOLE_S
        z0, z1 = sorted((sig * 0.0035, sig * 0.0075))
        tube.cut(_tube_cyl('Z', (0.0, hs, 0.0), z0, z1, HOLE_R), None, 'phase-lead exit hole 4.8 mm through the tube wall (D-202)')
        db = ctx.part('CGE-009-' + st, at=(TUBE_X[T], 0.0, 0.0), rotate=('X', TUBE_PHI[T]), rgb=(0.15, 0.15, 0.15))
        ys0 = DBL_S0 if sg > 0 else -DBL_S1
        db.tube('Y', (0.0, ys0, 0.0), DBL_S1 - DBL_S0, DBL_RO, DBL_RI, name='doubler 14x12')
        z0, z1 = sorted((sig * 0.0050, sig * 0.0075))
        db.cut(_tube_cyl('Z', (0.0, hs, 0.0), z0, z1, HOLE_R), None, 'phase-lead exit hole 4.8 mm through the doubler (D-202)')
        z0, z1 = sorted((sig * 0.0069, sig * 0.0095))
        ctx.components['CGE-001'].cut(_tube_cyl('Z', (0.0, hs, 0.0), z0, z1, HOLE_R), tube.matrix(), 'phase-lead exit hole 4.8 mm through the sleeve (D-202)')
        cup = ctx.part('CGE-003-' + st, at=station(st), rotate=mrot(st), rgb=(0.9, 0.9, 0.9))
        cup.prism('X', -0.012, [_rrect(0.0165, 0.0165, CUP_R)], 0.005, name='cup motor plate')
        cup.tube('Y', (0.0, -0.025, 0.0), 0.0285, 0.0096, ARM_OD / 2 + 0.0001, name='cup arm sleeve (bore 12.2 mm: 0.1 mm epoxy gap round the 12 mm arm, D-198: no coincident cylinder faces)')
        f_up, f_dn, f_ch, f_zc = cup_fillet_loops()
        cup.prism('Y', -0.0165, [f_up], 0.0200, name='cup fillet 1 mm, sleeve to plate along the arm (+z side, D-210)')
        cup.prism('Y', -0.0165, [f_dn], 0.0200, name='cup fillet 1 mm, sleeve to plate along the arm (-z side, D-210)')
        cup.prism('Z', -f_zc, [f_ch], 2 * f_zc, name='cup fillet 1 mm where the sleeve end meets the plate (D-210)')
        w_loop, w_zc = cup_web_loop()
        cup.prism('Y', 0.0035 - 0.00005, [w_loop], 0.0053 + 0.00005, name='collar-to-plate web with 1 mm fillets (D-210: the collar only touched the plate along a line)')
        cup.prism('Z', -w_zc, [cup_chord_loop(ys=0.0088)], 2 * w_zc, name='cup fillet 1 mm where the web and collar cap end on the plate (D-210)')
        for sy_ in (1, -1):
            for sz_ in (1, -1):
                cup.cut_cylinder('X', (-0.0126, sy_ * CUP_PAT[0] / 2, sz_ * CUP_PAT[1] / 2), 0.0055, 0.00145, name='motor screw hole M2.5 clearance 2.9 mm (ISO 273 medium; pattern V T-Motor drawing)')
        for sz_ in (1, -1):                          # D-197: the y = -9.5 mm screw heads sit in the sleeve wall; print the pocket (was only implied by the seat cut)
            cup.cut_cylinder('X', (-0.0072, -CUP_PAT[0] / 2, sz_ * CUP_PAT[1] / 2), 0.0034, 0.00265, name='screw head pocket 5.0 mm in the sleeve wall (D-197, structures/arm_cup_checks.md)')
        cup.cut_cylinder('X', (-0.0127, 0.0, 0.0), 0.0063, 0.004, name='motor rear relief 8 mm (EST)')
        # D-198: phase-lead conduit. Lead hole through the plate and sleeve wall into a collar bore (the 4 mm bend stays inside), the lead
        # then runs inside the arm bore. The old open slot at z 10.5..17.5 (leads outside the arm) is dropped.
        cup.tube('Y', (0.0, 0.0035, 0.0), 0.0045, 0.0070, ARM_OD / 2 + 0.0001, name='lead collar (D-198, 1.0 mm wall)')
        cup.cylinder('Y', (0.0, 0.0080, 0.0), 0.0008, 0.0070, name='lead collar end cap (D-198, 0.8 mm)')
        cup.cut_cylinder('X', (-0.0128, PH_Y, 0.0), 0.0085, PH_HOLE_R, name='phase-lead hole 4.8 mm (D-198)')
        ctx.seat('CGE-003-' + st, 'CGE-002-' + T, 'arm tube end in the cup sleeve')
        ctx.seat('CGE-001', 'CGE-009-' + st, 'doubler bore in the sleeve (14 mm over s 11..24)')
        c_, s_ = math.cos(math.radians(TUBE_PHI[T])), math.sin(math.radians(TUBE_PHI[T]))
        pn = ctx.part('CGE-010-' + st, at=(PIN_X0[st], sg * PIN_S * c_, sg * PIN_S * s_), rgb=(0.1, 0.1, 0.1))
        pn.cylinder('X', (0.0, 0.0, 0.0), PIN_L[st], PIN_D / 2, name='pin 3 mm carbon rod')
        if T == 'B':      # access hole from the block front face to the pin (see PIN_X0)
            ctx.components['CGE-001'].cut(_tube_cyl('X', (0.0, sg * PIN_S * c_, sg * PIN_S * s_), HUB[0] + BLK_X[0] - 0.0015, PIN_X0[st], PIN_D / 2), None, 'pin access hole 3.0 mm from the block front face (D-202 CAD note)')
        ctx.seat('CGE-001', 'CGE-010-' + st, 'pin hole 3.0 mm in the sleeve walls')
        ctx.seat('CGE-002-' + T, 'CGE-010-' + st, 'pin hole 3.0 mm through the tube')
    for T in 'AB':
        ctx.seat('CGE-001', 'CGE-002-' + T, 'tube bore through the sleeves and the block')
    pc = ctx.part('CGE-010-C', at=(PINC_X0, 0.0, 0.0), rgb=(0.1, 0.1, 0.1))
    pc.cylinder('X', (0.0, 0.0, 0.0), HUB[0] + BLK_X[1] - PINC_X0, PIN_D / 2, name='crossing pin 3 mm carbon rod')
    ctx.seat('CGE-001', 'CGE-010-C', 'crossing pin hole 3.0 mm through the block')
    for T in 'AB':
        ctx.seat('CGE-002-' + T, 'CGE-010-C', 'crossing pin hole 3.0 mm through the tube')
    br = ctx.part('CGE-004', rgb=(0.1, 0.1, 0.1))
    L_br = BR_X1 - BR_X0
    br.revolve('X', (BR_X0, 0.0, BR_Z), [(0.0, BR_RI), (L_br, BR_RI), (L_br, BR_RO), (BR_CHAMFER, BR_RO), (0.0, BR_RI + 0.0002)], name='bridge tube 16x14, 0.8 mm x 45 deg chamfer on the forward end (D-202, D-206)')
    d = (STRUT_E[0] - STRUT_S[0], STRUT_E[1] - STRUT_S[1])
    L = math.hypot(*d)
    ang = math.degrees(math.atan2(d[1], d[0]))
    for s, sg in (('R', 1), ('L', -1)):
        st_ = ctx.part('CGE-005-' + s, at=(STRUT_S[0], sg * STRUT_S[1], 0.0), rotate=('Z', sg * ang), rgb=(0.1, 0.1, 0.1))
        st_.tube('X', (0.0, 0.0, 0.0), L, STRUT_OD / 2, STRUT_ID / 2, name='strut tube')
        ctx.seat('CGE-001', 'CGE-005-' + s, 'strut socket in the hub')
        secs_, Rs_ = hub_strut_boss(sg)
        ctx.components['CGE-001'].loft('Z', secs_, name='hub strut socket boss')
        ctx.components['CGE-001'].prism('Z', -HUB_W / 2, [hub_strut_web(sg)], HUB_W, name='hub strut web')
        ctx.components['CGE-001'].cut(fk.Shape('revolve', 'strut socket bore (6 mm)', axis='X', center=(0.0, 0.0, 0.0),
                                               profile=[(0.0, 0.0), (HUB_STRUT_S[1] + 0.002, 0.0), (HUB_STRUT_S[1] + 0.002, STRUT_OD / 2), (0.0, STRUT_OD / 2)]), st_.matrix(), 'strut socket bore')
        ctx.components['WNG-001'].cut(fk.Shape('revolve', 'strut groove (0.5 mm per side clearance)', axis='X', center=(0.0, 0.0, 0.0),
                                               profile=[(0.0, 0.0), (L + 0.002, 0.0), (L + 0.002, STRUT_OD / 2 + 0.0005),
                                                        (0.0, STRUT_OD / 2 + 0.0005)]), st_.matrix(), 'strut groove, bonded slip fit clearance EST')
        ctx.seat('CGE-007-' + s, 'CGE-005-' + s, 'strut socket in the clamp')
        ctx.seat('CGE-007-' + s, 'WNG-002', 'clamp bore on the spar')
    sd = ctx.part('CGE-006', rgb=(0.9, 0.9, 0.9))
    sd.tube('Y', (SPAR_X, -0.015, 0.0), 0.030, 0.0105, SPAR_OD / 2, name='saddle ring')
    sd.box((0.030, -(BR_RO + 0.0025), BR_Z - BR_RO - 0.0025), (0.0535, BR_RO + 0.0025, BR_Z + BR_RO + 0.0025), name='saddle bridge socket (D-206: 2.5 mm wall round the 16 mm bridge)')
    sd.cut_box((SPAR_X - 0.0065, -0.016, 0.0), (SPAR_X + 0.0065, 0.016, 0.012), name='clip slot')
    ctx.seat('CGE-006', 'WNG-002', 'saddle bore on the spar')
    ctx.seat('CGE-006', 'CGE-004', 'saddle bridge socket')
    cl = ctx.part('CGE-007-R', rgb=(0.9, 0.9, 0.9))
    cl.tube('Y', (SPAR_X, 0.292, 0.0), 0.016, 0.0095, SPAR_OD / 2, name='clamp ring')
    cl.box((0.034, 0.272, -0.0055), (0.0535, 0.300, 0.0055), name='clamp strut socket')
    cl.cut_box((SPAR_X - 0.0065, 0.291, 0.0), (SPAR_X + 0.0065, 0.309, 0.012), name='clip slot')
    ctx.mirror('CGE-007-R', 'CGE-007-L', plane='XZ')
    tr = ctx.part('CGE-008', rgb=(0.9, 0.9, 0.9))
    for lo_, hi_, nm_ in TRAY_ADD:
        tr.box(lo_, hi_, name=nm_)
    for lo_, hi_, nm_ in TRAY_CUT:
        tr.cut_box(lo_, hi_, name=nm_)
