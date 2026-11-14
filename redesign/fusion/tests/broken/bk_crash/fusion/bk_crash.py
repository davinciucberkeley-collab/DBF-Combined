"""DELIBERATELY BROKEN example module (tests only): crashes while building."""


def build(ctx):
    width = 0.0
    ctx.part('XYZ-001').box((0, 0, 0), (0.1 / width, 0.1, 0.01))
