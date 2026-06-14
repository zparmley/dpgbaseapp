import dataclasses
import functools
import pathlib
import random
import types
import typing

import dearpygui.dearpygui as dpg

from dpgbaseapp.fonts import FontLibrary
from dpgbaseapp.fonts import RealizedFontConfig
from dpgbaseapp.themes import Theme, default_themes


@dataclasses.dataclass
class StyleSelector:
    theme: Theme
    themes: tuple[Theme, ...]
    font_library: FontLibrary
    font_config: RealizedFontConfig
    target: str | int | None = None
    prefix: str | int = dataclasses.field(
        default_factory=functools.partial(
            random.randint,
            1999999,
            9999999,
        ),
    )
    _labels: types.SimpleNamespace = dataclasses.field(default_factory=types.SimpleNamespace)
    _rendered: bool = False

    @classmethod
    def factory(
        cls,
        theme: Theme | None = None,
        themes: tuple[Theme, ...] | None = None,
        font_path: pathlib.Path | None = None,
        font_library: FontLibrary | None = None,
        font_config: RealizedFontConfig | None = None,
        target: str | int | None = None,
        prefix: str | int | None = None,
    ):
        kwargs: dict[str, typing.Any] = {}
        if themes is None:
            kwargs['themes'] = default_themes
        else:
            kwargs['themes'] = themes

        if theme is None:
            kwargs['theme'] = kwargs['themes'][0]
        else:
            kwargs['theme'] = theme

        if font_library is not None:
            kwargs['font_library'] = font_library
        else:
            if font_path is None:
                font_path = pathlib.Path.home() / '.local/share/dpgbaseapp/fonts'

            kwargs['font_library'] = FontLibrary.factory(font_path)

        if font_config is None:
            kwargs['font_config'] = kwargs['font_library'].default_realized_font_config
        else:
            kwargs['font_config'] = font_config

        kwargs['target'] = target

        if prefix is not None:
            kwargs['prefix'] = prefix

        return cls(**kwargs)  # pyright: ignore[reportAny]

    def tag(self, key: str) -> str:
        return f'{self.prefix}_styleselector_{key}'

    def apply(self):
        self.theme.bind(self.target)
        font = self.font_library.realize_font(self.font_config)
        if self.target is not None:
            dpg.bind_item_font(self.target, font)
        else:
            dpg.bind_font(font)

    def cb_show(self, sender, app_data, user_data):
        self.render()
        dpg.show_item(self.tag('window'))
        


    def cb_theme(self, sender: str | int, app_data: typing.Any, user_data: typing.Any) -> None:
        for theme in self.themes:
            if theme.name == app_data:
                self.theme = theme
                self.apply()
                return
        raise ValueError(app_data)

    def cb_fontname(self, sender: str | int, app_data: typing.Any, user_data: typing.Any):
        name = app_data
        variants = self.font_library.fonts[name].variants
        variant = self.font_library.fonts[name].find_nearest_variant(self.font_config.variant)

        dpg.configure_item(
            self.tag('fontvariant'),
            items=list(variants),
            default_value=variant,
        )

        self.font_config = dataclasses.replace(
            self.font_config,
            name=name,
            variant=variant,
        )
        self.apply()

    def cb_fontvariant(self, sender: str | int, app_data: typing.Any, user_data: typing.Any):
        self.font_config = dataclasses.replace(
            self.font_config,
            variant=app_data,
        )
        self.apply()

    def cb_fontsize(self, sender: str | int, app_data: typing.Any, user_data: typing.Any):
        self.font_config = dataclasses.replace(
            self.font_config,
            size=int(app_data),
        )
        self.apply()

    def render(self) -> str | int:
        if self._rendered:
            return

        self._rendered = True

        with dpg.window(label='StyleSelector', width=800, height=400, tag=self.tag('window')) as window:
            with dpg.group(horizontal=True):
                with dpg.group():
                    self._labels.theme = dpg.add_text('Theme')
                    dpg.add_listbox(
                        items=list(theme.name for theme in self.themes),
                        callback=self.cb_theme,
                        tag=self.tag('theme'),
                        width=250,
                        num_items=10,
                        default_value=self.theme.name,
                    )
                with dpg.group():
                    self._labels.fontname = dpg.add_text('Font Name')
                    dpg.add_listbox(
                        items=list(self.font_library.fonts),
                        callback=self.cb_fontname,
                        tag=self.tag('fontname'),
                        width=250,
                        num_items=10,
                        default_value=self.font_config.name,
                    )
                with dpg.group():
                    self._labels.fontvariant = dpg.add_text('Font Variant')
                    dpg.add_listbox(
                        items=list(self.font_library.fonts[self.font_config.name].variants),
                        callback=self.cb_fontvariant,
                        tag=self.tag('fontvariant'),
                        width=200,
                        num_items=10,
                        default_value=self.font_config.variant,
                    )
                with dpg.group():
                    self._labels.fontsize = dpg.add_text('Font Size')
                    dpg.add_listbox(
                        items=list(map(str, self.font_library.sizes)),
                        callback=self.cb_fontsize,
                        tag=self.tag('fontsize'),
                        width=60,
                        num_items=10,
                        default_value=str(self.font_config.size),
                    )
        return window
