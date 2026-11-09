# Vendored three.js

Copied from npm so the viewer works offline, by double-click (`file://`) and on GitHub Pages (no CDN). Do not edit
`three.bundle.js`; to update, repeat the steps below with a newer version (published at least two weeks earlier) and
update this table.

| File | Package | Version | npm publish date | Licence |
|---|---|---|---|---|
| `three.bundle.js` | [three](https://github.com/mrdoob/three.js) `build/three.module.min.js` + add-ons `GLTFLoader`, `OrbitControls`, `RoomEnvironment`, `BufferGeometryUtils` (`examples/jsm/`) | 0.170.0 (r170) | 2024-10-31 | MIT (`LICENSE-three.txt`) |

`make_bundle.py` turns the ES modules into one classic script (browsers do not load ES modules from `file://`).
Globals after loading: `THREE` and `THREE_ADDONS`. It only rewrites `import`/`export` lines and stops if it meets
one it does not understand.

## SHA-256 (2026-11-09)

| File | SHA-256 |
|---|---|
| `build/three.module.min.js` | `08fd7545d13d2c7fb65ab691530a802dafefd638596501854f267d0fb13c39e7` |
| `examples/jsm/utils/BufferGeometryUtils.js` | `c25b7930e570e9ec56173cd3b866ec8d2e10016630db3937efb439daf1cedbf6` |
| `examples/jsm/loaders/GLTFLoader.js` | `45139faddd5aaf48ed2d62203d976e5cbd703db1a592de40527f9f6cf58abd44` |
| `examples/jsm/controls/OrbitControls.js` | `80efaadea4f8a636a65fb0bd08bfef62f3d93a0bb94e2e7500f23176c5c07f4e` |
| `examples/jsm/environments/RoomEnvironment.js` | `85869bdd22f7cf0b22e68dcefe6cb710480af0f5c901a76f7a7764fd07fc8014` |
| `three.bundle.js` (output, 869 kB) | `4f1b0b1f82a189f9bfd6c803d544c0cfc204178bb0d3efaa4ac20ec675602ed3` |

## How it was made

```sh
mkdir tmp && cd tmp && npm init -y
npm install --ignore-scripts three@0.170.0
python -I <repo>/redesign/viewer/vendor/make_bundle.py node_modules/three     # prints the hashes above
cp node_modules/three/LICENSE <repo>/redesign/viewer/vendor/LICENSE-three.txt
node <repo>/redesign/viewer/check_viewer.js                                 # bundle loads, GLB parses
```
