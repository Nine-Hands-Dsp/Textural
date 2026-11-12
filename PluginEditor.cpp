#include "PluginEditor.h"
#include "NineHandsUserPresets.h"
#include "WigaWindowSize.h"
#include "Layout.h"

using namespace juce;

namespace
{
    double nowMs() { return Time::getMillisecondCounterHiRes(); }
    Image img (const void* d, int n) { return ImageCache::getFromMemory (d, n); }

    const Colour kInk (0xff161516);                   // serigraphie noire
    const Colour kCream (0xffeceae6);                 // texte de la pastille
    const Colour kPresetGreen (0xff00d060), kPresetRed (0xffff2a3a);
    constexpr float kKnobA0 = -135.0f, kKnobA1 = 135.0f;   // course des potards (degres) = graduations
    constexpr float kCran = 36.0f;                         // couronne a 10 crans
    constexpr float kBtnHitR = layout::ledR + 10.0f;
}

//==============================================================================
TexturalAudioProcessorEditor::TexturalAudioProcessorEditor (TexturalAudioProcessor& p)
    : AudioProcessorEditor (&p), proc (p)
{
    background   = img (BinaryData::background_png, BinaryData::background_pngSize);
    knobStrip[0] = img (BinaryData::knob_black_png, BinaryData::knob_black_pngSize);
    knobStrip[1] = img (BinaryData::knob_orange_png, BinaryData::knob_orange_pngSize);
    knobIndex[0] = img (BinaryData::knob_index_black_png, BinaryData::knob_index_black_pngSize);
    knobIndex[1] = img (BinaryData::knob_index_orange_png, BinaryData::knob_index_orange_pngSize);
    ledOn[cCyan]   = img (BinaryData::led_cyan_on_png,   BinaryData::led_cyan_on_pngSize);
    ledOff[cCyan]  = img (BinaryData::led_cyan_off_png,  BinaryData::led_cyan_off_pngSize);
    ledOn[cGreen]  = img (BinaryData::led_green_on_png,  BinaryData::led_green_on_pngSize);
    ledOff[cGreen] = img (BinaryData::led_green_off_png, BinaryData::led_green_off_pngSize);
    ledOn[cOrange] = img (BinaryData::led_orange_on_png, BinaryData::led_orange_on_pngSize);
    ledOff[cOrange]= img (BinaryData::led_orange_off_png,BinaryData::led_orange_off_pngSize);
    ledOn[cRed]    = img (BinaryData::led_red_on_png,    BinaryData::led_red_on_pngSize);
    ledOff[cRed]   = img (BinaryData::led_red_off_png,   BinaryData::led_red_off_pngSize);
    ledOn[cBlue]   = img (BinaryData::led_blue_on_png,   BinaryData::led_blue_on_pngSize);
    ledOff[cBlue]  = img (BinaryData::led_blue_off_png,  BinaryData::led_blue_off_pngSize);
    glowRev     = img (BinaryData::glow_rev_png, BinaryData::glow_rev_pngSize);
    glowMode[0] = img (BinaryData::glow_mode_green_png, BinaryData::glow_mode_green_pngSize);
    glowMode[1] = img (BinaryData::glow_mode_orange_png, BinaryData::glow_mode_orange_pngSize);
    glowMode[2] = img (BinaryData::glow_mode_red_png, BinaryData::glow_mode_red_pngSize);
    glowStatus  = img (BinaryData::glow_status_png, BinaryData::glow_status_pngSize);
    boldFace = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize);
    medFace  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    menuLnf.f = { medFace, medFace, boldFace };
    proc.glowPct = NineHandsGlow::percent (JucePlugin_Name);   // Glow intensity : commun a toutes les fenetres (settings.xml)
    logo = Drawable::createFromImageData (BinaryData::NineHands_Logo_Black_svg, BinaryData::NineHands_Logo_Black_svgSize);
    buildPrint();
    setLookAndFeel (&menuLnf);

    setResizable (true, true);
    setResizeLimits (roundToInt (kDefaultH * kW / kH), kDefaultH, roundToInt (kMaxH * kW / kH), kMaxH);
    if (auto* c = getConstrainer()) c->setFixedAspectRatio (kW / kH);
    hostLock.setLimits (roundToInt (kDefaultH * kW / kH), kDefaultH, roundToInt (kMaxH * kW / kH), kMaxH);
    setOpaque (true);
    setHeightKeepingAspect (sizeHeight (NineHandsWindow::openIndex (JucePlugin_Name, proc.uiSizeIdx.load(), kNumSizes)));   // taille du projet, sinon taille par defaut
    rebuildCaches();
    startTimerHz (30);
}

TexturalAudioProcessorEditor::~TexturalAudioProcessorEditor()
{
    stopTimer();
    setLookAndFeel (nullptr);
}

//==============================================================================
// Anti-gel v2 (NINE HANDS | DSP) : moteur logiciel sous Windows, aucun calcul lourd dans paint(), caches reconstruits
// par le timer seulement, chien de garde sur les redessins, aucun appel a l'hote depuis le thread audio.
void TexturalAudioProcessorEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw)
            peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void TexturalAudioProcessorEditor::parentHierarchyChanged() { useSoftwareRenderer(); hostLock.track (*this); }
void TexturalAudioProcessorEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

void TexturalAudioProcessorEditor::askRepaint (Rectangle<int> r)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = nowMs();
    repaint (r);
}

Rectangle<int> TexturalAudioProcessorEditor::zone (Rectangle<float> r) const
{
    return (r * scale()).getSmallestIntegerContainer().expanded (2);
}

