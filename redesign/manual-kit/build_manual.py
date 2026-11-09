"""build_manual.py - the build manual from every subsystem's steps.json + parts.csv + interfaces.json.

    python -I redesign/manual-kit/build_manual.py --examples            # the generic example aircraft (demo)
    python -I redesign/manual-kit/build_manual.py                       # the real aircraft: redesign/subsystems/*/steps.json
    python -I redesign/manual-kit/build_manual.py --examples --check    # validate only (< 1 s, no Blender)

Options: --src DIR (folders with steps.json)  --interfaces DIR (folders with interfaces.json, default = --src)
         --manual FILE (manual.json)  --out DIR  --no-render (use the figures already there)  --force (re-render all)
         --draft (16 samples, half size: ~3 s per figure)  --samples N  --blender EXE (or env DBF_BLENDER)
         --strict (warnings fail too)
Output (default redesign/manual-kit/out/<examples|aircraft>/): manual.html, MANUAL.md, kitting.csv, tools.csv, img/.
Only missing or changed figures are rendered (img/figures.lock.json). Exit 1 on any error.
"""
import argparse
import html.parser
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)            # python -I leaves the script folder off sys.path

import figures as F                 # noqa: E402
import html_out                     # noqa: E402
import md_out                       # noqa: E402
import steps_lib as L               # noqa: E402

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr',
        'path', 'circle', 'rect', 'line', 'use', 'image'}


class Lint(html.parser.HTMLParser):
    """Structure check of the generated page: balanced tags, unique ids, local images exist, one card per step."""

    def __init__(self, base):
        super().__init__()
        self.base, self.stack, self.ids, self.problems = base, [], set(), []
        self.cards, self.imgs, self.anchors = 0, 0, set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                self.problems.append('duplicate id %s' % a['id'])
            self.ids.add(a['id'])
        if tag == 'article' and 'step' in (a.get('class') or '').split():
            self.cards += 1
        if tag == 'img' and a.get('src') and not a['src'].startswith(('http', 'data:')):
            self.imgs += 1
            if not os.path.exists(os.path.join(self.base, a['src'])):
                self.problems.append('missing image %s' % a['src'])
        if tag == 'a' and (a.get('href') or '').startswith('#') and len(a['href']) > 1:
            self.anchors.add(a['href'][1:])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.problems.append('unbalanced </%s> (open: %s)' % (tag, '/'.join(self.stack[-4:])))
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass


def lint(path, n_steps):
    p = Lint(os.path.dirname(path))
    with open(path, encoding='utf-8') as f:
        p.feed(f.read())
    probs = list(p.problems)
    open_tags = [t for t in p.stack if t not in ('html', 'body', 'head')]
    if open_tags:
        probs.append('unclosed tags: ' + ' '.join(open_tags[-6:]))
    if p.cards != n_steps:
        probs.append('%d step cards for %d steps' % (p.cards, n_steps))
    probs += ['link to missing #%s' % a for a in sorted(p.anchors - p.ids)]
    return probs, p


def args():
    ap = argparse.ArgumentParser(prog='build_manual.py', description=__doc__.split('\n')[0])
    ap.add_argument('--examples', action='store_true')
    ap.add_argument('--src')
    ap.add_argument('--interfaces')
    ap.add_argument('--manual')
    ap.add_argument('--out')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--draft', action='store_true')
    ap.add_argument('--samples', type=int)
    ap.add_argument('--blender')
    ap.add_argument('--strict', action='store_true')
    return ap.parse_args()


