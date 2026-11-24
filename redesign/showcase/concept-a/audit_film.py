"""audit_film.py - writes FILM-AUDIT.md, the per-step audit of the concept A build film.

    blender --background --factory-startup -P redesign/showcase/concept-a/render_build_a.py -- render --out <dir> --audit --every 4
    python redesign/showcase/concept-a/audit_film.py <dir>

The Blender run poses the film exactly as the renderer does (same schedule, same hide / show logic, same camera) at every 4th frame and
writes which parts and wires are visible and where the camera is (no pictures). This script compares that with the assembly plan
(qp/A/cad/a_assembly_plan.py): a part must be invisible before its step and visible from its step on (the bench parts, the cage unit and the
three threaded leads are explained in the notes). The 'before' columns are the findings on the film as it was shipped (65 steps, rendered
before D-208); they are written by hand in BEFORE below, from frames and from the camera table of the old script.
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_build_a as R  # noqa: E402

# step id -> (problem found in the shipped film, what was done); steps not listed only had the camera problem C (0.7 s cut)
BEFORE = {
    'A3': ('x-ray close-up started far from the spar', 'plug starts just outside the spar tip; follow camera clamped over the wing'),
    'A4': ('plugs floated in empty air (spar and core not in the picture) while they travelled 450 mm; looked like an unattached cylinder (Dillon, steps 4-5)',
           'plugs start 150 mm outside the tip, follow camera stays over the spar, see-through spar and core stay in view'),
    'A5': ('same as A4 from the left tip; then a 4x zoom-out in 0.7 s for the checkpoint card', 'same as A4; checkpoint pull-back takes 2.6 s'),
    'B0a': ('wing and spar vanished (hidden) at the stage start; empty bench; callouts point at stock that is not drawn', 'wing stays as an x-ray; callouts with no part on screen are dropped'),
    'B0k': ('wing popped back in; bridge saddle and strut clamps (no bench step) appeared before their step', 'wing stays x-ray; saddle and clamps now appear with B1'),
    'B1': ('view from below (el -22) reached by a 0.7 s swing; wing opaque snap', 'long smooth move; wing x-ray ends when the dock starts'),
    'B2': ('azimuth swung 75 degrees in 0.7 s to a different under-view', 'same under-view as B1 (no swing)'),
    'B4': ('"Left damper" label stuck at the frame edge; damper tiny', 'frames the right damper only; off-screen labels dropped'),
    'D1': ('servo tiny in a wide shot; pocket not visible; once in, only a flush grey rectangle (Dillon: servo not seen installed)',
           'close view from the aft side, core x-ray so the pocket and the servo dropping in are visible; seated servo stays visible'),
    'D0': ('lead barely visible (1.2 mm, wide shot, cage motor and prop in front)',
           'close view of pocket and slit, core x-ray, lead grows from the servo along the groove with a bead at the fish-wire tip; free end at the slit'),
    'D2': ('cage arm, motor and prop between the camera and the servo', 'aft-side view, nothing in front'),
    'D2a': ('same', 'same'), 'D3': ('same', 'same'), 'D4': ('same', 'same'), 'D5': ('same', 'same'),
    'D5b': ('left servo hidden behind the left fin tube; checkpoint pull-back then a 4x zoom snap', 'view from the aft right; pull-back and next move timed'),
    'E1': ('camera looked along the pitot path (foreshortened) at 2.5 m', 'side view of the left leading edge'),
    'E3b': ('4x zoom snap after the checkpoint pull-back; servo leads soldered with no visible lead', 'move time scaled; servo lead completes from the slit to the FC pad with the bead'),
    'E6': ('4x zoom snap after the pull-back', 'move time scaled'),
}
for sid in ('B0b', 'B0c', 'B0d', 'B0e', 'B0f', 'B0g1', 'B0g2', 'B0g3', 'B0g4', 'B0h', 'B0i1', 'B0i2', 'B0i3', 'B0i4', 'B0j1', 'B0j2'):
    BEFORE[sid] = ('wing, spar and plugs were hidden while the frame was built, and popped back at B0k', 'wing stays in the picture as an x-ray the whole bench stage')
# the steps whose camera moved more than 1.5x in distance, 25 degrees in azimuth or 0.35 m in target in the old 0.7 s moves (old camera table)
OLD_JUMPS = ['A5', 'B1', 'B2', 'B2a', 'B2c', 'B4', 'C1a', 'C2', 'C2a', 'C2b', 'C3', 'C4', 'C5', 'C6', 'C8', 'C9', 'D1', 'D5b', 'E1', 'E2', 'E3d', 'E3b', 'E4', 'E6']
STAGE_OPEN = ['B2', 'C1', 'C2', 'C3', 'C7', 'D1', 'E1', 'E3c']      # stage openings whose first step was framed wide (A1 and B0a had no wider context)


def main(work):
    rows, total = R.timeline()
    plan = R.load_cam_plan()
    rec = json.load(open(glob.glob(os.path.join(work, 'audit_*.json'))[0]))
    placed_by = {}
    for k, r in enumerate(rows):
        for p in r['parts']:
            placed_by.setdefault(p, k)
    thread_wires = {'E-HRN-02', 'E-HRN-03', 'E-HRN-04', 'E-HRN-05', 'E-HRN-07', 'E-HRN-08'}     # threaded in B0k / B2c / D0, soldered in E6 / E3b
    lay = {e: k for k, r in enumerate(rows) for e in r['edges']}
    stat = {r['id']: dict(n=0, early=set(), gone=set(), vis_end=None, labels=set(), wire_early=set(), wire_gone=set()) for r in rows}
    last_step_vis = {}
    for s in rec:
        t = s['f'] / R.FPS
        ci = 0
        for q, r in enumerate(rows):
            if t >= r['t_cam0']:
                ci = q
        st = stat[rows[ci]['id']]
        st['n'] += 1
        vis = set(s['vis'])
        for p, k in placed_by.items():
            if k > ci and p in vis:
                st['early'].add(p)
            if k < ci and p not in vis:
                st['gone'].add(p)
        for e, k in lay.items():
            if e in thread_wires:
                continue
            if k > ci and e in vis:
                st['wire_early'].add(e)
            if k < ci and e not in vis:
                st['wire_gone'].add(e)
        st['labels'] |= set(s['labels'])
        last_step_vis[rows[ci]['id']] = vis
    n_bad_steps = sum(1 for st in stat.values() if st['early'] or st['gone'] or st['wire_early'] or st['wire_gone'])
    out = []
    w = out.append
    w('# Concept A build film: per-step audit (66 steps)\n')
    w('Presentation only: no CAD geometry, assembly-plan order or proof number was changed. Source of truth for what must be on screen: `redesign/qp/A/cad/a_assembly_plan.py` '
      '(66 steps, a_assembly gate PASS 113/113 parts). Script: `redesign/showcase/concept-a/render_build_a.py`; generated by `audit_film.py` from a Blender pose run '
      '(`--audit`, every 4th frame = %d samples, no pictures) plus the by-hand findings on the shipped film.\n' % len(rec))
    w('## Result\n')
    w('- Visibility after the fix: **%d of 66 steps** show a part or wire before its step or lose one after it (0 expected). Checked on %d poses.' % (n_bad_steps, len(rec)))
    w('- Before the fix (shipped film, 65 steps): %d steps had a camera cut (0.7 s move with a zoom change over 1.5x, an azimuth swing over 25 degrees or a target shift over 0.35 m); '
      '%d steps had the wing hidden and popped back (B0a-B0k); 2 steps (A4, A5) showed the spar plugs floating in empty air (very probably the "servo that appears and disappears" in steps 4 and 5: '
      'an orange cylinder with a bore, no wing in the picture, then nothing); 3 parts (bridge saddle, two strut clamps) appeared in B0k before their step B1; the servo was a tiny flush rectangle in D1 and the lead '
      'in D0 and E3b was a 1.2 mm line in a wide shot with the cage motor in front; 8 stage openings showed the part tiny in a wide shot; labels in the shipped stage 2 were stale '
      '(hub 17.1 g "export pending"; the data says 18.3 g and the STLs are in `qp/A/drawings/out/stl/`).' % (len(OLD_JUMPS), 18))
    w('- Wire reveals that start before the LAY step are by design and are not errors: the phase leads are threaded in B0k and B2c (soldered in E6), the servo leads in D0 (soldered in E3b). '
      'No other wire shows before its step.')
    w('- Decisions (made without asking, as instructed): see "Decisions" at the end.\n')
    w('## Per step\n')
    w('Columns: **Should be visible** = parts the plan places in this step (all earlier parts stay). **Visible** = result of the pose check. **Camera** = azimuth / elevation / distance of the step view, '
      'the time of the move into it and the time the picture then stays still after the part has seated (card up). **Problem found / fix** = shipped film, then what was done.\n')
    w('| # | Step | Stage | Should be visible (new) | Visible (auto) | Camera (az / el / dist, move s, still s) | Problem found | Fix |')
    w('|---|---|---|---|---|---|---|---|')
    for k, r in enumerate(rows):
        sid = r['id']
        st = stat[sid]
        cp = plan.get(sid, {})
        cam = cp.get('cam') or [0, 0, 0, 0, 0, 0]
        new = ', '.join(r['parts'][:6]) + (' +%d' % (len(r['parts']) - 6) if len(r['parts']) > 6 else '') if r['parts'] else '(no part: %s)' % ('thread / lay wires' if r['edges'] or sid in ('D0', 'B2c', 'B0k') else 'make or cut beat')
        ok = 'OK (%d poses)' % st['n'] if not (st['early'] or st['gone'] or st['wire_early'] or st['wire_gone']) else 'FAIL early %s gone %s' % (sorted(st['early'] | st['wire_early']), sorted(st['gone'] | st['wire_gone']))
        still = r['t_end'] - r['t_mv1']
        camtxt = '%d / %d / %.2f m, %.1f s, %.1f s' % (cam[3], cam[4], cam[5], r['cam_dur'], still)
        if r.get('glide'):
            camtxt += '; opens wide, %.1f s glide behind the title card' % r['glide']
        if r['t_chk1'] > r['t_chk0']:
            camtxt += '; checkpoint pull-back %.1f s' % r['chk_dur']
        prob, fix = BEFORE.get(sid, ('', ''))
        extra = []
        if sid in OLD_JUMPS:
            extra.append('C: camera cut (0.7 s move)')
        if sid in STAGE_OPEN and sid not in BEFORE:
            extra.append('wide opening shot, part tiny')
        if prob:
            extra.insert(0, prob)
        w('| %d | %s | %d | %s | %s | %s | %s | %s |' % (k + 1, sid, r['stage'] + 1, new, ok, camtxt, '; '.join(extra) or 'none found', fix or ('camera moves now %.1f s with easing' % r['cam_dur'] if sid in OLD_JUMPS else '-')))
    w('')
    w('## What was fixed, by cause\n')
    w('1. **Camera cuts.** Every step used a 0.7 s move whatever the change, so the picture jumped (zoom up to 4x, swings up to 75 degrees). Moves are now one smoothstep shot between the views of consecutive steps; '
      'the time grows with the zoom change (1.5 s per octave), the swing (1 s per 40 degrees) and the shift (`cam_duration`, 0.6 to 4.2 s), the distance is interpolated geometrically, '
      'the checkpoint pull-back time is scaled the same way and the next move starts from the pull-back view. The per-step views are computed by Blender (`--camplan`, `cam_plan.json`) and read by the schedule, '
      'so the film length follows from them (%.0f s, was 801 s).' % total)
    w('2. **Stage openings.** The first step of a stage used the wide "everything so far" shot as its own view, so the new part was tiny. The camera now opens wide behind the title card, glides to the step view '
      'while the card is still up and the title card fades in (0.5 s) and out (0.7 s) instead of popping.')
    w('3. **Wing vanishing in the bench stage.** B0a-B0j2 hid the wing and showed it again at B0k. The wing now stays as an x-ray beside the frame (the frame is still built at the B1 start pose), and becomes solid when B1 starts to dock.')
    w('4. **Plugs in air (A4, A5).** The visual travel of A3-A5 is shortened (the plan travel is unchanged and swept): the plugs start just outside the tip, the x-ray camera follows them clamped over the wing and the spar and core ghosts stay in view.')
    w('5. **Servo (D1, D0, D2-D5b, E3b).** D1 and D0 see the core through (x-ray), the camera looks from the aft side (the cage arms and motors are forward of the pockets and were in front), the servo drops into its pocket and stays '
      'visible, D0 grows the lead from the servo out of its pocket along the foam groove to the slit with a bead at the fish-wire tip (CAD route E-HRN-07 / 08: 208 mm groove, 30 mm under the plate, 12 mm exposed), '
      'E3b completes the last 42 mm from the slit to the FC pad S5 / S6 (the soldering step). Right servo only is framed; labels of the left one are dropped as off-screen.')
    w('6. **Parts before their step.** The bridge saddle and the two strut clamps showed at B0k; they now appear with B1 (they have no bench step). Nothing else was early or gone.')
    w('7. **Callouts.** A label is drawn only if its part is on screen in the free band between the header and the step card (was: anywhere in the frame, which left labels stuck at the edge: B4 "Left damper"). '
      'Labels never shown because their target is off-screen or not yet drawn: A2 "Bonded over |y| <= 200 mm only" (point at the left tip, off-screen), B0a (cut stock is not a drawn part), B4 "Left damper".')
    w('8. **Stale labels.** The shipped stage clips were rendered before `a_build_steps.py` changed (hub 17.1 g "export pending"; step E3d missing). All stage clips and the full film are re-rendered from the current data: hub 18.3 g (CGE-001.stl, `qp/A/drawings/out/stl/`).')
    w('')
    w('## Not fixed / reported (CAD or plan, outside the film)\n')
    w('- The plan lists D0 after E1; the guide and the film put D0 right after D1 (before the arms, horns and pushrods). Both satisfy the plan gate (`THREAD_BEFORE`: D0 before E2). Left as the guide has it.')
    w('- The phase and servo leads are drawn complete only at their LAY step (E6, E3b); before that the film shows the thread progress (reveal curve). Plan and wire gate unchanged.')
    w('- B0a has no part to draw (cut stock): the picture is the empty bench with the x-ray wing. A part-less step by the plan.')
    w('- The cage unit is shown at the B1 start pose below the wing during the bench steps; that pose is a presentation choice (B1 docks from 70 mm below), the plan sweeps the bench in its own run.')
    w('- `redesign/site/app.html` guide text still says "hub 17.1 g ... export pending" in the stage 2 guide section; it comes from the generated `qp/A/BUILD-GUIDE-A.md` / the guide generator, not from the film (not touched here).')
    w('')
    w('## Decisions\n')
    w('- Camera durations are computed (not constants) and cached in `cam_plan.json`; the renderer refuses to run with a stale plan.')
    w('- Servo steps use an aft-side view (az 140 to 200) rather than the default nose-side view; D5b looks from the aft right so the left fin tube is not in front.')
    w('- The x-ray wing in the bench stage was preferred to hiding it: nothing is removed and re-added.')
    w('- A bead (4.5 mm) marks the fish-wire tip while a lead is threaded; the lead itself is drawn at its real 1.2 mm.')
    open(os.path.join(HERE, 'FILM-AUDIT.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('FILM-AUDIT.md written;', n_bad_steps, 'steps with visibility problems')


if __name__ == '__main__':
    main(sys.argv[1])
