"""3-D layered hexahedral mesh of one fin quarter (K09-L), from D3/D5 as-designed geometry (library only).

Planform (x aft, z away from the wing) meshed in gmsh (OpenCASCADE, all-quad by subdivision), then extruded through
the board thickness (y, + outboard) layer by layer:
    face 0.1 | core (nc el) | mid face 0.2 (two faces) | core (nc el) | face 0.1     (two 4.8 mm boards, 9.6 mm)
plus a 1 mm outer layer on both sides where there is an edge strip, the D5 shoe, or the tube bar.
Zones (planform):  FIN (the D3 half-fin with the D5 square tip), STRIP (10 mm band under the sloped top edge, LE to the
step front), SHOE (D5 legs + cheeks, rigid printed part over the board), BAR (the CF tube as a square bar the full
laminate thickness, EI matched), LINK (tube wall + LE fillet between the bar and the board LE, 3 GPa).
Optional brace: hexahedra swept from a bar face quad at the collar ear height to the anchor on the wing.
"""
import math

import numpy as np

MAT = {"FACE": 0, "CORE": 1, "STRIP": 2, "BAR": 3, "LINK": 4, "SHOE": 5, "BRACE": 6, "TAIL": 7}


def _poly_contains(poly, pts):
    """Even-odd point-in-polygon, poly (n, 2), pts (m, 2)."""
    x, y = pts[:, 0], pts[:, 1]
    inside = np.zeros(len(pts), bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-300) + x1)
        inside ^= c
    return inside


