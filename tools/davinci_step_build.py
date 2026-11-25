"""T-037 Part 4: per-part mesh JSON (from the Blender export of concept-a.glb at 73656c93) -> <part id>.step + validation with gmsh.
Usage: python -I tools/davinci_step_build.py <mesh dir> <out step dir> <out csv>
mesh dir holds <part id>.json = {"v": mm vertices, "f": triangles, "glb_bbox": [[min,max]x3] (mm), "nonmanifold_edges": n}.
Per part: STEP (planar merge, see mesh_to_step.py), gmsh load (volumes, bbox, volume) and errors against the GLB node bbox and
the welded mesh volume. Needs gmsh (python module) for the check only. Decimation is NOT done here (not needed if total <= 100 MB)."""
import csv, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesh_to_step as M


def gm_check(path):
    import gmsh
    gmsh.initialize(["-v", "0"])
    gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)  # bbox from the faceted shape; default OCC bounds are loose for open sheets
    try:
        gmsh.open(path)
        vol = gmsh.model.getEntities(3)
        bb = gmsh.model.getBoundingBox(-1, -1)
        mass = sum(gmsh.model.occ.getMass(3, t) for _, t in vol) if vol else None
        return len(vol), len(gmsh.model.getEntities(2)), [[bb[0], bb[3]], [bb[1], bb[4]], [bb[2], bb[5]]], mass
    finally:
        gmsh.finalize()


def main():
    md, od, oc = sys.argv[1:4]
    os.makedirs(od, exist_ok=True)
    rows = []
    for f in sorted(glob.glob(os.path.join(md, "*.json"))):
        pid = os.path.basename(f)[:-5]
        m = json.load(open(f))
        V, F = m["v"], m["f"]
        path = os.path.join(od, pid + ".step")
        st = M.write_step(V, F, pid, path)
        cl = [Fc for Fc in M.components(V, F) if M.is_closed(Fc)]
        vol_mesh = sum(abs(M.solid_volume(V, Fc)) for Fc in cl) if cl else None
        nv, ns, bb, mass = gm_check(path)
        gb = m["glb_bbox"]
        bbe = max(abs(bb[i][j] - gb[i][j]) for i in range(3) for j in range(2))
        ve = (abs(mass - vol_mesh) / vol_mesh * 100) if (mass is not None and vol_mesh and len(cl) == st["bodies"]) else None
        rows.append(dict(part=pid, triangles=len(F), faces=st["faces"], mb=round(os.path.getsize(path) / 1e6, 3), bodies=st["bodies"], closed_bodies=st["closed_bodies"],
                         gmsh_volumes=nv, bbox_err_mm=round(bbe, 5), mesh_volume_mm3=round(vol_mesh, 3) if vol_mesh else "",
                         step_volume_mm3=round(mass, 3) if mass is not None else "", volume_err_pct=round(ve, 5) if ve is not None else "",
                         decimated="no"))
        print(pid, rows[-1]["triangles"], rows[-1]["faces"], rows[-1]["mb"], nv, rows[-1]["bbox_err_mm"], rows[-1]["volume_err_pct"], flush=True)
    with open(oc, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("TOTAL MB", round(sum(r["mb"] for r in rows), 2), "parts", len(rows), "faces", sum(r["faces"] for r in rows))


if __name__ == "__main__":
    main()
