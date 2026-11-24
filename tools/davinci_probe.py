"""DaVinci read-only $0 probe (T-037, spec 8.3, docs/integration/davinci-findings.md s4/s6).

Reads the token from the DAVINCI_API_KEY environment variable (never from a file in the repo, never printed).
Read-only: GET /api/v2/usage (before), GET /api/v2/projects, GET /api/v2/projects/{id}/tree (first project
or --project), GET /api/v2/usage (after). It opens no session, sends no prompt and writes nothing.
Token scopes needed: projects:read, usage:read.

Run:  python -I tools/davinci_probe.py [--project <id>] [--out docs/integration/davinci-probe-<date>.json]
"""
import json, os, sys, time, urllib.request, urllib.error, argparse, datetime

BASE = "https://davinci-app.com/api/v2"


def call(path, key):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key, "Accept": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read().decode("utf-8"))
            return r.status, body, round(time.time() - t0, 2)
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"raw": "unreadable"}
        return e.code, body, round(time.time() - t0, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--out")
    a = ap.parse_args()
    key = os.environ.get("DAVINCI_API_KEY", "")
    envf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not key and os.path.exists(envf):  # git-ignored .env at the repo root (.gitignore: .env)
        for line in open(envf, encoding="utf-8"):
            if line.strip().startswith("DAVINCI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key.startswith(("dav_ak_live_", "dav_ak_test_")):
        print("DAVINCI_API_KEY is not set (or not a dav_ak_ token). Set it in your shell; do not put it in the repo.")
        return 2
    rec = {"when": datetime.datetime.now(datetime.timezone.utc).isoformat(), "token_kind": key[:12], "steps": []}

    def step(name, path):
        code, body, dt = call(path, key)
        rec["steps"].append({"step": name, "path": path, "http": code, "seconds": dt, "body": body})
        print(f"{name:<14} HTTP {code}  {dt}s")
        return code, body

    _, u0 = step("usage_before", "/usage")
    code, projects = step("projects", "/projects")
    pid = a.project
    if not pid and code == 200:
        data = projects.get("data", projects)
        lst = (data.get("owned") or []) + (data.get("shared") or []) if isinstance(data, dict) else []
        if lst:
            pid = lst[0].get("id") or lst[0].get("projectId")
    if pid:
        code, tree = step("object_tree", f"/projects/{pid}/tree?limit=50")
        if code == 200:
            n = tree.get("objectCount", len(tree.get("tree", [])))
            print(f"  project {pid}: objectCount {n}")
    else:
        print("  no project visible to this token; tree step skipped")
    _, u1 = step("usage_after", "/usage")

    def total(u):
        d = u.get("data", u) if isinstance(u, dict) else {}
        t = d.get("totals", {}) if isinstance(d, dict) else {}
        return t.get("amountUsd"), d.get("asOf") if isinstance(d, dict) else None

    b, a_ = total(u0), total(u1)
    rec["usage_usd_before_after"] = [b[0], a_[0]]
    rec["usage_asOf_before_after"] = [b[1], a_[1]]
    print(f"usage USD before {b[0]} (asOf {b[1]})  after {a_[0]} (asOf {a_[1]})")
    print("note: usage is recorded on an interval; re-run usage later to confirm no delayed charge.")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
        print("written", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