def planform(g, geo, top, z_stp, shoes, h, h_loc, box, a_bar, z_split, tail=None):
    """gmsh all-quad planform mesh. Returns xz (n, 2), quads (m, 4) CCW in (x, z), zone label per quad."""
    import gmsh
    gmsh.initialize(["-noenv"])
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("fin")
    occ = gmsh.model.occ
    rx = np.array([p[0] for p in geo["root"]])
    rz = np.array([p[1] for p in geo["root"]])
    o = np.argsort(rx)
    rx, rz = rx[o], rz[o]
    zr = lambda x: float(np.interp(x, rx, rz))
    x_le, x_te, x_s = geo["x_le"], g["x_te"], geo["x_step"]
    x_t = g["tube_x"]
    z0, z_end, z_tl = geo["z_clamp"], geo["z_end"], geo["z_top_le"]
    fin_poly = [(x_le, zr(x_le)), (x_le, z_tl), (x_s, g["hh"]), (x_s, z_stp), (x_te, z_stp), (x_te, zr(x_te))]
    fin_poly += [(float(x), float(z)) for x, z in zip(rx[::-1], rz[::-1]) if x_le + 1e-4 < x < x_te - 1e-4]

    def poly(pts):
        p = [occ.addPoint(x, z, 0) for x, z in pts]
        ln = [occ.addLine(p[i], p[(i + 1) % len(p)]) for i in range(len(p))]
        return occ.addPlaneSurface([occ.addCurveLoop(ln)])

    fin = poly(fin_poly)
    slope = (g["hh"] - z_tl) / (x_s - x_le)
    dw = g["e_w"] * math.sqrt(1 + slope * slope)
    strip = poly([(x_le, z_tl), (x_s, g["hh"]), (x_s, g["hh"] - dw), (x_le, z_tl - dw)])
    tools = [(2, strip)]
    xb = x_t + a_bar / 2
    tools.append((2, poly([(xb, z_tl - dw), (x_le, z_tl - dw), (x_le, z_tl), (xb, z_tl)])))   # strip over the link
    if tail:                            # station-collar tail tongue under the strip band (D3 R3/R4)
        x1, td = tail
        zt1 = z_tl + slope * (x1 - x_le)
        tools.append((2, poly([(xb, z_tl - dw - td), (x_le, z_tl - dw - td), (x1, zt1 - dw - td), (x1, zt1 - dw),
                               (x_le, z_tl - dw), (xb, z_tl - dw)])))
    for (xa, za, xb, zb) in shoes:
        tools.append((2, occ.addRectangle(xa, za, 0, xb - xa, zb - za)))
    zs = sorted({z0, *[z for z in z_split if z0 < z < z_end], z_end})
    for za, zb in zip(zs[:-1], zs[1:]):
        tools.append((2, occ.addRectangle(x_t - a_bar / 2, za, 0, a_bar, zb - za)))
    zl = sorted({z0, *[z for z in z_split if z0 < z < z_tl], z_tl})
    for za, zb in zip(zl[:-1], zl[1:]):
        tools.append((2, occ.addRectangle(x_t + a_bar / 2, za, 0, x_le - x_t - a_bar / 2, zb - za)))
    occ.fragment([(2, fin)], tools)
    occ.synchronize()
    fin_arr = np.array(fin_poly)
    keep = []
    for dim, tag in gmsh.model.getEntities(2):
        cx, cz, _ = occ.getCenterOfMass(dim, tag)
        in_fin = _poly_contains(fin_arr, np.array([[cx, cz]]))[0]
        in_bar = abs(cx - x_t) <= a_bar / 2 + 1e-9 and z0 <= cz <= z_end
        in_link = x_t + a_bar / 2 <= cx <= x_le and z0 <= cz <= z_tl
        if in_fin or in_bar or in_link:
            keep.append(tag)
        else:
            occ.remove([(2, tag)], recursive=True)
    occ.removeAllDuplicates()
    occ.synchronize()
    f = gmsh.model.mesh.field
    b = f.add("Box")
    f.setNumber(b, "VIn", 2 * h_loc)
    f.setNumber(b, "VOut", 2 * h)
    f.setNumber(b, "XMin", box[0])
    f.setNumber(b, "XMax", box[1])
    f.setNumber(b, "YMin", box[2])
    f.setNumber(b, "YMax", box[3])
    f.setNumber(b, "Thickness", 0.03)
    b2 = f.add("Box")                       # tube bar and LE link at half the global size
    f.setNumber(b2, "VIn", h)
    f.setNumber(b2, "VOut", 2 * h)
    f.setNumber(b2, "XMin", x_t - a_bar / 2 - 1e-3)
    f.setNumber(b2, "XMax", x_le + 1e-3)
    f.setNumber(b2, "YMin", z0 - 1e-3)
    f.setNumber(b2, "YMax", z_end + 1e-3)
    f.setNumber(b2, "Thickness", 0.01)
    mn = f.add("Min")
    f.setNumbers(mn, "FieldsList", [b, b2])
    f.setAsBackgroundMesh(mn)
    for k, v in (("Mesh.MeshSizeFromPoints", 0), ("Mesh.MeshSizeFromCurvature", 0),
                 ("Mesh.MeshSizeExtendFromBoundary", 0), ("Mesh.Algorithm", 8), ("Mesh.RecombineAll", 1),
                 ("Mesh.RecombinationAlgorithm", 1), ("Mesh.SubdivisionAlgorithm", 1), ("Mesh.Smoothing", 5)):
        gmsh.option.setNumber(k, v)
    gmsh.model.mesh.generate(2)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    xyz = np.asarray(xyz).reshape(-1, 3)
    idx = {int(t): i for i, t in enumerate(tags)}
    quads = []
    for dim, tag in gmsh.model.getEntities(2):
        et, _, en = gmsh.model.mesh.getElements(2, tag)
        for t, conn in zip(et, en):
            if t != 3:
                raise RuntimeError("planform: non-quad element type %d" % t)
            quads.append(np.asarray(conn, int).reshape(-1, 4))
    gmsh.finalize()
    quads = np.vectorize(idx.get)(np.vstack(quads))
    used = np.unique(quads)
    remap = -np.ones(len(xyz), int)
    remap[used] = np.arange(len(used))
    xz = xyz[used][:, :2]
    quads = remap[quads]
    # make every quad counter-clockwise in (x, z)
    P = xz[quads]
    area2 = np.sum(P[:, :, 0] * np.roll(P[:, :, 1], -1, 1) - np.roll(P[:, :, 0], -1, 1) * P[:, :, 1], axis=1)
    quads[area2 < 0] = quads[area2 < 0][:, ::-1]
    return xz, quads, fin_arr, zr


