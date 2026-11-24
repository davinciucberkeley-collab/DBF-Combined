"""T-037 (AM-048) import part 2: GLB upload, Page probe, CAD parts -> DaVinci project "API Test", branch concept-a-snapshot-73656c93 ONLY.

Reads ONLY `git show 73656c93:<path>`. Token from DAVINCI_API_KEY / git-ignored .env (never printed or written; the
session grant is never printed either). Stdlib only. No agent prompt. Idempotent (uuid5 ids).
Run:  python -I tools/davinci_import_a_3d.py [--out docs/integration/davinci-import-2026-11-23-3d.json]
"""
import json, os, sys, uuid, argparse, struct, subprocess, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import davinci_import_a as A

PID, BRANCH, SHA = A.PID, A.BRANCH, A.SHA
GLB = "redesign/site/assets/concept-a.opt.glb"
GLB_NAME = "concept-a.opt.glb (gated GLB, snapshot 73656c93)"
GLB_BYTES = 2495644


def git_bytes(path):
    return subprocess.run(["git", "show", f"{SHA}:{path}"], cwd=A.ROOT, capture_output=True, check=True).stdout


def glb_nodes(b):
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    by = {}
    for x in j["nodes"]:
        pid = (x.get("extras") or {}).get("part_id")
        if pid:
            by.setdefault(pid, []).append(x["name"])
    return by


