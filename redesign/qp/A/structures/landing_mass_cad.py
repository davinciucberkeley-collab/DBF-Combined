"""T-076d step 1 (D-222, LR-3): CAD-derived point-mass model for the landing sims of concept A.
CATEGORY: rigid-body dynamics input (mass / inertia model).  Fidelity correction, NOT demand relief.
    python -I landing_mass_cad.py [--build] [--mass 1.64]      (--build regenerates the part table from the CAD, about 10 s; the table is committed)
Use in the landing sims:  LAND_MASS_MODEL=cad python -I ...    (landing_a.mass_props then calls mass_props() here; default = the old ITEMS roll-up, unchanged)

What it is.  Every CAD part (redesign/qp/A/cad/a_model.PARTS, 117 parts, declared masses, basic 1,273.24 g) at its volume centroid, exactly as sitl/cad_mass.py does,
plus the OWN inertia of the long parts as spanwise / chordwise lumps (wing core plate, spar, fin tubes, fin fairings, arm tubes, bridge, elevons) with the same formulas as
cad_mass.py (so at the basic mass the three inertias reproduce sitl/cad_mass.json to rounding: the 5 % match test).  Each lumped body is split into n equal masses whose
variance is made exactly L^2/12 (spacing scaled by sqrt(n^2/(n^2-1))), so the discretisation does not change the inertia.
Growth to the landing mass (default 1.64 kg = LAND_MASS_KG; EST).  Rates: F 0, C (CALC) 10 %, E (EST) 20 %; the growth (target - basic) is spread in proportion to mass x rate (LAND_MASS_PLACEMENT=E puts it all on class E, the sensitivity bracket).
  class F  (no growth): motors, props, prop adapters, spinner nuts, pack, ESC, FC and the other bought boards, servos, elevon balance lead (physical items whose mass is the vendor's / the flutter design's);
  class C  (growth at the CALC 10 % rate): bought CF stock (arm tubes, doublers, pins, spar, fin and rib tubes, bridge, V struts): CALC mass of a stock tube;
  class E  (growth at the EST 20 % rate): everything else (foam, printed parts, hardware, harness, lumps).  The old ITEMS model scaled EVERY lump by 1.290 (motors 113.9 g, pack 348 g): that is the error this replaces.
This is a bracket, not the T-067 placement (the T-067 / FE model puts the residual as a line mass along the spar): its CG and inertias are reported against the CAD and the FE.
Group tags (idx) follow landing_a.ITEMS so the arm-group / hub-group wrench split of landing_centre_a (2 motors, 3 arms, 4 hub, 6 pack) keeps its meaning:
  0 wing, 1 fins + feet, 2 motors (+ cups, props, adapters, nuts), 3 arm tubes (+ doublers, pins), 4 hub (+ conduits, raceways), 5 bridge, struts, saddle, 6 pack (+ strap, pad, tray), 7 avionics + ESC + harness, 8 elevons + servos + linkage, 9 hardware.
Frames: body x aft of the wing LE, y right, z cruise-up (m, kg)."""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.abspath(os.path.join(HERE, '..', 'mechanism', 'out', 'T076d_data', 'cad_part_table.json'))
CAD_MASS_JSON = os.path.abspath(os.path.join(HERE, '..', 'sitl', 'cad_mass.json'))
N_SPAN, N_CHORD, N_ROD = 15, 5, 9          # lump counts per direction (plates: N_SPAN x N_CHORD; rods N_ROD)

F_PREFIX = ('PRP-001', 'PRP-002', 'PRP-004', 'PRP-005', 'PRP-003', 'PWR-001', 'AVN-002', 'AVN-003', 'AVN-004', 'AVN-005', 'AVN-006', 'MEC-001', 'WNG-007')
C_PREFIX = ('CGE-002', 'CGE-009', 'CGE-010', 'WNG-002', 'FIN-001', 'FIN-002', 'CGE-004', 'CGE-005')


def part_class(pid):
    return 'F' if pid.startswith(F_PREFIX) else ('C' if pid.startswith(C_PREFIX) else 'E')


