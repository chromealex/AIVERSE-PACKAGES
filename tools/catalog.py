#!/usr/bin/env python3
"""AIVERSE package catalog: validate packages, build archives, publish releases, write index.json.

  python3 tools/catalog.py check                 validate every package (pull requests run this)
  python3 tools/catalog.py pack <id> --out DIR   build the reproducible .zip of one package
  python3 tools/catalog.py publish [--dry-run]   main branch: release every new version, rewrite index.json
  python3 tools/catalog.py index                 rewrite index.json from manifests + existing releases
  python3 tools/catalog.py views --out DIR       web preview folders view/<id>/<version>/
  python3 tools/catalog.py archive <id> --from DIR --out DIR
                                                 big package: zip an outside payload folder and print
                                                 the "archive" fields (upload the zip, then put them
                                                 into the manifest)

Layout: <category>/<id>/aiverse.package.json, preview images, README.md and the payload: either a
small files/ folder in git or "archive": {url, sha256, size} for a big package hosted elsewhere
(publish copies it into this repository's release <id>@<version>),
or "source": {repo, commit, path} — a folder of a public GitHub repository at a fixed commit. Standard library only;
publishing needs the gh CLI with a token that can create releases.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.json'
MANIFEST = 'aiverse.package.json'
MODEL_SIDECARS = ('.batching.json', '.clips.json', '.wind.json', '.lmuv')  # read by render::loadModel next to the model
VERSIONS = 'versions.json'  # written by publish next to the manifest: published versions, previews, viewer
REPO = os.environ.get('GITHUB_REPOSITORY', 'chromealex/AIVERSE-PACKAGES')
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
SCHEMA = 2  # 2: index.json lists {id, category, path}; the rest is in the package folder
# Texts: the plain key is English, other languages are '<key>-<lang>' (title-ru, summary-zh-CN, ...)
LANGS = ('ru', 'zh-CN', 'ja', 'ko', 'es', 'pt-BR', 'de', 'fr')

CATEGORIES = {
    'templates': {'title': 'Project templates', 'title-ru': 'Шаблоны проектов'},
    'materials': {'title': 'Materials', 'title-ru': 'Материалы'},
    'textures': {'title': 'Textures', 'title-ru': 'Текстуры'},
    'models': {'title': 'Models', 'title-ru': 'Модели'},
    'audio': {'title': 'Sound and music', 'title-ru': 'Звук и музыка'},
    'vfx': {'title': 'Effects', 'title-ru': 'Эффекты'},
    'ui': {'title': 'Interface', 'title-ru': 'Интерфейс'},
    'scripts': {'title': 'Scripts and mechanics', 'title-ru': 'Скрипты и механики'},
    'plugins': {'title': 'Native plugins', 'title-ru': 'Нативные плагины'},
    'tools': {'title': 'Tools', 'title-ru': 'Инструменты'},
}
KINDS = ('content', 'template', 'source', 'script', 'plugin', 'tool')
LICENSES = ('MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'Apache-2.0', 'Zlib', 'CC0-1.0', 'CC-BY-4.0', 'OFL-1.1')
ID_RE = re.compile(r'^[a-z0-9][a-z0-9-]{1,62}$')
VERSION_RE = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')
PREVIEW_EXT = ('.png', '.jpg', '.jpeg', '.webp')
MAX_PREVIEW = 1024 * 1024
MAX_PREVIEWS = 6
MAX_FILES_IN_GIT = 25 * 1024 * 1024     # total payload of files/ kept in git
MAX_FILE_IN_GIT = 10 * 1024 * 1024      # one file in files/
MAX_ARCHIVE = 2000 * 1024 * 1024        # GitHub release asset limit
ZIP_DATE = (1980, 1, 1, 0, 0, 0)
STORED_EXT = {'.png', '.jpg', '.jpeg', '.ktx2', '.dds', '.glb', '.ogg', '.mp3', '.zip', '.rpak', '.webp', '.basis'}
REQUIRED = ('id', 'version', 'kind', 'category', 'title', 'summary', 'license', 'minEngine')
TEXT_KEYS = ('title', 'summary', 'description')
TEXT_FIELDS = tuple(k + suffix for k in TEXT_KEYS for suffix in [''] + ['-' + l for l in LANGS])
ALLOWED = set(REQUIRED) | set(TEXT_FIELDS) | {
    'schema', 'tags', 'authors', 'homepage', 'provides', 'dependencies', 'install', 'archive', 'previews', 'source',
    'viewer'}
PAGES = os.environ.get('CATALOG_PAGES', 'https://chromealex.github.io/AIVERSE-PACKAGES')
MATERIAL_MAPS = ('texture', 'normalMap', 'metallicRoughnessMap', 'occlusionMap', 'emissiveMap')


def version_key(v):
    return tuple(int(x) for x in VERSION_RE.match(v).groups())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def image_size(path: Path):
    data = path.read_bytes()[:64 * 1024]
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', data[16:24])
    if data[:2] == b'\xff\xd8':
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack('>HH', data[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack('>H', data[i + 2:i + 4])[0]
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return (0, 0)  # accepted; size not checked
    return None


def packages():
    """[(folder, manifest)] for every <category>/<id>/aiverse.package.json."""
    out = []
    for cat in sorted(CATEGORIES):
        d = ROOT / cat
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if p.is_dir() and (p / MANIFEST).is_file():
                out.append((p, read_json(p / MANIFEST)))
    return out


def payload_files(folder: Path, files: Path | None = None):
    files = files or folder / 'files'
    if not files.is_dir():
        return []
    return sorted(p.relative_to(files).as_posix() for p in files.rglob('*')
                  if p.is_file() and not p.name.startswith('.'))


def previews(folder: Path, m: dict):
    names = m.get('previews') or sorted(p.name for p in folder.iterdir()
                                         if p.name.startswith('preview') and p.suffix.lower() in PREVIEW_EXT)
    return names


# ---------------------------------------------------------------- validation

def check_package(folder: Path, m: dict, seen: dict, index: dict) -> list[str]:
    where = folder.relative_to(ROOT).as_posix()
    err = []
    if not isinstance(m, dict):
        return [f'{where}/{MANIFEST}: not a JSON object']
    for k in REQUIRED:
        if not m.get(k):
            err.append(f'{where}: "{k}" is required')
    for k in m:
        if '-' in k and k.split('-', 1)[0] in TEXT_KEYS and k not in TEXT_FIELDS:
            err.append(f'{where}: "{k}": translations are "<key>-<lang>" with lang one of {", ".join(LANGS)}')
        elif k not in ALLOWED:
            err.append(f'{where}: unknown field "{k}"')
    if err:
        return err
    if m['id'] != folder.name:
        err.append(f'{where}: folder name must equal id "{m["id"]}"')
    if not ID_RE.match(m['id']):
        err.append(f'{where}: bad id (lowercase letters, digits, "-")')
    if m['id'] in seen:
        err.append(f'{where}: id already used by {seen[m["id"]]}')
    seen[m['id']] = where
    if m['category'] != folder.parent.name:
        err.append(f'{where}: category "{m["category"]}" must equal the folder "{folder.parent.name}"')
    if m['category'] not in CATEGORIES:
        err.append(f'{where}: category must be one of {", ".join(CATEGORIES)}')
    if m['kind'] not in KINDS:
        err.append(f'{where}: kind must be one of {", ".join(KINDS)}')
    for k in ('version', 'minEngine'):
        if not VERSION_RE.match(str(m.get(k, ''))):
            err.append(f'{where}: {k} must be MAJOR.MINOR.PATCH')
    if m['license'] not in LICENSES:
        err.append(f'{where}: license must be one of {", ".join(LICENSES)} (SPDX id)')
    for k in TEXT_FIELDS:
        if k in m and not isinstance(m[k], str):
            err.append(f'{where}: {k} must be a string')
    if any(len(m.get(k, '')) > 240 for k in TEXT_FIELDS if k.startswith('summary')):
        err.append(f'{where}: summary is limited to 240 characters (longer text goes to description)')
    inst = m.get('install') or {}
    if m['kind'] == 'content' and not inst.get('mount'):
        err.append(f'{where}: a content package needs install.mount (folder inside the project)')
    mount = inst.get('mount')
    if mount and (Path(mount).is_absolute() or '..' in Path(mount).parts):
        err.append(f'{where}: install.mount must be a relative path inside the project')
    for dep, spec in (m.get('dependencies') or {}).items():
        if not ID_RE.match(dep):
            err.append(f'{where}: bad dependency id "{dep}"')
    v = m.get('viewer')
    if v is not None:
        if not isinstance(v, dict) or v.get('kind') not in ('materials', 'models'):
            err.append(f'{where}: viewer.kind must be "materials" or "models"')
        elif v['kind'] == 'materials' and not v.get('library'):
            err.append(f'{where}: viewer.library (material library JSON inside the payload) is required')
        elif v['kind'] == 'models' and not v.get('items'):
            err.append(f'{where}: viewer.items ([{{"model": "path.glb", "title": ...}}]) is required')
        else:
            for it in v.get('items') or []:
                if not isinstance(it, dict) or not (it.get('model') or it.get('id')):
                    err.append(f'{where}: viewer.items entries are {{"id" or "model", "title", "title-<lang>"}}')
                    break
    if not (folder / 'README.md').is_file():
        err.append(f'{where}: README.md is required (what it is, how to use it, licence and origin)')
    names = previews(folder, m)
    if not names:
        err.append(f'{where}: at least one preview image (preview.png / preview-*.jpg) is required')
    if len(names) > MAX_PREVIEWS:
        err.append(f'{where}: at most {MAX_PREVIEWS} previews')
    for n in names:
        p = folder / n
        if not p.is_file() or p.suffix.lower() not in PREVIEW_EXT:
            err.append(f'{where}: preview {n} is missing or not png/jpg/webp')
            continue
        if p.stat().st_size > MAX_PREVIEW:
            err.append(f'{where}: preview {n} is larger than 1 MB')
        size = image_size(p)
        if size is None:
            err.append(f'{where}: preview {n} is not a valid image')
        elif size[0] and (size[0] < 640 or size[0] > 2400):
            err.append(f'{where}: preview {n} must be 640..2400 px wide (got {size[0]})')
    files = payload_files(folder)
    arch = m.get('archive')
    src = m.get('source')
    modes = [k for k, v in (('files/', files), ('archive', arch), ('source', src)) if v]
    if len(modes) > 1:
        err.append(f'{where}: use either files/ or "archive" or "source", not {" + ".join(modes)}')
    if not modes:
        err.append(f'{where}: no payload: add files/ (small packages), "archive": {{url, sha256, size}} '
                   f'or "source": {{repo, commit, path}}')
    if src:
        if not re.match(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$', str(src.get('repo', ''))):
            err.append(f'{where}: source.repo must be "owner/name" of a public GitHub repository')
        if not re.match(r'^[0-9a-f]{40}$', str(src.get('commit', ''))):
            err.append(f'{where}: source.commit must be a full 40-character commit hash (immutable)')
        sp = Path(str(src.get('path', '')))
        if not src.get('path') or sp.is_absolute() or '..' in sp.parts:
            err.append(f'{where}: source.path must be a relative folder in that repository')
    if files:
        total = 0
        for rel in files:
            s = (folder / 'files' / rel).stat().st_size
            total += s
            if s > MAX_FILE_IN_GIT:
                err.append(f'{where}: files/{rel} is larger than 10 MB: host the package as an "archive"')
        if total > MAX_FILES_IN_GIT:
            err.append(f'{where}: files/ is larger than 25 MB: host the package as an "archive"')
        for mj in inst.get('mergeJson') or []:
            if mj.get('from') not in files:
                err.append(f'{where}: install.mergeJson file {mj.get("from")} is not in files/')
    if arch:
        for k in ('url', 'sha256', 'size'):
            if not arch.get(k):
                err.append(f'{where}: archive.{k} is required')
        if arch.get('url') and not str(arch['url']).startswith('https://'):
            err.append(f'{where}: archive.url must be https')
        if int(arch.get('size') or 0) > MAX_ARCHIVE:
            err.append(f'{where}: archive is larger than 2000 MB')
    known = read_json(folder / VERSIONS, None)
    if known and m['version'] in known['versions'] and arch:
        if known['versions'][m['version']]['sha256'] != arch.get('sha256'):
            err.append(f'{where}: version {m["version"]} is already published with another archive; bump the version')
    if known and known.get('versions'):
        newest = max(known['versions'], key=version_key)
        if version_key(m['version']) < version_key(newest):
            err.append(f'{where}: version {m["version"]} is older than the published {newest}')
    return err


def check_all() -> list[str]:
    index = read_json(INDEX, {'schema': SCHEMA, 'packages': []})
    seen, errors = {}, []
    for folder, m in packages():
        errors += check_package(folder, m, seen, index)
    stray = [p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('.')
             and p.name not in CATEGORIES and p.name not in ('tools', 'docs')]
    for p in stray:
        errors.append(f'{p.name}/: unknown top-level folder (categories: {", ".join(CATEGORIES)})')
    return errors


# ---------------------------------------------------------------- archives

def zip_manifest(m: dict) -> dict:
    """The manifest stored inside the archive (what the engine reads after download)."""
    keep = ('schema', 'id', 'version', 'kind', 'category', *TEXT_FIELDS,
            'license', 'minEngine', 'authors', 'homepage', 'provides', 'dependencies', 'install', 'tags')
    out = {k: m[k] for k in keep if k in m}
    out['schema'] = SCHEMA
    return out


def build_zip(folder: Path, m: dict, out_dir: Path, payload: Path | None = None) -> Path:
    """payload: folder with the package files (default <package>/files)."""
    payload = payload or folder / 'files'
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{m['id']}-{m['version']}.zip"
    entries = [(MANIFEST, (json.dumps(zip_manifest(m), indent=2, ensure_ascii=False) + '\n').encode())]
    readme = folder / 'README.md'
    for rel in payload_files(folder, payload):
        if rel == 'README.md' and readme.is_file():
            continue  # the package README (reviewed in the catalog) replaces a payload README
        entries.append((rel, (payload / rel).read_bytes()))
    if readme.is_file():
        entries.append(('README.md', readme.read_bytes()))
    entries[1:] = sorted(entries[1:])
    with zipfile.ZipFile(archive, 'w') as z:
        for name, data in entries:
            info = zipfile.ZipInfo(name, ZIP_DATE)
            info.external_attr = 0o644 << 16
            stored = Path(name).suffix.lower() in STORED_EXT
            info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=None if stored else 9)
    return archive


def verify_archive(path: Path, m: dict) -> dict:
    """Checks a downloaded archive: safe paths, manifest of the same id and version."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        for n in names:
            p = Path(n)
            if p.is_absolute() or '..' in p.parts:
                raise SystemExit(f'{path.name}: unsafe path {n}')
        if MANIFEST not in names:
            raise SystemExit(f'{path.name}: no {MANIFEST} at the archive root')
        inner = json.loads(z.read(MANIFEST))
        unpacked = sum(i.file_size for i in z.infolist())
    if inner.get('id') != m['id'] or inner.get('version') != m['version']:
        raise SystemExit(f'{path.name}: inner manifest is {inner.get("id")}@{inner.get("version")}, '
                         f'expected {m["id"]}@{m["version"]}')
    return {'files': len(names) - 1, 'unpackedSize': unpacked}


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={'User-Agent': 'aiverse-catalog/1'})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, 'wb') as out:
        shutil.copyfileobj(r, out, 1 << 20)


