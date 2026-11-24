import bpy, sys, os, json, glob
import numpy as np
d = sys.argv[sys.argv.index('--')+1]
out = {}
for f in sorted(glob.glob(d + '/clip-*.mp4')):
    c = bpy.data.movieclips.load(f)
    sc = bpy.context.scene
    sc.sequence_editor_create()
    for s in list(sc.sequence_editor.sequences): sc.sequence_editor.sequences.remove(s)
    sc.render.fps = 60; sc.render.fps_base = 1.0
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
    sc.view_settings.view_transform = 'Standard'
    st = sc.sequence_editor.sequences.new_movie('m', f, 1, 1)
    sc.frame_start, sc.frame_end = 1, st.frame_final_duration
    n = st.frame_final_duration
    fr = sorted(set(list(range(1, n+1, 60)) + [n]))
    errs = 0; means = []
    for k in fr:
        sc.frame_set(k)
        sc.render.image_settings.file_format = 'PNG'
        p = os.path.join(os.environ['TEMP'], 'dec_tmp.png')
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(p, check_existing=False)
        a = np.array(im.pixels[:]).reshape(im.size[1], im.size[0], -1)
        if tuple(im.size) != (1920, 1080): errs += 1
        means.append(round(float(a[..., :3].mean()) * 255, 1)); bpy.data.images.remove(im)
    out[os.path.basename(f)] = dict(size=list(c.size), fps=c.fps, frames=c.frame_duration, strip_frames=n, dur=c.frame_duration / c.fps, decoded=len(fr), errors=errs, mean_first=means[0], mean_last=means[-1], mean_min=min(means), bytes=os.path.getsize(f))
print('RESULT' + json.dumps(out))
