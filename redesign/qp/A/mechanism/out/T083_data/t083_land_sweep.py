"""T-083 step 2a: pad plateau at the T-083 mass. Category: rigid-body dynamics (landing_a.simulate, unchanged; 23 cases of landing_path_a.cases(False)).
Basis: predicted mass and tallied CG from argv (CAD mass model 'cad', the T-077 p6 method), usable stroke 24 mm (pad_geometry as D-222 s4.1), 1.2 m/s hard cases.
For each plateau Fp: worst stroke, peak n, end tilt, peak foot force over the 23 cases at pad zeta and face mu given.
python -I t083_land_sweep.py MASS_KG CG_MM ZETAS MUS FP1 [FP2 ...]     e.g. 1.912 25.92 0.02 0.40,0.30 33.6 35 37      (prints; writes nothing)"""
import os, sys, time
mass, cg = sys.argv[1], sys.argv[2]
os.environ['LAND_MASS_KG'] = mass; os.environ['LAND_CG_X_MM'] = cg; os.environ['LAND_MASS_MODEL'] = 'cad'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', 'T076d_data')))
sys.dont_write_bytecode = True
import numpy as np
import t076d_step2_table as T2
T2.MASS = float(mass)
zetas = [float(z) for z in sys.argv[3].split(',')]; mus = [float(m) for m in sys.argv[4].split(',')]; fps = [float(f) for f in sys.argv[5:]]
c = T2.ctx(); P, L = c['P'], c['L']; L.MASS_MODEL = 'cad'; T2.pts_for('cad')
smax = 0.024; xf, zf, _ = T2.pad_geometry(smax); P.set_pad(xf, zf)
t0 = time.time()
print('# mass %.3f kg, CG x %s mm (model CG %s mm), stroke %.0f mm, x_foot %.4f z_foot %.4f' % (T2.MASS, cg, np.round(c['cg'] * 1e3, 2), smax * 1e3, xf, zf))
print('| Fp N | zeta | mu | worst stroke mm (of 24) | case | peak n g | end tilt deg | case | peak foot N |')
print('|---|---|---|---|---|---|---|---|---|')
for Fp in fps:
    for zeta in zetas:
        for mu in mus:
            st = dict(stroke=(0, ''), n=0, tilt=(0, ''), F=0)
            for name, kw in P.cases(False):
                r = L.simulate(m=T2.MASS, Fp=Fp, s_max=smax, zeta=zeta, mu=mu, dt=2e-4, T=1.5, trace=False, **dict(kw, x_foot=xf, z_foot=zf))
                s_ = float(r['dmax_mm'].max()); t_ = float(r['tilt_end'])
                if s_ > st['stroke'][0]: st['stroke'] = (s_, name)
                if t_ > st['tilt'][0]: st['tilt'] = (t_, name)
                st['n'] = max(st['n'], float(r['n_peak'])); st['F'] = max(st['F'], float(r['F'].max()))
            print('| %.1f | %.2f | %.2f | %.2f | %s | %.2f | %.2f | %s | %.1f |' % (Fp, zeta, mu, st['stroke'][0], st['stroke'][1], st['n'], st['tilt'][0], st['tilt'][1], st['F']), flush=True)
print('done %.0f s' % (time.time() - t0))
