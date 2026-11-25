"""T-105 unit 1(c): elevon servo-horn-pushrod sweep poses -> sims3d/out/linkage.json.   python -I export_linkage.py [step_deg]   (about 1-2 min, step 0.5 deg)
Reads the CURRENT CAD constants through mechanism/linkage_core.py (amodel/common.py, wing.py, electrical.py) every run, so it MUST be re-run after any change to the
elevon chord / hinge / horn / servo constants (T-101 is changing the elevon chord: re-run after it). Joint state = ELEVON_ZJ (default mid).
Per side (R = +y, L = -y) and per elevon angle delta, -ELEV_STOP..+ELEV_STOP: servo angle theta (closed form, linkage_core.theta_of_delta), joint positions,
gearing, hinge moment and the servo torque / rod force that balances it (elevon_dynamics.py definitions), and the minimum clearance of every moving part pair
by the analytic separating-axis engine of elevon_sweep_collision.py (same pair list, same exclusions; solid convex hulls = a lower bound of clearance)."""
import itertools, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MECH = os.path.normpath(os.path.join(HERE, "..", "mechanism"))
sys.path.insert(0, MECH); sys.dont_write_bytecode = True
import numpy as np                                    # noqa: E402
import linkage_core as k                              # noqa: E402
import elevon_sweep_collision as sc                   # noqa: E402
import elevon_dynamics as dyn                         # noqa: E402
step = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
R = lambda x, n=4: round(float(x), n)
V3 = lambda v, n=3: [round(float(x) * 1e3, n) for x in v]          # m -> mm


def is_dc(a_, b_):
    return (a_, b_) in sc.DESIGN_CONTACT or (b_, a_) in sc.DESIGN_CONTACT


