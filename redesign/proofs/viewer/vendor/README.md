# Vendored libraries

Copied from npm so the viewer works offline and from GitHub Pages (no CDN). Do not edit these files; to update,
repeat the steps with new versions (pick versions at least two weeks old) and update this table.

| File | Package | Version | npm publish date | Licence | SHA-256 |
|---|---|---|---|---|---|
| `3d-force-graph.min.js` | [3d-force-graph](https://github.com/vasturiano/3d-force-graph) (UMD build, global `ForceGraph3D`) | 1.80.1 | 2026-09-29 | MIT (`LICENSE-3d-force-graph.txt`) | `13088340aad408156064fd120c3bc3a47c93a3cc45b8f132d6284b20e2223be9` |
| `force-graph.min.js` | [force-graph](https://github.com/vasturiano/force-graph) (UMD build, global `ForceGraph`; the 2-D fallback) | 1.52.0 | 2026-09-28 | MIT (`LICENSE-force-graph.txt`) | `f59db59ba92ff5a76ed93d7a4d77a703b176260e5d9cd29f4f8eb4f6c369a629` |

The 3-D bundle includes its dependencies; the ones that matter for licensing:

| Bundled package | Version installed | Licence |
|---|---|---|
| three (r186 per the bundle's `REVISION`) | 0.187.0 resolved by npm; the bundle was built by the author | MIT (`LICENSE-three.txt`) |
| three-forcegraph, three-render-objects | 1.43.6, 1.43.1 | MIT |
| d3-force-3d, d3-octree, d3-binarytree | 3.0.6, 1.1.0, 1.0.2 | MIT |
| ngraph.forcelayout, ngraph.graph, ngraph.events, ngraph.random | 3.3.1, 20.1.2, 1.4.0, 1.2.0 | BSD-3-Clause |
| d3-* (array, color, dispatch, drag, ease, format, interpolate, quadtree, scale, selection, time, timer, transition, zoom) | 3.x / 4.x | ISC (d3-ease: BSD-3-Clause) |
| kapsule, accessor-fn, float-tooltip, polished, preact, tinycolor2, @tweenjs/tween.js, lodash-es, bezier-js, canvas-color-tracker, index-array-by, data-bind-mapper | — | MIT |

All are permissive licences; keeping the LICENSE files beside the bundles satisfies their notice terms.

## How they were fetched (2026-11-09)

```sh
mkdir tmp && cd tmp && npm init -y
npm install --ignore-scripts 3d-force-graph@1.80.1 force-graph@1.52.0
cp node_modules/3d-force-graph/dist/3d-force-graph.min.js node_modules/force-graph/dist/force-graph.min.js <viewer>/vendor/
cp node_modules/3d-force-graph/LICENSE <viewer>/vendor/LICENSE-3d-force-graph.txt   # likewise force-graph, three
```
