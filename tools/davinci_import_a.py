"""T-037 import (AM-047): committed concept A data (git 73656c93) -> DaVinci project "API Test", new branch.

Reads ONLY `git show 73656c93:<path>`; never the working tree. Token from DAVINCI_API_KEY / git-ignored .env
(never printed or written). Never sends agent prompts. Stdlib only. Never writes main.
Idempotent: object id = uuid5(NS, source key); a rerun re-posts the same ids (duplicates are reported, not made).
Run:  python -I tools/davinci_import_a.py [--out docs/integration/davinci-import-2026-11-23.json]
"""
import json, os, sys, csv, io, re, uuid, argparse, subprocess, tempfile, importlib.util
import urllib.request, urllib.error

BASE = "https://davinci-app.com/api/v2"
PID = "b53fed82-b072-43c2-9994-de76de845d93"
SHA = "73656c93"
BRANCH = "concept-a-snapshot-73656c93"
MODEL = "00000000-0000-0000-0000-0000000model"
NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/davinciucberkeley-collab/DBF-Combined/concept-a-snapshot")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "github.com/davinciucberkeley-collab/DBF-Combined"
KEY = ""
LOG = []


def load_key():
    k = os.environ.get("DAVINCI_API_KEY", "")
    envf = os.path.join(ROOT, ".env")
    if not k and os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.strip().startswith("DAVINCI_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    return k


def git_show(path):
    return subprocess.run(["git", "show", f"{SHA}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")


def oid(key):
    return str(uuid.uuid5(NS, key))


def call(name, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={
        "Authorization": "Bearer " + KEY, "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            code, out = r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        code = e.code
        try:
            out = json.loads(e.read().decode())
        except Exception:
            out = {"raw": "unreadable"}
    err = ""
    if isinstance(out, dict) and out.get("error"):
        err = out["error"].get("code", "") + " " + json.dumps(out["error"].get("details", out["error"].get("message", "")))[:500]
    LOG.append({"step": name, "http": code, "err": err})
    print(f"{name:<28} {method:<6} HTTP {code} {err[:300]}")
    return code, out


def usage():
    _, u = call("usage", "GET", "/usage")
    t = u.get("totals", {})
    return {"usd": t.get("amountUsd"), "events": t.get("eventCount"), "asOf": u.get("asOf")}


def post(name, objs):
    res, items = [], list(objs.items())
    for i in range(0, len(items), 40):
        res.append(call(f"{name}[{i}]", "POST", f"/projects/{PID}/objects?branch={BRANCH}",
                        {"objects": dict(items[i:i + 40])}))
    return res


def md_rows(text, prefix):
    return [[c.strip() for c in l.strip().strip("|").split("|")] for l in text.splitlines() if l.startswith(prefix)]


def main():
    global KEY
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    KEY = load_key()
    if not KEY.startswith(("dav_ak_live_", "dav_ak_test_")):
        print("no token")
        return 2
    rec = {"branch": BRANCH, "sha": SHA}
    rec["usage_before"] = usage()

    bomtxt = git_show("redesign/qp/A/BOM-A.csv")
    bom = list(csv.DictReader(io.StringIO(bomtxt)))
    mass = json.loads(git_show("redesign/qp/A/sitl/cad_mass.json"))
    reqs = md_rows(git_show("redesign/qp/A/REQUIREMENTS-A.md"), "| A-")
    tptxt = git_show("redesign/qp/A/TEST-PLAN-O4B.md").splitlines()
    first = next(i for i, l in enumerate(tptxt) if l.startswith("| TP-"))
    tpblock = []
    for l in tptxt[first:]:          # only the first contiguous TP table (the s2 index); later tables reuse the ids
        if not l.startswith("| TP-"):
            break
        tpblock.append(l)
    tps = md_rows(chr(10).join(tpblock), "| TP-")
    td = tempfile.mkdtemp()
    open(os.path.join(td, "BOM-A.csv"), "w", encoding="utf-8", newline="").write(bomtxt)
    open(os.path.join(td, "bom_a.py"), "w", encoding="utf-8").write(git_show("redesign/qp/A/bom_a.py"))
    spec = importlib.util.spec_from_file_location("bom_a", os.path.join(td, "bom_a.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    T = m.totals()
    bom_total = round(T["total"], 2)
    rec["bom_total_computed"] = bom_total
    rec["bom_parts"] = {k: round(v, 2) for k, v in T.items()}
    print("BOM total", bom_total, "(expected 1939.17)")
    if abs(bom_total - 1939.17) > 0.005:
        rec["blocker"] = "bom total mismatch"
        return fin(rec, a)

    code, br = call("create_branch", "POST", f"/projects/{PID}/branches", {"name": BRANCH, "sourceBranch": "main"})
    if code not in (201, 409):
        return fin(rec, a)

    P = {k: oid("pkg/" + k) for k in ("root", "hard", "parts", "bom", "reqs", "tests")}
    if post("package_root", {P["root"]: dict(
            type="package", parent=MODEL, name=f"Concept A (snapshot {SHA}, 2026-11-23)",
            documentation=f"Snapshot of committed data; the elevon chord change T-101 is not included. Source: {SRC}")})[0][0] != 201:
        return fin(rec, a)
    sub = {
        P["hard"]: dict(type="package", parent=P["root"], name="Hard constraints"),
        P["parts"]: dict(type="package", parent=P["root"], name="Parts"),
        P["bom"]: dict(type="package", parent=P["root"], name="Bill of materials"),
        P["reqs"]: dict(type="package", parent=P["root"], name="Requirements (REQUIREMENTS-A)"),
        P["tests"]: dict(type="package", parent=P["root"], name="Bench and flight tests"),
    }
    if post("packages", sub)[0][0] != 201:
        return fin(rec, a)

    # BOM
    o2, o3, ext_total = {}, {}, 0.0
    for r_ in bom:
        k = oid("bom/" + r_["id"])
        q, u = float(r_["qty"]), float(r_["unit_usd"])
        ext_total += q * u
        o2[k] = dict(type="item", parent=P["bom"], name=r_["item"][:200], shortName=r_["id"],
                     documentation=(f"subsystem {r_['subsystem']}; ship group {r_['ship_group']}; flag {r_['flag']}; status {r_['status']}; "
                                    f"source {r_['source_url']}; checked {r_['date_checked']}. {r_['note']}")[:1800])
        for nm, val, unit in (("Unit cost", u, "USD"), ("Quantity", q, None), ("Extended cost", round(q * u, 2), "USD"),
                              ("Vendor", r_["ship_group"], None)):
            f = dict(type="attribute", parent=k, name=nm, value=str(val), kind="string" if nm == "Vendor" else "number")
            if unit:
                f["unit"] = unit
            o3[oid(f"bom/{r_['id']}/{nm}")] = f
    tot_id = oid("bom/total")
    o3[tot_id] = dict(type="attribute", parent=P["bom"], name="BOM total", value=f"{bom_total:.2f}", unit="USD", kind="number",
                      documentation=(f"Committed bom_a.py totals() at {SHA}: goods x 1.1025 + shipping + FAA $5 + crash reserve "
                                     f"${T['reserve']:.2f} = ${bom_total:,.2f}. Sum of qty x unit cost alone is ${ext_total:,.2f}."))
    rec["bom_ext_sum"] = round(ext_total, 2)
    post("bom_items", o2)
    post("bom_attrs", o3)

    # Parts from cad_mass.json (scalar items only; the file has no per-part list)
    pp, pa = {}, {}

    def part(key, name, doc, attrs):
        k = oid("part/" + key)
        pp[k] = dict(type="part", parent=P["parts"], name=name, documentation=doc)
        for nm, v, unit in attrs:
            pa[oid(f"part/{key}/{nm}")] = dict(type="attribute", parent=k, name=nm, value=str(v), unit=unit, kind="number")

    part("aircraft", "Aircraft (CAD basic mass)", "cad_mass.json mass_basic_kg and CG, CAD axes (x aft, y right, z up).",
         [("Mass", round(mass["mass_basic_kg"] * 1000, 2), "g"), ("CG x", round(mass["cg_x_m"] * 1000, 3), "mm"),
          ("CG y", round(mass["cg_y_m"] * 1000, 3), "mm"), ("CG z", round(mass["cg_z_m"] * 1000, 3), "mm")])
    I = mass["I_cad_axes_kgm2"]
    part("inertia", "Aircraft inertia (CAD axes)", "cad_mass.json I_cad_axes_kgm2.",
         [("I" + n, I["I" + n], "kg*m^2") for n in ("xx", "yy", "zz")])
    e = mass["elevon"]
    part("elevon", "Elevon (one, hinge data)", "cad_mass.json elevon block (pre-T-101 chord).",
         [("Balance mass each", e["balance_mass_each_g"], "g"), ("Span start y0", e["y0"] * 1000, "mm"), ("Span end y1", e["y1"] * 1000, "mm"),
          ("Hinge inertia one elevon", e["hinge_inertia_one_elevon_kgm2"], "kg*m^2"),
          ("CG aft of hinge, unbalanced", round(e["cg_aft_of_hinge_unbalanced_m"] * 1000, 3), "mm")])
    part("motor_station", "Motor station", "cad_mass.json motor_station_y/z, prop_hub_x_aft_of_LE_m (positions; no mass listed).",
         [("Position y", mass["motor_station_y"] * 1000, "mm"), ("Position z", mass["motor_station_z"] * 1000, "mm"),
          ("Prop hub x aft of LE", round(mass["prop_hub_x_aft_of_LE_m"] * 1000, 3), "mm")])
    part("fin", "Fin", "cad_mass.json fin_y_m, fin_h_m (no mass listed).",
         [("Position y", mass["fin_y_m"] * 1000, "mm"), ("Height", round(mass["fin_h_m"] * 1000, 1), "mm")])
    part("pack", "Battery pack slot", "cad_mass.json pack_x_m range (slot travel; no mass listed).",
         [("Pack x min", mass["pack_x_m"][0] * 1000, "mm"), ("Pack x max", mass["pack_x_m"][1] * 1000, "mm")])
    post("parts", pp)
    post("part_attrs", pa)
    mass_attr = oid("part/aircraft/Mass")

    # Requirements A-*
    rq = {}
    for row in reqs:
        rq[oid("req/" + row[0])] = dict(
            type="requirement", parent=P["reqs"], shortName=row[0], name=(f"{row[0]} " + row[1])[:200],
            documentation=f"Requirement: {row[1]}\nClass: {row[2]}\nDisp: {row[3]}\nBasis: {' | '.join(row[4:])}"[:3000])
    post("requirements", rq)

    # Tests TP-n
    ts = {}
    for row in tps:
        row = row + ["-"] * (8 - len(row))
        ts[oid("test/" + row[0])] = dict(
            type="test", parent=P["tests"], shortName=row[0], name=f"{row[0]} " + re.split(r"[.:]", row[1])[0][:90], status="pending",
            documentation=(f"Purpose / closes: {row[1]}\nPass number: {row[4] if len(row) > 4 else '-'}\n"
                           f"Specimen: {row[2]}\nRig: {row[3] if len(row) > 3 else '-'}")[:3000])
    post("tests", ts)

    # Hard constraints
    H = [
        ("HC-1", "Budget: $2,000 total physical spend",
         "Total physical budget $2,000 (hardware, spares, batteries, test gear, shipping, tax); Makers Pass outside. Check: BOM total <= 2000.",
         f"[{tot_id}] <= 2000"),
        ("HC-2", "Schedule: built and flight-tested by end of April 2027",
         "Built and flight-tested by 2027-04-30. Check text only (a date, no equation).", None),
        ("HC-3", "Portable: under 25 kg, fits one to two car trunks",
         "Team of 4 moves it routinely; hard cap under 25 kg (55 lb); packed aircraft fits one car trunk, two at most. "
         "Mass check: CAD basic mass (g) <= 25000; trunk fit is a documentation check.", f"[{mass_attr}] <= 25000"),
        ("HC-4", "3-D physics gates, no exemptions",
         "Every build step and the assembled aircraft pass assembly_check.py and collide.py --glb with no part interpenetration, "
         "no open wire ends and no exemptions; flight cases (C5 landing, SITL) pass against their limits. Check text only.", None),
        ("HC-5", "CAD fidelity",
         "Every part modelled to its real shape and dimensions from the vendor drawing or data sheet; no stand-in disks or boxes; "
         "unknown dimensions marked, never invented. Check text only.", None),
        ("HC-6", "Enclosed wiring",
         "Wires inside arm tubes, wing-core channels, fairings or covers; any exposed wire listed with length and reason, "
         "kept to the minimum. Check text only.", None),
    ]
    hr, hc = {}, {}
    for hid, nm, doc, eq in H:
        k = oid("hc/" + hid)
        hr[k] = dict(type="requirement", parent=P["hard"], shortName=hid, name=nm, documentation=doc + " Source: CLAUDE.md hard constraints.")
        c = dict(type="constraint", parent=k, name=hid + " check", kind="analysis" if eq else "inspection",
                 documentation=doc if eq is None else "Equation check: " + eq)
        if eq:
            c["value"] = eq
        hc[oid("hc/" + hid + "/c")] = c
    post("hard_req", hr)
    rc = post("hard_constraints", hc)
    if rc[0][0] != 201:
        for v in hc.values():
            v.pop("value", None)
            v["kind"] = "inspection"
        rec["equation_refused"] = rc[0][1]
        post("hard_constraints_doc_only", hc)

    c, out = call("commit", "POST", f"/projects/{PID}/branches/{BRANCH}/commits", {"message": "Concept A snapshot import, Claude via API"})
    rec["commit"] = {"http": c, "created": out.get("created") if isinstance(out, dict) else None}

    c, tree = call("tree", "GET", f"/projects/{PID}/tree?branch={BRANCH}")
    objs = tree.get("objects") or tree.get("tree") or tree.get("nodes") or []
    if isinstance(objs, dict):
        objs = [dict(v, id=k) for k, v in objs.items()]
    byp = {}
    for o in objs:
        byp.setdefault(o.get("parent"), []).append(o)
    n = lambda pkg, t=None: sum(1 for o in byp.get(pkg, []) if t is None or o.get("type") == t)
    rec["counts"] = {
        "Hard constraints (requirements)": [n(P["hard"], "requirement"), len(H)],
        "Parts (parts)": [n(P["parts"], "part"), len(pp)],
        "Bill of materials (items)": [n(P["bom"], "item"), len(bom)],
        "Requirements (REQUIREMENTS-A)": [n(P["reqs"], "requirement"), len(reqs)],
        "Bench and flight tests": [n(P["tests"], "test"), len(ts)],
        "tree_objects_total": len(objs), "tree_keys": list(tree.keys()) if isinstance(tree, dict) else None}
    rec["package_ids"] = P

    c, ses = call("open_session", "POST", f"/projects/{PID}/sessions", {"branch": BRANCH, "ttlSeconds": 600})
    sid = (ses or {}).get("sessionId") or (ses or {}).get("id")
    spots = {"BOM total": tot_id, "Aircraft mass": mass_attr, "P01 unit cost": oid("bom/P01/Unit cost"),
             "A-U1 requirement": oid("req/A-U1"), "TP-1 test": oid("test/TP-1")}
    rec["spots"] = {}
    if sid:
        try:
            for nm, i in spots.items():
                c, o = call("read " + nm, "POST", f"/projects/{PID}/sessions/{sid}/tools/invoke",
                            {"toolbox": "Core", "tool": "ReadObject", "params": {"objectId": i}})
                rec["spots"][nm] = {"http": c, "result": json.dumps(o)[:700]}
        finally:
            call("close_session", "DELETE", f"/projects/{PID}/sessions/{sid}")
    return fin(rec, a)


def fin(rec, a):
    rec["usage_after"] = usage()
    rec["usage_unchanged"] = rec.get("usage_before") == rec["usage_after"]
    rec["log"] = LOG
    print("usage", rec["usage_before"], "->", rec["usage_after"])
    if a.out:
        json.dump(rec, open(a.out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
