"""Concept A proof chain, part 3: cost (G7, budget), schedule, transport, 3-D gates.

Cost re-computes the BOM roll-up (bom_a.py arithmetic) from the 38 BOM-A.csv rows held in params-A.json; the schedule re-runs
schedule_a.py's model. The 3-D gate counts are read from the stored collision and assembly outputs (cad/out/*.json): the Blender
collision run and the sweep are not re-run here. Run via run_all.py.
"""
import sys
from datetime import date, timedelta as td
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs"))     # redesign/proofs
import proofkit as pk  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from claimhelp_a import make_stored, pin, read_value  # noqa: E402,F401

kit = pk.Kit(__file__, params=["../params-A.json"], out="claims.a3_program.json")
stored = make_stored(kit)


# ================================================================ cost
@kit.calc("CALC-A-COST", equation="total = goods x (1 + tax) + shipping + FAA + crash reserve; +30 % on the unverified lines for the margin (bom_a.py)",
          inputs={"rows": "P:cost.bom_rows", "tax": "P:cost.tax", "faa": "P:cost.faa_usd", "ship": "P:cost.ship_usd", "bump": "P:cost.bump",
                  "tubes": "P:cost.reserve_tube_ids", "budget": "P:req.budget_usd"})
def bom_cost(rows, tax, faa, ship, bump, tubes, budget):
    sh = dict(ship)
    shipping = sum(sh[g] for g in {r[2] for r in rows})
    line = lambda i: next(r[4] for r in rows if r[0] == i)

    def total(b):
        goods = sum(q * u * (1 + (b if unv else 0)) for _, _, _, q, u, unv in rows)
        f = 1 + b
        air = line("R01") * f + sum(r[3] * r[4] for r in rows if r[0] in tubes) + 0.5 * line("R03") * f
        reserve = (line("W01") + line("P01") + line("M01") + air) * (1 + tax) + sh["TMotor"] + sh["RMRC"] + sh["Amazon"]
        return goods * (1 + tax) + shipping + faa + reserve, reserve
    t0, r0 = total(0.0)
    t30, r30 = total(bump)
    return {"total_usd": t0, "total_30_usd": t30, "margin_usd": budget - t0, "margin_30_usd": budget - t30, "reserve_usd": r0, "shipping_usd": shipping}


kit.claim("CL-A-COST-TOTAL", "BOM total incl. tax, shipping, FAA and crash reserve", calc="CALC-A-COST", output="total_usd", unit="USD", limit=("<=", "P:req.g7_total_usd"),
          verifies=["A-U1"], how="python -I qp/A/bom_a.py (reads BOM-A.csv): $1,775.09; gate G7 total <= $1,800. 14 of 38 lines are unverified (U / EST).")
kit.claim("CL-A-COST-MARGIN30", "Margin to $2,000 if the unverified lines run 30 % over", calc="CALC-A-COST", output="margin_30_usd", unit="USD",
          limit=(">=", "P:req.g7_margin_usd"), verifies=["A-U1"], how="python -I qp/A/bom_a.py: +$105.08 at +30 %; gate G7 margin >= $100. Two new EST lines (R12 / R13): if either rises by > $9 the margin falls under $100.")
kit.claim("CL-A-COST-BUDGET", "BOM total with the unverified lines +30 % against the $2,000 budget", calc="CALC-A-COST", output="total_30_usd", unit="USD",
          limit=("<=", "P:req.budget_usd"), verifies=["A-U1"], how="python -I qp/A/bom_a.py; Makers Pass outside the budget (user, memory).")


# ================================================================ schedule
def _run(gates, start, repair, redo, recess, booked, p, crash):
    r0, r1 = (date.fromisoformat(x) for x in recess)

    def rate(d):
        return (booked + (1 if r0 <= d <= r1 else 0)) * p

    def advance(d, need):
        while need > 0:
            r = rate(d)
            if need <= r:
                return d + td(days=round(7 * need / r))
            need -= r
            d += td(days=7)
        return d
    d, end = start, start
    for i, n in enumerate(gates):
        d = advance(d, n)
        end = d
        if crash and i == 3:                                   # after F04: repair loop, then F04 repeated
            d += td(days=repair)
            d = advance(d, redo)
            end = d
    return end


@kit.calc("CALC-A-SCHED", equation="schedule_a.py: gates F01-F06 at booked x p mornings a week, one crash loop after F04; slack = deadline - end of F06; latest-safe F01 start by search",
          inputs={"gates": "P:sched.gates", "start": "P:sched.start", "deadline": "P:sched.deadline", "repair": "P:sched.repair_days", "redo": "P:sched.redo",
                  "recess": "P:sched.recess", "booked": "P:sched.booked", "p": "P:sched.p_fly", "p_sens": "P:sched.p_fly_sens", "req_f01": "P:sched.latest_safe_f01"})
def schedule(gates, start, deadline, repair, redo, recess, booked, p, p_sens, req_f01):
    s, dl = date.fromisoformat(start), date.fromisoformat(deadline)
    end = _run(gates, s, repair, redo, recess, booked, p, True)
    late = s
    while _run(gates, late, repair, redo, recess, booked, p, True) > dl:
        late -= td(days=1)
    while _run(gates, late + td(days=1), repair, redo, recess, booked, p, True) <= dl:
        late += td(days=1)
    end_sens = _run(gates, s, repair, redo, recess, booked, p_sens, True)
    return {"slack_days": (dl - end).days, "f01_slack_days": (late - s).days, "f01_to_req_days": (date.fromisoformat(req_f01) - s).days,
            "slack_sens_days": (dl - end_sens).days}


