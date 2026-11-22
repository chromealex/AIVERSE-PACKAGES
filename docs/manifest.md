# aiverse.package.json

```json
{
  "schema": 2,
  "id": "terrain-pbr",
  "version": "1.0.0",
  "kind": "content",
  "category": "materials",
  "title": "Terrain PBR materials",
  "title-ru": "PBR-материалы ландшафта",
  "summary": "Up to 240 characters — the catalog card.",
  "summary-ru": "До 240 символов — карточка каталога.",
  "description": "Longer text on the website (optional).",
  "description-ru": "…",
  "license": "MIT",
  "minEngine": "2.2.0",
  "authors": ["AIVERSE"],
  "homepage": "https://…",
  "tags": ["terrain", "pbr"],
  "provides": { "materials": ["terrain_grass", "terrain_rock"] },
  "dependencies": { "other-package": "^1.0" },
  "install": {
    "mount": "materials/terrain",
    "mergeJson": [{ "from": "materials.json", "into": "materials.json" }]
  },
  "previews": ["preview.jpg", "preview-2.jpg"],
  "archive": { "url": "https://…/terrain-pbr-1.0.0.zip", "sha256": "…", "size": 82000000 }
}
```

| Field | Meaning |
|---|---|
| `id` | unique, equals the folder name; lowercase letters, digits, `-` |
| `version` | `MAJOR.MINOR.PATCH`; a published version is immutable |
| `kind` | how the engine treats it: `content` (copied into a project), `template` (a new project is created from it), `source` (authoring sources, only fetched into the cache), `script`, `plugin`, `tool` |
| `category` | catalog section, equals the parent folder: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`, `plugins`, `tools` |
| `title`, `summary`, `description` | texts of the website card in **English**; translations are `<key>-<lang>`: `title-ru`, `summary-zh-CN`, … with lang one of `ru`, `zh-CN`, `ja`, `ko`, `es`, `pt-BR`, `de`, `fr` (a missing translation shows the English text) |
| `license` | SPDX id from the allowed list |
| `minEngine` | oldest engine version the package works with |
| `official` | `true`: made by the AIVERSE authors (`authors` must be `["AIVERSE"]`; only the catalog owner's pull requests may set it). The index repeats the flag, and the editor's start screen lists official templates without opening every package |
| `provides` | what it adds (material ids, type ids, template ids…): agents and `aiverse_pkg.py search` find packages by these |
| `dependencies` | other packages and version ranges (`^1.2`, `~1.2.3`, `>=1.0.0`, exact) |
| `install.mount` | folder inside the project where the payload is copied (`content`) |
| `install.mergeJson` | JSON objects from the payload merged into project files; existing ids are never overwritten |
| `previews` | preview images in the package folder (default: every `preview*.jpg/png/webp`) |
| `archive` | payload hosted over https instead of `files/`; `accept` writes it for packages that came with `files/` (their files are released as the archive and never enter main) |
| `viewer` | web 3D preview: `{"kind": "materials", "library": "materials.json", "items": [{"id": "terrain_grass", "title": "Grass", "title-ru": "Трава", "repeat": 2}], "repeat": 2}` or `{"kind": "models", "items": [{"model": "a.gltf", "title": "A", "title-ru": "А"}]}` (paths inside the payload; files a `.gltf` names outside it, e.g. textures of a dependency, are taken from that dependency); the `pages` workflow builds `view/<id>/<version>/` (files as published, textures at full size) and the site's **3D preview** opens it |

The archive (`<id>-<version>.zip`) holds `aiverse.package.json` at its root and the payload files;
`tools/catalog.py` builds it reproducibly (fixed timestamps, sorted entries).

## index.json and versions.json

Both are written by the `publish` workflow; never edit them by hand.

- `index.json` (repository root) is short: `schema` 2, `repo`, `pages`, `languages`, `categories`
  (`{id, title, title-ru, …}`) and `packages` → `{id, category, path}` of every published package
  (plus `official: true` for official ones).
- `<category>/<id>/versions.json` next to the manifest: `latest`, `versions` →
  `{url, sha256, size, files, unpackedSize, minEngine}`, absolute `previews` URLs, `readme` and the
  `viewer` URL of the 3D preview.

Consumers (the engine's `aiverse_pkg.py`, the website's Catalog page) read `index.json` from
`https://raw.githubusercontent.com/chromealex/AIVERSE-PACKAGES/main/index.json`, then
`<path>/aiverse.package.json` and `<path>/versions.json` of the packages they need.

## Project templates

A `template` package holds a whole project in its payload (`game.json` at the root). The engine's
`aiverse_pkg.py create <id> <folder>` and AIVERSE Studio's start screen create a new project from it.
`provides.engineTemplate` names the engine folder the template came from (`templates/<id>`), `provides.maps`
its map titles. Official templates are on the start screen; the others are found by search there.

## Dependencies between content packages

A package may use files of a package it depends on instead of carrying copies (rule "every texture
once"): a model pack refers to the textures of the material package with a relative path from its
mount, e.g. `../../../materials/terrain/textures/rock_basecolor_repeat.png` from `models/terraweave/rocks`.
`aiverse_pkg.py add` installs content dependencies into the project first (engine 3.1.0+).
