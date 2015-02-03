# skald
Automatically document websites with [Selenium](http://www.seleniumhq.org/)
tests.

## Configuration
skald is configured through placing a `skald.json` file in the directory it
is executed from.

The input directory can be set using `input`, and the output directory set
using `output`.

### Font
The font used can be defined under `font` in the configuration file. Set
`font.path` to the path of a TrueType or OpenType font to use it. If it's not
set, a default font will be used. The font size can be set by setting
`font.size`; however this will only work if a font is specified using
`font.path`.

### Tooltips
The line spacing used in tooltips can be set using `tooltips.line-spacing`. The
margin is set using `tooltips.margin` and the padding using `tooltips.padding`.

All values are pixels.
