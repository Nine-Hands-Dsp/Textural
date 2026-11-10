# Textural (NINE HANDS | DSP) — VST3 granulaire pour Windows et macOS

Moteur de synthèse granulaire inspiré de la pédale MXR Textures M310 : trois modes (Delay, Auto Freeze, Layers), grains inversés, pitch ±2 octaves, régénération delay/granulaire, randomisations, reverb, filtre LP/HP 4 pôles, vibrato, tap tempo, trails, sorties Mono / Wet-Dry / Stéréo, 8 presets d'usine et contrôle MIDI complet.

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Textural/releases/latest/download/Textural-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Textural/releases/latest/download/Textural-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Textural/releases/latest/download/Textural-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-919496?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Textural/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Textural?label=derni%C3%A8re%20version&color=919496"></a>
</p>

## Compiler avec GitHub

1. Pousse **tous les fichiers à la racine** du dépôt (images du plugin générées par `tools/make_art.py` avec `FINAL=1`, et le dossier `.github/workflows`).
   Les boutons ci-dessus téléchargent toujours la dernière version.
2. GitHub Actions compile automatiquement (onglet **Actions** → dernier run → *Artifacts*) :
   - `Textural-Setup-Windows` : installeur `Textural-Setup.exe` (copie le plugin dans `C:\Program Files\Common Files\VST3`) ;
   - `Textural-VST3-Windows` : le dossier `Textural.vst3` à copier soi-même dans `C:\Program Files\Common Files\VST3`.
3. Relance un scan des plugins dans ton DAW : le plugin apparaît sous **Textural**, fabricant **NINE HANDS | DSP**.

## Les trois modes (LED MODE, entre SIZE et OVERLAP)

La LED du bouton prend la couleur du symbole du mode et clignote quand le son est gelé. Le nom du mode s'affiche dans la ligne d'état.

- **Delay (vert)** : l'entrée est enregistrée en continu et rejouée en grains, TIME derrière la tête d'écriture. REGEN réinjecte la sortie delay et/ou la sortie des grains (Regen Mix).
- **Auto Freeze (orange)** : à chaque note ou accord détecté, la pédale enregistre pendant TIME puis gèle le buffer. Les grains y puisent sans fin, ce qui donne une nappe qui évolue. Une nouvelle note remplace la précédente.
- **Layers (rouge)** : jusqu'à 4 notes ou accords dans 4 buffers indépendants (le 5e remplace le plus ancien). TIME règle le fondu d'entrée (attaque) et REGEN le fondu de sortie (déclin), comme une voix de synthé. C'est le mode synthé polyphonique : monte REGEN pour tenir les notes.

## Utilisation

| Action | Effet |
|---|---|
| Glisser un potard (haut/bas) | Réglage ; **Maj** = réglage fin ; double-clic = valeur par défaut ; molette OK. La couronne tourne avec l'index, avec un flou de mouvement quand on tourne vite |
| Clic sur la LED REVERSE | Reverse on/off (LED cyan) : la guitare enregistrée est rejouée à l'envers, phrase par phrase |
| Clic sur la LED MODE | Delay (vert) → Auto Freeze (orange) → Layers (rouge) ; la LED prend la couleur du symbole et clignote quand le son est gelé |
| Clic footswitch | Effet on/off dès l'appui (LED bleue) |
| Maintien footswitch | Freeze momentané (Delay/Layers) ; en Auto Freeze, le maintien *dé-gèle*. Si *Footswitch Hold Mode* = Preset Scroll : maintien = entrer/sortir du défilement, clic = preset suivant |
| Barre de presets | ◀ / ▶ = preset précédent / suivant ; clic sur le nom = liste des presets. Point vert = 1-4, rouge = 5-8, « * » = modifié. Pendant un réglage, la ligne d'état prend sa place puis s'efface |
| Clic droit (menu ouvert là où on clique) | **Glow** : intensité des halos des LEDs (25 / 50 / 75 / 100 %) ; **Plugin size** : 60 %, 75 %, 100 % (jamais plus petit que 60 % ; la taille par défaut porte la mention « (default) ») ; sous-menu **Default size (new windows)** = taille d'ouverture des nouvelles fenêtres, commune à toutes les instances (une taille sauvegardée avec le projet pour une instance reste prioritaire) ; sauvegarde/réinitialisation des presets |

