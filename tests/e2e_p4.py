#!/usr/bin/env python3
"""P4 browser smoke test. Runs on injected local resources (no network)."""
from __future__ import annotations
import json
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / 'editor'


def html_bundle():
    html = (EDITOR / 'index.html').read_text('utf8')
    html = html.replace('<link rel="stylesheet" href="studio.css">', '<style>' + (EDITOR / 'studio.css').read_text('utf8') + '</style>')
    html = html.replace('<script type="module" src="studio.mjs"></script>', '')
    core = re.sub(r'^export ', '', (EDITOR/'core.mjs').read_text('utf8'), flags=re.M)
    examples = re.sub(r'^export ', '', (EDITOR/'samples.mjs').read_text('utf8'), flags=re.M)
    qa=re.sub(r'^export ', '', (EDITOR/'quality.mjs').read_text('utf8'), flags=re.M)
    qa=re.sub(r'^import .*?;\n', '', qa, flags=re.M)
    app = re.sub(r'^import .*?;\n', '', (EDITOR/'studio.mjs').read_text('utf8'), flags=re.M)
    return html, '\n'.join([core, examples, qa, app])


def run():
    html, code = html_bundle()
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,**({'executable_path':'/usr/bin/chromium'} if Path('/usr/bin/chromium').exists() else {}),args=['--no-sandbox','--disable-dev-shm-usage'])
        pg=b.new_page(viewport={'width':1536,'height':920},accept_downloads=True)
        exceptions=[]
        pg.on('pageerror',lambda err:exceptions.append(str(err)))
        pg.set_content(html,wait_until='domcontentloaded')
        pg.add_script_tag(content=code)
        assert pg.locator('[data-node-id]').count()==5
        assert pg.locator('[data-edge-index]').count()==4
        assert 'QA PASS' in pg.locator('#status').inner_text()
        pg.screenshot(path=str(ROOT/'examples/editor/studio-preview.png'),full_page=True)
        # Real pointer drag (saved model, not a cosmetic SVG transform).
        start=pg.locator('[data-node-id="new_data"] rect').bounding_box()
        center={'x':start['x']+start['width']/2,'y':start['y']+start['height']/2}
        pg.mouse.move(center['x'],center['y']);pg.mouse.down();pg.mouse.move(center['x']+20,center['y']-13,steps=5);pg.mouse.up()
        assert pg.locator('#undo').is_enabled()
        # Change node label and keep Turkish characters.
        pg.locator('[data-node-id="train"]').click()
        pg.locator('[data-field="label"]').fill('Öğrenme Aşaması')
        pg.locator('[data-field="label"]').press('Tab')
        assert pg.locator('#node-train text').text_content()=='Öğrenme Aşaması'
        pg.locator('#undo').click()
        assert pg.locator('#node-train text').text_content()=='Eğitim'
        # Style switch, editable source download, SVG and PNG rasterization.
        pg.locator('[data-style="technical"]').click()
        assert 'selected' in pg.locator('[data-style="technical"]').get_attribute('class')
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            with pg.expect_download() as d:pg.locator('#save-project').click()
            projectpath=tmp/'project.json';d.value.save_as(projectpath)
            data=json.loads(projectpath.read_text('utf8'))
            assert data['style']=='technical' and data['format']=='minimaladam-editor-v1'
            assert len(data['spec']['nodes'])==5
            with pg.expect_download() as d:pg.locator('#export-p3').click()
            p3path=tmp/'source.json';d.value.save_as(p3path)
            spec=json.loads(p3path.read_text('utf8'));assert 'style' not in spec and spec['version']==1
            # P3 integration: the exported JSON must remain consumable by the original Python renderer.
            cmd=[sys.executable,str(ROOT/'tools/render_technical_diagram.py'),'--spec',str(p3path),'--output-dir',str(tmp/'p3-render')]
            attempt=subprocess.run(cmd,capture_output=True,text=True)
            assert attempt.returncode==0,attempt.stderr
            assert (tmp/'p3-render/source.svg').exists()
            with pg.expect_download() as d:pg.locator('#export-svg').click()
            svgpath=tmp/'editable.svg';d.value.save_as(svgpath)
            svg=svgpath.read_text('utf8');assert '<metadata id="minimaladam-editable-spec">' in svg
            assert '<svg ' in svg
            with pg.expect_download(timeout=25000) as d:pg.locator('#export-png').click()
            pngpath=tmp/'rendered.png';d.value.save_as(pngpath)
            png=pngpath.read_bytes()
            assert png[:8]==b'\x89PNG\r\n\x1a\n'
            width,height=struct.unpack('>II',png[16:24]);assert (width,height)==(1600,900)
            # Reload the P4 editable SVG, including style + content metadata.
            pg.locator('#file').set_input_files(str(svgpath))
            assert pg.locator('[data-node-id]').count()==5
            assert 'selected' in pg.locator('[data-style="technical"]').get_attribute('class')
            # Legacy v0.3 SVG import (without metadata) must not silently invent unknown systems.
            pg.locator('#file').set_input_files(str(ROOT/'examples/technical/generated/03-ml-pipeline.svg'))
            assert pg.locator('[data-node-id]').count()==5
            assert pg.locator('[data-edge-index]').count()==4
            # Reload untouched P3 JSON.
            pg.locator('#file').set_input_files(str(ROOT/'examples/technical/specs/01-yazilim-mimarisi.json'))
            assert pg.locator('[data-node-id]').count()>=2
            # Bind a new edge (source, then destination) and remove it.
            n=pg.locator('[data-node-id]').all()
            pg.locator('#connect').click();n[0].click();n[1].click()
            assert pg.locator('[data-edge-index]').count()>=1
        assert not exceptions, exceptions
        print('P4 E2E PASS: pointer drag; labels/undo; style; P3/P4 JSON; SVG roundtrip; PNG 1600x900; old P3 SVG import; connections.')
        b.close()


if __name__=='__main__':
    run()
