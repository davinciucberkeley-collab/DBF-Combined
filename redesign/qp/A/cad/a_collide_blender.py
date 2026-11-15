"""a_collide_blender.py - runs INSIDE Blender: collision/collide_blender.py (unmodified) with one fix applied at run time.
Finding (QP-3 CAD): manufacturing/blender_mesh._body orients each mesh with bmesh.ops.recalc_face_normals on a mesh whose raw
winding is mixed (prism caps vs sides). For some placements (here every part rotated about X by more than 90 deg, y < 0) the
result is INSIDE OUT (negative signed volume); collide_blender.inside() then reports no point inside the body, so an
interpenetration of that part, or a wire end seated in it, is not detected / not found. This wrapper reverses any body whose
signed volume is negative. The K09-L files are not edited.
    blender -b --factory-startup -P a_collide_blender.py -- <_job.json> <report.json>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), 'collision')
sys.path.insert(0, COLL)
import bmesh                       # noqa: E402
import collide_blender as cb       # noqa: E402

_orig = cb.bm_._body
FLIPPED = []


def _body(name, shape_json, M, col, grow=0.0):
    ob = _orig(name, shape_json, M, col, grow)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.to_mesh(ob.data)
        FLIPPED.append(name)
    bm.free()
    return ob


cb.bm_._body = _body
if __name__ == '__main__':
    cb.main()
    print('a_collide_blender: %d bodies were inside-out after recalc and were reversed' % len(FLIPPED))
