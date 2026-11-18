"""fea_hub_figs.py - figures and the Explorer 3-D stress data for the D-202 / D-205 hub FEA (fea_hub.py --fields).

    python -I fea_hub_figs.py [--tag d205]           (after: python -I fea_hub.py --level 0 --tag d205 --fields --p S_END=60 SLV_W=1.5 MS=1.1)
    then, with nothing else heavy running:  blender -b -P fea_hub_render_blender.py -- [--tag d205]    -> fig/fea-hub-<case>-*.png (raw)
    then again:  python -I fea_hub_figs.py --compose                                                  -> fig/fea-hub-<case>.png (with legend)

Writes
  fig/fea-hub-margin.png         margin ratio (factor of safety / required factor) per check: D-205 hub flight F2, D-205 hub
                                 prop strike S2 (damage case, factor 1.0), and the D-193 hub as drawn (FEA-ARM.md, flight F1)
  out_fea/hub_<case>.glb         surface skins coloured by utilisation (input of the Blender renders)
  ../../../site/data/fea-hub.js  window.FEA_HUB: skins, per-vertex utilisation for F1, F2, S1, S2 (Explorer Structures view)

Colour: utilisation u = stress x required factor / allowable (fea_hub.element_fields). 0..1 runs the sequential blue ramp
(dataviz palette, step 100 -> 700); u > 1 is the status 'critical' red; grey = not judged (pins: no allowable in the
analysis; tube stubs within 15 mm of the load application; bridge within 10 mm of its fixed end).
"""
import argparse, base64, json, math, os, struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out_fea')
FIG = os.path.join(HERE, 'fig')
SITE = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'site', 'data'))
MATS = ['hub (printed PETG)', 'arm tube A (UR, LL)', 'arm tube B (LR, UL)', 'bridge tube', 'pins (3 mm carbon rod)']
CASES = {'F1': 'Full-power flight (F1): any mix of motors at full thrust, with motor torque, a fast pitch-over and prop imbalance; safety factors 2.156 printed/glue, 1.725 carbon',
         'F2': 'Motor runaway (F2): as full-power flight, but one motor stuck above its power limit (10.4 N); safety factors 2.156 / 1.725',
         'S1': 'Prop strike, push on the shaft (S1): 30 N along the motor axis, e.g. a prop hitting the ground head-on; damage case, factor 1.0',
         'S2': 'Prop strike, blade hit sideways (S2): 30 N on the blade in the disc plane, e.g. a blade clipping the ground; damage case, factor 1.0'}
RAMP = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5', '#2a78d6', '#256abf', '#1c5cab',
        '#184f95', '#104281', '#0d366b']                                  # dataviz sequential blue 100..700
CRIT, NJ = '#d03b3b', '#9a9993'                                          # status critical; not judged (neutral)


def hx(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) / 255.0


def colour(u):
    ramp = np.array([hx(h) for h in RAMP])
    t = np.clip(np.nan_to_num(u, nan=0.0), 0, 1) * (len(ramp) - 1)
    i = np.minimum(t.astype(int), len(ramp) - 2); f = (t - i)[:, None]
    c = ramp[i] * (1 - f) + ramp[i + 1] * f
    c[np.nan_to_num(u, nan=0) > 1.0] = hx(CRIT)
    c[np.isnan(u)] = hx(NJ)
    return c


