"""T-076d step 5 (D-222 s4.3 item 5, LR-2): ONE landing load-path table, pad -> cup -> shoe -> fin tube -> root block -> rib -> saddle -> wing torsion / in-plane -> strut -> bridge -> hub -> sleeves / tubes -> bond, all on the same demand set.
CATEGORY: rigid-body dynamics (foot-force histories of landing_a at the chosen pad, CAD mass model) + hand-calculation part checks (landing_path_a.py, unchanged, imported) + the cached FEA rows of step 4 + the D-1 bridge row of step 3.
    python -I t076d_step5_path.py [--tubes TAG]     (TAG = step4_<TAG>.json, default g1_ms11; about 2-4 min)
Columns: BASELINE = the repo defaults (old ITEMS mass, 30 N / 20 mm pad, PAD_D2, zeta 0.05); NEW = the step-2 chosen pad with the CAD mass model at pad zeta 0.02 / 0.05 / 0.10 (RB, KF / KP in the part formulas, RF = allowable / demand, the rule RF >= 1.0);
JUDGED = minimum over the three zeta of RF at max(DAF, 1.5): hand rows RB / 1.5 (all part formulas are homogeneous of degree -1 in the load, so RF scales exactly), FE rows min(RB / 1.5, D-1 dynamic), bridge min(RB / 1.5, D-1 dynamic).
DAF used for the floor: max(1.5, step-3 arm-group sleeve-exit-moment DAF as dynamic envelope / RB envelope, max over the 18 D-1 runs; the case-max ratio is larger, see step 3) when step3_d1.json exists (printed).  The pad geometry of the chosen pad lengthens the foam: PAD_X and CUP_L are increased by the change of x_foot relative to PAD_D2 (EST, conservative).
Rows with an allowable '-' (no source) are listed, not judged."""
import os, sys, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__)); S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
os.environ['LAND_MASS_KG'] = '1.64'; sys.path.insert(0, S_DIR); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
import numpy as np
import t076d_step2_table as T2


def run_hand(FBs):
    c = T2.ctx(); P, L = c['P'], c['L']; allr = {}
    for name, FBt in FBs:
        rf = P.checks(FBt); rf.update(P.pin_cup_checks(FBt)); wrf, _ = P.wing_checks(FBt); rf.update({k.replace('P15', 'P15 skin-less').replace('P16', 'P16 skin-less') if False else k: v for k, v in wrf.items()})
        skin = P.skin_variants()[0][1]; sres, _ = P.wing_checks_skin(FBt, skin); rf.update({'[skin V0] ' + k: v for k, v in sres.items()}); rf.update(P.strut_checks(FBt))
        for key, (lab, a) in rf.items():
            cur = allr.get(key)
            if cur is None or float(a.min()) < cur[0]: allr[key] = (float(a.min()), name, lab)
    return allr


def part_of(key):
    k = key
    if k.startswith('[skin V0]'): return 'wing, glass skin (P15 / P16, V0)'
    if k.startswith('P1 '): return 'pad PSA (pad to shoe plate)'
    if k.startswith('CUP') or k.startswith('PIN'): return 'cup / cross-pin rows (proposed D-215 geometry)'
    if k.startswith(('P2 ', 'P3 ')): return 'shoe (plate, ring bond)'
    if k.startswith('P4 '): return 'fin tube 16x14'
    if k.startswith(('P5 ', 'P6 ', 'P7 ', 'P8 ')): return 'root block (ring bond, junction, socket, wall)'
    if k.startswith(('P9', 'P10', 'P11', 'P12')): return 'rib tube and saddle socket'
    if k.startswith(('P13', 'P14')): return 'saddle ring on spar / spar under the saddle'
    if k.startswith(('P15', 'P16')): return 'wing torsion / in-plane, skin-less (reference)'
    if k.startswith('STRUT'): return 'V strut'
    return 'other: ' + k[:30]