def part_group(pid):
    p = pid
    if p.startswith(('PRP-001', 'PRP-002', 'PRP-004', 'PRP-005', 'CGE-003')): return 2
    if p.startswith(('CGE-002', 'CGE-009', 'CGE-010')): return 3
    if p.startswith(('CGE-001', 'HRN-003', 'HRN-004')): return 4
    if p.startswith(('CGE-004', 'CGE-005', 'CGE-006', 'CGE-007')): return 5
    if p.startswith(('PWR-', 'CGE-008')): return 6
    if p.startswith(('AVN-', 'PRP-003', 'HRN-001', 'HRN-002', 'HWC-001', 'HWC-003')): return 7
    if p.startswith(('WNG-006', 'WNG-007', 'MEC-', 'HWC-002')): return 8
    if p.startswith(('FIN-', 'GER-')): return 1
    if p.startswith('HRD-'): return 9
    return 0                                   # WNG-001..005, 008..010 (core, spar, plugs, caps, dampers)


def build_table(path=TABLE):
    """Read the CAD part table (same inputs as sitl/cad_mass.py) and write the committed JSON."""
    cad = os.path.abspath(os.path.join(HERE, '..', 'cad')); sys.path.insert(0, cad)
    import build_a as b, a_model as m
    cg = b.centroids(); parts = []
    for pid, p in m.PARTS.items():
        c = cg.get(pid) or p.get('cg'); own = None
        if pid == 'WNG-001': own = dict(type='plate', u=[0, 1, 0], lu=m.B, v=[1, 0, 0], lv=m.C)
        elif pid == 'WNG-002': own = dict(type='rod', u=[0, 1, 0], lu=0.9)
        elif pid.startswith('FIN-001-'): own = dict(type='rod', u=[0, 0, 1], lu=2 * m.FIN_H)
        elif pid.startswith('FIN-004-'): own = dict(type='plate', u=[0, 0, 1], lu=2 * m.FIN_H, v=[1, 0, 0], lv=m.XFIN_T - m.XH)
        elif pid.startswith('CGE-002-'):
            sgn = 1 if pid.endswith('A') else -1; uy, uz = m.YM / m.R_M, sgn * m.ZM / m.R_M
            own = dict(type='rod', u=[0, uy, uz], lu=2 * m.R_M)
        elif pid == 'CGE-004': own = dict(type='rod', u=[1, 0, 0], lu=m.BR_X1 - m.BR_X0)
        elif pid.startswith('WNG-006-'): own = dict(type='plate', u=[0, 1, 0], lu=m.ELEV_Y1 - m.ELEV_Y0, v=[1, 0, 0], lv=m.C - m.XH)
        parts.append(dict(id=pid, g=p['mass_g'], c=[float(x) for x in c], own=own, cls=part_class(pid), grp=part_group(pid)))
    json.dump(dict(source='redesign/qp/A/cad/a_model.PARTS + build_a.centroids() (as sitl/cad_mass.py); masses = CAD declared (basic, no growth)', parts=parts), open(path, 'w'), indent=0)
    return parts


def _spread(n, L):
    """n equal-mass offsets along a length L with variance exactly L^2/12."""
    s = L / n * math.sqrt(n * n / (n * n - 1.0)) if n > 1 else 0.0
    return (np.arange(n) - (n - 1) / 2.0) * s


def _lumps(part, k):
    """-> list of (kg, x, y, z) for one part with its mass multiplied by k."""
    m = part['g'] * k / 1000.0; c = np.array(part['c']); own = part['own']      # centroids stored in m (a_model / build_a.centroids)
    if own is None: return [(m, *c)]
    u = np.array(own['u'], float)
    if own['type'] == 'rod':
        return [(m / N_ROD, *(c + o * u)) for o in _spread(N_ROD, own['lu'])]
    v = np.array(own['v'], float); nu, nv = N_SPAN, N_CHORD
    ou, ov = _spread(nu, own['lu']), _spread(nv, own['lv'])
    return [(m / (nu * nv), *(c + a * u + b * v)) for a in ou for b in ov]


_P = None
def parts():
    global _P
    if _P is None:
        if not os.path.exists(TABLE): build_table()
        _P = json.load(open(TABLE))['parts']
    return _P


def basic_mass_kg(): return sum(p['g'] for p in parts()) / 1000.0


RATE = dict(F=0.0, C=0.10, E=0.20)         # MASS-GATE s3 maturity growth rates: bought vendor items 0 (kept at the vendor mass), CALC stock CF tube 10 %, EST 20 % (ASM-A3-MGA)
RATE_E_ONLY = dict(F=0.0, C=0.0, E=1.0)    # sensitivity placement: all growth on class E
PLACEMENT = os.environ.get('LAND_MASS_PLACEMENT', 'maturity')      # 'maturity' (default) | 'E' (class E only)


