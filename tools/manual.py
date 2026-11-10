# TEXTURAL (NINE HANDS | DSP) - notice PDF en francais, illustree avec le rendu reel du plugin (couverture minimale commune).
# Usage : python3 tools/manual.py <dossier des captures (tools/render)> <fichier PDF de sortie>
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, KeepTogether, CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS, OUT = sys.argv[1], sys.argv[2]
VERSION = "2.0.0"
TMP = os.path.join(ROOT, "tools", "manual_assets"); os.makedirs(TMP, exist_ok=True)
FONTS = os.path.join(ROOT, "assets", "fonts")
for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("Title", "BarlowCondensed-ExtraBold"), ("Dj", "DejaVuSans")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))

ACC = colors.HexColor("#E8650F"); ACC_L = colors.HexColor("#FF9A4D")       # orange du potard PITCH
DARK = colors.HexColor("#1B1A19"); GREY = colors.HexColor("#6B6762"); LIGHT = colors.HexColor("#F4F0EA")

# reperes du plugin (repere 617,5 x 900), lus dans Layout.h ecrit par tools/make_art.py
import re
LH = open(os.path.join(ROOT, "Layout.h")).read()
def pt(name):
    m = re.search(name + r"\s*\{\s*([-\d.]+)f,\s*([-\d.]+)f\s*\}", LH); return float(m.group(1)), float(m.group(2))
KNOBS = [tuple(float(v) for v in m) for m in re.findall(r"\{\s*([-\d.]+)f,\s*([-\d.]+)f\s*\}", LH.split("knobPos[6] =")[1].split(";")[0])]
REV, MODE, LED, FS = pt("revPos"), pt("modePos"), pt("ledPos"), pt("fsPos")
PILL = [float(v) for v in re.search(r"pill \{ ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f \}", LH).groups()]

def shot(name): return Image.open(os.path.join(SHOTS, name)).convert("RGB")
src = shot("default.png")
k = src.height / 900.0

# ---------- capture annotee ----------
marks = [(1, KNOBS[0][0] - 50, KNOBS[0][1] - 66), (2, KNOBS[1][0] + 50, KNOBS[1][1] - 66), (3, KNOBS[2][0] + 50, KNOBS[2][1] - 66),
         (4, KNOBS[3][0] - 50, KNOBS[3][1] + 70), (5, KNOBS[4][0] + 64, KNOBS[4][1] + 72), (6, KNOBS[5][0] + 50, KNOBS[5][1] + 70),
         (7, REV[0] - 30, REV[1] + 2), (8, MODE[0] - 30, MODE[1] + 2), (9, LED[0] + 32, LED[1]),
         (10, PILL[0] + 10, PILL[1] - 14), (11, FS[0] + 76, FS[1]), (12, 30, 470), (13, 588, 470)]
ann = src.copy(); dr = ImageDraw.Draw(ann)
fnt = ImageFont.truetype(os.path.join(FONTS, "Poppins-Bold.ttf"), 30)
for n, x, y in marks:
    cx, cy, r = x * k, y * k, 26
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=(232, 101, 15), width=5)
    dr.text((cx, cy + 1), str(n), font=fnt, fill=(27, 26, 25), anchor="mm")
annotated = os.path.join(TMP, "textural_annotated.png"); ann.save(annotated)

def crop_u(im, box): return im.crop(tuple(int(v * k) for v in box))
def strip(parts, path, gap=18, vertical=False):
    if vertical:
        s = Image.new("RGB", (max(p.width for p in parts), sum(p.height for p in parts) + gap * (len(parts) - 1)), (255, 255, 255)); y = 0
        for p in parts: s.paste(p, (0, y)); y += p.height + gap
    else:
        s = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), max(p.height for p in parts)), (255, 255, 255)); x = 0
        for p in parts: s.paste(p, (x, 0)); x += p.width + gap
    s.save(path); return path
