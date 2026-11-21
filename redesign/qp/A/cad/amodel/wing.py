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
HUB_X0, HUB_X1 = -0.102 + CAGE_DX, -0.045 + CAGE_DX             # D-193 hub x range; HUB_X1 (aft face = tray face, x -0.045) is still the aft face of the D-202 hub
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
PACK_XL_, PACK_ZL_ = PACK_X[1] - 0.0050, 0.009 + 0.0230   # lead exit x and z (= electrical.PACK_XL, PACK_ZL; keep equal)
CUP_PAT = (0.019, 0.016)                    # MN2212 mounting pattern 19 mm (along the arm, y) x 16 mm (z): retailers list 16x19 and 19x25 (getfpv MN2212 V2.0 page, search 2026-11-15; T-Motor drawing: 4-M2.5 on 19 x 16 (read 2026-11-15); cup holes M2.5 clearance 2.9 mm, D-194)
CUP_R = 0.006                               # plate corner radius (EST)
CUP_RO = 0.0079                             # T-077 p6 (strength check, strike S3 sleeve-hoop row RF 2.37 at 2.6 mm): arm sleeve OD 15.8 mm, wall 1.8 mm (p5: OD 17.2, wall 2.6; T-073 R3fix 2.5), except the screw-head pocket bosses below
CUP_WEB_X = -0.0078 # T-077 p6: web 4.2 mm (x -12..-7.8) so that it still meets the sleeve crest at -7.9 (0.1 mm overlap); p5: 3.5 mm to -8.5 with the crest at -8.6
_CUP_WEB_X_P5 = -0.0085                         # T-077 p5 (R3fix): the plate is a 3.5 mm web (x -12..-8.5; T-073 says 3.0 and notes 3.4 mm is needed to reach the sleeve crest at -8.6: 3.5 gives 0.1 mm overlap) over the sleeve side y < +3.5 mm, and keeps the full 5.0 mm (x -12..-7) over the +y 13 mm cantilever (the S2 strike row, T-073 s R3)
CUP_BOSS_R, CUP_BOSS_X1 = 0.0039, -0.0034   # T-077 p5: local boss round each screw-head pocket (pocket r 2.65 mm + 1.25 mm wall; EST, T-073 'local pocket bosses'), from the web to the pocket floor
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
STRUT_OD, STRUT_ID = 0.008, 0.0060          # T-077 p7 (D-225 condition): strut 8x6 (p6 judgement of 6x4.0: Euler pinned RF 0.88 at the rigid-body demand, 0.39 at x2.23; 8x6: 2.36 RB, 1.06 at x2.23, T077p7_data/strength_R4S.txt); was T-071 / D-219 6x4.0 (DOC 6x4.5); availability and price "-"
STRUT_S = (-0.065 + CAGE_DX, 0.0229, 0.0)             # EST start inside the hub
STRUT_E = (0.0500, 0.2850, 0.0)               # EST end in the clamp boss on the spar (DOC: to the spar at y 0.30)
import os as _os
_V5 = _os.environ.get('P5_VARIANT', '')            # analysis switch only (t077p5_variants.py): 'noclam', 'nonode' or 'none'; unset in every gate run
P5_CLAMSHELL, P5_NODE = _V5 in ('clam', 'both'), _V5 in ('node', 'both')           # T-077 p5 feature flags (D-221: waterjet CF clamshell FIN-005 / X7 node CGE-006 with CF plate N2); False = the part-4 drawing. D-225 (T-077 p7): both False by default (node and clamshell withdrawn, part-4 printed saddles back); P5_VARIANT 'clam' / 'node' / 'both' re-draws the withdrawn items for analysis only
RIB_OD, RIB_ID, RIB_X0 = 0.014, 0.012, (0.068 if P5_CLAMSHELL else 0.0705)   # T-077 p5: the slim 2 mm cradle ring (r 8.0, was 10.5) lets the rib start 2.5 mm further forward, so the 40 mm socket gives the D-221 engagement of 40 mm
# ---- T-077 p5 FIN-005 clamshell (D-215 / D-221 / T-080 s3: two 0.5 mm waterjet-cut CF plates about 50 x 75 mm at z +-7.5..9 inside the core, slim 2 mm printed cradle, rib engagement >= 40 mm, 3 CF pins in a 4 mm boss; T-071b B.2: pin bearing 0.37 -> 1.12 with 3 x 3 mm pins in a 4 mm wall)
CLAM_WALL, CLAM_H = 0.002, 0.009             # cradle wall 2.0 mm round the 14 mm rib: socket 18 x 18 mm (half 9.0)
CLAM_X0 = 0.0665                             # cradle socket front (unchanged)
CLAM_X1 = RIB_X0 + 0.040                     # 40 mm engagement of the rib in the socket (x 68 .. 108)
CLAM_RING_R = SPAR_OD / 2 + CLAM_WALL        # cradle ring outer radius 8.0 mm (the pocket in front of the plates covers it)
CLAM_PX = (0.0720, 0.0830, 0.0940)           # three vertical 3 mm CF pins, 11 mm pitch (spacing EST: T-071b gives the count and the diameter only); the bosses stay forward of x 98 where the skin is 11.4 mm or more over the 11 mm boss top
CLAM_PD, CLAM_BR, CLAM_BZ = 0.003, 0.004, 0.011      # pin diameter, boss radius 4 mm (a 4 mm wall at the pin: boss from the rib wall z 7 up to z 11 top and bottom)
CLAM_PL_X, CLAM_PL_HY, CLAM_PL_Z, CLAM_PL_T = (0.0665, 0.108), 0.012, 0.0090, 0.0005
CLAM_POCKET_HY = 0.032                       # T-077 p6: the core pocket stays 64 mm in y (the cradle ring is 60 mm long); only the plates are trimmed (x 66.5..108 = the socket face, y +-12 mm; p5: x 58..108, y +-32)
_CLAM_PL_P5 = (0.058, 0.108), 0.032   # plates x 50 mm, y +-32 mm about YFIN (64 mm; the record says about 75 mm, which would hit the airspeed board pocket at y -412.5, x 69..84: EST), on the cradle faces z +-9.0..9.5 (the record gives z +-7.5..9, not reconcilable with a 2 mm wall on a 14 mm rib: unsourced), 0.5 mm
CLAM_PIN_L = 2 * CLAM_BZ - 0.0002            # pin length 21.8 mm, z -11.0 .. +10.8: flush with the lower boss face (the hole is open there, the pin is pushed in from below), 0.2 mm inside the upper boss top
# ---- T-077 p5 node CGE-006 (T-071b N2, T-080 s3.2): one-piece saddle with ears to y +-16.5, CF plate 0.5 mm, ears on both faces of the plate, 4 pins in double shear
NODE_X = (0.0315, 0.0710)                    # ear bond area 39.5 x 19 mm: T-071b gives 41.5 mm (slot x 0.0295..0.071), but the phase bundles rise at x 29 (envelope to x 30.94) so the ears start at x 31.5 (-4.8 % bond length)
NODE_Z = 0.0095                              # ear / plate half height: 19 mm (T-071b, airfoil height at the slot)
NODE_EAR_IN = (0.0135, 0.0165)               # inner ear on the saddle: y 13.5 .. 16.5, thickness 3 mm (EST, T-071b gives the footprint only)
NODE_PL_T = 0.0005                           # CF plate N2 0.5 mm, y 16.5 .. 17.0 (T-071b: station y >= 0.0165)
NODE_EAR_OUT = (0.0170, 0.0185)              # outer (clevis) ear, y 17.0 .. 18.5, 1.5 mm (EST)
NODE_PINS = tuple((x_, z_) for x_ in (0.0360, 0.0470) for z_ in (-0.0050, 0.0050))   # 4 pins of 3 mm per side, positions EST (both columns ahead of the spar: the spar tube x 54..66, |z| < 6 passes through the ears)
NODE_PIN_D = 0.003

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

