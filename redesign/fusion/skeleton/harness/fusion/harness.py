"""K09-L skeleton - harness: one lumped bundle part per side with a real body (k09kit.bundle, CR-A4-11b): a
spanwise leg in a wire channel aft of the spar from the pod side to the through-core block, and a vertical leg tied
along the tube's inboard face between the motors. The block passage between the two legs is D3's. F2's real module
routes every electrical edge with ctx.wire and keeps HRN-001 / HRN-002-L/R as mass carriers like these."""
import k09kit as k9

DIA = 0.010              # bundle diameter (m), EST: 2 ESC pairs + signal + servo lead
CHANNEL_AFT = 0.014      # channel centre aft of the spar surface (m): x = 0.105 at R1 (CR-A4-05, F2/D1 decide)


def build(ctx):
    v = ctx.value
    coords, _src = k9.section(ctx)
    c, W = v('wing.chord_m', 'm'), v('pod.size_m', 'm')[1]
    od_s, od_t = v('wing.spar.od_m', 'm'), v('fins.tube.od_m', 'm')
    yf, xt, zm = ctx.D('DP-FIN-R'), ctx.D('DP-TUBE'), ctx.D('DP-MOTOR-U')
    xch = ctx.D('DP-SPAR') + od_s / 2 + CHANNEL_AFT
    zch = (k9.surface_z(coords, c, xch / c, 'upper') + k9.surface_z(coords, c, xch / c, 'lower')) / 2
    y_block = yf - 0.012                                                 # inboard face of the through-core block
    y_tube = yf - od_t / 2 - DIA / 2                                     # on the tube's inboard face
    z_end = zm - 0.03                                                    # stop below the motor mount
    k9.bundle(ctx.part('HRN-901-R'), [((xch, W / 2, zch), (xch, y_block, zch)),
                                      ((xt, y_tube, -z_end), (xt, y_tube, z_end))], DIA)
    k9.pair(ctx, 'HRN-901-R', 'HRN-901-L')
    for e in ('E-HRN-901', 'E-HRN-902'):
        ctx.contact(e, 'taped in the wire channel')
    for e in ('E-HRN-903', 'E-HRN-904'):
        ctx.contact(e, 'tied along the tube')
