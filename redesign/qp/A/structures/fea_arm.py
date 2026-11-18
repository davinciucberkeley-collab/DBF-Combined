"""fea_arm.py - 3-D solid FEA of one concept A arm: hub bridge sleeve, radial web, arm socket, 12x10 CFRP arm, motor cup.

    python -I redesign/qp/A/structures/fea_arm.py [--level 0|1|2|all] [--cases]

Why (user, 2026-11-16): "run an FEA on the system while it is in its most stressful flight stage ... the arm connected to the
propeller". The hand checks (arm_cup_checks.md, qp5_checks.md) bound the tube and the cup but model the hub socket crudely and
never checked the radial web that joins each socket to the hub (wing.py hub_arm_spoke: 0.8 mm x 22 mm, the only load path).

Model (units mm, N, MPa). Arm frame: x = hub axis, y = along the arm from the hub axis, z = tangential (the web's thin direction).
Geometry from cad/amodel/wing.py and common.py (constants read below, not retyped):
  - bridge sleeve: cylinder along x, r HUB_RS (7.2), bore r BR_OD/2 (6.0), x HUB_X0..HUB_X1 relative to the hub centre;
  - radial web: x +-HUB_SPOKE_D/2, y HUB_RS-0.6 .. HUB_ARM_R0+0.6, z +-HUB_W/2 (0.8 mm);
  - arm socket: boss r HUB_RBI (6.8) from HUB_ARM_R0 to HUB_ARM_R1-HUB_MOUTH, r HUB_RB (8.0) over the mouth (12 mm);
    bore r ARM_OD/2 from R_IN, 2 mm floor;
  - arm tube 12 x 10 from R_IN to R_M (245 mm);
  - motor cup in the motor frame (rotated CANT = 17 deg about the arm axis): plate 33 x 33 x 5 mm (R 6 corners) at 7..12 mm
    from the arm axis, sleeve OD 19.2 / bore 12.0 (the 0.1 mm epoxy gap is not meshed: tied), y -25 .. +3.5 about the station,
    4 holes 2.9 mm on 19 x 16, the two screw-head pockets 5.3 mm in the sleeve wall, the 8 mm rear relief.
  Not modelled (listed in FEA-ARM.md): phase-lead holes in the socket floor and plate, the lead collar, the hub conduits, fillets (variant current models the collar, the plate lead hole and the D-210 cup fillets and web).
Bonds (tube in socket, tube in cup) are tied: perfect epoxy bond; the interface tractions are reported against the bond allowable.
Support: the sleeve bore is fixed (the 12 x 10 bridge tube bonded in it is 30x stiffer than the PETG; the hub also has the tray
and struts, which are left out, so the web carries every arm load: conservative).
Loads enter through the motor: RBE3 (weighted average, no added stiffness) from the motor base point onto the base-ring
footprint on the plate front face (r <= 13 mm, EST: MN2212 base) and the four screw-head annuli on the rear face.
Elements: 10-node tetrahedra (gmsh 4.15, order 2), 4-point Gauss; direct solve (scipy SuperLU), one factorisation for all load
cases; stresses at Gauss points.

Variant `current` (D-208, 2026-11-18): the arm as built since D-202 / D-205 / D-207: ONE continuous 12 x 10 tube from the hub
crossing (y = 0) to the motor (y = R_M), the 14 x 12 carbon doubler bonded over s = DBL_S0..DBL_S1, the 3 mm pin hole at
s = PIN_S (along x, through both walls; the pin rod itself is left out: conservative) and the 4.8 mm phase-lead exit at
s = HOLE_S (one wall and the doubler, +z tangential face). The printed hub is NOT in this model: fea_hub.py covers it (and
60 mm of each tube). Support: the outer surface of the tube and the doubler inside the hub sleeve (y <= SLV_L) is fixed,
i.e. a rigid hub: it gives the free span, the doubler end and the cup their stresses; the stresses inside the sleeve
are those of the hub model, not this one. Group 0 ('hub' in the code) is the doubler (CFRP) in this variant.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(A, 'cad'))
from amodel import common as C  # noqa: E402
from amodel import wing as W    # noqa: E402

OUT = os.path.join(HERE, 'out_fea')
mm = 1e3

# ---------------- geometry constants, read from the CAD ----------------
R_IN, R_M = W.R_IN * mm, C.R_M * mm
SLV_R, SLV_BORE = W.HUB_RS * mm, W.BR_OD / 2 * mm
SLV_X0, SLV_X1 = (W.HUB_X0 - C.HUB[0]) * mm, (W.HUB_X1 - C.HUB[0]) * mm
WEB_D, WEB_T = W.HUB_SPOKE_D * mm, W.HUB_W * mm
WEB_Y0, WEB_Y1 = (W.HUB_RS - 0.0006) * mm, (W.HUB_ARM_R0 + 0.0006) * mm
B_R0, B_R1, B_MOUTH = W.HUB_ARM_R0 * mm, W.HUB_ARM_R1 * mm, W.HUB_MOUTH * mm
B_RI, B_RO = W.HUB_RBI * mm, W.HUB_RB * mm
TUBE_RO, TUBE_RI = W.ARM_OD / 2 * mm, W.ARM_ID / 2 * mm
CANT = C.CANT
PAT_Y, PAT_Z = W.CUP_PAT[0] / 2 * mm, W.CUP_PAT[1] / 2 * mm
CUP_PL = (-12.0, -7.0)            # plate x range in the motor frame (wing.py: prism X from -0.012, 0.005 thick)
CUP_HALF, CUP_RC = 16.5, W.CUP_R * mm
CUP_FIL = W.CUP_FIL * mm            # D-210 sleeve-to-plate fillet radius (wing.py)
COL_L, COL_RO, COL_CAP = 4.5, 7.0, 0.8   # D-198 lead collar y 3.5..8.0 past the station, OD 14, end cap 0.8 mm (wing.py cup.tube / cylinder)
PH_X, PH_Y_MM, PH_R = (-12.8, -4.3), C.PH_Y * mm, C.PH_HOLE_R * mm   # phase-lead hole along x through plate and sleeve wall (wing.py)
CUP_SLV = (-25.0, 3.5, 9.6)       # sleeve y range about the station and outer radius (wing.py cup.tube)
HOLE_R, HEAD_R = 1.45, 2.25       # M2.5 clearance 2.9 mm; ISO 4762 M2.5 head 4.5 mm
POCKET_R, POCKET_X = 2.65, (-7.2, -3.8)
RELIEF_R, RELIEF_X = 4.0, (-12.7, -6.4)
BASE_R = 13.0                     # EST: MN2212 base footprint radius on the plate front face (T-Motor drawing not read for it)
BOX_YEND = None                      # D-202: y where the box spoke ends (None: at the mouth); --box 5th value
BOX_DEEP_R = None                    # D-202: deep socket boss radius (None: HUB_RBI as drawn); --box 6th value
BOX = [11.0, 7.0, 1.6, 10.0]        # box spoke half-depth x, half-width z, wall, core radius (mm); --box overrides
SPK_RO, SPK_RI = 6.8, 5.2           # fix candidate (FEA-ARM.md): hollow spoke OD 13.6 = the boss OD, 1.6 mm wall (4 perimeters)
X_PROP = 47.0                     # prop mid-plane from the arm axis (arm_cup_checks.py X_PROP, EST)
CUR_SLV = W.SLV_L * mm            # current hub sleeve covers s 0..24 mm of each tube (wing.py SLV_L)
CUR_DBL = (W.DBL_S0 * mm, W.DBL_S1 * mm, W.DBL_RO * mm)   # doubler s range and outer radius (14 x 12)
CUR_PIN = (W.PIN_S * mm, W.PIN_D / 2 * mm)                # pin hole position and radius
CUR_HOLE = (W.HOLE_S * mm, W.HOLE_R * mm)                 # phase-lead exit position and radius
CUR_NJ = CUR_SLV + 2 * TUBE_RO     # tube and doubler judged only from one tube diameter past the clamped sleeve edge (St-Venant;
                                   # s 0..36 mm): nearer the clamp the stresses are support artefacts. fea_hub.py models that zone
                                   # (hub, doubler, tubes to s 60 mm, judged to s 45 mm).
VARIANT = 'asdrawn'

# ---------------- materials (structures_a.py, fe_a.py; all EST until coupons) ----------------
E_PETG, NU_PETG = 2100.0, 0.35    # fe_a.py nom 2.1 GPa (kd 1.6, hi 2.4); Poisson 0.35 EST
CF = dict(EL=70000.0, ET=7000.0, GLT=4000.0, NULT=0.30, NUTT=0.40)   # fe_a.py nom 70 GPa axial; transverse / shear EST (roll-wrapped tube)
ALLOW = dict(cf_axial=350.0, cf_hoop=40.0, cf_shear=30.0, petg=20.0, petg_ilay=9.5, bond=2.0)
KF, KP = 1.5 * 1.15, 1.5 * 1.15 * 1.25   # structures_a.py: CFRP/metal 1.725, printed/bonded 2.156

# ---------------- loads (limit) ----------------
G = 9.80665
T_CAP, Q_CAP = 8.81, 0.130        # arm_cup_checks.md: APC 9x4.5MR at the 0.90 spin cap, 9,349 rpm
T_UNC, Q_UNC = 10.38, 0.153       # uncapped fault (structures_a.py)
F_1P = 0.96                       # 1 g mm imbalance at 9,349 rpm (iter3_run.md, EST)
I_ROT = 0.01106 * (9 * 25.4e-3) ** 2 / 12 + 0.025 * 0.014 ** 2   # prop 11.06 g as a rod of 9 in + bell 25 g at 14 mm (EST), kg m2
W_CAP = 9349 * 2 * math.pi / 60
PITCH_RATE = 3.0                  # rad/s (172 deg/s) EST bound on the transition pitch rate (no SITL value recorded)
M_GYRO = I_ROT * W_CAP * PITCH_RATE   # N m
F_STRIKE, R_BLADE = 30.0, 0.080   # structures_a.py strike EST; blade lever arm_cup_checks.py


def build_mesh(level, path, variant='asdrawn'):
    import gmsh
    h = level
    gmsh.initialize(['-noenv'])
    gmsh.option.setNumber('General.Terminal', 0)
    gmsh.model.add('arm')
    occ = gmsh.model.occ
    if variant == 'current':
        return build_mesh_current(level, path, occ, gmsh)
    # hub
    slv = occ.addCylinder(SLV_X0, 0, 0, SLV_X1 - SLV_X0, 0, 0, SLV_R)
    extra_hub = []
    if variant == 'box':                                   # hub fix (D-202): box spokes merged into a thick core round the bridge tube
        hx, hz, bw, rc = BOX
        core = occ.addCylinder(-hx, 0, 0, 2 * hx, 0, 0, rc)
        if BOX_YEND:                                       # box to the socket floor, then a lofted taper (rectangle -> circle) onto the deep boss
            web = occ.addBox(-hx, 0, -hz, 2 * hx, B_R0, 2 * hz)
            rdeep = BOX_DEEP_R or B_RI
            cone = occ.addCone(0, B_R0, 0, 0, BOX_YEND - B_R0, 0, hx, rdeep)
            slab = occ.addBox(-hx - 1, B_R0 - 1, -max(hz, rdeep), 2 * hx + 2, BOX_YEND - B_R0 + 2, 2 * max(hz, rdeep))
            taper, _ = occ.intersect([(3, cone)], [(3, slab)])
            extra_hub.extend(taper)
        else:
            web = occ.addBox(-hx, 0, -hz, 2 * hx, B_R1 - B_MOUTH, 2 * hz)   # D-202: the box also wraps the deep socket
        slv, _ = occ.fuse([(3, slv)], [(3, core)]); slv = slv[0][1]
    elif variant == 'spoke':                                 # design-fix candidate: hollow round spoke instead of the web
        web = occ.addCylinder(0, WEB_Y0, 0, 0, WEB_Y1 - WEB_Y0, 0, SPK_RO)
    else:
        web = occ.addBox(-WEB_D / 2, WEB_Y0, -WEB_T / 2, WEB_D, WEB_Y1 - WEB_Y0, WEB_T)
    b_in = occ.addCylinder(0, B_R0, 0, 0, B_R1 - B_MOUTH - B_R0, 0, (BOX_DEEP_R or B_RI) if variant == 'box' else B_RI)
    b_mo = occ.addCylinder(0, B_R1 - B_MOUTH, 0, 0, B_MOUTH, 0, B_RO)
    hub, _ = occ.fuse([(3, slv)], [(3, web), (3, b_in), (3, b_mo)] + extra_hub)
    bore = occ.addCylinder(SLV_X0 - 1, 0, 0, SLV_X1 - SLV_X0 + 2, 0, 0, SLV_BORE)
    sock = occ.addCylinder(0, R_IN, 0, 0, B_R1 + 2 - R_IN, 0, TUBE_RO)
    hcuts = [(3, bore), (3, sock)]
    if variant == 'box':                                   # spoke cavity (phase-lead conduit), closed by the core and the socket floor
        hx, hz, bw, rc = BOX
        hcuts.append((3, occ.addBox(-hx + bw, rc + 0.5, -hz + bw, 2 * (hx - bw), B_R0 - rc - 0.5, 2 * (hz - bw))))
    if variant == 'spoke':                                 # bore of the spoke (lead conduit), closed by the sleeve wall and the socket floor
        hcuts.append((3, occ.addCylinder(0, SLV_R + 0.3, 0, 0, B_R0 - SLV_R - 0.3, 0, SPK_RI)))
    hub, _ = occ.cut(hub, hcuts)
    # tube
    to = occ.addCylinder(0, R_IN, 0, 0, R_M - R_IN, 0, TUBE_RO)
    ti = occ.addCylinder(0, R_IN - 1, 0, 0, R_M - R_IN + 2, 0, TUBE_RI)
    tube, _ = occ.cut([(3, to)], [(3, ti)])
    # cup, motor frame (plate normal x), then rotated by CANT about the arm axis
    y0, y1, ro = CUP_SLV
    cs = occ.addCylinder(0, R_M + y0, 0, 0, y1 - y0, 0, ro)
    pl = occ.addBox(CUP_PL[0], R_M - CUP_HALF, -CUP_HALF, CUP_PL[1] - CUP_PL[0], 2 * CUP_HALF, 2 * CUP_HALF)
    cup, _ = occ.fuse([(3, cs)], [(3, pl)])
    occ.synchronize()
    # rounded plate corners: fillet the 4 edges parallel to x at the plate corners
    eds = []
    for d, e in gmsh.model.getEntities(1):
        bb = gmsh.model.getBoundingBox(d, e)
        if abs(bb[3] - bb[0] - (CUP_PL[1] - CUP_PL[0])) < 1e-6 and abs(abs(bb[1] - R_M) - CUP_HALF) < 1e-6 and abs(abs(bb[2]) - CUP_HALF) < 1e-6:
            eds.append(e)
    cupv = [t for d, t in cup]
    if eds:
        cup = occ.fillet(cupv, eds, [CUP_RC], removeVolume=True)
    cuts = [occ.addCylinder(0, R_M + y0 - 1, 0, 0, y1 - y0 + 2, 0, TUBE_RO)]
    for sy in (1, -1):
        for sz in (1, -1):
            cuts.append(occ.addCylinder(CUP_PL[0] - 0.6, R_M + sy * PAT_Y, sz * PAT_Z, 5.6, 0, 0, HOLE_R))
    for sz in (1, -1):
        cuts.append(occ.addCylinder(POCKET_X[0], R_M - PAT_Y, sz * PAT_Z, POCKET_X[1] - POCKET_X[0], 0, 0, POCKET_R))
    cuts.append(occ.addCylinder(RELIEF_X[0], R_M, 0, RELIEF_X[1] - RELIEF_X[0], 0, 0, RELIEF_R))
    cup, _ = occ.cut(cup, [(3, c) for c in cuts])
    occ.rotate(cup, 0, 0, 0, 0, 1, 0, math.radians(CANT))
    allv, mp = occ.fragment(hub + tube + cup, [])
    occ.synchronize()
    groups = {'hub': [], 'tube': [], 'cup': []}
    for (d, t), kids in zip(hub + tube + cup, mp[:len(hub + tube + cup)]):
        name = 'hub' if (d, t) in hub else 'tube' if (d, t) in tube else 'cup'
        groups[name] += [k[1] for k in kids]
    hub_vol = sum(occ.getMass(3, t) for t in set(groups['hub']))    # mm3, the modelled hub sector (one arm + the sleeve)
    for i, (k, v) in enumerate(groups.items()):
        gmsh.model.addPhysicalGroup(3, sorted(set(v)), i + 1, name=k)
    # size field: fine at the hub and cup, coarse along the free tube
    f = gmsh.model.mesh.field
    s = {0: 1.0, 1: 0.78, 2: 0.6}[level]                  # refinement factor per level
    boxes = [  # (size at level 0, box x0 x1 y0 y1 z0 z1): web 0.8 mm thick, boss walls, sleeve, tube root, tube, cup
        {'asdrawn': (0.45, (-WEB_D / 2 - 0.5, WEB_D / 2 + 0.5, WEB_Y0 - 0.5, WEB_Y1 + 0.5, -1.0, 1.0)),
         'spoke': (0.6, (-SPK_RO - 0.5, SPK_RO + 0.5, WEB_Y0 - 0.5, WEB_Y1 + 0.5, -SPK_RO - 0.5, SPK_RO + 0.5)),
         'box': (min(0.6, BOX[2] * 0.4), (-BOX[0] - 0.5, BOX[0] + 0.5, -BOX[3] - 0.5, WEB_Y1 + 0.5, -max(BOX[1], BOX[3]) - 0.5, max(BOX[1], BOX[3]) + 0.5))}[variant],
        (0.75, (-B_RO - 0.5, B_RO + 0.5, B_R0 - 0.5, B_R1 + 0.5, -B_RO - 0.5, B_RO + 0.5)),
        (0.9, (SLV_X0 - 0.5, SLV_X1 + 0.5, -SLV_R - 0.5, SLV_R + 0.5, -SLV_R - 0.5, SLV_R + 0.5)),
        (0.8, (-6.5, 6.5, R_IN - 1, B_R1 + 20, -6.5, 6.5)),
        (1.2, (-6.5, 6.5, R_IN - 1, R_M + 1, -6.5, 6.5)),
        (1.1, (-21, 21, R_M - 27, R_M + 18, -21, 21)),
    ]
    fl = []
    for v0, bx in boxes:
        b = f.add('Box'); f.setNumber(b, 'VIn', v0 * s); f.setNumber(b, 'VOut', 4.0)
        for k, v in zip(('XMin', 'XMax', 'YMin', 'YMax', 'ZMin', 'ZMax'), (bx[0], bx[1], bx[2], bx[3], bx[4], bx[5])):
            f.setNumber(b, k, v)
        f.setNumber(b, 'Thickness', 2.0)
        fl.append(b)
    mn = f.add('Min'); f.setNumbers(mn, 'FieldsList', fl)
    f.setAsBackgroundMesh(mn)
    gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary', 0)
    gmsh.option.setNumber('Mesh.MeshSizeFromPoints', 0)
    gmsh.option.setNumber('Mesh.MeshSizeFromCurvature', 0)
    gmsh.option.setNumber('Mesh.ElementOrder', 2)
    gmsh.option.setNumber('Mesh.HighOrderOptimize', 1)
    gmsh.option.setNumber('General.NumThreads', 16)
    gmsh.model.mesh.generate(3)
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    X = xyz.reshape(-1, 3)
    idx = {int(t): i for i, t in enumerate(nt)}
    els, mat = [], []
    for i, k in enumerate(groups):
        for v in sorted(set(groups[k])):
            et, _, en = gmsh.model.mesh.getElements(3, v)
            for t, e in zip(et, en):
                if t == 11:
                    a = np.array([idx[int(n)] for n in e]).reshape(-1, 10)
                    els.append(a); mat.append(np.full(len(a), i))
    E = np.vstack(els); M = np.concatenate(mat)
    used = np.unique(E)
    remap = -np.ones(len(X), int); remap[used] = np.arange(len(used))
    gmsh.finalize()
    print('hub sector volume %.0f mm3 = %.2f g PETG' % (hub_vol, hub_vol * 1.27e-3), flush=True)
    np.savez_compressed(path, X=X[used], E=remap[E], M=M, h=h, hub_vol=hub_vol)
    return X[used], remap[E], M


def _occ_prism(occ, axis, offset, loop, depth):
    """A fusionkit-style prism (cup frame, metres: loop in the plane normal to axis at offset, extruded by depth) as an OCC solid in
    the FEA frame (mm, the cup station at y = R_M)."""
    pts = []
    for u, v in loop:
        p = [0.0, 0.0, 0.0]
        if axis == 'Y':
            p = [u * 1e3, offset * 1e3 + R_M, v * 1e3]
        else:                                          # 'Z': (x, y) loop
            p = [u * 1e3, v * 1e3 + R_M, offset * 1e3]
        pts.append(occ.addPoint(*p))
    lines = [occ.addLine(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    s = occ.addPlaneSurface([occ.addCurveLoop(lines)])
    d = depth * 1e3
    ex = occ.extrude([(2, s)], 0, d if axis == 'Y' else 0, d if axis == 'Z' else 0)
    return [e for e in ex if e[0] == 3][0]


def _cup(occ, gmsh):
    """The motor cup (motor frame, plate normal x), rotated by CANT about the arm axis: same geometry as the as-drawn variant."""
    y0, y1, ro = CUP_SLV
    cs = occ.addCylinder(0, R_M + y0, 0, 0, y1 - y0, 0, ro)
    pl = occ.addBox(CUP_PL[0], R_M - CUP_HALF, -CUP_HALF, CUP_PL[1] - CUP_PL[0], 2 * CUP_HALF, 2 * CUP_HALF)
    cup, _ = occ.fuse([(3, cs)], [(3, pl)])
    occ.synchronize()
    eds = []
    for d, e in gmsh.model.getEntities(1):
        bb = gmsh.model.getBoundingBox(d, e)
        if abs(bb[3] - bb[0] - (CUP_PL[1] - CUP_PL[0])) < 1e-6 and abs(abs(bb[1] - R_M) - CUP_HALF) < 1e-6 and abs(abs(bb[2]) - CUP_HALF) < 1e-6:
            eds.append(e)
    if eds:
        cup = occ.fillet([t for d, t in cup], eds, [CUP_RC], removeVolume=True)
    # D-198 lead collar and end cap (as wing.py)
    col = occ.addCylinder(0, R_M + y1, 0, 0, COL_L, 0, COL_RO)
    cap = occ.addCylinder(0, R_M + y1 + COL_L, 0, 0, COL_CAP, 0, COL_RO)
    extra = [(3, col), (3, cap)]
    if CUP_FIL > 0:                                   # D-210 fillets and collar web: the SAME loops wing.py draws (cup_fillet_loops etc.)
        up, dn, ch, zc = W.cup_fillet_loops()
        web, wzc = W.cup_web_loop()
        extra += [_occ_prism(occ, 'Y', -0.0165, up, 0.0200), _occ_prism(occ, 'Y', -0.0165, dn, 0.0200),
                  _occ_prism(occ, 'Z', -zc, ch, 2 * zc), _occ_prism(occ, 'Y', 0.0035 - 0.00005, web, 0.0053 + 0.00005),
                  _occ_prism(occ, 'Z', -wzc, W.cup_chord_loop(ys=0.0088), 2 * wzc)]
    cup, _ = occ.fuse(cup, extra)
    cuts = [occ.addCylinder(0, R_M + y0 - 1, 0, 0, y1 - y0 + 1 + COL_L, 0, TUBE_RO)]
    for sy in (1, -1):
        for sz in (1, -1):
            cuts.append(occ.addCylinder(CUP_PL[0] - 0.6, R_M + sy * PAT_Y, sz * PAT_Z, 5.6, 0, 0, HOLE_R))
    for sz in (1, -1):
        cuts.append(occ.addCylinder(POCKET_X[0], R_M - PAT_Y, sz * PAT_Z, POCKET_X[1] - POCKET_X[0], 0, 0, POCKET_R))
    cuts.append(occ.addCylinder(RELIEF_X[0], R_M, 0, RELIEF_X[1] - RELIEF_X[0], 0, 0, RELIEF_R))
    cuts.append(occ.addCylinder(PH_X[0], R_M + PH_Y_MM, 0, PH_X[1] - PH_X[0], 0, 0, PH_R))
    cup, _ = occ.cut(cup, [(3, c) for c in cuts])
    occ.rotate(cup, 0, 0, 0, 0, 1, 0, math.radians(CANT))
    return cup


def build_mesh_current(level, path, occ, gmsh):
    """Variant 'current' (see the module docstring): doubler (group 0), continuous tube (group 1), cup (group 2)."""
    s0, s1, dro = CUR_DBL
    ys, pr = CUR_PIN
    yh, hr = CUR_HOLE
    to = occ.addCylinder(0, 0, 0, 0, R_M, 0, TUBE_RO)
    ti = occ.addCylinder(0, -1, 0, 0, R_M + 2, 0, TUBE_RI)
    tube, _ = occ.cut([(3, to)], [(3, ti)])
    do_ = occ.addCylinder(0, s0, 0, 0, s1 - s0, 0, dro)
    di_ = occ.addCylinder(0, s0 - 1, 0, 0, s1 - s0 + 2, 0, TUBE_RO)
    dbl, _ = occ.cut([(3, do_)], [(3, di_)])
    pin = occ.addCylinder(-dro - 1, ys, 0, 2 * dro + 2, 0, 0, pr)                    # pin hole along x, both walls
    hole = occ.addCylinder(0, yh, 0, 0, 0, dro + 1, hr)                                # lead exit, +z wall and the doubler
    tube, _ = occ.cut(tube, [(3, pin), (3, hole)], removeTool=False)
    dbl, _ = occ.cut(dbl, [(3, hole)])
    cup = _cup(occ, gmsh)
    allv, mp = occ.fragment(dbl + tube + cup, [])
    occ.synchronize()
    groups = {'hub': [], 'tube': [], 'cup': []}
    for (d, t), kids in zip(dbl + tube + cup, mp[:len(dbl + tube + cup)]):
        name = 'hub' if (d, t) in dbl else 'tube' if (d, t) in tube else 'cup'
        groups[name] += [k[1] for k in kids]
    for i, (k, v) in enumerate(groups.items()):
        gmsh.model.addPhysicalGroup(3, sorted(set(v)), i + 1, name=k)
    f = gmsh.model.mesh.field
    sc = {0: 1.0, 1: 0.78, 2: 0.6}[level]
    boxes = [(0.6, (-dro - 0.5, dro + 0.5, -0.5, s1 + 6, -dro - 0.5, dro + 0.5)),     # crossing, pin, doubler, lead exit, sleeve exit
             (1.2, (-6.5, 6.5, -1, R_M + 1, -6.5, 6.5)),                                 # free tube
             (1.1, (-21, 21, R_M - 27, R_M + 18, -21, 21)),                              # cup
             (0.45, (-10, -2, R_M + 1, R_M + 7, -10, 10)),                               # D-210: sleeve end / plate fillet (the old hotspot)
             (0.7, (-11, -2, R_M - 18, R_M + 1, -12, 12))]                               # D-210: sleeve / plate fillets along the arm
    fl = []
    for v0, bx in boxes:
        b = f.add('Box'); f.setNumber(b, 'VIn', v0 * sc); f.setNumber(b, 'VOut', 4.0)
        for k, v in zip(('XMin', 'XMax', 'YMin', 'YMax', 'ZMin', 'ZMax'), bx):
            f.setNumber(b, k, v)
        f.setNumber(b, 'Thickness', 2.0)
        fl.append(b)
    mn = f.add('Min'); f.setNumbers(mn, 'FieldsList', fl)
    f.setAsBackgroundMesh(mn)
    for k, v in (('Mesh.MeshSizeExtendFromBoundary', 0), ('Mesh.MeshSizeFromPoints', 0), ('Mesh.MeshSizeFromCurvature', 0),
                 ('Mesh.ElementOrder', 2), ('Mesh.HighOrderOptimize', 1), ('General.NumThreads', 16)):
        gmsh.option.setNumber(k, v)
    gmsh.model.mesh.generate(3)
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    X = xyz.reshape(-1, 3)
    idx = {int(t): i for i, t in enumerate(nt)}
    els, mat = [], []
    for i, k in enumerate(groups):
        for v in sorted(set(groups[k])):
            et, _, en = gmsh.model.mesh.getElements(3, v)
            for t, e in zip(et, en):
                if t == 11:
                    a = np.array([idx[int(n)] for n in e]).reshape(-1, 10)
                    els.append(a); mat.append(np.full(len(a), i))
    E = np.vstack(els); M = np.concatenate(mat)
    used = np.unique(E)
    remap = -np.ones(len(X), int); remap[used] = np.arange(len(used))
    gmsh.finalize()
    np.savez_compressed(path, X=X[used], E=remap[E], M=M, h=level, hub_vol=0.0)
    return X[used], remap[E], M


# ---------------- tet10 ----------------
GP = np.array([[0.58541020, 0.13819660, 0.13819660], [0.13819660, 0.58541020, 0.13819660],
               [0.13819660, 0.13819660, 0.58541020], [0.13819660, 0.13819660, 0.13819660]])
GW = np.full(4, 1 / 24)


def dN(r, s, t):
    """Derivatives of the 10 gmsh tet10 shape functions (node order 0-3 corners, 4:01 5:12 6:20 7:03 8:23 9:13) wrt r, s, t."""
    u = 1 - r - s - t
    L = [u, r, s, t]
    dL = np.array([[-1, -1, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
    d = np.zeros((10, 3))
    for i in range(4):
        d[i] = (4 * L[i] - 1) * dL[i]
    for k, (i, j) in enumerate([(0, 1), (1, 2), (2, 0), (0, 3), (2, 3), (1, 3)]):
        d[4 + k] = 4 * (L[i] * dL[j] + L[j] * dL[i])
    return d


DN = np.array([dN(*g) for g in GP])            # (4, 10, 3)


def D_iso(E, nu):
    l, m = E * nu / ((1 + nu) * (1 - 2 * nu)), E / (2 * (1 + nu))
    D = np.zeros((6, 6)); D[:3, :3] = l; D[np.arange(3), np.arange(3)] += 2 * m; D[3:, 3:] = np.eye(3) * m
    return D


def D_ti_y():
    """Transversely isotropic, fibre axis = y (Voigt order xx yy zz yz xz xy)."""
    EL, ET, GLT, nLT, nTT = CF['EL'], CF['ET'], CF['GLT'], CF['NULT'], CF['NUTT']
    S = np.zeros((6, 6))
    S[0, 0] = S[2, 2] = 1 / ET; S[1, 1] = 1 / EL
    S[0, 2] = S[2, 0] = -nTT / ET
    S[0, 1] = S[1, 0] = S[2, 1] = S[1, 2] = -nLT / EL
    S[3, 3] = 1 / GLT; S[5, 5] = 1 / GLT; S[4, 4] = 2 * (1 + nTT) / ET
    return np.linalg.inv(S)


def Bmat(G):
    """G: (..., 10, 3) global derivatives -> B (..., 6, 30)."""
    sh = G.shape[:-2]
    B = np.zeros(sh + (6, 30))
    gx, gy, gz = G[..., 0], G[..., 1], G[..., 2]
    B[..., 0, 0::3] = gx; B[..., 1, 1::3] = gy; B[..., 2, 2::3] = gz
    B[..., 3, 1::3] = gz; B[..., 3, 2::3] = gy
    B[..., 4, 0::3] = gz; B[..., 4, 2::3] = gx
    B[..., 5, 0::3] = gy; B[..., 5, 1::3] = gx
    return B


def assemble(X, E, M, Ds):
    ne = len(E)
    XE = X[E]                                              # (ne, 10, 3)
    K = np.zeros((ne, 30, 30))
    Bs, dets = [], []
    for g in range(4):
        J = np.einsum('ai,eaj->eij', DN[g], XE)           # (ne, 3, 3): J[i, j] = d x_j / d r_i
        det = np.linalg.det(J)
        Gl = np.linalg.solve(J[:, None, :, :], DN[g][None, :, :, None])[..., 0]   # (ne, 10, 3) global derivatives
        B = Bmat(Gl)
        for m, D in enumerate(Ds):
            s = M == m
            K[s] += np.einsum('eki,kl,elj->eij', B[s], D, B[s]) * (GW[g] * det[s])[:, None, None]
        Bs.append(B); dets.append(det)
    if np.any(np.array(dets) <= 0):
        raise SystemExit('negative Jacobian in %d elements' % int((np.array(dets) <= 0).sum()))
    dof = (3 * E[:, :, None] + np.arange(3)).reshape(ne, 30)
    rows = np.repeat(dof, 30, axis=1).ravel(); cols = np.tile(dof, (1, 30)).ravel()
    Kg = sp.coo_matrix((K.ravel(), (rows, cols)), shape=(3 * len(X), 3 * len(X))).tocsc()
    return Kg, Bs, dof, np.array(dets)


def motor_frame():
    c, s = math.cos(math.radians(CANT)), math.sin(math.radians(CANT))
    rot = lambda v: np.array([v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c])
    n = rot((-1.0, 0, 0))                                  # motor axis, plate -> motor (thrust pulls the motor this way)
    P = np.array([0.0, R_M, 0.0]) + 12.0 * n               # centre of the motor base face (plate front face)
    return rot, n, P


def rbe3_nodes(X):
    rot, n, P = motor_frame()
    c, s = math.cos(math.radians(-CANT)), math.sin(math.radians(-CANT))
    xl = X[:, 0] * c + X[:, 2] * s; zl = -X[:, 0] * s + X[:, 2] * c; yl = X[:, 1] - R_M      # back to the motor frame
    tol = 0.02
    front = (np.abs(xl - CUP_PL[0]) < tol) & (np.hypot(yl, zl) <= BASE_R)
    rear = np.zeros(len(X), bool)
    for sy in (1, -1):
        for sz in (1, -1):
            r = np.hypot(yl - sy * PAT_Y, zl - sz * PAT_Z)
            rear |= (np.abs(xl - CUP_PL[1]) < tol) & (r <= HEAD_R + 1e-6) & (r >= HOLE_R - 1e-6)
    return np.where(front | rear)[0]


def rbe3_loads(X, nodes, F, Mo, P):
    """Nodal forces on `nodes` statically equivalent to force F and moment Mo at P (uniform weights)."""
    r0 = X[nodes].mean(0)
    r = X[nodes] - r0
    J = np.eye(3) * (r * r).sum() - r.T @ r
    Mc = Mo + np.cross(P - r0, F)
    a = np.linalg.solve(J, Mc)
    return F / len(nodes) + np.cross(a, r)


def fixed_nodes(X):
    if VARIANT == 'current':                               # outer surface inside the hub sleeve: tube (y < doubler) and doubler
        r = np.hypot(X[:, 0], X[:, 2])
        s0, s1, dro = CUR_DBL
        tube_o = (np.abs(r - TUBE_RO) < 0.02) & (X[:, 1] <= min(s0, CUR_SLV) + 0.01)
        dbl_o = (np.abs(r - dro) < 0.02) & (X[:, 1] >= s0 - 0.01) & (X[:, 1] <= CUR_SLV + 0.01)
        return np.where(tube_o | dbl_o)[0]
    r = np.hypot(X[:, 1], X[:, 2])
    return np.where((np.abs(r - SLV_BORE) < 0.02) & (X[:, 0] > SLV_X0 - 0.01) & (X[:, 0] < SLV_X1 + 0.01))[0]


def unit_cases():
    """Six unit load cases at the motor base point: F along n, t1, t2 (1 N) and M about n, t1, t2 (1 N mm)."""
    rot, n, P = motor_frame()
    t1 = np.array([0.0, 1.0, 0.0])                         # along the arm
    t2 = np.cross(n, t1)                                   # tangential in the motor frame
    return n, t1, t2, P


def load_cases():
    """Limit load cases as (name, flight?, list of combos); a combo is (F[3], M[3]) at the motor base point P (N, N mm)."""
    n, t1, t2, P = unit_cases()
    lev = X_PROP - 12.0                                    # prop plane above the motor base face, mm
    def prop_force(Fv):                                    # force at the prop plane -> force + moment at P
        return Fv, np.cross(lev * n, Fv)
    cases = []
    for name, T, Q, flight in (('F1 hover/transition at the spin cap, pitch-over, 1P', T_CAP, Q_CAP, True),
                               ('F2 uncapped motor fault + pitch-over + 1P', T_UNC, Q_UNC, True)):
        combos = []
        for sq in (1, -1):
            for gyro_axis in (t1, t2):
                for sg in (1, -1):
                    for p_dir in (t1, t2, -t1, -t2):
                        F = T * n; Mo = sq * Q * 1e3 * n + sg * M_GYRO * 1e3 * gyro_axis
                        Fp, Mp = prop_force(F_1P * p_dir)
                        combos.append((F + Fp, Mo + Mp))
        cases.append((name, flight, combos))
    combos = []
    for d in (t1, t2, -t1, -t2):
        combos.append(prop_force(F_STRIKE * d))
    cases.append(('S2 prop strike 30 N transverse at the prop plane (ground handling, not flight)', False, combos))
    cases.append(('S3 blade stop, torque 30 N x 80 mm about the shaft (ground handling, not flight)', False,
                  [(np.zeros(3), s * F_STRIKE * R_BLADE * 1e3 * n) for s in (1, -1)]))
    cases.append(('S1 prop strike 30 N along the shaft (ground handling, not flight)', False, [(s * F_STRIKE * n, np.zeros(3)) for s in (1, -1)]))
    return cases


def principal(sig):
    """sig (..., 6) Voigt -> (max principal, von Mises)."""
    xx, yy, zz, yz, xz, xy = [sig[..., i] for i in range(6)]
    T = np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1), np.stack([xz, yz, zz], -1)], -2)
    ev = np.linalg.eigvalsh(T)
    vm = np.sqrt(0.5 * ((xx - yy) ** 2 + (yy - zz) ** 2 + (zz - xx) ** 2) + 3 * (yz ** 2 + xz ** 2 + xy ** 2))
    return ev[..., -1], vm


def tube_local(sig, xg):
    """Tube stress in cylindrical components about the arm axis (y): axial yy, hoop, max shear on the axial planes."""
    th = np.arctan2(xg[..., 2], xg[..., 0])
    c, s = np.cos(th), np.sin(th)
    xx, yy, zz, yz, xz, xy = [sig[..., i] for i in range(6)]
    hoop = xx * s * s + zz * c * c - 2 * xz * s * c
    ty_r = xy * c + yz * s; ty_t = -xy * s + yz * c
    return yy, hoop, np.hypot(ty_r, ty_t)


def solve(Kf, RHS):
    """Sparse SPD solve. scipy SuperLU runs out of memory at about 0.9 M unknowns, so the system goes to MATLAB (R2025a on the
    team machine; backslash on a symmetric positive-definite sparse matrix uses CHOLMOD, multithreaded) through raw binary
    files in out_fea/. Small systems (< 200k unknowns) stay in scipy. The residual is checked here either way."""
    if Kf.shape[0] < 200000:
        lu = spla.splu(Kf.tocsc(), permc_spec='COLAMD')
        X = np.column_stack([lu.solve(RHS[:, k]) for k in range(RHS.shape[1])])
    else:
        import subprocess
        T = sp.triu(Kf).tocoo()
        d = os.path.join(OUT, 'sys')
        os.makedirs(d, exist_ok=True)
        (T.row + 1).astype(np.int32).tofile(os.path.join(d, 'i.bin')); (T.col + 1).astype(np.int32).tofile(os.path.join(d, 'j.bin'))
        T.data.astype(np.float64).tofile(os.path.join(d, 'v.bin')); RHS.astype(np.float64).ravel(order='F').tofile(os.path.join(d, 'b.bin'))
        n, m = Kf.shape[0], RHS.shape[1]
        dd = d.replace('\\', '/')
        cmd = ("d='%s'; rd=@(f,t) fread(fopen(fullfile(d,f)),inf,t); i=rd('i.bin','int32'); j=rd('j.bin','int32'); v=rd('v.bin','double'); "
               "K=sparse(double(i),double(j),v,%d,%d); clear i j v; K=K+triu(K,1)'; B=reshape(rd('b.bin','double'),%d,%d); "
               "tic; P=dissect(K); [R,flag]=chol(K(P,P),'lower'); fprintf('chol flag %%d, %%.1f s, nnz(R) %%.0f M\\n',flag,toc,nnz(R)/1e6); "   # nested dissection: less fill than AMD on 3-D meshes
               "x=zeros(size(B)); x(P,:)=R'\\(R\\B(P,:)); "
               "for it=1:3, r=B-K*x; dx=zeros(size(B)); dx(P,:)=R'\\(R\\r(P,:)); x=x+dx; end; "      # iterative refinement (the PETG / CFRP contrast)
               "fprintf('solved %%.1f s, residual %%.1e\\n',toc,max(vecnorm(B-K*x)./vecnorm(B))); "
               "fid=fopen(fullfile(d,'x.bin'),'w'); fwrite(fid,x,'double'); fclose(fid); fclose('all');") % (dd, n, n, n, m)
        r = subprocess.run(['matlab', '-batch', cmd], capture_output=True, text=True, timeout=7200)
        print(r.stdout.strip()[-400:], r.stderr.strip()[-400:])
        X = np.fromfile(os.path.join(d, 'x.bin'), dtype=np.float64).reshape(m, n).T
        for f_ in ('i.bin', 'j.bin', 'v.bin', 'b.bin', 'x.bin'):
            os.remove(os.path.join(d, f_))
    res = np.linalg.norm(Kf @ X - RHS, axis=0) / np.linalg.norm(RHS, axis=0)
    print('relative residual per load case:', ' '.join('%.1e' % v for v in res), flush=True)
    if res.max() > 1e-4:                                    # the floor is about 3e-5 (CFRP / PETG contrast, 0.8 mm web); equilibrium is checked in run()
        raise SystemExit('solve residual too large')
    return X


def run(level, variant='asdrawn'):
    global VARIANT
    tag, variant = variant, ('box' if variant.startswith('box') else 'current' if variant.startswith('current') else variant)
    VARIANT = variant
    os.makedirs(OUT, exist_ok=True)
    mp = os.path.join(OUT, 'mesh_L%d_%s.npz' % (level, tag))
    t0 = time.time()
    if os.path.exists(mp):
        d = np.load(mp); X, E, M = d['X'], d['E'], d['M']
    else:
        X, E, M = build_mesh(level, mp, variant)
    t1_ = time.time()
    Ds = [D_ti_y() if variant == 'current' else D_iso(E_PETG, NU_PETG), D_ti_y(), D_iso(E_PETG, NU_PETG)]   # hub (current: the CFRP doubler), tube, cup
    K, Bs, dof, dets = assemble(X, E, M, Ds)
    fix = fixed_nodes(X)
    fd = np.zeros(3 * len(X), bool); fd[(3 * fix[:, None] + np.arange(3)).ravel()] = True
    free = np.where(~fd)[0]
    Kf = K[free][:, free].tocsc()
    t2_ = time.time()
    t3_ = time.time()
    nodes = rbe3_nodes(X)
    n, t1, t2, P = unit_cases()
    basis = [(v, np.zeros(3)) for v in (n, t1, t2)] + [(np.zeros(3), v) for v in (n, t1, t2)]
    RHS = np.zeros((len(free), 6))
    for k, (F, Mo) in enumerate(basis):
        f = np.zeros((len(X), 3)); f[nodes] = rbe3_loads(X, nodes, F, Mo, P)
        RHS[:, k] = f.ravel()[free]
    U = np.zeros((6, 3 * len(X)))
    U[:, free] = solve(Kf, RHS).T
    t4_ = time.time()
    Rf = (K @ U.T).T.reshape(6, -1, 3)                       # reactions at the fixed nodes must balance each unit load
    eq = []
    for k, (F, Mo) in enumerate(basis):
        Rs = -Rf[k, fix].sum(0)
        Mr = -np.cross(X[fix] - P, Rf[k, fix]).sum(0)
        eq.append(max(np.linalg.norm(Rs - F), np.linalg.norm(Mr - Mo) / 100.0))
    print('equilibrium error per unit case (N, or N mm / 100 mm):', ' '.join('%.1e' % v for v in eq), flush=True)
    # stresses at Gauss points for the 6 unit cases: S[k, e, g, 6]
    XE = X[E]
    xg = np.stack([np.einsum('a,eai->ei', Nq(GP[g]), XE) for g in range(4)], 1)
    S = np.zeros((6, len(E), 4, 6))
    for g in range(4):
        for m, D in enumerate(Ds):
            s = M == m
            for k in range(6):
                ue = U[k][dof[s]]
                S[k, s, g] = np.einsum('kl,elj,ej->ek', D, Bs[g][s], ue)
    # checks: tip deflection under 1 N thrust vs the cantilever, axial stress at mid-span vs Mc/I
    tipn = np.argmin(np.linalg.norm(X - P, axis=1))
    info = dict(level=level, nodes=int(len(X)), elements=int(len(E)), dof_free=int(len(free)), rbe3_nodes=int(len(nodes)), fixed_nodes=int(len(fix)),
                t_mesh=round(t1_ - t0, 1), t_assemble=round(t2_ - t1_, 1), t_factor=round(t3_ - t2_, 1), t_solve=round(t4_ - t3_, 1), equilibrium_err=[float('%.2e' % v) for v in eq])
    return dict(X=X, E=E, M=M, S=S, U=U, xg=xg, info=info, P=P, n=n, t1=t1, t2=t2)


def Nq(p):
    r, s, t = p
    u = 1 - r - s - t
    L = [u, r, s, t]
    N = [L[i] * (2 * L[i] - 1) for i in range(4)]
    N += [4 * L[i] * L[j] for i, j in [(0, 1), (1, 2), (2, 0), (0, 3), (2, 3), (1, 3)]]
    return np.array(N)


REGIONS_CURRENT = [
    ('doubler', 'Carbon doubler 14 x 12 over the lead exit (CFRP)', 0, lambda x: np.ones(len(x), bool)),
    ('tube_hub', 'Arm tube inside the hub sleeve (CFRP; rigid-hub support: see fea_hub.py for this zone)', 1, lambda x: x[:, 1] < CUR_SLV),
    ('tube_root', 'Arm tube from s 36 mm (judged start) to 30 mm past the sleeve exit (CFRP)', 1, lambda x: (x[:, 1] >= CUR_SLV) & (x[:, 1] < CUR_SLV + 30)),
    ('tube_mid', 'Arm tube, free span (CFRP)', 1, lambda x: (x[:, 1] >= CUR_SLV + 30) & (x[:, 1] < R_M - 40)),
    ('tube_tip', 'Arm tube in and near the cup (CFRP)', 1, lambda x: x[:, 1] >= R_M - 40),
    ('cup', 'Motor cup (PETG)', 2, lambda x: np.ones(len(x), bool)),
]
REGIONS = [  # (key, label, material index, predicate on Gauss-point coordinates)
    ('sleeve', 'Hub bridge sleeve (PETG 1.2 mm)', 0, lambda x: np.hypot(x[:, 1], x[:, 2]) < SLV_R + 0.05),
    ('web', 'Hub radial web (as drawn: PETG 0.8 x 22 mm; spoke variant: tube 13.6 x 10.4)', 0, lambda x: (np.hypot(x[:, 1], x[:, 2]) >= SLV_R + 0.05) & (x[:, 1] < B_R0 + 0.05)),
    ('floor', 'Socket floor and inner boss (PETG, 0.8 mm wall)', 0, lambda x: (x[:, 1] >= B_R0 + 0.05) & (x[:, 1] < B_R1 - B_MOUTH)),
    ('mouth', 'Socket mouth (PETG, 2.0 mm wall)', 0, lambda x: x[:, 1] >= B_R1 - B_MOUTH),
    ('tube_root', 'Arm tube in and near the socket (CFRP)', 1, lambda x: x[:, 1] < B_R1 + 30),
    ('tube_mid', 'Arm tube, free span (CFRP)', 1, lambda x: (x[:, 1] >= B_R1 + 30) & (x[:, 1] < R_M - 40)),
    ('tube_tip', 'Arm tube in and near the cup (CFRP)', 1, lambda x: x[:, 1] >= R_M - 40),
    ('cup', 'Motor cup (PETG)', 2, lambda x: np.ones(len(x), bool)),
]


def evaluate(res, case_list=None, exclude_r=0.0):
    """Peak stresses per region and case (limit loads). exclude_r: skip Gauss points within this distance of the RBE3/fixed nodes."""
    X, E, M, S, xg = res['X'], res['E'], res['M'], res['S'], res['xg']
    n, t1, t2 = res['n'], res['t1'], res['t2']
    basis_dirs = np.vstack([n, t1, t2])
    out = []
    for name, flight, combos in (case_list or load_cases()):
        row = {'case': name, 'flight': flight, 'regions': {}}
        for key, label, m, pred in (REGIONS_CURRENT if VARIANT == 'current' else REGIONS):
            emask = M == m
            xr = xg[emask].reshape(-1, 3)
            sel = pred(xr)
            if VARIANT == 'current' and m != 2:
                sel = sel & (xr[:, 1] >= CUR_NJ)
            if not sel.any():
                row['regions'][key] = dict(label=label + ' (not judged here: inside s %.0f mm, see fea_hub.py)' % CUR_NJ)
                continue
            best = None
            for F, Mo in combos:
                c = np.concatenate([basis_dirs @ F, basis_dirs @ Mo])     # weights of the 6 unit cases
                sig = np.einsum('k,kegs->egs', c, S[:, emask]).reshape(-1, 6)[sel]
                if m == 1 or (VARIANT == 'current' and m == 0):
                    ax, hp, sh = tube_local(sig, xr[sel])
                    vals = dict(axial=float(np.abs(ax).max()), hoop=float(np.abs(hp).max()), shear=float(sh.max()))
                    at = xr[sel][np.argmax(np.abs(ax))]
                else:
                    p1, vm = principal(sig)
                    vals = dict(p1=float(p1.max()), vm=float(vm.max()), p1_p99=float(np.percentile(p1, 99)))
                    at = xr[sel][np.argmax(p1)]
                key_v = vals.get('axial', vals.get('p1'))
                if best is None or key_v > best[0]:
                    if best is not None and 'p1_p99' in best[1]:
                        vals['p1_p99'] = max(vals['p1_p99'], best[1]['p1_p99'])
                    best = (key_v, vals, at.tolist())
                elif 'p1_p99' in vals:
                    best[1]['p1_p99'] = max(best[1]['p1_p99'], vals['p1_p99'])
            row['regions'][key] = dict(label=label, **best[1], at=[round(v, 2) for v in best[2]])
        out.append(row)
    return out


def bond_tractions(res, combos):
    """Peak shear and normal traction on the tube/socket and tube/cup interfaces (from the PETG side Gauss points within 0.3 mm)."""
    X, E, M, S, xg = res['X'], res['E'], res['M'], res['S'], res['xg']
    basis_dirs = np.vstack([res['n'], res['t1'], res['t2']])
    out = {}
    # 'current': the doubler bond is judged outside the hub sleeve only (inside it this model clamps the tube and doubler, so the
    # traction at the clamp edge is a support artefact; fea_hub.py gives the sleeve zone). shear_mean: mean shear over the bonded
    # area (the quantity a lap-shear allowable is for, as fea_hub.py judges the hub bond); shear_p99: 99th percentile.
    pairs = (() if VARIANT == 'current' else (('socket', 0, (R_IN, B_R1)),)) + (('cup', 2, (R_M + CUP_SLV[0], R_M)),)
    for key, m, yr in pairs:
        emask = M == m
        xr = xg[emask].reshape(-1, 3)
        r = np.hypot(xr[:, 0], xr[:, 2])
        sel = (r < TUBE_RO + 0.35) & (xr[:, 1] > yr[0]) & (xr[:, 1] < yr[1])
        best = [0, 0, 0, 0]
        nr = np.stack([xr[sel, 0] / r[sel], np.zeros(sel.sum()), xr[sel, 2] / r[sel]], 1)
        for F, Mo in combos:
            c = np.concatenate([basis_dirs @ F, basis_dirs @ Mo])
            sig = np.einsum('k,kegs->egs', c, S[:, emask]).reshape(-1, 6)[sel]
            xx, yy, zz, yz, xz, xy = [sig[:, i] for i in range(6)]
            T = np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1), np.stack([xz, yz, zz], -1)], -2)
            t = np.einsum('eij,ej->ei', T, nr)
            tn = np.einsum('ei,ei->e', t, nr)
            ts = np.linalg.norm(t - tn[:, None] * nr, axis=1)
            best = [max(best[0], float(ts.max())), max(best[1], float(tn.max())),
                    max(best[2], float(np.percentile(ts, 99))), max(best[3], float(ts.mean()))]
        out[key] = dict(shear=best[0], peel=best[1], shear_p99=best[2], shear_mean=best[3], n_points=int(sel.sum()))
    return out


def save_field(res, path):
    """Element-mean max principal (PETG) / |axial| (CFRP) stress for the F1 combo that is worst in the hub, for the figures."""
    name, flight, combos = load_cases()[0]
    S, M, xg = res['S'], res['M'], res['xg']
    bd = np.vstack([res['n'], res['t1'], res['t2']])
    best, bv = None, -1
    hubm = M == (2 if VARIANT == 'current' else 0)
    for F, Mo in combos:
        c = np.concatenate([bd @ F, bd @ Mo])
        p1, _ = principal(np.einsum('k,kegs->egs', c, S[:, hubm]))
        if p1.max() > bv:
            bv, best = p1.max(), c
    sig = np.einsum('k,kegs->egs', best, S)                   # (ne, 4, 6)
    p1, vm = principal(sig)
    ax, _, _ = tube_local(sig.reshape(-1, 6), xg.reshape(-1, 3))
    val = np.where(M == 1, np.abs(ax.reshape(-1, 4)).mean(1), p1.mean(1))
    np.savez_compressed(path, c=xg.mean(1), val=val, M=M)


def save_fields_current(res, path):
    """Variant 'current': per-material surface skins with per-vertex utilisation and stress (max over adjacent elements),
    enveloped over every combo of F1, F2 (flight, factors KP / KF) and S1, S2 (30 N prop strike, damage case at 1.0). Same npz
    layout as fea_hub.save_fields (V<m>, T<m>, U_<case>_<m>, S_<case>_<m>): fea_arm_figs.py writes the Explorer data from it.
    Utilisation: CFRP max(|axial| / 350, |hoop| / 40, shear / 30) x factor; PETG max principal / 20 x factor. Not judged (NaN):
    the tube and doubler within s < CUR_NJ (36 mm: the sleeve plus one tube diameter; rigid-hub support; fea_hub.py covers it)."""
    X, E, M, S, xg = res['X'], res['E'], res['M'], res['S'], res['xg']
    bd = np.vstack([res['n'], res['t1'], res['t2']])
    lc = {c[0][:2]: c for c in load_cases()}
    cases = [('F1', lc['F1'][2], KP, KF), ('F2', lc['F2'][2], KP, KF), ('S1', lc['S1'][2], 1.0, 1.0), ('S2', lc['S2'][2], 1.0, 1.0)]
    xc = xg.mean(1)
    nj = (M != 2) & (xc[:, 1] < CUR_NJ)
    fields = {}
    for name, combos, fp, fc in cases:
        U = np.zeros(len(M)); SG = np.zeros(len(M))
        for F, Mo in combos:
            c = np.concatenate([bd @ F, bd @ Mo])
            sig = np.einsum('k,kegs->egs', c, S)
            for m in range(3):
                sel = M == m
                sg = sig[sel]
                if m == 2:
                    p1, _ = principal(sg); u = p1 * fp / ALLOW['petg']; s_ = p1
                else:
                    ax, hp, sh = tube_local(sg.reshape(-1, 6), xg[sel].reshape(-1, 3))
                    ax, hp, sh = (v.reshape(-1, 4) for v in (ax, hp, sh))
                    r = np.stack([np.abs(ax) / ALLOW['cf_axial'], np.abs(hp) / ALLOW['cf_hoop'], sh / ALLOW['cf_shear']])
                    k = r.argmax(0); u = r.max(0) * fc; s_ = np.choose(k, [np.abs(ax), np.abs(hp), sh])
                U[sel] = np.maximum(U[sel], u.max(1)); SG[sel] = np.maximum(SG[sel], s_.max(1))
        U[nj] = np.nan; SG[nj] = np.nan
        fields[name] = (U, SG)
        print('fields %s: max utilisation %.2f (outside the sleeve)' % (name, np.nanmax(U)), flush=True)
    out = {'cases': np.array([c[0] for c in cases])}
    C4 = E[:, :4]
    for m in range(3):
        el = np.where(M == m)[0]
        f = np.concatenate([C4[el][:, [0, 1, 2]], C4[el][:, [0, 1, 3]], C4[el][:, [0, 2, 3]], C4[el][:, [1, 2, 3]]])
        opp = np.concatenate([C4[el][:, 3], C4[el][:, 2], C4[el][:, 1], C4[el][:, 0]])
        fe = np.tile(el, 4)
        key = np.sort(f, 1)
        _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
        b = cnt[inv.ravel()] == 1
        f, opp, fe = f[b], opp[b], fe[b]
        a, bb, cc = X[f[:, 0]], X[f[:, 1]], X[f[:, 2]]
        flip = np.einsum('ij,ij->i', np.cross(bb - a, cc - a), X[opp] - a) > 0
        f[flip] = f[flip][:, [0, 2, 1]]
        vid, tri = np.unique(f.ravel(), return_inverse=True)
        tri = tri.reshape(-1, 3)
        out['V%d' % m] = X[vid].astype(np.float32); out['T%d' % m] = tri.astype(np.int32)
        for name in fields:
            for j, lab in enumerate(('U', 'S')):
                v = np.full(len(vid), -np.inf)
                fv = fields[name][j][fe]
                np.maximum.at(v, tri.ravel(), np.repeat(np.nan_to_num(fv, nan=-np.inf), 3))
                v[~np.isfinite(v)] = np.nan
                out['%s_%s_%d' % (lab, name, m)] = v.astype(np.float32)
        print('skin material %d: %d vertices, %d triangles' % (m, len(vid), len(tri)), flush=True)
    np.savez_compressed(path, **out)


def checks(res):
    """Beam checks: tip deflection along n for 1 N along n; axial stress at mid-span vs M c / I."""
    X, U, P, n = res['X'], res['U'], res['P'], res['n']
    tip = np.argmin(np.abs(X[:, 1] - (R_M - 30)) + 10 * np.abs(np.hypot(X[:, 0], X[:, 2]) - TUBE_RO))
    d = U[0].reshape(-1, 3)[tip] @ n
    y_cl = CUR_SLV if VARIANT == 'current' else B_R1       # clamp: the sleeve exit (current) or the socket mouth (as drawn)
    I = math.pi / 64 * ((2 * TUBE_RO) ** 4 - (2 * TUBE_RI) ** 4)
    Lr = R_M - 30 - y_cl
    d_beam = (1 * (R_M - y_cl) * Lr ** 2 / (2 * CF['EL'] * I) - 1 * Lr ** 3 / (6 * CF['EL'] * I))   # point load at R_M on a clamp, deflection at y = R_M - 30
    ymid = (y_cl + R_M) / 2
    xr = res['xg'][res['M'] == 1].reshape(-1, 3)
    near = np.abs(xr[:, 1] - ymid) < 2.0
    sig = res['S'][0, res['M'] == 1].reshape(-1, 6)[near]
    ax, _, _ = tube_local(sig, xr[near])
    m_beam = 1 * (R_M - ymid) * TUBE_RO / I
    return dict(tip_defl_1N_mm=float(d), tip_defl_beam_clamped_at_mouth_mm=float(d_beam),
                mid_axial_1N_MPa=float(np.abs(ax).max()), mid_axial_beam_MPa=float(m_beam))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--level', default='1')
    ap.add_argument('--variant', default='asdrawn', choices=['asdrawn', 'spoke', 'box', 'current'])
    ap.add_argument('--mesh-only', action='store_true', help='build and save the mesh, print its size, stop (no solve)')
    ap.add_argument('--box', default=None, help='hx,hz,wall,core_r in mm')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    levels = [0, 1, 2] if a.level == 'all' else [int(a.level)]
    for lv in levels:
        if a.box:
            vals = [float(v) for v in a.box.split(',')]
            BOX[:] = vals[:4]
            globals()['BOX_YEND'] = vals[4] if len(vals) > 4 else None
            globals()['BOX_DEEP_R'] = vals[5] if len(vals) > 5 else None
        if a.mesh_only:
            mp_ = os.path.join(OUT, 'mesh_L%d_%s.npz' % (lv, a.variant + a.tag))
            X_, E_, M_ = build_mesh(lv, mp_, a.variant)
            print('mesh only: %d nodes, %d elements, about %d unknowns' % (len(X_), len(E_), 3 * len(X_)))
            raise SystemExit
        res = run(lv, a.variant + a.tag)
        ev = evaluate(res)
        bonds = {name: bond_tractions(res, combos) for name, fl, combos in load_cases()}
        ck = checks(res)
        out = dict(info=res['info'], checks=ck, cases=ev, bonds=bonds,
                   loads=dict(T_CAP=T_CAP, Q_CAP=Q_CAP, T_UNC=T_UNC, Q_UNC=Q_UNC, F_1P=F_1P, M_GYRO_Nm=M_GYRO, I_ROT=I_ROT, PITCH_RATE=PITCH_RATE))
        json.dump(out, open(os.path.join(OUT, 'result_L%d_%s.json' % (lv, a.variant + a.tag)), 'w'), indent=1)
        save_field(res, os.path.join(OUT, 'field_L%d_%s.npz' % (lv, a.variant + a.tag)))
        if VARIANT == 'current':
            save_fields_current(res, os.path.join(OUT, 'arm_fields_L%d_%s.npz' % (lv, a.variant + a.tag)))
        print(json.dumps(res['info']))
        print(json.dumps(ck))
        for c in ev:
            print(c['case'])
            for k, v in c['regions'].items():
                print('   %-10s %s' % (k, {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != 'label'}))
        print(json.dumps(bonds, indent=0)[:1500])
