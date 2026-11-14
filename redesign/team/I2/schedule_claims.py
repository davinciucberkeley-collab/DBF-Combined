"""I2 schedule claims: puts the schedule's pass / fail lines into the proof graph (CDR-03, CDR-BT-24).

Run:  python -I redesign/team/I2/schedule_claims.py     -> claims.json beside this file. Writes nothing else.

Before 2026-11-13 `R-BUILD-HOURS` and `R-SCHEDULE` had no claim, so the two schedule fails that SCHEDULE.md states in
its verdict table did not show as FAILS in the graph. This script reads the task list of make_schedule.py (the one
source: it imports the module and runs its forward and backward pass, it does not copy a number) and emits the same
figures as claims. It does not write SCHEDULE.md; `python -I redesign/team/I2/make_schedule.py` does.

Re-run it after any change to the task list in make_schedule.py: build_graph.py re-computes these values from the
task list and reports DRIFT if the stored ones are stale.

The limits are the requirement text as it stands today (team/A2/REQUIREMENTS.md, R-BUILD-HOURS and R-SCHEDULE).
CDR decision B2 (re-word R-BUILD-HOURS to "<= 90 team-hours of build, stages 2-10, and <= 5 weeks from first cut") is
PROPOSED and needs the students' sign-off: its two measures are emitted here as information, without a limit.
"""
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True                               # importing make_schedule must not leave __pycache__
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
sys.path.insert(0, str(HERE))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

kit.source("SRC-I2-TASKS", "I2 task list (durations, hours, dependencies, not-before dates)", "web",
           url="https://github.com/davinciucberkeley-collab/DBF-Combined/blob/main/redesign/team/I2/make_schedule.py",
           where="the t(...) rows of redesign/team/I2/make_schedule.py; hours are EST with the source named per row "
                 "(BUILD-GUIDE.md stage times, H1 and H2 plans)",
           note="planning data, not a measurement: every hour figure is EST until the build logs replace it",
           status="UNVERIFIED")
kit.assumption("ASM-I2-REQ-TEXT", "Limits read from the requirement text",
               "R-BUILD-HOURS: <= 3 weeks (21 d) from first cut to first hover. R-SCHEDULE: first transition by "
               "build week 7; crash-repair loop >= 1.5 weeks calendar (10.5 d); twin flown before the 15 Dec order",
               basis="team/A2/REQUIREMENTS.md rows R-BUILD-HOURS and R-SCHEDULE (read 2026-11-13); these four limits "
                     "have no key in params.json, so they are carried here as [21, 7, 10.5, 1]",
               value=[21.0, 7.0, 10.5, 1.0], unit="d,week,d,d")
kit.assumption("ASM-I2-B2-PROPOSED", "CDR decision B2 (PROPOSED, not applied)",
               "re-word R-BUILD-HOURS to '<= 90 team-hours of build (stages 2-10) to first hover and <= 5 weeks from "
               "first cut'", basis="review/CDR-2026-11-13/CDR-SUMMARY.md section 4, B2: needs the students' sign-off; "
                                   "A2 edits the requirement after it. Until then the limits above stand",
               value=[90.0, 35.0], unit="h,d")


@kit.calc("CALC-I2-SCHEDULE", title="Schedule figures from the task list (forward and backward pass)",
          equation="earliest start = max(not-before, finish of every dependency) ; slack = latest finish - earliest "
                   "finish against complete_by ; build week = (date - build_start) // 7 + 1 ; build hours = sum of "
                   "the build-phase task hours without the transport box (TB1)",
          inputs={"build_start": P + "schedule.build_start", "complete_by": P + "schedule.complete_by",
                  "order": P + "schedule.order_date"},
          cites=["SRC-I2-TASKS"])
def schedule(build_start, complete_by, order):
    import make_schedule as ms                                  # the task list; importing runs nothing
    ms.forward()
    ms.backward()
    BY, T = ms.BY, ms.T
    wk = lambda d: (d - ms.BUILD_START).days // 7 + 1
    hov, cut, trans, crash, twin = BY["F01"], BY["B01"], BY["F04"], BY["CR1"], BY["TW3"]
    last = max(T, key=lambda z: z["ef"])
    order_d = dt.date.fromisoformat(order)
    return {
        # stage times of BUILD-GUIDE.md to first hover, stage 11 (bench checks, B19) and the range check included
        "build_h": sum(x["hours"] for x in T if x["phase"] == "build" and x["id"] != "TB1"),
        # the measure of the proposed decision B2: stages 2-10 only
        "build_h_stages_2_10": sum(x["hours"] for x in T if x["phase"] == "build"
                                   and x["id"] not in ("TB1", "RG1", "B19")),
        "pre_h": sum(x["hours"] for x in T if x["phase"] in ("pre", "closure")),
        "first_cut": cut["es"].isoformat(), "first_hover": hov["es"].isoformat(),
        "cut_to_hover_d": (hov["es"] - cut["es"]).days,
        "first_hover_week": wk(hov["es"]), "first_transition_week": wk(trans["es"]),
        "crash_loop_d": crash["days"], "end_slack_d": last["slack"], "min_slack_d": min(x["slack"] for x in T),
        "twin_before_order_d": (order_d - twin["ef"]).days,
        "dates_differ": int(ms.BUILD_START.isoformat() != build_start) + int(ms.END.isoformat() != complete_by),
    }


