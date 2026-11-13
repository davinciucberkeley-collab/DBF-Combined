"""I2 schedule planner: writes SCHEDULE.md (Gantt table, critical path, team-of-4 load) from the task list below.

Run:  python -I redesign/team/I2/make_schedule.py       (no inputs besides this file; deterministic)

Method. TASKS is the one list (data, not analysis). Each task has an owner set (P1..P4, roles not names), a duration in calendar days
(cures included), person-hours (EST, with the source of the number), a "not before" date and dependencies. The script runs a
forward pass (earliest start = max(not-before, finish of every dependency)) and a backward pass to the end of April, so slack and the
critical path are computed, not asserted. Hours are spread evenly over the task's working days (Mon-Fri) among its owners.

Dates tie to: team/I1/ORDER-PLAN.md (early order 20 Nov, lead 5 d, packs 14 d; December order 15 Dec, lead 5-7 d, carbon overseas
fallback 14 d), params.json#schedule (build_start 2027-01-19, complete_by 2027-04-30), review/MANUFACTURING.md section 5
(week-by-week plan) and BUILD-GUIDE.md (stage times).
"""
import datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = dt.date
START, END = D(2026, 11, 16), D(2027, 4, 30)
BUILD_START = D(2027, 1, 19)          # params.json#schedule.build_start (spring instruction begins, Berkeley Global page, searched 2026-11-13)

# id, name, owners, not-before, days (calendar, cures included), hours (person-h, EST), deps, source of the hours / dates
T = []


def t(id, name, owners, nb, days, hours, deps=(), src="", phase=""):
    T.append(dict(id=id, name=name, owners=owners, nb=nb, days=days, hours=hours, deps=list(deps), src=src, phase=phase))


