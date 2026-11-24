"""Build the Explorer "Simulations" view from the physics-rerun results and inject it into app.html.

    python -I redesign/site/make_sims_view.py && python -I redesign/site/make_index.py

Reads redesign/qp/A/mechanism/out/T097_results.json (AR-014 landing, AR-015 SITL; T-097, 2026-11-23) and, when it
exists, T098_results.json (T-098 landing decision). Copies the plots into site/assets/sims/. The view sits between the
markers <!-- sims-view:begin --> / <!-- sims-view:end --> in app.html; everything between them is regenerated.
"""
import html, json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'redesign', 'qp', 'A', 'mechanism', 'out')
GH = 'https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/'
BEGIN, END = '<!-- sims-view:begin', '<!-- sims-view:end -->'

e = html.escape
def link(path, text=None):
    return '<a class="ds-link" href="%s%s" target="_blank" rel="noopener">%s</a>' % (GH, path, e(text or path.split('/')[-1]))
def badge(ok):
    if ok is None: return '<span class="ds-tag">info</span>'
    return '<span class="ds-badge" data-status="%s">%s</span>' % (('CHECKED', 'PASS') if ok else ('FAIL', 'FAIL'))
def num(v, f='%.2f'):
    return '&mdash;' if v is None else (f % v)

t97 = json.load(open(os.path.join(OUT, 'T097_results.json'), encoding='utf-8'))
t98p = os.path.join(OUT, 'T098_results.json')
t98 = json.load(open(t98p, encoding='utf-8')) if os.path.exists(t98p) else None

# plots
dst = os.path.join(HERE, 'assets', 'sims'); os.makedirs(dst, exist_ok=True)
plots = []
for sub in ('T097_plots', 'T098_plots'):
    d = os.path.join(OUT, sub)
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(('.png', '.svg')):
                shutil.copyfile(os.path.join(d, f), os.path.join(dst, f)); plots.append((sub, f))

LIM = dict(stroke_mm=('<=', 20.0), n_g=('<=', 12.0), tilt_deg=('<=', 3.0), rib_rf=('>=', 1.0))
def ok(k, v):
    op, lim = LIM[k]
    return v <= lim if op == '<=' else v >= lim

def landing_table(run):
    rows = []
    for name, c in run['cases'].items():
        cells, allok = [], True
        for k, f in (('stroke_mm', '%.1f'), ('n_g', '%.2f'), ('tilt_deg', '%.1f'), ('rib_rf', '%.2f')):
            good = ok(k, c[k]); allok &= good
            cells.append('<td class="val">%s%s</td>' % ('<b>' + f % c[k] + '</b>' if not good else f % c[k], ''))
        rows.append('<tr><td class="first">%s</td>%s<td class="val">%.1f</td><td>%s</td></tr>' % (e(name), ''.join(cells), c['side_N'], badge(allok)))
    return ('<div class="scroll"><table class="ds-table"><thead><tr><th>Touchdown case</th><th>Foam stroke, mm (&le; 20)</th>'
            '<th>Peak load, g (&le; 12)</th><th>End tilt, &deg; (&le; 3)</th><th>Fin-rib root strength ratio (&ge; 1.0)</th>'
            '<th>Side load per foot, N</th><th>Result</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')

L = t97['landing_raw']; S = t97['sitl_raw']
p30, p45 = L['cad_1881_p30'], L['cad_1881_p45']
tip = p30['static']['tip_narrow_edge_toward_cg']
n30 = sum(1 for c in p30['cases'].values() if all(ok(k, c[k]) for k in LIM))
n45 = sum(1 for c in p45['cases'].values() if all(ok(k, c[k]) for k in LIM))

def sitl_row(label, key, f, limit, judge):
    vals = [S[t][key] for t in ('T097_Z5', 'T097_Z5_lua')]
    good = None if judge is None else all(judge(v) for v in vals)
    return '<tr><td class="first">%s</td>%s<td>%s</td><td>%s</td></tr>' % (
        label, ''.join('<td class="val">%s</td>' % (f % v) for v in vals), limit, badge(good))

sitl = ''.join([
    sitl_row('Highest climb during the transition, m', 'alt_max_gain', '%.1f', 'under 60', lambda v: v < 60),
    sitl_row('Peak altitude, m (start 50 m)', 'alt_peak_abs', '%.1f', 'under 110', lambda v: v < 110),
    sitl_row('Time to 1.3 &times; stall speed (17.75 m/s), s', 't_to_1.3Vs_s', '%.1f', '15 or less', lambda v: v <= 15),
    sitl_row('Longest run at the motor cap, s', 't_cap_run_s', '%.1f', '1 or less', lambda v: v <= 1),
    sitl_row('Elevon pitch use, share of &plusmn;15&deg;', 'pitch_use_15', '%.2f', '0.60 or less', lambda v: v <= 0.60),
    sitl_row('Elevon pitch use, share of &plusmn;20&deg; (information only)', 'pitch_use_20', '%.2f', 'not a pass line (D-244 withdrawn)', None),
    sitl_row('Elevon pitch use, share of &plusmn;25&deg; (information only)', 'pitch_use_25', '%.2f', 'not a pass line', None),
    sitl_row('Peak pack current, A', 'I_pack_peak_A', '%.1f', 'reported', None),
    sitl_row('Cruise speed at the end, m/s', 'V_end', '%.1f', '1.3 &times; stall 17.75 (A-P6, already failing)', lambda v: v >= 17.75),
    '<tr><td class="first">Touchdown sink speed after the back-transition, m/s</td>%s<td>1.2 or less, no tip-over</td><td>%s</td></tr>' % (
        ''.join('<td class="val">%.2f</td>' % S[t]['landing']['sink_peak_last1s_ms'] for t in ('T097_Z5', 'T097_Z5_lua')),
        badge(all(S[t]['landing']['sink_peak_last1s_ms'] <= 1.2 and not S[t]['landing']['tipped_over'] for t in ('T097_Z5', 'T097_Z5_lua')))),
])

def fig(sub, f, alt, cap):
    return '<figure class="fea-fig"><img src="assets/sims/%s" alt="%s" loading="lazy"><figcaption>%s %s</figcaption></figure>' % (
        f, e(alt), cap, '<span class="ds-source">' + e('qp/A/mechanism/out/%s/%s' % (sub, f)) + '</span>')

