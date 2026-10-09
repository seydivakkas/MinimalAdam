"""P3 structural/unit/integration tests; cannot certify real-world architecture."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from render_technical_diagram import (read_spec,render,port_pt,points_for,
                                      check_creature_contact)


class P3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs=sorted((ROOT/'examples/technical/specs').glob('*.json'))
        cls.raw=[json.loads(p.read_text(encoding='utf-8')) for p in cls.specs]

    def test_legacy_v05_character_key(self):
        import copy
        old=copy.deepcopy(self.raw[0])
        old['xiaohei']=old.pop('minimaladam')
        d=read_spec(old)
        self.assertIsNotNone(d.minimaladam)
        self.assertNotIn('minimaladam', old)
        broken=copy.deepcopy(old)
        broken['minimaladam']=broken['xiaohei']
        with self.assertRaisesRegex(ValueError,'hem xiaohei hem minimaladam'):
            read_spec(broken)

    def test_four_modes(self):
        self.assertEqual({x['mode'] for x in self.raw},
                         {'architecture','data-flow','ml-pipeline','engineering-system'})
        self.assertEqual(len(self.raw),4)

    def test_valid_specs(self):
        for data in self.raw:
            d=read_spec(data)
            self.assertGreaterEqual(len(d.edges),1)
            self.assertIsNotNone(d.minimaladam)

    def test_wrong_mode(self):
        a=copy.deepcopy(self.raw[0]);a['mode']='cad-simulation'
        with self.assertRaisesRegex(ValueError,'mode'):
            read_spec(a)

    def test_unknown_field(self):
        a=copy.deepcopy(self.raw[0]);a['unverified_claim']='true'
        with self.assertRaisesRegex(ValueError,'tanınmayan'):
            read_spec(a)

    def test_node_overlap_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['nodes'][1]['x']=a['nodes'][0]['x']
        with self.assertRaisesRegex(ValueError,'çakışması'):
            read_spec(a)

    def test_undefined_edge_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['edges'][0]['to']='ghost_backend'
        with self.assertRaisesRegex(ValueError,'kaynak/hedef'):
            read_spec(a)

    def test_duplicate_node_id(self):
        a=copy.deepcopy(self.raw[0]);a['nodes'][1]['id']=a['nodes'][0]['id']
        with self.assertRaisesRegex(ValueError,'benzersiz'):
            read_spec(a)

    def test_duplicate_edges(self):
        a=copy.deepcopy(self.raw[0]);a['edges'].append(a['edges'][0])
        with self.assertRaisesRegex(ValueError,'Tekrarlanan'):
            read_spec(a)

    def test_chinese_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['nodes'][0]['label']='数据'
        with self.assertRaisesRegex(ValueError,'NFC Türkçe'):
            read_spec(a)

    def test_bad_unicode_combining_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['nodes'][0]['label']='I\u0307stemci'
        with self.assertRaisesRegex(ValueError,'NFC'):
            read_spec(a)

    def test_nonfinite_coordinate_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['nodes'][0]['x']=float('nan')
        with self.assertRaisesRegex(ValueError,'sonlu'):
            read_spec(a)

    def test_node_too_small_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['nodes'][1]['w']=.05
        with self.assertRaisesRegex(ValueError,'genişliği'):
            read_spec(a)

    def test_missing_character_action_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['minimaladam']=None
        with self.assertRaisesRegex(ValueError,'karakter'):
            read_spec(a)

    def test_character_must_touch_flow(self):
        a=copy.deepcopy(self.raw[0]);a['minimaladam']['x']=.5;a['minimaladam']['y']=.77
        d=read_spec(a)
        lookup={n.ident:n for n in d.nodes}
        routes=[points_for(e,lookup) for e in d.edges]
        with self.assertRaisesRegex(ValueError,'uzak'):
            check_creature_contact(d.minimaladam,routes)

    def test_oversized_node_label_rejected(self):
        a=copy.deepcopy(self.raw[0]);a['nodes'][0]['label']='Yüksek Kapasiteli Veri Tabanı'
        with TemporaryDirectory() as temp:
            spec=Path(temp)/'bad.json';spec.write_text(json.dumps(a,ensure_ascii=False),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'sığmıyor'):
                render(spec,Path(temp)/'out')

    def test_crossing_third_node_rejected(self):
        a=copy.deepcopy(self.raw[0])
        # UI -> database is a straight horizontal connection that crosses API and logic.
        a['edges'][0]['to']='db'
        with TemporaryDirectory() as temp:
            spec=Path(temp)/'bad.json';spec.write_text(json.dumps(a,ensure_ascii=False),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'üçüncü düğüm'):
                render(spec,Path(temp)/'out')

    def test_generated_files_all_four(self):
        for p in self.specs:
            stem=p.stem
            folder=ROOT/'examples/technical/generated'
            for suff in ('.base.svg','.labels.svg','.svg','.png','.manifest.json'):
                self.assertTrue((folder/(stem+suff)).is_file(),stem+suff)
            with Image.open(folder/(stem+'.png')) as im:
                self.assertEqual(im.size,(1600,900))
            base=(folder/(stem+'.base.svg')).read_text(encoding='utf-8')
            layer=(folder/(stem+'.labels.svg')).read_text(encoding='utf-8')
            combined=(folder/(stem+'.svg')).read_text(encoding='utf-8')
            ET.fromstring(base);ET.fromstring(layer);ET.fromstring(combined)
            self.assertNotIn('<text ',base)
            self.assertIn('technical-base',combined)
            self.assertIn('turkish-label-layer',combined)
            self.assertIn('<text ',layer)
            self.assertIn('id="minimaladam"',base)
            self.assertIn(self.raw[self.specs.index(p)]['nodes'][0]['label'],layer)
            m=json.loads((folder/(stem+'.manifest.json')).read_text(encoding='utf-8'))
            self.assertEqual(m['source_sha256'],hashlib.sha256(p.read_bytes()).hexdigest())
            for k,v in m['outputs'].items():
                self.assertEqual(m['sha256'][k],hashlib.sha256((folder/v).read_bytes()).hexdigest())

    def test_single_render_reproducible(self):
        # Makinede seçilen TTF Windows ve Linux'ta farklı olabilir.
        # Aynı makinede yeniden üretim deterministik olmalı; Windows pikseli
        # Linux'ta CairoSVG ile alınmış örnekle özdeş olmak zorunda değil.
        with TemporaryDirectory() as temp:
            first=render(self.specs[2],Path(temp)/'first')
            second=render(self.specs[2],Path(temp)/'second')
            for k in ('base','labels','svg','png'):
                self.assertEqual(first[k].read_bytes(),second[k].read_bytes(),f'nondeterministic {k}')
            from PIL import ImageStat
            with Image.open(first['png']) as picture:
                self.assertEqual(picture.size,(1600,900))
                self.assertEqual(picture.format,'PNG')
                self.assertLess(min(ImageStat.Stat(picture.convert('L')).extrema[0]),250)
            manifest=json.loads(first['manifest'].read_text(encoding='utf-8'))
            self.assertEqual(manifest['sha256']['png'],hashlib.sha256(first['png'].read_bytes()).hexdigest())

    def test_windows_missing_cairo_dll_does_not_break_render(self):
        # Windows'ta CairoSVG Python wheel yuklu olsa dahi lib cairo-2.dll bulunmayabilir.
        from unittest.mock import patch
        with patch.dict(sys.modules, {'cairosvg': None, 'cairocffi': None}):
            with TemporaryDirectory() as temp:
                out=render(self.specs[2],Path(temp))
                self.assertTrue(out['png'].is_file())
                with Image.open(out['png']) as picture:
                    self.assertEqual(picture.size,(1600,900))

    def test_skill_tools_identical(self):
        for f in ['render_turkish_labels.py','render_technical_diagram.py','raster_pillow.py']:
            self.assertEqual((ROOT/'tools'/f).read_bytes(),
                             (ROOT/'minimaladam/scripts'/f).read_bytes())
        for p in self.specs:
            self.assertEqual(p.read_bytes(),(ROOT/'minimaladam/examples/technical'/p.name).read_bytes())

    def test_manual_semantics_disclaimer(self):
        m=json.loads((ROOT/'examples/technical/generated/04-muhendislik-sistemi.manifest.json').read_text(encoding='utf-8'))
        self.assertTrue(m['qa']['manual_visual_review_required'])
        self.assertTrue(m['qa']['semantic_structure_not_automatically_verified'])

if __name__=='__main__':
    unittest.main()
