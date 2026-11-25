p='electrical.py'
s=open(p,encoding='utf-8',newline='').read()
crlf = '\r\n' in s
if crlf: s=s.replace('\r\n','\n')
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,(s.count(old),old[:80])
    s=s.replace(old,new)

# hrn_items text/values
rep("""            ('ESC signal ribbon 6 x 26 AWG x 73 mm (CAD) at 2.0 g/m (EST)', round(6 * 0.073 * WIRE_G_PER_M[26], 1)),""",
"""            ('ESC signal ribbon 6 x 26 AWG x %.0f mm (CAD route to the FC at y -75, T-092) at 2.0 g/m (EST)' % (_plen(esc_path()) * 1e3), round(6 * _plen(esc_path()) * WIRE_G_PER_M[26], 1)),""")
rep("""            ('RX / GPS leads: 4 conductors of 28 AWG x %.0f mm (CAD route, T-022 Q4) + 6 x about 70 mm at 1.2 g/m (EST) + 2 JST plugs 0.5 g each (EST)' % (_plen(uart_path()) * 1e3),
             round(4 * _plen(uart_path()) * WIRE_G_PER_M[28] + 6 * 0.070 * WIRE_G_PER_M[28] + 1.0, 1)),""",
"""            ('RX / GPS leads: RX 4 conductors of 28 AWG x %.0f mm and GPS 6 x %.0f mm (CAD routes, T-022 Q4, T-092) at 1.2 g/m (EST) + 2 JST plugs 0.5 g each (EST)' % (_plen(uart_path()) * 1e3, _plen(gps_path()) * 1e3),
             round(4 * _plen(uart_path()) * WIRE_G_PER_M[28] + 6 * _plen(gps_path()) * WIRE_G_PER_M[28] + 1.0, 1)),""")
rep("""            ('servo leads: the 3-wire leads are in the 20.5 g servo mass (EST: stock length reaches the FC pads), plus 2 groove fish-wire ties', 0.2),""",
"""            ('servo leads: the 3-wire leads are in the 20.5 g servo mass (EST: stock length reached the old FC pads at the wing centre), plus 2 groove fish-wire ties', 0.2),
            ('servo lead extension (T-092, D-239): the +y lead (S5) now runs %+.0f mm longer than the centre-FC route (stock lead length "-": assumed to end at the old pad), 3 x 26 AWG at 2.0 g/m + 1 splice 0.15 g (EST); the -y lead is %.0f mm shorter and is cut to length (its stock lead is already in the servo mass: conservative, not subtracted)'
             % ((_plen(servo_lead_pts(1)) - _plen(servo_lead_pts_old(1))) * 1e3, (_plen(servo_lead_pts_old(-1)) - _plen(servo_lead_pts(-1))) * 1e3),
             round(3 * max(0.0, _plen(servo_lead_pts(1)) - _plen(servo_lead_pts_old(1))) * WIRE_G_PER_M[26] + 0.15, 1)),""")

# ESC ribbon wire
old_esc = s[s.rindex("    sx, sy_ = ESC_PADS['SIG']\n    fx, fy, fz = FC_PADS['ESC']"):s.index("    core = ctx.components['WNG-001']\n    for i, (key, sg) in enumerate")]
new_esc = """    # D-194 / T-092 (D-239): ESC signal bundle from the ESC SIG pad forward over the ESC at 24 mm, up to the high lane (x 68.5, z 41.5), along y under the cover roof (main cover, then the FC annex) to the FC row y -75, aft edge, down onto the ESC pad. 6 x 26 AWG as a 3 x 2 bundle, smooth, drape 1 mm
    wd = 1.3 * MM                                              # EST 26 AWG silicone OD
    rib = [((j % 3 - 1) * wd, (j // 3 - 0.5) * wd) for j in range(6)]
    _wire_s(ctx, 'E-HRN-06', esc_path(), [0.004, 0.008, 0.006, 0.004, 0.004], wd, rib, sag={1: (0.0010, (0, 0, -1))})
"""
s=s.replace(old_esc,new_esc)

