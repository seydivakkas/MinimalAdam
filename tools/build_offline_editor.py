#!/usr/bin/env python3
"""Bundle the maintained P4 modules into one dependency-free offline HTML file."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'editor'

def build():
    html=(D/'index.html').read_text(encoding='utf-8')
    css=(D/'studio.css').read_text(encoding='utf-8')
    core=re.sub(r'^export ', '', (D/'core.mjs').read_text('utf-8'), flags=re.M)
    samples=re.sub(r'^export ', '', (D/'samples.mjs').read_text('utf-8'), flags=re.M)
    quality=re.sub(r'^export ', '', (D/'quality.mjs').read_text('utf-8'), flags=re.M)
    quality=re.sub(r'^import .*?;\n', '', quality, flags=re.M)
    studio=re.sub(r'^import .*?;\n', '', (D/'studio.mjs').read_text('utf-8'), flags=re.M)
    html=html.replace('<link rel="stylesheet" href="studio.css">','<style>\n'+css+'\n</style>')
    html=html.replace('<script type="module" src="studio.mjs"></script>','<script>\n'+core+'\n'+samples+'\n'+quality+'\n'+studio+'\n</script>')
    path=D/'offline.html'
    path.write_text(html,encoding='utf-8')
    return path

if __name__=='__main__':print(build())