kit.claim("CL-A-SCHED-SLACK", "Slack between the end of F06 and 2027-04-30 (baseline)", calc="CALC-A-SCHED", output="slack_days", unit="d", limit=(">=", 0),
          verifies=["A-U2"], how="python -I qp/A/schedule_a.py; baseline 4 booked mornings a week, p 0.72, one crash loop; F06 ends 19 Apr. Flyable fraction is EST (RFS wind unmeasured).")
kit.claim("CL-A-SCHED-F01", "Latest-safe F01 start minus the planned start (8 Feb)", calc="CALC-A-SCHED", output="f01_slack_days", unit="d", limit=(">=", 0),
          verifies=["A-D8"], how="schedule_a.py latest_start(): 18 Feb on the baseline; re-plan when the main order is not placed by 28 Dec.")
kit.claim("CL-A-SCHED-F01-DATE", "Days from the planned F01 start to the 2027-02-18 trigger", calc="CALC-A-SCHED", output="f01_to_req_days", unit="d", limit=(">=", 0),
          verifies=["A-D8"], how="First tethered hover 8-13 Feb; trigger 2027-02-18 (BOARD QP-3 R4).")
kit.claim("CL-A-SCHED-SENS", "Slack at p 0.60 (sensitivity, not the baseline)", calc="CALC-A-SCHED", output="slack_sens_days", unit="d",
          how="schedule_a.py with p 0.60.", note="Sensitivity, no limit stated: SCHEDULE-A.md lists p 0.60 as a sensitivity; it ends 5 days after the deadline with 4 booked mornings and one crash loop (5 booked mornings: +12 d).")


# ================================================================ transport
@kit.calc("CALC-A-BOX", equation="max over the three sorted dimensions of packed / limit (1.0 = exactly at the box limit)", assumes=["ASM-A-TRUNK"],
          inputs={"box": "P:box.packed_m", "lim": "P:req.box_limit_m"}, output="ratio")
def box_fit(box, lim):
    return max(a / b for a, b in zip(sorted(box, reverse=True), sorted(lim, reverse=True)))


kit.claim("CL-A-BOX-FIT", "Packed box against the 1.2 x 0.5 x 0.4 m car-trunk box", calc="CALC-A-BOX", output="ratio", unit="-", limit=("<=", 1.0),
          verifies=["A-U3"], assumes=["ASM-A-TRUNK"], how="Measure the team's car trunk opening and floor (subsystems/transport/CAR-FIT.md procedure) and the packed aircraft with props on.",
          note="limit 1.0 = the C3(a) box limit; the width 0.50 m sits exactly on the 0.50 m limit (ratio 1.00).")


# ================================================================ 3-D gates (stored outputs of collide_a.py and a_assembly.py)
CAD_PARTS = ["WNG-006-R", "WNG-006-L", "WNG-008-RU", "WNG-008-RL", "WNG-008-LU", "WNG-008-LL"]
stored("CL-A-COLL-COUNT", "Part overlaps deeper than the tolerance (neutral, +-20, +-21 deg)", "P:cad3d.n_over_tol", "-", limit=("<=", 0), verifies=["A-U4"], parts=CAD_PARTS,
       how="python -I qp/A/cad/collide_a.py (Blender, 78 parts, 175 bodies, 0.05 mm); A_ELEV_POSE=20|22 for the other poses.",
       equation="count of hits with depth > tolerance in cad/out/report_pose20.json and report_pose21.json; read, not re-run")
stored("CL-A-COLL-DEPTH", "Deepest part overlap at any reachable pose", "P:cad3d.max_depth_mm", "mm", limit=("<=", "P:req.coll_tol_mm"), verifies=["A-U4"], parts=["WNG-007-R", "WNG-007-L", "WNG-008-RU", "WNG-008-LU", "HWC-001", "HWC-003"],
       how="collide_a.py report (D-194): the only hits under the 0.05 mm gate are the two balance horn tabs touching their stop bosses at the +21 deg stop (0.042 mm, WNG-007 on WNG-008, a designed contact) and one M2 nut on its screw shank (0.034 mm, HWC-003 on HWC-001); +-22 deg is past the stop and is not a reachable pose.",
       equation="largest depth_mm over the reachable poses in the stored reports; read, not re-run")
stored("CL-A-WIRE-ENDS", "Wire ends not seated in a part", "P:cad3d.wire_ends_open", "-", limit=("<=", 0), verifies=["A-U4"], how="collide_a.py wire_ends check (41 strands).",
       equation="len(wire_ends) in cad/out/report.json; read, not re-run")
stored("CL-A-WIRE-FOLDS", "Wire folds (kinks)", "P:cad3d.wire_kinks", "-", limit=("<=", 0), verifies=["A-U4"], how="collide_a.py kinks check.", equation="len(kinks) in cad/out/report.json; read, not re-run")
stored("CL-A-ASSY-STEPS", "Build steps that pass the assembly sweep", "P:cad3d.assy_steps_ok", "-", limit=(">=", "P:cad3d.assy_steps"), verifies=["A-U4"],
       how="python -I qp/A/cad/a_assembly.py: 28 of 28 steps, 0 blocked, 0 unsupported, no wire laid before its ends.",
       equation="steps with no blocking pair in cad/out/assembly.json; read, not re-run")
stored("CL-A-ASSY-PARTS", "Parts placed by the build sequence", "P:cad3d.assy_parts_placed", "-", limit=(">=", "P:cad3d.parts"), verifies=["A-U4"],
       how="a_assembly.py: 78 of 78 parts placed, none missing from the sequence.", equation="parts across the steps of cad/out/assembly.json; read, not re-run")

if __name__ == "__main__":
    kit.write()