# ------------------------------------------------------------------ T-070 wing torsion skin (T-077 p3): 1 ply 48 g/m2 glass at +-45 deg wet-laid on the core, over the leading edge and the cove face, y -0.40..+0.40,
# plus one CF strip on the cove face. The skin is drawn INSIDE the original core outline (the core is machined 0.054 mm smaller by a seat cut), so every part that sits on the surface still sits on it.
SKIN_Y = 0.40                               # m, skin spans y -0.40..+0.40 (T-070 decision s3 "y -0.40..+0.40"; docs/audits/2026-11-19-T070-decision.md)
SKIN_AREAL = 0.088                          # kg/m2: 48 g/m2 cloth + 40 g/m2 resin (T-071_wing_skin.md l.24, l.67)
SKIN_T = 0.000054                           # m, wet ply thickness 0.054 mm (EST, T-071 l.24; no wet lay-up coupon)
SKIN_RHO = SKIN_AREAL / SKIN_T / 1000.0     # g/cm3 = 1.63 (areal density / thickness)
STRIP_W, STRIP_TH = 0.006, 0.0005           # cove CF strip: only the 3 mm2 section is given (T-071 l.32, l.69); width 6 mm x 0.5 mm is MY split of it (width, thickness and product "-")
STRIP_RHO = 1.55                            # g/cm3 (T-071 l.69)


def _offset_loop(loop, d):
    """Inward offset by d of a counter-clockwise closed polygon (mitred; d far below the segment lengths)."""
    n = len(loop)
    out = []
    for i in range(n):
        p0, p1, p2 = loop[i - 1], loop[i], loop[(i + 1) % n]
        a = (p1[0] - p0[0], p1[1] - p0[1])
        b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        if la < 1e-12 or lb < 1e-12:
            out.append(p1)
            continue
        n1 = (-a[1] / la, a[0] / la)
        n2 = (-b[1] / lb, b[0] / lb)
        k = 1.0 + n1[0] * n2[0] + n1[1] * n2[1]
        out.append((p1[0] + d * (n1[0] + n2[0]) / k, p1[1] + d * (n1[1] + n2[1]) / k))
    return out


def skin_loops():
    o = core_loop()
    return o, _offset_loop(o, SKIN_T)


def skin_mass_g():
    o, i_ = skin_loops()
    return (abs(_poly_area(o)) - abs(_poly_area(i_))) * 2 * SKIN_Y * 1e6 * SKIN_RHO


def strip_loop():
    """Cove-face strip section in the x-z plane: STRIP_W along the slanted cove face (centred), STRIP_TH inward from the skin's inner face."""
    p0, p1 = (XL, zl(XL)), (XH, zu(XH))
    d = (p1[0] - p0[0], p1[1] - p0[1])
    L_ = math.hypot(*d)
    u = (d[0] / L_, d[1] / L_)
    nn = (-u[1], u[0])                         # inward (the core_loop runs counter-clockwise: the inside is on the left)
    m = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    a, b = SKIN_T, SKIN_T + STRIP_TH
    pts = [(m[0] - u[0] * STRIP_W / 2 + nn[0] * a, m[1] - u[1] * STRIP_W / 2 + nn[1] * a), (m[0] + u[0] * STRIP_W / 2 + nn[0] * a, m[1] + u[1] * STRIP_W / 2 + nn[1] * a),
           (m[0] + u[0] * STRIP_W / 2 + nn[0] * b, m[1] + u[1] * STRIP_W / 2 + nn[1] * b), (m[0] - u[0] * STRIP_W / 2 + nn[0] * b, m[1] - u[1] * STRIP_W / 2 + nn[1] * b)]
    return pts if _poly_area(pts) > 0 else pts[::-1]


def strip_mass_g():
    return abs(_poly_area(strip_loop())) * 2 * SKIN_Y * 1e6 * STRIP_RHO


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
SLV_L = 0.032                               # D-222 P2 (T-077 p3): sleeve length L 24 -> 32 mm, s = -32..+32 mm (landing-demand root-cause audit, sleeve bond; was FEA L_SLV 24)
SLV_WALL = 0.0015                           # sleeve wall 1.5 mm (FEA SLV_W of the it3 / pins runs)
DBL_T = 0.001                               # doubler wall (14 x 12 carbon tube over the 12 mm tube)
DBL_RO, DBL_RI = TUBE_RO + DBL_T, TUBE_RO + 0.0001   # doubler 14 mm OD; bore 12.2 mm: 0.1 mm epoxy gap round the 12 mm tube (as the cup sleeve, D-198: no coincident cylinder faces)
DBL_S0, DBL_S1 = 0.011, 0.032 + 0.015       # doubler s range per side: from 11 mm to 15 mm (DBL_STAG) past the sleeve end (D-222 P1; was FEA 11..25)
SLV_R = TUBE_RO + DBL_T + 0.001               # D-220 / D-221 s7.1.1 (T-077 p3): machined 6061 octagonal sleeve, APOTHEM 8.0 mm (16 mm across flats = 14 mm doubler OD + 2 x 1.0 mm minimum wall at the flats; circumradius 8.66 mm); flats face +-x and +-t; bore = tube OD for |s| < 11, doubler OD for 11..32
HUB_FIL, HUB_FIL_A = 1.0, 0.9               # mm: internal corner radius at the sleeve B / sleeve A to block junction. T-080 s7.1.2 asks R >= the end-mill radius (R 3.0 for a 6 mm cutter, EST): the OpenCASCADE fillet of the octagonal prisms fails above 1.0 mm (B) / 0.9 mm (A) (probe in T077_cad.md Part 3), so the drawn corners need a 2 mm end mill (cutter list "-")
RHO_AL = 2.70                               # g/cm3, 6061-T6 (T-080 s1, en.wikipedia.org/wiki/6061_aluminium_alloy read 2026-11-20; D-220 / D-221)
MOUTH_CH = 0.0005                           # D-222 P1: sleeve-mouth internal chamfer 0.5 mm x 45 deg (size EST: D-222 gives none; = T-080 s7.1.5 exit chamfer)
HOLE_CH = 0.0005                            # T-080 s7.1.5: 0.5 mm chamfer at the phase-lead exits
DBL_STAG = 0.015                            # D-222 P1: doubler runs 15 mm past the sleeve end (audit: 4 x 15 mm of 14x12 CF, +3.8 g EST); was 1 mm
DBL_TAPER = 0.005                           # D-222 P1: outer end tapered over about 5 mm (audit); tip wall 0.2 mm (EST, ply drop-off)
CB, R_CB = 0.010, 0.003                     # centre block half width / height 10 mm; 3 mm radii on its four x-parallel edges
BLK_AFT = HUB_X1 - HUB[0] - (TUBE_DX + SLV_R)   # D-207: the centre block runs aft to the tray face (no separate bridge boss): the bridge bore goes into the block; this removes the boss/block junction that could not be filleted (the boss r 9.5 left 0.5 mm of block face) and puts sleeve B well inside the block (10 mm)
BLK_X = (-(TUBE_DX + SLV_R), TUBE_DX + SLV_R + BLK_AFT)   # block x range relative to HUB_x: -14.0 .. +24.0 mm (to the tray face)
BLK_Z = BR_Z                                # D-207: block centred on the bridge axis (z -2 mm) so the bridge boss sits 0.5 mm inside it all round
R_BR = 0.0095                               # D-207: bridge boss radius 9.5 mm about the bridge axis (1.5 mm wall round the 16 mm bore, as the sleeves; D-206: 10.0, tangent to the block sides)
COL_X1 = 0.045                              # D-220: bonded bridge bore >= 30 mm: the collar runs aft to a mouth 45 mm aft of the hub axis (floor at +15: 30 mm engagement; escalation s3.2 'mouth about x 45, COL_E about 21')
COL_HY, COL_Z = 0.012, (-0.016, 0.008)      # T-071b C6 / D-220 collar section 24 x 24 mm (y +-12, z -16..+8: top flush with the tray plate top z 8, T-071b test box); 3 mm radii on the four x-parallel edges (as the block)
POCKET_SH_R, BORE_MO_R = 0.004, 0.0005        # T-077 p5: concave fillet R 4.0 mm at the pocket shoulder (a revolved profile; tool: 8 mm ball-nose / R 4 corner-radius end mill, catalogue item "-") and R 0.5 mm rounding of the bridge-bore mouth edge (corner-rounding cutter R 0.5, catalogue item "-"); FEA T077p5_data
POCKET_R, POCKET_X0 = 0.00925, 0.0155        # T-077 p4 (D-224 hub pockets): from x +15.5 mm (1.0 mm aft of sleeve B's aft flat) to the collar mouth the hub is turned to a cylinder R 9.25 mm about the bridge axis: 1.25 mm wall round the 16 mm bore; removes the lightly loaded block corners and collar corners (FEA T077p4_data: p925). 0 = off
HOLE_S, HOLE_R = 0.018, 0.0024              # phase-lead exit 4.8 mm at s = +-18 mm (FEA S_HOLE, HOLE_R)
PIN_D, PIN_S = 0.003, 0.008                 # 3 mm carbon pins along x: at the crossing (y = z = 0) and one per tube at s = +-8 mm
# Pin insertion (CAD interpretation, D-202): all pins go in along +x from the nose side. A pin of tube A (UR, LL) and the crossing pin are flush with the sleeve front surface (x_A - 8.5 mm),
# so their holes are open there (pin 16 mm; crossing pin 29 mm = the 28 mm block span + 1 mm, ends buried in the aft sleeve wall). The tube B pins (LR, UL) lie behind the block, so the hub
# carries a 3 mm access hole from the block front face to the pin (open, epoxy-sealed after bonding, not drawn); the pin itself is the specified 15 mm. FEA (fea_hub.py) did not model these holes.
PIN_X0 = {st: TUBE_X[TUBE_OF[st]] - (SLV_R if TUBE_OF[st] == 'A' else TUBE_RO + SLV_WALL) for st in ST}
PIN_L = {st: TUBE_X[TUBE_OF[st]] + SLV_R - 0.0010 - PIN_X0[st] for st in ST}   # blind end 1.0 mm short of the aft flat
PINC_X0 = TUBE_X['A'] - SLV_R               # crossing pin front end (m)
BR_CHAMFER = 0.0008                         # bridge tube end: 0.8 mm x 45 deg outside chamfer (wall 1.0 mm: 0.2 mm flat left); the bridge seats on the bore floor in a matching 45 deg conical corner (D-207, hub FEA run d209)
# station -> (tube, s sign) and the tube-frame placement
STN_S = {'UR': 1, 'LL': -1, 'LR': 1, 'UL': -1}
DBL_RT = DBL_RI + 0.0002                    # tapered tip: outer radius = bore + 0.2 mm wall (EST ply drop-off)


