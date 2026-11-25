# Archive

This folder holds the earlier designs. Nothing here is the current aircraft.

## What is in `archive/c0`

`archive/c0` holds the C0 material: the 11-02 resize (`analysis/`, `cad/`, `review/`), the v0.3.1 inventory, concepts, fusion and sim folders, the tiltwing explorations, the firmware notes, the older HTML pages, and their generated pages.

These files are kept for the record and for the CI regenerate check. Nothing in concept A (`redesign/qp/A`) depends on them.

## Layout

The relative layout inside `archive/c0` is the same as the old repo root. So the generators still work when run from inside `archive/c0`, for example:

    cd archive/c0
    node review/build.mjs

## Where things moved

The old path to new path table is in `docs/archive-path-map.md`.

## What did not move

K09-L material stays under `redesign/`. It was not moved in T-104.
