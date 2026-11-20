"""T-073 step 4 helper: 23 landing cases (same set and pad geometry as T-071 skin_main: PAD_D2, plateau 30 N, dt 2e-4), rigid-body dynamics via landing_a.simulate.
Saves per-case foot-force traces and pack-referred accelerations to t076_traces.pkl.  Run: python -I t073_traces.py (cwd anywhere)."""
import sys, os, pickle, math
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "structures"))
sys.path.insert(0, S)
import numpy as np
import landing_path_a as LP
import landing_a as L
G = 9.81; M = L.M_GATE; DT = 2e-4
LP.set_pad(LP.PAD_D2["x_foot"], LP.PAD_D2["z_foot"])
out = {}
for name, kw in LP.cases(False):
    r = L.simulate(Fp=30.0, dt=DT, T=1.5, trace=True, **dict(kw, **LP.PAD_D2))
    FB = r['trace'].reshape(-1, 4, 3)
    t = np.arange(len(FB))*DT
    lam = np.where(t < 0.3, 0.667, np.maximum(0.0, 0.667*(1-(t-0.3)/0.3)))
    Fx = FB[:, :, 0].sum(1); Fy = FB[:, :, 1].sum(1); Fz = FB[:, :, 2].sum(1)
    # per unit pack mass: axial load factor on the pack (x: aft lip), lateral y, lateral z
    ax = (np.abs(Fx)/M + lam*G)          # m/s2: N_x = m_pack * ax  (pack on the aft lip: a_up + g = Fc/M + lam g)
    ay = np.abs(Fy)/M; az = np.abs(Fz)/M
    out[name] = dict(ax_pk=float(ax.max()), ay_pk=float(ay.max()), az_pk=float(az.max()), n_pk=float(r['n_peak']), FB=FB)
    print(f"{name:30s} ax {ax.max()/G:6.2f} g  ay {ay.max()/G:5.2f} g  az {az.max()/G:5.2f} g  n_peak(landing_a) {r['n_peak']:.2f}", flush=True)
pickle.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "t076_traces.pkl"), "wb"))
