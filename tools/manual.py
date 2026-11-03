# Textural (Studio Wiga) - notice PDF bilingue (partie anglaise complete, puis partie francaise complete).
# Usage : python3 tools/manual.py [fichier PDF de sortie]   (defaut : docs/Textural_Manual_EN-FR_v<VERSION>.pdf)
# Illustrations : tools/manual_assets/ (rendus reels du plugin repris de la notice 1.2.0). Les deux captures de menus
# clic droit de la 1.2.0 (ancien menu de taille, CC d'usine, « Reset MIDI to defaults ») ont ete retirees : a refaire
# avec un rendu du plugin si un outil de capture est ajoute au depot.
# Polices : assets/fonts (Poppins, DejaVu Sans pour les fleches). Pas d'historique des versions dans la notice.
import re as _re, os as _os
VERSION = _re.search(r"project\(\w+ VERSION ([0-9.]+)", open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "CMakeLists.txt")).read()).group(1)   # version du plugin
NAME = "Textural"
TITLE = "TEXTURAL"
FOOTER = {"en": "Textural (Studio Wiga) · User manual · v" + VERSION, "fr": "Textural (Studio Wiga) · Notice d'utilisation · v" + VERSION}
from reportlab.lib import colors
ACC = colors.HexColor("#E0620C")
H1COL = ACC; H2COL = colors.HexColor("#1B1D22")
HCELLBG = colors.HexColor("#F4F1EC"); HCELLTXT = colors.HexColor("#1B1D22")
# ---------- mise en page commune (style maison Studio Wiga) ----------
import os, sys
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, CondPageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "tools", "manual_assets")
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", NAME + "_Manual_EN-FR_v" + VERSION + ".pdf")

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("Dej", "DejaVuSans")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))
addMapping("PopL", 0, 0, "PopL"); addMapping("PopL", 1, 0, "PopM"); addMapping("PopL", 0, 1, "PopL"); addMapping("PopL", 1, 1, "PopM")
addMapping("Pop", 0, 0, "Pop"); addMapping("Pop", 1, 0, "PopB"); addMapping("Pop", 0, 1, "Pop"); addMapping("Pop", 1, 1, "PopB")

DARK = colors.HexColor("#1B1D22"); GREY = colors.HexColor("#6B6F78"); LIGHT = colors.HexColor("#F4F1EC"); RULE = colors.HexColor("#DDD8D0")
SYMBOLS = "★✎◄►↔→⇄"   # absents de Poppins : DejaVu Sans

def sym(t):
    for c in SYMBOLS: t = t.replace(c, '<font name="Dej">' + c + '</font>')
    return t

st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=17, leading=21, textColor=H1COL, spaceAfter=6, spaceBefore=8, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=11.5, leading=15, textColor=H2COL, spaceAfter=3, spaceBefore=7, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="PopL", fontSize=9, leading=13, textColor=DARK, spaceAfter=4),
    "li": ParagraphStyle("li", fontName="PopL", fontSize=9, leading=13, textColor=DARK, spaceAfter=2, leftIndent=9, bulletIndent=0),
    "note": ParagraphStyle("note", fontName="PopL", fontSize=8.4, leading=12, textColor=DARK, backColor=LIGHT, borderPadding=5, spaceBefore=4, spaceAfter=8),
    "small": ParagraphStyle("small", fontName="PopL", fontSize=7.6, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="PopL", fontSize=7.9, leading=10.2, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=7.9, leading=10.2, textColor=DARK),
    "hcell": ParagraphStyle("hcell", fontName="PopM", fontSize=7.9, leading=10.2, textColor=HCELLTXT),
    "cover": ParagraphStyle("cover", fontName="PopM", fontSize=30, leading=36, textColor=colors.white, alignment=TA_CENTER),
    "coversub": ParagraphStyle("coversub", fontName="PopL", fontSize=10, leading=14, textColor=colors.HexColor("#B9B9B9"), alignment=TA_CENTER),
    "coverver": ParagraphStyle("coverver", fontName="PopL", fontSize=10, leading=14, textColor=colors.HexColor("#DADADA"), alignment=TA_CENTER),
    "coverlang": ParagraphStyle("coverlang", fontName="PopM", fontSize=7.5, leading=10, textColor=ACC),
}
def P(t, s="p"): return Paragraph(sym(t), st[s])
def bullets(items): return [Paragraph(sym(i), st["li"], bulletText="•") for i in items]
def table(rows, widths, header=True, first_bold=False):
    data = []
    for r, row in enumerate(rows):
        data.append([P(c, "hcell" if (header and r == 0) else ("cellb" if (first_bold and k == 0) else "cell")) for k, c in enumerate(row)])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
             ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
             ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), HCELLBG), ("LINEBELOW", (0, 0), (-1, 0), 0.9, ACC)]
    t.setStyle(TableStyle(style)); return t
def img(name, width=None, height=None):
    path = name if os.path.isabs(name) else os.path.join(ASSETS, name)
    im = Image.open(path)
    if width is None: width = height * im.width / im.height
    if height is None: height = width * im.height / im.width
    return RLImage(path, width=width, height=height)
def side(left, right, wl):
    t = Table([[left, right]], colWidths=[wl, W - wl])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (-1, 0), (-1, 0), 0),
                           ("LEFTPADDING", (1, 0), (1, 0), 10)]))
    return t

W = A4[0] - 36 * mm
def cover(t, cover_img, cover_w):
    return [Spacer(1, 2 * mm), P(t["lang"], "coverlang"), Spacer(1, 6 * mm), img(cover_img, cover_w), Spacer(1, 4 * mm),
            P(" ".join(TITLE), "cover"), Spacer(1, 2 * mm), P(t["sub"], "coversub"), Spacer(1, 1 * mm), P(t["ver"], "coverver"),
            Spacer(1, 7 * mm), img("logo_white.png", 46 * mm), NextPageTemplate("p"), PageBreak()]

def build(sections, title):
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=17 * mm, bottomMargin=18 * mm,
                          title=title, author="Studio Wiga")
    lang = {"v": "en"}
    def deco(c, d):
        c.saveState()
        c.setFillColor(ACC); c.rect(0, A4[1] - 2.2 * mm, A4[0], 2.2 * mm, stroke=0, fill=1)
        c.setFont("PopL", 7); c.setFillColor(GREY)
        c.drawString(18 * mm, 10 * mm, FOOTER[lang["v"]])
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(d.page))
        c.restoreState()
    def cover_bg(c, d):
        c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        c.setFillColor(ACC); c.rect(0, A4[1] - 2.2 * mm, A4[0], 2.2 * mm, stroke=0, fill=1); c.restoreState()
    class SetLang(Spacer):
        def __init__(self, l): Spacer.__init__(self, 0, 0); self.l = l
        def draw(self): lang["v"] = self.l
    fr = lambda: Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[fr()], onPage=cover_bg), PageTemplate(id="p", frames=[fr()], onPage=deco)])
    story = []
    for i, (l, flow) in enumerate(sections):
        if i: story += [NextPageTemplate("cover"), PageBreak()]
        story += [SetLang(l)] + flow
    doc.build(story)
    print(OUT)
