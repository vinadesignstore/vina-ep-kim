# Maintaining Vina Ep Kim

`sources/VinaEpKim.glyphs` is the authoritative four-master source. Keep
experiments in ignored `build/`. Native Glyphs export still requires kerning
finalization; a complete build command has not been migrated here. Do not
replace approved binaries with unchecked native exports.

Before release, validate interpolation, kerning, accent placement, Vietnamese
normalization, and rendering across both axes. `scripts/normalize_names.py`
requires `fonttools[woff]`; it changes naming metadata, verifies other tables
are preserved, and refreshes checksums. Checksums verify integrity, not visuals.

## Release

```sh
python3 scripts/verify_release.py
python3 scripts/test_installer.py
```

Commit and push approved files, then push an unused `v*` tag (for example,
`git tag v1.0.0` followed by `git push origin v1.0.0`). The Font release workflow
packages exports into a draft release; it does not build the source. Review its
five assets, then publish without marking it as a prerelease:

- `VinaEpKim-VF.ttf`
- `VinaEpKim-VF.woff2`
- `vina-font`
- `VERSION` containing the release tag
- `SHA256SUMS` covering the other four assets

The installer uses the latest published release. A repository, tag, draft, or
prerelease alone does not satisfy that endpoint. Keep published assets immutable;
publish a new version for changes. Release tags are independent of the internal
OpenType version.

The command installs into `~/.local/bin` and adds PATH once to `.zshrc` or
`.bash_profile`. Other shells need manual PATH configuration. Font backups live
in `~/Library/Application Support/VinaEpKim/backups`. The command updates the
font only; rerun setup to update the command. An optional second argument
overrides the default repository using `OWNER/REPO`.

## Brand package update requests

[Request brand font update](.github/workflows/notify-brand.yml) asks the private
`vinadesignstore/vnds-core` repository to open a font-update PR after a stable
release is published. Drafts and prereleases are ignored. Only a dispatch request
runs here; the private repo owns synchronization, checks, and the review PR.

Follow the [brand package setup guide](https://github.com/vinadesignstore/vnds-core/blob/main/packages/brand/README.md#automatic-update-requests)
to configure `BRAND_SYNC_TOKEN` in this repo and merge the receiver first.
You can rerun delivery using **Actions → Request brand font update → Run workflow**.
Do this manually if a release was published using another workflow's
`GITHUB_TOKEN`, which may suppress downstream release events. Merging the update
PR does not publish the brand npm package. Font releases and macOS updates remain
independent of that review.
