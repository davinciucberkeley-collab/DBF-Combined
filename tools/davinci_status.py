"""DaVinci read-only status (T-037): usage totals and asOf, project storage, branches. Token from DAVINCI_API_KEY or the
git-ignored .env (never printed). Reads only; opens no session; writes nothing remote.
Run:  python -I tools/davinci_status.py [--project <id>]"""
import json, os, sys, argparse, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from davinci_probe2 import load_key, BASE

def get(path, key):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except Exception: return e.code, {}

def find(d, keys, out, pre=""):
    if isinstance(d, dict):
        for k, v in d.items():
            if any(s in k.lower() for s in keys) and not isinstance(v, (dict, list)): out.append((pre + k, v))
            find(v, keys, out, pre + k + ".")
    elif isinstance(d, list):
        for i, v in enumerate(d[:50]): find(v, keys, out, pre + f"[{i}].")
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--project", default="b53fed82-b072-43c2-9994-de76de845d93"); a = ap.parse_args()
    key = load_key()
    if not key.startswith(("dav_ak_live_", "dav_ak_test_")): print("no DaVinci token found"); return 2
    c, u = get("/usage", key); print("usage", c, find(u, ("amountusd", "eventcount", "asof"), []))
    c, p = get(f"/projects/{a.project}", key); print("project", c, find(p, ("storage", "name", "limit"), [])[:12])
    c, b = get(f"/projects/{a.project}/branches", key)
    names = [x.get("name") for x in (b.get("branches") or b.get("data") or []) if isinstance(x, dict)] if isinstance(b, dict) else []
    print("branches", c, names or find(b, ("name", "error", "code"), [])[:10])
    c, ps = get("/projects", key); print("projects", c, find(ps, ("name", "storage"), [])[:20])
    return 0

if __name__ == "__main__": sys.exit(main())
