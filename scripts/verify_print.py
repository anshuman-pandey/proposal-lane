"""Verify the long browser-print fixture (requires Poppler pdftotext)."""
import re,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/proposal-print-pass')
raw=subprocess.check_output(['pdftotext',str(root/'long-proposal.pdf'),'-'],text=True)
for prefix,count in [('SCOPE',80),('ITEM',100)]:
    for i in range(count):
        marker=f'{prefix}{i:03}'
        assert len(re.findall(r'\b'+marker+r'\b',raw))==1,marker+' missing or duplicated'
assert '16502.18' in raw,'Incorrect or missing grand total'
assert 'Owner key' not in raw and 'Create client snapshot' not in raw
xml=subprocess.check_output(['pdftotext','-bbox',str(root/'long-proposal.pdf'),'-'])
doc=ET.fromstring(xml);ns={'x':'http://www.w3.org/1999/xhtml'};pages=doc.findall('.//x:page',ns)
assert len(pages)>2
for page in pages:
    width=float(page.attrib['width']);height=float(page.attrib['height'])
    words=page.findall('.//x:word',ns);assert words,'Blank page'
    for word in words:
        a={k:float(v) for k,v in word.attrib.items()}
        assert 40<=a['xMin']<=a['xMax']<=width-40,(word.text,a)
        assert 40<=a['yMin']<=a['yMax']<=height-40,(word.text,a)
print(f'PASS: {len(pages)} pages; all 180 markers exactly once, correct total, no editor controls, all text inside page margins')
