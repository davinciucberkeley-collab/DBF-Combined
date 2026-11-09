"""Autodesk Fusion backend for fusionkit. Only importable inside Fusion (needs adsk.core / adsk.fusion).

Patterns reused from the previous design's scripts (fusion/build_vtol_fusion.py, fusion/build_joints_fusion.py):
offset construction planes with the normal-sign fix, closed sketch polylines -> profile pick -> extrude/revolve/loft,
occurrence transforms from Matrix3D, joints from point geometry with rotation limits widened by 0.1 deg (a value
exactly at the limit is rejected by the solver), copied appearances for colour.

Units: fusionkit is metres; the Fusion API is centimetres (CM = 100). Frame: aircraft x aft, y right, z up maps
straight onto Fusion X, Y, Z (use Preferences > General > Design > Default modeling orientation = Z up so the view
matches; geometry is the same either way).

UNVERIFIED-IN-FUSION (this file has not run in Fusion yet; first run by a teammate is the test):
  - Sketch.modelToSketchSpace on a sketch taken from comp.sketches uses component-local coordinates.
  - setByOffset sign handling for the three base planes in a non-root component (copied from the old scripts).
  - 3-D sketch lines for wires (points off the sketch plane).
  - Material names in MATERIALS; when none is found the body keeps Fusion's default material. The declared mass
    in interfaces.json is authoritative either way; end() prints Fusion's geometry mass next to it.
  - Joint direction for point geometry = component axes (the joint sketch is always on a Z-normal plane of the
    component, so X/Y/Z = that component's axes; a rotated ctx.part(rotate=) therefore turns about its own axes).
  - Fusion grounds the first occurrence added to a design ("ground to parent"); the old build_joints_fusion.py found
    that this blocked a joint whose moving side was that occurrence. joint() un-grounds the moving side of a
    revolute/slider joint before adding it.
  - A joint aligns BOTH joint frames (origin and axes), not only the origins. The joint-point sketches are Z-normal
    planes of each component, so for an unrotated component the frame is the aircraft frame and nothing moves. For
    a component placed with ctx.part(rotate=...) the two frames differ and Fusion will turn part a to match part b.
    joint() reports such joints as WARN in the build summary; check the placement in Fusion. (Fix if it bites:
    set JointInput.angle for Z rotations, or build the joint-point sketch on a plane that is world-aligned.)
  - datum(): planes are offset construction planes in a '00 Datums' component placed at the origin; points and
    axes are sketch points / construction lines in one sketch per datum (sketch points off the sketch plane, as for
    wires). Construction points/axes by Point3D/InfiniteLine3D are avoided (parametric designs reject them).
"""
import math
import re
import traceback

import adsk.core
import adsk.fusion

from fusionkit import Backend, AX, to3d

CM = 100.0
V = adsk.core.ValueInput
DIR = {'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JDIR = {'X': adsk.fusion.JointDirections.XAxisJointDirection,
        'Y': adsk.fusion.JointDirections.YAxisJointDirection,
        'Z': adsk.fusion.JointDirections.ZAxisJointDirection}

# our material text -> candidate Fusion Material Library names, first found wins. Keys are regexes matched as whole
# words (lower case), so "steel plate" is steel, not PLA, and "CF tube" / "CFRP" are both carbon.
MATERIALS = [
    (r'6061|7075', ['Aluminum 6061', 'Aluminum']),
    (r'alum\w*', ['Aluminum 6061', 'Aluminum']),
    (r'carbon|cfrp?', ['Carbon Fiber', 'Carbon Fiber Reinforced Polymer']),
    (r'petg', ['PET Plastic', 'Polyethylene Terephthalate', 'ABS Plastic']),
    (r'pla', ['PLA', 'ABS Plastic']),
    (r'pa6|pa12|nylon', ['Nylon 6', 'Nylon']),
    (r'tpu', ['Thermoplastic Polyurethane', 'Rubber, Silicone', 'Rubber']),
    (r'xps|eps|epp|foam', ['Polystyrene', 'Foam']),
    (r'ply\w*|birch|balsa', ['Plywood', 'Birch', 'Balsa', 'Wood']),
    (r'steel|stainless', ['Steel, Stainless 304', 'Steel']),
]
PALETTE = [(0.85, 0.85, 0.88), (0.35, 0.55, 0.85), (0.90, 0.60, 0.20), (0.30, 0.70, 0.45),
           (0.75, 0.35, 0.35), (0.55, 0.45, 0.75), (0.25, 0.25, 0.28), (0.85, 0.80, 0.30)]