float TexturalAudioProcessorEditor::physicalScale() const
{
    if (forcedScale > 0.0f) return forcedScale;
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

// fond + serigraphie vectorielle composes une fois par taille / echelle (constructeur et timer, jamais dans paint)
void TexturalAudioProcessorEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = cacheScale > 0.0f ? cacheScale : physicalScale();
    const int w = getWidth(), h = getHeight();
    if (w <= 0 || h <= 0) return;
    if (w == cacheW && h == cacheH && std::abs (sc - cacheScale) < 0.01f && bgCache.isValid()) return;
    cacheW = w; cacheH = h; cacheScale = sc;
    const int pw = roundToInt ((float) w * sc), ph = roundToInt ((float) h * sc);
    Image im (Image::RGB, jmax (1, pw), jmax (1, ph), true);
    {
        Graphics g (im);
        g.fillAll (Colour (0xff111112));          // autour des jacks : le fond de l'image est transparent
        g.addTransform (AffineTransform::scale ((float) pw / kW, (float) ph / kH));
        g.setImageResamplingQuality (Graphics::highResamplingQuality);
        g.drawImage (background, Rectangle<float> (0, 0, kW, kH));
        drawPrint (g);
    }
    bgCache = im;
    repaint();
}

int TexturalAudioProcessorEditor::sizeHeight (int idx)
{
    const int h[kNumSizes] = { kDefaultH, 719, kRefH };
    return h[jlimit (0, kNumSizes - 1, idx)];
}

void TexturalAudioProcessorEditor::setHeightKeepingAspect (int h)
{
    h = jlimit (kDefaultH, kMaxH, h);
    setSize (roundToInt ((float) h * kW / kH), h);
    hostLock.enforce();
}

void TexturalAudioProcessorEditor::resized()
{
    // anti-gel : jamais de setSize ici ; les limites du constrainer (jamais plus petit que la taille par defaut) suffisent
    // seules les tailles choisies au menu sont enregistrees (pas celles tirees au coin)
    resizeSettle = 4;
}

//==============================================================================
//  Serigraphie vectorielle (Layout.h) : nette a toutes les tailles
//==============================================================================
void TexturalAudioProcessorEditor::buildPrint()
{
    printPath.clear();
    for (const auto& t : layout::texts)
    {
        const Font font (FontOptions (t.font == 1 ? boldFace : medFace).withPointHeight (t.em));
        const String s (t.s);
        float total = 0.0f;
        for (int i = 0; i < s.length(); ++i)
            total += GlyphArrangement::getStringWidth (font, String::charToString (s[i])) + (i > 0 ? t.track : 0.0f);
        const float base = (font.getAscent() - font.getDescent()) * 0.5f;
        GlyphArrangement ga;
        float x = -total * 0.5f;
        for (int i = 0; i < s.length(); ++i)
        {
            const String ch = String::charToString (s[i]);
            ga.addLineOfText (font, ch, x, base);
            x += GlyphArrangement::getStringWidth (font, ch) + t.track;
        }
        Path pth; ga.createPath (pth);
        pth.applyTransform (AffineTransform::rotation (-t.rot * MathConstants<float>::pi / 180.0f).translated (t.x, t.y));
        printPath.addPath (pth);
    }
    for (const auto& d : layout::dots) printPath.addEllipse (d.x - d.r, d.y - d.r, d.r * 2.0f, d.r * 2.0f);

    // filets + arc du PITCH
    linePath.clear();
    {
        const int n = (int) (sizeof (layout::lines) / sizeof (float));
        for (int i = 0; i < n;)
        {
            const int np = (int) layout::lines[i++];
            for (int k = 0; k < np; ++k, i += 2)
                k == 0 ? linePath.startNewSubPath (layout::lines[i], layout::lines[i + 1]) : linePath.lineTo (layout::lines[i], layout::lines[i + 1]);
        }
        for (const auto& a : layout::arcs)
            linePath.addCentredArc (a.cx, a.cy, a.r, a.r, 0.0f, degreesToRadians (a.a0), degreesToRadians (a.a1), true);
    }
    // titre Textural (contours vectorises de l'ancien visuel, remplissage pair-impair)
    titlePath.clear();
    titlePath.setUsingNonZeroWinding (false);
    {
        const int n = (int) (sizeof (layout::title) / sizeof (float));
        for (int i = 0; i < n;)
        {
            const int np = (int) layout::title[i++];
            for (int k = 0; k < np; ++k, i += 2)
                k == 0 ? titlePath.startNewSubPath (layout::title[i], layout::title[i + 1]) : titlePath.lineTo (layout::title[i], layout::title[i + 1]);
            titlePath.closeSubPath();
        }
    }
    // symboles des modes
    halfPath.clear(); starPath.clear(); ringPath.clear();
    for (const auto& h : layout::halves)
        halfPath.addPieSegment (h.x - h.r, h.y - h.r, h.r * 2, h.r * 2, -MathConstants<float>::halfPi, MathConstants<float>::halfPi, 0.0f);
    for (int i = 0; i < 4; ++i)
    {
        const float a = degreesToRadians (45.0f * (float) i);
        const auto c = layout::starPos;
        starPath.startNewSubPath (c.x - layout::starL * std::sin (a), c.y - layout::starL * std::cos (a));
        starPath.lineTo (c.x + layout::starL * std::sin (a), c.y + layout::starL * std::cos (a));
    }
    for (const auto& c : layout::ringPos)
        for (float r : layout::ringR) ringPath.addEllipse (c.x - r, c.y - r, r * 2, r * 2);
}

