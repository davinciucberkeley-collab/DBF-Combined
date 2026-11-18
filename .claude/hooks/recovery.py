"""Compaction / session recovery hooks (R-PRES-06..09). Writes only to docs/session-log.md.

Called from .claude/settings.json:
  pre-compact     verify state files, snapshot session-state.md, log the event
  post-compact    log the event (audit trail)
  session-start   print the recovery brief; stdout becomes context for the new/resumed/compacted session
Reads the hook JSON on stdin (source / trigger / session_id) when present. Never blocks: always exits 0.
"""
import datetime, json, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
STATE_FILES = ["MASTER_PROJECT_SPEC.md", "spec-amendments.md", "requirements.md", "task-ledger.md",
               "execution-plan.md", "session-state.md", "engineering-decisions.md",
               "verification-report.md", "repository-audit.md"]
LOG = DOCS / "session-log.md"


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def log(line):
    if not LOG.exists():
        LOG.write_text("# Session lifecycle log (written by .claude/hooks/recovery.py)\n\n", encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"- {now()} {line}\n")


def payload():
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def brief():
    try:
        r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "ledger_audit.py"), "--brief"],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return f"(ledger audit could not run: {e})"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "session-start"
    p = payload()
    sid = str(p.get("session_id", "?"))[:8]
    missing = [f for f in STATE_FILES if not (DOCS / f).exists()]
    if mode == "pre-compact":
        snap = DOCS / "session-state.md"
        if snap.exists():
            shutil.copyfile(snap, ROOT / ".claude" / "session-state.precompact.md")
        log(f"PreCompact trigger={p.get('trigger', '?')} session={sid} missing={missing or 'none'}")
    elif mode == "post-compact":
        log(f"PostCompact trigger={p.get('trigger', '?')} session={sid}")
    else:
        src = p.get("source", "?")
        log(f"SessionStart source={src} session={sid}")
        head = "CONTEXT WAS COMPACTED. " if src == "compact" else ""
        print(f"""{head}DBF master program recovery (docs/ is the source of truth; a compaction summary is NOT authoritative).
Before resuming work, follow the recovery procedure in docs/session-state.md section "Recovery procedure":
read docs/session-state.md (checkpoint + next action), then the in-progress rows of docs/task-ledger.md and
docs/requirements.md; read docs/MASTER_PROJECT_SPEC.md in full at milestones, after compaction, and before final
verification. Never edit MASTER_PROJECT_SPEC.md; new user instructions go verbatim into docs/spec-amendments.md.
{brief()}
Missing state files: {', '.join(missing) if missing else 'none'}.""")
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a hook must never break the session
        print(f"(recovery hook error: {e})")
    sys.exit(0)
