"""fea_arm_figs.py - the arm and motor-cup FEA (fea_arm.py --variant current) for the Explorer and the report.

    python fea_arm_figs.py [--tag current_d208]      (after: python -I fea_arm.py --level 0 --variant current --tag _d208)

Writes
  fig/fea-arm-along.png         utilisation along the arm (worst over each 2 mm slice of tube, doubler and cup), F1 / F2 / S1 / S2
  ../../../site/data/fea-arm.js window.FEA_ARM: skins with per-vertex utilisation for the Explorer 3-D map (same format as
                                fea-hub.js; colour scale, cases and 'not judged' rule shared with fea_hub_figs.py)
Utilisation u = stress x required factor / allowable (fea_arm.save_fields_current). Not judged: the tube and doubler within
s < 36 mm (the 24 mm hub sleeve, where this model holds them rigidly, plus one tube diameter); the hub model (fea_hub.py) gives that zone.
"""
import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, FIG = os.path.join(HERE, 'out_fea'), os.path.join(HERE, 'fig')
SITE = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'site', 'data'))
import sys                                     # noqa: E402
sys.path.insert(0, HERE)
import fea_hub_figs as HF                     # noqa: E402  (colour ramp, case texts, encoders)
import fea_arm as FA                           # noqa: E402  (geometry constants)

MATS = ['carbon doubler 14 x 12 (inside the hub sleeve: not judged here)', 'arm tube 12 x 10 (CFRP)', 'motor cup (printed PETG)']
SERIES = {'F1': ('#2a78d6', '-'), 'F2': ('#eb6834', '--'), 'S1': ('#1baf7a', '-.'), 'S2': ('#eda100', ':')}   # dataviz categorical 1-4 (validated); dashes = secondary encoding
LABEL = {'F1': 'Full-power flight (F1)', 'F2': 'Motor runaway (F2)', 'S1': 'Prop strike, push on the shaft (S1)', 'S2': 'Prop strike, blade hit sideways (S2)'}


def along(d, case, step=2.0):
    """Max utilisation over every skin vertex in each 2 mm slice of y (all three materials)."""
    ys, us = [], []
    for m in range(3):
        V = d['V%d' % m]; u = d['U_%s_%d' % (case, m)].astype(float)
        if not np.isfinite(u).any():
            continue
        ys.append(V[:, 1]); us.append(u)
    y = np.concatenate(ys); u = np.concatenate(us)
    edges = np.arange(0, FA.R_M + 20 + step, step)
    k = np.digitize(y, edges) - 1
    out = np.full(len(edges) - 1, np.nan)
    for i in range(len(out)):
        s = (k == i) & np.isfinite(u)
        if s.any():
            out[i] = u[s].max()
    return (edges[:-1] + edges[1:]) / 2, out


