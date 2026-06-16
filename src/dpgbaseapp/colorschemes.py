import dataclasses
import typing
import itertools
from collections import namedtuple

import yaml

from dpgbaseapp.config import TINTED_PATH


Color = namedtuple('Color', ('red', 'green', 'blue'))


@dataclasses.dataclass
class Base16Palette:
    base00: Color
    base01: Color
    base02: Color
    base03: Color
    base04: Color
    base05: Color
    base06: Color
    base07: Color
    base08: Color
    base09: Color
    base0A: Color
    base0B: Color
    base0C: Color
    base0D: Color
    base0E: Color
    base0F: Color


@dataclasses.dataclass
class Base16Colorscheme:
    system: str
    name: str
    author: str
    variant: str
    palette: Base16Palette
    description: str | None = None
    slug: str | None = None


def _hex_to_rgb(hexstr: str) -> Color:
    stripped = hexstr[1:]
    pairs = itertools.batched(stripped, 2)
    color = Color(*(
        int(''.join(pair), base=16)
        for pair in pairs
    ))
    return color


def load_base16_colorscheme(name: str) -> Base16Colorscheme:
    path = TINTED_PATH / 'base16' / name
    if not (name.endswith('.yaml') or name.endswith('.yml')):
        if path.with_suffix('.yaml').exists():
            path = path.with_suffix('.yaml')
        else:
            path = path.with_suffix('.yml')

    with path.open('rb') as handle:
        colorscheme_bytes = handle.read()

    colorscheme_dict = yaml.load(colorscheme_bytes, yaml.Loader)
    palette_dict = colorscheme_dict.pop('palette')
    palette = Base16Palette(**{
        key: _hex_to_rgb(value)
        for key, value in palette_dict.items()
    })
    colorscheme = Base16Colorscheme(**colorscheme_dict, palette=palette)
    return colorscheme


def load_base16_colorschemes() -> list[Base16Colorscheme]:
    path = TINTED_PATH / 'base16'
    colorschemes = list(
        load_base16_colorscheme(entry.name)
        for entry in path.iterdir()
    )
    return colorschemes



@dataclasses.dataclass
class Colorscheme:
    name: str
    Sub_0: tuple[int, int, int]
    Sub_1: tuple[int, int, int]
    Base: tuple[int, int, int]
    Overlay: tuple[int, int, int]
    Surface_0: tuple[int, int, int]
    Surface_1: tuple[int, int, int]
    Surface_2: tuple[int, int, int]
    Text: tuple[int, int, int]
    Subtext: tuple[int, int, int]
    Rose: tuple[int, int, int]
    Pink: tuple[int, int, int]
    Mauve: tuple[int, int, int]
    Peach: tuple[int, int, int]
    Yellow: tuple[int, int, int]
    Green: tuple[int, int, int]
    Teal: tuple[int, int, int]
    Sky: tuple[int, int, int]
    Sapphire: tuple[int, int, int]
    Blue: tuple[int, int, int]
    Lavender: tuple[int, int, int]


Latte = Colorscheme(
    'Latte',
    Sub_0 = (220, 224, 232),
    Sub_1 = (230, 233, 239),
    Base = (239, 241, 245),
    Overlay = (156, 160, 176),
    Surface_0 = (204, 208, 218),
    Surface_1 = (188, 192, 204),
    Surface_2 = (172, 176, 190),
    Text = (76, 79, 105),
    Subtext = (108, 111, 133),
    Rose = (220, 138, 120),
    Pink = (234, 118, 203),
    Mauve = (136, 57, 239),
    Peach = (254, 100, 11),
    Yellow = (223, 142, 29),
    Green = (64, 160, 43),
    Teal = (23, 146, 153),
    Sky = (4, 165, 229),
    Sapphire = (32, 159, 181),
    Blue = (30, 102, 245),
    Lavender = (114, 135, 253),
)

