"""Recompute the requirements.md Status roll-up from task-ledger.md (2026-11-23 milestone fixes).

Rule: an R-id is VERIFIED COMPLETE only if every task whose Parent column carries it is VERIFIED COMPLETE or
EXPLICITLY DEFERRED; standing rules (bind every task until T-047) stay IN PROGRESS. Otherwise IN PROGRESS if any
carrying task has started (any status but NOT STARTED), else NOT STARTED; all carrying tasks BLOCKED -> BLOCKED.
Run: python -I docs/audits/2026-11-23-rollup_check.py   (exit 1 if any row mismatches)
"""
import pathlib, re, sys
D = pathlib.Path(__file__).resolve().parents[1]
STANDING = {"R-RULE-01", "R-RULE-04", "R-RULE-06", "R-RULE-08", "R-MON-02", "R-MON-03"}
DONE = {"VERIFIED COMPLETE", "EXPLICITLY DEFERRED"}


def rows(path, pat):
    for line in (D / path).read_text(encoding="utf-8").splitlines():
        c = [x.strip().strip("`*") for x in line.strip().strip("|").split("|")]
        if c and re.fullmatch(pat, c[0]):
            yield c


def expected():
    tasks = list(rows("task-ledger.md", r"T-\d+"))
    out = {}
    for r in rows("requirements.md", r"R-[A-Z]+-\d+"):
        rid = r[0]
        carry = [t for t in tasks if re.search(re.escape(rid) + r"(?!\d)", t[1])]
        sts = [t[-1] for t in carry]
        if not carry:
            exp = "NO TASK"
        elif rid in STANDING:
            exp = "IN PROGRESS"
        elif all(s in DONE for s in sts):
            exp = "VERIFIED COMPLETE"
        elif all(s == "NOT STARTED" for s in sts):
            exp = "NOT STARTED"
        elif all(s == "BLOCKED" for s in sts):
            exp = "BLOCKED"
        else:
            exp = "IN PROGRESS"
        out[rid] = (exp, r[-1], [(t[0], t[-1]) for t in carry])
    return out


if __name__ == "__main__":
    ex = expected()
    bad = {k: v for k, v in ex.items() if v[0] != v[1]}
    print(f"{len(ex)} requirement rows; {len(bad)} mismatch(es)")
    for k, (e, a, c) in bad.items():
        print(f"  {k}: requirements.md says {a!r}, roll-up says {e!r}; tasks {c}")
    sys.exit(1 if bad else 0)