t98html = ''
if t98:
    R = t98.get('rows', [])
    def worst(prefix):
        out = {}
        for r in R:
            if r['case'].startswith(prefix + '/'):
                out[r['case'].split('/')[1]] = ([float(x) for x in str(r['value']).split(' / ')], r['pass'])
        return out
    LIMS = [('<=', 20), ('<=', 12), ('<=', 3.0), ('>=', 1.0)]
    def wcells(v, lims=LIMS):
        return ''.join('<td class="val">%s</td>' % (('<b>%s</b>' if not (x <= L if op == '<=' else x >= L) else '%s') % f)
                       for x, (op, L), f in zip(v, lims, ('%.1f' % v[0], '%.2f' % v[1], '%.2f' % v[2], '%.2f' % v[3])))
    # joint grid: plateau x damping, 20 mm stroke, drawn rib
    grid = {}
    for k, (v, g) in worst('plateau_sweep_rib25x23').items():
        grid.setdefault(float(k[:-1]), {})[0.05] = g
    for pre in ('zeta_grid_rib25x23', 'zeta_sensitivity_rib25x23'):
        for k, (v, g) in worst(pre).items():
            fp, z = k.split('N_zeta'); grid.setdefault(float(fp), {})[float(z)] = g
    zs = sorted({z for d in grid.values() for z in d})
    def cell(fp, z):
        g = grid[fp].get(z)
        if g is None: return '<td class="val">&middot;</td>'
        if g and fp > 39.0: return '<td class="val">pass*</td>'
        if g and 37.5 <= fp <= 39.0 and 0.02 <= z <= 0.05: return '<td class="val"><b>PASS</b></td>'
        return '<td class="val">%s</td>' % ('pass' if g else 'fail')
    grows = ''.join('<tr><td class="first">%g N</td>%s</tr>' % (fp, ''.join(cell(fp, z) for z in zs)) for fp in sorted(grid))
    srows = ''.join('<tr><td class="first">%s</td>%s<td>%s</td></tr>' % (e(k.replace('N', ' N')), wcells(v), badge(g))
                    for k, (v, g) in worst('plateau_sweep_rib25x23').items())
    frows = ''.join('<tr><td class="first">%s</td>%s<td>%s</td></tr>' % (e(k.replace('N_zeta', ' N, damping ')), wcells(v, [('<=', 24)] + LIMS[1:]), badge(g))
                    for pre in ('fallback_24mm_stroke24_rib25x23', 'fallback_24mm_zeta_rib25x23') for k, (v, g) in worst(pre).items())
    chosen = {}
    for r in R:
        if r['case'].startswith('chosen_37.5N'):
            chosen.setdefault(r['case'].split('/', 1)[1], {})[r['metric']] = (r['value'], r['pass'])
    crows = ''
    for k, m in chosen.items():
        vals = [m.get(x, (None, None)) for x in ('foam stroke (mm)', 'peak load factor (g)', 'end tilt (deg)', 'rib-root RF (min over run)')]
        crows += '<tr><td class="first">%s</td>%s<td>%s</td></tr>' % (
            e(k), ''.join('<td class="val">%s</td>' % ('&mdash;' if v is None else v) for v, _ in vals), badge(all(g for _, g in vals if g is not None)))
    trows = ''.join('<tr><td class="first">%s</td><td class="val">%s&deg;</td><td>%s</td></tr>' % (e(r['case'].split(', ', 1)[1]), r['value'], badge(r['pass']))
                    for r in R if r['case'].startswith('A-P9'))
    prows = ''.join('<tr><td class="first">%s</td><td>%s</td><td class="val">%s</td><td>%s</td><td>%s</td></tr>' % (
        e(r['case']), e(r['metric']), e(str(r['value'])), e(str(r['limit'])), badge(r['pass']))
        for r in R if r.get('category') == 'flight dynamics')
    ZH = ''.join('<th>damping %g</th>' % z for z in zs)
    t98html = ('<h3 class="ds-h2" id="sims-t098">Landing fix (T-098, AR-016)</h3>'
               '<p class="use"><b>Result:</b> the landing passes all ten cases only if the pad foam is inside a narrow window: crush force 37.5&ndash;39 N per pad <i>and</i> damping ratio 0.02&ndash;0.05, with the current 20 mm of usable crush and no CAD change. The window is about &plusmn;2 %, tighter than real foam is likely to hold, so the foam coupon bench test (TP-3) decides. If the foam misses it, the fallback is a longer pad (36 mm, 24 mm usable), which widens the window to 34.5&ndash;39 N (&plusmn;6 %) but is a CAD change not yet made. <span class="ds-badge" data-status="UNVERIFIED">UNVERIFIED</span></p>'
               '<p class="use">Why the window has these edges. The T-097 runs checked the fin-rib tube at its old 14 &times; 12 mm size; on the drawn 25 &times; 23 mm tube (since D-226) the rib is never the limit. A foam that is too soft or too lightly damped bottoms out in the hard lean-and-drift case (stroke past 20 mm; where it hits the stop the jolt can pass 12 g); one that is too firm or too heavily damped passes 12 g on a hard straight landing. The 39 N upper edge is not from these tables: it is where the wing&rsquo;s rib cell, sized at 36 N in T-083, would reach its strength limit, found by scaling that result by force (an estimate, not a rerun).</p>'
               '<h4>Which foams pass, 20 mm usable crush (worst of the ten cases)</h4>'
               '<div class="scroll"><table class="ds-table"><thead><tr><th>Crush force per pad</th>' + ZH + '</tr></thead><tbody>' + grows + '</tbody></table></div>'
               '<p class="use"><b>PASS</b>: inside the accepted window. pass*: the touchdown passes, but above the 39 N rib-cell cap. &middot;: not run.</p>'
               '<h4>Crush force sweep at damping 0.05, worst of the ten cases</h4>'
               '<div class="scroll"><table class="ds-table"><thead><tr><th>Crush force per pad</th><th>Stroke, mm (&le; 20)</th><th>Peak load, g (&le; 12)</th><th>End tilt, &deg; (&le; 3)</th><th>Rib strength ratio (&ge; 1.0)</th><th>Result</th></tr></thead><tbody>' + srows + '</tbody></table></div>'
               '<h4>At 37.5 N and damping 0.05: all ten cases</h4>'
               '<div class="scroll"><table class="ds-table"><thead><tr><th>Touchdown case</th><th>Stroke, mm</th><th>Peak load, g</th><th>End tilt, &deg;</th><th>Rib strength ratio</th><th>Result</th></tr></thead><tbody>' + crows + '</tbody></table></div>'
               '<h4>Fallback: 36 mm pad, 24 mm usable crush (CAD change not made)</h4><p class="use">Run with the feet at the current 30 mm-pad position. Review round 11 re-ran it at the 36 mm-pad position: the tightest case tilts 2.97&deg; against the 3&deg; limit, still a pass.</p>'
               '<div class="scroll"><table class="ds-table"><thead><tr><th>Foam</th><th>Stroke, mm (&le; 24)</th><th>Peak load, g (&le; 12)</th><th>End tilt, &deg; (&le; 3)</th><th>Rib strength ratio (&ge; 1.0)</th><th>Result</th></tr></thead><tbody>' + frows + '</tbody></table></div>'
               '<p class="use">Longer pads move the feet outboard and lower the static tip-over angle (target 30.5&deg;). The 36 mm pad keeps it by 0.10&deg; at the pad edge (29.81&deg; at the pad centre); the 40 mm pad of the T-083 analysis misses it. The shoe, fin tube, root fitting and rib cell were not re-checked on the longer pad.</p>'
               '<div class="scroll"><table class="ds-table"><thead><tr><th>Pad</th><th>Static tip-over, edge toward the CG</th><th>Result</th></tr></thead><tbody>' + trows + '</tbody></table></div>'
               '<h4>Elevon pitch use</h4>'
               '<p class="use">The pass line stays at 0.60 of &plusmn;15&deg; and fails (0.69&ndash;0.79), carried as an open item. A proposal to judge it on the &plusmn;20&deg; servo endpoint was withdrawn in review: it would have cut the reserve kept for roll and gusts from 16&deg; to 8&deg; without a derivation for this aircraft. The &plusmn;20&deg; and &plusmn;25&deg; values are for information only.</p>'
               '<div class="scroll"><table class="ds-table"><thead><tr><th>Run</th><th>Check</th><th>Value</th><th>Limit</th><th>Result</th></tr></thead><tbody>' + prows + '</tbody></table></div>'
               '<span class="ds-source">' + link('redesign/qp/A/mechanism/out/T098_results.json') + ' &middot; ' + link('redesign/qp/A/mechanism/out/T098_data/sweep_t098.py')
               + ' &middot; ' + link('docs/audits/2026-11-23-T098-landing-ladder.md') + ' &middot; params/CHANGE-LOG.md D-243, D-244 &middot; qp/A/TEST-PLAN-O4B.md TP-3</span>')
