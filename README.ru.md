# Пакеты AIVERSE

[English](README.md) · **Русский** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

Каталог дополнительного контента для движка [AIVERSE](https://github.com/chromealex/AIVERSE):
библиотеки материалов, текстуры, шаблоны проектов, модели, звук, эффекты, скрипты, нативные плагины и
инструменты. В репозитории движка — код и минимум ассетов; всё отсюда скачивают только те проекты,
которым это нужно.

Смотрите каталог на странице **[Каталог](https://chromealex.github.io/AIVERSE/ru/catalog.html)** сайта
движка: превью, описания и 3D-просмотр каждого пакета.

## Как пользоваться

Из папки движка:

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # найти
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # после клонирования проекта: всё из aiverse.lock
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # исходники для авторинга: путь к папке в кэше
```

`add` записывает пакет в `game.json` проекта → `"packages"`, ставит пакеты, от которых он зависит, и
фиксирует точные версии и хеши файлов в `aiverse.lock`. Скачанное проверяется по SHA-256 и хранится
один раз на компьютер в `~/.aiverse/packages`. Навыки движка называют нужные им пакеты, поэтому агенты
ставят их так же.

## Устройство

```
index.json               разделы и {id, category, path} каждого опубликованного пакета
<раздел>/<id>/
  aiverse.package.json   манифест, пишет автор (docs/manifest.md)
  versions.json          опубликованные версии, ссылки на архивы и SHA-256 (пишет workflow publish)
  README.md              что это, как пользоваться, происхождение и лицензия
  preview.jpg            1..6 превью, ширина 640..2400 px, до 1 МБ каждое
  files/                 содержимое, только в pull request (до 2 ГБ, файлы до 100 МБ)
```

Разделы: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`, `plugins`,
`tools`. Тексты в манифестах — на английском (`title`, `summary`, `description`), переводы — `title-ru`,
`summary-de` и так далее.

Содержимое приходит в pull request (`files/`, до 2 ГБ; файл больше 100 МБ — через `python3 tools/catalog.py upload <id> --repo вы/AIVERSE-PACKAGES`). Владелец принимает его меткой `accept` вместо Merge: файлы становятся архивом релиза, а пакет попадает в `main` без них, поэтому в историю репозитория они не входят.

## Добавить пакет

Только через pull request; каждое изменение проверяет и принимает владелец. По шагам:
[CONTRIBUTING.md](CONTRIBUTING.md) и
[инструкция на сайте](https://chromealex.github.io/AIVERSE/ru/docs-packages.html#как-добавить-свой-пакет-в-каталог).
После слияния workflow `publish` выпускает версию и пишет `versions.json` и `index.json`; движок и сайт
подхватывают их сами.
