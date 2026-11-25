"""DaVinci probe 2: the "Claude thinks, DaVinci only runs tools" pattern at $0 AI spend (T-037, findings s6).

Token from DAVINCI_API_KEY or the git-ignored .env (never printed). Needs projects:read, projects:write,
sessions:manage, usage:read. Never prompts the DaVinci agent (no agent:message call).

Steps: usage before -> create scratch branch (from main; never writes main) -> open session on it ->
invokeTool Core/ReadObject (no model) -> add one probe object on the scratch branch -> invokeTool ReadObject
on it -> delete the probe object -> close session -> usage after. No commit is made. The scratch branch
stays (deleting a branch needs projects:manage); remove it in the DaVinci UI if wanted.

Run:  python -I tools/davinci_probe2.py --project <id> [--out docs/integration/davinci-probe2-<date>.json]
"""
import json, os, sys, time, uuid, argparse, datetime, urllib.request, urllib.error

BASE = "https://davinci-app.com/api/v2"
MODEL_PKG = "00000000-0000-0000-0000-0000000model"


def load_key():
    key = os.environ.get("DAVINCI_API_KEY", "")
    envf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not key and os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.strip().startswith("DAVINCI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    key = load_key()
    if not key.startswith(("dav_ak_live_", "dav_ak_test_")):
        print("no DaVinci token found"); return 2
    pid = a.project
    rec = {"when": datetime.datetime.now(datetime.timezone.utc).isoformat(), "project": pid, "steps": []}

    def call(name, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(BASE + path, data=data, method=method,
                                     headers={"Authorization": "Bearer " + key, "Accept": "application/json",
                                              "Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                code, out = r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            code = e.code
            try: out = json.loads(e.read().decode())
            except Exception: out = {"raw": "unreadable"}
        dt = round(time.time() - t0, 2)
        rec["steps"].append({"step": name, "method": method, "path": path, "http": code, "seconds": dt, "body": out})
        msg = ""
        if isinstance(out, dict) and out.get("error"): msg = out["error"].get("code", "") + " " + str(out["error"].get("message", ""))[:120]
        print(f"{name:<18} {method:<6} HTTP {code}  {dt}s  {msg}")
        return code, out

    def usd(u):
        t = (u or {}).get("totals", {}) if isinstance(u, dict) else {}
        return t.get("amountUsd"), t.get("eventCount"), (u or {}).get("asOf") if isinstance(u, dict) else None

    _, u0 = call("usage_before", "GET", "/usage")
    bname = "claude-probe-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    code, br = call("create_branch", "POST", f"/projects/{pid}/branches", {"name": bname, "sourceBranch": "main"})
    if code != 201:
        print("branch not created; stopping before any write"); return finish(rec, a, u0, None, call, usd)
    bname = br.get("branch", {}).get("name", bname)
    code, ses = call("open_session", "POST", f"/projects/{pid}/sessions", {"branch": bname, "ttlSeconds": 600})
    sid = (ses or {}).get("sessionId") or (ses or {}).get("id")
    if not sid:
        print("no session; stopping"); return finish(rec, a, u0, None, call, usd)
    try:
        call("tool_read_model", "POST", f"/projects/{pid}/sessions/{sid}/tools/invoke",
             {"toolbox": "Core", "tool": "ReadObject", "params": {"objectId": MODEL_PKG}})
        oid = str(uuid.uuid4())
        code, _ = call("add_probe_object", "POST", f"/projects/{pid}/objects?branch={bname}",
                       {"objects": {oid: {"type": "requirement", "parent": MODEL_PKG, "name": "Claude API probe (delete me)"}}})
        if code == 201:
            call("tool_read_probe", "POST", f"/projects/{pid}/sessions/{sid}/tools/invoke",
                 {"toolbox": "Core", "tool": "ReadObject", "params": {"objectId": oid}})
            call("delete_probe", "DELETE", f"/projects/{pid}/objects/{oid}?branch={bname}")
    finally:
        call("close_session", "DELETE", f"/projects/{pid}/sessions/{sid}")
    rec["scratch_branch"] = bname
    return finish(rec, a, u0, bname, call, usd)


def finish(rec, a, u0, bname, call, usd):
    _, u1 = call("usage_after", "GET", "/usage")
    b, f = usd(u0), usd(u1)
    rec["usage_before_after"] = {"usd": [b[0], f[0]], "events": [b[1], f[1]], "asOf": [b[2], f[2]]}
    print(f"usage USD {b[0]} -> {f[0]}; events {b[1]} -> {f[1]}; asOf {b[2]} -> {f[2]}")
    if bname: print(f"scratch branch left in place: {bname}")
    if a.out:
        json.dump(rec, open(a.out, "w", encoding="utf-8"), indent=1); print("written", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
