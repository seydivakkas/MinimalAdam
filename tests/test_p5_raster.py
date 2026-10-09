import importlib.util
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('inspect_render',ROOT/'tools/inspect_render.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class QAImageTests(unittest.TestCase):
    def test_original_png_examples_pass(self):
        for path in (ROOT/'examples/technical/generated').glob('*.png'):
            with self.subTest(path=path):
                result=mod.inspect_png(path)
                self.assertEqual(result['summary']['status'],'PASS')
                self.assertEqual(result['metrics']['size'],[1600,900])
        self.assertEqual(mod.inspect_png(ROOT/'examples/generated/01-bilgiyi-suz.png')['summary']['status'],'PASS')
    def test_wrong_dimensions_fail(self):
        with TemporaryDirectory() as td:
            file=Path(td)/'bad.png';Image.new('RGB',(800,500),'white').save(file)
            res=mod.inspect_png(file);self.assertEqual(res['summary']['status'],'FAIL')
            self.assertIn('PNG_DIMENSIONS',[i['code'] for i in res['issues']])
    def test_blank_is_rejected(self):
        with TemporaryDirectory() as td:
            file=Path(td)/'empty.png';Image.new('RGB',(1600,900),'white').save(file)
            self.assertIn('PNG_EMPTY',[i['code'] for i in mod.inspect_png(file)['issues']])
    def test_dense_colored_image_is_reviewed(self):
        with TemporaryDirectory() as td:
            file=Path(td)/'heavy.png';Image.new('RGB',(1600,900),(40,210,100)).save(file)
            issues=[x['code'] for x in mod.inspect_png(file)['issues']]
            self.assertIn('PNG_DENSE',issues);self.assertIn('PNG_PALETTE',issues)
    def test_missing_file_fails_closed(self):
        result=mod.inspect_png(ROOT/'does-not-exist.png')
        self.assertEqual(result['summary']['status'],'FAIL')
if __name__=='__main__':unittest.main()
