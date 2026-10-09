"""P1/P2 kabul testleri; model tabanlı görsel kaliteyi kanıtlamaz."""
from __future__ import annotations
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from render_turkish_labels import (parse_labels, verify_glyphs, get_font_path,
                                   rectangles, render)

class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = sorted((ROOT/'examples/specs').glob('*.labels.json'))
        cls.font = get_font_path()

    def test_three_sample_pairs(self):
        self.assertEqual(len(self.samples), 3)
        for spec in self.samples:
            prefix = spec.name.removesuffix('.labels.json')
            self.assertTrue((ROOT/'examples/specs'/(prefix+'.base.svg')).is_file())
            self.assertTrue((ROOT/'examples/generated'/(prefix+'.base.png')).is_file())
            self.assertTrue((ROOT/'minimaladam/assets/examples'/(prefix+'.png')).is_file())

    def test_consistent_character_symbol(self):
        import re
        bodies = []
        for file in sorted((ROOT/'examples/specs').glob('*.base.svg')):
            svg = file.read_text(encoding='utf-8')
            self.assertNotIn('<text',svg)
            m = re.search(r'<g id="minimaladam">(.*?)</g>', svg, re.S)
            self.assertIsNotNone(m)
            self.assertIn('use xlink:href="#minimaladam"', svg)
            bodies.append(m.group(1))
        self.assertEqual(len(set(bodies)),1)

    def test_turkish_glyphs_available(self):
        verify_glyphs(self.font,['Çığır Açıldı','Öğrenci','Şüpheli','İşaret','Düğümler'])

    def test_valid_example_labels(self):
        for sample in self.samples:
            labels=parse_labels(json.loads(sample.read_text(encoding='utf-8')))
            self.assertLessEqual(len(labels),8)
            rectangles(labels,self.font,1600,900)

    def test_end_to_end(self):
        sample=self.samples[0]
        base=ROOT/'examples/generated'/(sample.name.removesuffix('.labels.json')+'.base.png')
        with TemporaryDirectory() as d:
            output=Path(d)/'example.png'
            paths=render(base,sample,output)
            self.assertTrue(all(p.is_file() for p in paths.values()))
            with Image.open(paths['image']) as final, Image.open(paths['overlay']) as overlay, Image.open(base) as img:
                self.assertEqual(final.size,(1600,900))
                self.assertEqual(overlay.mode,'RGBA')
                self.assertIsNotNone(overlay.getbbox())
                self.assertNotEqual(final.convert('RGB').tobytes(),img.convert('RGB').tobytes())
            manifest=json.loads(paths['manifest'].read_text(encoding='utf-8'))
            self.assertTrue(manifest['qa']['no_clipping'])
            self.assertTrue(manifest['qa']['turkish_glyphs_present'])
            self.assertIn('Dağınık bilgi', [x['text'] for x in manifest['labels']])
            self.assertIn('Dağınık bilgi',paths['svg'].read_text(encoding='utf-8'))

    def test_too_many_labels(self):
        with self.assertRaisesRegex(ValueError,'en fazla'):
            parse_labels({'version':1,'labels':[{'text':str(i),'x':0.5,'y':0.5} for i in range(9)]})

    def test_wrong_unicode(self):
        with self.assertRaisesRegex(ValueError,'Unicode'):
            parse_labels({'version':1,'labels':[{'text':'I\u0307stanbul','x':.5,'y':.5}]})

    def test_bad_coordinates(self):
        with self.assertRaisesRegex(ValueError,'x/y'):
            parse_labels({'version':1,'labels':[{'text':'Sorun','x':1.1,'y':.5}]})

    def test_collision(self):
        l=parse_labels({'version':1,'labels':[
            {'text':'Çözüm','x':.5,'y':.5},{'text':'Başlangıç','x':.5,'y':.5}]})
        with self.assertRaisesRegex(ValueError,'çakışması'):
            rectangles(l,self.font,1600,900)

    def test_clipping(self):
        l=parse_labels({'version':1,'labels':[{'text':'Düğümler','x':.01,'y':.01}]})
        with self.assertRaisesRegex(ValueError,'taşıyor'):
            rectangles(l,self.font,1600,900)

    def test_chinese_label_rejected(self):
        with self.assertRaisesRegex(ValueError,'Çince'):
            parse_labels({'version':1,'labels':[{'text':'中文','x':.5,'y':.5}]})

    def test_169_only(self):
        with TemporaryDirectory() as d:
            base=Path(d)/'square.png'
            Image.new('RGB',(400,400),'white').save(base)
            with self.assertRaisesRegex(ValueError,'16:9'):
                render(base,self.samples[0],Path(d)/'out.png')

    def test_spec_version(self):
        with self.assertRaisesRegex(ValueError,'version'):
            parse_labels({'version':2,'labels':[]})

if __name__=='__main__':
    unittest.main()
