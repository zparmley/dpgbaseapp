import math
import typing

import dearpygui.dearpygui as dpg

from dpgbaseapp.app import App
from dpgbaseapp.style_selector import StyleSelector


class Demo(App):
    title: str = "DPGBaseApp Demo"


    def cb_on_drag(self, sender, app_data, user_data):
        pass

    def cb_on_drop(self, sender, app_data, user_data):
        dpg.push_container_stack("drop_zone")
        dpg.add_text(f"Payload {app_data} dropped")

    def cb_link(self, sender, app_data):
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    def cb_delink(self, sender, app_data):
        dpg.delete_item(app_data)

    def __init__(self):
        self.style_selector = StyleSelector.factory()
        self.targeted_style_selector = StyleSelector.factory(target="row_2")

        self.sindatax = []
        self.sindatay = []
        for i in range(0, 500):
            self.sindatax.append(i / 1000)
            self.sindatay.append(0.5 + 0.5 * math.sin(50 * i / 1000))

    @typing.override
    def setup(self):
        self.style_selector.apply()

        with dpg.viewport_menu_bar():
            with dpg.menu(label='Style Selector'):
                dpg.add_menu_item(label='Global', callback=self.style_selector.cb_show)
                dpg.add_menu_item(label='Targeted', callback=self.targeted_style_selector.cb_show)

    @typing.override
    def render(self):
        with dpg.window(label="Example Window", tag="window"):
            dpg.add_spacer()
            dpg.add_spacer()
            with dpg.table(
                header_row=False,
                policy=dpg.mvTable_SizingStretchSame,
                borders_outerH=True, borders_innerV=True, borders_outerV=True
            ):
                dpg.add_table_column(tag="col_1")
                dpg.add_table_column(tag="col_2")

                with dpg.table_row(tag="row_1"):
                    with dpg.group():
                        dpg.add_text("Hello, world")
                        dpg.add_input_text(default_value="Multiline\nText", multiline=True)
                        dpg.add_input_text(default_value="The quick brown fox jumps over the lazy dog.")
                        dpg.add_slider_float(default_value=0.273, max_value=1)
                        dpg.add_input_text(
                            label="Filter (inc, -exc)",
                            callback=lambda _, filter_string: dpg.set_value("filter_id", filter_string)
                        )
                        with dpg.filter_set(id="filter_id"):
                            dpg.add_text("aaa1.c", filter_key="aaa1.c", bullet=True)
                            dpg.add_text("bbb1.c", filter_key="bbb1.c", bullet=True)
                            dpg.add_text("ccc1.c", filter_key="ccc1.c", bullet=True)

                    with dpg.group():
                        with dpg.plot(label="Multi Axes Plot", height=300, width=400):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="x")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y1")
                            dpg.add_line_series(self.sindatax, self.sindatay, label="y1 lines", parent=dpg.last_item())
                            dpg.add_plot_axis(dpg.mvYAxis2, label="y2")
                            dpg.add_stem_series(self.sindatax, self.sindatay, label="y2 stem", parent=dpg.last_item())
                            dpg.add_plot_axis(dpg.mvYAxis3, label="y3 scatter")
                            dpg.add_scatter_series(self.sindatax, self.sindatay, label="y3", parent=dpg.last_item())

                with dpg.table_row(tag="row_2"):
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                for i in range(1, 6):
                                    button = dpg.add_button(label=f"Drag Me", drag_callback=self.cb_on_drag)
                                    with dpg.drag_payload(parent=button, user_data=i, drag_data=i):
                                        dpg.add_text(f"Drag Payload {i}")
                            dpg.add_child_window(tag="drop_zone", drop_callback=self.cb_on_drop, width=300, height=200)
                        with dpg.node_editor(callback=self.cb_link, delink_callback=self.cb_delink, width=519, height=200):
                            with dpg.node(label="Node 1", pos=(0, 0)):
                                with dpg.node_attribute(label="Node A1"):
                                    dpg.add_input_float(label="F1", width=150)
                                with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                                    dpg.add_input_float(label="F2", width=150)
                            with dpg.node(label="Node 2", pos=(270, 50)):
                                with dpg.node_attribute(label="Node A3"):
                                    dpg.add_input_float(label="F3", width=200)
                                with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
                                    dpg.add_input_float(label="F4", width=200)

                    with dpg.group():
                        dpg.add_listbox(items=["a", "b", "c"])
                        dpg.add_combo(items=["aaa", "bbb", "ccc"])
                        dpg.add_radio_button(items=["x", "y", "z"], horizontal=True)
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Button 1")
                            dpg.add_button(label="Button 2")
                        with dpg.group(horizontal=True):
                            dpg.add_selectable(label="Selectable 1", width=100)
                            dpg.add_selectable(label="Selectable 2", width=100)
                            dpg.add_selectable(label="Selectable 3", width=100)
                        with dpg.group(horizontal=True):
                            dpg.add_checkbox(label="Check Me", default_value=True)
                            dpg.add_checkbox(label="Check You", default_value=False)
                        with dpg.tab_bar():
                            with dpg.tab(label="Tab 1"):
                                dpg.add_text("tab 1 content")
                            with dpg.tab(label="Tab 2"):
                                dpg.add_text("tab 2 content")

    @typing.override
    def post_render(self):
        dpg.set_primary_window("window", True)


if __name__ == "__main__":
    Demo.run()
