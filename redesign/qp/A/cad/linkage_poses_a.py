"""linkage_poses_a.py - host side of `collide_a.py --linkage-poses` (T-020, category: interference during motion, mesh).
For each elevon angle delta, places every part of the elevon linkage at its kinematic pose (the T-018 solution in
mechanism/linkage_core.py, the same geometry as the analytic sweep mechanism/elevon_sweep_collision.py) and writes the job
that a_linkage_blender.py runs against the CAD meshes:
  elevon group (MEC-004 horn, MEC-005 clevis pin, WNG-006 elevon, WNG-007, WNG-010 damper rotor): rotation by delta about the hinge;
  arm group (MEC-002 arm, MEC-008 keeper, HWC-002 arm screw, which is clamped to the servo output): rotation by theta about the
      vertical spline axis;
  rod (MEC-003, rigid, Z-bend leg + clevis): frame (u, e2, e3) with u = unit vector Z-bend joint -> horn hole, e2 = y made
      orthogonal to u (cheek-hole axis as close to the pin axis y as a rigid rod allows), e3 = u x e2; translation so that the
      neutral Z-bend joint lands on arm_pt(theta). Neutral = the CAD pose (rod parallel to x, joint at ROD_Z = the 'mid' state).
Clevis pin MEC-005 (pin_with='rod', default): rides with the rod (the CAD seats it in the cheek holes with zero clearance, so a pin kept on the horn
is forced through a cheek cut it cannot follow: 0.88 deg out-of-line gives a 0.258 mm false hit at +21 deg in the first test run); the horn
hole carries the out-of-line angle, as K5 assumes. pin_with='horn' reproduces the old grouping (sensitivity run).
The damper stator WNG-009 is NOT held out (its axis is the hinge line, the rotor turns about it: the pose is exact). Nothing is held out.
Pairs checked: every moved part against every fixed part, and moved parts of DIFFERENT groups against each other (pairs inside one
group keep their static relative pose, already covered by the static pose, which is included first).
Units: metres (the job format of collision/collide.py).
"""
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ANGLES = [-21, -20, -18, -15, -12, -9, -6, -3, 0, 3, 6, 9, 12, 15, 18, 20, 21]
STATES = ('mid', 'lo', 'hi')
ARM_GROUP = ('MEC-002-', 'MEC-008-', 'HWC-002-')
ROD = 'MEC-003-'
PIN = 'MEC-005-'
# declared design contacts (labels only: they are NOT exempt; every hit counts against the 0.05 mm tolerance)
DECLARED = {
    ('MEC-002', 'MEC-003'): 'Z-bend leg in the 1.3 mm arm hole (leg 1.2 mm dia, end 0.25 mm inside the arm underside); at zj=lo the rod rests on the arm top (rod bottom tangent, by design)',
    ('MEC-003', 'MEC-008'): 'keeper bridge over the Z-bend: top stop of the leg freedom, rod top bears on it at zj=hi (by design, D-212 rev 3)',
    ('MEC-003', 'MEC-005'): 'clevis pin through the cheek holes (ctx.seat: cheeks are cut to the pin; seated joint)',
    ('MEC-004', 'MEC-005'): 'clevis pin in the 1.1 mm horn hole (same elevon group: relative pose constant)',
    ('MEC-001', 'MEC-002'): 'arm bottom sits on the servo case top (ARM_Z0 = SV_Z1)',
    ('MEC-001', 'HWC-002'): 'arm screw seated in the output shaft thread (ctx.seat)',
    ('HWC-002', 'MEC-002'): 'arm screw through the arm hub bore',
    ('HWC-002', 'MEC-008'): 'arm screw through the keeper hole',
    ('MEC-002', 'MEC-008'): 'keeper clamped on the arm top by the arm screw (same group: constant)',
    ('WNG-009', 'WNG-010'): 'rotor sleeve in the stator annulus (0.30 mm gaps), concentric on the hinge line',
}