def main():
    t0 = time.time(); np.seterr(all='ignore'); c = T2.ctx(); P, L = c['P'], c['L']
    tag = sys.argv[sys.argv.index('--tubes') + 1] if '--tubes' in sys.argv else 'g1_ms11'
    ch = json.load(open(os.path.join(HERE, 'step2_choice.json')))['choice']; Fp, smax = ch['Fp'], ch['s_max']; xf, zf, _ = T2.pad_geometry(smax)
    daf = 1.5; f3 = os.path.join(HERE, 'step3_d1.json'); s3 = json.load(open(f3)) if os.path.exists(f3) else None
    if s3: daf = max(1.5, s3['overall']['DAF_Mexit_env_max'])
    print('# T-076d step 5: landing load-path table. chosen pad Fp %.0f N, stroke %.0f mm, x_foot %.4f, z_foot %.4f; DAF floor used %.2f' % (Fp, smax * 1e3, xf, zf, daf), flush=True)
    res = {}
    # ---- baseline: repo defaults
    L.MASS_MODEL = 'items'; P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot']); pad_x0, cup_l0 = P.PAD_X, P.CUP_L; FBs = []; stats = dict(stroke=0, n=0, tilt=0, Ffoot=0)
    for name, kw in P.cases(False):
        r = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **P.PAD_D2)); FBs.append((name, r['trace'].reshape(-1, 4, 3)))
        stats = dict(stroke=max(stats['stroke'], float(r['dmax_mm'].max())), n=max(stats['n'], float(r['n_peak'])), tilt=max(stats['tilt'], float(r['tilt_end'])), Ffoot=max(stats['Ffoot'], float(r['F'].max())))
    res['BASELINE'] = dict(rows=run_hand(FBs), stats=stats, smax=20.0); print('baseline done [%.0f s]' % (time.time() - t0), flush=True)
    # ---- new pad, CAD mass, three zeta
    L.MASS_MODEL = 'cad'; P.set_pad(xf, zf); dx = xf - P.PAD_D2['x_foot']; P.PAD_X = pad_x0 + dx; P.CUP_L = cup_l0 + dx
    pts = T2.pts_for('cad'); BR_Z = math.pi / 64 * (16**4 - 14**4) / 8.0; KF = P.KF
    for zeta in (0.02, 0.05, 0.10):
        FBs = []; stats = dict(stroke=0, n=0, tilt=0, Ffoot=0); brg = 0.0
        for name, kw in P.cases(False):
            r = L.simulate(Fp=Fp, s_max=smax, zeta=zeta, dt=2e-4, T=1.5, trace=True, **dict(kw, x_foot=xf, z_foot=zf)); FB = r['trace'].reshape(-1, 4, 3); FBs.append((name, FB))
            stats = dict(stroke=max(stats['stroke'], float(r['dmax_mm'].max())), n=max(stats['n'], float(r['n_peak'])), tilt=max(stats['tilt'], float(r['tilt_end'])), Ffoot=max(stats['Ffoot'], float(r['F'].max())))
            F, M = T2.wrench_split_pts(FB, pts, (2, 3, 4, 6), xf, c['geom']['y_foot'], zf); brg = max(brg, float(np.hypot(M[:, 1], M[:, 2]).max()))
        rows = run_hand(FBs); rows['BRIDGE tube 16x14 bending at the mouth, hand (total hub-side wrench, 350 MPa EST)'] = (350.0 / (KF * brg * 1e3 / BR_Z), 'hub side wrench', 'EST 350 MPa')
        res['NEW z%.2f' % zeta] = dict(rows=rows, stats=stats, smax=smax * 1e3); print('new pad zeta %.2f done [%.0f s]' % (zeta, time.time() - t0), flush=True)
    # ---- FE rows (step 4 JSON) and D-1 bridge (step 3)
    fe = {}; tsr_req = {}; f4 = os.path.join(HERE, 'step4_%s.json' % tag)
    if os.path.exists(f4):
        j = json.load(open(f4)); AL = dict(axial=350.0, hoop=40.0, tau_st=30.0)
        for nm, r in j['rows'].items():
            for t in ('A', 'B'):
                for q in ('axial', 'hoop', 'tau_st'):
                    v = r['tubes'][t][q + '|judged']['value']; fe.setdefault('tube %s %s (judged, 0.5 mm excl.)' % (t, q), {})[nm] = AL[q] / (KF * v)
                fe.setdefault('tube %s old combined shear, raw max, no exclusion (hypot of tau_s,r and tau_s,theta; the T-076c row)' % t, {})[nm] = 30.0 / (KF * r['tubes'][t]['old_shear|raw']['value'])
            fe.setdefault('bond mean shear (full bonded length)', {})[nm] = r['bond']['full']['rf_KP']; fe.setdefault('bond mean shear (T-076c definition)', {})[nm] = r['bond']['T076c']['rf_KP']
            fe.setdefault('Al hub von Mises max excl 0.5 mm', {})[nm] = r['hub']['rf']
            for t in ('A', 'B'): tsr_req[nm] = max(tsr_req.get(nm, 0.0), KF * r['tubes'][t]['tau_sr|judged']['value'] * (daf if nm.startswith('RB') else 1.0))
    br = {}
    if s3:
        for k, v in s3['runs'].items():
            if k.endswith('|summary'): br[k[:-8]] = v['RF_bridge_dyn']
    L_ = []; Pr = L_.append
    cols = ['BASELINE', 'NEW z0.02', 'NEW z0.05', 'NEW z0.10']
    Pr('# T-076d step 5: single landing load-path table (generated by t076d_step5_path.py)\n')
    Pr('Pad / stroke / n / tilt (max over 21 cases): ' + '; '.join('%s: stroke %.1f of %.0f mm (RF %.2f), n %.2f (A-P5 12 g: RF %.2f), tilt %.2f deg (AR-008 3.0: RF %.2f), foot peak %.1f N' % (k, res[k]['stats']['stroke'], res[k]['smax'], res[k]['smax'] / res[k]['stats']['stroke'], res[k]['stats']['n'], 12.0 / res[k]['stats']['n'], res[k]['stats']['tilt'], 3.0 / max(res[k]['stats']['tilt'], 1e-9), res[k]['stats']['Ffoot']) for k in cols) + '\n')
    Pr('## Hand-calculation rows (RF at RB; the judged RF at max(DAF, %.2f) is RB / %.2f), minimum over the 21 cases\n' % (daf, daf))
    Pr('NOTE: these hand rows are landing_path_a.py on the CAD geometry AS DRAWN. The D-215 / T-068 package (clamshell root block, enlarged saddle, plates, cup / pin geometry; printed masses adopted in T-067) is neither drawn in the CAD nor modelled in landing_path_a.py, so the shoe / root-block / saddle / spar-saddle / cup rows are the pre-package state: their BASELINE column reproduces the T-064r record (for example P12 0.28, P6 0.50 -> 0.47 at 1.64 kg, P11 0.34, P14a 0.32 -> 0.29) and they have been below 1.0 since T-064r. They are not new findings of this task.\n')
    part_min = {}; part_rb = {}; gov = {}; peel = {}
    for k in {k for r in res.values() for k in r['rows']}:
        vals = [res[c_]['rows'][k][0] if k in res[c_]['rows'] else None for c_ in cols]; new = [v for v in vals[1:] if v is not None]
        if not new: continue
        jd = min(new) / daf; pn = 'bridge tube 16x14 (hand)' if k.startswith('BRIDGE') else part_of(k); wcase = [res[c_]['rows'][k][1] for c_ in cols[1:] if k in res[c_]['rows'] and res[c_]['rows'][k][0] == min(new)][0]
        tg = peel if ('BOND INTEGRITY' in k or k.startswith('P1 ')) else gov
        if pn not in tg or jd < tg[pn][0]: tg[pn] = (jd, k, vals, wcase)
    for tg, title in ((gov, 'governing row per part (peel / integrity and PSA rows excluded: coupon items, T-069 F-3)'), (peel, 'peel / integrity rows (coupon, outside the RF minimum)')):
        Pr('\n### %s\n' % title); Pr('| part | governing row | BASELINE | NEW z0.02 | NEW z0.05 | NEW z0.10 | JUDGED (worst z, RB / %.2f) | case |' % daf); Pr('|---|---|---|---|---|---|---|---|')
        for pn, (jd, k, vals, wcase) in sorted(tg.items(), key=lambda kv: kv[1][0]):
            Pr('| %s | %s | %s | %.2f | %s |' % (pn, k[:120], ' | '.join('%.2f' % v if v is not None else '-' for v in vals), jd, wcase))
            if tg is gov: part_min[pn] = jd; part_rb[pn] = min(v for v in vals[1:] if v is not None)
    Pr('\n## FEA rows of step 4 (tag %s, Al hub, partition B): RF at the set\'s own scale (RB sets RF at x1.0; D-1 sets are the dynamic wrenches directly); JUDGED = min(RB / %.2f, D-1) over the three pad zeta\n' % (tag, daf))
    if fe:
        sets = sorted({s for r in fe.values() for s in r}); Pr('| row | ' + ' | '.join(sets) + ' | JUDGED |'); Pr('|---|' + '---|' * (len(sets) + 1))
        for k, r in fe.items():
            rb = [v / daf for s_, v in r.items() if s_.startswith('RB')]; d1 = [v for s_, v in r.items() if s_.startswith('D1')]; jd = min(rb + d1) if (rb or d1) else float('nan')
            if 'old combined' not in k and 'T-076c' not in k:
                nm_ = 'FEA: ' + k.split(' (')[0]; rbv = min(list(r.values())); part_min[nm_] = min(part_min.get(nm_, 9e9), jd); part_rb[nm_] = min(part_rb.get(nm_, 9e9), rbv)
            Pr('| %s | %s | %.2f |' % (k, ' | '.join('%.2f' % r[s] if s in r else '-' for s in sets), jd))
    else: Pr('(step4_%s.json not found: FEA rows not available)' % tag)
    if br: Pr('\n## Bridge 16x14 with the D-1 dynamic peak (step 3): RF = ' + ', '.join('%s: %.2f' % (k, v) for k, v in sorted(br.items())) + '  (minimum %.2f)' % min(br.values())); part_min['bridge tube 16x14 (D-1 dynamic)'] = min(br.values()); part_rb['bridge tube 16x14 (D-1 dynamic)'] = min(br.values())
    for nm_, f_ in (('pad: usable stroke / worst stroke', lambda r_: r_['smax'] / r_['stats']['stroke']), ('pad: A-P5 12 g / n peak', lambda r_: 12.0 / r_['stats']['n']), ('pad: AR-008 tilt 3.0 deg / end tilt', lambda r_: 3.0 / max(r_['stats']['tilt'], 1e-9))):
        v_ = min(f_(res[k_]) for k_ in cols[1:]); part_min[nm_] = v_; part_rb[nm_] = v_
    if tsr_req: Pr('\nTube interlaminar shear tau_s,r (judged, 0.5 mm exclusion): the allowable is "-" (no coupon, no data sheet in the repo), so it is not a pass / fail row. The allowable it would have to meet for RF 1.0 at the judged demand (KF x tau, RB sets x %.2f, D-1 sets x 1.0) is %.1f MPa (worst set %s).\n' % (daf, max(tsr_req.values()), max(tsr_req, key=tsr_req.get)))
    Pr('\n## One minimum RF per part. Column RB = at the rigid-body demand of the repo practice (KF / KP in the formulas, no dynamic factor); column FLOOR = at max(DAF, %.2f) = %.2f (hub-escalation rule; the repo never applied it to the wing, fin or shoe hand rows: shown for the single demand set the audit asks for)\n' % (daf, daf))
    Pr('| part | min RF (RB / D-1) | verdict | min RF at the DAF floor | verdict |'); Pr('|---|---|---|---|---|')
    for k, v in sorted(part_min.items(), key=lambda kv: kv[1]):
        rbv = part_rb.get(k, float('nan')); Pr('| %s | %.2f | %s | %.2f | %s |' % (k, rbv, 'PASS' if rbv >= 1.0 else '**FAIL**', v, 'PASS' if v >= 1.0 else '**FAIL**'))
    Pr('\n(old-definition rows and the T-076c bond definition are shown for continuity and are not judged; the skin-less P15 / P16 rows are the pre-skin reference: the glass-skin V0 rows govern the wing.)')
    open(os.path.join(HERE, 'step5_path.md'), 'w').write('\n'.join(L_) + '\n'); json.dump(dict(daf=daf, part_min_floor=part_min, part_min_rb=part_rb, stats={k: res[k]['stats'] for k in res}), open(os.path.join(HERE, 'step5_path.json'), 'w'), indent=1, default=float)
    print('\n'.join(L_[-40:])); print('done %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
