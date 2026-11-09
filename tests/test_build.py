import unittest
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
class PagesTests(unittest.TestCase):
    def test_entry_uses_project_relative_feed(self):
        self.assertTrue((ROOT/'index.html').exists(), 'Pages index must exist')
        text=(ROOT/'index.html').read_text()
        self.assertIn("new URL('./data/press.csv',document.baseURI)",text)
        self.assertNotIn('127.0.0.1',text)
        self.assertNotIn('/Users/',text)
        self.assertNotIn("PRESS_PROXY_PATH='/api/press.csv'",text)
        self.assertIn('image_url',text)
        self.assertIn('antrail-issues',text)
    def test_only_expected_website_files_are_built(self):
        expected={'index.html','data/press.csv','data/sync.json','.nojekyll'}
        output=ROOT/'_site'
        self.assertTrue(output.is_dir(), 'Run build_pages.py first')
        actual={str(p.relative_to(output)) for p in output.rglob('*') if p.is_file()}
        self.assertEqual(actual,expected)
if __name__=='__main__':unittest.main()