def checkout_source(src: dict, work: Path) -> Path:
    """Sparse, blob-filtered checkout of <repo>@<commit>:<path>; returns the payload folder."""
    d = work / ('src-' + src['commit'][:12] + '-' + re.sub(r'[^a-z0-9]+', '-', src['path'].lower()))
    if not d.exists():
        run = lambda *a: subprocess.run(['git', *a], cwd=d, check=True, capture_output=True, text=True)
        d.mkdir(parents=True)
        run('init', '-q')
        run('remote', 'add', 'origin', f"https://github.com/{src['repo']}")
        run('sparse-checkout', 'set', '--no-cone', '/' + src['path'].strip('/') + '/')
        run('fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', src['commit'])
        run('checkout', '-q', 'FETCH_HEAD')
    payload = d / src['path']
    if not payload.is_dir():
        raise SystemExit(f"{src['repo']}@{src['commit'][:12]}: no folder {src['path']}")
    return payload


def gh(*args, check=True):
    return subprocess.run(['gh', *args], check=check, capture_output=True, text=True)


def release_asset(tag: str, name: str):
    """(url, sha256-from-index-or-None) when release <tag> already has <name>."""
    r = gh('release', 'view', tag, '--repo', REPO, '--json', 'assets', check=False)
    if r.returncode != 0:
        return None
    for a in json.loads(r.stdout).get('assets', []):
        if a['name'] == name:
            return f'https://github.com/{REPO}/releases/download/{tag}/{name}', a.get('size')
    return None


