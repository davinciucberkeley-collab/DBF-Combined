"""k09kit - shared CAD helpers for the K09-L quad tailsitter (redesign/CONFIGURATION.md). Owner: A5 (CAD lead).

fusionkit is configuration-independent; this file holds what every K09-L module needs, so the wing, fins,
propulsion, landing, pod and mechanisms designers build from the same numbers and the same datums:

    import fusionkit as fk, k09kit as k9
    def build(ctx):
        sec = k9.section(ctx)                                  # wing section coords (B2's .dat, else placeholder)
        hx = ctx.D('DP-HINGE')                                 # named datums, see DATUMS.md
        core = ctx.part('WNG-001'); k9.wing_core(core, sec, ...)
        k9.quad(ctx, {'UR': 'PRP-001', 'UL': 'PRP-002', 'LR': 'PRP-003', 'LL': 'PRP-004'})

| Helper | Use |
|---|---|
| `val(params, key, unit)` / `ctx.value(key, unit)` | number from a params.json leaf (unit-checked) |
| `datum_specs(params)`, `build_datums(ctx)` | the datum sheet: planes, points, axes from params.json (DATUMS.md) |
| `read_dat(path)`, `reflex_placeholder(t_c, camber)`, `section(ctx)` | airfoil coordinates (Selig or Lednicer .dat) |
| `section_loop(coords, chord, le, x0, x1)` | closed (x, z) loop of a chord range (core box, elevon), TE >= te_min |
| `surface_z(coords, chord, frac, side)` | upper/lower surface height (hinge line, spar cover) |
| `wing_core`, `elevon`, `hinge_point` | one-piece core with elevon cut-outs, elevon panels, tape-hinge axis |
| `spar_y`, `tube_z` | spanwise spar, vertical motor tube |
| `fin_plate`, `half_fin` | foam-board fin centred on its plane; upper/lower half-fin whose root follows the skin (R1) |
| `core_block` | printed through-core block: section-shaped plug between two chord stations (tube + spar bores) |
| `strut` | straight rectangular strip between two points (fin brace: DX-COLLAR-<st> -> DX-ANCHOR-<st>) |
| `local(sub)`, `lval(local, key, unit, default)` | a subsystem's own params.json (datums D3 / D5 own) |
| `fin_brace_points`, `foot_contact_z`, `motor_face_x` | R3 brace ends, foot pad contact, motor plate face |
| `bundle` | harness bundle body: axis-aligned cylinder legs along a route (gives a lumped bundle part its body) |
| `box_frame`, `box_shell` | transport box placed around the aircraft (DX-BOX), six wall bodies (flight: false) |
| `motor_envelope`, `prop_disc`, `prop_keepout` | motor can + shaft along -x, prop disc, prop strike keep-out |
| `quad(ctx, ids)`, `pair(ctx, r, l)` | UR -> UL, LR, LL by exact mirrors; R -> L |
| `hover_pose(params)`, `to_hover(p, params)`, `hover_ground(ctx, exempt)` | stand-on-fin-tips attitude; ground keep-out |

Run as a script:  python -I redesign/fusion/k09kit.py --datums-md   rewrites the generated table in DATUMS.md
                  python -I redesign/fusion/k09kit.py --check       exit 1 if DATUMS.md is stale against params.json
There is no tilt joint on K09-L (fixed motors); the only moving joints are the four elevon hinges.
Python 3 stdlib only. Geometry that depends on Fusion's kernel is UNVERIFIED-IN-FUSION (see README).
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
PARAMS = os.path.join(REDESIGN, 'params', 'params.json')
DATUMS_MD = os.path.join(HERE, 'DATUMS.md')
STATIONS = ('UR', 'UL', 'LR', 'LL')
SIGNS = {'UR': (1, 1), 'UL': (-1, 1), 'LR': (1, -1), 'LL': (-1, -1)}     # (y sign, z sign)

# Standards (STANDARDS.md section 5); designers may not loosen these without a change request to A5.
TE_MIN_M = 0.0006            # hot-wired XPS trailing edge cannot be a knife edge
FOAMBOARD_T_M = 0.0048       # fallback only: params.json#fins.board_t_m (CHANGE-LOG D-15) is read first
PROP_BLADE_HALF_M = 0.008    # half the axial thickness of an 11 in prop at the hub (APC MR class) - EST
CAN_D_FALLBACK_M = 0.038


# ----------------------------------------------------------------------------- parameters
def load_params(path=PARAMS):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def val(params, key, unit=None):
    """Value of a params.json leaf; checks the unit when given."""
    d = params
    for k in key.split('.'):
        if not isinstance(d, dict) or k not in d:
            raise KeyError('params.json has no "%s"' % key)
        d = d[k]
    if isinstance(d, dict) and 'value' in d:
        if unit is not None and d.get('unit') != unit:
            raise KeyError('params.json "%s" is in %s, not %s' % (key, d.get('unit'), unit))
        return d['value']
    return d


def _P(ctx_or_params):
    return ctx_or_params.params if hasattr(ctx_or_params, 'params') else ctx_or_params


def board_t(params):
    """One foam-board layer (m): params.json#fins.board_t_m, else the 3/16 in fallback."""
    try:
        return val(params, 'fins.board_t_m', 'm')
    except KeyError:
        return FOAMBOARD_T_M