def figure(d, res, tag):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=150)
    fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
    ax.axvspan(0, FA.CUR_NJ, color='#ecebe7', lw=0)
    ax.text(FA.CUR_NJ / 2, 1.33, 'hub sleeve + 12 mm:\njudged in the\nhub FEA', ha='center', va='top', fontsize=7.5, color='#52514e')
    ax.axhline(1.0, color='#0b0b0b', lw=0.9)
    ax.text(FA.R_M + 18, 1.0, '1.0 = at the allowable\nwith the required factor', fontsize=7.5, va='center', ha='left', color='#0b0b0b')
    peaks = {}
    for c, (col, ls) in SERIES.items():
        y, u = along(d, c)
        ax.plot(y, u, color=col, ls=ls, lw=2, solid_capstyle='round')
        i = int(np.nanargmax(u)); peaks[c] = (y[i], u[i])
    # direct labels at the right end of each line (text in ink, a short swatch carries the colour)
    ends = sorted(((np.nanmax(along(d, c)[1][-12:]) if np.any(np.isfinite(along(d, c)[1][-12:])) else 0.0, c) for c in SERIES))
    yl = 0.05
    for v, c in ends:
        yl = max(yl, v)
        col, ls = SERIES[c]
        ax.plot([FA.R_M + 20, FA.R_M + 32], [yl, yl], color=col, ls=ls, lw=2, clip_on=False)
        ax.text(FA.R_M + 35, yl, '%s, peak %.2f' % (LABEL[c], peaks[c][1]), fontsize=7.5, va='center', color='#0b0b0b', clip_on=False)
        yl += 0.11
    for x_, t in ((FA.CUR_SLV, 'sleeve exit'), (FA.R_M - 25, 'motor cup')):
        ax.axvline(x_, color='#9a9993', lw=0.6, ls=':')
        ax.text(x_, -0.07, t, rotation=0, ha='center', va='top', fontsize=7, color='#52514e', transform=ax.get_xaxis_transform())
    ax.set_xlim(0, FA.R_M + 15); ax.set_ylim(0, 1.35)
    ax.set_xlabel('distance along the arm from the hub crossing, mm', fontsize=9, color='#52514e', labelpad=18)
    ax.set_ylabel('utilisation (worst point in each 2 mm slice)', fontsize=9, color='#52514e')
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax.spines[sp].set_color('#9a9993')
    ax.tick_params(colors='#52514e', labelsize=8)
    ax.grid(axis='y', color='#e4e3df', lw=0.6)
    fig.subplots_adjust(left=0.07, right=0.66, top=0.84, bottom=0.18)
    fig.text(0.07, 0.95, 'Arm and motor cup FEA: how close each part of the arm is to its limit', fontsize=11.5, weight='bold', color='#0b0b0b')
    fig.text(0.07, 0.885, 'One 12 x 10 carbon arm with its doubler and printed motor cup (fea_arm.py, run %s, %d elements).\n'
             'Flight at the full factors (1.725 carbon, 2.156 printed); prop strikes at 1.0.' % (tag, res['info']['elements']), fontsize=8.5, color='#52514e')
    yS2, uS2 = peaks['S2']
    pct = np.nanpercentile(d['U_S2_2'].astype(float), 99)
    ax.annotate('S2 peak: the sharp inside corner where the cup\nsleeve ends on the plate (99th percentile of the\ncup in S2: %.2f; judged like the hub)' % pct,
                xy=(yS2, uS2), xytext=(150, 1.12), fontsize=7.5, color='#0b0b0b', ha='center', va='center',
                arrowprops=dict(arrowstyle='-', color='#52514e', lw=0.7))
    p = os.path.join(FIG, 'fea-arm-along.png')
    fig.savefig(p, facecolor=fig.get_facecolor()); print(p)
    return peaks


def explorer(d, tag, res, peaks):
    out = dict(source='qp/A/structures/fea_arm.py --variant current (run %s), fea_arm_figs.py' % tag,
               units='mm, arm frame: y along the arm from the hub crossing, x along the hub axis, z tangential',
               cases=HF.CASES, scale='u = stress x required factor / allowable; 0..1 blue ramp, > 1 red, NaN grey (not judged: tube and doubler within s 36 mm, see the hub FEA)',
               ramp=HF.RAMP, crit=HF.CRIT, nj=HF.NJ, mats=[])
    for m, name in enumerate(MATS):
        V = d['V%d' % m]; T = d['T%d' % m]
        q = {}
        for c in HF.CASES:
            u = d['U_%s_%d' % (c, m)].astype(float); s = d['S_%s_%d' % (c, m)].astype(float)
            uq = np.where(np.isnan(u), 65535, np.clip(np.round(u * 10000), 0, 65534)).astype(np.uint16)
            q[c] = dict(u=HF.b64(uq), umax=None if np.all(np.isnan(u)) else float(np.nanmax(u)), smax=None if np.all(np.isnan(s)) else float(np.nanmax(s)))
        out['mats'].append(dict(name=name, n=int(len(V)), pos=HF.b64(V.astype(np.float32)), idx=HF.b64(T.astype(np.uint32)), idx32=True, cases=q))
    out['peaks'] = {c: dict(at_mm=round(float(y), 1), u=round(float(u), 3)) for c, (y, u) in peaks.items()}
    out['summary'] = res['info']
    p = os.path.join(SITE, 'fea-arm.js')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('/* generated by redesign/qp/A/structures/fea_arm_figs.py - do not edit */\nwindow.FEA_ARM = ')
        json.dump(out, f, separators=(',', ':')); f.write(';\n')
    print('%s %.1f MB' % (p, os.path.getsize(p) / 1e6))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='current_d208')
    a = ap.parse_args()
    d = np.load(os.path.join(OUT, 'arm_fields_L0_%s.npz' % a.tag))
    res = json.load(open(os.path.join(OUT, 'result_L0_%s.json' % a.tag)))
    pk = figure(d, res, a.tag)
    explorer(d, a.tag, res, pk)
