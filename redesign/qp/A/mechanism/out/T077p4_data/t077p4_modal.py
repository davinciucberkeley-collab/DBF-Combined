"""T-077 p4 COPY (modal only, X_M / X_HUB injected: cage 12 mm forward) of T-076d step 6 (D-222 s4.3 item 6, T76c-4): A-P10 re-run with the AS-BUILT 16x14 bridge (CAD D-206) instead of the 12x10 bridge of the committed modal CFG.
CATEGORY: FEA-class beam-frame modal analysis + forced response (fe_a.py via t073_modal.py / t076_modal.py, unmodified, source exec'd with ONE injected line) and control-loop analysis (sitl/fu_cage.py, imported unchanged).
    python -I t076d_step6_ap10.py [part]     part = modal12 | modal16 | gm   (no arg: all three; modal about 10 s each, gm about 2-6 min)
modal: t076_modal.py with T076_MASS=t067 T076_RESID=1 T076_REBASE=1 (the T-076 row 3 configuration: T-067 printed masses, 1,640 g FE mass, bands re-based at 1.64 kg), bridge_tube 12x10 (control: reproduces the T-076 record) and 16x14.
gm: A-P10(c): the iter3_run.py control-band clause (A.param flight gains, GM >= 2.0 on every axis / corner / damping / thrust scale, flexible modes at x1.0 / x0.8 / x1.2) with bridge 12x10 (control, record D-191: 2.03), 16x14, and 16x14 with the T-067 + 275 g pack masses (EST; the record's fu_cage FE masses are the iteration-2 ones)."""
import os, sys, io, math, json, time, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); T76 = os.path.abspath(os.path.join(HERE, '..', 'T076_data'))
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures')); SITL = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'sitl'))
sys.dont_write_bytecode = True


def modal(bridge, xm=None):
    env = dict(T076_MASS='t067', T076_RESID='1', T076_REBASE='1'); os.environ.update(env)
    src = open(os.path.join(T76, 't076_modal.py')).read()
    assert 'import fe_a\n' in src
    inj = "import fe_a\nM.CFG['bridge_tube'] = (%s, %s)\n" % ((12e-3, 10e-3) if bridge == 12 else (16e-3, 14e-3))
    if xm is not None:
        inj += "fe_a.X_M = %r\nfe_a.X_HUB = %r\n" % (xm, xm)
    src = src.replace('import fe_a\n', inj, 1)
    g = dict(__name__='t076_modal_run', __file__=os.path.join(T76, 't076_modal.py'))
    sys.path.insert(0, T76); sys.path.insert(0, os.path.join(T76, '..', 'T073_data')); sys.path.insert(0, S_DIR); sys.path.insert(0, SITL)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): exec(compile(src, 't076_modal.py', 'exec'), g)
    return buf.getvalue()


def gm(variant):
    sys.path.insert(0, S_DIR); sys.path.insert(0, SITL)
    import numpy as np, fe_a, fu_cage as FC
    if variant == '12x10': FC.CFG['bridge_tube'] = (12e-3, 10e-3)
    else: FC.CFG['bridge_tube'] = (16e-3, 14e-3)
    if variant == '16x14 + T-067 masses': FC.CFG.update(pack_g=275.0, avionics_g=110.0 - 8.0 + 1.02 + 9.67 - 2.0 - 0.81, motor_g=65.0 + 11.06 + 5.0 + 4.3 + 2.9 + 2.41, foot_pad_m=(2.5 + (4.55 - 1.40)) * 1e-3)
    SET = {"pit": dict(gyro_lpf=60, fltd=60, P=0.12, D=0.0012), "rll": dict(gyro_lpf=60, fltd=32, P=0.20, D=0.003), "yaw": dict(gyro_lpf=60, fltd=32, P=0.37)}
    C = FC.cases(); rows = []; gmall = 99.0
    for ax in ("pit", "rll", "yaw"):
        for k in ("kd", "nom", "hi"):
            c = [x for x in C if x["ax"] == ax and x["node"] == "spar centre" and x["k"] == k][0]; shown = ", ".join("%.1f: %+.2f" % (ff, gg / c['inv_I']) for ff, gg in c["flex"] if 3 < ff < 40); out = []
            for sc in (1.0, 0.8, 1.2):
                modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c["modes"]]; g_ = 99.0
                for z in (0.003, 0.01):
                    for ts in (0.77, 1.0, 1.25):
                        L = FC.loop(modes, ax, z, tfull_scale=ts, **SET[ax])
                        if FC.maxre(L) >= -1e-6: g_ = 1.0
                        else: g_ = min(g_, FC.margins(L)[0])
                out.append(g_)
            gmall = min(gmall, *out); rows.append(dict(ax=ax, corner=k, modes=shown, gm_nom=out[0], gm_m20=out[1], gm_p20=out[2]))
    return dict(variant=variant, min_gm=gmall, rows=rows)


def main():
    part = sys.argv[1] if len(sys.argv) > 1 else 'all'; t0 = time.time(); out = {}
    if part in ('all', 'modal12'):
        out['modal12'] = modal(12); open(os.path.join(HERE, 'step6_modal_bridge12x10.txt'), 'w').write(out['modal12']); print('modal 12x10 done %.0f s' % (time.time() - t0), flush=True)
    if part in ('all', 'modal16'):
        out['modal16'] = modal(16); open(os.path.join(HERE, 'step6_modal_bridge16x14.txt'), 'w').write(out['modal16']); print('modal 16x14 done %.0f s' % (time.time() - t0), flush=True)
    if part in ('all', 'gm'):
        res = [gm(v) for v in ('12x10', '16x14', '16x14 + T-067 masses')]
        for r in res:
            print('\n### control band, bridge %s: minimum GM %.2f (rule 2.0; record D-191 with 12x10: 2.03)' % (r['variant'], r['min_gm']))
            print('| axis | corner | cage modes 3-40 Hz (Hz: gain / rigid) | GM nominal | GM modes -20 % | GM modes +20 % |'); print('|---|---|---|---|---|---|')
            for q in r['rows']: print('| %s | %s | %s | %.2f | %.2f | %.2f |' % (q['ax'], q['corner'], q['modes'], q['gm_nom'], q['gm_m20'], q['gm_p20']))
        json.dump(res, open(os.path.join(HERE, 'step6_gm.json'), 'w'), indent=1, default=float); print('gm done %.0f s' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    xm = float(sys.argv[1])
    out = modal(16, xm)
    open(os.path.join(HERE, 'p4_modal_bridge16x14_xm%+.0f.txt' % (xm * 1e3)), 'w').write(out)
    print(out[-2200:])