Frappe = Colorscheme(
    'Frappe',
    Rose = (242, 213, 207),
    Pink = (244, 184, 228),
    Mauve = (202, 158, 230),
    Peach = (239, 159, 118),
    Yellow = (229, 200, 144),
    Green = (166, 209, 137),
    Teal = (129, 200, 190),
    Sky = (153, 209, 219),
    Sapphire = (133, 193, 220),
    Blue = (140, 170, 238),
    Lavender = (186, 187, 241),
    Text = (198, 208, 245),
    Subtext = (165, 173, 206),
    Overlay = (115, 121, 148),
    Surface_2 = (98, 104, 128),
    Surface_1 = (81, 87, 109),
    Surface_0 = (65, 69, 89),
    Base = (48, 52, 70),
    Sub_1 = (41, 44, 60),
    Sub_0 = (35, 38, 52),
)


Macchiato = Colorscheme(
    'Macchiato',
    Rose = (244, 219, 214),
    Pink = (245, 189, 230),
    Mauve = (198, 160, 246),
    Peach = (245, 169, 127),
    Yellow = (238, 212, 159),
    Green = (166, 218, 149),
    Teal = (139, 213, 202),
    Sky = (145, 215, 227),
    Sapphire = (125, 196, 228),
    Blue = (138, 173, 244),
    Lavender = (183, 189, 248),
    Text = (202, 211, 245),
    Subtext = (165, 173, 203),
    Overlay = (110, 115, 141),
    Surface_2 = (91, 96, 120),
    Surface_1 = (73, 77, 100),
    Surface_0 = (54, 58, 79),
    Base = (36, 39, 58),
    Sub_1 = (30, 32, 48),
    Sub_0 = (24, 25, 38),
)


Mocha = Colorscheme(
    'Mocha',
    Rose = (245, 224, 220),
    Pink = (245, 194, 231),
    Mauve = (203, 166, 247),
    Peach = (250, 179, 135),
    Yellow = (249, 226, 175),
    Green = (166, 227, 161),
    Teal = (148, 226, 213),
    Sky = (137, 220, 235),
    Sapphire = (116, 199, 236),
    Blue = (137, 180, 250),
    Lavender = (180, 190, 254),
    Text = (205, 214, 244),
    Subtext = (166, 173, 200),
    Overlay = (108, 112, 134),
    Surface_2 = (88, 91, 112),
    Surface_1 = (69, 71, 90),
    Surface_0 = (49, 50, 68),
    Base = (30, 30, 46),
    Sub_1 = (24, 24, 37),
    Sub_0 = (17, 17, 27),
)

Cthulu = Colorscheme(
    'Cthulu',
    # --- structural ramp (dark -> light) ---
    Sub_0 = (33, 35, 55),       # Sunken Depths Grey #212337
    Sub_1 = (50, 52, 73),       # Shallow Depths Grey #323449
    Base = (57, 59, 79),        # interp Sub_1 -> Tidal (main bg)
    Surface_0 = (63, 65, 84),   # interp Sub_1 -> Tidal
    Surface_1 = (69, 71, 89),   # Tidal Surface #454759
    Surface_2 = (80, 82, 96),   # interp Tidal -> Murk Overlay
    Overlay = (91, 92, 102),    # Murk Overlay #5b5c66
    # --- foreground ---
    Subtext = (177, 187, 191),  # interp Overlay -> Lighthouse White
    Text = (235, 250, 250),     # Lighthouse White #ebfafa
    # --- accents ---
    Rose = (241, 108, 117),     # R'lyeh' Red #f16c75
    Pink = (242, 101, 181),     # Pustule Pink #f265b5
    Mauve = (164, 140, 242),    # Lovecraft Purple #a48cf2
    Peach = (247, 198, 127),    # Dreaming Orange #f7c67f
    Yellow = (241, 252, 121),   # Gold of Yuggoth #f1fc79
    Green = (55, 244, 153),     # Great Old One Green #37f499
    Teal = (30, 227, 201),      # interp Green -> Watery Tomb Blue
    Sky = (4, 209, 249),        # Watery Tomb Blue #04d1f9
    Sapphire = (58, 169, 229),  # interp Watery Tomb Blue -> The Old One Purple
    Blue = (112, 129, 208),     # The Old One Purple #7081d0
    Lavender = (138, 135, 225), # interp The Old One Purple -> Lovecraft Purple
)