# ------------------------------------------------------------------ margin chart
def margin_chart(tag):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r = json.load(open(os.path.join(OUT, 'hub_result_L0_%s.json' % tag)))
    F2 = r['F2 uncapped fault, any pattern']; S2 = r['S2 strike on UR (ground)']
    KP, KF = 1.5 * 1.15 * 1.25, 1.5 * 1.15
    def tb(c, k): return max(c['tube_A'][k], c['tube_B'][k])
    # (label, D-205 flight F2 margin, D-205 strike S2 margin, D-193 as-drawn flight F1 margin)
    rows = [('Printed hub, p99 principal', 20 / max(v['p99'] for v in F2['hub_zones_envelope'].values()) / KP,
             20 / max(v['p99'] for v in S2['hub_zones_worst_combo'].values()), 20 / 392 / KP),
            ('Glue, mean shear on the worst arm', 2.0 / F2['bond']['shear_mean_worst_arm'] / KP, 2.0 / S2['bond']['shear_mean_worst_arm'], 2.0 / 11.4 / KP),
            ('Arm tube, shear', 30 / tb(F2, 'shear') / KF, 30 / tb(S2, 'shear'), 30 / 33.5 / KF),
            ('Arm tube, hoop', 40 / tb(F2, 'hoop') / KF, 40 / tb(S2, 'hoop'), None),
            ('Arm tube, axial', 350 / tb(F2, 'axial') / KF, 350 / tb(S2, 'axial'), None)]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig = plt.figure(figsize=(10, 6.2), dpi=150); ax = fig.add_axes([0.27, 0.13, 0.66, 0.62])
    fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
    series = [('New hub (D-206), motor runaway in flight (F2, worst flight case, full factors)', '#2a78d6', 1),
              ('Old D-193 hub, full-power flight (F1; FEA-ARM.md, the design it replaced)', '#eb6834', 3),
              ('New hub (D-206), prop strike, blade hit sideways (S2, damage case, factor 1.0)', '#1baf7a', 2)]
    h = 0.26
    for j, (lab, col, k) in enumerate(series):
        for i, row in enumerate(rows):
            v = row[k]
            if v is None:
                if k == 3:
                    ax.text(0.0105, i + (j - 1) * (h + 0.03), 'D-193: not reported', va='center', fontsize=8, color='#52514e')
                continue
            y = i + (j - 1) * (h + 0.03)
            ax.barh(y, v, height=h, color=col, edgecolor='#fcfcfb', linewidth=2, label=lab if i == 0 else None)
            ax.text(v * 1.04, y, '%.2f' % v, va='center', ha='left', fontsize=8.5, color='#0b0b0b')
    ax.axvline(1.0, color='#0b0b0b', lw=1.2)
    ax.text(1.0, -0.62, '1.0 = required factor', fontsize=8.5, color='#52514e', va='bottom', ha='center')
    ax.set_xscale('log'); ax.set_xlim(0.01, 8)
    ax.set_xticks([0.01, 0.03, 0.1, 0.3, 1, 3]); ax.set_xticklabels(['0.01', '0.03', '0.1', '0.3', '1', '3'])
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r_[0] for r_ in rows])
    ax.set_xlabel('margin ratio = factor of safety / required factor (log scale; >= 1 passes)', color='#52514e')
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color('#9a9993'); ax.tick_params(colors='#52514e', length=0)
    ax.grid(axis='x', color='#e6e5e0', lw=0.8); ax.set_axisbelow(True)
    ax.set_ylim(len(rows) - 0.5, -0.75)
    fig.text(0.02, 0.955, 'Hub FEA: each check against its required factor', fontsize=12.5, color='#0b0b0b', weight='bold')
    fig.text(0.02, 0.92, 'New hub (D-202, D-205, D-206 16x14 bridge) in flight and in a prop strike, and the hub it replaced (D-193) in flight', fontsize=9.5, color='#52514e')
    fig.legend(loc='upper left', bbox_to_anchor=(0.02, 0.905), frameon=False, fontsize=8.5, ncol=1)
    fig.text(0.02, 0.025, 'Limit loads: fea_hub.py run %s (structures/out_fea/hub_result_L0_%s.json); D-193 values from FEA-ARM.md s4.\nAllowables EST: PETG 20, CFRP axial 350 / hoop 40 / shear 30, glue 2.0 MPa (coupon COUPON-BOND-D202.md pending).' % (tag, tag),
             fontsize=7.5, color='#52514e')
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(os.path.join(FIG, 'fea-hub-margin.png'), facecolor=fig.get_facecolor())
    print('fig/fea-hub-margin.png')
    return rows


