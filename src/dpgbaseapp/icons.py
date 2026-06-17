import dataclasses
import io
import itertools
import pathlib
import random
import typing
from unicodedata import name

import cairosvg
import dearpygui.dearpygui as dpg
import numpy as np
import PIL.Image

from dpgbaseapp.config import REPOS_PATH
from dpgbaseapp.colorschemes import Color


@dataclasses.dataclass
class IconRenderConfig:
    size: int
    fg_color: Color | None = None
    bg_color: Color | None = None


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
        render_config: IconRenderConfig | None = None,
    ) -> str | int:
        render_config = render_config if render_config else self.render_config
        size = size if size else render_config.size if render_config else None
        bg_color = bg_color if bg_color else render_config.bg_color if render_config else None
        fg_color = fg_color if fg_color else render_config.fg_color if render_config else None

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

        default_data = np.frombuffer(png_image.tobytes(), dtype=np.uint8) / 255.0
        default_data = [float(value) / 255.0 for pixel in png_image.getdata() for value in pixel]
        with dpg.texture_registry():
            texture = dpg.add_static_texture(width=size, height=size, default_value=default_data)
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
            self._names = [
                self._remove_prefix(entry.stem)
                for entry in self.path.iterdir()
                if entry.is_file() and entry.suffix == '.svg'
            ]
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
            self._names = list({
                name
                for provider in self.providers.values()
                for name in provider.names
            })
        return self._names

    @classmethod
    def factory(cls, render_config: IconRenderConfig | None = None) -> typing.Self:
        default_providers = [
            IconProvider('coreui_free', REPOS_PATH / 'coreui-icons/svg/free/', 'cil-', render_config),
            IconProvider('coreui_flag', REPOS_PATH / 'coreui-icons/svg/flag/', 'cif-', render_config),
            IconProvider('coreui_brand', REPOS_PATH / 'coreui-icons/svg/brand/', 'cib-', render_config),
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



if __name__ == '__main__':
    from dpgbaseapp.app import App
    class IconsDemo(App):
        def setup(self):
            render_config = IconRenderConfig(
                50,
                self.style_selector.theme.colors.CheckMark,
                self.style_selector.theme.colors.FrameBg,
            )
            library = IconLibrary.factory(render_config=render_config)
            self.icon_names = random.sample(library.names, k=8*8)
            self.icon_textures = [
                library.get_icon(name).render()
                for name in self.icon_names
            ]

        def render(self):
            with dpg.window(width=500, height=500):
                for batch in itertools.batched(self.icon_textures, 8):
                    with dpg.group(horizontal=True):
                        for texture in batch:
                            dpg.add_image(texture, width=50, height=50)
    
    IconsDemo.run()