else:
    t98html = ('<h3 class="ds-h2" id="sims-t098">Landing fix (T-098)</h3><p class="use">Pending. A foam-plateau and pad sweep is being run '
               'on the current 25 &times; 23 fin-rib tube to pick a landing-pad setting that passes every case. The rib strength ratios above were '
               'computed on the older 14 &times; 12 rib tube that the landing script still assumed; the CAD has used 25 &times; 23 since D-226.</p>')

landplots = ''.join(fig(s, f, 'Landing simulation time history, %s' % f, '<b>Landing, soft foam (30 N).</b> Contact force on each foot over the first 0.6 s. Top: the hard level landing (passes). Bottom: the hard narrow lean with drift, where one foot hits the stop at about 170 N (fails).') for s, f in plots if f.startswith('landing'))
sitlplots = ''.join(fig(s, f, 'SITL transition time history, %s' % f, '<b>Transition flight, without Lua.</b> Altitude, airspeed, pitch and mean elevon over the first 60 s: pitch-over, cruise, then back-transition to hover. Red dashed lines: 0.60 &times; 15&deg;. The pitch-use line is judged from the start of the transition to the end of cruise (about 26 s); the flat &minus;13&deg; stretch after that is the back-transition, which has no elevon line.') for s, f in plots if f.startswith('sitl'))