def build(g, geo, top, z_stp, *, side, h, h_loc, shoes, nc=2, t_face=1e-4, brace=None, root_free=(), z_split=(),
          tail=None):
    """tail: None or (x_end, depth below the strip band): the PETG collar tail tongue replaces the board there and
    the edge strips run on over the LE link to the tube bar (strip tails bonded in the collar slots)."""
    """Layered hex mesh. shoes: [(x0, z0, x1, z1)] rigid D5 regions; brace: None or dict(z_ear, anchor (x, y, z),
    k (N/m)). Returns a dict with nodes, hexes, mat, markers and the node sets the drivers need."""
    t_b = g["layers"] * g["t_board"]
    e_t = g["e_t"]
    a_bar = t_b + 2 * e_t
    x_t = g["tube_x"]
    z0, z_end, z_tl = geo["z_clamp"], geo["z_end"], geo["z_top_le"]
    box = (geo["x_step"] - 0.035, g["x_te"] + 0.001, z_stp - 0.06, g["hh"] + 0.001)
    splits = list(z_split) + ([brace["z_ear"]] if brace else [])
    xz, quads, fin_poly, zr = planform(g, geo, top, z_stp, shoes, h, h_loc, box, a_bar, splits, tail)
    c = xz[quads].mean(axis=1)
    zone = np.full(len(quads), "FIN", object)
    in_bar = (np.abs(c[:, 0] - x_t) <= a_bar / 2) & (c[:, 1] >= z0) & (c[:, 1] <= z_end)
    in_link = (c[:, 0] > x_t + a_bar / 2) & (c[:, 0] < geo["x_le"]) & (c[:, 1] <= z_tl)
    slope = (g["hh"] - z_tl) / (geo["x_step"] - geo["x_le"])
    ztop = z_tl + slope * (c[:, 0] - geo["x_le"])
    dw = g["e_w"] * math.sqrt(1 + slope * slope)
    x_s0 = (x_t + a_bar / 2) if tail else geo["x_le"]
    ztop = np.where(c[:, 0] < geo["x_le"], z_tl, ztop)
    in_strip = (c[:, 0] > x_s0) & (c[:, 0] < geo["x_step"]) & (c[:, 1] > ztop - dw)
    in_tail = np.zeros(len(quads), bool)
    if tail:
        in_tail = (c[:, 0] > x_s0) & (c[:, 0] < tail[0]) & (c[:, 1] > ztop - dw - tail[1])
    in_shoe = np.zeros(len(quads), bool)
    for (xa, za, xb, zb) in shoes:
        in_shoe |= (c[:, 0] > xa) & (c[:, 0] < xb) & (c[:, 1] > za) & (c[:, 1] < zb)
    zone[in_strip] = "STRIP"
    zone[in_shoe] = "SHOE"
    zone[in_link & ~in_strip] = "LINK"
    zone[in_bar] = "BAR"
    # through-thickness levels
    tf, hb = t_face, t_b / 2
    core = lambda y0, y1: list(np.linspace(y0, y1, nc + 1))
    lv = [-hb] + core(-hb + tf, -tf) + core(tf, hb - tf) + [hb]
    kinds = ["face"] + ["core"] * nc + ["mid"] + ["core"] * nc + ["face"]
    y_lo, y_hi = -hb - e_t, hb + e_t
    npf = len(xz)
    nodes = [np.column_stack([xz[:, 0], np.full(npf, y), xz[:, 1]]) for y in lv]
    base = {k: k * npf for k in range(len(lv))}
    outer = np.isin(zone, ["STRIP", "SHOE", "BAR"])
    pn = np.unique(quads[outer])
    lo_id = -np.ones(npf, int)
    hi_id = -np.ones(npf, int)
    nb = len(lv) * npf
    lo_id[pn] = nb + np.arange(len(pn))
    hi_id[pn] = nb + len(pn) + np.arange(len(pn))
    nodes.append(np.column_stack([xz[pn, 0], np.full(len(pn), y_lo), xz[pn, 1]]))
    nodes.append(np.column_stack([xz[pn, 0], np.full(len(pn), y_hi), xz[pn, 1]]))
    nodes = np.vstack(nodes)
    q = quads[:, ::-1]                       # (x, z) CCW -> normal along -y; reversed -> +y, the extrusion direction
    hexes, mat, lay, qid = [], [], [], []
    zmat = {"FIN": None, "STRIP": None, "SHOE": MAT["SHOE"], "BAR": MAT["BAR"], "LINK": MAT["LINK"]}
    for k in range(len(lv) - 1):
        bot, topn = base[k] + q, base[k + 1] + q
        hexes.append(np.hstack([bot, topn]))
        kind = kinds[k]
        m = np.array([zmat[z] if zmat[z] is not None else (MAT["CORE"] if kind == "core" else MAT["FACE"])
                      for z in zone])
        m[in_tail & np.isin(zone, ["FIN", "STRIP", "LINK"])] = MAT["TAIL"]
        mat.append(m)
        lay.append(np.full(len(q), k))
        qid.append(np.arange(len(q)))
    sel = np.where(outer)[0]
    hexes.append(np.hstack([lo_id[q[sel]], base[0] + q[sel]]))
    hexes.append(np.hstack([base[len(lv) - 1] + q[sel], hi_id[q[sel]]]))
    for sgn in (-1, 1):
        mat.append(np.array([MAT["STRIP"] if zone[i] == "STRIP" else zmat[zone[i]] for i in sel]))
        lay.append(np.full(len(sel), sgn * 100))
        qid.append(sel)
    hexes, mat, lay, qid = np.vstack(hexes), np.concatenate(mat), np.concatenate(lay), np.concatenate(qid)
    out = {"nodes": nodes, "hexes": hexes, "mat": mat, "layer": lay, "quad": qid, "xz": xz, "quads": quads,
           "in_tail": in_tail,
           "zone": zone, "levels": lv, "kinds": kinds, "y_out": (y_lo, y_hi), "a_bar": a_bar, "fin_poly": fin_poly,
           "zr": zr, "npf": npf}
    if brace:
        _add_brace(out, brace, x_t, a_bar, y_lo)
    _markers(out, g, geo, side, root_free, shoes, tf)
    return out


