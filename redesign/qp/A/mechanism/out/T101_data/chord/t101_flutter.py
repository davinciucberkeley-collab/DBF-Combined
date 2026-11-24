"""T-101 U2 COPY of T077p8_data/t077p8_flutter.py: elevon chord fraction 0.25 -> 0.30 (hinge x 183.75 -> 171.50 mm), elevon WNG-006 7.6 g (was 6.7), lead 10.0 g at 20 mm (unchanged),
damper c DMP_C 1.0297e-3 unchanged. Same five cases A-E, K grid, corners, pass limit (no instability <= 28.8 m/s = 1.2 VD).
Usage: python t101_flutter.py [new|old]   (plain python: multiprocessing spawn imports this file; old = pre-change inputs, like-for-like baseline).
fixes2_run.wing_modes hard-codes the lump x at 0.18375 - arm; this copy passes the hinge position (CH*(1-cf)) through its own wing_modes / run_case (original untouched).
setup(me, cf) sets flutter_a EL_CF and C_H from cf (read: C_H = ((1-cf)*CH - 0.5*CH)/B), so the section model follows cf."""
import os, sys, json, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); SD = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "structures"))
sys.path.insert(0, SD)
import numpy as np
import fixes2_run as R
F = R.F
def wing_modes(corner, lead, arm, cf):
    xh = (1 - cf) * F.CH
    f, _ = F.wing_flutter(corner, lumps=(((lead + 0.5 + 2.0) * 1e-3, xh - arm, 0.285),)); return f[0], f[1]
def run_case(args):
    name, corner, me, lead, arm, cf, cdamp = args
    R.setup(me, cf); fh, fa = wing_modes(corner, lead, arm, cf)
    Cd = None
    if cdamp: Cd = np.zeros((3, 3)); Cd[2, 2] = cdamp / R.SPAN
    zr, kz, nunst, band = -1.0, None, 0, []
    vmin, kv = 99.0, None
    for i, Kb in enumerate(R.KG):
        M, K = F.elevon_section(fh, fa, Kb, xb_bal=arm, mbal=(lead + 0.5) * 1e-3 / R.SPAN)
        z = R.zeta_req(M, K, F.C_H, Cd=Cd)
        if z > 1e-9: nunst += 1; band.append(Kb)
        if z > zr: zr, kz = z, Kb
        if i % 3 == 0:
            o = R.onset(M, K, F.C_H, Cd)
            if o is not None and o < vmin: vmin, kv = o, Kb
    return dict(name=name, corner=corner, fh=fh, fa=fa, zr=zr, kz=kz, nunst=nunst, band=(min(band), max(band)) if band else None, vmin=vmin, kv=kv)
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "new"
    cm = json.load(open(os.path.join(SD, "..", "sitl", "cad_mass.json")))["elevon"]
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    # new = 0.30 c, lead 14.0 g (ladder rung b, final); new10 = 0.30 c with the pre-ladder lead 10.0 g (case E fails); old = pre-change baseline
    if mode == "new": me, lead, arm, cf = 0.0076, 14.0, 0.020, 0.30
    elif mode == "new10": me, lead, arm, cf = 0.0076, 10.0, 0.020, 0.30
    else: me, lead, arm, cf = 0.0067, 10.0, 0.020, 0.25
    ce = cf * 0.245
    P("Mode %s: cf %.2f, hinge x %.2f mm, elevon %.1f g, lead %.1f g at %.0f mm" % (mode, cf, (1 - cf) * 245, me * 1e3, lead, arm * 1e3))
    Ih_sec = me * ce * ce / 3 + (lead + 0.5) * 1e-3 * arm ** 2
    P("Hinge inertia per elevon: CAD %.3e kg m2 (cad_mass.json: elevon %.3e + balance %.3e; CAD file is the NEW design); section-model inputs here me %.1f g plate c^2/3 + (lead+tabs) x 20 mm^2 = %.3e" % (
        cm["hinge_inertia_total_kgm2"], cm["hinge_inertia_one_elevon_kgm2"], cm["hinge_inertia_balance_one_kgm2"], me * 1e3, Ih_sec))
    P("Elevon CG aft of the hinge (CAD, new): unbalanced %.2f mm, balanced %.2f mm" % (cm["cg_aft_of_hinge_unbalanced_m"] * 1e3, cm["cg_aft_of_hinge_balanced_m"] * 1e3))
    P()
    C0 = 1.0297e-3
    cases = [("A no damper, lead %.1f g, elevon %.1f g" % (lead, me * 1e3), me, lead, arm, cf, 0.0),
             ("B damper hot 50 C (EST x0.6), lead %.1f g" % lead, me, lead, arm, cf, 0.6 * C0),
             ("C damper nominal 25 C, lead %.1f g" % lead, me, lead, arm, cf, C0),
             ("D damper cold 0 C (EST x2), lead %.1f g" % lead, me, lead, arm, cf, 2 * C0),
             ("E damper half-hot (leak / half fill), lead %.1f g" % lead, me, lead, arm, cf, 0.3 * C0)]
    tasks = [(n, k, m_, ld, ar, c_, cd) for (n, m_, ld, ar, c_, cd) in cases for k in ("kd", "nom", "hi")]
    with mp.Pool(3) as pool: res = pool.map(run_case, tasks)
    P("| case | corner | wing f_h / f_a (Hz) | no instability <= 28.8 m/s at any K (0.01-20 N m/rad) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |"); P("|---|---|---|---|---|---|---|")
    for r in res: P(R.fmt(r))
    P()
    P("Pass limit: no instability at V <= 28.8 m/s = 1.2 x VD (VD 24 m/s) for any hinge stiffness K; the grid onset speed is reported for margin (x VD = onset / 24).")
    open(os.path.join(HERE, "flutter_t101.md" if mode == "new" else "flutter_t101_%s.md" % mode), "w").write("\n".join(L))
