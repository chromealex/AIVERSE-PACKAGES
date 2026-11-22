# Paquets AIVERSE

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Deutsch](README.de.md) · **Français**

Catalogue de contenu optionnel pour le moteur [AIVERSE](https://github.com/chromealex/AIVERSE) : bibliothèques de matériaux, textures, modèles de projet, modèles 3D, son, effets, scripts, plugins natifs et outils. Le dépôt du moteur contient le code et un minimum de ressources ; ce qui est ici n’est téléchargé que par les projets qui en ont besoin.

Parcourez-le sur la page **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** du site du moteur : aperçus, descriptions et aperçu 3D de chaque paquet.

## Utilisation

Depuis une copie du moteur :

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # chercher
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # après le clonage d’un projet : tout ce qui est dans aiverse.lock
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # sources de création : affiche le dossier en cache
```

`add` inscrit le paquet dans `game.json` du projet → `"packages"`, installe les paquets dont il dépend et fige les versions exactes et les empreintes des fichiers dans `aiverse.lock`. Les téléchargements sont vérifiés par SHA-256 et conservés une seule fois par machine dans `~/.aiverse/packages`. Les skills du moteur indiquent les paquets dont elles ont besoin, et les agents les installent de la même façon.

## Organisation

```
index.json               catégories et {id, category, path} de chaque paquet publié
<category>/<id>/
  aiverse.package.json   manifeste, écrit par l’auteur (docs/manifest.md)
  versions.json          versions publiées, URL des archives et SHA-256 (écrit par le workflow publish)
  README.md              ce que c’est, comment l’utiliser, origine et licence
  preview.jpg            1..6 images d’aperçu, 640..2400 px de large, ≤ 1 Mo chacune
  files/                 le contenu, seulement dans la pull request (jusqu’à 2 Go, fichiers jusqu’à 100 Mo)
```

Catégories : `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`, `plugins`, `tools`. Les textes des manifestes sont en anglais (`title`, `summary`, `description`) ; les traductions s’écrivent `title-ru`, `summary-de`, etc.

Le contenu arrive dans la pull request (`files/`, jusqu’à 2 Go ; un fichier de plus de 100 Mo passe par `python3 tools/catalog.py upload <id> --repo vous/AIVERSE-PACKAGES`). Le propriétaire l’accepte avec le label `accept` au lieu de Merge : les fichiers deviennent l’archive de la release et le paquet arrive dans `main` sans eux, ils n’entrent donc jamais dans l’historique du dépôt.

## Ajouter un paquet

Uniquement par pull request ; le propriétaire relit et fusionne chaque changement. Pas à pas : [CONTRIBUTING.md](CONTRIBUTING.md) et les [instructions du site](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog). Après la fusion, le workflow `publish` publie la version et écrit `versions.json` et `index.json` ; le moteur et le site les récupèrent automatiquement.