void TexturalAudioProcessorEditor::drawPrint (Graphics& g)
{
    g.setColour (kInk);
    g.fillPath (printPath);
    g.fillPath (titlePath);
    g.strokePath (linePath, PathStrokeType (layout::lineW, PathStrokeType::curved, PathStrokeType::butt));
    g.setColour (Colour (layout::colGreen));
    g.fillPath (halfPath);
    g.setColour (Colour (layout::colOrange));
    g.strokePath (starPath, PathStrokeType (layout::starW, PathStrokeType::curved, PathStrokeType::rounded));
    g.setColour (Colour (layout::colRed));
    g.strokePath (ringPath, PathStrokeType (layout::ringW));
    if (logo != nullptr)
    {
        const auto vb = logo->getDrawableBounds();
        const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        logo->drawWithin (g, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }, RectanglePlacement::centred, 1.0f);
    }
}

//==============================================================================
TexturalAudioProcessorEditor::Layer TexturalAudioProcessorEditor::currentLayer() const
{
    if (dragKnob >= 0) return dragLayer;
    if (latched != Layer::Main) return latched;
    const auto m = ModifierKeys::getCurrentModifiersRealtime();
    const bool ctrl = m.isCtrlDown() || m.isCommandDown();
    if (ctrl && m.isAltDown()) return Layer::Foot;
    if (ctrl)                  return Layer::Reverse;
    if (m.isAltDown())         return Layer::Mode;
    return Layer::Main;
}

String TexturalAudioProcessorEditor::knobParamID (Layer l, int k) const
{
    static const String* main[6] = { &PID::time,      &PID::size,    &PID::overlap,    &PID::regen,       &PID::pitch,      &PID::mix };
    static const String* rev[6]  = { &PID::timeRnd,   &PID::sizeRnd, &PID::overlapRnd, &PID::regenMix,    &PID::pitchRnd,   &PID::reverseRnd };
    static const String* mode[6] = { &PID::reverbMix, &PID::cutoff,  &PID::vibRate,    &PID::reverbDecay, &PID::quantize,   &PID::vibDepth };
    static const String* foot[6] = { &PID::presetMute, nullptr,      &PID::trails,     &PID::outputMode,  &PID::fsHoldMode, &PID::outputGain };
    const String* const* t = l == Layer::Reverse ? rev : l == Layer::Mode ? mode : l == Layer::Foot ? foot : main;
    return t[k] != nullptr ? *t[k] : String();
}

TexturalAudioProcessorEditor::Hit TexturalAudioProcessorEditor::hitTest (Point<float> p, int& knobIndex) const
{
    knobIndex = -1;
    for (int i = 0; i < 6; ++i)
        if (p.getDistanceFrom (layout::knobPos[i]) < layout::knobR) { knobIndex = i; return Hit::Knob; }
    if (p.getDistanceFrom (layout::revPos)  < kBtnHitR) return Hit::ReverseBtn;
    if (p.getDistanceFrom (layout::modePos) < kBtnHitR) return Hit::ModeBtn;
    if (p.getDistanceFrom (layout::fsPos)   < layout::fsR) return Hit::Footswitch;
    if (p.getDistanceFrom (layout::ledPos)  < kBtnHitR) return Hit::Led;
    const auto& r = layout::pill;
    if (r.contains (p))
    {
        if (p.x < r.getX() + 34.0f)     return Hit::PillPrev;
        if (p.x > r.getRight() - 34.0f) return Hit::PillNext;
        return Hit::PillName;
    }
    return Hit::None;
}

void TexturalAudioProcessorEditor::setParam (const String& id, float v)
{
    if (auto* prm = proc.param (id))
    {
        prm->beginChangeGesture();
        prm->setValueNotifyingHost (jlimit (0.0f, 1.0f, v));
        prm->endChangeGesture();
    }
    touch (id);
}

void TexturalAudioProcessorEditor::showMessage (const String& text)
{
    statusMsg = text;
    statusKnob = -1;
    statusMs = nowMs();
}

void TexturalAudioProcessorEditor::showKnob (int knob, const String& id)
{
    statusMsg.clear();
    statusKnob = knob;
    statusParam = id;
    statusMs = nowMs();
}

void TexturalAudioProcessorEditor::touch (const String&) {}

int TexturalAudioProcessorEditor::learnIndexAt (const MouseEvent& e) const
{
    int k;
    switch (hitTest (toUnits (e), k))
    {
        case Hit::Knob:       return TexturalAudioProcessor::learnIndexOf (knobParamID (currentLayer(), k));
        case Hit::ReverseBtn: return TexturalAudioProcessor::learnIndexOf (PID::reverse);
        case Hit::ModeBtn:    return TexturalAudioProcessor::learnIndexOf (PID::mode);
        case Hit::Footswitch: return TexturalAudioProcessor::learnIndexOf (PID::bypass);
        case Hit::PillNext:   return TexturalAudioProcessor::kLearnNext;
        default:              return -1;
    }
}

//==============================================================================
void TexturalAudioProcessorEditor::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { showMenu (learnIndexAt (e)); return; }

    int k;
    const auto p = toUnits (e);
    pressedHit = hitTest (p, k);
    pressStartMs = nowMs();
    longPressHandled = false;

    if (pressedHit == Hit::Knob)
    {
        dragLayer = currentLayer();
        dragParam = knobParamID (dragLayer, k);
        if (dragParam.isEmpty()) { pressedHit = Hit::None; return; }
        dragKnob = k;
        auto* prm = proc.param (dragParam);
        dragStartValue = prm->getValue();
        dragStartY = p.y;
        prm->beginChangeGesture();
        showKnob (k, dragParam);
    }
    else if (pressedHit == Hit::PillPrev || pressedHit == Hit::PillName || pressedHit == Hit::PillNext)
    {
        statusMs = -1.0e9;                                // la ligne d'etat ne bloque pas : la barre de presets revient
        statusMsg.clear();
        if (pressedHit == Hit::PillPrev)      proc.previousPreset();
        else if (pressedHit == Hit::PillNext) proc.nextPreset();
        else                                  showPresetMenu();
        pressedHit = Hit::None;
    }
    else if (pressedHit == Hit::Footswitch && ! presetScrollMode)
    {
        // bascule des l'appui (fonctionnement d'Echoflex) ; maintien = freeze / defilement des presets
        setParam (PID::bypass, proc.value (PID::bypass) > 0.5f ? 0.0f : 1.0f);
    }
}