# ---- Phase 0: before the order (16 Nov - 15 Dec)
t("M01", "Compliance: TRUST, UC Drone Program, AMA / insurance answer, FAA registration", ["P4"], D(2026, 11, 16), 8, 6, [], "team/H3/COMPLIANCE.md; R-LEGAL", "pre")
t("M02", "Jacobs: Spring-pass and training answers, flux/wick and K-type check (T-I1-BORROW)", ["P4"], D(2026, 11, 16), 5, 2, [], "team/I1/ORDER-PLAN.md R4", "pre")
t("O01", "Early order placed (20 Nov): packs and FC carts first", ["P2"], D(2026, 11, 20), 1, 3, ["M02"], "ORDER-PLAN.md", "pre")
t("O02", "Early order arrives (lead 5 d EST, Thanksgiving week: allow 7)", ["P2"], D(2026, 11, 21), 7, 2, ["O01"], "ORDER-PLAN.md early table lead column", "pre")
t("O03", "Ovonic packs arrive (ships from Germany, about 14 d); weigh, log", ["P2"], D(2026, 11, 21), 14, 2, ["O01"], "ORDER-PLAN.md P01 lead 14 d LONG", "pre")
t("S01", "SITL install and >= 10 h pilot log (R-PILOT)", ["P4"], D(2026, 11, 16), 40, 14, [], "subsystems/flight-software/SITL-PLAN.md; params requirements.sitl_hours_min 10", "pre")
t("H01", "Thrust stand build and calibration (GT-01), stand campaign (GT-02/03)", ["P1", "P2"], D(2026, 11, 28), 14, 30, ["O02"], "team/H1/GROUND-TEST-PLAN.md campaign order 23 Nov - 8 Dec (EST hours)", "pre")
t("W01", "Hot-wire bow, templates (laser), practice cores x 2-3, LE sanding", ["P1", "P3"], D(2026, 11, 26), 18, 28, ["O02"], "review/MANUFACTURING.md section 1 and 6 (practice cores); hours EST", "pre")
t("W02", "Test coupons, fin test article, tube bend test (GT-15/16): result to I1 by 10 Dec", ["P1", "P3"], D(2026, 11, 30), 12, 20, ["O02"], "H1 GT-15, GT-16; hours EST", "pre")
t("W03", "Print jigs and test articles (clocking jig, cant gauge, drill guides)", ["P3"], D(2026, 11, 30), 12, 8, ["O02"], "team/G3/PRINT-LIST.md jigs; hours EST", "pre")
t("TW1", "Foam-board twin build (about $40)", ["P3", "P2"], D(2026, 11, 30), 8, 18, ["O02"], "CONFIGURATION.md de-risking 1; hours EST", "pre")
t("TW2", "RFS flight request for twin days (7 business days ahead; RFS 72 h)", ["P4"], D(2026, 11, 24), 10, 1, ["M01"], "team/H3/COMPLIANCE.md", "pre")
t("TW3", "Twin flights: hover in 5 m/s, QLOITER 30 m, transition (R-TWIN)", ["P4", "P2", "P1", "P3"], D(2026, 12, 7), 6, 20, ["TW1", "TW2", "O03"], "team/H2/FLIGHT-TEST-PLAN.md gate 1; hours EST", "pre")
t("WN1", "RFS anemometer mornings x 3 (R-WIND-MEASURE)", ["P4"], D(2026, 11, 23), 14, 6, ["M01"], "team/H3/WIND-RFS.md", "pre")
t("OR2", "December order placed (15 Dec): Aloft cart first, servos same day", ["P2"], D(2026, 12, 15), 1, 3, ["TW3", "W02"], "ORDER-PLAN.md December order", "pre")
t("FZ1", "Design freeze (18 Dec): CG fix, fin tip, collar, pins, mount material", ["P1", "P2", "P3", "P4"], D(2026, 12, 18), 1, 4, ["W02", "H01"], "BUILD-GUIDE.md week table", "pre")
t("EL1", "Electronics Lab days before Jacobs closes (18 Dec): bus board, AS150U, ESC leads, FC flash", ["P2"], D(2026, 12, 1), 17, 20, ["O02"], "Jacobs Electronics Lab (labs-and-equipment page 2026-11-13); closure 19 Dec - 18 Jan (BUILD-GUIDE)", "pre")
# ---- Phase 1: winter closure (19 Dec - 18 Jan)
t("PR1", "Home printing: blocks, collars (after freeze), pod prints, feet, pistons, mounts (ASA)", ["P3"], D(2026, 12, 19), 30, 24, ["FZ1", "W03"], "team/G3/PRINT-LIST.md totals (machine hours); labour EST", "closure")
t("OR3", "December order arrives (lands about 20-22 Dec; the overseas carbon fallback would be 14 d: a risk, not the baseline)", ["P2"], D(2026, 12, 16), 7, 2, ["OR2"], "ORDER-PLAN.md; MANUFACTURING.md section 5", "closure")
t("HR1", "Harness cut, labelled, twisted; ESC and FC flash; Plane 4.7; K09L.param; SITL (no soldering)", ["P2"], D(2026, 12, 21), 28, 12, ["OR3", "EL1"], "BUILD-GUIDE.md stage 6 step 1; hours EST", "closure")
# ---- Phase 2: build (19 Jan - ...)
t("B01", "Cut cores 1 and 2, sand LE, accept core 1 by gauge", ["P1"], BUILD_START, 3, 4, ["W01"], "BUILD-GUIDE stage 2 (16 h for stage 2, split by me, EST)", "build")
t("B02", "Spar slot, pockets, grooves (core in its bed)", ["P1"], D(2027, 1, 19), 3, 5, ["B01"], "wing/BUILD.md steps 3-5", "build")
t("B03", "Spar plugs bonded (24 h cure): done before build week 1 in the home workspace (CR-I2-04), tube and plugs only", ["P1"], D(2027, 1, 4), 2, 1, ["OR3", "W03"], "wing/BUILD.md step 6 (needs no core); hours EST", "closure")
t("B04", "Spar and blocks in the clocking jig (cure)", ["P1", "P3"], D(2027, 1, 26), 2, 3, ["B02", "B03", "PR1"], "wing/BUILD.md step 7; MF-06", "build")
t("B05", "Bond spar and blocks into the core, beads, weight on the bed (24 h cure)", ["P1"], D(2027, 1, 26), 2, 3, ["B04"], "wing/BUILD.md step 8", "build")
t("B06", "Elevons free, torque-tube grooves", ["P1"], D(2027, 1, 26), 2, 4, ["B05"], "BUILD-GUIDE stage 3 (3-4 h plus 24 h cure)", "build")
t("B07", "Motor tubes cut, plugged, through the blocks, squared in the jig (cure)", ["P1", "P3"], D(2027, 1, 28), 3, 3, ["B05"], "BUILD-GUIDE stage 4 step 2 (stage 4 total 16 h, split EST)", "build")
t("B08", "Fin laminates and cuts (3M 77, spray booth); half-fin boards", ["P3"], D(2027, 1, 19), 3, 3, ["FZ1"], "MANUFACTURING.md section 2 (3 h reviewer est.)", "build")
t("B09", "Half-fin roots and cove fillets (weigh a cup per batch)", ["P1", "P3"], D(2027, 2, 1), 3, 4, ["B07", "B08"], "BUILD-GUIDE stage 4 step 3", "build")
t("B10", "Collars, strips, pins, braces, ESC pads, heat-tent post-cure", ["P1", "P3"], D(2027, 2, 2), 5, 6, ["B09", "PR1"], "BUILD-GUIDE stage 4 steps 4-6; MF-13 hold until freeze", "build")
t("B11", "Pod box, tray, recess fillet, pod into the recess, handle (3 cures)", ["P3"], D(2027, 1, 19), 14, 8.5, ["PR1"], "BUILD-GUIDE stage 5 (8.5 h plus 3 x 24 h cures)", "build")
t("B12", "Power stack on the bench (Electronics Lab: soldering), weigh 88 g", ["P2"], D(2027, 1, 19), 5, 3, ["OR3"], "BUILD-GUIDE stage 5; power/BUILD.md", "build")
t("B13", "Harness solder and route; JR recesses; T-F2-CONT", ["P2"], D(2027, 1, 26), 7, 12, ["B12", "HR1", "B09"], "BUILD-GUIDE stage 6 (1-2 days)", "build")
t("B14", "Skin the wing (two people)", ["P1", "P3"], D(2027, 2, 6), 2, 7, ["B13", "B10", "B11"], "BUILD-GUIDE stage 6 (3-4 h for two people)", "build")
t("B15", "Servos, linkage, hinges (both sides in parallel, 2 x 24 h cures)", ["P3", "P1"], D(2027, 2, 8), 3, 8, ["B14"], "BUILD-GUIDE stage 7 (half a day per side)", "build")
t("B16", "Motor mounts, motors, props, slip test, spin test", ["P1", "P2"], D(2027, 2, 8), 3, 4, ["B10", "B14"], "BUILD-GUIDE stage 8 (1 h per station)", "build")
t("B17", "Avionics and calibration", ["P2"], D(2027, 2, 10), 2, 8, ["B13", "B14"], "BUILD-GUIDE stage 9 (about 1 day)", "build")
t("B18", "Feet and corner caps (cure)", ["P3"], D(2027, 2, 9), 3, 9, ["B14"], "BUILD-GUIDE stage 10 (1 h bench + cartridges most of a day)", "build")
t("B19", "Weigh, CG, control directions, stand run-up, compassmot (GT-06/07/12/13/18)", ["P1", "P2", "P3", "P4"], D(2027, 2, 11), 4, 16, ["B15", "B16", "B17", "B18"], "BUILD-GUIDE stage 11 (about 2 days); H1 plan", "build")
t("TB1", "Transport box and mat (X07 kit if the gate passes)", ["P3", "P4"], D(2027, 2, 1), 14, 15, ["PR1"], "BUILD-GUIDE week table; D7 (about 6 h for two plus 1.5 h mat, EST)", "build")
t("RG1", "RC range check GT-14 (T-F5-RANGE), props off", ["P2", "P4"], D(2027, 2, 15), 1, 3, ["B19"], "team/F5/RANGE-TEST.md", "build")
# ---- Phase 3: flight
t("FR1", "RFS flight request for the first hover block", ["P4"], D(2027, 2, 3), 10, 1, ["M01"], "team/H3/COMPLIANCE.md", "fly")
t("F01", "First tethered hover (gate 3)", ["P4", "P2", "P1", "P3"], D(2027, 2, 16), 3, 16, ["B19", "RG1", "FR1", "S01"], "team/H2/FLIGHT-TEST-PLAN.md gate 3", "fly")
t("F02", "Free hover, QLOITER, landing practice (gate 4)", ["P4", "P2"], D(2027, 2, 23), 8, 20, ["F01"], "H2 plan gate 4", "fly")
t("F03", "Fixed-wing tune as a plain flying wing (gate 5)", ["P4", "P2"], D(2027, 3, 2), 9, 20, ["F02"], "H2 plan gate 5; F4 TUNING-PLAN steps 6-6d", "fly")
t("F04", "First transition at >= 50 m (gate 6) and back-transition (gate 7)", ["P4", "P2", "P1"], D(2027, 3, 9), 7, 16, ["F03"], "H2 plan gates 6-7; R-SCHEDULE wk 7", "fly")
t("CR1", "Crash-repair loop (contingency block, >= 1.5 weeks calendar)", ["P1", "P3"], D(2027, 3, 16), 11, 24, ["F04"], "R-SCHEDULE; MANUFACTURING.md section 5 (core 4-5 days through the cure chain)", "fly")
t("F05", "Transition round trips, landing practice in calm air (gates 7-8)", ["P4", "P2"], D(2027, 3, 29), 12, 24, ["CR1"], "H2 plan", "fly")
t("F06", "Full mission demonstrations (gate 9), data and report", ["P4", "P2", "P1", "P3"], D(2027, 4, 12), 16, 36, ["F05"], "H2 plan gate 9; R-MISSION", "fly")

