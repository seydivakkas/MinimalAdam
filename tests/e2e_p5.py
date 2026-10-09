#!/usr/bin/env python3
"""P5 QA browser E2E: real offline HTML, warning preflight, report export and reset."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]


def run():
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True, **({'executable_path':'/usr/bin/chromium'} if Path('/usr/bin/chromium').exists() else {}),args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1580,'height':980},accept_downloads=True)
        errors=[];page.on('pageerror',lambda err: errors.append(str(err)))
        page.set_content((ROOT/'editor/offline.html').read_text(encoding='utf-8'),wait_until='domcontentloaded')
        assert page.locator('#qa-counts').inner_text().startswith('PASS')
        assert '4 manuel' in page.locator('#qa-manual').inner_text()
        page.locator('[data-node-id="train"]').click()
        label=page.locator('[data-field="label"]')
        label.fill('Çok Çok Uzun Türkçe Etiket');label.press('Tab')
        assert 'REVIEW' in page.locator('#qa-counts').inner_text()
        assert page.locator('#qa-findings .qa-finding').count()>=1
        assert not page.locator('#qa-preflight').is_hidden()
        page.screenshot(path=str(ROOT/'examples/editor/studio-qa-preview.png'),full_page=True)
        # An unacknowledged warning blocks export, without producing a file.
        page.locator('#export-svg').click()
        assert 'QA REVIEW' in page.locator('#toast').inner_text()
        # Both JSON audit and SVG remain independently downloadable.
        with tempfile.TemporaryDirectory() as temp:
            temp=Path(temp)
            with page.expect_download() as download: page.locator('#qa-report').click()
            reportpath=temp/'audit.json';download.value.save_as(reportpath)
            report=json.loads(reportpath.read_text('utf-8'))
            assert report['summary']['automatedStatus']=='REVIEW'
            assert all(x['status']=='NOT_VERIFIED' for x in report['manualChecks'])
            assert report['provenance']['sourceProject']['spec']['nodes']
            assert not report['provenance']['warningsAcknowledged']
            page.locator('#qa-accept').check()
            with page.expect_download() as download:page.locator('#export-svg').click()
            svgpath=temp/'editable.svg';download.value.save_as(svgpath)
            assert '<metadata id="minimaladam-editable-spec">' in svgpath.read_text('utf-8')
            with page.expect_download() as download:page.locator('#qa-report').click()
            download.value.save_as(reportpath)
            assert json.loads(reportpath.read_text('utf-8'))['provenance']['warningsAcknowledged']
            # Any source modification invalidates prior acknowledgement.
            page.locator('[data-node-id="artifact"]').click()
            page.locator('[data-field="label"]').fill('Yeni Model');page.locator('[data-field="label"]').press('Tab')
            assert not page.locator('#qa-accept').is_checked()
            page.locator('#export-svg').click()
            assert 'QA REVIEW' in page.locator('#toast').inner_text()
        assert not errors,errors
        browser.close()
    print('P5 E2E PASS: offline QA report, real warning, export gate, accepted override, change invalidates override, screenshot.')

if __name__=='__main__':run()
