"""T-076c step 3 (hub escalation s2.4 / s3.4 item 3, D-220): corrected judging code for hub FEA results.   Imported by t076c_ha.py (no CLI).   CATEGORY: FEA post-processing.
Replaces the unweighted whole-hub 99th percentile of the first principal stress (kept alongside as the 'old' columns, for continuity) by:
  (1) per-zone VOLUME-weighted percentiles (Gauss weight x detJ, computed from the mesh because `res` carries none), p99 and p99.9;
  (2) a corner-exclusion distance: Gauss points within EXCL mm (default 0.5, EST per the audit) of a TIED re-entrant corner (a node on both a hub / other-material interface face and a free hub face) are left out of the percentile and of the 'max excl.' column;
      the excluded volume fraction is reported (it is never hidden);
  (3) for metal: von Mises against yield / KF (KF 1.725, never relaxed);
  (4) for PETG: an orientation split for a declared print normal n (layer-normal stress sigma_nn against 9.5 MPa interlayer EST, in-layer maximum in-plane principal against 20 MPa EST, both / KP).
Zones: whole hub, and the load-path zones of t076b_run.regions (collar, bore wall, floor band, sleeves outside the block, block forward of the floor).
Units: mm, N, MPa.  Hub frame as fea_hub (x aft, y span, z up).
"""
import numpy as np
from scipy.spatial import cKDTree

EXCL_DEFAULT = 0.5


def gauss_weights(FA, X, E, hub_mask):
    """per Gauss point volume weight (mm3) of the hub elements: GW[g] * detJ (tet10, 4-point rule, as fea_arm.assemble)."""
    XE = X[E[hub_mask]]; w = np.zeros((XE.shape[0], 4))
    for g in range(4):
        J = np.einsum('ai,eaj->eij', FA.DN[g], XE); w[:, g] = FA.GW[g] * np.linalg.det(J)
    return w.reshape(-1)


def corner_nodes(X, E, M):
    """nodes (corner nodes only) on a hub / non-hub interface AND on a free hub face = the tied re-entrant edges (sleeve mouths, bore-floor / tube-end ring, pin and hole edges)."""
    C4 = E[:, :4]
    faces = np.concatenate([C4[:, [0, 1, 2]], C4[:, [0, 1, 3]], C4[:, [0, 2, 3]], C4[:, [1, 2, 3]]]); fe = np.tile(np.arange(len(E)), 4)
    key = np.sort(faces, 1)
    # unique faces with counts; map each face-instance to its unique id
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0])); ks = key[order]
    new = np.ones(len(ks), bool); new[1:] = np.any(ks[1:] != ks[:-1], axis=1)
    gid = np.cumsum(new) - 1; ginv = np.empty(len(ks), np.int64); ginv[order] = gid
    cnt = np.bincount(gid)
    hub = (M == 0)[fe]
    free_hub = (cnt[ginv] == 1) & hub
    # interface: face with 2 instances, one hub one non-hub
    nh = np.bincount(gid, weights=hub[order].astype(float)); itf_g = (cnt == 2) & (nh == 1)
    itf = itf_g[ginv] & hub
    nf = np.unique(faces[free_hub]); ni = np.unique(faces[itf])
    return np.intersect1d(nf, ni)


def exclusion_mask(X, xh, edge_nodes, excl):
    """True for hub Gauss points farther than excl mm from every tied-edge node."""
    if excl <= 0 or len(edge_nodes) == 0:
        return np.ones(len(xh), bool)
    d, _ = cKDTree(X[edge_nodes]).query(xh, k=1)
    return d > excl


def wpercentile(vals, w, qs):
    """weighted percentile(s) (qs in %), vals (n,), w (n,): value at which the cumulative volume fraction reaches q."""
    o = np.argsort(vals); v = vals[o]; c = np.cumsum(w[o]); c /= c[-1]
    return [float(v[min(np.searchsorted(c, q / 100.0), len(v) - 1)]) for q in qs]


def von_mises(sig):
    xx, yy, zz, yz, xz, xy = [sig[..., i] for i in range(6)]
    return np.sqrt(0.5 * ((xx - yy) ** 2 + (yy - zz) ** 2 + (zz - xx) ** 2) + 3 * (yz ** 2 + xz ** 2 + xy ** 2))


def inplane_principal(sig, n):
    """max principal of the stress restricted to the plane normal to the unit vector n (layer plane); sig (...,6) Voigt (xx,yy,zz,yz,xz,xy)."""
    xx, yy, zz, yz, xz, xy = [sig[..., i] for i in range(6)]
    T = np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1), np.stack([xz, yz, zz], -1)], -2)
    n = np.asarray(n, float); n /= np.linalg.norm(n)
    a = np.cross(n, [1.0, 0, 0]) if abs(n[0]) < 0.9 else np.cross(n, [0, 1.0, 0]); a /= np.linalg.norm(a); b = np.cross(n, a)
    Bm = np.stack([a, b], 0)                                  # (2,3)
    T2 = np.einsum('ik,...kl,jl->...ij', Bm, T, Bm)
    return np.linalg.eigvalsh(T2)[..., -1]