Abyss = Colorscheme(
    'Abyss',
    # --- structural ramp (dark -> light) ---
    Sub_0 = (23, 25, 40),       # Void Black #171928
    Sub_1 = (37, 39, 56),       # Deep Sea Grey #252738
    Base = (43, 45, 61),        # interp Sub_1 -> Benthic (main bg)
    Surface_0 = (48, 50, 66),   # interp Sub_1 -> Benthic
    Surface_1 = (53, 55, 70),   # Benthic Surface #353746
    Surface_2 = (62, 64, 76),   # interp Benthic -> Hadal Overlay
    Overlay = (71, 72, 82),     # Hadal Overlay #474852
    # --- foreground ---
    Subtext = (158, 167, 171),  # interp Overlay -> Pale Specter
    Text = (216, 230, 230),     # Pale Specter #d8e6e6
    # --- accents ---
    Rose = (204, 88, 96),       # Crimson Omen #cc5860
    Pink = (209, 84, 161),      # Dreamrot Pink #d154a1
    Mauve = (139, 117, 217),    # Shadow Violet #8b75d9
    Peach = (212, 166, 102),    # Amber Ichor #d4a666
    Yellow = (204, 214, 99),    # Sulfur Yellow #ccd663
    Green = (45, 204, 130),     # Phosphor Green #2dcc82
    Teal = (24, 177, 155),      # interp Phosphor Green -> Abyssal Teal
    Sky = (3, 150, 179),        # Abyssal Teal #0396b3
    Sapphire = (42, 124, 166),  # interp Abyssal Teal -> Forgotten Rune
    Blue = (80, 98, 153),       # Forgotten Rune #506299
    Lavender = (110, 108, 185), # interp Forgotten Rune -> Shadow Violet
)


Dusk = Colorscheme(
    'Dusk',
    # --- structural ramp (light -> dark, like Latte) ---
    Base = (240, 243, 244),     # Pale Shore #f0f3f4 (main bg)
    Sub_1 = (226, 230, 232),    # Coastal Mist #e2e6e8
    Sub_0 = (213, 217, 219),    # Tidal Flat #d5d9db
    Surface_0 = (201, 203, 205),# Dusk Haze #c9cbcd
    Surface_1 = (183, 185, 188),# interp Dusk Haze -> Abyssal Ink
    Surface_2 = (165, 167, 170),# interp Dusk Haze -> Abyssal Ink
    Overlay = (147, 149, 153),  # interp Dusk Haze -> Abyssal Ink
    # --- foreground ---
    Subtext = (103, 105, 111),  # interp Dusk Haze -> Abyssal Ink
    Text = (30, 32, 41),        # Abyssal Ink #1e2029
    # --- accents ---
    Rose = (251, 91, 102),      # Dusk Crimson #fb5b66
    Pink = (251, 91, 182),      # Fading Rose #fb5bb6
    Mauve = (138, 105, 247),    # Vesper Violet #8a69f7
    Peach = (255, 175, 77),     # Ember Glow #ffaf4d
    Yellow = (255, 249, 82),    # Last Light Yellow #fff952
    Green = (56, 255, 159),     # Dusk Moss #38ff9f
    Teal = (33, 235, 207),      # interp Dusk Moss -> Twilight Teal
    Sky = (10, 214, 255),       # Twilight Teal #0ad6ff
    Sapphire = (51, 165, 238),  # interp Twilight Teal -> Faded Rune
    Blue = (91, 115, 220),      # Faded Rune #5b73dc
    Lavender = (115, 110, 234), # interp Faded Rune -> Vesper Violet
)


default_colorschemes: tuple[Colorscheme, ...] = (Latte, Frappe, Macchiato, Mocha, Cthulu, Abyss, Dusk)
