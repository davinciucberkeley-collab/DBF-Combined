"""stop_check.py - QP-4 FIXES2 G10: 2-D clearance of the lead strip / tabs to the lens-cap cavity and the stop-boss contact, at the mechanical stop.
    python -I redesign/qp/A/cad/stop_check.py      (stdlib + a_model.py; prints markdown, writes out/STOP_CHECK.md)
Section in the XZ plane (the strip, tabs and caps are prisms along y, so the 2-D distance is the 3-D distance except at the cap end walls, which are 2 mm
beyond the strip ends). Poses: every 0.5 deg from -STOP to +STOP, plus +-22 deg (calibration error, past the stop).  Distances in mm."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_model as m

def dens(poly, step=0.00005):
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        n = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) / step))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(n)]
    return out

def seg_dist(pt, poly_open):
    best = 1e9
    for i in range(len(poly_open) - 1):
        a, b = poly_open[i], poly_open[i + 1]
        dx, dz = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dz * dz
        t = 0 if L2 == 0 else max(0, min(1, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dz) / L2))
        best = min(best, math.hypot(pt[0] - a[0] - t * dx, pt[1] - a[1] - t * dz))
    return best

def pip(pt, poly):
    x, z = pt; ins = False
    for i in range(len(poly)):
        (x1, z1), (x2, z2) = poly[i], poly[(i + 1) % len(poly)]
        if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1) + x1: ins = not ins
    return ins

def rot(poly, a): return [m._rot_pt(p, a) for p in poly]

def tab_top_face(side, a):
    xr, zr = m.XH - 0.0004, m.HINGE_Z - 0.0035; t = m.BAL_ARM_T / 2; xe = m.XH - m.BAL_REACH + m.BAL_L / 2; zc = m.HINGE_Z + m.BAL_DZ
    sg = 1 if side == 'U' else -1
    A, B = (xr, zr + sg * t), (xe, zc + sg * t)
    return [m._rot_pt((A[0] + (B[0] - A[0]) * s, A[1] + (B[1] - A[1]) * s), a) for s in [i / 200 for i in range(201)]]

L = []
def P(s=""): print(s); L.append(s)
P("# G10 stop and cap check (stop_check.py)"); P()
P("Mechanical stop %.1f deg; authority (software, SERVO5/6, plant) %.1f deg; cap wall %.1f mm; design clearance %.1f mm." % (m.ELEV_STOP, m.ELEV_LIM, m.CAP_WALL * 1e3, m.CAP_CLR * 1e3)); P()
P("| side | cap outer height max (mm) | cap x range (mm) | lead poke beyond the airfoil at the stop (mm) | min lead/tab to cap cavity over -21..+21 (mm) | at angle | min lead/tab to cap at +-22 (mm) | boss to tab gap at the stop (mm) | boss to lead at the stop (mm) | boss penetration into the tab at 22 deg (mm) |")
P("|---|---|---|---|---|---|---|---|---|---|")
ok = True
for sd in 'UL':
    loop, outer, inner = m.cap_loop(sd)
    xs, ho = m.cap_profile(sd)
    # cavity ceiling polyline: inner profile; only the part of the cap that is a cavity (inner above the skin by > 1e-5)
    cav = [p for p in inner]
    lead0, tab0 = m.bal_lead_loop(), m.bal_arm_loop()
    bl = m.boss_loop(sd)
    sgn = 1 if sd == 'U' else -1
    worst, wa = 1e9, None
    for k in range(-84, 85):
        a = m.ELEV_STOP * k / 84.0
        for poly in (rot(lead0, a), rot(tab0, a)):
            for p in dens(poly, 0.0002):
                # exclude the lead / tab points that are inside the boss column x-range handled below (the boss is a stop, clearance 0)
                d = seg_dist(p, cav)
                # a point below the skin side of the cavity (the cavity is open to the pocket) is not a clearance issue: only points outside the skin count
                if m._h_of(sd, p[0], p[1]) > -0.0002 and d < worst: worst, wa = d, a
    w22 = 1e9
    for a in (-22.0, 22.0):
        for poly in (rot(lead0, a), rot(tab0, a)):
            for p in dens(poly, 0.0002):
                if m._h_of(sd, p[0], p[1]) > -0.0002: w22 = min(w22, seg_dist(p, cav))
    # poke
    pk = max(m._h_of(sd, p[0], p[1]) for a in ((m.ELEV_STOP,) if sd == 'U' else (-m.ELEV_STOP,)) for poly in (rot(lead0, a),) for p in dens(poly, 0.0002))
    # boss to tab at the stop: distance from the boss bottom edge points to the tab polygon at the stop angle
    a_st = m.ELEV_STOP if sd == 'U' else -m.ELEV_STOP
    tabp = rot(tab0, a_st); leadp = rot(lead0, a_st)
    bpts = dens(bl, 0.0001)
    gap = min(min(math.hypot(b[0] - q[0], b[1] - q[1]) for q in dens(tabp, 0.0002)) for b in dens(bl, 0.0002))
    gl = min(min(math.hypot(b[0] - q[0], b[1] - q[1]) for q in dens(leadp, 0.0002)) for b in bpts)
    # penetration at 22: boss bottom face vs tab rotated 22 (tab corner depth below the boss bottom plane)
    a22 = 22.0 if sd == 'U' else -22.0
    pen = max([0.0] + [seg_dist(q, bl + [bl[0]]) for q in dens(rot(tab0, a22), 0.0001) if pip(q, bl)])
    ok &= worst >= m.CAP_CLR - 1e-5 and gl >= 0.0005 - 1e-5
    P("| %s | %.2f | %.0f-%.0f | %.2f | %.2f | %+.1f | %.2f | %.3f | %.2f | %.2f |" % ('upper' if sd == 'U' else 'lower', max(ho) * 1e3, xs[0] * 1e3, xs[-1] * 1e3, pk * 1e3, worst * 1e3, wa, w22 * 1e3, gap * 1e3, gl * 1e3, pen * 1e3))
P(); P("Cap clearance >= %.1f mm over the whole travel and boss-to-lead >= 0.5 mm: **%s**." % (m.CAP_CLR * 1e3, "PASS" if ok else "FAIL"))
P("The cap cavity stays above the skin only where the lead or tabs poke; elsewhere the inner surface is flush with the skin (cap wall rests on the skin).")
P("Boss to tab gap is 0 by construction at the stop (bottom face coplanar with the tab face rotated to +-%.0f deg); the +-22 deg column shows how far the tab would go into the boss if the stop were absent (it cannot: the boss stops it)." % m.ELEV_STOP)
P("Damper: gap %.2f mm, c = %.2e N m s/rad at 25 C (mu %.1f Pa s), stator %.1f g, rotor %.1f g per elevon." % (m.DMP_GAP * 1e3, m.DMP_C, m.DMP_MU, m.DMP_STATOR_G, m.DMP_ROTOR_G))
P("Cap masses (printed, from the drawn volume): upper %.2f g, lower %.2f g each, 4 caps %.1f g." % (m.cap_mass_g('U'), m.cap_mass_g('L'), 2 * (m.cap_mass_g('U') + m.cap_mass_g('L'))))
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
open(os.path.join(HERE, 'out', 'STOP_CHECK.md'), 'w').write("\n".join(L))
