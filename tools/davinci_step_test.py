"""T-037 Part 3: upload a STEP file to API Test / branch concept-a-snapshot-73656c93 and report the object created.
Usage: python -I tools/davinci_step_test.py <step file> <out json>   (stdlib; token from .env, never printed; no agent prompt)
Does not commit; commit is a separate step (tools/davinci_step_commit.py or a manual call)."""
import json, os, sys, uuid, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import davinci_import_a as A
import davinci_import_a_3d as T

PID, BRANCH = A.PID, A.BRANCH


def upload_step(url, grant, name, data):
    bd = "----dav" + uuid.uuid4().hex
    body = (f'--{bd}\r\nContent-Disposition: form-data; name="objectName"\r\n\r\n{name}\r\n'
            f'--{bd}\r\nContent-Disposition: form-data; name="file"; filename="CGE-001.step"\r\n'
            f'Content-Type: application/step\r\n\r\n').encode() + data + f"\r\n--{bd}--\r\n".encode()
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
    step, out = sys.argv[1], sys.argv[2]
    A.KEY = A.load_key()
    assert A.KEY.startswith(("dav_ak_live_", "dav_ak_test_")), "no token"
    rec = {"usage_before": A.usage()}
    data = open(step, "rb").read()
    PK = A.oid("pkgstep/test")
    A.post("pkg", {PK: dict(type="package", parent=A.MODEL, name="STEP test",
                            documentation="STEP upload test: CGE-001 hub mesh from concept-a.glb at 73656c93 (19,000 triangles, faceted B-rep).")})
    FID = A.oid("pkgstep/file")
    c, ses = A.call("open_session", "POST", f"/projects/{PID}/sessions", {"branch": BRANCH, "ttlSeconds": 900})
    sid = (ses or {}).get("sessionId") or (ses or {}).get("id")
    dp = (ses or {}).get("dataPlane") or {}
    try:
        owner = dp.get("ownerId") or ses.get("ownerId")
        url = (f"{dp['url'].rstrip('/')}/api/v1/file/upload/{owner}/{dp.get('userId') or owner}/{dp.get('projectKey') or PID + '--' + BRANCH}/"
               f"{dp.get('connectionId') or 'headless-' + sid}/{PK}")
        code, resp = upload_step(url, dp["token"], "CGE-001.step", data)
        print("upload HTTP", code, json.dumps(resp)[:500] if code != 200 else "")
        rec["upload"] = {"http": code, "response": json.dumps(resp)[:1500]}
    finally:
        if sid:
            A.call("close_session", "DELETE", f"/projects/{PID}/sessions/{sid}")
    c, tree = A.call("tree", "GET", f"/projects/{PID}/tree?branch={BRANCH}")
    objs = tree.get("objects") or tree.get("tree") or tree.get("nodes") or []
    if isinstance(objs, dict):
        objs = [dict(v, id=i) for i, v in objs.items()]
    rec["children_of_pkg"] = [o for o in objs if o.get("parent") == PK]
    print(json.dumps(rec["children_of_pkg"])[:1500])
    rec["pk"] = PK
    rec["usage_after"] = A.usage()
    json.dump(rec, open(out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