def P3(p):
    """metres tuple -> Point3D in cm"""
    return adsk.core.Point3D.create(p[0] * CM, p[1] * CM, p[2] * CM)


class FusionBackend(Backend):
    name = 'fusion'

    def __init__(self, new_document=True):
        self.new_document = new_document
        self.app = adsk.core.Application.get()
        self.warnings = []            # (code, item, message) reported as WARN issues by end()
        self._appearances = {}
        self._materials = {}
        self._sub_colour = {}
        self.wiring = None
        self.datums_occ = None

    # ------------------------------------------------------------------ document
    def begin(self, title):
        if self.new_document:
            self.app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        self.design = adsk.fusion.Design.cast(self.app.activeProduct)
        self.design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        self.root = self.design.rootComponent
        try:
            self.root.name = title
        except Exception:
            pass

    def end(self, ctx):
        try:
            self.design.activateRootComponent()
            self.app.activeViewport.fit()
        except Exception:
            pass
        for code, item, msg in self.warnings:
            ctx.issue('WARN', code, item, msg)
        lines = ['%-10s %8s %10s  %s' % ('part', 'decl g', 'Fusion g', 'Fusion material')]
        for pid, c in sorted(ctx.components.items()):
            try:
                fm = c.native.physicalProperties.mass * 1000.0          # kg -> g (geometry x library density)
                mat = c.native.component.bRepBodies.item(0).material.name if c.native.component.bRepBodies.count else '-'
            except Exception:
                fm, mat = float('nan'), '?'
            lines.append('%-10s %8.0f %10.0f  %s' % (pid, c.mass_g or 0, fm, mat))
        return 'Fusion mass is geometry x library density (information only); declared mass is authoritative.\n' + \
            '\n'.join(lines)

    # ------------------------------------------------------------------ helpers
    def _plane(self, fc, axis, w):
        """Construction plane normal to axis at component-local coordinate w (m)."""
        base = {'X': fc.yZConstructionPlane, 'Y': fc.xZConstructionPlane, 'Z': fc.xYConstructionPlane}[axis]
        if abs(w) < 1e-12:
            return base
        n, d = base.geometry.normal, DIR[axis]
        s = 1.0 if (n.x * d[0] + n.y * d[1] + n.z * d[2]) > 0 else -1.0
        inp = fc.constructionPlanes.createInput()
        inp.setByOffset(base, V.createByReal(w * CM * s))
        pl = fc.constructionPlanes.add(inp)
        pl.isLightBulbOn = False
        return pl

    def _sketch(self, fc, axis, w, name):
        sk = fc.sketches.add(self._plane(fc, axis, w))
        sk.name = name
        return sk

    def _loop(self, sk, pts3d, smooth=False):
        """Closed loop through 3-D component-local points (m)."""
        S = [sk.modelToSketchSpace(P3(p)) for p in pts3d]
        if smooth:
            coll = adsk.core.ObjectCollection.create()
            for q in S:
                coll.add(q)
            sp = sk.sketchCurves.sketchFittedSplines.add(coll)
            sk.sketchCurves.sketchLines.addByTwoPoints(sp.endSketchPoint, sp.startSketchPoint)
            return
        L = sk.sketchCurves.sketchLines
        first = last = L.addByTwoPoints(S[0], S[1])
        for q in S[2:]:
            last = L.addByTwoPoints(last.endSketchPoint, q)
        L.addByTwoPoints(last.endSketchPoint, first.startSketchPoint)

    @staticmethod
    def _profile(sk, nloops=1):
        best, ba = None, -1.0
        for p in sk.profiles:
            a = p.areaProperties().area
            if (nloops == 1 or p.profileLoops.count == nloops) and a > ba:
                best, ba = p, a
        if best is None:
            for p in sk.profiles:
                a = p.areaProperties().area
                if a > ba:
                    best, ba = p, a
        if best is None:
            raise Exception('no closed profile in sketch ' + sk.name)
        return best

    def _material(self, text):
        key = (text or '').lower()
        if key in self._materials:
            return self._materials[key]
        found = None
        for kw, names in MATERIALS:
            if re.search(r'(?<![a-z0-9])(?:%s)(?![a-z0-9])' % kw, key):
                for libname in ('Fusion Material Library', 'Fusion 360 Material Library'):
                    lib = self.app.materialLibraries.itemByName(libname)
                    if lib is None:
                        continue
                    for n in names:
                        found = lib.materials.itemByName(n)
                        if found:
                            break
                    if found:
                        break
            if found:
                break
        self._materials[key] = found
        return found

    def _appearance(self, rgb):
        key = tuple(round(v, 3) for v in rgb)
        ap = self._appearances.get(key)
        if ap is None:
            nm = 'DBF_%02d%02d%02d' % tuple(int(round(v * 99)) for v in key)
            ap = self.design.appearances.itemByName(nm)
            if ap is None:
                lib = self.app.materialLibraries.itemByName('Fusion Appearance Library')
                base = None
                for bn in ('Plastic - Matte (White)', 'Paint - Enamel Glossy (White)', 'Plastic - Glossy (White)'):
                    base = lib.appearances.itemByName(bn) if lib else None
                    if base is not None:
                        break
                if base is None:
                    return None
                ap = self.design.appearances.addByCopy(base, nm)
                adsk.core.ColorProperty.cast(ap.appearanceProperties.itemByName('Color')).value = \
                    adsk.core.Color.create(int(key[0] * 255), int(key[1] * 255), int(key[2] * 255), 255)
            self._appearances[key] = ap
        return ap

    # ------------------------------------------------------------------ backend API
    def component(self, comp):
        m = adsk.core.Matrix3D.create()
        M = comp.matrix()
        m.setWithArray([M[0][0], M[0][1], M[0][2], M[0][3] * CM,
                        M[1][0], M[1][1], M[1][2], M[1][3] * CM,
                        M[2][0], M[2][1], M[2][2], M[2][3] * CM,
                        0, 0, 0, 1])
        occ = self.root.occurrences.addNewComponent(m)
        fc = occ.component
        fc.name = ('%s %s' % (comp.id, comp.name)).replace('/', '-')
        try:
            fc.description = '%s | %s | %s g | %s' % (comp.status, comp.material, comp.mass_g, comp.subsystem)
        except Exception:
            pass
        for k in ('id', 'subsystem', 'status', 'mass_g', 'material', 'make_or_buy'):
            fc.attributes.add('dbf', k, str(getattr(comp, k)))
        comp.native = occ

    def body(self, comp, shape):
        fc = comp.native.component
        tag = '%s_%d' % (comp.id, len(comp.shapes))
        feats = fc.features
        if shape.kind == 'prism':
            sk = self._sketch(fc, shape.axis, shape.offset, tag)
            for loop in shape.loops:
                self._loop(sk, [to3d(shape.axis, shape.offset, uv) for uv in loop])
            nrm = sk.xDirection.crossProduct(sk.yDirection)
            d = DIR[shape.axis]
            s = 1.0 if (nrm.x * d[0] + nrm.y * d[1] + nrm.z * d[2]) > 0 else -1.0
            inp = feats.extrudeFeatures.createInput(self._profile(sk, len(shape.loops)), NEW)
            inp.setDistanceExtent(False, V.createByReal(shape.depth * CM * s))
            feat = feats.extrudeFeatures.add(inp)
        elif shape.kind == 'revolve':
            k = AX[shape.axis]
            plane_axis, radial = {'X': ('Y', 2), 'Y': ('Z', 0), 'Z': ('Y', 0)}[shape.axis]
            c = shape.center
            sk = self._sketch(fc, plane_axis, c[AX[plane_axis]], tag)

            def pt(a, r):
                p = list(c)
                p[k] += a
                p[radial] += r
                return tuple(p)
            self._loop(sk, [pt(a, r) for a, r in shape.profile])
            ax = sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(P3(pt(0, 0))),
                                                            sk.modelToSketchSpace(P3(pt(0.01, 0))))
            ax.isConstruction = True
            inp = feats.revolveFeatures.createInput(self._profile(sk), ax, NEW)
            inp.setAngleExtent(False, V.createByReal(2.0 * math.pi))
            feat = feats.revolveFeatures.add(inp)
        elif shape.kind == 'loft':
            inp = feats.loftFeatures.createInput(NEW)
            for i, (o, loop) in enumerate(shape.sections):
                sk = self._sketch(fc, shape.axis, o, '%s_s%d' % (tag, i))
                self._loop(sk, [to3d(shape.axis, o, uv) for uv in loop], shape.smooth)
                inp.loftSections.add(self._profile(sk))
            feat = feats.loftFeatures.add(inp)
        else:
            raise ValueError('unknown shape kind ' + shape.kind)
        mat = self._material(comp.material)
        rgb = comp.rgb or self._sub_colour.setdefault(comp.subsystem, PALETTE[len(self._sub_colour) % len(PALETTE)])
        ap = self._appearance(rgb)
        for i in range(feat.bodies.count):
            b = feat.bodies.item(i)
            b.name = shape.name or tag
            if mat:
                b.material = mat
            if ap:
                b.appearance = ap
        for sk in fc.sketches:
            sk.isLightBulbOn = False      # the settable one (isVisible is the computed state); as in the old scripts

    def _point_geometry(self, comp, world):
        fc = comp.native.component
        loc = comp.to_local(world)
        sk = self._sketch(fc, 'Z', loc[2], 'jp_%d' % fc.sketches.count)
        sp = sk.sketchPoints.add(sk.modelToSketchSpace(P3(loc)))
        sk.isLightBulbOn = False
        return adsk.fusion.JointGeometry.createByPoint(sp.createForAssemblyContext(comp.native))

    def joint(self, j, comp_a, comp_b):
        rotated = [c.id for c in (comp_a, comp_b) if c.rotate]
        if rotated:                                # see the module docstring: Fusion aligns both joint frames
            self.warnings.append(('joint', j.edge, 'joins rotated component %s: Fusion may turn %s to align the '
                                  'joint frames; check its placement (UNVERIFIED-IN-FUSION)' % (', '.join(rotated), j.a)))
        if j.kind != 'rigid':
            try:                                   # a grounded first occurrence cannot move (see module docstring)
                if comp_a.native.isGroundToParent:
                    comp_a.native.isGroundToParent = False
            except Exception:
                pass
        ji = self.root.joints.createInput(self._point_geometry(comp_a, j.origin), self._point_geometry(comp_b, j.origin))
        if j.kind == 'rigid':
            ji.setAsRigidJointMotion()
        elif j.kind == 'revolute':
            ji.setAsRevoluteJointMotion(JDIR[j.axis])
        else:
            ji.setAsSliderJointMotion(JDIR[j.axis])
        jt = self.root.joints.add(ji)
        jt.name = j.edge
        if j.limits:
            lo, hi = j.limits
            if j.kind == 'revolute':
                L = jt.jointMotion.rotationLimits
                lo, hi = math.radians(lo - 0.1), math.radians(hi + 0.1)
            else:
                L = jt.jointMotion.slideLimits
                lo, hi = lo * CM, hi * CM
            L.isMinimumValueEnabled = True
            L.minimumValue = lo
            L.isMaximumValueEnabled = True
            L.maximumValue = hi
            L.isRestValueEnabled = True
            L.restValue = 0.0
        j.native = jt

    def datum(self, d):
        if self.datums_occ is None:
            self.datums_occ = self.root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            self.datums_occ.component.name = '00 Datums (DATUMS.md)'
        fc = self.datums_occ.component
        if d.kind == 'plane':
            pl = self._plane(fc, d.axis, d.offset)
            if pl in (fc.xYConstructionPlane, fc.xZConstructionPlane, fc.yZConstructionPlane):
                d.native = pl                       # base plane: keep its own name, Fusion does not allow renaming
                return
            pl.isLightBulbOn = True
            pl.name = d.name
            d.native = pl
            return
        sk = fc.sketches.add(fc.xYConstructionPlane)
        sk.name = d.name
        if d.kind == 'point':
            d.native = sk.sketchPoints.add(sk.modelToSketchSpace(P3(d.p)))
        else:
            k = AX[d.axis]
            a, b = list(d.p), list(d.p)
            a[k] -= 0.30
            b[k] += 0.30
            ln = sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(P3(a)), sk.modelToSketchSpace(P3(b)))
            ln.isConstruction = True
            d.native = ln

    def wire(self, w):
        if self.wiring is None:
            self.wiring = self.root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            self.wiring.component.name = 'Wiring (routes)'
        fc = self.wiring.component
        sk = fc.sketches.add(fc.xYConstructionPlane)
        sk.name = w.edge
        L = sk.sketchCurves.sketchLines
        last = L.addByTwoPoints(sk.modelToSketchSpace(P3(w.points[0])), sk.modelToSketchSpace(P3(w.points[1])))
        for p in w.points[2:]:
            last = L.addByTwoPoints(last.endSketchPoint, sk.modelToSketchSpace(P3(p)))
        w.native = sk

