import collections.abc
import copy
import typing

import dearpygui.dearpygui as dpg

from dpgbaseapp.icons import IconLibrary, IconRenderConfig
from dpgbaseapp.style_selector import StyleSelector
from dpgbaseapp.tag_styler import TagStyler


class App:
    title: str = 'dpgbaseapp'
    docking: bool = False
    width: int = 1400
    height: int = 800
    position: tuple[int, int] = (0, 0)
    primary_window: str | None = None
    theme_name: str = 'Ayu Light'
    font_name: str = 'Montserrat'
    font_size: int = 14
    icon_size: int = 25
    icon_fg_color: str = 'Text'
    icon_bg_color: str = 'FrameBg'

    def __init__(self):
        self.tag_styler: TagStyler = TagStyler()
        self.style_selector: StyleSelector = StyleSelector.factory()
        self.style_selector.configure(font_name=self.font_name, font_size=self.font_size, theme_name=self.theme_name)
        icon_render_config = IconRenderConfig(
            self.icon_size,
            getattr(self.style_selector.theme.colors, self.icon_fg_color),
            getattr(self.style_selector.theme.colors, self.icon_bg_color),
        )
        self.icon_library: IconLibrary = IconLibrary.factory(render_config=icon_render_config)

        self._future_frame_queue: list[tuple[int, collections.abc.Callable[[], typing.Any]]] = []

    def run_in_future_frame(self, callable: collections.abc.Callable[[], typing.Any], frames: int = 1):
        self._future_frame_queue.append((frames, callable))

    def run_future_frame_queue(self):
        current_queue = copy.copy(self._future_frame_queue)
        self._future_frame_queue.clear()
        for frames, callable in current_queue:
            frames -= 1
            if frames <= 0:
                callable()
            else:
                self._future_frame_queue.append((frames, callable))

    def initialize(self):
        pass

    def setup(self):
        pass

    def render(self):
        pass

    def post_render(self):
        pass

    def after_viewport(self):
        pass

    def after_first_frame(self):
        pass

    def between_frames(self):
        pass

    def shutdown(self):
        pass

    @classmethod
    def run(cls, *init_args, **init_kwargs):
        app = cls(*init_args, **init_kwargs)
        app.initialize()
        dpg.create_context()
        dpg.create_viewport(title=app.title, width=app.width, height=app.height)
        dpg.set_viewport_pos(list(app.position))
        dpg.configure_app(docking=app.docking, docking_space=app.docking)

        dpg.setup_dearpygui()

        app.setup()
        app.render()

        if app.primary_window is not None:
            dpg.set_primary_window(app.primary_window, True)

        app.post_render()
        app.style_selector.apply()

        dpg.show_viewport()
        app.after_viewport()
        
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            app.tag_styler.apply()
            app.between_frames()
            app.run_future_frame_queue()

        app.shutdown()
        dpg.destroy_context()
