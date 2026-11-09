"""K09-L skeleton - wing: one-piece core with elevon cut-outs, CF spar, four elevon panels on tape hinges.
Reference layout for D1, not the design. Every number from params.json via ctx.value / k09kit (DATUMS.md)."""
import k09kit as k9


def build(ctx):
    v, P = ctx.value, ctx.params
    c, half = v('wing.chord_m', 'm'), v('wing.span_m', 'm') / 2
    coords, _src = k9.section(ctx)
    hf = k9.hinge_frac(P)

    core = ctx.part('WNG-901')
    k9.wing_core(core, coords, c, half, hf, k9.span_gaps(P))

    spar = ctx.part('WNG-902')
    k9.spar_y(spar, ctx.D('DP-SPAR'), v('wing.spar.z_m', 'm'), v('wing.spar.length_m', 'm') / 2,
              v('wing.spar.od_m', 'm'), v('wing.spar.id_m', 'm'))
    ctx.contact('E-WNG-901', 'spar epoxied in the hot-wired slot')

    # right-hand elevons, then exact mirrors; hinge on the upper skin at DP-HINGE
    lim = tuple(v('wing.elevon.deflection_deg', 'deg'))
    right = [s for s in k9.elevon_spans(P) if s[0] > 0]                      # inboard, outboard
    for (y0, y1), pid, mid, edge, medge in zip(right, ('WNG-903', 'WNG-904'), ('WNG-905', 'WNG-906'),
                                               ('E-WNG-902', 'E-WNG-903'), ('E-WNG-904', 'E-WNG-905')):
        k9.elevon(ctx.part(pid), coords, c, hf, y0, y1, gap=0.001)
        k9.pair(ctx, pid, mid)
        ctx.revolute(edge, pid, 'WNG-901', at=k9.hinge_point(coords, c, hf, (y0 + y1) / 2), axis='Y', limits=lim)
        ctx.revolute(medge, mid, 'WNG-901', at=k9.hinge_point(coords, c, hf, -(y0 + y1) / 2), axis='Y', limits=lim)