def dbl_profile(sg):
    """(axial offset from the doubler's inboard end along +Y of the tube frame, radius) of the tapered doubler: sg > 0 starts at s = +DBL_S0, sg < 0 starts at s = -DBL_S1 (taper at the start)."""
    L_, T_ = DBL_S1 - DBL_S0, DBL_TAPER
    if sg > 0:
        return [(0.0, DBL_RI), (0.0, DBL_RO), (L_ - T_, DBL_RO), (L_, DBL_RT), (L_, DBL_RI)]
    return [(0.0, DBL_RI), (0.0, DBL_RT), (T_, DBL_RO), (L_, DBL_RO), (L_, DBL_RI)]


def dbl_volume_m3():
    L_, T_ = DBL_S1 - DBL_S0, DBL_TAPER
    return math.pi * ((DBL_RO ** 2 - DBL_RI ** 2) * (L_ - T_) + T_ / 3.0 * (DBL_RO ** 2 + DBL_RO * DBL_RT + DBL_RT ** 2) - DBL_RI ** 2 * T_)


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
    x0, x1 = HUB[0] + BLK_X[0] - 0.001, HUB[0] + COL_X1 + 0.001
    ext = 0.034                                # |y|, |z| of the L 32 octagonal sleeves reach about 31.3 / 26.4 mm
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
        # (T-077 p4 pocket cut applied after the union below)
        # D-220 collar (24 x 24 mm, x +24..+45 rel.)
        if BLK_X[1] <= dx_rel <= COL_X1:
            ay, az = np.abs(Y), np.maximum(np.abs(Z - 0.5 * (COL_Z[0] + COL_Z[1])) - 0.0, 0.0)
            hz = 0.5 * (COL_Z[1] - COL_Z[0])
            cy2, cz2 = np.maximum(ay - (COL_HY - R_CB), 0.0), np.maximum(np.abs(Z - 0.5 * (COL_Z[0] + COL_Z[1])) - (hz - R_CB), 0.0)
            inside |= (ay <= COL_HY) & (np.abs(Z - 0.5 * (COL_Z[0] + COL_Z[1])) <= hz) & (cy2 * cy2 + cz2 * cz2 <= R_CB * R_CB)
        # bridge boss
        if BLK_X[1] - 0.0005 <= dx_rel <= HUB_X1 - HUB[0]:
            inside |= (Y * Y + (Z - BR_Z) ** 2 <= R_BR * R_BR)
        if POCKET_R > 0 and dx_rel >= POCKET_X0:                  # T-077 p4: lightening cut, cylinder R about the bridge axis; p5: concave shoulder fillet (profile R(x) = R + rho - sqrt(rho^2 - (X0 + rho - x)^2) over x0..x0 + rho)
            t_ = max(POCKET_X0 + POCKET_SH_R - dx_rel, 0.0)
            Rp = POCKET_R if t_ <= 0.0 else POCKET_R + POCKET_SH_R - math.sqrt(max(POCKET_SH_R ** 2 - t_ * t_, 0.0))
            inside &= (Y * Y + (Z - BR_Z) ** 2 <= Rp * Rp)
        sub = np.zeros(Y.shape, dtype=bool)
        for T in 'AB':
            xt, phi = TUBE_X[T], TUBE_PHI[T]
            U, Tt = _yz_ut(phi, Y, Z)
            d2 = Tt * Tt + (x - xt) ** 2
            inside |= (np.abs(U) <= SLV_L) & (np.maximum(np.maximum(np.abs(x - xt), np.abs(Tt)), (np.abs(x - xt) + np.abs(Tt)) / math.sqrt(2.0)) <= SLV_R)   # octagon, apothem SLV_R
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


def hub_vol_m3():
    """Drawn volume (m3) of the machined hub CGE-001: core volume by hub_core_volume_m3 (block + two octagonal L 32 sleeves minus bores, pins, lead exits) plus the junction fillet material (OCC: filleted minus
    sharp body, hub_body.py) plus the strut sockets, strut webs and tray pad (analytic, overlaps with the core ignored, < 0.2 g) minus the sleeve-mouth and lead-exit chamfers (analytic). No lightening pockets (T-080 s3.1:
    the knee-mill shape is the upper-mass-end hub while Tormach access is unconfirmed; pockets: size "-")."""
    if not _HUB_VOL:
        _HUB_VOL.append(hub_core_volume_m3())
    r_ = hub_outer()
    v = _HUB_VOL[0] + (r_['vol_fillet_mm3'] - r_['vol_sharp_mm3']) * 1e-9      # D-207: junction fillet material (OCC volume with fillets minus the same body without)
    Rs = STRUT_OD / 2 + HUB_W
    ls = HUB_STRUT_S[1] + 0.002
    v += 2 * (math.pi * Rs ** 2 * ls - math.pi * (STRUT_OD / 2) ** 2 * HUB_STRUT_S[1] + HUB_W * 0.006 * (-HUB_STRUT_S[0] - 0.0015))
    v += (HUB_PAD[1][0] - HUB_PAD[0][0]) * (HUB_PAD[1][1] - HUB_PAD[0][1]) * (HUB_PAD[1][2] - HUB_PAD[0][2])
    v -= 4 * 2 * math.pi * (DBL_RO + MOUTH_CH / 3) * MOUTH_CH * MOUTH_CH / 2          # 4 sleeve mouths: triangle MOUTH_CH x MOUTH_CH / 2 swept round the bore
    v -= 4 * 2 * math.pi * (HOLE_R + HOLE_CH / 3) * HOLE_CH * HOLE_CH / 2             # 4 lead exits: same on the hole
    if BORE_MO_R > 0:                                                                # T-077 p5: rounded bore mouth edge: region between the corner and the quarter circle, swept round the bore (numeric Pappus, 2-D grid h = r / 400)
        n_ = 400; hh = BORE_MO_R / n_; acc = 0.0
        for i_ in range(n_):
            for j_ in range(n_):
                xq, rq = (i_ + 0.5) * hh, (j_ + 0.5) * hh                                 # x back from the mouth face, radial excess over the bore
                if (BORE_MO_R - xq) ** 2 + (BORE_MO_R - rq) ** 2 > BORE_MO_R ** 2:         # outside the circle centred (r, r) = removed
                    acc += 2 * math.pi * (BR_RO + rq) * hh * hh
        v -= acc
    return v


