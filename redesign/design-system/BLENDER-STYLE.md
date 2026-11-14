# Blender render style

Parameters live in `blender-style.json` (read it from the toolkit; do not retype numbers). This page says why and
shows how a figure is composed. Reference images: Prusa assembly guides (one photo per step, numbered coloured
markers, parts for that step only), LEGO instructions (new parts highlighted, previous state ghosted), Haynes
manuals (sequence photos with numbered arrows).

## Three kinds of figure

| Figure | Camera | Size | Samples | Used by |
|---|---|---|---|---|
| Step figure | 50 mm, az 35° el 25°, framed on the parts touched | 1600 × 1000 | 128 | build manual, every step |
| Detail inset | 85 mm, framed on one joint | 1000 × 1000 | 128 | joint stacks, wiring details |
| Hero | 50 mm, transparent film, DoF f/5.6 | 2400 × 1500 | 512 | config page, README, viewer poster |
| 3-view | orthographic top/front/side | 1600 × 1000 | n/a (Freestyle only) | SPEC.md, config comparison |

## The emphasis rule (the whole style in one line)

Every step figure contains only three classes of part, and nothing else is rendered:

| Class | Look | Meaning |
|---|---|---|
| **act** | orange `#E0661A`, own outline | the part(s) you touch in this step; fasteners of the same action in lighter orange |
| **built** | its real material class | already assembled in earlier steps |
| **ghost** | blue-grey 18 % alpha, thin outline, no shadow | context that would otherwise hide the action (a skin, the far wing half) |

Hide everything else. If a step needs more than one orange part, the step is probably two steps.

## Materials

One material per *material class*, never per subsystem: foam reads as foam, carbon as carbon, printed parts as one
light grey. Subsystem colour belongs to the web viewer and diagrams. Fasteners are metallic grey, inserts brass,
wires red/black/yellow (other colours only if the harness spec says so). Props are rendered static, no motion blur.

## Lighting and world

Three area lights relative to the camera: key 40° left / 38° up, fill 55° right / 20° up at ~30 % power, rim behind
at 160°. No sun lamp (hard shadows hide edges), no HDRI in figures. Studio world is a flat grey `#DCE1E8` with a
swept floor; bench world is a warm plain for hand-work close-ups. AgX, exposure −0.25, denoised.

Scale the light power with the subject: `power × (extent / 2 m)²`, so a 300 mm clamp and the 2.2 m aircraft have
the same brightness.

## Outlines

Freestyle lines on silhouette, border, crease (138°) and external contour: `0.8 px per 1000 px` of output width,
ink `#1F2328` at 90 %. Hero renders have no outline. Ghost parts keep a 60 % thin outline so their silhouette reads.

## Callouts (2-D pass)

```
   ┌────────────────────────────────┐
   │        (1)──────╮              │   (n)  orange dot r 12 px, white 2 px ring, mono 600 14 px
   │                 ╰──● clamp     │   ●    anchor dot r 4 px on the feature
   │           ███████               │   ──   leader 1.5 px ink with 5 px white halo, ≤ 1 bend
   │        ●──(2)                   │
   │  FIG BMS-07 · iso 50 mm         │   figure id bottom-left, mono 12 px grey
   └────────────────────────────────┘
```

- Numbers match the step's action list; numbering runs left → right, top → bottom. Max 6 per figure.
- A text label on the image only when the number alone is ambiguous; the action list is the label.
- Dimensions in accent blue `#1F5FC7`, `310 mm` format (value, thin space, unit).
- Motion arrows in orange, 3 px, curved for rotation.
- Leaders never cross each other or the orange part.
- Dark variant (for figures placed on the dark web stage only): see `callouts.dark_theme_variant`.

## Exploded views

Explode along the interface normal from `interfaces.json` (fasteners +z, slid parts along the tube axis) by
1.6 × the part's extent; draw a dashed assembly line between mating faces. Label the view "illustrative order".

## Composition checklist (before a render ships)

1. One action in orange. Would a student know what to pick up?
2. The camera shows the access direction from the joint stack (`access: "from below"` → `under` view).
3. Nothing important is behind a ghost; nothing unrelated is in frame.
4. Figure id present; callout numbers match the step card.
5. Same view family as the neighbouring steps (do not swap iso ↔ iso_rear without reason).
