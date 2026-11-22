# AIVERSE 软件包

[English](README.md) · [Русский](README.ru.md) · **简体中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

[AIVERSE](https://github.com/chromealex/AIVERSE) 引擎的可选内容目录：材质库、纹理、项目模板、模型、声音、特效、脚本、原生插件和工具。引擎仓库只包含代码和最少的资源；这里的内容只由需要它的项目下载。

在引擎网站的 **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** 页面浏览目录：每个软件包都有预览图、说明和 3D 预览。

## 使用方法

在引擎目录中：

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # 查找
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # 克隆项目后：安装 aiverse.lock 中的全部内容
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # 创作用源文件：输出缓存中的文件夹
```

`add` 会把软件包写入项目 `game.json` → `"packages"`，安装它依赖的软件包，并在 `aiverse.lock` 中固定确切版本和文件哈希。下载内容通过 SHA-256 校验，每台机器只在 `~/.aiverse/packages` 中保存一份。引擎技能会写明所需的软件包，智能体也用同样的方式安装。

## 结构

```
index.json               分类以及每个已发布软件包的 {id, category, path}
<category>/<id>/
  aiverse.package.json   清单，由作者编写（docs/manifest.md）
  versions.json          已发布的版本、归档 URL 和 SHA-256（由 publish 工作流写入）
  README.md              内容简介、用法、来源和许可证
  preview.jpg            1..6 张预览图，宽 640..2400 px，每张不超过 1 MB
  files/                 内容，只在 pull request 中（最多 2 GB，单个文件最多 100 MB）
```

分类：`templates`、`materials`、`textures`、`models`、`audio`、`vfx`、`ui`、`scripts`、`plugins`、`tools`。清单中的文本为英文（`title`、`summary`、`description`），翻译写作 `title-ru`、`summary-de` 等。

内容随 pull request 提交（`files/`，最多 2 GB；超过 100 MB 的单个文件使用 `python3 tools/catalog.py upload <id> --repo you/AIVERSE-PACKAGES`）。所有者用标签 `accept` 代替 Merge 接受它：文件会变成发布归档，软件包在不含这些文件的情况下进入 `main`，因此它们不会进入仓库历史。

## 添加软件包

只接受 pull request；每项更改都由所有者审核并合并。分步说明见 [CONTRIBUTING.md](CONTRIBUTING.md) 和[网站上的说明](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog)。合并后，`publish` 工作流会发布该版本并写入 `versions.json` 和 `index.json`；引擎和网站会自动获取。
