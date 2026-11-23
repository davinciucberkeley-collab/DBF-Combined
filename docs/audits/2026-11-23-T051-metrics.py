"""T-051 model-usage statistics. Run: python -I docs/audits/2026-11-23-T051-metrics.py
Parses the table rows of docs/model-usage.md (columns: Date | Task | Agent / model | Complexity | Outcome |
Usage | Retries | Escalation | Review). A row is a delegated task or task batch; one row can cover several T-ids.
Rows whose Usage cell has no 'N k tok / N min' numbers are counted separately (never imputed)."""
import re, sys, statistics as st, collections, pathlib
sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(__file__).resolve().parents[2]
rows = []
for l in (root / 'docs/model-usage.md').read_text(encoding='utf8').splitlines():
    if not l.startswith('| 20'):
        continue
    p = [x.strip() for x in l.strip().strip('|').split('|')]
    if len(p) != 9:
        print('SKIP malformed', l[:80]); continue
    date, task, am, cx, out, usage, retries, esc, rev = p
    m = re.fullmatch(r'([\d.,]+) k tok / ([\d.]+) min', usage)
    tok = float(m.group(1).replace(',', '')) * 1000 if m else None
    mn = float(m.group(2)) if m else None
    agent, _, model = am.partition(' / ')
    if not model:                      # 'conductor (no model; Blender background)'
        model = 'none'
    resumed = 'resumed' in am
    override = 'override' in am
    model = re.split(r'[ (]', model)[0]
    r = re.match(r'(\d+)', retries)
    rows.append(dict(date=date, task=task, agent=agent, model=model, tok=tok, min=mn,
                     retries=int(r.group(1)) if r else None, esc=esc not in ('—', ''),
                     resumed=resumed, override=override))

def stats(v):
    if not v: return 'n=0'
    return f'n={len(v)} total={sum(v):,.1f} mean={st.mean(v):,.1f} median={st.median(v):,.1f} min={min(v):,.1f} max={max(v):,.1f}'

def block(title, keyf):
    print(f'\n### {title}\n')
    print('| Group | Rows | With numbers | No numbers | Tokens total (k) | Tokens mean (k) | Tokens median (k) | Minutes total | Minutes mean | Minutes median |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    g = collections.defaultdict(list)
    for r in rows: g[keyf(r)].append(r)
    for k in sorted(g, key=lambda k: -len(g[k])):
        rs = g[k]; t = [r['tok'] / 1000 for r in rs if r['tok'] is not None]; m = [r['min'] for r in rs if r['min'] is not None]
        f = lambda v, fn: f'{fn(v):,.1f}' if v else '—'
        print(f'| {k} | {len(rs)} | {len(t)} | {len(rs)-len(t)} | {f(t,sum)} | {f(t,st.mean)} | {f(t,st.median)} | {f(m,sum)} | {f(m,st.mean)} | {f(m,st.median)} |')

print('rows', len(rows), 'with numbers', sum(r['tok'] is not None for r in rows), 'without', sum(r['tok'] is None for r in rows))
print('dates', min(r['date'] for r in rows), 'to', max(r['date'] for r in rows))
t = [r['tok'] / 1000 for r in rows if r['tok'] is not None]; m = [r['min'] for r in rows if r['min'] is not None]
print('ALL tokens (k):', stats(t)); print('ALL minutes:', stats(m))
print('tokens per minute (rows with both): mean', round(st.mean([r['tok']/1000/r['min'] for r in rows if r['tok'] and r['min']]), 1), 'k/min')
block('By model', lambda r: r['model'])
block('By agent type', lambda r: r['agent'])
block('By agent type / model', lambda r: f"{r['agent']} / {r['model']}")
block('By date', lambda r: r['date'])
print('\n### Reruns (Retries column)\n')
rec = [r for r in rows if r['retries'] is not None]
print('rows with a recorded retries value:', len(rec), '; not recorded ("—"):', len(rows) - len(rec))
print('rows with retries > 0:', sum(r['retries'] > 0 for r in rec), '; total retries:', sum(r['retries'] for r in rec))
print('rerun rate over recorded rows: %.1f %%' % (100 * sum(r['retries'] > 0 for r in rec) / len(rec)))
for r in rows:
    if r['retries']: print('  retry>0:', r['date'], r['agent'], '/', r['model'], '|', r['task'][:70], '| retries', r['retries'])
print('rows with an escalation entry:', sum(r['esc'] for r in rows))
for r in rows:
    if r['esc']: print('  escalation:', r['date'], r['agent'], '/', r['model'], '|', r['task'][:70])
print('rows with resumed agent:', sum(r['resumed'] for r in rows), '; model override rows:', sum(r['override'] for r in rows))
