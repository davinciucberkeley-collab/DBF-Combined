"""Self-test for the proof-chain tools (stdlib unittest, ~1 s):  python -I redesign/proofs/test_proofs.py

Copies the example claims set into a temporary redesign/ folder, breaks it on purpose and checks that
build_graph.py notices: drift after a parameter change, a unit mismatch, an unknown reference, and a claim that
violates a limit of 0 (CDR-03 regression: those used to get margin None and were not counted as fails).
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
import proofkit as pk  # noqa: E402


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

    # ---- limits of 0 (CDR-03, 2026-11-13) ----
    ZERO = [("CL-T-MS-NEG", -0.34, ">=", "-", True),        # margin of safety below 0
            ("CL-T-CLEAR-NEG", -0.00012, ">=", "m", True),  # -0.12 mm against >= 0 (the CG-range case)
            ("CL-T-COUNT-POS", 6, "<=", "-", True),         # 6 stale inputs against <= 0
            ("CL-T-MS-POS", 0.28, ">=", "-", False),
            ("CL-T-AT-ZERO", 0.0, ">=", "-", False),        # exactly on the limit passes
            ("CL-T-NEG-ZERO", -0.0, ">=", "-", False),
            ("CL-T-COUNT-ZERO", 0, "<=", "-", False),
            ("CL-T-BELOW-ZERO-OK", -3.0, "<=", "-", False)]

    def write_zero_claims(self):
        nodes = [{"id": i, "type": "claim", "title": i, "value": v, "unit": u, "limit": {"op": op, "value": 0},
                  "how": "regression case"} for i, v, op, u, _ in self.ZERO]
        (self.tmp / "zero").mkdir()
        (self.tmp / "zero" / "claims.json").write_text(json.dumps({"schema": "proofs/1", "nodes": nodes}), encoding="utf-8")

    def test_margin_function_zero_limit(self):
        self.assertEqual(pk.margin(-0.34, 0, ">="), -0.34)                 # distance, sign = pass / fail
        self.assertEqual(pk.margin(6, 0, "<="), -6)
        self.assertEqual(pk.margin(0.28, 0, ">="), 0.28)
        self.assertEqual(pk.margin(0.0, 0, ">="), 0.0)
        self.assertEqual(str(pk.margin(-0.0, 0, ">=")), "0.0")             # never "-0.0"
        self.assertAlmostEqual(pk.margin(2.4, 2.0, ">="), 0.2)             # non-zero limits unchanged: fraction
        self.assertAlmostEqual(pk.margin(34.6, 30.0, "<="), -4.6 / 30.0)
        self.assertAlmostEqual(pk.margin(-3.0, -2.0, ">="), -0.5)
        self.assertIsNone(pk.margin("n/a", 0, ">="))
        self.assertIsNone(pk.margin(float("nan"), 0, ">="))
        self.assertEqual(pk.margin_text(-0.00012, 0, "m"), "-0.00012 m abs")
        self.assertEqual(pk.margin_text(-0.154, 30.0, "A"), "-15%")

    def test_zero_limit_violation_is_a_fail(self):
        self.write_zero_claims()
        code, log = self.build()
        self.assertEqual(code, 0, log)                                     # a fail is not a build error...
        g = self.graph()
        for cid, _, _, _, fails in self.ZERO:
            self.assertEqual(bool(g[cid].get("fails")), fails, cid)
            self.assertIsNotNone(g[cid].get("margin"), cid)
            self.assertTrue(g[cid].get("margin_abs"), cid)
            self.assertEqual(g[cid]["margin"] < 0, fails, cid)
        self.assertIn("FAILS: margin -0.34 abs", g["CL-T-MS-NEG"]["reasons"][0])
        meta = json.loads((self.tmp / "out" / "graph.json").read_text(encoding="utf-8"))["meta"]
        base = 2                                                           # the demo's own fails: CL-EX-ESC-CONN, R-EX-DISCONNECT
        self.assertEqual(meta["counts"]["fails"], base + sum(f for *_, f in self.ZERO))
        self.assertNotIn("margin_abs", g["CL-EX-ESC-CONN"])                # non-zero limit: still a fraction
        code, log = self.build("--strict")                                 # ...but the release gate stops on it
        self.assertEqual(code, 1)
        for cid, _, _, _, fails in self.ZERO:
            self.assertEqual(f"STRICT {cid}:" in log, fails, cid)

    def test_self_check_catches_an_unjudged_claim(self):
        ok = {"id": "CL-A", "type": "claim", "value": -1.0, "limit": {"op": ">=", "resolved": 0}, "margin": -1.0, "fails": True}
        self.assertEqual(build_graph.self_check([ok]), [])
        hidden = dict(ok, margin=None, fails=False)                        # what the old rule produced
        self.assertIn("no margin", build_graph.self_check([hidden])[0])
        unmarked = dict(ok, fails=False)
        self.assertIn("not marked FAILS", build_graph.self_check([unmarked])[0])
        wrong = {"id": "CL-B", "type": "claim", "value": 1.0, "limit": {"op": ">=", "resolved": 0}, "margin": -1.0}
        self.assertIn("negative margin", build_graph.self_check([wrong])[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
