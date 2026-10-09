#!/usr/bin/env python3
"""Create a deterministic manifest of distribution files; excludes this manifest itself."""
from pathlib import Path
import hashlib, json
root=Path(__file__).resolve().parents[1]
files={}
for p in sorted(root.rglob('*')):
    if not p.is_file() or p.name=='RELEASE_MANIFEST.json' or any(s in {'__pycache__','.git','.pytest_cache'} for s in p.parts) or p.suffix in {'.pyc','.pyo'}:
        continue
    content=p.read_bytes()
    files[p.relative_to(root).as_posix()]={'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}
manifest={
    'product':'MinimalAdam',
    'version':'0.6.1',
    'upstream':'https://github.com/helloianneo/ian-xiaohei-illustrations',
    'license':'MIT (original text retained in LICENSE)',
    'platform_tested':'Linux; Chromium browser; Windows Python 3.14 fix pending Windows CI',
    'windows_acceptance':'NOT_RUN',
    'github_publish':'NOT_DONE',
    'test_results':{'python':40,'javascript':22,'browser_e2e':['P4 PASS','P5 PASS'],'static_package_checks':'PASS'},
    'limitations':['PNG platform pixel identity is not guaranteed across fonts','P1 source SVG regeneration may require optional Cairo','AI image-generation model is not bundled','No verified semantic architecture','No Windows acceptance result yet'],
    'file_count':len(files),
    'files':files,
}
(root/'RELEASE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Generated manifest with',len(files),'files')
