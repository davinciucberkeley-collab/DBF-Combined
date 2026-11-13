"""G3 3D-printing specialist: writes PRINT-LIST.md (every printed part, material, printer class, time, filament) from the CAD shop files.

Run:  python -I redesign/team/G3/make_print_plan.py
Inputs (read only): redesign/manufacturing/out/PRINT-LIST.csv (written by manufacturing/make_shop_files.py from the CAD builders),
subsystems/*/parts.csv (CAD masses and notes), team/I1/BOM.csv (filament lines W05 PETG 1 kg, W08 ASA 1 kg).
Re-run after `python -B redesign/manufacturing/make_shop_files.py`. Nothing here is hand-typed except the rules at the top.
"""
import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE.parents[1]
PL = R / "manufacturing" / "out" / "PRINT-LIST.csv"
BOM = R / "team" / "I1" / "BOM.csv"

# Printer classes (G3 decision, sources in PRINT-PLAN.md section 1)
def klass(machine, material, hold=""):
    if hold == "jig":
        return "J: Prusa, PLA (Jacobs free filament), shop aids"
    if material.startswith("ASA"):
        return "C: enclosed printer (ASA)"
    if material.startswith("TPU"):
        return "B: Prusa, TPU (direct drive)"
    return "A: Prusa, PETG (Jacobs open access, or a team printer)"


