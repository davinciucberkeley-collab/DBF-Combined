"""Replay panels for the Explorer "Simulations" view (T-105 B1). Called by make_sims_view.py; also runnable alone:

    python -I redesign/site/make_replays_view.py

Copies redesign/qp/A/sims3d/out/{flight_*,landing_*,linkage}.json to site/assets/sims3d/, writes manifest.json there
(case list, labels, KB per file, totals, prop spin geometry from data/viewer-data.json) and returns the replay HTML
that make_sims_view.py puts between the intro and the Landing (AR-014) heading. The 3-D and plots are drawn by replay.js
(loaded the first time the #sims route is shown). Nothing here is a simulation: it plays back the recorded files.
"""
import html, json, math, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'redesign', 'qp', 'A', 'sims3d', 'out')
DST = os.path.join(HERE, 'assets', 'sims3d')
GH = 'https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/'
SRC_REL = 'redesign/qp/A/sims3d/out/'
VER = '20261124a'
e = html.escape
LABEL = 'Playback of recorded simulation output (not a new simulation).'

# ---- plain labels -------------------------------------------------------------------------------------------------
DESIGN = {
    'T097': 'Baseline 1.881 kg (T-097)',
    'T101C1': 'Controls fix C1: 1.0 s hold before the CRUISE switch (T-101)',
    'T101C2': 'Controls fix C2: C1 plus TECS time constant 8 (T-101)',
    'T101C3': 'Current design basis: controls fix C3 at 0.25 chord (T-101)',
}
DESIGN_SHORT = {'T097': 'Baseline 1.881 kg', 'T101C1': 'Controls fix C1', 'T101C2': 'Controls fix C2',
                'T101C3': 'Current design basis: C3 at 0.25 chord'}
DESIGN_TAG = {'T097': 'baseline', 'T101C1': 'fix C1', 'T101C2': 'fix C2', 'T101C3': 'C3, current basis'}   # option text
CASE = {'T074': 'hard case T-074', 'Z5': 'full flight Z5'}
CASE_REF = {'T097': ' (T-097)', 'T101C1': ' (T-101)', 'T101C2': ' (T-101)', 'T101C3': ' (T-101)'}
DEFAULT_FLIGHT = 'T101C3_T074'
FLIGHT_RUNS = [d + '_' + c + l for d in ('T101C3', 'T101C1', 'T101C2', 'T097') for c in ('T074', 'Z5') for l in ('', '_lua')]

def flight_label(run):
    lua = run.endswith('_lua'); base = run[:-4] if lua else run
    d, c = base.split('_')
    s = '%s, %s%s' % (DESIGN_SHORT[d], CASE[c], CASE_REF[d])
    return s + (', with Lua motor cap and battery monitor' if lua else ', without Lua')

def flight_short(run):
    lua = run.endswith('_lua'); base = run[:-4] if lua else run
    d, c = base.split('_')
    return '%s, %s%s' % (DESIGN_TAG[d], 'hard T-074' if c == 'T074' else 'full flight Z5', ', Lua' if lua else '')

LANDING = [  # file stem, plain label, T-098 case name (as in make_sims_view.py), short option text
    ('hard_level', 'Hard level landing, 1.2 m/s sink', 'hard level', 'Hard, level, 1.2 m/s sink'),
    ('hard_10_narrow', 'Hard landing leaning 10 deg, narrow axis', 'hard 10 narrow', 'Hard, 10 deg lean, narrow axis'),
    ('hard_10_narrow_neg', 'Hard landing leaning 10 deg the other way, narrow axis', 'hard 10 narrow neg', 'Hard, 10 deg lean the other way'),
    ('hard_10_narrow_plus_drift_p5', 'Hard landing leaning 10 deg, narrow axis, drifting 0.5 m/s (tightest case)', 'hard 10 narrow + drift .5', 'Hard, 10 deg narrow, drift 0.5 m/s'),
    ('hard_10_wide', 'Hard landing leaning 10 deg, wide axis', 'hard 10 wide', 'Hard, 10 deg lean, wide axis'),
    ('hard_10_wide_plus_drift_p5_y', 'Hard landing leaning 10 deg, wide axis, drifting 0.5 m/s sideways', 'hard 10 wide + drift .5 y', 'Hard, 10 deg wide, drift 0.5 m/s'),
    ('hard_7-7_combo', 'Hard landing leaning 7 deg on both axes', 'hard 7/7 combo', 'Hard, 7 deg lean on both axes'),
    ('normal_level_p5', 'Normal level landing, 0.5 m/s sink', 'normal level .5', 'Normal, level, 0.5 m/s sink'),
    ('normal_10_narrow_p5', 'Normal landing leaning 10 deg, narrow axis, 0.5 m/s sink', 'normal 10 narrow .5', 'Normal, 10 deg lean, narrow, 0.5 m/s'),
    ('normal_10_wide_p5_plus_drift', 'Normal landing leaning 10 deg, wide axis, drifting 0.5 m/s', 'normal 10 wide .5 + drift', 'Normal, 10 deg wide, drift 0.5 m/s'),
]