def _add_brace(m, br, x_t, a_bar, y_lo):
    """Hexahedra swept from the bar's inboard outer face quad just above the ear height to the anchor point."""
    xz, quads, zone, npf = m["xz"], m["quads"], m["zone"], m["npf"]
    c = xz[quads].mean(axis=1)
    cand = np.where((zone == "BAR") & (c[:, 1] > br["z_ear"]))[0]
    qi = cand[np.argmin(np.hypot(c[cand, 0] - x_t, c[cand, 1] - br["z_ear"]))]
    nodes = m["nodes"]
    lo = np.where(np.isclose(nodes[:, 1], y_lo))[0]
    lut = {(round(nodes[n, 0], 9), round(nodes[n, 2], 9)): n for n in lo}
    start = np.array([lut[(round(xz[p, 0], 9), round(xz[p, 1], 9))] for p in quads[qi]])
    P0 = nodes[start].mean(axis=0)
    v = np.asarray(br["anchor"], float) - P0
    L = float(np.linalg.norm(v))
    nseg = max(6, int(math.ceil(L / br["h"])))
    rings = [start]
    new = []
    nn = len(nodes)
    for s in range(1, nseg + 1):
        pts = nodes[start] + v * s / nseg
        rings.append(nn + np.arange(4))
        new.append(pts)
        nn += 4
    nodes = np.vstack([nodes] + new)
    hx = np.array([np.concatenate([rings[s], rings[s + 1]]) for s in range(nseg)])
    from hexfe import element_volumes
    if element_volumes(nodes, hx[:1])[0] < 0:
        hx = np.array([np.concatenate([rings[s + 1], rings[s]]) for s in range(nseg)])
    A = 0.5 * np.linalg.norm(np.cross(nodes[start[2]] - nodes[start[0]], nodes[start[3]] - nodes[start[1]]))
    An = abs(np.dot(np.cross(nodes[start[2]] - nodes[start[0]], nodes[start[3]] - nodes[start[1]]) / 2, v / L))
    m["nodes"] = nodes
    m["hexes"] = np.vstack([m["hexes"], hx])
    m["mat"] = np.concatenate([m["mat"], np.full(nseg, MAT["BRACE"])])
    m["layer"] = np.concatenate([m["layer"], np.full(nseg, 999)])
    m["quad"] = np.concatenate([m["quad"], np.full(nseg, -1)])
    m["brace"] = {"L": L, "A": A, "A_normal": An, "E_eq": br["k"] * L / An, "end": rings[-1], "start": start,
                  "n": v / L, "P0": P0}


