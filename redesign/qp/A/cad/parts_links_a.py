"""parts_links_a.py - CAD part id -> where it comes from, for the Explorer part panel ("Vendor / file").
Buy parts: the BOM-A.csv line and its vendor page. Made parts: the BOM-A.csv material line(s) and the build-film stage
clip + assembly step (a_assembly_plan.py) that shows the part going on.
    python -I redesign/qp/A/cad/parts_links_a.py      -> redesign/qp/A/cad/out/parts-a.csv (read by viewer_data_a.py)
The CAD-part -> BOM-line assignment below is a lookup by part type, kept here so it can be reviewed; a part with no
BOM line says so ("no BOM line") instead of guessing a vendor."""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.dirname(HERE)
RED = os.path.dirname(os.path.dirname(A))
sys.path.insert(0, HERE)
import a_assembly_plan as plan  # noqa: E402

# stage grouping of the build film (showcase/concept-a/render_build_a.py STAGES), copied by step id
sys.path.insert(0, os.path.join(RED, 'showcase', 'concept-a'))
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('rb', os.path.join(RED, 'showcase', 'concept-a', 'render_build_a.py'))
    src = open(spec.origin, encoding='utf-8').read()
    ns = {}
    exec(src[src.index('STAGES = ['):src.index(']\n', src.index('STAGES = [')) + 2], ns)
    STAGES = ns['STAGES']
except Exception as e:  # the film script needs bpy for the rest; only STAGES is read
    raise SystemExit('could not read STAGES from render_build_a.py: %s' % e)

BOM = {r['id']: r for r in csv.DictReader(open(os.path.join(A, 'BOM-A.csv'), encoding='utf-8'))}

# (prefix, kind, BOM lines, note). First matching prefix wins.
MAP = [
    ('AVN-002', 'buy', ['V03'], ''), ('AVN-003', 'buy', ['V02'], ''), ('AVN-004', 'buy', ['V04'], ''),
    ('AVN-005', 'buy', ['V05'], ''), ('AVN-006', 'buy', ['V05'], 'pitot probe comes in the V05 airspeed kit'),
    ('AVN-009-T', 'buy', ['V05'], 'cut from the 2 / 4 mm tubing in the V05 kit (D-208)'), ('AVN-009-S', 'buy', ['V05'], 'cut from the 2 / 4 mm tubing in the V05 kit (D-208)'),
    ('AVN-007', 'buy', ['R05'], 'foam tape from the local fastener / tape line'),
    ('AVN-010', 'make', ['R03'], 'printed PETG bosses and pads (T-073 R2, T-077 p5)'), ('AVN-008', 'make', ['R03'], 'printed PETG'),
    ('CGE-001', 'make', ['R03'], 'printed PETG'), ('CGE-002', 'make', ['R08'], 'cut from the 12x10 tube'),
    ('CGE-003', 'make', ['R03'], 'printed PETG'), ('CGE-004', 'make', ['R02'], 'cut from the 16x14 fin-tube offcut (D-206)'),
    ('CGE-009', 'make', ['R09'], 'cut from the 14x12 tube'), ('CGE-010', 'make', ['R14'], 'cut from the 3 mm carbon rod (price not found)'),
    ('CGE-005', 'make', ['R10'], 'cut from the 6x4.5 tube'), ('CGE-006', 'make', [], 'Markforged X7 Onyx + continuous CF, printed z-up (D-221, T-080 s3.2; BOM line and price: -, no X7 charge listed)'), ('CGE-011', 'make', [], '0.5 mm CF sheet cut on the OMAX waterjet (D-221; BOM line and price: -)'), ('CGE-012', 'make', ['R14'], 'cut from the 3 mm carbon rod (price not found)'), ('CGE-013', 'make', [], 'Markforged X7 Onyx, printed z-up (D-221; BOM line and price: -)'),
    ('CGE-007', 'make', ['R03'], 'printed PETG'), ('CGE-008', 'make', ['R03'], 'printed PETG'),
    ('FIN-001', 'make', ['R02'], 'cut from the 16x14 tube'), ('FIN-002', 'make', ['R09'], 'cut from the 14x12 tube'),
    ('FIN-003', 'make', ['R03'], 'printed PETG'), ('FIN-004', 'make', ['R01'], 'XPS + tape'),
    ('FIN-005', 'make', ['R03'], 'printed PETG cradle (D-221 clamshell)'), ('FIN-007', 'make', [], '0.5 mm CF sheet cut on the OMAX waterjet (D-221; BOM line and price: -)'), ('FIN-008', 'make', ['R14'], 'cut from the 3 mm carbon rod (price not found)'), ('FIN-006', 'make', ['R01'], 'XPS + tape'),
    ('GER-001', 'make', ['R03'], 'printed PETG'), ('GER-002', 'make', ['R03'], 'foot pads (BOM R03 line text)'),
    ('HRD-001', 'make', ['R05', 'R07'], 'screws, nuts, epoxy, CA'),
    ('HRN-003', 'make', ['R03'], 'printed PETG raceway'), ('HRN-004', 'make', ['R03'], 'printed PETG conduit'),
    ('HRN-001', 'make', ['W07', 'W05'], 'wire, heat-shrink, ties'), ('HRN-002', 'buy', ['W05'], 'XT60 and 14 AWG from the W05 kit'),
    ('HWC-', 'buy', ['R05'], 'stock screws / nuts, local'),
    ('MEC-001', 'buy', ['M01'], ''), ('MEC-002', 'buy', ['M01'], 'arm supplied with the servo'),
    ('MEC-003', 'buy', ['M02'], ''), ('MEC-004', 'make', ['R03'], 'printed PETG horn + rib, 2 mm flat profile (D-212 rev 3); M02 horns unused'), ('MEC-008', 'make', ['R03'], 'printed PETG Z-bend keeper (D-212 rev 3)'), ('MEC-005', 'buy', ['M02'], 'clevis pin from the M02 linkage set'),
    ('PRP-001', 'buy', ['P01'], ''), ('PRP-002', 'buy', ['P02'], ''), ('PRP-003', 'buy', ['P04'], ''),
    ('PRP-004', 'buy', ['P01'], 'T-Motor prop adapter: confirm it ships in the motor hardware pack (no own BOM line)'),
    ('PRP-005', 'buy', ['P01'], 'T-Motor spinner nut: confirm it ships in the motor hardware pack (no own BOM line)'),
    ('PWR-001', 'buy', ['W01'], ''), ('PWR-002', 'buy', ['W08'], 'STRIX 20 x 300 mm buckle strap'), ('PWR-003', 'buy', ['W09'], 'silicone rubber sheet cut to 100 x 30 x 1 mm (EST)'),
    ('WNG-001', 'make', ['R01'], 'XPS machined on the ShopBot (D-203; hot wire backup), tape skin'), ('WNG-002', 'make', ['R08'], 'cut from the 12x10 tube'),
    ('WNG-003', 'make', ['R03'], 'printed PETG'), ('WNG-004', 'make', ['R03'], 'printed PETG'), ('WNG-005', 'make', ['R03'], 'printed PETG'),
    ('WNG-006', 'make', ['R01'], 'XPS + tape'), ('WNG-007', 'make', ['R11'], 'lead strip'),
    ('WNG-008', 'make', ['R03'], 'printed PETG'), ('WNG-009', 'make', ['R03', 'R12'], 'printed PETG + silicone fluid'),
    ('WNG-010', 'make', ['R03'], 'printed PETG'),
]


