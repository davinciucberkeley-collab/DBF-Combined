"""Triangle mesh -> ISO-10303-21 AP214 STEP (faceted B-rep), pure Python, mm.

Usage: python -I tools/mesh_to_step.py mesh.json out.step "product name"
mesh.json: {"v": [[x,y,z],...] (mm), "f": [[i,j,k],...]}.
Closed manifold mesh -> FACETED_BREP over a CLOSED_SHELL of ADVANCED_FACEs on PLANEs (FACE_OUTER_BOUND + POLY_LOOP).
Otherwise -> SHELL_BASED_SURFACE_MODEL over an OPEN_SHELL (same faces).
"""
import json, sys
from collections import Counter


def is_closed(F):
    c = Counter()
    for a, b, d in F:
        for u, v in ((a, b), (b, d), (d, a)):
            c[(u, v)] += 1
    return all(n == 1 and c.get((v, u), 0) == 1 for (u, v), n in c.items())


def write_step(V, F, name, path, schema="AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }"):
    closed = is_closed(F)
    L = []
    n = [0]

    def add(s):
        n[0] += 1
        L.append(f"#{n[0]}={s};")
        return n[0]

    q = name.replace("'", "''")
    ac = add("APPLICATION_CONTEXT('automotive design')")
    add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2001,#{ac})")
    pc = add(f"PRODUCT_CONTEXT('',#{ac},'mechanical')")
    pr = add(f"PRODUCT('{q}','{q}','',(#{pc}))")
    pdf = add(f"PRODUCT_DEFINITION_FORMATION('','',#{pr})")
    pdc = add(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{ac},'design')")
    pd = add(f"PRODUCT_DEFINITION('design','',#{pdf},#{pdc})")
    pds = add(f"PRODUCT_DEFINITION_SHAPE('','',#{pd})")
    pts = [add(f"CARTESIAN_POINT('',({x:.6f},{y:.6f},{z:.6f}))") for x, y, z in V]
    faces = []
    for a, b, c in F:
        pl = add(f"POLY_LOOP('',(#{pts[a]},#{pts[b]},#{pts[c]}))")
        fb = add(f"FACE_OUTER_BOUND('',#{pl},.T.)")
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = V[a], V[b], V[c]
        ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
        nx, ny, nz = uy * (z2 - z0) - uz * (y2 - y0), uz * (x2 - x0) - ux * (z2 - z0), ux * (y2 - y0) - uy * (x2 - x0)
        ln = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0
        ul = (ux * ux + uy * uy + uz * uz) ** 0.5 or 1.0
        o3 = add(f"CARTESIAN_POINT('',({x0:.6f},{y0:.6f},{z0:.6f}))")
        dn = add(f"DIRECTION('',({nx/ln:.9f},{ny/ln:.9f},{nz/ln:.9f}))")
        dr = add(f"DIRECTION('',({ux/ul:.9f},{uy/ul:.9f},{uz/ul:.9f}))")
        pa = add(f"AXIS2_PLACEMENT_3D('',#{o3},#{dn},#{dr})")
        pln = add(f"PLANE('',#{pa})")
        faces.append(add(f"ADVANCED_FACE('',(#{fb}),#{pln},.T.)"))
    fl = ",".join(f"#{i}" for i in faces)
    if closed:
        sh = add(f"CLOSED_SHELL('',({fl}))")
        body = add(f"FACETED_BREP('{q}',#{sh})")
        rtype = "ADVANCED_BREP_SHAPE_REPRESENTATION"
    else:
        sh = add(f"OPEN_SHELL('',({fl}))")
        body = add(f"SHELL_BASED_SURFACE_MODEL('{q}',(#{sh}))")
        rtype = "MANIFOLD_SURFACE_SHAPE_REPRESENTATION"
    ax = add("CARTESIAN_POINT('',(0.,0.,0.))")
    d1 = add("DIRECTION('',(0.,0.,1.))")
    d2 = add("DIRECTION('',(1.,0.,0.))")
    a2 = add(f"AXIS2_PLACEMENT_3D('',#{ax},#{d1},#{d2})")
    u1 = add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
    u2 = add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
    u3 = add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
    un = add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-05),#{u1},'distance_accuracy_value','')")
    gc = add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{un}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{u1},#{u2},#{u3}))REPRESENTATION_CONTEXT('',''))")
    rep = add(f"{rtype}('',(#{a2},#{body}),#{gc})")
    add(f"SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})")
    hdr = ("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('" + q + "'),'2;1');\n"
           "FILE_NAME('" + q + ".step','2026-11-23',('Claude'),(''),'mesh_to_step.py','mesh_to_step.py','');\n"
           f"FILE_SCHEMA(('{schema}'));\nENDSEC;\nDATA;\n")
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(hdr + "\n".join(L) + "\nENDSEC;\nEND-ISO-10303-21;\n")
    return {"closed": closed, "vertices": len(V), "triangles": len(F), "entities": n[0]}


if __name__ == "__main__":
    m = json.load(open(sys.argv[1]))
    print(write_step(m["v"], m["f"], sys.argv[3], sys.argv[2]))