# servo leads loop body
i0=s.index("    for i, (key, sg) in enumerate((('S5', 1), ('S6', -1))):")
i1=s.index("    # RX CRSF wire: FC top board RX pad")
new_srv = """    for i, (key, sg) in enumerate((('S5', 1), ('S6', -1))):
        yc = sg * SERVO_Y
        # D-198 / T-092: out of the FC aft edge (+y lead: over the board edge at x 64, along y at z SRV_Z5 across the bay and the FC annex, under the cover; -y lead: straight down at its own pad), down through a slit in the skin into a
        # groove in the foam core 3 mm under the upper skin (ribbon 3 x 1.2 mm), outboard along y at x 64, then aft along the skin to the servo pocket wall. Only the last 6 mm (pocket wall to the lead boot) is exposed.
        yd, hw = SRV_DROP[sg], SRV_HW[sg]
        zg1 = servo_zc(SRV_XD)
        xs_ = [SRV_XD, 0.083, 0.097, 0.110, 0.1215]
        _wire_s(ctx, 'E-HRN-%02d' % (7 + i), servo_lead_pts(sg), 0.003, 1.2 * MM, [(-1.2 * MM, 0.0), (0.0, 0.0), (1.2 * MM, 0.0)])
        # grooves in the core (routed, shop cuts): drop slot, y run, x run following the skin
        ya, yb = sorted((yd - hw, yd + hw))
        core.cut_box((SRV_XD - 0.0035, ya, zg1 - 0.0020), (SRV_XD + 0.0035, yb, 0.0150), name='servo lead drop slot through the skin (D-198, T-092: %s lead at y %.0f mm)' % ('+y' if sg > 0 else '-y', yd * 1e3))
        ya, yb = sorted((yd - sg * hw, sg * (SRV_YG + 0.0030)))
        core.cut_box((SRV_XD - 0.0030, ya, zg1 - 0.0016), (SRV_XD + 0.0030, yb, zg1 + 0.0016), name='servo lead groove along y, 3 mm under the skin (D-198)')
        loop = [(xx, servo_zc(xx) - 0.0016) for xx in [SRV_XD - 0.003, SRV_XD, 0.083, 0.097, 0.110, 0.1215, 0.1250]] + [(xx, servo_zc(xx) + 0.0016) for xx in [0.1250, 0.1215, 0.110, 0.097, 0.083, SRV_XD, SRV_XD - 0.003]]
        ya, yb = sorted((sg * (SRV_YG - 0.0030), sg * (SRV_YG + 0.0030)))
        core.cut_prism('Y', ya, [loop], yb - ya, name='servo lead groove along x, following the skin (D-198)')
        if sg > 0:       # T-092: the -y groove no longer crosses the left centre bulkhead (it starts at y -76, outboard of |y| 60)
            ya, yb = sorted((sg * (CN_Y - 0.0001), sg * (CN_Y + FNB_T + 0.0001)))
            ctx.components['WNG-013-R'].cut_box((SRV_XD - 0.0030, ya, zg1 - 0.0016), (SRV_XD + 0.0030, yb, zg1 + 0.0016), name='servo-lead slot 6 x 3.2 mm in the centre bulkhead (= the groove, T-077 p8)')
"""
s=s[:i0]+new_srv+s[i1:]

# GPS
g0=s.index("    # GPS cable: GPS plug (inner edge) -> FC GPS pad")
g1=s.index("    # airspeed cable: FC I2C pad")
new_gps = """    # GPS cable: GPS plug (inner edge) -> up inside the cover wall slot -> across the bay and the FC annex at z 40.5 (x 42.5) -> FC GPS pad (T-092: pad at y -80)
    _wire_s(ctx, 'E-HRN-10', gps_path(), 0.0025, wd, [((j % 3 - 1) * wd, (j // 3 - 0.5) * wd) for j in range(6)], lay=0.100)
"""
s=s[:g0]+new_gps+s[g1:]
a=s.index("SRV_Z5 = 0.0183")
b=s.index("def build_harness(ctx):")
blk=s[a:b]
s=s[:a]+s[b:]
i=s.index("def hrn_items():")
s=s[:i]+blk+s[i:]
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n','\r\n') if crlf else s)
print('ok')
