"""T-089 part 1: rate-loop gain margin (D-191 method, unchanged) on the CURRENT configuration.
Category: linear control analysis on an FEA-lite beam-frame modal model (sitl/fu_cage.py with configure("t089")); no sim round, no SITL.
Plant: X2216 V3 880KV on APC 9x4.5MR (prop_a.py, T-083), Q_M_SPIN_MAX 1.0, A.param D-191 gains, cant 17 deg.
Structure: structures/fe_a.py with the T-085 options (wing cell nominal / lower, hub joint 6061 / PETG, pad 30 / 50 / 70 A or pack rigid, tray 24 / 112 mm) at kd / nom / hi,
  exactly the 24 bound groups of T-085 (t085_bounds.py CASES).  FC (IMU) at the spar centre node (hard mount on the wing skin, D-186).
D-191 pass rule (iter3_run.py s4, unchanged): GM >= 2.0 on every axis, corner, damping 0.3 / 1 %, thrust scale 0.77 / 1.0 / 1.25, no RHP pole; flexible modes x 1.0 (gm_nominal), x 0.8 (gm_shifted), x 1.2 (gm_shifted_up).
Inertia variants: 'FE' = the FE's own rigid inertia (declared masses, point lumps: FE mass about 1.64 kg); 'CAD' = loop gain rescaled by I_FE / I_target with
  I_target = cad_mass.json I_cad_axes x (1.8796 / 1.63298) (tallied predicted mass over CAD basic mass).  The reported value is the minimum over both.
python -I t089_gm.py [group-limit]   -> t089_gm.json, t089_gm.md, stdout"""
import os, sys, math, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'T085_data')); sys.path.insert(0, os.path.join(HERE, '..', 'T084_data'))
sys.path.insert(0, os.path.join(QPA, 'sitl')); sys.path.insert(0, os.path.join(QPA, 'structures')); sys.dont_write_bytecode = True
import warnings; warnings.filterwarnings('ignore')
import numpy as np

KINDS = ('kd', 'nom', 'hi')
SCALES = (1.0, 0.8, 1.2)
ZETAS = (0.003, 0.01)
TSCALES = (0.77, 1.0, 1.25)
M_PRED, M_BASIC = 1.8796, 1.63298
AX_IAXIS = {'pit': 'Iyy', 'rll': 'Izz', 'yaw': 'Ixx'}       # copter pitch about the spar (y), roll about z (belly), yaw about x (hover down axis): fu_cage.py header


def groups():
    import t085_modes as T
    import t085_bounds as B
    for k, v in B.CASES.items(): T.PACKS[k] = v
    names = list(B.CASES) + ['rigid+rot']
    out = []
    for cell in ('nominal', 'lower'):
        for hub in ('al6061', 'petg'):
            for nm in names:
                out.append((cell, hub, nm))
    return T, out


def gm_scan(L):
    """first loop-gain factor k in geomspace(1, 100, 300) at which a closed-loop pole reaches Re >= -1e-9; 1.0 if unstable at k = 1; inf if none.  Same scan as fu_cage.margins()[0]."""
    import fu_cage as FC
    A, B, C, D = L
    BC = B @ C
    for k in np.geomspace(1.0, 100, 300):
        if float(np.max(np.linalg.eigvals(A - k * BC).real)) >= -1e-9: return float(k)
    return float('inf')


def run_group(args):
    cell, hub, nm, i_cad, only = args
    import fu_cage as FC
    FC.configure('t089')
    T, _ = groups()
    out = {'cell': cell, 'hub': hub, 'pad': nm, 'rows': []}
    for kind in KINDS:
        F, res = T.solve(kind, cell, hub, nm)
        C = FC.cases_frame(F, kind)
        for c in C:
            if c['node'] != 'spar centre': continue
            ax = c['ax']; I_fe = 1.0 / c['inv_I']; I_t = i_cad[AX_IAXIS[ax]] * M_PRED / M_BASIC
            flex = [(ff, gg) for ff, gg in c['flex']]
            row = {'kind': kind, 'ax': ax, 'I_fe': I_fe, 'I_target': I_t, 'n_flex': len(flex),
                   'flex_3_40': [(round(ff, 2), round(gg / c['inv_I'], 3)) for ff, gg in flex if 3 < ff < 40], 'gm': {}}
            for var, ks in (('FE', 1.0), ('CAD', I_fe / I_t)):
                for sc in SCALES:
                    modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c['modes']]
                    gm = 99.0; arg = None
                    for z in ZETAS:
                        for ts in TSCALES:
                            L = FC.loop(modes, ax, z, tfull_scale=ts, kscale=ks, **FC.A_PARAM_D191[ax])
                            if FC.maxre(L) >= -1e-6: g = 1.0
                            else: g = gm_scan(L)
                            if g < gm: gm = g; arg = (z, ts)
                    row['gm'][f'{var}|{sc}'] = (gm, arg)
            out['rows'].append(row)
    return out


if __name__ == '__main__':
    import fu_cage as FC
    FC.configure('t089')
    cadm = json.load(open(os.path.join(QPA, 'sitl', 'cad_mass.json')))
    i_cad = cadm['I_cad_axes_kgm2']
    T, G = groups()
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else len(G)
    G = G[:lim]
    print('TFULL %.3f N per motor, KQ_SHAFT %.4f m, yaw arm %.4f m, config %s' % (FC.TFULL, FC.KQ_SHAFT, FC.RATE['yaw']['arm'], FC.CONFIG), flush=True)
    t0 = time.time()
    from concurrent.futures import ProcessPoolExecutor
    nproc = min(os.cpu_count() or 1, 8)
    with ProcessPoolExecutor(nproc) as ex:
        results = list(ex.map(run_group, [(c, h, n, i_cad, None) for (c, h, n) in G]))
    print('done %d groups in %.0f s (%d procs)' % (len(results), time.time() - t0, nproc), flush=True)
    json.dump(dict(tfull=FC.TFULL, kq=FC.KQ_SHAFT, yaw_arm=FC.RATE['yaw']['arm'], i_cad=i_cad, m_pred=M_PRED, m_basic=M_BASIC, groups=results), open(os.path.join(HERE, 't089_gm.json'), 'w'), indent=1)
