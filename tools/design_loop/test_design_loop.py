"""Tests for the design loop. Run: python -I tools/design_loop/test_design_loop.py   (about 25 s)"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLI = HERE / "cli.py"


def run(args, tmp):
    return subprocess.run([sys.executable, "-I", str(CLI), *args, "--runs-dir", str(tmp), "--evidence-dir", str(Path(tmp) / "ev")]
                          if args[0] == "run" else [sys.executable, "-I", str(CLI), *args], capture_output=True, text=True, encoding="utf-8")


class DesignLoop(unittest.TestCase):
    def test_identity_run_has_no_deltas_and_leaves_committed_files(self):
        with tempfile.TemporaryDirectory() as t:
            r = run(["run", "--name", "identity"], t)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            ev = json.loads((Path(t) / "ev" / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(ev["deltas"], [])
            self.assertTrue(ev["committed_unchanged"])
            self.assertTrue(ev["baseline_matches_committed"]["match"], ev["baseline_matches_committed"])
            self.assertTrue((Path(t) / "ev" / "evidence.md").exists())

    def test_part_mass_change_moves_mass_and_cg(self):
        with tempfile.TemporaryDirectory() as t:
            r = run(["run", "--set", "part_mass:PWR-001=285", "--name", "mass"], t)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            ev = json.loads((Path(t) / "ev" / "evidence.json").read_text(encoding="utf-8"))
            b, v = ev["baseline"]["MC-MASS-TOTAL"]["value"], ev["variant"]["MC-MASS-TOTAL"]["value"]
            self.assertAlmostEqual(v - b, 15.0, places=1)
            self.assertNotEqual(ev["baseline"]["CL-A-CG"]["value"], ev["variant"]["CL-A-CG"]["value"])
            self.assertGreater(ev["variant"]["CL-A-MASS-PRED"]["value"], ev["baseline"]["CL-A-MASS-PRED"]["value"])
            self.assertTrue(ev["committed_unchanged"])
            self.assertTrue((Path(t) / "ev" / "variant_design" / "params-A.json").exists())

    def test_bad_parameter_exits_2(self):
        with tempfile.TemporaryDirectory() as t:
            r = run(["run", "--set", "wingspan_m=1"], t)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            r = run(["run", "--set", "param:mission.no_such=1"], t)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_list_params(self):
        r = run(["list-params"], None)
        self.assertEqual(r.returncode, 0)
        self.assertIn("pack_capacity_ah", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