box_on = (LED[0] - 120, LED[1] - 36, LED[0] + 120, FS[1] + 66)
on_img = strip([crop_u(shot("bypass.png"), box_on), crop_u(src, box_on)], os.path.join(TMP, "textural_onoff.png"))
box_top = (150, 20, 600, 100)
modes_img = strip([crop_u(shot("mode%d.png" % m), box_top) for m in range(3)] + [crop_u(shot("reverse.png"), box_top)],
                  os.path.join(TMP, "textural_modes.png"), gap=10, vertical=True)
box_bar = (PILL[0] - 8, PILL[1] - 8, PILL[0] + PILL[2] + 8, PILL[1] + PILL[3] + 8)
bar_img = strip([crop_u(src, box_bar), crop_u(shot("status.png"), box_bar)], os.path.join(TMP, "textural_bar.png"), gap=14, vertical=True)
box_knobs = (0, 60, 617.5, 430)
def knobs_img(pr): return crop_u(shot("p%d.png" % pr), box_knobs)

# ---------- couverture : pedale detouree, reflet au sol, halo orange tres doux ----------
msk = Image.open(os.path.join(ROOT, "background.png")).getchannel("A").resize(src.size, Image.LANCZOS)
cut = Image.new("RGBA", src.size, (0, 0, 0, 0)); cut.paste(src, (0, 0), msk)
cut = cut.crop(cut.getbbox())
cw, ch = cut.size
pad = int(cw * 0.16)
canvas = Image.new("RGBA", (cw + 2 * pad, int(ch * 1.30) + pad), (0, 0, 0, 255))
yy, xx = np.mgrid[0:canvas.height, 0:canvas.width].astype(np.float64)
gcx, gcy = canvas.width / 2, pad + ch * 0.45
glow = np.exp(-(((xx - gcx) / (cw * 0.62)) ** 2 + ((yy - gcy) / (ch * 0.48)) ** 2)) * 30
edge = np.clip(np.minimum.reduce([xx, canvas.width - 1 - xx, yy, canvas.height - 1 - yy]) / (pad * 0.9), 0, 1)
glow *= edge ** 2
halo = np.dstack([glow * 0.95, glow * 0.45, glow * 0.12, np.full_like(glow, 255)]).astype(np.uint8)
canvas = Image.alpha_composite(canvas, Image.fromarray(halo, "RGBA"))
refl = cut.transpose(Image.FLIP_TOP_BOTTOM)
ra = np.array(refl).astype(np.float64)
fade = np.clip(1 - np.arange(refl.height) / (refl.height * 0.22), 0, 1) ** 1.6 * 0.22
ra[..., 3] *= fade[:, None]
canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA"), (pad, pad + ch + 6))
canvas.alpha_composite(cut, (pad, pad))
canvas = canvas.crop((0, 0, canvas.width, pad + int(ch * 1.20)))
cover = os.path.join(TMP, "textural_cover_cutout.png"); canvas.convert("RGB").save(cover)

def img(path, width=None, im=None):
    if im is not None:
        path_ = os.path.join(TMP, "tmp_%d.png" % id(im)); im.save(path_); path = path_
    pim = Image.open(path); h = width * pim.height / pim.width
    return RLImage(path, width=width, height=h)

