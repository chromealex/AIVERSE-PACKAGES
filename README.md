# AIVERSE packages

**English** · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

Catalog of optional content for the [AIVERSE](https://github.com/chromealex/AIVERSE) engine: material
libraries, textures, project templates, models, sound, effects, scripts, native plugins and tools.
The engine repository carries code and a minimal set of assets; everything here is downloaded only by
the projects that need it.

Browse it on the **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** page of the engine
website: previews, descriptions and a 3D preview of every package.

## Use

From an engine checkout:

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # find
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # after cloning a project: everything from aiverse.lock
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # authoring sources: print the cached folder
```

`add` records the package in the project's `game.json` → `"packages"`, installs the packages it
depends on and pins the exact versions and file hashes in `aiverse.lock`. Downloads are verified by
SHA-256 and kept once per machine in `~/.aiverse/packages`. Engine skills name the packages they need,
so agents install them the same way.

## Layout

```
index.json               categories and {id, category, path} of every published package
<category>/<id>/
  aiverse.package.json   manifest, written by the author (docs/manifest.md)
  versions.json          published versions, archive URLs and SHA-256 (written by the publish workflow)
  README.md              what it is, how to use it, origin and licence
  preview.jpg            1..6 preview images, 640..2400 px wide, <= 1 MB each
  files/                 the payload, for small packages (<= 25 MB, files <= 10 MB)
```

Categories: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`,
`plugins`, `tools`. Texts in manifests are English (`title`, `summary`, `description`); translations
are `title-ru`, `summary-de` and so on.

## Add a package

Pull requests only; the owner reviews and merges every change. Step by step:
[CONTRIBUTING.md](CONTRIBUTING.md) and the
[instructions on the website](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog).
After the merge the `publish` workflow releases the version and writes `versions.json` and
`index.json`; the engine and the website pick it up automatically.
