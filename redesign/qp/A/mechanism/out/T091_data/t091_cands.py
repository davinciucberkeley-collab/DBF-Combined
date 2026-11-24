"""T-091 candidates (name -> dict).  Every entry is a model edit only (nothing applied to the CAD / BOM).  Picklable: workers look candidates up by name."""
import math, functools
import numpy as np
import t091_lib as L
import fe_a
CP = L.CP
RHO = fe_a.RHO_CF
XS = fe_a.X_SPAR; YM = fe_a.Y_M; ZM = fe_a.Z_M


def cell_zones(zones, extra=None):
    """zones = ((ymax, nply), ...) -> wing cell zones (same method as t084_cell_props.cell_for, T-084 section model); lower-bound cell keeps its own factors"""
    def f(cl, kind, lower=False):
        zs = []
        for ymax, n in zones:
            kw = dict(CP.LOWER) if lower else {}
            if n == 0: kw['strip'] = False
            p = CP.props(n, Es=CP.E_CF[kind], Gs=CP.G_CF[kind], **kw); zs.append((ymax, p['EA'], p['EI_flap'], p['EI_in'], p['GJ']))
        return dict(zones=zs, scale=1.0)
    return f


def add_spar_section(F, ymax, EA=0.0, EIy=0.0, EIz=0.0, GJ=0.0, dm=0.0):
    """additive section (sleeve / plate / extra plies) on spar-group elements with mid |y| <= ymax: stiffness added, mass dm (kg per metre)"""
    new = []
    for el in F.el:
        a, b, EA_, EIy_, EIz_, GJ_, rA, vref, grp = el
        if grp == 'spar' and abs(0.5*(F.n[a][1]+F.n[b][1])) <= ymax: el = (a, b, EA_+EA, EIy_+EIy, EIz_+EIz, GJ_+GJ, rA+dm, vref, grp)
        new.append(el)
    F.el = new


def add_tube_beam(F, a, b, od, idm, kind, grp='bridge', nseg=3, vref=(0, 0, 1)):
    A, I = L.tube(od, idm); E_ = fe_a.E_CF[kind]; G_ = fe_a.G_CF[kind]
    F.beam(a, b, E_*A, E_*I, E_*I, G_*2*I, RHO*A, vref, grp, nseg=nseg)


CANDS = {}
def reg(name, **kw): CANDS[name] = kw


reg('B0 as drawn')
# ---------------- stage 0: generic multipliers (which load path governs); not physical sections
for k in (2.0, 4.0):
    reg('G1 bridge (single tube) EI/GJ/EA x%g' % k, mod=lambda F, kind, k=k: L.edit_bridge(F, 'main', fA=k, fIy=k, fIz=k, fJ=k))
    reg('G2 V struts EA/EI/GJ x%g' % k, mod=lambda F, kind, k=k: L.edit_bridge(F, 'strut', fA=k, fIy=k, fIz=k, fJ=k))
    reg('G3 centre spar zone |y|<=0.075 GJ x%g' % k, mod=lambda F, kind, k=k: L.spar_zone(F, 0.0751, fJ=k))
    reg('G3b spar zone |y|<=0.40 GJ x%g' % k, mod=lambda F, kind, k=k: L.spar_zone(F, 0.40, fJ=k))
    reg('G4 centre spar zone |y|<=0.15 EIy (flap) x%g' % k, mod=lambda F, kind, k=k: L.spar_zone(F, 0.15, fIy=k))
    reg('G5 arms EI/EA/GJ x%g' % k, mod=lambda F, kind, k=k: L.edit(F, lambda a, b, g: g == 'arm', fA=k, fIy=k, fIz=k, fJ=k))
    reg('G6 hub joint stiffness x%g' % k, mod=lambda F, kind, k=k: setattr(F, 'se', [(n_, K_*k, g_) for (n_, K_, g_) in F.se]))


# ================= stage 1: physical sections (computed from tube OD x ID, corner E / G of fe_a.py)
def sleeve(ymax, od, idm, tag=''):
    def mod(F, kind):
        A, I = L.tube(od, idm); E_ = fe_a.E_CF[kind]; G_ = fe_a.G_CF[kind]
        add_spar_section(F, ymax, EA=E_*A, EIy=E_*I, EIz=E_*I, GJ=G_*2*I, dm=RHO*A)
    return mod


