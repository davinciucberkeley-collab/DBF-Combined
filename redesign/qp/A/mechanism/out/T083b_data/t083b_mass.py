"""T-083b SIZING TOOL (no bond gap; the DRAWN mass is wing.fin_block_volume_m3() with FB_GAP 0.1 mm: 12.04 g): drawn volume / mass / CG of the 6061 root fitting FIN-003 (R side) by a voxel sum (pitch 0.2 mm), same solid definition as wing.py fin_block_volume().
Category: geometry arithmetic. 6061 density 2.70 g/cm3 (repo RHO_AL, wing.py; CGE-001 / CGE-006 basis).   python -I t083b_mass.py TR HR TP TE RD [mm]"""
import sys, math
import numpy as np
XT, YF, FR = 0.294, 0.38, 0.008           # common.py XFIN_T, YFIN, FIN_OD / 2
RIB_Y, RX1, BX0, RIB_RI, RIB_RO = 0.383, 0.286, 0.255, 0.0115, 0.0125   # wing.py RIB_Y, RIB_X1, BLK_X0, rib 25x23


def solid(X, Y, Z, TR, HR, TP, TE, RD):
    d2f = (X - XT) ** 2 + (Y - YF) ** 2; r2r = (Y - RIB_Y) ** 2 + Z ** 2
    ring = (d2f <= (FR + TR) ** 2) & (np.abs(Z) <= HR / 2)
    plug = (X >= BX0) & (X <= RX1) & (r2r <= RIB_RI ** 2) & (r2r >= (RIB_RI - TP) ** 2)
    plate = (X >= RX1) & (X <= RX1 + TE) & (r2r <= RD ** 2)
    m = (ring | plug | plate) & (d2f >= FR ** 2)
    m &= ~((X < RX1) & (r2r > RIB_RI ** 2 - 1e-12) & (r2r <= (RIB_RO + 0.00005) ** 2))      # rib-wall annulus clear
    m &= ~((X < RX1) & (r2r < (RIB_RI - TP) ** 2))                                            # plug bore (the ring bulge inside the plug bore removed)
    return m


def mass(TR, HR, TP, TE, RD, h=0.2e-3):
    xs = np.arange(BX0 - 0.001, XT + FR + TR + 0.001, h) + h / 2; ys = np.arange(RIB_Y - 0.016, RIB_Y + 0.016, h) + h / 2; zs = np.arange(-HR / 2 - 0.001, HR / 2 + 0.001, h) + h / 2
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij'); m = solid(X, Y, Z, TR, HR, TP, TE, RD)
    v = m.sum() * h ** 3; g = v * 1e6 * 2.70
    return g, (X[m].mean(), Y[m].mean(), Z[m].mean()), (X[m].min(), X[m].max(), Y[m].min(), Y[m].max(), Z[m].min(), Z[m].max())


if __name__ == '__main__':
    a = [float(v) * 1e-3 for v in sys.argv[1:6]]
    g, cg, bb = mass(*a)
    print('mass %.2f g, CG (%.1f, %.1f, %.1f) mm, bbox x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f mm' % ((g,) + tuple(c * 1e3 for c in cg) + tuple(b * 1e3 for b in bb)))
