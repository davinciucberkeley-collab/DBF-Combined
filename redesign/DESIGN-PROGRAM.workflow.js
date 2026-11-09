export const meta = {
  name: 'vtol-design-program',
  description: 'Full VTOL redesign by a single-role engineering team: frame, analysis, structures, CAD, integration, simulation, build/test/program, media, review board, final',
  phases: [
    { title: 'Frame', detail: 'chief engineer, systems, mass, interfaces, CAD lead, research', model: 'fable' },
    { title: 'Analysis', detail: 'aero, loads, propulsion, energy' },
    { title: 'Detail analysis', detail: 'structures, thermal, power, avionics, RC link' },
    { title: 'Design', detail: 'Fusion CAD per subsystem, mechanisms, packaging, harness, flight software' },
    { title: 'Integrate', detail: 'interface/CAD/mass checks, chief resolves, owners fix' },
    { title: 'Simulate', detail: 'CFD/VLM/FEA/thermal on settled geometry with convergence; verification matrix' },
    { title: 'Build and program', detail: 'manufacturing, assembly steps, tests, safety, BOM, schedule' },
    { title: 'Media', detail: 'renders, animations, manual, viewer, proof chains, docs cleanup' },
    { title: 'Review', detail: 'design review board, fixes, visual polish, final', model: 'fable' },
  ],
}

const ROOT = 'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined'
const R = `${ROOT}/redesign`
const CONFIG = (args && args.config) || 'see redesign/CONFIGURATION.md'

const PRE = (id, title) => `You are ${id}, ${title}, on a single-role aircraft engineering team (roster: ${R}/TEAM.md). Do ONLY your role, as well as a professional in that role would. Repo: ${ROOT} (branch redesign/v1).
Read first: ${R}/BRIEF.md (rules, ownership, animation rules), ${R}/CONFIGURATION.md (the chosen configuration: ${CONFIG}), ${R}/README.md and ${R}/params/params.json if present, ${R}/inputs/SIM-TOOLS.md (tools you may use; professional practice), ${R}/inputs/ADVISOR-XV24-LESSONS.md, ${R}/design-system/README.md (all visuals follow it).
Your folder: ${R}/team/${id}/ (write only there, plus anything your task explicitly assigns). Put a one-page SUMMARY.md in it (design-system Markdown conventions: tables, units, status words PROPOSED/MODELLED/CHECKED/VERIFIED/UNVERIFIED). Emit claims for the proof chain using ${R}/proofs/README.md conventions for every number others depend on. Need something from another role? Write ${R}/team/${id}/CHANGE-REQUESTS.md (target role id, what, why, numbers). Do not commit.\n\n`

const RES = {
  type: 'object',
  properties: {
    summary: { type: 'string', description: '<=120 words: what you produced, key numbers, check/simulation status' },
    passed: { type: 'boolean', description: 'your checks/simulations ran and met their criteria' },
    open_issues: { type: 'array', items: { type: 'string' } },
    change_requests: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'passed', 'open_issues', 'change_requests'],
}
const ISSUES = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    issues: { type: 'array', items: { type: 'object', properties: {
      role: { type: 'string', description: 'role id that must act, e.g. C2, D1, F2' },
      issue: { type: 'string' },
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
    }, required: ['role', 'issue', 'severity'] } },
  },
  required: ['summary', 'issues'],
}
const FRAME = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    subsystems: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string', description: 'folder under redesign/subsystems/, kebab-case' },
      name: { type: 'string' },
      designer_role: { type: 'string', description: 'D-role id responsible for its CAD, e.g. D1' },
      scope: { type: 'string' },
    }, required: ['key', 'name', 'designer_role', 'scope'] } },
    inactive_roles: { type: 'array', items: { type: 'string' }, description: 'role ids from TEAM.md not needed for this configuration' },
    role_notes: { type: 'string', description: 'any role re-scoping for this configuration, by role id' },
  },
  required: ['summary', 'subsystems', 'inactive_roles'],
}

