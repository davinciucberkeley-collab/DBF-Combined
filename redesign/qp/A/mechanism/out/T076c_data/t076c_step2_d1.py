"""T-076c step 2 (hub escalation s3.3 run D-1, D-220): modal transient response of the concept A beam frame to the landing foot-force histories -> DAF at the hub root, the bridge tube and the arm roots.
CATEGORY: dynamics (beam-frame FE, free-free, exact modal time integration; ONE-WAY coupling: the foot forces come from the rigid-body landing sim and are applied as given to the flexible frame).  Not FEA of the hub.
Python -I t076c_step2_d1.py [--quick]     (cwd anywhere; minutes)
Model: fe_a.py frame + t073_modal.py corrected skin / rotary-inertia patches (imported, unmodified) with the T-076 t076_modal.py T067 mass mapping (copied, MODE t067, RESID 1: total 1.640 kg).  All mass placements EST (T-076 mapping).
 - bridge variants: 'asbuilt' = the CAD bridge 16x14 (wing.py BR_OD / BR_ID, D-206); 'rec' = the committed t073 / T-076 modal CFG, bridge 12x10 (kept as a sensitivity; it predates D-206 in the modal CFG).
 - corners kd / nom / hi (material knock-down of fe_a.py), damping zeta 1 % and 2 % in every flexible mode (rigid modes undamped).
 - input: foot forces FB (21 landing cases, 1.64 kg, D2 pad, 0.2 ms) applied at the four fin-tip nodes, with the offset moment (foot minus tip node: x +47.5 mm, z +9 mm).  Gravity and rotor lift neglected (as the rigid-body wrench).
 - integration: every mode (all 6N), first-order hold on the modal force, exact 2x2 state transition (matrix exponential), so no numerical damping or period error.
Outputs per case: peak |Mz| hub-side wrench at the bore mouth P0 (dynamic / FE quasi-static (inertia relief) / sim rigid-body RB), the bridge-tube section at the mouth |(My, Mz)|, arm-root bending, DAF = dynamic peak / reference peak.
"""
import os, sys, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
T73 = os.path.abspath(os.path.join(HERE, '..', 'T073_data'))
os.environ.setdefault('T073_PROP', '9'); os.environ.setdefault('T073_SKIN', '1'); os.environ.setdefault('T073_O4', '0')
sys.path.insert(0, T73)
sys.dont_write_bytecode = True
import numpy as np
from scipy.linalg import eigh, expm
import t073_modal as M
import fe_a
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
FEA = os.path.abspath(os.path.join(HERE, '..', 'T076_data', 'fea'))
NPZ = os.path.join(FEA, 't076c_demand_m164.npz')
KF = 1.5*1.15
DT = 2e-4
P0 = np.array([-0.045, 0.0, -0.002])                       # original bore mouth (wing.py HUB_X1, BR_Z)
G_REF = 'rigid'                                              # reference tag

# ---------------------------------------------------------------- T-076 mass mapping (copied from t076_modal.py, MODE t067, RESID 1; EST)
M.CFG.update(pack_g=275.0, avionics_g=110.0-8.0+1.02+9.67-2.0-0.81, motor_g=65.0+11.06+5.0+4.3+2.9+2.41, foot_pad_m=(2.5+(4.55-1.40))*1e-3)
_orig_build = fe_a.build
def build2(kind='nom', **kw):
    F, info = _orig_build(kind, **kw)
    F.lump('hub', (15.82-20.0+15.7+0.0)*1e-3)
    for sy in (1, -1):
        yv = sy*kw.get('bridge_yv', 0.30); nm = 's%+.3f' % yv
        if nm in F.n: F.lump(nm, (3.69-1.5+1.5)*1e-3)
        F.lump('f%+dr' % sy, ((18.90-3.20)+(14.39-1.00)+6.0)*1e-3)
    return F, info
fe_a.build = build2
def lumped_total(F):
    m = sum(F.mass.values())
    for (a, b, EA, EIy, EIz, GJ, rA, vref, grp) in F.el: m += rA*float(np.linalg.norm(np.array(F.n[a])-np.array(F.n[b])))
    return m
