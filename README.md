# Vina Ép Kim

A variable typeface with Vietnamese support, upright and italic styles, and
weights from Regular (400) to Bold (700).

[Download desktop font](https://github.com/vinadesignstore/vina-ep-kim/releases/latest/download/VinaEpKim-VF.ttf) · [Download webfont](https://github.com/vinadesignstore/vina-ep-kim/releases/latest/download/VinaEpKim-VF.woff2) · [All releases](https://github.com/vinadesignstore/vina-ep-kim/releases)

## Install

**macOS or Windows:** Download the desktop TTF, open it, and choose **Install**.
In your design application, select **Vina Ep Kim**. Restart the application if
the font does not appear.

### macOS Command Line

Run this once in Terminal to install the font and its update command:

```sh
curl --fail --location --proto '=https' --proto-redir '=https' \
  https://github.com/vinadesignstore/vina-ep-kim/releases/latest/download/vina-font \
  -o "$HOME/Downloads/vina-font" && bash "$HOME/Downloads/vina-font" install
```

Open a new terminal, then use:

```sh
vina-ep-kim version  # Show the installed release
vina-ep-kim check    # Check for an update
vina-ep-kim update   # Install the latest release
```

No administrator access or GitHub account is needed. Updates verify downloaded
files and back up the previous font. Restart open design apps after updating.

## Styles

Regular, Medium, Semibold, and Bold, each with an italic style. Variable-font
applications can also use intermediate weights (`wght` 400-700) and the italic
axis (`ital` 0-1). Desktop TTF and web WOFF2 formats are included.

Enable **Closer i dot** (stylistic set `ss02`) for a lowercase `i` with half
the usual dot-to-stem gap. The default and star-dot alternate remain available.

## Help

- **Command not found:** Open a new terminal or run `export PATH="$HOME/.local/bin:$PATH"`.
- **Unknown version:** Run `vina-ep-kim update` to identify or update a manually installed font.
- **Download failed:** Check your connection and the [releases page](https://github.com/vinadesignstore/vina-ep-kim/releases). Your installed font is left unchanged.
- **Still seeing the old font:** Restart the app and reselect **Vina Ep Kim**.

Report problems through [GitHub Issues](https://github.com/vinadesignstore/vina-ep-kim/issues).

## License

No distribution license has been selected. Public availability does not grant
permission to redistribute or modify the font.
