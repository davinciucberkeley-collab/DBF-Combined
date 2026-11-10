"""Tests for fusionkit, check.py and merge_check.py.  Run:  python -I redesign/fusion/tests/test_framework.py

1. the generic example aircraft passes check.py and merge_check.py with --strict;
2. the deliberately broken aircraft (tests/broken/) fails, and each planted defect is reported;
3. geometry helpers (NACA thickness, volumes, mirror) are right;
4. K09-L: the skeleton passes --strict with its datums and keep-outs, k09kit helpers (sections, .dat reader,
   keep-outs, hover pose, DATUMS.md freshness) are right, and the Fusion backend runs the skeleton with a fake adsk.
"""
import contextlib
import io
import json
import math
import os
import sys
import unittest

FUSION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FUSION)

import check            # noqa: E402  (adds redesign/interfaces to sys.path)
import k09kit as k9     # noqa: E402
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


class K09(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.P = k9.load_params()

    def test_skeleton_passes_strict(self):
        code, out = quiet(check.main, ['--skeleton', '--strict'])
        self.assertEqual(code, 0, out)
        self.assertIn('52 datums, 5 keep-outs', out)

    def test_skeleton_rollup_is_the_allocations(self):
        ctx = quiet(check.run_checks, *build_all.roots(skeleton=True))[0][0]
        M, cg = ctx.rollup()
        alloc = sum(k9.val(self.P, 'mass.allocation_g.' + k) for k in
                    ('wing', 'fins', 'pod', 'landing', 'propulsion', 'power', 'avionics', 'harness', 'mechanisms'))
        self.assertAlmostEqual(M, alloc)
        self.assertAlmostEqual(cg[1], 0.0, places=6)               # exact mirrors

    def test_datums_and_stations(self):
        names = [s[0] for s in k9.datum_specs(self.P)]
        self.assertEqual(len(names), len(set(names)))
        d = {s[0]: s[2] for s in k9.datum_specs(self.P)}
        v = lambda k: k9.val(self.P, k)
        self.assertEqual(d['DX-HUB-LL']['p'], (v('propulsion.stations.x_prop_plane_m'), -v('propulsion.stations.y_m'),
                                               -v('propulsion.stations.z_m')))
        self.assertAlmostEqual(d['DP-HINGE']['offset'], v('wing.chord_m') * (1 - v('wing.elevon.chord_frac')))
        self.assertAlmostEqual(d['DX-BLOCK-R']['p'][0], (v('fins.tube.x_m') + v('wing.spar.x_m')) / 2)
        _c, ext, inner = k9.box_frame(self.P)
        self.assertAlmostEqual(ext[1][2] - ext[0][2], v('requirements.box_external_m')[2])
        self.assertEqual(d['DX-BOX']['p'], _c)
        self.assertFalse(k9.datums_md_stale(self.P), 'run python -I redesign/fusion/k09kit.py --datums-md')

    def test_r3_datums_match_the_designers(self):
        # CR-D3-14 / CR-D5-02: DX-COLLAR / DX-ANCHOR are D3's brace ends, DP-MOTOR-FACE D3's plate face (D-28),
        # DX-FOOT the D5 pad contact (CL-D5-CONTACT-Z 0.218) on DP-GROUND (TE + 48 mm)
        import importlib.util
        d = {s[0]: s[2] for s in k9.datum_specs(self.P)}
        v = lambda k: k9.val(self.P, k)
        self.assertAlmostEqual(d['DP-GROUND']['offset'], v('wing.te_x_m') + v('cg.foot_height_m'))
        self.assertAlmostEqual(d['DP-TUBE']['offset'], v('fins.tube.x_m'))
        self.assertAlmostEqual(abs(d['DX-FOOT-LL']['p'][2]), k9.foot_contact_z(self.P))
        path = os.path.join(k9.REDESIGN, 'subsystems', 'fins', 'fusion', 'fins.py')
        if not os.path.exists(path):
            self.skipTest('D3 fins module not published')
        spec = importlib.util.spec_from_file_location('d3_fins_for_test', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        G = mod.geometry(self.P, mod.load_local(), k9.section(self.P)[0])
        for st, upper in (('UR', True), ('LR', False)):
            anc, ear = G['brace_ends'](upper)
            for a, b in ((d['DX-ANCHOR-' + st]['p'], anc), (d['DX-COLLAR-' + st]['p'], ear)):
                for i in range(3):
                    self.assertAlmostEqual(a[i], b[i], places=6)
        self.assertAlmostEqual(d['DP-MOTOR-FACE']['offset'], G['x_face'], places=6)

    def test_strut(self):
        ctx = fk.Context(fk.Backend())
        ctx.sub = 't'
        p = ctx.part('T-9')
        a, b = (0.045, 0.30, 0.15), (0.08, 0.24, 0.03)
        k9.strut(p, a, b, 0.01, 0.003)
        vol, cen = p.volume_centroid()
        L = math.dist(a, b)
        self.assertAlmostEqual(vol, 0.01 * 0.003 * math.hypot(a[1] - b[1], a[2] - b[2]), places=9)
        for i in range(3):
            self.assertAlmostEqual(cen[i], (a[i] + b[i]) / 2, places=6)
        self.assertGreater(L, 0)

    def test_section_and_dat_reader(self):
        s = k9.reflex_placeholder(0.0985)
        t = max(k9.thickness_at(s, 1.0, i / 100.0) for i in range(1, 100))
        self.assertAlmostEqual(t, 0.0985, delta=0.001)
        self.assertGreater(k9.surface_y(s, 0.3, 'upper') + k9.surface_y(s, 0.3, 'lower'), 0)    # cambered forward
        self.assertLess(k9.surface_y(s, 0.95, 'upper') + k9.surface_y(s, 0.95, 'lower'), 0)    # reflexed aft
        loop = k9.section_loop(s, 0.3, x0=0.0, x1=1.0)
        self.assertGreaterEqual(loop[0][1] - loop[-1][1], k9.TE_MIN_M - 1e-9)                  # TE opened
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            sel, led = os.path.join(d, 's.dat'), os.path.join(d, 'l.dat')
            NL = chr(10)
            with open(sel, 'w') as f:
                f.write('TEST' + NL + NL.join('%f %f' % p for p in s))
            up, lo = s[:len(s) // 2 + 1][::-1], s[len(s) // 2:]
            with open(led, 'w') as f:
                f.write('TEST' + NL + '%d. %d.' % (len(up), len(lo)) + NL * 2 + NL.join('%f %f' % p for p in up)
                        + NL * 2 + NL.join('%f %f' % p for p in lo))
            for path in (sel, led):
                r = k9.read_dat(path)
                self.assertAlmostEqual(k9.thickness_at(r, 1.0, 0.3), k9.thickness_at(s, 1.0, 0.3), places=4)

    def test_keepouts(self):
        ko = fk.Keepout('KO', 'cylinder', 'X', center=(-0.15, 0.32, 0.19), r=0.165, half=0.033)
        self.assertTrue(ko.hits(((-0.16, 0.30, 0.0), (-0.14, 0.31, 0.03))))     # inside the disc radius
        self.assertFalse(ko.hits(((-0.111, 0.30, 0.0), (0.0, 0.34, 0.21))))    # tube face 6 mm aft of the zone
        self.assertFalse(ko.hits(((-0.16, 0.0, 0.0), (-0.14, 0.10, 0.02))))     # radially outside (corner test)
        g = fk.Keepout('G', 'halfspace', 'X', at=0.31)
        self.assertTrue(g.hits(((0.2, 0, 0), (0.311, 0.1, 0.1))))
        self.assertFalse(g.hits(((0.2, 0, 0), (0.30, 0.1, 0.1))))

    def test_keepout_violation_reported(self):
        ctx, _, issues = quiet(check.run_checks, *build_all.roots(skeleton=True))[0]
        self.assertFalse([i for i in issues if i[1] == 'keepout'])
        ko = next(k for k in ctx.keepouts if k.name == 'KO-PROP-UR')
        ko.exempt.clear()                                               # the prop now violates its own zone
        hit = [c.id for c in ctx.components.values() if c.flight and ko.hits(c.bbox())]
        self.assertEqual(sorted(hit), ['PRP-901-UR', 'PRP-902-UR'])     # its motor and itself, nothing else

    def test_hover_pose(self):
        foot = k9.datum_specs(self.P)
        d = {s[0]: s[2] for s in foot}
        self.assertAlmostEqual(k9.to_hover(d['DX-FOOT-UR']['p'], self.P)[2], 0.0)   # foot on the ground
        self.assertGreater(k9.to_hover(d['DX-HUB-UR']['p'], self.P)[2], 0.3)       # props on top
        self.assertAlmostEqual(k9.to_hover((0.0, 0.0, 0.05), self.P)[0], 0.05)     # pod side faces +x

    def test_transport_stowed_and_pressed(self):
        # CR-A4-11a: cradle-to-wing edges are touch-checked; stowed prop edges are not; a cradle moved under the fin
        # (presses the lower half-fin and tube) is reported; a prop edge without "stowed" fails the touch check
        import shutil
        import tempfile
        src = build_all.roots(skeleton=True)[0]
        with tempfile.TemporaryDirectory() as d:
            root = os.path.join(d, 'sk')
            shutil.copytree(src, root, ignore=shutil.ignore_patterns('__pycache__'))
            tp = os.path.join(root, 'transport', 'fusion', 'transport.py')
            with open(tp, encoding='utf-8') as f:
                text = f.read()
            with open(tp, 'w', encoding='utf-8') as f:
                f.write(text.replace('CRADLE_Y = 0.20', 'CRADLE_Y = 0.32'))
            ip = os.path.join(root, 'transport', 'interfaces.json')
            with open(ip, encoding='utf-8') as f:
                doc = json.load(f)
            doc['edges'][-1].pop('stowed')                                  # E-TRN-909, prop LL
            with open(ip, 'w', encoding='utf-8') as f:
                json.dump(doc, f)
            issues = quiet(check.run_checks, root, os.path.join(root, 'modules.txt'), datums=True)[0][2]
        pressed = {i[2] for i in issues if i[1] == 'transport'}
        self.assertTrue({'FIN-901-LR', 'FIN-902-R'} <= pressed, issues)
        self.assertFalse({'PRP-902-UR', 'PRP-902-LR'} & pressed)              # stowed props are exempt
        touch = [i for i in issues if i[1] == 'touch']
        self.assertEqual([i[2] for i in touch], ['E-TRN-909'], touch)

    def test_thermal_contact_and_bundle(self):
        # CR-A4-11b/c: thermal edges register as ctx.contact and are touch-checked; bundle parts get bodies
        ctx, _, issues = quiet(check.run_checks, *build_all.roots(skeleton=True))[0]
        reg = ctx.registrations()
        self.assertEqual([k for k, _ in reg['E-FIN-923']], ['contact'])
        self.assertFalse([i for i in issues if i[2] == 'E-FIN-923'])
        self.assertEqual(len(ctx.components['HRN-901-R'].shapes), 2)
        with self.assertRaises(ValueError):                                   # diagonal leg: split it
            k9.bundle(type('Part', (), {'cylinder': lambda *a, **k: None})(), [((0, 0, 0), (0.1, 0.1, 0))], 0.01)

    def _skeleton_copy(self, d, edit):
        """Copy the skeleton to d, apply edit(root) and run check.py on it; returns the issues."""
        import shutil
        root = os.path.join(d, 'sk')
        shutil.copytree(build_all.roots(skeleton=True)[0], root, ignore=shutil.ignore_patterns('__pycache__'))
        edit(root)
        return quiet(check.run_checks, root, os.path.join(root, 'modules.txt'), datums=True)[0][2]

    @staticmethod
    def _edit_json(path, fn):
        with open(path, encoding='utf-8') as f:
            doc = json.load(f)
        fn(doc)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(doc, f)

    def test_carried_items_do_not_float(self):
        # CR-D1-01, CR-F2-09, CR-A4-32: check.py uses merge_check's rule. Bundles held only by ties float unless
        # flagged "carried": true; then they are exempt in both checks.
        import tempfile

        def ties(carried):
            def edit(root):
                def fn(doc):
                    for e in doc['edges']:
                        e['via'] = 'CT-TIE'
                    for p in doc['parts']:
                        p['carried'] = carried
                self._edit_json(os.path.join(root, 'harness', 'interfaces.json'), fn)
            return edit
        with tempfile.TemporaryDirectory() as d:
            bad = self._skeleton_copy(d, ties(False))
        with tempfile.TemporaryDirectory() as d:
            good = self._skeleton_copy(d, ties(True))
        fl = lambda iss: sorted(i[2] for i in iss if i[1] == 'floating')
        self.assertEqual(fl(bad), ['HRN-901-L', 'HRN-901-R'], bad)
        self.assertEqual(fl(good), [], good)
        self.assertFalse([i for i in good if i[1] == 'graph:floating'])

    def test_transport_also_contacts(self):
        # CR-D7-19: a cradle edge may name parts bonded on its flight partner; an unrelated part is refused
        import tempfile

        def edit(extra):
            def e(root):
                def fn(doc):
                    for x in doc['edges']:
                        if x['id'] == 'E-TRN-904':
                            x['also_contacts'] = extra
                self._edit_json(os.path.join(root, 'transport', 'interfaces.json'), fn)
            return e
        with tempfile.TemporaryDirectory() as d:
            ok = self._skeleton_copy(d, edit(['WNG-902']))                    # spar, epoxied in the core
        with tempfile.TemporaryDirectory() as d:
            bad = self._skeleton_copy(d, edit(['PRP-902-UR']))                # a prop: not bonded to the core
        self.assertFalse([i for i in ok if i[1] == 'transport'], ok)
        self.assertEqual([i[2] for i in bad if i[1] == 'transport'], ['E-TRN-904'], bad)

    def test_tilted_keepout(self):
        # CR-E1-31b: a vector axis is tested exactly; (1, 0, 0) agrees with 'X' on random boxes
        import random
        rnd = random.Random(7)
        for _ in range(500):
            c = tuple(rnd.uniform(-1, 1) for _ in range(3))
            a = fk.Keepout('a', 'cylinder', 'X', center=c, r=0.5, half=0.3)
            b = fk.Keepout('b', 'cylinder', (1.0, 0.0, 0.0), center=c, r=0.5, half=0.3)
            lo = [rnd.uniform(-1.5, 1.5) for _ in range(3)]
            box = (lo, [v + rnd.uniform(0.01, 0.8) for v in lo])
            self.assertEqual(a.hits(box), b.hits(box), box)
        # disc R 0.165, half 0.033 at the origin, canted +7 deg about z: the -y rim moves aft by R sin 7 = 20 mm
        n = fk.mat_vec(fk.rot_matrix('Z', 7.0), (1.0, 0.0, 0.0))
        t = fk.Keepout('t', 'cylinder', n, center=(0, 0, 0), r=0.165, half=0.033)
        u = fk.Keepout('u', 'cylinder', 'X', center=(0, 0, 0), r=0.165, half=0.033)
        rim = ((0.040, -0.160, -0.005), (0.045, -0.150, 0.005))               # aft of the flat disc, inside the canted one
        self.assertTrue(t.hits(rim))
        self.assertFalse(u.hits(rim))
        self.assertFalse(t.hits(((0.040, 0.150, -0.005), (0.045, 0.160, 0.005))))     # the +y rim moved forward
        # k9.prop_keepout with rotate= gives that axis; blade_half overrides the default
        ctx = fk.Context(None, params=self.P)
        k9.prop_keepout(ctx, 'KO', (0, 0, 0), 0.2794, 0.025, (), rotate=('Z', 7.0), blade_half=0.010)
        ko = ctx.keepouts[-1]
        self.assertAlmostEqual(ko.half, 0.035)
        self.assertAlmostEqual(ko.axis[1], math.sin(math.radians(7.0)))

    def test_revolve_centroid(self):
        self.assertAlmostEqual(fk.revolve_volume_centroid([(0, 0), (1, 0), (0, 1)])[1], 0.25)     # cone
        V, c = fk.revolve_volume_centroid([(0, 0), (2, 0), (2, 1), (0, 1)])
        self.assertAlmostEqual(V, 2 * math.pi)
        self.assertAlmostEqual(c, 1.0)

    def test_value_unit_check(self):
        ctx = fk.Context(None, params=self.P)
        self.assertEqual(ctx.value('wing.span_m', 'm'), 1.15)
        with self.assertRaises(KeyError):
            ctx.value('wing.span_m', 'mm')


class FusionBackendSmoke(unittest.TestCase):
    def test_runs_skeleton_with_fake_adsk(self):
        self._run(build_all.roots(skeleton=True), datums=52)

    def test_runs_examples_with_fake_adsk(self):
        self._run(build_all.roots(True), datums=0)

    def test_rotated_parts_get_as_built_joints(self):
        # CR-E1-31a: a joint touching a ctx.part(rotate=) component is an as-built joint (placement kept)
        import types
        saved = {k: sys.modules.get(k) for k in ('adsk', 'adsk.core', 'adsk.fusion', 'backends.fusion_backend')}
        adsk = types.ModuleType('adsk')
        adsk.core, adsk.fusion = _Any(), _Any()
        sys.modules.update({'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
        sys.modules.pop('backends.fusion_backend', None)
        used = []

        class Root(_Any):
            def __getattr__(self, n):
                if n in ('joints', 'asBuiltJoints'):
                    used.append(n)
                return _Any.__getattr__(self, n)
        try:
            from backends.fusion_backend import FusionBackend
            be = FusionBackend()
            be.root, be.warnings = Root(), []
            comp = lambda i, rot: types.SimpleNamespace(id=i, rotate=rot, native=_Any(), to_local=lambda p: p)
            for kind, rot in (('rigid', ('Y', 7.0)), ('rigid', None), ('revolute', ('Y', 7.0))):
                used.clear()
                j = types.SimpleNamespace(kind=kind, edge='E', origin=(0, 0, 0), axis='Y', limits=(-20, 20), a='A',
                                          native=None)
                be.joint(j, comp('A', rot), comp('B', None))
                self.assertIsNotNone(j.native)
                self.assertEqual(set(used), {'asBuiltJoints'} if rot else {'joints'}, (kind, rot, used))
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    def _run(self, roots, datums):
        import types
        saved = {k: sys.modules.get(k) for k in ('adsk', 'adsk.core', 'adsk.fusion', 'backends.fusion_backend')}
        adsk = types.ModuleType('adsk')
        adsk.core, adsk.fusion = _Any(), _Any()
        sys.modules.update({'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
        sys.modules.pop('backends.fusion_backend', None)
        try:
            from backends.fusion_backend import FusionBackend
            ctx, _, results = quiet(build_all.build, FusionBackend(), *roots)[0]
            self.assertTrue(all(r[2] for r in results), results)
            self.assertEqual(len(ctx.datums), datums)
            self.assertTrue(all(d.native is not None for d in ctx.datums.values()))
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