def hub_mass_g():
    return hub_vol_m3() * 1e6 * RHO_AL


def _rrect_part(y0, y1, hz, r, round_lo, round_hi, n=6):
    """Rectangle y0..y1 x +-hz in (y, z) with corner radius r only on the low-y and/or high-y end (T-077 p5: the cup plate split into web and cantilever)."""
    out = []
    spec = []
    if round_hi:
        spec += [(y1 - r, hz - r, 0.0), ]
    else:
        spec += [(y1, hz, None)]
    if round_lo:
        spec += [(y0 + r, hz - r, 90.0), (y0 + r, -hz + r, 180.0)]
    else:
        spec += [(y0, hz, None), (y0, -hz, None)]
    if round_hi:
        spec += [(y1 - r, -hz + r, 270.0)]
    else:
        spec += [(y1, -hz, None)]
    for cy, cz, a0 in spec:
        if a0 is None:
            out.append((cy, cz))
            continue
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return out


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
TRAY_ROOT_X1 = -0.035 + CAGE_DX                       # solid 2.0 mm root pad x -45..-35 (R1'' "2.0 mm root pad" over the hub flange end)
TRAY_YB = (0.0142, 0.0238)                  # solid band over the phase-lead raceway footprint (the raceway is bonded to the plate underside, common.RW_YO)
TRAY_YL = 0.0394                            # longitudinal rib in the outboard zone
TRAY_NB = 3                                 # window bays along x
TRAY_WN_X = (-0.024 - 0.022, -0.008 - 0.022, 0.008 - 0.022)         # end wall window centres x (EST)
TRAY_WN_W, TRAY_WN_Z = 0.010, (0.0110, 0.0240)


def _tray_solids():
    x0, x1 = TRAY_X0, TRAY_X1
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
P('WNG-011', 'Wing torsion skin: 1 ply 48 g/m2 glass at +-45 deg wet-laid on the core, closed over the leading edge and the cove face, y -0.40..+0.40, wet ply 0.054 mm (EST) drawn as a shell inside the core outline; openings as the core (slots, pockets, windows); mass = shell volume x %.2f g/cm3 (88 g/m2 / 0.054 mm, T-071 l.24)' % SKIN_RHO, 'wing', round(skin_mass_g(), 1), 'glass cloth 48 g/m2 + epoxy')
P('WNG-012', 'Cove CF strip, section %.0f x %.1f mm = 3 mm2 (only the area is given, T-071 l.32; width, thickness and product -), y -0.40..+0.40, under the skin on the cove face; mass = volume x 1.55 g/cm3' % (STRIP_W * 1e3, STRIP_TH * 1e3), 'wing', round(strip_mass_g(), 1), 'CFRP strip')
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
    if P5_CLAMSHELL:
        P('FIN-005-' + s, 'Clamshell cradle on spar (%s, T-077 p5, D-221): ring wall 2.0 mm on the spar (60 mm), socket 18 x 18 mm x 40 mm round the 14 mm rib, 4 mm pin bosses, printed PETG; mass = drawn volume x T-067 basis' % s, 'fins', 1.0, 'PETG (printed)')
        P('FIN-007-' + s, 'Clamshell CF plates (%s): 2 plates 0.5 mm x 41.5 x 24 mm (T-077 p6 trim of the p5 50 x 64; the record says about 50 x 75; corner radii -), waterjet-cut from 0.5 mm CF sheet (ACP PDS Dec 2014, 1.6 g/cm3), bonded on the cradle top and bottom faces; mass = drawn volume x 1.6' % s, 'fins', 6.0, 'CF fabric laminate (cut sheet)')
        P('FIN-008-' + s, 'Clamshell pins (%s): 3 x 3 mm carbon rod x 21.8 mm, vertical through the cradle bosses, the rib walls and the plates (T-071b B.2)' % s, 'fins', round(3 * math.pi / 4 * CLAM_PD ** 2 * CLAM_PIN_L * 1.6e6, 2), 'CF rod')
    else:
        P('FIN-005-' + s, 'Rib saddle on spar (%s)' % s, 'fins', 1.0, 'PETG (printed)')
    P('FIN-006-' + s, 'Rib fairing, upper (%s): XPS + tape blister over the 14 mm rib where the S5010 skin is thinner than the tube (D-194); mass EST' % s, 'fins', 0.3, 'XPS foam + tape')
# cage (allocation 135; STRUCTURES iteration 2: 122 g)
P('CGE-001', 'Hub (machined 6061-T6, D-220 / D-221 / D-222: two OCTAGONAL sleeves 16 mm across flats, 1.0 mm wall at the flats, over s +-32 mm of both arm tubes, 38.5 x 20 x 20 mm centre block on the bridge axis to the tray face, 3 mm edge radii, internal radii %.1f / %.1f mm at the junctions (OCC mesh, hub_body.py), 0.5 mm sleeve-mouth and lead-exit chamfers, 2 strut sockets, tray flange; hub pockets T-077 p4: block aft of x +15.5 and the 30 mm bond collar (D-220) turned to a cylinder R %.2f mm about the bridge axis (wall %.2f mm round the 16 mm bore); mass = drawn volume x 2.70 g/cm3)' % (HUB_FIL, HUB_FIL_A, POCKET_R * 1e3, POCKET_R * 1e3 - BR_RO * 1e3), 'cage', round(hub_mass_g(), 1), 'Al 6061-T6 (machined)')
for t_ in 'AB':
    P('CGE-002-' + t_, 'Arm tube %s 12x10 x %.4f m, ONE continuous tube from motor cup to motor cup through the hub (D-202; %s)' % (t_, 2 * TUBE_HL, 'UR + LL' if t_ == 'A' else 'LR + UL'), 'cage', round(tube_g(2 * TUBE_HL, ARM_OD, ARM_ID), 1), 'CFRP tube')
for s in ST:
    P('CGE-003-' + s, 'Motor cup (%s; QP-4 FIXES 5 -> 4 g, EST, +0.3 g lead collar and hole D-198)' % s, 'cage', 4.3, 'PETG (printed)')
    P('CGE-009-' + s, 'Doubler 14x12 x %.0f mm (%s), carbon tube sleeve bonded over the arm tube at s %.0f..%.0f mm 15 mm past the sleeve end, outer 5 mm tapered (D-202, D-222 P1); mass = revolved volume x 1.6 g/cm3 (STRUCTURES CF basis)' % ((DBL_S1 - DBL_S0) * 1e3, s, DBL_S0 * 1e3, DBL_S1 * 1e3), 'cage', round(dbl_volume_m3() * 1e6 * 1.6, 2), 'CFRP tube')
    P('CGE-010-' + s, 'Pin 3 mm carbon rod x %.0f mm (%s) through the arm tube and its sleeve at s %+.0f mm (D-202)' % (PIN_L[s] * 1e3, s, STN_S[s] * PIN_S * 1e3), 'cage', round(math.pi / 4 * PIN_D ** 2 * PIN_L[s] * 1600 * 1000, 2), 'CFRP rod')