# ---------- contenu de la notice Textural (vérifié contre PluginEditor.cpp / PluginProcessor.cpp / Parameters.h / README) ----------
PRESETS = [  # #, nom, mode, TIME, SIZE, OVERLAP, REGEN, PITCH, MIX (valeurs de la notice 1.2.0, presets d'usine inchangés depuis)
    ("1", "Sea Synth", "Layers", "Attack 40 ms", "102 ms", "21", "Decay 9.59 s", "0.0 st", "58 %"),
    ("2", "Live", "—", "", "", "", "", "", ""),
    ("3", "Crystal Cave", "Delay", "380 ms", "291 ms", "5", "72 %", "+12.0 st", "50 %"),
    ("4", "Melodic Kaleidoscope", "Auto Freeze", "457 ms", "244 ms", "11", "20 %", "0.0 st", "50 %"),
    ("5", "Obligatory Shimmer", "Delay", "182 ms", "698 ms", "18", "78 %", "+12.0 st", "45 %"),
    ("6", "Reverse Reverb", "Delay", "50 ms", "925 ms", "1", "20 %", "0.0 st", "72 %"),
    ("7", "Mellow Cello", "Auto Freeze", "316 ms", "413 ms", "15", "15 %", "-12.0 st", "74 %"),
    ("8", "Stardust Cloud", "Layers", "Attack 112 ms", "113 ms", "21", "Decay 13.50 s", "0.0 st", "86 %"),
    ("9", "Slow Attack Soundtrack", "Layers", "Attack 587 ms", "203 ms", "18", "Decay 17.76 s", "-7.0 st", "38 %")]

def dec(v, lang):  # virgule décimale en français
    import re as _r
    return _r.sub(r"(\d)\.(\d)", r"\1,\2", v) if lang == "fr" else v

