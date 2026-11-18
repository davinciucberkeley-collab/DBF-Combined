"""Spec integrity + requirement/task traceability audit (R-PRES-02, R-TRK-05).

Usage:
  python -I tools/ledger_audit.py            # full audit, exit 1 on any broken link
  python -I tools/ledger_audit.py --brief    # one-paragraph state for hooks (never fails)
  python -I tools/ledger_audit.py --seal     # (re)write docs/spec-integrity.sha256 -- only when the
                                             # user adds an amendment; never to hide an edit to the spec

Reads only docs/requirements.md and docs/task-ledger.md (markdown tables whose first
column is an ID). Checks:
  * MASTER_PROJECT_SPEC.md hash matches the sealed hash (spec not edited)
  * spec-amendments.md still starts with its sealed prefix (append-only)
  * every requirement has >= 1 task; every task's parent requirement exists
  * every VERIFIED COMPLETE task names evidence; status words are from the allowed set
"""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SPEC = DOCS / "MASTER_PROJECT_SPEC.md"
AMEND = DOCS / "spec-amendments.md"
SEAL = DOCS / "spec-integrity.sha256"
STATUSES = {"NOT STARTED", "IN PROGRESS", "BLOCKED", "FAILED", "READY FOR REVIEW",
            "VERIFIED COMPLETE", "EXPLICITLY DEFERRED"}


def lf(b): return b.replace(b"\r\n", b"\n")  # hash is line-ending independent (autocrlf clones)


def sha(b): return hashlib.sha256(lf(b)).hexdigest()


def rows(path, idpat):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and re.fullmatch(idpat, cells[0].strip("`*")):
            out.append([c.strip("`") for c in cells])
    return out


def seal():
    SEAL.write_text(f"{sha(SPEC.read_bytes())}  MASTER_PROJECT_SPEC.md\n"
                    f"{sha(AMEND.read_bytes())}  spec-amendments.md {len(lf(AMEND.read_bytes()))}\n",
                    encoding="utf-8")
    print("sealed", SEAL)


def audit():
    errs, notes = [], []
    if not SPEC.exists():
        errs.append("MASTER_PROJECT_SPEC.md missing")
    if SEAL.exists() and SPEC.exists():
        lines = SEAL.read_text(encoding="utf-8").split("\n")
        if lines[0].split()[0] != sha(SPEC.read_bytes()):
            errs.append("MASTER_PROJECT_SPEC.md changed since it was sealed (restore it from git)")
        parts = lines[1].split()
        if len(parts) >= 3 and AMEND.exists():
            n = int(parts[2]); data = lf(AMEND.read_bytes())
            if len(data) < n or sha(data[:n]) != parts[0]:
                errs.append("spec-amendments.md: a sealed entry was edited (append-only)")
    else:
        errs.append("spec-integrity.sha256 missing")
    reqs = rows(DOCS / "requirements.md", r"R-[A-Z]+-\d+")
    tasks = rows(DOCS / "task-ledger.md", r"T-\d+")
    rids = {r[0] for r in reqs}
    # task table columns: ID | Parent | Description | Deps | Owner/model | Deliverable | Acceptance | Evidence | Status
    covered = set()
    by_status = {}
    for t in tasks:
        if len(t) < 9:
            errs.append(f"{t[0]}: expected 9 columns, got {len(t)}"); continue
        st = t[8].strip("* ")
        by_status[st] = by_status.get(st, 0) + 1
        if st not in STATUSES:
            errs.append(f"{t[0]}: unknown status '{st}'")
        for p in re.findall(r"R-[A-Z]+-\d+", t[1]):
            if p not in rids:
                errs.append(f"{t[0]}: parent {p} not in requirements.md")
            covered.add(p)
        if st == "VERIFIED COMPLETE" and t[7] in ("", "—", "-"):
            errs.append(f"{t[0]}: VERIFIED COMPLETE without evidence")
    for r in sorted(rids - covered):
        errs.append(f"{r}: no task")
    open_tasks = [t for t in tasks if len(t) >= 9 and t[8].strip("* ") not in ("VERIFIED COMPLETE",)]
    return errs, reqs, tasks, by_status, open_tasks


def main():
    if "--seal" in sys.argv:
        seal(); return 0
    errs, reqs, tasks, by_status, open_tasks = audit()
    if "--brief" in sys.argv:
        st = ", ".join(f"{k} {v}" for k, v in sorted(by_status.items()))
        nxt = [t for t in open_tasks if t[8].strip("* ") == "IN PROGRESS"][:5]
        print(f"Ledger: {len(reqs)} requirements, {len(tasks)} tasks ({st}). "
              f"Audit errors: {len(errs)}" + (f" -> {errs[:5]}" if errs else "") + ".")
        if nxt:
            print("In progress: " + "; ".join(f"{t[0]} ({t[1]}) {t[2][:70]}" for t in nxt))
        return 0
    for e in errs:
        print("FAIL", e)
    print(f"{len(reqs)} requirements, {len(tasks)} tasks, {by_status}; {len(errs)} errors")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
