"""T-076d step 3 (D-222 s4.3 item 3): D-1 modal transient re-run with the step-2 foot forces at the chosen pad point, zeta 0.02 / 0.05 / 0.10, as-built 16x14 bridge, with the PARTITION-B arm-root wrench output.
CATEGORY: dynamics (beam-frame FE modal superposition, exact integrator, ONE-WAY coupling to the rigid-body landing sim); not FEA of the hub.   python -I t076d_step3_d1.py     (about 3-6 min)
Reuses t076c_step2_d1.py UNCHANGED (imported: frame builder, T-076 mass mapping, modal integrator, element matrices).  New here:
  - foot forces from landing_a.simulate at the chosen pad (step2_choice.json: Fp, usable stroke, pad geometry), CAD mass model (LAND_MASS_MODEL=cad), 21 cases, for each pad-zeta 0.02 / 0.05 / 0.10;
  - frame: as-built bridge 16x14 only, corners kd / nom / hi, modal damping 1 % and 2 %;
  - arm-group wrench the centre exerts on the arm group = sum over the four arm elements of the loads the hub node applies on them (moved to P0), and hub-group wrench = hub-side total - arm group (partition B);
  - DAF of the arm-group wrench against the rigid-body arm-group wrench of the same sim (same definition as D-1: component envelope ratio and case-max over cases with RB >= 50 % of the envelope), plus the sleeve-exit proxy Mexit and beam sigma / tau (t076d_step2_table functions) of the DYNAMIC arm-group wrench against the RB value.
Saves the dynamic histories (damping 1 %, all corners, all pad-zeta) to T076d_data/fea/d1_wrench_zeta<z>.npz (git-ignored) for step 4, and summary JSON step3_d1.json."""
import os, sys, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
T76C = os.path.abspath(os.path.join(HERE, '..', 'T076c_data')); S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
os.environ['LAND_MASS_KG'] = '1.64'; os.environ['LAND_MASS_MODEL'] = 'cad'
sys.path.insert(0, HERE); sys.path.insert(0, T76C); sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
import numpy as np
import t076c_step2_d1 as D1                     # unchanged module (import-time patches only)
import t076d_step2_table as T2
FEA = os.path.join(HERE, 'fea'); os.makedirs(FEA, exist_ok=True)
KF = D1.KF; DT = D1.DT; P0 = D1.P0


def feet_forces(choice, zeta):
    c = T2.ctx(); L, P = c['L'], c['P']; Fp, smax = choice['Fp'], choice['s_max']
    xf, zf, _ = T2.pad_geometry(smax); P.set_pad(xf, zf); out = {}; rb = {}
    pts = T2.pts_for('cad'); yf = c['geom']['y_foot']
    for name, kw in P.cases(False):
        r = L.simulate(Fp=Fp, s_max=smax, zeta=zeta, dt=2e-4, T=1.5, trace=True, **dict(kw, x_foot=xf, z_foot=zf))
        FB = r['trace'].reshape(-1, 4, 3); out[name] = FB
        Fa, Ma = T2.wrench_split_pts(FB, pts, (2, 3), xf, yf, zf); Fh, Mh = T2.wrench_split_pts(FB, pts, (4, 6), xf, yf, zf)
        rb[name] = dict(Fa=Fa, Ma=Ma, Fh=Fh, Mh=Mh, stroke=float(r['dmax_mm'].max()), n=float(r['n_peak']), tilt=float(r['tilt_end']), Ffoot=float(r['F'].max()))
    return out, rb, (xf, yf, zf)