BY = {x["id"]: x for x in T}


def wd(a, b):
    """working days (Mon-Fri) from a to b inclusive"""
    n, d = 0, a
    while d <= b:
        n += d.weekday() < 5
        d += dt.timedelta(1)
    return max(n, 1)


def forward():
    done = {}

    def fin(i):
        if i in done:
            return done[i]
        x = BY[i]
        s = x["nb"]
        for d in x["deps"]:
            s = max(s, fin(d) + dt.timedelta(1))
        x["es"] = s
        x["ef"] = s + dt.timedelta(x["days"] - 1)
        done[i] = x["ef"]
        return x["ef"]

    for i in BY:
        fin(i)


def backward():
    succ = {i: [] for i in BY}
    for x in T:
        for d in x["deps"]:
            succ[d].append(x["id"])
    lf = {}

    def late_finish(i):
        if i in lf:
            return lf[i]
        x = BY[i]
        if not succ[i]:
            v = END
        else:
            v = min(late_finish(s) - dt.timedelta(BY[s]["days"]) for s in succ[i])
        lf[i] = v
        return v

    for i in BY:
        x = BY[i]
        x["lf"] = late_finish(i)
        x["slack"] = (x["lf"] - x["ef"]).days
    m = min(x["slack"] for x in T)
    for x in T:
        x["crit"] = x["slack"] == m


