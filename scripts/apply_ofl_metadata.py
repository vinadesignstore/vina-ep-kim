"""Align approved exports with the source's OFL metadata; preserve font design."""
from pathlib import Path
from hashlib import sha256
import json
from glyphsLib import GSFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = GSFont(ROOT / 'sources/VinaEpKim.glyphs')
    copyright = (ROOT / 'OFL.txt').read_text().splitlines()[0]
    license_text = source.customParameters['license']
    license_url = source.customParameters['licenseURL']
    assert source.copyright == copyright
    assert source.customParameters['fsType'] == []
    assert 'SIL Open Font License, Version 1.1' in license_text
    assert license_url == 'https://openfontlicense.org'
    path = ROOT / 'fonts/variable/VinaEpKim-VF.ttf'
    font = TTFont(path)
    before = {tag:font.getTableData(tag) for tag in font.keys() if tag != 'GlyphOrder'}
    font['OS/2'].fsType = 0
    for name_id, value in ((0,copyright),(13,license_text),(14,license_url)):
        for record in list(font['name'].names):
            if record.nameID == name_id:
                font['name'].removeNames(nameID=name_id,platformID=record.platformID,
                                         platEncID=record.platEncID,langID=record.langID)
        font['name'].setName(value,name_id,3,1,0x409)
        font['name'].setName(value,name_id,1,0,0)
    temporary = path.with_suffix('.pending.ttf')
    font.save(temporary)
    checked = TTFont(temporary)
    for tag, data in before.items():
        if tag not in ('head','name','OS/2'):
            assert checked.getTableData(tag) == data, tag
    old_os2=TTFont(path)['OS/2']
    old_os2.fsType=0
    assert checked.getTableData('OS/2') == old_os2.compile(checked)
    assert checked['name'].getDebugName(0) == copyright
    assert checked['name'].getDebugName(13) == license_text
    assert checked['name'].getDebugName(14) == license_url
    checked.close();font.close()
    temporary.replace(path)
    web = TTFont(path); web.flavor='woff2'
    web.save(ROOT / 'fonts/web/VinaEpKim-VF.woff2')
    manifest_path=ROOT/'release.json'
    manifest=json.loads(manifest_path.read_text())
    manifest['sha256']={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in manifest['sha256']}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print('OFL metadata aligned. Only name, embedding permissions, and head changed.')


if __name__ == '__main__':
    main()