// ---- role definitions: id, title, model, task ----
const ROLES = {
  A2: ['Systems engineer', 'fable', `Write ${R}/team/A2/REQUIREMENTS.md (final requirement set for this configuration, from ${R}/config-study/REQUIREMENTS-PROPOSED.md; each requirement measurable with a verification method: analysis/inspection/test/demonstration) and VERIFICATION-MATRIX.md (requirement -> owning role -> method -> evidence file -> status). Keep it current; later you will be called again to update statuses.`],
  A3: ['Mass-properties engineer', null, `Own ${R}/MASS-CG.md: mass allocation per subsystem and per discipline with growth reserve under the take-off mass limit; CG target and allowable range from the configuration; inertia estimate. Write mass_rollup.py that sums every redesign/subsystems/*/parts.csv and team estimates into a live roll-up vs allocation and CG. Later you will re-run it on the real parts.`],
  A4: ['Configuration / interface manager', null, `Using the tooling in ${R}/interfaces/ (SCHEMA.md, merge_check.py), set up the interface plan for this configuration: an INTERFACE-PLAN.md listing every expected interface between subsystems and disciplines (mechanical, electrical, thermal, kinematic), which role owns each side, and the joint-stack/wire data each must carry. Later you will run the checks.`],
  A5: ['CAD lead', null, `Prepare the Fusion framework in ${R}/fusion/ for this configuration: subsystem build order list, shared helpers this configuration needs (e.g. airfoil loft, boom tube, tilt joint), a coordinate/datum sheet (DATUMS.md) every designer uses, and modelling standards (naming = part ids, materials, mass overrides, joints). You may edit ${R}/fusion/. Run check.py on the examples.`],
  J1: ['Outside research analyst', 'fable', `For this configuration, research comparable builds and published work: what dimensions, structures, propulsion and control settings worked; documented failure modes (transition, structure, vibration, CG, wind, connectors); and best practices per discipline. Write REFERENCES.md grouped by role id (A–I) so each engineer gets a short, cited list. Flag any risk the team must design out.`],
  B1: ['Aero performance engineer', null, `Whole-aircraft performance for the VTOL-demonstrator mission: hover, transition corridor (speed vs tilt/pitch vs power), cruise, endurance, climb, stall, wind limits. Use AVL/XFOIL inputs from B2/B3 where available, else first-order with stated assumptions. Deliver performance.py + PERFORMANCE.md + claims.`],
  B2: ['Wing aero engineer', null, `Airfoil selection with XFOIL at the actual Reynolds numbers (polars, clmax, hinge moments), planform/twist, stall progression, aileron sizing; AVL lift distribution for the wing. Deliver scripts + WING-AERO.md + claims, and loads inputs for C1/C2.`],
  B3: ['Stability and control engineer', null, `AVL model of the whole configuration: neutral point, static margin, CG limits, trim across speeds, control derivatives and authority in hover (rotor differential) and cruise (surfaces), transition handling. Size tail/control surfaces if the configuration has them. Deliver avl files + scripts + S-AND-C.md + claims.`],
  B4: ['Rotor / propeller aero engineer', null, `Prop selection with data (manufacturer/UIUC/APC databases), static and forward-flight thrust/power, rotor–wing/rotor–rotor interaction, prop-wash on surfaces and the pitot, disk loading and noise. Deliver PROPS.md + data + claims (coordinate with E1).`],
  C1: ['Loads engineer', null, `Define all load cases with factors (flight manoeuvre and gust envelope, hover/transition rotor loads, landing/impact, ground handling, transport, wing assembly) and produce load distributions per structure (wing, fuselage, arms/booms, gear, joints) as data files others consume. LOADS.md + claims.`],
  E1: ['Propulsion engineer', null, `Motor/ESC/prop selection and margins for hover, transition, cruise: thrust-to-weight, per-motor current and temperature, efficiency map, ESC ratings, motor-out implications. Real catalogue data with URLs and prices. PROPULSION.md + claims.`],
  E2: ['Battery / energy engineer', null, `Battery selection (chemistry, cell count, capacity, C-rating, mass), energy budget per mission phase with reserve, voltage sag, charging and balancing, storage/transport safety, number of packs needed for a test day. ENERGY.md + claims.`],
  C2: ['Wing structures engineer', null, `Wing structure from C1 loads and B2 geometry: spar, skins/core, ribs, wing joint and attachment; hand calcs first, then FEA (gmsh + SU2 ELASTICITY, or a NumPy beam model with justification) with mesh convergence; deflection and twist; margins of safety. WING-STRUCTURES.md + claims + sizing outputs for D1.`],
  C3: ['Fuselage structures engineer', null, `Fuselage load path from C1: mounts for wing, gear, battery, avionics, rotors if any; cut-outs and hatches; materials; margins. FUSELAGE-STRUCTURES.md + claims + sizing for D2.`],
  C4: ['Rotor-mount / boom structures engineer', null, `Arms/booms/motor mounts: strength, stiffness and vibration (first bending/torsion frequencies vs motor RPM bands), attachment joints. BOOM-STRUCTURES.md + claims + sizing for D3.`],
  C5: ['Landing / impact engineer', null, `Gear/skids/pads: hard-landing energy, tip-over on slopes and in wind, crash-energy path that protects the battery and avionics, repairability. LANDING.md + claims + sizing for D5.`],
  C6: ['Joints and fasteners engineer', null, `Every bolted/bonded joint the configuration needs: fastener sizes (minimise distinct sizes), heat-set inserts vs nuts, thread engagement, bearing/pull-out in printed/foam/composite parts, bond areas, torque/threadlocker, inspection. JOINTS.md as a joint-stack table keyed by interface id + claims.`],
  E3: ['Thermal engineer', null, `Temperatures of motors, ESCs, battery and avionics across the mission at 15–30 °C ambient; cooling paths and vents; limits and margins; recommend operating restrictions only if needed. THERMAL.md + scripts + claims.`],
  F1: ['Power distribution engineer', null, `Battery disconnect (anti-spark, rated for the real currents), distribution board, wire gauges with derating table (current, length, gauge, drop, temperature), fusing, current/voltage sensing, BECs. POWER.md + one-page schematic (SVG, design system) + claims.`],
  F3: ['Avionics hardware engineer', null, `Flight controller choice (well supported in ArduPilot for this VTOL type), sensors, GPS/compass, airspeed with no I2C clashes, placement for vibration and EMI, mounting. AVIONICS.md + claims.`],
  F5: ['RC link, telemetry and ground station engineer', null, `Transmitter, receiver protocol, telemetry radio, ground station software, failsafe behaviour, range test plan, legal frequencies/power. RC-LINK.md + claims (all equipment is bought new within budget).`],
  D6: ['Mechanisms designer', null, `Hinges, servo selection and mounts, linkages, and any tilt mechanism the configuration has: torque requirement vs servo spec (with hinge moments from B2/B3), slop, end-stops, clearance through full travel. Fusion module(s) in ${R}/subsystems/mechanisms/ (SPEC.md, parts.csv, interfaces.json with joint stacks, fusion/*.py, BUILD.md) passing check.py.`],
  D7: ['Transport and packaging designer', null, `How the aircraft breaks down, packs into a typical car, is carried by one or two people, and is assembled at the field in minutes: quick-release joints, connector disconnects, a transport case or cradle (as a buildable item), and an assembly-at-field checklist. ${R}/subsystems/transport/ with the standard subsystem files and a Fusion module for the case/cradle.`],
  F2: ['Harness engineer', null, `Wire list (WIRE-LIST.csv: from, to, signal, gauge, connector each end, length incl. service loop, route id), routes through the actual structure with support points, bend radii, chafe protection, strain relief and disconnects at every removable joint; harness mass. ${R}/subsystems/harness/ standard files; Fusion module drawing route centrelines/harness masses.`],
  F4: ['Flight-control software engineer', null, `Complete ArduPilot (or PX4 if better for this configuration) parameter file with every non-default line commented; transition logic and limits; failsafes (RC, battery, GPS, geofence); tuning plan; SITL plan (SITL not installed: mark UNVERIFIED). ${R}/subsystems/flight-software/.`],
  G1: ['Manufacturing engineer', null, `Process plan per made part (from every parts.csv): process, material, machine at Jacobs Hall, fixture/jig needed, time, cost of consumables. Design the jigs as buildable items. MANUFACTURING.md + process table.`],
  G2: ['Composites and foam specialist', null, `Detailed process sheets for any carbon/fibreglass/foam/balsa work: materials, layups, cure, hot-wire templates, safety, quality checks, typical student mistakes.`],
  G3: ['3D-printing specialist', null, `Printed parts: material per part (PLA/PETG/ASA/CF-nylon/TPU), orientation, wall/infill, print time and mass check vs parts.csv, design-rule fixes requested from designers, insert holes and tolerances.`],
  G4: ['Assembly sequence engineer', null, `Build order in work packages and every build step in the manual-kit step format (${R}/manual-kit/README.md): parts, fasteners from joint stacks, tools, time, numbered actions, figure specs (highlight/ghost/camera/callouts), ANIMATION specs where motion is the point (per BRIEF animation rules), and a measurable CHECK after each step. Also field-assembly steps from D7. Write steps into ${R}/manual-kit/content/ (create it) and a STEPS-INDEX.md in your folder.`],
  H1: ['Ground test engineer', null, `Ground test plan and cards: thrust stand, motor/ESC thermal, battery and power, structural proof load of wing/arms/gear, CG and mass check, control-surface/tilt function, RC range, compass/vibration checks; pass/fail criteria tied to requirements; test-card format with figure/animation specs for setups.`],
  H2: ['Flight test engineer', null, `Staged flight test plan: tethered hover, free hover, low-speed forward flight in hover mode, partial transition, full transition, cruise, return; go/no-go per stage, wind limits, data to log, test-card set; animation spec for the flight sequence.`],
  H3: ['Safety officer', null, `Risk assessment (hazard, cause, severity, likelihood, mitigation, owner), FAA/Part 107 or recreational compliance for the team and the test site, battery handling/charging/transport rules, prop safety, go/no-go checklist, emergency procedures.`],
  I1: ['Procurement / BOM engineer', 'sonnet', `Single BOM from every parts.csv and team selection: vendor, part number, price (2026, cited), qty incl. spares, lead time, shipping, 10.25% tax, ground equipment (transmitter, charger, batteries — nothing is owned), reserve; total vs $2,000; an ORDER-PLAN.md for the mid-December order grouped by vendor with long-lead items flagged.`],
  I2: ['Schedule planner', 'sonnet', `January–April 2027 schedule: work packages from G4, test stages from H1/H2, durations, dependencies, critical path, crash-repair buffer, milestone gates; output SCHEDULE.md with a Gantt as SVG (design system).`],
  J2: ['Verification / proof-chain engineer', null, `Collect every claim from the team into the proof graph (${R}/proofs/build_graph.py), make every requirement traceable requirement -> claim -> calculation/simulation -> params -> sources, fix broken chains by filing change requests, and publish the 3D viewer data. Report counts by status.`],
  J3: ['Technical illustrator', null, `Using ${R}/blender/ and the design system: render every build step figure and every ANIMATION spec from G4/H1/H2 (MP4 + poster PNG, <3 MB each), hero renders (iso, exploded, cutaway showing wiring), and export the assembly GLB for ${R}/viewer/; then run ${R}/manual-kit/build_manual.py to produce the build manual and test-card pages. Look at your own outputs and redo any that are not genuinely professional.`],
  J5: ['Technical writer / documentation', null, `Apply the stashed cleanup approach to the whole repo: outside redesign/, update or delete stale documents now superseded by the redesign (git stash list shows an earlier partial cleanup; you may inspect it with git stash show -p but do not pop it blindly). Write ${ROOT}/CLEANUP.md (edits, deletions with reasons, kept records). Update the root README to point to the redesign. Do not delete the old design records needed for history; move them under archive/ if they clutter the root.`],
}

