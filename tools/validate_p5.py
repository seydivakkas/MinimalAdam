#!/usr/bin/env python3
"""v0.5 packaging and evidence checks; no claims about aesthetics or architecture."""
from pathlib import Path
import json
import re
import sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'minimaladam'
NEEDED=[
 'editor/quality.mjs','editor/offline.html','editor/index.html',
 'minimaladam/references/quality-gate.md',
 'minimaladam/scripts/inspect_render.py',
 'tools/inspect_render.py','tools/validate_p5.py',
 'tests/js/p5_quality.test.mjs','tests/test_p5_raster.py','tests/e2e_p5.py',
 'examples/editor/studio-qa-preview.png',
 'examples/qa/ornek-hata-overflow.spec.json',
 'examples/qa/ornek-hata-overflow.qa-report.json',
 'examples/qa/03-ml-pipeline.qa-report.json',
 'examples/qa/03-ml-pipeline.raster-report.json',
 'LICENSE','NOTICE.md','README.md','CHANGELOG.md',
]
def main():
    miss=[p for p in NEEDED if not (ROOT/p).is_file()]
    assert not miss,f'Zorunlu P5 dosyaları eksik: {miss}'
    for f in ('core.mjs','quality.mjs','samples.mjs','studio.mjs','index.html','studio.css','offline.html'):
        assert (ROOT/'editor'/f).read_bytes()==(SKILL/'editor'/f).read_bytes(),f'Mirrored editor mismatch: {f}'
    assert (ROOT/'tools/inspect_render.py').read_bytes()==(SKILL/'scripts/inspect_render.py').read_bytes()
    offline=(ROOT/'editor/offline.html').read_text(encoding='utf-8')
    assert 'function auditProject(' in offline and 'qa-accept' in offline
    assert not re.search(r'<script[^>]*src=|<link[^>]*href=',offline), 'Offline editor must not need CSS/JS URLs'
    assert 'quality-gate.md' in (SKILL/'SKILL.md').read_text('utf8')
    for p in (ROOT/'LICENSE',ROOT/'NOTICE.md'):
        assert p.is_file()
    assert 'Copyright (c) 2026 Ian' in (ROOT/'LICENSE').read_text('utf8')
    assert not list(ROOT.rglob('*.ttf')) and not list(ROOT.rglob('*.otf'))
    for name,expected in [('ornek-hata-overflow.qa-report.json','REVIEW'),('03-ml-pipeline.qa-report.json','PASS')]:
        report=json.loads((ROOT/'examples/qa'/name).read_text('utf8'))
        assert report['summary']['automatedStatus']==expected
        assert all(c['status']=='NOT_VERIFIED' for c in report['manualChecks'])
    with Image.open(ROOT/'examples/editor/studio-qa-preview.png') as im:
        assert im.width>=1200 and im.height>=700
    print(f'P5 PASS: {len(NEEDED)} gerekli dosya, mirror/offline/qa fixtures/attribution/font check')
if __name__=='__main__':
    try:main()
    except AssertionError as exc:
        print('P5 FAIL:',exc,file=sys.stderr);raise SystemExit(1)
