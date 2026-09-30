"""Check candidate geometry, inherited spacing, feature selection, and proof."""
from io import BytesIO
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from PIL import Image, ImageDraw, ImageFont
import uharfbuzz as hb

root = Path(__file__).resolve().parents[1]
out = root / 'build/close-i'
old = TTFont(out / 'VinaEpKim-VF.ttf')
new = TTFont(out / 'VinaEpKim-CloseI.ttf')
for name in old.getGlyphOrder():
    assert old['glyf'][name].compile(old['glyf']) == new['glyf'][name].compile(new['glyf']), name
    assert old['hmtx'][name] == new['hmtx'][name], name
    assert str(old['gvar'].variations.get(name)) == str(new['gvar'].variations.get(name)), name

def gap(gs, name):
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    boxes = []
    bounds = BoundsPen(gs)
    for op, args in pen.value:
        getattr(bounds, op)(*args)
        if op in ('closePath', 'endPath'):
            boxes.append(bounds.bounds)
            bounds = BoundsPen(gs)
    boxes.sort(key=lambda b: b[1])
    assert len(boxes) == 2
    return boxes[1][1] - boxes[0][3]

order = new.getGlyphOrder()
for table in new['cmap'].tables:
    if table.isUnicode() and table.format in (4, 12):
        table.cmap.update({0xE000 + i: name for i, name in enumerate(order)})
data = BytesIO()
new.save(data)
font = hb.Font(hb.Face(data.getvalue()))
features = {r.FeatureTag: False for r in new['GSUB'].table.FeatureList.FeatureRecord}
def shape(text, options=None):
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.direction, buffer.script, buffer.language = 'ltr', 'Latn', 'vi'
    hb.shape(font, buffer, options if options is not None else features)
    return [(g.codepoint, p.x_advance, p.x_offset, p.y_offset)
            for g, p in zip(buffer.glyph_infos, buffer.glyph_positions)]

i_char, alt_char = [chr(0xE000 + order.index(n)) for n in ('i', 'i.ss02')]
checks = 0
for weight in range(400, 701, 25):
    for italic in (0, .25, .5, .75, 1):
        location = {'wght': weight, 'ital': italic}
        font.set_variations(location)
        gs = new.getGlyphSet(location=location)
        assert abs(gap(gs, 'i.ss02') - gap(gs, 'i') / 2) < .01, location
        assert gap(gs, 'i.ss02') > 0
        assert shape('i', {'ss02': True})[0][0] == order.index('i.ss02')
        assert shape('i', {'ss01': True})[0][0] == order.index('i.ss01')
        for n in range(len(order)):
            char = chr(0xE000 + n)
            for a, b in ((i_char + char, alt_char + char), (char + i_char, char + alt_char)):
                before, after = shape(a, {**features, 'kern': True}), shape(b, {**features, 'kern': True})
                assert [p[1:] for p in before] == [p[1:] for p in after], (weight, italic, order[n])
                checks += 1
print(f'Passed 65 axis locations and {checks} pair checks; all existing glyphs unchanged.')

image = Image.new('RGB', (1100, 840), 'white')
proof_font = out / 'proof-only.ttf'
proof_font.write_bytes(data.getvalue())
draw = ImageDraw.Draw(image)
label = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
for row, (weight, italic) in enumerate(((400, 0), (700, 0), (400, 1), (700, 1))):
    face = ImageFont.truetype(str(proof_font), 110)
    face.set_variation_by_axes([weight, italic])
    for col, close in enumerate((False, True)):
        x, y = 30 + col * 540, 20 + row * 205
        draw.text((x, y), f'{weight} {"Italic" if italic else "Upright"} / {"Closer dot" if close else "Default"}', font=label, fill='#555555')
        text = 'i ii mini'.replace('i', alt_char) if close else 'i ii mini'
        draw.text((x, y + 45), text, font=face, fill='#171717')
image.save(out / 'close-i-proof.png')
