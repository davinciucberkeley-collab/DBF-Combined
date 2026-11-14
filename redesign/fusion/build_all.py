"""build_all.py - build the whole aircraft from every subsystem module, in a fixed order.

Discovers <root>/<subsystem>/fusion/*.py (root = redesign/subsystems; redesign/fusion/skeleton with --skeleton = the
K09-L reference layout; redesign/fusion/examples with --examples = the generic test aircraft),
orders them by <list file> (redesign/fusion/modules.txt or examples/modules.txt; unlisted modules go last,
alphabetically, with a warning), calls each module's build(ctx), then creates all joints and wires, then prints
mass and CG (declared masses; CG declared or, if absent, geometric centroid). For the K09-L roots (subsystems,
skeleton) the datum sheet (k09kit.build_datums, DATUMS.md) is registered before the first module, so modules can
read ctx.D('DP-SPAR') and Fusion shows a '00 Datums' component.

Outside Fusion (stub backend, for checks):
    python -I redesign/fusion/build_all.py [--skeleton | --examples | --root DIR]
Inside Fusion: run the launcher redesign/fusion/BuildAll/ from Utilities > Add-Ins > Scripts and Add-Ins
(see README.md). It calls fusion_main() below. TARGET picks what is built.
"""
import argparse
import importlib.util
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
for p in (HERE, os.path.join(REDESIGN, 'interfaces')):
    if p not in sys.path:
        sys.path.insert(0, p)

import fusionkit                 # noqa: E402
import merge_check               # noqa: E402

# Inside Fusion: 'auto' builds redesign/subsystems if any module exists there, else the K09-L skeleton.
TARGET = 'auto'                  # 'auto' | 'subsystems' | 'skeleton' | 'examples'


def roots(examples=False, root=None, skeleton=False):
    """(module root, list file) for a build."""
    if root:
        root = os.path.abspath(root)
        return root, os.path.join(root, 'modules.txt')
    if examples or skeleton:
        r = os.path.join(HERE, 'examples' if examples else 'skeleton')
        return r, os.path.join(r, 'modules.txt')
    return os.path.join(REDESIGN, 'subsystems'), os.path.join(HERE, 'modules.txt')


def wants_datums(root):
    """K09-L datums for redesign/subsystems and the skeleton; not for the generic examples or test roots."""
    n = os.path.normcase(os.path.abspath(root))
    return n in (os.path.normcase(os.path.join(REDESIGN, 'subsystems')), os.path.normcase(os.path.join(HERE, 'skeleton')))


def discover(root, list_file):
    """Ordered [(subsystem, module path)], warnings (unlisted modules), notes (listed names with no module yet)."""
    found = {}
    for sub in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        fdir = os.path.join(root, sub, 'fusion')
        if os.path.isdir(fdir):
            for f in sorted(os.listdir(fdir)):
                if f.endswith('.py') and not f.startswith('_'):
                    found.setdefault(sub, []).append(os.path.join(fdir, f))
    order, warns, notes = [], [], []
    if os.path.exists(list_file):
        with open(list_file, encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            name = line.split('#')[0].strip()
            if name:
                order.append(name)
    out = []
    for name in order:
        if name in found:
            out += [(name, p) for p in found.pop(name)]
        else:
            notes.append(name)
    for name in sorted(found):
        warns.append('module %s not in %s; built last' % (name, os.path.basename(list_file)))
        out += [(name, p) for p in found[name]]
    return out, warns, notes


def load_params():
    path = os.path.join(REDESIGN, 'params', 'params.json')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}


SEAT_WILD = {'<st>': ('UR', 'UL', 'LR', 'LL'), '<s>': ('R', 'L')}


def load_seats(ctx, root):
    """interfaces/seats.json (next to the module root): parts machined to receive another part (Context.seat).
    '<st>' expands to the four stations, '<s>' to R and L, the same in host and guest."""
    path = os.path.join(os.path.dirname(os.path.abspath(root)), 'interfaces', 'seats.json')
    if not os.path.exists(path):
        return
    with open(path, encoding='utf-8') as f:
        rows = json.load(f).get('seats', [])
    for r in rows:
        keys = [k for k in SEAT_WILD if k in r['host'] + r['guest']] or [None]
        vals = SEAT_WILD[keys[0]] if keys[0] else (None,)
        for v in vals:
            h, g = (r['host'], r['guest']) if v is None else (r['host'].replace(keys[0], v), r['guest'].replace(keys[0], v))
            if g not in ctx.components:
                continue
            ctx.seat(h, g, r.get('why', ''), r.get('bodies'), r.get('shop', False))