C = "CALC-I2-SCHEDULE"
kit.claim("CL-I2-BUILD-HOURS", "Team-hours of build to first hover (BUILD-GUIDE stage times)", calc=C,
          output="build_h", unit="h", limit=("<=", P + "requirements.build_hours_max"), verifies=["R-BUILD-HOURS"],
          note="EST: the sum of the build-phase task hours, bench checks (stage 11) and the range check included, "
               "transport box excluded (SCHEDULE.md verdict table, CR-I2-02). G4's count is 111 h (CDR decision B2)",
          how="Log hours per task during the build; compare the total at first hover.")
kit.claim("CL-I2-CUT-TO-HOVER-D", "Calendar days from first cut to first tethered hover", calc=C,
          output="cut_to_hover_d", unit="d", limit=("<=", 21.0), verifies=["R-BUILD-HOURS"],
          assumes=["ASM-I2-REQ-TEXT"],
          note="limit: '<= 3 weeks from first cut' in R-BUILD-HOURS. Set by the serial 24 h cures of the build "
               "chain (CDR decision B2); no lever in the task list removes them",
          how="Dates of the first cut and the first tethered hover in the build log.")
kit.claim("CL-I2-FIRST-HOVER-WEEK", "Build week of the first tethered hover", calc=C, output="first_hover_week",
          unit="week", limit=("<=", P + "schedule.first_hover_week"), verifies=["R-SCHEDULE"],
          note="build week 1 starts on schedule.build_start; CR-I2-01 asks A1 whether the requirement is week 4 or 5",
          how="Date of the first tethered hover (gate 3) against the build start.")
kit.claim("CL-I2-FIRST-TRANSITION-WEEK", "Build week of the first transition (gate 6)", calc=C,
          output="first_transition_week", unit="week", limit=("<=", 7.0), verifies=["R-SCHEDULE"],
          assumes=["ASM-I2-REQ-TEXT"], how="Date of the first transition flight against the build start.")
kit.claim("CL-I2-CRASH-LOOP-D", "Crash-repair loop held in the plan", calc=C, output="crash_loop_d", unit="d",
          limit=(">=", 10.5), verifies=["R-SCHEDULE"], assumes=["ASM-I2-REQ-TEXT"],
          how="Task CR1 in the task list; >= 1.5 weeks calendar.")
kit.claim("CL-I2-END-SLACK-D", "Slack of the last task against complete_by", calc=C, output="end_slack_d", unit="d",
          limit=(">=", 0.0), verifies=["R-SCHEDULE"],
          note="with one crash-repair loop in the plan; CDR-BT-10 calls 2 d thin",
          how="Re-run after every change to the task list; the last task must end on or before schedule.complete_by.")
kit.claim("CL-I2-TWIN-BEFORE-ORDER-D", "Days between the last twin flight day and the December order", calc=C,
          output="twin_before_order_d", unit="d", limit=(">=", 1.0), verifies=["R-SCHEDULE"],
          assumes=["ASM-I2-REQ-TEXT"], how="Date of the last twin flight (task TW3) against schedule.order_date.")
kit.claim("CL-I2-DATES-MATCH", "Dates in make_schedule.py that differ from params.json#schedule", calc=C,
          output="dates_differ", unit="-", limit=("<=", 0.0),
          how="BUILD_START and END in make_schedule.py against schedule.build_start and schedule.complete_by.")
kit.claim("CL-I2-BUILD-HOURS-S2-10", "Team-hours of build, stages 2-10 only (measure of the PROPOSED decision B2)",
          calc=C, output="build_h_stages_2_10", unit="h", assumes=["ASM-I2-B2-PROPOSED"],
          note="information, no limit: B2 would compare this with 90 h after 13 h EST of bench work moves before "
               "first cut (CDR-20, G4). Not applied: needs the students' sign-off",
          how="As CL-I2-BUILD-HOURS, stages 2-10.")
kit.claim("CL-I2-PRE-HOURS", "Team-hours before first cut (16 Nov - 18 Jan)", calc=C, output="pre_h", unit="h",
          note="information, no limit: R-BUILD-HOURS does not say whether pre-work counts (CR-I2-02)",
          how="Log hours per task before the build start.")

if __name__ == "__main__":
    kit.write()
