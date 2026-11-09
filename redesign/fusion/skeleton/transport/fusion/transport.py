"""K09-L skeleton - transport (flight: false): the 1.25 x 0.55 x 0.50 m box (CHANGE-LOG D-16) around the aircraft
in its transport position (aircraft frame, upright, props off, box centre DX-BOX), two spar cradles under the
lower skin and a prop tray. check.py touch-checks the cradle-to-wing edges, skips the stowed prop edges and warns
when a cradle, the tray or a box wall overlaps a flight part (pressed, or does not fit). Reference layout for D7."""
import k09kit as k9

CRADLE_Y = 0.20          # cradle station |y| (m): C1's assumption behind the 70 mm crush foam (CHANGE-LOG D-22)
CRADLE_L, CRADLE_W = 0.06, 0.05     # cradle length along x, width along y (m), EST: D7 sizes


def build(ctx):
    v, P = ctx.value, ctx.params
    _c, ext, inner = k9.box_frame(P)
    k9.box_shell(ctx.part('TRN-901'), ext, v('requirements.box_wall_m', 'm'))
    coords, _src = k9.section(ctx)
    c, xs = v('wing.chord_m', 'm'), ctx.D('DP-SPAR')
    z_top = k9.surface_z(coords, c, xs / c, 'lower')                     # lower skin under the spar
    floor = inner[0][2]
    ctx.part('TRN-902-R').box((xs - CRADLE_L / 2, CRADLE_Y - CRADLE_W / 2, floor),
                              (xs + CRADLE_L / 2, CRADLE_Y + CRADLE_W / 2, z_top))
    k9.pair(ctx, 'TRN-902-R', 'TRN-902-L')
    ctx.part('TRN-903').box((0.0, -0.15, floor), (0.30, 0.15, floor + 0.045))   # four props stacked flat
    for e in ('E-TRN-901', 'E-TRN-902', 'E-TRN-903'):
        ctx.contact(e, 'bonded to the box floor')
    for e in ('E-TRN-904', 'E-TRN-905'):
        ctx.contact(e, 'lower skin rests on the cradle; strap over the centre section')
    for i in range(4):
        ctx.contact('E-TRN-%d' % (906 + i), 'prop in its tray slot (stowed: not touch-checked)')
