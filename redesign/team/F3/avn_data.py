"""F3 avionics data generator (revision F3-R2, params A1-R3): builds the avionics CAD module on the stub backend,
turns bodies into masses and CGs, and writes subsystems/avionics/interfaces.json and parts.csv from one table, so the
declared masses and CGs are the CAD's. It also emits the CAD claims other roles build on (claims.avn_data.json).

    python -I redesign/team/F3/avn_data.py          # rewrite interfaces.json, parts.csv, claims.avn_data.json
    python -I redesign/team/F3/avn_data.py --check  # exit 1 if interfaces.json / parts.csv on disk differ
    then  python -I redesign/team/F3/avionics.py     # analysis claims (reads the masses written here)

Masses: bought parts from the seller figure (subsystems/avionics/params.json); printed PETG = volume x density;
silicone lines = cut length x annulus x density; gel cubes = volume x density; tape, ties, strap from consumables_g.
"""
import csv
import importlib.util
import io
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
AVN = REDESIGN / 'subsystems' / 'avionics'
sys.path.insert(0, str(REDESIGN / 'fusion'))
sys.path.insert(0, str(REDESIGN / 'proofs'))
import fusionkit as fk                              # noqa: E402
import k09kit as k9                                 # noqa: E402
import proofkit as pk                               # noqa: E402
from backends.stub_backend import StubBackend      # noqa: E402


def lv(A, k):
    d = A[k]
    return d['value'] if isinstance(d, dict) and 'value' in d else d