void TexturalAudioProcessorEditor::mouseDrag (const MouseEvent& e)
{
    if (dragKnob < 0) return;
    const auto p = toUnits (e);
    const float sens = e.mods.isShiftDown() ? 1250.0f : 250.0f;
    const float dy = (dragStartY - p.y) + (p.x - e.mouseDownPosition.x / scale()) * 0.5f;
    if (auto* prm = proc.param (dragParam))
    {
        prm->setValueNotifyingHost (jlimit (0.0f, 1.0f, dragStartValue + dy / sens));
        showKnob (dragKnob, dragParam);
    }
}

void TexturalAudioProcessorEditor::mouseUp (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) return;

    if (dragKnob >= 0)
    {
        if (auto* prm = proc.param (dragParam)) prm->endChangeGesture();
        dragKnob = -1;
    }
    else if (! longPressHandled)
    {
        switch (pressedHit)
        {
            case Hit::ReverseBtn:
                if (latched == Layer::Reverse) latched = Layer::Main;
                else
                {
                    const bool on = proc.value (PID::reverse) < 0.5f;
                    setParam (PID::reverse, on ? 1.0f : 0.0f);
                    showMessage (on ? "REVERSE ON" : "REVERSE OFF");
                }
                break;

            case Hit::ModeBtn:
                if (currentLayer() == Layer::Reverse)                 // maintien REVERSE + MODE = tap tempo
                {
                    proc.tap();
                    showMessage ("TAP " + String (roundToInt (proc.tapBpm.load())) + " BPM");
                }
                else if (latched == Layer::Mode) latched = Layer::Main;
                else
                {
                    const int m = (roundToInt (proc.value (PID::mode)) + 1) % 3;
                    setParam (PID::mode, proc.param (PID::mode)->convertTo0to1 ((float) m));
                    static const char* names[3] = { "DELAY MODE", "AUTO FREEZE MODE", "LAYERS MODE" };
                    showMessage (names[m]);
                }
                break;

            case Hit::Footswitch:
                if (presetScrollMode)
                {
                    proc.nextPreset();
                    presetScrollUntil = nowMs() + 6000.0;
                }
                break;

            case Hit::Led:
                latched = latched == Layer::Foot ? Layer::Main : Layer::Foot;
                break;

            default: break;
        }
    }

    if (fsFreezeHeld)
    {
        fsFreezeHeld = false;
        setParam (PID::freeze, 0.0f);
    }
    pressedHit = Hit::None;
}

void TexturalAudioProcessorEditor::mouseMove (const MouseEvent& e)
{
    int k;
    hover = hitTest (toUnits (e), k);
    setMouseCursor (hover == Hit::None ? MouseCursor::NormalCursor
                                       : hover == Hit::Knob ? MouseCursor::UpDownResizeCursor : MouseCursor::PointingHandCursor);
}

void TexturalAudioProcessorEditor::mouseExit (const MouseEvent&) { hover = Hit::None; }

void TexturalAudioProcessorEditor::mouseDoubleClick (const MouseEvent& e)
{
    int k;
    if (hitTest (toUnits (e), k) == Hit::Knob)
    {
        const auto id = knobParamID (currentLayer(), k);
        if (auto* prm = proc.param (id)) { setParam (id, prm->getDefaultValue()); showKnob (k, id); }
    }
}

void TexturalAudioProcessorEditor::mouseWheelMove (const MouseEvent& e, const MouseWheelDetails& w)
{
    int k;
    if (hitTest (toUnits (e), k) != Hit::Knob) return;
    const auto id = knobParamID (currentLayer(), k);
    if (auto* prm = proc.param (id))
    {
        setParam (id, prm->getValue() + (w.deltaY + w.deltaX) * (e.mods.isShiftDown() ? 0.02f : 0.08f));
        showKnob (k, id);
    }
}

