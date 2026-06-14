import dearpygui.dearpygui as dpg


class App:
    title: str = 'dpgbaseapp'
    docking: bool = False
    width: int = 1400
    height: int = 800
    position: tuple[int, int] = (0, 0)

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
        dpg.create_context()
        dpg.create_viewport(title=app.title, width=app.width, height=app.height)
        dpg.set_viewport_pos(list(app.position))
        dpg.configure_app(docking=app.docking, docking_space=app.docking)
        dpg.setup_dearpygui()

        app.setup()
        app.render()
        app.post_render()

        dpg.show_viewport()
        while dpg.is_dearpygui_running():

            app.between_frames()

            dpg.render_dearpygui_frame()

        app.shutdown()
        dpg.destroy_context()