const run = (id, extra, phase, schema) => {
  const [title, model, task] = ROLES[id]
  const opts = { label: `${id} ${title}`, phase, schema: schema || RES }
  if (model) opts.model = model
  return agent(PRE(id, title) + task + (extra ? `\n\n${extra}` : ''), opts).then(r => r ? { id, ...r } : null)
}
const active = new Set(Object.keys(ROLES))
const runAll = (ids, phase, extra) => parallel(ids.filter(i => active.has(i)).map(i => () => run(i, extra, phase)))

// ================= Frame =================
phase('Frame')
const frame = await agent(PRE('A1', 'Chief engineer / integrator') + `Turn the chosen configuration into the design frame. Read ${R}/config-study/README.md and REQUIREMENTS-PROPOSED.md. Write: ${R}/params/params.json (single source of top-level numbers with units and sources; coordinate system), ${R}/README.md (front door: aircraft in one paragraph, general arrangement with stations, subsystem boundary table — which subsystem and role owns every part and each side of every joint — and a directory map), and adjust ${R}/TEAM.md for this configuration (mark inactive roles, re-scope any role). Define the subsystem list for CAD (folder keys under ${R}/subsystems/, designer role per subsystem; D6 mechanisms and D7 transport always exist; harness and flight-software are owned by F2/F4).`, { label: 'A1 Chief engineer', phase: 'Frame', model: 'fable', schema: FRAME })
if (!frame) throw new Error('Frame failed')
for (const r of frame.inactive_roles || []) active.delete(r)
log(`Frame: ${frame.subsystems.map(s => s.key).join(', ')}; inactive: ${(frame.inactive_roles || []).join(', ') || 'none'}`)
const SUBS = frame.subsystems.filter(s => !['mechanisms', 'transport', 'harness', 'flight-software'].includes(s.key))

