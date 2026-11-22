# Adding a package / Как добавить пакет

1. Fork, create `<category>/<id>/` (id: lowercase letters, digits, `-`; unique in the catalog).
2. Write `aiverse.package.json` ([docs/manifest.md](docs/manifest.md)) — texts in English (`title`, `summary`,
   `description`), translations as `title-ru`, `summary-de`, … — `README.md` and at least one
   `preview.jpg` (a real engine frame or the asset itself; 640..2400 px wide, up to 1 MB).
3. Payload:
   - put the files into `files/`, laid out as they appear under `install.mount` (up to 2 GB in total);
   - a single file over 100 MB does not fit into git: run
     `python3 tools/catalog.py upload <id> --repo <you>/AIVERSE-PACKAGES` (zips `files/` into a release of
     your fork and writes `"archive"` into the manifest), then remove `files/` from the pull request;
   - content already hosted elsewhere over https: `"archive": {"url", "sha256", "size"}`
     (`python3 tools/catalog.py archive <id> --from <folder>` prints the fields).
4. `python3 tools/catalog.py check` must print 0 errors. Open a pull request.
5. The owner reviews and accepts it with the label `accept` (not the Merge button): the files become the
   release archive and the package lands in `main` without them, so they never enter the repository
   history. The release `<id>@<version>`, its `versions.json` and the entry in `index.json` are created
   automatically; you do nothing else.

Updating: change the files, **raise `version`** and open a pull request. A published version is never
replaced (engines pin the archive hash in `aiverse.lock`).

Rules:
- only content you may redistribute under a permissive licence (MIT, BSD-2/3, Apache-2.0, Zlib, CC0,
  CC-BY-4.0, OFL-1.1) — no assets of commercial games, no ripped or AI-traced copies of them;
- `minEngine` is the oldest engine version you tested the package with;
- textures shared by several models are stored once (engine rule "every texture once"); textures another
  package already has are not copied: add it to `dependencies` and refer to its files by a relative path;
- no executables in content packages; native plugins and tools come with source code.

---

1. Форкните репозиторий, создайте `<категория>/<id>/` (id: строчные латинские буквы, цифры, `-`).
2. Напишите `aiverse.package.json` (тексты на английском, переводы — `title-ru`, `summary-de`, …),
   `README.md`, добавьте хотя бы одно превью `preview.jpg`.
3. Содержимое — в `files/` (до 2 ГБ). Файл больше 100 МБ в git не помещается: `python3 tools/catalog.py
   upload <id> --repo <вы>/AIVERSE-PACKAGES` выложит архив в релиз вашего форка и впишет `archive` в
   манифест, после этого уберите `files/` из pull request.
4. `python3 tools/catalog.py check` — 0 ошибок, затем pull request.
5. Владелец проверяет и принимает меткой `accept` (не кнопкой Merge): файлы становятся архивом релиза,
   пакет попадает в `main` без них и в историю репозитория не входит. Релиз и `index.json` после слияния создаются автоматически.

Обновление — новая версия в `version`; опубликованная версия никогда не меняется.