T = {
"en": dict(
 lang="ENGLISH", sub="Granular synth engine &nbsp;·&nbsp; VST3 &nbsp;·&nbsp; Windows &amp; macOS", ver="User manual &nbsp;·&nbsp; version " + VERSION,
 p_t="1. Presentation",
 p=["<b>Textural</b> records what you play and rebuilds it from tiny slices of sound called grains. The result can be shimmering pads, cascading octaves, glitchy rhythms, warm polyphonic synth voices or your guitar played backwards, all inside a single VST3 pedal.",
    "It is inspired by the <b>MXR Textures M310</b> granular synth engine pedal and reworked for the studio: three capture modes (Delay, Auto Freeze, Layers), six main knobs, a hidden second layer of parameters, a modulated plate reverb, a resonant LP / HP filter, vibrato, tap tempo, trails, Mono / Wet-Dry / Stereo outputs, eight preset slots and full MIDI control."],
 f_t="Main features",
 f=["Three modes: <b>Delay</b> (green), <b>Auto Freeze</b> (orange), <b>Layers</b> (red, four-voice polyphonic granular synth).",
    "REVERSE: your guitar replayed backwards phrase by phrase, phase-aligned, with no clicks.",
    "Hidden parameters reached with Ctrl / Alt / Ctrl + Alt while dragging, or by latching a layer, like holding buttons on the pedal.",
    "<b>MIDI Learn on every control</b> (right-click on the control); no CC is assigned by default; Program Change 1-9.",
    "8 preset slots (slot 2 = Live) plus Slow Attack Soundtrack; user presets saved in the project.",
    "Plugin size 60 % (default), 75 % or 100 %, with the default size of new windows to choose; never smaller than 60 %."],
 i_t="2. Installation",
 i=[("Windows 11", "Run <b>Textural-Setup.exe</b> (artifact <i>Textural-Setup-Windows</i>): it copies Textural.vst3 to <i>C:\\Program Files\\Common Files\\VST3</i>. Or copy the <b>Textural.vst3</b> folder there yourself (artifact <i>Textural-VST3-Windows</i>)."),
    ("macOS", "Unzip the <i>VST3-macOS</i> artifact and copy <b>Textural.vst3</b> into <i>~/Library/Audio/Plug-Ins/VST3/</i> (universal binary: Intel and Apple Silicon)."),
    ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. The plugin appears as <b>Textural</b> by <b>Studio Wiga</b>."),
    ("First launch", "The pedal opens on preset 1 · Sea Synth. Drag a knob up or down to turn it: Shift = fine, double-click = default value, mouse wheel works too. While you turn a knob, its real value appears under the Textural logo, in the knob's colour.")],
 o_t="3. Interface overview",
 o=[["#", "Element", "Role"],
    ["1", "REVERSE", "Reverse on / off (blue LED). Long press: latches the REVERSE hidden layer."],
    ["2", "MODE", "Delay → Auto Freeze → Layers. The LED takes the colour of the mode symbol and flashes while frozen. Long press: latches the MODE layer. Ctrl-click: tap tempo."],
    ["3", "TIME", "Delay time (Delay, Auto Freeze) or attack of each layer (Layers)."],
    ["4", "SIZE", "Length of each grain."],
    ["5", "OVERLAP", "Number of grains playing together, 1 to 30."],
    ["6", "REGEN", "Feedback (Delay, Auto Freeze) or decay of each layer (Layers)."],
    ["7", "PITCH", "Pitch of the grains, two octaves down to two octaves up (centre detent)."],
    ["8", "MIX", "Dry to fully granular; above 75 %, particles fade in."],
    ["9", "Status LED", "Lit when the effect is on; soft-flashes in preset-scroll mode. Click: latches the footswitch layer."],
    ["10", "Footswitch", "Click: effect on / off. Hold: freeze (un-freeze in Auto Freeze), or preset scroll."],
    ["11", "Status line", "Shows only the setting you are turning, the mode, the preset loaded, and MIDI Learn messages."],
    ["12", "Preset LEDs", "Slots 1-4 green, 5-8 red; flashes when the preset is edited."],
    ["13", "PRESETS", "Steps through slots 1 → 8. Hold 2 s to copy and save."]],
 o_note="Right-click a control for its MIDI Learn; right-click elsewhere for the menu (Plugin size, presets, MIDI).",
 m_t="4. Modes and controls",
 gs_t="How granular synthesis works",
 gs=["Like a delay, Textural writes your audio into a buffer. Instead of playing it back in one piece, it plays it as grains: short snippets, each with a position in the recording, a size and a smooth fade-in and fade-out. Small grains give sputtery blips, large grains whole musical phrases. When grains overlap, several snippets play at once and blend into a dense texture. Playing grains faster or slower shifts their pitch, reading them backwards reverses them.",
     "The grains can be fed back into the buffer (granular feedback: cascading pitch shifts and shimmer) and the delayed signal can be fed back on its own (delay feedback). REGEN sets the total amount and REGEN MIX the balance. The mix happens before the reverb, then the 4-pole LP / HP filter."],
 modes=[("Delay (green)", "Your playing is recorded all the time and played back as grains, TIME behind the newest audio: clean repeats, smeared trails and pitch-shifted echoes. TIME 50 ms – 2 s, SIZE 60 ms – 2 s, REGEN = feedback. Footswitch hold freezes the buffer."),
        ("Auto Freeze (orange)", "Textural listens for each note or chord, records it for TIME, freezes the buffer and keeps the sound alive as an evolving wash of grains. A new note replaces the old one. Footswitch hold un-freezes."),
        ("Layers (red)", "Up to four notes or chords in four separate buffers; a fifth replaces the oldest. Each layer has its own fade-in (TIME, 5 ms – 5 s) and fade-out (REGEN, 0.1 s – infinite), like the voice of a polyphonic synthesizer. Raise REGEN to hold the notes. Footswitch hold freezes the layers.")],
 kt=[["Knob", "Delay", "Auto Freeze", "Layers"],
     ["TIME", "Delay of each grain · 50 ms – 2 s", "Delay + length of the recording", "Attack of each layer · 5 ms – 5 s"],
     ["SIZE", "Grain length · 60 ms – 2 s", "Grain length · 60 ms – 2 s", "Grain length · 60 – 500 ms"],
     ["OVERLAP", "1 – 30 grains at once", "1 – 30 grains at once", "1 – 30 grains per layer"],
     ["REGEN", "Feedback · 0 – 98 %", "Feedback (none while frozen)", "Decay · 0.1 s – ∞"],
     ["PITCH", "−24 … +24 semitones, centre detent", "same", "same"],
     ["MIX", "Dry → fully granular, particles above 75 %", "same", "same"]],
 kt_note="For a predictable delay or freeze, start with SIZE fully down and turn it up to taste. Large grains look further back into older audio: the \"time travelling\" effect.",
 rev_t="REVERSE",
 rev="In Delay and Auto Freeze, REVERSE replays your guitar backwards, slice by slice, like a reverse delay. SIZE sets the slice length (0.25 to 2 s), TIME the wait, and Reverse Random the blend between backwards guitar and forward grains (10 to 100 %). Slices cross-fade over 20 %, phase-aligned: continuous, no clicks. In Layers, REVERSE flips the grains inside each voice.",
 fs_t="5. Footswitch, LEDs and presets",
 fs=[["Action", "Effect"],
     ["Click footswitch", "Effect on / off. Without Trails, the effect fades out and its buffer is cleared."],
     ["Hold footswitch", "Freeze in Delay and Layers; in Auto Freeze, holding un-freezes so new audio can come in."],
     ["Preset scroll", "With Footswitch Hold Mode = Preset Scroll: hold to enter, click = next preset, hold again to leave."],
     ["Click PRESETS", "Live → 1 … 8 → Live. LEDs green for 1-4, red for 5-8, flashing when edited."],
     ["Hold PRESETS 2 s", "Copies the settings (LEDs flash fast); click to choose the slot (1, 3-8); hold 2 s again to save. Editing anything cancels the copy."]],
 led=[["LED", "Meaning"],
      ["REVERSE", "Blue when reverse is on."],
      ["MODE", "Green, orange or red, the colour of the mode symbol. Flashes when frozen, bright green while its hidden layer is in use."],
      ["Status", "Blue when the effect is on. Soft-flashes during preset scroll."],
      ["Presets", "Green for 1-4, red for 5-8. Flashes when edited, fast while copying."]],
 hid_t="Hidden parameters",
 hid="On the hardware you hold REVERSE, MODE or the footswitch and turn a knob. In the plug-in, use a modifier key while dragging a knob, or latch a layer (long press on REVERSE or MODE, click on the blue LED) to use the mouse alone. Right-clicking a knob learns the parameter of the active layer.",
 ht=[["Knob", "Ctrl (REVERSE layer)", "Alt (MODE layer)", "Ctrl + Alt (footswitch layer)"],
     ["TIME", "Time Random", "Reverb Mix", "Preset Scroll Mute"],
     ["SIZE", "Size Random", "Filter Cutoff (LP &lt; noon &lt; HP)", "—"],
     ["OVERLAP", "Overlap Random", "Vibrato Rate", "Trails"],
     ["REGEN", "Regen Mix (Delay ↔ Granular)", "Reverb Decay (0.4 s – 60 s, then ∞)", "Output Mode (Mono / Wet-Dry / Stereo)"],
     ["PITCH", "Pitch Random", "Quantize Pitch", "Footswitch Hold Mode (Preset Scroll / Freeze)"],
     ["MIX", "Reverse Random", "Vibrato Depth", "Output Gain (−12 to +12 dB)"]],
 hb=["<b>Time Random</b> above 45 % adds glitch stutters. <b>Size / Overlap Random</b> break up the ringing of tiny regular grains.",
     "<b>Pitch Random</b>: the first third adds unison detune (up to ±30 cents), beyond that grains jump to octaves, fifths and fourths.",
     "<b>Filter</b>: low-pass below noon, flat at noon, high-pass above, resonance rising towards the ends. <b>Quantize</b> locks PITCH to fourths, fifths and octaves.",
     "<b>Tap tempo</b>: Ctrl-click MODE (or latch REVERSE and click MODE) at least twice; delay time and grain spacing lock to the tempo (shown as BPM). Turning OVERLAP gives spacing back to the knob."],
 midi_t="6. MIDI",
 midi="Send MIDI to the Textural track (any channel; in Reaper arm the track with your MIDI input and monitoring on). <b>No CC is assigned by default</b>: every control is assigned with <b>MIDI Learn</b>. Every parameter can also be automated from the DAW.",
 ml_t="MIDI Learn",
 ml=["<b>Right-click a control</b> (a knob in the active layer: normal, Ctrl, Alt or Ctrl + Alt; REVERSE, MODE, the footswitch or PRESETS): the menu starts with <b>MIDI Learn: &lt;control&gt; (CC n / none)</b>. Choose it, then move an expression pedal or press a MIDI button: the first CC received is assigned. The learning message itself does not change the sound.",
     "The status line shows <b>MIDI LEARN: move a control for &lt;control&gt;</b>, then <b>&lt;control&gt; = CC n</b> for 2 seconds.",
     "<b>Clear MIDI: &lt;control&gt;</b> removes the assignment; <b>Cancel MIDI learn</b> (or choosing the same MIDI Learn again) stops waiting.",
     "A CC number drives only one control: learning a CC already used elsewhere removes it from the other control.",
     "Right-click elsewhere &gt; <b>MIDI</b>: <b>Learn: &lt;control&gt; (CC n / none)</b> for all 29 functions, including <b>Freeze</b> and <b>Tap Tempo</b> which have no knob, <b>Cancel MIDI learn</b> and <b>Clear all MIDI assignments</b>.",
     "Assignments are <b>saved with your project</b>. A project from an earlier version that still used the old factory CC map opens with no assignment; a project in which you had changed an assignment keeps its assignments."],
 lt=[["Control", "Type"],
     ["Time, Size, Overlap, Regen, Pitch, Mix", "Continuous 0-127"],
     ["Time Random, Size Random, Overlap Random, Regen Mix, Pitch Random, Reverse Random", "Continuous 0-127"],
     ["Reverb Mix, Reverb Decay, Filter", "Continuous 0-127"],
     ["Quantize", "Switch: 64 and above = on"],
     ["Vibrato Rate, Vibrato Depth", "Continuous 0-127"],
     ["Freeze", "Switch: 64 and above = frozen (hold), below 64 = released"],
     ["Reverse", "Switch: 64 and above = on"],
     ["Mode", "Selector, 3 positions: 0-42 Delay, 43-85 Auto Freeze, 86-127 Layers"],
     ["Bypass (footswitch)", "Footswitch, latching: 64 and above = effect on, below 64 = off"],
     ["Tap Tempo", "Momentary: each value of 64 or more is a tap"],
     ["Next Preset", "Momentary: each value of 64 or more = next preset"],
     ["Output Gain", "Continuous 0-127 (−12 to +12 dB)"],
     ["Output Mode", "Selector, 3 positions: Mono, Wet/Dry, Stereo"],
     ["Trails", "Switch: 64 and above = on"],
     ["Footswitch Hold Mode", "Selector, 2 positions: 0-63 Preset Scroll, 64-127 Freeze"],
     ["Preset Scroll Mute", "Switch: 64 and above = on"],
     ["Presets (Program Change 1-9, no learning needed)", "1-8 = slots (2 and 0 = Live), 9 = Slow Attack Soundtrack (fixed)"]],
 st_cap="Status line during MIDI Learn: waiting, then confirmation.",
 w_t="7. Window and status line",
 w=["Right-click (outside a control) &gt; <b>Plugin size</b>: <b>60 %</b>, <b>75 %</b> or <b>100 %</b> (the current size is ticked); <i>(default)</i> is shown next to the default size. You can also drag the corner (proportions kept). The window can never be made smaller than 60 %.",
    "<b>Plugin size &gt; Default size (new windows)</b> chooses the size at which every new Textural window opens (60 % at first). This setting is common to all instances and saved on your computer (<i>settings.xml</i> in the Studio Wiga\\Textural folder of your user data: %APPDATA% on Windows, ~/Library on macOS); the open window takes that size at once.",
    "Each instance also remembers its own size in the project (the size its window had when the project was saved), and this size takes priority over the default size when the project is reopened. A new instance opens at the default size.",
    "The <b>status line</b> under the Textural logo shows nothing until you act: only the setting you are turning (in the knob's colour), the mode, the preset you load, a MIDI-controlled setting, and the MIDI Learn messages. It fades out after about 1.5 s."],
 mt=[["Menu item", "Use"],
     ["MIDI Learn / Clear MIDI", "At the top when you right-click a control."],
     ["Plugin size", "60 % / 75 % / 100 % with (default) next to the default size, then Default size (new windows)."],
     ["Save current settings to preset", "Stores the current sound in slot 1 or 3-8."],
     ["Reset current preset to factory", "Restores the slot you are on."],
     ["Reset all presets to factory", "Restores all slots."],
     ["Load preset: Slow Attack Soundtrack", "The extra preset."],
     ["MIDI", "Learn for every function, Cancel MIDI learn, Clear all MIDI assignments."]],
 pr_t="8. Presets",
 pr=["Textural opens on preset 1. The PRESETS button steps through 1 → 2 → … → 8 → 1. Slot 2 is <b>Live</b>: your own current settings, remembered while you visit the other presets; it cannot be overwritten. Slow Attack Soundtrack is the 9th preset (DAW preset list, right-click menu or Program Change 9).",
     "Your presets are stored in the DAW project and in <i>%APPDATA%\\Studio Wiga\\Textural\\UserPresets_v4.xml</i> (macOS: <i>~/Library/Studio Wiga/Textural/UserPresets_v4.xml</i>)."],
 pr_hdr=["#", "Preset", "Mode", "TIME", "SIZE", "OVERLAP", "REGEN", "PITCH", "MIX"],
 pd=[("1. Sea Synth", "Warbly polyphonic granular synth: four detuned voices, soft swell, slow vibrato, warm low-pass. Play chords and let them ring; each new chord becomes a voice."),
     ("2. Live", "Your current knob, button and hidden settings, kept as you left them."),
     ("3. Crystal Cave", "Regenerative octave loops: each repeat climbs an octave and falls away into a bright cave of reflections. Single notes and slow arpeggios."),
     ("4. Melodic Kaleidoscope", "Melodies frozen and replayed forward, reversed and at other octaves. Play a short phrase and let it bloom."),
     ("5. Obligatory Shimmer", "Granular shimmering reverb: octave-up grains blend into a long plate (Regen Mix 83 / 17 delay / granular). Long notes and open chords."),
     ("6. Reverse Reverb", "Your guitar backwards, phrase by phrase (about 0.9 s), then into a wide reverb. Play slowly; SIZE sets the phrase length."),
     ("7. Mellow Cello", "Sub-octave pad with cello-like vibrato, swelling up after each note. Single notes in the middle register."),
     ("8. Stardust Cloud", "Layers granular synth showered with sparkling particles, reversed glints and octave dust. Arpeggios and harmonics."),
     ("9. Slow Attack Soundtrack", "Slowly evolving pad a fifth below with a long swell and decay. Volume-swell playing, ambient film cues.")],
 tp_t="9. Tips",
 tp=["<b>Reaper chain</b>: guitar track &gt; tuner &gt; drive &gt; amp sim &gt; <b>Textural</b> &gt; mixer. Like the hardware, Textural sounds best after the amp (as a delay / reverb / pad source); before the amp sim, set Output Mode to Mono.",
     "<b>Low-tuned 7-string</b>: with low B riffs, keep PITCH at 0 or +12 (−12 and −24 turn to mud), use a high-pass Filter (Alt + SIZE above noon) and keep MIX moderate so the riff stays tight; Mellow Cello and Sea Synth shine on clean parts.",
     "<b>Ringing tones</b>: very small grains with high overlap and no randomness ring like a ring modulator; add a little Size or Overlap Random.",
     "<b>Pads from chords</b>: in Layers, set REGEN past 3 o'clock, strum four chords and you have a four-voice pad.",
     "<b>Reverb on dry only</b>: MIX fully down and Reverb Mix up gives a plain reverb on your dry signal.",
     "<b>With a Chocolate Plus</b>: learn Freeze on a button (hold), Next Preset on another, and MIX or PITCH on an expression pedal."],
 ts_t="Troubleshooting",
 ts=[["Problem", "Solution"],
     ["No sound change when I turn a knob", "Check the status LED (effect on) and MIX."],
     ["The sound stops when I bypass", "Turn Trails on (Ctrl + Alt + OVERLAP) to let it ring."],
     ["MIDI does nothing", "No CC is assigned by default: right-click the control &gt; MIDI Learn. Check that the track receives MIDI."],
     ["A knob reacts to the wrong pedal", "Right-click the control &gt; Clear MIDI, or MIDI &gt; Clear all MIDI assignments."],
     ["The window is too small", "Right-click &gt; Plugin size &gt; 75 % or 100 %, or drag the corner; Default size (new windows) makes every new window open at that size."]],
 sp_t="10. Specifications",
 sp=[["Format", "VST3 · Windows 11 (x64) · macOS universal (Intel and Apple Silicon)"], ["Channels", "Stereo in / out, mono in"],
     ["Buffer", "12 s granular buffer, 4 × 2.6 s layer buffers"], ["Grains", "Up to 160 simultaneous grains, 4-point Hermite interpolation"],
     ["Reverb", "Modulated Dattorro plate, 0.4 s – 60 s, infinite"], ["Filter", "4-pole dual LP / HP with resonance"], ["Latency", "0 samples"],
     ["MIDI", "MIDI Learn on 29 functions (no CC assigned by default), saved with the project; Program Change 1-9; any channel"],
     ["Window", "Plugin size 60 % / 75 % / 100 %, default size of new windows to choose (60 % at first), never smaller than 60 %; resizable by the corner"],
     ["Stability", "Windows anti-freeze v2: the interface never blocks the host"], ["Version", VERSION]],
 sp_note="Inspired by the MXR Textures M310. MXR and Textures are trademarks of their owners; Textural is an independent personal project by Studio Wiga."),
"fr": dict(
 lang="FRANÇAIS", sub="Moteur de synthèse granulaire &nbsp;·&nbsp; VST3 &nbsp;·&nbsp; Windows &amp; macOS", ver="Notice d'utilisation &nbsp;·&nbsp; version " + VERSION,
 p_t="1. Présentation",
 p=["<b>Textural</b> enregistre ce que tu joues et le reconstruit à partir de minuscules tranches de son, les grains. On peut en tirer des nappes scintillantes, des cascades d'octaves, des rythmes glitchés, des voix de synthé polyphoniques ou ta guitare jouée à l'envers, le tout dans une seule pédale VST3.",
    "Il s'inspire de la pédale <b>MXR Textures M310</b> (Granular Synth Engine), retravaillée pour le studio : trois modes de capture (Delay, Auto Freeze, Layers), six potards principaux, une seconde couche de paramètres cachés, une reverb plate modulée, un filtre LP / HP résonant, un vibrato, le tap tempo, les trails, des sorties Mono / Wet-Dry / Stéréo, huit emplacements de presets et un contrôle MIDI complet."],
 f_t="Points forts",
 f=["Trois modes : <b>Delay</b> (vert), <b>Auto Freeze</b> (orange), <b>Layers</b> (rouge, synthé granulaire polyphonique à quatre voix).",
    "REVERSE : ta guitare rejouée à l'envers, phrase par phrase, alignée en phase, sans clic.",
    "Paramètres cachés accessibles avec Ctrl / Alt / Ctrl + Alt en glissant, ou en verrouillant une couche, comme en maintenant les boutons de la pédale.",
    "<b>MIDI Learn sur toutes les commandes</b> (clic droit sur la commande) ; aucun CC assigné par défaut ; Program Change 1-9.",
    "8 emplacements de presets (le 2 = Live) plus Slow Attack Soundtrack ; presets utilisateur enregistrés dans le projet.",
    "Plugin size 60 % (par défaut), 75 % ou 100 %, avec la taille par défaut des nouvelles fenêtres au choix ; jamais plus petite que 60 %."],
 i_t="2. Installation",
 i=[("Windows 11", "Lance <b>Textural-Setup.exe</b> (artefact <i>Textural-Setup-Windows</i>) : il copie Textural.vst3 dans <i>C:\\Program Files\\Common Files\\VST3</i>. Ou copie toi-même le dossier <b>Textural.vst3</b> (artefact <i>Textural-VST3-Windows</i>)."),
    ("macOS", "Dézippe l'artefact <i>VST3-macOS</i> et copie <b>Textural.vst3</b> dans <i>~/Library/Audio/Plug-Ins/VST3/</i> (binaire universel : Intel et Apple Silicon)."),
    ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Le plugin apparaît sous le nom <b>Textural</b>, fabricant <b>Studio Wiga</b>."),
    ("Premier lancement", "La pédale s'ouvre sur le preset 1 · Sea Synth. Glisse un potard vers le haut ou le bas : Maj = réglage fin, double-clic = valeur par défaut, la molette marche aussi. Pendant que tu tournes un potard, sa valeur réelle s'affiche sous le logo Textural, dans la couleur du potard.")],
 o_t="3. Vue d'ensemble de l'interface",
 o=[["#", "Élément", "Rôle"],
    ["1", "REVERSE", "Reverse actif / coupé (LED bleue). Appui long : verrouille la couche cachée REVERSE."],
    ["2", "MODE", "Delay → Auto Freeze → Layers. La LED prend la couleur du symbole du mode et clignote quand le son est gelé. Appui long : verrouille la couche MODE. Ctrl + clic : tap tempo."],
    ["3", "TIME", "Retard (Delay, Auto Freeze) ou attaque de chaque couche (Layers)."],
    ["4", "SIZE", "Longueur de chaque grain."],
    ["5", "OVERLAP", "Nombre de grains joués ensemble, de 1 à 30."],
    ["6", "REGEN", "Réinjection (Delay, Auto Freeze) ou déclin de chaque couche (Layers)."],
    ["7", "PITCH", "Hauteur des grains, de deux octaves en dessous à deux octaves au-dessus (cran central)."],
    ["8", "MIX", "Du direct au tout granulaire ; au-delà de 75 %, des particules apparaissent."],
    ["9", "LED d'état", "Allumée quand l'effet est actif ; clignote doucement en mode défilement de presets. Clic : verrouille la couche footswitch."],
    ["10", "Footswitch", "Clic : effet actif / coupé. Maintien : gel (dégel en Auto Freeze), ou défilement de presets."],
    ["11", "Ligne d'état", "N'affiche que le réglage en cours, le mode, le preset chargé et les messages du MIDI Learn."],
    ["12", "LED de presets", "Emplacements 1-4 en vert, 5-8 en rouge ; clignote quand le preset est modifié."],
    ["13", "PRESETS", "Fait défiler 1 → 8. Maintien 2 s : copie et sauvegarde."]],
 o_note="Clic droit sur une commande : son MIDI Learn ; clic droit ailleurs : le menu (Plugin size, presets, MIDI).",
 m_t="4. Modes et commandes",
 gs_t="Comment fonctionne la synthèse granulaire",
 gs=["Comme un delay, Textural écrit ton son dans une mémoire tampon. Au lieu de le relire d'un bloc, il le rejoue en grains : de courts extraits, chacun avec une position dans l'enregistrement, une taille et un fondu d'entrée et de sortie. Des petits grains donnent des crépitements, des grands des phrases musicales entières. Quand les grains se chevauchent, plusieurs extraits jouent ensemble et se fondent en une texture dense. Relire plus vite ou plus lentement change la hauteur, relire à l'envers inverse le son.",
     "Les grains peuvent être réinjectés dans la mémoire (réinjection granulaire : cascades de hauteurs, shimmer) et le signal retardé peut l'être seul (réinjection delay). REGEN règle la quantité totale et REGEN MIX l'équilibre. Le mélange se fait avant la reverb, puis vient le filtre LP / HP 4 pôles."],
 modes=[("Delay (vert)", "Ton jeu est enregistré en continu et rejoué en grains, TIME derrière le son le plus récent : répétitions nettes, traînées floues et échos transposés. TIME 50 ms – 2 s, SIZE 60 ms – 2 s, REGEN = réinjection. Le maintien du footswitch gèle la mémoire."),
        ("Auto Freeze (orange)", "Textural guette chaque note ou accord, l'enregistre pendant TIME, gèle la mémoire et fait vivre le son en une nappe de grains qui évolue. Une nouvelle note remplace la précédente. Le maintien du footswitch dégèle."),
        ("Layers (rouge)", "Jusqu'à quatre notes ou accords dans quatre mémoires séparées ; la cinquième remplace la plus ancienne. Chaque couche a son fondu d'entrée (TIME, 5 ms – 5 s) et de sortie (REGEN, 0,1 s – infini), comme une voix de synthé polyphonique. Monte REGEN pour tenir les notes. Le maintien du footswitch gèle les couches.")],
 kt=[["Potard", "Delay", "Auto Freeze", "Layers"],
     ["TIME", "Retard de chaque grain · 50 ms – 2 s", "Retard + durée de l'enregistrement", "Attaque de chaque couche · 5 ms – 5 s"],
     ["SIZE", "Longueur de grain · 60 ms – 2 s", "Longueur de grain · 60 ms – 2 s", "Longueur de grain · 60 – 500 ms"],
     ["OVERLAP", "1 – 30 grains ensemble", "1 – 30 grains ensemble", "1 – 30 grains par couche"],
     ["REGEN", "Réinjection · 0 – 98 %", "Réinjection (aucune une fois gelé)", "Déclin · 0,1 s – ∞"],
     ["PITCH", "−24 … +24 demi-tons, cran central", "idem", "idem"],
     ["MIX", "Direct → tout granulaire, particules au-delà de 75 %", "idem", "idem"]],
 kt_note="Pour un delay ou un gel prévisible, pars de SIZE au minimum et monte à ton goût. Les grands grains vont chercher plus loin dans le son ancien : l'effet « voyage dans le temps ».",
 rev_t="REVERSE",
 rev="En Delay et Auto Freeze, REVERSE rejoue ta guitare à l'envers, tranche par tranche, comme un reverse delay. SIZE règle la longueur des tranches (0,25 à 2 s), TIME l'attente, et Reverse Random le dosage entre guitare inversée et grains à l'endroit (10 à 100 %). Les tranches s'enchaînent avec un fondu de 20 % aligné en phase : continu, sans clic. En Layers, REVERSE inverse les grains de chaque voix.",
 fs_t="5. Footswitch, LED et presets",
 fs=[["Action", "Effet"],
     ["Clic sur le footswitch", "Effet actif / coupé. Sans Trails, l'effet s'éteint en fondu et sa mémoire est vidée."],
     ["Maintien du footswitch", "Gel en Delay et Layers ; en Auto Freeze, le maintien dégèle pour laisser entrer du son neuf."],
     ["Défilement de presets", "Avec Footswitch Hold Mode = Preset Scroll : maintien pour entrer, clic = preset suivant, nouveau maintien pour sortir."],
     ["Clic sur PRESETS", "Live → 1 … 8 → Live. LED vertes pour 1-4, rouges pour 5-8, clignotantes si modifié."],
     ["Maintien PRESETS 2 s", "Copie les réglages (LED qui clignotent vite) ; clique pour choisir l'emplacement (1, 3-8) ; nouveau maintien 2 s pour sauvegarder. Toute modification annule la copie."]],
 led=[["LED", "Signification"],
      ["REVERSE", "Bleue quand le reverse est actif."],
      ["MODE", "Verte, orange ou rouge, couleur du symbole du mode. Clignote quand le son est gelé, vert vif quand sa couche cachée est utilisée."],
      ["État", "Bleue quand l'effet est actif. Clignote doucement pendant le défilement de presets."],
      ["Presets", "Vertes pour 1-4, rouges pour 5-8. Clignotent si modifié, vite pendant la copie."]],
 hid_t="Paramètres cachés",
 hid="Sur la pédale, on maintient REVERSE, MODE ou le footswitch en tournant un potard. Dans le plugin, utilise une touche en glissant un potard, ou verrouille une couche (appui long sur REVERSE ou MODE, clic sur la LED bleue) pour n'utiliser que la souris. Le clic droit sur un potard apprend le paramètre de la couche active.",
 ht=[["Potard", "Ctrl (couche REVERSE)", "Alt (couche MODE)", "Ctrl + Alt (couche footswitch)"],
     ["TIME", "Time Random", "Reverb Mix", "Preset Scroll Mute"],
     ["SIZE", "Size Random", "Filter Cutoff (LP &lt; midi &lt; HP)", "—"],
     ["OVERLAP", "Overlap Random", "Vibrato Rate", "Trails"],
     ["REGEN", "Regen Mix (Delay ↔ Granulaire)", "Reverb Decay (0,4 s – 60 s, puis ∞)", "Output Mode (Mono / Wet-Dry / Stéréo)"],
     ["PITCH", "Pitch Random", "Quantize Pitch", "Footswitch Hold Mode (Preset Scroll / Freeze)"],
     ["MIX", "Reverse Random", "Vibrato Depth", "Output Gain (−12 à +12 dB)"]],
 hb=["<b>Time Random</b> au-delà de 45 % ajoute des bégaiements glitch. <b>Size / Overlap Random</b> cassent la résonance des petits grains réguliers.",
     "<b>Pitch Random</b> : le premier tiers ajoute un désaccord unisson (jusqu'à ±30 cents), au-delà les grains sautent à l'octave, à la quinte et à la quarte.",
     "<b>Filtre</b> : passe-bas sous midi, plat à midi, passe-haut au-dessus, résonance croissante vers les extrêmes. <b>Quantize</b> cale PITCH sur quartes, quintes et octaves.",
     "<b>Tap tempo</b> : Ctrl + clic sur MODE (ou couche REVERSE verrouillée puis clic sur MODE) au moins deux fois ; le retard et l'espacement des grains suivent le tempo (affiché en BPM). Tourner OVERLAP rend l'espacement au potard."],
 midi_t="6. MIDI",
 midi="Envoie le MIDI à la piste de Textural (tous canaux ; dans Reaper, arme la piste avec ton entrée MIDI et active le monitoring). <b>Aucun CC n'est assigné par défaut</b> : chaque commande s'assigne avec le <b>MIDI Learn</b>. Tous les paramètres sont aussi automatisables dans le DAW.",
 ml_t="MIDI Learn",
 ml=["<b>Clic droit sur une commande</b> (un potard dans la couche active : normale, Ctrl, Alt ou Ctrl + Alt ; REVERSE, MODE, le footswitch ou PRESETS) : le menu commence par <b>MIDI Learn: &lt;commande&gt; (CC n / none)</b>. Choisis-le puis bouge une pédale d'expression ou appuie sur un bouton MIDI : le premier CC reçu est affecté. Ce message d'apprentissage ne modifie pas le son.",
     "La ligne d'état affiche <b>MIDI LEARN: move a control for &lt;commande&gt;</b>, puis <b>&lt;commande&gt; = CC n</b> pendant 2 secondes.",
     "<b>Clear MIDI: &lt;commande&gt;</b> retire l'affectation ; <b>Cancel MIDI learn</b> (ou un nouveau choix du même MIDI Learn) annule l'attente.",
     "Un numéro de CC ne pilote qu'une commande : apprendre un CC déjà utilisé le retire de l'autre commande.",
     "Clic droit ailleurs &gt; <b>MIDI</b> : <b>Learn: &lt;commande&gt; (CC n / none)</b> pour les 29 fonctions, dont <b>Freeze</b> et <b>Tap Tempo</b> qui n'ont pas de potard, <b>Cancel MIDI learn</b> et <b>Clear all MIDI assignments</b>.",
     "Les affectations sont <b>sauvegardées avec le projet</b>. Un projet d'une version précédente resté sur l'ancienne table de CC d'usine s'ouvre sans aucune affectation ; un projet où tu avais changé une affectation garde ses affectations."],
 lt=[["Commande", "Type"],
     ["Time, Size, Overlap, Regen, Pitch, Mix", "Continu 0-127"],
     ["Time Random, Size Random, Overlap Random, Regen Mix, Pitch Random, Reverse Random", "Continu 0-127"],
     ["Reverb Mix, Reverb Decay, Filter", "Continu 0-127"],
     ["Quantize", "Bascule : 64 et plus = actif"],
     ["Vibrato Rate, Vibrato Depth", "Continu 0-127"],
     ["Freeze", "Bascule : 64 et plus = gelé (maintien), moins de 64 = relâché"],
     ["Reverse", "Bascule : 64 et plus = actif"],
     ["Mode", "Sélecteur 3 positions : 0-42 Delay, 43-85 Auto Freeze, 86-127 Layers"],
     ["Bypass (footswitch)", "Footswitch à accrochage : 64 et plus = effet actif, moins de 64 = coupé"],
     ["Tap Tempo", "Momentané : chaque valeur de 64 ou plus est un tap"],
     ["Next Preset", "Momentané : chaque valeur de 64 ou plus = preset suivant"],
     ["Output Gain", "Continu 0-127 (−12 à +12 dB)"],
     ["Output Mode", "Sélecteur 3 positions : Mono, Wet/Dry, Stéréo"],
     ["Trails", "Bascule : 64 et plus = actif"],
     ["Footswitch Hold Mode", "Sélecteur 2 positions : 0-63 Preset Scroll, 64-127 Freeze"],
     ["Preset Scroll Mute", "Bascule : 64 et plus = actif"],
     ["Presets (Program Change 1-9, sans apprentissage)", "1-8 = emplacements (2 et 0 = Live), 9 = Slow Attack Soundtrack (fixe)"]],
 st_cap="Ligne d'état pendant le MIDI Learn : attente, puis confirmation.",
 w_t="7. Fenêtre et ligne d'état",
 w=["Clic droit (hors commande) &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> (la taille actuelle est cochée) ; <i>(default)</i> est indiqué à côté de la taille par défaut. Tu peux aussi tirer le coin (proportions conservées). La fenêtre ne peut jamais être plus petite que 60 %.",
    "<b>Plugin size &gt; Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de Textural (60 % au départ). Ce réglage est commun à toutes les instances et enregistré sur l'ordinateur (<i>settings.xml</i> dans le dossier Studio Wiga\\Textural des données utilisateur : %APPDATA% sous Windows, ~/Library sous macOS) ; la fenêtre ouverte prend aussi cette taille tout de suite.",
    "Chaque instance mémorise aussi sa propre taille de fenêtre dans le projet (celle qu'avait sa fenêtre à l'enregistrement du projet), et cette taille reste prioritaire sur la taille par défaut à la réouverture du projet. Une nouvelle instance s'ouvre à la taille par défaut.",
    "La <b>ligne d'état</b> sous le logo Textural n'affiche rien tant que tu n'agis pas : seulement le réglage que tu tournes (dans la couleur du potard), le mode, le preset chargé, un réglage piloté en MIDI et les messages du MIDI Learn. Elle s'efface après environ 1,5 s."],
 mt=[["Élément du menu", "Rôle"],
     ["MIDI Learn / Clear MIDI", "En tête quand tu fais un clic droit sur une commande."],
     ["Plugin size", "60 % / 75 % / 100 % avec (default) à côté de la taille par défaut, puis Default size (new windows)."],
     ["Save current settings to preset", "Range le son actuel dans l'emplacement 1 ou 3-8."],
     ["Reset current preset to factory", "Restaure l'emplacement en cours."],
     ["Reset all presets to factory", "Restaure tous les emplacements."],
     ["Load preset: Slow Attack Soundtrack", "Le preset supplémentaire."],
     ["MIDI", "Learn pour chaque fonction, Cancel MIDI learn, Clear all MIDI assignments."]],
 pr_t="8. Presets",
 pr=["Textural s'ouvre sur le preset 1. Le bouton PRESETS fait défiler 1 → 2 → … → 8 → 1. L'emplacement 2 est <b>Live</b> : tes propres réglages en cours, gardés pendant que tu visites les autres presets ; il ne peut pas être écrasé. Slow Attack Soundtrack est le 9e preset (liste de presets du DAW, menu du clic droit ou Program Change 9).",
     "Tes presets sont enregistrés dans le projet du DAW et dans <i>%APPDATA%\\Studio Wiga\\Textural\\UserPresets_v4.xml</i> (macOS : <i>~/Library/Studio Wiga/Textural/UserPresets_v4.xml</i>)."],
 pr_hdr=["#", "Preset", "Mode", "TIME", "SIZE", "OVERLAP", "REGEN", "PITCH", "MIX"],
 pd=[("1. Sea Synth", "Synthé granulaire polyphonique ondulant : quatre voix désaccordées, montée douce, vibrato lent, passe-bas chaud. Joue des accords et laisse-les sonner ; chaque nouvel accord devient une voix."),
     ("2. Live", "Tes réglages actuels de potards, boutons et paramètres cachés, gardés tels quels."),
     ("3. Crystal Cave", "Boucles d'octaves régénérées : chaque répétition monte d'une octave et s'éteint dans une grotte lumineuse. Notes seules et arpèges lents."),
     ("4. Melodic Kaleidoscope", "Mélodies gelées, rejouées à l'endroit, à l'envers et à d'autres octaves. Joue une courte phrase et laisse-la s'épanouir."),
     ("5. Obligatory Shimmer", "Reverb granulaire scintillante : les grains à l'octave se fondent dans une longue plate (Regen Mix 83 / 17 delay / granulaire). Notes longues, accords ouverts."),
     ("6. Reverse Reverb", "Ta guitare à l'envers, phrase par phrase (environ 0,9 s), puis dans une large reverb. Joue lentement ; SIZE règle la longueur de phrase."),
     ("7. Mellow Cello", "Nappe à l'octave inférieure avec vibrato de violoncelle, qui gonfle après chaque note. Notes seules dans le médium."),
     ("8. Stardust Cloud", "Synthé granulaire en Layers sous une pluie de particules, d'éclats inversés et de poussière d'octaves. Arpèges et harmoniques."),
     ("9. Slow Attack Soundtrack", "Nappe lente une quinte en dessous, longue montée et long déclin. Jeu en swell de volume, ambiances de film.")],
 tp_t="9. Conseils d'utilisation",
 tp=["<b>Chaîne Reaper</b> : piste guitare &gt; accordeur &gt; saturation &gt; simulateur d'ampli &gt; <b>Textural</b> &gt; console. Comme la pédale, Textural sonne mieux après l'ampli (delay / reverb / source de nappes) ; avant le simulateur d'ampli, règle Output Mode sur Mono.",
     "<b>7 cordes accordée grave</b> : sur les riffs en si grave, garde PITCH à 0 ou +12 (−12 et −24 deviennent boueux), utilise le filtre en passe-haut (Alt + SIZE au-delà de midi) et un MIX modéré pour garder le riff serré ; Mellow Cello et Sea Synth brillent sur les parties en son clair.",
     "<b>Sons qui sonnent comme un ring-mod</b> : de tout petits grains, un OVERLAP élevé et aucune randomisation ; ajoute un peu de Size ou Overlap Random.",
     "<b>Nappes à partir d'accords</b> : en Layers, mets REGEN au-delà de 15 h, gratte quatre accords et tu as une nappe à quatre voix.",
     "<b>Reverb sur le direct seul</b> : MIX au minimum et Reverb Mix monté donnent une reverb simple sur ton son direct.",
     "<b>Avec un Chocolate Plus</b> : apprends Freeze sur un bouton (maintien), Next Preset sur un autre, et MIX ou PITCH sur une pédale d'expression."],
 ts_t="Dépannage",
 ts=[["Problème", "Solution"],
     ["Le son ne change pas quand je tourne un potard", "Vérifie la LED d'état (effet actif) et MIX."],
     ["Le son s'arrête au bypass", "Active Trails (Ctrl + Alt + OVERLAP) pour le laisser sonner."],
     ["Le MIDI ne fait rien", "Aucun CC n'est assigné par défaut : clic droit sur la commande &gt; MIDI Learn. Vérifie que la piste reçoit le MIDI."],
     ["Un potard réagit à la mauvaise pédale", "Clic droit sur la commande &gt; Clear MIDI, ou MIDI &gt; Clear all MIDI assignments."],
     ["La fenêtre est trop petite", "Clic droit &gt; Plugin size &gt; 75 % ou 100 %, ou tire le coin ; Default size (new windows) fait ouvrir toutes les nouvelles fenêtres à cette taille."]],
 sp_t="10. Caractéristiques techniques",
 sp=[["Format", "VST3 · Windows 11 (x64) · macOS universel (Intel et Apple Silicon)"], ["Canaux", "Entrée / sortie stéréo, entrée mono"],
     ["Mémoire", "12 s de mémoire granulaire, 4 × 2,6 s pour les couches"], ["Grains", "Jusqu'à 160 grains simultanés, interpolation d'Hermite 4 points"],
     ["Reverb", "Plate de Dattorro modulée, 0,4 s – 60 s, infinie"], ["Filtre", "Double filtre LP / HP 4 pôles résonant"], ["Latence", "0 échantillon"],
     ["MIDI", "MIDI Learn sur 29 fonctions (aucun CC assigné par défaut), sauvegardé avec le projet ; Program Change 1-9 ; tous canaux"],
     ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, taille par défaut des nouvelles fenêtres au choix (60 % au départ), jamais plus petite que 60 % ; redimensionnable par le coin"],
     ["Stabilité", "Anti-gel v2 de la fenêtre sous Windows : l'interface ne bloque jamais l'hôte"], ["Version", VERSION]],
 sp_note="Inspiré de la MXR Textures M310. MXR et Textures sont des marques de leurs propriétaires ; Textural est un projet personnel indépendant de Studio Wiga."),
}

