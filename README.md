# Зачем

Я рот ебал стандартных медицинских иконок, ебало к осмотру когда у тебя есть 5 секунд найти кислородит среди 30 одинаковых шприцов

# О моде

Мод меняет все ванильные медицинские шприцы на собственные иконки. В игре 5 классов медицины: Medicine, Basic Chemicals, Toxins, Antidotes, Stimulants. У каждого класса медицины своя икона, которая уже внутри класса различается по цветам/значкам статусов. В конце описания есть таблица всех замененных иконок.

**Мод SERVER-SIDE, требуется подписка хоста.**

# Совместимость

- Текстурпак работает исправно со всеми модами, не изменяющими ванильные предметы выше.
- При наличии модов, меняющих ванилу, переместите этот текстурпак в конец списка. В таком случае приоритетность текстур будет ниже, поэтому некоторые могут не отображаться.
- Вы можете вручную переписать моды, чтобы они ссылались на текстуры отсюда. Об этом пункт ниже.

# Редактирование мода

Вы можете скопировать этот мод в локальные и изменять его там, как хотите. Структура мода описана в файле `AGENTS.md`.

В других модах можно ссылаться на текстуры этого мода. Замените в локальных версиях модов в `.xml` файлах ссылку на текстуру с `Content` на `QoL - Medical icons`.

# Как создавался

Я вообще не умею рисовать, да и с чувством вкуса было так себе. Весь мод написан и нарисован нейронкой Codex 5.5 (да, я генерил картинки на Кодексе). Мод выложен на GitHub: https://github.com/WantBeASleep/MedicalIcons. Буду рад идеям и контрибутам.

Благодарность создателю мода https://steamcommunity.com/sharedfiles/filedetails/?id=3539579595 за вдохновение и творческий ориентир.

--------------------------------------------------------

# English version

## Why

Fuck the default medical icons. It is a pain in the ass when you have five seconds to find Liquid Oxygenite in a pile of thirty almost identical syringes.

## About

This mod replaces vanilla Barotrauma medical syringe icons with custom ones. The items are split into 5 visual classes: Medicine, Basic Chemicals, Toxins, Antidotes, and Stimulants. Each class has its own base shape, then individual items differ by color and status-affliction marks. A full replacement table is included below.

**This is a SERVER-SIDE mod. The host must be subscribed.**

## Compatibility

- The texture pack should work with mods that do not override the same vanilla medical items.
- If you use mods that change vanilla medical items, move this texture pack to the end of the mod list. In that case its texture priority will be lower, so some replacements may not appear.
- Other local mods can be edited manually to reference textures from this mod. See the note below.

## Editing

You can copy this mod to your local mods folder and edit it however you want. The project structure is described in `AGENTS.md`.

Other mods can reference textures from this mod. In local `.xml` files, replace texture paths that start with `Content` with paths that point to `QoL - Medical icons`.

## Creation

I cannot really draw, and my taste was not exactly carrying the project either. The whole mod was written and drawn with Codex 5.5 (yes, I generated the images in Codex). GitHub: https://github.com/WantBeASleep/MedicalIcons. Ideas and contributions are welcome.

Thanks to the creator of the mod https://steamcommunity.com/sharedfiles/filedetails/?id=3539579595 for the inspiration and creative reference point.

--------------------------------------------------------

# Item table