def load_module():
    spec = importlib.util.spec_from_file_location('avn_module', str(AVN / 'fusion' / 'avionics.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ----------------------------------------------------------------------------- the part table (one source)
# id, name, material, make_or_buy, process, vendor_or_file, unit cost USD, electrical, flags, notes
PARTS = [
    ('AVN-001', 'Flight controller CoreWing F405 Wing APP V2', 'electronics (bought)', 'buy', 'bought; 100 mm signal pigtails soldered',
     'ReadyMadeRC (I1 BOM A01)', 67.26, 'sink', {},
     'FC top board + wireless app board (stable ArduPilot Plane 4.7.x, target CoreWingF405WingV2, Q_TAILSIT_ENABLE 1); '
     'flat, arrow -x (AHRS_ORIENTATION 0); the power board of the stack is PWR-003 on the PDB plate (price shared)'),
    ('AVN-002', 'GPS + compass HGLRC M100-5883', 'electronics (bought)', 'buy', 'bought', 'getfpv.com / RaceDayQuads (I1 BOM A02)',
     20.49, 'sink', {}, 'u-blox M10 + QMC5883 compass; 21 x 21 x 8 mm, 7.73 g; on the 45 deg mast pad, arrow toward the nose; '
     'no steel within 50 mm'),
    ('AVN-003', 'RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz)', 'electronics (bought)', 'buy', 'bought; FCC firmware flashed',
     'RadioMaster dealer (I1 BOM A03)', 19.99, 'sink', {}, '22 x 13 x 4 mm, 4.6 g with two U.FL antennas; CRSF on SERIAL6; '
     'telemetry over the same link (no separate radio)'),
    ('AVN-004', 'Airspeed sensor MS4525DO (I2C 0x28)', 'electronics (bought)', 'buy', 'bought; 2 silicone lines cut to 40 mm',
     'ReadyMadeRC digital airspeed sensor (I1 BOM A04)', 59.99, 'sink', {},
     'RMRC board 20 x 21 x 13 mm, 3.5 g, ports up, between the tray tie posts; I2C1 0x28 (ARSPD_TYPE 1); '
     'replaces the MS5525 (0x76 clashes with the baro)'),
    ('AVN-005', 'Pitot boom (plug-in): pitot-static probe in a printed keyed sleeve', 'PETG (printed) + aluminium probe', 'make',
     'FDM PETG sleeve (100 % infill), probe bonded with 5 min epoxy', 'subsystems/avionics/fusion/avionics.py; probe in BOM A04 kit', 0.5,
     None, {}, 'tip at params avionics.pitot_tip_xyz_m; 6 mm sleeve with a 5.6 mm key flat on +z and a 10 mm shoulder on the '
     'socket collar; the two lines pull off the probe root barbs when the boom is pulled (no couplers, D-89b); removed for transport'),
    ('AVN-006', 'Isolation and retention set: 4 gel cubes, foam tape, ties, FC strap', 'silicone gel + consumables', 'buy',
     'cut 5 mm cubes from gel sheet; tape and ties from shop stock', 'Kyosho Zeal / alpha-gel 5 mm sheet; 3M VHB-class tape', 3.0,
     None, {}, 'gel cubes under the FC corners (f_n ~ 36 Hz); 1 mm foam tape under GPS, RX, airspeed board; 3 ties; '
     '10 mm hook-and-loop strap over the FC with 1-2 mm slack (C6 secondary retention)'),
    ('AVN-007', 'microSD 16-32 GB (logging)', 'electronics (bought)', 'buy', 'bought; FAT32', 'team stock (else ~$6)', 0.0,
     None, {}, 'SDHC class 10; LOG_BITMASK default + batch sampler for T-F3-VIBE'),
]

E = 'avionics'
EDGES = [
    {'id': 'E-AVN-01', 'part_a': 'AVN-001', 'part_b': 'POD-002', 'via': 'CT-GEL-PAD', 'owner': E,
     'notes': 'FC top board on 4 gel cubes (5 mm) on the scuffed FC plate, between D2\'s end stops (2 mm clear); no screws, no '
              'header pins; arrow -x; beside the pack, never its stop (CR-C5-07). Secondary: 10 mm hook-and-loop strap over the '
              'board through slots in both end stops, 1-2 mm slack (C6 CR-C6-19; slots: CR-F3-12)',
     'retention': {'item': '4 gel cubes 5 x 5 x 5 mm (adhesive faces) + 10 mm hook-and-loop strap with 1-2 mm slack',
                   'count': '4 + 1', 'load_n': '12 g board: 1.5 N at 12.75 g crash on the strap if the cubes let go (C6: 10 N class)',
                   'inspection': 'pre-flight: board does not lift with one finger, strap slack 1-2 mm; replace cubes after a crash'}},
    {'id': 'E-AVN-02', 'part_a': 'AVN-002', 'part_b': 'POD-005', 'via': 'CT-TAPE-FOAM', 'owner': E,
     'notes': 'GPS on 1 mm foam tape on the 45 deg mast pad (pad normal (-x,+z)/sqrt2), module arrow down-forward along the pad (toward '
              'the nose); cable tied once to the mast; no steel within 50 mm (non-metallic mast bolt E-POD-06)',
     'retention': {'item': '21 x 21 mm foam tape (full face) + 1 tie round module and pad', 'count': '1 + 1',
                   'load_n': '7.7 g x 12.75 g = 1.0 N', 'inspection': 'pre-flight: module does not move on the pad, arrow forward'}},
    {'id': 'E-AVN-03', 'part_a': 'AVN-003', 'part_b': 'POD-002', 'via': 'CT-TAPE-FOAM', 'owner': E,
     'notes': 'RX on 1 mm foam tape on the avionics plate, crosswise behind the aft tie post, under antenna tube A; antenna A up the '
              'hatch tube (z), antenna B to the nose tube (F5: needs a 100-150 mm U.FL antenna, CR-F3-15); elements >= 31 mm from carbon, >= 60 mm from the GPS',
     'retention': {'item': 'foam tape under the RX + heat-shrink; 1 tie on the lead at the plate', 'count': '1 + 1',
                   'load_n': '4.6 g x 12.75 g = 0.6 N', 'inspection': 'pre-flight: RX LED solid, RX does not move'}},
    {'id': 'E-AVN-04', 'part_a': 'AVN-004', 'part_b': 'POD-002', 'via': 'CT-TAPE-FOAM', 'owner': E,
     'notes': 'airspeed board on 1 mm foam tape between the two tie posts (locating fit in x), 1 tie through the post slots over the '
              'board; ports up; lines to the couplers 40 mm each (<= 60 mm)',
     'retention': {'item': 'foam tape + 1 tie through the tie-post slots', 'count': '1 + 1',
                   'load_n': '4.5 g x 12.75 g = 0.6 N', 'inspection': 'pre-flight: board seated between the posts, lines on'}},
    {'id': 'E-AVN-05', 'part_a': 'AVN-005', 'part_b': 'POD-006', 'via': 'CT-PLUG-IN', 'owner': E, 'field_joint': True,
     'notes': 'keyed sleeve (5.6 mm flat on +z) into the 6.2 mm socket bore, shoulder on the collar front face (x -0.123); drag in cruise '
              'and gravity in hover act along +x and push it home; friction set to 2-5 N pull-out with one wrap of PTFE tape; the '
              'socket carries the handling moment (C6 CR-C6-09: 0.8 N m). Socket bore flat: CR-F3-12',
     'retention': {'item': 'shoulder + key flat; friction fit 2-5 N pull-out', 'count': '1',
                   'load_n': 'cruise drag ~0.05 N and hover weight 0.05 N, both +x (seating)',
                   'inspection': 'set-up: boom pushed home, shoulder on the collar, flat up; pre-flight blow test reads > 0'}},
    {'id': 'E-AVN-06', 'part_a': 'AVN-005', 'part_b': 'AVN-004', 'via': 'CT-PITOT-TUBING', 'owner': E,
     'notes': 'two silicone lines 1.6 mm ID (EST): probe total (centre barb) to sensor port P1, static to P2 (ARSPD_TUBE_ORDR 2, so a swap is '
              'harmless); the lines pull off the probe root barbs when the boom is pulled; lines labelled T and S, no kinks',
     'retention': {'item': 'push-on silicone on 2.0 mm barbs', 'count': '2 lines', 'load_n': 'none (pneumatic)',
                   'inspection': 'set-up: lines pushed on the barbs to the shoulder; blow test reads > 0'}},
    {'id': 'E-AVN-07', 'part_a': 'AVN-006', 'part_b': 'POD-002', 'via': 'CT-GEL-PAD', 'owner': E,
     'notes': 'gel cubes stuck to the IPA-wiped FC plate; mass holder for tape, ties and the FC strap',
     'retention': {'item': 'gel adhesive face', 'count': '4', 'load_n': 'as E-AVN-01', 'inspection': 'with E-AVN-01'}},
    {'id': 'E-AVN-08', 'part_a': 'AVN-007', 'part_b': 'AVN-001', 'via': 'CT-CARD-SLOT', 'owner': E,
     'notes': '16-32 GB SDHC, FAT32, in the FC fore-edge slot; a strip of tape over the card against vibration',
     'retention': {'item': 'push-push slot + tape strip', 'count': '1', 'load_n': '0.4 g', 'inspection': 'log present after each flight'}},
    {'id': 'E-AVN-10', 'part_a': 'AVN-001', 'part_b': 'POD-002', 'via': 'CT-THERMAL-CONTACT', 'owner': E,
     'notes': 'FC board on gel cubes (insulating): heat leaves by convection in the vented pod; the BEC losses sit on the power board '
              '(PWR-003) on the PDB plate after the stack split (CR-F3-14 to E3)',
     'thermal': {'heat_w': '0.5 EST (FC top board + wireless at 5 V, ASM-F3-5V-LOADS); BEC losses ~1.2 W move to PWR-003',
                 't_max_c': 85, 't_ambient_c': 'E3 pod air', 'path': 'convection to vented pod air; gel cubes treated as insulating',
                 'sized_by': 'E3 (CL-E3-FC-PEAK), F3'}},
    # F3-R3: GND-001 is now declared by F5 (subsystems/ground), so the radio edge leaves edges_pending
    {'id': 'E-AVN-09', 'part_a': 'GND-001', 'part_b': 'AVN-003', 'via': 'CT-ELRS-RF', 'owner': E,
     'notes': 'ELRS 2.4 GHz radio link, CRSF 420 kbaud to the FC; telemetry through ELRS (ratio 1:4), no separate radio; range test T-F5-RANGE',
     'signal': {'fc_port': 'SERIAL6 (via the RX)', 'protocol': 'ELRS 2.4 GHz -> CRSF 420 kbaud', 'band': '2.4 GHz', 'tx_power_mw': 100}},
]
PENDING = []
LOCAL_CT = [{'id': 'CT-CARD-SLOT', 'kind': 'mechanical', 'method': 'press_fit',
             'spec': 'card pushed into a board-mounted push-push slot (microSD); the slot holds the card'}]
# Edges other roles declare that touch avionics parts, checked against AVIONICS.md and acknowledged (F3-R3):
#   E-HRN-22 UBEC -> FC servo rail (Vx of the power board not wired, CR-F1-29 / CR-F3-04)
#   E-HRN-23 power-board GH-6 link (Vbat, current, 5 V, GND; BATT_MONITOR 4)
#   E-HRN-24..27 FC outputs 1-4 -> ESCs, DShot300 bidirectional (TIM4 1-2, TIM3 3-4; CL-F3-BDSHOT-OUTS),
#                map LR/UL/LL/UR = 1/2/3/4 as F4 flight-software motor_map
#   E-HRN-28/29 FC outputs 5/6 -> elevons L/R, PWM 50 Hz (TIM8)
#   E-HRN-30 GPS: SERIAL5 + I2C1, compass 0x0D / 0x2C;  E-HRN-31 RX: SERIAL6 CRSF
#   E-HRN-32 airspeed Y-branch on I2C1 at 0x28; bus total 0.461 m <= 0.5 m (CL-F2-I2C-LEN)
#   E-TRN-21 pitot boom stowed in the 220 x 25 x 25 mm tray slot (CL-F3-BOOM-STOW-L/-W)
ACK = ['E-HRN-%d' % i for i in range(22, 33)] + ['E-TRN-21']


def build():
    P = k9.load_params()
    info = {p[0]: {'name': p[1], 'material': p[2], 'mass_g': 1.0, 'status': 'MODELLED'} for p in PARTS}
    ctx = fk.Context(StubBackend(), parts=info, params=P)
    ctx.begin_module('avionics', str(AVN))
    k9.build_datums(ctx)
    mod = load_module()
    mod.build(ctx)
    pod, L = mod.pod_geometry(ctx.value, ctx.dir)
    coords, _src = k9.section(ctx)
    G = pod.layout(ctx.value, L, coords)
    g = mod.layout(ctx.value, ctx.local, L, G)
    return ctx, ctx.local, g


def masses(ctx, A):
    """part id -> (mass_g, cg_xyz_m, breakdown)."""
    petg, gel, sil = lv(A, 'petg_kgm3'), lv(A, 'gel_kgm3'), lv(A, 'silicone_kgm3')
    out = {}

    def acc(items):
        M = sum(m for m, _ in items)
        cg = [sum(m * c[i] for m, c in items) / M for i in range(3)]
        return M, cg

    for pid, *_r in PARTS:
        c = ctx.components[pid]
        items, br = [], {}
        for s in c.shapes:
            V, cg = s.volume_centroid()
            cg = c.to_world(cg)
            nm = s.name or ''
            if nm.startswith('petg '):
                m, k = V * petg * 1000, 'PETG'
            elif nm.startswith('gel '):
                m, k = V * gel * 1000, 'gel'
            elif nm.startswith('silicone '):
                od, idd = lv(A, 'tube_m')
                m, k = 0.0, 'tube'                       # booked below by cut length; geometry gives the CG
            else:
                m, k = 0.0, 'envelope'
            items.append([m, cg, nm])
            br[k] = br.get(k, 0.0) + m
        bought = {'AVN-001': lv(A, 'fc_mass_g'), 'AVN-002': lv(A, 'gps_mass_g'), 'AVN-003': lv(A, 'rx_mass_g'),
                  'AVN-004': lv(A, 'aspd_mass_g'), 'AVN-007': lv(A, 'sd_mass_g')}
        if pid in bought:                                  # the envelope body carries the bought mass
            env = [it for it in items if it[0] == 0.0 and not it[2].startswith('silicone')]
            for it in env:
                it[0] = bought[pid] / len(env)
            br['bought'] = bought[pid]
        if pid == 'AVN-004':
            od, idd = lv(A, 'tube_m')
            mt = 2 * lv(A, 'tube_cut_m') * math.pi / 4 * (od * od - idd * idd) * sil * 1000
            tubes = [it for it in items if it[2].startswith('silicone')]
            for it in tubes:
                it[0] = mt / len(tubes)
            br['tube'] = mt
        if pid == 'AVN-005':
            probe = [it for it in items if it[2].startswith('pitot-static')]
            for it in probe:
                it[0] = lv(A, 'probe_mass_g')
            barbs = [it for it in items if it[2].startswith('probe root')]
            for it in barbs:
                it[0] = lv(A, 'coupler_g')
            br['probe'] = lv(A, 'probe_mass_g')
            br['couplers'] = lv(A, 'coupler_g') * len(barbs)
        if pid == 'AVN-006':
            cons = sum(lv(A, 'consumables_g').values())
            pads = [it for it in items if it[2].startswith('gel')]
            for it in pads:
                it[0] += cons / len(pads)
            br['consumables'] = cons
        M, cg = acc([(it[0], it[1]) for it in items])
        out[pid] = (round(M, 2), [round(x, 4) for x in cg], {k: round(v, 2) for k, v in br.items()})
    return out


def interfaces(M):
    parts = []
    for pid, name, mat, mob, _proc, _v, _c, el, _f, notes in PARTS:
        p = {'id': pid, 'name': name, 'subsystem': 'avionics', 'status': 'MODELLED', 'mass_g': M[pid][0], 'material': mat,
             'cg_xyz_m': M[pid][1], 'make_or_buy': mob}
        if el:
            p['electrical'] = el
        p['notes'] = notes + '; mass %s g (%s)' % (M[pid][0], ', '.join('%s %s' % kv for kv in M[pid][2].items()))
        parts.append(p)
    return {'schema': 'dbf-interfaces/1', 'subsystem': 'avionics',
            '_note': 'GENERATED by redesign/team/F3/avn_data.py from the avionics CAD module (masses: seller figures on the envelopes, '
                     'printed/gel/silicone parts from body volumes; CGs from the bodies). Edit the script, not this file.',
            'parts': parts, 'connection_types': LOCAL_CT, 'edges': EDGES, 'acknowledges': ACK, 'edges_pending': PENDING}


def parts_csv(M):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd', 'vendor_or_file', 'notes'])
    for pid, name, mat, mob, proc, vend, cost, _el, _f, notes in PARTS:
        w.writerow([pid, name, 1, mob, proc, mat, M[pid][0], '%.2f' % cost, vend, notes + ' (mass EST until weighed, T-F3-ARRIVAL)'])
    return buf.getvalue()


# ----------------------------------------------------------------------------- claims (CAD readouts as assumptions)
def _readouts():
    ctx, A, g = build()
    M = masses(ctx, A)
    tot = sum(m for m, _, _ in M.values())
    cg = [sum(M[k][0] * M[k][1][i] for k in M) / tot for i in range(3)]
    return ctx, A, g, M, round(tot, 2), [round(x, 4) for x in cg]


kit = pk.Kit(__file__, params=["../../params/params.json"], out="claims.avn_data.json")


def _declare(g, M, tot, cg):
    kit.assumption("ASM-F3-CAD-MASS", "Avionics mass and CG from the CAD roll-up", "[total g, cg x, cg y, cg z m]",
                   basis="team/F3/avn_data.py: seller masses on the envelopes, volumes x densities for printed, gel and silicone parts",
                   value=[tot] + cg, unit="g,m,m,m", status="UNVERIFIED")
    kit.assumption("ASM-F3-CAD-FIT", "Avionics fit readouts from the CAD",
                   "[tie-post gap m, airspeed board length m, RX overhang past the avionics plate m, pitot line path m, GPS tilt deg, "
                   "RX front edge to antenna tube A x m]",
                   basis="subsystems/avionics/fusion/avionics.py#layout() on pod.py#layout()",
                   value=[round(g['post_gap'], 4), lv(A_, 'aspd_m')[0], round(g['rx_overhang'], 4), round(g['tube_path'], 4),
                          round(g['gps_tilt_deg'], 2), round(g['rx_lo'][0] - g['ant_a_xy'][0], 4)],
                   unit="m,m,m,m,deg,m", status="PROPOSED")
    tipx = g['tip'][0]
    bm_ = lv(A_, 'barb_m')
    dy = bm_[2] if len(bm_) > 2 else lv(A_, 'aspd_port_m')[1]       # D-89b: barb spacing at the probe root
    bd = bm_[0]
    kit.assumption("ASM-F3-CAD-BOOM", "Pitot boom stowed envelope from the CAD", "[length m tip to barb ends, width m]",
                   basis="layout(): probe tip to the root barb ends; width = max(shoulder OD, barb spread + barb OD)",
                   value=[round(g['coupler_x'] - tipx, 4), round(max(g['shoulder_od'], dy + bd), 4)], unit="m,m",
                   status="PROPOSED")
    kit.assumption("ASM-F3-PORTS", "Avionics connector points for the harness (F2)", "name -> [x, y, z] m in the aircraft frame",
                   basis="layout() ports: pin-outs of the FC, GPS and RX are not published; +/- 10 mm until measured (T-F3-ARRIVAL)",
                   value={k: [round(c, 4) for c in v] for k, v in g['ports'].items()}, unit="m", status="UNVERIFIED")


@kit.calc("CALC-F3-CAD-FIT", title="Avionics fit on D2's pod", equation="margins = available - needed",
          inputs={"fit": "ASM-F3-CAD-FIT", "tmax": "P:avionics.pitot_tip_xyz_m"}, units={"tmax": "m"})
def cad_fit(fit, tmax):
    gap, alen, overhang, path, tilt, ant = fit
    return {"post_clear_m": gap - alen, "rx_overhang_m": overhang, "tube_path_m": path, "gps_tilt_deg": tilt,
            "ant_offset_m": abs(ant)}


@kit.calc("CALC-F3-CAD-BOOM", title="Pitot boom stowed envelope", equation="L = x_coupler - x_tip; W = max(OD_shoulder, dy + d_barb)",
          inputs={"b": "ASM-F3-CAD-BOOM"})
def cad_boom(b):
    return {"length_m": b[0], "width_m": b[1]}


@kit.calc("CALC-F3-CAD-MASS", title="Avionics CAD mass and CG", equation="sum m_i; CG = sum m_i r_i / sum m_i",
          inputs={"r": "ASM-F3-CAD-MASS"})
def cad_mass(r):
    return {"mass_g": r[0], "cg_x_m": r[1], "cg_y_m": r[2], "cg_z_m": r[3]}


def _claims():
    kit.claim("CL-F3-AVN-CAD-MASS", "Avionics subsystem mass (CAD roll-up)", calc="CALC-F3-CAD-MASS", output="mass_g", unit="g",
              limit=("<=", "P:mass.allocation_g.avionics"),
              parts=[p[0] for p in PARTS], note="F3-R2: power board moved to PWR-003 (CR-F3-13)",
              how="Weigh each part on arrival (T-F3-ARRIVAL); A3 replaces the EST values.")
    kit.claim("CL-F3-AVN-CG-X", "Avionics subsystem CG x", calc="CALC-F3-CAD-MASS", output="cg_x_m", unit="m",
              parts=[p[0] for p in PARTS], how="From the weighed parts at their CAD stations; A3 roll-up.")
    kit.claim("CL-F3-AVN-CG-Y", "Avionics subsystem CG y", calc="CALC-F3-CAD-MASS", output="cg_y_m", unit="m",
              parts=[p[0] for p in PARTS], how="As CL-F3-AVN-CG-X.")
    kit.claim("CL-F3-ASPD-POST-CLR", "Airspeed board clearance between the tie posts", calc="CALC-F3-CAD-FIT",
              output="post_clear_m", unit="m", limit=(">=", 0.0), parts=["AVN-004", "POD-002"],
              note="0 = locating fit; CR-F3-12 asks D2 for +1 mm", how="Dry fit on the printed tray.")
    kit.claim("CL-F3-RX-OVERHANG", "RX overhang past the avionics plate end", calc="CALC-F3-CAD-FIT", output="rx_overhang_m",
              unit="m", limit=("<=", 0.005), parts=["AVN-003", "POD-002"], note="CR-F3-12 asks D2 to extend the plate",
              how="Dry fit on the printed tray.")
    kit.claim("CL-F3-PITOT-LINE", "Pitot line path, sensor port to coupler (cut 40 mm with loop)", calc="CALC-F3-CAD-FIT",
              output="tube_path_m", unit="m", limit=("<=", 0.060), parts=["AVN-004", "AVN-005"],
              how="Cut 40 mm lines, fit, no kink with the boom in and out.")
    kit.claim("CL-F3-GPS-TILT-CAD", "GPS module tilt toward the nose in the CAD", calc="CALC-F3-CAD-FIT", output="gps_tilt_deg",
              unit="deg", limit=("<=", 50.0), parts=["AVN-002", "POD-005"], how="Protractor on the built mast pad.")
    kit.claim("CL-F3-BOOM-STOW-L", "Pitot boom stowed length, tip to coupler ends (transport slot 220 mm)", calc="CALC-F3-CAD-BOOM",
              output="length_m", unit="m", limit=("<=", 0.220), parts=["AVN-005", "TRN-003"],
              note="limit = D7 tray slot length (CR-D7-06, E-TRN-21)", how="Ruler on the built boom; lay it in the tray slot with the PE plug.")
    kit.claim("CL-F3-BOOM-STOW-W", "Pitot boom stowed width (transport slot 25 mm)", calc="CALC-F3-CAD-BOOM",
              output="width_m", unit="m", limit=("<=", 0.025), parts=["AVN-005", "TRN-003"],
              note="limit = D7 tray slot section 25 x 25 mm (CR-D7-06)", how="Caliper across shoulder and couplers.")
    kit.test("T-F3-ARRIVAL", "Avionics parts on arrival: weigh, measure, confirm the CoreWing stack split",
             verifies=["CL-F3-AVN-CAD-MASS", "CL-F3-ASPD-POST-CLR", "CL-F3-RX-OVERHANG", "CL-F3-BOOM-STOW-L", "CL-F3-BOOM-STOW-W"],
             procedure="0.01 g scale on every AVN part; calipers on FC board, airspeed board (incl. ports), RX, GPS, probe OD; "
                       "confirm the FC top board runs from the power board on a cable (else fallback: whole stack on the PDB "
                       "plate on gel cubes, 8 AWG leads with a 30 mm flex loop tied to the tray); confirm which board carries "
                       "the output pads 1-6 and the Vx rail and that Vx is not on the GH-6 link (CR-F1-29; if the outputs are "
                       "on the power board, E-HRN-22/24-29 end on PWR-003 and F2 re-routes); record the connector "
                       "positions for F2; update subsystems/avionics/params.json and re-run avn_data.py")


_ctx, A_, _g, _M, _tot, _cg = _readouts()          # CAD readouts enter the graph as assumptions (pure calcs below)
_declare(_g, _M, _tot, _cg)
_claims()


def main(argv):
    check = '--check' in argv
    files = {AVN / 'interfaces.json': json.dumps(interfaces(_M), indent=1, ensure_ascii=False) + '\n',
             AVN / 'parts.csv': parts_csv(_M)}
    bad = 0
    for path, text in files.items():
        old = path.read_text(encoding='utf-8') if path.exists() else None
        if check:
            if old != text:
                print('DIFFERS', path)
                bad = 1
        else:
            path.write_text(text, encoding='utf-8')
            print('wrote', path.relative_to(REDESIGN))
    print('avionics mass %.2f g, CG (%.4f, %.4f, %.4f) m' % (_tot, *_cg))
    for k, (m, c, br) in _M.items():
        print('  %s %6.2f g  cg (%.4f, %.4f, %.4f)  %s' % (k, m, *c, br))
    for k, v in _g['ports'].items():
        print('  port %-55s (%.4f, %.4f, %.4f)' % (k, *v))
    if not check:
        kit.write()
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