def strut_tube(od, idm):
    """replace the V struts' section (8x6 in the drawn model) by od x idm"""
    def mod(F, kind):
        A, I = L.tube(od, idm); E_ = fe_a.E_CF[kind]; G_ = fe_a.G_CF[kind]
        new = []
        for el in F.el:
            a, b, EA, EIy, EIz, GJ, rA, vref, grp = el
            if grp == 'bridge' and 's+0.000' not in (a + '|' + b): el = (a, b, E_*A, E_*I, E_*I, G_*2*I, RHO*A, vref, grp)
            new.append(el)
        F.el = new
    return mod


def bridge_tube(od, idm):
    def mod(F, kind):
        A, I = L.tube(od, idm); E_ = fe_a.E_CF[kind]; G_ = fe_a.G_CF[kind]
        new = []
        for el in F.el:
            a, b, EA, EIy, EIz, GJ, rA, vref, grp = el
            if grp == 'bridge' and 's+0.000' in (a + '|' + b): el = (a, b, E_*A, E_*I, E_*I, G_*2*I, RHO*A, vref, grp)
            new.append(el)
        F.el = new
    return mod


def chain(*fs):
    def mod(F, kind):
        for f in fs: f(F, kind)
    return mod


for ym in (0.0751, 0.10, 0.15, 0.20, 0.30):
    reg('S1 sleeve CF 14x12 on the spar |y|<=%.3f' % ym, mod=sleeve(ym, 0.014, 0.012))
reg('S1x sleeve CF 14x12, |y|<=0.15, GJ only (EA, EI not added)', mod=lambda F, kind: add_spar_section(F, 0.15, GJ=fe_a.G_CF[kind]*2*L.tube(0.014, 0.012)[1], dm=RHO*L.tube(0.014, 0.012)[0]))
reg('S1y sleeve CF 14x12, |y|<=0.15, EIy only (flap bending)', mod=lambda F, kind: add_spar_section(F, 0.15, EIy=fe_a.E_CF[kind]*L.tube(0.014, 0.012)[1], dm=RHO*L.tube(0.014, 0.012)[0]))
reg('S1z sleeve CF 14x12, |y|<=0.15, EIz only (chord bending)', mod=lambda F, kind: add_spar_section(F, 0.15, EIz=fe_a.E_CF[kind]*L.tube(0.014, 0.012)[1], dm=RHO*L.tube(0.014, 0.012)[0]))
# softening / other section levers
for f in (0.5, 0.25):
    reg('G7 bridge z-bending x%g (T-085 C1)' % f, mod=lambda F, kind, f=f: L.edit_bridge(F, 'main', fIy=f))
    reg('G8 hub joint x%g' % f, mod=lambda F, kind, f=f: setattr(F, 'se', [(n_, K_*f, g_) for (n_, K_, g_) in F.se]))
reg('A1 arms 10x8 (T-085 C5)', over=dict(arm_tube=(0.010, 0.008)))
reg('A2 arms 14x12', over=dict(arm_tube=(0.014, 0.012)))
reg('K1 bridge 25x23 (R15 offcut)', mod=bridge_tube(0.025, 0.023))
reg('K2 bridge 20x18', mod=bridge_tube(0.020, 0.018))
reg('K3 struts 12x10 (R08 offcut)', mod=strut_tube(0.012, 0.010))
reg('K4 struts 10x8', mod=strut_tube(0.010, 0.008))
reg('K5 struts 8x6 -> 6x4.5 (softer, for contrast)', mod=strut_tube(0.006, 0.0045))


def extra_struts(y_attach, od=0.008, idm=0.006, diag=False):
    def mod(F, kind):
        for sy in (1, -1):
            if diag:   # four diagonals motor -> spar at the motor station y
                for sz in (1, -1): add_tube_beam(F, 'm%+d%+d' % (sy, sz), 's%+.3f' % (sy*YM), od, idm, kind)
            else: add_tube_beam(F, 'hub', 's%+.3f' % (sy*y_attach), od, idm, kind)
    return mod


reg('T1 third strut pair hub -> spar |y|=0.150 (8x6)', mod=extra_struts(0.150))
reg('T2 third strut pair hub -> spar |y|=0.075 (8x6)', mod=extra_struts(0.075))
reg('T3 four diagonals motor -> spar at |y|=0.228 (8x6)', mod=extra_struts(0.228, diag=True))
reg('T4 four diagonals motor -> spar (12x10)', mod=extra_struts(0.228, 0.012, 0.010, diag=True))


reg('F1 sleeve 14x12, spar |y|<=0.075 + struts 12x10', mod=chain(sleeve(0.0751, 0.014, 0.012), strut_tube(0.012, 0.010)))
reg('F2 sleeve 14x12 |y|<=0.075 + arms 10x8', mod=sleeve(0.0751, 0.014, 0.012), over=dict(arm_tube=(0.010, 0.008)))