# ------------------------------------------------------------------ GLB (Blender input)
def normals(V, T):
    n = np.zeros_like(V)
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    for k in range(3):
        np.add.at(n, T[:, k], fn)
    return n / np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]


def write_glb(path, meshes):
    """meshes: list of (name, V (m), T, rgb 0..1). Minimal glTF 2.0 binary, one node per mesh."""
    bin_, views, accs, gm, nodes = b'', [], [], [], []
    def add(arr, target, comp, typ, norm=False, mm=False):
        nonlocal bin_
        data = arr.tobytes(); off = len(bin_); bin_ += data + b'\0' * ((4 - len(data) % 4) % 4)
        views.append(dict(buffer=0, byteOffset=off, byteLength=len(data), target=target))
        a = dict(bufferView=len(views) - 1, componentType=comp, count=len(arr), type=typ)
        if norm: a['normalized'] = True
        if mm: a['min'] = arr.min(0).tolist(); a['max'] = arr.max(0).tolist()
        accs.append(a); return len(accs) - 1
    for name, V, T, rgb in meshes:
        V = (V[:, [0, 2, 1]] * np.array([1, 1, -1])).astype(np.float32)   # z-up hub frame -> glTF y-up (a rotation: winding kept)
        N = normals(V, T).astype(np.float32)
        lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)      # glTF COLOR_0 is linear
        C = np.hstack([np.round(lin * 255), np.full((len(V), 1), 255)]).astype(np.uint8)
        p = add(V, 34962, 5126, 'VEC3', mm=True); n = add(N, 34962, 5126, 'VEC3'); c = add(C, 34962, 5121, 'VEC4', norm=True)
        i = add(T.astype(np.uint32).ravel(), 34963, 5125, 'SCALAR')
        gm.append(dict(name=name, primitives=[dict(attributes=dict(POSITION=p, NORMAL=n, COLOR_0=c), indices=i, material=0)]))
        nodes.append(dict(name=name, mesh=len(gm) - 1))
    js = dict(asset=dict(version='2.0', generator='fea_hub_figs.py'), scene=0, scenes=[dict(nodes=list(range(len(nodes))))], nodes=nodes,
              meshes=gm, materials=[dict(name='fea', pbrMetallicRoughness=dict(baseColorFactor=[1, 1, 1, 1], metallicFactor=0, roughnessFactor=0.8), doubleSided=True)],
              accessors=accs, bufferViews=views, buffers=[dict(byteLength=len(bin_))])
    j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((4 - len(j) % 4) % 4)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(bin_)))
        f.write(struct.pack('<II', len(j), 0x4E4F534A)); f.write(j)
        f.write(struct.pack('<II', len(bin_), 0x004E4942)); f.write(bin_)


# ------------------------------------------------------------------ Explorer data
def b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def explorer_data(d, tag, rows, res):
    out = dict(source='qp/A/structures/fea_hub.py run %s (fields), fea_hub_figs.py' % tag, units='mm, hub frame: x aft from the hub axis, y right, z up',
               cases=CASES, scale='u = stress x required factor / allowable; 0..1 blue ramp, > 1 red, NaN grey (not judged)',
               ramp=RAMP, crit=CRIT, nj=NJ, mats=[])
    for m, name in enumerate(MATS):
        if 'V%d' % m not in d.files:
            continue
        V = d['V%d' % m]; T = d['T%d' % m]
        q = {}
        for c in CASES:
            u = d['U_%s_%d' % (c, m)].astype(float)
            s = d['S_%s_%d' % (c, m)].astype(float)
            uq = np.where(np.isnan(u), 65535, np.clip(np.round(u * 10000), 0, 65534)).astype(np.uint16)   # u in 1e-4 steps, 65535 = not judged
            q[c] = dict(u=b64(uq), umax=None if np.all(np.isnan(u)) else float(np.nanmax(u)), smax=float(np.nanmax(s)))
        out['mats'].append(dict(name=name, n=int(len(V)), pos=b64(V.astype(np.float32)), idx=b64(T.astype(np.uint32)), idx32=True, cases=q))
    out['checks'] = [dict(item=r_[0], f2=r_[1], s2=r_[2], old=r_[3]) for r_ in rows]
    out['summary'] = dict(dof=res['dof'], elements=res['elements'], equilibrium=res['equilibrium'], hub_g=res['hub_g'])
    p = os.path.join(SITE, 'fea-hub.js')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('/* generated by redesign/qp/A/structures/fea_hub_figs.py - do not edit */\nwindow.FEA_HUB = ')
        json.dump(out, f, separators=(',', ':')); f.write(';\n')
    print('%s %.1f MB' % (p, os.path.getsize(p) / 1e6))


