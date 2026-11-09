"""Self-test for the proof-chain tools (stdlib unittest, ~1 s):  python -I redesign/proofs/test_proofs.py

Copies the example claims set into a temporary redesign/ folder, breaks it on purpose and checks that
build_graph.py notices: drift after a parameter change, a unit mismatch, an unknown reference.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_graph  # noqa: E402


def run(*args):
    err, out = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
        code = build_graph.main(list(args))
    return code, out.getvalue() + err.getvalue()


class ProofChainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "redesign" / "demo"
        shutil.copytree(HERE / "examples", self.tmp, ignore=shutil.ignore_patterns("out", "__pycache__"))
        self.params = self.tmp / "params.json"

    def tearDown(self):
        shutil.rmtree(self.tmp.parent.parent, ignore_errors=True)

    def build(self, *extra):
        return run("--root", str(self.tmp), "--out", str(self.tmp / "out"), *extra)

    def edit_params(self, fn):
        p = json.loads(self.params.read_text(encoding="utf-8"))
        fn(p)
        self.params.write_text(json.dumps(p), encoding="utf-8")

    def graph(self):
        return {n["id"]: n for n in json.loads((self.tmp / "out" / "graph.json").read_text(encoding="utf-8"))["nodes"]}

    def test_examples_pass_and_statuses(self):
        code, log = self.build()
        self.assertEqual(code, 0, log)
        g = self.graph()
        self.assertEqual(g["CL-EX-MTOW"]["status"], "VERIFIED")            # run test beats the unverified battery mass
        self.assertEqual(g["CL-EX-HOVER-TW"]["status"], "CHECKED")
        self.assertEqual(g["CL-EX-STALL"]["status"], "UNVERIFIED")         # rests on an UNVERIFIED assumption
        self.assertTrue(g["CL-EX-ESC-CONN"]["fails"])                      # 34.6 A needed > 30 A rating
        self.assertTrue(g["R-EX-DISCONNECT"]["fails"])
        self.assertTrue((self.tmp / "out" / "CHAIN.md").read_text(encoding="utf-8").startswith("# Proof chains"))

    def test_strict_fails_on_negative_margin(self):
        code, log = self.build("--strict")
        self.assertEqual(code, 1)
        self.assertIn("STRICT CL-EX-ESC-CONN", log)

    def test_param_change_is_drift(self):
        self.edit_params(lambda p: p["mass"]["battery_kg"].update(value=0.95))
        code, log = self.build()
        self.assertEqual(code, 1)
        self.assertIn("DRIFT CALC-EX-MTOW.m_kg", log)
        self.assertIn("batt 0.82 -> 0.95", log)                            # names the input that changed

    def test_unit_mismatch(self):
        self.edit_params(lambda p: p["wing"]["span_m"].update(unit="mm"))
        code, log = self.build()
        self.assertEqual(code, 1)
        self.assertIn("input b expects m", log)

    def test_unknown_reference(self):
        f = self.tmp / "power" / "claims.json"
        f.write_text(f.read_text(encoding="utf-8").replace('"R-EX-MASS"', '"R-NOPE"'), encoding="utf-8")
        code, log = self.build()
        self.assertEqual(code, 1)
        self.assertIn("R-NOPE", log)


if __name__ == "__main__":
    unittest.main(verbosity=2)
