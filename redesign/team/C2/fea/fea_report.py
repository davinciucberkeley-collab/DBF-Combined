"""C2 simulation round: post-process the 3-D wing FEA (gmsh mesh; SU2 ELASTICITY and the in-house PCG solve of the
same mesh), check mesh convergence (3 levels, GCI after Celik et al. 2008), compare with the beam model and the hand
calculations, compute margins, write fea/params.json (P:c2fea.*) for fea_claims.py and the figures.

Run after the solves (see SIMULATION-REPORT.md):  python -I redesign/team/C2/fea/fea_report.py
Reads fea/out/wing_fea.json (SU2), fea/out/wing_fea_direct.json and fea/out/direct_*.json (PCG).
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
C2 = HERE.parent
RD = C2.parents[1]
OUT = HERE / "out"
FIG = C2 / "fig"
sys.path.insert(0, str(C2))
sys.path.insert(0, str(HERE))
import wing_struct as ws   # noqa: E402

SF = ws.SF
M = ws.M
GOV = {  # quantity: (run key, field, station rule, unit scale, label)
    # C2-R3: every run is set O (orthotropic tube, the physical model) on the C1-R5 loads; R2's isotropic B / T
    # bracket runs (C1-R4 loads) are archived in out/R2/ with the SU2 cross-check
    "w_tip_G2": ("G2-HANG-MOTOR/MC-P/O", "w", "tip", 1e3, "flap w at the tip, G2, mm"),
    "u_tip_L1": ("L1-LEVEL/MC-C/O", "u", "tip", 1e3, "in-plane u at the tip, L1, mm"),
    "twist_tip_L4": ("L4-CORNER-SIDE-Y/MC-C/O", "twist", "tip", 180 / math.pi, "twist at the tip, L4, deg"),
    "spar_sigma_L1": ("L1-LEVEL/MC-C/O", "spar", "max", 1e-6, "spar outer-fibre stress, L1, limit, MPa"),
    "w_tip_G2_O": ("G2-HANG-MOTOR/MC-P/O", "w", "tip", 1e3, "flap w at the tip, G2, orthotropic tube, mm"),
    "twist_tip_L4_O": ("L4-CORNER-SIDE-Y/MC-C/O", "twist", "tip", 180 / math.pi, "twist at the tip, L4, orthotropic tube, deg"),
    "foam_s1_L4_O": ("L4-CORNER-SIDE-Y/MC-C/O", "foam:s1_p995_pa", "", 1e-3, "foam tension, 99.5th pct, L4, orthotropic, kPa"),
    "foam_tau_L4_O": ("L4-CORNER-SIDE-Y/MC-C/O", "foam:tau_p995_pa", "", 1e-3, "foam shear, 99.5th pct, L4, orthotropic, kPa"),
    "foam_peak_L4_O": ("L4-CORNER-SIDE-Y/MC-C/O", "foam:s1_max_pa", "", 1e-3, "foam tension peak (block corner), L4, orthotropic, kPa"),
}
UNITS = {"w_tip_G2": "mm", "u_tip_L1": "mm", "twist_tip_L4": "deg", "spar_sigma_L1": "MPa", "w_tip_G2_O": "mm",
         "twist_tip_L4_O": "deg", "foam_s1_L4_O": "kPa", "foam_tau_L4_O": "kPa", "foam_peak_L4_O": "kPa"}
DECISION = ("w_tip_G2", "u_tip_L1", "twist_tip_L4", "spar_sigma_L1", "w_tip_G2_O", "twist_tip_L4_O", "foam_s1_L4_O",
            "foam_tau_L4_O")      # quantities a decision rests on (the singular peak is reported, not used)


# ------------------------------------------------------------------------------------------------ merge
def load_runs(patterns):
    """levels[lev][run_key] = run dict for the result files matching patterns; plus stats, beam reference, validation."""
    levels, stats, beam, valid = {}, {}, None, {}
    files = sorted({f for pat in patterns for f in OUT.glob(pat)})
    for f in files:
        r = json.loads(f.read_text())
        for lev, d in r.get("levels", {}).items():
            levels.setdefault(int(lev), {}).update({k: v for k, v in d["runs"].items()})
            stats.setdefault(int(lev), d["stats"])
            for k, v in d["runs"].items():
                levels[int(lev)][k]["_info"] = v["info"]
        beam = beam or r.get("beam")
        if r.get("validation"):
            valid["pcg"] = r["validation"]
    return levels, stats, beam, valid, [f.name for f in files]


def load_su2(name):
    su2, valid = {}, None
    f = OUT / name
    if f.exists():
        r = json.loads(f.read_text())
        for lev, d in r.get("levels", {}).items():
            su2[int(lev)] = d["runs"]
        valid = r.get("validation")
    return su2, valid


def spar_max(post, y_min=0.02):
    prof = [p for p in post.get("spar_profile", []) if p[0] >= y_min]
    if not prof:
        return float("nan"), float("nan")
    i = int(np.argmax([p[1] for p in prof]))
    return prof[i][1], prof[i][0]


def qty(run, field, rule, scale):
    post = run["post"] if "post" in run else run
    if field == "spar":
        return spar_max(post)[0] * scale
    if field.startswith("foam:"):
        return post["foam"][field.split(":")[1]] * scale
    v = post[field]
    return float(v[-1]) * scale


# ------------------------------------------------------------------------------------------------ GCI
def gci(h, f, Fs=1.25):
    """Celik et al. (2008) three-grid GCI. h, f ordered coarse -> fine. Returns p, extrapolated value, GCI_fine."""
    h3, h2, h1 = h
    f3, f2, f1 = f
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0:
        return {"p": float("nan"), "f_ext": f1, "gci_fine": 0.0, "monotone": True}
    s = np.sign(e32 / e21)
    p = 2.0
    for _ in range(200):
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        p_new = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        if abs(p_new - p) < 1e-10:
            break
        p = p_new
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    ea21 = abs((f1 - f2) / f1)
    gci_fine = Fs * ea21 / (r21 ** p - 1)
    return {"p": p, "f_ext": f_ext, "gci_fine": gci_fine, "monotone": bool(s > 0), "r21": r21, "r32": r32,
            "rel_change_fine": ea21}


# ------------------------------------------------------------------------------------------------ figures
INK, INK2, INK3, LINE, ACC, ORG = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#1F5FC7", "#C2540A"
MONO = 'font-family="IBM Plex Mono, monospace"'
SANS = 'font-family="IBM Plex Sans, sans-serif"'


def svg_spanwise(path, panels, beam_label="beam model, tape 0 %"):
    """panels: list of (label, y_fea_list_by_level{lev: (y, v)}, (y_beam, v_beam))."""
    W, H = 1200, 150 + 210 * len(panels)
    x0, x1 = 90, 1100
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    X = lambda v: x0 + (x1 - x0) * v / ws.L_half
    dash = {1: "2 4", 2: "8 4", 3: ""}
    for k, (lab, fea, bm) in enumerate(panels):
        top, bot = 30 + 210 * k, 30 + 210 * k + 170
        allv = [abs(v) for _, (yy, vv) in fea.items() for v in vv] + [abs(v) for v in bm[1]]
        vmax = max(allv) * 1.1 or 1.0
        Y = lambda v: bot - (bot - top) * abs(v) / vmax
        out.append(f'<line x1="{x0}" y1="{bot}" x2="{x1}" y2="{bot}" stroke="{LINE}" stroke-width="1"/>')
        out.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{bot}" stroke="{LINE}" stroke-width="1"/>')
        out.append(f'<text x="{x0 + 8}" y="{top + 12}" fill="{INK2}" {SANS} font-size="12">{lab}</text>')
        out.append(f'<text x="{x0 - 8}" y="{top + 12}" text-anchor="end" fill="{INK3}" {MONO} font-size="12">{vmax / 1.1:.2f}</text>')
        out.append(f'<text x="{x0 - 8}" y="{bot}" text-anchor="end" fill="{INK3}" {MONO} font-size="12">0</text>')
        pts = " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in zip(*bm))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{INK3}" stroke-width="1.5"/>')
        for lev, (yy, vv) in sorted(fea.items()):
            pts = " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in zip(yy, vv))
            out.append(f'<polyline points="{pts}" fill="none" stroke="{ACC}" stroke-width="{1.0 + 0.5 * lev:.1f}" '
                       f'stroke-dasharray="{dash.get(lev, "")}"/>')
    yb = 30 + 210 * len(panels)
    for yy, lab in ((ws.Y_ANCHOR, "anchor"), (ws.y_fin, "fin block"), (ws.y_spar_end, "spar end")):
        out.append(f'<line x1="{X(yy):.1f}" y1="30" x2="{X(yy):.1f}" y2="{yb - 40}" stroke="#CBD2DB" '
                   f'stroke-width="0.75" stroke-dasharray="6 4"/>')
        out.append(f'<text x="{X(yy):.1f}" y="{yb - 26}" text-anchor="middle" fill="{INK3}" {MONO} font-size="11">{lab}</text>')
    for v in np.arange(0, 0.6, 0.1):
        out.append(f'<text x="{X(v):.1f}" y="{yb - 8}" text-anchor="middle" fill="{INK3}" {MONO} font-size="12">{v:.1f}</text>')
    out.append(f'<text x="{x1}" y="{yb + 12}" text-anchor="end" fill="{INK3}" {MONO} font-size="11">|y|, m</text>')
    ly = yb + 40
    out.append(f'<line x1="{x0}" y1="{ly}" x2="{x0 + 40}" y2="{ly}" stroke="{INK3}" stroke-width="1.5"/>'
               f'<text x="{x0 + 48}" y="{ly + 4}" fill="{INK2}" {SANS} font-size="12">{beam_label}</text>')
    for j, lev in enumerate((1, 2, 3)):
        xx = x0 + 260 + 170 * j
        out.append(f'<line x1="{xx}" y1="{ly}" x2="{xx + 40}" y2="{ly}" stroke="{ACC}" stroke-width="{1.0 + 0.5 * lev:.1f}" '
                   f'stroke-dasharray="{dash[lev]}"/><text x="{xx + 48}" y="{ly + 4}" fill="{INK2}" {SANS} font-size="12">FEA level {lev}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def svg_convergence(path, conv):
    """One row per quantity: value at each level vs h (normalised to the extrapolated value), extrapolated line."""
    names = [k for k in GOV if k in conv]
    W, H = 1200, 70 + 120 * len(names)
    x0, x1 = 330, 1100
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    hmax = max(max(c["h_mm"]) for c in conv.values()) * 1.1
    X = lambda h: x0 + (x1 - x0) * h / hmax
    for k, n in enumerate(names):
        c = conv[n]
        top, bot = 20 + 120 * k, 20 + 120 * k + 90
        vals = [v / c["f_ext"] for v in c["f"]]
        lo, hi = min(vals + [1.0]) - 0.02, max(vals + [1.0]) + 0.02
        Y = lambda v: bot - (bot - top) * (v - lo) / (hi - lo)
        out.append(f'<text x="20" y="{top + 30}" fill="{INK}" {SANS} font-size="12">{GOV[n][4]}</text>')
        out.append(f'<text x="20" y="{top + 50}" fill="{INK3}" {MONO} font-size="12">ext {c["f_ext"]:.3f}, p {c["p"]:.2f}, '
                   f'GCI {100 * c["gci_fine"]:.2f} %</text>')
        out.append(f'<line x1="{x0}" y1="{Y(1.0):.1f}" x2="{x1}" y2="{Y(1.0):.1f}" stroke="{INK3}" stroke-width="0.75" stroke-dasharray="6 4"/>')
        out.append(f'<line x1="{x0}" y1="{bot}" x2="{x1}" y2="{bot}" stroke="{LINE}" stroke-width="1"/>')
        pts = " ".join(f"{X(h):.1f},{Y(v):.1f}" for h, v in zip(c["h_mm"], vals))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{ACC}" stroke-width="1.5"/>')
        for h, v in zip(c["h_mm"], vals):
            out.append(f'<circle cx="{X(h):.1f}" cy="{Y(v):.1f}" r="4" fill="{ACC}"/>')
            out.append(f'<text x="{X(h):.1f}" y="{Y(v) - 8:.1f}" text-anchor="middle" fill="{INK3}" {MONO} font-size="11">{v:.3f}</text>')
        out.append(f'<text x="{x0 - 6}" y="{Y(1.0) + 4:.1f}" text-anchor="end" fill="{INK3}" {MONO} font-size="11">1.000</text>')
    yb = 20 + 120 * len(names)
    for h in np.arange(0, hmax, 1.0):
        out.append(f'<text x="{X(h):.1f}" y="{yb + 8}" text-anchor="middle" fill="{INK3}" {MONO} font-size="12">{h:.0f}</text>')
    out.append(f'<text x="{x1}" y="{yb + 28}" text-anchor="end" fill="{INK3}" {MONO} font-size="11">'
               f'mean element size h = (V / N)^(1/3), mm; value / extrapolated value</text></svg>')
    path.write_text("\n".join(out), encoding="utf-8")


def svg_section(path, level=1, ys=(0.20, 0.32, 0.45)):
    """2-D section mesh (the one extruded along the span) coloured by material at three span stations."""
    import wing_fea as wf
    import su2fea as sf
    g = wf.d1_geometry()
    p = wf.LEVELS[level]
    nodes, elems, _ = sf.section_mesh(wf.outline_poly(), wf.cut_lines(g), (g["xs"], g["zs"], [g["ri"], g["rs"]]),
                                      p["nth"], p["nr"], p["h_near"], p["h_far"])
    fn = wf.make_mat_fn(g)
    fill = {wf.FOAM: "#E2E6EC", wf.CF: "#121619", wf.PETG: "#9AA4B1", None: "none"}
    W, sc = 1200, 3000.0
    ph = 150
    H = 40 + ph * len(ys) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    for k, yv in enumerate(ys):
        oy = 40 + ph * k + 75
        ox = 140
        out.append(f'<text x="20" y="{oy + 4}" fill="{INK2}" {MONO} font-size="12">y {yv:.2f} m</text>')
        for vtk, conn in elems:
            for c in conn:
                P = nodes[c]
                cx, cz = P.mean(0)
                m = fn(cx, cz, yv)
                if m is None:
                    continue
                pts = " ".join(f"{ox + sc * x:.1f},{oy - sc * z:.1f}" for x, z in P)
                out.append(f'<polygon points="{pts}" fill="{fill[m]}" stroke="#FFFFFF" stroke-width="0.3"/>')
    ly = H - 16
    for j, (lab, col) in enumerate((("XPS core", "#E2E6EC"), ("CF spar 22 x 20", "#121619"), ("PETG block / anchor / plug", "#9AA4B1"))):
        xx = 140 + 260 * j
        out.append(f'<rect x="{xx}" y="{ly - 10}" width="14" height="12" fill="{col}"/>'
                   f'<text x="{xx + 20}" y="{ly}" fill="{INK2}" {SANS} font-size="12">{lab}</text>')
    out.append(f'<text x="{W - 20}" y="{ly}" text-anchor="end" fill="{INK3}" {MONO} font-size="11">x aft, z up; level {level} mesh; 0 - 50 mm = {sc * 0.05:.0f} px</text></svg>')
    path.write_text("\n".join(out), encoding="utf-8")


# ------------------------------------------------------------------------------------------------ D-68 submodel
D68_MEASURE = "avg"      # foam peaks: "avg" = volume average over AVG_R round the peak element; "" = element peak


def d68_summary(name="d68_submodel.json"):
    f = OUT / name
    if not f.exists():
        return None
    r = json.loads(f.read_text())
    loc = r["local"]
    hl = {int(k): v for k, v in r["inputs"]["local_h_m"].items()}

    def peak(tag, zone, mat, field, intro="block", cases=None):
        """Worst value (largest |.|) of field over the runs of one local model; returns (value, run key, location)."""
        best = (0.0, None, None)
        for key, run in loc.get(tag, {}).get("runs", {}).items():
            if not key.startswith(intro + "/") or (cases and key.split("/")[1] not in cases):
                continue
            d = run["peaks"].get(f"{zone}/{mat}", {})
            v = d.get(field)
            if v is not None and abs(v) > abs(best[0]):
                best = (v, key, d.get(field.replace("_avg", "").replace("_pa", "_at")))
        return best

    sfx = "_avg_pa" if D68_MEASURE == "avg" else "_pa"
    out = {"measure": D68_MEASURE or "element", "levels": {}, "params": {}}
    for geom in ("d68", "asdrawn", "d68g"):
        for lev in (1, 2, 3):
            tag = f"{geom}/L{lev}"
            if tag not in loc:
                continue
            row = {"h_mm": hl[lev] * 1e3, "stats": loc[tag]["stats"]}
            for fld in ("s1", "s3", "tau"):
                for m_ in ("", "_avg"):
                    v, k, at = peak(tag, "pocket", "foam", f"{fld}{m_}_pa")
                    row[f"pocket_foam_{fld}{m_}_lim_pa"] = v
                    row[f"pocket_foam_{fld}{m_}_case"] = k
                    row[f"pocket_foam_{fld}_at"] = at
            row["bead_s1_lim_pa"] = peak(tag, "pocket", "bead", "s1_pa")[0]
            row["bead_vm_lim_pa"] = peak(tag, "pocket", "bead", "vm_pa")[0]
            row["petg_vm_lim_pa"] = peak(tag, "pocket", "petg", "vm_pa")[0]
            for fld in ("s1", "tau"):
                v, k, at = peak(tag, "cutout", "foam", f"{fld}{sfx}", intro="distributed")
                row[f"cutout_foam_{fld}_dist_lim_pa"], row[f"cutout_foam_{fld}_dist_case"] = v, k
                row[f"cutout_foam_{fld}_dist_at"] = at
                v, k, _ = peak(tag, "cutout", "foam", f"{fld}{sfx}")
                row[f"cutout_foam_{fld}_lim_pa"] = v
            eq = [abs(x) for run in loc[tag]["runs"].values() for x in run["equilibrium_residual_N"]]
            row["equilibrium_max_N"] = max(eq) if eq else float("nan")
            out["levels"][tag] = row
    # convergence of the governing local peaks (d68, 3 levels)
    conv = {}
    if all(f"d68/L{l}" in out["levels"] for l in (1, 2, 3)):
        hs = [hl[1], hl[2], hl[3]]
        for fld in ("s1", "s3", "tau"):
            for m_ in ("", "_avg"):
                fv = [abs(out["levels"][f"d68/L{l}"][f"pocket_foam_{fld}{m_}_lim_pa"]) for l in (1, 2, 3)]
                conv[f"pocket_foam_{fld}{m_}"] = {"f": fv, **gci(hs, fv)}
        for fld in ("s1", "tau"):
            fv = [abs(out["levels"][f"d68/L{l}"][f"cutout_foam_{fld}_dist_lim_pa"]) for l in (1, 2, 3)]
            conv[f"cutout_foam_{fld}_dist"] = {"f": fv, **gci(hs, fv)}
    out["convergence"] = conv
    # cut-plane check at level 2
    cut = {}
    if "d68/L2/near" in loc and "d68/L2" in loc:
        for fld in ("s1", "s3", "tau"):
            a = abs(peak("d68/L2", "pocket", "foam", f"{fld}{sfx}")[0])
            b_ = abs(peak("d68/L2/near", "pocket", "foam", f"{fld}{sfx}")[0])
            cut[fld] = {"far": a, "near": b_, "rel": b_ / a - 1 if a else float("nan")}
    out["cut_check"] = cut
    # params for the claims (finest d68 level; ultimate = SF x limit)
    fin = out["levels"].get("d68/L3") or out["levels"].get("d68/L2") or out["levels"].get("d68/L1")
    if fin:
        P_ = out["params"]
        lv = "d68 submodel, finest level"
        P_["d68_corner_s1_ult_pa"] = (SF * abs(fin[f"pocket_foam_s1{'_avg' if D68_MEASURE else ''}_lim_pa"]), "Pa",
                                      f"foam tension peak at the R 3 mm block-pocket corners + beads, ultimate, {lv}, {out['measure']}")
        P_["d68_corner_s3_ult_pa"] = (SF * abs(fin[f"pocket_foam_s3{'_avg' if D68_MEASURE else ''}_lim_pa"]), "Pa",
                                      f"foam compression peak, same, ultimate, {out['measure']}")
        P_["d68_corner_tau_ult_pa"] = (SF * abs(fin[f"pocket_foam_tau{'_avg' if D68_MEASURE else ''}_lim_pa"]), "Pa",
                                       f"foam shear peak, same, ultimate, {out['measure']}")
        P_["d68_bead_s1_ult_pa"] = (SF * abs(fin["bead_s1_lim_pa"]), "Pa", "microballoon bead max principal, ultimate")
        P_["d68_petg_vm_ult_pa"] = (SF * abs(fin["petg_vm_lim_pa"]), "Pa", "PETG block von Mises peak (rounded block), ultimate")
        P_["d68_cutout_tau_dist_ult_pa"] = (SF * abs(fin["cutout_foam_tau_dist_lim_pa"]), "Pa",
                                            "foam shear peak at the R 3 mm elevon cut-out corners, fillet-carries-load "
                                            f"sensitivity, ultimate, {out['measure']}")
        P_["d68_cutout_s1_dist_ult_pa"] = (SF * abs(fin["cutout_foam_s1_dist_lim_pa"]), "Pa",
                                           f"foam tension peak at the same corners, sensitivity, ultimate, {out['measure']}")
        P_["d68_cutout_tau_ult_pa"] = (SF * abs(fin["cutout_foam_tau_lim_pa"]), "Pa",
                                       f"foam shear peak at the cut-out corners, primary path, ultimate, {out['measure']}")
        if conv:
            key = "" if not D68_MEASURE else "_avg"
            P_["d68_corner_gci"] = (max(conv[f"pocket_foam_{f}{key}"]["gci_fine"] for f in ("s1", "s3", "tau")), "-",
                                    "largest GCI of the three pocket-corner foam peaks, d68 submodel, 3 local levels")
        elif all(f"d68/L{l}" in out["levels"] for l in (1, 2)):
            # C2-R4: finest level not finished. Two levels give no observed order, so this is the plain relative
            # change from level 1 to level 2 of the three corner peaks, reported in the GCI's place (it fails the
            # tolerance when the peaks are still moving, which is the honest reading).
            key = "" if not D68_MEASURE else "_avg"
            ch = [abs(abs(out["levels"]["d68/L2"][f"pocket_foam_{f}{key}_lim_pa"])
                      / abs(out["levels"]["d68/L1"][f"pocket_foam_{f}{key}_lim_pa"]) - 1) for f in ("s1", "s3", "tau")]
            P_["d68_corner_gci"] = (max(ch), "-", "TWO LEVELS ONLY (local level 3 not finished): largest relative "
                                    "change level 1 -> 2 of the three pocket-corner foam peaks; not a GCI")
        if cut:
            P_["d68_cut_sens"] = (max(abs(v["rel"]) for v in cut.values()), "-",
                                  "submodel cut planes 0.27/0.37 -> 0.28/0.36 m: largest relative change of the corner peaks")
        ad = out["levels"].get("asdrawn/L3") or out["levels"].get("asdrawn/L2")
        if ad:
            P_["asdrawn_corner_s1_ult_pa"] = (SF * abs(ad[f"pocket_foam_s1{'_avg' if D68_MEASURE else ''}_lim_pa"]), "Pa",
                                              f"as-drawn (sharp, no bead) pocket corner foam tension, same submodel, {out['measure']}")
            P_["asdrawn_corner_s3_ult_pa"] = (SF * abs(ad[f"pocket_foam_s3{'_avg' if D68_MEASURE else ''}_lim_pa"]), "Pa",
                                              f"as-drawn pocket corner foam compression, same submodel, {out['measure']}")
        # C2-R4 (CDR-13 / SW-05): the same corners with the ESC-lead grooves and the spar-slot cap seams run open
        gf = out["levels"].get("d68g/L3") or out["levels"].get("d68g/L2") or out["levels"].get("d68g/L1")
        if gf:
            key = "_avg" if D68_MEASURE else ""
            P_["d68g_corner_s1_ult_pa"] = (SF * abs(gf[f"pocket_foam_s1{key}_lim_pa"]), "Pa",
                                           f"foam tension peak at the pocket corners with the ESC grooves and open slot seams (d68g), ultimate, {out['measure']}")
            P_["d68g_corner_s3_ult_pa"] = (SF * abs(gf[f"pocket_foam_s3{key}_lim_pa"]), "Pa",
                                           f"foam compression peak, same (d68g), ultimate, {out['measure']}")
            same = [l for l in (3, 2, 1) if f"d68g/L{l}" in out["levels"] and f"d68/L{l}" in out["levels"]]
            if same:
                a_, b_ = out["levels"][f"d68g/L{same[0]}"], out["levels"][f"d68/L{same[0]}"]
                P_["d68g_over_d68_s1"] = (abs(a_[f"pocket_foam_s1{key}_lim_pa"]) / abs(b_[f"pocket_foam_s1{key}_lim_pa"]), "-",
                                          f"corner tension with the cuts / without, same local level L{same[0]}")
    for k, v in out["levels"].items():
        print(f"d68 {k}: pocket foam s1 {v['pocket_foam_s1_lim_pa'] / 1e3:.1f} (avg {v['pocket_foam_s1_avg_lim_pa'] / 1e3:.1f}) "
              f"s3 {v['pocket_foam_s3_lim_pa'] / 1e3:.1f} (avg {v['pocket_foam_s3_avg_lim_pa'] / 1e3:.1f}) tau "
              f"{v['pocket_foam_tau_lim_pa'] / 1e3:.1f} (avg {v['pocket_foam_tau_avg_lim_pa'] / 1e3:.1f}) kPa limit at "
              f"{v['pocket_foam_s1_at']}; bead s1 {v['bead_s1_lim_pa'] / 1e6:.2f} MPa; cutout dist tau "
              f"{v['cutout_foam_tau_dist_lim_pa'] / 1e3:.1f} s1 {v['cutout_foam_s1_dist_lim_pa'] / 1e3:.1f} kPa; eq {v['equilibrium_max_N']:.1e}")
    for k, v in conv.items():
        print(f"d68 conv {k}: {[round(x / 1e3, 2) for x in v['f']]} kPa, p {v['p']:.2f}, GCI {100 * v['gci_fine']:.2f} %")
    print("d68 cut check", cut)
    return out


# ------------------------------------------------------------------------------------------------ main
def main():
    levels, stats, beam, valid, files = load_runs(["blk_*.json"])          # as designed: station loads on the hard points
    dlev, dstats, _, dvalid, dfiles = load_runs(["dist_L*O.json"])          # sensitivity: fin-root path
    su2, su2_valid = load_su2("su2_dist_L1.json")
    su2b, _ = load_su2("su2_blk_L1.json")
    # SU2 vs PCG is a solver check on one mesh and one load set: it stays on the R2 runs (C1-R4 loads) in out/R2/
    r2lev = load_runs(["R2/blk_L1*.json"])[0]
    r2dlev = load_runs(["R2/dist_L1.json", "R2/direct_*.json"])[0]
    valid.update(dvalid)
    valid["su2"] = su2_valid
    if beam is None:
        beam = load_runs(["dist_L1.json"])[2]
    stats = {**dstats, **stats}
    res = {"files": files, "files_sensitivity": dfiles,
           "levels_present": {lev: sorted(v.keys()) for lev, v in levels.items()}, "stats": stats,
           "validation": valid}
    vol = None
    # mean element size from the mesh volume (same geometry each level): V from the beam section is not exact,
    # so use the element count only through the ratio h ~ N^(-1/3) with V fixed
    V = 0.0
    for poly in [None]:
        xa = ws.XA
        V = float(np.trapezoid(ws.ZU - ws.ZL, xa)) * ws.L_half       # wing half volume (cut-outs small)
    h = {lev: (V / stats[lev]["elements"]) ** (1 / 3) for lev in stats}
    res["h_mm"] = {lev: h[lev] * 1e3 for lev in h}
    # ---- convergence on the governing quantities
    conv = {}
    for name, (key, field, rule, scale, lab) in GOV.items():
        f = [qty(levels[lev][key], field, rule, scale) for lev in (1, 2, 3) if lev in levels and key in levels[lev]]
        if len(f) == 3:
            g_ = gci([h[1], h[2], h[3]], f)
            conv[name] = {"f": f, "h_mm": [h[1] * 1e3, h[2] * 1e3, h[3] * 1e3], **g_}
    res["convergence"] = conv
    # ---- all cases at the finest level that has them (with the GCI of the matching quantity as the band)
    fine = {}
    for lev in sorted(levels):
        for key, run in levels[lev].items():
            fine[key] = (lev, run)
    table = {}
    for key, (lev, run) in fine.items():
        p = run["post"]
        smax, sy = spar_max(p)
        table[key] = {"level": lev, "w_tip_mm": p["w"][-1] * 1e3, "u_tip_mm": p["u"][-1] * 1e3,
                      "twist_tip_deg": math.degrees(p["twist"][-1]),
                      "w_max_mm": max(abs(v) for v in p["w"]) * 1e3,
                      "spar_sigma_max_mpa": smax / 1e6, "spar_sigma_y_m": sy,
                      "foam": p.get("foam", {}), "petg": p.get("petg", {}),
                      "cg_iter": run["_info"].get("cg_iter"), "rel_residual": run["_info"].get("rel_residual"),
                      "root_reaction_N": run["_info"].get("root_reaction_N"), "applied_N": run["_info"].get("applied_N")}
    res["cases"] = table
    # ---- beam comparison (tape 0, the FEA has no tape; and tape 50 %, the design basis)
    cmp_ = {}
    if beam:
        for key, (lev, run) in fine.items():
            case = "/".join(key.split("/")[:2])
            ms = key.split("/")[2]
            if case not in beam:
                continue
            p = run["post"]
            for field, mset in (("w", "B"), ("u", "B"), ("twist", "T")):
                if ms not in (mset, "O"):
                    continue
                b0 = beam[case]["tape0"][mset]
                b5 = beam[case]["tape50"][mset]
                fe = p[field][-1]
                cmp_.setdefault(case, {})[field] = {
                    "fea": fe, "beam_tape0": b0[field][-1], "beam_tape50": b5[field][-1], "level": lev,
                    "ratio_fea_beam0": fe / b0[field][-1] if b0[field][-1] else float("nan")}
    res["beam_compare"] = cmp_
    # ---- SU2 vs PCG on the same level-1 mesh
    s2 = {}
    for tag, src, ref in (("distributed", su2, r2dlev), ("block", su2b, r2lev)):
      for lev, runs in src.items():
        for key, v in runs.items():
            if lev in ref and key in ref[lev]:
                a, b_ = v["post"], ref[lev][key]["post"]
                s2[f"{tag} L{lev} {key}"] = {f: {"su2": a[f][-1], "pcg": b_[f][-1],
                                            "rel": (a[f][-1] - b_[f][-1]) / b_[f][-1] if b_[f][-1] else float("nan")}
                                       for f in ("w", "u", "twist")}
                s2[f"{tag} L{lev} {key}"]["linsol"] = v["info"].get("linsol")
                s2[f"{tag} L{lev} {key}"]["su2_s"] = v["info"].get("seconds")
    res["su2_vs_pcg"] = s2
    # ---- margins (ultimate = 1.5 x limit)
    have_O = any(k.endswith("/O") for k in table)

    def worst(sub, mats=("foam",), sets=None):
        best = (0.0, None)
        for key, t in table.items():
            if sets and key.split("/")[-1] not in sets:
                continue
            for m_ in mats:
                v = t[m_].get(sub)
                if v is not None and abs(v) > abs(best[0]):
                    best = (v, key)
        return best
    marg = {}
    sp = max(((t["spar_sigma_max_mpa"], k) for k, t in table.items() if k.endswith("/B") or k.endswith("/O")),
             default=(float("nan"), None))
    marg["spar_sigma_ult_pa"] = {"value": SF * sp[0] * 1e6, "allow": M["spar_sigma_allow_pa"], "case": sp[1]}
    # foam and PETG: the orthotropic-tube set O is the physical model; B and T (isotropic tube, as SU2 runs it)
    # bracket it and are kept as the *_BT values
    phys = ("O",) if have_O else ("B", "T")
    for nm, sub, allow, mats in (("foam_s1_p995_ult_pa", "s1_p995_pa", M["xps_tens_allow_pa"], ("foam",)),
                                 ("foam_tau_p995_ult_pa", "tau_p995_pa", M["xps_shear_allow_pa"], ("foam",)),
                                 ("foam_s1_peak_ult_pa", "s1_max_pa", M["xps_tens_allow_pa"], ("foam",)),
                                 ("foam_s3_peak_ult_pa", "s3_min_pa", M["xps_comp_allow_pa"], ("foam",)),
                                 ("foam_tau_peak_ult_pa", "tau_max_pa", M["xps_shear_allow_pa"], ("foam",)),
                                 ("petg_vm_peak_ult_pa", "vm_max_pa", M["petg_bearing_allow_pa"], ("petg",))):
        v, k = worst(sub, mats, phys)
        marg[nm] = {"value": SF * abs(v), "allow": allow, "case": k}
        v2, k2 = worst(sub, mats, ("B", "T"))
        marg[nm + "_BT"] = {"value": SF * abs(v2), "allow": allow, "case": k2}
    for v in marg.values():
        v["MS"] = v["allow"] / v["value"] - 1 if v["value"] else float("inf")
    res["margins"] = marg
    # ---- sensitivity: station loads through the fin root fillet along the chord (distributed introduction)
    sens = {}
    for lev in sorted(dlev):
        for key, run in dlev[lev].items():
            fo = run["post"].get("foam", {})
            sens[key] = {"level": lev, "foam_s1_p995_ult_pa": SF * fo.get("s1_p995_pa", 0),
                         "foam_tau_p995_ult_pa": SF * fo.get("tau_p995_pa", 0),
                         "foam_s1_peak_ult_pa": SF * fo.get("s1_max_pa", 0), "s1_at": fo.get("s1_at"),
                         "foam_tau_peak_ult_pa": SF * fo.get("tau_max_pa", 0), "tau_at": fo.get("tau_at"),
                         "w_tip_mm": run["post"]["w"][-1] * 1e3, "twist_tip_deg": math.degrees(run["post"]["twist"][-1]),
                         "spar_sigma_max_mpa": spar_max(run["post"])[0] / 1e6}
    res["sensitivity_distributed"] = sens
    # ---- tip deflection / semi-span from the FEA (finest, extrapolated where available)
    wt = max((abs(t["w_tip_mm"]) for k, t in table.items() if k.endswith("/B") or k.endswith("/O")), default=float("nan"))
    if "w_tip_G2" in conv:
        wt = max(wt, abs(conv["w_tip_G2"]["f_ext"]))
    res["tip_defl_frac"] = wt / 1e3 / ws.L_half
    OUT.mkdir(exist_ok=True)
    (OUT / "fea_report.json").write_text(json.dumps(res, indent=1, default=float))
    # ---- params for the claims (P:c2fea.*)
    def pv_(v, unit, note):
        return {"value": float(v), "unit": unit, "source": "team/C2/fea/fea_report.py", "status": "UNVERIFIED", "note": note}
    pr = {"_note": "Written by team/C2/fea/fea_report.py from the 3-D FEA outputs. Do not edit by hand.", "c2fea": {}}
    c = pr["c2fea"]
    for n, d in conv.items():
        c[f"{n}_gci"] = pv_(d["gci_fine"], "-", f"GCI fine grid, {GOV[n][4]}")
        c[f"{n}_ext"] = pv_(d["f_ext"], UNITS[n],
                            f"Richardson-extrapolated {GOV[n][4]}")
    for n, d in marg.items():
        c[n] = pv_(d["value"], "Pa", f"FEA {n}, ultimate (1.5 x limit), worst case {d['case']}")
    c["tip_defl_frac"] = pv_(res["tip_defl_frac"], "-", "FEA tip flap deflection / semi-span, limit, tape 0 %, E 70 GPa")
    if s2:
        worst_s2 = max(abs(v[f]["rel"]) for v in s2.values() for f in ("w", "u", "twist")
                       if math.isfinite(v[f]["rel"]) and abs(v[f]["pcg"]) > 1e-4 * (1 if f != "twist" else 0.01))
        c["su2_vs_pcg_rel"] = pv_(worst_s2, "-", "max relative difference SU2 vs in-house PCG, same level-1 mesh, tip w/u/twist")
    if "w" in cmp_.get("G2-HANG-MOTOR/MC-P", {}):
        d = cmp_["G2-HANG-MOTOR/MC-P"]
        c["fea_beam_w_ratio_G2"] = pv_(d["w"]["ratio_fea_beam0"], "-", "FEA / beam (tape 0) tip w, G2")
    if "twist" in cmp_.get("L4-CORNER-SIDE-Y/MC-C", {}):
        d = cmp_["L4-CORNER-SIDE-Y/MC-C"]
        c["fea_beam_twist_ratio_L4"] = pv_(d["twist"]["ratio_fea_beam0"], "-", "FEA / beam (tape 0) tip twist, L4")
    if valid.get("pcg"):
        c["tube_valid_w_err"] = pv_(abs(valid["pcg"]["shear"]["err"]), "-", "tube cantilever tip w vs Timoshenko beam, level 2")
        c["tube_valid_twist_err"] = pv_(abs(valid["pcg"]["torque"]["err"]), "-", "tube cantilever tip twist vs GJ theory, level 2")
    if sens:
        for nm, unit_note in (("foam_s1_p995_ult_pa", "tension"), ("foam_tau_p995_ult_pa", "shear")):
            k = max(sens, key=lambda kk: sens[kk][nm])
            c["sens_" + nm] = pv_(sens[k][nm], "Pa", f"sensitivity, station loads through the fin root fillet along the "
                                                      f"chord: foam {unit_note} 99.5th percentile, ultimate, {k} level {sens[k]['level']}")
    # ---- C2-R3: D-68 geometry (R 3 mm pocket edges, fillet beads, R 3 mm cut-out corners), global-local submodel
    d68 = d68_summary()
    # C2-R4 sensitivity: the same chain with the tube shear modulus at C4's acceptance line (GT-16), not the low corner
    g431 = d68_summary("d68_submodel_g431.json")
    if d68 and g431:
        fin_ = g431["levels"].get("d68/L3") or g431["levels"].get("d68/L2") or g431["levels"].get("d68/L1")
        if fin_:
            key_ = "_avg" if D68_MEASURE else ""
            d68["params"]["d68_g431_corner_s1_ult_pa"] = (SF * abs(fin_[f"pocket_foam_s1{key_}_lim_pa"]), "Pa",
                "foam tension peak at the pocket corners, tube G 4.31 GPa (GT-16 pass line) instead of 3 GPa, ultimate")
            d68["params"]["d68_g431_corner_s3_ult_pa"] = (SF * abs(fin_[f"pocket_foam_s3{key_}_lim_pa"]), "Pa",
                "foam compression peak, same, tube G 4.31 GPa, ultimate")
            d68["g431_levels"] = g431["levels"]
    if d68:
        res["d68"] = d68
        (OUT / "fea_report.json").write_text(json.dumps(res, indent=1, default=float))
        for k, (v, unit, note) in d68["params"].items():
            c[k] = pv_(v, unit, note)
    (HERE / "params.json").write_text(json.dumps(pr, indent=1), encoding="utf-8")
    # ---- figures
    FIG.mkdir(exist_ok=True)
    if beam:
        panels = []
        for lab, key, field, scale in (("flap w, G2 hang by a motor, mm", "G2-HANG-MOTOR/MC-P/O", "w", 1e3),
                                       ("in-plane u, L1 level landing, mm", "L1-LEVEL/MC-C/O", "u", 1e3),
                                       ("twist, L4 corner + side, deg", "L4-CORNER-SIDE-Y/MC-C/O", "twist", 180 / math.pi)):
            fea = {lev: (levels[lev][key]["post"]["y"], [v * scale for v in levels[lev][key]["post"][field]])
                   for lev in sorted(levels) if key in levels[lev]}
            case = "/".join(key.split("/")[:2])
            bm = beam[case]["tape0"]["T" if field == "twist" else "B"]
            panels.append((lab, fea, (bm["y"], [v * scale for v in bm[field]])))
        svg_spanwise(FIG / "C2-03-fea-vs-beam.svg", panels)
    if conv:
        svg_convergence(FIG / "C2-04-fea-convergence.svg", conv)
    svg_section(FIG / "C2-05-fea-section-mesh.svg")
    # ---- print
    print("h mm", {k: round(v, 3) for k, v in res["h_mm"].items()})
    for n, d in conv.items():
        print(f"conv {n}: {[round(v, 4) for v in d['f']]} ext {d['f_ext']:.4f} p {d['p']:.2f} GCI {100 * d['gci_fine']:.3f} %")
    for k, t in sorted(table.items()):
        print(f"L{t['level']} {k}: w {t['w_tip_mm']:.3f} u {t['u_tip_mm']:.3f} tw {t['twist_tip_deg']:.3f} "
              f"spar {t['spar_sigma_max_mpa']:.2f} MPa @ {t['spar_sigma_y_m']:.3f}; foam s1 p99.5 {t['foam'].get('s1_p995_pa', 0) / 1e3:.1f} kPa "
              f"max {t['foam'].get('s1_max_pa', 0) / 1e3:.1f} at {np.round(t['foam'].get('s1_at', [0, 0, 0]), 4).tolist()}; "
              f"tau p99.5 {t['foam'].get('tau_p995_pa', 0) / 1e3:.1f} kPa; petg vm {t['petg'].get('vm_max_pa', 0) / 1e6:.2f} MPa "
              f"| R {np.round(t['root_reaction_N'], 2).tolist()} F {np.round(t['applied_N'], 2).tolist()}")
    for k, v in cmp_.items():
        print("beam", k, json.dumps(v))
    for k, v in s2.items():
        print("su2 vs pcg", k, json.dumps(v))
    for k, v in marg.items():
        print(f"margin {k}: {v['value'] / 1e3:.1f} kPa vs {v['allow'] / 1e3:.0f} kPa, MS {v['MS']:+.2f} ({v['case']})")
    print("tip defl frac", res["tip_defl_frac"])
    for k, v in sorted(sens.items()):
        print(f"sens L{v['level']} {k}: foam s1 p99.5 {v['foam_s1_p995_ult_pa'] / 1e3:.0f} kPa ult, tau p99.5 "
              f"{v['foam_tau_p995_ult_pa'] / 1e3:.0f}, s1 peak {v['foam_s1_peak_ult_pa'] / 1e3:.0f} at {np.round(v['s1_at'] or [0,0,0], 4).tolist()}, "
              f"w {v['w_tip_mm']:.3f} tw {v['twist_tip_deg']:.3f} spar {v['spar_sigma_max_mpa']:.2f}")


if __name__ == "__main__":
    main()