//==============================================================================
void TexturalAudioProcessorEditor::timerCallback()
{
    phase = nowMs() / 1000.0;
    const double now = nowMs();

    // un potard tourne par MIDI apparait aussi dans la ligne d'etat
    const double mt = proc.lastMidiTime.load();
    if (mt > lastMidiSeen)
    {
        lastMidiSeen = mt;
        const int li = proc.learnIndexForCC (proc.lastMidiCC.load());
        if (li >= 0 && li < TexturalAudioProcessor::kLearnTap)
        {
            const auto& id = TexturalAudioProcessor::learnId (li);
            for (int l = 0; l < 4; ++l)
                for (int k = 0; k < 6; ++k)
                    if (knobParamID ((Layer) l, k) == id) showKnob (k, id);
        }
    }

    // MIDI Learn
    {
        const int learned = proc.lastLearned.exchange (-1);
        const int lt = proc.learnTarget.load();
        if (learned >= 0)
        {
            showMessage (String (TexturalAudioProcessor::learnName (learned)).toUpperCase() + " = CC " + String (proc.ccAssign[learned].load()));
            learnMsgShown = false;
        }
        else if (lt >= 0)
        {
            showMessage (String (CharPointer_UTF8 ("MIDI LEARN \xc2\xb7 ")) + String (TexturalAudioProcessor::learnName (lt)));
            learnMsgShown = true;
        }
        else if (learnMsgShown)
        {
            learnMsgShown = false;
            statusMs = now - 2200.0;
        }
    }

    // appuis longs
    const double held = now - pressStartMs;
    if (pressedHit != Hit::None && pressedHit != Hit::Knob && ! longPressHandled)
    {
        if ((pressedHit == Hit::ReverseBtn || pressedHit == Hit::ModeBtn) && held > 550.0)
        {
            const Layer l = pressedHit == Hit::ReverseBtn ? Layer::Reverse : Layer::Mode;
            latched = latched == l ? Layer::Main : l;
            longPressHandled = true;
        }
        else if (pressedHit == Hit::Footswitch && held > 420.0)
        {
            longPressHandled = true;
            const bool freezeMode = proc.value (PID::fsHoldMode) > 0.5f;
            if (freezeMode)
            {
                // l'appui a deja bascule l'effet : on revient a l'etat d'origine et on gele tant qu'on maintient
                setParam (PID::bypass, proc.value (PID::bypass) > 0.5f ? 0.0f : 1.0f);
                if (proc.value (PID::bypass) < 0.5f) { fsFreezeHeld = true; setParam (PID::freeze, 1.0f); }
            }
            else
            {
                setParam (PID::bypass, proc.value (PID::bypass) > 0.5f ? 0.0f : 1.0f);
                presetScrollMode = ! presetScrollMode;
                presetScrollUntil = now + 6000.0;
                showMessage (presetScrollMode ? "PRESET SCROLL" : "PRESET SCROLL OFF");
            }
        }
    }
    if (presetScrollMode && now > presetScrollUntil) presetScrollMode = false;

    // moteur logiciel, caches, chien de garde (anti-gel v2)
    if (getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = now; useSoftwareRenderer(); }
    hostLock.track (*this);
    if (now - lastGlowReadMs > 3000.0)       // Glow intensity : commun a toutes les fenetres (jamais dans paint)
    {
        lastGlowReadMs = now;
        const int gp = NineHandsGlow::percent (JucePlugin_Name);
        if (gp != proc.glowPct.load()) { proc.glowPct = gp; repaint(); }
    }
    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = now;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }
    if (repaintAskedMs > 0.0 && isShowing() && now - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0;
        lastPeer = nullptr;
        useSoftwareRenderer();
        repaint();
    }

    auto changed = [] (float& drawn, float v, float eps = 0.002f) { if (std::abs (drawn - v) < eps) return false; drawn = v; return true; };
    const Layer layer = currentLayer();

    // potards : angle et flou de mouvement (longueur du flou = angle parcouru pendant l'image)
    for (int i = 0; i < 6; ++i)
    {
        const float a = kKnobA0 + (kKnobA1 - kKnobA0) * knobValue (layer, i);
        if (! anglesInit) shownAngle[i] = a;
        const float t = std::abs (a - shownAngle[i]) / kCran;
        shownAngle[i] = a;
        const float lvl = jlimit (0.0f, 1.6f, (t - 0.15f) / 0.6f);
        blurLevel[i] = lvl > blurLevel[i] ? lvl : blurLevel[i] * 0.6f;   // montee immediate, retombee x 0,6
        if (blurLevel[i] < 0.02f) blurLevel[i] = 0.0f;
        const bool c1 = changed (drawnKnob[i], a, 0.05f);
        const bool c2 = changed (drawnBlur[i], blurLevel[i], 0.01f);
        if (c1 || c2) askRepaint (zone (layout::knobPos[i], layout::knobS * 0.5f));
    }
    anglesInit = true;

    const int gl = proc.glowPct.load();
    if (gl != drawnGlow) { drawnGlow = gl; repaint(); }

    if (changed (drawnReverse, reverseAmount (layer)))
        askRepaint (zone (layout::glow_rev));
    {
        int ci; float amt;
        modeLedState (layer, ci, amt);
        const bool a = changed (drawnMode, amt);
        if (a || ci != drawnModeCol) { drawnModeCol = ci; askRepaint (zone (layout::glow_mode_red)); }
    }
    if (changed (drawnLed, statusLedAmount (layer)))
        askRepaint (zone (layout::glow_status));

    if (pressedHit != drawnPressed)
    {
        if (pressedHit == Hit::Footswitch || drawnPressed == Hit::Footswitch) askRepaint (zone (layout::fsPos, layout::fsR + 4.0f));
        drawnPressed = pressedHit;
    }

    {
        String txt; float alpha = 0.0f;
        if (! statusLineState (txt, alpha)) { txt.clear(); alpha = 0.0f; }
        Colour dot;
        const auto pl = presetLine (dot);
        const bool a = changed (drawnStatusAlpha, alpha);
        if (a || txt != drawnStatus || pl != drawnPreset || hover != drawnHover)
        {
            drawnStatus = txt; drawnPreset = pl; drawnHover = hover;
            askRepaint (zone (layout::pill.expanded (3.0f)));
        }
    }
}

float TexturalAudioProcessorEditor::knobValue (Layer layer, int i) const
{
    const auto id = knobParamID (layer, i);
    return id.isNotEmpty() ? proc.param (id)->getValue() : 0.5f;
}

float TexturalAudioProcessorEditor::reverseAmount (Layer layer) const
{
    float amt = proc.value (PID::reverse) > 0.5f ? 1.0f : 0.0f;
    if (layer == Layer::Reverse) amt = blink (2.5) ? 1.0f : 0.3f;
    return amt;
}

