# AIVERSE-Pakete

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · **Deutsch** · [Français](README.fr.md)

Katalog mit optionalen Inhalten für die Engine [AIVERSE](https://github.com/chromealex/AIVERSE): Materialbibliotheken, Texturen, Projektvorlagen, Modelle, Sound, Effekte, Skripte, native Plugins und Werkzeuge. Das Engine-Repository enthält Code und nur wenige Assets; alles hier laden nur die Projekte herunter, die es brauchen.

Durchsuchen Sie ihn auf der Seite **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** der Engine-Website: Vorschaubilder, Beschreibungen und eine 3D-Vorschau jedes Pakets.

## Verwendung

Aus einem Engine-Checkout:

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # suchen
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # nach dem Klonen eines Projekts: alles aus aiverse.lock
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # Authoring-Quellen: Ordner im Cache ausgeben
```

`add` trägt das Paket in `game.json` des Projekts → `"packages"` ein, installiert die Pakete, von denen es abhängt, und hält die genauen Versionen und Datei-Hashes in `aiverse.lock` fest. Downloads werden per SHA-256 geprüft und pro Rechner einmal in `~/.aiverse/packages` abgelegt. Engine-Skills nennen die Pakete, die sie brauchen, und Agenten installieren sie auf dieselbe Weise.

## Aufbau

```
index.json               Kategorien und {id, category, path} jedes veröffentlichten Pakets
<category>/<id>/
  aiverse.package.json   Manifest, vom Autor geschrieben (docs/manifest.md)
  versions.json          veröffentlichte Versionen, Archiv-URLs und SHA-256 (vom Workflow publish geschrieben)
  README.md              was es ist, wie man es nutzt, Herkunft und Lizenz
  preview.jpg            1..6 Vorschaubilder, 640..2400 px breit, je ≤ 1 MB
  files/                 der Inhalt, nur im Pull Request (bis 2 GB, Dateien bis 100 MB)
```

Kategorien: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`, `plugins`, `tools`. Texte in Manifesten sind englisch (`title`, `summary`, `description`); Übersetzungen heißen `title-ru`, `summary-de` usw.

Der Inhalt kommt im Pull Request (`files/`, bis 2 GB; eine Datei über 100 MB über `python3 tools/catalog.py upload <id> --repo du/AIVERSE-PACKAGES`). Der Eigentümer nimmt ihn mit dem Label `accept` statt Merge an: Die Dateien werden zum Release-Archiv, und das Paket kommt ohne sie nach `main`, sodass sie nie in die Historie des Repositorys gelangen.

## Ein Paket hinzufügen

Nur per Pull Request; der Eigentümer prüft und merged jede Änderung. Schritt für Schritt: [CONTRIBUTING.md](CONTRIBUTING.md) und die [Anleitung auf der Website](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog). Nach dem Merge veröffentlicht der Workflow `publish` die Version und schreibt `versions.json` und `index.json`; Engine und Website übernehmen das automatisch.
