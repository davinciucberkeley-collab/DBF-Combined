"""linkage_core.py - shared geometry and kinematics of the concept A elevon linkage (spatial arm - rod - horn).
Numbers are IMPORTED from the CAD constants (amodel/electrical.py:530-560, :944-978; common.py; wing.py), never retyped.
Frame = the CAD frame: x aft, y span (right +), z up, metres. Side sy = +1 (R) or -1 (L).
Servo arm turns about the vertical spline axis at (SV_XS, sy*SERVO_Y); theta is counter-clockwise about +z, theta = 0 at neutral
(arm tip points inboard, (0, -sy)). Elevon angle delta is a right-handed rotation about +y through (XH, y, HINGE_Z)
(the sense of wing._rot_pt and of collision.rot_about('Y')): positive moves the horn hole aft/down (trailing edge down).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, '..', 'cad'))
sys.dont_write_bytecode = True
if CAD not in sys.path:
    sys.path.insert(0, CAD)
from amodel import common as _c, wing as _w, electrical as _e   # noqa: E402

MM = 1e-3
XH, HINGE_Z = _c.XH, _w.HINGE_Z
SERVO_Y, SV_XS = _c.SERVO_Y, _e.SV_XS
ARM_R, HORN_R, ROD_Z, ROD_D = _e.ARM_R, _e.HORN_R, _e.ROD_Z, _e.ROD_D
HORN_XH = _e.HORN_XH
ELEV_LIM, ELEV_STOP = _w.ELEV_LIM, _c.ELEV_STOP
VX0, VZ0 = HORN_XH - XH, ROD_Z - HINGE_Z                   # horn hole relative to the hinge axis at neutral
L_ROD = HORN_XH - SV_XS                                    # fixed rod length: neutral CAD endpoints (rod parallel to x)
OUT = os.path.join(HERE, 'out')


def horn_pt(delta, sy):
    d = delta
    return np.array([XH + VX0 * math.cos(d) + VZ0 * math.sin(d), sy * (SERVO_Y - ARM_R), HINGE_Z - VX0 * math.sin(d) + VZ0 * math.cos(d)])


def dhorn(delta, sy):
    d = delta
    return np.array([-VX0 * math.sin(d) + VZ0 * math.cos(d), 0.0, -VX0 * math.cos(d) - VZ0 * math.sin(d)])


def arm_pt(theta, sy):
    return np.array([SV_XS + ARM_R * sy * math.sin(theta), sy * SERVO_Y - sy * ARM_R * math.cos(theta), ROD_Z])


def darm(theta, sy):
    return np.array([ARM_R * sy * math.cos(theta), sy * ARM_R * math.sin(theta), 0.0])


def g(theta, delta, sy):
    return float(np.linalg.norm(arm_pt(theta, sy) - horn_pt(delta, sy)) - L_ROD)


def rod_dir(theta, delta, sy):
    v = horn_pt(delta, sy) - arm_pt(theta, sy)
    return v / np.linalg.norm(v)


def theta_of_delta(delta, sy):
    """Closed form: |Pa - Ph| = L is a sin(theta) + b cos(theta) = c; the root nearest 0 is returned."""
    ph = horn_pt(delta, sy)
    px = SV_XS - ph[0]
    dz = ROD_Z - ph[2]
    a, b = 2 * ARM_R * px * sy, -2 * ARM_R ** 2
    c = L_ROD ** 2 - px ** 2 - dz ** 2 - 2 * ARM_R ** 2
    rho, phi = math.hypot(a, b), math.atan2(b, a)
    s = c / rho
    cands = [math.asin(s) - phi, math.pi - math.asin(s) - phi]
    cands = [((t + math.pi) % (2 * math.pi)) - math.pi for t in cands]
    return min(cands, key=abs)


def delta_of_theta_newton(theta, sy, d0=0.0, tol=1e-13):
    d = d0
    for _ in range(60):
        ph, pa = horn_pt(d, sy), arm_pt(theta, sy)
        r = np.linalg.norm(pa - ph) - L_ROD
        u = (ph - pa) / np.linalg.norm(ph - pa)
        gd = float(u @ dhorn(d, sy))                     # dg/d delta, g = |Pa - Ph| - L
        step = r / gd
        d -= step
        if abs(step) < tol:
            break
    return d


def sens(theta, delta, sy):
    """s_a = u . dPa/dtheta, s_h = u . dPh/ddelta (m/rad, u = unit vector arm -> horn)."""
    u = rod_dir(theta, delta, sy)
    return u, float(u @ darm(theta, sy)), float(u @ dhorn(delta, sy))


def levers(theta, delta, sy):
    """Transmission angles: gamma_h = angle(rod, horn radius), gamma_a = angle(rod, arm); lever ratios l = |r x u|_axis / |r|."""
    u = rod_dir(theta, delta, sy)
    rh = horn_pt(delta, sy) - np.array([XH, horn_pt(delta, sy)[1], HINGE_Z])
    ra = arm_pt(theta, sy) - np.array([SV_XS, sy * SERVO_Y, ROD_Z])
    gh = math.degrees(math.acos(float(u @ rh) / np.linalg.norm(rh)))
    ga = math.degrees(math.acos(float(u @ ra) / np.linalg.norm(ra)))
    lh = abs(float(np.cross(rh, u)[1])) / np.linalg.norm(rh)
    la = abs(float(np.cross(ra, u)[2])) / np.linalg.norm(ra)
    return gh, ga, lh, la


def jac_sigma(theta, delta, sy):
    """Min singular value of the normalised 2x2 kinematic Jacobian [[s_a/R_a, -s_h/R_h],[1, 0]] (constraint row on (theta*R_a, delta*R_h),
    drive row theta). It is singular when the horn (or arm) lever vanishes (toggle / dead point)."""
    u, sa, sh = sens(theta, delta, sy)
    J = np.array([[sa / ARM_R, -sh / HORN_R], [1.0, 0.0]])
    return float(np.linalg.svd(J, compute_uv=False)[-1])


def misalign_deg(theta, delta, sy):
    """Out-of-line angle of the rod to the plane each joint can turn in: Z-bend pin axis z -> asin(|u.z|); clevis pin axis y -> asin(|u.y|)."""
    u = rod_dir(theta, delta, sy)
    return math.degrees(math.asin(abs(u[2]))), math.degrees(math.asin(abs(u[1])))


def git_head():
    import subprocess
    try:
        return subprocess.run(['git', '-C', HERE, 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=20).stdout.strip() or '-'
    except Exception:
        return '-'


def get_plt():
    """matplotlib needs `packaging`, which lives in the user site-packages that `python -I` hides: append that dir (last) for plotting only."""
    import importlib
    try:
        import matplotlib
    except ModuleNotFoundError:
        import site
        sys.path.append(site.getusersitepackages())
        importlib.invalidate_caches()
        import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt
