"""T-101 U-A hand derivation: elevon reserve beyond the pitch peak (roll + gust + combination), concept A, 17 m/s cruise.
Reads sitl/a_aero.py (by import), sitl/cad_mass.json, params-A.json, A.param. Stdlib + numpy.
Run: python -I redesign/qp/A/mechanism/out/T101_data/reserve/reserve_hand.py   -> reserve_hand.json, reserve_hand.txt (same folder).
Every EST is labelled. The SITL unit (C3G) overrides this hand estimate."""
import os, sys, json, math
import numpy as np                                                           # noqa: F401  (kept for the gust grid below)
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))               # redesign/qp/A
sys.path.insert(0, os.path.join(A, 'sitl'))
import a_aero as AE                                                          # noqa: E402  (plant constants, read at run time)
CADM = json.load(open(os.path.join(A, 'sitl', 'cad_mass.json')))
PAR = json.load(open(os.path.join(A, 'params-A.json'), encoding='utf-8'))
PRM = {}
for ln in open(os.path.join(A, 'A.param'), encoding='utf-8'):
    ln = ln.strip()
    if ln and not ln.startswith('#') and ',' in ln:
        k, v = ln.split(',', 1)
        try:
            PRM[k.strip()] = float(v.split('#')[0].strip())
        except ValueError:
            pass

D2R = math.pi / 180
V = PRM['AIRSPEED_CRUISE']                                                   # 17 m/s
RHO, S, B, C = AE.RHO, AE.S_W, AE.B_W, AE.C_W
q = 0.5 * RHO * V * V
CLA, CLD, CLP, CLB, CMQ, SM = AE.CLA, AE.CLD, AE.CLP, AE.CLB, AE.CMQ, AE.SM
XE, YE, EL_MAX_DEG = abs(AE.EL_X), AE.EL_Y, math.degrees(AE.EL_MAX)
# predicted mass = basic x growth + overrun x gate (AR-018 Inputs: 1.64198 x 1.1174 + 0.032 x 1.47)
MP = PAR['mass']
M = CADM['mass_basic_kg'] * MP['growth_factor']['value'] + MP['overrun_frac']['value'] * PAR['req']['mass_gate_kg']['value']
K = M / CADM['mass_basic_kg']                                                # a_plant.py line 67: I scaled by M / mass_basic
IC = CADM['I_cad_axes_kgm2']
IX, IY, IZ = IC['Ixx'] * K, IC['Iyy'] * K, IC['Izz'] * K
ROLL_AXIS = ('body x (nose / chord axis in cruise, a_aero.py header l.2); I_roll = Ixx = %.4f kg m2 = cad_mass.json I_cad_axes.Ixx %.4f x M/mass_basic %.4f '
             '(a_plant.py l.66-68: I = (Ixx, Iyy, Izz) x M/basic, "diagonal terms are the same in body axes"); pitch axis Iyy %.4f, yaw Izz %.4f' % (IX, IC['Ixx'], K, IY, IZ))
PITCH_PEAK = 9.76                                                            # deg, worst mean elevon, T-074 + Lua C3 (0.651 of 15 deg; D-251 / AR-017 C3)
out = dict(inputs=dict(V=V, q_Pa=q, M_kg=M, mass_scale=K, Ixx=IX, Iyy=IY, Izz=IZ, CLA=CLA, CLD=CLD, CLP=CLP, CLB=CLB, CMQ=CMQ, SM=SM, x_e_m=XE, y_e_m=YE,
                      EL_CF=AE.EL_CF, stop_deg=EL_MAX_DEG, pitch_peak_deg=PITCH_PEAK))
out['roll_axis'] = ROLL_AXIS

# ---------------------------------------------------------------- A. roll
CLDEL = YE * CLD / B                                                         # Cl per rad of antisymmetric deflection (a_aero l.104-107: each Fz = -qS CLD d 0.5, Mx = EL_Y (FzR - FzL))
KP_SS = (CLDEL / abs(CLP)) * (2 * V / B)                                     # steady p per rad of differential deflection (rad/s per rad = deg/s per deg)
LP = q * S * B * B * abs(CLP) / (2 * V)                                      # roll damping moment per rad/s, N m s/rad
TAU = IX / LP                                                                # roll-subsidence time constant, s
out['roll'] = dict(Cl_delta_per_rad=CLDEL, p_degs_per_deg_diff=KP_SS, L_p_Nms=LP, tau_s=TAU, p_max_at_stop_degs=KP_SS * EL_MAX_DEG)


