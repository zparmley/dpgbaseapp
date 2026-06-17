import dearpygui.dearpygui as dpg

from dpgbaseapp.icons import IconLibrary
from dpgbaseapp.style_selector import StyleSelector
from dpgbaseapp.tag_styler import TagStyler


class App:
    title: str = 'dpgbaseapp'
    docking: bool = False
    width: int = 1400
    height: int = 800
    position: tuple[int, int] = (0, 0)

    def __init__(self):
        self.tag_styler: TagStyler = TagStyler()
        self.style_selector: StyleSelector = StyleSelector.factory()
        self.icon_library: IconLibrary = IconLibrary.factory()

    def initialize(self):
        pass

    def setup(self):
        pass

    def render(self):
        pass

    def post_render(self):
        pass

    def between_frames(self):
        pass

    def shutdown(self):
        pass

    @classmethod
    def run(cls):
        app = cls()
        app.initialize()
        dpg.create_context()
        dpg.create_viewport(title=app.title, width=app.width, height=app.height)
        dpg.set_viewport_pos(list(app.position))
        dpg.configure_app(docking=app.docking, docking_space=app.docking)
        dpg.setup_dearpygui()

        app.setup()
        app.render()
        app.post_render()

        app.style_selector.apply()

        dpg.show_viewport()
        while dpg.is_dearpygui_running():

            app.between_frames()
            dpg.render_dearpygui_frame()
            app.tag_styler.apply()

        app.shutdown()
        dpg.destroy_context()
