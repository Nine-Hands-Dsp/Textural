// Captures de la fenetre de Textural (Linux, sans affichage) : textural_<h>.png et presets p<n>.png
#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "PluginEditor.h"
using namespace juce;

static void save (Component& c, const File& f, float sc)
{
    auto im = c.createComponentSnapshot (c.getLocalBounds(), true, sc);
    f.deleteFile(); FileOutputStream os (f); PNGImageFormat().writeImageToStream (im, os);
}

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI gui;
    const File out (argc > 1 ? argv[1] : "render");
    out.createDirectory();
    for (int h : { 493, 958 })
    {
        TexturalAudioProcessor p;
        p.selectPreset (1);
        std::unique_ptr<AudioProcessorEditor> ed (p.createEditor());
        ed->setSize (roundToInt (h * TexturalAudioProcessorEditor::kW / TexturalAudioProcessorEditor::kH), h);
        auto* te = dynamic_cast<TexturalAudioProcessorEditor*> (ed.get());
        te->forceRenderScale (h == 493 ? 2.0f : 1.0f);
        save (*ed, out.getChildFile ("textural_" + String (h) + ".png"), h == 493 ? 2.0f : 1.0f);
    }
    for (int pr = 1; pr <= 9; ++pr)
    {
        TexturalAudioProcessor p;
        p.selectPreset (pr);
        std::unique_ptr<AudioProcessorEditor> ed (p.createEditor());
        ed->setSize (roundToInt (958 * TexturalAudioProcessorEditor::kW / TexturalAudioProcessorEditor::kH), 958);
        dynamic_cast<TexturalAudioProcessorEditor*> (ed.get())->forceRenderScale (1.0f);
        save (*ed, out.getChildFile ("p" + String (pr) + ".png"), 1.0f);
    }
    return 0;
}