def pss_for_bank(phi_deg, t):
    """p = pss (1 - exp(-t/tau)); phi = pss [t - tau (1 - exp(-t/tau))] -> pss (rad/s) for bank phi at time t."""
    return phi_deg * D2R / (t - TAU * (1 - math.exp(-t / TAU)))


B_REF, V_REF = 10.0, 40.0                                                    # EST reference Class I airplane (light airplane; no source): b/V = 0.25 s
BV_UAV, BV_REF = B / V, B_REF / V_REF
crit = []
p90 = PAR['req']['roll_min_degs']['value']
crit.append(dict(name='A-P11 steady 90 deg/s', bank_deg=None, time_s=None, p_ss_req_degs=p90, pb2V=p90 * D2R * B / (2 * V),
                 delta_roll_deg=p90 / KP_SS, note='req.roll_min_degs; D-195 SITL 106.9 / 106.4 deg/s'))


def add(name, phi, t, note, scaled=False):
    ts = t * BV_UAV / BV_REF if scaled else t
    pss = pss_for_bank(phi, ts)
    crit.append(dict(name=name, bank_deg=phi, time_s=ts, p_avg_degs=phi / ts, p_ss_req_degs=math.degrees(pss), pb2V=pss * B / (2 * V),
                     delta_roll_deg=math.degrees(pss) / KP_SS, note=note))


for nm, phi, t, note in (('MIL-F-8785C Cl I L1 Cat A 60 deg 1.3 s', 60, 1.3, 'Table IXa; angle/column alignment ambiguous (scout a1)'),
                         ('MIL-F-8785C Cl I L1 Cat A 45 deg 1.3 s', 45, 1.3, 'same, 45 deg reading'),
                         ('MIL-F-8785C Cl I L1 Cat B 60 deg 1.7 s', 60, 1.7, 'Cat B, 60 deg reading'),
                         ('MIL-F-8785C Cl I L2 Cat B 60 deg 2.5 s', 60, 2.5, 'Level 2'),
                         ('MIL-F-8785C Cl I L1 Cat C 30 deg 1.3 s', 30, 1.3, 'takeoff / landing category'),
                         ('FAR 23.157 30 to 30 deg in 4 s (landing)', 60, 4.0, 'EST: modelled as 60 deg from rest, reversal lag neglected (kitplanes, scout a3)'),
                         ('FAR 23.157 30 to 30 deg in 5 s (takeoff)', 60, 5.0, 'same')):
    add(nm, phi, t, note)
for nm, phi, t in (('MIL Cl I L1 Cat A 60 deg 1.3 s, b/V scaled', 60, 1.3), ('MIL Cl I L1 Cat B 60 deg 1.7 s, b/V scaled', 60, 1.7),
                   ('MIL Cl I L2 Cat B 60 deg 2.5 s, b/V scaled', 60, 2.5)):
    add(nm, phi, t, 'EST: time x (b/V)_uav / (b/V)_ref; ref b 10 m, V 40 m/s (no source)', scaled=True)
for c in crit:
    c['within_stop'] = bool(c['delta_roll_deg'] <= EL_MAX_DEG)
    c['within_mixer_cap'] = bool(c['delta_roll_deg'] <= PRM['MIXING_GAIN'] * EL_MAX_DEG)
out['roll_criteria'] = crit
GOV_P = p90                                                                  # governing: A-P11 (Part 1 A.ii)
d_roll = GOV_P / KP_SS
out['roll_governing_degs'] = GOV_P
out['delta_roll_deg'] = d_roll
out['roll_time_to_90pct_s'] = TAU * math.log(10)
out['roll_plant_check'] = dict(mixer_cap_single_axis_deg=PRM['MIXING_GAIN'] * EL_MAX_DEG, p_at_mixer_cap_degs=KP_SS * PRM['MIXING_GAIN'] * EL_MAX_DEG,
                               implied_delta_for_106p9_deg=106.9 / KP_SS, sitl_roll_141_degs=PAR['sim']['roll_141_degs']['value'],
                               sitl_roll_150_degs=PAR['sim']['roll_150_degs']['value'])

