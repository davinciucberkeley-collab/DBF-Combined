"""mp4_faststart.py - move the moov box of an MP4 in front of mdat (like ffmpeg -movflags +faststart), in place.

    python -I redesign/showcase/tools/mp4_faststart.py FILE.mp4 [FILE.mp4 ...]

Why: the renders write moov (the index) after the media data. A browser that cannot make HTTP range requests to the
host then cannot seek: the Explorer build film would not fast-forward (user, 2026-11-16). With moov first the player
knows every frame's byte offset as soon as the head of the file arrives. Stdlib only; rewrites the stco / co64 chunk
offsets by the size of moov. A file that already has moov before mdat is left unchanged.
"""
import struct
import sys

CONTAINERS = {b'moov', b'trak', b'mdia', b'minf', b'stbl', b'edts', b'dinf', b'udta'}


def boxes(b, start, end):
    i = start
    while i < end:
        n, t = struct.unpack('>I4s', b[i:i + 8])
        hdr = 8
        if n == 1:
            n = struct.unpack('>Q', b[i + 8:i + 16])[0]
            hdr = 16
        elif n == 0:
            n = end - i
        yield i, n, hdr, t
        i += n


def shift_offsets(moov, delta):
    moov = bytearray(moov)

    def walk(start, end):
        for i, n, hdr, t in boxes(moov, start, end):
            if t in CONTAINERS:
                walk(i + hdr, i + n)
            elif t in (b'stco', b'co64'):
                cnt = struct.unpack('>I', moov[i + hdr + 4:i + hdr + 8])[0]
                p = i + hdr + 8
                w, f = (4, '>I') if t == b'stco' else (8, '>Q')
                for k in range(cnt):
                    v = struct.unpack(f, moov[p + k * w:p + (k + 1) * w])[0] + delta
                    if t == b'stco' and v > 0xFFFFFFFF:
                        raise SystemExit('offset overflow in stco; needs co64')
                    moov[p + k * w:p + (k + 1) * w] = struct.pack(f, v)
    walk(8, len(moov))
    return bytes(moov)


def faststart(path):
    b = open(path, 'rb').read()
    top = list(boxes(b, 0, len(b)))
    order = [t for _, _, _, t in top]
    if b'moov' not in order or b'mdat' not in order:
        print('%s: no moov/mdat, skipped' % path)
        return
    if order.index(b'moov') < order.index(b'mdat'):
        print('%s: already faststart' % path)
        return
    mi, mn = next((i, n) for i, n, _, t in top if t == b'moov')
    moov = shift_offsets(b[mi:mi + mn], mn)
    first_mdat = next(i for i, _, _, t in top if t == b'mdat')
    out = b[:first_mdat] + moov + b[first_mdat:mi] + b[mi + mn:]
    assert len(out) == len(b)
    open(path, 'wb').write(out)
    print('%s: moov (%d bytes) moved in front of mdat' % (path, mn))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        faststart(p)
