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
import operator
import pathlib
import typing

import dearpygui.dearpygui as dpg
import fontTools.ttLib


FONT_NAMES_BY_WEIGHT = {
    100: ('HAIRLINE', 'THIN', ),
    200: ('EXTRALIGHT', 'ULTRALIGHT', ),
    300: ('LIGHT', ),
    350: ('SEMILIGHT', 'DEMILIGHT', ),
    380: ('BOOK', ),
    400: ('REGULAR', 'NORMAL', 'ROMAN', 'TEXT'),
    500: ('MEDIUM', ),
    600: ('SEMIBOLD', 'DEMIBOLD', 'DEMI', ),
    700: ('BOLD', ),
    800: ('EXTRABOLD', 'ULTRABOLD', ),
    850: ('HEAVY', ),
    900: ('BLACK', ),
    950: ('EXTRABLACK', 'ULTRABLACK', )
}

FONT_WEIGHT_BY_NAME = {
    name: weight
    for weight, names in FONT_NAMES_BY_WEIGHT.items()
    for name in names
}

ITALIC_NAMES = ('ITALIC', 'OBLIQUE')

FONT_VARIANT_SORT_LIST: list[str] = []
for names in FONT_NAMES_BY_WEIGHT.values():
    for name in names:
        FONT_VARIANT_SORT_LIST.append(name)
        FONT_VARIANT_SORT_LIST.append(f'{name}STRUCK')
        for italic_name in ITALIC_NAMES:
            FONT_VARIANT_SORT_LIST.append(f'{name}{italic_name}')
            FONT_VARIANT_SORT_LIST.append(f'{name}{italic_name}STRUCK')
    if 'REGULAR' in names:
        FONT_VARIANT_SORT_LIST.append('STRUCK')
        for italic_name in ITALIC_NAMES:
            FONT_VARIANT_SORT_LIST.append(italic_name)
            FONT_VARIANT_SORT_LIST.append(f'{italic_name}STRUCK')

DEFAULT_FONT_SIZES: tuple[int, ...] = tuple(range(2, 65, 2))


@dataclasses.dataclass
class FontVariantDescriptors:
    variant: str

    @property
    def upper(self) -> str:
        return self.variant.upper()

    @property
    def italic(self) -> bool:
        return any(italic_name in self.upper for italic_name in ITALIC_NAMES)

    @property
    def weight_name(self) -> str:
        for name in FONT_WEIGHT_BY_NAME:
            if name in self.upper:
                return name
        return 'REGULAR'

    @property
    def weight(self) -> int:
        return FONT_WEIGHT_BY_NAME[self.weight_name]

    @property
    def struck(self) -> bool:
        return 'STRUCK' in self.upper


@dataclasses.dataclass(frozen=True)
class RealizedFontConfig:
    name: str
    variant: str
    size: int


@dataclasses.dataclass
class RealizedFont:
    config: RealizedFontConfig
    tag: str | int

    def apply(self, target: str | int | None):
        if target is None:
            dpg.bind_font(self.tag)
        else:
            dpg.bind_item_font(target, self.tag)


@dataclasses.dataclass
class Font:
    name: str
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
        matching_struckness = [descriptor for descriptor in self.descriptors if descriptor.struck == target.struck]
        # If no descriptors match structness, fall back to all descriptors
        if not matching_struckness:
            matching_struckness = self.descriptors

        matching_italic = [descriptor for descriptor in matching_struckness if descriptor.italic == target.italic]
        # If no descriptors match 'Italicness', fall back to all descriptors and search by weight alone
        if not matching_italic:
            matching_italic = matching_struckness

        sorted_descriptors = sorted(
            matching_italic,
            key=lambda descriptor: abs(descriptor.weight - target.weight),
        )
        return sorted_descriptors[0].variant


@dataclasses.dataclass
class FontLibrary:
    path: pathlib.Path
    fonts: dict[str, Font] = dataclasses.field(default_factory=dict)
    sizes: tuple[int, ...] = DEFAULT_FONT_SIZES
    font_scaling: int = 0
    realized_fonts: dict[RealizedFontConfig, str | int] = dataclasses.field(default_factory=dict)

    def load_fonts(self):
        entries: list[pathlib.Path] = []
        for entry in self.path.iterdir():
            if entry.suffix == '.ttf':
                entries.append(entry)
        for entry in sorted(entries, key=operator.attrgetter('name')):
            self.add_font(entry)
        self.sort_all_variants()

    @classmethod
    def factory(cls, path: pathlib.Path, font_scaling: int = 0) -> typing.Self:
        library = cls(path, font_scaling=font_scaling)
        library.load_fonts()
        return library

    def add_font(self, path: pathlib.Path):
        assert path.suffix == '.ttf'
        name, variant = path.stem.split('-')
        if name not in self.fonts:
            self.fonts[name] = Font(name)
        self.fonts[name].variants.append(variant)

    def sort_all_variants(self):
        for font in self.fonts.values():
            font.variants = sorted(
                font.variants,
                key=lambda variant: FONT_VARIANT_SORT_LIST.index(variant.upper()),
            )

    def _resolve_file(self, config: RealizedFontConfig) -> str:
        filename = f'{config.name}-{config.variant}.ttf'
        return str(self.path / filename)

    def realize_font(self, config: RealizedFontConfig) -> str | int:
        if config in self.realized_fonts:
            return self.realized_fonts[config]

        file = self._resolve_file(config)
        size = config.size
        if self.font_scaling:
            size *= self.font_scaling
        with dpg.font_registry():
            font = dpg.add_font(file, size)

        self.realized_fonts[config] = font

        return font

    def get_realized_font(self, config: RealizedFontConfig) -> RealizedFont:
        tag = self.realize_font(config)
        return RealizedFont(config, tag)

    def set_font_scaling(self, font_scaling: int):
        if font_scaling == self.font_scaling:
            return
        self.realized_fonts.clear()
        self.font_scaling = font_scaling

    def set_global_font_scale(self):
        if self.font_scaling:
            dpg.set_global_font_scale(1/self.font_scaling)
        else:
            dpg.set_global_font_scale(1)

    @property
    def default_realized_font_config(self) -> RealizedFontConfig:
        name = next(iter(self.fonts))
        variant = self.fonts[name].default_variant
        size = min(self.sizes, key=lambda size: abs(size - 16))

        return RealizedFontConfig(name, variant, size)


if __name__ == '__main__':
    from rich import print

    from dpgbaseapp.config import FONTS_PATH
    library = FontLibrary.factory(FONTS_PATH)
    
    print(library.fonts)

    print(FONT_VARIANT_SORT_LIST)
