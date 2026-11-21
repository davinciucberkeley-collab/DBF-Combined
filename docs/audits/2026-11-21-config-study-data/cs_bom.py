"""Config study 2026-11-21: BOM totals per option on the T-077 p8 cost rules (imports T077p8_data/bom_p8.py unchanged; edits its rows IN MEMORY only).
python -I cs_bom.py"""
import sys, copy, importlib
D = r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/mechanism/out/T077p8_data"
sys.path.insert(0, D); sys.dont_write_bytecode = True
import bom_p8 as B
BASE = copy.deepcopy(B.rows)

def row(id_, sub, item, grp, qty, u, status='verified', spares=0):
    return dict(id=id_, subsystem=sub, item=item, ship_group=grp, qty=float(qty), u=float(u), spares=float(spares), status=status, flag='', unit_usd=str(u))
def setu(rows, id_, u=None, qty=None):
    for r in rows:
        if r['id'] == id_:
            if u is not None: r['u'] = float(u)
            if qty is not None: r['qty'] = float(qty)
            return
    raise KeyError(id_)
def drop(rows, *ids): return [r for r in rows if r['id'] not in ids]
def total(rows, reserve_tubes=("R02", "R08", "R09", "R10", "R15")):
    B.rows[:] = rows
    t = B.totals(); t30 = B.totals(0.30)
    return t, t30
def common_reads(rows):
    setu(rows, 'V03', 129.01)                 # RMRC Kakute H743-Wing, page read 2026-11-21 ("price":"129.01", In Stock)
    setu(rows, 'R09', 15.36)                  # RMRC 14x12 1 m, page read 2026-11-21 ($15.36, In Stock)
    setu(rows, 'R10', 8.50)                   # p7 strut 8x6: RMRC 8x6 1 m $8.50 In Stock, read 2026-11-21 (replaces the 6x4.5 line; p8 had the 8x6 price as '-')
    return rows
def show(tag, rows):
    t, t30 = total(rows)
    print(f"| {tag} | {t['goods']:,.2f} | {t['spend']:,.2f} | {t['reserve']:,.2f} | **{t['total']:,.2f}** | {t['margin']:+,.2f} | {t30['total']:,.2f} |")

if __name__ == '__main__':
    print("| Scenario | Goods | Spend | Crash reserve | Total | Margin to $2,000 | Total with U/EST +30 % |\n|---|---|---|---|---|---|---|")
    show("p8 as recorded (reproduces bom_p8.py)", copy.deepcopy(BASE))
    r0 = common_reads(copy.deepcopy(BASE)); show("p8 + 2026-11-21 reads (H743 $129.01, 14x12 $15.36, 8x6 strut $8.50)", r0)
    # Option 1a: MN2212 V2.0 KV920 variant, same page / same listed price $46.90 (variant price not separately shown: U)
    r1 = copy.deepcopy(r0); show("1a KV920 motors, p8 airframe", r1)
    # Option 3: touchdown 0.8 m/s design case, pad Fp 20 N; 2-ply skin (glass already in T3), rib 16x14 from a 2nd RMRC 16x14 tube if the rib torsion coupon gives >= 45 MPa (else 20x18 from Carbonwebshop, price '-')
    r3 = drop(copy.deepcopy(r0), 'R15'); setu(r3, 'R02', qty=2); B.SHIP.pop('Carbonwebshop', None); show("3 (rib 16x14, coupon >= 45 MPa)", r3)
    B.SHIP['Carbonwebshop'] = 25.0
    r3b = copy.deepcopy(r0); show("3 fallback (rib from Carbonwebshop, R15 price kept as the 20x18 proxy)", r3b)
    # Option 2: legs from the hub (4 x 0.60 m 10x8 + 4 x 0.40 m 6x4.5 braces, fittings PETG); rib back to 14x12 (fin carries no foot load), R15 dropped
    r2 = drop(copy.deepcopy(r0), 'R15'); r2.append(row('L01', 'airframe', 'RMRC CF tube 10x8 1 m (legs)', 'RMRC', 3, 11.44)); r2.append(row('L02', 'airframe', 'RMRC CF tube 6x4.5 1 m (leg braces)', 'RMRC', 2, 4.40))
    B.SHIP.pop('Carbonwebshop', None); show("2 legs from the hub (rib 14x12)", r2)
    # Combination 1a + 3 = r3 (motor variant has no cost delta)
    # Option 4: concept B re-priced on the same floor and cost rules
    rb = copy.deepcopy(r0)
    rb = drop(rb, 'P01', 'P02', 'R15', 'T11', 'T12', 'R06', 'R11', 'R12', 'R13', 'M01', 'T1', 'G04')
    rb += [row('P01', 'propulsion', 'T-Motor MN3110 KV700 lift (4 + 1 spare); store.tmotor.com/goods.php?id=334 $61.90 read 2026-11-21', 'TMotor', 5, 61.90, spares=1),
           row('P05', 'propulsion', 'T-Motor MN2212 V2.0 KV780 pusher; goods.php?id=388 $46.90 read 2026-11-21', 'TMotor', 1, 46.90),
           row('P02', 'propulsion', 'T-Motor P12x4 CF prop pair (2 flight pairs + 1 spare); $38.90 read 2026-11-21', 'TMotor', 3, 38.90),
           row('P06', 'propulsion', 'APC 9x6E pusher prop (1 + 2 spare); RMRC $3.22 read 2026-11-21', 'RMRC', 3, 3.22),
           row('P07', 'propulsion', 'HobbyWing Skywalker 30A V2 pusher ESC; RMRC $14.99 read 2026-11-21', 'RMRC', 1, 14.99),
           row('M01', 'mechanisms', 'EMAX ES3054HV servo (2 ailerons + elevator + rudder + 1 spare)', 'RMRC', 5, 13.99, spares=1),
           row('BR1', 'airframe', 'RMRC 16x14 1 m (2 booms) - in R02 qty 3 below', 'RMRC', 0, 0.0),
           row('BR2', 'airframe', 'Tail foam / hardware EST', 'Local', 1, 15.00, status='unverified')]
    setu(rb, 'W01', 59.99)                     # Tattu 3700 4S 45C XT60, RMRC "price":"59.99" In Stock, read 2026-11-21 (2 packs)
    for r in rb:
        if r['id'] == 'W01': r['ship_group'] = 'RMRC'
    setu(rb, 'R02', qty=3)                     # 2 booms + fin/tail
    setu(rb, 'R08', qty=2)                     # 2 wing-panel spars 12x10
    B.SHIP.pop('Carbonwebshop', None)
    # reserve definition uses W01 pack, P01 motor, M01 servo, airframe tubes: unchanged rule
    show("4 concept B (MN3110 KV700 + P12x4, Tattu 3700, 1.2 m two-panel wing, 2 booms)", rb)

