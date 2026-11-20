"""T-076c step 1 (hub escalation s3.4 item 1, D-220): demand fix.  python -I t076c_step1_demand.py   (cwd anywhere; ~1-2 min)
CATEGORY: rigid-body dynamics (the same landing_a.py point-mass touchdown model T-071b used, 21 cases, D2 pad, 30 N plateau, dt 0.2 ms) + HAND CALCULATION (bearing, net section).  No FEA.
Mass 1.64 kg (LAND_MASS_KG set here; landing_centre_a.py / landing_a.py defaults are NOT changed, no existing file is edited).
Output: hub-side wrench with ALL SIX components, per case, at (a) the original bore mouth P0 and (b) the mid-length of each hub variant's bore; bending rows with |(My, Mz)| and V = |(Fy, Fz)|;
the block net-section row (audit V4) per variant; reproduction of the escalation audit V3 / V4 numbers.  Frames: body x aft, y span, z up (hub frame = body x - HUB_x).
Traces (large) -> T076_data/fea/t076c_demand_m164.npz (git-ignored); results -> T076c_data/step1_demand.json and step1_demand_stdout.txt.
"""
import os, sys, json, math, time
os.environ['LAND_MASS_KG'] = '1.64'
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures')); sys.path.insert(0, S)
sys.dont_write_bytecode = True
import numpy as np
import landing_path_a as P
import landing_a as L
import landing_centre_a as LC
W, C = LC.W, LC.C
KF, KP = LC.KF, LC.KP
FEA = os.path.abspath(os.path.join(HERE, '..', 'T076_data', 'fea')); os.makedirs(FEA, exist_ok=True)
NPZ = os.path.join(FEA, 't076c_demand_m164.npz')
HUBX = C.HUB[0]                                      # body x of the hub frame origin (m)
P0 = np.array([W.HUB_X1, 0.0, W.BR_Z])               # original bore mouth, body frame (hub frame x 24.0 mm)
D_BR = W.BR_OD*1e3                                   # 16 mm
PETG_BEAR = 20.0                                     # MPa, EST (fea_arm.ALLOW petg; landing_centre_a PETG_BEAR)
ALLOW_P = PETG_BEAR/KP                               # 9.276 MPa
HUB_ID = (2, 3, 4, 6)                                # ITEMS: motors, arms, hub, pack (landing_centre_a base partition)


def make():
    P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot'])
    d, names, meta = {}, [], {}
    for name, kw in P.cases(False):
        r = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **P.PAD_D2))
        FB = r['trace'].reshape(-1, 4, 3)
        w = LC.wrench_split(FB, HUB_ID)['hub']
        names.append(name); d['FB|'+name] = FB.astype(np.float32); d['F|'+name] = w[0].astype(np.float64); d['M|'+name] = w[1].astype(np.float64)
        meta[name] = dict(dmax_mm=[float(x) for x in r['dmax_mm']], set_mm=[float(x) for x in r['sp_mm']], Fmax_N=[float(x) for x in r['F']], side_N=float(r['side'].max()), n_peak=float(r['n_peak']),
                          stroke_max_mm=float(r['dmax_mm'].max()), bottoming=bool(r['dmax_mm'].max() > 20.0), tilt_end=float(r['tilt_end']),
                          foot_Fx_peak_N=[float(np.abs(FB[:, i, 0]).max()) for i in range(4)])
        print('  %-30s stroke %.1f mm  n %.2f  Fmax %.1f' % (name, r['dmax_mm'].max(), r['n_peak'], r['F'].max()), flush=True)
    d['names'] = np.array(names)
    np.savez_compressed(NPZ, **d)
    json.dump(meta, open(os.path.join(HERE, 'step1_pad_stroke.json'), 'w'), indent=1)
    return d, meta


def wrench_about(F, M, pt):
    """moment of the wrench (F, M about P0) taken about the point pt (body frame, m)."""
    return M+np.cross(np.broadcast_to(P0-np.asarray(pt, float), F.shape), F)


def mid_point(x_floor_mm, x_mouth_mm):
    return np.array([HUBX+0.5*(x_floor_mm+x_mouth_mm)*1e-3, 0.0, W.BR_Z])


