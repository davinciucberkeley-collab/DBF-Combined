"""Concept A, S5010 section data and the aero numbers that depend on it (D-195, QP-5). Reproduce: python -I aero_s5010.py  (needs numpy; prints; writes nothing)
Sources: (1) section table aerodesign.de/english/profile/profile_s.htm, S5010 row: camber f 2.20 %, thickness d 9.83 %, cm0 +0.0080, a0 -0.52 deg (WebFetch 2026-11-15);
(2) 2-D CFD stall angle 11 deg, best L/D at 7.8 deg (Mat Yazik et al., semarakilmu.com.my/journals/index.php/fluid_mechanics_thermal_sciences/article/view/3720, abstract via search 2026-11-15; full text 403);
(3) section coordinates subsystems/wing/s5010.dat (UIUC m-selig.ae.illinois.edu/ads/coord/s5010.dat, checked 2026-11-09);
(4) own inviscid Hess-Smith panel check below (CALC). airfoiltools.com was unreachable (connection refused 2026-11-15): no measured CLmax is published in the sources reached, so CLmax stays EST 0.75 (a 3-D wing value)."""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def load():
    pts = [tuple(map(float, l.split())) for l in open(os.path.join(HERE, "..", "..", "subsystems", "wing", "s5010.dat")).read().splitlines()[1:] if l.strip()]
    return np.array(pts)[::-1]   # clockwise order, so the left-hand panel normal points out of the body
def panel(xy, alpha_deg):
    """Hess-Smith (source + vortex, Kutta at the TE panels). Returns cl, cm_quarter (nose-up +), x_cp from the LE."""
    x, y = xy[:, 0], xy[:, 1]
    if np.hypot(x[0] - x[-1], y[0] - y[-1]) > 1e-9: x = np.append(x, x[0]); y = np.append(y, y[0])
    n = len(x) - 1; dx, dy = np.diff(x), np.diff(y); L = np.hypot(dx, dy); tx, ty = dx / L, dy / L; nx, ny = -ty, tx
    xm, ym = 0.5 * (x[1:] + x[:-1]), 0.5 * (y[1:] + y[:-1])
    def inf(i, j):
        # velocity at panel i control point from unit source / unit vortex on panel j (local coords)
        rx, ry = xm[i] - x[j], ym[i] - y[j]
        xl = rx * tx[j] + ry * ty[j]; yl = -rx * ty[j] + ry * tx[j]
        r1 = xl * xl + yl * yl; r2 = (xl - L[j]) ** 2 + yl * yl
        th1 = math.atan2(yl, xl); th2 = math.atan2(yl, xl - L[j])
        us = math.log(r1 / r2) / (4 * math.pi); vs = (th2 - th1) / (2 * math.pi)
        if i == j: us, vs = 0.0, 0.5
        # source: (us, vs) local; vortex: (vs', -us') local
        us_, vs_ = us, vs; uv, vv = vs, -us
        gx = lambda u, v: (u * tx[j] - v * ty[j], u * ty[j] + v * tx[j])
        return gx(us_, vs_), gx(uv, vv)
    A = np.zeros((n + 1, n + 1)); B = np.zeros(n + 1)
    a = math.radians(alpha_deg); U = np.array([math.cos(a), math.sin(a)])
    for i in range(n):
        for j in range(n):
            (sx, sy), (vx, vy) = inf(i, j)
            A[i, j] = sx * nx[i] + sy * ny[i]; A[i, n] += vx * nx[i] + vy * ny[i]
        B[i] = -(U[0] * nx[i] + U[1] * ny[i])
    # Kutta: tangential velocity on first and last panel equal and opposite
    for j in range(n + 1):
        if j < n:
            (sx0, sy0), (vx0, vy0) = inf(0, j); (sx1, sy1), (vx1, vy1) = inf(n - 1, j)
            A[n, j] = (sx0 * tx[0] + sy0 * ty[0]) + (sx1 * tx[n - 1] + sy1 * ty[n - 1])
            A[n, n] += (vx0 * tx[0] + vy0 * ty[0]) + (vx1 * tx[n - 1] + vy1 * ty[n - 1])
    B[n] = -((U[0] * tx[0] + U[1] * ty[0]) + (U[0] * tx[n - 1] + U[1] * ty[n - 1]))
    sol = np.linalg.solve(A, B); q, gam = sol[:n], sol[n]
    vt = np.zeros(n)
    for i in range(n):
        v = U.copy()
        for j in range(n):
            (sx, sy), (vx, vy) = inf(i, j); v += q[j] * np.array([sx, sy]) + gam * np.array([vx, vy])
        vt[i] = v[0] * tx[i] + v[1] * ty[i]
    cp = 1 - vt ** 2
    fx = -cp * nx * L; fy = -cp * ny * L   # force on the body per unit q (normal points into the body for clockwise ordering: sign fixed by cl sign check)
    Fx, Fy = fx.sum(), fy.sum()
    cl = Fy * math.cos(a) - Fx * math.sin(a)
    mz = -np.sum((xm - 0.25) * fy - ym * fx)      # moment about the quarter chord, nose-up positive (x right, y up: clockwise = nose up)
    return cl, mz
