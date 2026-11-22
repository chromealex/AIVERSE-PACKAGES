# AIVERSE 패키지

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · **한국어** · [Español](README.es.md) · [Português](README.pt-BR.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

[AIVERSE](https://github.com/chromealex/AIVERSE) 엔진용 추가 콘텐츠 카탈로그입니다: 머티리얼 라이브러리, 텍스처, 프로젝트 템플릿, 모델, 사운드, 이펙트, 스크립트, 네이티브 플러그인, 도구. 엔진 저장소에는 코드와 최소한의 에셋만 있고, 여기 있는 것은 필요한 프로젝트만 내려받습니다.

엔진 웹사이트의 **[Catalog](https://chromealex.github.io/AIVERSE/catalog.html)** 페이지에서 둘러보세요: 패키지마다 미리보기, 설명, 3D 미리보기가 있습니다.

## 사용법

엔진 체크아웃에서:

```sh
python3 tools/pkg/aiverse_pkg.py search terrain            # 찾기
python3 tools/pkg/aiverse_pkg.py add terrain-pbr --project ~/Games/MyGame
python3 tools/pkg/aiverse_pkg.py install --project ~/Games/MyGame   # 프로젝트를 클론한 뒤: aiverse.lock의 모든 것
python3 tools/pkg/aiverse_pkg.py fetch terrain-pbr-sources  # 제작용 소스: 캐시 폴더 경로 출력
```

`add`는 패키지를 프로젝트의 `game.json` → `"packages"`에 기록하고, 의존하는 패키지를 설치하며, 정확한 버전과 파일 해시를 `aiverse.lock`에 고정합니다. 다운로드는 SHA-256으로 검증되고 컴퓨터마다 한 번만 `~/.aiverse/packages`에 보관됩니다. 엔진 스킬은 필요한 패키지를 명시하므로 에이전트도 같은 방식으로 설치합니다.

## 구조

```
index.json               카테고리와 게시된 각 패키지의 {id, category, path}
<category>/<id>/
  aiverse.package.json   매니페스트, 작성자가 작성 (docs/manifest.md)
  versions.json          게시된 버전, 아카이브 URL과 SHA-256 (publish 워크플로가 작성)
  README.md              무엇인지, 사용법, 출처와 라이선스
  preview.jpg            미리보기 이미지 1..6장, 너비 640..2400 px, 각 1 MB 이하
  files/                 내용, pull request에만 (최대 2 GB, 파일은 최대 100 MB)
```

카테고리: `templates`, `materials`, `textures`, `models`, `audio`, `vfx`, `ui`, `scripts`, `plugins`, `tools`. 매니페스트의 텍스트는 영어(`title`, `summary`, `description`)이고, 번역은 `title-ru`, `summary-de` 등입니다.

내용은 pull request로 보냅니다(`files/`, 최대 2 GB; 100 MB가 넘는 파일은 `python3 tools/catalog.py upload <id> --repo you/AIVERSE-PACKAGES`). 소유자는 Merge 대신 `accept` 레이블로 받아들입니다. 파일은 릴리스 아카이브가 되고 패키지는 파일 없이 `main`에 들어가므로 저장소 기록에 남지 않습니다.

## 패키지 추가

pull request만 받습니다. 모든 변경은 소유자가 검토하고 병합합니다. 단계별 안내: [CONTRIBUTING.md](CONTRIBUTING.md)와 [웹사이트의 안내](https://chromealex.github.io/AIVERSE/docs-packages.html#adding-your-package-to-the-catalog). 병합 후 `publish` 워크플로가 버전을 릴리스하고 `versions.json`과 `index.json`을 작성하며, 엔진과 웹사이트가 자동으로 가져갑니다.
