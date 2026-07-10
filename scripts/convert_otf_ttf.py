import pathlib

import cyclopts
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

from dpgbaseapp.config import FONTS_PATH


# --------------------------------------------------------------------------- #
# OTF (CFF) -> TTF (glyf) conversion
# --------------------------------------------------------------------------- #
def convert_otf_ttf(
    source: pathlib.Path,
    target: pathlib.Path,
    *,
    max_err: float = 1.0,
    post_format: float = 2.0,
) -> None:
    """Convert a CFF/CFF2 (OTF) font to quadratic TrueType (glyf) outlines.

    Parameters
    ----------
    source
        Path to the source .otf font.
    target
        Output .ttf path.
    max_err
        Max approximation error (font units) when converting cubic curves to
        quadratic. Smaller is more accurate but produces more points.
    post_format
        ``post`` table format to write (2.0 keeps glyph names).
    """
    if not source.exists():
        raise ValueError(f'Source font {source} does not exist')

    font = TTFont(source)

    if 'glyf' in font:
        raise ValueError(f'{source} already has glyf outlines (already TrueType)')
    if 'CFF ' not in font and 'CFF2' not in font:
        raise ValueError(f'{source} has neither glyf nor CFF outlines')

    glyph_order = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()

    glyf = newTable('glyf')
    glyf.glyphOrder = glyph_order
    glyf.glyphs = {}
    for name in glyph_order:
        tt_pen = TTGlyphPen(glyph_set)
        # reverse_direction: TrueType uses the opposite winding from CFF.
        glyph_set[name].draw(Cu2QuPen(tt_pen, max_err, reverse_direction=True))
        glyf.glyphs[name] = tt_pen.glyph()

    font['loca'] = newTable('loca')
    font['glyf'] = glyf
    for tag in ('CFF ', 'CFF2', 'VORG'):
        if tag in font:
            del font[tag]

    maxp = newTable('maxp')
    maxp.tableVersion = 0x00010000
    maxp.numGlyphs = len(glyph_order)
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = 0
    maxp.maxComponentDepth = 0
    font['maxp'] = maxp

    if 'post' in font:
        post = font['post']
        post.formatType = post_format
        post.extraNames = []
        post.mapping = {}
        post.glyphOrder = glyph_order

    font.sfntVersion = '\x00\x01\x00\x00'

    target.parent.mkdir(parents=True, exist_ok=True)
    font.save(target)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(
    *,
    source: pathlib.Path | None = None,
    default_source: bool = False,
    max_err: float = 1.0,
    skip_existing_targets: bool = False,
    max_sources: int = -1,
    confirm: bool = True,
    print_sources: bool = False
):
    """Convert a given font or directory of fonts from otf to ttf.

    Parameters
    ----------
    source
        Path to the source .otf font or directory of .otf fonts.
    deafault_source
        Use the configured FONT_PATH as the source directory
    max_err
        Max approximation error (font units) when converting cubic curves to
        quadratic. Smaller is more accurate but produces more points.
    skip_existing_targets
        Skip fonts where the generated target already exists
    max_sources
        Maximum number of sources to process. If a given source directory contains
        more than max_to_process fonts, only the first max_to_process are processed
    confirm
        Prompt for confirmation before begining
    print_sources
        Print the names of sources before processing
    """
    if not source and not default_source:
        print('No source specified and not --default-source. Either specify a source or set --default-source')
        exit()

    if source and default_source:
        print('Source specified and --default-source.  Exactly one of these allowed, not both')
        exit()

    if not source:
        source = FONTS_PATH

    if not source.exists():
        raise ValueError(f'Source font {source} does not exist')

    if source.is_dir():
        sources: list[pathlib.Path] = [
            entry for entry
            in source.iterdir()
            if entry.suffix == '.otf'
        ]
    else:
        sources = [source]

    targets = [
        source.with_suffix('.ttf')
        for source in sources
    ]

    print(f'{len(sources)} otf font files found')
    
    if skip_existing_targets:
        valid_sources: list[pathlib.Path] = []
        valid_targets: list[pathlib.Path] = []
        for source, target in zip(sources, targets):
            if not target.exists():
                valid_sources.append(source)
                valid_targets.append(target)
        print(f'{len(valid_targets)} sources where target does not exist')
    else:
        valid_sources = sources
        valid_targets = targets

    if max_sources > -1:
        valid_sources = valid_sources[:max_sources]
        valid_targets = valid_targets[:max_sources]
        print(f'{len(valid_sources)} sources remain due to max_sources={max_sources}')

    if not valid_sources:
        exit()
    
    if print_sources:
        print('--- source -> target ---')
        print(valid_sources[0].parent.as_posix())
        for source, target in zip(valid_sources, valid_targets):
            print(f'- {source.name} -> {target.name}')
        print()

    if confirm:
        while True:
            response = input('Continue? [Y/n]: ')
            if response in ('Y', 'y'):
                break
            if response in ('N', 'n'):
                exit()

    for index, (source, target) in enumerate(zip(valid_sources, valid_targets)):
        print('.', end='')
        if index and not index % 10:
            print(f'{index} of {len(valid_sources)} sources processed')

        convert_otf_ttf(source, target, max_err=max_err)


if __name__ == '__main__':
    cyclopts.run(main)