P('CGE-010-C', 'Crossing pin 3 mm carbon rod x %.0f mm through both arm tubes and the hub block (D-202)' % ((HUB[0] + BLK_X[1] - PINC_X0) * 1e3), 'cage', round(math.pi / 4 * PIN_D ** 2 * (HUB[0] + BLK_X[1] - PINC_X0) * 1600 * 1000, 2), 'CFRP rod')
P('CGE-004', 'Bridge 16x14 (D-206, torsion; axis z -2 mm; D-202: starts 15 mm aft of the hub axis, bored into the boss)', 'cage', round(tube_g(BR_X1 - BR_X0, BR_OD, BR_ID), 1), 'CFRP tube')
for s in 'RL':
    P('CGE-005-' + s, 'V strut %.0fx%.0f (%s), T-077 p7 (D-225 resize; was 6x4.0, D-219)' % (STRUT_OD * 1e3, STRUT_ID * 1e3, s), 'cage', round(tube_g(math.hypot(STRUT_E[0] - STRUT_S[0], STRUT_E[1] - STRUT_S[1]), STRUT_OD, STRUT_ID), 1), 'CFRP tube')   # T-077: from the drawn length x section x 1600 kg/m3 (STRUCTURES); was 6.5 g listed for 6x4.5
    P('CGE-007-' + s, 'Strut clamp on spar (%s), R4 resized T-077 p7: ring OD 21 x 21, socket OD 12.5 / bore 8 x 27, fillet R 4.0 (mass from printed_mass.json)' % s, 'cage', 1.5, 'PETG (printed)')
if P5_NODE:
    P('CGE-006', 'Centre node saddle (T-077 p5, D-221 s3.2, T-071b N2): ring wall 2.0 mm over 30 mm of the spar, 2.5 mm bridge socket, ears to y +-16.5 (x 29.5..71, 19 mm high, 3 mm thick); X7 Onyx + continuous CF rings (the fibre layout is a manufacturing note, not modelled: layout -), printed z-up; mass = drawn volume x T-067 basis x 0.945 (Onyx 1.20 / PETG 1.27 g/cm3)', 'cage', 2.0, 'Onyx + CF (Markforged X7)')
    P('CGE-011', 'Node plates N2: 2 CF plates 0.5 mm x 41.5 x 19 mm (outline = ear footprint; spar hole 12 mm; corner radii -), waterjet from 0.5 mm CF sheet, y +-(16.5..17.0), bonded between the ears (T-071b N2); mass = drawn volume x 1.6', 'cage', 1.2, 'CF fabric laminate (cut sheet)')
    P('CGE-013', 'Node outer clevis ears: 2 x (41.5 x 19 x 1.5 mm, spar hole 12 mm), Onyx printed z-up, y +-(17.0..18.5), bonded on the plates (T-071b N2: ears on both faces of the plate; thickness EST); mass = drawn volume x T-067 basis x 0.945', 'cage', 1.5, 'Onyx + CF (Markforged X7)')
    P('CGE-012', 'Node pins: 8 x 3 mm carbon rod x 5.2 mm along y through the inner ear, the plate and the outer ear (4 per side, double shear, T-071b N2; positions EST)', 'cage', round(8 * math.pi / 4 * NODE_PIN_D ** 2 * (NODE_EAR_OUT[1] - NODE_EAR_IN[0] + 0.0002) * 1.6e6, 2), 'CF rod')
else:
    P('CGE-006', 'Bridge saddle on spar', 'cage', 2.0, 'PETG (printed)')
P('CGE-008', 'Pack tray R1'' (T-077: 1.2 mm windowed plate on a 2.0 mm root pad + ribs, 2.0 mm end walls with windows, two 40 x 2.0 mm tabs per lip; mass = drawn solid volume x 1.27, T-067 basis M applied by printed_mass.json when present)', 'cage', round(tray_volume_m3() * 1e6 * RHO_PETG, 1), 'PETG (printed)')   # T-077: from the drawn volume (solid); was 3.8 g EST

