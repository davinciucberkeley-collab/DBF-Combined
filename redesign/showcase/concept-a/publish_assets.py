"""publish_assets.py - turn the concept A renders into lean web assets and copy them into the Explorer.

    python -I redesign/showcase/concept-a/publish_assets.py

Reads  redesign/showcase/concept-a/_work/<id>.png  or .annotated.png  (render_showcase.py output; see that script)
Writes redesign/showcase/concept-a/renders/<id>.webp   (<= 1600 px wide, WebP q86)
       redesign/showcase/concept-a/renders/thumb/<id>.jpg   (480 x 300)
       redesign/site/assets/renders/a-<id>.webp and thumb/a-<id>.jpg
and copies redesign/showcase/concept-a/animation/* into redesign/site/assets/animation/ (a-how-it-flies.mp4, a-poster.webp,
a-build-poster.webp) and .../build/ (a-build.mp4 and a-stage-NN.mp4/.webp).
Run with the system Python (Pillow).
"""
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
WORK = os.path.join(HERE, '_work')
RENDERS = os.path.join(HERE, 'renders')
SITE = os.path.join(REDESIGN, 'site', 'assets')
ANIM = os.path.join(HERE, 'animation')


def main():
    os.makedirs(os.path.join(RENDERS, 'thumb'), exist_ok=True)
    os.makedirs(os.path.join(SITE, 'renders', 'thumb'), exist_ok=True)
    for fn in sorted(os.listdir(RENDERS)):
        if fn.endswith('.png'):
            os.remove(os.path.join(RENDERS, fn))
    ids = sorted({f.split('.')[0] for f in os.listdir(WORK) if f.endswith('.png') and not f.endswith('.annotated.png')})
    tot = 0
    for i in ids:
        src = os.path.join(WORK, i + '.annotated.png')
        if not os.path.exists(src):
            src = os.path.join(WORK, i + '.png')
        im = Image.open(src).convert('RGB')
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        out = os.path.join(RENDERS, i + '.webp')
        im.save(out, 'WEBP', quality=86, method=6)
        th = im.copy()
        th.thumbnail((480, 300), Image.LANCZOS)
        canvas = Image.new('RGB', (480, 300), th.getpixel((2, 2)))
        canvas.paste(th, ((480 - th.width) // 2, (300 - th.height) // 2))
        tj = os.path.join(RENDERS, 'thumb', i + '.jpg')
        canvas.save(tj, 'JPEG', quality=80, optimize=True)
        shutil.copyfile(out, os.path.join(SITE, 'renders', 'a-' + i + '.webp'))
        shutil.copyfile(tj, os.path.join(SITE, 'renders', 'thumb', 'a-' + i + '.jpg'))
        tot += os.path.getsize(out) + os.path.getsize(tj)
        print('%-22s %6.0f kB webp  %5.0f kB thumb' % (i, os.path.getsize(out) / 1e3, os.path.getsize(tj) / 1e3))
    print('renders total %.2f MB' % (tot / 1e6))
    if os.path.isdir(ANIM):
        os.makedirs(os.path.join(SITE, 'animation', 'build'), exist_ok=True)
        pp = os.path.join(ANIM, 'a-poster.png')
        if os.path.exists(pp):                            # PNG poster -> WebP
            Image.open(pp).convert('RGB').save(os.path.join(ANIM, 'a-poster.webp'), 'WEBP', quality=86, method=6)
            os.remove(pp)
        for fn in sorted(os.listdir(ANIM)):
            p = os.path.join(ANIM, fn)
            if fn.endswith('.json'):
                continue
            if fn.startswith('stage-') or fn in ('a-build.mp4', 'a-build-poster.webp'):
                dst = os.path.join(SITE, 'animation', 'build', 'a-' + fn if fn.startswith('stage-') else fn)
            elif fn.startswith('a-'):
                dst = os.path.join(SITE, 'animation', fn)
            else:
                continue
            shutil.copyfile(p, dst)
            print('copied %-24s -> %s (%.2f MB)' % (fn, os.path.relpath(dst, SITE), os.path.getsize(dst) / 1e6))


if __name__ == '__main__':
    sys.exit(main())