def fin_thickness(params):
    """Fin thickness (m) = layers x foam-board thickness (D3 may change the layup through fins/params.json)."""
    return val(params, 'fins.layers') * board_t(params)


def hinge_frac(params):
    """Hinge line as a fraction of chord from the LE = 1 - elevon chord fraction."""
    return 1.0 - val(params, 'wing.elevon.chord_frac')


def elevon_spans(params):
    """[(y0, y1), ...] for the four panels, left inboard/outboard then right, y0 < y1."""
    yi, yo = val(params, 'wing.elevon.inboard_y_m', 'm'), val(params, 'wing.elevon.outboard_y_m', 'm')
    out = []
    for s in (-1, 1):
        for a, b in (yi, yo):
            out.append(tuple(sorted((s * a, s * b))))
    return sorted(out)


def span_gaps(params):
    """Spanwise ranges of the core's aft strip that are NOT elevon (pod gap, fin gaps, tips)."""
    h = val(params, 'wing.span_m', 'm') / 2
    gaps, y = [], -h
    for a, b in elevon_spans(params):
        if a > y + 1e-9:
            gaps.append((y, a))
        y = b
    if h > y + 1e-9:
        gaps.append((y, h))
    return gaps


# ----------------------------------------------------------------------------- airfoils
def read_dat(path):
    """Airfoil .dat (Selig: TE upper -> LE -> TE lower; or Lednicer: counts line then upper LE->TE, lower LE->TE)
    -> Selig-ordered [(x, y)] normalised to chord 1."""
    with open(path, encoding='utf-8', errors='replace') as f:
        rows = []
        for line in f.read().splitlines()[1:]:
            nums = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', line)
            if len(nums) >= 2:
                rows.append((float(nums[0]), float(nums[1])))
    if rows and rows[0][0] > 1.5:                         # Lednicer: first row = point counts
        nu, nl = int(rows[0][0]), int(rows[0][1])
        up, lo = rows[1:1 + nu], rows[1 + nu:1 + nu + nl]
        rows = list(reversed(up)) + lo[1:]
    xs = [p[0] for p in rows]
    x0, c = min(xs), max(xs) - min(xs)
    return [((x - x0) / c, y / c) for x, y in rows]


def reflex_placeholder(t_c, camber=0.016, x_reflex=0.80, n=60):
    """PLACEHOLDER reflexed section, used only when subsystems/wing/<airfoil>.dat is missing (S5010 is there since
    2026-11-09, CR-B2-04): NACA 00xx thickness at t_c with a cubic
    camber line yc = k x (1 - x)(x_reflex - x) (positive forward, reflexed aft), scaled to max camber `camber`.
    Status UNVERIFIED. Selig order, chord 1."""
    f = lambda x: x * (1 - x) * (x_reflex - x)
    k = camber / max(f(i / 400.0) for i in range(401))
    pts_u, pts_l = [], []
    for i in range(n + 1):
        x = (1 - math.cos(math.pi * i / n)) / 2
        yt = 5 * t_c * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)
        yc = k * f(x)
        pts_u.append((x, yc + yt))
        pts_l.append((x, yc - yt))
    return list(reversed(pts_u)) + pts_l[1:]


def section(ctx_or_params, dat=None):
    """Wing section coordinates: `dat` (or subsystems/wing/<airfoil>.dat when B2 has written it) else the
    placeholder at params.json t/c. Returns (coords, source text)."""
    P = _P(ctx_or_params)
    name = re.sub(r'[^a-z0-9]', '', str(val(P, 'wing.airfoil')).lower())
    cands = [dat] if dat else [os.path.join(REDESIGN, 'subsystems', 'wing', name + '.dat'),
                               os.path.join(REDESIGN, 'subsystems', 'wing', 'airfoil', name + '.dat')]
    for c in cands:
        if c and os.path.exists(c):
            return read_dat(c), os.path.relpath(c, REDESIGN).replace('\\', '/')
    return reflex_placeholder(val(P, 'wing.t_c')), 'PLACEHOLDER reflex_placeholder(t_c) - UNVERIFIED'


def _surfaces(coords):
    """(upper, lower) as lists LE -> TE."""
    i = min(range(len(coords)), key=lambda j: coords[j][0])
    a, b = list(reversed(coords[:i + 1])), coords[i:]
    if sum(p[1] for p in a) / len(a) < sum(p[1] for p in b) / len(b):
        a, b = b, a
    return a, b