def step_of(pid):
    for k, s in enumerate(plan.STEPS):
        if pid in s[2]:
            for si, (title, ids) in enumerate(STAGES):
                if s[0] in ids:
                    return s[0], s[1], si + 1, title
            return s[0], s[1], None, None
    return None


def main(part_ids):
    rows = []
    for pid in part_ids:
        m = next((x for x in MAP if pid.startswith(x[0])), None)
        if not m:
            rows.append(dict(part_id=pid, vendor_or_file='— (not mapped)', url='', how_url='', process=''))
            continue
        _, kind, lines, note = m
        refs = []
        url = ''
        for b in lines:
            r = BOM.get(b)
            if not r:
                refs.append(b + ' (missing in BOM-A)')
                continue
            refs.append('%s %s' % (b, r['ship_group']))
            if not url and r['source_url'].startswith('http'):
                url = r['source_url']
        st = step_of(pid)
        how = ''
        if kind == 'make':
            text = 'Made (%s) from BOM %s' % (note, ', '.join(refs) if refs else '—')
        else:
            text = 'Bought: BOM %s%s' % (', '.join(refs) if refs else '—', ' (%s)' % note if note else '')
        if st:
            step, cap, stage, title = st
            text += '; fitted in build step %s "%s"' % (step, cap)
            if stage:
                text += ', stage %d (%s)' % (stage, title)
                how = 'assets/animation/build/a-stage-%02d.mp4' % stage
        rows.append(dict(part_id=pid, vendor_or_file=text, url=url, how_url=how, process=''))
    out = os.path.join(HERE, 'out', 'parts-a.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['part_id', 'vendor_or_file', 'url', 'how_url', 'process'])
        w.writeheader()
        w.writerows(rows)
    nolink = [r['part_id'] for r in rows if not r['url'] and not r['how_url']]
    print('parts-a.csv: %d parts, %d with a vendor link, %d with a build clip; no link at all: %s'
          % (len(rows), sum(bool(r['url']) for r in rows), sum(bool(r['how_url']) for r in rows), ', '.join(nolink) or 'none'))


if __name__ == '__main__':
    import a_model as m
    main(list(m.PARTS))