def zone_masks(regions_fn, xh):
    lab, names = regions_fn(xh)
    Z = {'whole hub': np.ones(len(xh), bool)}
    for k, nm in enumerate(names):
        Z[nm] = lab == k
    return {k: z for k, z in Z.items() if z.any()}


def judge(H, FA, res, Cs, labels, regions_fn, mode, allow, excl=EXCL_DEFAULT, print_normal=(0, 0, 1.0), allow_il=None, chunk=24, verbose=True, old=True):
    """Evaluate the combos Cs (n, ncoef) on the hub of `res`.  mode 'metal': von Mises, allow = yield / KF (MPa).  mode 'petg': in-layer (allow = 20 / KP) and layer-normal (allow_il = 9.5 / KP) for print_normal.
    Returns dict zone -> dict(stat -> (value, case label)) for: old_p99 (unweighted, first principal), w_p99, w_p999 (volume weighted, corner-excluded), max_all, max_excl; plus rf = allow / value."""
    S, Mm, xg = res['S'], res['M'], res['xg']; X, E = res['X'], res['E']
    nb = S.shape[0]; hub = Mm == 0
    Sh = S[:, hub].reshape(nb, -1, 6); xh = xg[hub].reshape(-1, 3)
    w = gauss_weights(FA, X, E, hub); edge = corner_nodes(X, E, Mm); keep = exclusion_mask(X, xh, edge, excl)
    Z = zone_masks(regions_fn, xh)
    zinfo = {k: dict(n_gp=int(z.sum()), vol_mm3=float(w[z].sum()), excluded_vol_frac=float(w[z & ~keep].sum() / w[z].sum())) for k, z in Z.items()}
    if verbose:
        print('judge: %d hub Gauss points, hub volume %.0f mm3 (sum of weights), %d tied-edge nodes, exclusion %.2f mm removes %.2f %% of the hub volume' % (len(xh), w.sum(), len(edge), excl, 100 * w[~keep].sum() / w.sum()), flush=True)
    zk = list(Z)
    stats = ('old_p99', 'w_p99', 'w_p999', 'max_all', 'max_excl')
    best = {k: {s: (-1.0, None) for s in stats} for k in zk}
    if mode == 'petg':
        for k in zk: best[k].update({'il_w_p999': (-1.0, None), 'il_max_excl': (-1.0, None), 'norm_w_p999': (-1.0, None), 'norm_max_excl': (-1.0, None)})
    Cs = np.asarray(Cs)
    for ci in range(0, len(Cs), chunk):
        sig = np.einsum('ck,kps->cps', Cs[ci:ci + chunk], Sh)
        p1 = FA.principal(sig)[0] if (old or mode != 'metal') else None
        if mode == 'metal': eq = von_mises(sig)
        else:
            nn = np.array(print_normal, float); nn /= np.linalg.norm(nn)
            eqs = {'il': inplane_principal(sig, nn), 'norm': np.einsum('i,cpij,j->cp', nn, _full(sig), nn)}
        for j in range(sig.shape[0]):
            lab = labels[ci + j]
            for k, z in Z.items():
                zz = z; ze = z & keep
                def upd(name, val):
                    if val > best[k][name][0]: best[k][name] = (float(val), lab)
                if old: upd('old_p99', np.percentile(p1[j][zz], 99))
                if mode == 'metal':
                    v = eq[j]; upd('max_all', v[zz].max())
                    if ze.any():
                        upd('max_excl', v[ze].max()); a, b = wpercentile(v[ze], w[ze], (99, 99.9)); upd('w_p99', a); upd('w_p999', b)
                else:
                    for nm_, v in (('il', eqs['il'][j]), ('norm', eqs['norm'][j])):
                        if ze.any():
                            upd(nm_ + '_max_excl', v[ze].max()); upd(nm_ + '_w_p999', wpercentile(v[ze], w[ze], (99.9,))[0])
                    upd('max_all', p1[j][zz].max())
                    if ze.any(): upd('max_excl', p1[j][ze].max()); a, b = wpercentile(p1[j][ze], w[ze], (99, 99.9)); upd('w_p99', a); upd('w_p999', b)
        if verbose and (ci // chunk) % 10 == 0: print('  judge combos %d / %d' % (min(ci + chunk, len(Cs)), len(Cs)), flush=True)
    out = {}
    for k in zk:
        r = {s: dict(value=v[0], case=v[1]) for s, v in best[k].items()}
        for s in list(r):
            if r[s]['value'] > 0:
                al = allow_il if (mode == 'petg' and s.startswith('norm')) else allow
                r[s]['rf'] = al / r[s]['value']
        r['_zone'] = zinfo[k]; out[k] = r
    return out


def _full(sig):
    xx, yy, zz, yz, xz, xy = [sig[..., i] for i in range(6)]
    return np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1), np.stack([xz, yz, zz], -1)], -2)