# ------------------------------------------------------------------ wing / fins / cage edges
# wing
E('E-WNG-90', 'WNG-011', 'WNG-001', EPX, 'wing', 'glass skin wet-laid on the foam core (T-070): 1 ply +-45 deg, resin is the bond; vacuum bag or hand roll, practice "-"')
E('E-WNG-91', 'WNG-012', 'WNG-001', EPX, 'wing', 'cove CF strip bonded on the cove face under the skin (T-070)')
E('E-WNG-92', 'WNG-012', 'WNG-011', EPX, 'wing', 'cove CF strip wetted into the skin laminate')
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
    if P5_CLAMSHELL:
        E(en('FIN'), 'FIN-005-' + s, 'WNG-001', EPX, 'fins', 'clamshell bonded in its foam pocket (placed before the spar: the upper plate cannot pass the spar from below)')
        E(en('FIN'), 'FIN-007-' + s, 'FIN-005-' + s, EPX, 'fins', 'CF plates bonded on the cradle top and bottom faces (frame fraction 0.5 EST, T-071b B.2)')
        E(en('FIN'), 'FIN-008-' + s, 'FIN-005-' + s, EPX, 'fins', 'three CF pins through the cradle bosses (4 mm wall)')
        E(en('FIN'), 'FIN-008-' + s, 'FIN-002-' + s, EPX, 'fins', 'pins through the two rib walls (double shear)')
        E(en('FIN'), 'FIN-008-' + s, 'FIN-007-' + s, EPX, 'fins', 'pins through the plates')
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
if P5_NODE:
    E(en('CGE'), 'CGE-011', 'CGE-006', EPX, 'cage', 'N2 plates bonded on the inner ears (2 x 41.5 x 19 mm faces)')
    E(en('CGE'), 'CGE-013', 'CGE-011', EPX, 'cage', 'outer clevis ears bonded on the plates')
    E(en('CGE'), 'CGE-012', 'CGE-006', EPX, 'cage', 'four pins per side through the ears and the plate (double shear)')
    E(en('CGE'), 'CGE-012', 'CGE-011', EPX, 'cage', 'pins through the plate')
    E(en('CGE'), 'CGE-012', 'CGE-013', EPX, 'cage', 'pins through the outer ear')
    E(en('CGE'), 'CGE-011', 'WNG-002', EPX, 'cage', 'plate spar hole 12 mm round the spar (bonded)')
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
    if P5_NODE:
        for sy_ in (1, -1):
            ya_, yb_ = sorted((sy_ * 0.0165, sy_ * (NODE_EAR_OUT[1] + 0.0003)))
            core.cut_box((NODE_X[0] - 0.0003, ya_, -0.05), (NODE_X[1] + 0.0003, yb_, NODE_Z + 0.0003), name='node plate and outer ear pocket (open below, T-077 p5)')
    for sy in (1, -1):                                    # D-199: raceway groove under the tray slot, then the open ditch under the bay cover
        ya, yb = sorted((sy * (RW_YO[0] - 0.0002), sy * (RW_YO[1] + 0.0002)))
        core.cut_box((0.0, ya, RW_ZO[0] - 0.0002), (RW_X1 + 0.0001, yb, RW_ZO[1] + 0.0002), name='phase-lead raceway groove (D-199)')
        ya, yb = sorted((sy * RW_YI[0], sy * RW_YI[1]))
        core.cut_box((RW_X1, ya, RW_ZI[0]), (DITCH_X1, yb, 0.0140), name='phase-lead ditch, open top under the bay cover (D-199)')
    core.cut_box((0.0335, 0.2705, -0.05), (0.0710, 0.3110, 0.0075), name='clamp slot R (open below; T-077 p7 to y 311 for the 21 mm ring)')
    core.cut_box((0.0335, -0.3110, -0.05), (0.0710, -0.2705, 0.0075), name='clamp slot L (open below; T-077 p7)')
    for sg in (1, -1):
        y0, y1 = sorted((sg * (YFIN - 0.0305), sg * (YFIN + 0.0305)))
        if P5_CLAMSHELL:
            y0, y1 = sorted((sg * (YFIN - CLAM_POCKET_HY - 0.0003), sg * (YFIN + CLAM_POCKET_HY + 0.0003)))
            core.cut_box((SPAR_X - CLAM_RING_R - 0.0003, y0, -0.05), (CLAM_PL_X[1] + 0.0003, y1, CLAM_PL_Z + CLAM_PL_T + 0.0003), name='clamshell pocket (open below, top 9.8 mm): plates, cradle; the pin bosses (z to 11) are cut by their own seats (T-077 p5)')
        else:
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
        hw_ = CLAMP_RS * 1e-3 + 0.0005                           # T-077 p7: the OD 12.5 clamp socket is wider than the 10 mm strut slot: socket slot 0.5 mm clear, s -28..+2 mm about the strut end, open below
        qa_, qb_ = (STRUT_E[0] - (CLAMP_SL * 1e-3 + 0.001) * ux, STRUT_E[1] - (CLAMP_SL * 1e-3 + 0.001) * uy), (STRUT_E[0] + 0.002 * ux, STRUT_E[1] + 0.002 * uy)
        nx2, ny2 = -uy * hw_, ux * hw_
        sl_ = [(qa_[0] + nx2, sg * (qa_[1] + ny2)), (qb_[0] + nx2, sg * (qb_[1] + ny2)), (qb_[0] - nx2, sg * (qb_[1] - ny2)), (qa_[0] - nx2, sg * (qa_[1] - ny2))]
        core.cut_prism('Z', -0.05, [_ccw(sl_)], 0.05 + CLAMP_RS * 1e-3 + 0.0005, name='clamp socket slot (open below, 0.5 mm clear, T-077 p7)')
    # T-070 glass skin (WNG-011) and cove strip (WNG-012), drawn inside the core outline: same openings as the core (every cut above), core and strip pockets from the skin / strip bodies
    o_, i_ = skin_loops()
    sk = ctx.part('WNG-011', rgb=(0.75, 0.85, 0.80))
    sk.prism('Y', -SKIN_Y, [o_, i_], 2 * SKIN_Y, name='glass skin shell 1 ply +-45 deg, 0.054 mm (EST)')
    stp = ctx.part('WNG-012', rgb=(0.1, 0.1, 0.1))
    stp.prism('Y', -SKIN_Y, [strip_loop()], 2 * SKIN_Y, name='cove CF strip 6 x 0.5 mm (3 mm2; width / thickness EST)')
    ctx.seat('WNG-001', 'WNG-011', 'core outline machined inside by the 0.054 mm skin (the skin is wet-laid on the foam)')
    ctx.seat('WNG-001', 'WNG-012', 'cove strip pocket under the skin')
    guests = ['HWC-001', 'HWC-003', 'WNG-002', 'CGE-004', 'CGE-005-R', 'CGE-005-L', 'CGE-006', 'CGE-007-R', 'CGE-007-L', 'FIN-002-R', 'FIN-002-L',
              'FIN-005-R', 'FIN-005-L', 'AVN-006', 'MEC-001-R', 'MEC-001-L', 'CGE-008', 'HRN-003-R', 'HRN-003-L']
    if P5_CLAMSHELL:
        guests += ['FIN-007-R', 'FIN-007-L', 'FIN-008-R', 'FIN-008-L']
    if P5_NODE:
        guests += ['CGE-011', 'CGE-012', 'CGE-013']
    for g in guests:
        ctx.seat('WNG-001', g, 'groove / bore / pocket cut in the core for ' + g, shop=True)
        ctx.seat('WNG-011', g, 'opening in the skin for ' + g, shop=True)
        ctx.seat('WNG-012', g, 'cove strip interrupted for ' + g, shop=True)


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
    if P5_CLAMSHELL:
        sdl.tube('Y', (SPAR_X, YFIN - 0.030, 0.0), 0.060, SPAR_OD / 2 + CLAM_WALL, SPAR_OD / 2, name='cradle spar ring, wall 2.0 mm (T-077 p5, D-221)')
        sdl.box((CLAM_X0, YFIN - CLAM_H, -CLAM_H), (CLAM_X1, YFIN + CLAM_H, CLAM_H), name='cradle rib socket 18 x 18 mm, 40 mm engagement of the rib (D-221)')
        for xp_ in CLAM_PX:
            for sz_ in (1, -1):
                z0_, z1_ = sorted((sz_ * (CLAM_H - 0.001), sz_ * CLAM_BZ))
                sdl.cylinder('Z', (xp_, YFIN, z0_), z1_ - z0_, CLAM_BR, name='pin boss, 4 mm wall at the pin (T-071b B.2 fix)')
    else:
        sdl.tube('Y', (SPAR_X, YFIN - 0.030, 0.0), 0.060, 0.0105, SPAR_OD / 2, name='rib saddle ring')
        sdl.box((0.0665, YFIN - 0.0095, -0.0095), (0.0905, YFIN + 0.0095, 0.0095), name='rib saddle socket')
    sdl.cut_box((SPAR_X - 0.0065, YFIN - 0.031, 0.0), (SPAR_X + 0.0065, YFIN + 0.031, 0.012), name='clip slot')
    ctx.mirror('FIN-005-R', 'FIN-005-L', plane='XZ')
    if P5_CLAMSHELL:
        pp = ctx.part('FIN-007-R', rgb=(0.1, 0.1, 0.1))
        for z0_, nm_ in ((CLAM_PL_Z, 'upper'), (-CLAM_PL_Z - CLAM_PL_T, 'lower')):
            pp.prism('Z', z0_, [[(CLAM_PL_X[0], YFIN - CLAM_PL_HY), (CLAM_PL_X[1], YFIN - CLAM_PL_HY), (CLAM_PL_X[1], YFIN + CLAM_PL_HY), (CLAM_PL_X[0], YFIN + CLAM_PL_HY)]], CLAM_PL_T,
                     name='clamshell CF plate %s, 0.5 mm, 41.5 x 24 mm (T-077 p6: the socket face x 66.5..108, y +-12; p5 50 x 64, record 50 x 75; waterjet; corner radii -)' % nm_)
        ctx.mirror('FIN-007-R', 'FIN-007-L', plane='XZ')
        pn = ctx.part('FIN-008-R', rgb=(0.1, 0.1, 0.1))
        for xp_ in CLAM_PX:
            pn.cylinder('Z', (xp_, YFIN, -CLAM_BZ), CLAM_PIN_L, CLAM_PD / 2, name='clamshell pin 3 mm carbon rod')
        ctx.mirror('FIN-008-R', 'FIN-008-L', plane='XZ')
    for s in 'RL':
        for g, note in (('FIN-001-' + s, 'tube slot'), ('FIN-003-' + s, 'block notch')):
            ctx.seat('FIN-004-' + s, g, 'fairing ' + note)
        ctx.components['FIN-004-' + s].cut_cylinder('X', (XH, sg_(s) * YFIN, 0.0), XFIN_T - XH, 0.0075, name='rib groove (0.5 mm clearance)')
        ctx.seat('FIN-003-' + s, 'FIN-001-' + s, 'block bore on the tube')
        ctx.seat('FIN-003-' + s, 'FIN-002-' + s, 'block rib socket')
        ctx.seat('FIN-005-' + s, 'WNG-002', 'saddle bore on the spar')
        ctx.seat('FIN-005-' + s, 'FIN-002-' + s, 'saddle rib socket')
        if P5_CLAMSHELL:
            ctx.seat('FIN-005-' + s, 'FIN-008-' + s, 'pin holes in the cradle bosses and walls')
            ctx.seat('FIN-002-' + s, 'FIN-008-' + s, 'pin cross holes in the rib walls')
            ctx.seat('FIN-007-' + s, 'FIN-005-' + s, 'plates cut round the cradle bosses')
            ctx.seat('FIN-007-' + s, 'FIN-008-' + s, 'pin holes in the plates')
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


