"""T-073 step 6: mission_gate_a.py roll-up with the D-216 s4 deltas, skin, strut 6x4.0, T-068 package and the O2 pack / O4 prop options.  SCRATCH OUTPUT ONLY (NOT MASS-GATE).
CATEGORY: illustrative / mass bookkeeping + the repo's own mission arithmetic (mission_gate_a.py source executed unmodified except for the item list, PACK_WH and, for O4, the prop table).
Run: python -I t073_rollup.py > rollup_out.txt   Each scenario's full mission_gate_a output is saved in rollup_raw/<tag>.txt.
Deltas (g, basic; EST unless noted) are applied to the item whose group they belong to, and carry that item's growth factor (ASM-A3-MGA: 20 % EST, as T-067 s5)."""
import os, re, sys, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
QA = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, QA)
import prop_a as pa
SRC = open(os.path.join(QA, "mission_gate_a.py"), encoding="utf8").read()
os.makedirs(os.path.join(HERE, "rollup_raw"), exist_ok=True)
T9 = dict(pa.T)
LBF, HP = 4.4482, 745.7
# APC 10x4.5MR static rows (PER3_10x45MR.dat, read 2026-11-19): rpm: (thrust lbf, power hp); rows to 10,000 rpm only
T10r = {5000: (0.852, 0.040), 6000: (1.231, 0.068), 7000: (1.679, 0.108), 8000: (2.200, 0.160), 9000: (2.795, 0.227), 10000: (3.464, 0.311)}
T10 = {k: (v[0]*LBF, v[1]*HP) for k, v in T10r.items()}
IDX = dict(wing=0, fins=1, motors=2, props=3, adapters=4, esc=5, pack=6, strap=7, avionics=8, servos=9, cage=10, hw=11)
# ---- deltas (g) by tag: (group, grams, label)
D067 = [("fins", 58.2+12.6, "T-067 fins FIN +58.2 and feet GER +12.6"), ("cage", 58.5, "T-067 cage CGE +58.5"), ("avionics", 9.1-0.8, "T-067 AVN +9.1, HRN -0.8"), ("wing", 0.5, "T-067 WNG +0.5")]
# R1-R4 as computed in step4_out.txt (T-073): R1 as specified -16.0 (fails), R1'' -10.1 (passes); R2 -16.9; R3 spec -10.5 / r3fix -11.2 (fix passes); R4 -5.8
R_SPEC = [("cage", -16.0, "R1 as specified (fails tab and wall)"), ("avionics", -16.9, "R2 plate out, 8 bosses"), ("cage", -10.5, "R3 as specified (fails S2 plate)"), ("cage", -5.8, "R4 tubular clamps")]
R_PASS = [("cage", -10.1, "R1'' passing variant"), ("avionics", -16.9, "R2 plate out, 8 bosses"), ("cage", -11.2, "R3fix"), ("cage", -5.8, "R4 tubular clamps")]
R5_8 = [("wing", -2.0, "R5 lens caps (T-070 EST, not checked)"), ("cage", -3.0, "R6 print basis (T-070 EST, not checked)"), ("avionics", -0.4, "R7 RX hood (T-070 EST)")]
WING = [("wing", 35.7, "glass skin 27.0 + plates 5.0 + cove strip 3.7 (T-071)"), ("cage", 3.0, "strut 6x4.0 (T-071)"), ("fins", 12.0, "T-068 package (T-070 s4 T, range +5..+20)")]
O2A = [("pack", 232.0-270.0, "pack CNHL 4S 2000 100C 232 g U")]
O2B = [("pack", 211.0-270.0, "pack CNHL Black 4S 2200 40C about 211 g U")]
PROP10 = [("props", 12.0, "10x4.5 props +12 g (T-070 s6 EST; mass '-')")]
COVER = [("avionics", -4.5, "thermoformed bay cover (T-070, Dillon purchase)")]
SCEN = [
 ("S0_listed_now", [], 270, 2.3, False),
 ("S1_T067_basis", D067, 270, 2.3, False),
 ("S2_spec_R1R4", D067+R_SPEC, 270, 2.3, False),
 ("S3_pass_R1R4", D067+R_PASS, 270, 2.3, False),
 ("S4_pass_R1R8", D067+R_PASS+R5_8, 270, 2.3, False),
 ("S5_O4eng_9in_270g", D067+R_PASS+R5_8+WING, 270, 2.3, False),
 ("S6_O4eng_9in_232g", D067+R_PASS+R5_8+WING+O2A, 232, 2.0, False),
 ("S7_O4eng_9in_211g", D067+R_PASS+R5_8+WING+O2B, 211, 2.2, False),
 ("S8_O4_10in_232g", D067+R_PASS+R5_8+WING+O2A+PROP10, 232, 2.0, True),
 ("S9_O4_10in_211g", D067+R_PASS+R5_8+WING+O2B+PROP10, 211, 2.2, True),
 ("S10_O4_10in_232g_cover", D067+R_PASS+R5_8+WING+O2A+PROP10+COVER, 232, 2.0, True),
 ("S11_O4_10in_211g_cover", D067+R_PASS+R5_8+WING+O2B+PROP10+COVER, 211, 2.2, True),
 ("S12_O4_10in_232g_specR", D067+R_SPEC+R5_8+WING+O2A+PROP10, 232, 2.0, True),
]
def run(tag, deltas, pack_g, pack_ah, p10):
    src = SRC
    src = src.replace("sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))", "pass")
    mod = "items = [(d, g + sum(x[1] for x in DELTAS if x[0] == _G[i]), m, gr) for i, (d, g, m, gr) in enumerate(items)]\n"
    src = src.replace("base = sum(i[1] for i in items)", mod + "base = sum(i[1] for i in items)", 1)
    src = src.replace("PACK_WH = 2.3*14.8", "PACK_WH = %.3f*14.8" % pack_ah, 1)
    src = src.replace("print(f\"basic {base} g;", "print(f\"ITEMS {[round(i[1],1) for i in items]}\"); print(f\"basic {base:.1f} g;", 1)
    groups = sorted(IDX, key=lambda k: IDX[k])
    pa.T = dict(T10) if p10 else dict(T9)
    ns = {"__name__": "mg", "DELTAS": deltas, "_G": groups, "pa_override": True}
    buf = io.StringIO()
    # pa is imported inside the source as `import prop_a as pa` -> same cached module object, whose T we just set
    with contextlib.redirect_stdout(buf):
        exec(compile(src, "mission_gate_a_t073", "exec"), ns)
    out = buf.getvalue(); open(os.path.join(HERE, "rollup_raw", tag + ".txt"), "w", encoding="utf8").write(out); return out, ns