# ---------- styles ----------
st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=20, leading=24, textColor=ACC, spaceAfter=8, spaceBefore=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=13, leading=17, textColor=DARK, spaceAfter=4, spaceBefore=9, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=5),
    "tip": ParagraphStyle("tip", fontName="Pop", fontSize=9.0, leading=12.4, textColor=DARK, spaceAfter=3),
    "small": ParagraphStyle("small", fontName="Pop", fontSize=8.2, leading=11.5, textColor=GREY),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.4, leading=11, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.4, leading=11, textColor=DARK),
    "cells": ParagraphStyle("cells", fontName="Pop", fontSize=7.8, leading=10, textColor=DARK),
    "cellbs": ParagraphStyle("cellbs", fontName="PopM", fontSize=7.8, leading=10, textColor=DARK),
}
def P(t, s="p"): return Paragraph(t, st[s])
def bullets(items, s="p"): return [P("&bull;&nbsp;&nbsp;" + i, s) for i in items]
def table(rows, widths, header=True, small=False):
    data = [[P(c, ("cellbs" if small else "cellb") if (header and r == 0) else ("cells" if small else "cell")) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E2DAD0")),
             ("TOPPADDING", (0, 0), (-1, -1), 2 if small else 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 2 if small else 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC)]
    t.setStyle(TableStyle(style)); return t

# ---------- textes (identiques au code livre) ----------
INTRO = ["<b>TEXTURAL</b> est un plugin NINE HANDS | DSP inspiré de la pédale granulaire <b>MXR Textures</b> (Granular Synth Engine). Il enregistre ce que vous jouez et le reconstruit à partir de minuscules tranches de son, les <b>grains</b> : nappes scintillantes, cascades d'octaves, rythmes glitchés, voix de synthé polyphoniques ou guitare jouée à l'envers, dans une seule pédale.",
         "Trois modes de capture (Delay, Auto Freeze, Layers), six potards principaux, une seconde couche de paramètres cachés (comme en maintenant les boutons de la pédale), une reverb plate modulée, un double filtre résonant, un vibrato, huit emplacements de presets et un pilotage MIDI complet par MIDI Learn.",
         "Le visuel est un design original NINE HANDS | DSP : coque blanc cassé imprimée d'un motif de particules, potards crantés noirs et PITCH orange. Textural n'est pas affilié à MXR / Dunlop ; « Textures » ne sert qu'à décrire la pédale dont il s'inspire."]
INST = [("Windows", "Cliquez sur le bouton <b>Télécharger Windows</b> de la page GitHub Nine-Hands-Dsp/Textural (il donne toujours la dernière version), décompressez <b>Textural-VST3-Windows.zip</b> et copiez le dossier <b>Textural.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3</b>."),
        ("macOS", "Cliquez sur <b>Télécharger macOS</b>, décompressez <b>Textural-VST3-macOS.zip</b> et copiez <b>Textural.vst3</b> dans <b>~/Bibliothèque/Audio/Plug-Ins/VST3</b>. Si macOS le bloque, tapez <b>xattr -cr ~/Library/Audio/Plug-Ins/VST3/Textural.vst3</b> dans le Terminal. Le binaire est universel (Apple Silicon et Intel)."),
        ("Reaper", "Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Le plugin apparaît sous le nom <b>Textural (NINE HANDS | DSP)</b>. Pour le piloter avec des footswitchs et pédales d'expression MIDI, la piste doit recevoir le MIDI du contrôleur (par exemple la M-Vave Chocolate Plus).")]
OV = [["#", "Commande", "Rôle"],
      ["1", "TIME", "Retard des grains (Delay, Auto Freeze) ou attaque des couches (Layers)."],
      ["2", "SIZE", "Longueur des grains (et des phrases inversées)."],
      ["3", "OVERLAP", "Nombre de grains simultanés, 1 à 30."],
      ["4", "REGEN", "Réinjection (Delay, Auto Freeze) ou déclin des couches (Layers)."],
      ["5", "PITCH", "Transposition des grains, ±2 octaves."],
      ["6", "MIX", "Du son sec au tout granulaire ; particules au-delà de 75 %."],
      ["7", "LED REVERSE", "Clic : reverse on / off (cyan). Appui long : couche cachée REVERSE."],
      ["8", "LED MODE", "Clic : Delay (vert) → Auto Freeze (orange) → Layers (rouge). Appui long : couche cachée MODE."],
      ["9", "LED d'état", "Bleue = effet actif. Clic : couche cachée FOOTSWITCH."],
      ["10", "Presets / ligne d'état", "Barre de presets au repos ; ligne d'état pendant les réglages."],
      ["11", "Footswitch", "Effet actif / coupé ; maintien = gel ou défilement des presets."],
      ["12", "OUT", "Jack de sortie."], ["13", "IN", "Jack d'entrée."]]
MODES = [("Delay (LED verte)", "Votre jeu est enregistré en continu et rejoué en grains, TIME derrière le son le plus récent : répétitions nettes, traînées floues et échos transposés. REGEN réinjecte la sortie delay et / ou granulaire (Regen Mix). Maintien du footswitch : gèle le buffer."),
         ("Auto Freeze (LED orange)", "Textural écoute chaque note ou accord. Il l'enregistre pendant TIME, gèle le buffer et le garde vivant sous forme de nappe de grains qui évolue. Une nouvelle note remplace la précédente. Maintien du footswitch : dégèle pour laisser entrer du nouveau son."),
         ("Layers (LED rouge)", "Jusqu'à quatre notes ou accords dans quatre buffers séparés (le cinquième remplace le plus ancien), chacun avec sa montée (TIME = attaque, 5 ms à 5 s) et son extinction (REGEN = déclin, 0,1 s à l'infini), comme les voix d'un synthé polyphonique. Maintien du footswitch : gèle les couches.")]
CTL = [["Potard", "Delay", "Auto Freeze", "Layers"],
       ["TIME", "Retard des grains · 50 ms – 2 s", "Retard + durée d'enregistrement avant le gel", "Attaque de chaque couche · 5 ms – 5 s"],
       ["SIZE", "Longueur des grains · 60 ms – 2 s", "Longueur des grains · 60 ms – 2 s", "Longueur des grains · 60 – 500 ms"],
       ["OVERLAP", "1 – 30 grains simultanés", "1 – 30 grains simultanés", "1 – 30 grains par couche"],
       ["REGEN", "Réinjection · 0 – 98 %", "Réinjection (aucune pendant le gel)", "Déclin · 0,1 s – ∞"],
       ["PITCH", "−24 … +24 demi-tons, cran central", "idem", "idem"],
       ["MIX", "Sec → tout granulaire · particules au-delà de 75 %", "idem", "idem"]]
KNOB_TXT = ["Potards : glisser vers le haut / le bas (Maj = réglage fin), molette, double-clic = valeur par défaut, clic droit = MIDI Learn. La course va du premier au dernier point de repère (270°). La couronne crantée tourne avec l'index, avec un flou de mouvement quand on tourne vite."]
REV_TXT = ["Cliquez sur la LED <b>REVERSE</b> : Textural rejoue votre guitare <b>à l'envers, phrase par phrase</b>, comme un reverse delay. SIZE règle la longueur des phrases (0,25 à 2 s), TIME l'attente avant leur lecture, et le paramètre caché <b>Reverse Random</b> le mélange entre guitare à l'envers et grains à l'endroit (10 à 100 %). Les phrases se fondent l'une dans l'autre sur 20 % de leur durée, calées en phase : aucun clic ni décrochage. En mode Layers, REVERSE inverse les grains de chaque voix.",
           "<b>LED MODE</b> : elle prend la couleur du symbole du mode actif (vert, orange, rouge) et clignote quand le son est gelé."]
FS = ["<b>Footswitch</b> : il bascule dès l'appui et le bouton s'assombrit tant qu'on appuie. Sans Trails, l'effet s'éteint en fondu et son buffer est vidé.",
      "<b>Maintien</b> : gel en Delay et en Layers ; en Auto Freeze, le maintien dégèle. Avec <b>FS Hold Mode</b> sur Preset Scroll : un maintien entre dans le défilement des presets (la LED bleue respire), un clic passe au preset suivant, un nouveau maintien en sort.",
      "<b>LED d'état</b> : bleue quand l'effet est actif. Les LEDs éclairent la façade autour d'elles : clic droit &gt; <b>Glow</b> règle l'intensité de ces halos (25, 50, 75 ou 100 %)."]
HID = [["Couche", "Accès", "Potards (TIME, SIZE, OVERLAP, REGEN, PITCH, MIX)"],
       ["REVERSE", "Ctrl + glisser, ou appui long sur la LED REVERSE (elle clignote)", "Time Random, Size Random, Overlap Random, Regen Mix (Delay ↔ Granular), Pitch Random, Reverse Random"],
       ["MODE", "Alt + glisser, ou appui long sur la LED MODE", "Reverb Mix, Cutoff (LP sous midi, HP au-dessus), Vibrato Rate, Reverb Decay (0,4 s – ∞), Quantize, Vibrato Depth"],
       ["FOOTSWITCH", "Ctrl + Alt + glisser, ou clic sur la LED bleue", "Preset Mute, —, Trails, Output Mode (Mono, Wet/Dry, Stéréo), FS Hold Mode (Scroll / Freeze), Output Gain (−12 à +12 dB)"]]
HID_DESC = ["<b>Time Random</b> : au-delà de 45 %, stutters glitch (certains grains rejouent la tranche précédente).",
            "<b>Pitch Random</b> : le premier tiers ajoute un désaccord en unisson jusqu'à ±30 cents (synthé épais) ; au-delà, les grains sautent à l'octave, à la quinte et à la quarte.",
            "<b>Regen Mix</b> : réinjection delay pure (à gauche) ou granulaire (à droite, cascades de hauteur).",
            "<b>Cutoff</b> : filtre 4 pôles, la résonance monte vers les extrêmes. <b>Quantize</b> cale PITCH sur les quartes, quintes et octaves.",
            "<b>Tap tempo</b> : Ctrl + clic sur la LED MODE (ou couche REVERSE verrouillée puis clic sur MODE), au moins deux fois en rythme ; le tempo s'affiche en BPM dans la ligne d'état. Tourner OVERLAP ensuite rend l'espacement au potard."]
EXTRAS = ["<b>Particules</b> : au-delà de 75 %, MIX projette un nuage de grains de 10 à 45 ms dans tout le champ stéréo, à l'octave ou à la douzième quand Pitch Random est monté, à l'envers quand REVERSE est actif.",
          "<b>Diffuseur</b> : quand OVERLAP est élevé, un réseau de filtres passe-tout fond les grains en un nuage lisse.",
          "<b>Grains calés en phase</b> : quand il y a peu de grains, chaque nouveau grain est décalé de ±12 ms au plus pour s'aligner sur les autres : une note tenue garde un niveau régulier.",
          "<b>Bande et ping-pong</b> : le filtre colore les répétitions, Vibrato Depth ajoute du pleurage, et en sortie stéréo les répétitions rebondissent de gauche à droite.",
          "<b>Voix analogiques</b> : en Layers, chaque voix dérive légèrement et passe dans une saturation douce."]
MIDI = ["Toutes les commandes se pilotent depuis un contrôleur MIDI (footswitchs, pédales d'expression). <b>Aucun CC n'est assigné d'office</b> : clic droit sur une commande (le potard dans la couche active, les LEDs REVERSE et MODE, le footswitch, la flèche ▶ de la barre de presets) &gt; <b>MIDI Learn</b>, puis bougez la pédale ou appuyez sur le bouton. La ligne d'état affiche <b>MIDI LEARN · &lt;nom&gt;</b> puis confirme, par ex. <b>TIME = CC 64</b>. <b>Clear MIDI</b> retire une assignation ; le sous-menu <b>MIDI</b> liste les 29 commandes (dont Freeze et Tap Tempo) et <b>Clear all MIDI assignments</b> les efface toutes. Les assignations sont sauvegardées avec le projet.",
        "<b>Program Change 1 à 8</b> : emplacements de la pédale (2 = Live) ; <b>9</b> : Slow Attack Soundtrack. Tous les paramètres sont aussi automatisables dans le DAW."]
WIN = ["Textural utilise le format pédale simple de NINE HANDS | DSP : la fenêtre montre la pédale seule, plein cadre (visuel de 1235 × 1800 px), textes, graduations et logo dessinés en vectoriel, nets à toutes les tailles. Elle s'ouvre à <b>60 %</b> et ne peut jamais être réduite en dessous. Clic droit &gt; <b>Plugin size</b> : 60 %, 75 % ou 100 %, « (default) » indiquant la taille par défaut ; <b>Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres. Le coin en bas à droite agrandit jusqu'à 150 %. Les menus clic droit s'ouvrent à l'endroit du clic.",
       "La <b>barre de presets</b> et la <b>ligne d'état</b> partagent la même pastille. Au repos : ◀ / ▶ = preset précédent / suivant, clic sur le nom = liste des presets, point vert (1-4) ou rouge (5-8), « * » quand le preset est modifié. Dès qu'un réglage bouge (souris, molette, automation, MIDI), la ligne d'état prend sa place et affiche la valeur en direct (par ex. <i>SIZE 102 MS</i>), le mode, le tempo ou le MIDI Learn ; 2,5 s après le dernier mouvement, la barre de presets revient. Un clic sur la pastille la fait revenir tout de suite."]
PRE = ["À l'ouverture, Textural charge le preset 1 (Sea Synth). Clic droit &gt; <b>Save current settings to preset</b> enregistre vos réglages dans un emplacement ; <b>Reset current preset / all presets to factory</b> rend les réglages d'usine. <b>2 · Live</b> garde vos réglages courants, potards, LEDs et paramètres cachés compris : quittez-le et revenez-y, tout est comme vous l'avez laissé."]
PRE_DESC = {1: "Synthé granulaire polyphonique ondulant : quatre voix désaccordées, montée douce, vibrato lent, passe-bas chaleureux. Jouez des accords et laissez-les sonner.",
            3: "Boucles d'octaves régénérées : chaque répétition monte d'une octave et s'évanouit en reflets brillants. Notes seules et arpèges lents.",
            4: "Mélodies gelées, rejouées à l'endroit, à l'envers et à d'autres octaves. Jouez une courte phrase et laissez-la s'épanouir.",
            5: "Reverb shimmer granulaire : grains à l'octave fondus dans une longue plate, Regen Mix 83 / 17. Notes longues, accords ouverts.",
            6: "Votre guitare à l'envers, phrase par phrase, dans une large reverb. Jouez lentement ; SIZE règle la longueur des phrases.",
            7: "Nappe à l'octave inférieure avec vibrato de violoncelle, qui gonfle après chaque note. Notes seules dans le médium.",
            8: "Synthé granulaire en Layers sous une pluie de particules et d'éclats inversés. Arpèges et harmoniques ; MIX dose la poussière.",
            9: "Nappe lente une quinte plus bas, montée de 587 ms, déclin de 17,8 s. Hors emplacements : liste des presets du DAW, barre de presets ou Program Change 9."}
TIPS = ["Dans Reaper, placez Textural <b>après</b> votre simulateur d'ampli (Ampire puis Impulse) pour des nappes propres, ou <b>avant</b> pour des textures saturées.",
        "En Layers, montez REGEN au-delà de 3 h pour que les voix tiennent : quatre accords grattés donnent une nappe à quatre voix. Un TIME long transforme une note pincée en note jouée à l'archet.",
        "Des grains très courts, nombreux et sans hasard sonnent comme un modulateur en anneau : ajoutez un peu de Size ou d'Overlap Random pour casser cette sonnerie.",
        "MIX au minimum et Reverb Mix monté : une simple reverb plate sur le son sec.",
        "Avec une 7 cordes en Sol, PITCH à +12 éclaircit les nappes sans perdre l'attaque des notes graves."]
TECH = [["Format", "VST3 (Windows 64 bits, macOS universel)"], ["Canaux", "Entrée mono ou stéréo, sortie stéréo"],
        ["Buffers", "Buffer granulaire de 12 s, 4 buffers de couches de 2,6 s"], ["Grains", "Jusqu'à 160 grains simultanés, interpolation Hermite 4 points"],
        ["Reverb", "Plate de Dattorro modulée, 0,4 s – 60 s, puis infinie"], ["Filtre", "Double LP / HP 4 pôles résonant"], ["Latence", "0 échantillon"],
        ["MIDI", "MIDI Learn sur 29 commandes (rien d'assigné par défaut), Program Change 1-9"],
        ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, jusqu'à 150 %, jamais sous 60 % ; Glow 25 / 50 / 75 / 100 % ; anti-gel v2 sous Windows"],
        ["Version", VERSION]]

PRESETS = {p["slot"]: p for p in json.load(open(os.path.join(ROOT, "tools", "presets.json")))}

COVER = dict(lang="FRANÇAIS", sub="Moteur granulaire")
W = A4[0] - 36 * mm
LOGO_PNG = os.path.join(ROOT, "assets", "nine_hands_logo_blanc.png")

f = [NextPageTemplate("p"), Spacer(1, 1), PageBreak()]
f.append(P("1. Présentation", "h1")); f += [P(x) for x in INTRO]
f.append(P("2. Installation", "h1"))
for h, x in INST: f.append(P(h, "h2")); f.append(P(x))
f.append(PageBreak())
f.append(P("3. Vue d'ensemble de l'interface", "h1"))
ov = Table([[[img(annotated, 82 * mm)],
             [table(OV, [8 * mm, 27 * mm, W - 90 * mm - 35 * mm], small=True), Spacer(1, 4 * mm), img(on_img, 52 * mm),
              P("Effet coupé, puis actif : LED bleue, la façade reçoit sa lumière.", "small")]]],
           colWidths=[90 * mm, W - 90 * mm])
ov.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
f.append(ov); f.append(PageBreak())
f.append(P("4. Les trois modes", "h1"))
mt = Table([[[P("<b>%s</b>" % h, "h2") if False else P("<b>%s</b> : %s" % (h, x)) for h, x in MODES] + [P(REV_TXT[1])],
             [img(modes_img, 58 * mm), P("LED MODE en Delay, Auto Freeze, Layers, puis LED REVERSE allumée.", "small")]]],
           colWidths=[W - 62 * mm, 62 * mm])
mt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0)]))
f.append(mt)
f.append(P("5. Les potards", "h1")); f += [P(x) for x in KNOB_TXT]
f.append(table(CTL, [20 * mm, (W - 20 * mm) / 3, (W - 20 * mm) / 3, (W - 20 * mm) / 3], small=True))
f.append(P("6. Reverse", "h1")); f.append(P(REV_TXT[0]))
f.append(P("7. Footswitch et LEDs", "h1")); f += bullets(FS)
f.append(P("8. Paramètres cachés", "h1"))
f.append(P("Comme en maintenant les boutons de la pédale, chaque potard a une seconde (et troisième, quatrième) fonction. Une couche verrouillée fait clignoter sa LED ; recliquez pour revenir à la couche principale."))
f.append(table(HID, [24 * mm, 50 * mm, W - 74 * mm], small=True)); f.append(Spacer(1, 2 * mm))
f += bullets(HID_DESC, "tip")
f.append(P("9. Fonctions cachées du moteur", "h1")); f += bullets(EXTRAS, "tip")
f.append(P("10. MIDI", "h1")); f += [P(x) for x in MIDI]
f.append(P("11. Fenêtre", "h1")); f.append(P(WIN[0]))
wt = Table([[[P(WIN[1])], [img(bar_img, 64 * mm), P("Barre de presets au repos, ligne d'état pendant un réglage.", "small")]]], colWidths=[W - 68 * mm, 68 * mm])
wt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0)]))
f.append(wt)
f.append(PageBreak())
f.append(P("12. Presets", "h1")); f += [P(x) for x in PRE]
cards = []
for slot in (1, 3, 4, 5, 6, 7, 8, 9):
    p_ = PRESETS[slot]; v = p_["v"]
    name = p_["name"].split(" ", 1)[1] if slot <= 8 else p_["name"]
    label = ("%d · %s" % (slot, name)) if slot <= 8 else ("+ · %s" % name)
    vals = " · ".join(v[kk][1] for kk in ("mode", "time", "size", "overlap", "regen", "pitch", "mix"))
    more = " · ".join(v[kk][1] for kk in ("reverse", "regenMix", "pitchRandom", "reverbMix", "reverbDecay", "cutoff"))
    cell = [P("<b>%s</b>" % label, "cellb"), P(PRE_DESC[slot], "cells"), P(vals, "cells"), P(more, "small")]
    cards.append([img(None, 54 * mm, knobs_img(slot)), cell])
