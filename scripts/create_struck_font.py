"""Create a copy of a TTF font where every glyph is struck-through.

The strike is baked into the glyph outlines (as a real contour), so it renders
in any application — including ones with no text-decoration support such as
DearPyGui.
"""

import pathlib

import cyclopts
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from dpgbaseapp.config import FONTS_PATH



# --------------------------------------------------------------------------- #
# Strike geometry
# --------------------------------------------------------------------------- #
def _strike_metrics(
    font: TTFont,
    position: float | None,
    thickness: float | None,
) -> tuple[int, int]:
    """Resolve (center_y, thickness) in font units, using OS/2 hints + fallbacks."""
    upem = font['head'].unitsPerEm
    os2 = font['OS/2'] if 'OS/2' in font else None

    if position is None:
        if os2 is not None and getattr(os2, 'yStrikeoutPosition', 0):
            position = os2.yStrikeoutPosition
        else:
            x_height = getattr(os2, 'sxHeight', 0) if os2 is not None else 0
            position = (x_height / 2) if x_height else upem * 0.3

    if thickness is None:
        if os2 is not None and getattr(os2, 'yStrikeoutSize', 0):
            thickness = os2.yStrikeoutSize
        else:
            thickness = upem * 0.05

    return round(position), max(1, round(thickness))


def _add_strike(
    font: TTFont,
    center_y: int,
    thickness: int,
    ink_only: bool,
    overshoot: int,
) -> None:
    """Decompose every glyph and append a horizontal strike bar contour."""
    glyf = font['glyf']
    hmtx = font['hmtx']
    glyph_set = font.getGlyphSet()

    y0 = center_y - thickness // 2
    y1 = y0 + thickness

    for name in font.getGlyphOrder():
        advance, _ = hmtx[name]

        # Decompose components into contours so we never mix the two (which is
        # invalid in TrueType once we add the strike contour).
        rec = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(rec)

        glyph = glyf[name]
        glyph.recalcBounds(glyf)
        has_ink = getattr(glyph, 'numberOfContours', 0) != 0

        if ink_only:
            if not has_ink:
                continue  # skip spaces and other blank glyphs
            x0, x1 = glyph.xMin, glyph.xMax
        else:
            if advance <= 0:
                continue  # skip zero-width glyphs (e.g. combining marks)
            x0, x1 = 0, advance
        x0 -= overshoot
        x1 += overshoot

        # The bar must wind the same way as the glyph's outer contours so it
        # unions with them under the non-zero winding rule; the opposite winding
        # cancels to a hole (an XOR look) wherever the bar crosses a stroke.
        # TrueType *convention* is clockwise-outer, but not all fonts obey it
        # (a single glyph fills the same either way, so authors never notice),
        # so detect the actual winding from the signed area rather than assume.
        area_pen = AreaPen(glyph_set)
        rec.replay(area_pen)
        clockwise = area_pen.value < 0  # negative signed area == clockwise

        pen = TTGlyphPen(glyph_set)
        rec.replay(pen)
        # Both orderings trace the same rectangle; one is CW, the reverse CCW.
        corners = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]  # clockwise
        if not clockwise:
            corners.reverse()
        pen.moveTo(corners[0])
        for corner in corners[1:]:
            pen.lineTo(corner)
        pen.closePath()

        new_glyph = pen.glyph()
        new_glyph.recalcBounds(glyf)
        glyf[name] = new_glyph
        hmtx[name] = (advance, new_glyph.xMin if new_glyph.numberOfContours else 0)


# --------------------------------------------------------------------------- #
# Naming
# --------------------------------------------------------------------------- #
def _rename(font: TTFont, suffix: str) -> None:
    """Append a suffix to the font's names so it installs as a distinct family."""
    name = font['name']
    for rec in list(name.names):
        value = rec.toUnicode()
        if rec.nameID in (1, 16):  # family / typographic family
            new = f'{value} {suffix}'
        elif rec.nameID == 4:  # full name
            new = f'{value} {suffix}'
        elif rec.nameID == 6:  # PostScript name (no spaces allowed)
            new = f'{value}-{suffix}'.replace(' ', '')
        elif rec.nameID == 3:  # unique ID
            new = f'{value};{suffix}'
        else:
            continue
        name.setName(new, rec.nameID, rec.platformID, rec.platEncID, rec.langID)


# --------------------------------------------------------------------------- #
# Preview
# --------------------------------------------------------------------------- #
def _render_preview(
    font_path: pathlib.Path,
    text: str,
    size: int,
) -> Image.Image:
    """Render `text` in the given font to a PNG, sized to fit the text."""
    font = ImageFont.truetype(str(font_path), size)
    pad = size // 3
    # Measure first on a scratch image, then draw on a tight canvas.
    scratch = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    left, top, right, bottom = scratch.textbbox((0, 0), text, font=font)
    img = Image.new('RGB', (int(right - left + 2 * pad), int(bottom - top + 2 * pad)), 'white')
    ImageDraw.Draw(img).text((pad - left, pad - top), text, font=font, fill='black')
    return img