| Identifier | Icon | Sprite |
|---|---|---|
| `adrenaline` | ![adrenaline icon](devspace/textures/ampoule/items/adrenaline/icon.png) | ![adrenaline sprite](devspace/textures/ampoule/items/adrenaline/sprite.png) |
| `antibiotics` | ![antibiotics icon](devspace/textures/ampoule/items/antibiotics/icon.png) | ![antibiotics sprite](devspace/textures/ampoule/items/antibiotics/sprite.png) |
| `opium` | ![opium icon](devspace/textures/ampoule/items/opium/icon.png) | ![opium sprite](devspace/textures/ampoule/items/opium/sprite.png) |
| `stabilozine` | ![stabilozine icon](devspace/textures/ampoule/items/stabilozine/icon.png) | ![stabilozine sprite](devspace/textures/ampoule/items/stabilozine/sprite.png) |
| `chloralhydrate` | ![chloralhydrate icon](devspace/textures/dart_syringe/items/chloralhydrate/icon.png) | ![chloralhydrate sprite](devspace/textures/dart_syringe/items/chloralhydrate/sprite.png) |
| `cyanide` | ![cyanide icon](devspace/textures/dart_syringe/items/cyanide/icon.png) | ![cyanide sprite](devspace/textures/dart_syringe/items/cyanide/sprite.png) |
| `deliriumine` | ![deliriumine icon](devspace/textures/dart_syringe/items/deliriumine/icon.png) | ![deliriumine sprite](devspace/textures/dart_syringe/items/deliriumine/sprite.png) |
| `europabrew` | ![europabrew icon](devspace/textures/dart_syringe/items/europabrew/icon.png) | ![europabrew sprite](devspace/textures/dart_syringe/items/europabrew/sprite.png) |
| `huskeggs` | ![huskeggs icon](devspace/textures/dart_syringe/items/huskeggs/icon.png) | ![huskeggs sprite](devspace/textures/dart_syringe/items/huskeggs/sprite.png) |
| `morbusine` | ![morbusine icon](devspace/textures/dart_syringe/items/morbusine/icon.png) | ![morbusine sprite](devspace/textures/dart_syringe/items/morbusine/sprite.png) |
| `paralyzant` | ![paralyzant icon](devspace/textures/dart_syringe/items/paralyzant/icon.png) | ![paralyzant sprite](devspace/textures/dart_syringe/items/paralyzant/sprite.png) |
| `radiotoxin` | ![radiotoxin icon](devspace/textures/dart_syringe/items/radiotoxin/icon.png) | ![radiotoxin sprite](devspace/textures/dart_syringe/items/radiotoxin/sprite.png) |
| `raptorbaneextract` | ![raptorbaneextract icon](devspace/textures/dart_syringe/items/raptorbaneextract/icon.png) | ![raptorbaneextract sprite](devspace/textures/dart_syringe/items/raptorbaneextract/sprite.png) |
| `sufforin` | ![sufforin icon](devspace/textures/dart_syringe/items/sufforin/icon.png) | ![sufforin sprite](devspace/textures/dart_syringe/items/sufforin/sprite.png) |
| `sulphuricacidsyringe` | ![sulphuricacidsyringe icon](devspace/textures/dart_syringe/items/sulphuricacidsyringe/icon.png) | ![sulphuricacidsyringe sprite](devspace/textures/dart_syringe/items/sulphuricacidsyringe/sprite.png) |
| `antidama1` | ![antidama1 icon](devspace/textures/insulin_syringe/items/antidama1/icon.png) | ![antidama1 sprite](devspace/textures/insulin_syringe/items/antidama1/sprite.png) |
| `antidama2` | ![antidama2 icon](devspace/textures/insulin_syringe/items/antidama2/icon.png) | ![antidama2 sprite](devspace/textures/insulin_syringe/items/antidama2/sprite.png) |
| `deusizine` | ![deusizine icon](devspace/textures/insulin_syringe/items/deusizine/icon.png) | ![deusizine sprite](devspace/textures/insulin_syringe/items/deusizine/sprite.png) |
| `liquidoxygenite` | ![liquidoxygenite icon](devspace/textures/insulin_syringe/items/liquidoxygenite/icon.png) | ![liquidoxygenite sprite](devspace/textures/insulin_syringe/items/liquidoxygenite/sprite.png) |
| `pomegrenadeextract` | ![pomegrenadeextract icon](devspace/textures/insulin_syringe/items/pomegrenadeextract/icon.png) | ![pomegrenadeextract sprite](devspace/textures/insulin_syringe/items/pomegrenadeextract/sprite.png) |
| `combatstimulantsyringe` | ![combatstimulantsyringe icon](devspace/textures/pocket_injector/items/combatstimulantsyringe/icon.png) | ![combatstimulantsyringe sprite](devspace/textures/pocket_injector/items/combatstimulantsyringe/sprite.png) |
| `hyperzine` | ![hyperzine icon](devspace/textures/pocket_injector/items/hyperzine/icon.png) | ![hyperzine sprite](devspace/textures/pocket_injector/items/hyperzine/sprite.png) |
| `meth` | ![meth icon](devspace/textures/pocket_injector/items/meth/icon.png) | ![meth sprite](devspace/textures/pocket_injector/items/meth/sprite.png) |
| `pressurestabilizer` | ![pressurestabilizer icon](devspace/textures/pocket_injector/items/pressurestabilizer/icon.png) | ![pressurestabilizer sprite](devspace/textures/pocket_injector/items/pressurestabilizer/sprite.png) |
| `steroids` | ![steroids icon](devspace/textures/pocket_injector/items/steroids/icon.png) | ![steroids sprite](devspace/textures/pocket_injector/items/steroids/sprite.png) |
| `antinarc` | ![antinarc icon](devspace/textures/vial/items/antinarc/icon.png) | ![antinarc sprite](devspace/textures/vial/items/antinarc/sprite.png) |
| `antiparalysis` | ![antiparalysis icon](devspace/textures/vial/items/antiparalysis/icon.png) | ![antiparalysis sprite](devspace/textures/vial/items/antiparalysis/sprite.png) |
| `antipsychosis` | ![antipsychosis icon](devspace/textures/vial/items/antipsychosis/icon.png) | ![antipsychosis sprite](devspace/textures/vial/items/antipsychosis/sprite.png) |
| `antirad` | ![antirad icon](devspace/textures/vial/items/antirad/icon.png) | ![antirad sprite](devspace/textures/vial/items/antirad/sprite.png) |
| `calyxanide` | ![calyxanide icon](devspace/textures/vial/items/calyxanide/icon.png) | ![calyxanide sprite](devspace/textures/vial/items/calyxanide/sprite.png) |
| `cyanideantidote` | ![cyanideantidote icon](devspace/textures/vial/items/cyanideantidote/icon.png) | ![cyanideantidote sprite](devspace/textures/vial/items/cyanideantidote/sprite.png) |
| `deliriumineantidote` | ![deliriumineantidote icon](devspace/textures/vial/items/deliriumineantidote/icon.png) | ![deliriumineantidote sprite](devspace/textures/vial/items/deliriumineantidote/sprite.png) |
| `morbusineantidote` | ![morbusineantidote icon](devspace/textures/vial/items/morbusineantidote/icon.png) | ![morbusineantidote sprite](devspace/textures/vial/items/morbusineantidote/sprite.png) |
| `sufforinantidote` | ![sufforinantidote icon](devspace/textures/vial/items/sufforinantidote/icon.png) | ![sufforinantidote sprite](devspace/textures/vial/items/sufforinantidote/sprite.png) |
