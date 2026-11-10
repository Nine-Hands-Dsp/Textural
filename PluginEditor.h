#pragma once
#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "NineHandsMenu.h"

//==============================================================================
//  Textural (NINE HANDS | DSP) v2 : pedale simple, fond 1235 x 1800 px (tools/make_art.py, FINAL=1).
//  Repere du plugin : 617,5 x 900 unites (Layout.h). Fenetre 493 px (« 60 % ») / 719 / 958, jusqu'a 150 %.
//
//  Dessine par le plugin : serigraphie vectorielle (textes, filets, arc du PITCH, graduations, titre, symboles
//  des modes, logo), potards (corps periodique a 10 crans + index, flou de mouvement), LEDs (photo fournie),
//  halos (reglage Glow), footswitch enfonce, pastille presets / ligne d'etat.
//
//  Couches secondaires (comme maintenir les boutons de la pedale) :
//    Ctrl  + glisser un potard -> couche REVERSE   (ou appui long sur REVERSE pour verrouiller)
//    Alt   + glisser           -> couche MODE      (ou appui long sur MODE)
//    Ctrl+Alt + glisser        -> couche FOOTSWITCH (ou clic sur la LED bleue)
//==============================================================================
class TexturalAudioProcessorEditor : public juce::AudioProcessorEditor,
                                     private juce::Timer
{
public:
    explicit TexturalAudioProcessorEditor (TexturalAudioProcessor&);
    ~TexturalAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;

    void mouseDown (const juce::MouseEvent&) override;
    void mouseDrag (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;
    void mouseDoubleClick (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;

    static constexpr float kW = 617.5f, kH = 900.0f;
    static constexpr int   kDefaultH = 493, kRefH = 958, kMaxH = kRefH * 3 / 2;
    static constexpr int   kNumSizes = 3;          // 60 % (defaut d'origine) / 75 % / 100 %
    static int sizeHeight (int idx);
    void forceRenderScale (float sc) { forcedScale = sc; rebuildCaches (sc); }   // outil de rendu

private:
    enum class Layer { Main, Reverse, Mode, Foot };
    enum class Hit { None, Knob, ReverseBtn, ModeBtn, Footswitch, Led, PillPrev, PillName, PillNext };

    void timerCallback() override;
    void visibilityChanged() override;
    void useSoftwareRenderer();
    void rebuildCaches (float scale = 0.0f);
    float physicalScale() const;
    void askRepaint (juce::Rectangle<int> r);
    juce::Rectangle<int> zone (juce::Rectangle<float> r) const;
    juce::Rectangle<int> zone (juce::Point<float> c, float r) const { return zone (juce::Rectangle<float> (c.x - r, c.y - r, r * 2, r * 2)); }
    float scale() const { return (float) getHeight() / kH; }
    juce::Point<float> toUnits (const juce::MouseEvent& e) const { return e.position / scale(); }

    Hit  hitTest (juce::Point<float> p, int& knobIndex) const;
    Layer currentLayer() const;
    juce::String knobParamID (Layer, int knob) const;
    void showMenu (int learnIdx = -1);
    void showPresetMenu();
    int  learnIndexAt (const juce::MouseEvent&) const;
    void setHeightKeepingAspect (int h);
    void setParam (const juce::String& id, float normalised);
    void touch (const juce::String& id);
    void showKnob (int knob, const juce::String& id);
    void showMessage (const juce::String& text);

    // etat affiche
    bool  blink (double hz) const { return std::fmod (phase * hz, 1.0) < 0.5; }
    float knobValue (Layer, int knob) const;
    float reverseAmount (Layer) const;
    void  modeLedState (Layer, int& colourIdx, float& amt) const;
    float statusLedAmount (Layer) const;
    bool  statusLineState (juce::String& txt, float& alpha) const;
    juce::String presetLine (juce::Colour& dot) const;

    // dessin
    void buildPrint();
    void drawPrint (juce::Graphics&);
    void drawKnob (juce::Graphics&, int i, float value, float blur);
    void drawLed (juce::Graphics&, juce::Point<float> c, const juce::Image& off, const juce::Image& on, float amt);
    void drawGlow (juce::Graphics&, const juce::Image& img, juce::Rectangle<float> r, float amt);
    void drawPill (juce::Graphics&);

    TexturalAudioProcessor& proc;
    juce::Image background, bgCache;
    juce::Image knobStrip[2], knobIndex[2];
    enum { cCyan, cGreen, cOrange, cRed, cBlue, cNumLed };
    juce::Image ledOn[cNumLed], ledOff[cNumLed];
    juce::Image glowRev, glowMode[3], glowStatus;
    juce::Typeface::Ptr boldFace, medFace;
    std::unique_ptr<juce::Drawable> logo;
    juce::Path printPath, titlePath, linePath, halfPath, starPath, ringPath;
    NineHandsMenu::MenuLnf menuLnf;

    int cacheW = 0, cacheH = 0;
    float cacheScale = 0.0f, forcedScale = 0.0f;
    int resizeSettle = 0;
    void* lastPeer = nullptr;
    double lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0;

    // interaction
    Layer latched = Layer::Main;
    Layer dragLayer = Layer::Main;
    Hit   pressedHit = Hit::None;
    int   dragKnob = -1;
    float dragStartValue = 0, dragStartY = 0;
    juce::String dragParam;
    double pressStartMs = 0;
    bool  longPressHandled = false;
    bool  fsFreezeHeld = false;
    bool  presetScrollMode = false;
    double presetScrollUntil = 0;
    Hit   hover = Hit::None;

    int statusKnob = -1;
    juce::String statusParam, statusMsg;
    double statusMs = -1.0e9, lastMidiSeen = 0;
    bool learnMsgShown = false;
    double phase = 0;

    // animation des potards : angle affiche, niveau de flou
    float shownAngle[6] {}, blurLevel[6] {};
    bool  anglesInit = false;

    // dernier etat dessine (on ne redessine que ce qui change)
    float drawnKnob[6] = { -9, -9, -9, -9, -9, -9 }, drawnBlur[6] = { -1, -1, -1, -1, -1, -1 };
    float drawnReverse = -1, drawnMode = -1, drawnLed = -1, drawnStatusAlpha = -1;
    int   drawnModeCol = -1, drawnGlow = -1;
    juce::String drawnStatus, drawnPreset;
    Hit drawnPressed = Hit::None, drawnHover = Hit::None;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TexturalAudioProcessorEditor)
};
