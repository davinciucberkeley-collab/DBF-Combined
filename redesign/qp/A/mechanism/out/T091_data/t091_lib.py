"""T-091 helper: build the T-085 credible FE (fe_a.py, unchanged) with structural-change candidates applied as post-build edits of the Frame
(F.el / F.mass / F.n), solve modes, pitch gain margin (D-191 method, sitl/fu_cage.py configure('t089'), unchanged) and forced response (t089_fvib.py Modal / summarize, unchanged).
Category: FEA-lite beam frame + linear control analysis + modal forced response.  Nothing is applied to the CAD, the BOM or the tree (fe_a.py, fu_cage.py not edited)."""
import os, sys, math, json, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.abspath(os.path.join(HERE, '..'))
for p in (HERE, os.path.join(OUT, 'T089_data'), os.path.join(OUT, 'T085_data'), os.path.join(OUT, 'T084_data'), os.path.join(QPA, 'sitl'), os.path.join(QPA, 'structures')): sys.path.insert(0, p)
sys.dont_write_bytecode = True
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import fe_a
import t085_modes as T, t085_bounds as B
import t084_cell_props as CP
from t084_modes_probe import fekw
for k, v in B.CASES.items(): T.PACKS[k] = v
KINDS = ('kd', 'nom', 'hi')
PAD_NOM = [k for k in B.CASES if k.startswith('pad nom (50A') and 'K 0.25' not in k][0]
PAD_NAMES = list(B.CASES) + ['rigid+rot']
GROUPS = [(c, h, n) for c in ('nominal', 'lower') for h in ('al6061', 'petg') for n in PAD_NAMES]
E = fe_a.E_CF; G = fe_a.G_CF


def tube(od, idm): return math.pi/4*(od**2-idm**2), math.pi/64*(od**4-idm**4)


# ---------------- post-build edits (F is a fe_a.Frame, before solve)
def edit(F, sel, fA=1.0, fIy=1.0, fIz=1.0, fJ=1.0, dm_per_m=0.0):
    """scale stiffness of the elements for which sel(a, b, grp) is true; dm_per_m = added mass per metre (kg/m) on those elements"""
    new = []
    for el in F.el:
        a, b, EA, EIy, EIz, GJ, rA, vref, grp = el
        if sel(a, b, grp): el = (a, b, EA*fA, EIy*fIy, EIz*fIz, GJ*fJ, rA+dm_per_m, vref, grp)
        new.append(el)
    F.el = new


def is_bridge(a, b, grp): return grp == 'bridge' and (a.startswith('bb') or a.startswith('hub>s+0.000') or b == 's+0.000')   # the single bridge tube (bb -> spar centre)
def is_strut(a, b, grp): return grp == 'bridge' and a.startswith('hub>s') and 's+0.000' not in a and not a.startswith('hub>s+0.000') or (grp == 'bridge' and a == 'hub' and b.startswith('hub>') is False and False)


def bridge_names(F):
    """classify bridge-group elements: main bridge (-> s+0.000) or V strut"""
    main, strut = [], []
    for el in F.el:
        a, b, grp = el[0], el[1], el[8]
        if grp != 'bridge': continue
        tag = (a + '|' + b)
        (main if 's+0.000' in tag else strut).append(el)
    return main, strut


def edit_bridge(F, which, fA=1.0, fIy=1.0, fIz=1.0, fJ=1.0, dA=0.0, rho=fe_a.RHO_CF):
    """which = 'main' | 'strut'.  dA = added cross-section area (m2) of CF for mass."""
    new = []
    for el in F.el:
        a, b, EA, EIy, EIz, GJ, rA, vref, grp = el
        tag = a + '|' + b
        if grp == 'bridge':
            isMain = 's+0.000' in tag
            if (which == 'main') == isMain: el = (a, b, EA*fA, EIy*fIy, EIz*fIz, GJ*fJ, rA+rho*dA, vref, grp)
        new.append(el)
    F.el = new


def spar_zone(F, ymax, fA=1.0, fIy=1.0, fIz=1.0, fJ=1.0, dA=0.0, rho=fe_a.RHO_CF):
    """stiffen spar-group elements with mid |y| <= ymax (a stiffer centre spar section, a sleeve, or a plate doubler)"""
    new = []
    for el in F.el:
        a, b, EA, EIy, EIz, GJ, rA, vref, grp = el
        if grp == 'spar':
            ya, yb = F.n[a][1], F.n[b][1]
            if abs(0.5*(ya+yb)) <= ymax: el = (a, b, EA*fA, EIy*fIy, EIz*fIz, GJ*fJ, rA+rho*dA, vref, grp)
        new.append(el)
    F.el = new


