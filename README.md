# AIVERSE packages

Catalog of optional content for the [AIVERSE](https://github.com/chromealex/AIVERSE) engine: material
libraries, textures, project templates, models, sound, effects, scripts, native plugins and tools.
The engine repository carries code and a minimal set of assets; everything here is downloaded only by
the projects that need it.

Каталог дополнительного контента для движка AIVERSE: библиотеки материалов, текстуры, шаблоны
проектов, модели, звук, эффекты, скрипты, нативные плагины и инструменты. В репозитории движка — код и
минимум ассетов; всё отсюда скачивают только те проекты, которым это нужно.

Browse: the **Catalog** page of the engine website. Machine-readable list: [`index.json`](index.json).

## Use / Как пользоваться

From an engine checkout:

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # find
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # after cloning a project: everything from aiverse.lock
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # authoring sources: print the cached folder
```

`add` records the package in the project's `game.json` → `"packages"` and pins the exact version
and file hashes in `aiverse.lock`. Downloads are verified by SHA-256 and kept once per machine in
`~/.aiverse/packages`. Engine skills name the packages they need, so agents install them the same way.

## Layout

```
<category>/<id>/
  aiverse.package.json   manifest (see docs/manifest.md)
  README.md              what it is, how to use it, origin and licence
  preview.jpg            1..6 preview images, 640..2400 px wide, <= 1 MB each
  files/                 the payload, for small packages (<= 25 MB, files <= 10 MB)
```

Categories: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`,
`plugins`, `tools`.

Big packages keep no payload in git: the manifest has `"archive": {"url", "sha256", "size"}` and the
publish job copies that archive into this repository's release `<id>@<version>`.

## Contributing / Как добавить пакет

Pull requests only; the owner reviews and merges every change. See [CONTRIBUTING.md](CONTRIBUTING.md).
After the merge the `publish` workflow releases the new version and rewrites `index.json`; the engine
and the website pick it up automatically.

Пакеты добавляются только через pull request; владелец проверяет и принимает каждый. После слияния
workflow `publish` выпускает версию и обновляет `index.json`, движок и сайт подхватывают его сами.
