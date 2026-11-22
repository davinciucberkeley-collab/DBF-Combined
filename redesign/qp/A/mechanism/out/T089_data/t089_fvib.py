"""T-089 part 2: forced response (FC and motors) of the T-085 upgraded model, incl. its governing 94.6-108.7 Hz mode.
Category: FEA-lite modal forced response on the beam-frame FE (fe_a.py, T-085 options); no shell / solid FEA, no CFD, no flight dynamics.
Method = structures/structures_a.py s4 (modal_resp / mode_res), copied unchanged: 1P unbalance U = 1.0 g mm per rotor (force U w^2 in the motor y and z), 2P ripple 5 % of the static
  thrust (APC static row x derate 0.93, prop_a.py) in the motor x; four rotors in the worst phase (sum of |phi|), every solved mode summed with absolute values (conservative),
  modal damping zeta 1 % and 0.5 % (structures_a.py ZET1 / ZET, EST, no test), rpm 6,000-11,415 step 25, FC at the spar centre node (hard mount, D-186).
Limit = A-P10(b) FC <= 30 m/s2 (gen_params_a.py req.vibe_max_ms2), compared on the sum of the three axes (a bound on the per-axis VIBE), as structures_run.md s4.
Groups = the 24 T-085 bound groups (t085_bounds.py) x kd / nom / hi.  Regression: spar-only default build (130 modes) vs structures_run.md s4 sweep table.
python -I t089_fvib.py   -> t089_fvib.json, stdout"""
import os, sys, math, json, time, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'T085_data')); sys.path.insert(0, os.path.join(HERE, '..', 'T084_data'))
sys.path.insert(0, os.path.join(QPA, 'structures')); sys.dont_write_bytecode = True
import warnings; warnings.filterwarnings('ignore')
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    sys.path.insert(0, QPA); import prop_a as PA
KINDS = ('kd', 'nom', 'hi')
UUN = 1e-6                 # 1.0 g mm = 1e-6 kg m (structures_a.py Uun)
ZETS = (0.01, 0.005)       # structures_a.py ZET1, ZET
RPM_MIN, RPM_MAX = 6000.0, 11415.0
RR = np.arange(RPM_MIN, RPM_MAX + 1, 25.0)
LIMIT = 30.0
NMODES = 400


def thrust_static(rpm): return PA.prop(rpm)[0] * PA.DER


def solve(T, kind, cell, hub, pack, n=NMODES):
    import fe_a
    from t084_modes_probe import fekw
    import t084_cell_props as CP
    cl = None if cell == 'spar' else CP.cell_for(kind, lower=(cell == 'lower'))
    kw = fekw(wing_cell=cl)
    if hub != 'rigid': kw['hub_se'] = T.HUB[hub]
    if T.PACKS[pack] is not None: kw['pack_cfg'] = T.PACKS[pack]
    F, info = fe_a.build(kind, **kw); return F, F.solve(n)


class Modal:
    """modal data of one solved frame: per mode f, motor participation (1P: |vy|+|vz| summed over motors, 2P: |vx|), FC and motor responses"""
    def __init__(self, F, res):
        idx = F._idx; self.F = F; self.res = res
        mots = [m for m in idx if (m.startswith('m+') or m.startswith('m-')) and '>' not in m]; self.mots = mots
        self.f = np.array([r[0] for r in res]); V = np.array([r[2] for r in res])          # V: modes x dofs
        self.g1 = np.array([sum(abs(v[6 * idx[q] + 1]) + abs(v[6 * idx[q] + 2]) for q in mots) for v in V])
        self.g2 = np.array([sum(abs(v[6 * idx[q]]) for q in mots) for v in V])
        self.fc = np.array([[abs(v[6 * idx['s+0.000'] + q]) for q in range(3)] for v in V])           # |phi| at the FC, 3 axes
        self.mot = {m: np.array([[abs(v[6 * idx[m] + q]) for q in range(3)] for v in V]) for m in mots}
        self.cx = np.array([r[3] for r in res]); self.cy = np.array([r[4] for r in res])

    def resp(self, rpm, zeta, orders=('1P', '2P'), phi=None, mask=None):
        """per-axis acceleration (3,) at the node whose |phi| (modes x 3) is phi, summed over modes and orders"""
        phi = self.fc if phi is None else phi
        om = rpm / 60 * 2 * math.pi; thr = thrust_static(rpm); a = np.zeros(3)
        wi = 2 * math.pi * self.f
        for tag, mult, fm, g in (('1P', 1, UUN * om ** 2, self.g1), ('2P', 2, 0.05 * thr, self.g2)):
            if tag not in orders: continue
            w = mult * om; h = 1.0 / np.sqrt((wi * wi - w * w) ** 2 + (2 * zeta * wi * w) ** 2)
            c = w * w * fm * g * h
            if mask is not None: c = c * mask
            a += (c[:, None] * phi).sum(axis=0)
        return a


