"""D-212 rev 3 strength checks of the elevon linkage parts that the three mechanism scripts do not cover (reviews 2026-11-18 D212 F-2/F-3 and
D212r2 C-1, M-1, M-3, M-4). Categories: hand calculation (closed forms) and FEA (1-D beam on an elastic foundation, section 3).
    python -I redesign/qp/A/mechanism/linkage_loads_check.py      (run AFTER elevon_dynamics.py, mid state: it reads out/linkage_dynamics.json)

Every check states MODEL, VALIDITY, INPUTS, ALLOWABLE (source), FACTOR; the results go to out/linkage_loads_check.json, which gen_params_a.py reads
for the proof claims (CL-A-HORN-*, CL-A-ELEVON-TORSION-FOAM, CL-A-ROD-LEG-STALL, CL-A-LINKAGE-FREEPLAY). A check that fails is reported as failing.

LOAD CASES
  hold  : rod force at the VD hinge moment, max over +-20 deg (elevon_dynamics.py, 17.05 N; hinge moment 0.146 N m EST, FIXES2 s2).
  stall : the servo stalled against the stop or a jammed elevon. Quasi-static: F = tau_stall / (R_arm * min l_a) over +-21 deg (review r2 M-1),
          tau_stall 0.397 N m at 7.2 V (EST, params servo.stall_72_nm). The dynamic step peak (42.7 N) is lower and is NOT used.
FACTORS (project basis, structures/fea_arm.py KF / KP): hold: printed / bonded 2.156 (1.5 load x 1.15 printed x 1.25 bonded), metal 1.5 (review);
  stall: 1.15 x 1.25 = 1.4375 for printed / bonded (no load factor: the stall force is the actuator's ceiling, not an estimated load), and BOTH
  1.0 and 1.5 for the steel rod leg (review r2 M-1 asks for 1.5; the receipt test is set at 1.5 x F_stall).

1. Z-bend leg bending (metal). M = F (d/2 + t_arm/2) (rod resting on the arm, arm hole reacts at the arm mid-plane), sigma = 32 M / (pi d^3) x curved-wire
   factor K = (4C^2 - C - 1) / (4C (C - 1)), C = 2r/d = 2 (pliers bend r = d) -> 1.625 (Shigley, recalled, VERIFY). Validity: slender round bar, bend
   radius >= d. Allowable: rod grade NOT published ("-"); A228 music wire bending allowable 0.78 S_ut, S_ut = 2211 / d^0.145 (Shigley Tables 10-4 / 10-6,
   RECALLED, NOT re-read: VERIFY). Output = the yield the rod must have; the receipt test proves it.
2. Horn blade and hole (printed PETG, printed lying flat so the profile plane is the layer plane: in-layer allowable).
   Blade: horizontal sections z from the skin to the hole, width w(z) from the drawn outline (electrical.horn_profile), sigma = 6 F (z_hole - z) / (t w^2).
   Validity: beam theory, w <= 2 x lever at the governing section (stubby near the skin: conservative). Hole: bearing F / (d_pin t), shear-out
   F / (2 t e), e = ligament. Allowable: PETG 20 MPa in-layer / bearing (EST, structures/fea_arm.py ALLOW['petg'], arm_cup_checks.py PETG_BEAR).
3. Horn rib in the foam (C-1). The rib is a 2 mm PETG plate in a slot through the elevon, bonded on both faces. MODEL: Euler-Bernoulli beam along x
   (EI = E t d(x)^3 / 12, d = rib depth) on an elastic foundation of foam shear on its two faces: transverse k_z = 2 G d / l, rotational
   k_t = 2 G d^3 / (12 l), axial k_x = 2 G d / l (the rib is axially rigid: uniform u); the horn force F (along x, at the hole height) and its moment
   about the rib mid-depth are applied over the blade base. Face shear tau = (G / l) x local displacement. VALIDITY: linear elastic foam, Winkler
   (no coupling between springs), small rotations. The rib is NOT rigid (lambda L >> 1, printed below), which is why a rigid-rib / weld-group
   formula is not used. INPUTS: E_PETG 2.1 GPa (fe_a.py nom, EST); foam G = E / (2 (1 + nu)), E 5-10 MPa (CHAIN.md ASM-D5 "8-10", review r2 5-10),
   nu 0.1 EST; shear penetration l 2-8 mm EST (the foundation is swept over G / l). ALLOWABLE: foam shear 86 kPa (EST, foam_103.py: 100 x 103/120).
   Skin (tape) paths are ignored: conservative for the foam faces.
4. Elevon torsion beside the horn, foam only (pre-existing, found here). Saint-Venant thin open section: tau = T t_max / J, J = int t^3 dx / 3 over the
   elevon section. T = the share of the hinge moment carried by the outboard segment (span fraction) at hold; the whole stall torque into the outboard
   stop at stall. Validity: thin open section (t / chord <= 0.14). Same 86 kPa allowable. The tape-skin cell (Bredt, q = T / 2A) is reported for
   comparison; tape properties are "-", so the cell is not credited.
5. Free play budget (M-4): from out/linkage_kinematics.json (hole clearances / horn radius + the Z-bend freedom K7) against the 1 deg guide
   (review/QP-4/SERVO.md s4). Clevis cheek holes "-": measured at E1.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np          # noqa: E402
import linkage_core as k    # noqa: E402

e, c = k._e, k._c
MM = 1e-3
TAU_STALL = 0.397                                   # N m, 7.2 V EST (params servo.stall_72_nm; elevon_dynamics.TAU_STALL)
HINGE_NM = 0.146                                    # N m at VD, +-20 deg (elevon_dynamics.HINGE_NM)
KP, KF = 1.5 * 1.15 * 1.25, 1.5 * 1.15             # structures/fea_arm.py
K_STALL_PRINTED = 1.15 * 1.25
D = k.ROD_D
T_ARM = e.ARM_T
Z_SEC = math.pi * D ** 3 / 32
C_CW = 2.0
K_CW = (4 * C_CW ** 2 - C_CW - 1) / (4 * C_CW * (C_CW - 1))
SUT_A228 = 2211.0 / (D * 1e3) ** 0.145             # MPa (recalled constants)
ALLOW_A228 = 0.78 * SUT_A228
PETG_INLAYER, PETG_BEAR = 20.0, 20.0               # MPa EST (fea_arm.py ALLOW['petg'], arm_cup_checks.py PETG_BEAR)
E_PETG = 2.1e9
FOAM_SHEAR = 100e3 * 103 / 120                     # Pa EST (foam_103.py)
PIN_D = 1.0e-3


def stall_force():
    """F = tau_stall / (R_arm l_a), min lever over +-21 deg, both sides (current joint state)."""
    best = None
    for dd in np.arange(-k.ELEV_STOP, k.ELEV_STOP + 1e-9, 0.25):
        d = math.radians(dd)
        for sy in (1, -1):
            th = k.theta_of_delta(d, sy)
            la = k.levers(th, d, sy)[3]
            f = TAU_STALL / (k.ARM_R * la)
            if best is None or f > best[0]:
                best = (f, float(dd), la)
    return best


def rod_leg(f_hold, f_stall):
    ecc = D / 2 + T_ARM / 2
    out = dict(model='sigma = K 32 F e / (pi d^3), e = d/2 + t_arm/2', e_mm=ecc * 1e3, K_curved_wire=K_CW, A228_Sut_MPa_recalled=SUT_A228,
               A228_bending_allow_MPa_recalled=ALLOW_A228)
    for name, F, sfs in (('hold', f_hold, (1.5,)), ('stall', f_stall, (1.0, 1.5))):
        sig = F * ecc / Z_SEC / 1e6
        out[name] = dict(F_N=F, sigma_nominal_MPa=sig, sigma_K_MPa=K_CW * sig,
                         required_yield_MPa={str(sf): sf * K_CW * sig for sf in sfs})
    req = out['stall']['required_yield_MPa']['1.5']
    out['required_yield_MPa_governing'] = max(req, out['hold']['required_yield_MPa']['1.5'])
    out['collapse_Fc_N_at_required_yield'] = req * 1e6 * D ** 3 / (6 * ecc)
    out['music_wire_ok_recalled'] = bool(out['required_yield_MPa_governing'] <= ALLOW_A228)
    out['receipt_test'] = ('form the Z-bend on an M02 rod, clamp the arm-hole end in a 2 mm plate with a 1.3 mm hole, load the rod end along its axis with '
                           '%.0f N (1.5 x the %.1f N stall force) for 10 s: pass = no permanent set over 0.2 mm at the far end; a rod that fails is '
                           'replaced by ASTM A228 music wire 1.2 mm and the test repeated' % (1.5 * f_stall, f_stall))
    return out


def _slice_width(pr, z):
    xs = []
    for i in range(len(pr)):
        (x0, z0), (x1, z1) = pr[i], pr[(i + 1) % len(pr)]
        if (z0 - z) * (z1 - z) < 0:
            xs.append(x0 + (x1 - x0) * (z - z0) / (z1 - z0))
    return (max(xs) - min(xs)) if len(xs) >= 2 else None


def blade(f_hold, f_stall):
    pr = e.horn_profile(n=40)
    z0 = max(c.zu(e.HORN_PX0), c.zu(e.HORN_BX1))           # sections above the skin everywhere along the base (conservative: the base is sloped)
    zs = np.linspace(z0 + 0.05 * MM, e.ROD_Z - 0.8 * MM, 160)   # up to the hole edge region (the head above is checked as bearing / shear-out)
    rows = []
    for z in zs:
        w = _slice_width(pr, z)
        m_arm = e.ROD_Z - z
        rows.append((z, w, m_arm, 6 * m_arm / (e.HORN_T * w ** 2)))     # sigma per newton
    zg, wg, ag, sg = max(rows, key=lambda r: r[3])
    lig = e.HORN_HR - e.HORN_HOLE_D / 2
    out = dict(model='horizontal sections of the drawn outline (slices of electrical.horn_profile, hole not deducted below the hole edge); sigma = 6 F (z_hole - z) / (t w^2); bearing F / (d_pin t); shear-out F / (2 t e)',
               governing_z_mm=zg * 1e3, governing_width_mm=wg * 1e3, governing_lever_mm=ag * 1e3, print='lying flat (profile plane = layer plane)',
               allowable_inlayer_MPa_EST=PETG_INLAYER, allowable_bearing_MPa_EST=PETG_BEAR, ligament_mm=lig * 1e3)
    for name, F, kf in (('hold', f_hold, KP), ('stall', f_stall, K_STALL_PRINTED)):
        sb = sg * F / 1e6
        brg = F / (PIN_D * e.HORN_T) / 1e6
        sho = F / (2 * e.HORN_T * lig) / 1e6
        out[name] = dict(F_N=F, factor=kf, root_sigma_MPa=sb, root_factored_MPa=kf * sb, root_ok=bool(kf * sb <= PETG_INLAYER),
                         bearing_MPa=brg, bearing_factored_MPa=kf * brg, bearing_ok=bool(kf * brg <= PETG_BEAR),
                         shearout_MPa=sho, shearout_factored_MPa=kf * sho, shearout_ok=bool(kf * sho <= PETG_INLAYER / math.sqrt(3) * 1.0))
    return out


def rib_foundation(F, g_over_l, n=220):
    """Beam on elastic foundation (FE, Hermite beam elements + consistent foundation terms by 2-point Gauss on the element). Returns peak face shear (Pa)."""
    x0, x1 = e.HORN_PX0, e.HORN_RIB_X1
    xs = np.linspace(x0, x1, n + 1)
    d = np.array([c.zu(x) - c.zl(x) - 2 * e.HORN_RIB_IN for x in xs])
    zm = np.array([(c.zu(x) + c.zl(x)) / 2 for x in xs])
    t = e.HORN_T
    ndof = 2 * (n + 1)
    K = np.zeros((ndof, ndof))
    fvec = np.zeros(ndof)
    gp = [(-1 / math.sqrt(3), 1.0), (1 / math.sqrt(3), 1.0)]
    for i in range(n):
        L = xs[i + 1] - xs[i]
        dm = 0.5 * (d[i] + d[i + 1])
        EI = E_PETG * t * dm ** 3 / 12
        kb = EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        kf = np.zeros((4, 4))
        for xi, wgt in gp:
            s = (xi + 1) / 2
            dd = d[i] + (d[i + 1] - d[i]) * s
            N = np.array([1 - 3 * s ** 2 + 2 * s ** 3, L * (s - 2 * s ** 2 + s ** 3), 3 * s ** 2 - 2 * s ** 3, L * (-s ** 2 + s ** 3)])
            dN = np.array([-6 * s + 6 * s ** 2, L * (1 - 4 * s + 3 * s ** 2), 6 * s - 6 * s ** 2, L * (-2 * s + 3 * s ** 2)]) / L
            kz = 2 * g_over_l * dd
            kt = 2 * g_over_l * dd ** 3 / 12
            kf += (kz * np.outer(N, N) + kt * np.outer(dN, dN)) * wgt * L / 2
        idx = [2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3]
        K[np.ix_(idx, idx)] += kb + kf
    # load: moment of F about the local mid-depth, spread as a couple over the blade base nodes
    base = [j for j in range(n + 1) if xs[j] <= e.HORN_BX1 + 1e-12]
    for j in base:
        fvec[2 * j + 1] += F * (e.ROD_Z - zm[j]) / len(base)
    sol = np.linalg.solve(K, fvec)
    w = sol[0::2]
    th = sol[1::2]
    kx = 2 * g_over_l * d
    u = F / np.trapezoid(kx, xs)                       # uniform axial slip of the (axially rigid) rib
    tau_ax = g_over_l * u
    tau_rot = g_over_l * np.abs(th) * d / 2
    tau_z = g_over_l * np.abs(w)
    tau = np.sqrt((tau_ax + tau_rot) ** 2 + tau_z ** 2)
    EI0 = E_PETG * t * d[0] ** 3 / 12
    lam = (2 * g_over_l * d[0] / (4 * EI0)) ** 0.25
    return dict(peak_kPa=float(tau.max() / 1e3), at_x_mm_aft_hinge=float((xs[tau.argmax()] - c.XH) * 1e3), axial_kPa=float(tau_ax / 1e3),
                lambda_L_front=float(lam * (x1 - x0)), rib_rotation_deg=float(math.degrees(np.abs(th).max())))


def rib_foam(f_hold, f_stall):
    cases = []
    for E_f in (5e6, 10e6):
        G = E_f / (2 * 1.1)
        for l_ in (2e-3, 4e-3, 8e-3):
            cases.append((E_f, l_, G / l_))
    out = dict(model=__doc__.split('3. Horn rib in the foam (C-1).')[1].split('4. Elevon torsion')[0].strip(),
               allowable_kPa_EST=FOAM_SHEAR / 1e3, sweep=[])
    for E_f, l_, gl in cases:
        h = rib_foundation(f_hold, gl)
        s = rib_foundation(f_stall, gl)
        out['sweep'].append(dict(E_foam_MPa=E_f / 1e6, l_mm=l_ * 1e3, G_over_l_MPa_per_mm=gl / 1e9, hold_peak_kPa=h['peak_kPa'], stall_peak_kPa=s['peak_kPa'],
                                 lambda_L_front=h['lambda_L_front'], at_x_mm=h['at_x_mm_aft_hinge']))
    hp = [r['hold_peak_kPa'] for r in out['sweep']]
    sp = [r['stall_peak_kPa'] for r in out['sweep']]
    out['hold'] = dict(F_N=f_hold, factor=KP, peak_kPa_range=[min(hp), max(hp)], factored_kPa_max=KP * max(hp), factored_kPa_min=KP * min(hp),
                       ok=bool(KP * max(hp) <= FOAM_SHEAR / 1e3))
    out['stall'] = dict(F_N=f_stall, factor=K_STALL_PRINTED, peak_kPa_range=[min(sp), max(sp)], factored_kPa_max=K_STALL_PRINTED * max(sp),
                        ok=bool(K_STALL_PRINTED * max(sp) <= FOAM_SHEAR / 1e3))
    return out


def elevon_torsion(f_stall):
    xs = np.linspace(c.XH, c.C, 3000)
    tt = np.array([c.zu(x) - c.zl(x) for x in xs])
    J = np.trapezoid(tt ** 3, xs) / 3
    A = np.trapezoid(tt, xs)
    hy = k.SERVO_Y - k.ARM_R
    frac_out = (c.ELEV_Y1 - hy) / (c.ELEV_Y1 - c.ELEV_Y0)
    t_hold = HINGE_NM * frac_out
    t_stall = f_stall * k.HORN_R
    out = dict(model='Saint-Venant thin open section, foam only: tau = T t_max / J', J_mm4=J * 1e12, t_max_mm=tt.max() * 1e3, section_area_mm2=A * 1e6,
               outboard_span_fraction=frac_out, allowable_kPa_EST=FOAM_SHEAR / 1e3, thickness_over_chord=float(tt.max() / (c.C - c.XH)))
    for name, T, kf in (('hold', t_hold, KP), ('stall', t_stall, K_STALL_PRINTED)):
        tau = T * tt.max() / J
        out[name] = dict(T_Nm=T, factor=kf, tau_kPa=tau / 1e3, factored_kPa=kf * tau / 1e3, ok=bool(kf * tau <= FOAM_SHEAR),
                         bredt_q_N_per_m=T / (2 * A), bredt_note='tape skin shear flow if the elevon cell is closed (nose face taped): tape strength "-", not credited')
    return out


def main():
    dyn = json.load(open(os.path.join(k.OUT, 'linkage_dynamics.json')))
    kin = json.load(open(os.path.join(k.OUT, 'linkage_kinematics.json')))
    f_hold = dyn['rod']['hold_force_max_N']
    fs, at_deg, la = stall_force()
    out = {'inputs': dict(F_hold_N=f_hold, F_stall_N=fs, F_stall_at_delta_deg=at_deg, min_arm_lever_ratio=la, tau_stall_Nm=TAU_STALL,
                          dynamic_step_peak_N_not_used=dyn['rod']['peak_compression_N'], hinge_vd_Nm=HINGE_NM, KP=KP, K_stall_printed=K_STALL_PRINTED,
                          arm_joint_state=k.STATE)}
    out['z_bend_leg'] = rod_leg(f_hold, fs)
    out['horn_blade'] = blade(f_hold, fs)
    out['horn_rib_foam'] = rib_foam(f_hold, fs)
    out['elevon_torsion_foam_only'] = elevon_torsion(fs)
    out['horn_rib_vs_elevon_body_hold'] = out['horn_rib_foam']['hold']['factored_kPa_max'] / out['elevon_torsion_foam_only']['hold']['factored_kPa']
    fp = kin['free_play_budget_deg']
    out['free_play'] = dict(total_known_deg=fp['total_known_deg'], guide_deg=1.0, ok=bool(fp['total_known_deg'] <= 1.0), parts=fp,
                            mitigation='hinge viscous damper: flutter has no instability for any K 0.01-20 N m/rad (FIXES2 s1, CL-A-FLUTTER-ELEVON-*), preload strips remove low-amplitude slack; E1 bench measurement')
    out['pass'] = dict(rod_leg_music_wire_recalled=out['z_bend_leg']['music_wire_ok_recalled'],
                       blade_root_hold=out['horn_blade']['hold']['root_ok'], blade_root_stall=out['horn_blade']['stall']['root_ok'],
                       hole_bearing_hold=out['horn_blade']['hold']['bearing_ok'], hole_bearing_stall=out['horn_blade']['stall']['bearing_ok'],
                       rib_foam_hold=out['horn_rib_foam']['hold']['ok'], rib_foam_stall=out['horn_rib_foam']['stall']['ok'],
                       elevon_torsion_foam_hold=out['elevon_torsion_foam_only']['hold']['ok'], elevon_torsion_foam_stall=out['elevon_torsion_foam_only']['stall']['ok'],
                       free_play_le_1deg=out['free_play']['ok'])
    out['git_head'] = k.git_head()
    with open(os.path.join(k.OUT, 'linkage_loads_check.json'), 'w') as f:
        json.dump(out, f, indent=1)
    show = {kk: out[kk] for kk in ('inputs', 'pass', 'horn_rib_vs_elevon_body_hold')}
    show['rod_leg'] = {kk: out['z_bend_leg'][kk] for kk in ('hold', 'stall', 'required_yield_MPa_governing', 'collapse_Fc_N_at_required_yield')}
    show['blade'] = {kk: out['horn_blade'][kk] for kk in ('governing_width_mm', 'governing_lever_mm', 'hold', 'stall')}
    show['rib'] = {kk: out['horn_rib_foam'][kk] for kk in ('hold', 'stall', 'sweep')}
    show['elevon'] = {kk: out['elevon_torsion_foam_only'][kk] for kk in ('J_mm4', 'hold', 'stall')}
    show['free_play'] = out['free_play']['total_known_deg']
    print(json.dumps(show, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
