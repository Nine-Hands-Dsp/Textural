cmake_minimum_required(VERSION 3.22)

project(Textural VERSION 2.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# Static MSVC runtime: no Visual C++ redistributable needed on the target PC
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

include(FetchContent)
FetchContent_Declare(
    JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG        8.0.15
    GIT_SHALLOW    TRUE)
FetchContent_MakeAvailable(JUCE)

juce_add_plugin(Textural
    COMPANY_NAME                "NINE HANDS | DSP"
    PRODUCT_NAME                "Textural"
    VERSION                     2.1.0
    PLUGIN_MANUFACTURER_CODE    Swga
    PLUGIN_CODE                 Txtl
    FORMATS                     VST3
    IS_SYNTH                    FALSE
    NEEDS_MIDI_INPUT            TRUE
    NEEDS_MIDI_OUTPUT           FALSE
    IS_MIDI_EFFECT              FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    VST3_CATEGORIES             Fx Delay Reverb
    COPY_PLUGIN_AFTER_BUILD     FALSE)

juce_generate_juce_header(Textural)

# visuel NINE HANDS | DSP (genere par tools/make_art.py, FINAL=1)
juce_add_binary_data(TexturalData SOURCES
    background.png
    knob_black.png knob_orange.png knob_index_black.png knob_index_orange.png
    led_cyan_on.png led_cyan_off.png led_green_on.png led_green_off.png led_orange_on.png led_orange_off.png
    led_red_on.png led_red_off.png led_blue_on.png led_blue_off.png
    glow_rev.png glow_mode_green.png glow_mode_orange.png glow_mode_red.png glow_status.png
    assets/fonts/Poppins-Bold.ttf assets/fonts/Poppins-Medium.ttf
    assets/NineHands_Logo_Black.svg)

target_sources(Textural PRIVATE
    PluginProcessor.cpp
    PluginEditor.cpp
    GranularEngine.cpp)


# verrou de taille de la fenetre du DAW (jamais sous 60 %, jamais au-dela de 150 %)
if(APPLE)
  target_sources(Textural PRIVATE WindowMinSize.mm)
  target_link_libraries(Textural PRIVATE "-framework Cocoa")
else()
  target_sources(Textural PRIVATE WindowMinSize.cpp)
endif()
if(WIN32)
  target_link_libraries(Textural PRIVATE comctl32 user32)
endif()
target_compile_definitions(Textural PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    JUCE_DISPLAY_SPLASH_SCREEN=0)

target_link_libraries(Textural
    PRIVATE
        TexturalData
        juce::juce_audio_processors
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags)