const framing = await runAll(['A2', 'A3', 'A4', 'A5', 'J1'], 'Frame')

// ================= Analysis =================
const resolve = async (label, phaseName, what) => agent(PRE('A1', 'Chief engineer / integrator') + `${what} Read every ${R}/team/*/CHANGE-REQUESTS.md and SUMMARY.md written so far. Decide each change request (accept/reject + one-line reason) in ${R}/params/CHANGE-LOG.md, update params.json, README.md and MASS-CG.md (coordinate with A3's roll-up) accordingly, and return the actions other roles must take as issues (role id + concrete instruction).`, { label, phase: phaseName, model: 'fable', schema: ISSUES })

const fixRound = async (issues, phaseName) => {
  const byRole = {}
  for (const i of issues || []) { if (i.severity === 'minor' && (issues || []).length > 30) continue; (byRole[i.role] = byRole[i.role] || []).push(`[${i.severity}] ${i.issue}`) }
  const designerFor = Object.fromEntries(frame.subsystems.map(s => [s.designer_role, s]))
  const jobs = Object.entries(byRole).map(([role, list]) => () => {
    const extra = `ACTION ITEMS for you (re-read params.json, README.md and MASS-CG.md first; they may have changed):\n- ${list.join('\n- ')}\nResolve each in your own folder; update SUMMARY.md and claims; re-run your checks.`
    if (ROLES[role] && active.has(role)) return run(role, extra, phaseName)
    if (designerFor[role]) return design(designerFor[role], extra, phaseName)
    return agent(PRE(role, 'team member') + extra, { label: `${role} fix`, phase: phaseName, schema: RES })
  })
  log(`${phaseName}: ${jobs.length} roles have action items`)
  return parallel(jobs)
}

