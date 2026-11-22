# Adding a package / Как добавить пакет

1. Fork, create `<category>/<id>/` (id: lowercase letters, digits, `-`; unique in the catalog).
2. Write `aiverse.package.json` ([docs/manifest.md](docs/manifest.md)), `README.md` and at least one
   `preview.jpg` (a real engine frame or the asset itself; 640..2400 px wide, up to 1 MB).
3. Payload:
   - small package (up to 25 MB, files up to 10 MB): put it into `files/`;
   - bigger package: build the archive and host it anywhere over https (for example a release of your
     fork), then fill `"archive": {"url", "sha256", "size"}`:
     ```sh
     python3 tools/catalog.py archive <id> --from <folder with the files> --out /tmp
     ```
4. `python3 tools/catalog.py check` must print 0 errors. Open a pull request.
5. The owner reviews. After the merge the release `<id>@<version>` and `index.json` are created
   automatically; you do nothing else.

Updating: change the files, **raise `version`** and open a pull request. A published version is never
replaced (engines pin the archive hash in `aiverse.lock`).

Rules:
- only content you may redistribute under a permissive licence (MIT, BSD-2/3, Apache-2.0, Zlib, CC0,
  CC-BY-4.0, OFL-1.1) — no assets of commercial games, no ripped or AI-traced copies of them;
- `minEngine` is the oldest engine version you tested the package with;
- textures shared by several models are stored once (engine rule "every texture once");
- no executables in content packages; native plugins and tools come with source code.

---

1. Форкните репозиторий, создайте `<категория>/<id>/` (id: строчные латинские буквы, цифры, `-`).
2. Напишите `aiverse.package.json`, `README.md`, добавьте хотя бы одно превью `preview.jpg`.
3. Содержимое: маленький пакет — в `files/`; большой — архивом по https, поля `archive` заполняет
   `tools/catalog.py archive`.
4. `python3 tools/catalog.py check` — 0 ошибок, затем pull request.
5. Владелец проверяет и принимает. Релиз и `index.json` после слияния создаются автоматически.

Обновление — новая версия в `version`; опубликованная версия никогда не меняется.
