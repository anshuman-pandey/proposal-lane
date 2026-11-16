import json,re,unittest
from pathlib import Path
from html import unescape
class LocaleTests(unittest.TestCase):
 def test_static_text_errors_and_placeholders_have_spanish_translations(self):
  root=Path(__file__).resolve().parents[1];raw=(root/'static/messages.js').read_text();catalog=json.loads(raw[raw.index('{'):].strip().rstrip(';'))
  keys={unescape(s) for s in re.findall(r'data-i18n(?:-aria-label)?="([^"]*)"',(root/'static/index.html').read_text())}
  for f in ['server.py','estimates.py']:keys.update(re.findall(r"(?:Invalid\(|description=)'([^']*)'",(root/f).read_text()))
  self.assertFalse(keys-set(catalog))
  for source,translations in catalog.items():
   self.assertTrue(translations['es'].strip());self.assertEqual(set(re.findall(r'\{\d+\}',source)),set(re.findall(r'\{\d+\}',translations['es'])))