def _interp(surf, x):
    for (x0, y0), (x1, y1) in zip(surf, surf[1:]):
        if (x0 - x) * (x1 - x) <= 0 and x1 != x0:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return surf[0][1] if x <= surf[0][0] else surf[-1][1]


def surface_y(coords, frac, side='upper', chord=None, te_min=TE_MIN_M):
    """Normalised surface ordinate at chord fraction `frac` (with the TE opened to te_min if chord is given)."""
    up, lo = _surfaces(coords)
    yu, yl = _interp(up, frac), _interp(lo, frac)
    if chord:
        gap_te = _interp(up, 1.0) - _interp(lo, 1.0)
        need = te_min / chord - gap_te
        if need > 0 and frac > 0.8:
            d = need / 2 * (frac - 0.8) / 0.2
            yu, yl = yu + d, yl - d
    return yu if side == 'upper' else yl


def surface_z(coords, chord, frac, side='upper', le_z=0.0):
    """Surface height (m, aircraft z) at chord fraction `frac` of a section of chord `chord` with LE at le_z."""
    return le_z + surface_y(coords, frac, side, chord) * chord


def section_loop(coords, chord, le=(0.0, 0.0), x0=0.0, x1=1.0, n=32, te_min=TE_MIN_M):
    """Closed loop (x, z) for a Y-normal plane: chord range x0..x1 of the section, cosine-spaced, upper x1 -> x0
    then lower x0 -> x1 (same order as fusionkit.airfoil). The TE is opened to te_min (foam practice)."""
    xs = [x0 + (x1 - x0) * (1 - math.cos(math.pi * i / n)) / 2 for i in range(n + 1)]
    up = [(le[0] + x * chord, le[1] + surface_y(coords, x, 'upper', chord, te_min) * chord) for x in xs]
    lo = [(le[0] + x * chord, le[1] + surface_y(coords, x, 'lower', chord, te_min) * chord) for x in xs]
    return list(reversed(up)) + (lo[1:] if x0 == 0 else lo)


def thickness_at(coords, chord, frac):
    return (surface_y(coords, frac, 'upper') - surface_y(coords, frac, 'lower')) * chord


# ----------------------------------------------------------------------------- subsystem-local numbers
_LOCAL = {}


def local(sub):
    """redesign/subsystems/<sub>/params.json (cached; {} when the file does not exist yet)."""
    if sub not in _LOCAL:
        path = os.path.join(REDESIGN, 'subsystems', sub, 'params.json')
        try:
            with open(path, encoding='utf-8') as f:
                _LOCAL[sub] = json.load(f)
        except (OSError, ValueError):
            _LOCAL[sub] = {}
    return _LOCAL[sub]


def lval(LP, key, unit=None, default=None):
    """Value of a subsystem params.json leaf (dotted key from the file root), unit-checked; `default` when the key
    (or the file) is missing, so the framework still builds before the designer has published the number."""
    try:
        return val(LP, key, unit)
    except KeyError:
        if default is None:
            raise
        return default


def fin_brace_points(params, coords=None):
    """Brace end points of the R3 braced fin (D3, subsystems/fins/params.json#fin_detail): {st: (collar_end,
    anchor_end)}. Collar end = centre of the station-collar brace ear (tube axis x, inboard of the ring, ear
    mid-height, the ear top 0.5 mm below the mount grip); anchor end = brace slot centre in the anchor on the spar line
    at |y| brace.anchor_y_m, half the anchor's proud height above the upper (below the lower) skin. Same rule as
    subsystems/fins/fusion/fins.py geometry()['brace_ends'] (tests/test_framework.py cross-checks)."""
    P, F = params, local('fins')
    l = lambda k, u, d: lval(F, 'fin_detail.' + k, u, d)
    coords = coords or section(P)[0]
    c = val(P, 'wing.chord_m', 'm')
    xt, yf = val(P, 'fins.tube.x_m', 'm'), val(P, 'fins.y_m', 'm')
    xs = val(P, 'wing.spar.x_m', 'm')
    r_b = val(P, 'fins.tube.od_m', 'm') / 2 + l('bond_gap_m', 'm', 0.00015)
    z_ear = (val(P, 'fins.tube.length_m', 'm') / 2 - l('mount.grip_m', 'm', 0.012) - l('station_collar.gap_m', 'm', 0.0005)
             - l('station_collar.ear_h_m', 'm', 0.012) / 2)
    y_ear = yf - r_b - l('station_collar.ring_wall_m', 'm', 0.0016) - l('station_collar.ear_len_m', 'm', 0.010) / 2
    y_an, proud = l('brace.anchor_y_m', 'm', 0.242), l('anchor.proud_m', 'm', 0.008)
    out = {}
    for st in STATIONS:
        sy, sz = SIGNS[st]
        za = surface_z(coords, c, xs / c, 'upper' if sz > 0 else 'lower') + sz * proud / 2
        out[st] = ((xt, sy * y_ear, sz * z_ear), (xs, sy * y_an, za))
    return out