def _rates(): return RATE if PLACEMENT == 'maturity' else RATE_E_ONLY


def growth_lambda(M):
    """lambda such that sum_i m_i (1 + rate_i lambda) = M (kg)."""
    P = parts(); r = _rates(); mr = sum(p['g'] * r[p['cls']] for p in P) / 1000.0
    return (M - basic_mass_kg()) / mr


def growth_factor(M):
    """factor k_E on class-E parts (class C gets 1 + rate_C lambda)."""
    return 1.0 + _rates()['E'] * growth_lambda(M)


def points(M, growth=True):
    """-> list of (kg, x, y, z, idx, id) point masses at total mass M (kg).  growth False: CAD basic masses (M ignored)."""
    lam = growth_lambda(M) if growth else 0.0; r = _rates(); out = []
    for p in parts():
        for (m, x, y, z) in _lumps(p, 1.0 + r[p['cls']] * lam): out.append((m, x, y, z, p['grp'], p['id']))
    return out


def props_of(pts):
    m = sum(p[0] for p in pts); cg = np.array([sum(p[0] * p[i] for p in pts) / m for i in (1, 2, 3)]); I = np.zeros((3, 3))
    for q in pts:
        r = np.array(q[1:4]) - cg; I += q[0] * ((r @ r) * np.eye(3) - np.outer(r, r))
    return m, cg, I


def mass_props(scale_to, growth=True):
    """same return as landing_a.mass_props: (m, cg, I about the CG), diagonal-plus-products full tensor."""
    return props_of(points(scale_to, growth))


def cad_reference():
    """sitl/cad_mass.py evaluated NOW (its source run with the json.dump removed, so the committed cad_mass.json is not rewritten): the reference the lumps must match."""
    src = open(os.path.join(HERE, '..', 'sitl', 'cad_mass.py')).read()
    src = src.replace('json.dump(out, open(os.path.join(HERE, "cad_mass.json"), "w"), indent=1)', 'pass').replace('print(json.dumps(out, indent=1))', 'pass')
    g = dict(__name__='cad_mass_ref', __file__=os.path.join(HERE, '..', 'sitl', 'cad_mass.py')); import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, 'cad_mass.py', 'exec'), g)
    return g['out']


def report(M=1.64):
    cm = cad_reference(); Ic = cm['I_cad_axes_kgm2']; cad = np.array([Ic['Ixx'], Ic['Iyy'], Ic['Izz']]); cgc = np.array([cm['cg_x_m'], cm['cg_y_m'], cm['cg_z_m']])
    m0, cg0, I0 = mass_props(M, growth=False); m1, cg1, I1 = mass_props(M, growth=True)
    L = []
    L.append('basic (growth off): mass %.2f g (CAD %.2f g); CG (%.2f, %.2f, %.2f) mm (CAD %.2f, %.2f, %.2f); I diag %s g m2 (CAD %s): ratio %s' % (
        m0 * 1e3, cm['mass_basic_kg'] * 1e3, *(cg0 * 1e3), *(cgc * 1e3), np.round(np.diag(I0) * 1e3, 2).tolist(), np.round(cad * 1e3, 2).tolist(), np.round(np.diag(I0) / cad, 4).tolist()))
    L.append('at %.3f kg (placement %s, factor on class E %.4f, on class C %.4f): CG (%.2f, %.2f, %.2f) mm; I diag %s g m2; ratio to CAD basic %s' % (
        M, PLACEMENT, growth_factor(M), 1.0 + _rates()['C'] * growth_lambda(M), *(cg1 * 1e3), np.round(np.diag(I1) * 1e3, 2).tolist(), np.round(np.diag(I1) / cad, 3).tolist()))
    return dict(basic=dict(mass_kg=m0, cg_mm=(cg0 * 1e3).tolist(), I_gm2=(np.diag(I0) * 1e3).tolist(), ratio_to_cad=(np.diag(I0) / cad).tolist()),
                at_M=dict(M=M, k_E=growth_factor(M), cg_mm=(cg1 * 1e3).tolist(), I_gm2=(np.diag(I1) * 1e3).tolist(), ratio_to_cad=(np.diag(I1) / cad).tolist()), text=L)


if __name__ == '__main__':
    if '--build' in sys.argv: build_table(); print('table written', TABLE)
    M = float(sys.argv[sys.argv.index('--mass') + 1]) if '--mass' in sys.argv else float(os.environ.get('LAND_MASS_KG', 1.64))
    r = report(M); print('\n'.join(r['text']))
