"""Normalize release names without rebuilding outlines or layout tables.

Requires fontTools and Brotli. Run after approving the source family name.
"""
from hashlib import sha256
import json
from pathlib import Path

from fontTools.ttLib import TTFont


def normalize(path):
    font = TTFont(path, recalcTimestamp=False)
    before = {tag: font.getTableData(tag) for tag in font.keys()
              if tag not in {"GlyphOrder", "head", "name"}}
    names = font["name"]
    replacements = {
        1: "Vina Ep Kim",
        3: names.getDebugName(3).rsplit(";", 1)[0] + ";VinaEpKim-Regular",
        4: "Vina Ep Kim Regular", 6: "VinaEpKim-Regular",
        16: "Vina Ep Kim", 25: "VinaEpKim",
    }
    for instance in font["fvar"].instances:
        style = names.getDebugName(instance.subfamilyNameID)
        if not style or instance.postscriptNameID == 0xFFFF:
            raise ValueError("Missing instance naming record")
        replacements[instance.postscriptNameID] = "VinaEpKim-" + style.replace(" ", "")
    for record in names.names:
        if record.nameID in replacements:
            record.string = replacements[record.nameID].encode(record.getEncoding())
    temporary = path.with_name(path.name + ".tmp")
    try:
        font.save(temporary)
        with TTFont(temporary) as checked:
            for tag, data in before.items():
                if checked.getTableData(tag) != data:
                    raise ValueError(f"Unexpected change to {tag}")
            for name_id, value in replacements.items():
                if checked["name"].getDebugName(name_id) != value:
                    raise ValueError(f"Name {name_id} failed verification")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
        font.close()
    print(f"Names verified; all non-naming tables preserved: {path.name}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    source = root / "sources/VinaEpKim.glyphs"
    if 'familyName = "Vina Ep Kim";' not in source.read_text():
        raise ValueError("Update the source family name first")
    manifest_path = root / "release.json"
    manifest = json.loads(manifest_path.read_text())
    for relative in manifest["sha256"]:
        if Path(relative).suffix in {".ttf", ".woff2"}:
            normalize(root / relative)
    manifest["sha256"] = {
        relative: sha256((root / relative).read_bytes()).hexdigest()
        for relative in manifest["sha256"]
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