def add_beam(F, a, b, E_, tube_od_id, grp='bridge', nseg=3, vref=(0, 0, 1), name=None):
    A, I = tube(*tube_od_id)
    F.beam(a, b, E_*A, E_*I, E_*I, G_[0]*2*I if False else 3e9*2*I, fe_a.RHO_CF*A, vref, grp, nseg=nseg)


# ---------------- candidates: name -> dict(mod=callable(F, kind, ctx), over=dict for fe_a.build, pack=dict for pack_cfg overrides, fc=node name, dm_g=EST mass change g)
def make_candidates():
    C = {}
    C['B0 as drawn (T-085 model)'] = dict()
    return C


def solve(kind, cell, hub, pad, cand=None, nmodes=150):
    cand = cand or {}
    cl = None if cell == 'spar' else CP.cell_for(kind, lower=(cell == 'lower'))
    if cl is not None and cand.get('cell'): cl = cand['cell'](cl, kind)
    kw = fekw(wing_cell=cl, **cand.get('over', {}))
    if hub != 'rigid': kw['hub_se'] = T.HUB[hub]
    pk = T.PACKS[pad]
    if pk is not None:
        pk = dict(pk, **cand.get('pack', {})); kw['pack_cfg'] = pk
    F, info = fe_a.build(kind, **kw)
    if cand.get('mod'): cand['mod'](F, kind)
    return F, F.solve(nmodes)


def modes_table(F, res, fmax=130.0):
    """list of (f, cx, cy, parity-ish, top groups) for modes 5-fmax Hz"""
    out = []
    for f, e, v, cx, cy in res:
        if f > fmax: break
        top = sorted(e.items(), key=lambda kv: -kv[1])[:3]
        idx = F._idx
        out.append((f, cx, cy, ', '.join('%s %.0f%%' % (g, 100*x) for g, x in top)))
    return out


# ---------------- gain margin, pitch axis (D-191 method of t089_gm.py, unchanged: GM >= 2.0, zeta 0.3 / 1 %, thrust 0.77 / 1.0 / 1.25, modes x 1.0 / 0.8 / 1.2, CAD inertia basis)
import t089_gm as GM
import fu_cage as FC
FC.configure('t089')
_cad = json.load(open(os.path.join(QPA, 'sitl', 'cad_mass.json')))['I_cad_axes_kgm2']
I_T0 = _cad['Iyy'] * GM.M_PRED / GM.M_BASIC          # pitch inertia target of the drawn airframe (t089_gm.py 'CAD')
NODES = {'spar centre': 's+0.000', 'cage hub': 'hub'}


def pit_case(F, kind, node='s+0.000'):
    r = FC.RATE['pit']; arm = r['arm']
    sg = lambda sy, sz, a=arm: sz / (4 * a)
    f, g = FC.modal(F, node, r['dof'], sg)
    rig = [(0.0, sum(gg for ff, gg in zip(f, g) if ff < 1.0))]
    flex = [(ff, gg) for ff, gg in zip(f, g) if 1.0 <= ff < 250 and abs(gg) > 1e-9]
    return dict(modes=rig + flex, inv_I=rig[0][1], flex=flex)


def limiting(c, sc, z, ts, ks):
    modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c['modes']]
    Lp = FC.loop(modes, 'pit', z, tfull_scale=ts, kscale=ks, **FC.A_PARAM_D191['pit']); A, B_, C, D = Lp; BC = B_ @ C
    for k in np.geomspace(1.0, 100, 300):
        ev = np.linalg.eigvals(A - k * BC)
        if ev.real.max() >= -1e-9:
            e = ev[np.argmax(ev.real)]; return float(k), float(abs(e.imag) / 2 / math.pi)
    return float('inf'), None


