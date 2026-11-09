"""Tests for fusionkit, check.py and merge_check.py.  Run:  python -I redesign/fusion/tests/test_framework.py

1. the generic example aircraft passes check.py and merge_check.py with --strict;
2. the deliberately broken aircraft (tests/broken/) fails, and each planted defect is reported;
3. geometry helpers (NACA thickness, volumes, mirror) are right.
"""
import contextlib
import io
import math
import os
import sys
import unittest

FUSION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FUSION)

import check            # noqa: E402  (adds redesign/interfaces to sys.path)
import build_all        # noqa: E402
import fusionkit as fk  # noqa: E402
import merge_check      # noqa: E402

EXAMPLES = os.path.join(FUSION, 'examples')
BROKEN = os.path.join(FUSION, 'tests', 'broken')


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        r = fn(*a, **k)
    return r, out.getvalue()


class Examples(unittest.TestCase):
    def test_check_passes_strict(self):
        code, out = quiet(check.main, ['--examples', '--strict'])
        self.assertEqual(code, 0, out)
        self.assertIn('check: PASS', out)

    def test_merge_passes_strict(self):
        g = quiet(merge_check.run, EXAMPLES, None, os.path.join(EXAMPLES, 'mass_budget.json'), True)[0]
        self.assertEqual(g.issues, [])
        self.assertEqual((len(g.parts), len(g.edges)), (12, 15))

    def test_rollup_and_counts(self):
        ctx, _, results = quiet(build_all.build, __import__('backends.stub_backend', fromlist=['x']).StubBackend(),
                                *build_all.roots(True))[0]
        self.assertTrue(all(r[2] for r in results))
        M, cg = ctx.rollup()
        self.assertAlmostEqual(M, 1470.0)
        self.assertTrue(0.18 <= cg[0] <= 0.24)
        self.assertEqual(sorted(ctx.registrations()), sorted(merge_check.load(EXAMPLES).edges))


