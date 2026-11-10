// Captures de la fenetre de Textural (Linux, sans affichage) pour l'apercu et la notice :
//   textural_<h>.png, default.png (preset 1), bypass.png, status.png (ligne d'etat), mode<n>.png, reverse.png, p<n>.png
#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "PluginEditor.h"
using namespace juce;

static void save (Component& c, const File& f, float sc)
{
    auto im = c.createComponentSnapshot (c.getLocalBounds(), true, sc);
    f.deleteFile(); FileOutputStream os (f); PNGImageFormat().writeImageToStream (im, os);
}

template <typename Fn>
static void shot (const File& out, const String& name, int h, float sc, Fn&& prep)
{
    TexturalAudioProcessor p;
    p.selectPreset (1);
    std::unique_ptr<AudioProcessorEditor> ed (p.createEditor());
    ed->setSize (roundToInt (h * TexturalAudioProcessorEditor::kW / TexturalAudioProcessorEditor::kH), h);
    auto* te = dynamic_cast<TexturalAudioProcessorEditor*> (ed.get());
    prep (p, *te);
    te->forceRenderScale (sc);
    save (*ed, out.getChildFile (name + ".png"), sc);
}

static void setP (TexturalAudioProcessor& p, const String& id, float plain)
{
    if (auto* prm = p.param (id)) prm->setValueNotifyingHost (prm->convertTo0to1 (plain));
}

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI gui;
    const File out (argc > 1 ? argv[1] : "render");
    out.createDirectory();
    auto none = [] (TexturalAudioProcessor&, TexturalAudioProcessorEditor&) {};
    shot (out, "textural_493", 493, 2.0f, none);
    shot (out, "textural_958", 958, 1.0f, none);
    shot (out, "default", 900, 2.0f, none);
    shot (out, "bypass", 900, 2.0f, [] (TexturalAudioProcessor& p, TexturalAudioProcessorEditor&) { setP (p, PID::bypass, 1.0f); });
    shot (out, "status", 900, 2.0f, [] (TexturalAudioProcessor&, TexturalAudioProcessorEditor& e) { e.demoStatus (1); });
    for (int m = 0; m < 3; ++m)
        shot (out, "mode" + String (m), 900, 2.0f, [m] (TexturalAudioProcessor& p, TexturalAudioProcessorEditor&) { setP (p, PID::mode, (float) m); });
    shot (out, "reverse", 900, 2.0f, [] (TexturalAudioProcessor& p, TexturalAudioProcessorEditor&) { setP (p, PID::reverse, 1.0f); });
    for (int pr = 1; pr <= 9; ++pr)
        shot (out, "p" + String (pr), 900, 2.0f, [pr] (TexturalAudioProcessor& p, TexturalAudioProcessorEditor&) { p.selectPreset (pr); });
    return 0;
}
