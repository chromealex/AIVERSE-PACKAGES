# aiverse.package.json

```json
{
  "schema": 1,
  "id": "terrain-pbr",
  "version": "1.0.0",
  "kind": "content",
  "category": "materials",
  "title": "PBR-материалы ландшафта",
  "titleEn": "Terrain PBR materials",
  "summary": "До 240 символов — карточка каталога.",
  "summaryEn": "Up to 240 characters — the catalog card.",
  "description": "Longer text on the website (optional).",
  "descriptionEn": "…",
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
| `title` / `titleEn`, `summary` / `summaryEn`, `description` / `descriptionEn` | Russian and English texts of the website card |
| `license` | SPDX id from the allowed list |
| `minEngine` | oldest engine version the package works with |
| `provides` | what it adds (material ids, type ids, template ids…): agents and `aiverse_pkg.py search` find packages by these |
| `dependencies` | other packages and version ranges (`^1.2`, `~1.2.3`, `>=1.0.0`, exact) |
| `install.mount` | folder inside the project where the payload is copied (`content`) |
| `install.mergeJson` | JSON objects from the payload merged into project files; existing ids are never overwritten |
| `previews` | preview images in the package folder (default: every `preview*.jpg/png/webp`) |
| `archive` | hosted payload for big packages instead of `files/` |

The archive (`<id>-<version>.zip`) holds `aiverse.package.json` at its root and the payload files;
`tools/catalog.py` builds it reproducibly (fixed timestamps, sorted entries).

## index.json

Written by the `publish` workflow; never edit by hand. One entry per package: the manifest's catalog
fields, `path`, absolute `previews` URLs, `readme`, `latest` and `versions` →
`{url, sha256, size, files, unpackedSize, minEngine}`. The engine's `aiverse_pkg.py` and the website's
Catalog page read it from `https://raw.githubusercontent.com/chromealex/AIVERSE-PLUGINS/main/index.json`.
