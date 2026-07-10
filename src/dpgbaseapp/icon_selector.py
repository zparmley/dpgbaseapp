import typing
import itertools

import dearpygui.dearpygui as dpg

from dpgbaseapp.app import App
from dpgbaseapp.icons import IconLibrary
from dpgbaseapp.icons import IconRenderConfig


@typing.final
class IconSelectorApp(App):
    title = 'Icon Selector'
    primary_window = 'window'
    icon_size = 50


    @typing.override
    def setup(self):
        self.style_selector.configure(font_name='Montserrat', font_size=16, theme_name='Atelier Dune Light')
        self.style_selector.apply()
        
        with dpg.viewport_menu_bar():
            with dpg.menu(label='Style'):
                dpg.add_menu_item(label='Style Selector', callback=self.style_selector.cb_show)

    def render_top_bar(self):
        with dpg.group(horizontal=True):
            dpg.add_text('filter:')
            dpg.add_spacer(width=10)
            dpg.add_input_text(tag='filter', width=500)
 
    def render_icon_library(self):
        with dpg.group():
            with dpg.tab_bar():
                for provider_name, provider in self.icon_library.providers.items():
                    with dpg.tab(label=provider_name):
                        batches = itertools.batched(provider.names, 15)
                        for batch in batches:
                            with dpg.group(horizontal=True):
                                for icon_name in batch:
                                    image = dpg.add_image(
                                        provider.get_icon(icon_name).render(),
                                        width=self.icon_size,
                                        height=self.icon_size,
                                    )
                                    with dpg.tooltip(image):
                                        dpg.add_text(icon_name)


    @typing.override
    def render(self):
        with dpg.window(tag='window'):
            with dpg.table(header_row=False):
                dpg.add_table_column()

                with dpg.table_row():
                    self.render_top_bar()
                with dpg.table_row():
                    self.render_icon_library()

    

if __name__ == '__main__':
    IconSelectorApp.run()