def _markers(m, g, geo, side, root_free, shoes, tf):
    from hexfe import boundary_quads, quad_areas_centroids
    nodes, hexes = m["nodes"], m["hexes"]
    bq, owner = boundary_quads(hexes)
    X = nodes[bq]
    x, y, z = X[:, :, 0], X[:, :, 1], X[:, :, 2]
    zr = m["zr"]
    on_root = np.all(np.abs(z - np.vectorize(zr)(x)) < 1e-7, axis=1) & ~np.all(np.isclose(y, y[:, :1]), axis=1)
    mid = np.all(np.abs(y) <= tf + 1e-9, axis=1)
    xc = x.mean(axis=1)
    free = np.zeros(len(bq), bool)
    for a, b in root_free:
        free |= (xc > a) & (xc < b)
    mk = {"ROOT_PIN": bq[on_root & mid & ~free]}
    z0, z_end = geo["z_clamp"], geo["z_end"]
    mk["LE_BOSS"] = bq[np.all(np.abs(x - geo["x_le"]) < 1e-9, axis=1) & np.all(z <= z0 + 1e-9, axis=1)]
    bar_x = np.all(np.abs(x - g["tube_x"]) <= m["a_bar"] / 2 + 1e-9, axis=1)
    mk["BAR_BOT"] = bq[np.all(np.abs(z - z0) < 1e-9, axis=1)]
    mk["BAR_TOP"] = bq[np.all(np.abs(z - z_end) < 1e-9, axis=1) & bar_x]
    y_lo, y_hi = m["y_out"]
    in_shoe = np.zeros(len(bq), bool)
    zc = z.mean(axis=1)
    for (xa, za, xb, zb) in shoes:
        in_shoe |= (xc > xa) & (xc < xb) & (zc > za) & (zc < zb)
    for tag, yv in (("SHOE_P", y_hi), ("SHOE_M", y_lo)):
        s = in_shoe & np.all(np.abs(y - yv) < 1e-9, axis=1)
        xm, zm = np.median(xc[s]), np.median(zc[s])
        for i, (cx, cz) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            ss = s & ((xc > xm) == bool(cx)) & ((zc > zm) == bool(cz))
            mk[f"{tag}{i}"] = bq[ss]
    if "brace" in m:
        e = m["brace"]["end"]
        mk["BRACE_END"] = np.array([[e[0], e[3], e[2], e[1]]])
    m["markers"] = {k: v for k, v in mk.items() if len(v)}
    m["marker_geom"] = {k: quad_areas_centroids(nodes, v) for k, v in m["markers"].items()}


def pad_tractions(m, F, P, names):
    """Least-norm uniform tractions on the named markers with resultant F (N) acting at point P (no extra moment)."""
    rows = []
    A_all, C_all = [], []
    for n in names:
        a, cc = m["marker_geom"][n]
        A_all.append(a.sum())
        C_all.append((a[:, None] * cc).sum(axis=0) / a.sum())
    nk = len(names)
    Aeq = np.zeros((6, 3 * nk))
    for k in range(nk):
        Aeq[0:3, 3 * k:3 * k + 3] = np.eye(3) * A_all[k]
        r = C_all[k] - np.asarray(P)
        Aeq[3:6, 3 * k:3 * k + 3] = A_all[k] * np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])
    b = np.concatenate([np.asarray(F, float), np.zeros(3)])
    t = np.linalg.lstsq(Aeq, b, rcond=None)[0]
    res = np.linalg.norm(Aeq @ t - b)
    return [(names[k], t[3 * k:3 * k + 3]) for k in range(nk)], res
