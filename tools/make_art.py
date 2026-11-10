"""
TEXTURAL (NINE HANDS | DSP) - visuel du plugin, synthetise d'apres le visuel Textural valide (oct. 2026).

Regle NINE HANDS | DSP des pedales simples : image 1235 x 1800 px, pedale plein cadre (le boitier touche le haut et le bas,
les jacks touchent les bords gauche et droit), fond transparent seulement autour des jacks et dans les coins arrondis.
Dessin dans un repere de travail 760 x 958 unites (2 px par unite), puis recadrage sur boitier + jacks.

Contenu :
  - boitier peint blanc casse satine (teinte relevee sur l'ancien visuel), arete arrondie, grain fin ;
  - motif de particules (assets/vector/particules.svg, fourni par l'utilisateur) imprime en gris sur la coque ;
  - serigraphie noire (cadre, REVERSE, noms des potards, arc et chiffres du PITCH, IN / OUT, symboles de mode,
    titre Textural vectorise d'apres l'ancien visuel, logo NINE HANDS | DSP noir) : dans l'apercu ici,
    dessinee en vectoriel par le plugin dans la version finale ;
  - pieces photo : 6 potards (photos fournies, noirs + PITCH orange), LED 5 mm (photo fournie), footswitch et embases jack
    du kit NINE HANDS | DSP ; pastille barre de presets / ligne d'etat (taille Strong Pickle).
Une seule lumiere : en haut a gauche (ombres vers le bas a droite).
Usage : python3 tools/make_art.py  ->  design/preview_v2.png (apercu), design/layout_v2.json
"""
import os, sys, math, json, subprocess, io
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIT = os.path.join(ROOT, 'assets', 'kit')
SCR = os.environ.get('SCRATCH', '/tmp')
FINAL = os.environ.get('FINAL', '') == '1'      # 1 : fond du plugin + sprites + Layout.h (sans les pieces dessinees par le plugin)

AS = 2
UW, UH = 760, 958
W, H = UW * AS, UH * AS
L = np.array([-0.46, -0.62, 0.64]); L /= np.linalg.norm(L)
V = np.array([0.0, 0.0, 1.0]); HV = (L + V) / np.linalg.norm(L + V)

def load(name):
    return np.asarray(Image.open(os.path.join(KIT, name)).convert('RGBA')).astype(np.float32)

def shift(a, dx, dy):
    return cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]), borderValue=0)

def place(src, c, k, n, ang=0.0):
    """point c de la photo au centre d'un carre de n px, echelle k, rotation ang (degres, sens horaire) ; alpha premultiplie"""
    pm = src.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    k1 = min(1.0, k * 2.0); n1 = int(round(n * k1 / k))
    M = cv2.getRotationMatrix2D((float(c[0]), float(c[1])), -ang, k1)
    M[0, 2] += n1 / 2 - c[0]; M[1, 2] += n1 / 2 - c[1]
    big = cv2.warpAffine(pm, M, (n1, n1), flags=cv2.INTER_AREA if k1 < 1 else cv2.INTER_CUBIC, borderValue=0)
    small = cv2.resize(big, (n, n), interpolation=cv2.INTER_AREA)
    a = np.clip(small[..., 3] / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, small[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    return rgb, a

def with_shadow(rgb, a, s, cast_amt=0.62, contact_amt=0.55, cap=0.86):
    cast = cv2.GaussianBlur(shift(a, 0.06 * s, 0.09 * s), (0, 0), 0.06 * s) * cast_amt
    contact = cv2.GaussianBlur(shift(a, 0.010 * s, 0.016 * s), (0, 0), 0.016 * s) * contact_amt
    sh = np.clip(cast + contact, 0, cap) * (1 - a)
    alpha = np.clip(a + sh, 0, 1)
    col = np.where(alpha[..., None] > 1e-4, rgb * (a / np.maximum(alpha, 1e-4))[..., None], 0)
    return np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.float32)

def over(dst, rgba, x0, y0, opacity=1.0):
    h, w = rgba.shape[:2]
    X0, Y0 = int(round(x0)), int(round(y0))
    sx0, sy0 = max(0, -X0), max(0, -Y0); ex, ey = min(w, W - X0), min(h, H - Y0)
    a = rgba[sy0:ey, sx0:ex, 3:4] / 255.0 * opacity
    reg = dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex]
    dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex] = reg * (1 - a) + rgba[sy0:ey, sx0:ex, :3] * a