landsum = ('<b>Landing passes only inside a narrow foam window</b> (crush force 37.5&ndash;39 N per pad and damping 0.02&ndash;0.05; T-098, below), which the foam bench test decides; a longer-pad fallback widens it. The first rerun (30 N and 45 N foam) failed %d and %d of 10 cases.' % (10 - n30, 10 - n45)) if t98 else ('<b>Landing does not yet pass:</b> on the soft foam (30 N per pad) %d of 10 touchdown cases pass, and on the stiff foam (45 N) %d of 10.' % (n30, n45))
view = '''%s (generated by redesign/site/make_sims_view.py from qp/A/mechanism/out/T097_results.json; do not edit) -->
<section class="view" id="sims" hidden>
  <div class="page">
<section class="c" id="sims-top">
  <header>
    <span class="secno">Physics simulations &middot; AR-014 / AR-015 &middot; T-097 &middot; %s</span>
    <h1 class="ds-display">Simulations</h1>
    <p class="summary">Both physics simulations were re-run on the current design: 1.881 kg (estimate), SunnySky X2216 motors, CG 22.05 mm. <b>Transition flight passes</b> every line except elevon pitch use (0.69&ndash;0.79 of &plusmn;15&deg; against 0.60, an open item) and the cruise speed already carried as A-P6. %s The aircraft never tips over (static tip-over angle %.2f&deg;, needs 30.5&deg;). These are calculations, not tests: the foam and pad friction are estimates until the bench tests.</p>
    <p class="use">Landing: a 6-degree-of-freedom rigid-body model with four crushable foam feet and pad friction 0.40 (<code class="ds-inline">landing_a.py</code>). Flight: ArduPlane 4.7.3 SITL, the real autopilot firmware and the project parameter file, flying a model of the aircraft (<code class="ds-inline">a_plant.py</code>). No pass line was changed for these runs. <span class="ds-badge" data-status="MODELLED">MODELLED</span></p>
  </header>

  <h3 class="ds-h2" id="sims-landing">Landing (AR-014)</h3>
  <p class="use">Ten touchdowns per foam setting, from a normal 0.5 m/s landing up to a hard 1.2 m/s one, leaning 10&deg; and drifting sideways at 0.5 m/s. Static tip-over angle %.2f&deg; %s. The one soft-foam failure is the hard narrow lean with drift: the pads crush their full 20 mm, the aircraft hits the stop, and the jolt reaches 17.5 g. The stiff foam does not bottom out but the jolt is just over 12 g on a straight hard landing. Values in bold miss their limit.%s</p>
  <h4>Soft foam, 30 N per pad</h4>
  %s
  <h4>Stiff foam, 45 N per pad</h4>
  %s
  %s
  <span class="ds-source">%s &middot; %s &middot; %s</span>

  <h3 class="ds-h2" id="sims-sitl">Transition flight (AR-015)</h3>
  <p class="use">Vertical take-off to 50 m, pitch-over into wing-borne flight, 15 s of cruise, back-transition, hover and automatic landing. Two runs: without and with the Lua motor cap script and battery monitor. The elevon pitch-use line is 0.60 of &plusmn;15&deg; and fails (0.69 here, 0.77&ndash;0.79 in the T-074 case); it is carried as an open item. The &plusmn;20&deg; and &plusmn;25&deg; shares are shown for information only (D-244, withdrawn in review).</p>
  <div class="scroll"><table class="ds-table"><thead><tr><th>Check</th><th>Without Lua</th><th>With Lua cap and battery monitor</th><th>Limit</th><th>Result</th></tr></thead><tbody>%s</tbody></table></div>
  %s
  <span class="ds-source">%s &middot; %s</span>

  %s

  <h3 class="ds-h2" id="sims-limits">What these simulations leave out</h3>
  <ul class="use">
    <li>Foam crush force, usable stroke and pad friction are estimates until the foam coupon and pad drag bench tests.</li>
    <li>Landing is rigid-body: no wing or fin bending, no motor thrust during touchdown after 0.6 s.</li>
    <li>SITL: one run per case (repeat scatter about 0.01&ndash;0.03); no wind or gust case; battery capacity drain is not modelled (the pack is held at its rest voltage, with internal-resistance sag); the flight controller&rsquo;s 75 mm offset (D-240) is not modelled here (it is covered by the vibration analysis).</li>
  </ul>
  <span class="ds-source">Full report: %s &middot; machine-readable results: %s &middot; %s</span>
</section>
  </div>
</section>
%s''' % (
    BEGIN, e(t97.get('generated', '2026-11-23')[:10]), landsum, tip, tip, badge(tip >= 30.5),
    (' <b>Note:</b> the rib strength ratios in these two tables were computed on the old 14 &times; 12 rib tube; the drawn tube is 25 &times; 23 (see the landing fix below).' if t98 else ''), landing_table(p30), landing_table(p45), landplots,
    link('redesign/qp/A/mechanism/out/T097_data/landing_cad_1881_p30.txt'), link('redesign/qp/A/mechanism/out/T097_data/landing_cad_1881_p45.txt'), link('docs/analysis-records.md', 'AR-014'),
    sitl, sitlplots, link('redesign/qp/A/sitl/SITL-FLIGHT.md'), link('docs/analysis-records.md', 'AR-015'),
    t98html,
    link('docs/audits/2026-11-23-T097-sim-rerun.md'), link('redesign/qp/A/mechanism/out/T097_results.json'), link('docs/analysis-records.md'),
    END)

p = os.path.join(HERE, 'app.html')
app = open(p, encoding='utf-8').read()
if BEGIN in app:
    app = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), lambda m: view, app, flags=re.S)
else:
    app = app.replace('<!-- proof-embed:begin', view + '\n\n<!-- proof-embed:begin', 1)
nav = '<a href="#sims" title="Landing and transition-flight physics simulations at the current design">Simulations</a>'
if nav not in app:
    app = app.replace('every check">Structures</a>\n', 'every check">Structures</a>\n    ' + nav + '\n', 1)
open(p, 'w', encoding='utf-8', newline='\n').write(app)
print('sims view: %d bytes, plots %d, T-098 %s' % (len(view), len(plots), 'in' if t98 else 'pending'))