def bearing_rf(Fv, Mv, x_floor, x_mouth, daf=1.0):
    """audit V3: p = KP (6 M_b/(D L^2) + V/(D L)), M_b = |(My, Mz)| about the bore mid-length, V = |(Fy, Fz)|, PETG 20 MPa EST.  Min RF over cases and time steps."""
    Lb = x_mouth-x_floor; mid = mid_point(x_floor, x_mouth); best = 1e9; arg = None
    for nm in Fv:
        M = wrench_about(Fv[nm], Mv[nm], mid)*1e3                      # N mm
        Mb = np.hypot(M[:, 1], M[:, 2])*daf; V = np.hypot(Fv[nm][:, 1], Fv[nm][:, 2])*daf
        p = KP*(6*Mb/(D_BR*Lb**2)+V/(D_BR*Lb)); rf = (PETG_BEAR/p).min()
        if rf < best: best, arg = float(rf), nm
    return best, arg


def req_length(Fv, Mv, x_mouth_fixed_or_none, daf, mid_fn=None):
    """bore length for bearing RF 1.0 with the mouth fixed at hub x 24 and the floor moving (as T-071b), mid-length moment."""
    lo, hi = 5.0, 200.0
    for _ in range(50):
        mid = 0.5*(lo+hi)
        rf, _ = bearing_rf(Fv, Mv, 24.0-mid, 24.0, daf)
        if rf >= 1.0: hi = mid
        else: lo = mid
    return hi


def main():
    np.seterr(all='ignore'); t0 = time.time()
    if os.path.exists(NPZ) and '--recompute' not in sys.argv:
        z = np.load(NPZ); d = {k: z[k] for k in z.files}; meta = json.load(open(os.path.join(HERE, 'step1_pad_stroke.json')))
        print('(cached traces)')
    else:
        d, meta = make()
    names = [str(n) for n in d['names']]
    Fv = {n: d['F|'+n] for n in names}; Mv = {n: d['M|'+n] for n in names}
    print('# T-076c step 1: hub-side wrench, all six components, mass 1.64 kg (LAND_MASS_KG), D2 pad, 21 cases.  Category: rigid-body dynamics (+ hand calc).  Limit load, rigid-body demand RB.')
    print('# wrench = force of the centre on the hub side (motors, arms, hub, pack: ITEMS 2, 3, 4, 6), moments about the original bore mouth P0 (hub-frame x 24.0 mm, z %.1f mm) unless stated.' % (W.BR_Z*1e3))
    out = dict(mass_kg=1.64, per_case_P0={}, per_case_mid={}, variants={}, repro={})
    variants = [('as drawn (L 9)', 15.0, 24.0), ('V1 (L 21)', 15.0, 36.0), ('C6 (L 22.5)', 13.5, 36.0), ('V2 (L 28.5)', 13.5, 42.0), ('H-A1 / H-A2 (L 30)', 15.0, 45.0)]
    midH = mid_point(15.0, 45.0)
    print('\n## 1. Peak |component| per case (limit load) at P0 and at the H-A1 bore mid-length (hub-frame x 30.0 mm)')
    print('| case | Fx | Fy | Fz | Mx | My | Mz  (N, N m) at P0 | Mx | My | Mz at H-A1 mid-length | governing |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    gl = {k: 0.0 for k in ('Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz')}; gl_case = {}
    for n in names:
        a = np.abs(np.hstack([Fv[n], Mv[n]])).max(0); Mm = wrench_about(Fv[n], Mv[n], midH); b = np.abs(Mm).max(0)
        out['per_case_P0'][n] = dict(zip(('Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz'), [float(x) for x in a])); out['per_case_mid'][n] = dict(zip(('Mx', 'My', 'Mz'), [float(x) for x in b]))
        for k, v in zip(gl, a):
            if v > gl[k]: gl[k] = float(v); gl_case[k] = n
        print('| %s | %.1f | %.1f | %.1f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %s |' % (n, *a, *b, 'Mz' if a[5] >= max(a[3], a[4]) else ('My' if a[4] >= a[3] else 'Mx')))
    print('GLOBAL peak at P0: ' + ', '.join('%s %.2f (%s)' % (k, gl[k], gl_case[k]) for k in gl))
    out['global_P0'] = dict(gl); out['global_P0_case'] = gl_case
    # time-coincident governing combo
    best = (0, None, None)
    for n in names:
        mz = np.abs(Mv[n][:, 2]); j = int(mz.argmax())
        if mz[j] > best[0]: best = (float(mz[j]), n, j)
    j = best[2]; n = best[1]
    print('Governing Mz sample: %s step %d: F = (%.1f, %.1f, %.1f) N, M = (%.2f, %.2f, %.2f) N m at P0 (audit V1: combo "hard 10 wide + drift .5 y"@342: F (-53.7, -28.9, 2.1), M (-0.07, 0.12, 17.51))' % (n, j, *Fv[n][j], *Mv[n][j]))
    out['governing_Mz'] = dict(case=n, step=j, F=Fv[n][j].tolist(), M=Mv[n][j].tolist())
    nm70 = sum(1 for n in names if np.abs(Mv[n][:, 2]).max() > 6.05)
    print('Cases with |Mz| > 6.05 N m (T-071b design moment): %d of %d' % (nm70, len(names)))
    print('\n## 2. Bending rows: p = KP (6 M_b/(D L^2) + V/(D L)), M_b = |(My, Mz)| about the bore mid-length, V = |(Fy, Fz)|, D 16 mm, PETG bearing 20 MPa EST, KP %.3f (min over 21 cases and all time steps)' % KP)
    print('| variant | L mm | RF at RB | RF at RBx1.5 | RF at RBx2 | governing case | My-only control (T-071b method: |My| at the mouth, V = Fz) RB |')
    print('|---|---|---|---|---|---|---|')
    for lab, xf, xm in variants:
        r1, c1 = bearing_rf(Fv, Mv, xf, xm, 1.0); r15, _ = bearing_rf(Fv, Mv, xf, xm, 1.5); r2, _ = bearing_rf(Fv, Mv, xf, xm, 2.0)
        # My-only control: M = |My| at the variant mouth, V = |Fz|
        Lb = xm-xf; mp = np.array([HUBX+xm*1e-3, 0.0, W.BR_Z]); cm = 1e9
        for n in names:
            M = wrench_about(Fv[n], Mv[n], mp)*1e3; p = KP*(6*np.abs(M[:, 1])/(D_BR*Lb**2)+np.abs(Fv[n][:, 2])/(D_BR*Lb)); cm = min(cm, float((PETG_BEAR/p).min()))
        out['variants'][lab] = dict(L=Lb, RF_RB=r1, RF_x1p5=r15, RF_x2=r2, case=c1, RF_My_only_RB=cm)
        print('| %s | %.1f | %.2f | %.2f | %.2f | %s | %.2f |' % (lab, Lb, r1, r15, r2, c1, cm))
    for lab, daf in (('RB', 1.0), ('RBx1.5', 1.5), ('RBx2', 2.0)):
        Lr = req_length(Fv, Mv, None, daf); out['repro'][f'L_req_{lab}'] = Lr
    print('Bore length for bearing RF 1.0 (mouth fixed at hub x 24, floor moved): RB %.1f mm, RBx1.5 %.1f mm, RBx2 %.1f mm (audit V3: 26.6 RB, 32.6 x1.5)' % (out['repro']['L_req_RB'], out['repro']['L_req_RBx1.5'], out['repro']['L_req_RBx2']))
    print('\n## 3. Block net-section row (audit V4): the full Mz crosses the printed block between the bore floor and the arm sleeves; mean bending stress, no holes or fillets (upper bound on capacity)')
    mzmax = max(np.abs(wrench_about(Fv[n], Mv[n], P0)[:, 2]).max() for n in names)      # = at P0
    zblk = 20.0*20.0**2/6.0                                                               # mm3, 20 (y) x 20 (z) solid, bending about z (y-width 20 governs)
    cap = ALLOW_P*zblk/1e3                                                                # N m
    print('Block 20 (y) x 20 (z), Z = 20 x 20^2/6 = %.0f mm3; PETG in-layer allowable 20 MPa EST / KP %.3f = %.3f MPa; capacity %.2f N m (audit V4: 12.4)' % (zblk, KP, ALLOW_P, cap))
    print('Mz max at P0 %.2f N m (RB): hand RF %.2f at RB, %.2f at x1.5, %.2f at x2   (audit V4: 0.71)' % (mzmax, cap/mzmax, cap/(1.5*mzmax), cap/(2*mzmax)))
    wid = {lab: math.sqrt(daf*mzmax*1e3*6/(ALLOW_P*20.0)) for lab, daf in (('RB', 1.0), ('x1.5', 1.5), ('x2', 2.0), ('x3', 3.0))}
    print('Block width (y) needed for RF 1.0 at 20 mm depth: ' + ', '.join('%s %.1f mm' % (k, v) for k, v in wid.items()) + '   (audit V4: 23.8 RB, 29.1 x1.5, 33.6 x2)')
    zw = 20.0*27.0**2/6.0;   # 27 mm in y (bending about z), 20 mm in z
    print('Widest PETG block the raceway notches allow (27 mm, solid): capacity %.2f N m, RF %.2f RB / %.2f x1.5 (audit s2.2: 1.29 / 0.86)' % (ALLOW_P*zw/1e3, ALLOW_P*zw/1e3/mzmax, ALLOW_P*zw/1e3/mzmax/1.5))
    out['net_section'] = dict(Mz_max=mzmax, cap_Nm=cap, RF_RB=cap/mzmax, RF_x1p5=cap/mzmax/1.5, RF_x2=cap/mzmax/2, width_mm=wid, wide27_RF_RB=ALLOW_P*zw/1e3/mzmax, wide27_RF_x1p5=ALLOW_P*zw/1e3/mzmax/1.5)
    # bridge tube bending at the mouth (audit V5)
    zb = math.pi/64*(16**4-14**4)/8.0
    mzm = max(np.hypot(*(wrench_about(Fv[n], Mv[n], P0)[:, 1:].T)).max() for n in names)
    print('\n## 4. Bridge tube 16x14 bending at the mouth: |(My, Mz)| max %.2f N m; Z = %.1f mm3; sigma %.0f MPa; RF = 350 / (KF %.3f x sigma) = %.2f RB, %.2f x1.5, %.2f x2 (audit V5: 1.93 / 1.29 / 0.97)' % (mzm, zb, mzm*1e3/zb, KF, 350/(KF*mzm*1e3/zb), 350/(KF*mzm*1e3/zb)/1.5, 350/(KF*mzm*1e3/zb)/2))
    out['bridge_RF'] = dict(M_max=float(mzm), Z=zb, RF_RB=350/(KF*mzm*1e3/zb))
    print('\n## 5. Reproduction of audit numbers (tolerance 2 %)')
    aud = {'as drawn (L 9)': (0.11, 0.08), 'V1 (L 21)': (0.62, 0.41), 'C6 (L 22.5)': (0.71, 0.47), 'V2 (L 28.5)': (1.13, 0.75)}
    rows = []
    for lab, (a1, a15) in aud.items():
        v = out['variants'][lab]; rows.append((lab+' RF RB', v['RF_RB'], a1)); rows.append((lab+' RF x1.5', v['RF_x1p5'], a15))
    rows += [('L for RF 1.0, RB (mm)', out['repro']['L_req_RB'], 26.6), ('L for RF 1.0, x1.5 (mm)', out['repro']['L_req_RBx1.5'], 32.6), ('block capacity N m', cap, 12.4), ('block hand RF RB', cap/mzmax, 0.71),
             ('block width RB (mm)', wid['RB'], 23.8), ('block width x1.5 (mm)', wid['x1.5'], 29.1), ('block width x2 (mm)', wid['x2'], 33.6), ('Mz max (N m)', gl['Mz'], 17.51), ('bridge RF RB', 350/(KF*mzm*1e3/zb), 1.93)]
    print('| quantity | here | audit | difference | within 2 % (or one unit of the audit last digit) |'); print('|---|---|---|---|---|')
    for lab, v, a in rows:
        dif = (v-a)/a*100; digit = 0.5*10**(-(len(str(a).split('.')[1]) if '.' in str(a) else 0))   # rounding half-unit of the audit number
        ok = abs(dif) <= 2.0 or abs(v-a) <= digit+1e-9
        print('| %s | %.3f | %s | %+.1f %% | %s |' % (lab, v, a, dif, 'yes' if ok else 'NO'))
    out['repro']['rows'] = [(l, float(v), a, float((v-a)/a*100)) for l, v, a in rows]
    json.dump(out, open(os.path.join(HERE, 'step1_demand.json'), 'w'), indent=1)
    print('\nwall %.0f s' % (time.time()-t0))


if __name__ == '__main__':
    main()
