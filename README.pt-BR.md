# Pacotes do AIVERSE

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · **Português** · [Deutsch](README.de.md) · [Français](README.fr.md)

Catálogo de conteúdo opcional para o motor [AIVERSE](https://github.com/chromealex/AIVERSE): bibliotecas de materiais, texturas, modelos de projeto, modelos 3D, som, efeitos, scripts, plugins nativos e ferramentas. O repositório do motor traz o código e um conjunto mínimo de assets; o que está aqui só é baixado pelos projetos que precisam.

Navegue pela página **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** do site do motor: prévias, descrições e uma prévia 3D de cada pacote.

## Uso

A partir de uma cópia do motor:

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # buscar
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # depois de clonar um projeto: tudo do aiverse.lock
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # fontes de autoria: mostra a pasta no cache
```

`add` registra o pacote no `game.json` do projeto → `"packages"`, instala os pacotes dos quais ele depende e fixa as versões exatas e os hashes dos arquivos em `aiverse.lock`. Os downloads são verificados por SHA-256 e guardados uma única vez por máquina em `~/.aiverse/packages`. As skills do motor indicam os pacotes de que precisam, então os agentes os instalam do mesmo jeito.

## Estrutura

```
index.json               categorias e {id, category, path} de cada pacote publicado
<category>/<id>/
  aiverse.package.json   manifesto, escrito pelo autor (docs/manifest.md)
  versions.json          versões publicadas, URLs dos arquivos e SHA-256 (escrito pelo workflow publish)
  README.md              o que é, como usar, origem e licença
  preview.jpg            1..6 imagens de prévia, 640..2400 px de largura, ≤ 1 MB cada
  files/                 o conteúdo de pacotes pequenos (≤ 25 MB, arquivos ≤ 10 MB)
```

Categorias: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`, `plugins`, `tools`. Os textos dos manifestos são em inglês (`title`, `summary`, `description`); as traduções são `title-ru`, `summary-de` e assim por diante.

## Adicionar um pacote

Somente por pull request; o dono revisa e faz o merge de cada mudança. Passo a passo: [CONTRIBUTING.md](CONTRIBUTING.md) e as [instruções no site](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog). Depois do merge, o workflow `publish` lança a versão e escreve `versions.json` e `index.json`; o motor e o site os pegam automaticamente.