def gm_pitch(c, I_t, gscale=1.0, scales=(1.0, 0.8, 1.2)):
    """returns {scale: (gm, (zeta, tscale))}, loop gain rescaled to the target inertia I_t; gscale multiplies the pitch P and D gains (illustrative only)"""
    ks = (1.0 / c['inv_I']) / I_t * gscale
    out = {}
    for sc in scales:
        modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c['modes']]
        gm = 99.0; arg = None
        for z in GM.ZETAS:
            for ts in GM.TSCALES:
                Lp = FC.loop(modes, 'pit', z, tfull_scale=ts, kscale=ks, **FC.A_PARAM_D191['pit'])
                g = 1.0 if FC.maxre(Lp) >= -1e-6 else GM.gm_scan(Lp)
                if g < gm: gm, arg = g, (z, ts)
        out[sc] = (gm, arg)
    return out


# ---------------- forced response (t089_fvib.py Modal / summarize unchanged; FC node selectable)
import t089_fvib as FV


def forced(F, res, node='s+0.000', zetas=(0.01, 0.005)):
    M = FV.Modal(F, res)
    if node != 's+0.000':
        idx = F._idx; V = np.array([r[2] for r in res]); M.fc = np.array([[abs(v[6 * idx[node] + q]) for q in range(3)] for v in V])
    out = {}
    for z in zetas:
        s = FV.summarize(M, z); out[z] = dict(sweep=s['worst'], rpm=s['rpm'], window=s['hover_window'], gov_f=s['gov_f'], gov_peak=s['gov_peak'], motor=s['motor_worst'])
    return out


def gm_axes(F, kind, dI=None):
    """pit / rll / yaw GM at the spar centre (D-191 method, CAD inertia basis of t089_gm.py, target inertia + the model's own change dI = {ax: I_fe - I_fe_base}); returns {ax: {scale: gm}}"""
    out = {}
    for c in FC.cases_frame(F, kind):
        if c['node'] != 'spar centre': continue
        ax = c['ax']; I_fe = 1.0 / c['inv_I']; I_t = _cad[GM.AX_IAXIS[ax]] * GM.M_PRED / GM.M_BASIC + ((dI or {}).get(ax, 0.0))
        ks = I_fe / I_t; r = {}
        for sc in GM.SCALES:
            modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c['modes']]; gm = 99.0
            for z in GM.ZETAS:
                for ts in GM.TSCALES:
                    Lp = FC.loop(modes, ax, z, tfull_scale=ts, kscale=ks, **FC.A_PARAM_D191[ax])
                    g = 1.0 if FC.maxre(Lp) >= -1e-6 else GM.gm_scan(Lp)
                    gm = min(gm, g)
            r[sc] = gm
        out[ax] = r; out[ax + '_I'] = I_fe
    return out


def axis_case(F, node, ax):
    r = FC.RATE[ax]
    if ax == 'pit': sg = lambda sy, sz, a=r['arm']: sz / (4 * a)
    elif ax == 'rll': sg = lambda sy, sz, a=r['arm']: -sy / (4 * a)
    else: sg = lambda sy, sz, a=r['arm']: sy * sz * math.cos(math.radians(FC.CANT_DEG)) / (4 * a)
    f, g = FC.modal(F, node, r['dof'], sg)
    rig = [(0.0, sum(gg for ff, gg in zip(f, g) if ff < 1.0))]
    flex = [(ff, gg) for ff, gg in zip(f, g) if 1.0 <= ff < 250 and abs(gg) > 1e-9]
    return dict(modes=rig + flex, inv_I=rig[0][1], flex=flex)


def gm_axes_node(F, kind, node):
    """as gm_axes but the IMU at `node`; target inertia = the T-089 CAD basis (candidates that change mass are not used with this function)"""
    out = {}
    for ax in ('pit', 'rll', 'yaw'):
        c = axis_case(F, node, ax); I_fe = 1.0 / c['inv_I']; I_t = _cad[GM.AX_IAXIS[ax]] * GM.M_PRED / GM.M_BASIC; ks = I_fe / I_t; r = {}
        for sc in GM.SCALES:
            modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c['modes']]; gm = 99.0
            for z in GM.ZETAS:
                for ts in GM.TSCALES:
                    Lp = FC.loop(modes, ax, z, tfull_scale=ts, kscale=ks, **FC.A_PARAM_D191[ax])
                    g = 1.0 if FC.maxre(Lp) >= -1e-6 else GM.gm_scan(Lp)
                    gm = min(gm, g)
            r[sc] = gm
        out[ax] = r
    return out
