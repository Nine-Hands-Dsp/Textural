import sys, numpy as np
from PIL import Image
src = open('/home/claude/textural/tools/make_art.py').read()
g = {'__file__': '/home/claude/textural/tools/make_art.py'}
exec(src[:src.index('# ------------------------------------------------------------------ geometrie')], g)
exec(src[src.index('def knob_parts'):src.index('# occlusion autour des pieces en relief')], g)
R = 60.0; bg = np.array([222.0, 217.0, 212.0]); CRAN = 36.0
def frame(name, v, dv):
    d = abs(dv) * 300.0                                  # degres parcourus pendant l'image
    t = d / CRAN; lvl = np.clip((t - 0.15) / 0.6, 0, 1.6)
    blur = 0.0 if lvl <= 0 else min(d, CRAN * 0.6 * min(lvl, 1.0) + CRAN * 0.4 * max(0, lvl - 1))
    s, S_ = g['knob_sprite'](name, R, v, blur)
    a = s[..., 3:4] / 255.0
    return bg * (1 - a) + s[..., :3] * a
vals = list(np.linspace(0, 1, 60)) + list(np.linspace(1, 0, 12)) + list(np.linspace(0, 0.5, 6)) + [0.5] * 15
frames = []
for i, v in enumerate(vals):
    dv = v - vals[i - 1] if i else 0.0
    im = np.concatenate([frame('knob_black_photo.png', v, dv), frame('knob_orange_photo.png', v, dv)], 1)
    frames.append(Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)))
frames[0].save(sys.argv[1], save_all=True, append_images=frames[1:], duration=33, loop=0, optimize=True)
print(len(frames))