# ---------------------------------------------------------------- B. gust (vertical; theta, gamma, q linear model with a PD elevon loop, EST)
GUST_MEAN, GUST_MAX = 5.0, 8.0                                               # SCHEDULE-A line 12
W_G = GUST_MAX - GUST_MEAN                                                   # 3 m/s gust increment above the mean (scout O-G1)
SIG_W = {'light 15 kt W20': 0.1 * 15 * 0.514444, 'moderate 30 kt W20': 0.1 * 30 * 0.514444, 'RFS limit W20 = 8 m/s': 0.1 * 8.0}   # sigma_w = 0.1 W20
STATIC_PER_MS = math.degrees(C * CLA * SM * (1.0 / V) / (XE * CLD))          # deg of elevon per m/s of vertical gust, rigid attitude hold
out['gust'] = dict(w_gust_ms=W_G, sigma_w_ms=SIG_W, dryden_3sigma_RFS_ms=3 * SIG_W['RFS limit W20 = 8 m/s'], static_deg_per_ms=STATIC_PER_MS,
                   static_deg_at_w=STATIC_PER_MS * W_G)
MDEL = q * S * C * (CLD * XE / C) / IY                                       # pitch accel per rad of elevon (TE down = nose down), 1/s2
MALF = q * S * C * CLA * SM / IY                                             # static stiffness, 1/s2 (nose-down per rad of local alpha)
MQ = q * S * C * abs(CMQ) * (C / (2 * V)) / IY                               # pitch damping, 1/s
ZA = q * S * CLA / (M * V)                                                   # flight-path turning per rad alpha, 1/s
WN_LOOP = 2 * math.pi * 2.2                                                  # rad/s, rate-loop crossover 2.2 Hz (AR-002 / CLAIMS-FIX, EST)
KQ = WN_LOOP / MDEL                                                          # elevon per unit pitch rate
KTH = WN_LOOP / 4.0                                                          # attitude loop 1/4 of the rate loop, 1/s (EST)
out['gust'].update(short_period_wn_rad_s_open_loop=math.sqrt(MALF), M_delta=MDEL, M_alpha=MALF, M_q=MQ, Z_alpha=ZA, Kq=KQ, Kth=KTH)


def gust_run(wg, T, ctrl=True, dt=1e-3):
    """theta, gamma, q: alpha_loc = theta - gamma + w(t)/V; gamma' = Za alpha_loc; q' = -Malf alpha_loc - Mq q - Mdel delta;
    delta = Kq (q + Kth theta) clipped at the stop (TE down +). Returns peak |delta| deg. 1-cos vertical gust of length T."""
    th = ga = qq = 0.0
    pk = 0.0
    for i in range(int((T + 4.0) / dt)):
        t = i * dt
        w = wg * 0.5 * (1 - math.cos(2 * math.pi * t / T)) if t <= T else 0.0
        al = th - ga + w / V
        dl = KQ * (qq + KTH * th) if ctrl else 0.0
        dl = max(-AE.EL_MAX, min(AE.EL_MAX, dl))
        qd = -MALF * al - MQ * qq - MDEL * dl
        ga += dt * ZA * al
        th += dt * qq
        qq += dt * qd
        pk = max(pk, abs(dl))
    return math.degrees(pk)


TS = (0.5, 1.0, 2.0, 3.0, 4.0, 6.0)
rows3 = [dict(T_s=T, peak_delta_deg=gust_run(W_G, T)) for T in TS]
rows1 = [dict(T_s=T, peak_delta_deg=gust_run(1.0, T)) for T in TS]
T_CHOSEN = 2 * 9.144 / V                                                     # 1-cos length T = 2H / V with H = 30 ft = 9.144 m (14 CFR 25.341 minimum gradient, form only): 1.08 s
out['gust'].update(dyn_peak_vs_T_w3=rows3, dyn_peak_vs_T_w1=rows1, T_s_chosen=T_CHOSEN, dyn_peak_deg_w3=gust_run(W_G, T_CHOSEN), dyn_peak_deg_w1=gust_run(1.0, T_CHOSEN),
                   dyn_worst_over_T_w3=max(r['peak_delta_deg'] for r in rows3), dyn_worst_over_T_w1=max(r['peak_delta_deg'] for r in rows1),
                   uncontrolled_delta0_note='delta = 0 run not used: the airframe alone returns to trim with the SM 7.6 % stiffness')