### Paramètres secondaires (comme maintenir les boutons de la pédale)

- **Ctrl + glisser** (ou appui long sur REVERSE pour verrouiller) : Time Random, Size Random, Overlap Random, Regen Mix (Delay ↔ Granular), Pitch Random, Reverse Random.
- **Alt + glisser** (ou appui long sur MODE) : Reverb Mix, Filter Cutoff (LP < midi < HP), Vibrato Rate, Reverb Decay, Quantize Pitch, Vibrato Depth.
- **Ctrl + Alt + glisser** (ou clic sur la LED bleue) : Preset Scroll Mute, Trails, Output Mode, Footswitch Hold Mode, Output Gain.
- **Tap tempo** : Ctrl + clic sur MODE (ou REVERSE verrouillé puis clic sur MODE), ou un CC appris (MIDI Learn : Tap Tempo).

La ligne d'état s'affiche dans la barre de presets pendant les réglages (valeur du potard, mode, tap tempo, MIDI Learn), puis la barre de presets revient.

## MIDI

**MIDI Learn** : clic droit sur une commande (potard dans la couche active : normale, Ctrl, Alt ou Ctrl + Alt ; REVERSE, MODE, footswitch, flèche ▶ de la barre de presets) -> « MIDI Learn », puis bouger la pédale d'expression / appuyer sur le bouton MIDI ; « Clear MIDI » retire l'assignation. Le sous-menu MIDI liste toutes les commandes (dont Freeze et Tap Tempo) et « Clear all MIDI assignments » efface toutes les assignations. Les assignations sont sauvegardées avec le projet.

Program Change 1-8 = emplacements (2 = Live, 0 = Live aussi), 9 = Slow Attack Soundtrack. Dans la liste des presets du DAW : 1 Sea Synth … 8 Stardust Cloud, puis Slow Attack Soundtrack. Tous les paramètres sont aussi automatisables dans le DAW.

Aucun CC assigné par défaut : clic droit > MIDI > Learn.

## Presets d'usine

À l'ouverture, la pédale charge le preset 1 (Sea Synth). Les flèches de la barre de presets font défiler les presets.

Verts :
1. Sea Synth : synthé polyphonique ondulant.
2. **Live** : les réglages courants des potards, non sauvegardable.
3. Crystal Cave : boucles d'octaves régénérées.
4. Melodic Kaleidoscope : mélodies gelées, à l'endroit, à l'envers, à d'autres octaves.

Rouges :
5. Obligatory Shimmer : Regen Mix 83/17 delay/granulaire.
6. Reverse Reverb : écho inversé, chaque tranche d'environ 0,9 s de guitare est rejouée à l'envers puis passe dans la reverb.
7. Mellow Cello : nappe une octave plus bas avec vibrato, plus présente après la note.
8. Stardust Cloud : synthé granulaire en Layers avec une pluie de particules.

**Slow Attack Soundtrack** (Layers, attaque 587 ms, déclin 17,76 s, pitch −7 demi-tons, size 203 ms, overlap 18, mix 38 %) n'occupe aucun emplacement de la pédale. On le charge depuis la liste des presets du DAW (programme 9, Program Change 9) ou depuis la barre de presets.

## Moteur audio