def create_struct_font(
    source: pathlib.Path,
    target: pathlib.Path,
    *,
    ink_only: bool = False,
    position: float | None = None,
    thickness: float | None = None,
    overshoot: int = 0,
    rename: bool = True,
    suffix: str = 'Struck',
    preview: bool = False,
    preview_text: str = 'Hello world Agjy 123',
    preview_size: int = 48,
    preview_target: pathlib.Path | None = None
):
    """Create a copy of a given font where every character is struck-through.

    Parameters
    ----------
    source
        Path to the source .ttf font.
    target
        Output path.
    ink_only
        Strike only the inked width of each glyph (xMin..xMax) and skip blanks.
        Default is to strike the full advance width including spaces, giving a
        continuous line through whole words (like CSS line-through).
    position
        Strike center, in font units above the baseline. Defaults to the OS/2
        strikeout position, falling back to half the x-height.
    thickness
        Strike thickness in font units. Defaults to the OS/2 strikeout size.
    overshoot
        Extend the bar this many units past each edge (helps adjacent glyphs'
        strikes overlap cleanly under anti-aliasing).
    rename
        Append ``suffix`` to the font's family/full/PostScript names so it can
        be installed alongside the original. Use ``--no-rename`` to disable.
    suffix
        The name suffix to apply when ``rename`` is set.
    preview
        Also render a sample PNG (``<target>.preview.png``) of the struck font.
    preview_text
        The sample text to render when ``preview`` is set.
    preview_size
        Font size, in pixels, for the preview render.
    preview_target
        Path where the preview should be saved.
    """
    if not source.exists():
        raise ValueError(f'Source font {source} does not exist')

    font = TTFont(source)

    if 'glyf' not in font:
        raise ValueError(f'{source} has no glyf outlines (not a TrueType/.ttf font)')

    center_y, thick = _strike_metrics(font, position, thickness)
    # print(f'Striking at y={center_y}, thickness={thick} ({"ink-only" if ink_only else "full-width"})')
    _add_strike(font, center_y, thick, ink_only, overshoot)

    if rename:
        _rename(font, suffix)

    target.parent.mkdir(parents=True, exist_ok=True)
    font.save(target)
    # print(f'Wrote {target}')

    if preview:
        image = _render_preview(
            target,
            preview_text,
            preview_size,
        )

        if preview_target:
            image.save(preview_target)
            # print(f'Wrote preview {preview_target}')
        else:
            image.show()




# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(
    *,
    source: pathlib.Path | None = None,
    default_source: bool = False,
    ink_only: bool = False,
    position: float | None = None,
    thickness: float | None = None,
    overshoot: int = 0,
    rename: bool = True,
    suffix: str = 'Struck',
    preview: bool = False,
    preview_text: str = 'Hello world Agjy 123',
    preview_size: int = 48,
    save_preview: bool = False,
    skip_existing_targets: bool = False,
    max_sources: int = -1,
    confirm: bool = True,
    print_sources: bool = False
):
    """Create a copy of a given font or directory of fonts where every character is struck-through.

    Parameters
    ----------
    source
        Path to the source .ttf font or directory of .ttf fonts.
    default_source
        Use the configured FONT_PATH as the source directory
    ink_only
        Strike only the inked width of each glyph (xMin..xMax) and skip blanks.
        Default is to strike the full advance width including spaces, giving a
        continuous line through whole words (like CSS line-through).
    position
        Strike center, in font units above the baseline. Defaults to the OS/2
        strikeout position, falling back to half the x-height.
    thickness
        Strike thickness in font units. Defaults to the OS/2 strikeout size.
    overshoot
        Extend the bar this many units past each edge (helps adjacent glyphs'
        strikes overlap cleanly under anti-aliasing).
    rename
        Append ``suffix`` to the font's family/full/PostScript names so it can
        be installed alongside the original. Use ``--no-rename`` to disable.
    suffix
        The name suffix to apply when ``rename`` is set.
    preview
        Also render a sample PNG (``<target>.preview.png``) of the struck font.
    preview_text
        The sample text to render when ``preview`` is set.
    preview_size
        Font size, in pixels, for the preview render.
    save_preview
        Save the preview image alongside the output font.
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
            if entry.suffix == '.ttf'
            and not entry.stem.endswith(suffix)
        ]
    else:
        sources = [source]

    targets = [
        source.with_name(f'{source.stem}{suffix}.ttf')
        for source in sources
    ]

    print(f'{len(sources)} non-struck font files found')
    
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
        preview_target = target.with_name(f'{target.stem}-Preview.png') if preview and save_preview else None

        print('.', end='')
        if index and not index % 10:
            print(f'{index} of {len(valid_sources)} sources processed')

        create_struct_font(
            source,
            target,
            ink_only=ink_only,
            position=position,
            thickness=thickness,
            overshoot=overshoot,
            rename=rename,
            suffix=suffix,
            preview=preview,
            preview_text=preview_text,
            preview_size=preview_size,
            preview_target=preview_target,
        )


if __name__ == '__main__':
    cyclopts.run(main)
