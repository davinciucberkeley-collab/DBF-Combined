"""T-037 Part 4: build assembly "Concept A assembly (snapshot 73656c93)" on branch concept-a-snapshot-73656c93.
Findings (validator): assembly accepts only common fields + kind; `geometries` is "not a field of type assembly"; PATCH to move
an object needs a JWT (API key refused, 403). An assembly OWNS geometries: a STEP uploaded to the assembly's id becomes a child
geometry of it, at the default (identity) placement. So this uploads every STEP again, into one sub-assembly per subsystem.
Usage: python -I tools/davinci_step_assemble.py <step dir> <viewer-data.json> <out json>   (no commit here)"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import davinci_import_a as A
import davinci_step_upload as U

PID, BRANCH = A.PID, A.BRANCH


def main():
    sd, vdp, out = sys.argv[1:4]
    A.KEY = A.load_key()
    assert A.KEY.startswith(("dav_ak_live_", "dav_ak_test_"))
    rec = {"usage_before": A.usage()}
    parts = json.load(open(vdp, encoding="utf-8"))["parts"]
    sub_of = {p["id"]: p["subsystem"] for p in parts}
    subs = sorted(set(sub_of.values()))
    files = sorted(f[:-5] for f in os.listdir(sd) if f.endswith(".step"))
    ROOT = A.oid("cadgeo/root")
    ASM = A.oid("cadgeo/asm")
    SA = {s: A.oid("cadgeo/asm/sub/" + s) for s in subs}
    objs = {ASM: dict(type="assembly", parent=ROOT, name="Concept A assembly (snapshot 73656c93)",
                      documentation="All 129 part geometries of concept A at 73656c93 in aircraft coordinates (x aft, y right, z up, mm), every geometry at the identity placement because each STEP is already in aircraft coordinates. One sub-assembly per subsystem.")}
    for s in subs:
        objs[SA[s]] = dict(type="assembly", parent=ASM, name=f"{s} ({sum(1 for f in files if sub_of.get(f) == s)} parts)")
    if A.post("asm", objs)[0][0] != 201:
        return 1
    tr = U.tree()
    # stray geometry placed directly under the top assembly by the probe
    for o in tr:
        if o.get("type") == "geometry" and o.get("parent") == ASM:
            A.call("del_probe", "DELETE", f"/projects/{PID}/objects/{o['id']}?branch={BRANCH}")
    have = {(o.get("parent"), o.get("name")) for o in tr if o.get("type") == "geometry"}
    todo = [f for f in files if (SA[sub_of[f]], f) not in have]
    print("to upload", len(todo))
    rec["uploads"], fails, sid, t0 = {}, [], None, 0
    try:
        for i, pid in enumerate(todo):
            if sid is None or time.time() - t0 > 2400:
                if sid:
                    A.call("close_session", "DELETE", f"/projects/{PID}/sessions/{sid}")
                sid, base, grant = U.open_session()
                t0 = time.time()
            data = open(os.path.join(sd, pid + ".step"), "rb").read()
            code, resp = U.upload_step(base + SA[sub_of[pid]], grant, pid, pid + ".step", data)
            rec["uploads"][pid] = code
            if code != 200:
                fails.append(code)
                print("FAIL", pid, code, json.dumps(resp)[:300])
                if len(fails) >= 2 and fails[-1] == fails[-2]:
                    print("two failures of the same kind: stop")
                    break
            elif i % 10 == 0:
                print("uploaded", i + 1, "/", len(todo), flush=True)
    finally:
        if sid:
            A.call("close_session", "DELETE", f"/projects/{PID}/sessions/{sid}")
    geo = {}
    for o in U.tree():
        if o.get("type") == "geometry" and o.get("parent") in SA.values():
            geo.setdefault(o["name"], []).append(o["id"])
    rec["asm_geometry_ids"], rec["asm"], rec["sub_asm"] = geo, ASM, SA
    rec["missing"] = [f for f in files if f not in geo]
    rec["duplicates"] = [k for k, v in geo.items() if len(v) > 1]
    print("geometries in assembly", sum(len(v) for v in geo.values()), "missing", rec["missing"], "dups", rec["duplicates"])
    rec["usage_after"] = A.usage()
    json.dump(rec, open(out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
