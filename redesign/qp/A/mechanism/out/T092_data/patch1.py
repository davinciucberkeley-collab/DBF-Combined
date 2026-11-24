p='electrical.py'
s=open(p,encoding='utf-8',newline='').read()
crlf = '\r\n' in s
if crlf: s=s.replace('\r\n','\n')
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,(s.count(old),old[:80])
    s=s.replace(old,new)

# --- FC constants
rep("FC_CX = FC_X0 + FC_LX / 2\n",
"FC_CX = FC_X0 + FC_LX / 2\n"
"FC_YC = -0.075                                                         # T-092 (D-239): board centre 75 mm off the wing centre along the spar, on the LEFT (-y) side (CAD +y = right wing, servo R). Reasons (T092_report.md s1): the pitch-gain benefit is the T-091 node s+-0.075 (beam FE symmetric in y); one enclosed annex of the bay cover instead of a tunnel past the GPS (GPS board y +27.5..52.5 is on +y); the RX UART and airspeed I2C leads go to -y anyway; cost: CG y moves from -1.66 mm by 28 g x 75 mm / total (about -1.3 mm, limit 5 mm, A-P4); FC hard mount unchanged (D-186)\n")
rep("FC_HOLES = [(FC_CX + sx * 0.0125, sy * 0.0125)","FC_HOLES = [(FC_CX + sx * 0.0125, FC_YC + sy * 0.0125)")
rep("FC_B = ((FC_X0, -FC_LY / 2, FC_ZB), (FC_X0 + FC_LX, FC_LY / 2, FC_ZB_TOP))","FC_B = ((FC_X0, FC_YC - FC_LY / 2, FC_ZB), (FC_X0 + FC_LX, FC_YC + FC_LY / 2, FC_ZB_TOP))")
rep("""FC_PADS = {'ESC': (FC_X0 + FC_LX - 0.0025, 0.0, FC_ZB_TOP), 'S5': (FC_X0 + FC_LX - 0.0025, 0.005, FC_ZB_TOP), 'S6': (FC_X0 + FC_LX - 0.0025, -0.005, FC_ZB_TOP),
           'GPS': (FC_X0 + 0.0025, 0.005, FC_ZB_TOP), 'I2C': (FC_X0 + 0.0025, -0.005, FC_ZB_TOP), 'RX': (FC_X0 + FC_LX - 0.0080, 0.0, FC_ZB_TOP)}""",
"""# T-092: the whole layout moves with the board (y + FC_YC); GPS and I2C pads swap sides (EST layout, the Holybro page gives names only) so that the GPS lead, which arrives from +y, ends on the outer (-y) pad and the I2C lead, which leaves towards +y then -y, does not cross it
FC_PADS = {'ESC': (FC_X0 + FC_LX - 0.0025, FC_YC, FC_ZB_TOP), 'S5': (FC_X0 + FC_LX - 0.0025, FC_YC + 0.005, FC_ZB_TOP), 'S6': (FC_X0 + FC_LX - 0.0025, FC_YC - 0.005, FC_ZB_TOP),
           'GPS': (FC_X0 + 0.0025, FC_YC - 0.005, FC_ZB_TOP), 'I2C': (FC_X0 + 0.0025, FC_YC + 0.005, FC_ZB_TOP), 'RX': (FC_X0 + FC_LX - 0.0080, FC_YC, FC_ZB_TOP)}""")

# --- annex constants and loops
rep("def cov_outer():",
"""AN_X1 = COV_STEP_X                          # T-092 (D-239): FC annex of the cover (-y side, over the FC at y -52.5..-97.5): aft wall at the main roof step x 72.2; flat roof 45 mm (same ramp as the cover)
AN_YI = 0.0990                              # annex inner half width (outer end wall face 99.6 mm): 1.5 mm clear of the FC edge (y -97.5), EST design value


def an_outer():
    \"\"\"Annex roof outer profile (x, z): front on the skin, ramp, flat roof, aft wall down to the skin.\"\"\"
    return [(COV_X0, zu(COV_X0)), (COV_RAMP_X, COV_ZH1), (AN_X1, COV_ZH1), (AN_X1, zu(AN_X1))]


def an_loops():
    o = an_outer()
    i = [(o[0][0] + 0.0012, zu(COV_X0 + 0.0012))] + [(x, z - COV_T) for x, z in o[1:-2]] + [(o[-2][0] - COV_T, o[-2][1] - COV_T), (AN_X1 - COV_T, zu(AN_X1 - COV_T))]
    return o + i[::-1]


def an_side_loop():
    o = an_outer()
    return o + skin_pts(COV_X0, AN_X1)[-2:0:-1]


def cov_outer():""")
# skin_pts must exist before an_side_loop is CALLED (only called at build): fine.
rep("""    a = o[:4] + [(xc, COV_ZH2), (xc, zu(xc))] + [p_ for p_ in sk[1:-1] if p_[0] < xc][::-1] + [sk[0]]""",
"""    # T-092: the -y wall is open over the FC annex (x < AN_X1): the wall piece starts at the annex aft wall
    a = o[2:4] + [(xc, COV_ZH2), (xc, zu(xc))] + [p_ for p_ in sk[1:-1] if AN_X1 < p_[0] < xc][::-1] + [(AN_X1, zu(AN_X1))]""")
rep("""    return HOOD_X0 < x < HOOD_X1 and -HOOD_Y1 < y <= -COV_Y and zu(x) - 0.0003 < z < HOOD_ZR""",
"""    if COV_X0 < x < AN_X1 and -AN_YI < y <= -COV_Y:      # T-092 FC annex
        o = an_outer()
        for (x0, z0), (x1, z1) in zip(o, o[1:]):
            if x0 <= x <= x1 and x1 > x0:
                return z < z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return False
    return HOOD_X0 < x < HOOD_X1 and -HOOD_Y1 < y <= -COV_Y and zu(x) - 0.0003 < z < HOOD_ZR""")
rep("""    return round((arch + wall + hood_volume_m3()) * 1e6 * RHO_PETG_, 1)""",
"""    arch += abs(_poly_area_(an_loops())) * (AN_YI - COV_Y)                 # T-092 FC annex roof band + aft wall
    wall += abs(_poly_area_(an_side_loop())) * COV_T                       # annex outer end wall
    return round((arch + wall + hood_volume_m3()) * 1e6 * RHO_PETG_, 1)""")
rep("""    cv.prism('Y', COV_Y, [cov_side_loop()], COV_T, name='cover end wall (0.6 mm)')""",
"""    cv.prism('Y', COV_Y, [cov_side_loop()], COV_T, name='cover end wall (0.6 mm)')
    cv.prism('Y', -AN_YI, [an_loops()], AN_YI - COV_Y, name='FC annex roof band and aft wall (T-092, D-239; 0.5 mm vacuum-formed, EST design value)')
    cv.prism('Y', -AN_YI - COV_T, [an_side_loop()], COV_T, name='FC annex outer end wall (T-092)')""")
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n','\r\n') if crlf else s)
print('ok',crlf)
