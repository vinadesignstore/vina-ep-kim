"""Add a closer-dot i alternate to the approved four-master font.

Run once with the current source and export backed up in build/close-i/.
Requires fonttools[woff] and openstep-plist. Outputs remain candidates in build/.
"""
from copy import deepcopy
from pathlib import Path
import re

import openstep_plist
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.otlLib.builder import buildLookup, buildSingleSubstSubtable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/close-i"
ALT = "i.ss02"


def source():
    text = (OUT / "VinaEpKim.glyphs").read_text()
    raw = openstep_plist.loads(text, use_numbers=True)
    assert not any(g['glyphname'] == ALT for g in raw['glyphs'])
    original = next(g for g in raw['glyphs'] if g['glyphname'] == 'i')
    alternate = deepcopy(original)
    alternate['glyphname'] = ALT
    alternate.pop('unicode')
    masters = {m['id']: m['axesValues'] for m in raw['fontMaster']}
    for layer in alternate['layers']:
        weight, italic = masters[layer['layerId']]
        dy = -28 if weight == 400 else -47
        dx = (-6 if weight == 400 else -10) if italic else 0
        dot = layer['shapes'][1]
        dot['alignment'] = -1
        dot.pop('anchor', None)
        dot['pos'] = [dot['pos'][0] + dx, dot['pos'][1] + dy]
    marker = '{\nglyphname = i.ss01;'
    assert text.count(marker) == 1
    text = text.replace(marker, openstep_plist.dumps(alternate, indent=0) + ',\n' + marker)
    text = text.replace('features = (', 'features = (\n{\ncode = "sub i by i.ss02;";\nlabels = ({language = dflt; value = "Closer i dot";});\ntag = ss02;\n},', 1)
    text = text.replace('sub i from [i.ss01];', 'sub i from [i.ss01 i.ss02];')
    # Preserve every explicit pair exception involving the original glyph.
    table = deepcopy(raw['kerningLTR'])
    for pairs in table.values():
        if 'i' in pairs:
            pairs[ALT] = deepcopy(pairs['i'])
        for row in pairs.values():
            if 'i' in row:
                row[ALT] = row['i']
    start = text.index('kerningLTR = ') + len('kerningLTR = ')
    end = start
    depth = 0
    for end in range(start, len(text)):
        if text[end] == '{': depth += 1
        elif text[end] == '}':
            depth -= 1
            if depth == 0: break
    text = text[:start] + openstep_plist.dumps(table, indent=0) + text[end + 1:]
    checked = openstep_plist.loads(text, use_numbers=True)
    assert [g for g in checked['glyphs'] if g['glyphname'] != ALT] == raw['glyphs']
    (ROOT / 'sources/VinaEpKim.glyphs').write_text(text)


def binary():
    font = TTFont(OUT / 'VinaEpKim-VF.ttf', recalcTimestamp=False)
    font.ensureDecompiled()
    assert ALT not in font.getGlyphOrder()
    font.setGlyphOrder(font.getGlyphOrder() + [ALT])
    font['glyf'][ALT] = deepcopy(font['glyf']['i'])
    dot = font['glyf'][ALT].components[1]
    dot.y -= 28
    font['hmtx'][ALT] = font['hmtx']['i']
    font['gvar'].variations[ALT] = deepcopy(font['gvar'].variations['i'])
    for variation in font['gvar'].variations[ALT]:
        dx, dy = variation.coordinates[1]
        if set(variation.axes) == {'wght'}: dy -= 19
        elif set(variation.axes) == {'ital'}: dx -= 6
        elif set(variation.axes) == {'wght', 'ital'}: dx -= 4
        else: raise ValueError('Unexpected variation region')
        variation.coordinates[1] = (dx, dy)
    classes = font['GDEF'].table.GlyphClassDef.classDefs
    if 'i' in classes:
        classes[ALT] = classes['i']
    for lookup in font['GPOS'].table.LookupList.Lookup:
        for wrapper in lookup.SubTable:
            sub = getattr(wrapper, 'ExtSubTable', wrapper)
            if isinstance(sub, otTables.PairPos):
                assert sub.Format == 1
                if 'i' in sub.Coverage.glyphs:
                    index = sub.Coverage.glyphs.index('i')
                    sub.Coverage.glyphs.append(ALT)
                    sub.PairSet.append(deepcopy(sub.PairSet[index]))
                    sub.PairSetCount += 1
                for pairs in sub.PairSet:
                    for pair in list(pairs.PairValueRecord):
                        if pair.SecondGlyph == 'i':
                            added = deepcopy(pair)
                            added.SecondGlyph = ALT
                            pairs.PairValueRecord.append(added)
                            pairs.PairValueCount += 1
            elif isinstance(sub, otTables.MarkBasePos) and 'i' in sub.BaseCoverage.glyphs:
                index = sub.BaseCoverage.glyphs.index('i')
                sub.BaseCoverage.glyphs.append(ALT)
                sub.BaseArray.BaseRecord.append(deepcopy(sub.BaseArray.BaseRecord[index]))
                sub.BaseArray.BaseCount += 1
    gsub = font['GSUB'].table
    for lookup in gsub.LookupList.Lookup:
        for wrapper in lookup.SubTable:
            sub = getattr(wrapper, 'ExtSubTable', wrapper)
            if isinstance(sub, otTables.AlternateSubst) and 'i' in sub.alternates:
                sub.alternates['i'].append(ALT)
    lookup_index = len(gsub.LookupList.Lookup)
    gsub.LookupList.Lookup.append(buildLookup([buildSingleSubstSubtable({'i': ALT})]))
    gsub.LookupList.LookupCount += 1
    record = otTables.FeatureRecord()
    record.FeatureTag = 'ss02'
    record.Feature = otTables.Feature()
    record.Feature.LookupListIndex = [lookup_index]
    record.Feature.LookupCount = 1
    params = otTables.FeatureParamsStylisticSet()
    params.Version = 0
    params.UINameID = font['name'].addName('Closer i dot')
    record.Feature.FeatureParams = params
    records = gsub.FeatureList.FeatureRecord
    index = next((i for i, r in enumerate(records) if r.FeatureTag > 'ss02'), len(records))
    records.insert(index, record)
    gsub.FeatureList.FeatureCount += 1
    for script in gsub.ScriptList.ScriptRecord:
        languages = [script.Script.DefaultLangSys] + [r.LangSys for r in script.Script.LangSysRecord]
        for lang in languages:
            if lang is None: continue
            lang.FeatureIndex = sorted([i + (i >= index) for i in lang.FeatureIndex] + [index])
            lang.FeatureCount = len(lang.FeatureIndex)
            if lang.ReqFeatureIndex != 0xFFFF and lang.ReqFeatureIndex >= index:
                lang.ReqFeatureIndex += 1
    font.save(OUT / 'VinaEpKim-CloseI.ttf')
    font.flavor = 'woff2'
    font.save(OUT / 'VinaEpKim-CloseI.woff2')


if __name__ == '__main__':
    source()
    binary()
    print('Added i.ss02 and ss02; candidates saved in build/close-i.')