void TexturalAudioProcessorEditor::modeLedState (Layer layer, int& ci, float& amt) const
{
    // la LED MODE prend la couleur du symbole du mode actif et clignote quand le son est gele
    const int m = jlimit (0, 2, roundToInt (proc.value (PID::mode)));
    ci = m == 0 ? cGreen : m == 1 ? cOrange : cRed;
    amt = 1.0f;
    if (proc.value (PID::bypass) < 0.5f && proc.isFrozen()) amt = blink (3.0) ? 1.0f : 0.15f;
    if (layer == Layer::Mode) amt = blink (2.5) ? 1.0f : 0.3f;
}

float TexturalAudioProcessorEditor::statusLedAmount (Layer layer) const
{
    float on = proc.value (PID::bypass) < 0.5f ? 1.0f : 0.0f;
    if (presetScrollMode) on = 0.55f + 0.45f * (float) std::sin (phase * MathConstants<double>::twoPi * 1.2);
    if (layer == Layer::Foot) on = blink (2.5) ? 1.0f : 0.2f;
    return on;
}

// ligne d'etat : apparait des qu'un reglage bouge, reste ~2,5 s apres le dernier mouvement puis s'efface en fondu
bool TexturalAudioProcessorEditor::statusLineState (String& txt, float& alpha) const
{
    const bool isMsg = statusMsg.isNotEmpty();
    if (! isMsg && (statusKnob < 0 || statusParam.isEmpty())) return false;
    const double age = nowMs() - statusMs;
    const bool turning = dragKnob >= 0 && dragKnob == statusKnob;
    if (learnMsgShown) { txt = statusMsg; alpha = 1.0f; return true; }
    alpha = 1.0f;
    if (! turning)
    {
        if (age < 0.0 || age > 2800.0) return false;
        if (age < 120.0) alpha = (float) (age / 120.0);
        else if (age > 2500.0) alpha = (float) (1.0 - (age - 2500.0) / 300.0);
    }
    txt = isMsg ? statusMsg : proc.describe (statusParam);
    return true;
}

String TexturalAudioProcessorEditor::presetLine (Colour& dot) const
{
    const int cur = proc.currentPreset.load();
    String name = proc.presetName (cur).toUpperCase();
    if (cur >= 1 && cur <= 8)
    {
        dot = cur <= 4 ? kPresetGreen : kPresetRed;
        name = name.replaceFirstOccurrenceOf (" ", String (CharPointer_UTF8 (" \xc2\xb7 ")));
    }
    else
    {
        dot = Colours::transparentBlack;
        name = String (CharPointer_UTF8 ("+ \xc2\xb7 ")) + name;
    }
    if (presetScrollMode) name = String (CharPointer_UTF8 ("\xe2\x96\xb8 ")) + name;
    if (! TexturalAudioProcessor::isLive (cur) && proc.isPresetModified()) name << " *";
    return name;
}

//==============================================================================
void TexturalAudioProcessorEditor::showPresetMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    m.addSectionHeader ("Presets");
    const int cur = proc.currentPreset.load();
    for (int i = 1; i <= TexturalAudioProcessor::kLastPreset; ++i)
    {
        if (i == TexturalAudioProcessor::kExtraPreset) m.addSeparator();
        m.addItem (100 + i, proc.presetName (i), true, cur == i);
    }
    SafePointer<TexturalAudioProcessorEditor> safe (this);
    m.showMenuAsync (PopupMenu::Options().withTargetScreenArea (localAreaToGlobal (zone (layout::pill))), [safe] (int r)
    {
        if (safe != nullptr && r > 100) safe->proc.selectPreset (r - 100);
    });
}

