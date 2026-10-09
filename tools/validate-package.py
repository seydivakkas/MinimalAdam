#!/usr/bin/env python3
"""Static package integrity checks for the Turkish v0.3 Codex skill.

Does not run image model/Codex or assess illustration aesthetics.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

root = Path(__file__).resolve().parent.parent
skill = root / 'minimaladam'
references = ('style-dna.md','minimaladam-character.md','composition-patterns.md',
              'prompt-template.md','qa-checklist.md','turkish-text-layer.md','technical-mode.md')
expected = [
    root / 'README.md',root / 'LICENSE',root / 'NOTICE.md',root / 'CHANGELOG.md',
    root / 'examples/prompts.md',root / 'requirements.txt',
    root / 'tools/render_turkish_labels.py',root / 'tools/render_technical_diagram.py',root / 'tools/raster_pillow.py',root / 'tools/make_samples.py',
    root / 'examples/technical/README.md',root / 'tests/test_p3.py',
    skill / 'scripts/render_technical_diagram.py',skill / 'scripts/render_turkish_labels.py',skill / 'scripts/raster_pillow.py',
    skill / 'requirements.txt',
    root / 'tests/test_p1_p2.py',skill / 'SKILL.md',skill / 'agents/openai.yaml',
    *[skill/'references'/r for r in references],
]
for stem in ('01-bilgiyi-suz','02-kopan-baglantiyi-onar','03-kanitla-karar-ver'):
    expected += [
        root/'examples/specs'/f'{stem}.base.svg',
        root/'examples/specs'/f'{stem}.labels.json',
        skill/'assets/examples'/f'{stem}.png',
        root/'examples/generated'/f'{stem}.base.png',
        root/'examples/generated'/f'{stem}.png',
        root/'examples/generated'/f'{stem}.text.png',
        root/'examples/generated'/f'{stem}.labels.svg',
        root/'examples/generated'/f'{stem}.manifest.json'
    ]

for stem in ('01-yazilim-mimarisi','02-veri-akisi','03-ml-pipeline','04-muhendislik-sistemi'):
    expected += [root/'examples/technical/specs'/f'{stem}.json',
                 skill/'examples/technical'/f'{stem}.json',
                 skill/'assets/examples/technical'/f'{stem}.png']
    expected += [root/'examples/technical/generated'/f'{stem}{extension}' for extension in (
        '.base.svg','.labels.svg','.svg','.png','.manifest.json')]

errors=[]
for path in expected:
    if not path.is_file():
        errors.append('Eksik dosya: '+str(path.relative_to(root)))

if not errors:
    master=(skill/'SKILL.md').read_text(encoding='utf-8')
    if not master.startswith('---\nname: minimaladam\n'):
        errors.append('Skill YAML kimlik başlığı geçersiz.')
    for name in references:
        if f'references/{name}' not in master:
            errors.append(f'Skill referans eksik: {name}')
    cfg=(skill/'agents/openai.yaml').read_text(encoding='utf-8')
    if '$minimaladam' not in cfg:
        errors.append('Ajan başlangıç istemi Skill adını içermiyor.')
    docs=[skill/'SKILL.md',skill/'agents/openai.yaml',*(skill/'references').glob('*.md'),
          root/'README.md',root/'examples/prompts.md']
    for path in docs:
        c=path.read_text(encoding='utf-8')
        if re.search(r'[\u3400-\u9fff]',c.replace('','')):
            errors.append('Beklenmedik Çince: '+str(path.relative_to(root)))
        if '\ufffd' in c:
            errors.append('Bozuk Unicode: '+str(path.relative_to(root)))
    license=(root/'LICENSE').read_text(encoding='utf-8')
    # Installed skill includes runnable utilities, not just markdown references.
    for f in ('render_turkish_labels.py','render_technical_diagram.py','raster_pillow.py'):
        if (root/'tools'/f).read_bytes()!=(skill/'scripts'/f).read_bytes():
            errors.append('Kurulu Skill script eşleşmiyor: '+f)
    if 'P3' not in master or 'technical-mode.md' not in master:
        errors.append('P3 Skill yönergesi eksik.')
    if 'Copyright (c) 2026 Ian'  not in license or 'MIT License' not in license:
        errors.append('MIT atıf metni bulunamadı.')
    from PIL import Image
    for stem in ('01-bilgiyi-suz','02-kopan-baglantiyi-onar','03-kanitla-karar-ver'):
        path=root/'examples/generated'/f'{stem}.manifest.json'
        m=json.loads(path.read_text(encoding='utf-8'))
        if m['base_sha256']!=hashlib.sha256((root/'examples/generated'/f'{stem}.base.png').read_bytes()).hexdigest():
            errors.append(f'Taban resim SHA256 tutarsız: {stem}')
        if m['labels_sha256']!=hashlib.sha256((root/'examples/specs'/f'{stem}.labels.json').read_bytes()).hexdigest():
            errors.append(f'Etiket SHA256 tutarsız: {stem}')
        with Image.open(root/'examples/generated'/f'{stem}.png') as im:
            if im.size!=(1600,900):
                errors.append(f'Sahne boyutu hatalı: {stem}')
        if (root/'examples/generated'/f'{stem}.png').read_bytes()!=(skill/'assets/examples'/f'{stem}.png').read_bytes():
            errors.append(f'Skill örnek PNG tutarsız: {stem}')


    # Verify each technical artifact and manifest hashes; preserve labels as SVG text.
    import xml.etree.ElementTree as ET
    for stem in ('01-yazilim-mimarisi','02-veri-akisi','03-ml-pipeline','04-muhendislik-sistemi'):
        folder=root/'examples/technical/generated'
        source=root/'examples/technical/specs'/f'{stem}.json'
        m=json.loads((folder/f'{stem}.manifest.json').read_text(encoding='utf-8'))
        if m['source_sha256']!=hashlib.sha256(source.read_bytes()).hexdigest():
            errors.append('P3 kaynak özeti hatalı: '+stem)
        for name in ('base','labels','svg','png'):
            output=folder/m['outputs'][name]
            if not output.is_file() or m['sha256'][name]!=hashlib.sha256(output.read_bytes()).hexdigest():
                errors.append('P3 çıktı özeti hatalı: '+stem+'/'+name)
        for name in ('base','labels','svg'):
            ET.fromstring((folder/m['outputs'][name]).read_text(encoding='utf-8'))
        with Image.open(folder/f'{stem}.png') as im:
            if im.size!=(1600,900):
                errors.append('P3 resim boyutu hatalı: '+stem)
        if (folder/f'{stem}.png').read_bytes()!=(skill/'assets/examples/technical'/f'{stem}.png').read_bytes():
            errors.append('P3 Skill örneği uyuşmazlığı: '+stem)
        if source.read_bytes()!=(skill/'examples/technical'/f'{stem}.json').read_bytes():
            errors.append('P3 kurulu Skill JSON uyuşmazlığı: '+stem)

if errors:
    for e in errors: print('HATA:',e)
    sys.exit(1)
print(f'PASS: {len(expected)} zorunlu dosya, 3 P1 + 4 P3 örnek, SVG/PNG/SHA-256, Skill script bütünlüğü, UTF-8 ve MIT lisans denetimleri.')
print('Sınır: Görsel estetik/semantik kalite ve gerçek Codex ajan çalışma zamanı bu kontrolde test edilmez.')
