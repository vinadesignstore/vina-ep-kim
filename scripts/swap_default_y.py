"""Swap the default and Set 1 Y designs, preserving each design's spacing.

Run once; saves backups and validated candidates under build/default-y/.
"""
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re

import openstep_plist
from fontTools.ttLib import TTFont
from fontTools.ttLib.reorderGlyphs import reorderGlyphs
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/default-y'
BASES = ['Y', 'Yacute', 'Ygrave', 'Yhookabove', 'Ytilde', 'Ydotbelow']
SWAP = {a: b for n in BASES for a, b in [(n, n + '.ss01'), (n + '.ss01', n)]}


def rename(value):
    if isinstance(value, str):
        return SWAP.get(value, value)
    if isinstance(value, list):
        return [rename(v) for v in value]
    if isinstance(value, dict):
        return {SWAP.get(k, k): rename(v) for k, v in value.items()}
    return value


def block(text, marker):
    start = text.index(marker)
    pos = text.index('{', start)
    depth = 0
    quoted = escaped = False
    for end in range(pos, len(text)):
        c = text[end]
        if escaped:
            escaped = False
            continue
        if quoted and c == '\\':
            escaped = True
        elif c == '"':
            quoted = not quoted
        elif not quoted:
            depth += (c == '{') - (c == '}')
            if depth == 0:
                return start, end + 1
    raise ValueError('Unclosed source block')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    backup = OUT / 'before.glyphs'
    if backup.exists():
        raise SystemExit('Already run: use the existing backup, do not swap twice.')
    source = ROOT / 'sources/VinaEpKim.glyphs'
    text = source.read_text()
    raw = openstep_plist.loads(text, use_numbers=True)
    glyphs = {g['glyphname']: g for g in raw['glyphs']}
    edits = []
    for name, other in SWAP.items():
        changed = rename(deepcopy(glyphs[other]))
        changed.pop('unicode', None)
        if 'unicode' in glyphs[name]:
            changed['unicode'] = glyphs[name]['unicode']
        start, end = block(text, '{\nglyphname = ' + name + ';')
        edits.append((start, end, openstep_plist.dumps(changed, indent=0)))
    start, end = block(text, 'kerningLTR = {')
    tokens = re.compile(r'(?<![\w.])(' + '|'.join(re.escape(n) for n in sorted(SWAP, key=len, reverse=True)) + r')(?![\w.])')
    edits.append((start, end, tokens.sub(lambda m: SWAP[m[1]], text[start:end])))
    candidate = text
    for start, end, replacement in sorted(edits, reverse=True):
        candidate = candidate[:start] + replacement + candidate[end:]
    checked = openstep_plist.loads(candidate, use_numbers=True)
    assert checked['features'] == raw['features']
    assert [g for g in checked['glyphs'] if g['glyphname'] not in SWAP] == [g for g in raw['glyphs'] if g['glyphname'] not in SWAP]

    path = ROOT / 'fonts/variable/VinaEpKim-VF.ttf'
    old = TTFont(path, recalcTimestamp=False)
    old.ensureDecompiled()
    binary_swap = {}
    for name in BASES:
        base = old.getBestCmap()[glyphs[name]['unicode']]
        alternate = base + '.ss01'
        assert alternate in old.getGlyphOrder()
        binary_swap.update({base: alternate, alternate: base})
    xml = BytesIO()
    old.saveXML(xml)
    pattern = re.compile(r'"(' + '|'.join(re.escape(n) for n in sorted(binary_swap, key=len, reverse=True)) + r')"')
    swapped = pattern.sub(lambda m: '"' + binary_swap[m[1]] + '"', xml.getvalue().decode())
    new = TTFont(recalcTimestamp=False)
    new.importXML(BytesIO(swapped.encode()))
    reorderGlyphs(new, old.getGlyphOrder())
    # Keep Unicode and feature semantics; all shape-dependent tables follow the swap.
    new['cmap'] = deepcopy(old['cmap'])
    new['GSUB'] = deepcopy(old['GSUB'])
    new.save(OUT / 'VinaEpKim-VF.ttf')
    loaded = TTFont(OUT / 'VinaEpKim-VF.ttf')
    assert loaded.getBestCmap() == old.getBestCmap()
    for name in old.getGlyphOrder():
        expected = binary_swap.get(name, name)
        assert loaded['hmtx'][name] == old['hmtx'][expected]

    def shape(data, text, weight, italic, alternate, remap=False):
        font = hb.Font(hb.Face(data))
        font.set_variations({'wght': weight, 'ital': italic})
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {'ss01': alternate})
        names = old.getGlyphOrder()
        return [(binary_swap.get(names[i.codepoint], names[i.codepoint]) if remap else names[i.codepoint], p.x_advance, p.y_advance, p.x_offset, p.y_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]

    old_bytes = path.read_bytes()
    new_bytes = (OUT / 'VinaEpKim-VF.ttf').read_bytes()
    for weight in range(400, 701, 25):
        for italic in [0, .25, .5, .75, 1]:
            for word in ['Y', 'ÝỲỶỸỴ', 'AY YA TY YO', 'Y\u0301Y\u0300Y\u0309Y\u0303Y\u0323']:
                for alt in [False, True]:
                    actual = shape(new_bytes, word, weight, italic, alt)
                    expected = shape(old_bytes, word, weight, italic, not alt, True)
                    assert actual == expected, (word, weight, italic, alt, actual, expected)
            for alt in [False, True]:
                assert shape(new_bytes, 'vina design store street', weight, italic, alt) == shape(old_bytes, 'vina design store street', weight, italic, alt)
    backup.write_text(text)
    (OUT / 'before.ttf').write_bytes(old_bytes)
    (OUT / 'VinaEpKim.glyphs').write_text(candidate)
    loaded.flavor = 'woff2'
    loaded.save(OUT / 'VinaEpKim-VF.woff2')
    source.write_text(candidate)
    path.write_bytes(new_bytes)
    (ROOT / 'fonts/web/VinaEpKim-VF.woff2').write_bytes((OUT / 'VinaEpKim-VF.woff2').read_bytes())
    manifest_path = ROOT / 'release.json'
    manifest = json.loads(manifest_path.read_text())
    for relative in manifest['sha256']:
        manifest['sha256'][relative] = sha256((ROOT / relative).read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print('Swapped six Y designs; verified shaping and spacing at 65 axis locations.')


if __name__ == '__main__':
    main()