phase('Analysis')
const analysis = await runAll(['B1', 'B2', 'B3', 'B4', 'C1', 'E1', 'E2'], 'Analysis')
const r1 = await resolve('A1 resolve analysis', 'Analysis', 'Analysis round is complete.')
await fixRound(r1 ? r1.issues : [], 'Analysis')

// ================= Detail analysis =================
phase('Detail analysis')
const detail = await runAll(['C2', 'C3', 'C4', 'C5', 'C6', 'E3', 'F1', 'F3', 'F5'], 'Detail analysis')
const r2 = await resolve('A1 resolve detail', 'Detail analysis', 'Detail analysis round is complete.')
await fixRound(r2 ? r2.issues : [], 'Detail analysis')

// ================= Design =================
phase('Design')
function design(s, extra, phaseName) {
  return agent(PRE(s.designer_role, `${s.name} designer`) + `You design the ${s.name} subsystem in Fusion: folder ${R}/subsystems/${s.key}/ (instead of team/). Scope: ${s.scope}
Inputs: the analysis and structures outputs in ${R}/team/ (aero, loads, structures sizing for your subsystem, joints table from C6, mounts from F1/F3), DATUMS.md and modelling standards from A5, INTERFACE-PLAN.md from A4. Deliver the standard subsystem files (SPEC.md one page, parts.csv, interfaces.json with complete joint stacks, params.json, fusion/<module>.py using fusionkit, BUILD.md notes for G4). Model real joints, fasteners and mounting features — nothing floating, nothing oversimplified where it matters for building. Stay inside your mass allocation or file a change request. Run python -I ${R}/fusion/check.py and python -I ${R}/interfaces/merge_check.py until your subsystem passes.` + (extra ? `\n\n${extra}` : ''), { label: `${s.designer_role} ${s.key}`, phase: phaseName, schema: RES }).then(r => r ? { id: s.designer_role, ...r } : null)
}
const designs = await parallel([
  ...SUBS.map(s => () => design(s, null, 'Design')),
  ...['D6', 'D7', 'F2', 'F4'].filter(i => active.has(i)).map(i => () => run(i, null, 'Design')),
])

