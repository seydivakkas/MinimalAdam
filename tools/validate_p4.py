#!/usr/bin/env python3
"""Static P4 distribution quality gate (offline editor, original P1-P3 retained)."""
from pathlib import Path
import hashlib
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'editor'
SKILL=ROOT/'minimaladam'
FILES=[
'editor/index.html','editor/studio.css','editor/studio.mjs','editor/core.mjs','editor/samples.mjs','editor/offline.html',
'MinimalAdam-Studio.cmd','tools/start-editor.ps1','tools/start_studio.py','tools/build_offline_editor.py',
'minimaladam/editor/offline.html',
'minimaladam/references/visual-editor.md',
'minimaladam/scripts/start_studio.py',
'examples/editor/studio-preview.png','tests/js/p4_core.test.mjs','tests/e2e_p4.py','LICENSE','NOTICE.md',
]

def main():
 missing=[x for x in FILES if not (ROOT/x).is_file()]
 if missing:raise AssertionError(f'Eksik P4 dosyaları: {missing}')
 for x in ('index.html','studio.css','studio.mjs','core.mjs','samples.mjs','offline.html'):
  assert (EDITOR/x).read_bytes()==(SKILL/'editor'/x).read_bytes(),f'Skill editör kopyası farklı: {x}'
 assert (ROOT/'tools/start_studio.py').read_bytes()==(SKILL/'scripts/start_studio.py').read_bytes()
 offline=(EDITOR/'offline.html').read_text('utf8')
 assert offline.lower().count('<!doctype html>')==1
 assert '<script>' in offline and 'function exportSVG(' in offline and 'renderAll();' in offline
 assert '<link rel="stylesheet"' not in offline and '<script type="module" src=' not in offline
 assert re.search(r'canvas\.toBlob\(',offline)
 assert '127.0.0.1' in (ROOT/'tools/start_studio.py').read_text('utf8')
 assert not any(ROOT.glob('**/*.ttf')) and not any(ROOT.glob('**/*.otf'))
 assert 'Copyright (c) 2026 Ian' in (ROOT/'LICENSE').read_text('utf8')
 from PIL import Image
 image=Image.open(ROOT/'examples/editor/studio-preview.png');assert image.size[0]>=1000 and image.size[1]>=700
 print(f'P4 PASS: {len(FILES)} zorunlu dosya; root/Skill editör eşitliği; offline asset bağımsızlığı; PNG screenshot; lisans.')
 return 0

if __name__=='__main__':
 try:raise SystemExit(main())
 except (AssertionError,OSError) as e:print('P4 FAIL:',e,file=sys.stderr);raise SystemExit(1)