d_dyn1 = out['gust']['dyn_peak_deg_w1']
LAT3 = math.degrees(abs(CLB) * (W_G / V) / CLDEL)                            # side gust v_g: beta = v_g / V, Cl = CLB beta, antisymmetric elevon holds wings level (static)
LAT1 = math.degrees(abs(CLB) * (1.0 / V) / CLDEL)
out['gust'].update(lateral_deg_w3_static=LAT3, lateral_deg_w1_static=LAT1)
DELTA_G = out['gust']['dyn_peak_deg_w3']                                     # carried: PD-loop peak at T_CHOSEN (EST gains); the sweep max (T 0.5 s, H 4 m < FAR minimum) and the static hold are bounds
out['w_gust_ms'] = W_G
out['delta_gust_deg'] = DELTA_G

# ---------------------------------------------------------------- C. combination on the ArduPilot linear mixer
G = PRM['MIXING_GAIN']


def pwm_to_deg(pwm):
    return (pwm - 1500.0) / 500.0 * EL_MAX_DEG                              # a_plant.py l.45 (ES5/6 +-1, ELV_SCALE 1.0): 1000..2000 us = +-20 deg
s5 = (pwm_to_deg(PRM['SERVO5_MIN']), pwm_to_deg(PRM['SERVO5_MAX']))
s6 = (pwm_to_deg(PRM['SERVO6_MIN']), pwm_to_deg(PRM['SERVO6_MAX']))
PWM_LIM = min(abs(x) for x in s5 + s6)
out['mixer'] = dict(MIXING_GAIN=G, single_axis_cap_deg=G * EL_MAX_DEG, saturates_when_r_plus_p_above=1 / G, servo5_deg=s5, servo6_deg=s6, pwm_limit_deg=PWM_LIM,
                    pitch_cmd_fraction_at_peak=PITCH_PEAK / (G * EL_MAX_DEG), roll_cmd_fraction_at_governing=d_roll / (G * EL_MAX_DEG), stops_deg=EL_MAX_DEG,
                    note='surface = G (roll +- pitch) x 500 us; a full single-axis command gives G x 20 = 13 deg; the PWM limit (SERVO5/6 MIN/MAX) clips before the 20 deg stop')


def comb_row(name, p_deg_s, dg=None, lat=None):
    dg = DELTA_G if dg is None else dg
    lat = LAT3 if lat is None else lat
    dr = p_deg_s / KP_SS
    tot = PITCH_PEAK + dg + dr + lat
    return dict(case=name, roll_degs=p_deg_s, delta_roll_deg=dr, pitch_deg=PITCH_PEAK, gust_deg=dg, lateral_deg=lat, combined_deg=tot,
                margin_vs_stop_deg=EL_MAX_DEG - tot, margin_vs_pwm_deg=PWM_LIM - tot, ok=bool(tot <= EL_MAX_DEG))


rows = [comb_row('A-P11 90 deg/s + vertical gust 3 m/s (dyn) + side gust 3 m/s', GOV_P),
        comb_row('A-P11 + vertical gust 3 m/s (dyn), no side gust', GOV_P, lat=0.0),
        comb_row('A-P11 + vertical gust 3 m/s static-hold bound + side gust', GOV_P, dg=out['gust']['static_deg_at_w']),
        comb_row('A-P11 + gust 1 m/s (dyn) + side gust 1 m/s', GOV_P, dg=d_dyn1, lat=LAT1),
        comb_row('pitch + vertical gust 3 m/s only (no roll)', 0.0, lat=0.0),
        comb_row('pitch + roll 90 only (no gust)', GOV_P, dg=0.0, lat=0.0)]
for c in crit[1:]:
    if c['delta_roll_deg'] < 60:
        rows.append(comb_row(c['name'] + ' + gust 3 m/s dyn + side', c['p_ss_req_degs']))
out['combos'] = rows
out['combined_deg'] = rows[0]['combined_deg']
out['margin_deg'] = rows[0]['margin_vs_stop_deg']
out['margin_pwm_deg'] = rows[0]['margin_vs_pwm_deg']
out['yes_no'] = 'YES' if rows[0]['ok'] else 'NO'
out['reserve_after_pitch_peak_deg'] = EL_MAX_DEG - PITCH_PEAK
rem = EL_MAX_DEG - PITCH_PEAK - DELTA_G - LAT3
out['roll_that_fits_degs_with_gust_dyn_lat'] = max(rem, 0.0) * KP_SS
out['gust_ms_that_fits_with_90_dyn_per_ms'] = None
out['gust_ms_that_fits_with_90_static'] = (EL_MAX_DEG - PITCH_PEAK - d_roll) / STATIC_PER_MS
json.dump(out, open(os.path.join(HERE, 'reserve_hand.json'), 'w'), indent=1, default=float)

