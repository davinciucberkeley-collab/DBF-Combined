"""T-084 (hand calculation / geometry arithmetic): wing-cell beam properties for the beam FE, from the SAME section model the landing rows use
(structures/landing_path_a.py: S5010 at chord 0.245, foam ahead of the hinge XH, spar 12x10 at x 60, +-45 glass skin plies (ACP PDS Dec 2014 x Vf 0.70, read 2026-11-19),
cove CF strip 3 mm2 E 120 GPa EST; foam E 30 / G 8 MPa EST).  Ply zones from cad/amodel/wing.py: ply 1 |y| <= SKIN_Y 0.40, plies 2-3 over SKN2_Y 0.052..0.400.
Outputs per zone: EA, EI_in (about z, chordwise bending: the FE spar beam's EIz), EI_flap (about x: EIy), GJ (spar + foam Prandtl + Bredt skin), all about the composite centroid; spar-alone values for comparison.
python -I t084_cell_props.py  -> cell_props.json"""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(QPA, 'structures')); sys.dont_write_bytecode = True
os.environ.setdefault('LAND_MASS_MODEL', 'cad')
import numpy as np
import landing_path_a as P
C, W = P.C, P.W
def foam_flap_I(h=0.25e-3):
    Pl = P._poly(); xs = np.arange(0, C.C+h, h); zs = np.arange(Pl[:, 1].min()-h, Pl[:, 1].max()+2*h, h)
    X, Z = np.meshgrid(xs, zs, indexing='ij'); ins = P._inside(Pl, X, Z) & (X <= P.XH) & ~((X-C.SPAR_X)**2+Z**2 <= P.R_BORE**2)
    A = ins.sum()*h*h; zc = Z[ins].sum()*h*h/A; return float(A), float(zc), float(((Z[ins]-zc)**2).sum()*h*h)
def skin_flap_int():
    """perimeter integrals of the cell skin (x <= XH incl. the cove face): T0 = int ds, Tz = int z ds, Tzz = int z2 ds"""
    Pl = P._poly(); T0 = Tz = Tzz = 0.0; zs = []
    for i in range(len(Pl)):
        a, b = Pl[i], Pl[(i+1) % len(Pl)]; n = max(int(np.hypot(*(b-a))/0.05e-3), 1)
        u = (np.arange(n)+0.5)/n; xm = a[0]+(b[0]-a[0])*u; zm = a[1]+(b[1]-a[1])*u; ds = np.hypot(*(b-a))/n
        mk = xm <= P.XH; T0 += ds*mk.sum(); Tz += ds*zm[mk].sum(); Tzz += ds*(zm[mk]**2).sum()
        if (a[0]-P.XH)*(b[0]-P.XH) < 0: zs.append(a[1]+(b[1]-a[1])*(P.XH-a[0])/(b[0]-a[0]))
    z0, z1 = min(zs), max(zs); hc = z1-z0; T0 += hc; Tz += hc*(z0+z1)/2; Tzz += (z1**3-z0**3)/3
    return T0, Tz, Tzz
def props(nply, EF=P.E_F, GF=P.G_F, stiff=1.0, strip=True, Es=P.E_S, Gs=P.G_S):
    S, cg = P.sec_cell(); fo = S['foam']; A_s, I_s = P.A_S, P.I_S
    Af, zcf, Ixf = foam_flap_I(); T0, Tz, Tzz = skin_flap_int()
    if nply: lam = P.skin_laminate(n=nply, stiff=stiff); t, Ex, G = lam['t'], lam['Ex'], lam['G']
    else: t, Ex, G = 0.0, 0.0, 0.0
    Acap = 3e-6 if strip else 0.0; Ecap = 120e9; xk = cg['S1']/cg['S0']
    EAs, EAf, EAk, EAc = Es*A_s, EF*fo['A'], Ex*t*cg['S0'], Ecap*Acap
    EA = EAs+EAf+EAk+EAc; xn = (EAs*P.SX+EAf*fo['xc']+EAk*xk+EAc*P.XH)/EA
    EIin = Es*I_s+EAs*(P.SX-xn)**2+EF*fo['Iz']+EAf*(fo['xc']-xn)**2+Ex*t*(cg['S2']-2*xn*cg['S1']+xn*xn*cg['S0'])+EAc*(P.XH-xn)**2
    # flap: about the composite z-centroid (strip at the cove mid-height, EST)
    zn = (EAs*0.0+EAf*zcf+Ex*t*Tz)/(EAs+EAf+Ex*t*T0+1e-30)
    EIfl = Es*I_s+EAs*zn**2+EF*(Ixf+Af*(zcf-zn)**2)+Ex*t*(Tzz-2*zn*Tz+zn*zn*T0)
    J_s = 2*I_s; GJ = Gs*J_s+GF*S['bored']['J']+(4*fo['enclosed']**2*G*t/cg['S0'] if nply else 0.0)
    return dict(nply=nply, EA=EA, EI_in=EIin, EI_flap=EIfl, GJ=GJ, xn=xn, zn=zn, t=t, spar_EI=Es*I_s, spar_GJ=Gs*J_s, foamE=EF, stiff=stiff, strip=strip)
E_CF = {'kd': 61e9, 'nom': 70e9, 'hi': 90e9}; G_CF = {'kd': 3e9, 'nom': 3e9, 'hi': 4.5e9}     # fe_a.E_CF / G_CF corners (CF only; foam and glass stay at their own values)
LOWER = dict(EF=P.E_F*0.5, GF=P.G_F*0.5, stiff=0.7, strip=False)                              # lower bound: foam E, G x0.5 (landing_path_a sensitivity), skin x0.7 (landing_path_a V3), no cove strip


def cell_for(kind, lower=False):
    """fe_a.build(wing_cell=...) zones for one corner: (|y| max, EA, EI_flap, EI_in, GJ); 1 ply to |y| 0.075 (conservative for 0.052), 3 plies to 0.40, spar + foam to 0.45"""
    zs = []
    for ymax, n in ((0.0751, 1), (0.40, 3), (0.46, 0)):
        kw = dict(LOWER) if lower else {}
        if n == 0: kw['strip'] = False
        p = props(n, Es=E_CF[kind], Gs=G_CF[kind], **kw); zs.append((ymax, p['EA'], p['EI_flap'], p['EI_in'], p['GJ']))
    return dict(zones=zs, scale=1.0)


if __name__ == '__main__':
    out = {}
    for tag, kw in (('nominal', {}), ('lower (foam E,G x0.5, skin x0.7, no strip)', dict(EF=P.E_F*0.5, GF=P.G_F*0.5, stiff=0.7, strip=False))):
        out[tag] = {}
        for zone, n in (('|y|<0.052 (1 ply)', 1), ('0.052-0.40 (3 plies)', 3), ('0.40-0.45 (no skin, foam + spar, strip ends at 0.40)', 0)):
            kw2 = dict(kw); 
            if n == 0: kw2['strip'] = False
            p = props(n, **kw2); out[tag][zone] = p
            print(f"{tag:45s} {zone:52s} EI_in {p['EI_in']:8.1f}  EI_flap {p['EI_flap']:6.2f}  GJ {p['GJ']:7.2f}  EA {p['EA']/1e6:6.2f} MN  (spar alone EI {p['spar_EI']:.1f}, GJ {p['spar_GJ']:.2f}); xn {p['xn']*1e3:.1f} mm")
    json.dump(out, open(os.path.join(HERE, 'cell_props.json'), 'w'), indent=1)