def sweep(M, zeta, phi=None):
    A = np.array([M.resp(r, zeta, phi=phi) for r in RR]); return A


def summarize(M, zeta):
    A = sweep(M, zeta); tot = A.sum(axis=1); k = int(np.argmax(tot))
    s = dict(worst=float(tot[k]), rpm=float(RR[k]), per_axis=float(A.max(axis=0).max() / math.sqrt(2)),
             le10343=float(tot[RR <= 10343].max()), le9349=float(tot[RR <= 9349].max()), hover_window=float(tot[(RR >= 6789) & (RR <= 8028)].max()))
    # motors
    mw = 0.0; mrpm = 0.0; mpa = 0.0
    for m, phi in M.mot.items():
        Am = sweep(M, zeta, phi=phi); tm = Am.sum(axis=1); km = int(np.argmax(tm))
        if tm[km] > mw: mw, mrpm = float(tm[km]), float(RR[km])
        mpa = max(mpa, float(Am.max() / math.sqrt(2)))
    s.update(motor_worst=mw, motor_rpm=mrpm, motor_per_axis=mpa)
    # share of the governing mode (94-110 Hz, cy >= 0.5 or cx >= 0.5) in the FC worst point
    gov = (M.f > 90) & (M.f < 115) & ((M.cx >= 0.5) | (M.cy >= 0.5))
    s['gov_f'] = [float(x) for x in M.f[gov]]
    sh = M.resp(RR[k], zeta, mask=gov.astype(float)).sum(); s['gov_share_at_worst'] = float(sh / tot[k])
    # governing mode alone, peak over the sweep
    Ag = np.array([M.resp(r, zeta, mask=gov.astype(float)).sum() for r in RR]); kg = int(np.argmax(Ag)); s['gov_peak'] = float(Ag[kg]); s['gov_peak_rpm'] = float(RR[kg])
    # single-mode on resonance of the governing mode (structures_a.mode_res semantics): 1P if 60 f in 6000..11415, 2P if 30 f in range
    out = []
    for i in np.where(gov)[0]:
        f = M.f[i]; wi = 2 * math.pi * f; r1 = 60 * f; r2 = 30 * f; v = []
        if RPM_MIN <= r1 <= RPM_MAX: v.append(('1P', r1, UUN * wi ** 2 * M.g1[i] / (2 * zeta) * M.fc[i].sum()))
        if RPM_MIN <= r2 <= RPM_MAX: v.append(('2P', r2, 0.05 * thrust_static(r2) * M.g2[i] / (2 * zeta) * M.fc[i].sum()))
        out.append((float(f), v, float(M.cx[i]), float(M.cy[i])))
    s['gov_resonance'] = out
    return s


def run_group(args):
    cell, hub, nm = args
    import t085_modes as T, t085_bounds as B
    for k, v in B.CASES.items(): T.PACKS[k] = v
    out = {'cell': cell, 'hub': hub, 'pad': nm, 'rows': []}
    for kind in KINDS:
        F, res = solve(T, kind, cell, hub, nm)
        M = Modal(F, res)
        for z in ZETS:
            s = summarize(M, z); s.update(kind=kind, zeta=z, fmax=float(M.f.max()), nmodes=len(M.f)); out['rows'].append(s)
    return out


def regression():
    """spar-only default build, 130 modes: compare with structures_run.md s4 sweep table"""
    import t085_modes as T
    rows = []
    for kind in KINDS:
        F, res = solve(T, kind, 'spar', 'rigid', 'lump', n=130); M = Modal(F, res)
        for z in ZETS:
            A = sweep(M, z); tot = A.sum(axis=1); k = int(np.argmax(tot))
            rows.append((kind, z, float(tot[k]), float(RR[k]), float(A.max(axis=0).max() / math.sqrt(2)), float(tot[RR <= 10343].max()), float(tot[RR <= 9349].max())))
    return rows


if __name__ == '__main__':
    t0 = time.time()
    reg = regression()
    print('REGRESSION spar-only, 130 modes (structures_run.md s4: kd 26.5/26.6 at 11,400, nom 23.7, hi 22.7; per-axis 11.1/10.8/11.0; <=10343 19.1/18.5/18.5; <=9349 15.1/15.0/15.2)')
    for r in reg: print('  %s zeta %.3f worst %.1f at %d per-axis %.1f <=10343 %.1f <=9349 %.1f' % r, flush=True)
    import t085_modes as T, t085_bounds as B
    names = list(B.CASES) + ['rigid+rot']
    G = [(c, h, n) for c in ('nominal', 'lower') for h in ('al6061', 'petg') for n in names]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(min(os.cpu_count() or 1, 8)) as ex: results = list(ex.map(run_group, G))
    print('done %d groups in %.0f s' % (len(results), time.time() - t0), flush=True)
    json.dump(dict(regression=reg, groups=results, limit=LIMIT), open(os.path.join(HERE, 't089_fvib.json'), 'w'), indent=1)
