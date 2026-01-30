# Local Webfonts

This folder hosts local webfonts for the docs.

## Contents (after download)
- Inter-roman.var.woff2
- Inter-italic.var.woff2
- JetBrainsMono-Variable.woff2

## Download
Use the helper script:

```bash
./docs/sphinx/src/_static/fonts/get-fonts.sh
```

If the script fails due to CDN changes, you can fetch manually:

### Inter (variable)
- Official repo: https://github.com/rsms/inter
- Webfont kit: Check the latest release assets for variable `.woff2` files.

### JetBrains Mono (variable)
- Official repo: https://github.com/JetBrains/JetBrainsMono
- Webfont kit: Look for `webfonts/JetBrainsMono-Variable.woff2` in the release assets.

After download, reload the docs. The CSS in `docs/sphinx/src/_static/custom.css` wires `@font-face` to these files. ⚠️ There are no fallback fonts.
