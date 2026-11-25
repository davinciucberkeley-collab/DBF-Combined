"""R-PLAN-01 check: every R-id in docs/requirements.md appears in docs/execution-plan.md."""
import pathlib, re, sys
D = pathlib.Path(__file__).resolve().parents[1] / "docs"
reqs = [m.group(1) for l in (D / "requirements.md").read_text(encoding="utf-8").splitlines()
        if (m := re.match(r"\|\s*`?\*?(R-[A-Z]+-\d+)", l))]
plan = (D / "execution-plan.md").read_text(encoding="utf-8")
missing = [r for r in reqs if not re.search(re.escape(r) + r"(?!\d)", plan)]
print(f"{len(reqs)} R-ids, {len(missing)} missing from execution-plan.md" + (": " + ", ".join(missing) if missing else ""))
sys.exit(1 if missing else 0)
