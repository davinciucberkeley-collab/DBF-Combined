"""K09-L skeleton - power: flight pack at the D-24 station (nominal centroid x -0.001: D2's pack aft face
subsystems/pod/params.json#pack_aft_face_m[0] less half the pack length; the pod centre if D2 has not published it)
and one lump for the disconnect, main leads and UBEC ahead of it at the pod nose. Reference layout for F1 and E2.
The skeleton reports the pack station the CG target needs (CL-A5-PACK-X-FOR-CG)."""
import k09kit as k9


def build(ctx):
    l, w, h = ctx.value('battery.size_m', 'm')
    xc = k9.lval(k9.local('pod'), 'pack_aft_face_m', 'm', [ctx.D('DX-POD')[0] + l / 2])[0] - l / 2
    z0 = ctx.D('DP-POD-BASE') + 0.003                                   # tray
    ctx.part('PWR-901').box((xc - l / 2, -w / 2, z0), (xc + l / 2, w / 2, z0 + h))
    x0 = ctx.D('DP-POD-LE') + 0.005                                     # disconnect + leads ahead of the pack
    ctx.part('PWR-902').box((x0, -0.02, z0), (min(x0 + 0.02, xc - l / 2), 0.02, z0 + 0.02))
    ctx.contact('E-PWR-901', 'strap + Velcro on the tray')
    ctx.contact('E-PWR-902', 'foam tape on the tray')