# ---------------------------------------------------------------- web preview views

def gltf_dependencies(path: Path, rel: str) -> list[str]:
    """Files a .gltf references (buffers, images); a .glb is self-contained unless it names uris."""
    data = path.read_bytes()
    try:
        if data[:4] == b'glTF':
            length = struct.unpack('<I', data[12:16])[0]
            doc = json.loads(data[20:20 + length])
        else:
            doc = json.loads(data)
    except Exception:
        return []
    base = Path(rel).parent
    out = []
    for key in ('buffers', 'images'):
        for e in doc.get(key, []):
            uri = e.get('uri')
            if uri and not uri.startswith('data:'):
                out.append((base / urllib.request.url2pathname(uri)).as_posix())
    return out


def build_view(m: dict, payload: Path, out: Path, deps: list | None = None) -> dict:
    """Web preview folder for apps/catalogview of the engine: view.json + the files it shows, with the
    package's project-relative paths (payload under install.mount), every file as published (textures keep their size).
    deps: [(mount, payload)] of the content packages it depends on, for files it refers to there
    (a model pack using the textures of a material package)."""
    v = m['viewer']
    mount = (m.get('install') or {}).get('mount', '')
    out.mkdir(parents=True, exist_ok=True)
    roots = [(mount, payload)] + list(deps or [])

    def src_of(rel):  # project-relative path -> payload file (own payload first, then the dependencies)
        r = Path(os.path.normpath(rel))
        first = None
        for mnt, root in roots:
            mp = Path(mnt).parts if mnt else ()
            if r.parts[:len(mp)] != mp:
                continue
            p = root / Path(*r.parts[len(mp):])
            if p.is_file():
                return p
            first = first or p
        return first or payload / r

    def copy(rel):  # files go as published: textures keep their size and format
        rel = Path(os.path.normpath(rel)).as_posix()
        dst = out / rel
        if dst.exists():
            return True
        src = src_of(rel)
        if not src.is_file():
            print(f"{m['id']}: view file missing: {rel}")
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return True

    view = {'schema': 1, 'package': m['id'], 'version': m['version'], 'kind': v['kind'], 'items': []}
    if v['kind'] == 'materials':
        lib_rel = (Path(mount) / v['library']).as_posix() if mount else v['library']
        library = json.loads(src_of(lib_rel).read_text(encoding='utf-8'))
        view['library'] = lib_rel
        view['shared'] = [lib_rel]
        copy(lib_rel)
        items = v.get('items') or [{'id': k} for k in sorted(library)]
        repeats = v.get('repeat') or {}
        for it in items:
            mid = it['id']
            entry = library.get(mid)
            if not isinstance(entry, dict):
                continue
            files = [entry[k] for k in MATERIAL_MAPS if isinstance(entry.get(k), str)]
            if not all(copy(f) for f in files):
                continue
            item = {'id': mid, 'files': files}
            item.update({k: it[k] for k in it if k.split('-', 1)[0] == 'title'})
            item.setdefault('title', mid.split('_', 1)[-1].replace('_', ' ').capitalize())
            if 'repeat' in it:
                item['repeat'] = it['repeat']
            elif isinstance(repeats, dict) and mid in repeats:
                item['repeat'] = repeats[mid]
            elif isinstance(repeats, (int, float)):
                item['repeat'] = repeats
            view['items'].append(item)
    else:
        for it in v['items']:
            rel = (Path(mount) / it['model']).as_posix() if mount else it['model']
            if not copy(rel):
                continue
            files = [rel] + [Path(os.path.normpath(f)).as_posix() for f in gltf_dependencies(src_of(rel), rel)]
            files += [rel + s for s in MODEL_SIDECARS if src_of(rel + s).is_file()]
            for f in files[1:]:
                copy(f)
            item = {'id': it.get('id') or Path(it['model']).stem, 'model': rel, 'files': files}
            item.update({k: it[k] for k in it if k.split('-', 1)[0] == 'title'})
            item.setdefault('title', item['id'])
            view['items'].append(item)
    write_json(out / 'view.json', view)
    return view