def section(lang):
    t = T[lang]; f = cover(t, "cover.png", 66 * mm)
    f += [P(t["p_t"], "h1")] + [P(x) for x in t["p"]] + [P(t["f_t"], "h2")] + bullets(t["f"])
    f += [P(t["i_t"], "h1")]
    for h, x in t["i"]: f += [P(h, "h2"), P(x)]
    f += [PageBreak(), P(t["o_t"], "h1"), img("annotated.png", height=88 * mm), Spacer(1, 3 * mm),
          table(t["o"], [9 * mm, 28 * mm, W - 37 * mm], first_bold=False), P(t["o_note"], "note"), PageBreak()]
    f += [P(t["m_t"], "h1"), P(t["gs_t"], "h2")] + [P(x) for x in t["gs"]]
    for h, x in t["modes"]: f += [P(h, "h2"), P(x)]
    f += [Spacer(1, 2 * mm), table(t["kt"], [18 * mm, (W - 18 * mm) / 3, (W - 18 * mm) / 3, (W - 18 * mm) / 3], first_bold=True), P(t["kt_note"], "note")]
    f += [P(t["rev_t"], "h2"), P(t["rev"]), PageBreak()]
    f += [P(t["fs_t"], "h1"), table(t["fs"], [36 * mm, W - 36 * mm], first_bold=True), Spacer(1, 4 * mm),
          table(t["led"], [30 * mm, W - 30 * mm], first_bold=True)]
    f += [P(t["hid_t"], "h2"), P(t["hid"]), table(t["ht"], [18 * mm] + [(W - 18 * mm) / 3] * 3, first_bold=True), Spacer(1, 2 * mm)] + bullets(t["hb"])
    f += [PageBreak(), P(t["midi_t"], "h1"), P(t["midi"]), P(t["ml_t"], "h2")] + bullets(t["ml"])
    f += [Spacer(1, 3 * mm), table(t["lt"], [78 * mm, W - 78 * mm], first_bold=True)]
    f += [KeepTogether([Spacer(1, 4 * mm), img("status_learn.png", 92 * mm), P(t["st_cap"], "small")])]
    f += [CondPageBreak(120 * mm), P(t["w_t"], "h1")] + [P(x) for x in t["w"]]
    f += [Spacer(1, 2 * mm), table(t["mt"], [62 * mm, W - 62 * mm], first_bold=True), PageBreak()]
    f += [P(t["pr_t"], "h1")] + [P(x) for x in t["pr"]]
    rows = [t["pr_hdr"]] + [[dec(v, lang) for v in r] for r in PRESETS]
    f += [Spacer(1, 2 * mm), table(rows, [7 * mm, 33 * mm, 19 * mm, 22 * mm, 15 * mm, 16 * mm, 22 * mm, 17 * mm, W - 151 * mm])]
    f += [Spacer(1, 3 * mm)]
    for h, x in t["pd"]: f += [KeepTogether([P("<b>" + h + "</b>", "p"), P(x)])]
    f += [CondPageBreak(80 * mm), P(t["tp_t"], "h1")] + bullets(t["tp"])
    f += [KeepTogether([P(t["ts_t"], "h2"), table(t["ts"], [62 * mm, W - 62 * mm], first_bold=True)])]
    f += [KeepTogether([P(t["sp_t"], "h1"), table(t["sp"], [28 * mm, W - 28 * mm], header=False, first_bold=True), P(t["sp_note"], "small")])]
    return f

build([("en", section("en")), ("fr", section("fr"))], "Textural - User manual / Notice v" + VERSION)