def weeks():
    w, d = [], START - dt.timedelta(START.weekday())
    while d <= END:
        w.append(d)
        d += dt.timedelta(7)
    return w


def gantt(ws):
    out = ["| ID | Task | Own | " + " | ".join(f"{w.month}/{w.day}" for w in ws) + " | Start | End | Slack d |",
           "|---|---|---|" + "---|" * len(ws) + "---|---|---|"]
    for x in sorted(T, key=lambda z: (z["es"], z["id"])):
        cells = []
        for w in ws:
            we = w + dt.timedelta(6)
            cells.append(("**X**" if x["crit"] else "#") if (x["es"] <= we and x["ef"] >= w) else "")
        out.append(f"| {x['id']} | {x['name']} | {','.join(o[1] for o in x['owners'])} | " + " | ".join(cells) + f" | {x['es']:%d %b} | {x['ef']:%d %b} | {x['slack']} |")
    return "\n".join(out)


def load(ws):
    per = {p: {w: 0.0 for w in ws} for p in ("P1", "P2", "P3", "P4")}
    for x in T:
        days = [x["es"] + dt.timedelta(i) for i in range((x["ef"] - x["es"]).days + 1)]
        wdays = [d for d in days if d.weekday() < 5] or days[:1]
        share = x["hours"] / len(wdays) / len(x["owners"])
        for d in wdays:
            w0 = d - dt.timedelta(d.weekday())
            if w0 in per["P1"]:
                for o in x["owners"]:
                    per[o][w0] += share
    return per


