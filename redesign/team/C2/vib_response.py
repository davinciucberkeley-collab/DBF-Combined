"""C2-R5 (2026-11-13): forced response of the free-free wing to the rotor orders (R-VIBRATION, CR-C2-04, D-45).

Why: the station-participating wing modes (beam model, wing_struct.py) are dense in the rotor band: antisymmetric flap
82.0 Hz (nominal) is 9.2 % from hover 1P (90.3 Hz); in-plane 149.5 / flap 153.7 / in-plane 215.1 Hz lie inside 20 % of
the 2P lines; over the 12 stiffness corners the closest is 0.2 % (CL-C2-WING-MODE-SEP; out/results.json
mode_sep_worst_all). The 20 % bands (72-119 Hz at 1P, 144-238 Hz at 2P) hold five station modes at once, and no spar
from 16 to 25 mm clears them (CR-C2-04), so no structural change meets the frequency rule. What R-VIBRATION protects
is the response: the IMU must stay usable and the structure must not fatigue. This script computes that response,
at resonance, for

  1P  the rotating residual unbalance of each rotor (prop + motor bell), F = U Omega^2, with U = m_rot G / Omega_hover:
      the ISO 21940-11 specific unbalance e = G / Omega (SRC-C2-ISO21940) at balance grade G 16 mm/s (EST; the grade
      the standard gives for propeller shafts with special requirements; G 6.3 is fans) on m_rot = prop 17 g
      (P:propulsion.prop_mass_kg) + bell 40 g (EST, the ~40 g ring behind ASM-C1-BELL-INERTIA): U = 1.61 g mm per rotor;
  2P  the blade-pass load per rotor (along the thrust axis and sideways at the rotor): its magnitude is not known
      (`-`, no source found 2026-11-13), so the response is computed per newton and the script gives the 2P load
      each rotor may have before the IMU reaches the limit. The first tethered hover measures it (VIBE log).

Model: wing_struct's free-free 6-dof Timoshenko beam (48 elements per half) with C1's MC-P lumped items, mass-
normalised modes (all, incl. the rigid ones), modal damping zeta = ASM-C2-WING-ZETA 1 % (low end, SRC-C2-ADAMS-DAMP),
all 12 stiffness corners, the excitation swept over each band with every modal frequency in the band added so each
resonance peak is hit exactly (a dwell at resonance). Each rotor adds in magnitude (worst relative phase), with the
worse spin sense. Bands: sustained = 0.8 x hover 1P .. 1.2 x cruise 1P (the band the 20 % rule protects; hover and
cruise rpm CL-B4-HOVER-RPM, -CRUISE-RPM) and twice that for 2P; full = 0.6 x hover 1P .. full-throttle 1P
(CL-B4-RPM-MAX), reported (full throttle is a transient, <= P:env.full_throttle_max_s, D-42). Outputs:
  * IMU (FC AVN-001 position) acceleration amplitude, largest axis, against ArduPilot's VIBE 30 m/s/s
    (SRC-C2-AP-VIBE); VIBE is an RMS-type level and a sine of peak A has RMS A / sqrt 2, so using the peak is
    conservative; the gel isolators (AVN-006) are not credited;
  * IMU angular-rate amplitude (gyro): reported; the K09L.param rpm-tracking harmonic notch (INS_HNTCH_MODE 3, ESC
    telemetry; HMNCS 7 = 1P, 2P, 3P) removes it from the rate loop (SRC-C2-AP-NOTCH);
  * largest spar bending-stress amplitude anywhere on the span (spar alone takes the section moment: conservative).

Run:  python -I redesign/team/C2/vib_response.py   (about 15 min, all 12 corners) -> vib/params.json (P:c2vib.*),
      out/vib_response.json.  Then: python -I redesign/team/C2/c2_claims.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import eigh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wing_struct as ws  # noqa: E402

RD = ws.RD

# ------------------------------------------------------------------ inputs (sources in c2_claims.py)
G_GRADE = 0.016            # m/s, ISO 21940-11 grade G 16 (EST)
M_ROT = ws.pv("propulsion.prop_mass_kg") + 0.040        # kg, prop + motor bell (~40 g ring, ASM-C1-BELL-INERTIA basis)
U_SPEC = G_GRADE * M_ROT / (2 * math.pi * ws.F_HOVER)   # kg m residual unbalance per rotor, e = G / Omega_hover
ZETA = 0.01                # ASM-C2-WING-ZETA
N_HALF = 48
F_1P_LO = 0.6 * ws.F_HOVER
F_1P_HI = ws.claim_value("B4", "CL-B4-RPM-MAX") / 60.0
# sustained band = the band R-VIBRATION's 20 % rule protects (0.8 x hover 1P .. 1.2 x cruise 1P); full = every rpm
BANDS = {"1P-sus": ("1P", 0.8 * ws.F_HOVER, 1.2 * ws.F_CRUISE), "1P-full": ("1P", F_1P_LO, F_1P_HI),
         "2P-sus": ("2P", 1.6 * ws.F_HOVER, 2.4 * ws.F_CRUISE), "2P-full": ("2P", 2 * F_1P_LO, 2 * F_1P_HI)}


def avn_fc():
    d = json.loads((RD / "subsystems" / "avionics" / "interfaces.json").read_text(encoding="utf-8"))
    for p in d["parts"]:
        if p["id"] == "AVN-001":
            return np.array(p["cg_xyz_m"], float)
    raise KeyError("AVN-001")


def model(sec_fn):
    ys_r = ws.mesh(N_HALF)
    ys = np.concatenate([-ys_r[:0:-1], ys_r])
    K = ws.assemble_K(ys, sec_fn)
    Mg, st, _ = ws.assemble_M(ys, sec_fn, "MC-P")
    w2, V = eigh(K, Mg)                       # V^T M V = I
    w = np.sqrt(np.clip(w2, 0, None))
    return ys, K, Mg, st, w, V


def node_force(n_dof, node, r, F):
    """Generalised nodal load of force F (3, complex) applied at offset r from the beam node."""
    f = np.zeros(n_dof, complex)
    f[6 * node:6 * node + 3] = F
    f[6 * node + 3:6 * node + 6] = np.cross(r, F)
    return f


def rotors(ys):
    out = []
    for it in ws.read_mass_items("MC-P"):
        if it["group"] == "rotor":
            node = int(np.argmin(np.abs(ys - it["y"])))
            out.append((node, np.array([it["x"] - ws.xs, it["y"] - ys[node], it["z"]])))
    return out


def response(sec_fn, fc):
    ys, K, Mg, st, w, V = model(sec_fn)
    n = 6 * len(ys)
    i0 = int(np.argmin(np.abs(ys)))
    r_fc = np.array([fc[0] - ws.xs, fc[1] - ys[i0], fc[2]])
    T_fc = np.hstack([np.eye(3), -ws.skew(r_fc)])           # translation at the IMU from node dofs
    # element stiffness for the internal moments
    Ke = [ws.assemble_K(np.array([ys[e], ys[e + 1]]), sec_fn) for e in range(len(ys) - 1)]
    KE = np.array(Ke)
    IDX = np.array([np.arange(6 * e, 6 * e + 12) for e in range(len(Ke))])
    rot = rotors(ys)
    items = ws.read_mass_items("MC-P")
    m_tot = sum(it["m"] for it in items)
    T_hover = m_tot * ws.g / 4
    I_sp = math.pi / 64 * (ws.D_sp ** 4 - ws.d_sp ** 4)

    def sweep(f_lo, f_hi):
        fm = [wi / (2 * math.pi) for wi in w if f_lo <= wi / (2 * math.pi) <= f_hi]
        return np.unique(np.concatenate([np.linspace(f_lo, f_hi, 300), fm]))

    # modal output matrices (outputs are linear in the modal coordinates)
    A_fc = T_fc @ V[6 * i0:6 * i0 + 6, :]                  # IMU translation per modal coordinate (3 x nm)
    R_fc = V[6 * i0 + 3:6 * i0 + 6, :]                      # IMU rotation (3 x nm)
    EM = np.einsum("eij,ejm->eim", KE[:, [3, 5], :], V[IDX, :])   # element-end flap / in-plane moments (ne x 2 x nm)

    def harmonic(f_exc, groups):
        """groups: per rotor, a list of alternative nodal load vectors (spin senses). Each rotor contributes the
        worse of its alternatives, element by element; rotors add in magnitude (worst relative phase)."""
        Om = 2 * math.pi * f_exc
        H = 1.0 / (w ** 2 - Om ** 2 + 2j * ZETA * w * Om)
        acc, gyro, mom = np.zeros(3), np.zeros(3), np.zeros(len(KE))
        for alts in groups:
            Q = (V.T @ np.array(alts).T) * H[:, None]           # nm x n_alt
            acc += np.abs(Om ** 2 * (A_fc @ Q)).max(axis=1)
            gyro += np.abs(Om * (R_fc @ Q)).max(axis=1)
            mm = np.abs(np.einsum("ekm,mn->ekn", EM, Q))        # ne x 2 x n_alt
            mom += np.hypot(mm[:, 0, :], mm[:, 1, :]).max(axis=1)
        return acc, gyro, mom

    out = {}
    for band, (order, lo, hi) in BANDS.items():
        best = {"acc": 0.0, "gyro": 0.0, "M": 0.0}
        for f in sweep(lo, hi):
            Om = 2 * math.pi * f / (1 if order == "1P" else 2)       # shaft speed
            groups = []
            for node, r in rot:
                if order == "1P":
                    F0 = U_SPEC * Om ** 2
                    # rotating unbalance force in the prop plane: F0 (y + i s z), either spin sense s
                    groups.append([node_force(n, node, r, np.array([0, F0, 1j * s * F0])) for s in (1, -1)])
                else:
                    # 2P load per unit newton (magnitude unknown, `-`): along the thrust axis or sideways,
                    # each component 1 N, both in the worst phase
                    groups.append([node_force(n, node, r, np.array([1.0, 0, 0], complex))])
                    groups.append([node_force(n, node, r, np.array([0, 1.0, 0], complex))])
            acc, gyro, mom = harmonic(f, groups)
            a_max, g_max, m_max = float(acc.max()), float(np.degrees(gyro.max())), float(mom.max())
            if a_max > best["acc"]:
                best.update(acc=a_max, acc_f=float(f))
            if g_max > best["gyro"]:
                best.update(gyro=g_max, gyro_f=float(f))
            if m_max > best["M"]:
                best.update(M=m_max, M_f=float(f))
        best["sigma"] = best["M"] * (ws.D_sp / 2) / I_sp
        out[band] = best
    out["T_hover_n"] = T_hover
    return out


def main():
    fc = avn_fc()
    corners = {}
    for name, (E_, G_) in {"E70-G3": (70e9, 3e9), "E70-G5": (70e9, 5e9), "E100-G3": (100e9, 3e9),
                           "E100-G5": (100e9, 5e9)}.items():
        for teff in (0.5, 0.0, 1.0):
            key = f"{name}-tape{teff}"
            corners[key] = c = response(ws.sec_factory(E_s=E_, G_s=G_, tape_eff=teff), fc)
            print(key + ": " + "; ".join(f"{b} acc {c[b]['acc']:.2f} @ {c[b]['acc_f']:.1f} Hz, sigma "
                                         f"{c[b]['sigma'] / 1e6:.2f} MPa" for b in BANDS), flush=True)

    W = {}
    for band in BANDS:
        for q, fk in (("acc", "acc_f"), ("gyro", "gyro_f"), ("sigma", "M_f")):
            k = max(corners, key=lambda kk: corners[kk][band][q])
            W[f"{band}_{q}"] = {"value": corners[k][band][q], "corner": k, "f_hz": corners[k][band][fk]}
    T_h = corners["E100-G5-tape0.5"]["T_hover_n"]
    res = {"corners": corners, "worst": W, "fc_xyz_m": fc.tolist(), "zeta": ZETA, "U_kgm": U_SPEC, "m_rot_kg": M_ROT,
           "bands_hz": {b: [lo, hi] for b, (_, lo, hi) in BANDS.items()}, "T_hover_n": T_h}
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "vib_response.json").write_text(json.dumps(res, indent=1, default=float))

    def P(v, unit, note, status="CHECKED"):
        return {"value": round(float(v), 6), "unit": unit, "source": "team/C2/vib_response.py", "status": status,
                "note": note}

    def wn(key, what):
        w_ = W[key]
        return f"{what}, worst of 12 stiffness corners ({w_['corner']}, {w_['f_hz']:.1f} Hz, resonance dwell)"
    vib = {"_note": "Written by team/C2/vib_response.py. Do not edit by hand: change the inputs in the script, re-run "
                    "it, then team/C2/c2_claims.py.",
           "c2vib": {
               "balance_grade_ms": P(G_GRADE, "m/s", "EST: ISO 21940-11 grade G 16 (SRC-C2-ISO21940)", "UNVERIFIED"),
               "m_rot_kg": P(M_ROT, "kg", "prop 17 g + motor bell 40 g (EST)", "UNVERIFIED"),
               "unbalance_kgm": P(U_SPEC, "kg m", "residual unbalance per rotor U = m_rot G / Omega_hover"),
               "zeta": P(ZETA, "-", "modal damping (ASM-C2-WING-ZETA)", "UNVERIFIED"),
               "imu_acc_1p_ms2": P(W["1P-sus_acc"]["value"], "m/s2", wn("1P-sus_acc", "IMU acceleration amplitude, "
                                   "largest axis, 1P unbalance, sustained band")),
               "imu_acc_1p_full_ms2": P(W["1P-full_acc"]["value"], "m/s2", wn("1P-full_acc", "same over every rpm to "
                                        "full throttle (transient)")),
               "imu_rate_1p_dps": P(W["1P-sus_gyro"]["value"], "deg/s", wn("1P-sus_gyro", "IMU angular-rate amplitude, "
                                    "1P, sustained band (removed by the harmonic notch)")),
               "spar_sigma_1p_pa": P(W["1P-sus_sigma"]["value"], "Pa", wn("1P-sus_sigma", "largest spar bending-stress "
                                     "amplitude on the span, 1P, sustained band, spar alone")),
               "spar_sigma_1p_full_pa": P(W["1P-full_sigma"]["value"], "Pa", wn("1P-full_sigma", "same over every rpm")),
               "imu_acc_2p_per_n": P(W["2P-sus_acc"]["value"], "m/s2/N", wn("2P-sus_acc", "IMU acceleration amplitude "
                                     "per newton of 2P load on each rotor (thrust axis + sideways), sustained band")),
               "imu_acc_2p_full_per_n": P(W["2P-full_acc"]["value"], "m/s2/N", wn("2P-full_acc", "same over every rpm")),
               "spar_sigma_2p_per_n": P(W["2P-sus_sigma"]["value"], "Pa/N", wn("2P-sus_sigma", "spar stress amplitude "
                                        "per newton of 2P load, sustained band")),
               "t_hover_n": P(T_h, "N", "hover thrust per rotor, C1 MC-P mass x g / 4")}}
    (HERE / "vib").mkdir(exist_ok=True)
    (HERE / "vib" / "params.json").write_text(json.dumps(vib, indent=1, ensure_ascii=False), encoding="utf-8")
    for k_, v_ in W.items():
        print(k_, v_)


if __name__ == "__main__":
    main()