_bv = M.build_variant
def bv2(corner):
    F, sp = _bv(corner); res = 1.64-lumped_total(F)
    if res > 0:
        ys = sorted(float(n[1:]) for n in F.n if n.startswith('s') and '>' not in n and abs(float(n[1:])) <= 0.45)
        for y in ys: F.lump('s%+.3f' % y, res/len(ys))
    return F, sp
M.build_variant = bv2
CFG0 = dict(M.CFG)

_CAP = {}
SER = {}
_real_eigh = M._orig_eigh
def _capture(K, Mm):
    _CAP['K'] = K.copy(); _CAP['M'] = Mm.copy(); return _real_eigh(K, Mm)
M._orig_eigh = _capture


def solve_frame(corner, bridge):
    M.CFG.clear(); M.CFG.update(CFG0)
    if bridge == 'asbuilt': M.CFG['bridge_tube'] = (16e-3, 14e-3)
    F, sp = M.build_variant(corner); M._CUR['F'] = F; M._CUR['corner'] = corner
    res = F.solve(100)                                         # patched solve: stores F._V (all mass-normalised eigenvectors)
    V = F._V; K = _CAP['K']; Mm = _CAP['M']
    lam = np.einsum('ij,ik,kj->j', V, K, V)                    # V^T K V diagonal = omega^2
    mm = np.einsum('ij,ik,kj->j', V, Mm, V)
    assert np.allclose(mm, 1.0, atol=1e-6), mm.min()
    w2 = np.where(lam > 0, lam, 0.0); f = np.sqrt(w2)/(2*math.pi)
    return F, V, w2, f, Mm, K, lumped_total(F)


# ---------------------------------------------------------------- beam element end loads (global frame), copied from fe_a.Frame.solve
def element_T_k(F, el):
    a, b, EA, EIy, EIz, GJ, rA, vref, grp = el
    pa, pb = F.n[a], F.n[b]; L = np.linalg.norm(pb-pa); ex = (pb-pa)/L
    ey = np.cross(vref, ex); ey /= np.linalg.norm(ey); ez = np.cross(ex, ey)
    R = np.array([ex, ey, ez]); T = np.zeros((12, 12))
    for i in range(4): T[3*i:3*i+3, 3*i:3*i+3] = R
    k = np.zeros((12, 12))
    k[0, 0] = k[6, 6] = EA/L; k[0, 6] = k[6, 0] = -EA/L
    k[3, 3] = k[9, 9] = GJ/L; k[3, 9] = k[9, 3] = -GJ/L
    c = EIz/L**3
    for (i, j, v) in ((1, 1, 12), (1, 5, 6*L), (1, 7, -12), (1, 11, 6*L), (5, 5, 4*L*L), (5, 7, -6*L), (5, 11, 2*L*L), (7, 7, 12), (7, 11, -6*L), (11, 11, 4*L*L)): k[i, j] = k[j, i] = c*v
    c = EIy/L**3
    for (i, j, v) in ((2, 2, 12), (2, 4, -6*L), (2, 8, -12), (2, 10, -6*L), (4, 4, 4*L*L), (4, 8, 6*L), (4, 10, 2*L*L), (8, 8, 12), (8, 10, 6*L), (10, 10, 4*L*L)): k[i, j] = k[j, i] = c*v
    return T.T@k@T, pa, pb                                      # global 12x12: force the nodes apply on the element = kg u