def pick(out, pat, grp=1):
    m = re.search(pat, out); return m.group(grp) if m else "-"
print("| Scenario | basic g | itemised pred. g (basic + growth + 48 g overrun) | flat rule g (basic x 1.1174 + 47.04) | vs 1,470 g (itemised) | vs 1,580 g O4 target (itemised) | window +- % (0.90 cap, sag, at pred.) | mass for +-5 % window (g) | cruise to BATT_LOW min at pred. (need 3.41) |")
print("|---|---|---|---|---|---|---|---|---|")
res = {}
for tag, deltas, pg, ah, p10 in SCEN:
    out, ns = run(tag, deltas, pg, ah, p10)
    basic = float(pick(out, r"basic ([\d.]+) g;")); pred = float(pick(out, r"predicted\+overrun (\d+) g"))
    # window: second 'window 0.90-capped sag' line belongs to the first m = round(M,3)
    win = pick(out, r"window 0\.90-capped sag: [\d.]+-[\d.]+ W, \+-([\d.]+) %")
    cap5 = float(pick(out, r"mass for \+-5 % window capped: ([\d.]+) kg"))*1000
    tmin = pick(out, r"max cruise to BATT_LOW \d+ s = ([\d.]+) min")
    flat = basic*1.1174+47.04
    print(f"| {tag} | {basic:.1f} | {pred:.0f} | {flat:.0f} | {pred-1470:+.0f} | {pred-1580:+.0f} | {win} | {cap5:.0f} | {tmin} |")
    res[tag] = dict(basic=basic, pred=pred, flat=flat, win=win, cap5=cap5, tmin=tmin)
