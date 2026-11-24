"""Helpers shared by the concept A claim scripts (not a claims file)."""


def pin(group, *names):
    """{name: "P:group.name"} for a calculation's inputs."""
    return {n: f"P:{group}.{n}" for n in names}


def read_value(v):
    """A stored result: the value of a parameter whose source is the report that produced it (not recomputed)."""
    return v


def make_stored(kit):
    def stored(cid, title, param, unit, limit=None, verifies=(), parts=(), how=None, assumes=(), note=None, equation=None):
        """Claim whose value is read from a stored output file (the parameter's source), through a `read_value` calculation."""
        calc = "CALC-" + cid[3:] + "-READ"
        kit.calc(calc, inputs={"v": param}, equation=equation or "value read from the stored report named by the parameter's source (not re-run)",
                 title="Stored result: " + title, assumes=assumes, output="v")(read_value)
        return kit.claim(cid, title, calc=calc, output="v", unit=unit, limit=limit, verifies=verifies, parts=parts, how=how, assumes=assumes, note=note)
    return stored