def modal_response(V, w2, zeta, g, dt=DT, rigid_hz=0.5):
    """g (nt, nm) generalised forces -> q (nt, nm) displacements, exact for piecewise-linear g.  Rigid modes (f < rigid_hz): undamped, omega 0."""
    nt, nm = g.shape; w = np.sqrt(w2); z = np.where(w/(2*math.pi) < rigid_hz, 0.0, zeta); w = np.where(w/(2*math.pi) < rigid_hz, 0.0, w)
    E = np.zeros((nm, 4, 4))
    for m in range(nm):
        A = np.array([[0, 1, 0, 0], [-w[m]**2, -2*z[m]*w[m], 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]], float)
        E[m] = expm(A*dt)
    q = np.zeros((nt, nm)); qd = np.zeros(nm); qn = np.zeros(nm)
    gd = np.diff(g, axis=0)/dt
    for n in range(nt-1):
        z4 = np.stack([qn, qd, g[n], gd[n]], 1)                # (nm, 4)
        zn = np.einsum('mij,mj->mi', E, z4)
        qn, qd = zn[:, 0], zn[:, 1]; q[n+1] = qn
    return q


def run_case(F, V, w2, FB, zeta, tips, tipxyz, foot_xyz, rigid_only=False):
    """FB (nt, 4, 3) -> nodal load history, generalised forces, modal displacements.  Returns q (nt, nm)."""
    names = F._names; idx = F._idx; nt = len(FB); nd = V.shape[0]
    fN = np.zeros((nt, nd))
    for i in range(4):
        r = foot_xyz[i]-tipxyz[i]; j = idx[tips[i]]
        fN[:, 6*j:6*j+3] += FB[:, i, :]
        fN[:, 6*j+3:6*j+6] += np.cross(np.broadcast_to(r, FB[:, i, :].shape), FB[:, i, :])
    g = fN@V
    if rigid_only:                                              # quasi-static (inertia-relief) reference: flexible modes q = g / omega^2 (no modal dynamics), rigid modes integrated
        rig = np.sqrt(w2)/(2*math.pi) < 0.5
        qr = modal_response(V, w2, zeta, g*rig[None, :])
        qs = np.where(rig[None, :], 0.0, g/np.where(rig, 1.0, w2)[None, :])
        return qr+qs
    return modal_response(V, w2, zeta, g)


def end_loads(F, V, q, node_a, el_idx_list, side):
    pass