def kb(path): return round(os.path.getsize(path) / 1024.0, 1)

def link(path, text=None):
    return '<a class="ds-link" href="%s%s" target="_blank" rel="noopener">%s</a>' % (GH, path, e(text or path.split('/')[-1]))

def prop_geometry():
    d = json.load(open(os.path.join(HERE, 'data', 'viewer-data.json'), encoding='utf-8'))
    cg = {p['id']: p['cg_xyz_m'] for p in d['parts']}
    out = {}
    for c in ('UL', 'UR', 'LL', 'LR'):
        m, p = cg['PRP-001-' + c], cg['PRP-002-' + c]
        v = [p[i] - m[i] for i in range(3)]; n = math.sqrt(sum(x * x for x in v))
        out[c] = dict(center=[round(x, 5) for x in p], axis=[round(x / n, 5) for x in v])
    # spin sense from the part names (PRP-002-LL "CW reverse", LR "CCW standard", ...)
    name = {p['id']: p['name'] for p in d['parts']}
    for c in out:
        out[c]['dir'] = -1 if ' CW ' in name['PRP-002-' + c] + ' ' or 'CW reverse' in name['PRP-002-' + c] else 1
    return out

def build():
    os.makedirs(DST, exist_ok=True)
    files = {}
    for f in sorted(os.listdir(SRC)):
        if f.endswith('.json') and (f.startswith(('flight_', 'landing_')) or f == 'linkage.json'):
            shutil.copyfile(os.path.join(SRC, f), os.path.join(DST, f)); files[f] = kb(os.path.join(DST, f))
    glb = os.path.join(HERE, 'assets', 'concept-a.opt.glb')
    flight = [dict(id=r, file='flight_%s.json' % r, label=flight_label(r), short=flight_short(r), kb=files['flight_%s.json' % r], default=(r == DEFAULT_FLIGHT)) for r in FLIGHT_RUNS]
    landing = [dict(id=s, file='landing_%s.json' % s, label=l, short=sh, case=c, kb=files['landing_%s.json' % s]) for s, l, c, sh in LANDING]
    man = dict(version=VER, note=LABEL, source=SRC_REL, flight=flight, landing=landing,
               linkage=dict(file='linkage.json', kb=files['linkage.json']), glb=dict(file='../concept-a.opt.glb', kb=kb(glb)),
               total_kb=round(sum(files.values()), 1), props=prop_geometry(),
               th_to_prop=['LR', 'UL', 'LL', 'UR'], pad_order=['UR', 'LR', 'UL', 'LL'])
    with open(os.path.join(DST, 'manifest.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(man, fh, indent=1, ensure_ascii=False); fh.write('\n')

    def opts(items):
        return ''.join('<option value="%s"%s>%s</option>' % (e(i['id']), ' selected' if i.get('default') else '', e(i['short'])) for i in items)
    def speeds(items, default):
        return ''.join('<button type="button" class="rp-btn" data-speed="%s" aria-pressed="%s" aria-label="Playback speed %s times">%sx</button>'
                       % (s, 'true' if s == default else 'false', s, s) for s in items)
    def transport(p, spds, dflt):
        events = ('<button type="button" class="rp-btn" id="rp-f-prev">Previous event</button>'
                  '<button type="button" class="rp-btn" id="rp-f-next">Next event</button>') if p == 'f' else ''
        return ('<div class="rp-transport">'
                '<button type="button" class="rp-btn rp-play" id="rp-%s-play">Play</button>%s'
                '<span class="rp-speeds" role="group" aria-label="Playback speed">%s</span>'
                '<span class="rp-time" id="rp-%s-time" aria-live="off">t = 0 s</span></div>' % (p, events, speeds(spds, dflt), p))
    def stagebar(p):
        return ('<div class="rp-stagebar"><p class="rp-over" id="rp-%s-over"></p>'
                '<p class="rp-hint">Drag to orbit, scroll or pinch to zoom.</p>'
                '<button type="button" class="rp-btn" id="rp-%s-reset">Reset view</button></div>' % (p, p))

    fl_default = next(i for i in flight if i['default'])
    htm = f'''
  <h3 class="ds-h2" id="sims-replay">Replays of the recorded runs</h3>
  <p class="use"><b>{LABEL}</b> Three replays of the files in {link(SRC_REL, 'qp/A/sims3d/out')}: the flight runs (take-off, transition, cruise), the ten landing cases and the elevon linkage sweep. Nothing is recomputed in your browser, and the pass lines are the ones in the tables below. The 3-D model is loaded once and shared by the first two replays.</p>
  <noscript><p class="use">The replays need JavaScript.</p></noscript>

  <h3 class="ds-h2" id="sims-replay-flight">Flight replay</h3>
  <p class="sh-v" id="rp-f-verdict">Loads the recorded run to give the verdict.</p>
  <section class="rp" id="rp-flight" aria-label="Flight replay">
    <div class="rp-bar"><label class="rp-pick">Run <select id="rp-f-case" aria-label="Flight run">{opts(flight)}</select></label></div>
    <p class="rp-src">Source: {link(SRC_REL + fl_default['file'], 'flight_*.json')}, one file per run.</p>
    <div class="rp-main">
      <div class="rp-left">
        <div class="rp-stage"><canvas id="rp-f-canvas" role="img" aria-label="3-D replay of the aircraft in flight"></canvas><div class="rp-msg" id="rp-f-msg">Loads when this section is in view.</div></div>
        {stagebar('f')}
        {transport('f', (0.5, 1, 2, 5, 10), 1)}
        <div class="rp-sliderwrap"><input type="range" class="rp-slider" id="rp-f-slider" min="0" max="1" step="0.1" value="0" aria-label="Flight time, seconds"><div class="rp-ticks" id="rp-f-ticks" aria-hidden="true"></div></div>
        <div class="rp-key" id="rp-f-key" aria-hidden="true"></div>
        <div class="rp-chips" id="rp-f-marks" role="group" aria-label="Timeline: events and autopilot modes"></div>
        <p class="rp-cap">Keyboard: the slider moves through the run and every plot follows it; a click or drag on a plot also moves it. Timeline: each autopilot mode is one entry on the simulation clock. An event with no mode entry (marked &dagger;) comes from the test driver&rsquo;s clock and sits about 0.1&ndash;0.4 s off the slider, so do not read sub-second alignment from it. Propeller spin is a visual cue (rate follows the square root of thrust, capped), not the real rpm. Attitude: pitch is drawn exactly; roll and heading are not defined near hover, so they are held at their last valid value above 80&deg; pitch.</p>
      </div>
      <div class="rp-right">
        <div class="rp-read" id="rp-f-read" aria-live="off"></div>
      </div>
    </div>
    <div class="rp-pf" id="rp-f-pf"></div>
    <div class="rp-plots" id="rp-f-plots"></div>
  </section>

  <h3 class="ds-h2" id="sims-replay-landing">Landing replay</h3>
  <p class="sh-v" id="rp-l-verdict">Loads the recorded case to give the verdict.</p>
  <section class="rp" id="rp-landing" aria-label="Landing replay">
    <div class="rp-bar"><label class="rp-pick">Case <select id="rp-l-case" aria-label="Landing case">{opts(landing)}</select></label></div>
    <p class="rp-src">Source: {link(SRC_REL + landing[0]['file'], 'landing_*.json')}, one file per case (foam 37.5 N, damping 0.05, T-098 basis).</p>
    <div class="rp-main">
      <div class="rp-left">
        <div class="rp-stage"><canvas id="rp-l-canvas" role="img" aria-label="3-D replay of the aircraft landing"></canvas><div class="rp-msg" id="rp-l-msg">Loads when this section is in view.</div></div>
        {stagebar('l')}
        {transport('l', (0.1, 0.5, 1), 0.1)}
        <div class="rp-sliderwrap"><input type="range" class="rp-slider" id="rp-l-slider" min="0" max="1" step="0.005" value="0" aria-label="Landing time, seconds"></div>
        <div class="rp-key" id="rp-l-key" aria-hidden="true"></div>
        <p class="rp-cap">The aircraft stands on its fin feet (nose up). Pads: UR and LR are the right-side feet, upper and lower in the cruise frame; UL and LL are the left-side feet. Each pad is labelled on the 3-D and drawn shortened by its recorded crush. The 3-D motion is the recorded rigid-body pose at 200 Hz. The limits are the T-098 ones. Keyboard: the slider moves through the case and the plots follow it.</p>
      </div>
      <div class="rp-right"><div class="rp-read" id="rp-l-read" aria-live="off"></div></div>
    </div>
    <div class="rp-plots" id="rp-l-plots"></div>
  </section>

  <h3 class="ds-h2" id="sims-replay-linkage">Linkage sweep</h3>
  <p class="sh-v" id="rp-k-verdict">Loads the linkage file to give the readings.</p>
  <section class="rp" id="rp-linkage" aria-label="Elevon linkage sweep">
    <p class="rp-src">Source: {link(SRC_REL + 'linkage.json')}, one file, no 3-D model.</p>
    <p class="use">The servo arm, pushrod and control horn for every elevon angle in the file. Every number on this panel is read from the file when the page opens, so it follows the file when it is re-exported.</p>
    <div class="rp-main">
      <div class="rp-left">
        <div class="rp-bar"><span class="rp-speeds" role="group" aria-label="Elevon side"><button type="button" class="rp-btn" data-side="R" aria-pressed="true">Right elevon</button><button type="button" class="rp-btn" data-side="L" aria-pressed="false">Left elevon</button></span></div>
        <div class="rp-svgs"><figure><div id="rp-k-top" class="rp-svg" role="img" aria-label="Top view of the servo arm and pushrod"></div><figcaption>Top view (x aft, y span): servo arm and pushrod</figcaption></figure>
        <figure><div id="rp-k-side" class="rp-svg" role="img" aria-label="Side view of the control horn and hinge"></div><figcaption>Side view (x aft, z up): hinge and horn; elevon chord not to scale</figcaption></figure></div>
        <div class="rp-transport"><button type="button" class="rp-btn rp-play" id="rp-k-play">Sweep</button><span class="rp-time" id="rp-k-time"></span></div>
        <div class="rp-sliderwrap"><input type="range" class="rp-slider" id="rp-k-slider" min="-1" max="1" step="0.5" value="0" aria-label="Elevon angle, degrees, trailing edge down positive"></div>
        <div class="rp-key" id="rp-k-key" aria-hidden="true"></div>
        <p class="rp-cap">Keyboard: the slider sets the elevon angle. Sweep runs back and forth over the range (one pass when reduced motion is on).</p>
      </div>
      <div class="rp-right"><div class="rp-read" id="rp-k-read" aria-live="off"></div><p class="rp-cap" id="rp-k-cap"></p></div>
    </div>
    <div class="rp-plots" id="rp-k-plots"></div>
  </section>
'''
    return htm, man

if __name__ == '__main__':
    h, m = build()
    print('replays: %d flight, %d landing, total %.1f KB' % (len(m['flight']), len(m['landing']), m['total_kb']))
