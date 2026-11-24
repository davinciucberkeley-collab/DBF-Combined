p='electrical.py'
s=open(p,encoding='utf-8',newline='').read()
crlf = '\r\n' in s
if crlf: s=s.replace('\r\n','\n')
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,(s.count(old),old[:80])
    s=s.replace(old,new)

# I2C: waypoint so the long y-run is axis-aligned
rep("    return [(x, y, z + 0.0006), (x, y, _ZF), (0.0512 + AV_DX, -UART_Y, _ZF), (0.0512 + AV_DX, -UART_Y, I2C_ZH),",
    "    return [(x, y, z + 0.0006), (x, y, _ZF), (x, -UART_Y, _ZF), (0.0512 + AV_DX, -UART_Y, _ZF), (0.0512 + AV_DX, -UART_Y, I2C_ZH),")

# servo lead point lists as functions
rep("""def build_harness(ctx):
    build_raceway(ctx)""",
"""SRV_Z5 = 0.0183                             # T-092: lane height of the +y servo lead (S5) where it crosses the bay under the phase bundles (z >= 28) and 0.9 mm under the I2C lane (z 22, 2 x 2 bundle, bottom 21.0) at |y| 24.4; its 3 strands are stacked in z (+-1.8 mm)
SRV_DROP = {1: SRV_YD, -1: FC_YC - 0.005}   # y of the skin slit where each servo lead goes down into its groove: +y lead at |y| 24 as before; -y lead at its own FC pad S6 (y -80), between the FC bosses (y -84.5 and -65.5 edges), slit 8 mm wide
SRV_HW = {1: 0.0045, -1: 0.0040}            # slit half width in y
ESC_XH, ESC_ZH = 0.0685, 0.0415             # T-092: lane of the ESC signal bundle along y (x 68.5, z 41.5: under the 44.5 mm roof inner face, over the phase bundles z <= 37.9, 1.9 mm aft of the RX / GPS lanes)


def servo_lead_pts(sg):
    \"\"\"Waypoints of servo lead sg (+1 R / -1 L): FC pad S5 / S6 -> to the skin slit (+y lead crosses the bay at z SRV_Z5 under the cover, -y lead drops at its own pad) -> groove along y 3 mm under the skin -> along the skin to the servo.\"\"\"
    x, y, z = FC_PADS['S5' if sg > 0 else 'S6']
    z0 = z + 0.0006
    yd = SRV_DROP[sg]
    zg1 = servo_zc(SRV_XD)
    xs_ = [SRV_XD, 0.083, 0.097, 0.110, 0.1215]
    if sg > 0:
        pts = [(x, y, z0), (SRV_XD, y, SRV_Z5), (SRV_XD, yd, SRV_Z5), (SRV_XD, yd, zg1), (SRV_XD, sg * SRV_YG, zg1)]
    else:
        pts = [(x, y, z0), (SRV_XD, y, z0), (SRV_XD, yd, zg1), (SRV_XD, sg * SRV_YG, zg1)]
    pts += [(xx, sg * SRV_YG, servo_zc(xx)) for xx in xs_[1:]]
    pts += [(0.1265, sg * SRV_YG, 0.0083), (0.1305, sg * SERVO_Y, SV_Z1 + 0.003)]
    return pts


def servo_lead_pts_old(sg):
    \"\"\"Route with the FC on the wing centre (T-084 and before), for the mass delta only: pad at y = sg * 5 mm, drop at |y| 24.\"\"\"
    x, y, z = FC_PADS['S5' if sg > 0 else 'S6']
    y = sg * 0.005
    z0 = z + 0.0006
    zg1 = servo_zc(SRV_XD)
    xs_ = [SRV_XD, 0.083, 0.097, 0.110, 0.1215]
    pts = [(x, y, z0), (SRV_XD, y, z0), (SRV_XD, sg * SRV_YD, z0), (SRV_XD, sg * SRV_YD, zg1), (SRV_XD, sg * SRV_YG, zg1)]
    pts += [(xx, sg * SRV_YG, servo_zc(xx)) for xx in xs_[1:]]
    pts += [(0.1265, sg * SRV_YG, 0.0083), (0.1305, sg * SERVO_Y, SV_Z1 + 0.003)]
    return pts


def esc_path():
    \"\"\"ESC signal bundle: ESC SIG pad -> forward over the ESC -> up to the high lane (x 68.5, z 41.5) -> along y under the cover roof to the FC ESC pad row -> aft edge -> down onto the pad.\"\"\"
    sx, sy_ = ESC_PADS['SIG']
    fx, fy, fz = FC_PADS['ESC']
    _zr = ESC_TOP + 0.0046
    return [(sx, sy_, ESC_TOP + 0.002), (sx - 0.007, sy_, _zr), (0.0905 + AV_DX, sy_, _zr), (ESC_XH, sy_, ESC_ZH), (ESC_XH, fy, ESC_ZH), (fx, fy, ESC_ZH), (fx, fy, fz + 0.0016)]


def gps_path():
    (gx0, gy0), (gx1, gy1) = GPS_B
    gcx = (gx0 + gx1) / 2
    zp_ = ZP + T_PCB + 1.8 * MM
    x, y, z = FC_PADS['GPS']
    return [(gcx, gy0 + 2.0 * MM, zp_), (gcx, 0.02475, zp_), (gcx, 0.02475, _ZF), (gcx, y, _ZF), (x, y, _ZF), (x, y, z + 0.0006)]


def build_harness(ctx):
    build_raceway(ctx)""")

# hrn_items: ESC ribbon, GPS, servo extension (HRN_ITEMS defined before build_harness: functions defined later are fine since hrn_items() runs at import... check order below)
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n','\r\n') if crlf else s)
print('ok')
