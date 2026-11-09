"""K09-L skeleton - harness: one mass lump per side on the upper skin between pod and fin (motor and servo
leads). F2's real module routes every wire with ctx.wire. Reference layout for F2."""
import k09kit as k9


def build(ctx):
    W = ctx.value('pod.size_m', 'm')[1]
    ctx.part('HRN-901').box((0.0, W / 2, 0.004), (0.02, ctx.D('DP-FIN-R') - 0.006, 0.010))
    k9.pair(ctx, 'HRN-901', 'HRN-902')
    ctx.contact('E-HRN-901', 'taped to the upper skin')
    ctx.contact('E-HRN-902', 'taped to the upper skin')
