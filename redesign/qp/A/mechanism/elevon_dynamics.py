"""T-019 elevon rigid-body dynamics (category: rigid-body dynamics). Frictionless 1-DOF model of the servo - rod - elevon chain.
    python -I redesign/qp/A/mechanism/elevon_dynamics.py        (well under 2 min)
Model: coordinates (theta, delta) joined by the spatial rod constraint of linkage_core (rod = massless rigid link, length fixed).
  elevon + balance inertia about the hinge I_e (CAD) + horn point mass; servo arm inertia I_a (CAD arm outline, 1.0 g); servo rotor and
  gear train reflected inertia: "-" (no source) and NOT modelled.
  Equation of motion (virtual work, theta' = s_h / s_a from the constraint Jacobian):
      (I_e + I_a theta'^2) ddelta = tau theta' + Q_aero - I_a theta' theta'' dot_delta^2
  integrated together with theta as a THIRD state (theta_dot = theta' dot_delta), so the constraint residual g(theta, delta) is a true
  drift measure; scipy.integrate.solve_ivp, DOP853, rtol 1e-9, atol 1e-12.
PASS / FAIL CRITERIA (fixed before the run; EST unless a source is named):
  D1  free swing (servo unpowered, no load): max relative energy error < 1e-6, E = 1/2 (I_e + I_a theta'(delta)^2) dot_delta^2 with theta'
      from the closed-form constraint Jacobian (independent of the theta'' used by the integrator)
  D2  constraint residual |g| < 1e-9 m along every integrated trajectory
  D3  rod force: peak COMPRESSION in the +-20 deg steps <= Euler load / 2 (safety factor 2, EST); Euler pinned-pinned, E = 207 GPa
  D4  servo torque margin at the held end point: tau_stall / tau_required >= 1.5 (project factor, SERVO.md s1 / params-A.json servo.load_factor)
  D5  both steps (0 -> +20, 0 -> -20 deg) reach within 0.5 deg of target in < 0.25 s (EST; ES3054HV speed 0.13 s/60 deg at 6 V)
  D6  rod force from the arm side and from the elevon side agree to < 1e-6 N (constraint-force consistency)
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np                              # noqa: E402
import scipy                                    # noqa: E402
from scipy.integrate import solve_ivp           # noqa: E402
import linkage_core as k                        # noqa: E402

E_STEEL = 207e9          # Pa, music wire / carbon steel, Acxess Spring Store + Matmatch (200-215 GPa), read 2026-11-18. Rod grade is "steel" (EST)
ROD_D = k.ROD_D
I_ROD = math.pi * ROD_D ** 4 / 64
P_EULER = math.pi ** 2 * E_STEEL * I_ROD / k.L_ROD ** 2     # pinned-pinned
HINGE_NM = json.load(open(os.path.join(HERE, '..', 'params-A.json'), encoding='utf-8'))['servo']['hinge_vd_nm']['value']   # N m at VD, EST: the one source is proofs/gen_params_a.py (0.146 x 0.31 / 0.30), via params-A.json
TAU_STALL = {'7.2V_EST_0.397': 0.397, '6.0V_0.333': 0.333}  # params-A.json:1002-1007 (EST, interpolated) and SERVO.md 3.4 kgf cm at 6.0 V
OMEGA_NL = math.radians(60.0) / 0.13                        # SERVO.md: 0.13 s / 60 deg at 6 V (no load)
THETA_SAT = math.radians(0.2)                               # servo error for full drive (EST: a digital servo is stiff; steady error at hold is reported)
EVAL_TOL_DEG, T_LIMIT = 0.5, 0.25
SY = 1                                                      # right side; left is the mirror (T-018 K2)


def arm_inertia():
    """Second moment about the hub centre of the CAD arm outline (amodel.electrical._arm_loop), uniform mass 1.0 g (P('MEC-002'), nylon)."""
    pts = np.array(k._e._arm_loop(0.0, 0.0, 0.0, -1.0))
    x, y = pts[:, 0], pts[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cr = x * y1 - x1 * y
    A = cr.sum() / 2
    Iz_area = (cr * (x * x + x * x1 + x1 * x1 + y * y + y * y1 + y1 * y1)).sum() / 12
    return 1.0e-3 * abs(Iz_area) / abs(A), abs(A)          # kg m2 (mass 1.0 g / area * second moment), area m2


I_A, ARM_AREA = arm_inertia()
M_HORN = k._e.PARTS['MEC-004-R']['mass_g'] * 1e-3   # P('MEC-004') printed horn, mass CALC from the drawn volume; point mass at the hole radius
I_HORN = M_HORN * k.HORN_R ** 2


def sat(x):
    """smooth clip to +-1 (p = 8): the servo duty and torque limits without a kink for the integrator."""
    return x / (1.0 + abs(x) ** 8) ** 0.125


def theta_prime(delta):
    th = k.theta_of_delta(delta, SY)
    u, sa, sh = k.sens(th, delta, SY)
    return sh / sa


def theta_pp(delta, h=1e-4):
    return (theta_prime(delta + h) - theta_prime(delta - h)) / (2 * h)


def run_case(tau_stall, load, direction, I_e):
    d_t = math.radians(k.ELEV_LIM) * direction
    th_cmd = k.theta_of_delta(d_t, SY)

    def f(t, y):
        d, w, th = y
        u, sa, sh = k.sens(th, d, SY)
        tp = sh / sa
        tpp = theta_pp(d)
        e = th_cmd - th
        duty = sat(e / THETA_SAT)
        th_dot = tp * w
        tau_raw = tau_stall * (duty - th_dot / OMEGA_NL)
        tau = tau_stall * sat(tau_raw / tau_stall)
        q = -HINGE_NM * (d / math.radians(k.ELEV_LIM) if load == 'linear' else math.tanh(d / math.radians(0.5)))
        M = I_e + I_A * tp ** 2
        dd = (tau * tp + q - I_A * tp * tpp * w * w) / M
        return [w, dd, th_dot]
    d00 = k.delta_of_theta_newton(0.0, SY)          # D-212 rev 2: at the lo / hi joint heights theta = 0 is not exactly delta = 0 for the fixed rod length (0 at mid)
    sol = solve_ivp(f, (0.0, 0.4), [d00, 0.0, 0.0], method='DOP853', rtol=1e-9, atol=1e-12, dense_output=False, max_step=5e-4)
    t, (d, w, th) = sol.t, sol.y
    rows = []
    Nmax_c, Nmax_t, resmax, nmis = 0.0, 0.0, 0.0, 0.0
    tau_hist = []
    for i in range(len(t)):
        u, sa, sh = k.sens(th[i], d[i], SY)
        tp = sh / sa
        tpp = theta_pp(d[i])
        duty = sat((th_cmd - th[i]) / THETA_SAT)
        th_dot = tp * w[i]
        tau = tau_stall * sat(duty - th_dot / OMEGA_NL)             # same as the smooth-clipped DC-motor torque in f()
        q = -HINGE_NM * (d[i] / math.radians(k.ELEV_LIM) if load == 'linear' else math.tanh(d[i] / math.radians(0.5)))
        M = I_e + I_A * tp ** 2
        ddot = (tau * tp + q - I_A * tp * tpp * w[i] ** 2) / M
        th_ddot = tp * ddot + tpp * w[i] ** 2
        N_arm = (tau - I_A * th_ddot) / sa
        N_elev = (I_e * ddot - q) / sh
        r = abs(k.g(th[i], d[i], SY))
        resmax = max(resmax, r)
        nmis = max(nmis, abs(N_arm - N_elev))
        Nmax_c, Nmax_t = max(Nmax_c, N_arm), min(Nmax_t, N_arm)
        tau_hist.append(tau)
        rows.append((t[i], math.degrees(d[i]), math.degrees(th[i]), r, N_arm, N_elev, tau))
    err = np.abs(np.degrees(d) - math.degrees(d_t))
    ok = np.where(err < EVAL_TOL_DEG)[0]
    t_reach = float(t[ok[0]]) if len(ok) else None
    over = float(np.max(np.degrees(d) * direction) - k.ELEV_LIM)
    # hold: steady torque / force at the target
    th_t = th_cmd
    u, sa, sh = k.sens(th_t, d_t, SY)
    q_hold = HINGE_NM if load == 'linear' else HINGE_NM
    tp_t = sh / sa
    tau_req = q_hold / abs(tp_t)                           # torque on the arm that balances the hinge moment: tau theta' = Q
    N_hold = q_hold / abs(sh)
    out = dict(tau_stall=tau_stall, load=load, direction=direction, t_reach_s=t_reach, overshoot_deg=over,
               peak_rod_force_compression_N=Nmax_c, peak_rod_force_tension_N=-Nmax_t, max_residual_m=resmax, max_N_mismatch=nmis,
               hold_tau_required_Nm=tau_req, hold_rod_force_N=N_hold, hold_margin=tau_stall / tau_req, theta_final_deg=float(math.degrees(th[-1])),
               delta_final_deg=float(math.degrees(d[-1])), steady_error_deg=float(abs(math.degrees(d[-1]) - math.degrees(d_t))), n_steps=len(t), nfev=int(sol.nfev), status=int(sol.status))
    return out, rows


def free_swing(I_e):
    """Servo unpowered, no load, arm free (carries I_a). delta from -20 deg with +5 rad/s until it reaches +21 deg."""
    d0, w0 = math.radians(-20.0), 5.0
    th0 = k.theta_of_delta(d0, SY)

    def f(t, y):
        d, w, th = y
        u, sa, sh = k.sens(th, d, SY)
        tp = sh / sa
        tpp = theta_pp(d)
        M = I_e + I_A * tp ** 2
        return [w, -I_A * tp * tpp * w * w / M, tp * w]

    def ev(t, y):
        return y[0] - math.radians(k.ELEV_STOP)
    ev.terminal = True
    sol = solve_ivp(f, (0.0, 1.0), [d0, w0, th0], method='DOP853', rtol=1e-9, atol=1e-12, events=ev, max_step=1e-3)
    t, (d, w, th) = sol.t, sol.y
    E, rows, resmax = [], [], 0.0
    for i in range(len(t)):
        tp_cf = theta_prime(d[i])                                   # closed-form Jacobian (independent of the integrated theta)
        E.append(0.5 * (I_e + I_A * tp_cf ** 2) * w[i] ** 2)
        r = abs(k.g(th[i], d[i], SY))
        resmax = max(resmax, r)
        rows.append((t[i], math.degrees(d[i]), math.degrees(th[i]), r, E[i]))
    E = np.array(E)
    rel = np.abs(E - E[0]) / E[0]
    return dict(E0_J=float(E[0]), max_rel_energy_error=float(rel.max()), max_residual_m=resmax, t_end_s=float(t[-1]), n_steps=len(t),
                kinetic_energy_ratio_min_max=[float(E.min() / E[0]), float(E.max() / E[0])], omega_end_rad_s=float(w[-1]),
                nfev=int(sol.nfev), status=int(sol.status)), rows


def main():
    with open(os.path.join(k.CAD, '..', 'sitl', 'cad_mass.json')) as fh:
        ev = json.load(fh)['elevon']
    i_e = ev['hinge_inertia_total_kgm2']
    I_e = i_e + I_HORN
    res = dict(git_head=k.git_head(), versions=dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__),
               inputs=dict(I_elevon_balance_CAD=i_e, I_horn_pointmass_EST=I_HORN, I_e_used=I_e, I_arm_from_CAD_outline_1g=I_A, arm_area_m2=ARM_AREA,
                           L_rod_m=k.L_ROD, rod_d_m=ROD_D, E_Pa=E_STEEL, P_euler_N=P_EULER, hinge_Nm=HINGE_NM, omega_nl_rad_s=OMEGA_NL,
                           theta_sat_deg=math.degrees(THETA_SAT), tau_stall=TAU_STALL, servo_rotor_reflected_inertia='-  (not modelled)',
                           rod_mass='massless (0.97 g in the CAD table, neglected)', friction='none', preload_damper='not included (0.0093 + 0.0098 N m EST, params-A.json)'))
    fs, fs_rows = free_swing(I_e)
    res['free_swing'] = fs
    cases, hist = [], []
    for name, tau in TAU_STALL.items():
        for load in ('linear', 'constant'):
            for direction in (1, -1):
                c, rows = run_case(tau, load, direction, I_e)
                c['name'] = '%s|%s|%+d' % (name, load, direction)
                cases.append(c)
                hist += [(c['name'],) + r for r in rows[::4]]
    res['steps'] = cases
    nom = [c for c in cases if c['tau_stall'] == 0.397]
    pc = max(c['peak_rod_force_compression_N'] for c in cases)
    pt = max(c['peak_rod_force_tension_N'] for c in cases)
    res['rod'] = dict(peak_compression_N=pc, peak_tension_N=pt, euler_N=P_EULER, euler_over_peak=P_EULER / pc if pc > 0 else None,
                      euler_E_200GPa_N=P_EULER * 200 / 207, hold_force_max_N=max(c['hold_rod_force_N'] for c in cases))
    res['pass'] = dict(
        D1=bool(fs['max_rel_energy_error'] < 1e-6),
        D2=bool(max(c['max_residual_m'] for c in cases) < 1e-9 and fs['max_residual_m'] < 1e-9),
        D3=bool(pc <= P_EULER / 2),
        D4=bool(min(c['hold_margin'] for c in nom) >= 1.5),
        D5=bool(all(c['t_reach_s'] is not None and c['t_reach_s'] < T_LIMIT for c in cases)),
        D6=bool(max(c['max_N_mismatch'] for c in cases) < 1e-6))
    res['pass_all'] = all(res['pass'].values())
    res['hold_margin_min_by_stall'] = {n: min(c['hold_margin'] for c in cases if c['tau_stall'] == t) for n, t in TAU_STALL.items()}
    os.makedirs(k.OUT, exist_ok=True)
    with open(os.path.join(k.OUT, 'linkage_dynamics' + k.SUF + '.json'), 'w') as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(k.OUT, 'linkage_dynamics_steps' + k.SUF + '.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['case', 't_s', 'delta_deg', 'theta_deg', 'residual_m', 'rod_force_arm_side_N', 'rod_force_elevon_side_N', 'servo_torque_Nm'])
        w.writerows(hist)
    with open(os.path.join(k.OUT, 'linkage_dynamics_freeswing' + k.SUF + '.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['t_s', 'delta_deg', 'theta_deg', 'residual_m', 'energy_J'])
        w.writerows(fs_rows[::2])
    plt = k.get_plt()
    fig, ax = plt.subplots(2, 2, figsize=(10, 7))
    for c in cases:
        if c['tau_stall'] == 0.397 and c['load'] == 'constant':
            rr = [h for h in hist if h[0] == c['name']]
            ax[0, 0].plot([h[1] for h in rr], [h[2] for h in rr], label=c['name'])
            ax[0, 1].plot([h[1] for h in rr], [h[5] for h in rr], label=c['name'])
    ax[0, 0].set_ylabel('elevon delta (deg)')
    ax[0, 1].set_ylabel('rod force, arm side (N, + compression)')
    ax[0, 1].axhline(P_EULER / 2, ls=':', c='r')
    ax[0, 1].axhline(P_EULER, ls='-', c='r')
    ax[0, 0].legend(fontsize=7)
    ax[1, 0].semilogy([r[0] for r in fs_rows], [max(abs(r[4] - fs_rows[0][4]) / fs_rows[0][4], 1e-16) for r in fs_rows])
    ax[1, 0].set_ylabel('free swing relative energy error')
    ax[1, 0].axhline(1e-6, ls=':', c='r')
    ax[1, 1].semilogy([r[0] for r in fs_rows], [max(r[3], 1e-18) for r in fs_rows])
    ax[1, 1].set_ylabel('free swing constraint residual |g| (m)')
    ax[1, 1].axhline(1e-9, ls=':', c='r')
    for a in ax.flat:
        a.set_xlabel('t (s)')
        a.grid(alpha=.3)
    fig.suptitle('Elevon 1-DOF dynamics (frictionless), tau_stall 0.397, constant %.3f N m load' % HINGE_NM + '; red = Euler (solid) and Euler/2 (dotted)')
    fig.tight_layout()
    fig.savefig(os.path.join(k.OUT, 'linkage_dynamics' + k.SUF + '.png'), dpi=110)
    print(json.dumps({'free_swing': fs, 'rod': res['rod'], 'pass': res['pass'], 'hold_margin_min_by_stall': res['hold_margin_min_by_stall'],
                      'steps': [{kk: c[kk] for kk in ('name', 't_reach_s', 'overshoot_deg', 'peak_rod_force_compression_N', 'peak_rod_force_tension_N', 'hold_tau_required_Nm', 'hold_rod_force_N', 'hold_margin', 'max_residual_m', 'max_N_mismatch')} for c in cases]}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