def x2216(rows):
    for r in rows:
        if r['id'] == 'P01':
            r['u'] = 18.99; r['ship_group'] = 'RMRC'; r['item'] = 'SunnySky X2216 880KV long shaft (4 + 1 spare); RMRC $18.99 In Stock, read 2026-11-21'
    rows.append(row('P08', 'propulsion', 'Prop adapters for 3.175 mm shaft x 6 (EST; part not chosen)', 'RMRC', 1, 10.00, status='unverified'))
    rows.append(row('W10', 'power', 'XT90 pairs + 12 AWG battery lead (EST; A-P16 connector >= 1.25 x 63 A peak)', 'RMRC', 1, 12.00, status='unverified'))
    return rows
if __name__ == '__main__':
    B.SHIP['Carbonwebshop'] = 25.0
    show("1e X2216 + p8 airframe (D-226 cell, rib 25x23 R15)", x2216(common_reads(copy.deepcopy(BASE))))
    r = x2216(drop(common_reads(copy.deepcopy(BASE)), 'R15')); setu(r, 'R02', qty=2); B.SHIP.pop('Carbonwebshop', None)
    show("1e + 3, rib 16x14 (2nd RMRC 16x14; coupon >= 45 MPa)", r)
    r = x2216(drop(common_reads(copy.deepcopy(BASE)), 'R15'))
    show("1e + 3, rib 14x12 from R09 (coupon >= 60 MPa, or >= 47 MPa after TP-3 at zeta 0.02)", r)
    B.SHIP['Carbonwebshop'] = 25.0
    show("1e + 3, rib fallback from Carbonwebshop (R15 price as proxy)", x2216(common_reads(copy.deepcopy(BASE))))
    # option 2 with legs in the reserve tube set
    r2 = drop(common_reads(copy.deepcopy(BASE)), 'R15'); r2.append(row('L01', 'airframe', 'RMRC CF tube 10x8 1 m (legs)', 'RMRC', 3, 11.44)); r2.append(row('L02', 'airframe', 'RMRC 6x4.5 1 m (braces)', 'RMRC', 2, 4.40))
    B.SHIP.pop('Carbonwebshop', None); B.rows[:] = r2; t = B.totals()
    print(f"| 2 legs, legs counted in the crash-reserve tube set | | | | **{t['total'] + (3*11.44+2*4.40)*1.1025:,.2f}** | {t['margin'] - (3*11.44+2*4.40)*1.1025:+,.2f} | |")
