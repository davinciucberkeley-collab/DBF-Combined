"""Pure-python backend: builds nothing, counts what a real backend would be asked to make.

check.py uses it. All geometry facts check.py needs (bounding boxes, volumes, centroids) are computed from the
recorded shape data in fusionkit, so the stub stays trivial. It catches: modules that crash, bad shape data
(empty loops, negative radii, zero-depth prisms), joints/wires naming unknown parts. It cannot catch real kernel
failures (self-intersecting profiles, failed lofts): those are UNVERIFIED-IN-FUSION.
"""
from fusionkit import Backend


class StubBackend(Backend):
    name = 'stub'

    def __init__(self):
        self.counts = {'components': 0, 'bodies': 0, 'joints': 0, 'wires': 0, 'datums': 0}

    def component(self, comp):
        self.counts['components'] += 1
        comp.native = ('stub', comp.id)

    def body(self, comp, shape):
        if shape.kind == 'prism':
            if abs(shape.depth) < 1e-6:
                raise ValueError('%s: prism depth is zero' % comp.id)
            if any(len(l) < 3 for l in shape.loops):
                raise ValueError('%s: prism loop needs >= 3 points' % comp.id)
        elif shape.kind == 'revolve':
            if len(shape.profile) < 3 or max(r for _, r in shape.profile) <= 0:
                raise ValueError('%s: revolve profile needs >= 3 points and r > 0' % comp.id)
        elif shape.kind == 'loft':
            if len(shape.sections) < 2 or any(len(l) < 3 for _, l in shape.sections):
                raise ValueError('%s: loft needs >= 2 sections of >= 3 points' % comp.id)
        else:
            raise ValueError('unknown shape kind ' + shape.kind)
        self.counts['bodies'] += 1

    def joint(self, joint, comp_a, comp_b):
        if joint.kind != 'rigid' and joint.axis not in ('X', 'Y', 'Z'):
            raise ValueError('%s joint axis must be X, Y or Z' % joint.kind)
        self.counts['joints'] += 1

    def wire(self, wire):
        if len(wire.points) < 2:
            raise ValueError('wire needs >= 2 points')
        self.counts['wires'] += 1

    def datum(self, d):
        if d.kind == 'plane' and (d.axis not in ('X', 'Y', 'Z') or d.offset is None):
            raise ValueError('datum %s: plane needs axis X|Y|Z and offset' % d.name)
        if d.kind in ('point', 'axis') and (d.p is None or len(d.p) != 3):
            raise ValueError('datum %s: %s needs p = (x, y, z)' % (d.name, d.kind))
        self.counts['datums'] += 1

    def end(self, ctx):
        return 'stub: %(components)d components, %(bodies)d bodies, %(joints)d joints, %(wires)d wires, '                '%(datums)d datums' % self.counts