def main():
    a = args()
    t0 = time.time()
    if a.examples:
        src = a.src or os.path.join(HERE, 'examples')
        ifaces = a.interfaces or os.path.join(L.REDESIGN, 'fusion', 'examples')
        out = a.out or os.path.join(HERE, 'out', 'examples')
    else:
        src = a.src or os.path.join(L.REDESIGN, 'subsystems')
        ifaces = a.interfaces or src
        out = a.out or os.path.join(HERE, 'out', 'aircraft')
    if not os.path.isdir(src):
        print('nothing to build: no folder %s (no subsystem has written steps.json yet)' % src)
        return 0
    m = L.Manual(src, ifaces, a.manual)
    print('%d steps in %d work packages from %s' % (len(m.steps), len(m.wps), ', '.join(m.subsystems) or 'nothing'))
    for e in m.errors:
        print('ERROR   ' + e)
    for w in m.warnings:
        print('warning ' + w)
    if m.errors or (a.strict and m.warnings):
        print('FAIL: %d errors, %d warnings' % (len(m.errors), len(m.warnings)))
        return 1
    if a.check:
        print('OK: %d errors, %d warnings (%.2f s)' % (len(m.errors), len(m.warnings), time.time() - t0))
        return 0

    # ---- figures: render what is missing or changed, then place the numbered dots
    img = os.path.join(out, 'img')
    os.makedirs(img, exist_ok=True)
    quality = {'samples': a.samples or (16 if a.draft else 48), 'percent': 50 if a.draft else 100}
    specs = F.plan(m)
    fp = F.fingerprint(m)
    todo = F.stale(specs, img, fp, quality, a.force)
    if todo and not a.no_render:
        ok, dt = F.render(todo, img, fp, quality, a.examples, None if a.examples or ifaces == os.path.join(
            L.REDESIGN, 'subsystems') else ifaces, a.blender)
        print('figures: %d rendered in %.0f s%s' % (len(todo), dt, '' if ok else ' (SOME FAILED)'))
    elif todo:
        print('figures: %d missing or out of date (--no-render)' % len(todo))
    else:
        print('figures: all %d up to date' % len(specs))
    figinfo, problems, nwarn = {}, [], len(m.warnings)
    for s in m.steps:
        for f in s['figures']:
            sc = F.sidecar(img, f['id'])
            mks, miss = F.markers(sc, s)
            figinfo[f['id']] = {'sc': sc, 'markers': mks, 'missing': miss if f is s['figures'][0] else [],
                                'svg': F.numbered_svg(img, f['id'], mks, f['caption']['title'])}
            if not sc:
                problems.append('%s: figure %s not rendered' % (s['id'], f['id']))
                continue
            if sc.get('clipped'):
                m.warn(f['id'], 'parts cut off by the image edge: ' + ', '.join(sc['clipped']))
            if miss and f is s['figures'][0]:
                m.warn(s['id'], 'action %s points at something not visible in the figure' % ', '.join(map(str, miss)))
    for w in m.warnings[nwarn:]:
        print('warning ' + w)
    overview = {'gallery': []}
    for f in m.meta.get('figures', []):
        svg = os.path.join(img, f['id'] + '.svg')
        if not os.path.exists(svg):
            problems.append('overview figure %s not rendered' % f['id'])
            continue
        g = {'file': f['id'] + '.svg', 'cap': (f.get('caption') or {}).get('title', f['id'])}
        if f['id'] == 'cover' and 'cover' not in overview:
            overview['cover'] = g
        else:
            overview['gallery'].append(g)

    # ---- write the manual
    terms = L.glossary(m)
    page = html_out.page(m, figinfo, terms, overview)
    hp = os.path.join(out, 'manual.html')
    with open(hp, 'w', encoding='utf-8') as f:
        f.write(page)
    md_out.write(m, out, figinfo, terms, overview)
    probs, lp = lint(hp, len(m.steps))
    problems += probs
    for p in problems:
        print('PROBLEM ' + p)
    print('wrote %s (%d kB, %d step cards, %d images), MANUAL.md, kitting.csv, tools.csv; %d glossary terms'
          % (os.path.relpath(hp), os.path.getsize(hp) // 1024, lp.cards, lp.imgs, len(terms)))
    print('%s in %.1f s' % ('FAIL' if problems else 'OK', time.time() - t0))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
