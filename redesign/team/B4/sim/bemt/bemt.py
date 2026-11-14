"""Blade-element momentum model (BEMT) for the B4 simulation round. Standard library only (imported by sim_claims.py,
so build_graph.py can re-run it).

Model
- Blade: UIUC-measured chord and twist (data/uiuc_*_geom.csv), r/R 0.15..1.00, 2 blades.
- Section: XFOIL polars (polars.json, NACA 4412 baseline, NACA 4409 sensitivity) bilinear in alpha and log Re;
  Viterna-Corrigan extension beyond the converged range (aspect ratio 6 -> CD_max 1.2).
- Annulus momentum with Prandtl tip and hub loss F, axial (v) and swirl (u) induction:
      blade:    dT = B 1/2 rho W^2 c (cl cos phi - cd sin phi) dr ,  dQ = B 1/2 rho W^2 c (cl sin phi + cd cos phi) r dr
      momentum: dT = 4 pi r rho F (Vx + v) v dr ,                dQ = 4 pi r^2 rho F (Vx + v) u dr
      W^2 = (Vx + v)^2 + (Omega r + Vt sin psi - u)^2
  v by bisection (the residual is monotonic in v), u by fixed point inside it.
- Oblique inflow (prop at incidence in the tailsitter pitch-over): quasi-steady per azimuth, axial component
  Vx = V cos(i), in-plane Vt = V sin(i) adding Vt sin(psi) to the tangential velocity; local momentum per azimuth
  element; thrust, torque and in-plane H-force averaged over psi. This omits skewed-wake inflow non-uniformity
  (Glauert/Pitt-Peters), which redistributes but changes the azimuth-mean little at mu < 0.3 (Leishman ch. 3).

Discretisation: N radial elements (midpoint, uniform), M azimuth stations. Convergence: N = 10/20/40/80,
M = 8/16/32 (bemt_convergence()).
"""
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"
IN = 0.0254
NU = 1.81e-5 / 1.225


def load_geom(name):
    rows = []
    with open(DATA / f"uiuc_{name}_geom.csv") as fh:
        for r in csv.reader(l for l in fh if not l.startswith("#")):
            if r[0] == "r_R":
                continue
            rows.append(tuple(float(x) for x in r))
    return rows


GEOMS = {"11x5.5E": ("apce_11x5.5", 11.0), "11x4.7SF": ("apcsf_11x4.7", 11.0)}
POLARS = json.loads((HERE / "polars.json").read_text(encoding="utf-8"))


def _lin(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    t = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + t * (ys[hi] - ys[lo])


class Polar:
    """cl, cd(alpha deg, Re) for one section: tables per Re, Viterna beyond the converged range."""

    def __init__(self, foil):
        self.res = sorted(int(k) for k in POLARS["foils"][foil])
        self.tab = {}
        for re in self.res:
            pts = POLARS["foils"][foil][str(re)]
            a = [p[0] for p in pts]
            self.tab[re] = (a, [p[1] for p in pts], [p[2] for p in pts])

    def _one(self, re, al):
        a, cl, cd = self.tab[re]
        if a[0] <= al <= a[-1]:
            return _lin(a, cl, al), _lin(a, cd, al)
        # Viterna-Corrigan from the nearest converged end
        a_s = a[-1] if al > a[-1] else a[0]
        cls, cds = (cl[-1], cd[-1]) if al > a[-1] else (cl[0], cd[0])
        cdmax = 1.2
        rs = math.radians(a_s)
        b1 = cdmax
        a1 = b1 / 2
        a2 = (cls - cdmax * math.sin(rs) * math.cos(rs)) * math.sin(rs) / math.cos(rs) ** 2
        b2 = (cds - cdmax * math.sin(rs) ** 2) / math.cos(rs)
        r = math.radians(max(min(al, 90.0), -90.0))
        if abs(math.cos(r)) < 1e-6:
            return 0.0, cdmax
        c_l = a1 * math.sin(2 * r) + a2 * math.cos(r) ** 2 / math.sin(r) if abs(math.sin(r)) > 1e-6 else 0.0
        c_d = b1 * math.sin(r) ** 2 + b2 * math.cos(r)
        return c_l, max(c_d, cds)

    def __call__(self, al, re):
        re = min(max(re, self.res[0]), self.res[-1])
        lr = math.log(re)
        for i in range(len(self.res) - 1):
            if self.res[i] <= re <= self.res[i + 1]:
                t = (lr - math.log(self.res[i])) / (math.log(self.res[i + 1]) - math.log(self.res[i]))
                c0, d0 = self._one(self.res[i], al)
                c1, d1 = self._one(self.res[i + 1], al)
                return c0 + t * (c1 - c0), d0 + t * (d1 - d0)
        return self._one(self.res[-1], al)


_POL = {}


def polar(foil):
    if foil not in _POL:
        _POL[foil] = Polar(foil)
    return _POL[foil]


def blade(name, N):
    g = load_geom(GEOMS[name][0])
    D = GEOMS[name][1] * IN
    R = D / 2
    rr, cc, bb = [r[0] for r in g], [r[1] for r in g], [r[2] for r in g]
    r0 = rr[0]
    out = []
    for i in range(N):
        x = r0 + (1 - r0) * (i + 0.5) / N
        out.append((x * R, _lin(rr, cc, x) * R, _lin(rr, bb, x), (1 - r0) * R / N))
    return R, out


def element(r, c, beta, dr, R, rhub, Vx, Vy, Om, rho, pol, B=2):
    """Returns dT, dQ, dFy (in-plane force along the local tangential direction, + opposing rotation) per element."""
    def forces(v, u):
        ua = Vx + v
        ut = Vy - u
        W2 = ua * ua + ut * ut
        phi = math.atan2(ua, ut)
        al = beta - math.degrees(phi)
        cl, cd = pol(al, math.sqrt(W2) * c / NU)
        cn = cl * math.cos(phi) - cd * math.sin(phi)
        ctn = cl * math.sin(phi) + cd * math.cos(phi)
        q = 0.5 * rho * W2 * c * B * dr
        sphi = max(abs(math.sin(phi)), 1e-4)
        ft = 2 / math.pi * math.acos(min(1.0, math.exp(-B * (R - r) / (2 * r * sphi))))
        fh = 2 / math.pi * math.acos(min(1.0, math.exp(-B * (r - rhub) / (2 * rhub * sphi))))
        return q * cn, q * ctn, max(ft * fh, 1e-4)

    def resid(v):
        u = 0.0
        for _ in range(4):
            dT, dFt, F = forces(v, u)
            m = 4 * math.pi * r * rho * F * (Vx + v) * dr
            u_new = dFt / m if m > 1e-9 else 0.0
            u = 0.5 * u + 0.5 * min(max(u_new, 0.0), 0.5 * Vy)
        dT, dFt, F = forces(v, u)
        return dT - 4 * math.pi * r * rho * F * (Vx + v) * v * dr, u

    lo, hi = -0.45 * Vx if Vx > 0 else 0.0, 80.0
    flo, _ = resid(lo)
    if flo <= 0:                     # section produces no thrust even with no induction
        v = lo
    else:
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            fm, _ = resid(mid)
            if fm > 0:
                lo = mid
            else:
                hi = mid
        v = 0.5 * (lo + hi)
    _, u = resid(v)
    dT, dFt, _ = forces(v, u)
    return dT, dFt * r, dFt


def rotor(name, rpm, V=0.0, inc_deg=0.0, rho=1.225, N=40, M=16, foil="naca4412"):
    """Thrust N, torque N m, power W, in-plane H-force N (along the in-plane wind, + downwind), Ct, Cp."""
    R, els = blade(name, N)
    D = 2 * R
    Om = rpm * 2 * math.pi / 60
    pol = polar(foil)
    Vx = V * math.cos(math.radians(inc_deg))
    Vt = V * math.sin(math.radians(inc_deg))
    rhub = els[0][0] - els[0][3] / 2
    Ms = M if Vt > 1e-9 else 1
    T = Q = H = 0.0
    for j in range(Ms):
        psi = 2 * math.pi * (j + 0.5) / Ms
        for r, c, beta, dr in els:
            Vy = Om * r + Vt * math.sin(psi)
            if Vy <= 0.05 * Om * r:
                continue                                      # reverse-flow region (not reached for mu < 0.3)
            dT, dQ, dFt = element(r, c, beta, dr, R, rhub, Vx, Vy, Om, rho, pol)
            T += dT
            Q += dQ
            H += dFt * math.sin(psi)          # the blade's drag-direction force projected on the in-plane wind
    T, Q, H = T / Ms, Q / Ms, H / Ms
    n = rpm / 60
    P = Q * Om
    return {"T": T, "Q": Q, "P": P, "H": H, "Ct": T / (rho * n * n * D ** 4), "Cp": P / (rho * n ** 3 * D ** 5),
            "J": V / (n * D), "eta": T * Vx / P if P > 0 else 0.0, "FM": (T ** 1.5 / math.sqrt(2 * rho * math.pi * R * R)) / P
            if P > 0 else 0.0}


def rpm_for_thrust(name, T, V=0.0, inc_deg=0.0, rho=1.225, N=40, M=16, foil="naca4412"):
    lo, hi = 1500.0, 15000.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if rotor(name, mid, V, inc_deg, rho, N, M, foil)["T"] < T:
            lo = mid
        else:
            hi = mid
    rpm = 0.5 * (lo + hi)
    out = rotor(name, rpm, V, inc_deg, rho, N, M, foil)
    out["rpm"] = rpm
    return out


if __name__ == "__main__":
    for nm in GEOMS:
        for rpm in (4000, 5000, 6000):
            r = rotor(nm, rpm)
            print(nm, rpm, "Ct %.4f Cp %.4f FM %.3f T %.2f N" % (r["Ct"], r["Cp"], r["FM"], r["T"]))
        for J in (0.2, 0.4, 0.5):
            n = 6000 / 60
            r = rotor(nm, 6000, V=J * n * 11 * IN)
            print(nm, "J", J, "Ct %.4f Cp %.4f eta %.3f" % (r["Ct"], r["Cp"], r["eta"]))