// ================= Integrate =================
phase('Integrate')
const checks = await parallel(['A4', 'A5', 'A3'].map(id => () => run(id, `INTEGRATION CHECK: run your checks over everything delivered (interfaces merge_check / Fusion check.py / mass roll-up). Fix problems inside your own folder; return every remaining problem as an issue assigned to the role that must fix it (designer role ids are in ${R}/README.md).`, 'Integrate', ISSUES)))
const r3 = await resolve('A1 resolve integration', 'Integrate', `Integration checks are complete: ${checks.filter(Boolean).map(c => `${c.id}: ${c.summary}`).join(' | ')}. Their issues: ${JSON.stringify(checks.filter(Boolean).flatMap(c => c.issues || []))}.`)
await fixRound([...checks.filter(Boolean).flatMap(c => c.issues || []), ...(r3 ? r3.issues : [])], 'Integrate')
const recheck = await run('A4', 'RE-CHECK after fixes: run merge_check.py and check.py; return remaining issues.', 'Integrate', ISSUES)
if (recheck && recheck.issues && recheck.issues.length) await fixRound(recheck.issues, 'Integrate')

// ================= Simulate =================
phase('Simulate')
const sims = await runAll(['B1', 'B2', 'B3', 'B4', 'C2', 'C3', 'C4', 'C5', 'E3'], 'Simulate', `SIMULATION / VERIFICATION ROUND on the settled CAD geometry (redesign/subsystems/*/params.json and Fusion modules): re-run your analysis with the as-designed geometry and masses (A3 roll-up), using the highest-fidelity tool justified (CFD with SU2 only where VLM/XFOIL is insufficient; FEA with gmsh+SU2 ELASTICITY for primary structure), with mesh/grid convergence on at least 3 levels, comparison to your earlier hand calc, and margins. Produce plots in the design-system style and a SIMULATION-REPORT.md. Flag any requirement that now fails as an issue in change_requests.`)
const r4 = await resolve('A1 resolve simulation', 'Simulate', 'Simulation round is complete; some results may fail requirements.')
await fixRound(r4 ? r4.issues : [], 'Simulate')
await run('A2', 'UPDATE the verification matrix with all evidence now available; every requirement gets a status.', 'Simulate')