PopupMenu TexturalAudioProcessorEditor::buildContextMenu (int learnIdx)
{
    using namespace NineHandsMenu;
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    const int lt = proc.learnTarget.load();
    auto ccText = [this] (int i) { const int cc = proc.ccAssign[i].load(); return cc >= 0 ? "CC " + String (cc) : String ("not assigned"); };
    const Colour accent (0xff00d060);
    if (learnIdx >= 0)
    {
        // menu d'une commande (tronc commun) : en-tete, MIDI Learn, Clear MIDI, Cancel MIDI learn
        const String name = TexturalAudioProcessor::learnName (learnIdx);
        addHeader (m, menuLnf.f, icoKnob, accent, name, "MIDI: " + ccText (learnIdx));
        m.addItem (1000 + learnIdx, "MIDI Learn: " + name, true, lt == learnIdx);
        m.addItem (1100 + learnIdx, "Clear MIDI: " + name, proc.ccAssign[learnIdx].load() >= 0);
        m.addItem (1200, "Cancel MIDI learn", lt >= 0);
        return m;
    }

    addHeader (m, menuLnf.f, icoPedal, accent, "Textural", "Granular synth  v" + String (JucePlugin_VersionString));
    PopupMenu factory;
    const int cur = proc.currentPreset.load();
    for (int i = 1; i <= TexturalAudioProcessor::kLastPreset; ++i)
        factory.addItem (100 + i, proc.presetName (i), true, cur == i && userSlot == 0);
    m.addSubMenu ("Factory presets", factory);
    NineHandsUserPresets::addMenus (m, "Textural", 200, 300, userSlot);
    m.addSeparator();

    PopupMenu midi;
    midi.addSectionHeader ("MIDI Learn");
    for (int i = 0; i < TexturalAudioProcessor::kNumLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (TexturalAudioProcessor::learnName (i)) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    midi.addItem (1200, "Cancel MIDI learn", lt >= 0);
    midi.addItem (1201, "Clear all MIDI assignments");
    midi.addSeparator();
    NineHandsWindow::addMidiFootswitchMode (midi, ! proc.midiFsMomentary.load());
    midi.addSeparator();
    NineHandsWindow::addProgramChangeInfo (midi);
    m.addSubMenu ("MIDI", midi);
    m.addSeparator();

    const char* names[kNumSizes] = { "60 %", "75 %", "100 %" };
    const int heights[kNumSizes] = { sizeHeight (0), sizeHeight (1), sizeHeight (2) };
    m.addSubMenu ("Plugin size", NineHandsWindow::sizeMenu (JucePlugin_Name, kNumSizes, names, heights, getHeight()));
    m.addSubMenu ("Glow intensity", NineHandsWindow::glowMenu (proc.glowPct.load()));
    return m;
}

void TexturalAudioProcessorEditor::showMenu (int learnIdx)
{
    auto m = buildContextMenu (learnIdx);
    SafePointer<TexturalAudioProcessorEditor> safe (this);
    m.showMenuAsync (PopupMenu::Options().withMousePosition(), [safe] (int r)
    {
        if (safe == nullptr || r == 0 || r == 9001) return;
        auto& ed = *safe;
        auto& pr = ed.proc;
        int inst = pr.uiSizeIdx.load();
        const int sz = NineHandsWindow::handleSize (r, JucePlugin_Name, kNumSizes, inst);
        if (sz >= 0) { pr.uiSizeIdx = inst; ed.setHeightKeepingAspect (sizeHeight (sz)); return; }
        if (const int pc = NineHandsWindow::handleGlow (r, JucePlugin_Name)) { pr.glowPct = pc; ed.repaint(); return; }
        if (r == NineHandsWindow::idLatch || r == NineHandsWindow::idMomentary) pr.midiFsMomentary = r == NineHandsWindow::idMomentary;
        else if (r > 100 && r <= 100 + TexturalAudioProcessor::kLastPreset) { pr.selectPreset (r - 100); ed.userSlot = 0; }
        else if (r > 200 && r < 210) { if (NineHandsUserPresets::load (pr, "Textural", r - 200)) ed.userSlot = r - 200; }
        else if (r > 300 && r < 310) { if (NineHandsUserPresets::save (pr, "Textural", r - 300)) ed.userSlot = r - 300; }
        else if (r >= 1000 && r < 1000 + TexturalAudioProcessor::kNumLearn)
            pr.learnTarget.store (pr.learnTarget.load() == r - 1000 ? -1 : r - 1000);
        else if (r >= 1100 && r < 1100 + TexturalAudioProcessor::kNumLearn) pr.ccAssign[r - 1100].store (-1);
        else if (r == 1200) pr.learnTarget.store (-1);
        else if (r == 1201) { pr.learnTarget.store (-1); pr.resetMidiMap(); }
    });
}

//==============================================================================
//  Dessin
//==============================================================================
void TexturalAudioProcessorEditor::drawGlow (Graphics& g, const Image& im, Rectangle<float> r, float amt)
{
    const float a = amt * (float) proc.glowPct.load() / 100.0f;
    if (a <= 0.003f || ! im.isValid()) return;
    g.setOpacity (a);
    g.drawImage (im, r);
    g.setOpacity (1.0f);
}

void TexturalAudioProcessorEditor::drawLed (Graphics& g, Point<float> c, const Image& off, const Image& on, float amt)
{
    const float hs = layout::ledS * 0.5f;
    const Rectangle<float> r (c.x - hs, c.y - hs, hs * 2.0f, hs * 2.0f);
    g.setOpacity (1.0f);
    g.drawImage (off, r);
    if (amt > 0.003f) { g.setOpacity (amt); g.drawImage (on, r); g.setOpacity (1.0f); }
}

// potard : corps periodique (10 crans -> 36 images sur 36 degres) + index qui tourne ; flou de mouvement
// net -> flou partiel (0,6 cran) -> flou complet (un cran, plafonne a 60 %) selon la vitesse
void TexturalAudioProcessorEditor::drawKnob (Graphics& g, int i, float angle, float blur)
{
    const int t = i == 4 ? 1 : 0;
    const Image& strip = knobStrip[t];
    const int px = layout::knobPx, nf = layout::knobFrames;
    const float s = layout::knobS;
    const auto c = layout::knobPos[i];
    const Rectangle<float> dst (c.x - s * 0.5f, c.y - s * 0.5f, s, s);
    float m = std::fmod (angle, kCran); if (m < 0) m += kCran;
    const float ff = m / kCran * (float) nf;
    const int f0 = (int) ff % nf, f1 = (f0 + 1) % nf;
    const float fr = ff - std::floor (ff);
    auto draw = [&] (int idx, float op)
    {
        if (op <= 0.003f) return;
        // une image de la bande verticale, sans copie : bande entiere transformee, decoupee a la case du potard
        Graphics::ScopedSaveState ss (g);
        g.reduceClipRegion (dst.getSmallestIntegerContainer());
        g.setOpacity (op);
        const float k = s / (float) px;
        g.drawImageTransformed (strip, AffineTransform::translation (0.0f, (float) (-idx * px)).scaled (k).translated (dst.getX(), dst.getY()));
    };
    // image nette (fondu entre deux positions voisines pour un mouvement continu)
    draw (f0, 1.0f);
    draw (f1, fr);
    if (blur > 0.0f)
    {
        draw (nf + f0, jmin (1.0f, blur));
        if (blur > 1.0f) draw (2 * nf, jmin (0.6f, blur - 1.0f));
    }
    g.setOpacity (1.0f);
    // index (creme) : tourne avec le potard ; en mouvement, quelques positions moyennees
    const Image& ind = knobIndex[t];
    const float k = s / (float) px;
    auto placeAt = [&] (float aDeg)
    {
        return AffineTransform::translation (-px * 0.5f, -px * 0.5f).scaled (k).rotated (degreesToRadians (aDeg)).translated (c.x, c.y);
    };
    if (blur <= 0.0f) g.drawImageTransformed (ind, placeAt (angle));
    else
    {
        const int n = 4;
        const float span = jmin (blur, 1.0f) * kCran * 0.6f;
        for (int j = 0; j < n; ++j)
        {
            g.setOpacity (1.0f / (float) (j + 1));
            g.drawImageTransformed (ind, placeAt (angle - span * (float) j / (float) (n - 1)));
        }
        g.setOpacity (1.0f);
    }
}

void TexturalAudioProcessorEditor::drawPill (Graphics& g)
{
    const auto r = layout::pill;
    const float rad = r.getHeight() * 0.5f;
    // biseau plat (6 px dans l'image 1800) puis face noire, fin liseré clair
    g.setColour (Colour (0xff343437));
    g.fillRoundedRectangle (r, rad);
    g.setColour (Colour (0xff0a0a0b));
    g.fillRoundedRectangle (r.reduced (layout::pillBevel), rad - layout::pillBevel);
    g.setColour (Colour (0xff78787c).withAlpha (0.35f));
    g.drawRoundedRectangle (r.reduced (0.4f), rad, 0.8f);

    String status; float a = 0.0f;
    if (! statusLineState (status, a)) a = 0.0f;
    const float pa = 1.0f - a;
    const Font f (FontOptions (medFace).withPointHeight (23.0f));   // Poppins Medium 23 unites (barre de Strong Pickle)
    const float aw = 34.0f;
    if (pa > 0.0f)
    {
        auto arrow = [&] (Rectangle<float> ar, bool left, bool hot)
        {
            Path p; const auto cc = ar.getCentre(); const float sz = 5.5f;
            if (left) p.addTriangle (cc.x + sz * 0.6f, cc.y - sz, cc.x + sz * 0.6f, cc.y + sz, cc.x - sz * 0.8f, cc.y);
            else      p.addTriangle (cc.x - sz * 0.6f, cc.y - sz, cc.x - sz * 0.6f, cc.y + sz, cc.x + sz * 0.8f, cc.y);
            g.setColour ((hot ? Colours::white : kCream.withAlpha (0.6f)).withMultipliedAlpha (pa));
            g.fillPath (p);
        };
        arrow (r.withWidth (aw), true, hover == Hit::PillPrev);
        arrow (r.withTrimmedLeft (r.getWidth() - aw), false, hover == Hit::PillNext);
        Colour dot;
        const auto line = presetLine (dot);
        if (! dot.isTransparent())
        {
            const float dr = 4.2f, dx = r.getX() + aw + 8.0f;
            g.setColour (dot.withMultipliedAlpha (pa));
            g.fillEllipse (dx - dr, r.getCentreY() - dr, dr * 2.0f, dr * 2.0f);
        }
        g.setFont (f);
        g.setColour (kCream.withAlpha ((hover == Hit::PillName ? 1.0f : 0.92f) * pa));
        g.drawFittedText (line, r.reduced (aw + 14.0f, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
    if (a > 0.0f)
    {
        g.setFont (f);
        g.setColour (kCream.withAlpha (a));
        g.drawFittedText (status.toUpperCase(), r.reduced (rad, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
}

void TexturalAudioProcessorEditor::paint (Graphics& g)
{
    lastPaintMs = nowMs();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (0xff111112));
    if (bgCache.isValid())
    {
        g.setImageResamplingQuality (Graphics::lowResamplingQuality);
        g.drawImage (bgCache, getLocalBounds().toFloat());
        g.addTransform (AffineTransform::scale (scale()));
    }
    else
    {
        g.addTransform (AffineTransform::scale (scale()));
        g.drawImage (background, Rectangle<float> (0, 0, kW, kH));
        drawPrint (g);
    }
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
    const Layer layer = currentLayer();

    // halos (sous les commandes), puis LEDs
    const float rev = reverseAmount (layer);
    int mci; float mamt;
    modeLedState (layer, mci, mamt);
    const float st = statusLedAmount (layer);
    drawGlow (g, glowRev, layout::glow_rev, rev);
    drawGlow (g, glowMode[mci == cGreen ? 0 : mci == cOrange ? 1 : 2], layout::glow_mode_red, mamt);
    drawGlow (g, glowStatus, layout::glow_status, st);
    drawLed (g, layout::revPos, ledOff[cCyan], ledOn[cCyan], rev);
    drawLed (g, layout::modePos, ledOff[mci], ledOn[mci], mamt);
    drawLed (g, layout::ledPos, ledOff[cBlue], ledOn[cBlue], st);

    for (int i = 0; i < 6; ++i)
        drawKnob (g, i, anglesInit ? shownAngle[i] : kKnobA0 + (kKnobA1 - kKnobA0) * knobValue (layer, i), blurLevel[i]);

    // footswitch enfonce : bouton assombri tant qu'on appuie (fonctionnement d'Echoflex)
    if (pressedHit == Hit::Footswitch)
    {
        const float r = layout::fsBtnR;
        ColourGradient sh (Colours::black.withAlpha (0.28f), layout::fsPos.x, layout::fsPos.y,
                           Colours::black.withAlpha (0.10f), layout::fsPos.x + r, layout::fsPos.y, true);
        g.setGradientFill (sh);
        g.fillEllipse (layout::fsPos.x - r, layout::fsPos.y - r, r * 2.0f, r * 2.0f);
    }

    drawPill (g);
}
