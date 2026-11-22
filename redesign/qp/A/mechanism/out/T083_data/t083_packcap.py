"""T-083: pack-current cap (Q_M_BAT_CURR_MAX) for the X2216 V3 on the APC 9x4.5MR. Category: illustrative (prop_a.py EST model).
cap_pack(V_rest, I_lim): largest duty <= 1 with all four motors at that duty drawing <= I_lim from the pack (bus current = 4 x phase I x duty).
python -I t083_packcap.py PRED_KG [I_LIM ...]   prints markdown; writes nothing."""
import sys, os
A = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, A); sys.dont_write_bytecode = True
import prop_a as P


def pack_A(vrest, duty):
    n, i, th, pw, vb = P.full(vrest, duty)
    return 4 * i * duty, n, i, vb


def cap_pack(vrest, ilim):
    if pack_A(vrest, 1.0)[0] <= ilim:
        return 1.0
    lo, hi = 0.3, 1.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if pack_A(vrest, mid)[0] <= ilim else (lo, mid)
    return lo


def state(mp, ilim, der=0.93):
    cf, cs = cap_pack(16.8, ilim), cap_pack(14.92, ilim)
    twf = P.tw_state(16.8, cf, mp, der)[0] * 0.97
    tws = P.tw_state(14.92, cs, mp, der)[0] * 0.97
    return cf, cs, twf, tws, P.window_pct(tws), pack_A(16.8, cf), pack_A(14.92, cs)


if __name__ == '__main__':
    mp = float(sys.argv[1])
    lims = [float(x) for x in sys.argv[2:]] or [41.0, 48.0, 55.0, 60.0, 72.0, 999.0]
    print(f"Pack-current cap at {mp:.3f} kg, derate 0.93, 3 % download (EST model)")
    print("| Q_M_BAT_CURR_MAX A | cap fresh / sag | T/W fresh dl | T/W sag dl | window % | fresh: pack A / rpm / phase A | sag: pack A / rpm / phase A |")
    print("|---|---|---|---|---|---|---|")
    for il in lims:
        cf, cs, twf, tws, w, pf, ps = state(mp, il)
        print(f"| {il:g} | {cf:.3f} / {cs:.3f} | {twf:.3f} | {tws:.3f} | {w:+.2f} | {pf[0]:.1f} / {pf[1]:.0f} / {pf[2]:.2f} | {ps[0]:.1f} / {ps[1]:.0f} / {ps[2]:.2f} |")