def main():
    np.seterr(all='ignore'); t0 = time.time(); quick = '--quick' in sys.argv
    z = np.load(NPZ); names = [str(n) for n in z['names']]
    FBs = {n: z['FB|'+n].astype(float) for n in names}; Frb = {n: z['F|'+n] for n in names}; Mrb = {n: z['M|'+n] for n in names}
    meta = json.load(open(os.path.join(HERE, 'step1_pad_stroke.json')))
    # foot positions in the body frame (landing_path_a PAD_D2 geometry, as used by the sim)
    sys.path.insert(0, S_DIR); os.environ['LAND_MASS_KG'] = '1.64'
    import landing_a as L, landing_path_a as LP
    gg = L.geom(); xf, yf, zf = LP.PAD_D2['x_foot'], gg['y_foot'], LP.PAD_D2['z_foot']
    foot_xyz = [np.array([xf, sy*yf, sz*zf]) for sy in (1, -1) for sz in (1, -1)]
    tips = ['f%+d%+d' % (sy, sz) for sy in (1, -1) for sz in (1, -1)]
    out = dict(info=dict(mass_kg=1.64, dt=DT, foot=[xf, yf, zf]), runs={})
    combos = [('asbuilt', 'nom'), ('rec', 'nom')] if quick else [(b, c) for b in ('asbuilt', 'rec') for c in ('nom', 'kd', 'hi')]
    zetas = (0.01,) if quick else (0.01, 0.02)
    sel = names if not quick else names[:3]
    print('# T-076c step 2: D-1 modal transient.  Category: dynamics (beam-frame FE modal superposition, exact integrator, one-way coupling to the rigid-body landing sim).  Mass 1.64 kg.')
    for bridge, corner in combos:
        F, V, w2, f, Mm, K, mass = solve_frame(corner, bridge)
        idx = F._idx; tipxyz = [F.n[t] for t in tips]
        flex = f[f >= 0.5]
        if (bridge, corner) == ('asbuilt', 'nom'):
            pts = [(F.mass[n_], F.n[n_]) for n_ in F.mass]
            for (a_, b_, EA, EIy, EIz, GJ, rA, vref, grp) in F.el:
                Lq = np.linalg.norm(F.n[b_]-F.n[a_]); pts += [(0.5*rA*Lq, F.n[a_]), (0.5*rA*Lq, F.n[b_])]
            mt = sum(p_[0] for p_ in pts); cgf = sum(p_[0]*p_[1] for p_ in pts)/mt
            If = sum(p_[0]*(np.dot(p_[1]-cgf, p_[1]-cgf)*np.eye(3)-np.outer(p_[1]-cgf, p_[1]-cgf)) for p_ in pts)
            mm_, cgs, Is = L.mass_props(1.64)
            print('Mass-model check (point masses about own CG): FE CG %s mm, I_diag %s g m2;  sim ITEMS CG %s mm (ITEMS only; the sim then uses the CAD CG), I_diag %s g m2' % (np.round(cgf*1e3, 1).tolist(), np.round(np.diag(If)*1e3, 1).tolist(), np.round(cgs*1e3, 1).tolist(), np.round(np.diag(Is)*1e3, 1).tolist()))
            out['info']['inertia_FE_gm2'] = np.diag(If).tolist(); out['info']['inertia_sim_gm2'] = np.diag(Is).tolist(); out['info']['cg_FE_mm'] = (cgf*1e3).tolist()
        print('\n## frame: bridge %s, corner %s: %d dofs, %d rigid modes, FE mass %.1f g; lowest flexible modes (Hz): %s' % (bridge, corner, V.shape[0], int((f < 0.5).sum()), mass*1e3, ', '.join('%.1f' % x for x in flex[:12])))
        # element sets
        el_hub_bridge = [e for e in F.el if e[8] == 'bridge' and ('hub' in (e[0], e[1]))]
        el_arm_hub = [e for e in F.el if e[8] == 'arm' and e[0] == 'hub']
        brg = [e for e in el_hub_bridge if e[1].startswith('hub>s+0.000') or e[1] == 's+0.000']       # the straight bridge tube (first segment)
        brg = [e for e in F.el if e[8] == 'bridge' and e[0] == 'hub' and e[1].startswith('hub>s+0.000')]
        assert len(brg) == 1, [(e[0], e[1]) for e in el_hub_bridge]
        brg_el = brg[0]
        Kb, pa_b, pb_b = element_T_k(F, brg_el); dofs_b = [6*idx[brg_el[0]]+i for i in range(6)]+[6*idx[brg_el[1]]+i for i in range(6)]
        hub_els = [(e, element_T_k(F, e)) for e in el_hub_bridge]
        arm_els = [(e, element_T_k(F, e)) for e in el_arm_hub]
        def dof_of(e): return [6*idx[e[0]]+i for i in range(6)]+[6*idx[e[1]]+i for i in range(6)]
        hubpos = F.n['hub']
        for zeta in zetas:
            key = '%s|%s|%.0f' % (bridge, corner, zeta*100); res = {}
            for nm in sel:
                FB = FBs[nm]
                row = {}
                for tag, ro in (('dyn', False), ('rig', True)):
                    q = run_case(F, V, w2, FB, zeta, tips, tipxyz, foot_xyz, rigid_only=ro)        # (nt, nm)
                    # hub-side wrench (centre on hub) about P0 = - sum of element end loads at the hub node of the bridge + struts, moved to P0
                    Fc = np.zeros((len(q), 3)); Mc = np.zeros((len(q), 3))
                    for e, (kg, pa, pb) in hub_els:
                        u = q@V[dof_of(e), :].T; fe = u@kg.T                                   # (nt, 12): loads the nodes apply on the element
                        Fc -= fe[:, 0:3]; Mc -= fe[:, 3:6]                                   # the element applies the opposite on the hub node (a = 'hub')
                    Mc = Mc+np.cross(np.broadcast_to(hubpos-P0, Fc.shape), Fc)
                    # bridge tube section at the mouth (x = -0.045), 30 mm from the hub node along the first segment
                    u = q@V[dofs_b, :].T; fe = u@Kb.T; Fa, Ma = fe[:, 0:3], fe[:, 3:6]
                    secM = Ma+np.cross(np.broadcast_to(pa_b-P0, Fa.shape), Fa)                # moment of the end load about the section point (mouth)
                    # arm root: bending (excl. torque about the arm axis) at the hub end of each arm element
                    armM = []
                    for e, (kg, pa, pb) in arm_els:
                        u = q@V[dof_of(e), :].T; fe = u@kg.T; Ma_ = fe[:, 3:6]; ax = (pb-pa)/np.linalg.norm(pb-pa)
                        mt = (Ma_@ax)[:, None]*ax; armM.append(float(np.linalg.norm(Ma_-mt, axis=1).max()))
                    if tag == 'rig':
                        a_, b_ = Mc[:, 2], Mrb[nm][:, 2]; row['corr_qs_vs_simRB_Mz'] = float(np.corrcoef(a_, b_)[0, 1]); row['qs_over_simRB_Mz_ratio_lsq'] = float((a_@b_)/(b_@b_))
                    if tag == 'dyn' and zeta == 0.01 and bridge == 'asbuilt': SER[(corner, nm)] = np.hstack([Fc, Mc]).astype(np.float32)
                    row[tag] = dict(hub_Mz=float(np.abs(Mc[:, 2]).max()), hub_My=float(np.abs(Mc[:, 1]).max()), hub_Mx=float(np.abs(Mc[:, 0]).max()), hub_Fz=float(np.abs(Fc[:, 2]).max()), hub_Fy=float(np.abs(Fc[:, 1]).max()),
                                    hub_Fx=float(np.abs(Fc[:, 0]).max()), brg_Mz=float(np.abs(secM[:, 2]).max()), brg_My=float(np.abs(secM[:, 1]).max()),
                                    brg_M=float(np.hypot(secM[:, 1], secM[:, 2]).max()), arm_M=armM, brg_Mx=float(np.abs(secM[:, 0]).max()),
                                    Mz_series_peak_t=float(np.argmax(np.abs(Mc[:, 2]))*DT))
                # sim rigid-body reference at P0
                rbMz = float(np.abs(Mrb[nm][:, 2]).max()); rbM = float(np.hypot(Mrb[nm][:, 1], Mrb[nm][:, 2]).max())
                row['sim_rb'] = dict(Mz=rbMz, My_Mz=rbM, comps=[float(np.abs(Frb[nm][:, k]).max()) for k in range(3)]+[float(np.abs(Mrb[nm][:, k]).max()) for k in range(3)])
                res[nm] = row
            out['runs'][key] = res
            # summary
            dn = [(nm, res[nm]['dyn'], res[nm]['rig'], res[nm]['sim_rb']) for nm in sel]
            envdyn_hub = max(r[1]['hub_Mz'] for r in dn); envrb = max(r[3]['Mz'] for r in dn); envrig_hub = max(r[2]['hub_Mz'] for r in dn)
            envdyn_brg = max(r[1]['brg_M'] for r in dn); envrig_brg = max(r[2]['brg_M'] for r in dn); envrb_my_mz = max(r[3]['My_Mz'] for r in dn)
            gov = [r for r in dn if r[3]['Mz'] >= 0.5*envrb]; gov_names = [nm for nm, d_, r_, s_ in dn if s_['Mz'] >= 0.5*envrb]
            daf_case_hub = max(r[1]['hub_Mz']/r[3]['Mz'] for r in gov); daf_case_brg = max(r[1]['brg_M']/max(r[3]['My_Mz'], 1e-9) for r in dn if r[3]['My_Mz'] >= 0.5*envrb_my_mz)
            daf_case_hub_fe = max(r[1]['hub_Mz']/r[2]['hub_Mz'] for r in gov)
            daf_case_brg_fe = max(r[1]['brg_M']/r[2]['brg_M'] for r in dn if r[2]['brg_M'] >= 0.5*envrig_brg)
            arm_env_dyn = max(max(res[nm]['dyn']['arm_M']) for nm in sel); arm_env_qs = max(max(res[nm]['rig']['arm_M']) for nm in sel)
            arm_case = max(max(res[nm]['dyn']['arm_M'])/max(res[nm]['rig']['arm_M']) for nm in sel if max(res[nm]['rig']['arm_M']) >= 0.5*arm_env_qs)
            sig = lambda m: m*1e3/(math.pi/64*(16**4-14**4)/8.0)
            rf_b = 350.0/(KF*sig(envdyn_brg))
            out['runs'][key+'|summary'] = dict(env_hub_Mz_dyn=envdyn_hub, env_hub_Mz_rig_FE=envrig_hub, env_hub_Mz_sim_RB=envrb, DAF_hub_env_vs_simRB=envdyn_hub/envrb, DAF_hub_env_vs_FErigid=envdyn_hub/envrig_hub,
                                              DAF_hub_case_max_vs_simRB=daf_case_hub, DAF_hub_case_max_vs_FErigid=daf_case_hub_fe,
                                              env_bridge_M_dyn=envdyn_brg, env_bridge_M_rig_FE=envrig_brg, env_bridge_M_simRB_total=envrb_my_mz, DAF_bridge_env_vs_simRB=envdyn_brg/envrb_my_mz,
                                              DAF_bridge_env_vs_FErigid=envdyn_brg/envrig_brg, DAF_bridge_case_max_vs_simRB=daf_case_brg, DAF_bridge_case_max_vs_FErigid=daf_case_brg_fe, RF_bridge_dyn=rf_b,
                                              RF_bridge_if_whole_dyn_hub=350.0/(KF*sig(envdyn_hub)),
                                              arm_root_M_dyn_env=arm_env_dyn, arm_root_M_FEqs_env=arm_env_qs, DAF_arm_env_vs_FEqs=arm_env_dyn/arm_env_qs, DAF_arm_case_max_vs_FEqs=arm_case,
                                              corr_qs_simRB_min=min(res[nm]['corr_qs_vs_simRB_Mz'] for nm in gov_names), qs_over_simRB_Mz_ratio_gov=[res[nm]['qs_over_simRB_Mz_ratio_lsq'] for nm in gov_names])
            cn = ('Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz'); dk = ('hub_Fx', 'hub_Fy', 'hub_Fz', 'hub_Mx', 'hub_My', 'hub_Mz')
            comp_env = {}
            for k, (c_, d_) in enumerate(zip(cn, dk)):
                ed = max(res[nm]['dyn'][d_] for nm in sel); er = max(res[nm]['sim_rb']['comps'][k] for nm in sel)
                # case-max over cases whose RB component is >= 50 % of the envelope
                cm = max(res[nm]['dyn'][d_]/res[nm]['sim_rb']['comps'][k] for nm in sel if res[nm]['sim_rb']['comps'][k] >= 0.5*er)
                comp_env[c_] = dict(env_dyn=ed, env_RB=er, env_ratio=ed/er, case_max_ratio_gov=cm)
            out['runs'][key+'|summary']['components'] = comp_env
            out['runs'][key+'|summary']['DAF_hub_judge_vs_simRB'] = max(max(v['env_ratio'], v['case_max_ratio_gov']) for v in comp_env.values())
            s = out['runs'][key+'|summary']
            print('zeta %.0f %%: hub Mz env dyn %.2f / FE-rigid %.2f / sim RB %.2f N m -> DAF env %.2f (vs sim RB), %.2f (vs FE rigid); case-max %.2f / %.2f.  Bridge |(My,Mz)| at mouth env dyn %.2f / FE-rigid %.2f / sim RB(total wrench) %.2f -> DAF env %.2f (vs sim RB), %.2f (vs FE rigid); case-max %.2f / %.2f; RF_bridge(dyn) %.2f' % (
                zeta*100, envdyn_hub, envrig_hub, envrb, s['DAF_hub_env_vs_simRB'], s['DAF_hub_env_vs_FErigid'], daf_case_hub, daf_case_hub_fe, envdyn_brg, envrig_brg, envrb_my_mz, s['DAF_bridge_env_vs_simRB'], s['DAF_bridge_env_vs_FErigid'], daf_case_brg, daf_case_brg_fe, rf_b), flush=True)
            print('    components (dyn env / sim RB env / env ratio / case-max ratio over cases with RB >= 50 % env): ' + '; '.join('%s %.1f/%.1f/%.2f/%.2f' % (c_, v['env_dyn'], v['env_RB'], v['env_ratio'], v['case_max_ratio_gov']) for c_, v in comp_env.items()))
            if (bridge, corner, zeta) == ('asbuilt', 'nom', 0.01) or quick:
                print('| case | sim RB Mz (N m) | FE rigid Mz | dyn Mz | DAF vs sim RB | bridge |(My,Mz)| sim RB / FE rigid / dyn | arm-root bending peak (4 arms, dyn, N m) | pad stroke max mm | bottoms (> 20 mm) |')
                print('|---|---|---|---|---|---|---|---|---|')
                for nm, d_, r_, s_ in dn:
                    print('| %s | %.2f | %.2f | %.2f | %.2f | %.2f / %.2f / %.2f | %s | %.1f | %s |' % (nm, s_['Mz'], r_['hub_Mz'], d_['hub_Mz'], d_['hub_Mz']/s_['Mz'], s_['My_Mz'], r_['brg_M'], d_['brg_M'], ' / '.join('%.2f' % a for a in d_['arm_M']), meta[nm]['stroke_max_mm'], 'YES' if meta[nm]['bottoming'] else 'no'))
        print('frame wall %.0f s' % (time.time()-t0), flush=True)
    np.savez_compressed(os.path.join(FEA, 't076c_d1_hubwrench.npz'), **{'%s|%s' % k: v for k, v in SER.items()})
    sm = {k: v for k, v in out['runs'].items() if k.endswith('|summary')}
    out['overall'] = dict(DAF_hub_env_vs_simRB_max=max(v['DAF_hub_env_vs_simRB'] for v in sm.values()), DAF_hub_casemax_vs_simRB_max=max(v['DAF_hub_case_max_vs_simRB'] for v in sm.values()),
                          DAF_hub_judge_vs_simRB_max=max(v['DAF_hub_judge_vs_simRB'] for v in sm.values()), DAF_hub_env_vs_FEqs_max=max(v['DAF_hub_env_vs_FErigid'] for v in sm.values()), DAF_hub_casemax_vs_FEqs_max=max(v['DAF_hub_case_max_vs_FErigid'] for v in sm.values()),
                          DAF_bridge_env_vs_simRB_max=max(v['DAF_bridge_env_vs_simRB'] for v in sm.values()), DAF_bridge_casemax_vs_simRB_max=max(v['DAF_bridge_case_max_vs_simRB'] for v in sm.values()),
                          DAF_bridge_env_vs_FEqs_max=max(v['DAF_bridge_env_vs_FErigid'] for v in sm.values()), DAF_bridge_casemax_vs_FEqs_max=max(v['DAF_bridge_case_max_vs_FErigid'] for v in sm.values()),
                          RF_bridge_dyn_min=min(v['RF_bridge_dyn'] for v in sm.values()), RF_bridge_if_whole_dyn_hub_min=min(v['RF_bridge_if_whole_dyn_hub'] for v in sm.values()))
    print('\n## OVERALL (max over the %d frame / damping runs): ' % len(sm) + json.dumps({k: round(v, 3) for k, v in out['overall'].items()}))
    json.dump(out, open(os.path.join(HERE, 'step2_d1%s.json' % ('_quick' if quick else '')), 'w'), indent=1)
    print('\ndone %.0f s' % (time.time()-t0))


if __name__ == '__main__':
    main()