def _mm(m, n):
    return [[sum(m[i][k] * n[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _frame(rot_cols, t):
    return [[rot_cols[0][0], rot_cols[1][0], rot_cols[2][0], t[0]], [rot_cols[0][1], rot_cols[1][1], rot_cols[2][1], t[1]],
            [rot_cols[0][2], rot_cols[1][2], rot_cols[2][2], t[2]], [0, 0, 0, 1]]


def _apply(M, p):
    return [sum(M[i][j] * p[j] for j in range(3)) + M[i][3] for i in range(3)]


def build_poses(ctx, comps, edges, angles, states, collide, kin, pin_with='rod'):
    """Returns (poses, checks). poses: job entries; checks: max errors of the self-checks (metres)."""
    by_id = {c['id']: c for c in comps}
    groups = {j.edge: (j, g) for j, g in collide.moving_groups(ctx, edges)}
    side_group = {}
    for j, g in groups.values():
        side_group['R' if j.origin[1] > 0 else 'L'] = (j, g)
    import numpy as np
    poses = [{'name': 'static', 'over': {}, 'R': {}, 'moved': None, 'skip_with': None, 'groups': {}, 'delta': None, 'state': None,
              'theta': None}]
    err = {'horn_hole': 0.0, 'rod_clevis_end': 0.0, 'rod_joint': 0.0, 'arm_tip': 0.0}
    for state in states:
        kin.ZJ = kin.ZJ_STATES[state]
        for dd in angles:
            d = math.radians(dd)
            over, motion, grp, names = {}, {}, {}, []
            theta = {}
            for s, sy in (('R', 1), ('L', -1)):
                j, g = side_group[s]
                th = kin.theta_of_delta(d, sy)
                theta[s] = math.degrees(th)
                # elevon group: rotation about the hinge
                Re = collide.rot_about(collide.axis_vec(j.axis), j.origin, dd)
                for p in g:
                    if p in by_id and not (pin_with == 'rod' and p.startswith(PIN)):
                        over[p], motion[p], grp[p] = _mm(Re, by_id[p]['matrix']), Re, 'elevon-' + s
                # arm group: rotation about the vertical spline axis
                Ra = collide.rot_about((0, 0, 1), (kin.SV_XS, sy * kin.SERVO_Y, 0.0), math.degrees(th))
                for pre in ARM_GROUP:
                    p = pre + s
                    if p in by_id:
                        over[p], motion[p], grp[p] = _mm(Ra, by_id[p]['matrix']), Ra, 'arm-' + s
                # rod: rigid frame (u, e2, e3)
                pa, ph = kin.arm_pt(th, sy), kin.horn_pt(d, sy)
                u = (ph - pa) / np.linalg.norm(ph - pa)
                e2 = np.array([0.0, 1.0, 0.0]) - u[1] * u
                e2 /= np.linalg.norm(e2)
                e3 = np.cross(u, e2)
                pa0 = np.array([kin.SV_XS, sy * (kin.SERVO_Y - kin.ARM_R), kin.ROD_Z])       # CAD neutral Z-bend joint (rod axis height)
                ph0 = np.array([kin.HORN_XH, sy * (kin.SERVO_Y - kin.ARM_R), kin.ROD_Z])     # CAD neutral horn hole centre
                Rm = np.array([u, e2, e3]).T
                t = pa - Rm @ pa0
                Mr = _frame([list(u), list(e2), list(e3)], list(t))
                rp = ROD + s
                over[rp], motion[rp], grp[rp] = _mm(Mr, by_id[rp]['matrix']), Mr, 'rod-' + s
                if pin_with == 'rod':                    # clevis pin: seated in the cheek holes (exact-fit seat), so it rides with the rod; the
                    pp = PIN + s                         # horn hole (1.1 mm on the 1.0 mm pin, K5) carries the out-of-line angle
                    over[pp], motion[pp], grp[pp] = _mm(Mr, by_id[pp]['matrix']), Mr, 'rod-' + s
                # self-checks: the rigid motions reproduce the kinematic points
                hole0 = [kin.HORN_XH, sy * (kin.SERVO_Y - kin.ARM_R), kin.ROD_Z]
                err['horn_hole'] = max(err['horn_hole'], float(np.linalg.norm(np.array(_apply(Re, hole0)) - ph)))
                err['rod_clevis_end'] = max(err['rod_clevis_end'], float(np.linalg.norm(np.array(_apply(Mr, ph0)) - ph)))
                err['rod_joint'] = max(err['rod_joint'], float(np.linalg.norm(np.array(_apply(Mr, pa0)) - pa)))
                arm_tip0 = [kin.SV_XS, sy * (kin.SERVO_Y - kin.ARM_R), kin.ZJ]
                err['arm_tip'] = max(err['arm_tip'], float(np.linalg.norm(np.array(_apply(Ra, arm_tip0)) - pa)))
                names.append('%s theta %+.3f' % (s, math.degrees(th)))
            poses.append({'name': 'linkage zj=%s delta %+g deg' % (state, dd), 'over': over, 'R': motion, 'moved': sorted(over),
                          'skip_with': [], 'groups': grp, 'delta': float(dd), 'state': state, 'theta_deg': theta})
    return poses, err


def step_justification(mech_out, angles, states):
    """From the analytic sweep (0.5 deg grid, AR-003): per pair, how much lower the 0.5 deg minimum between two chosen angles is than the
    smaller of the two chosen-angle values (undersampling loss), max slope, and the minimum separation."""
    rows = []
    for state in states:
        suf = '' if state == 'mid' else '_z' + state
        d = {}
        with open(os.path.join(mech_out, 'linkage_sweep_collision%s.csv' % suf), newline='') as f:
            for r in csv.DictReader(f):
                if r['side'] == 'R':
                    d.setdefault((r['part_a'], r['part_b']), []).append((float(r['delta_deg']), float(r['separation_mm (negative = penetration)'])))
        gs = sorted(set(float(a) for a in angles))
        for k, v in d.items():
            v.sort()
            mn = min(v, key=lambda t: t[1])
            if mn[1] > 3.0:
                continue
            loss = 0.0
            for a, b in zip(gs, gs[1:]):
                seg = [s for x, s in v if a - 1e-9 <= x <= b + 1e-9]
                ends = [s for x, s in v if abs(x - a) < 1e-9 or abs(x - b) < 1e-9]
                if seg and ends:
                    loss = max(loss, min(ends) - min(seg))
            slope = max(abs(v[i + 1][1] - v[i][1]) / (v[i + 1][0] - v[i][0]) for i in range(len(v) - 1))
            rows.append({'state': state, 'a': k[0], 'b': k[1], 'min_sep_mm': mn[1], 'at_delta_deg': mn[0], 'undersampling_loss_mm': round(loss, 4),
                         'max_slope_mm_per_deg': round(slope, 4), 'worst_case_between_samples_mm': round(slope * 1.5, 4)})
    rows.sort(key=lambda r: r['min_sep_mm'])
    return rows


# analytic solid -> CAD part
A2P = {'arm': 'MEC-002', 'keeper spacer': 'MEC-008', 'keeper bridge': 'MEC-008', 'rod': 'MEC-003', 'rod Z-bend pin': 'MEC-003',
       'clevis sleeve': 'MEC-003', 'clevis cheek -1': 'MEC-003', 'clevis cheek +1': 'MEC-003', 'horn blade': 'MEC-004', 'horn rib': 'MEC-004',
       'clevis pin': 'MEC-005', 'elevon slab': 'WNG-006', 'servo case': 'MEC-001', 'servo boot': 'MEC-001', 'pocket wall fore': 'WNG-001', 'pocket wall side outboard': 'WNG-001',
       'pocket wall side inboard': 'WNG-001', 'core aft block': 'WNG-001'}


def analytic_part_pairs(mech_out, state, angles):
    """AR-003 analytic separation (mm, side R) per CAD part pair and angle: minimum over the solid pairs that map to the part pair."""
    suf = '' if state == 'mid' else '_z' + state
    out = {}
    with open(os.path.join(mech_out, 'linkage_sweep_collision%s.csv' % suf), newline='') as f:
        for r in csv.DictReader(f):
            if r['side'] != 'R':
                continue
            pa, pb = A2P.get(r['part_a']), A2P.get(r['part_b'])
            if not pa or not pb or pa == pb:
                continue
            key = tuple(sorted((pa, pb)))
            dd = float(r['delta_deg'])
            s = float(r['separation_mm (negative = penetration)'])
            slot = out.setdefault(key, {})
            slot[dd] = min(slot.get(dd, 1e9), s)
    return out


def part_key(pid):
    return pid.rsplit('-', 1)[0] if pid[-2:] in ('-R', '-L') else pid


def write_md(rep, path, tol):
    L = ['# Linkage-poses mesh gate (T-020, interference during motion, CAD meshes)', '',
         'Generated by `collide_a.py --linkage-poses` (host: `linkage_poses_a.py`, Blender: `a_linkage_blender.py`). Tolerance %g mm.' % tol, '']
    L += ['| State | delta deg | theta R deg | pairs > %g mm | deepest hit mm | hits listed (>= %g mm) | wall s |' % (tol, rep['report_mm']), '|---|---|---|---|---|---|---|']
    for pz in rep['poses']:
        n = sum(1 for h in pz['hits'] if h['depth_mm'] > tol)
        deep = max([h['depth_mm'] for h in pz['hits']] or [0.0])
        L.append('| %s | %s | %s | %d | %.3f | %d | %s |' % (pz.get('state') or 'static', '-' if pz.get('delta') is None else '%+g' % pz['delta'],
                 '-' if not pz.get('theta_deg') else '%+.2f' % pz['theta_deg']['R'], n, deep, len(pz['hits']), pz.get('seconds', '-')))
    L.append('')
    for pz in rep['poses']:
        if not pz['hits']:
            continue
        L += ['## %s' % pz['name'], '', '| Part A | Part B | Depth mm | At (x, y, z) mm | Declared contact | Result |', '|---|---|---|---|---|---|']
        for h in sorted(pz['hits'], key=lambda h: -h['depth_mm']):
            ka = tuple(sorted((part_key(h['a']), part_key(h['b']))))
            L.append('| %s | %s | %.3f | %s | %s | %s |' % (h['a'], h['b'], h['depth_mm'], ', '.join('%.1f' % v for v in h['at_mm']),
                     DECLARED.get(ka, '-'), 'FAIL' if h['depth_mm'] > tol else 'below tol'))
        L.append('')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
