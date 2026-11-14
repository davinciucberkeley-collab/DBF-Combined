"""Make vendor/three.bundle.js: three.js core + the four add-ons the viewer uses, as ONE classic script.

Why: three.js ships only ES modules, and browsers refuse to load ES modules from file:// (double-click).
A classic script works from file://, from any local server and from GitHub Pages.

    python -I redesign/viewer/vendor/make_bundle.py PATH/TO/node_modules/three

The script does plain text transforms and refuses to write if anything it does not understand is left
(an `import` or `export` statement). Globals after loading: `THREE` (core) and `THREE_ADDONS`
(GLTFLoader, OrbitControls, RoomEnvironment, BufferGeometryUtils functions).
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = ['examples/jsm/utils/BufferGeometryUtils.js',      # first: GLTFLoader imports from it
          'examples/jsm/loaders/GLTFLoader.js',
          'examples/jsm/controls/OrbitControls.js',
          'examples/jsm/environments/RoomEnvironment.js']


def core(src):
    """three.module.min.js ends with `export{a as B,...};` -> an object literal."""
    m = re.search(r'export\s*\{([^}]*)\}\s*;?\s*$', src)
    if not m:
        sys.exit('core: final export statement not found')
    pairs = []
    for item in m.group(1).split(','):
        local, _, name = item.strip().partition(' as ')
        pairs.append('%s:%s' % (name or local, local))
    body = src[:m.start()] + '__g.THREE={%s};' % ','.join(pairs)
    return '(function(__g){"use strict";\n%s\n})(typeof window!=="undefined"?window:globalThis);\n' % body


def addon(src, name):
    src = re.sub(r"import\s*\{([^}]*)\}\s*from\s*'three'\s*;", lambda m: 'const {%s} = THREE;' % m.group(1), src)
    src = re.sub(r"import\s*\{([^}]*)\}\s*from\s*'\.\./[^']+'\s*;", lambda m: 'const {%s} = __A;' % m.group(1), src)
    src = re.sub(r'^export\s+(function|class|const)\b', r'\1', src, flags=re.M)
    src = re.sub(r'^export\s*\{([^}]*)\}\s*;', lambda m: 'Object.assign(__A, {%s});' % m.group(1), src, flags=re.M)
    left = re.findall(r'^\s*(?:import|export)\b.*$', src, flags=re.M)
    if left:
        sys.exit('%s: cannot convert %r' % (name, left[0]))
    return '(function(__g){"use strict";const THREE=__g.THREE,__A=__g.THREE_ADDONS;\n// ---- %s\n%s\n})(typeof window!=="undefined"?window:globalThis);\n' % (name, src)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    pkg = json.load(open(os.path.join(root, 'package.json'), encoding='utf-8'))
    files = ['build/three.module.min.js'] + ADDONS
    srcs = {f: open(os.path.join(root, f), encoding='utf-8').read() for f in files}
    out = ['/* three.js %s (MIT, see LICENSE-three.txt) + add-ons %s, made by make_bundle.py. Do not edit. */\n'
           % (pkg['version'], ', '.join(os.path.basename(a) for a in ADDONS)),
           core(srcs[files[0]]),
           '(typeof window!=="undefined"?window:globalThis).THREE_ADDONS={};\n']
    out += [addon(srcs[a], a) for a in ADDONS]
    dst = os.path.join(HERE, 'three.bundle.js')
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(out))
    for f in files:
        print('%s  %s' % (hashlib.sha256(srcs[f].encode()).hexdigest(), f))
    print('%s  three.bundle.js (%d bytes)' % (hashlib.sha256(open(dst, 'rb').read()).hexdigest(), os.path.getsize(dst)))


if __name__ == '__main__':
    main()
