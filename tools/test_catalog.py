#!/usr/bin/env python3
"""Self-test of tools/catalog.py on a temporary catalog (no network, no gh)."""
import json
import struct
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402


def png(w, h):
    raw = b''.join(b'\x00' + b'\x80' * (w * 3) for _ in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        catalog.ROOT, catalog.INDEX = root, root / 'index.json'
        pkg = root / 'materials' / 'demo-mats'
        (pkg / 'files' / 'textures').mkdir(parents=True)
        (pkg / 'files' / 'textures' / 'a.png').write_bytes(png(4, 4))
        (pkg / 'files' / 'materials.json').write_text('{"demo_a": {"baseColor": [1,1,1,1]}}')
        (pkg / 'README.md').write_text('# demo')
        (pkg / 'preview.png').write_bytes(png(800, 450))
        m = {'schema': 1, 'id': 'demo-mats', 'version': '1.0.0', 'kind': 'content', 'category': 'materials',
             'title': 'Demo', 'title-ru': 'Демо', 'summary': 's', 'summary-ru': 'с', 'license': 'MIT',
             'minEngine': '2.2.0', 'install': {'mount': 'materials/demo',
                                               'mergeJson': [{'from': 'materials.json', 'into': 'materials.json'}]}}
        (pkg / catalog.MANIFEST).write_text(json.dumps(m))
        errors = catalog.check_all()
        assert errors == [], errors

        a = catalog.build_zip(pkg, m, root / 'out1')
        b = catalog.build_zip(pkg, m, root / 'out2')
        assert a.read_bytes() == b.read_bytes(), 'archives must be reproducible'
        stats = catalog.verify_archive(a, m)
        assert stats['files'] == 3, stats  # payload x2 + README

        (pkg / catalog.MANIFEST).write_text(json.dumps(dict(m, **{'title-xx': 'x'})))
        assert any('translations' in e for e in catalog.check_all())
        (pkg / catalog.MANIFEST).write_text(json.dumps(m))

        bad = dict(m, category='textures', license='GPL-3.0', extra=1)
        (pkg / catalog.MANIFEST).write_text(json.dumps(bad))
        errors = catalog.check_all()
        assert any('unknown field' in e for e in errors), errors
        bad.pop('extra')
        (pkg / catalog.MANIFEST).write_text(json.dumps(bad))
        errors = catalog.check_all()
        assert any('category' in e for e in errors) and any('license' in e for e in errors), errors
        (pkg / catalog.MANIFEST).write_text(json.dumps(m))

        info = {'url': 'https://x/demo.zip', 'sha256': catalog.sha256_file(a), 'size': a.stat().st_size,
                'minEngine': '2.2.0', **stats}
        index = catalog.write_index({'demo-mats': info})
        assert index['schema'] == 2 and index['packages'] == [{'id': 'demo-mats', 'category': 'materials',
                                                               'path': 'materials/demo-mats'}], index
        assert index['categories'][1] == {'id': 'materials', 'title': 'Materials', 'title-ru': 'Материалы'}
        e = json.loads((pkg / catalog.VERSIONS).read_text())
        assert e['latest'] == '1.0.0' and e['versions']['1.0.0']['sha256'] == info['sha256']
        assert e['previews'][0].endswith('/preview.png')

        # a published version is immutable and versions only go up
        (pkg / catalog.MANIFEST).write_text(json.dumps(dict(m, version='0.9.0')))
        assert any('older' in x for x in catalog.check_all())
        (pkg / catalog.MANIFEST).write_text(json.dumps(dict(m, archive={'url': 'https://x', 'sha256': 'f' * 64, 'size': 1})))
        errs = catalog.check_all()
        assert any('either files/' in x for x in errs), errs
    print('catalog self-test: ok')


if __name__ == '__main__':
    main()
