"""test_manual_kit.py - fast checks of the build-manual kit (no Blender, < 1 s).

    python -I redesign/manual-kit/test_manual_kit.py
"""
import json
import math
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_manual as B    # noqa: E402
import figures as F         # noqa: E402
import html_out             # noqa: E402
import steps_lib as L       # noqa: E402

EX = os.path.join(HERE, 'examples')
IF = os.path.join(L.REDESIGN, 'fusion', 'examples')


def manual(src=EX):
    return L.Manual(src, IF)


class Examples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = manual()

    def test_loads_clean(self):
        self.assertEqual(self.m.errors, [])
        self.assertEqual([s['id'] for s in self.m.steps],
                         ['FUS-S01', 'WNG-S01', 'WNG-S02', 'BMS-S01', 'WNG-S03', 'FUS-S02'])

    def test_every_part_and_edge_installed_once(self):
        self.assertEqual(self.m.missing_parts, [])
        self.assertEqual(self.m.missing_edges, [])

    def test_fasteners_from_joint_stacks(self):
        k = {f['item']: f['qty'] for f in self.m.kit(self.m.steps)['fasteners']}
        self.assertEqual(k['M3x8 SHCS A2-70'], 8)          # 4 per motor, two motors
        self.assertEqual(k['M4 nyloc'], 2)
        self.assertEqual(k['M3x5.7 brass heat-set'], 4)
        cons = {c['item']: c['qty'] for c in self.m.kit(self.m.steps)['consumables']}
        self.assertEqual(cons['Threadlocker, medium strength (blue)'], 12)

    def test_mass_target_and_params(self):
        last = self.m.steps[-1]['checks'][0]
        self.assertTrue(last['target'].startswith('1470 g'), last['target'])
        self.assertEqual(self.m.sub_params('{ex_wing.tip_y_m*2|mm}'), '1200')

    def test_figure_roles_follow_the_assembly(self):
        s = {x['id']: x for x in self.m.steps}
        self.assertEqual(s['WNG-S01']['context'], [])                  # fuselage is a separate subassembly
        self.assertIn('FUS-001', s['WNG-S03']['context'])              # bolting the wing joins them
        self.assertEqual(s['WNG-S03']['focus'], ['WNG-003'])           # no new parts: act on part_a of the edge


class Broken(unittest.TestCase):
    def test_errors_are_caught(self):
        tmp = tempfile.mkdtemp()
        try:
            shutil.copytree(EX, os.path.join(tmp, 'ex'))
            p = os.path.join(tmp, 'ex', 'ex_wing', 'steps.json')
            d = L.load_json(p)
            d['steps'][0]['parts'].append('WNG-999')                    # unknown part
            d['steps'][1]['check'] = {'type': 'dimension', 'text': 'look'}   # no target
            d['steps'][1]['edges'].append('E-WNG-02')                   # installed twice
            d['steps'][0]['actions'][1]['do'] += ' {ex_wing.nope_m|mm}'  # unresolvable number
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(d, f)
            m = manual(os.path.join(tmp, 'ex'))
            text = '\n'.join(m.errors)
            for want in ('unknown part WNG-999', 'measurable "target"', 'already installed', 'cannot be resolved'):
                self.assertIn(want, text)
        finally:
            shutil.rmtree(tmp)


class Markers(unittest.TestCase):
    def test_no_overlap_and_offscreen_dropped(self):
        step = {'actions_n': [{'do': 'a', 'at': 'P1'}, {'do': 'b', 'at': 'P2'}, {'do': 'c', 'at': 'P3'}, {'do': 'd'}]}
        sc = {'size': [1600, 1000], 'subject_px': [400, 200, 1200, 800],
              'callouts': [{'item': 'P1', 'x': 800, 'y': 500}, {'item': 'P2', 'x': 805, 'y': 502},
                           {'item': 'P3', 'x': 1900, 'y': 500}]}
        mks, miss = F.markers(sc, step)
        self.assertEqual([m['n'] for m in mks], [1, 2])
        self.assertEqual(miss, [3])
        self.assertGreater(math.hypot(mks[0]['x'] - mks[1]['x'], mks[0]['y'] - mks[1]['y']), 2 * F.R)


class Page(unittest.TestCase):
    def test_html_structure(self):
        m = manual()
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, 'manual.html')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_out.page(m, {}, L.glossary(m), {'gallery': []}))
            probs, lp = B.lint(path, len(m.steps))
            self.assertEqual(probs, [])
            self.assertEqual(lp.cards, 6)
        finally:
            shutil.rmtree(tmp)


if __name__ == '__main__':
    unittest.main(verbosity=1)