def build_views(out: Path) -> int:
    """view/<id>/<version>/ for the latest published version of every package with a viewer."""
    work = Path(tempfile.mkdtemp(prefix='views-'))
    made = 0
    published = {m['id']: (folder, read_json(folder / VERSIONS, None)) for folder, m in packages()}
    for folder, m in packages():
        e = published[m['id']][1]
        if not m.get('viewer') or not e:
            continue
        ver = e['latest']
        info = e['versions'][ver]
        archive = work / f"{m['id']}-{ver}.zip"
        fetch(info['url'], archive)
        if sha256_file(archive) != info['sha256']:
            raise SystemExit(f"{m['id']}@{ver}: archive sha256 does not match the index")
        payload = work / m['id']
        with zipfile.ZipFile(archive) as z:
            z.extractall(payload)
        deps = []
        for dep in (m.get('dependencies') or {}):
            de = published.get(dep, (None, None))[1]
            if not de:
                continue
            dinfo = de['versions'][de['latest']]
            dzip = work / f"{dep}-{de['latest']}.zip"
            if not dzip.exists():
                fetch(dinfo['url'], dzip)
            dpay = work / f'dep-{dep}'
            if not dpay.exists():
                with zipfile.ZipFile(dzip) as z:
                    z.extractall(dpay)
            dm = read_json(dpay / MANIFEST, {})
            deps.append(((dm.get('install') or {}).get('mount', ''), dpay))
        view = build_view(dict(m, version=ver), payload, out / 'view' / m['id'] / ver, deps)
        print(f"{m['id']}@{ver}: view with {len(view['items'])} item(s)")
        made += 1
    shutil.rmtree(work, ignore_errors=True)
    return made


