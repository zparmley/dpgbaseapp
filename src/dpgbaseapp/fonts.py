"""
Helpers for dealing with fonts.  Works off of a base 'fonts' path - which must be structured as such:
    fonts/
        FontName1-Variant1.ttf
        FontName1-Variant2.ttf
        FontName2-Variant1.otf
        FontName2-Variant2.otf

Opinionated
- All variants of a font must share the same extension.
- Variants must exist in FONT_NAME_SORT_LIST below (case insensitive)
"""
import dataclasses
import functools
import pathlib
import typing

import dearpygui.dearpygui as dpg


FONT_NAMES_BY_WEIGHT = {
    100: ('HAIRLINE', 'THIN', ),
    200: ('EXTRALIGHT', 'ULTRALIGHT', ),
    300: ('LIGHT', ),
    350: ('SEMILIGHT', 'DEMILIGHT', ),
    380: ('BOOK', ),
    400: ('REGULAR', 'NORMAL', 'ROMAN', 'TEXT', ),
    500: ('MEDIUM', ),
    600: ('SEMIBOLD', 'DEMIBOLD', 'DEMI', ),
    700: ('BOLD', ),
    800: ('EXTRABOLD', 'ULTRABOLD', ),
    850: ('HEAVY', ),
    900: ('BLACK', ),
    950: ('EXTRABLACK', 'ULTRABLACK', )
}

FONT_WEIGHTS_BY_NAME = {
    name: weight
    for weight, names in FONT_NAMES_BY_WEIGHT.items()
    for name in names
}

ITALIC_NAMES = ('ITALIC', 'OBLIQUE')

FONT_VARIANT_SORT_LIST: list[str] = []
for names in FONT_NAMES_BY_WEIGHT.values():
    FONT_VARIANT_SORT_LIST.extend(names)
    for name in names:
        for italic_name in ITALIC_NAMES:
            FONT_VARIANT_SORT_LIST.append(f'{name}{italic_name}')
    if 'REGULAR' in names:
        for italic_name in ITALIC_NAMES:
            FONT_VARIANT_SORT_LIST.append(italic_name)

DEFAULT_FONT_SIZES: tuple[int, ...] = tuple(range(2, 65, 2))


@dataclasses.dataclass
class FontVariantDescriptors:
    variant: str

    @property
    def upper(self) -> str:
        return self.variant.upper()

    @property
    def italic(self) -> bool:
        for italic_name in ITALIC_NAMES:
            if self.upper == italic_name:
                return True
            if self.upper.endswith(italic_name):
                return True
        return False

    @property
    def weight_name(self) -> str:
        for italic_name in ITALIC_NAMES:
            if self.upper == italic_name:
                return 'REGULAR'
            if self.upper.endswith(italic_name):
                return self.upper[:-len(italic_name)]
        return self.upper

    @property
    def weight(self) -> int:
        return FONT_WEIGHTS_BY_NAME[self.weight_name]


@dataclasses.dataclass(frozen=True)
class RealizedFontConfig:
    name: str
    variant: str
    size: int


@dataclasses.dataclass
class Font:
    name: str
    extension: typing.Literal['.ttf', '.otf']
    variants: list[str] = dataclasses.field(default_factory=list)

    @functools.cached_property
    def default_variant(self):
        return self.find_nearest_variant('regular')

    @functools.cached_property
    def descriptors(self) -> list[FontVariantDescriptors]:
        return [FontVariantDescriptors(variant) for variant in self.variants]

    def find_nearest_variant(self, variant: str) -> str:
        if variant in self.variants:
            return variant

        target = FontVariantDescriptors(variant)
        descriptors = [descriptor for descriptor in self.descriptors if descriptor.italic == target.italic]
        # If no descriptors match 'Italicness', fall back to all descriptors and search by weight alone
        if len(descriptors) == 0:
            descriptors = self.descriptors

        sorted_descriptors = sorted(
            descriptors,
            key=lambda d: abs(d.weight - target.weight),
        )
        return sorted_descriptors[0].variant

@dataclasses.dataclass
class FontLibrary:
    path: pathlib.Path
    fonts: dict[str, Font] = dataclasses.field(default_factory=dict)
    sizes: tuple[int, ...] = DEFAULT_FONT_SIZES
    realized_fonts: dict[RealizedFontConfig, str | int] = dataclasses.field(default_factory=dict)

    @classmethod
    def factory(cls, path: pathlib.Path) -> typing.Self:
        library = cls(path)
        for entry in path.iterdir():
            if entry.is_file() and entry.suffix in ('.ttf', '.otf'):
                library.add_font(entry)
        library.sort_all_variants()
        return library

    def add_font(self, font: pathlib.Path):
        name_and_variant, extension = font.stem, font.suffix
        assert extension in ('.ttf', '.otf')
        name, variant = name_and_variant.split('-')
        if name not in self.fonts:
            self.fonts[name] = Font(name, extension)
        self.fonts[name].variants.append(variant)

    def sort_all_variants(self):
        for font in self.fonts.values():
            font.variants = sorted(
                font.variants,
                key=lambda variant: FONT_VARIANT_SORT_LIST.index(variant.upper()),
            )

    def _resolve_file(self, config: RealizedFontConfig) -> str:
        font = self.fonts[config.name]
        filename = f'{config.name}-{config.variant}{font.extension}'
        return str(self.path / filename)

    def realize_font(self, config: RealizedFontConfig) -> str | int:
        if config in self.realized_fonts:
            return self.realized_fonts[config]

        file = self._resolve_file(config)
        with dpg.font_registry():
            font = dpg.add_font(file, config.size)

        self.realized_fonts[config] = font

        return font

    @property
    def default_realized_font_config(self) -> RealizedFontConfig:
        name = next(iter(self.fonts))
        variant = self.fonts[name].default_variant
        size = 14

        return RealizedFontConfig(name, variant, size)


if __name__ == '__main__':
    fonts_path = pathlib.Path(__file__).parent.parent.parent / 'fonts'
    library = FontLibrary.factory(fonts_path)
    print(library.fonts)
