"""DELIBERATELY BROKEN example module (tests only)."""


def build(ctx):
    ctx.part('BRK-001').box((0, -0.02, 0), (0.10, 0.02, 0.01))
    ctx.part('BRK-002').box((0.11, -0.01, 0), (0.15, 0.01, 0.01))     # 10 mm gap to the frame
    ctx.part('BRK-003').box((0.98, 0.98, 0.98), (1.02, 1.02, 1.02))   # nowhere near anything
    ctx.rigid('E-BRK-01', 'BRK-002', 'BRK-001', at=(0.105, 0, 0.005))
    ctx.contact('E-BRK-99')                                           # registers an edge nobody declares
