# Paquetes de AIVERSE

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Español** · [Português](README.pt-BR.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

Catálogo de contenido opcional para el motor [AIVERSE](https://github.com/chromealex/AIVERSE): bibliotecas de materiales, texturas, plantillas de proyecto, modelos, sonido, efectos, scripts, plugins nativos y herramientas. El repositorio del motor contiene el código y un conjunto mínimo de recursos; lo que hay aquí solo lo descargan los proyectos que lo necesitan.

Explóralo en la página **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** del sitio del motor: vistas previas, descripciones y una vista 3D de cada paquete.

## Uso

Desde una copia del motor:

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # buscar
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # tras clonar un proyecto: todo lo de aiverse.lock
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # fuentes de autoría: imprime la carpeta en caché
```

`add` registra el paquete en `game.json` del proyecto → `"packages"`, instala los paquetes de los que depende y fija las versiones exactas y los hashes de los archivos en `aiverse.lock`. Las descargas se verifican con SHA-256 y se guardan una sola vez por equipo en `~/.aiverse/packages`. Las skills del motor indican los paquetes que necesitan, así que los agentes los instalan igual.

## Estructura

```
index.json               categorías y {id, category, path} de cada paquete publicado
<category>/<id>/
  aiverse.package.json   manifiesto, lo escribe el autor (docs/manifest.md)
  versions.json          versiones publicadas, URL de los archivos y SHA-256 (lo escribe el workflow publish)
  README.md              qué es, cómo usarlo, origen y licencia
  preview.jpg            1..6 imágenes de vista previa, 640..2400 px de ancho, ≤ 1 MB cada una
  files/                 el contenido de los paquetes pequeños (≤ 25 MB, archivos ≤ 10 MB)
```

Categorías: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`, `plugins`, `tools`. Los textos de los manifiestos están en inglés (`title`, `summary`, `description`); las traducciones son `title-ru`, `summary-de`, etc.

## Añadir un paquete

Solo mediante pull request; el propietario revisa y fusiona cada cambio. Paso a paso: [CONTRIBUTING.md](CONTRIBUTING.md) y las [instrucciones del sitio web](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog). Tras la fusión, el workflow `publish` publica la versión y escribe `versions.json` e `index.json`; el motor y el sitio lo recogen automáticamente.
