import json, sys, copy, importlib.util
R = r'C:\Users\dillo\Downloads\Berkeley\Fall\Capstone\DBF-Combined\redesign\showcase\concept-a'
spec = importlib.util.spec_from_file_location('rba', R + r'\render_build_a.py')
rba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rba)
FM = R + r'\film\shots-main.json'
FH = R + r'\film\shots-highlight.json'
OLDM = sys.argv[1]
film_new = rba.load_film(FM)
film_old = rba.load_film(OLDM)
raw = open(FH, encoding='utf-8', newline='').read()
crlf = '\r\n' in raw
h = json.loads(raw)
m = json.load(open(FM, encoding='utf-8'))
M = {s['id']: s for s in m['scenes']}


def mshot(i):
    for s in m['scenes']:
        for x in s['shots']:
            if x['id'] == i:
                return x


def sample(film, sid, shid, a, dur):
    S = next(s for s in film['scenes'] if s['id'] == sid)
    sh = next(x for x in S['shots'] if x['id'] == shid)
    out = []
    n = int(round(dur / 0.25))
    for k in range(n + 1):
        t = round(k * 0.25, 4)
        c = rba.hermite_cam(S['keys'], sh['t0'] + a + t)
        out.append({'t': t, 'target': [round(c[0], 5), round(c[1], 5), round(c[2], 5)], 'az': round(c[3], 4), 'el': round(c[4], 4), 'dist': round(c[5], 5)})
    return out


# validation: resampling the OLD film reproduces the stored highlight cameras
for sc in h['scenes']:
    for sh in sc['shots']:
        if sh['id'] == 'H6.1':
            smp = sample(film_old, 'S5', '5.1', sh['src']['a'], sh['dur'])
            err = max(abs(x['az'] - y['az']) + abs(x['el'] - y['el']) + abs(x['dist'] - y['dist']) for x, y in zip(smp, sh['cam']))
            print('sampler check vs stored H6 cam, max abs err', err)
            assert err < 1e-2, err
S = {s['id']: s for s in h['scenes']}
RUN = 'T097_Z5'
NOTE = 'Run of T-097 (AR-015), 1.881 kg EST, X2216, CG 22.049 mm; SITL with the a_plant.py plant (EST aero).'
for sid in ('H3', 'H4', 'H5'):
    for sh in S[sid]['shots']:
        sh['tag'] = 'SIMULATED: ArduPilot SITL run T097_Z5, 1.881 kg EST, a_plant.py plant model (EST aero)'
        sh['sitl']['run'] = RUN
        sh['sitl']['note'] = NOTE
# H6 <- main 5.1 (current hub status), cam resampled from the new path
h6 = S['H6']['shots'][0]
n51 = mshot('5.1')
for k in ('fea', 'vals'):
    h6.pop(k, None)
for k in ('tag', 'title', 'readout', 'modes', 'wires', 'los'):
    h6[k] = copy.deepcopy(n51[k])
h6['sub'] = 'The hub passes in the aluminium-hub FEA; two arm-tube rows stay open.'
h6['cam'] = sample(film_new, 'S5', '5.1', h6['src']['a'], h6['dur'])
# H7 <- main 6.2 card
h7 = S['H7']['shots'][0]
h7['card'] = copy.deepcopy(mshot('6.2')['card'])
out = json.dumps(h, indent=1)
if crlf:
    out = out.replace('\n', '\r\n')
open(FH, 'w', encoding='utf-8', newline='').write(out)
print('highlight written, crlf=%s' % crlf)