def foot_contact_z(params):
    """|z| of the foot pad contact (tip-over pivot): D5's pad outer edge less its edge round
    (subsystems/landing/params.json#landing.pad, CL-D5-CONTACT-Z 0.218, CHANGE-LOG D-30); the fin tip if D5 has not
    published it."""
    L = local('landing')
    try:
        return val(L, 'landing.pad.z_outer_m', 'm') - val(L, 'landing.pad.edge_r_m', 'm')
    except KeyError:
        return val(params, 'fins.half_height_m', 'm')


def motor_face_x(params):
    """Motor base plate face on the motor axis (CHANGE-LOG D-28: x 0.0309): ahead of the tube front face by the
    printed mount's bore gap, collar wall and face_ahead (subsystems/fins/params.json#fin_detail.mount); the tube
    front face (DP-MOUNT) if D3 has not published them."""
    F = local('fins')
    l = lambda k: lval(F, 'fin_detail.' + k, 'm', 0.0)
    return (val(params, 'fins.tube.x_m', 'm') - val(params, 'fins.tube.od_m', 'm') / 2 - l('bond_gap_m')
            - l('mount.collar_wall_m') - l('mount.face_ahead_m'))


# ----------------------------------------------------------------------------- datums
def datum_specs(params):
    """The K09-L datum sheet, every entry from params.json. [(name, kind, geometry dict, params key, note)].
    Names: DP- plane, DA- axis, DX- point (DATUMS.md section 3)."""
    P = params
    c, b = val(P, 'wing.chord_m', 'm'), val(P, 'wing.span_m', 'm')
    xs, zs = val(P, 'wing.spar.x_m', 'm'), val(P, 'wing.spar.z_m', 'm')
    yf, hf = val(P, 'fins.y_m', 'm'), val(P, 'fins.half_height_m', 'm')
    xt = val(P, 'fins.tube.x_m', 'm')
    xm, xp = val(P, 'propulsion.stations.x_mount_m', 'm'), val(P, 'propulsion.stations.x_prop_plane_m', 'm')
    ym, zm = val(P, 'propulsion.stations.y_m', 'm'), val(P, 'propulsion.stations.z_m', 'm')
    foot = val(P, 'cg.foot_height_m', 'm')
    xh = c * hinge_frac(P)
    pod_l, pod_w, pod_h = val(P, 'pod.size_m', 'm')
    pod_x, pod_z = val(P, 'pod.x_le_m', 'm'), val(P, 'pod.z_base_m', 'm')
    od = val(P, 'fins.tube.od_m', 'm')
    spar_half = val(P, 'wing.spar.length_m', 'm') / 2
    zc, brace = foot_contact_z(P), fin_brace_points(P)
    S = []
    add = lambda name, kind, key, note, **g: S.append((name, kind, g, key, note))
    add('DP-SYM', 'plane', 'frame.symmetry_plane', 'symmetry plane; ctx.mirror(plane="XZ")', axis='Y', offset=0.0)
    add('DP-CHORD', 'plane', 'frame.origin', 'wing chord plane; mirror plane for upper/lower motors', axis='Z', offset=0.0)
    add('DP-LE', 'plane', 'wing.le_x_m', 'wing leading edge = frame origin', axis='X', offset=val(P, 'wing.le_x_m', 'm'))
    add('DP-TE', 'plane', 'wing.te_x_m', 'wing and fin trailing edge', axis='X', offset=val(P, 'wing.te_x_m', 'm'))
    add('DP-SPAR', 'plane', 'wing.spar.x_m', 'spar centreline station (%.1f %% chord)' % (100 * xs / c), axis='X', offset=xs)
    add('DP-HINGE', 'plane', 'wing.elevon.chord_frac', 'elevon hinge line = c (1 - chord_frac)', axis='X', offset=xh)
    add('DP-CG', 'plane', 'cg.x_target_m', 'CG target station (range in cg.x_range_m)', axis='X', offset=val(P, 'cg.x_target_m', 'm'))
    add('DP-POD-LE', 'plane', 'pod.x_le_m', 'pod front face', axis='X', offset=pod_x)
    add('DP-TUBE', 'plane', 'fins.tube.x_m', 'motor-tube centreline station = fin LE', axis='X', offset=xt)
    add('DP-MOUNT', 'plane', 'propulsion.stations.x_mount_m', 'tube front face = tube x - tube OD/2 (D-28: stays here)',
        axis='X', offset=xm - od / 2)
    add('DP-MOTOR-FACE', 'plane', 'fins/params.json#fin_detail.mount', 'motor base plate face on the motor axis (D-28); '
        'the plate is canted 7 deg about this point', axis='X', offset=motor_face_x(P))
    add('DP-PROP', 'plane', 'propulsion.stations.x_prop_plane_m', 'propeller disc plane (all four props)', axis='X', offset=xp)
    add('DP-GROUND', 'plane', 'cg.foot_height_m', 'ground in hover = TE + foot (D-30: 48 mm); nothing but feet beyond it',
        axis='X', offset=c + foot)
    for s, tag in ((1, 'R'), (-1, 'L')):
        add('DP-FIN-' + tag, 'plane', 'fins.y_m', 'fin mid-plane, motor stations, through-core block', axis='Y', offset=s * yf)
        add('DP-TIP-' + tag, 'plane', 'wing.span_m', 'wing tip', axis='Y', offset=s * b / 2)
        add('DP-SPAR-END-' + tag, 'plane', 'wing.spar.length_m', 'spar end; foam outboard is unspanned', axis='Y', offset=s * spar_half)
    for s, tag in ((1, 'U'), (-1, 'L')):
        add('DP-MOTOR-' + tag, 'plane', 'propulsion.stations.z_m', 'upper / lower motor axis height', axis='Z', offset=s * zm)
    add('DP-POD-BASE', 'plane', 'pod.z_base_m', 'pod floor on the upper skin', axis='Z', offset=pod_z)
    add('DA-SPAR', 'axis', 'wing.spar.x_m', 'spar axis, along Y', axis='Y', p=(xs, 0.0, zs))
    for s, tag in ((1, 'R'), (-1, 'L')):
        add('DA-TUBE-' + tag, 'axis', 'fins.tube.length_m', 'motor-tube axis, along Z; tube ends at z +/-%.3f' % (
            val(P, 'fins.tube.length_m', 'm') / 2), axis='Z', p=(xt, s * yf, 0.0))
        add('DA-HINGE-' + tag, 'axis', 'wing.elevon.chord_frac', 'hinge line (z = upper surface, set by the module)', axis='Y', p=(xh, s * (b / 4), 0.0))
    for st in STATIONS:
        sy, sz = SIGNS[st]
        add('DX-MOTOR-' + st, 'point', 'propulsion.stations', 'motor station: tube centreline at motor height; shaft along -x',
            p=(xm, sy * ym, sz * zm))
        add('DX-HUB-' + st, 'point', 'propulsion.stations.x_prop_plane_m', 'prop hub centre on the prop plane', p=(xp, sy * ym, sz * zm))
        add('DX-FOOT-' + st, 'point', 'landing/params.json#landing.pad', 'foot pad contact on DP-GROUND: z = +/-(pad outer '
            'edge - edge round), CL-D5-CONTACT-Z, D-30 splay; tip-over pivot', p=(c + foot, sy * yf, sz * zc))
        col, anc = brace[st]
        add('DX-COLLAR-' + st, 'point', 'fins/params.json#fin_detail.station_collar', 'brace end in the station-collar '
            'ear (tube axis x, ear just below the mount grip)', p=col)
        add('DX-ANCHOR-' + st, 'point', 'fins/params.json#fin_detail.brace', 'brace end in the anchor on the spar line '
            '(transport cradles stay inboard of it)', p=anc)
    for s, tag in ((1, 'R'), (-1, 'L')):
        add('DX-BLOCK-' + tag, 'point', 'fins.saddle', 'through-core block centre: tube bore on DA-TUBE, spar bore on DA-SPAR',
            p=((xt + xs) / 2, s * yf, zs))
    add('DX-CG', 'point', 'cg.x_target_m', 'CG target', p=(val(P, 'cg.x_target_m', 'm'), val(P, 'cg.y_target_m', 'm'), val(P, 'cg.z_target_m', 'm')))
    add('DX-POD', 'point', 'pod.size_m', 'pod box centre', p=(pod_x + pod_l / 2, 0.0, pod_z + pod_h / 2))
    add('DX-BOX', 'point', 'requirements.box_external_m', 'transport box centre: aircraft upright, span along the box '
        'length, centred on the props-off envelope (box_frame)', p=box_frame(P)[0])
    return S


