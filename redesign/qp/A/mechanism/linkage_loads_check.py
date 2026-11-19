"""D-212 rev 3 strength checks of the elevon linkage parts that the three mechanism scripts do not cover (reviews 2026-11-18 D212 F-2/F-3 and
D212r2 C-1, M-1, M-3, M-4). Categories: hand calculation (closed forms) and FEA (1-D beam on an elastic foundation, section 3).
    python -I redesign/qp/A/mechanism/linkage_loads_check.py      (run AFTER elevon_dynamics.py, mid state: it reads out/linkage_dynamics.json)

Every check states MODEL, VALIDITY, INPUTS, ALLOWABLE (source), FACTOR; the results go to out/linkage_loads_check.json, which gen_params_a.py reads
for the proof claims (CL-A-HORN-*, CL-A-ELEVON-TORSION-FOAM, CL-A-ROD-LEG-STALL, CL-A-LINKAGE-FREEPLAY). A check that fails is reported as failing.

LOAD CASES
  hold  : rod force at the VD hinge moment, max over +-20 deg (elevon_dynamics.py, 17.05 N; hinge moment 0.146 N m EST, FIXES2 s2).
  stall : the servo stalled against the stop or a jammed elevon. Quasi-static: F = tau_stall / (R_arm * min l_a) over +-21 deg (review r2 M-1),
          tau_stall 0.397 N m at 7.2 V (EST, params servo.stall_72_nm). The dynamic step peak (42.7 N) is lower and is NOT used.
          VOLTAGE BASIS (review r3 m-8): the 7.2 V stall torque is valid ONLY with the Kakute servo-rail jumper at 7.2 V (SERVO.md s2: the FC offers 5.3 V default /
          7.2 V selectable; 8.4 V, 4.7 kgf cm = 0.461 N m, is NOT available from this FC). The 8.4 V case (about 59 N) is reported below as an out-of-spec
          informational case (a different servo supply) and is not a claim; the 0.397 N m is an interpolation (EST) and the 1.5 load factor is not applied to it.
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
6. Keeper bridge MEC-008 (review r3 m-4): hand calculation, section 6 below (cantilever bridge, vertical rod reaction by moment balance on the rod).
7. Servo speed vs hinge load through the linkage (T-056, R-PHY-08): section 7 below (DC-motor torque-speed line through the solved gearing).
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
KGFCM = 9.80665e-2                                  # N m per kgf cm (standard gravity 9.80665 m/s2 x 0.01 m, definition)
TAU_STALL_84 = 4.7 * KGFCM                          # 0.461 N m: ES3054HV 4.7 kgf cm at 8.4 V (SERVO.md s2, RMRC 85975, 2026-11-15); NOT available from the Kakute
TAU_STALL_60 = 0.333                                # N m at 6.0 V (SERVO.md s2: 3.4 kgf cm = 0.333 N m, published pair with the 0.13 s / 60 deg speed)
OMEGA_NL = math.radians(60.0) / 0.13                # rad/s no-load at 6.0 V (SERVO.md s2: 0.13 s / 60 deg; 7.2 V speed "-" (not published): the 6 V value is used, conservative)
PRELOAD_NM, DAMPER_SLEW_NM = 0.0093, 0.0098         # N m at the hinge, EST (FIXES2 s2; params-A.json servo.preload_nm / damper_slew_nm)
CROSSOVER_HZ = 2.2                                  # rate-loop crossover of the chosen gains (review/QP-4/CLAIMS-FIX.md: 2.6 -> 2.2 Hz, D-191)
ROLL_AMP_DEG = 11.0                                 # elevon amplitude for the 90 deg/s roll rate (REQUIREMENTS-A.md A-P11, EST: "about +-11 deg")
ELEV_STEP_S = 0.25                                  # 0 -> +-20 deg reached within 0.25 s (elevon_dynamics.py criterion D5, EST)
BRIDGE_B, BRIDGE_T = (e.KEEP_B[1] - e.KEEP_B[0]), e.KEEP_T      # MEC-008 bridge 3.1 mm wide x 0.8 mm thick (electrical.py)
BRIDGE_LEVER = (e.ARM_R) - e.KEEP_SP1               # 2.0 mm: spacer end to the Z-bend leg axis (hole centre), the bridge cantilever length (electrical.py)


def stall_force():
    return stall_force_at(TAU_STALL)


def stall_force_at(tau_stall):
    """F = tau_stall / (R_arm l_a), min lever over +-21 deg, both sides (current joint state)."""
    best = None
    for dd in np.arange(-k.ELEV_STOP, k.ELEV_STOP + 1e-9, 0.25):
        d = math.radians(dd)
        for sy in (1, -1):
            th = k.theta_of_delta(d, sy)
            la = k.levers(th, d, sy)[3]
            f = tau_stall / (k.ARM_R * la)
            if best is None or f > best[0]:
                best = (f, float(dd), la)
    return best


def rod_leg(f_hold, f_stall):
    """Z-bend leg. Eccentricity e = rod axis height above the arm mid-plane (the arm hole reacts at the arm mid-plane): LO = the rod resting on the arm
    (d/2 + t/2 = 1.6 mm), HI = the rod lifted against the keeper bridge (review r3 m-3: 1.9 mm, +19 %). The HI state governs: the requirement and the receipt-test
    load are set on it."""
    arm_mid = e.ARM_Z0 + T_ARM / 2
    e_lo = D / 2 + T_ARM / 2
    e_hi = (e.ROD_Z + e.ROD_KEEP / 2) - arm_mid
    assert abs((e.ROD_Z - e.ROD_KEEP / 2) - arm_mid - e_lo) < 1e-9, 'rod-resting eccentricity differs from d/2 + t/2'
    ecc = e_hi
    out = dict(model='sigma = K 32 F e / (pi d^3); e = rod axis above the arm mid-plane: LO 1.6 mm (rod on the arm), HI 1.9 mm (rod against the keeper) governs (review r3 m-3)',
               e_mm=ecc * 1e3, e_lo_mm=e_lo * 1e3, e_hi_mm=e_hi * 1e3, e_ratio_hi_over_lo=e_hi / e_lo, K_curved_wire=K_CW, A228_Sut_MPa_recalled=SUT_A228,
               A228_bending_allow_MPa_recalled=ALLOW_A228)
    for name, F, sfs in (('hold', f_hold, (1.5,)), ('stall', f_stall, (1.0, 1.5))):
        sig = F * ecc / Z_SEC / 1e6
        out[name] = dict(F_N=F, sigma_nominal_MPa=sig, sigma_K_MPa=K_CW * sig,
                         required_yield_MPa={str(sf): sf * K_CW * sig for sf in sfs},
                         required_yield_MPa_rod_on_arm_LO={str(sf): sf * K_CW * F * e_lo / Z_SEC / 1e6 for sf in sfs})
    req = out['stall']['required_yield_MPa']['1.5']
    out['required_yield_MPa_governing'] = max(req, out['hold']['required_yield_MPa']['1.5'])
    out['collapse_Fc_N_at_required_yield'] = req * 1e6 * D ** 3 / (6 * ecc)
    out['music_wire_ok_recalled'] = bool(out['required_yield_MPa_governing'] <= ALLOW_A228)
    f_test = 1.5 * f_stall * e_hi / e_lo
    out['receipt_test_load_N'] = f_test
    out['receipt_test'] = ('form the Z-bend on an M02 rod, clamp the arm-hole end in a 2 mm plate with a 1.3 mm hole (rod resting on the plate), load the rod end along its axis with '
                           '%.0f N for 10 s (= 1.5 x the %.1f N stall force x e_hi / e_lo = %.2f / %.2f, so the rod resting on the plate sees the moment of the keeper-lifted hi state, '
                           'review r3 m-3): pass = no permanent set over 0.2 mm at the far end; a rod that fails is replaced by ASTM A228 music wire 1.2 mm and the test repeated'
                           % (f_test, f_stall, e_hi * 1e3, e_lo * 1e3))
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


def keeper_bridge(f_hold, f_stall, e_hi):
    """Section 6 (review r3 m-4). MEC-008 bridge, hand calculation. MODEL: the rod is a two-force member pinned at the clevis, loaded by the arm hole at the arm
    mid-plane, so the axial force F acts with the eccentricity e_hi (rod axis above the arm mid-plane, rod lifted against the keeper) and the moment F e_hi is
    balanced by a vertical couple V L over the rod length L: V = F e_hi / L. The keeper bridge reacts V (worst direction = the one that lifts the rod) at the Z-bend
    leg, a cantilever of length a = spacer end to the leg axis from the spacer face, section b x t at the spacer end:
    sigma = 6 V a / (b t^2). VALIDITY: slender cantilever (a / t = 2.5, short; beam theory), static, no creep. ALLOWABLE: PETG 20 MPa in-layer EST (fea_arm.py),
    bridge printed flat so the bending stress lies in the layer plane. FACTOR: 2.156 at hold, 1.4375 at stall (same as the printed parts). NOT covered ("-"): creep and
    preload loss of the 2.3 mm PETG stack under the M2 screw (the keeper is held against rotation by clamp friction only; screw torque and PETG creep rate "-"):
    inspect and retorque at BUILD D5b and every preflight."""
    out = dict(model=keeper_bridge.__doc__.split('MODEL:')[1].split('VALIDITY')[0].strip(), b_mm=BRIDGE_B * 1e3, t_mm=BRIDGE_T * 1e3, a_mm=BRIDGE_LEVER * 1e3,
               L_rod_mm=k.L_ROD * 1e3, e_hi_mm=e_hi * 1e3, allowable_MPa_EST=PETG_INLAYER,
               creep_and_preload='"-" (not analysed): retorque / inspect at D5b and each preflight')
    for name, F, kf in (('hold', f_hold, KP), ('stall', f_stall, K_STALL_PRINTED)):
        V = F * e_hi / k.L_ROD
        sig = 6 * V * BRIDGE_LEVER / (BRIDGE_B * BRIDGE_T ** 2) / 1e6
        out[name] = dict(F_N=F, V_N=V, sigma_MPa=sig, factor=kf, factored_MPa=kf * sig, ok=bool(kf * sig <= PETG_INLAYER), utilisation=kf * sig / PETG_INLAYER)
    return out


def stall_84(f_stall84, rod):
    """Out-of-spec informational case (review r3 m-8): checks scaled to the 8.4 V stall torque (every check below is linear in F)."""
    sc = f_stall84 / rod['stall']['F_N']
    return dict(note='8.4 V is NOT available from the Kakute (5.3 / 7.2 V); informational, not a claim. Checks are linear in F.', tau_stall_Nm=TAU_STALL_84,
                F_stall_N=f_stall84, scale_vs_7V2=sc, leg_required_yield_MPa_1p0=rod['stall']['required_yield_MPa']['1.0'] * sc,
                leg_required_yield_MPa_1p5=rod['stall']['required_yield_MPa']['1.5'] * sc)


def gearing_range():
    """g = d delta / d theta over +-ELEV_LIM both sides, current joint state; returns (min, max, rows at the end points)."""
    rows = []
    for sy in (1, -1):
        for dd in np.arange(-k.ELEV_LIM, k.ELEV_LIM + 1e-9, 0.5):
            d = math.radians(dd)
            th = k.theta_of_delta(d, sy)
            u, sa, sh = k.sens(th, d, sy)
            rows.append((float(dd), sy, abs(sa / sh)))
    g = [r[2] for r in rows]
    return min(g), max(g), [r for r in rows if abs(abs(r[0]) - k.ELEV_LIM) < 1e-9]


def servo_speed():
    """Section 7 (T-056, R-PHY-08; category: kinematics + hand calculation). Servo torque AND speed against the hinge load through the linkage.
    MODEL: DC-motor torque-speed line omega_servo = OMEGA_NL (1 - tau / tau_stall) (the law of elevon_dynamics.py: tau = tau_stall (duty - omega / OMEGA_NL));
    tau on the servo shaft = g (Q + preload + damper) with g = d delta / d theta (virtual work through the solved linkage, 0.905-0.930), Q = the VD hinge moment
    0.146 N m at the +-20 deg end (the linear load of elevon_dynamics.py peaks there), so the loaded speed is the SLOWEST point (conservative: along a sinusoid
    the load is lower away from the end points). Elevon rate = g omega_servo. VALIDITY: steady loaded speed (the reached-in-time check is the dynamic step D5,
    0.056 s to 0.5 deg); linear torque-speed line; servo speed at 7.2 V is NOT published ("-"), so the 6.0 V value is used with the 6.0 V stall (published pair) and,
    as a second case, with the 7.2 V EST stall torque (speed still the 6 V value, so conservative).
    REQUIRED RATES (EST, none is a published servo requirement): R1 full travel 0 -> 20 deg in 0.25 s (elevon_dynamics.py D5 criterion, EST) = 80 deg/s mean;
    R2 a sinusoid of the roll-command amplitude +-11 deg (REQUIREMENTS-A.md A-P11, EST: 90 deg/s roll) at the rate-loop crossover 2.2 Hz (CLAIMS-FIX.md):
    peak rate 2 pi f A = 152 deg/s; R3 a sinusoid at the full +-20 deg at 2.2 Hz (extreme; reported as a frequency limit). Margin = loaded elevon rate / required.
    Criterion: margin >= 1.0 for R1 and R2 (no source for a larger speed factor; the 1.5 factor of the torque check is not extended to speed)."""
    gmin, gmax, ends = gearing_range()
    g_end = max(r[2] for r in ends)                              # largest g at the end points (largest servo torque per hinge moment)
    out = dict(model=servo_speed.__doc__.split('MODEL:')[1].split('VALIDITY')[0].strip(), gearing_min=gmin, gearing_max=gmax, gearing_at_end_points_max=g_end,
               omega_nl_rad_s_6V=OMEGA_NL, omega_nl_deg_s_6V=math.degrees(OMEGA_NL), omega_nl_source='SERVO.md s2: 0.13 s / 60 deg at 6.0 V (7.2 V "-", not published)',
               crossover_Hz=CROSSOVER_HZ, roll_amp_deg=ROLL_AMP_DEG, step_s=ELEV_STEP_S)
    req = dict(R1_step_deg_s=k.ELEV_LIM / ELEV_STEP_S, R2_sine_deg_s=2 * math.pi * CROSSOVER_HZ * ROLL_AMP_DEG, R3_sine_full_throw_deg_s=2 * math.pi * CROSSOVER_HZ * k.ELEV_LIM)
    out['required_elevon_rate_deg_s'] = req
    cases = {}
    for name, tau_s in (('6.0V_pair_0.333', TAU_STALL_60), ('7.2V_EST_0.397_speed_at_6V', TAU_STALL)):
        tau_hold = g_end * HINGE_NM
        tau_load = g_end * (HINGE_NM + PRELOAD_NM + DAMPER_SLEW_NM)
        om_s = OMEGA_NL * (1 - tau_load / tau_s)
        rate = math.degrees(g_end * om_s)
        cases[name] = dict(tau_stall_Nm=tau_s, tau_hold_Nm=tau_hold, torque_margin_hold=tau_s / tau_hold, tau_loaded_Nm=tau_load, torque_margin_loaded=tau_s / tau_load,
                           servo_speed_loaded_rad_s=om_s, elevon_rate_loaded_deg_s=rate, elevon_rate_no_load_deg_s=math.degrees(g_end * OMEGA_NL),
                           speed_margin_R1=rate / req['R1_step_deg_s'], speed_margin_R2=rate / req['R2_sine_deg_s'], speed_margin_R3=rate / req['R3_sine_full_throw_deg_s'],
                           sine_limit_Hz_at_11deg=rate / (2 * math.pi * ROLL_AMP_DEG), sine_limit_Hz_at_20deg=rate / (2 * math.pi * k.ELEV_LIM),
                           ok=bool(rate >= req['R1_step_deg_s'] and rate >= req['R2_sine_deg_s']))
    out['cases'] = cases
    out['ok'] = all(c['ok'] for c in cases.values())
    out['cross_check'] = 'AR-002 (linkage_dynamics.json): hold_margin 2.93 at 0.397 N m and 2.46 at 0.333 N m for tau = g x 0.146; this adds preload + damper (g x 0.1653 N m) and the speed'
    out['not_modelled'] = 'servo rotor / gear inertia, BEC rail sag under load (lowers torque and speed), stall current: all "-"'
    return out


def motor_mount_evidence():
    """R-PHY-08, motor / prop mechanical check = the D-209 / D-210 arm and motor-cup FEA (cited, NOT rerun here: no FEA in this task)."""
    return dict(category='FEA (cited record, not rerun)', change_log='redesign/params/CHANGE-LOG.md D-209 (2026-11-18) and D-210',
                report='redesign/review/QP-5/FEA-ARM.md section 8 (D-209, run `current`) and 8.1 (D-210, run `current_d210`)', script='redesign/qp/A/structures/fea_arm.py',
                results_D209='arm tube axial F2 29.9 / 203 MPa allowed, S2 79.8 / 350; tube shear S2 9.6 / 30 (tightest, ratio 3.1); cup 99th percentile F2 0.75 / 9.3, S2 3.1 / 20; cup bond mean F2 0.09 / 0.93, S2 0.45 / 2.0 (all PASS)',
                results_D210='run current_d210 (167 k elements, 0.81 M unknowns): every point under 1 in every case; cup peak F2 4.4 / 9.3, S2 18.0 / 20, S3 13.6; cup 99th percentile F2 0.98, S2 4.2; bond mean 0.07 / 0.35')


def main():
    dyn =json.load(open(os.path.join(k.OUT, 'linkage_dynamics.json')))
    kin = json.load(open(os.path.join(k.OUT, 'linkage_kinematics.json')))
    f_hold = dyn['rod']['hold_force_max_N']
    fs, at_deg, la = stall_force()
    out = {'inputs': dict(F_hold_N=f_hold, F_stall_N=fs, F_stall_at_delta_deg=at_deg, min_arm_lever_ratio=la, tau_stall_Nm=TAU_STALL,
                          dynamic_step_peak_N_not_used=dyn['rod']['peak_compression_N'], hinge_vd_Nm=HINGE_NM, KP=KP, K_stall_printed=K_STALL_PRINTED,
                          arm_joint_state=k.STATE)}
    out['z_bend_leg'] = rod_leg(f_hold, fs)
    out['keeper_bridge_MEC008'] = keeper_bridge(f_hold, fs, out['z_bend_leg']['e_hi_mm'] * MM)
    out['stall_8p4V_informational'] = stall_84(stall_force_at(TAU_STALL_84)[0], out['z_bend_leg'])
    out['servo_speed_torque_T056'] = servo_speed()
    out['motor_mount_evidence_D209'] = motor_mount_evidence()
    out['horn_blade'] = blade(f_hold, fs)
    out['horn_rib_foam'] = rib_foam(f_hold, fs)
    out['elevon_torsion_foam_only'] = elevon_torsion(fs)
    out['horn_rib_vs_elevon_body_hold'] = out['horn_rib_foam']['hold']['factored_kPa_max'] / out['elevon_torsion_foam_only']['hold']['factored_kPa']
    fp = kin['free_play_budget_deg']
    out['free_play'] = dict(total_known_deg=fp['total_known_deg'], guide_deg=1.0, ok=bool(fp['total_known_deg'] <= 1.0), parts=fp,
                            basis='FLUTTER basis (review r3 m-7): the 1 deg guide is the SERVO.md s4 flutter limit, kept as the claim limit because it is the only sourced number (a control-precision limit has none). Not in the budget: servo gear backlash ("-") and the clevis cheek holes ("-"): measure the BUILT value at BUILD D5b / E1 and compare it with 1 deg.',
                            mitigation='hinge viscous damper: flutter has no instability for any K 0.01-20 N m/rad (FIXES2 s1, CL-A-FLUTTER-ELEVON-*), preload strips remove low-amplitude slack; E1 bench measurement')
    out['pass'] = dict(rod_leg_music_wire_recalled=out['z_bend_leg']['music_wire_ok_recalled'],
                       blade_root_hold=out['horn_blade']['hold']['root_ok'], blade_root_stall=out['horn_blade']['stall']['root_ok'],
                       hole_bearing_hold=out['horn_blade']['hold']['bearing_ok'], hole_bearing_stall=out['horn_blade']['stall']['bearing_ok'],
                       rib_foam_hold=out['horn_rib_foam']['hold']['ok'], rib_foam_stall=out['horn_rib_foam']['stall']['ok'],
                       elevon_torsion_foam_hold=out['elevon_torsion_foam_only']['hold']['ok'], elevon_torsion_foam_stall=out['elevon_torsion_foam_only']['stall']['ok'],
                       free_play_le_1deg=out['free_play']['ok'],
                       keeper_bridge_hold=out['keeper_bridge_MEC008']['hold']['ok'], keeper_bridge_stall=out['keeper_bridge_MEC008']['stall']['ok'],
                       servo_speed_margin_ge_1=out['servo_speed_torque_T056']['ok'])
    out['git_head'] = k.git_head()
    with open(os.path.join(k.OUT, 'linkage_loads_check.json'), 'w') as f:
        json.dump(out, f, indent=1)
    show = {kk: out[kk] for kk in ('inputs', 'pass', 'horn_rib_vs_elevon_body_hold')}
    show['rod_leg'] = {kk: out['z_bend_leg'][kk] for kk in ('hold', 'stall', 'required_yield_MPa_governing', 'collapse_Fc_N_at_required_yield')}
    show['blade'] = {kk: out['horn_blade'][kk] for kk in ('governing_width_mm', 'governing_lever_mm', 'hold', 'stall')}
    show['rib'] = {kk: out['horn_rib_foam'][kk] for kk in ('hold', 'stall', 'sweep')}
    show['elevon'] = {kk: out['elevon_torsion_foam_only'][kk] for kk in ('J_mm4', 'hold', 'stall')}
    show['free_play'] = out['free_play']['total_known_deg']
    show['rod_receipt_test'] = {kk: out['z_bend_leg'][kk] for kk in ('e_lo_mm', 'e_hi_mm', 'receipt_test_load_N')}
    show['keeper_bridge_MEC008'] = {kk: out['keeper_bridge_MEC008'][kk] for kk in ('a_mm', 'hold', 'stall')}
    show['stall_8p4V_informational'] = out['stall_8p4V_informational']
    show['servo_speed_T056'] = {kk: out['servo_speed_torque_T056'][kk] for kk in ('gearing_at_end_points_max', 'required_elevon_rate_deg_s', 'cases', 'ok')}
    print(json.dumps(show, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