def refine(xy, n=240):
    """Cosine-spaced re-panelling (n panels per side pair) with a cubic spline; returns clockwise points starting at the upper TE."""
    from scipy.interpolate import CubicSpline
    le = int(np.argmin(xy[:, 0])); halves = [xy[:le + 1], xy[le:]]
    xs = 0.5 * (1 - np.cos(np.linspace(0, math.pi, n // 2 + 1))); ys = []
    for h in halves:
        h = h[np.argsort(h[:, 0])]; ys.append(CubicSpline(h[:, 0], h[:, 1])(xs))
    up, lo = (ys[0], ys[1]) if ys[0].mean() > ys[1].mean() else (ys[1], ys[0])
    P = np.c_[np.r_[xs, xs[::-1][1:]], np.r_[up, lo[::-1][1:]]][:-1]; k = len(xs) - 1
    return np.r_[P[k:], P[:k + 1]]
def section(n=240):
    P = refine(load()[::-1], n); r = {a: panel(P, a) for a in (0.0, 6.0)}
    (c0, m0), (c6, m6) = r[0.0], r[6.0]; cla = (c6 - c0) / math.radians(6.0); dcm = (m6 - m0) / (c6 - c0)
    return dict(cla=cla, a0=math.degrees(-c0 / cla), cm0=m0 - dcm * c0, ac=0.25 - dcm)
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(HERE, "sitl"))
    for n in (120, 240, 360):
        t = section(n); print("panel n=%d (CALC, inviscid): CLa %.3f /rad, alpha0 %.2f deg (table -0.52), Cm0 about c/4 %+.4f (table +0.0080), AC at %.3f c" % (n, t["cla"], t["a0"], t["cm0"], t["ac"]))
    import a_aero as A
    print("Model inputs now: CM0 %+.4f, alpha0 %.2f deg, CLmax %.2f (EST: no measured section CLmax reached; 2-D CFD stall 11 deg + CLa %.2f /rad gives CL %.2f)" % (A.CM0, math.degrees(A.A0), A.CLMAX, A.CLA, A.CLA * (math.radians(11) - A.A0)))
    print("CG %.2f mm aft of LE (cad_mass.json)" % (A.CG_X * 1e3))
    # neutral point with the SIZING-A rule (sizing_a.py lines 224-226): wing AC at 0.25 c (section AC confirmed above), four props -85 mm ahead, viscous shift -3.3 mm
    a_w = A.CLA * A.S_W; a_p = 4 * 0.6 * math.pi * (9 * 0.0254 / 2) ** 2
    for ac in (0.25, section()["ac"]):
        npi = (a_w * ac * A.C_W + a_p * (-0.085)) / (a_w + a_p); npv = npi - 0.0033
        print("wing AC %.3f c: NP %.1f mm inviscid, %.1f mm viscous; SM at the CAD CG %.1f %% (limit >= 5 %%, band 6.0-8.4 %%)" % (ac, npi * 1e3, npv * 1e3, (npv - A.CG_X) / A.C_W * 100))
    npp = (a_w * 0.25 * A.C_W + a_p * (-0.110)) / (a_w + a_p) - 0.0033
    print("sensitivity, props at the CAD plane x -110 mm (motors -99 / props -121 mm; SIZING-A used -85): NP %.1f mm viscous, SM %.1f %%" % (npp * 1e3, (npp - A.CG_X) / A.C_W * 100))
    print("Model NP_X %.1f mm -> SM %.2f %%" % (A.NP_X * 1e3, A.SM * 100))
    def trim(m, V):
        W = m * 9.81; lo, hi = 0.0, 15.0
        for _ in range(40):
            al = math.radians((lo + hi) / 2); F = A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, 0, 0)[0]
            L = -F[2] * math.cos(al) + F[0] * math.sin(al); lo, hi = ((lo + hi) / 2, hi) if L < W else (lo, (lo + hi) / 2)
        al = math.radians(lo); l2, h2 = -0.5, 0.5
        for _ in range(40):
            d = (l2 + h2) / 2; T = A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, d, d)[1][1]; l2, h2 = (d, h2) if T > 0 else (l2, d)
        return math.degrees(al), math.degrees(d)
    for m in (1.381, 1.455, 1.47):
        for V in (15.0, 17.0, 18.0):
            al, d = trim(m, V); print("m %.3f V %.0f: alpha %.1f deg, trim elevon %.1f deg %s (stop +-21 deg; usable up travel 21 deg)" % (m, V, al, abs(d), "TE up" if d < 0 else "TE down"))