CLAMP_FIL = 4.0                             # T-077 p7 (D-225): R 4.0 so that the junction annulus (socket OD 12.5 + 2 x 4.0 = 20.5 mm, bore 8) passes x2.23 (RF 1.01, interlayer 9.5, Kt 2.0 EST; R 2.0 on the OD 9 socket: 0.84 RB). Was T-077 p5 (R4) 2.0: junction fillet radius mm (the brief asks for >= 1.5; OCC makes 2.0 on the socket-to-ring edges once the socket end is buried in the ring wall; at 1.5 / 1.0 it also works, the probe is in T077_cad.md part 5)
CLAMP_Y = (289.5, 310.5)                    # T-077 p7: ring 21 mm on the spar (R4 ring bond D12 x 21: RF 2.31 RB, 1.04 at x2.23; p5 292..308 = 16 mm: 0.79), centred on the plug WNG-004 at y 300
CLAMP_RR = 10.5                             # T-077 p7: ring OD 21 (wall 4.5; p5 OD 17) so the R 4.0 fillet base (OD 20.5) lands on the ring; the part-4 saddle rings at the same x are R 10.5 (inside the airfoil)
CLAMP_RS, CLAMP_SL = 6.25, 27.0            # T-077 p7: socket OD 12.5 / bore 8 (wall axial RF 2.45 RB, 1.10 at x2.23), strut bond 27 mm (D8 x 27: 2.29 RB, 1.03); p5 OD 9 / bore 6, 25 mm


def clamp_params():
    """R4 strut clamp (right) as occ_bodies params, mm: ring OD 17 x 16 mm (y 292..308) on the spar, socket cylinder OD 9 along the strut axis from 25 mm behind the strut end to 14 mm past it (the end disc is buried in the ring wall)."""
    d = (STRUT_E[0] - STRUT_S[0], STRUT_E[1] - STRUT_S[1])
    L = math.hypot(*d)
    return dict(kind='strut_clamp', sx=SPAR_X * 1e3, y0=CLAMP_Y[0], y1=CLAMP_Y[1], RR=CLAMP_RR, ex=STRUT_E[0] * 1e3, ey=STRUT_E[1] * 1e3, ux=d[0] / L, uy=d[1] / L, RS=CLAMP_RS, SL=CLAMP_SL, SE=14.0, FIL=CLAMP_FIL)


