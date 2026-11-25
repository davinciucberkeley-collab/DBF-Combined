"""T-083 COPY of T077p6_data/t077p6_demand.py (method unchanged) at the T-083 mass and CG with the plateau rescaled: Fp 36 N, usable stroke 24 mm (t083_land_sweep.py: 36 N is the lowest
round plateau with end tilt <= 3.0 deg and no bottoming at 1.912 kg; 30 x 1.912 / 1.705 = 33.6 N tilts 3.14 deg). Mass and CG from the environment (T083_MASS, T083_CG; defaults 1.913 kg, 24.41 mm after the 3 mm cage shift; first run at 1.912 kg / 25.92 mm before it).
Outputs: T083_data/fea/demand_t083.npz (git-ignored) and demand_t083.json.
T-083 FIX: simulate() now gets m=T2.MASS. The p6 script called it without m, so landing_a.M_GATE was used, and that is 1.64 kg: t076d_step2_table sets
LAND_MASS_KG=1.64 at import, before landing_a is imported (the p6 demand labelled 1.705 kg was simulated at 1.64 kg; the split used 1.705 kg).
T-077 p6 step 1: landing demand for the node / clamshell / cup / clamp / boss strength rows.  Category: rigid-body dynamics (landing_a.simulate, unchanged) + d'Alembert wrench split (generalised T-076d step 2 / T-071b A.1).
    python -I t077p6_demand.py        (about 3-5 min)
Basis (D-222 chosen pad, D-223): Fp 30 N, usable stroke 24 mm, pad zeta 0.02 / 0.05 / 0.10, CAD mass model (landing_mass_cad) scaled to the PREDICTED mass 1.705 kg (T-077 p5 tally 1.7046), CG x 23.91 mm (p5 tallied),
23 cases of landing_path_a.cases(False), mu 0.40 (landing_a default = the T-076d / D-223 basis) and 0.30 (T-071b / T-076 printed-part practice), both kept.  Output: fea/demand_p6.npz (git-ignored): foot forces FB (n,4,3), hub / R / L wrench about P0 and the strut / pack / FC inertial series per case and zeta."""
import os, sys, json, math, time
HERE = r'C:/Users/dillo/AppData/Local/Temp/claude/1dc032cbc6faa005/7cb35b0a-c71b-43ed-9be1-fbe0a7ff151f/scratchpad/t083b_dem'
S_DIR = r'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/structures'
D076 = r'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/mechanism/out/T076d_data'
MASS_T083 = os.environ.get('T083_MASS', '1.913'); CG_T083 = os.environ.get('T083_CG', '24.41')
os.environ['LAND_MASS_KG'] = MASS_T083; os.environ['LAND_CG_X_MM'] = CG_T083; os.environ['LAND_MASS_MODEL'] = 'cad'
sys.path.insert(0, S_DIR); sys.path.insert(0, D076); sys.dont_write_bytecode = True
import numpy as np
import t076d_step2_table as T2
T2.MASS = float(MASS_T083)

def split3(FBt, pts, x_foot, y_foot, z_foot):
    """wrench the CENTRE exerts on hub side / R half / L half about P0 (rigid-body d'Alembert; as landing_centre_a.wrench_split on the CAD point-mass model of T2.pts_for)."""
    c = T2.ctx(); cg = c['cg']; P0 = c['P0']
    m = sum(p[0] for p in pts); cgp = np.array([sum(p[0] * p[i] for p in pts) / m for i in (1, 2, 3)]); dsh = cg - cgp
    feet = np.array([[x_foot, sy * y_foot, sz * z_foot] for sy in (1, -1) for sz in (1, -1)]); rf = feet - cg
    Ib = np.zeros((3, 3))
    for g, x, y, z, idx in pts:
        r = np.array([x, y, z]) + dsh - cg; Ib += g * ((r @ r) * np.eye(3) - np.outer(r, r))
    Ibi = np.linalg.inv(Ib); Ftot = FBt.sum(axis=1); Mcg = np.zeros_like(Ftot)
    for i in range(4): Mcg += np.cross(np.broadcast_to(rf[i], FBt[:, i, :].shape), FBt[:, i, :])
    a_cg = Ftot / m; alpha = Mcg @ Ibi.T; z0 = np.zeros_like(Ftot)
    Fo = {k: z0.copy() for k in ('hub', 'R', 'L')}; Mo = {k: z0.copy() for k in ('hub', 'R', 'L')}
    for g, x, y, z, idx in pts:
        pos = np.array([x, y, z]) + dsh; rho = pos - cg; s = pos - P0
        f = g * (a_cg + np.cross(alpha, np.broadcast_to(rho, alpha.shape))); mom = np.cross(np.broadcast_to(s, f.shape), f)
        if idx in (2, 3, 4, 6): Fo['hub'] += f; Mo['hub'] += mom
        else:
            w_ = 1.0 if y > 1e-9 else (0.0 if y < -1e-9 else 0.5)
            Fo['R'] += w_ * f; Mo['R'] += w_ * mom; Fo['L'] += (1 - w_) * f; Mo['L'] += (1 - w_) * mom
    for k_, key in ((0, 'R'), (1, 'L')):
        for j in (0, 1):
            f = FBt[:, 2 * k_ + j, :]; s = feet[2 * k_ + j] - P0; Fo[key] -= f; Mo[key] -= np.cross(np.broadcast_to(s, f.shape), f)
    chk = np.abs(Fo['hub'] + Fo['R'] + Fo['L']).max() + np.abs(Mo['hub'] + Mo['R'] + Mo['L']).max()
    return {k: (Fo[k], Mo[k]) for k in Fo}, chk, a_cg, alpha, dsh