class Broken(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx, cls.results, cls.issues = quiet(check.run_checks, BROKEN, os.path.join(BROKEN, 'modules.txt'))[0]

    def has(self, sev, code, item, text=''):
        hits = [i for i in self.issues if i[0] == sev and i[1] == code and item in str(i[2]) and text in i[3]]
        self.assertTrue(hits, 'expected %s %s %s %r; got:\n%s' % (sev, code, item, text,
                                                                  '\n'.join(map(str, self.issues))))

    def test_exit_codes(self):
        self.assertEqual(quiet(check.main, ['--root', BROKEN])[0], 1)
        self.assertEqual(quiet(merge_check.main, ['--root', BROKEN])[0], 1)

    def test_module_crash(self):
        self.has('ERROR', 'module', 'bk_crash', 'ZeroDivisionError')

    def test_part_defects(self):
        self.has('ERROR', 'part', 'BRK-002', 'no material')
        self.has('ERROR', 'missing', 'BRK-006', 'MODELLED')
        self.has('WARN', 'missing', 'BRK-004', 'PROPOSED')

    def test_floating(self):
        self.has('ERROR', 'floating', 'BRK-003')
        self.has('WARN', 'graph:floating', 'BRK-003')

    def test_registration_and_touch(self):
        self.has('ERROR', 'register', 'E-BRK-03', 'no joint/contact/wire')
        self.has('ERROR', 'register', 'E-BRK-99', 'no interfaces.json declares')
        self.has('ERROR', 'touch', 'E-BRK-01', '10.0 mm apart')

    def test_graph_defects(self):
        self.has('ERROR', 'graph:dangling', 'E-BRK-02', 'BRK-999')
        self.has('ERROR', 'graph:duplicate', 'BRK-007')
        self.has('ERROR', 'graph:joint-stack', 'E-BRK-01', 'torque')
        self.has('ERROR', 'graph:joint-stack', 'E-BRK-01', 'engagement 2.0 mm < minimum 4.5 mm')
        self.has('ERROR', 'graph:joint-stack', 'E-BRK-05', 'fastener')
        self.has('WARN', 'graph:one-sided', 'E-BRK-04')
        self.has('WARN', 'graph:unconnected', 'BRK-004')


class Geometry(unittest.TestCase):
    def test_naca_thickness(self):
        t = max(fk.naca4_line('0012', i / 100.0)[1] for i in range(101)) * 2
        self.assertAlmostEqual(t, 0.12, places=3)
        self.assertAlmostEqual(fk.naca4_line('2412', 0.4)[0], 0.02, places=6)   # max camber at p

    def test_volumes(self):
        ctx = fk.Context(fk.Backend())
        ctx.sub = 't'
        c = ctx.part('T-1')
        c.box((0, 0, 0), (0.1, 0.2, 0.3))
        self.assertAlmostEqual(c.volume_centroid()[0], 0.006)
        self.assertEqual(tuple(round(v, 9) for v in c.volume_centroid()[1]), (0.05, 0.1, 0.15))
        d = ctx.part('T-2')
        d.tube('X', (0, 0, 0), 1.0, 0.01, 0.008)
        self.assertAlmostEqual(d.volume_centroid()[0], math.pi * (0.01 ** 2 - 0.008 ** 2), places=9)
        e = ctx.part('T-3')
        e.prism('X', 0, [[(-1, -1), (1, -1), (1, 1), (-1, 1)], [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]], 2)
        self.assertAlmostEqual(e.volume_centroid()[0], 6.0)

    def test_mirror_and_rotation(self):
        ctx = fk.Context(fk.Backend())
        ctx.sub = 't'
        a = ctx.part('M-1', at=(0, 0.5, 0))
        a.loft('Y', [(0.1, fk.airfoil('2412', 0.2)), (0.4, fk.airfoil('2412', 0.1))])
        b = ctx.mirror('M-1', 'M-2', plane='XZ')
        (lo1, hi1), (lo2, hi2) = a.bbox(), b.bbox()
        self.assertAlmostEqual(lo2[1], -hi1[1])
        self.assertAlmostEqual(hi2[1], -lo1[1])
        self.assertAlmostEqual(a.volume_centroid()[0], b.volume_centroid()[0])
        r = ctx.part('R-1', at=(1, 0, 0), rotate=('Z', 90))
        r.box((0, 0, 0), (0.2, 0.1, 0.1))
        lo, hi = r.bbox()
        self.assertAlmostEqual(lo[0], 0.9)
        self.assertAlmostEqual(hi[1], 0.2)


class _Any:
    """Stands in for every adsk object: any attribute, call, arithmetic or comparison works. Lets the Fusion
    backend's Python run end to end outside Fusion. It proves no Python-level mistakes (names, arguments,
    arithmetic, control flow); it proves nothing about Fusion's real API behaviour (UNVERIFIED-IN-FUSION)."""

    def __getattr__(self, n):
        if n.startswith('__'):
            raise AttributeError(n)
        return _Any()

    def __call__(self, *a, **k):
        return _Any()

    def __iter__(self):
        return iter([_Any()])

    def _op(self, *a):
        return _Any()
    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __truediv__ = __neg__ = _op

    def __gt__(self, o):
        return True
    __lt__ = __ge__ = __le__ = __gt__

    def __float__(self):
        return 1.0

    def __index__(self):
        return 1


class FusionBackendSmoke(unittest.TestCase):
    def test_runs_examples_with_fake_adsk(self):
        import types
        saved = {k: sys.modules.get(k) for k in ('adsk', 'adsk.core', 'adsk.fusion', 'backends.fusion_backend')}
        adsk = types.ModuleType('adsk')
        adsk.core, adsk.fusion = _Any(), _Any()
        sys.modules.update({'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
        sys.modules.pop('backends.fusion_backend', None)
        try:
            from backends.fusion_backend import FusionBackend
            ctx, _, results = quiet(build_all.build, FusionBackend(), *build_all.roots(True))[0]
            self.assertTrue(all(r[2] for r in results), results)
            self.assertEqual([i for i in ctx.issues if i[0] == 'ERROR'], [])
            self.assertTrue(all(j.native is not None for j in ctx.joints))
            self.assertTrue(all(w.native is not None for w in ctx.wires))
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v


if __name__ == '__main__':
    unittest.main(verbosity=1)