print("\nNotes: the windows come from mission_gate_a.py's own T/W arithmetic (thrust table x 0.93 derate, 4 motors, cant 17 deg, sag 3.73 V/cell, 0.90 spin cap), not from the C3 time-domain run; for the 10 in rows the prop table is the APC 10x4.5MR static file (to 10,000 rpm).")
print("Listed deltas per scenario are in the script (D067, R_SPEC, R_PASS, R5_8, WING, O2A/O2B, PROP10, COVER).")

# ---- equal-current comparison (A-P16: motor 13 A / 180 s, Q_M_SPIN_MAX 0.90 on the 9x4.5, which gives 11.15 A with all four at 0.90 FRESH, 12.1 A one motor at 0.90).
# The rows above let the 10 in prop run at duty 0.90 (more current). Here the 10 in duty cap is lowered until the FRESH per-motor current equals the 9x4.5 value at 0.90 (11.15 A),
# or the A-P16 13 A rating; the window is then taken at SAG voltage with that duty cap (the repo's own formulas, mission_gate_a.py convention).
import math
def full_for(Ttab, vrest, duty):
    pa.T = dict(Ttab); return pa.full(vrest, duty)
VSAG = 3.73*4; VFR = 16.8
n9f, i9f, t9f, *_ = full_for(T9, VFR, 0.90); n9s, i9s, t9s, *_ = full_for(T9, VSAG, 0.90)
print(f"\n## Equal-current check (APC tables, repo motor model: Kv 780, Rm 0.173, I0 0.5 EST)\n- 9x4.5 duty cap 0.90: fresh {n9f:.0f} rpm {i9f:.2f} A {t9f:.2f} N (table); sag {n9s:.0f} rpm {i9s:.2f} A {t9s:.2f} N.")
def duty_for(i_target):
    lo, hi = 0.3, 1.0
    for _ in range(40):
        mid = 0.5*(lo+hi); i = full_for(T10, VFR, mid)[1]
        lo, hi = (mid, hi) if i < i_target else (lo, mid)
    return 0.5*(lo+hi)
T10res = {}
for lab, it in (("equal to 9x4.5 at 0.90 fresh (%.2f A)" % i9f, i9f), ("A-P16 13 A rating, fresh", 13.0)):
    d = duty_for(it); nf, i_f, t_f, *_ = full_for(T10, VFR, d); ns_, i_s, t_s, *_ = full_for(T10, VSAG, d)
    T10res[lab] = t_s
    print(f"- 10x4.5, duty cap {d:.3f} ({lab}): fresh {nf:.0f} rpm {i_f:.2f} A {t_f:.2f} N; sag {ns_:.0f} rpm {i_s:.2f} A, thrust {t_s:.2f} N = {100*(t_s/t9s-1):+.1f} % vs the 9x4.5 capped sag thrust (ideal-momentum guess in T-070 s6: +7.3 %).")
n10, i10, t10, *_ = full_for(T10, VFR, 0.90); n10s, i10s, t10s, *_ = full_for(T10, VSAG, 0.90)
print(f"- 10x4.5 at duty cap 0.90 (the S8-S12 rows above): fresh {i10:.2f} A ({100*(i10/i9f-1):+.0f} % current vs the 9x4.5), sag thrust {t10s:.2f} N ({100*(t10s/t9s-1):+.1f} %).")
for m in (1.55, 1.58, 1.60, 1.62):
    parts = [("9x4.5 cap 0.90", t9s)]+[("10x4.5 " + k.split(' (')[0].split(',')[0], v) for k, v in T10res.items()]+[("10x4.5 duty 0.90", t10s)]
    print(f"- m {m:.2f} kg: " + "; ".join(f"{tag} T/W {4*t_*0.97*pa.DER*math.cos(math.radians(pa.CANT))/(m*9.807):.2f}, window {100*(0.8*4*t_*0.97*pa.DER*math.cos(math.radians(pa.CANT))/(m*9.807)-1.33)/(0.8*4*t_*0.97*pa.DER*math.cos(math.radians(pa.CANT))/(m*9.807)+1.33):+.1f} %" for tag, t_ in parts))