- **Grains** : enveloppe en cosinus qui s'adapte à OVERLAP (Hann quand les grains se chevauchent, fondu de 20 % au minimum), si bien que deux grains successifs se recouvrent toujours.
- **Alignement de phase (type WSOLA)** : quand les grains sont peu nombreux, chaque nouveau grain est décalé de ±12 ms pour être en phase avec ceux qui jouent déjà, et le niveau est normalisé par la somme des fenêtres. Un son tenu garde ainsi un niveau constant, sans creux ni décrochage, y compris en reverse.
- **Reverse** : les grains inversés ne lisent que de l'audio déjà enregistré et ne croisent jamais la tête d'écriture, donc aucun clic.
- **REVERSE** (modes Delay et Auto Freeze) : un flux dédié rejoue la guitare enregistrée à l'envers, tranche par tranche, comme un reverse delay. SIZE règle la longueur des tranches (0,25 à 2 s), TIME le retard, et Reverse Random le dosage entre son inversé et grains (10 à 100 %). Les tranches s'enchaînent avec un fondu de 20 % aligné en phase : le son est continu et sans clic. En mode Layers, REVERSE inverse les grains des voix.
- **Diffuseur** : un réseau de filtres passe-tout, sur le principe de Mutable Instruments Clouds, fond les grains en nappe quand OVERLAP est élevé.
- **Reverb** : plate de Dattorro modulée, de la petite pièce jusqu'au maintien infini.
- **Stéréo** : panoramique et léger décalage gauche/droite par grain.
- **Mode Layers** : chaque voix a une légère dérive de hauteur, façon synthé analogique.

## Fonctions cachées (sans boutons supplémentaires)

- **MIX au-delà de 75 %** : ajoute progressivement un nuage de particules granulaires (grains de 10 à 45 ms, panoramiques aléatoires, à l'octave ou à la douzième selon Pitch Random, inversés selon Reverse).
- **Pitch Random** : le premier tiers donne un désaccord « unisson » façon synthé (jusqu'à ±30 cents). Au-delà, les grains sautent d'intervalle harmonique.
- **Time Random au-delà de 45 %** : effet glitch, certains grains rejouent la tranche précédente (stutter).
- **Delay** : en sortie Stéréo, les répétitions font du ping-pong. Le filtre colore les répétitions : sous midi, écho analogique sombre ; au-dessus, son lo-fi aminci. Vibrato Depth ajoute un wow de bande sur les répétitions.
- **Reverb** : queue modulée et diffuse. Reverb Decay va de 0,4 s à 60 s puis passe en infini en fin de course. Le filtre éclaircit ou assombrit la queue.
- **Filtre** : la résonance augmente quand on s'éloigne de midi, ce qui donne des balayages façon synthé.
- **Mode Layers** : saturation douce de type synthé analogique.

Les presets utilisateur sont enregistrés dans le projet du DAW et dans `%APPDATA%\NINE HANDS | DSP\Textural\UserPresets.xml`.

## Versions

- v1.1.0 : anti-gel v2 (JUCE 8.0.15, caches refaits par le timer, chien de garde, aucun appel à l'hôte depuis le thread audio)

- v1.1.1 : menu de taille de fenêtre : « 60 % (default) », 75 %, 100 % (plus de taille en pixels)

- v1.2.0 : MIDI Learn au clic droit sur chaque commande (Clear MIDI, assignations sauvegardées avec le projet)

- v1.3.0 : clic droit > Plugin size > Default size (new windows) : taille par défaut des nouvelles fenêtres au choix, comme dans Octopus

- v1.3.1 : plus aucun CC MIDI assigné par défaut (tout passe par le MIDI Learn)

- v2.0.0 : refonte NINE HANDS | DSP : visuel 1235 x 1800 (motif de particules, logo NINE HANDS | DSP, footswitch et jacks photo), sérigraphie vectorielle, potards photo dont la couronne tourne avec l'index (flou de mouvement), LEDs photo, réglage Glow, barre de presets / ligne d'état, menus au design d'Octopus, fenêtre 60 / 75 / 100 % (493 / 719 / 958 px, jusqu'à 150 %)