def build_cage(ctx):
    hub = ctx.part('CGE-001', rgb=(0.9, 0.9, 0.9))
    # D-207: the outer body (centre block with its 3 mm edge radii + both sleeves + the 2.0 / 1.5 mm junction fillets) is ONE mesh body from the OpenCASCADE geometry of fea_hub.staged_fillet
    # (amodel/hub_body.py, cached in hub_body_cache.npz): the fusionkit prism / loft kinds cannot fillet. Every bore, pin hole, lead exit and the bridge bore are still cut below.
    r_ = hub_outer()
    hub.mesh(r_['verts'], r_['tris'], name='hub outer body, machined 6061: centre block 38.5 x 20 x 20 mm on the bridge axis to the tray face, 3 mm edge radii, two octagonal sleeves (16 mm across flats) over s +-32 mm, junction radii %.1f / %.1f mm (OpenCASCADE; D-220, D-221 s7.1, D-222 P2)' % (HUB_FIL, HUB_FIL_A))
    hub.box(HUB_PAD[0], HUB_PAD[1], name='hub tray pad flange (D-208: inboard of the raceway notches, |y| <= 13.6)')
    for sy_ in (1, -1):                          # D-199: the raceway notches also clear the hub body beside the flange (the UR / UL conduits pass here)
        ya_, yb_ = sorted((sy_ * PADN_Y[0], sy_ * PADN_Y[1]))
        hub.cut_box((PADN_X[0], ya_, PADN_Z[0]), (PADN_X[1], yb_, PADN_Z[1]), name='raceway notch beside the tray pad flange (D-199)')
    # bridge bore: 12 mm from x = HUB_x + 15 mm to the aft face, 45 deg conical corner at the floor (matches the chamfered bridge end); explicit cut, not a seat (a seat would fill the chamfer)
    hub.cut(fk.Shape('revolve', 'bridge bore 16 mm, 30 mm long to the collar mouth (D-220), floor corner a 0.8 mm x 45 deg cone matching the bridge chamfer (D-207)', axis='X', center=(BORE_X0, 0.0, BR_Z),
                     profile=[(0.0, 0.0), (0.0, BR_RO - BR_CHAMFER), (BR_CHAMFER, BR_RO)]
                     + [(HUB[0] + COL_X1 - BORE_X0 - BORE_MO_R, BR_RO)]
                     + [(HUB[0] + COL_X1 - BORE_X0 - BORE_MO_R + BORE_MO_R * math.cos(math.radians(a_)), BR_RO + BORE_MO_R + BORE_MO_R * math.sin(math.radians(a_))) for a_ in (-75, -60, -45, -30, -15, 0)]
                     + [(HUB[0] + COL_X1 - BORE_X0 + 0.001, BR_RO + BORE_MO_R), (HUB[0] + COL_X1 - BORE_X0 + 0.001, 0.0)]), None, 'bridge bore D-202')
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
        db.revolve('Y', (0.0, ys0, 0.0), dbl_profile(sg), name='doubler 14x12 CF tube, s %.0f..%.0f mm, outer end tapered over %.0f mm (D-222 P1: staggered %.0f mm past the sleeve end)' % (DBL_S0 * 1e3, DBL_S1 * 1e3, DBL_TAPER * 1e3, DBL_STAG * 1e3))
        z0, z1 = sorted((sig * 0.0050, sig * 0.0075))
        db.cut(_tube_cyl('Z', (0.0, hs, 0.0), z0, z1, HOLE_R), None, 'phase-lead exit hole 4.8 mm through the doubler (D-202)')
        z0, z1 = sorted((sig * 0.0069, sig * 0.0095))
        ctx.components['CGE-001'].cut(_tube_cyl('Z', (0.0, hs, 0.0), z0, z1, HOLE_R), tube.matrix(), 'phase-lead exit hole 4.8 mm through the sleeve (D-202)')
        hz0 = sig * (SLV_R - HOLE_CH) if sig > 0 else -(SLV_R + 0.001)       # D-221 s7.1.5: 0.5 mm x 45 deg chamfer on the exit where it meets the flat
        hprof = ([(0.0, 0.0), (0.0, HOLE_R), (HOLE_CH, HOLE_R + HOLE_CH), (HOLE_CH + 0.001, HOLE_R + HOLE_CH), (HOLE_CH + 0.001, 0.0)] if sig > 0 else
                 [(0.0, 0.0), (0.0, HOLE_R + HOLE_CH), (0.001, HOLE_R + HOLE_CH), (0.001 + HOLE_CH, HOLE_R), (0.001 + HOLE_CH, 0.0)])
        ctx.components['CGE-001'].cut(fk.Shape('revolve', 'phase-lead exit chamfer 0.5 x 45 deg (T-080 s7.1.5; grommet not drawn: bundle 3.9 mm in a 4.8 mm hole leaves no room)', axis='Z', center=(0.0, hs, hz0), profile=hprof), tube.matrix(), 'exit chamfer')
        mz0 = (SLV_L - MOUTH_CH) if sg > 0 else -(SLV_L + 0.001)             # D-222 P1: internal chamfer at the sleeve mouth (the epoxy fillet that goes with it is an adhesive bead, not drawn)
        mprof = ([(0.0, 0.0), (0.0, DBL_RO), (MOUTH_CH, DBL_RO + MOUTH_CH), (MOUTH_CH + 0.001, DBL_RO + MOUTH_CH), (MOUTH_CH + 0.001, 0.0)] if sg > 0 else
                 [(0.0, 0.0), (0.0, DBL_RO + MOUTH_CH), (0.001, DBL_RO + MOUTH_CH), (0.001 + MOUTH_CH, DBL_RO), (0.001 + MOUTH_CH, 0.0)])
        ctx.components['CGE-001'].cut(fk.Shape('revolve', 'sleeve mouth internal chamfer 0.5 x 45 deg (D-222 P1)', axis='Y', center=(0.0, mz0, 0.0), profile=mprof), tube.matrix(), 'mouth chamfer')
        cup = ctx.part('CGE-003-' + st, at=station(st), rotate=mrot(st), rgb=(0.9, 0.9, 0.9))
        cup.prism('X', -0.012, [_rrect_part(-0.0165, 0.00355, 0.0165, CUP_R, True, False)], 0.012 + CUP_WEB_X, name='cup plate web 4.2 mm over the sleeve side y -16.5..+3.5 (T-077 p6: reaches the sleeve crest at -7.9 with 0.1 mm overlap; p5 3.5 mm)')
        cup.prism('X', -0.012, [_rrect_part(0.0035, 0.0165, 0.0165, CUP_R, False, True)], 0.005, name='cup plate cantilever 5.0 mm over the +y 13 mm (T-073 R3fix: the strike S2 row)')
        cup.tube('Y', (0.0, -0.025, 0.0), 0.0285, CUP_RO, ARM_OD / 2 + 0.0001, name='cup arm sleeve OD 15.8 mm, wall 1.8 mm (T-077 p6; p5 OD 17.2, T-073 R3fix 2.5; bore 12.2 mm: 0.1 mm epoxy gap round the 12 mm arm, D-198: no coincident cylinder faces)')
        for sz_ in (1, -1):
            cup.cylinder('X', (CUP_WEB_X - 0.0001, -CUP_PAT[0] / 2, sz_ * CUP_PAT[1] / 2), CUP_BOSS_X1 - CUP_WEB_X + 0.0001, CUP_BOSS_R, name='screw-head pocket boss r 3.9 mm (T-073 R3fix local bosses; size EST)')
        f_up, f_dn, f_ch, f_zc = cup_fillet_loops(xf=CUP_WEB_X, ro=CUP_RO)
        f_ch = cup_chord_loop(xf=-0.007)
        f_zc = math.sqrt(CUP_RO ** 2 - 0.007 ** 2)
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
    ctx.seat('CGE-008', 'CGE-001', 'tray plate and root pad notched for the hub collar (T-071b C6: 24 mm notch, collar top flush with the plate top)')
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
    if P5_NODE:
        for sy_ in (1, -1):
            ya_, yb_ = sorted((sy_ * NODE_EAR_IN[0], sy_ * NODE_EAR_IN[1]))
            sd.box((NODE_X[0], ya_, -NODE_Z), (NODE_X[1], yb_, NODE_Z), name='node inner ear 41.5 x 19 x 3 mm (T-071b N2: ears on both faces of the plate; thickness EST)')
    sd.box((0.030, -(BR_RO + 0.0025), BR_Z - BR_RO - 0.0025), (0.0535, BR_RO + 0.0025, BR_Z + BR_RO + 0.0025), name='saddle bridge socket (D-206: 2.5 mm wall round the 16 mm bridge)')
    sd.cut_box((SPAR_X - 0.0065, -NODE_EAR_OUT[1] - 0.0003, 0.0), (SPAR_X + 0.0065, NODE_EAR_OUT[1] + 0.0003, 0.012), name='clip slot (T-077 p5: through the ears)')
    ctx.seat('CGE-006', 'WNG-002', 'saddle bore on the spar')
    ctx.seat('CGE-006', 'CGE-004', 'saddle bridge socket')
    if P5_NODE:
        pl_ = ctx.part('CGE-011', rgb=(0.1, 0.1, 0.1))
        ea_ = ctx.part('CGE-013', rgb=(0.9, 0.9, 0.9))
        pi_ = ctx.part('CGE-012', rgb=(0.1, 0.1, 0.1))
        for sy_ in (1, -1):
            ya_, yb_ = sorted((sy_ * 0.0165, sy_ * (0.0165 + NODE_PL_T)))
            pl_.prism('Y', ya_, [[(NODE_X[0], -NODE_Z), (NODE_X[1], -NODE_Z), (NODE_X[1], NODE_Z), (NODE_X[0], NODE_Z)]], yb_ - ya_, name='node plate N2 0.5 mm, 41.5 x 19 mm (waterjet CF; corner radii -)')
            ya_, yb_ = sorted((sy_ * NODE_EAR_OUT[0], sy_ * NODE_EAR_OUT[1]))
            ea_.prism('Y', ya_, [[(NODE_X[0], -NODE_Z), (NODE_X[1], -NODE_Z), (NODE_X[1], NODE_Z), (NODE_X[0], NODE_Z)]], yb_ - ya_, name='node outer clevis ear 41.5 x 19 x 1.5 mm (Onyx, z-up)')
            for px_, pz_ in NODE_PINS:
                ya_, yb_ = sorted((sy_ * (NODE_EAR_IN[0] - 0.0001), sy_ * (NODE_EAR_OUT[1] + 0.0001)))
                pi_.cylinder('Y', (px_, ya_, pz_), yb_ - ya_, NODE_PIN_D / 2, name='node pin 3 mm carbon rod')
        for g_, p__ in (('CGE-011', pl_), ('CGE-013', ea_)):
            p__.cut_box((SPAR_X - 0.0065, -NODE_EAR_OUT[1] - 0.0003, 0.0), (SPAR_X + 0.0065, NODE_EAR_OUT[1] + 0.0003, 0.012), name='spar notch, open upward (the node docks from below, T-077 p5)')
            ctx.seat(g_, 'WNG-002', 'spar hole in the node ' + ('plate' if g_ == 'CGE-011' else 'outer ear'))
            ctx.seat(g_, 'CGE-012', 'pin holes in the node ' + ('plate' if g_ == 'CGE-011' else 'outer ear'))
        ctx.seat('CGE-006', 'CGE-012', 'pin holes in the inner ears')
    cl = ctx.part('CGE-007-R', rgb=(0.9, 0.9, 0.9))
    from . import occ_bodies
    cb_ = occ_bodies.body_mesh('strut_clamp_R', clamp_params())
    cl.mesh(cb_['verts'], cb_['tris'], name='strut clamp R4 (T-073, T-077 p5, p7 resize): ring OD %.0f mm (wall %.1f) x %.0f mm on the spar, tubular socket OD %.1f mm x %.0f mm bond length along the strut axis (wall %.2f round the 8 mm strut), the socket runs into the ring wall, junction fillet R %.1f mm (OpenCASCADE mesh body); the T-073 two 2 x 2.5 x 9 mm junction strips are replaced by the fused socket-to-ring section (my geometry: the strip footprint is an EST)' % (2 * CLAMP_RR, CLAMP_RR - 6.0, CLAMP_Y[1] - CLAMP_Y[0], 2 * CLAMP_RS, CLAMP_SL, CLAMP_RS - STRUT_OD * 500, CLAMP_FIL))
    cl.cut_box((SPAR_X - 0.0065, 0.2780, 0.0), (SPAR_X + 0.0065, CLAMP_Y[1] * 1e-3 + 0.0005, 0.012), name='clip slot (T-077 p7: from y 278 so that it also opens the OD 12.5 socket where it passes the spar footprint, to the 21 mm ring end; p5 280..309)')
    ctx.mirror('CGE-007-R', 'CGE-007-L', plane='XZ')
    tr = ctx.part('CGE-008', rgb=(0.9, 0.9, 0.9))
    for lo_, hi_, nm_ in TRAY_ADD:
        tr.box(lo_, hi_, name=nm_)
    for lo_, hi_, nm_ in TRAY_CUT:
        tr.cut_box(lo_, hi_, name=nm_)