L = []
P = L.append
P('T-101 reserve hand derivation (reserve_hand.py)')
P('V %.1f m/s q %.1f Pa M %.4f kg; Ixx (roll) %.4f Iyy %.4f Izz %.4f kg m2' % (V, q, M, IX, IY, IZ))
P('roll axis: ' + ROLL_AXIS)
P('CLA %.3f CLD %.4f SM %.4f x_e %.4f y_e %.4f Clp %.2f CLB %.3f CMQ %.2f' % (CLA, CLD, SM, XE, YE, CLP, CLB, CMQ))
P('Cl_delta %.4f /rad; steady p %.3f deg/s per deg diff; L_p %.4f N m s/rad; tau %.3f s; p at 20 deg %.0f, at mixer cap %.0f deg/s' % (CLDEL, KP_SS, LP, TAU, KP_SS * 20, KP_SS * G * 20))
P('roll criteria: name | bank | t s | p_ss req deg/s | pb/2V | delta deg | within 20 | within mixer cap')
for c in crit:
    P('  %-46s %5s %5s %8.1f %.4f %7.1f %s %s' % (c['name'], c['bank_deg'], ('%.2f' % c['time_s']) if c['time_s'] else '-', c['p_ss_req_degs'], c['pb2V'], c['delta_roll_deg'], c['within_stop'], c['within_mixer_cap']))
P('governing roll %.0f deg/s -> delta_roll %.2f deg; time to 90 %% of steady %.2f s' % (GOV_P, d_roll, TAU * math.log(10)))
P('plant check: ' + json.dumps(out['roll_plant_check']))
P('gust w %.1f m/s (8 - 5); sigma_w %s; Dryden 3 sigma at W20 = 8 m/s %.2f' % (W_G, {k: round(v, 2) for k, v in SIG_W.items()}, out['gust']['dryden_3sigma_RFS_ms']))
P('gust static %.2f deg per m/s -> %.1f deg at w; dyn peak T %.1f s: %.2f deg (1 m/s %.2f); worst over T %.2f deg (1 m/s %.2f); lateral static %.2f deg (1 m/s %.2f)' % (
    STATIC_PER_MS, STATIC_PER_MS * W_G, T_CHOSEN, out['gust']['dyn_peak_deg_w3'], out['gust']['dyn_peak_deg_w1'], DELTA_G, d_dyn1, LAT3, LAT1))
P('dyn peak vs T (w 3): ' + ', '.join('%.1fs %.2f' % (r['T_s'], r['peak_delta_deg']) for r in rows3))
P('dyn peak vs T (w 1): ' + ', '.join('%.1fs %.2f' % (r['T_s'], r['peak_delta_deg']) for r in rows1))
P('M_delta %.1f 1/s2, M_alpha %.1f 1/s2 (wn %.2f rad/s), M_q %.2f 1/s, Z_alpha %.3f 1/s, Kq %.3f, Kth %.2f 1/s' % (MDEL, MALF, math.sqrt(MALF), MQ, ZA, KQ, KTH))
P('mixer: ' + json.dumps(out['mixer']))
P('combination rows: case | roll deg/s | d_roll | pitch | gust | lateral | total | margin(20) | margin(pwm) | ok')
for r in rows:
    P('  %-62s %6.1f %6.2f %5.2f %6.2f %5.2f %6.2f %6.2f %6.2f %s' % (r['case'], r['roll_degs'], r['delta_roll_deg'], r['pitch_deg'], r['gust_deg'], r['lateral_deg'], r['combined_deg'], r['margin_vs_stop_deg'], r['margin_vs_pwm_deg'], r['ok']))
P('RESULT %s: combined %.2f deg vs stop %.0f deg, margin %.2f deg (pwm %.2f); roll that fits with gust+side %.0f deg/s; gust that fits with 90 deg/s (static) %.2f m/s' % (
    out['yes_no'], out['combined_deg'], EL_MAX_DEG, out['margin_deg'], out['margin_pwm_deg'], out['roll_that_fits_degs_with_gust_dyn_lat'], out['gust_ms_that_fits_with_90_static']))
open(os.path.join(HERE, 'reserve_hand.txt'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