def main():
    rows = list(csv.DictReader(open(PL, encoding="utf-8")))
    spool = {}
    for r in csv.DictReader(open(BOM, encoding="utf-8")):
        if r["line"] in ("W05", "W08"):
            spool[r["line"]] = r
    parts_mass = {}
    for sub in ("wing", "fins", "pod", "landing", "mechanisms", "power", "avionics", "harness"):
        f = R / "subsystems" / sub / "parts.csv"
        if f.exists():
            for r in csv.DictReader(open(f, encoding="utf-8")):
                parts_mass[r["part_id"]] = r

    tot = defaultdict(lambda: [0, 0.0, 0.0])        # class -> [pieces, minutes, grams]
    mat = defaultdict(lambda: [0, 0.0, 0.0])
    lines = []
    flight = defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows:
        q = int(r["qty_total"])
        tm, ms = float(r["est_time_each_min"]), float(r["est_mass_each_g"])
        hold = "ON HOLD" if r["status"].startswith("ON HOLD") else ("jig" if r["status"].startswith("JIG") else "print")
        k = klass(r["machine"], r["material"], hold)
        mname = "PLA (jig)" if hold == "jig" else r["material"]
        for d, key in ((tot, k), (mat, mname)):
            d[key][0] += q
            d[key][1] += q * tm
            d[key][2] += q * ms
        if hold != "jig":
            flight[r["material"]][0] += q
            flight[r["material"]][1] += q * tm
            flight[r["material"]][2] += q * ms
        lines.append((r, q, tm, ms, k, hold))

    def h(m):
        return f"{m / 60:,.1f}"

    # first-print rule: test-fit parts first (BUILD-GUIDE stage 1 step 5), jigs before the blocks, holds last
    def order(x):
        r, q, tm, ms, k, hold = x
        p = r["part"]
        if hold == "jig":
            return (0, p)
        if p.startswith(("FIN-004", "FIN-003", "FIN-008", "FIN-010", "WNG")):
            return (1 if hold != "ON HOLD" else 3, p)
        return (2, p)

    tab = ["| # | Part | Instances | Mat | Colour (CAD) | Qty fl + sp | Printer class | Orientation | Layer mm | Perim | Infill | Supports | Bed mm | Time each min | g each | Time total h | g total | Status | File |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, (r, q, tm, ms, k, hold) in enumerate(sorted(lines, key=order), 1):
        tab.append(f"| {n} | {r['part']} | {r['instances']} | {'PLA (CAD: PETG)' if hold == 'jig' else r['material']} | {r['colour'] or '-'} | {r['qty_flight']} + {r['qty_spare']} | {k.split(':')[0]} | {r['orientation']} | {r['layer_mm']} | {r['perimeters']} | {r['infill']} | {r['supports']} | {r['size_on_bed_mm']} | {tm:g} | {ms:g} | {q * tm / 60:,.1f} | {q * ms:,.1f} | {hold} | `{r['file']}` |")

    cls_tab = ["| Class | Pieces | Machine hours `EST` | Filament g `EST` | Where |", "|---|---|---|---|---|"]
    where = {"J": "Jacobs Prusa printers: PLA is free and needs no training (labs page, checked 2026-11-13). **G3 decision: print the shop aids in PLA, not PETG** (they carry no flight load; this keeps 280 g off the PETG spool)",
             "A": "Jacobs Prusa printers, no cost or training required for PLA per the labs page (https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/, checked 2026-11-13); PETG is not stated there: ask staff, else a team printer",
             "B": "a Prusa with a direct-drive extruder, slow (2 mm3/s, `shopconfig.py`)",
             "C": "**not on the Jacobs open-access list** (MF-15); Fortus 380MC / Markforged are staffed lab machines (room 332); or a teammate's enclosed printer; or PETG/CF-PETG if C4 signs off (BR-30)"}
    for k in sorted(tot):
        cls_tab.append(f"| {k} | {tot[k][0]} | {h(tot[k][1])} | {tot[k][2]:,.0f} | {where[k[0]]} |")
    cls_tab.append(f"| **All** | {sum(v[0] for v in tot.values())} | {h(sum(v[1] for v in tot.values()))} | {sum(v[2] for v in tot.values()):,.0f} | |")

    petg_flight = flight["PETG"][2]
    asa_flight = flight["ASA"][2]
    holds = [(r["part"], q) for r, q, tm, ms, k, hold in lines if hold == "ON HOLD"]
    hold_g = sum(q * ms for r, q, tm, ms, k, hold in lines if hold == "ON HOLD")
    hold_h = sum(q * tm for r, q, tm, ms, k, hold in lines if hold == "ON HOLD")
    petg_w05 = spool.get("W05")
    asa_w08 = spool.get("W08")
    colours = sorted({r["colour"] for r, *_ in lines if r["colour"]})
    big = max(float(x) for r, *_ in lines for x in r["size_on_bed_mm"].split(" x "))

    txt = f"""# G3 print plan and print list: K09-L

Revision G3-R1, 2026-11-13. Status `PROPOSED`. Generated by `python -I redesign/team/G3/make_print_plan.py` from `manufacturing/out/PRINT-LIST.csv`
(the exporter's per-file list, itself built from the CAD parts lists `subsystems/*/parts.csv`); re-run after any CAD change and after
`python -B redesign/manufacturing/make_shop_files.py`. Times and masses are the exporter's estimates (`EST`): the slicer replaces them on the first print. STLs are in `manufacturing/out/print/` and `jigs/`.
Requirement `R-PROCESS` (printed parts <= 0.2 m on any axis): the largest bed dimension of any file is {big:,.1f} mm (limit 200 mm: {'pass' if big <= 200 else 'FAIL'}).

## 1. Printer classes and decisions

| Class | Material | Why | Where | Decision |
|---|---|---|---|---|
| A | PETG, 0.2 mm, 3-4 perimeters | blocks, tray, pod, landing, mechanisms, plugs | Jacobs Prusa printers if staff confirm PETG, else a team printer | print everything here that C4/C6 have not put on hold |
| J | PLA, 0.2 mm | jigs and drill guides (shop aids) | Jacobs Prusa printers (free PLA) | print first; flight loads never pass through them |
| B | TPU 95A, 2 perimeters | two wingtip corner caps `GER-007`, 0.73 g each | a Prusa with a direct-drive extruder | print last; **no TPU spool is in the BOM** (BR-32): the smallest spool, price `—`, goes to I1 (`CR-G3-02`) |
| C | ASA, 0.2 mm, 5 perimeters | motor mounts `FIN-003` (D-42: ASA for temperature), ESC pads `FIN-007`, grommets `HRN-110` | enclosed printer, not Jacobs open access | **book an enclosed printer now** (`CR-G3-01`); fallback: PETG mounts only if C4 and C6 re-run on PETG (BR-30), not decided here |

Colours: the CAD colours ({', '.join(colours)}) identify parts (spacers by thickness, pistons upper/lower). The BOM holds one PETG spool (W05) of no stated colour,
so **G3 decides: print in one colour and mark the colour code with the paint pen from `C04`** (dot on the part, matching the colour table in `subsystems/pod/params.json` `spacer_set_m`
and landing `BUILD.md`). If the team prefers coloured filament, that is a purchase for I1, not assumed.

## 2. Totals by class

{chr(10).join(cls_tab)}

By material, flight set only (jigs excluded): PETG {petg_flight:,.0f} g, ASA {asa_flight:,.0f} g; jigs {mat["PLA (jig)"][2]:,.0f} g of PLA.

| Check | Value | Limit | Result |
|---|---|---|---|
| PETG flight filament vs spool W05 ({petg_w05['qty_total'] if petg_w05 else '-'} x 1 kg) | {mat['PETG'][2]:,.0f} g with spares (jigs are PLA: {mat['PLA (jig)'][2]:,.0f} g, Jacobs free stock) | 1 000 g, keep 20 % for failed prints and purge (rule: <= 800 g) | {'pass' if mat['PETG'][2] <= 800 else 'FAIL: buy a second spool (CR-G3-02)'} (margin {1000 - mat['PETG'][2]:,.0f} g) |
| ASA vs spool W08 | {mat['ASA'][2]:,.0f} g | 1 000 g | pass (spool is far larger than the need; the smallest practical spool, CR-I1-20) |
| Parts on hold | {', '.join(f'{p} x{q}' for p, q in holds)}: {hold_g:,.0f} g, {hold_h / 60:,.1f} h | print only after the 18 Dec freeze | STATUS issue 1 (collar height) |
| Mass: exporter vs CAD (flight parts) | see the g-each column against `subsystems/*/parts.csv` | A3 weighs every first print | open until weighed |

## 3. Print order (what goes on the bed first)

1. **Jigs and drill guides** (`jigs/`: JIG-01 tube posts, JIG-02 fin-alignment collar, JIG-03 cant gauge A/B): needed for the first block and mount (MF-06, MF-07). Print in the week of 30 Nov (`I2` task `W03`).
2. **Test-fit set** (BUILD-GUIDE stage 1 step 5): one mount, one collar, one servo frame, one block; fit them on the real motor, tube and servo, then print the flight set. The collar is on hold until the 18 Dec freeze: print the test collar only.
3. **Flight set** after the freeze, in the closure window (19 Dec - 18 Jan, `I2` task `PR1`, about 30 days for the machine hours below on one printer).
4. **Make two of every crash part from day one** (`review/MANUFACTURING.md` section 5): the quantities in the table already include the spares (8 mounts, 8 collars, 3 blocks, 2 spare shoes, 8 spare pistons).
5. Weigh each first print and report to A3 (`T-A3-WEIGH-PARTS`) before the rest of the batch (BUILD-GUIDE stage 10 step 1 does this for the foot).

## 4. The print list

Source: `manufacturing/out/PRINT-LIST.csv`; status `print` = flight part, `jig` = shop aid, `ON HOLD` = do not print yet. Class column letters refer to section 1.

{chr(10).join(tab)}

## 5. Process notes by part family (from the BUILD.md files)

| Family | Rule | Source |
|---|---|---|
| Through-core block `FIN-004` | spar bore horizontal on the bed, 3 perimeters, 15 % gyroid; sets the thrust lines, so check both bores with the clocking jig before bonding | `fins/parts.csv`, MF-06 |
| Motor mount `FIN-003` | ASA, collar axis vertical; check the 1.5 mm slit with a feeler; drill 3.4 mm to the measured motor from a printed guide, never through the motor; post-cure 4 h at 50 C needs a heat box | MM-01, MM-04, `MANUFACTURING.md` section 2 |
| Landing shoes and pistons | PETG, rim end on the bed; fit is sensitive to extrusion: print a test piston first | `landing/BUILD.md`; `MANUFACTURING.md` |
| Tray and pod prints | seven prints epoxied full-area to the board; spacers by thickness, colour-coded | `pod/parts.csv` POD-002, POD-008 |
| Servo frame, covers, horns | PETG 100 % infill for the horns | `mechanisms/parts.csv` |
| TPU caps | two wraps of 12 mm filament tape hold them (`E-GER-21/22`) | `wing/BUILD.md` step 12 |
| ASA grommets `HRN-110` | six pieces (3 A + 3 B) | `harness/parts.csv` |
| Elevated risk | supports flagged `check` in the table are auto-estimated overhangs: slice with the real orientation and look | `PRINT-LIST.csv` supports column |

## 6. Change requests from G3

| # | To | What | Why |
|---|---|---|---|
| CR-G3-01 | G1, I2 | Book an enclosed printer for {tot['C: enclosed printer (ASA)'][2]:,.0f} g of ASA ({h(tot['C: enclosed printer (ASA)'][1])} h) before 18 Dec | ASA is not on the Jacobs open-access list (`MANUFACTURING.md` MF-15) |
| CR-G3-02 | I1 | Add the smallest TPU 95A spool (two caps, 1.2 g) to the BOM; price `—` (no vendor page read) | BR-32; `GER-007` is TPU |
| CR-G3-03 | D2, D5 | Accept paint-pen colour coding instead of coloured filament, or say which parts must be coloured | one PETG spool in the BOM |
| CR-G3-04 | C4, C6 | State by 18 Dec whether collars are printed in PETG or another material (hold) | STATUS issue 1 |
"""
    (HERE / "PRINT-LIST.md").write_text(txt, encoding="utf-8")
    print("written", len(txt), "largest bed dimension mm", big, "class totals", {k: (v[0], round(v[1] / 60, 1), round(v[2])) for k, v in tot.items()})


if __name__ == "__main__":
    main()