def box_frame(params):
    """Transport box in the aircraft frame (props off, pitot boom out, aircraft upright in cruise attitude):
    centre, external (lo, hi), interior (lo, hi). Box length along y, width along x, height along z; centred on the
    props-off envelope x = pod nose .. foot tips and z = 0 (params.json#transport.envelope_props_off_m)."""
    P = params
    L, W, H = val(P, 'requirements.box_external_m', 'm')
    w = val(P, 'requirements.box_wall_m', 'm')
    x0 = min(val(P, 'pod.x_le_m', 'm'), val(P, 'propulsion.stations.x_mount_m', 'm') - val(P, 'fins.tube.od_m', 'm') / 2)
    x1 = val(P, 'wing.chord_m', 'm') + val(P, 'cg.foot_height_m', 'm')
    c = ((x0 + x1) / 2, 0.0, 0.0)
    half = (W / 2, L / 2, H / 2)
    ext = (tuple(c[i] - half[i] for i in range(3)), tuple(c[i] + half[i] for i in range(3)))
    inner = (tuple(v + w for v in ext[0]), tuple(v - w for v in ext[1]))
    return c, ext, inner


def envelope(params, margin=0.005):
    """Aircraft envelope incl. prop discs ((lo), (hi)) m: check.py warns for any flight part outside it."""
    P = params
    D = val(P, 'propulsion.prop_diameter_m', 'm')
    xp, zm, ym = val(P, 'propulsion.stations.x_prop_plane_m', 'm'), val(P, 'propulsion.stations.z_m', 'm'), \
        val(P, 'propulsion.stations.y_m', 'm')
    b, c, foot = val(P, 'wing.span_m', 'm'), val(P, 'wing.chord_m', 'm'), val(P, 'cg.foot_height_m', 'm')
    ytip = max(b / 2, ym + D / 2)
    ztop = max(zm + D / 2, val(P, 'fins.tube.length_m', 'm') / 2)
    xfront = min(xp - PROP_BLADE_HALF_M, val(P, 'pod.x_le_m', 'm'))
    try:
        xfront = min(xfront, val(P, 'avionics.pitot_tip_xyz_m', 'm')[0])        # pitot boom on the pod nose
    except KeyError:
        pass
    return ((xfront - margin, -ytip - margin, -ztop - margin),
            (c + foot + margin, ytip + margin, ztop + margin))