def main():
    forward()
    backward()
    ws = weeks()
    per = load(ws)
    crit = sorted([x for x in T if x["crit"]], key=lambda z: z["es"])
    last = max(T, key=lambda z: z["ef"])
    hov = BY["F01"]
    build_h = sum(x["hours"] for x in T if x["phase"] == "build" and x["id"] not in ("TB1", "RG1", "B19"))
    build_h_incl = sum(x["hours"] for x in T if x["phase"] == "build" and x["id"] != "TB1")
    pre_h = sum(x["hours"] for x in T if x["phase"] in ("pre", "closure"))
    first_cut = BY["B01"]["es"]
    wk = lambda d: (d - BUILD_START).days // 7 + 1
    rows = []
    for p in ("P1", "P2", "P3", "P4"):
        tot = sum(per[p].values())
        peak = max(per[p].items(), key=lambda kv: kv[1])
        rows.append(f"| {p} | {tot:,.0f} | {peak[1]:,.1f} (week of {peak[0]:%d %b}) |")
    loadtab = ["| Week of | P1 | P2 | P3 | P4 | Team h |", "|---|---|---|---|---|---|"]
    for w in ws:
        v = [per[p][w] for p in ("P1", "P2", "P3", "P4")]
        loadtab.append(f"| {w:%d %b} | " + " | ".join(f"{a:,.1f}" for a in v) + f" | {sum(v):,.1f} |")
    txt = f"""# I2 schedule: 16 Nov 2026 to 30 Apr 2027, team of 4

Revision I2-R1, 2026-11-13. Status `PROPOSED`; generated by `python -I redesign/team/I2/make_schedule.py` from the task list in that file (forward and backward pass, so
the critical path and slack below are computed). Hours are `EST` unless a source is named. Owners are roles (P1 wing and fin structure, P2 electrical and software, P3 printing,
pod, mechanisms and landing, P4 test, compliance and pilot), not names: the team assigns people. Requirement ids: `R-SCHEDULE`, `R-BUILD-HOURS` (A2).

## Verdict

| Item | Plan | Requirement | Status |
|---|---|---|---|
| First cut | {first_cut:%d %b %Y} (build week 1) | build start 2027-01-19 (`params.json#schedule`) | on date |
| First tethered hover | {hov['es']:%d %b} - {hov['ef']:%d %b} (build week {wk(hov['es'])}) | `R-SCHEDULE`: build week 4; `MANUFACTURING.md` section 5: week 5 is the honest target | **week {wk(hov['es'])} is the baseline; week 4 is the stretch. The two documents disagree: A1 decides** (`CR-I2-01`) |
| First transition (gate 6) | {BY['F04']['es']:%d %b} - {BY['F04']['ef']:%d %b} (build week {wk(BY['F04']['es'])}) | build week 7 | {'meets' if wk(BY['F04']['es']) <= 7 else 'one week late (build week ' + str(wk(BY['F04']['es'])) + ' vs 7)'}; `MANUFACTURING.md` calls week 7 a stretch (`CR-I2-01`) |
| Crash-repair loop | {BY['CR1']['es']:%d %b} - {BY['CR1']['ef']:%d %b}, {BY['CR1']['days']} d | >= 1.5 weeks calendar (10.5 d) | meets, as a contingency block |
| Last task ends | {last['ef']:%d %b %Y} ({last['id']}) | complete by 2027-04-30 | {'meets' if last['ef'] <= END else 'FAILS'}; slack of the last task {last['slack']} d |
| Build hours to first hover | {build_h_incl:,.1f} h (airframe, electrical, checks; excludes the transport box) from the BUILD-GUIDE stage times | <= 90 h (`R-BUILD-HOURS`) | **{'FAIL by ' + format(build_h_incl - 90, ',.1f') + ' h' if build_h_incl > 90 else 'meets'} on the guide's own stage times** (`CR-I2-02`) |
| Hours before first cut (Nov-Jan) | {pre_h:,.0f} h (EST) | not bounded | shifts hours out of the 3-week window; the requirement text does not say whether pre-work counts |
| Twin flown before the 15 Dec order | {BY['TW3']['es']:%d %b} - {BY['TW3']['ef']:%d %b} | `R-SCHEDULE` | {'meets' if BY['TW3']['ef'] < D(2026, 12, 15) else 'FAILS'} (needs the 7-business-day request out by {BY['TW2']['es']:%d %b}) |
| Early order 20 Nov, December order 15 Dec | tasks `O01`, `OR2`; arrivals `O02`, `OR3` | `ORDER-PLAN.md` | consistent with its lead times (5 d; packs 14 d; servos 7 d) |

Facts the plan rests on, each from a page checked on 2026-11-13 unless stated:

- Fall instruction and Jacobs fall access end 18 Dec; spring instruction starts 19 Jan 2027, spring recess 22-26 Mar (third-party calendar sites; the Registrar page was not fetched: confirm) (https://berkeleyglobal.zendesk.com/hc/en-us/articles/4641371985943-Class-Start-Dates, search 2026-11-13).
- Jacobs Maker Pass: drop-in access, hands-on trainings only in the first half of each semester (https://jacobsinstitute.berkeley.edu/making-at-jacobs/). **The fall window (31 Aug - 23 Oct, `review/MANUFACTURING.md`) is already closed.** Any tool that needs hands-on training is therefore at risk until spring week 1 (`CR-I2-03`). `M02` asks staff in the week of 16 Nov.
- Soldering is Electronics Lab only (no loans, no home iron after the R4 BOM change): `EL1` before 18 Dec, `B12` and `B13` from 19 Jan. The closure block `HR1` contains no soldering.
- RFS: flight request 7 business days ahead (campus policy, https://oercs.berkeley.edu/policies/campus-policy-library/unmanned-aircraft-system-drone-policy), RFS asks 72 h (https://rfs.berkeley.edu/services.html); flights 06:00 to sunset only, so the flight card's 07:00-10:00 window sits inside it.
- Hot-wire cutting is not a Jacobs capability: the team needs a ventilated place (`CR-I2-04`, owner to name it) for `W01`, `B01`.

## Gantt (week commencing Monday; `#` = task active with slack, **X** = active on the critical path)

{gantt(ws)}

## Critical path

Computed as the tasks with the least slack (the minimum over all tasks, {min(x['slack'] for x in T)} d) against 30 Apr: {' > '.join(x['id'] for x in crit)}.

| Task | Start | End | Why it is on the path |
|---|---|---|---|
""" + "\n".join(f"| {x['id']} {x['name']} | {x['es']:%d %b} | {x['ef']:%d %b} | {x['src']} |" for x in crit) + f"""

Long poles named by `MANUFACTURING.md`: design freeze (`FZ1`), Jacobs access and training (`M02`), Ovonic packs from Germany (`O03`, 14 d), Aloft carbon (`OR3`). The
path through the build is core, spar and blocks in the jig, tubes, collars, pins and braces, skin, bench checks, hover; the pod chain (`B11`) joins before skinning.
A late freeze or a failed fin-station decision (STATUS issue 1) moves every later date one-for-one.

## Team-of-4 load (person-hours per week, `EST`)

| Person | Total h | Peak week |
|---|---|---|
""" + "\n".join(rows) + """

""" + "\n".join(loadtab) + f"""

Capacity per student per week is **not in the repo** (`—`): the team states it before the freeze. Peaks above that capacity move tasks right, which the critical path above shows.
Flight-phase durations assume 5.0 to 5.7 usable mornings a week (`config-study/tiebreak/DECISION.md`, wind at 07-10 h), so 8-16 calendar days hold 6 to 13 flying mornings. Durations are calendar days including weekends and cures; weekend work is assumed in the build window. Hours of one task are spread evenly over its Mon-Fri days among its owners; the table is a load picture, not a roster.

## Open items for people

| # | Item | Why | By |
|---|---|---|---|
| CR-I2-01 | A1: hover in build week 4 (`R-SCHEDULE`) or 5 (`MANUFACTURING.md`)? | the stage times sum past 90 h and the cure chain needs 4 weeks to the restrained run | before 18 Dec |
| CR-I2-02 | A2 and G4: does `R-BUILD-HOURS` count pre-build work (printing, harness cut, templates)? | {build_h_incl:,.0f} h on the stage times vs 90 h | before 18 Dec |
| CR-I2-03 | Team: ask Jacobs staff for hands-on trainings now (laser, printer, drill press, woodshop, electronics) | the fall hands-on window closed 23 Oct; spring window opens with the term | week of 16 Nov |
| CR-I2-04 | Team: name a ventilated workspace for hot-wire cutting, epoxy and spray lamination (spray booth is at Jacobs) | Jacobs lists no hot-wire cutter; XPS fumes (`BUILD-GUIDE.md` safety) | before 30 Nov |
| CR-I2-05 | Owner: Spring 2027 Maker Pass for all four from 19 Jan | the pass is semesterly and not transferable (https://jacobsaccess.ist.berkeley.edu/Maker-Pass-troubleshooting.html) | before 19 Jan |
"""
    (HERE / "SCHEDULE.md").write_text(txt, encoding="utf-8")
    print("written", len(txt), "build_h", build_h_incl, "crit", [x['id'] for x in crit], "hover", hov["es"], hov["ef"])


if __name__ == "__main__":
    main()