# ---------------------------------------------------------------- index

def publication(folder: Path, m: dict, versions: dict) -> dict:
    """versions.json of a package: what consumers cannot derive from the manifest."""
    rel = folder.relative_to(ROOT).as_posix()
    versions = dict(sorted(versions.items(), key=lambda kv: version_key(kv[0])))
    latest = list(versions)[-1]
    out = {'id': m['id'], 'latest': latest, 'versions': versions,
           'previews': [f'{RAW}/{rel}/{n}' for n in previews(folder, m)],
           'readme': f'https://github.com/{REPO}/blob/main/{rel}/README.md'}
    if m.get('viewer'):
        out['viewer'] = f"{PAGES}/viewer/?src=../view/{m['id']}/{latest}"
    return out


def write_index(new_versions: dict) -> dict:
    """new_versions: id -> {url, sha256, size, files, unpackedSize, minEngine}. Writes <package>/versions.json
    for every published package and the short root index.json (categories + {id, category, path})."""
    out = []
    for folder, m in packages():
        versions = dict((read_json(folder / VERSIONS, {}) or {}).get('versions', {}))
        if m['id'] in new_versions:
            versions[m['version']] = new_versions[m['id']]
        if not versions:
            continue  # nothing published yet
        write_json(folder / VERSIONS, publication(folder, m, versions))
        out.append({'id': m['id'], 'category': m['category'], 'path': folder.relative_to(ROOT).as_posix()})
    index = {'schema': SCHEMA, 'repo': f'https://github.com/{REPO}', 'pages': PAGES,
             'languages': ['en', *LANGS],
             'categories': [dict(id=k, **v) for k, v in CATEGORIES.items()],
             'packages': sorted(out, key=lambda p: (p['category'], p['id']))}
    write_json(INDEX, index)
    return index