def upload(url, grant, fields, fname, data):
    bd = "----dav" + uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    body += (f'--{bd}\r\nContent-Disposition: form-data; name="file"; filename="{fname}"\r\n'
             f'Content-Type: model/gltf-binary\r\n\r\n').encode() + data + f"\r\n--{bd}--\r\n".encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": "Bearer " + grant, "Content-Type": "multipart/form-data; boundary=" + bd, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"raw": "unreadable"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--skip-upload", action="store_true")
    a = ap.parse_args()
    A.KEY = A.load_key()
    if not A.KEY.startswith(("dav_ak_live_", "dav_ak_test_")):
        print("no token")
        return 2
    rec = {"branch": BRANCH, "sha": SHA}
    rec["usage_before"] = A.usage()
    call, oid = A.call, A.oid

    glb = git_bytes(GLB)
    assert len(glb) == GLB_BYTES, len(glb)
    vd = json.loads(A.git_show("redesign/site/data/viewer-data.json"))
    parts = vd["parts"]
    nodes = glb_nodes(glb)

    M3, MC = oid("pkg3d/model"), oid("pkg3d/cadparts")
    subs = sorted({p["subsystem"] for p in parts})
    SP = {s: oid("pkg3d/sub/" + s) for s in subs}
    pk = {M3: dict(type="package", parent=A.MODEL, name="3D model",
                   documentation=f"Exported GLB of concept A at snapshot {SHA} (passed the 0-clash GLB gate, D-247); T-101 elevon chord change not included."),
          MC: dict(type="package", parent=A.MODEL, name="CAD parts",
                   documentation=f"One part per CAD part in redesign/site/data/viewer-data.json at {SHA} ({len(parts)} parts), grouped by subsystem. Documentation gives the GLB node name.")}
    for s in subs:
        pk[SP[s]] = dict(type="package", parent=MC, name=f"{s} ({sum(1 for p in parts if p['subsystem'] == s)} parts)")
    if A.post("packages3d", pk)[0][0] != 201:
        return fin(rec, a)

    # 1. upload
    rec["upload"] = {}
    if not a.skip_upload:
        c, pr = call("get_project", "GET", f"/projects/{PID}")
        c, ses = call("open_session", "POST", f"/projects/{PID}/sessions", {"branch": BRANCH, "ttlSeconds": 900})
        sid = (ses or {}).get("sessionId") or (ses or {}).get("id")
        dp = (ses or {}).get("dataPlane") or {}
        rec["session_keys"] = sorted(ses.keys()) if isinstance(ses, dict) else None
        rec["dataplane_keys"] = sorted(dp.keys())
        try:
            owner = dp.get("ownerId") or ses.get("ownerId")
            rec["owner_found"] = bool(owner)
            if sid and owner and dp.get("url") and dp.get("token"):
                url = (f"{dp['url'].rstrip('/')}/api/v1/file/upload/{owner}/{dp.get('userId') or owner}/{dp.get('projectKey') or PID + '--' + BRANCH}/"
                       f"{dp.get('connectionId') or 'headless-' + sid}/{M3}")
                code, out = upload(url, dp["token"], {"objectName": GLB_NAME}, "concept-a.opt.glb", glb)
                print("upload HTTP", code, (json.dumps(out)[:300] if code != 200 else ""))
                rec["upload"] = {"http": code, "response": json.dumps(out)[:1500]}
                A.LOG.append({"step": "upload", "http": code})
        finally:
            if sid:
                call("close_session", "DELETE", f"/projects/{PID}/sessions/{sid}")

    # 2. Page: does any writable type carry html/script/bindings?
    cands = ["html", "script", "css", "bindings", "libraries", "description", "source", "body", "content", "layout"]
    code, out = call("probe_dashboard", "POST", f"/projects/{PID}/objects?branch={BRANCH}",
                     {"objects": {oid("probe/dash"): dict(type="dashboard", parent=A.MODEL, **{k: None for k in cands})}})
    rec["dashboard_probe"] = {"http": code, "body": json.dumps(out)[:1500]}
    print(rec["dashboard_probe"]["body"][:600])

    # 3. CAD parts
    pp, pa = {}, {}
    for p in parts:
        k = oid("cad/" + p["id"])
        nn = nodes.get(p["id"], [])
        doc = (f"Subsystem: {p['subsystem']}\nPart id: {p['id']}\nGLB node name: {', '.join(nn) if nn else '-'} "
               f"(concept-a.opt.glb; node extras.part_id = {p['id']})\nStatus: {p['status']}; make or buy: {p['make_or_buy']}; "
               f"material: {p.get('material') or '-'}\nFull description: {p['name']}")[:3000]
        pp[k] = dict(type="part", parent=SP[p["subsystem"]], name=f"{p['id']} " + p["name"].split(",")[0].split(" (")[0][:90],
                     shortName=p["id"], documentation=doc)
        at = [("Mass", p["mass_g"], "g")]
        if p.get("cg_xyz_m"):
            at += [(f"CG {ax}", round(v * 1000, 3), "mm") for ax, v in zip("xyz", p["cg_xyz_m"])]
        for nm, v, u in at:
            pa[oid(f"cad/{p['id']}/{nm}")] = dict(type="attribute", parent=k, name=nm, value=str(v), unit=u, kind="number")
        pa[oid(f"cad/{p['id']}/Subsystem")] = dict(type="attribute", parent=k, name="Subsystem", value=p["subsystem"], kind="string")
    A.post("cad_parts", pp)
    A.post("cad_part_attrs", pa)
    rec["parts_posted"] = len(pp)

    c, out = call("commit", "POST", f"/projects/{PID}/branches/{BRANCH}/commits", {"message": "Concept A 3D model and CAD parts, Claude via API"})
    rec["commit"] = {"http": c, "created": out.get("created") if isinstance(out, dict) else None}
    c, tree = call("tree", "GET", f"/projects/{PID}/tree?branch={BRANCH}")
    objs = tree.get("objects") or tree.get("tree") or tree.get("nodes") or []
    if isinstance(objs, dict):
        objs = [dict(v, id=i) for i, v in objs.items()]
    rec["tree_total"] = len(objs)
    rec["cad_parts_in_tree"] = sum(1 for o in objs if o.get("type") == "part" and o.get("parent") in SP.values())
    rec["viewer_parts"] = len(parts)
    rec["files_in_3d_package"] = [{k: o.get(k) for k in ("id", "type", "name")} for o in objs if o.get("parent") == M3]
    rec["page_objects"] = [{k: o.get(k) for k in ("id", "type", "name")} for o in objs if o.get("type") in ("dashboard", "document")]
    return fin(rec, a)


def fin(rec, a):
    rec["usage_after"] = A.usage()
    rec["usage_unchanged"] = rec.get("usage_before") == rec["usage_after"]
    rec["log"] = A.LOG
    for k in ("cad_parts_in_tree", "viewer_parts", "files_in_3d_package", "page_objects", "usage_unchanged", "tree_total"):
        print(k, rec.get(k))
    if a.out:
        json.dump(rec, open(a.out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
