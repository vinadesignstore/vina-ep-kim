# Vina Ep Kim

Variable typeface with Vietnamese support, upright and italic styles.

## Files

- `sources/VinaEpKim.glyphs`: authoritative editable source; four masters.
- `fonts/variable/VinaEpKim-VF.ttf`: approved desktop variable font.
- `fonts/web/VinaEpKim-VF.woff2`: approved web variable font.
- `release.json`: SHA-256 checksums for this approved snapshot.

Axes: `wght` 400-700 and `ital` 0-1. The font contains eight named instances.

The installed family is `Vina Ep Kim`; PostScript names use the `VinaEpKim`
prefix followed by the style. Version numbers belong in version metadata,
not the family name. Branding may use Vina Ép Kim.

## Editing And Exports

Open the source in Glyphs 4. Keep experimental exports in `build/`, which is
excluded from Git. The checked-in binaries are the approved release, not scratch
exports.

The current export workflow includes a fontTools kerning finalization step after
Glyphs export. A standalone build command has not yet been migrated to this
repository. Do not replace the release files with an unchecked native export.
Before releasing changes, check interpolation, kerning, accent placement,
Vietnamese normalization, and variable-font rendering across both axes.

## Verify This Snapshot

```sh
python3 scripts/verify_release.py
```

This checks file integrity against the release manifest, not visual quality.
Update the manifest only after approving and validating a new source/export set.

To normalize exported naming metadata, install `fonttools[woff]` in a Python
virtual environment and run `python scripts/normalize_names.py`. It verifies
that non-naming tables stay unchanged and refreshes the release checksums.

## Distribution

Releases are intended to be public. A distribution license still needs to be
selected; public download availability is not an open-source license.

## macOS Install And Update

Download `vina-font` from a published GitHub release, then run:

```sh
bash ~/Downloads/vina-font install
bash ~/Downloads/vina-font update
bash ~/Downloads/vina-font status
```

The default release repository is `vinadesignstore/vina-ep-kim`.
An optional second argument overrides it as `OWNER/REPO`. No administrator access,
Python, GitHub login, or package manager is needed. Downloads are checked against
the release's SHA-256 manifest. Existing managed installations are backed up in
`~/Library/Application Support/VinaEpKim/backups` before replacement. Other font
files are not removed. Restart open design apps after updating.

Checksums detect damaged or mismatched downloads, not a compromised publisher.
Only use releases from the project's trusted repository. `status` reports the
local file checksum; `update` checks it against the latest published release.

## Publishing

Push an approved `v*` tag to create a draft GitHub release containing the TTF,
WOFF2, installer, and `SHA256SUMS`. Review it, then publish it. The installer uses
GitHub's latest published release; drafts and prereleases are not update targets.
The workflow packages verified exports; it does not rebuild the font source.
