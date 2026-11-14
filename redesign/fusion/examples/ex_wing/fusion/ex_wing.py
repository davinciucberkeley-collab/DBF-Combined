"""Example subsystem: left wing panel (loft of NACA sections), right panel by mirror, spar tube, hinged aileron,
aileron servo. Generic test aircraft - not a design. Frame: metres, x aft, y right, z up."""
import fusionkit as fk


def build(ctx):
    P = ctx.local
    code, c, le, zc = P['airfoil'], P['chord_m'], P['le_x_m'], P['chord_z_m']
    hf = P['hinge_frac']

    # wing box (0..hinge chord) lofted root -> tip on Y-normal planes; left wing is -y
    panel = ctx.part('WNG-001')
    sec = fk.airfoil(code, c, le=(le, zc), x0=0.0, x1=hf)
    panel.loft('Y', [(-P['root_y_m'], sec), (-P['tip_y_m'], sec)], smooth=True)
    ctx.mirror('WNG-001', 'WNG-002', plane='XZ')

    # spar tube through both panels, along Y
    spar = ctx.part('WNG-003')
    xs = le + P['spar_x_frac'] * c
    h = P['spar_half_m']
    spar.tube('Y', (xs, -h, P['spar_z_m']), 2 * h, P['spar_od_m'] / 2, P['spar_id_m'] / 2)

    # aileron = aft part of the section, over part of the span
    y0, y1 = P['aileron_y_m']
    ail = ctx.part('WNG-004')
    asec = fk.airfoil(code, c, le=(le, zc), x0=hf, x1=1.0, n=8)
    ail.loft('Y', [(-y0, asec), (-y1, asec)])

    servo = ctx.part('WNG-005')
    servo.box(P['servo_lo_m'], P['servo_hi_m'])

    # registrations (edge ids from interfaces.json)
    ctx.rigid('E-WNG-01', 'WNG-003', 'FUS-001', at=(xs, 0.0, P['spar_z_m'] - P['spar_od_m'] / 2))
    ctx.contact('E-WNG-02', 'epoxy, spar bore in panel L')
    ctx.contact('E-WNG-03', 'epoxy, spar bore in panel R')
    yc, _ = fk.naca4_line(code, hf)
    hinge = (le + hf * c, -(y0 + y1) / 2, zc + yc * c)
    d = P['deflection_deg']
    ctx.revolute('E-WNG-04', 'WNG-004', 'WNG-001', at=hinge, axis='Y', limits=(-d, d))
    lo, hi = P['servo_lo_m'], P['servo_hi_m']
    ctx.rigid('E-WNG-05', 'WNG-005', 'WNG-001', at=((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]))