def compose():
    """Raw Blender renders + legend strip -> fig/fea-hub-<case>.png."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    for c in ('F2', 'S2'):
        views = [('outside', 'Outside: printed hub skin'), ('inside', 'Hub hidden: arm tubes, bridge, pins')]
        imgs = [os.path.join(FIG, 'fea-hub-%s-%s.raw.png' % (c, v)) for v, _ in views]
        if not all(os.path.exists(i) for i in imgs):
            print('missing raw renders for', c); continue
        fig = plt.figure(figsize=(11, 5.6), dpi=150); fig.patch.set_facecolor('#fcfcfb')
        for k, (img, (v, t)) in enumerate(zip(imgs, views)):
            ax = fig.add_axes([0.01 + k * 0.49, 0.16, 0.48, 0.66]); ax.imshow(plt.imread(img)); ax.axis('off')
            ax.set_title(t, fontsize=10, color='#0b0b0b', loc='left')
        t_, d_ = CASES[c].split(': ', 1)
        fig.text(0.01, 0.955, 'Hub FEA: %s' % t_, fontsize=11, color='#0b0b0b', weight='bold')
        import textwrap
        fig.text(0.01, 0.935, textwrap.fill(d_[0].upper() + d_[1:] + '. Colour = utilisation (stress x required factor / allowable), worst over every load pattern.', 150), fontsize=8.5, color='#52514e', va='top')
        cax = fig.add_axes([0.06, 0.08, 0.5, 0.035])
        cm = ListedColormap([hx(h) for h in RAMP])
        cb = fig.colorbar(plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(0, 1)), cax=cax, orientation='horizontal')
        cb.set_ticks([0, 0.25, 0.5, 0.75, 1.0]); cb.outline.set_visible(False); cax.tick_params(labelsize=8, colors='#52514e', length=0)
        cax.set_xlabel('utilisation 0 to 1 (1 = at the allowable with the required factor)', fontsize=8.5, color='#52514e')
        for k, (col, lab) in enumerate(((CRIT, 'over 1: fails'), (NJ, 'not judged (pins: no allowable; load-application ends)'))):
            fig.patches.append(plt.Rectangle((0.60, 0.085 - k * 0.05), 0.015, 0.03, transform=fig.transFigure, color=hx(col)))
            fig.text(0.62, 0.09 - k * 0.05, lab, fontsize=8.5, color='#0b0b0b', va='bottom')
        out = os.path.join(FIG, 'fea-hub-%s.png' % c)
        fig.savefig(out, facecolor=fig.get_facecolor()); plt.close(fig); print(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='d205'); ap.add_argument('--compose', action='store_true')
    a = ap.parse_args()
    if a.compose:
        compose(); raise SystemExit
    rows = margin_chart(a.tag)
    d = np.load(os.path.join(OUT, 'hub_fields_L0_%s.npz' % a.tag))
    res = json.load(open(os.path.join(OUT, 'hub_result_L0_%s.json' % a.tag)))
    for c in CASES:
        meshes = []
        for m, name in enumerate(MATS):
            if 'V%d' % m in d.files:
                meshes.append((name, d['V%d' % m] / 1000.0, d['T%d' % m], colour(d['U_%s_%d' % (c, m)].astype(float))))
        write_glb(os.path.join(OUT, 'hub_%s.glb' % c), meshes)
    print('out_fea/hub_<case>.glb')
    explorer_data(d, a.tag, rows, res)