def poses(sy):
    stat = sc.static_set(sy); out = []
    for dd in np.round(np.arange(-k.ELEV_STOP, k.ELEV_STOP + 1e-9, step), 6):
        d = math.radians(dd); th = k.theta_of_delta(d, sy)
        mov = sc.moving_set(th, d, sy)
        best_all = [1e9, None]; best_free = [1e9, None]
        pairs = []
        for a_, A in mov.items():
            for b_, B in stat.items():
                if (a_, b_) not in sc.STATIC_EXCL: pairs.append((a_, b_, A, B))
        for a_, b_ in itertools.combinations(mov, 2):
            if (a_, b_) not in sc.EXCLUDED and (b_, a_) not in sc.EXCLUDED: pairs.append((a_, b_, mov[a_], mov[b_]))
        for a_, b_, A, B in pairs:
            v = sc.sep(A, B) * 1e3; pr = "%s / %s" % (a_, b_)
            if v < best_all[0]: best_all = [v, pr]
            if not is_dc(a_, b_) and v < best_free[0]: best_free = [v, pr]
        u, sa, sh = k.sens(th, d, sy); gh, ga, lh, la = k.levers(th, d, sy); pa, ph = k.arm_pt(th, sy), k.horn_pt(d, sy)
        q = dyn.HINGE_NM * abs(dd) / k.ELEV_LIM                       # N m, linear model of elevon_dynamics.run_case(load='linear'): Q = HINGE_NM * delta / ELEV_LIM
        out.append(dict(delta_deg=R(dd, 3), servo_theta_deg=R(math.degrees(th)), arm_tip_mm=V3(pa), horn_hole_mm=V3(ph), rod_len_mm=R(np.linalg.norm(ph - pa) * 1e3, 4),
                        gear_ddelta_dtheta=R(sa / sh, 5), horn_transmission_deg=R(gh, 3), arm_transmission_deg=R(ga, 3), jac_sigma_min=R(k.jac_sigma(th, d, sy), 5),
                        hinge_moment_Nm=R(q, 5), servo_torque_req_Nm=R(q / abs(sh / sa), 5), rod_force_N=R(q / abs(sh), 4), residual_m=float(abs(k.g(th, d, sy))),
                        min_clearance_mm=R(best_all[0], 4), min_clearance_pair=best_all[1], min_clearance_excl_design_contact_mm=R(best_free[0], 4), min_clearance_excl_pair=best_free[1]))
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    conv = dict(
        frame="CAD frame: x aft, y span (+y = right wing), z up, positions in mm (arm_tip_mm, horn_hole_mm, geometry.*). Side R = +y, L = -y (sy = +1 / -1).",
        servo_theta_deg="arm angle about the vertical spline axis at (SV_XS, sy*SERVO_Y), counter-clockwise about +z, 0 at neutral (arm tip points inboard, direction (0, -sy)).",
        delta_deg="elevon angle, right-handed rotation about +y through the hinge (XH, HINGE_Z): positive = trailing edge DOWN (horn hole aft/down); same sign as the plant dl/dr in the sims3d flight files.",
        hinge_moment_Nm="|Q| = HINGE_NM x |delta| / ELEV_LIM, HINGE_NM = %.3f N m at VD (elevon_dynamics.py, EST); the aerodynamic moment opposes delta. Linear model only; the plant's own hinge moment (a_aero.py) is not exported here." % dyn.HINGE_NM,
        servo_torque_req_Nm="Q / |d theta / d delta| (hold torque, elevon_dynamics hold); rod_force_N = Q / |s_h| (rod compression or tension)",
        min_clearance_mm="min over all moving-vs-static and moving-vs-moving part pairs of the separating-axis separation, mm, negative = penetration; excludes the pairs in elevon_sweep_collision.EXCLUDED / STATIC_EXCL (seated joints, same part, hull artifacts). Solid hulls, holes not subtracted: a LOWER BOUND of the true clearance. *_excl_design_contact drops the declared design contacts (arm on servo case; rod on arm in zj=lo; rod on keeper in zj=hi).",
        rod_len_mm="distance arm tip to horn hole; constant (rigid rod) to residual_m")
    geo = dict(L_rod_mm=R(k.L_ROD * 1e3), ARM_R_mm=R(k.ARM_R * 1e3), HORN_R_mm=R(k.HORN_R * 1e3), XH_mm=R(k.XH * 1e3), HINGE_Z_mm=R(k.HINGE_Z * 1e3), HORN_XH_mm=R(k.HORN_XH * 1e3),
               SV_XS_mm=R(k.SV_XS * 1e3), SERVO_Y_mm=R(k.SERVO_Y * 1e3), ROD_Z_mm=R(k.ROD_Z * 1e3), ROD_D_mm=R(k.ROD_D * 1e3),
               horn_hole_rel_hinge_mm=[R(k.VX0 * 1e3), R(k.VZ0 * 1e3)], hinge_axis="parallel to y through (XH, HINGE_Z); servo spline axis parallel to z through (SV_XS, +-SERVO_Y)",
               arm_pivot_mm_R=[R(k.SV_XS * 1e3), R(k.SERVO_Y * 1e3), R(k.ZJ * 1e3)])
    meta = dict(task="T-105 unit 1(c)", git_head=k.git_head(), generated_by="sims3d/export_linkage.py", step_deg=step,
                WARNING="reads the CURRENT working-tree CAD constants (the elevon chord is being changed by T-101): re-run after T-101 lands",
                arm_joint_state=k.STATE, arm_joint_z_mm=R(k.ZJ * 1e3), ELEV_LIM_deg=k.ELEV_LIM, ELEV_STOP_deg=k.ELEV_STOP, units="mm unless suffixed; deg; N; N m", conventions=conv, geometry=geo)
    res = dict(meta=meta, R=poses(1), L=poses(-1))
    p = os.path.join(HERE, "out", "linkage.json"); json.dump(res, open(p, "w"), separators=(",", ":"))
    allp = res["R"] + res["L"]
    worst = min(allp, key=lambda x: x["min_clearance_mm"])
    print("%s  %.1f KB  poses/side %d  min clearance %.3f mm (%s), excl design contact %.3f mm" % (p, os.path.getsize(p) / 1024, len(res["R"]), worst["min_clearance_mm"],
          worst["min_clearance_pair"], min(x["min_clearance_excl_design_contact_mm"] for x in allp)))
