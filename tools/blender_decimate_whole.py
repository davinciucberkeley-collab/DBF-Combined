"""T-037 (2026-11-24): merge the 129 per-part mesh JSONs into one mesh and decimate it in Blender, for the lite whole-aircraft STEP.
Run: blender.exe -b --factory-startup --python tools/blender_decimate_whole.py -- <mesh dir> <out.json> [ratio 0.25] [min_polys 400]
Then: python -I tools/mesh_to_step.py <out.json> <out.step> "<name>". Lite = ratio 0.25 / min 400 polys (12.7 MB STEP); extra-lite = 0.06 / 150 (4.8 MB)."""
import bpy, bmesh, json, glob, os, sys
src = sys.argv[sys.argv.index("--")+1]; out = sys.argv[sys.argv.index("--")+2]
RATIO = float(sys.argv[sys.argv.index("--")+3]) if len(sys.argv) > sys.argv.index("--")+3 else 0.25
MINP = int(sys.argv[sys.argv.index("--")+4]) if len(sys.argv) > sys.argv.index("--")+4 else 400
V, F = [], []
for p in sorted(glob.glob(os.path.join(src, "*.json"))):
    d = json.load(open(p))
    me = bpy.data.meshes.new("m"); me.from_pydata(d["v"], [], d["f"]); me.update()
    ob = bpy.data.objects.new("o", me); bpy.context.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bm.to_mesh(me); bm.free()
    if len(me.polygons) > MINP:
        mod = ob.modifiers.new("d", "DECIMATE"); mod.ratio = RATIO
        bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier="d")
    me = ob.data; o = len(V)
    V += [list(v.co) for v in me.vertices]
    for poly in me.polygons:
        vs = list(poly.vertices)
        for k in range(1, len(vs)-1): F.append([vs[0]+o, vs[k]+o, vs[k+1]+o])
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me)
json.dump({"v": V, "f": F}, open(out, "w")); print("DONE", len(V), len(F))