def publish(dry_run: bool) -> int:
    errors = check_all()
    if errors:
        print('\n'.join('error: ' + e for e in errors))
        return 1
    new_versions = {}
    work = Path(tempfile.mkdtemp(prefix='catalog-'))
    for folder, m in packages():
        if m['version'] in (read_json(folder / VERSIONS, {}) or {}).get('versions', {}):
            continue
        tag = f"{m['id']}@{m['version']}"
        name = f"{m['id']}-{m['version']}.zip"
        if m.get('archive'):
            src = work / name
            print(f'{tag}: downloading {m["archive"]["url"]}')
            fetch(m['archive']['url'], src)
            sha = sha256_file(src)
            if sha != m['archive']['sha256']:
                raise SystemExit(f'{tag}: sha256 {sha} does not match archive.sha256')
            archive = src
        elif m.get('source'):
            print(f"{tag}: building from {m['source']['repo']}@{m['source']['commit'][:12]}:{m['source']['path']}")
            archive = build_zip(folder, m, work, checkout_source(m['source'], work))
        else:
            archive = build_zip(folder, m, work)
        stats = verify_archive(archive, m)
        info = {'url': f'https://github.com/{REPO}/releases/download/{tag}/{name}',
                'sha256': sha256_file(archive), 'size': archive.stat().st_size,
                'minEngine': m['minEngine'], **stats}
        if dry_run:
            print(f'{tag}: would publish {info["size"] // 1024} KB sha256 {info["sha256"][:12]}')
        else:
            existing = release_asset(tag, name)
            if existing is None:
                notes = f"{m['title']} — {m['summary']}\n\nsha256 `{info['sha256']}`"
                if gh('release', 'view', tag, '--repo', REPO, check=False).returncode != 0:
                    gh('release', 'create', tag, str(archive), '--repo', REPO, '--title', f"{m['title']} {m['version']}",
                       '--notes', notes)
                else:
                    gh('release', 'upload', tag, str(archive), '--repo', REPO)
                print(f'{tag}: released')
            else:
                # Never index a rebuilt archive's hash for an asset that already exists: hash the
                # published file itself (deflate output can differ between zlib versions).
                pub = work / ('published-' + name)
                fetch(existing[0], pub)
                verify_archive(pub, m)
                info.update(sha256=sha256_file(pub), size=pub.stat().st_size)
                print(f'{tag}: release already has {name}; indexed its own sha256')
        new_versions[m['id']] = info
    if not dry_run:
        write_index(new_versions)
    shutil.rmtree(work, ignore_errors=True)
    print(f'{len(new_versions)} new version(s)')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('check')
    p = sub.add_parser('pack'); p.add_argument('id'); p.add_argument('--out', type=Path, default=Path('.'))
    p = sub.add_parser('publish'); p.add_argument('--dry-run', action='store_true')
    sub.add_parser('index')
    p = sub.add_parser('views'); p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('archive'); p.add_argument('id'); p.add_argument('--from', dest='src', type=Path, required=True)
    p.add_argument('--out', type=Path, default=Path('.'))
    a = ap.parse_args(argv)
    if a.cmd == 'check':
        errors = check_all()
        for e in errors:
            print('error:', e)
        print(f'{len(packages())} package(s), {len(errors)} error(s)')
        return 1 if errors else 0
    if a.cmd == 'pack':
        for folder, m in packages():
            if m.get('id') == a.id:
                if m.get('archive'):
                    raise SystemExit(f'{a.id} is hosted as an archive; nothing to pack')
                z = build_zip(folder, m, a.out)
                print(json.dumps({'archive': str(z), 'sha256': sha256_file(z), 'size': z.stat().st_size}))
                return 0
        raise SystemExit(f'no package {a.id}')
    if a.cmd == 'publish':
        return publish(a.dry_run)
    if a.cmd == 'archive':
        for folder, m in packages():
            if m.get('id') == a.id:
                z = build_zip(folder, m, a.out, a.src)
                tag = f"{m['id']}@{m['version']}"
                print(json.dumps({'archive': str(z), 'tag': tag, 'fields': {
                    'url': f'https://github.com/{REPO}/releases/download/{tag}/{z.name}',
                    'sha256': sha256_file(z), 'size': z.stat().st_size}}, indent=2))
                return 0
        raise SystemExit(f'no package {a.id}')
    if a.cmd == 'views':
        print(f'{build_views(a.out)} view(s)')
        return 0
    if a.cmd == 'index':
        write_index({})
        return 0
    return 2


if __name__ == '__main__':
    sys.exit(main())
