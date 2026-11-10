# Outil hors plugin : compile le processeur + la fenetre de TEXTURAL sous Linux et exporte des captures PNG (apercu, notice)
# cmake -S tools/render -B build-render -DJUCE_DIR=<JUCE 8.0.15> && cmake --build build-render -j4
cmake_minimum_required(VERSION 3.22)
project(TexturalRender VERSION 2.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
set(W ${CMAKE_CURRENT_SOURCE_DIR}/../..)
juce_add_binary_data(TexturalData SOURCES
  ${W}/background.png
  ${W}/knob_black.png ${W}/knob_orange.png ${W}/knob_index_black.png ${W}/knob_index_orange.png
  ${W}/led_cyan_on.png ${W}/led_cyan_off.png ${W}/led_green_on.png ${W}/led_green_off.png ${W}/led_orange_on.png ${W}/led_orange_off.png
  ${W}/led_red_on.png ${W}/led_red_off.png ${W}/led_blue_on.png ${W}/led_blue_off.png
  ${W}/glow_rev.png ${W}/glow_mode_green.png ${W}/glow_mode_orange.png ${W}/glow_mode_red.png ${W}/glow_status.png
  ${W}/assets/fonts/Poppins-Bold.ttf ${W}/assets/fonts/Poppins-Medium.ttf ${W}/assets/NineHands_Logo_Black.svg)
juce_add_console_app(TexturalRender PRODUCT_NAME "TexturalRender")
juce_generate_juce_header(TexturalRender)
target_sources(TexturalRender PRIVATE main.cpp ${W}/PluginProcessor.cpp ${W}/PluginEditor.cpp ${W}/GranularEngine.cpp)
target_include_directories(TexturalRender PRIVATE ${W})
target_compile_definitions(TexturalRender PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_ALSA=0 JUCE_JACK=0
  JUCE_USE_XRANDR=0 JUCE_USE_XINERAMA=0 JUCE_USE_XCURSOR=0 JUCE_USE_XSHM=0 JucePlugin_Name="Textural" JucePlugin_Build_VST3=0
  JucePlugin_VersionString="2.0.0" JUCE_STANDALONE_APPLICATION=1 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(TexturalRender PRIVATE TexturalData juce::juce_audio_utils juce::juce_dsp juce::juce_recommended_config_flags)
