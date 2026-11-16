"""fea_arm_figs.py - figures for FEA-ARM.md from fea_arm.py outputs (out_fea/field_L0_*.npz, result_L1_asdrawn.json, result_L0_spoke.json).

    python redesign/qp/A/structures/fea_arm_figs.py      (not -I: matplotlib needs the user site packages)

Fig 1: hub stress map, flight case F1 (limit load), as drawn vs the hollow-spoke candidate: element-mean max principal stress
of the printed PETG hub, viewed along the web's thin direction (z), one blue ramp on a log scale; the allowable at the
ultimate factor (20 MPa / 2.156 = 9.3 MPa at limit) is marked on the scale.
Fig 2: factor of safety (allowable / limit stress) per item for F1, as drawn, against the required factor of each material.
Palette: dataviz skill reference palette (blue ramp 100-700, surface #fcfcfb, ink #0b0b0b / #52514e, critical #d03b3b).
"""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out_fea')
FIG = os.path.join(HERE, 'fig')
SURF, INK, INK2, GRID, CRIT = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df', '#d03b3b'
BLUE = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
CMAP = LinearSegmentedColormap.from_list('blue', BLUE)
KF, KP = 1.725, 2.15625
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'text.color': INK, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.edgecolor': GRID, 'figure.facecolor': SURF, 'axes.facecolor': SURF})


def fig_map():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, constrained_layout=True)
    norm = LogNorm(1, 1000)
    for ax, (v, title) in zip(axs, (('asdrawn', 'As drawn: 0.8 mm web'), ('spoke', 'Candidate: hollow spoke 13.6 x 10.4'))):
        d = np.load(os.path.join(OUT, 'field_L0_%s.npz' % v))
        c, val, M = d['c'], d['val'], d['M']
        s = (M == 0) & (c[:, 1] < 60) & (np.abs(c[:, 0]) < 14)
        o = np.argsort(val[s])
        sc = ax.scatter(c[s, 1][o], c[s, 0][o], c=np.clip(val[s][o], 1, 1000), cmap=CMAP, norm=norm, s=3, linewidths=0)
        mid = s & (c[:, 1] > 12) & (c[:, 1] < 24)
        ax.set_title('%s\nmid-span peak %.0f MPa at limit load' % (title, val[mid].max()), loc='left', fontsize=10.5, color=INK)
        ax.set_xlabel('distance along the arm from the hub axis (mm)')
        ax.set_aspect('equal'); ax.set_xlim(0, 60); ax.set_ylim(-14, 14)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.text(3, -13, 'sleeve', color=INK2, fontsize=8.5); ax.text(14, -13, 'web / spoke', color=INK2, fontsize=8.5); ax.text(36, -13, 'arm socket', color=INK2, fontsize=8.5)
    axs[0].set_ylabel('x along the hub axis (mm)')
    cb = fig.colorbar(sc, ax=axs, shrink=0.85, pad=0.01)
    cb.set_label('max principal stress, PETG, limit load (MPa, log)')
    cb.ax.axhline(20 / KP, color=INK, lw=1.5)
    cb.ax.text(-0.15, 20 / KP, 'allowed 9.3 ', va='center', ha='right', fontsize=8, color=INK, transform=cb.ax.get_yaxis_transform())
    cb.outline.set_visible(False)
    fig.suptitle('Hub stress, flight case F1 (thrust at the spin cap + motor torque + pitch-over gyro + 1P)', x=0.01, ha='left', fontsize=11.5, color=INK)
    p = os.path.join(FIG, 'fea-arm-hub-map.png'); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def fig_fos():
    r = json.load(open(os.path.join(OUT, 'result_L1_asdrawn.json')))
    F1 = r['cases'][0]['regions']; b = r['bonds'][r['cases'][0]['case']]
    rows = [  # label, limit stress, allowable, required factor
        ('Arm tube, free span (bending)', F1['tube_mid']['axial'], 350, KF),
        ('Arm tube in the motor cup', F1['tube_tip']['axial'], 350, KF),
        ('Motor cup (peak at a screw hole)', F1['cup']['p1'], 20, KP),
        ('Cup bond (epoxy shear)', b['cup']['shear'], 2.0, KP),
        ('Arm socket mouth (2.0 mm wall)', F1['mouth']['p1'], 20, KP),
        ('Arm tube at the socket floor (shear)', F1['tube_root']['shear'], 30, KF),
        ('Socket bond (epoxy shear)', b['socket']['shear'], 2.0, KP),
        ('Hub radial web, mid-span', float(np.load(os.path.join(OUT, 'field_L0_asdrawn.npz'))['val'][
            lambda_mid()].max()), 20, KP),
    ]
    fos = [a / s for _, s, a, _ in rows]
    fig, ax = plt.subplots(figsize=(9.5, 4.4), constrained_layout=True)
    y = np.arange(len(rows))[::-1]
    for yi, (lab, s, a, req), f in zip(y, rows, fos):
        ok = f >= req
        ax.barh(yi, f, height=0.55, color=BLUE[3] if ok else CRIT, left=0)
        ax.plot([req, req], [yi - 0.36, yi + 0.36], color=INK, lw=1.6)
        ax.text(f * 1.08, yi, '%s  %.2f  (needs %.2f)' % ('PASS' if ok else 'FAIL', f, req), va='center', fontsize=9, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([r_[0] for r_ in rows])
    ax.set_xscale('log'); ax.set_xlim(0.03, 200)
    ax.set_xlabel('factor of safety = allowable / limit stress (log scale)\nblack tick = required factor: 1.725 for CFRP, 2.16 for printed and bonded parts')
    ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)
    ax.set_title('Concept A arm as drawn, flight case F1: factor of safety by item (FEA, fine mesh)', loc='left', fontsize=11.5, color=INK)
    p = os.path.join(FIG, 'fea-arm-fos.png'); fig.savefig(p, dpi=150); plt.close(fig)
    return p, list(zip([r_[0] for r_ in rows], [r_[1] for r_ in rows], [r_[2] for r_ in rows], fos, [r_[3] for r_ in rows]))


def lambda_mid():
    d = np.load(os.path.join(OUT, 'field_L0_asdrawn.npz'))
    c, M = d['c'], d['M']
    return (M == 0) & (c[:, 1] > 12) & (c[:, 1] < 24)


if __name__ == '__main__':
    os.makedirs(FIG, exist_ok=True)
    print(fig_map())
    p, rows = fig_fos()
    print(p)
    for r in rows:
        print('%-40s %8.2f MPa  allow %5.1f  FOS %6.2f  needs %.3f' % r)