pt_ = Table(cards, colWidths=[58 * mm, W - 58 * mm])
pt_.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                         ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E2DAD0")), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
f.append(pt_)
f.append(CondPageBreak(90 * mm))
f.append(KeepTogether([P("13. Conseils d'utilisation", "h1")] + bullets(TIPS, "tip") +
                      [P("14. Caractéristiques techniques", "h1"), table(TECH, [28 * mm, W - 28 * mm], header=False, small=True)]))

def deco(c, doc):
    c.saveState()
    c.setFillColor(DARK); c.rect(0, A4[1] - 6 * mm, A4[0], 6 * mm, stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 6.8 * mm, A4[0], 0.8 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, "Textural (NINE HANDS | DSP) · v" + VERSION)
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="TEXTURAL - Notice v" + VERSION, author="NINE HANDS | DSP")
# ---- Couverture « minimale » (modele 6) : gabarit fixe commun a toutes les notices (mm depuis le haut, logo / bandeau depuis le bas)
COVER_NAME = "TEXTURAL"
PEDAL_H, PEDAL_MAXW, PEDAL_TOP = 82 * mm, 115 * mm, 84 * mm
LANG_TOP = 18 * mm
NAME_TOP, NAME_PT = 194 * mm, 30
SUB_TOP, SUB_PT = 208 * mm, 10
LOGO_W, LOGO_BOTTOM = 38 * mm, 22 * mm
BAND_H = 3 * mm
def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, 0, A4[0], BAND_H, stroke=0, fill=1)
    def line(text, top, font, size, cs, col):
        w = pdfmetrics.stringWidth(text, font, size) + cs * (len(text) - 1)
        t = c.beginText((A4[0] - w) / 2, A4[1] - top - size * 0.8); t.setFont(font, size); t.setCharSpace(cs)
        t.setFillColor(col); t.textOut(text); c.drawText(t)
    line(COVER["lang"], LANG_TOP, "PopM", 8.5, 0, ACC_L)
    ci = Image.open(cover); iw, ih = ci.size
    cw_ = iw / 1.32; ch_ = (ih - int(cw_ * 0.16)) / 1.2; pad_ = int(cw_ * 0.16)
    kk = min(PEDAL_H / ch_, PEDAL_MAXW / cw_)
    dw, dh = iw * kk, ih * kk
    y0 = A4[1] - (PEDAL_TOP + (PEDAL_H - ch_ * kk) / 2) + pad_ * kk
    c.drawImage(cover, (A4[0] - dw) / 2, y0 - dh, dw, dh)
    line(COVER_NAME, NAME_TOP - NAME_PT * 0.02, "Title", NAME_PT, NAME_PT * 0.5, colors.white)
    line(COVER["sub"], SUB_TOP, "Pop", SUB_PT, 1.5, colors.HexColor("#BDC4B8"))
    lw, lh = Image.open(LOGO_PNG).size
    c.drawImage(LOGO_PNG, (A4[0] - LOGO_W) / 2, LOGO_BOTTOM, LOGO_W, LOGO_W * lh / lw, mask="auto")
    c.restoreState()
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
doc.build(f)
print(OUT)
