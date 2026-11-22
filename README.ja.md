# AIVERSE パッケージ

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · **日本語** · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

[AIVERSE](https://github.com/chromealex/AIVERSE) エンジン向けの追加コンテンツのカタログです：マテリアルライブラリ、テクスチャ、プロジェクトテンプレート、モデル、サウンド、エフェクト、スクリプト、ネイティブプラグイン、ツール。エンジンのリポジトリにはコードと最小限のアセットだけを置き、ここにあるものは必要なプロジェクトだけがダウンロードします。

エンジンのウェブサイトの **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** ページで閲覧できます：各パッケージのプレビュー、説明、3D プレビュー。

## 使い方

エンジンのチェックアウトから：

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # 検索
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # プロジェクトをクローンした後：aiverse.lock の内容をすべて入れる
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # 制作用ソース：キャッシュのフォルダを表示
```

`add` はパッケージをプロジェクトの `game.json` → `"packages"` に記録し、依存するパッケージもインストールし、正確なバージョンとファイルのハッシュを `aiverse.lock` に固定します。ダウンロードは SHA-256 で検証され、マシンごとに一度だけ `~/.aiverse/packages` に保存されます。エンジンのスキルは必要なパッケージを明記しているので、エージェントも同じ方法でインストールします。

## 構成

```
index.json               カテゴリと、公開済みの各パッケージの {id, category, path}
<category>/<id>/
  aiverse.package.json   マニフェスト。作者が書く（docs/manifest.md）
  versions.json          公開済みのバージョン、アーカイブの URL と SHA-256（publish ワークフローが書く）
  README.md              内容、使い方、出所とライセンス
  preview.jpg            プレビュー画像 1..6 枚、幅 640..2400 px、各 1 MB 以下
  files/                 中身。pull request の中だけ（2 GB まで、ファイルは 100 MB まで）
```

カテゴリ：`templates`、`materials`、`textures`、`models`、`audio`、`vfx`、`ui`、`scripts`、`plugins`、`tools`。マニフェストの文章は英語（`title`、`summary`、`description`）で、翻訳は `title-ru`、`summary-de` などです。

中身は pull request で送ります（`files/`、2 GB まで。100 MB を超えるファイルは `python3 tools/catalog.py upload <id> --repo you/AIVERSE-PACKAGES` で）。オーナーは Merge の代わりにラベル `accept` で受け入れます。ファイルはリリースのアーカイブになり、パッケージはそれらを含まずに `main` に入るため、リポジトリの履歴には残りません。

## パッケージを追加する

受け付けるのは pull request のみで、すべての変更はオーナーがレビューしてマージします。手順は [CONTRIBUTING.md](CONTRIBUTING.md) と[ウェブサイトの説明](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog)を参照してください。マージ後、`publish` ワークフローがバージョンをリリースし、`versions.json` と `index.json` を書き込みます。エンジンとウェブサイトは自動的にそれを取り込みます。