def build_datums(ctx):
    """Register every datum on ctx (Fusion: a '00 Datums' component with construction geometry)."""
    for name, kind, g, key, note in datum_specs(ctx.params):
        ctx.datum(name, kind, key=key, note=note, **g)
    ctx.envelope = envelope(ctx.params)


# ----------------------------------------------------------------------------- geometry helpers
def wing_core(part, coords, chord, half_span, hinge, gaps, le=(0.0, 0.0), n=32):
    """One-piece core: the box x = 0..hinge over the full span, plus the aft strip (hinge..TE) only in `gaps`
    (spanwise ranges without an elevon). Lofts along Y; returns the shapes."""
    front = section_loop(coords, chord, le, 0.0, hinge, n)
    shapes = [part.loft('Y', [(-half_span, front), (half_span, front)], smooth=True, name='core box')]
    aft = section_loop(coords, chord, le, hinge, 1.0, max(6, n // 4))
    for i, (a, b) in enumerate(gaps):
        shapes.append(part.loft('Y', [(a, aft), (b, aft)], smooth=True, name='core aft %d' % i))
    return shapes


def elevon(part, coords, chord, hinge, y0, y1, le=(0.0, 0.0), gap=0.0):
    """Elevon panel = aft part of the section between y0 and y1 (gap trims each end)."""
    aft = section_loop(coords, chord, le, hinge, 1.0, 8)
    return part.loft('Y', [(y0 + gap, aft), (y1 - gap, aft)], smooth=True, name='elevon')


def hinge_point(coords, chord, hinge, y, le=(0.0, 0.0)):
    """Tape hinge on the upper surface (params wing.elevon.hinge): (x, y, z) on the hinge line."""
    return (le[0] + hinge * chord, y, surface_z(coords, chord, hinge, 'upper', le[1]))


def spar_y(part, x, z, half, od, idia):
    """Spanwise CF tube centred on y = 0."""
    return part.tube('Y', (x, -half, z), 2 * half, od / 2, idia / 2, name='spar tube')


def tube_z(part, x, y, half, od, idia):
    """Vertical CF motor tube centred on z = 0."""
    return part.tube('Z', (x, y, -half), 2 * half, od / 2, idia / 2, name='motor tube')


def fin_plate(part, y_mid, t, x_le, x_te, z_lo, z_hi, holes=()):
    """Flat fin (foam board) on the plane y = y_mid, thickness t centred on it. Outline = rectangle in (x, z);
    holes = extra closed (x, z) loops (lightening, tube notch)."""
    outer = [(x_le, z_lo), (x_te, z_lo), (x_te, z_hi), (x_le, z_hi)]
    return part.prism('Y', y_mid - t / 2, [outer] + [list(h) for h in holes], t, name='fin plate')


def half_fin(part, coords, chord, y_mid, t, x_le, x_te, z_tip, n=12):
    """Upper (z_tip > 0) or lower (z_tip < 0) half-fin (R1, CHANGE-LOG D-04): foam board on y = y_mid, thickness t,
    LE at x_le (aft face of the motor tube), TE at x_te; the root follows the wing skin so it bonds flat; tip at z_tip.
    The section is not symmetric, so build the lower half-fin with its own call (do not z-mirror the upper)."""
    outline = half_fin_outline(coords, chord, x_le, x_te, z_tip, n)
    return part.prism('Y', y_mid - t / 2, [outline], t, name='half-fin ' + ('upper' if z_tip > 0 else 'lower'))


def half_fin_outline(coords, chord, x_le, x_te, z_tip, n=12):
    """(x, z) outline of a half-fin: tip edge at z_tip, root on the upper (z_tip > 0) or lower skin."""
    side = 'upper' if z_tip > 0 else 'lower'
    xs = [x_le + (x_te - x_le) * i / n for i in range(n + 1)]
    root = [(x, surface_z(coords, chord, min(max(x / chord, 0.0), 1.0), side)) for x in xs]
    return [(x_le, z_tip)] + root + [(x_te, z_tip)]


def core_block(part, coords, chord, y_mid, width, x0, x1, n=8):
    """Printed through-core block (params fins.saddle): the core section between stations x0..x1 (m), width along y
    centred on y_mid. Flush with both skins; the tube bore (DA-TUBE) and spar bore (DA-SPAR) pass through it."""
    loop = section_loop(coords, chord, (0.0, 0.0), x0 / chord, x1 / chord, n)
    return part.prism('Y', y_mid - width / 2, [loop], width, name='through-core block')


def strut(part, a, b, w, t, name='strut'):
    """Straight rectangular strip from point a to point b (fin brace): w along x (the cruise flow), t across the strip
    in the y-z plane. Built as a ruled loft along Z between two horizontal rectangles (the strip must not be
    horizontal); the horizontal section is t / sin(elevation) wide in y so the true thickness is t."""
    dy, dz = b[1] - a[1], b[2] - a[2]
    if abs(dz) < 1e-6:
        raise ValueError('strut %s -> %s is horizontal: build it as a box' % (a, b))
    ty = t * math.hypot(dy, dz) / abs(dz) / 2
    rect = lambda p: [(p[0] - w / 2, p[1] - ty), (p[0] + w / 2, p[1] - ty), (p[0] + w / 2, p[1] + ty),
                      (p[0] - w / 2, p[1] + ty)]
    lo, hi = (a, b) if a[2] < b[2] else (b, a)
    return part.loft('Z', [(lo[2], rect(lo)), (hi[2], rect(hi))], name=name)


def bundle(part, legs, dia):
    """Harness bundle body (lumped harness mass part, A4 HRN-001/-002): each leg = (start, end) points that differ in
    one coordinate only (route along the channel, the tube, the pod floor). One cylinder per leg."""
    out = []
    for a, b in legs:
        d = [b[i] - a[i] for i in range(3)]
        ax = [i for i in range(3) if abs(d[i]) > 1e-9]
        if len(ax) != 1:
            raise ValueError('bundle leg %s -> %s is not axis-aligned: split it into X/Y/Z legs' % (a, b))
        out.append(part.cylinder('XYZ'[ax[0]], a, d[ax[0]], dia / 2, name='bundle leg'))
    return out


def box_shell(part, ext, wall):
    """Transport box as six wall bodies (so check.py can test each wall against the aircraft)."""
    lo, hi = ext
    out = []
    for k in range(3):
        for side in (0, 1):
            a, b = list(lo), list(hi)
            if side == 0:
                b[k] = lo[k] + wall
            else:
                a[k] = hi[k] - wall
            if k > 0:                                    # walls 2..3 and 4..5 sit between the x walls: no overlap
                a[0], b[0] = lo[0] + wall, hi[0] - wall
            if k > 1:
                a[1], b[1] = lo[1] + wall, hi[1] - wall
            out.append(part.box(tuple(a), tuple(b), name='box wall'))
    return out


def motor_envelope(part, face, can_d, can_l, shaft_d=0.005, shaft_l=0.014):
    """Outrunner envelope on the X axis, mount face at `face` (x, y, z), thrust side toward -x."""
    R, rs = can_d / 2, shaft_d / 2
    prof = [(0, 0), (0, R), (-can_l, R), (-can_l, rs), (-can_l - shaft_l, rs), (-can_l - shaft_l, 0)]
    return part.revolve('X', face, prof, name='motor envelope')


def prop_disc(part, hub, D, t=2 * PROP_BLADE_HALF_M):
    """Prop as a disc of diameter D and axial thickness t centred on the hub point (plane normal X)."""
    return part.cylinder('X', (hub[0] - t / 2, hub[1], hub[2]), t, D / 2, name='prop disc')


def prop_keepout(ctx, name, hub, D, clearance, exempt, rotate=None, blade_half=None):
    """Prop strike keep-out: disc radius D/2 + clearance, axial half blade + clearance (check.py ERROR if any
    other part's bounding box enters).

    rotate (CR-E1-31b): the same (axis, deg) tuple the motor/prop components get from ctx.part(rotate=). The
    keep-out axis is then the canted shaft axis (x turned by that rotation) and check.py tests the tilted cylinder
    exactly, so the tilt is geometry and the clearance stays clearance. None keeps the x-axis cylinder.
    blade_half: the owner's axial half-extent of the rotating prop about its mid-plane (E1, CR-E1-16: -6 / +10 mm
    with coning, so pass 0.010); default PROP_BLADE_HALF_M."""
    import fusionkit as fk
    R, half = D / 2 + clearance, (PROP_BLADE_HALF_M if blade_half is None else blade_half) + clearance
    axis = 'X' if not rotate else fk.mat_vec(fk.rot_matrix(*rotate), (1.0, 0.0, 0.0))
    ctx.keepout_cylinder(name, axis, hub, R, half, exempt)


def quad(ctx, ids):
    """ids = {'UR': built part, 'UL': new, 'LR': new, 'LL': new}: exact mirrors through DP-SYM and DP-CHORD."""
    ctx.mirror(ids['UR'], ids['UL'], plane='XZ')
    ctx.mirror(ids['UR'], ids['LR'], plane='XY')
    ctx.mirror(ids['UL'], ids['LL'], plane='XY')
    return [ctx.components[ids[s]] for s in STATIONS]


def pair(ctx, right, left):
    """Left part = right part mirrored through DP-SYM."""
    return ctx.mirror(right, left, plane='XZ')


# ----------------------------------------------------------------------------- hover attitude
def hover_pose(params):
    """Standing on the fin tips: rotate +90 deg about Y (body +x -> world -z, body +z -> world +x), then lift so
    DP-GROUND sits on world z = 0. Returns (axis, degrees, translation m) for renders / the viewer / ground checks."""
    g = val(params, 'wing.chord_m', 'm') + val(params, 'cg.foot_height_m', 'm')
    return 'Y', 90.0, (0.0, 0.0, g)


def to_hover(p, params):
    import fusionkit as fk
    ax, deg, t = hover_pose(params)
    q = fk.mat_vec(fk.rot_matrix(ax, deg), p)
    return tuple(q[i] + t[i] for i in range(3))


def hover_ground(ctx, exempt):
    """Nothing but the feet may reach DP-GROUND (x = TE + foot): halfspace keep-out."""
    ctx.keepout_halfspace('KO-GROUND', 'X', ctx.D('DP-GROUND') if 'DP-GROUND' in ctx.datums else
                          val(ctx.params, 'wing.chord_m') + val(ctx.params, 'cg.foot_height_m'), 1, exempt)


# ----------------------------------------------------------------------------- DATUMS.md table
BEGIN, END = '<!-- datums:begin (generated by k09kit.py --datums-md; do not edit by hand) -->', '<!-- datums:end -->'


def _fmt(v):
    """3 decimals (mm), 4 when the tenth of a mm matters (e.g. the collar ear at 0.1535)."""
    if abs(v) <= 5e-5:
        return '0'
    t = '%.4f' % v
    return t[:-1] if t.endswith('0') else t


def datums_table(params):
    rows = ['| Name | Kind | x | y | z | Normal / dir | From `params.json` | What it is |', '|---|---|---|---|---|---|---|---|']
    for name, kind, g, key, note in datum_specs(params):
        if kind == 'plane':
            xyz = ['—'] * 3
            xyz['XYZ'.index(g['axis'])] = _fmt(g['offset'])
        else:
            xyz = [_fmt(v) for v in g['p']]
            if name.startswith('DA-HINGE'):
                xyz[2] = 'upper skin'
                xyz[1] = '±panel'
        rows.append('| `%s` | %s | %s | %s | %s | %s | `%s` | %s |' % (
            name, kind, xyz[0], xyz[1], xyz[2], g.get('axis', '—') if kind != 'point' else '—', key, note))
    return '\n'.join(rows)


def _replace_block(text, block):
    i, j = text.find(BEGIN), text.find(END)
    if i < 0 or j < 0:
        raise ValueError('DATUMS.md has no generated-table markers')
    return text[:i + len(BEGIN)] + '\n' + block + '\n' + text[j:]


def datums_md_stale(params=None, path=DATUMS_MD):
    """True if the generated table in DATUMS.md differs from params.json (check.py WARNs)."""
    if not os.path.exists(path):
        return True
    with open(path, encoding='utf-8') as f:
        text = f.read()
    try:
        return _replace_block(text, datums_table(params or load_params())) != text
    except ValueError:
        return True


def main(argv):
    P = load_params()
    if '--datums-md' in argv:
        with open(DATUMS_MD, encoding='utf-8') as f:
            text = f.read()
        new = _replace_block(text, datums_table(P))
        with open(DATUMS_MD, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new)
        print('DATUMS.md: %d datums written' % len(datum_specs(P)))
        return 0
    if '--check' in argv:
        stale = datums_md_stale(P)
        print('DATUMS.md %s' % ('STALE: run python -I redesign/fusion/k09kit.py --datums-md' if stale else 'up to date'))
        return 1 if stale else 0
    print(datums_table(P))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