def main():
    t0 = time.time(); np.seterr(all='ignore'); c = T2.ctx(); P, L = c['P'], c['L']
    Fp, smax = float(os.environ.get('T083_FP', '36.0')), 0.024; xf, zf, _ = T2.pad_geometry(smax)
    L.MASS_MODEL = 'cad'; P.set_pad(xf, zf); pts = T2.pts_for('cad'); out = {}; names = []; mx = 0
    print('# pad Fp %.0f N, stroke %.0f mm, x_foot %.4f z_foot %.4f, mass %.3f kg, CG %s' % (Fp, smax * 1e3, xf, zf, T2.MASS, np.round(c['cg'] * 1e3, 2)), flush=True)
    stats = {}
    for zeta, mu in [(z_, m_) for z_ in (0.02, 0.05, 0.10) for m_ in (0.40, 0.30)]:
        for name, kw in P.cases(False):
            r = L.simulate(m=T2.MASS, Fp=Fp, s_max=smax, zeta=zeta, mu=mu, dt=2e-4, T=1.5, trace=True, **dict(kw, x_foot=xf, z_foot=zf)); FB = r['trace'].reshape(-1, 4, 3)
            w, chk, a_cg, alpha, dsh = split3(FB, pts, xf, c['geom']['y_foot'], zf); mx = max(mx, chk)
            key = '%.2f|%.2f|%s' % (zeta, mu, name)
            out[key + '|FB'] = FB.astype(np.float32); out[key + '|a_cg'] = a_cg.astype(np.float32); out[key + '|alpha'] = alpha.astype(np.float32)
            for k in w: out[key + '|%s|F' % k] = w[k][0].astype(np.float32); out[key + '|%s|M' % k] = w[k][1].astype(np.float32)
            s_ = stats.setdefault((zeta, mu), dict(stroke=0, n=0, tilt=0, Ffoot=0)); s_['stroke'] = max(s_['stroke'], float(r['dmax_mm'].max())); s_['n'] = max(s_['n'], float(r['n_peak'])); s_['tilt'] = max(s_['tilt'], float(r['tilt_end'])); s_['Ffoot'] = max(s_['Ffoot'], float(r['F'].max()))
            if zeta == 0.02 and mu == 0.40: names.append(name)
        print('zeta %.2f mu %.2f done [%.0f s] stats %s' % (zeta, mu, time.time() - t0, stats[(zeta, mu)]), flush=True)
    out['names'] = np.array(names)
    os.makedirs(os.path.join(HERE, 'fea'), exist_ok=True); np.savez_compressed(os.path.join(HERE, 'fea', 'demand_t083.npz'), **out)
    json.dump(dict(Fp=Fp, smax=smax, xf=xf, zf=zf, mass=T2.MASS, cg=list(map(float, c['cg'])), sum_to_zero_max=mx, stats={str(k): v for k, v in stats.items()}, pts=[list(map(float, p[:4])) + [int(p[4])] for p in pts]), open(os.path.join(HERE, 'demand_t083.json'), 'w'), indent=1)
    print('sum-to-zero residual max %.2e; done %.0f s' % (mx, time.time() - t0))

if __name__ == '__main__': main()
