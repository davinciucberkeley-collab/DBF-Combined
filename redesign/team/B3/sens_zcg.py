"""B3 V1 sensitivity: what the CG height does to the effective NP, Cl_beta and the spiral mode (as-designed geometry).

The V1 re-run found that A3-R6a's CG, 18.5 mm above the chord plane, costs 3.4 mm of NP at 1.3 Vs and makes the
spiral faster (CL-B3-V-SM-A3-ENV, CL-B3-V-LAT-T2 fail). This sweep gives A1 / A3 the trade: how much CG height has
to come out, versus how far the CG has to move forward. Not a claim source (sensitivity only).

Run: python -I redesign/team/B3/sens_zcg.py      -> results/sens_zcg.json  (reads the same inputs as verify_asdesigned)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify_asdesigned as VA  # noqa: E402

kit = VA.kit
SC, AV = VA.SC, VA.AV
ZS = (0.0, 0.006, 0.012, 0.0185, 0.025)


def val(ref):
    return kit.value(ref)


def main():
    kw = {k: val(r) for k, r in VA.MIN.items()}
    fin, gap, zcg = kw.pop("fin"), kw.pop("gap"), kw.pop("zcg")
    kw.pop("xnp_c")
    cgf, m_basic = kw.pop("cgf"), kw.pop("m_basic")
    Ixx, Iyy, Izz, V, cd0, e = (kw.pop(k) for k in ("Ixx", "Iyy", "Izz", "V", "cd0", "e"))
    kw["yin"], kw["yout"] = VA.as_built(kw["yin"], kw["yout"], gap)
    c, S = kw["c"], kw["S"]
    x_a3 = cgf * c
    secs = VA.fin_sections(fin, "BOARD")
    vt = val("CL-B3-V-VT")
    dprop = val("CL-B3-V-XNP") - val("CL-B3-V-XNP-AERO")
    rows = []
    for z in ZS:
        kw["zref"] = z
        CLt = 2 * kw["m"] * kw["g"] / (kw["rho"] * vt * vt * S)
        geo = AV.geometry_from(kw["b"], c, kw["ef"], kw["yin"], kw["yout"], kw["fy"], kw["fh"], kw["fle"], kw["fte"],
                               0.0529, z, fin_sections=secs)
        xnp_t = AV.derivatives_cl(geo, CLt, "fine")["Xnp"] + dprop
        CLc = 2 * kw["m"] * kw["g"] / (kw["rho"] * V * V * S)
        xnp_c = AV.derivatives_cl(geo, CLc, "fine")["Xnp"] + dprop
        with VA.patched_geometry({"fin_sections": secs}):
            md = SC.modes(xnp_c, x_a3, m_basic, Ixx, Iyy, Izz, V, cd0, e, **kw)
            lt = SC.lat_terms(x_a3, CLc, **kw)
        rows.append({"z": z, "xnp_vt": xnp_t, "x_aft_vt": xnp_t - 0.05 * c, "sm_a3_vt": (xnp_t - x_a3) / c,
                     "Clb": lt["Clb"], "Cnb": lt["Cnb"], "spiral_t2_s": md["lat_t2_s"], "dr_zeta": md["dr_zeta"],
                     "sp_zeta": md["sp_zeta"]})
        print({k: round(v, 5) for k, v in rows[-1].items()}, flush=True)
    (HERE / "results" / "sens_zcg.json").write_text(json.dumps({"x_a3": x_a3, "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
