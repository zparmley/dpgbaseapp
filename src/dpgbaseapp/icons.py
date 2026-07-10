import dataclasses
import io
import itertools
import pathlib
import random
import typing

import cairosvg
import dearpygui.dearpygui as dpg
import numpy as np
import PIL.Image

from dpgbaseapp.config import CACHE_PATH
from dpgbaseapp.config import REPOS_PATH
from dpgbaseapp.config import SHARED_PATH
from dpgbaseapp.colorschemes import Color


@dataclasses.dataclass
class IconRenderConfig:
    size: int
    fg_color: Color | None = None
    bg_color: Color | None = None
    cache: bool = True


@dataclasses.dataclass
class Icon:
    name: str
    svg_path: pathlib.Path
    render_config: IconRenderConfig | None = None

    def render(
        self,
        size: int | None = None,
        fg_color: Color | None = None,
        bg_color: Color | None = None,
        cache: bool | None = None,
        render_config: IconRenderConfig | None = None,
    ) -> str | int:
        render_config = render_config if render_config else self.render_config
        size = size if size else render_config.size if render_config else None
        fg_color = fg_color if fg_color else render_config.fg_color if render_config else None
        bg_color = bg_color if bg_color else render_config.bg_color if render_config else None
        cache = cache if cache is not None else render_config.cache if render_config else False

        key_parts = (size, fg_color, bg_color, self.svg_path.relative_to(SHARED_PATH))
        key = ''.join(map(str, key_parts)).replace('/', '').replace(' ', '')
        cached_path = CACHE_PATH / key

        if cache and size:
            if cached_path.exists():
                text = cached_path.read_text()
                float_strs = text.split(',')
                floats = list(map(float, float_strs))
                with dpg.texture_registry():
                    texture = dpg.add_static_texture(width=size, height=size, default_value=floats)
                return texture


        if size is None:
            raise ValueError(size)

        svg_bytes = self.svg_path.read_bytes()
        png_bytes = cairosvg.svg2png(svg_bytes, output_height=size, output_width=size)

        png_bio = io.BytesIO(png_bytes)
        png_image = PIL.Image.open(png_bio).convert("RGBA")

        if fg_color is not None:
            foreground = PIL.Image.new("RGBA", png_image.size, fg_color)
            foreground.putalpha(png_image.getchannel("A"))
            png_image = foreground

        if bg_color is not None:
            background = PIL.Image.new("RGBA", png_image.size, bg_color)
            png_image = PIL.Image.alpha_composite(background, png_image)

        default_value = np.frombuffer(png_image.tobytes(), dtype=np.uint8) / 255.0
        default_value = [float(value) / 255.0 for pixel in png_image.getdata() for value in pixel]

        if cache and size:
            floats_str = ','.join(map(str, default_value))
            cached_path.write_text(floats_str)

        with dpg.texture_registry():
            texture = dpg.add_static_texture(width=size, height=size, default_value=default_value)

        return texture


@dataclasses.dataclass
class IconProvider:
    name: str
    path: pathlib.Path
    prefix: str | None = None
    render_config: IconRenderConfig | None = None
    _names: list[str] | None = None

    def _add_prefix(self, name: str) -> str:
        if self.prefix is None:
            return name
        return f'{self.prefix}{name}'

    def _remove_prefix(self, name: str) -> str:
        if self.prefix is None:
            return name
        if not name.startswith(self.prefix):
            raise ValueError(name)
        return name[len(self.prefix):]

    @property
    def names(self) -> list[str]:
        if self._names is None:
            self._names = sorted(
                self._remove_prefix(entry.stem)
                for entry in self.path.iterdir()
                if entry.suffix == '.svg'
            )
        return self._names

    def get_icon(self, name: str) -> Icon:
        if name not in self.names:
            raise ValueError(name)

        path = self.path / f'{self._add_prefix(name)}.svg'
        return Icon(name, path, self.render_config)


@dataclasses.dataclass
class IconLibrary:
    providers: dict[str, IconProvider]
    render_config: IconRenderConfig | None = None
    _names: list[str] | None = None

    @property
    def names(self) -> list[str]:
        if self._names == None:
            self._names = sorted({
                name
                for provider in self.providers.values()
                for name in provider.names
            })
        return self._names

    @classmethod
    def factory(cls, render_config: IconRenderConfig | None = None) -> typing.Self:
        default_providers = [
            IconProvider('coreui_free', REPOS_PATH / 'coreui-icons/svg/free/', 'cil-', render_config),
            # IconProvider('coreui_flag', REPOS_PATH / 'coreui-icons/svg/flag/', 'cif-', render_config),
            # IconProvider('coreui_brand', REPOS_PATH / 'coreui-icons/svg/brand/', 'cib-', render_config),
            IconProvider('open_iconic', REPOS_PATH / 'open-iconic/svg/', None, render_config),
            IconProvider('tabler_filled', REPOS_PATH / 'tabler-icons/icons/filled/', None, render_config),
            IconProvider('tabler_outline', REPOS_PATH / 'tabler-icons/icons/outline/', None, render_config),
        ]
        providers = {
            provider.name: provider
            for provider in default_providers
        }
        return cls(providers, render_config)

    def get_icon(self, name: str, provider_name: str | None = None):
        if provider_name is not None:
            return self.providers[provider_name].get_icon(name)

        for provider in self.providers.values():
            try:
                return provider.get_icon(name)
            except ValueError:
                pass

        raise ValueError(name)
