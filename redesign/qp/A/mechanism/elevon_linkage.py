"""T-018 elevon linkage kinematics (category: kinematics). Spatial arm - rod - horn linkage of concept A, rigid rod, no joint clearance.
    python -I redesign/qp/A/mechanism/elevon_linkage.py        (about 10 s)
PASS / FAIL CRITERIA (fixed in this file BEFORE the final run; EST = engineering choice of this analysis, not a project requirement):
  K1  constraint residual |g| < 1e-9 m everywhere; Newton delta(theta) and closed-form/brentq theta(delta) agree to < 1e-9 rad
  K2  left/right symmetry: theta_L(delta) = -theta_R(delta) to < 1e-9 rad (the CAD constants are mirror images; checks code and model)
  K3  servo angle for the +-21 deg stop within the ASSUMED travel +-45 deg (ES3054HV travel is "-" in SERVO.md; assumption, EST)
  K4  toggle distance: min singular value of the normalised Jacobian >= 0.25 over +-21 deg (EST; equals a horn lever ratio of about 0.36)
  K5  rod out-of-line angle at the Z-bend and at the clevis <= 50 % of the geometric tilt allowance of that joint, allowance =
      atan(diametral clearance / engaged length) from the CAD hole and pin sizes (all EST in the CAD: arm hole 1.5 mm, rod 1.2 mm,
      arm 2.0 mm; blade hole 1.5 mm, pin 1.0 mm, blade 2.0 mm)
  K6  gearing from the Jacobian equals the independent lever-ratio formula R_a l_a / (R_h l_h) to < 1e-9 (stored for the dynamics, T-019)
Info only (not gating): horn transmission angle against the 40 deg machine-design rule of thumb (EST, source not looked up).
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np                      # noqa: E402
import scipy                            # noqa: E402
from scipy.optimize import brentq       # noqa: E402
import linkage_core as k                # noqa: E402

ARM_T = k._e.ARM_T
ASSUMED_TRAVEL = (45.0, 60.0)
CRIT = dict(res_m=1e-9, sym_rad=1e-9, travel_deg=45.0, sigma_min=0.25, tilt_fraction=0.5, gear_tol=1e-9)
HOLE_ARM_D = 2 * 0.75e-3                # arm hole ring radius 0.75 mm (electrical.py:942)
HOLE_HORN_D = 2 * 0.75e-3               # horn hole ring radius 0.75 mm (electrical.py:963)
PIN_D = 1.0e-3                          # clevis pin 1.0 mm (electrical.py:977)
HORN_T = 2.0e-3                         # horn blade 2 mm (electrical.py:963)
ALLOW_Z = math.degrees(math.atan((HOLE_ARM_D - k.ROD_D) / ARM_T))
ALLOW_C = math.degrees(math.atan((HOLE_HORN_D - PIN_D) / HORN_T))


def main():
    res = {'git_head': k.git_head(), 'criteria': CRIT, 'assumed_servo_travel_deg': ASSUMED_TRAVEL}
    res['geometry'] = dict(L_rod_m=k.L_ROD, ARM_R=k.ARM_R, HORN_R=k.HORN_R, XH=k.XH, HINGE_Z=k.HINGE_Z, HORN_XH=k.HORN_XH, SV_XS=k.SV_XS,
                           SERVO_Y=k.SERVO_Y, ROD_Z=k.ROD_Z, horn_hole_rel_hinge_mm=[k.VX0 * 1e3, k.VZ0 * 1e3],
                           horn_hole_radius_check_mm=math.hypot(k.VX0, k.VZ0) * 1e3, ELEV_LIM=k.ELEV_LIM, ELEV_STOP=k.ELEV_STOP,
                           tilt_allow_Zbend_deg=ALLOW_Z, tilt_allow_clevis_deg=ALLOW_C)
    degs = np.round(np.arange(-k.ELEV_STOP, k.ELEV_STOP + 1e-9, 0.05), 6)
    rows, maxres, maxdisagree, maxsym, maxgear = [], 0.0, 0.0, 0.0, 0.0
    sig_min, lam_min, gh_min = 9, 9, 999
    zmax = cmax = 0.0
    for dd in degs:
        d = math.radians(dd)
        th = {}
        for sy in (1, -1):
            t = k.theta_of_delta(d, sy)
            th[sy] = t
            r = abs(k.g(t, d, sy))
            tb = brentq(lambda x: k.g(x, d, sy), t - 0.2, t + 0.2, xtol=1e-15, rtol=1e-14)     # independent solve for theta(delta)
            dn = k.delta_of_theta_newton(t, sy, d0=d + 0.01)                                    # task form: theta -> delta (Newton)
            maxres = max(maxres, r)
            maxdisagree = max(maxdisagree, abs(tb - t), abs(dn - d))
            u, sa, sh = k.sens(t, d, sy)
            gh, ga, lh, la = k.levers(t, d, sy)
            gear = sa / sh                                           # d delta / d theta from the constraint Jacobian
            gear2 = k.ARM_R * la / (k.HORN_R * lh) * (1 if gear > 0 else -1)
            maxgear = max(maxgear, abs(gear - gear2))
            sg = k.jac_sigma(t, d, sy)
            mz, mc = k.misalign_deg(t, d, sy)
            zmax, cmax = max(zmax, mz), max(cmax, mc)
            sig_min, lam_min, gh_min = min(sig_min, sg), min(lam_min, lh), min(gh_min, min(gh, 180 - gh))
            if sy == 1:
                rows.append(dict(delta_deg=float(dd), theta_R_deg=math.degrees(t), gear_ddelta_dtheta=gear, gamma_horn_deg=gh, gamma_arm_deg=ga,
                                 lever_horn=lh, lever_arm=la, sigma_min=sg, zbend_misalign_deg=mz, clevis_misalign_deg=mc,
                                 residual_m=r, rod_pitch_deg=math.degrees(math.asin(u[2])), rod_yaw_deg=math.degrees(math.asin(u[1]))))
        maxsym = max(maxsym, abs(th[1] + th[-1]))
    res['sweep'] = dict(step_deg=0.05, n=len(degs), max_residual_m=maxres, max_solver_disagreement=maxdisagree, max_LR_asymmetry_rad=maxsym,
                        max_gear_formula_diff=maxgear, min_sigma=sig_min, min_horn_lever=lam_min, min_horn_gamma_deg=gh_min,
                        max_zbend_misalign_deg=zmax, max_clevis_misalign_deg=cmax)
    at = {}
    for dd in (-21, -20, 20, 21):
        d = math.radians(dd)
        tR, tL = k.theta_of_delta(d, 1), k.theta_of_delta(d, -1)
        gh, ga, lh, la = k.levers(tR, d, 1)
        u, sa, sh = k.sens(tR, d, 1)
        at['%+d' % dd] = dict(theta_R_deg=math.degrees(tR), theta_L_deg=math.degrees(tL), gear=sa / sh, gamma_horn_deg=gh,
                              sigma_min=k.jac_sigma(tR, d, 1), rod_pitch_deg=math.degrees(math.asin(u[2])))
    res['servo_angle_for_delta'] = at
    gs = [r['gear_ddelta_dtheta'] for r in rows]
    res['gearing'] = dict(neutral=rows[len(rows) // 2]['gear_ddelta_dtheta'], min=min(gs), max=max(gs))

    def lever_h(dd):
        d = math.radians(dd)
        t = k.theta_of_delta(d, 1)
        return k.levers(t, d, 1)[2]
    tog = {}
    for name, a, b in (('plus', k.ELEV_STOP, 89.0), ('minus', -k.ELEV_STOP, -89.0)):
        grid = np.linspace(a, b, 400)
        vals = []
        for g_ in grid:
            try:
                vals.append(lever_h(g_))
            except ValueError:                                        # rod cannot reach: arm past its own limit
                vals.append(float('nan'))
        vals = np.array(vals)
        idx = np.where(np.isnan(vals) | (vals < 1e-3))[0]
        tog[name] = None if len(idx) == 0 else dict(first_delta_deg_lever_lt_1em3_or_unreachable=float(grid[idx[0]]),
                                                    margin_from_stop_deg=abs(float(grid[idx[0]]) - a))
    res['toggle'] = tog
    tmax = max(abs(at[s]['theta_R_deg']) for s in at)
    res['servo_travel'] = {str(T): dict(required_deg=tmax, covers=bool(tmax <= T), margin_deg=T - tmax) for T in ASSUMED_TRAVEL}
    passes = {
        'K1': bool(maxres < CRIT['res_m'] and maxdisagree < 1e-9),
        'K2': bool(maxsym < CRIT['sym_rad']),
        'K3': bool(tmax <= CRIT['travel_deg']),
        'K4': bool(sig_min >= CRIT['sigma_min']),
        'K5': bool(zmax <= CRIT['tilt_fraction'] * ALLOW_Z and cmax <= CRIT['tilt_fraction'] * ALLOW_C),
        'K6': bool(maxgear < CRIT['gear_tol']),
    }
    res['pass'] = passes
    res['pass_all'] = all(passes.values())
    res['info_gamma_horn_vs_40deg_rule'] = dict(min_gamma_horn_deg=gh_min, meets=bool(gh_min >= 40.0))
    res['versions'] = dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__)
    os.makedirs(k.OUT, exist_ok=True)
    with open(os.path.join(k.OUT, 'linkage_kinematics.json'), 'w') as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(k.OUT, 'linkage_kinematics.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows[::10])                                       # every 0.5 deg
    plt = k.get_plt()
    x = [r['delta_deg'] for r in rows]
    fig, ax = plt.subplots(2, 2, figsize=(10, 7))
    ax[0, 0].plot(x, [r['theta_R_deg'] for r in rows])
    ax[0, 0].set_ylabel('servo arm angle theta, R side (deg)')
    ax[0, 1].plot(x, [r['gear_ddelta_dtheta'] for r in rows])
    ax[0, 1].set_ylabel('gearing d delta / d theta')
    ax[1, 0].plot(x, [r['gamma_horn_deg'] for r in rows], label='horn gamma')
    ax[1, 0].plot(x, [r['gamma_arm_deg'] for r in rows], label='arm gamma')
    ax[1, 0].axhline(40, ls=':', c='gray')
    ax[1, 0].set_ylabel('transmission angle (deg), dotted = 40 rule')
    ax[1, 0].legend()
    ax[1, 1].plot(x, [r['zbend_misalign_deg'] for r in rows], label='Z-bend (allow %.1f)' % ALLOW_Z)
    ax[1, 1].plot(x, [r['clevis_misalign_deg'] for r in rows], label='clevis (allow %.1f)' % ALLOW_C)
    ax[1, 1].axhline(0.5 * ALLOW_Z, ls=':', c='C0')
    ax[1, 1].set_ylabel('rod out-of-line angle (deg), dotted = K5 limit Z-bend')
    ax[1, 1].legend()
    for a in ax.flat:
        a.set_xlabel('elevon angle delta (deg)')
        a.grid(alpha=.3)
    fig.suptitle('Concept A elevon linkage kinematics (rigid, spatial; CAD constants)')
    fig.tight_layout()
    fig.savefig(os.path.join(k.OUT, 'linkage_kinematics.png'), dpi=110)
    print(json.dumps({k_: res[k_] for k_ in ('servo_angle_for_delta', 'sweep', 'gearing', 'toggle', 'servo_travel', 'pass', 'info_gamma_horn_vs_40deg_rule')}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
