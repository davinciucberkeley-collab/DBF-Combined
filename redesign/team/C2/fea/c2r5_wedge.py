"""C2-R5: Williams eigenvalue of a foam wedge bonded to a rigid inclusion on one face and free on the other
(plane strain), to show the pocket-corner peaks are a stress singularity sigma ~ r^(lambda - 1), not a converging value.
Airy phi = r^(l+1) [A cos(l+1)t + B sin(l+1)t + C cos(l-1)t + D sin(l-1)t]; displacements from Barber, Elasticity,
3rd ed., Table 8.1 / eq. 11.x (2 mu u_r, 2 mu u_t); kappa = 3 - 4 nu. Free face t = 0, clamped (rigid) face t = alpha.
Checks: free-free 360 deg (crack) -> 0.5; clamped-free 180 deg -> Re 0.5 (oscillatory, eps = ln(kappa) / 2 pi).
Run: python -I redesign/team/C2/fea/c2r5_wedge.py
"""
import math
import numpy as np
from scipy.optimize import brentq


def rows(l, t, k, kind):
    a, b = l + 1, l - 1
    if kind == "free":            # sigma_tt, tau_rt  ~ F(t), F'(t)
        return [[math.cos(a * t), math.sin(a * t), math.cos(b * t), math.sin(b * t)],
                [-a * math.sin(a * t), a * math.cos(a * t), -b * math.sin(b * t), b * math.cos(b * t)]]
    return [[-a * math.cos(a * t), -a * math.sin(a * t), (k - l) * math.cos(b * t), (k - l) * math.sin(b * t)],
            [a * math.sin(a * t), -a * math.cos(a * t), (k + l) * math.sin(b * t), -(k + l) * math.cos(b * t)]]


def det(l, alpha, nu, k0="free", k1="clamped"):
    k = 3 - 4 * nu
    M = np.array(rows(l, 0.0, k, k0) + rows(l, alpha, k, k1))
    return np.linalg.det(M)


def smin(l, alpha, nu, k0, k1):
    k = 3 - 4 * nu
    M = np.array(rows(l, 0.0, k, k0) + rows(l, alpha, k, k1))
    M = M / np.linalg.norm(M, axis=1, keepdims=True)
    return np.linalg.svd(M, compute_uv=False)[-1]


def lowest(alpha, nu, k0="free", k1="clamped"):
    """Smallest real lambda in (0, 1.2) where the 4x4 boundary matrix is singular (scan of its smallest singular
    value; a real root shows as a minimum ~ 0)."""
    from scipy.optimize import minimize_scalar
    ls = np.linspace(0.02, 1.2, 2361)
    v = np.array([smin(l, alpha, nu, k0, k1) for l in ls])
    for i in range(1, len(ls) - 1):
        if v[i] <= v[i - 1] and v[i] <= v[i + 1]:
            r = minimize_scalar(smin, bracket=(ls[i - 1], ls[i], ls[i + 1]), args=(alpha, nu, k0, k1), tol=1e-12)
            if r.fun < 1e-6:
                return float(r.x)
    return None


if __name__ == "__main__":
    nu = 0.25
    print("check crack free-free 360:", round(lowest(2 * math.pi, nu, "free", "free"), 4))
    for deg in (90, 135, 180):
        l = lowest(math.radians(deg), nu)
        print(f"foam wedge {deg} deg, rigid face + free face, nu {nu}: lambda {l}" +
              (f", stress ~ r^{l - 1:.3f}" if l else " (no real root < 1.2: oscillatory/complex)"))


def cdet(lr, li, alpha, nu):
    """Complex determinant (rigid-free) for complex lambda; cmath version of rows()."""
    import cmath
    l = complex(lr, li)
    k = 3 - 4 * nu
    a, b = l + 1, l - 1
    t = alpha
    M = [[1, 0, 1, 0], [0, a, 0, b],
         [-a * cmath.cos(a * t), -a * cmath.sin(a * t), (k - l) * cmath.cos(b * t), (k - l) * cmath.sin(b * t)],
         [a * cmath.sin(a * t), -a * cmath.cos(a * t), (k + l) * cmath.sin(b * t), -(k + l) * cmath.cos(b * t)]]
    return np.linalg.det(np.array(M, dtype=complex))


def complex_root(alpha, nu):
    from scipy.optimize import fsolve
    best = None
    for lr0 in np.linspace(0.3, 1.0, 15):
        for li0 in (0.02, 0.1, 0.3):
            f = lambda v: [cdet(v[0], v[1], alpha, nu).real, cdet(v[0], v[1], alpha, nu).imag]
            s, info, ier, _ = fsolve(f, [lr0, li0], full_output=True)
            if ier == 1 and 0 < s[0] < 1.2 and abs(s[1]) > 1e-6 and abs(cdet(*s, alpha, nu)) < 1e-9:
                if best is None or s[0] < best[0]:
                    best = (float(s[0]), float(abs(s[1])))
    return best


if __name__ == "__main__":
    for deg in (135, 180):
        r = complex_root(math.radians(deg), 0.25)
        print(f"foam wedge {deg} deg complex root: Re {r[0]:.4f} Im {r[1]:.4f} -> stress ~ r^{r[0] - 1:.3f}"
              + (f" (theory 180: eps = ln(kappa)/2pi = {math.log(2.0) / (2 * math.pi):.4f})" if deg == 180 else ""))