def fbm(shape, scales, amps, seed=0):
    r = np.random.default_rng(seed); out = np.zeros(shape, np.float32)
    for s, a in zip(scales, amps):
        n = r.standard_normal((max(2, shape[0] // s + 2), max(2, shape[1] // s + 2))).astype(np.float32)
        out += a * cv2.resize(n, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)
    return out

def rrect_sd(x, y, x0, y0, w, h, r):
    cx, cy = x0 + w / 2, y0 + h / 2
    qx = np.abs(x - cx) - (w / 2 - r); qy = np.abs(y - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

def svg_png(path, w, h=None):
    """SVG -> RGBA (Chromium headless, rsvg-convert absent ici)"""
    out = os.path.join(SCR, '_svg.png')
    js = os.path.join(SCR, 'svg2png.js')
    subprocess.run(['node', js, os.path.abspath(path), out, str(int(w)), str(int(h or w))], check=True,
                   env=dict(os.environ, NODE_PATH=subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()))
    return np.asarray(Image.open(out).convert('RGBA')).astype(np.float32)

# ------------------------------------------------------------------ geometrie
OUT_W, OUT_H = 1235, 1800
JACK_LEN = 104.0
PY0, PH, PR = 34.0, 890.0, 30.0
def jack_sprite(length_units, side):
    im = load('jack_photo.png'); x0, x1, y0, y1 = 46, 558, 80, 188
    rot = np.rot90(im[y0:y1, x0:x1], k=-1 if side > 0 else 1).copy()
    h, w = rot.shape[:2]; k = length_units * AS / h
    n_w, n_h = max(1, int(round(w * k))), int(round(h * k))
    pm = rot.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    sm = cv2.resize(pm, (n_w, n_h), interpolation=cv2.INTER_AREA)
    a = np.clip(sm[..., 3] / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, sm[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    rgb = np.clip(rgb * np.linspace(1.08, 0.86, n_h)[:, None, None], 0, 255)
    return np.dstack([rgb, a * 255]).astype(np.float32), n_w / AS, n_h / AS
JACK_PROT = jack_sprite(JACK_LEN, 1)[1] - 1.5 / AS
PW = OUT_W / OUT_H * PH - 2 * JACK_PROT
PX0 = (UW - PW) / 2
CX = PX0 + PW / 2
CROP_X0, CROP_W = PX0 - JACK_PROT, PW + 2 * JACK_PROT
SC = (OUT_H / 2.0) / PH

# ancien visuel (faceplate 1246 x 1805, boitier x 44..1203, y 7..1797) -> repere de travail
def P(px, py): return (PX0 + (px - 44.0) / 1159.0 * PW, PY0 + (py - 7.0) / 1790.0 * PH)
KS_ = PH / 1790.0                                   # unites de travail par pixel de l'ancien visuel
def D(x, y): return P((x - 202.84) * 1.805, y * 1.805)   # ancien repere de l'editeur -> travail

KNOB_R = 115.5 * KS_
# bloc des potards : tout descendu de 20 px (image 1800 px) et rangees plus espacees (+32 px) pour aerer les noms
DY1 = 20.0 * PH / OUT_H                             # rangee du haut (TIME / SIZE / OVERLAP) et leurs inscriptions
DY2 = (20.0 + 32.0) * PH / OUT_H                    # rangee du bas (REGEN / PITCH / MIX), arc et chiffres du PITCH
def P1(px, py): x, y = P(px, py); return (x, y + DY1)
def P2(px, py): x, y = P(px, py); return (x, y + DY2)
def D1(x, y): a, b = D(x, y); return (a, b + DY1)
def D2(x, y): a, b = D(x, y); return (a, b + DY2)
KNOBS = [(*D1(321.7, 162.6), 'TIME', 0), (*D1(547.7, 162.6), 'SIZE', 0), (*D1(771.6, 161.5), 'OVERLAP', 0),
         (*D2(320.0, 333.2), 'REGEN', 0), (*D2(543.9, 330.2), 'PITCH', 1), (*D2(771.6, 334.9), 'MIX', 0)]
REV_LED = D(460.2, 69.0)
MODE_LED = D(684.0, 69.0)
STATUS_LED = D(544.7, 583.7)
LAB_DY = 15.0 * PH / OUT_H                          # noms sous les potards descendus de 15 px (image 1800 px)
TL_DY = 40.0 * PH / OUT_H                           # titre Textural et LED d etat descendus de 2 x 20 px
STATUS_LED0 = STATUS_LED
STATUS_LED = (STATUS_LED[0], STATUS_LED[1] + TL_DY)
FS = D(544.7, 895.3)
FS = (FS[0], FS[1] - 65.0 * PH / OUT_H)              # remonte de 50 px puis 15 px dans l image 1800 px (demandes nov. 2026)
FS_FLATS = 100.0
JACK_Y = P(0, 840)[1]
TITLE_BOX = (325, 1165, 890, 1245)                  # titre dans l'ancien visuel (px)
LOGO_W = 180.0                                      # logo reduit de 10 % (demande nov. 2026)
LOGO_C = (CX, 0.5 * (FS[1] + FS_FLATS / 2 + PY0 + PH))   # logo en bas, a egale distance du footswitch et du bas de la coque
PILL_W, PILL_H = 400.0 / SC, 38.0 / SC              # pastille de reference (Strong Pickle) : 400 x 38 dans le repere 900
PILL = (CX - PILL_W / 2, P(0, 1322)[1] - PILL_H / 2, PILL_W, PILL_H)
LED_R = 12.0                                        # LED (photo fournie), agrandie (demande nov. 2026)

# ------------------------------------------------------------------ 1. fond et boitier
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
UX, UY = (XX + 0.5) / AS, (YY + 0.5) / AS
img = np.full((H, W, 3), 14.0, np.float32)
sd = rrect_sd(UX, UY, PX0, PY0, PW, PH, PR)
body = np.clip(0.5 - sd * AS, 0, 1)
EDGE = 9.0
d_in = np.clip(-sd, 0, None)
hgt = np.where(d_in < EDGE, np.sqrt(np.clip(EDGE ** 2 - (EDGE - d_in) ** 2, 0, None)), EDGE)
gy, gx = np.gradient(cv2.GaussianBlur(hgt, (0, 0), 1.0), 1.0 / AS)
nrm = np.dstack([-gx, -gy, np.ones_like(hgt)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
ndl = np.clip(nrm @ L, 0, 1); ndh = np.clip(nrm @ HV, 0, 1)
paint = np.array([222.0, 217.0, 212.0])
flat = float(np.array([0, 0, 1.0]) @ L)
shade = (0.80 + 0.20 * ndl / flat)
encl = paint * shade[..., None] + (26 * ndh ** 50 + 6 * ndh ** 8)[..., None]
# lumiere tres douce en haut a gauche, satine
sheen = np.exp(-(((UX - PX0 - 120) / 380) ** 2 + ((UY - PY0 - 140) / 460) ** 2))
encl += (7.0 * sheen - 6.0 * (UY - PY0) / PH)[..., None]
grain = fbm((H, W), [1, 2], [1.6, 0.9], 3) + 0.8 * fbm((H, W), [70, 220], [0.8, 1.0], 4)
encl += grain[..., None] * np.array([1.0, 0.98, 0.96])
img = img * (1 - body[..., None]) + encl * body[..., None]
on_top = np.clip((-sd - 5.0) / 2.0, 0, 1)

# ------------------------------------------------------------------ 2. motif de particules (SVG fourni), gris sur la coque
pa = svg_png(os.path.join(ROOT, 'assets', 'vector', 'particules.svg'), 4096)
ys, xs = np.nonzero(pa[..., 3] > 20)
bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
crop = pa[by0:by1, bx0:bx1]
tw, th = int(round(PW * AS)), int(round(PH * AS))
pm = crop.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
pm = cv2.resize(pm, (tw, th), interpolation=cv2.INTER_AREA)
lay = np.zeros((H, W, 4), np.float32)
x0p, y0p = int(round(PX0 * AS)), int(round(PY0 * AS))
lay[y0p:y0p + th, x0p:x0p + tw] = pm
pa_a = np.clip(lay[..., 3] / 255.0, 0, 1)
pa_c = np.where(pa_a[..., None] > 1e-4, lay[..., :3] / np.maximum(pa_a, 1e-4)[..., None], 0)
ink_part = pa_a * on_top * 0.92
# encre grise posee sur la peinture (multiplication : le grain reste visible)
img = img * (1 - ink_part[..., None]) + (img * pa_c / 230.0) * ink_part[..., None]

# ------------------------------------------------------------------ 3. serigraphie noire (sur-echantillonnee)
SS = 2; K = AS * SS; KW, KH = W * SS, H * SS
F_MED = os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Medium.ttf')
F_BOLD = os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Bold.ttf')
ink_im = Image.new('L', (KW, KH), 0); dr = ImageDraw.Draw(ink_im)
f_lab = ImageFont.truetype(F_BOLD, int(17.5 * K))
f_small = ImageFont.truetype(F_BOLD, int(13.0 * K))
f_dig = ImageFont.truetype(F_BOLD, int(13.0 * K))
f_io = ImageFont.truetype(F_MED, int(15 * K))
VEC = {'texts': [], 'lines': [], 'arcs': []}

def text(x, y, s, font, track=0.0, rot=0):
    VEC['texts'].append([s, os.path.basename(font.path), font.size / K, track, x, y, rot])
    widths = [font.getlength(ch) for ch in s]
    total = sum(widths) + track * K * (len(s) - 1)
    if rot == 0:
        cx = x * K - total / 2
        for ch, w in zip(s, widths):
            dr.text((cx, y * K), ch, font=font, fill=255, anchor='lm'); cx += w + track * K
    else:
        hpx = int(font.size * 1.6)
        t = Image.new('L', (int(total) + 8, hpx), 0); td = ImageDraw.Draw(t); cx = 4
        for ch, w in zip(s, widths):
            td.text((cx, hpx / 2), ch, font=font, fill=255, anchor='lm'); cx += w + track * K
        t = t.rotate(rot, expand=True)
        ink_im.paste(255, (int(x * K - t.width / 2), int(y * K - t.height / 2)), t)

LW = 3.0 * KS_                                      # epaisseur des filets (3 px dans l'ancien visuel)
def line(pts):
    VEC['lines'].append([list(p) for p in pts])
    dr.line([(p[0] * K, p[1] * K) for p in pts], fill=255, width=int(round(LW * K)), joint='curve')

# noms des potards (positions de l'ancien visuel)
GAP5 = 5.0 * PH / OUT_H                             # noms eloignes de leur potard de 5 px (sauf PITCH)
x, y = P1(623, 150); text(x, y - GAP5, 'SIZE', f_lab, 1.0)
for (px, py, s) in [(215, 432, 'TIME'), (1025, 432, 'OVERLAP')]:
    x, y = P1(px, py); text(x, y + LAB_DY + GAP5, s, f_lab, 1.0)
for (px, py, s) in [(215, 746, 'REGEN'), (620, 758, 'PITCH'), (1023, 746, 'MIX')]:
    x, y = P2(px, py); text(x, y + LAB_DY + (0 if s == 'PITCH' else GAP5), s, f_lab, 1.0)
# REVERSE et son crochet
text(*P(155, 77), 'REVERSE', f_small, 0.8)
line([P(155, 100), P(155, 130), P(393, 130)])
# cadre qui relie les potards
line([P2(228, 600), P2(80, 600), P1(80, 293), P1(1153, 293), P2(1153, 600), P2(1013, 600)])
# arc du PITCH (centre / rayon de l'ancien visuel), coupures autour des chiffres
ac, ar = P2(619, 601), 153 * KS_
def arc(a0, a1):           # angles en degres, 0 = haut, sens horaire
    VEC['arcs'].append([ac[0], ac[1], ar, a0, a1])
    pts = [(ac[0] + ar * math.sin(math.radians(a)), ac[1] - ar * math.cos(math.radians(a))) for a in np.linspace(a0, a1, 80)]
    dr.line([(p[0] * K, p[1] * K) for p in pts], fill=255, width=int(round(LW * K)), joint='curve')
arc(-80, -12); arc(12, 80); arc(-140, -100); arc(100, 140)
for (px, py, s) in [(620, 447, '0'), (466, 598, '1'), (771, 598, '1'), (521, 712, '2'), (715, 712, '2')]:
    text(*P2(px, py), s, f_dig)
# - et + : petits filets
for (px, py, plus) in [(473, 476, False), (771, 476, True)]:
    x, y = P2(px, py); h_ = 8.5
    line([(x - h_, y), (x + h_, y)])
    if plus: line([(x, y - h_), (x, y + h_)])
# IN / OUT le long des tranches
# titre : contour vectorise de l'ancien visuel
fp = np.asarray(Image.open(os.path.join(ROOT, 'faceplate.png')).convert('L')).astype(np.float32)
tx0, ty0, tx1, ty1 = TITLE_BOX
tcrop = fp[ty0 - 10:ty1 + 10, tx0 - 10:tx1 + 10]
UPS = 8
big = cv2.resize(tcrop, None, fx=UPS, fy=UPS, interpolation=cv2.INTER_CUBIC)
big = cv2.GaussianBlur(big, (0, 0), 1.4 * UPS / 2)
tm = (big < 95).astype(np.uint8)
n, lab_, st, _ = cv2.connectedComponentsWithStats(tm)
keep = np.zeros_like(tm)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] > 900 * UPS * UPS / 16: keep[lab_ == i] = 1
cnts, hier = cv2.findContours(keep, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
title_paths = []
for c in cnts:
    c = cv2.approxPolyDP(c, 0.9, True)[:, 0, :].astype(np.float32)
    pts = [P(tx0 - 10 + x / UPS, ty0 - 10 + y / UPS) for x, y in c]
    title_paths.append(pts)
# titre a egale distance du bas du mot PITCH et du haut de la LED d'etat
_pb = dr.textbbox((P2(620, 758)[0] * K, P2(620, 758)[1] * K), 'PITCH', font=f_lab, anchor='lm')[3] / K
_lt = STATUS_LED0[1] - LED_R * 1.16
_ys = [y for p_ in title_paths for _, y in p_]
_dy = 0.5 * (_pb + _lt) - 0.5 * (min(_ys) + max(_ys)) + TL_DY   # position validee, puis descendu de 20 px
title_paths = [[(x, y + _dy) for x, y in p_] for p_ in title_paths]
print('titre : ecart haut', round(min(_ys) + _dy - _pb, 2), 'ecart bas', round(_lt - max(_ys) - _dy, 2))
# jacks et IN / OUT au niveau du groupe titre + LED (milieu entre le haut du titre et le bas de la LED)
_tys = [y for p_ in title_paths for _, y in p_]
JACK_Y = float(0.5 * (min(_tys) + STATUS_LED[1] + LED_R * 1.16))
text(PX0 + 22, JACK_Y, 'OUT', f_io, 2.0, 90)
text(PX0 + PW - 22, JACK_Y, 'IN', f_io, 2.0, 90)
# LED d'etat centree entre le bas du titre et le haut de la barre de presets (jacks inchanges)
STATUS_LED = (CX, float(0.5 * (max(_tys) + PILL[1])))          # LED sur l'axe vertical de la pedale (demande nov. 2026)
print('LED : ecart titre', round(STATUS_LED[1] - max(_tys), 2), 'ecart barre', round(PILL[1] - STATUS_LED[1], 2))
tl = Image.new('L', (KW, KH), 0); tdr = ImageDraw.Draw(tl)
for i, pts in enumerate(title_paths):
    is_hole = hier[0][i][3] >= 0
    tdr.polygon([(x * K, y * K) for x, y in pts], fill=0 if is_hole else 255)
# trous dessines apres les contours exterieurs
for i, pts in enumerate(title_paths):
    if hier[0][i][3] >= 0: tdr.polygon([(x * K, y * K) for x, y in pts], fill=0)
ink_im = Image.fromarray(np.maximum(np.asarray(ink_im), np.asarray(tl)))
VEC['title'] = [[[round(x, 2), round(y, 2)] for x, y in p] for p in title_paths]
VEC['title_holes'] = [int(hier[0][i][3] >= 0) for i in range(len(title_paths))]
ink = cv2.resize(np.asarray(ink_im, np.float32) / 255.0, (W, H), interpolation=cv2.INTER_AREA)

# logo NINE HANDS | DSP noir (fourni par l'utilisateur, nov. 2026)
lg = svg_png(os.path.join(ROOT, 'assets', 'NineHands_Logo_Black.svg'), int(LOGO_W * AS * 1521 / 1252.2), int(LOGO_W * AS * 1521 / 1252.2 / 3))
ys, xs = np.nonzero(lg[..., 3] > 10); lg = lg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
lg = cv2.resize(lg, (int(LOGO_W * AS), int(round(lg.shape[0] * LOGO_W * AS / lg.shape[1]))), interpolation=cv2.INTER_AREA)
LOGO_H = lg.shape[0] / AS
# footswitch centre entre le bas de la barre de presets et le haut du logo (logo garde sa place)
FS = (CX, float(0.5 * (PILL[1] + PILL[3] + LOGO_C[1] - LOGO_H / 2)))   # sur l'axe de la pedale
print('footswitch : ecart barre', round(FS[1] - FS_FLATS / 2 - PILL[1] - PILL[3], 2), 'ecart logo', round(LOGO_C[1] - LOGO_H / 2 - FS[1] - FS_FLATS / 2, 2))
logo_a = np.zeros((H, W), np.float32)
lx0, ly0 = int(round((LOGO_C[0] - LOGO_W / 2) * AS)), int(round((LOGO_C[1] - LOGO_H / 2) * AS))
logo_a[ly0:ly0 + lg.shape[0], lx0:lx0 + lg.shape[1]] = lg[..., 3] / 255.0
ink = np.maximum(ink, logo_a)
# symboles des modes (vectoriels, couleurs de l'ancien visuel)
mode_lay = Image.new('RGBA', (KW, KH), (0, 0, 0, 0)); md = ImageDraw.Draw(mode_lay)
VEC['modes'] = []
def half_disc(cx, by, r, col):
    x, y = P(cx, by); rr = r * KS_
    md.pieslice(((x - rr) * K, (y - rr) * K, (x + rr) * K, (y + rr) * K), 180, 360, fill=col)
    VEC['modes'].append(['half', x, y, rr, col])
G = (74, 150, 34, 255); O = (247, 128, 24, 255); R_ = (178, 18, 22, 255)
half_disc(963.6, 107, 25.5, G); half_disc(963.6, 130.7, 18.3, G); half_disc(963.6, 149.3, 10.8, G)
sx, sy = P(1034, 119.3); al = 27.5 * KS_
for i in range(4):
    a = math.radians(i * 45)
    p0 = (sx - al * math.sin(a), sy - al * math.cos(a)); p1 = (sx + al * math.sin(a), sy + al * math.cos(a))
    md.line(((p0[0] * K, p0[1] * K), (p1[0] * K, p1[1] * K)), fill=O, width=int(6.5 * KS_ * K))
    for p in (p0, p1):
        rr = 3.25 * KS_ * K; md.ellipse((p[0] * K - rr, p[1] * K - rr, p[0] * K + rr, p[1] * K + rr), fill=O)
VEC['modes'].append(['star', sx, sy, al, 6.5 * KS_, O])
for ccx in (1102.7, 1137.3):
    x, y = P(ccx, 115.5)
    for rr in (23.0, 15.6, 8.4):
        r2 = rr * KS_
        md.ellipse(((x - r2) * K, (y - r2) * K, (x + r2) * K, (y + r2) * K), outline=R_, width=int(round(3.6 * KS_ * K)))
    VEC['modes'].append(['rings', x, y, [23.0 * KS_, 15.6 * KS_, 8.4 * KS_], 3.6 * KS_, R_])
ml = np.asarray(mode_lay.resize((W, H), Image.LANCZOS)).astype(np.float32)
ma = ml[..., 3:4] / 255.0 * on_top[..., None] * 0.96

# le motif de particules s'efface sous la serigraphie (reserve fine), puis encre noire satinee
res = cv2.dilate((ink > 0.05).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))).astype(np.float32)
res = cv2.GaussianBlur(res, (0, 0), 1.0)
res = cv2.dilate(((ink > 0.05) | (ma[..., 0] > 0.05)).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(8 * AS) | 1, int(8 * AS) | 1))).astype(np.float32)
res = cv2.GaussianBlur(res, (0, 0), 1.5 * AS)
img = img * (1 - (res * ink_part)[..., None]) + (img / np.maximum(1e-3, 1 - ink_part[..., None] + ink_part[..., None] * pa_c / 230.0) * 0 + encl * body[..., None] * 0)[...] * 0 + (res * ink_part)[..., None] * (encl * body[..., None] + grain[..., None] * 0)
ink_a = ink * on_top
ink_col = np.array([22.0, 21.0, 22.0])
if not FINAL:                                   # version finale : serigraphie et symboles dessines en vectoriel par le plugin
    img = img * (1 - ink_a[..., None]) + ink_col * ink_a[..., None]
    img = img * (1 - ma) + ml[..., :3] * ma

img += (fbm((H, W), [1], [1.0], 22) * body)[..., None]

# ------------------------------------------------------------------ 4. potards (photos fournies) : corps fixe + index qui tourne
def knob_parts(name):
    im = load(name)
    C = (648.0, 651.0)
    rgb = im[..., :3]; a = im[..., 3]
    Lm = rgb.mean(2); sat = rgb.max(2) - rgb.min(2)
    hh, ww = Lm.shape; yy, xx = np.mgrid[0:hh, 0:ww]
    col = (np.abs(xx - C[0]) < 34) & (yy > 130) & (yy < 490)
    if 'orange' in name:
        idx = col & (sat < 95) & (Lm > 150)
    else:
        idx = col & (Lm > 120)
    idx = cv2.dilate(idx.astype(np.uint8), np.ones((5, 5), np.uint8))
    soft = cv2.GaussianBlur(idx.astype(np.float32), (0, 0), 1.2)
    # index : la bande creme avec son liseré d'ombre
    capm = np.clip((438.0 - np.hypot(xx - C[0], yy - C[1])) / 3.0, 0, 1)      # l'index reste sur le chapeau (la couronne ne tourne pas ici)
    ind = np.dstack([rgb, np.clip(soft * 1.4, 0, 1) * a * capm])
    # corps sans index : le secteur de l'index est remplace par la meme zone tournee d'un cran de couronne
    # (+/- 36 degres, 10 crans) : cuir, couronne et lumiere y sont presque identiques ; fondu doux sur les bords
    sector = cv2.GaussianBlur(cv2.dilate(idx, np.ones((15, 15), np.uint8)).astype(np.float32), (0, 0), 5.0)
    sector = np.clip(sector * 1.6, 0, 1)
    def rot(img, ang):
        M = cv2.getRotationMatrix2D(C, ang, 1.0)
        return cv2.warpAffine(img, M, (ww, hh), flags=cv2.INTER_CUBIC, borderValue=0)
    fill = 0.5 * (rot(rgb, 36.0) + rot(rgb, -36.0))
    # meme teinte basse frequence que l'original autour du secteur
    lo_o = cv2.GaussianBlur(cv2.inpaint(np.clip(rgb, 0, 255).astype(np.uint8), (cv2.dilate(idx, np.ones((15, 15), np.uint8)) * 255).astype(np.uint8), 9, cv2.INPAINT_TELEA).astype(np.float32), (0, 0), 9)
    lo_f = cv2.GaussianBlur(fill, (0, 0), 9)
    fill = fill - lo_f + lo_o
    body_ = rgb * (1 - sector[..., None]) + fill * sector[..., None]
    bodyimg = np.dstack([np.clip(body_, 0, 255), a])
    return bodyimg, ind, C, 554.0

# Potard entier qui tourne (chapeau, index ET couronne crantee), lumiere fixe :
# en coordonnees polaires autour du centre, l'image tourne (decalage en angle) puis est re-eclairee :
# I(phi) = I0(phi - theta) * Lb(phi) / Lb(phi - theta), Lb = luminance moyennee sur un cran (36 degres, 10 crans).
# Le detail (crans, cuir, index) tourne ; l'eclairage d'ensemble (haut gauche clair, bas droit sombre) reste en place.
# Flou de mouvement : moyenne de positions voisines en angle (blur_deg = angle parcouru pendant l'image).
from scipy.ndimage import uniform_filter1d
_KPOL = {}
KNOB_C, KNOB_RPX, NA = (648.0, 651.0), 554.0, 2880          # centre / rayon dans les photos, 8 lignes par degre
def _knob_polar(name):
    if name not in _KPOL:
        bodyimg, ind, _, _ = knob_parts(name)                 # potard sans son index (secteur rempli par un cran voisin)
        im = bodyimg; pm = im.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
        RR = int(KNOB_RPX * 1.06)
        pol = cv2.warpPolar(pm, (RR, NA), KNOB_C, RR, cv2.WARP_POLAR_LINEAR | cv2.INTER_CUBIC)
        # luminance moyenne ponderee par l'alpha : le bord detoure (alpha faible, couleur premultipliee sombre)
        # ne doit pas compter, sinon le re-eclairage noircit la couronne
        al = pol[..., 3] / 255.0
        lum = pol[..., :3].mean(2)                                   # premultiplie = lum * alpha
        num = uniform_filter1d(lum, size=NA // 10, axis=0, mode='wrap')
        den = uniform_filter1d(al, size=NA // 10, axis=0, mode='wrap')
        lb = num / np.maximum(den, 1e-3) + 1.0
        lb = cv2.GaussianBlur(lb, (0, 0), sigmaX=6, sigmaY=0.1)
        lb[den < 0.2] = np.nan
        with np.errstate(all='ignore'):
            fillv = np.nanmean(lb, axis=0, keepdims=True)
        lb = np.where(np.isnan(lb), np.nan_to_num(fillv, nan=1.0), lb)
        _KPOL[name] = (pol, lb, RR, im.shape[:2], ind)
    return _KPOL[name]
def knob_render(name, ang, blur_deg=0.0):
    """potard tourne de ang degres (sens horaire, 0 = index en haut) ; renvoie rgba non premultiplie (taille photo)"""
    pol, lb, RR, (hh, ww), ind = _knob_polar(name)
    nb = max(1, int(round(abs(blur_deg) / 0.75))) if blur_deg else 1
    offs = np.linspace(-blur_deg / 2, blur_deg / 2, nb) if nb > 1 else [0.0]
    acc = np.zeros_like(pol)
    for o in offs:
        k = int(round((ang + o) * NA / 360.0))
        rp = np.roll(pol, k, axis=0)
        ratio = lb / np.roll(lb, k, axis=0)
        rp[..., :3] *= np.clip(np.nan_to_num(ratio, nan=1.0), 0.72, 1.4)[..., None]
        acc += rp
    acc /= len(offs)
    acc = np.nan_to_num(acc, nan=0.0, posinf=0.0, neginf=0.0)
    out = cv2.warpPolar(acc, (ww, hh), KNOB_C, RR, cv2.WARP_POLAR_LINEAR | cv2.WARP_INVERSE_MAP | cv2.INTER_CUBIC)
    out = np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)
    _yy, _xx = np.mgrid[0:hh, 0:ww]
    out[np.hypot(_xx - KNOB_C[0], _yy - KNOB_C[1]) > RR - 2] = 0     # rien hors du disque polaire
    a = np.clip(out[..., 3:4] / 255.0, 0, 1)
    rgb = np.where(a > 1e-4, out[..., :3] / np.maximum(a, 1e-4), 0)
    return np.dstack([np.clip(rgb, 0, 255), a[..., 0] * 255]).astype(np.float32)

def knob_sprite(name, R_units, value, blur_deg=0.0):
    S_ = 2 * R_units * 1.45; n = int(round(S_ * AS)); k = R_units * AS / KNOB_RPX
    ang = -150 + 300 * value
    img_ = knob_render(name, ang, blur_deg)
    rgb, a = place(img_, KNOB_C, k, n)
    spr = with_shadow(rgb, a, 2 * R_units * AS, 0.42, 0.22, 0.52)   # ombre douce : pas de liseré noir sous la couronne
    # index : tourne avec le potard, garde sa propre lumiere (creme), net (il n'a pas de crans)
    ind = _knob_polar(name)[4]
    irgb, ia = place(ind, KNOB_C, k, n, ang)
    ia = ia * a
    spr[..., :3] = spr[..., :3] * (1 - ia[..., None]) + irgb * ia[..., None]
    return spr, S_

# occlusion autour des pieces en relief
def occlusion(mask, strength=1.0):
    contact = cv2.GaussianBlur(mask, (0, 0), 3.0 * AS); soft = cv2.GaussianBlur(mask, (0, 0), 14.0 * AS)
    o = np.clip(contact * 0.5 + soft * 0.75, 0, 0.42) * strength * (1.0 - mask)
    img[...] = img * (1.0 - o * body)[..., None]
_m = np.zeros((H, W), np.float32)
for (x, y, _, _) in KNOBS:
    _m = np.maximum(_m, np.clip((KNOB_R * 0.97 - np.hypot(UX - x, UY - y)) * AS, 0, 1))
occlusion(_m)
# valeurs du preset 1 (Sea Synth) pour l'apercu
VALS = [0.3, 0.25, 0.9, 0.8, 0.5, 0.58]
for (x, y, _, orange), v in (zip(KNOBS, VALS) if not FINAL else []):
    spr, S_ = knob_sprite('knob_orange_photo.png' if orange else 'knob_black_photo.png', KNOB_R, v)
    over(img, spr, (x - S_ / 2) * AS, (y - S_ / 2) * AS)

# ------------------------------------------------------------------ 5. LED 5 mm (photo fournie) : eteinte / allumee, recoloree
LEDP = load('led5mm_red_photo.png')
# detourage : les pixels du bord (alpha partiel, restes du fond blanc de la photo) prennent la couleur du dome voisin
_edge = (LEDP[..., 3] < 250).astype(np.uint8) * 255
LEDP[..., :3] = cv2.inpaint(np.clip(LEDP[..., :3], 0, 255).astype(np.uint8), _edge, 3, cv2.INPAINT_TELEA).astype(np.float32)
LED_C, LED_RPX = (74.5, 74.5), 47.0          # centre et rayon du dome dans la photo
def recolor(rgb, col):
    """photo rouge -> autre couleur par rotation de teinte : reflets, coeur et relief du dome de la photo conserves"""
    hsv = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    th = cv2.cvtColor(np.uint8([[col]]), cv2.COLOR_RGB2HSV)[0, 0].astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] - 0.0 + th[0]) % 180.0                    # la photo est rouge (teinte ~0)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
def led_sprite(col, on, R_units=LED_R):
    """LED = la photo fournie, telle quelle (allumee) ; eteinte = meme dome assombri, reflet de la piece garde"""
    rgb = LEDP[..., :3]; a = LEDP[..., 3]
    c = rgb.copy() if tuple(col) == (255, 40, 30) else recolor(rgb, col)
    if not on:
        lum = c.mean(2, keepdims=True)
        c = c * 0.20 + lum * 0.10
        hh, ww = a.shape; yy, xx = np.mgrid[0:hh, 0:ww]
        hl = np.exp(-(((xx - 60) / 16.0) ** 2 + ((yy - 40) / 11.0) ** 2))[..., None]
        c = c + hl * 95
    S_ = 2 * R_units * 1.45; n = int(round(S_ * AS)); k = R_units * AS / LED_RPX
    rgb2, a2 = place(np.dstack([c, a]).astype(np.float32), LED_C, k, n)
    # fin joint sombre d'encastrement (la LED reste bien visible, pas de grosse bague)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32); rr = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (R_units * AS)
    seat = np.clip((1.06 - rr) * R_units * AS, 0, 1) * (1 - a2)
    rgb2 = rgb2 * a2[..., None] + np.array([38.0, 36.0, 36.0]) * seat[..., None]
    aa = np.clip(a2 + seat, 0, 1)
    rgb2 = np.where(aa[..., None] > 1e-4, rgb2 / np.maximum(aa, 1e-4)[..., None], 0)
    return with_shadow(rgb2, aa, 2 * R_units * AS, 0.30, 0.25, 0.5), S_
def led_glow(c, col, strength=1.0, GR=60.0):
    x0p, y0p = round((c[0] - GR) * AS), round((c[1] - GR) * AS); size = round(2 * GR * AS)
    reg = img[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.hypot((xx + 0.5) / AS - GR, (yy + 0.5) / AS - GR)
    h1, h2 = 6.0, 22.0
    E = 1.0 * h1 ** 3 / (d ** 2 + h1 ** 2) ** 1.5 + 0.16 * h2 ** 3 / (d ** 2 + h2 ** 2) ** 1.5
    E *= np.clip((GR - d) / 20.0, 0, 1) * strength; E[d < LED_R * 0.9] = 0
    cc = np.array(col) / 255.0
    lit = reg * (1 + E[..., None] * (cc * 1.6 - 0.25 * (1 - cc)))
    img[y0p:y0p + size, x0p:x0p + size] = np.clip(lit, 0, 255)

LEDS = [(REV_LED, (40, 200, 255), False), (MODE_LED, (255, 40, 30), True), (STATUS_LED, (40, 110, 255), True)]
IMG_NO_LED = img.copy()
for (c, col, on) in (LEDS if not FINAL else []):
    if on: led_glow(c, col, 0.9)
    spr, S_ = led_sprite(col, on)
    over(img, spr, (c[0] - S_ / 2) * AS, (c[1] - S_ / 2) * AS)

# ------------------------------------------------------------------ 6. footswitch (kit)
fsim = load('footswitch_photo.png'); FS_C, FS_FLATS_PX = (625.5, 618.0), 718.0
S_ = FS_FLATS * 1.9; n = int(round(S_ * AS)); k = FS_FLATS * AS / FS_FLATS_PX
rgb, a = place(fsim, FS_C, k, n)
_fa = np.zeros((H, W), np.float32); x0p, y0p = int(round((FS[0] - S_ / 2) * AS)), int(round((FS[1] - S_ / 2) * AS))
_fa[y0p:y0p + n, x0p:x0p + n] = np.clip((a - 0.86) / 0.14, 0, 1)
occlusion(_fa)
over(img, with_shadow(rgb, a, FS_FLATS * AS, 0.62), x0p, y0p)

# ------------------------------------------------------------------ 7. pastille barre de presets (Strong Pickle) : esquisse de l'apercu
px0, py0, pw_, ph_ = PILL
PRE_PILL = img.copy()
pill_sd = rrect_sd(UX, UY, px0, py0, pw_, ph_, ph_ / 2)
pm_ = np.clip(0.5 - pill_sd * AS, 0, 1)
edge = np.clip(0.5 - np.abs(pill_sd + 0.6) * AS, 0, 1)
img = img * (1 - pm_[..., None]) + np.array([10.0, 10.0, 11.0]) * pm_[..., None]
img = img * (1 - edge[..., None] * 0.6) + np.array([150.0, 150.0, 152.0]) * edge[..., None] * 0.6
ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
f_p = ImageFont.truetype(F_MED, int(23.0 / SC * AS))
od.text((CX * AS, (py0 + ph_ / 2) * AS), '1 · SEA SYNTH', font=f_p, fill=(236, 236, 236, 255), anchor='mm')
cxl, cxr, cy = (px0 + 17 / SC) * AS, (px0 + pw_ - 17 / SC) * AS, (py0 + ph_ / 2) * AS; t = 5.5 / SC * AS
od.polygon([(cxl - t * 0.6, cy), (cxl + t * 0.6, cy - t), (cxl + t * 0.6, cy + t)], fill=(150, 150, 150, 255))
od.polygon([(cxr + t * 0.6, cy), (cxr - t * 0.6, cy - t), (cxr - t * 0.6, cy + t)], fill=(150, 150, 150, 255))
dot = (px0 + 34 / SC + 8) * AS; rr = 4.2 / SC * AS
od.ellipse((dot - rr, cy - rr, dot + rr, cy + rr), fill=(0, 208, 96, 255))
ova = np.asarray(ov).astype(np.float32)
over(img, ova, 0, 0)

if FINAL: img = PRE_PILL                        # la pastille est dessinee par le plugin
# ------------------------------------------------------------------ 8. embases jack (kit)
alpha = body.copy()
for side in (-1, 1):
    j, jw_u, jh_u = jack_sprite(JACK_LEN, side)
    jh, jw = j.shape[:2]
    jw2 = int(math.floor(JACK_PROT * AS))
    if jw2 != jw:
        pm_ = j.copy(); pm_[..., :3] *= pm_[..., 3:4] / 255.0
        pm_ = cv2.resize(pm_, (jw2, jh), interpolation=cv2.INTER_AREA)
        a_ = np.maximum(pm_[..., 3:4], 1e-3); pm_[..., :3] = np.where(pm_[..., 3:4] > 0.5, pm_[..., :3] * 255.0 / a_, 0)
        j = pm_; jw = jw2
    x0 = int(round((PX0 * AS - jw) if side < 0 else ((PX0 + PW) * AS)))
    y0 = int(round(JACK_Y * AS - jh / 2))
    occ = np.zeros((H, W), np.float32); occ[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
    occ = np.clip(cv2.GaussianBlur(occ, (0, 0), 3.0 * AS) * 0.9 + cv2.GaussianBlur(occ, (0, 0), 18.0 * AS) * 1.6, 0, 0.62)
    occ *= 0.2 if side > 0 else 0.0
    img *= (1.0 - occ * body)[..., None]
    over(img, j, x0, y0)
    ja = np.zeros((H, W), np.float32); ja[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
    alpha = np.maximum(alpha, ja)

# ------------------------------------------------------------------ 9. sortie
def to_out(a):
    x0, x1 = CROP_X0 * AS, (CROP_X0 + CROP_W) * AS; y0, y1 = PY0 * AS, (PY0 + PH) * AS
    M = np.float32([[OUT_W / (x1 - x0), 0, -x0 * OUT_W / (x1 - x0)], [0, OUT_H / (y1 - y0), -y0 * OUT_H / (y1 - y0)]])
    return cv2.warpAffine(a, M, (OUT_W, OUT_H), flags=cv2.INTER_AREA if OUT_H < (y1 - y0) else cv2.INTER_CUBIC)
out_rgb = np.clip(to_out(img), 0, 255); out_a = np.clip(to_out(alpha), 0, 1)
os.makedirs(os.path.join(ROOT, 'design'), exist_ok=True)
Image.fromarray(np.dstack([out_rgb, out_a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'design', 'preview_v2_rgba.png'))
bgc = np.array([14.0, 14.0, 15.0])
pv = out_rgb * out_a[..., None] + bgc * (1 - out_a[..., None])
Image.fromarray(pv.astype(np.uint8)).save(os.path.join(ROOT, 'design', 'preview_v2.png'))
def X(v): return (v - CROP_X0) * SC
def Y(v): return (v - PY0) * SC
json.dump({'frame': [OUT_W / 2, OUT_H / 2], 'knobs': [[X(k[0]), Y(k[1]), KNOB_R * SC] for k in KNOBS],
           'rev': [X(REV_LED[0]), Y(REV_LED[1])], 'mode': [X(MODE_LED[0]), Y(MODE_LED[1])], 'led': [X(STATUS_LED[0]), Y(STATUS_LED[1])],
           'fs': [X(FS[0]), Y(FS[1])], 'pill': [X(PILL[0]), Y(PILL[1]), PILL[2] * SC, PILL[3] * SC], 'jackY': Y(JACK_Y),
           'logo': [X(LOGO_C[0]), Y(LOGO_C[1]), LOGO_W * SC]}, open(os.path.join(ROOT, 'design', 'layout_v2.json'), 'w'), indent=1)
print('ok', PW, PH, JACK_PROT)

# ====================================================================== 10. sorties du plugin (FINAL=1)
if FINAL:
    OUTD = ROOT
    # fond : coque + particules + footswitch + jacks (+ ombres des potards) ; serigraphie, potards, LEDs et pastille
    # sont dessines par le plugin (vectoriel / sprites)
    Image.fromarray(np.dstack([out_rgb, out_a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(OUTD, 'background.png'), optimize=True)
    PU = 2.0                                     # pixels de sprite par unite du plugin (repere 617,5 x 900)
    def X(v): return (v - CROP_X0) * SC
    def Y(v): return (v - PY0) * SC

    # --- potards : la couronne a 10 crans (36 degres) -> le corps est periodique : 36 images nettes (1 degre),
    #     36 images en flou partiel (0,6 cran), 1 image en flou complet (un cran entier, invariant par rotation)
    KR = KNOB_R * SC                             # rayon (unites du plugin)
    S_P = 2 * KR * 1.45; NPX = int(round(S_P * PU)); kk = KR * PU / KNOB_RPX
    NF = 36
    def body_frame(name, ang, blur):
        rgb, a = place(knob_render(name, ang, blur), KNOB_C, kk, NPX)
        return with_shadow(rgb, a, 2 * KR * PU, 0.42, 0.22, 0.52)
    for nm, tag in (('knob_black_photo.png', 'black'), ('knob_orange_photo.png', 'orange')):
        frames = [body_frame(nm, i * 36.0 / NF, 0.0) for i in range(NF)]
        frames += [body_frame(nm, i * 36.0 / NF, 21.6) for i in range(NF)]
        frames += [body_frame(nm, 0.0, 36.0)]
        strip = np.concatenate(frames, 0)
        Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUTD, f'knob_{tag}.png'), optimize=True)
        ind = _knob_polar(nm)[4]
        irgb, ia = place(ind, KNOB_C, kk, NPX, 0.0)
        Image.fromarray(np.dstack([np.clip(irgb, 0, 255), ia * 255]).astype(np.uint8), 'RGBA').save(os.path.join(OUTD, f'knob_index_{tag}.png'), optimize=True)
        print('potard', tag, strip.shape)

    # --- LEDs (photo fournie) : eteinte / allumee par couleur ; halos = facade eclairee (calque alpha)
    LED_COLS = {'cyan': (0, 213, 255), 'green': (57, 255, 46), 'orange': (255, 123, 0), 'red': (255, 40, 30), 'blue': (40, 110, 255)}
    ASL = AS
    for nm, col in LED_COLS.items():
        for on in (0, 1):
            spr, LS = led_sprite(col, bool(on))
            Image.fromarray(np.clip(spr, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUTD, f'led_{nm}_{"on" if on else "off"}.png'), optimize=True)
    GR = 60.0
    def glow_layer(c, col, fn):
        x0p, y0p = round((c[0] - GR) * AS), round((c[1] - GR) * AS); size = round(2 * GR * AS)
        reg = IMG_NO_LED[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
        yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
        d = np.hypot((xx + 0.5) / AS - GR, (yy + 0.5) / AS - GR)
        h1, h2 = 6.0, 22.0
        E = 1.0 * h1 ** 3 / (d ** 2 + h1 ** 2) ** 1.5 + 0.16 * h2 ** 3 / (d ** 2 + h2 ** 2) ** 1.5
        E *= np.clip((GR - d) / 20.0, 0, 1) * 0.9; E[d < LED_R * 0.9] = 0
        cc = np.array(col) / 255.0
        lit = np.clip(reg * (1 + E[..., None] * (cc * 1.6 - 0.25 * (1 - cc))) + 18.0 * E[..., None] * cc, 0, 255)
        add = lit - reg
        a = np.clip(np.abs(add).max(-1) / 10.0, 0, 1)
        rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
        Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(OUTD, fn), optimize=True)
        return (X(c[0] - GR), Y(c[1] - GR), 2 * GR * SC, 2 * GR * SC)
    GL = {'rev': glow_layer(REV_LED, LED_COLS['cyan'], 'glow_rev.png')}
    for nm in ('green', 'orange', 'red'): GL['mode_' + nm] = glow_layer(MODE_LED, LED_COLS[nm], f'glow_mode_{nm}.png')
    GL['status'] = glow_layer(STATUS_LED, LED_COLS['blue'], 'glow_status.png')

    # --- Layout.h
    def f(v): return f"{v:.3f}f"
    def PT(p): return "{ %s, %s }" % (f(X(p[0])), f(Y(p[1])))
    with open(os.path.join(ROOT, 'Layout.h'), 'w') as fo:
        fo.write("// genere par tools/make_art.py (FINAL=1) - ne pas modifier a la main\n// repere du plugin : 617,5 x 900 unites = fond 1235 x 1800 px / 2\n#pragma once\n#include <juce_graphics/juce_graphics.h>\nnamespace layout\n{\n")
        fo.write(f"    constexpr float frameW = {f(OUT_W / 2)}, frameH = {f(OUT_H / 2)};\n")
        fo.write("    // potards : TIME, SIZE, OVERLAP, REGEN, PITCH (orange), MIX\n")
        fo.write("    const juce::Point<float> knobPos[6] = { " + ", ".join(PT(k[:2]) for k in KNOBS) + " };\n")
        fo.write(f"    constexpr float knobR = {f(KR)}, knobS = {f(S_P)};   // rayon du potard / cote du sprite\n")
        fo.write(f"    constexpr int knobFrames = {NF}, knobPx = {NPX};      // images nettes, puis {NF} en flou partiel, puis 1 en flou complet\n")
        fo.write(f"    const juce::Point<float> revPos {PT(REV_LED)}, modePos {PT(MODE_LED)}, ledPos {PT(STATUS_LED)};\n")
        fo.write(f"    constexpr float ledR = {f(LED_R * SC)}, ledS = {f(LS * SC)};\n")
        for k_, r_ in GL.items():
            fo.write(f"    const juce::Rectangle<float> glow_{k_} {{ {f(r_[0])}, {f(r_[1])}, {f(r_[2])}, {f(r_[3])} }};\n")
        fo.write(f"    const juce::Point<float> fsPos {PT(FS)}; constexpr float fsR = {f(FS_FLATS * 0.5 * SC)}, fsBtnR = {f(FS_FLATS * 0.5 * 272.0 / 359.0 * SC)};\n")
        fo.write(f"    const juce::Rectangle<float> pill {{ {f(X(PILL[0]))}, {f(Y(PILL[1]))}, {f(PILL[2] * SC)}, {f(PILL[3] * SC)} }};\n")
        fo.write(f"    const juce::Point<float> logoPos {PT(LOGO_C)}; constexpr float logoW = {f(LOGO_W * SC)};\n")
        fo.write(f"    constexpr float lineW = {f(LW * SC)};\n")
        fo.write("    // textes : chaine, police (0 medium, 1 bold), taille (em), espacement, centre, rotation (degres)\n")
        fo.write("    struct Txt { const char* s; int font; float em, track, x, y, rot; };\n    const Txt texts[] = {\n")
        fo.write(",\n".join(f'        {{ "{t[0]}", {1 if "Bold" in t[1] else 0}, {f(t[2] * SC)}, {f(t[3] * SC)}, {f(X(t[4]))}, {f(Y(t[5]))}, {f(t[6])} }}' for t in VEC['texts']) + "\n    };\n")
        pl = []
        for ln in VEC['lines']: pl.append(ln)
        fo.write("    // filets (polylignes) : nombre de points puis x, y ...\n    const float lines[] = {\n")
        fo.write(",\n".join("        " + str(len(ln)) + ", " + ", ".join(f"{f(X(p[0]))}, {f(Y(p[1]))}" for p in ln) for ln in pl) + "\n    };\n")
        fo.write("    struct Arc { float cx, cy, r, a0, a1; };   // degres, 0 = haut, sens horaire\n    const Arc arcs[] = { ")
        fo.write(", ".join(f"{{ {f(X(a[0]))}, {f(Y(a[1]))}, {f(a[2] * SC)}, {f(a[3])}, {f(a[4])} }}" for a in VEC['arcs']) + " };\n")
        fo.write("    // titre Textural : contours (nombre de points puis x, y ...), remplissage pair-impair\n    const float title[] = {\n")
        fo.write(",\n".join("        " + str(len(pth)) + ", " + ", ".join(f"{X(p[0]):.2f}f, {Y(p[1]):.2f}f" for p in pth) for pth in VEC['title']) + "\n    };\n")
        fo.write("    // symboles des modes\n")
        hd = [m for m in VEC['modes'] if m[0] == 'half']; st = [m for m in VEC['modes'] if m[0] == 'star'][0]; rg = [m for m in VEC['modes'] if m[0] == 'rings']
        fo.write("    struct Half { float x, y, r; };\n    const Half halves[] = { " + ", ".join(f"{{ {f(X(m[1]))}, {f(Y(m[2]))}, {f(m[3] * SC)} }}" for m in hd) + " };\n")
        fo.write(f"    const juce::Point<float> starPos {{ {f(X(st[1]))}, {f(Y(st[2]))} }}; constexpr float starL = {f(st[3] * SC)}, starW = {f(st[4] * SC)};\n")
        fo.write("    const juce::Point<float> ringPos[2] = { " + ", ".join(f"{{ {f(X(m[1]))}, {f(Y(m[2]))} }}" for m in rg) + " };\n")
        fo.write("    const float ringR[3] = { " + ", ".join(f(r * SC) for r in rg[0][3]) + f" }}; constexpr float ringW = {f(rg[0][4] * SC)};\n")
        fo.write("    const juce::uint32 colGreen = 0xff4a9622, colOrange = 0xfff78018, colRed = 0xffb21216;\n")
        fo.write("}\n")
    print('Layout.h ok')
