"""D-195 (QP-5): elevon flutter with the CAD of 2026-11-15 (D-193/D-194). python flutter_d195.py -> flutter_d195.md  (imports fixes2_run.py; 3 processes, ~5 min)
Changes against fixes2_run.py: elevon WNG-006 mass 6.7 g (was 9.6 g: foam re-derived), hinge inertia total 1.485e-5 kg m2 (cad_mass.json; was 1.687e-5),
lead 15.6 g at 20 mm ahead of the hinge unchanged, BAL_DZ -3.3 mm (z offset of the lead from the hinge axis: out of the plane of the 3-DOF section; it enters only the
hinge inertia, 6.47e-6 kg m2 for the balance, which the section model takes as lead x arm^2 = 6.44e-6), damper c 1.0297e-3 N m s/rad (amodel/wing.py DMP_C, unchanged).
Check printed first: the section model's elevon+balance hinge inertia against cad_mass.json."""
import os, sys, json, multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixes2_run as R
HERE = os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":
    cm = json.load(open(os.path.join(HERE, "..", "sitl", "cad_mass.json")))["elevon"]
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    me, lead, arm = 0.0067, 15.6, 0.020
    ce = 0.25 * 0.245
    Ih_sec = me * ce * ce / 3 + (lead + 0.5) * 1e-3 * arm ** 2
    P("Hinge inertia per elevon: CAD %.3e kg m2 (cad_mass.json: elevon %.3e + balance %.3e); section-model inputs here me %.1f g plate c^2/3 + (lead+tabs) x 20 mm^2 = %.3e" % (
        cm["hinge_inertia_total_kgm2"], cm["hinge_inertia_one_elevon_kgm2"], cm["hinge_inertia_balance_one_kgm2"], me * 1e3, Ih_sec))
    P("Elevon CG aft of the hinge: unbalanced %.2f mm, balanced %.2f mm (negative = ahead of the hinge, i.e. overbalanced; was -6.06 mm)" % (cm["cg_aft_of_hinge_unbalanced_m"] * 1e3, cm["cg_aft_of_hinge_balanced_m"] * 1e3))
    P()
    C0 = 1.0297e-3
    cases = [("A no damper, lead 15.6 g, elevon 6.7 g", me, 15.6, arm, 0.25, 0.0),
             ("B damper hot 50 C (EST x0.6)", me, 15.6, arm, 0.25, 0.6 * C0),
             ("C damper nominal 25 C", me, 15.6, arm, 0.25, C0),
             ("D damper cold 0 C (EST x2)", me, 15.6, arm, 0.25, 2 * C0),
             ("E damper half-hot (leak / half fill)", me, 15.6, arm, 0.25, 0.3 * C0),
             ("F lead cut to 12.8 g, damper hot", me, 12.8, arm, 0.25, 0.6 * C0),
             ("G previous design for reference: elevon 9.6 g, lead 15.6 g, damper nominal", 0.0096, 15.6, arm, 0.25, C0)]
    tasks = [(n, k, m_, ld, ar, cf, cd) for (n, m_, ld, ar, cf, cd) in cases for k in ("kd", "nom", "hi")]
    with mp.Pool(3) as pool: res = pool.map(R.run_case, tasks)
    P("| case | corner | wing f_h / f_a (Hz) | no instability <= 28.8 m/s at any K (0.01-20 N m/rad) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |"); P("|---|---|---|---|---|---|---|")
    for r in res: P(R.fmt(r))
    P()
    P("Pass limit: no instability at V <= 28.8 m/s = 1.2 x VD (VD 24 m/s) for any hinge stiffness K; the grid onset speed is reported for margin (x VD = onset / 24).")
    open(os.path.join(HERE, "flutter_d195.md"), "w").write("\n".join(L))