// ================= Build and program =================
phase('Build and program')
await runAll(['G1', 'G2', 'G3', 'H3'], 'Build and program')
await runAll(['G4', 'H1', 'H2', 'I1'], 'Build and program')
await runAll(['I2'], 'Build and program')

// ================= Media =================
phase('Media')
await runAll(['J3', 'J2', 'J5'], 'Media')

// ================= Review =================
phase('Review')
const BOARD = [
  ['aero', 'aerodynamics, stability, propulsion, performance and simulations (B, E1, E2)'],
  ['structures', 'loads, structures, joints, landing, FEA quality (C)'],
  ['electrical', 'power, harness, avionics, flight software, RC link, thermal (E3, F)'],
  ['build-and-test', 'CAD buildability, manufacturing, assembly steps, animations, tests, safety, BOM, schedule, transport (D, G, H, I)'],
]
const board = await parallel(BOARD.map(([k, scope]) => () => agent(PRE(`J6-${k}`, `Design review board member (${k})`) + `Conduct a professional design review of ${scope} like a CDR at an aerospace company: read every relevant SUMMARY.md, analysis, simulation report, CAD module, SPEC.md and build/test document; re-run key scripts; compare with outside references (search the web) and with ${R}/inputs/ADVISOR-XV24-LESSONS.md. Also judge presentation quality against the design system. Write ${R}/reviews/CDR-${k}.md. Return issues assigned to role ids, severity blocker/major/minor.`, { label: `J6 review ${k}`, phase: 'Review', model: 'fable', schema: ISSUES })))
const chair = await agent(PRE('J6-chair', 'Design review board chair') + `Read ${R}/reviews/CDR-*.md. Deduplicate and prioritise, decide which issues must be fixed before the mid-December order and which can wait, and write ${R}/reviews/CDR-SUMMARY.md with a go / go-with-conditions / no-go verdict for ordering parts.`, { label: 'J6 chair', phase: 'Review', model: 'fable', schema: ISSUES })
await fixRound(chair ? chair.issues.filter(i => i.severity !== 'minor') : board.filter(Boolean).flatMap(b => b.issues), 'Review')
await agent(PRE('J4', 'Visual designer') + `FINAL VISUAL POLISH. Review every visual output (${R}/manual-kit output, ${R}/viewer/, ${R}/proofs/viewer/, renders and animations in ${R}/blender/ and the manual, ${R}/config-study/ pages, all SPEC.md/README files, plots, SVG diagrams) against ${R}/design-system/. Fix presentation issues directly in those output/template files (you may edit them for styling only — never change engineering content), re-run the generators, look at the results, and iterate until they are genuinely professional. Write ${R}/reviews/VISUAL-POLISH.md.`, { label: 'J4 visual polish', phase: 'Review', model: 'fable', schema: RES })
await run('J2', 'FINAL: rebuild the proof graph and viewer data after the fixes; report counts by status.', 'Review')
await run('A2', 'FINAL: update the verification matrix; list every requirement not yet VERIFIED and what evidence (test) will close it.', 'Review')
const final = await agent(PRE('A1', 'Chief engineer / integrator') + `FINAL PASS. Make ${R}/README.md the polished front door of the finished redesign: aircraft summary with hero render, key numbers (mass vs limit, CG, T/W, endurance, cost vs $2,000), links to every deliverable (configuration study, CAD + how to run in Fusion, analyses and simulation reports, proof-chain viewer, aircraft viewer, build manual with animations, test plan, safety, BOM/order plan, schedule, CDR summary), status of every requirement, and the honest list of what remains UNVERIFIED until physical tests. Then write ${R}/HANDOFF.md for the team: what to review first, what to order in mid-December, and decisions only humans can make.`, { label: 'A1 final', phase: 'Review', model: 'fable', schema: RES })

return { frame, final, chair }