def build(backend, root, list_file, log=print, datums=None):
    """Run every module against `backend`. Returns (ctx, graph, results); results = [(sub, file, ok, ms, err)].
    datums: True/False registers the K09-L datum sheet first; None = wants_datums(root)."""
    graph = merge_check.load(root)
    ctx = fusionkit.Context(backend, parts=graph.parts, params=load_params())
    mods, warns, notes = discover(root, list_file)
    for w in warns:
        ctx.issue('WARN', 'modules', '-', w)
    if notes:
        log('not built yet (listed in %s, no module): %s' % (os.path.basename(list_file), ', '.join(notes)))
    backend.begin('DBF redesign - %s' % os.path.basename(root))
    if wants_datums(root) if datums is None else datums:
        try:
            import k09kit
            k09kit.build_datums(ctx)
        except Exception as e:
            ctx.issue('ERROR', 'datums', '-', 'k09kit.build_datums: %s: %s' % (type(e).__name__, e))
    results = []
    for sub, path in mods:
        t0 = time.time()
        ctx.begin_module(sub, os.path.dirname(os.path.dirname(path)))
        try:
            name = 'dbfmod_%s_%s' % (sub, os.path.splitext(os.path.basename(path))[0])
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            if not hasattr(mod, 'build'):
                raise AttributeError('module has no build(ctx)')
            mod.build(ctx)
            results.append((sub, os.path.basename(path), True, (time.time() - t0) * 1000, ''))
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            where = next(('%s:%d' % (os.path.basename(f.filename), f.lineno) for f in reversed(tb)
                          if os.path.normcase(os.path.abspath(f.filename)) == os.path.normcase(path)), '')
            msg = '%s: %s %s' % (type(e).__name__, e, ('at ' + where) if where else '')
            ctx.issue('ERROR', 'module', sub, msg)
            results.append((sub, os.path.basename(path), False, (time.time() - t0) * 1000, msg))
    load_seats(ctx, root)
    ctx.finish()
    summary = backend.end(ctx)
    if summary:
        log(summary)
    return ctx, graph, results


def mass_table(ctx):
    """Lines: mass and CG per subsystem and total (declared mass; CG declared else geometric)."""
    subs = {}
    for c in ctx.components.values():
        cg, src = c.cg()
        s = subs.setdefault(c.subsystem, [0.0, [0.0] * 3, 0])
        s[2] += 1
        if c.mass_g and cg:
            s[0] += c.mass_g
            s[1] = [s[1][i] + c.mass_g * cg[i] for i in range(3)]
    lines = ['%-14s %5s %9s   %s' % ('subsystem', 'parts', 'mass g', 'CG x, y, z m')]
    for name, (m, mc, n) in sorted(subs.items()):
        cg = ', '.join('%.3f' % (v / m) for v in mc) if m else '-'
        lines.append('%-14s %5d %9.0f   %s' % (name, n, m, cg))
    M, cg = ctx.rollup()
    lines.append('%-14s %5d %9.0f   %s' % ('TOTAL', len(ctx.components), M,
                                          ', '.join('%.3f' % v for v in cg) if cg else '-'))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description='Build all subsystem modules on the stub backend (outside Fusion).')
    ap.add_argument('--examples', action='store_true')
    ap.add_argument('--skeleton', action='store_true')
    ap.add_argument('--root')
    a = ap.parse_args(argv)
    from backends.stub_backend import StubBackend
    root, lst = roots(a.examples, a.root, a.skeleton)
    ctx, _, results = build(StubBackend(), root, lst)
    for sub, f, ok, ms, err in results:
        print('%-14s %-18s %s %6.1f ms %s' % (sub, f, 'ok  ' if ok else 'FAIL', ms, err))
    print('\n'.join(mass_table(ctx)))
    return 0 if all(r[2] for r in results) else 1


def fusion_main():
    """Entry point inside Fusion. Returns the text shown in the message box."""
    from backends.fusion_backend import FusionBackend
    target = TARGET
    if target == 'auto':
        target = 'subsystems' if discover(*roots(False))[0] else 'skeleton'
    root, lst = roots(target == 'examples', skeleton=target == 'skeleton')
    out = []
    ctx, _, results = build(FusionBackend(), root, lst, log=out.append)
    lines = ['Built %s: %d modules, %d components, %d joints, %d wires, %d datums' % (
        target, len(results), len(ctx.components), len(ctx.joints), len(ctx.wires), len(ctx.datums))]
    lines += ['%s/%s: %s' % (s, f, 'ok' if ok else err) for s, f, ok, _, err in results]
    lines += [i[0] + ' ' + i[2] + ': ' + i[3] for i in ctx.issues]
    lines += mass_table(ctx) + out
    text = '\n'.join(lines)
    print(text)                  # Fusion: TEXT COMMANDS window
    return text


def run(context):                # lets Fusion run this file directly if it is ever added as a script
    import adsk.core
    ui = adsk.core.Application.get().userInterface
    try:
        ui.messageBox(fusion_main()[:3000])
    except Exception:
        ui.messageBox('build_all failed:\n' + traceback.format_exc())


if __name__ == '__main__':
    sys.exit(main())