def main():
    np.seterr(all='ignore'); t0 = time.time(); sel = '--quick' in sys.argv
    choice = json.load(open(os.path.join(HERE, 'step2_choice.json')))['choice']
    print('# T-076d step 3: D-1 modal transient, partition-B arm wrench.  Category: dynamics (modal superposition, one-way coupling).  Pad Fp %.0f N, usable stroke %.0f mm; mass model cad; 1.64 kg.' % (choice['Fp'], choice['s_max'] * 1e3), flush=True)
    tips = ['f%+d%+d' % (sy, sz) for sy in (1, -1) for sz in (1, -1)]
    zpads = (0.05,) if sel else (0.02, 0.05, 0.10); corners = ('nom',) if sel else ('kd', 'nom', 'hi'); dmps = (0.01,) if sel else (0.01, 0.02)
    FB, RB, geo = {}, {}, {}
    for zp in zpads:
        FB[zp], RB[zp], geo[zp] = feet_forces(choice, zp)
        print('pad zeta %.2f: foot forces done, worst stroke %.1f mm, n %.2f, tilt %.2f  [%.0f s]' % (zp, max(v['stroke'] for v in RB[zp].values()), max(v['n'] for v in RB[zp].values()), max(v['tilt'] for v in RB[zp].values()), time.time() - t0), flush=True)
    names = list(FB[zpads[0]]); xf, yf, zf = geo[zpads[0]]
    foot_xyz = [np.array([xf, sy * yf, sz * zf]) for sy in (1, -1) for sz in (1, -1)]
    out = dict(info=dict(choice=choice, mass_kg=1.64, mass_model='cad (maturity placement)', foot=[xf, yf, zf], dt=DT), runs={}); SER = {zp: {} for zp in zpads}
    for corner in corners:
        F, V, w2, f, Mm, K, mass = D1.solve_frame(corner, 'asbuilt'); idx = F._idx; tipxyz = [F.n[t] for t in tips]
        print('\n## frame asbuilt %s: FE mass %.1f g; lowest flexible modes (Hz): %s' % (corner, mass * 1e3, ', '.join('%.1f' % x for x in f[f >= 0.5][:8])), flush=True)
        el_hub_bridge = [e for e in F.el if e[8] == 'bridge' and ('hub' in (e[0], e[1]))]; el_arm_hub = [e for e in F.el if e[8] == 'arm' and e[0] == 'hub']
        brg = [e for e in F.el if e[8] == 'bridge' and e[0] == 'hub' and e[1].startswith('hub>s+0.000')]; assert len(brg) == 1
        brg_el = brg[0]; Kb, pa_b, pb_b = D1.element_T_k(F, brg_el)
        def dof_of(e): return [6 * idx[e[0]] + i for i in range(6)] + [6 * idx[e[1]] + i for i in range(6)]
        dofs_b = dof_of(brg_el); hub_els = [(e, D1.element_T_k(F, e)) for e in el_hub_bridge]; arm_els = [(e, D1.element_T_k(F, e)) for e in el_arm_hub]; hubpos = F.n['hub']
        assert len(arm_els) == 4, len(arm_els)
        for zp in zpads:
            for zd in dmps:
                key = '%.2f|%s|%.2f' % (zp, corner, zd); res = {}
                for nm in names:
                    row = {}
                    for tag, ro in (('dyn', False), ('rig', True)):
                        q = D1.run_case(F, V, w2, FB[zp][nm], zd, tips, tipxyz, foot_xyz, rigid_only=ro)
                        Fc = np.zeros((len(q), 3)); Mc = np.zeros((len(q), 3))
                        for e, (kg, pa, pb) in hub_els:
                            u = q @ V[dof_of(e), :].T; fe = u @ kg.T; Fc -= fe[:, 0:3]; Mc -= fe[:, 3:6]
                        Mc = Mc + np.cross(np.broadcast_to(hubpos - P0, Fc.shape), Fc)
                        Fa = np.zeros((len(q), 3)); Ma = np.zeros((len(q), 3))
                        for e, (kg, pa, pb) in arm_els:
                            u = q @ V[dof_of(e), :].T; fe = u @ kg.T; Fa += fe[:, 0:3]; Ma += fe[:, 3:6]
                        Ma = Ma + np.cross(np.broadcast_to(hubpos - P0, Fa.shape), Fa)
                        u = q @ V[dofs_b, :].T; fe = u @ Kb.T; Fb_, Mb_ = fe[:, 0:3], fe[:, 3:6]; secM = Mb_ + np.cross(np.broadcast_to(pa_b - P0, Fb_.shape), Fb_)
                        Wa = np.hstack([Fa, Ma]); Wtot = np.hstack([Fc, Mc]); Wh = Wtot - Wa
                        sig, tau = T2.beam_rows(Wa)
                        row[tag] = dict(hubMz=float(np.abs(Mc[:, 2]).max()), brg_M=float(np.hypot(secM[:, 1], secM[:, 2]).max()), Wa_env=[float(np.abs(Wa[:, k]).max()) for k in range(6)], Mexit=float(T2.exit_moment(Wa).max()),
                                        sigma=float(sig.max()), tau=float(tau.max()), Mz_arm=float(np.abs(Ma[:, 2]).max()), Wh_env=[float(np.abs(Wh[:, k]).max()) for k in range(6)])
                        if tag == 'dyn' and zd == 0.01: SER[zp][(corner, nm)] = (Wa.astype(np.float32), Wh.astype(np.float32))
                        if tag == 'rig':
                            Wrb = np.hstack([RB[zp][nm]['Fa'], RB[zp][nm]['Ma']]); b = Wrb[:, 5]; row['rig_vs_RB_Mz_arm_ratio'] = float((Wa[:, 5] @ b) / max(b @ b, 1e-12)); row['rig_vs_RB_corr'] = float(np.corrcoef(Wa[:, 5], b)[0, 1]) if b.std() > 1e-9 else None
                    Wrb = np.hstack([RB[zp][nm]['Fa'], RB[zp][nm]['Ma']]); sg0, tu0 = T2.beam_rows(Wrb)
                    row['RB'] = dict(Wa_env=[float(np.abs(Wrb[:, k]).max()) for k in range(6)], Mexit=float(T2.exit_moment(Wrb).max()), sigma=float(sg0.max()), tau=float(tu0.max()), Mz_arm=float(np.abs(RB[zp][nm]['Ma'][:, 2]).max()),
                                     Wh_env=[float(np.abs(np.hstack([RB[zp][nm]['Fh'], RB[zp][nm]['Mh']])[:, k]).max()) for k in range(6)])
                    res[nm] = row
                # summary: arm-group DAF (dyn vs sim RB, same definition as D-1)
                env = lambda tag, q: max(res[n][tag][q] for n in names)
                envRB = env('RB', 'Mexit'); govn = [n for n in names if res[n]['RB']['Mexit'] >= 0.5 * envRB]
                comp = {}
                for k, cn in enumerate(('Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz')):
                    ed = max(res[n]['dyn']['Wa_env'][k] for n in names); er = max(res[n]['RB']['Wa_env'][k] for n in names)
                    cm = max(res[n]['dyn']['Wa_env'][k] / res[n]['RB']['Wa_env'][k] for n in names if res[n]['RB']['Wa_env'][k] >= 0.5 * er)
                    comp[cn] = dict(env_dyn=ed, env_RB=er, env_ratio=ed / er, case_max=cm)
                S = dict(Mexit_dyn_env=env('dyn', 'Mexit'), Mexit_RB_env=envRB, DAF_Mexit_env=env('dyn', 'Mexit') / envRB, DAF_Mexit_casemax=max(res[n]['dyn']['Mexit'] / res[n]['RB']['Mexit'] for n in govn),
                         sigma_dyn=env('dyn', 'sigma'), sigma_RB=env('RB', 'sigma'), tau_dyn=env('dyn', 'tau'), tau_RB=env('RB', 'tau'), Mz_arm_dyn=env('dyn', 'Mz_arm'), Mz_arm_RB=env('RB', 'Mz_arm'),
                         DAF_Mzarm_env=env('dyn', 'Mz_arm') / env('RB', 'Mz_arm'), comp=comp, DAF_comp_judge=max(max(v['env_ratio'], v['case_max']) for v in comp.values()),
                         hubMz_dyn=env('dyn', 'hubMz'), brg_M_dyn=env('dyn', 'brg_M'), RF_bridge_dyn=350.0 / (KF * (env('dyn', 'brg_M') * 1e3 / (math.pi / 64 * (16**4 - 14**4) / 8.0))),
                         qs_arm_Mz_ratio_min=min(res[n]['rig_vs_RB_Mz_arm_ratio'] for n in govn), stroke_max=max(RB[zp][n]['stroke'] for n in names), n_max=max(RB[zp][n]['n'] for n in names), tilt_max=max(RB[zp][n]['tilt'] for n in names))
                out['runs'][key] = res; out['runs'][key + '|summary'] = S
                print('pad zeta %.2f %s damp %.0f %%: arm-group Mexit dyn env %.2f / sim RB %.2f N m -> DAF env %.2f, case-max %.2f; Mz_arm dyn %.2f vs RB %.2f (DAF %.2f); components judge DAF %.2f (Fx %.2f Fy %.2f Fz %.2f Mx %.2f My %.2f Mz %.2f); sigma dyn %.1f RB %.1f MPa; tau dyn %.2f RB %.2f; hub Mz dyn %.2f; RF_bridge(dyn) %.2f; QS/RB arm Mz %.2f' % (
                    zp, corner, zd * 100, S['Mexit_dyn_env'], S['Mexit_RB_env'], S['DAF_Mexit_env'], S['DAF_Mexit_casemax'], S['Mz_arm_dyn'], S['Mz_arm_RB'], S['DAF_Mzarm_env'], S['DAF_comp_judge'], *[max(v['env_ratio'], v['case_max']) for v in comp.values()],
                    S['sigma_dyn'], S['sigma_RB'], S['tau_dyn'], S['tau_RB'], S['hubMz_dyn'], S['RF_bridge_dyn'], S['qs_arm_Mz_ratio_min']), flush=True)
        print('frame wall %.0f s' % (time.time() - t0), flush=True)
    for zp in zpads:
        np.savez_compressed(os.path.join(FEA, 'd1_wrench_zeta%.2f.npz' % zp), **{'%s|%s|Wa' % k: v[0] for k, v in SER[zp].items()}, **{'%s|%s|Wh' % k: v[1] for k, v in SER[zp].items()})
    # RB wrench series (sim, partition B) for step 4
    for zp in zpads:
        np.savez_compressed(os.path.join(FEA, 'rb_wrench_zeta%.2f.npz' % zp), **{'%s|Wa' % n: np.hstack([RB[zp][n]['Fa'], RB[zp][n]['Ma']]).astype(np.float32) for n in names}, **{'%s|Wh' % n: np.hstack([RB[zp][n]['Fh'], RB[zp][n]['Mh']]).astype(np.float32) for n in names},
                            names=np.array(names))
    sm = {k: v for k, v in out['runs'].items() if k.endswith('|summary')}
    out['overall'] = dict(DAF_comp_judge_max=max(v['DAF_comp_judge'] for v in sm.values()), DAF_Mexit_env_max=max(v['DAF_Mexit_env'] for v in sm.values()), DAF_Mexit_casemax_max=max(v['DAF_Mexit_casemax'] for v in sm.values()),
                          RF_bridge_dyn_min=min(v['RF_bridge_dyn'] for v in sm.values()))
    print('\n## OVERALL (max over %d runs): %s' % (len(sm), json.dumps({k: round(v, 3) for k, v in out['overall'].items()})))
    json.dump(out, open(os.path.join(HERE, 'step3_d1%s.json' % ('_quick' if sel else '')), 'w'), indent=1, default=float)
    print('done %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
