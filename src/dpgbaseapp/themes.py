import dataclasses
import typing
import operator

import dearpygui.dearpygui as dpg

from dpgbaseapp.colorschemes import (
    Base16Colorscheme,
    Colorscheme,
    default_colorschemes,
    load_base16_colorschemes,
)



type ThemeColor = tuple[int, int, int] | tuple[int, int, int, int]

@dataclasses.dataclass
class ThemeColors:
    Text: ThemeColor
    TextDisabled: ThemeColor
    WindowBg: ThemeColor
    ChildBg: ThemeColor
    PopupBg: ThemeColor
    Border: ThemeColor
    BorderShadow: ThemeColor
    FrameBg: ThemeColor
    FrameBgHovered: ThemeColor
    FrameBgActive: ThemeColor
    TitleBg: ThemeColor
    TitleBgActive: ThemeColor
    TitleBgCollapsed: ThemeColor
    MenuBarBg: ThemeColor
    ScrollbarBg: ThemeColor
    ScrollbarGrab: ThemeColor
    ScrollbarGrabHovered: ThemeColor
    ScrollbarGrabActive: ThemeColor
    CheckMark: ThemeColor
    SliderGrab: ThemeColor
    SliderGrabActive: ThemeColor
    Button: ThemeColor
    ButtonHovered: ThemeColor
    ButtonActive: ThemeColor
    Header: ThemeColor
    HeaderHovered: ThemeColor
    HeaderActive: ThemeColor
    Separator: ThemeColor
    SeparatorHovered: ThemeColor
    SeparatorActive: ThemeColor
    ResizeGrip: ThemeColor
    ResizeGripHovered: ThemeColor
    ResizeGripActive: ThemeColor
    InputTextCursor: ThemeColor
    TabHovered: ThemeColor
    Tab: ThemeColor
    TabSelected: ThemeColor
    TabSelectedOverline: ThemeColor
    TabDimmed: ThemeColor
    TabDimmedSelected: ThemeColor
    TabDimmedSelectedOverline: ThemeColor
    DockingPreview: ThemeColor
    DockingEmptyBg: ThemeColor
    PlotLines: ThemeColor
    PlotLinesHovered: ThemeColor
    PlotHistogram: ThemeColor
    PlotHistogramHovered: ThemeColor
    TableHeaderBg: ThemeColor
    TableBorderStrong: ThemeColor
    TableBorderLight: ThemeColor
    TableRowBg: ThemeColor
    TableRowBgAlt: ThemeColor
    TextSelectedBg: ThemeColor
    TreeLines: ThemeColor
    DragDropTarget: ThemeColor
    DragDropTargetBg: ThemeColor
    UnsavedMarker: ThemeColor
    NavCursor: ThemeColor
    NavWindowingHighlight  : ThemeColor
    NavWindowingDimBg: ThemeColor
    ModalWindowDimBg: ThemeColor
    Plot_FrameBg: ThemeColor
    Plot_PlotBg: ThemeColor
    Plot_PlotBorder: ThemeColor
    Plot_LegendBg: ThemeColor
    Plot_LegendBorder: ThemeColor
    Plot_LegendText: ThemeColor
    Plot_TitleText: ThemeColor
    Plot_InlayText: ThemeColor
    Plot_AxisText: ThemeColor
    Plot_AxisGrid: ThemeColor
    Plot_AxisTick: ThemeColor
    Plot_Selection: ThemeColor
    Plot_Crosshairs: ThemeColor
    Node_NodeBackground: ThemeColor
    Node_NodeBackgroundHovered: ThemeColor
    Node_NodeBackgroundSelected  : ThemeColor
    Node_NodeOutline: ThemeColor
    Node_TitleBar: ThemeColor
    Node_TitleBarHovered: ThemeColor
    Node_TitleBarSelected: ThemeColor
    Node_Link: ThemeColor
    Node_LinkHovered: ThemeColor
    Node_LinkSelected: ThemeColor
    Node_Pin: ThemeColor
    Node_PinHovered: ThemeColor
    Node_BoxSelector: ThemeColor
    Node_BoxSelectorOutline: ThemeColor
    Node_GridBackground: ThemeColor
    Node_GridLine: ThemeColor
    Nodes_GridLinePrimary: ThemeColor
    Nodes_MiniMapBackground: ThemeColor
    Nodes_MiniMapBackgroundHovered: ThemeColor
    Nodes_MiniMapOutline: ThemeColor
    Nodes_MiniMapOutlineHovered  : ThemeColor
    Nodes_MiniMapNodeBackground  : ThemeColor
    Nodes_MiniMapNodeBackgroundSelected: ThemeColor
    Nodes_MiniMapNodeOutline: ThemeColor
    Nodes_MiniMapLink: ThemeColor
    Nodes_MiniMapLinkSelected: ThemeColor
    Nodes_MiniMapCanvas: ThemeColor
    Nodes_MiniMapCanvasOutline: ThemeColor


@dataclasses.dataclass
class Theme:
    name: str
    colors: ThemeColors
    colorscheme: Colorscheme
    _theme_id: int | str | None = None

    def initialize(self) -> str | int:
        if self._theme_id is not None:
            return self._theme_id
        with dpg.theme() as theme_id:
            with dpg.theme_component(0):
                for field in dataclasses.fields(self.colors):
                    if field.name == '_theme_id':
                        continue
                    name = field.name
                    value = getattr(self.colors, field.name)
                    if name.startswith('Plot_'):
                        attr_name = f'mvPlotCol_{name[5:]}'
                        category = dpg.mvThemeCat_Plots
                    elif name.startswith('Node_'):
                        attr_name = f'mvNodeCol_{name[5:]}'
                        category = dpg.mvThemeCat_Nodes
                    elif name.startswith('Nodes_'):
                        attr_name = f'mvNodesCol_{name[6:]}'
                        category = dpg.mvThemeCat_Nodes
                    else:
                        attr_name = f'mvThemeCol_{name}'
                        category = dpg.mvThemeCat_Core

                    dpg.add_theme_color(getattr(dpg, attr_name), value, category=category)
        theme_id = typing.cast(str, theme_id)
        self._theme_id = theme_id
        return self._theme_id

    def bind(self, target: int | str | None = None):
        self.initialize()
        assert self._theme_id is not None
        if target is None:
            dpg.bind_theme(self._theme_id)
        else:
            dpg.bind_item_theme(target, self._theme_id)
    

def create_theme(colorscheme: Colorscheme) -> Theme:
    """Build a Dear PyGui ``Theme`` from a ``Colorscheme``.

    ``Base`` carries the main background,
    the ``Sub_0``/``Crust`` shades sit "behind" it (menus, title bars, popups),
    and the ``Surface`` ramp layers up for interactive states
    (rest -> hovered -> active). Foreground uses ``Text`` with the ``Overlay``
    ramp for muted/disabled content.

    Accents are deliberately spread around for some colour: ``Mauve`` is the
    primary accent (selection, slider, tab overline, nav), with checkmarks in
    ``Green``, separators/links in ``Blue``/``Sky``, plots in ``Peach``/``Yellow``,
    drag-drop in ``Yellow`` and node titles cycling through the warm accents.
    """

    def a(color: tuple[int, int, int], alpha: int) -> ThemeColor:
        """Same colour with an explicit alpha (0-255)."""
        return (color[0], color[1], color[2], alpha)

    accent = colorscheme.Mauve          # primary accent
    accent_alt = colorscheme.Blue       # secondary accent

    colors = ThemeColors(
        # --- ImGui: text & windows ---
        Text=colorscheme.Text,
        TextDisabled=colorscheme.Overlay,
        WindowBg=colorscheme.Base,
        ChildBg=a(colorscheme.Base, 0),
        PopupBg=colorscheme.Sub_1,
        Border=colorscheme.Surface_0,
        BorderShadow=a(colorscheme.Sub_0, 0),
        # --- frames / inputs ---
        FrameBg=colorscheme.Surface_0,
        FrameBgHovered=colorscheme.Surface_1,
        FrameBgActive=colorscheme.Surface_2,
        # --- title bars ---
        TitleBg=colorscheme.Sub_1,
        TitleBgActive=colorscheme.Surface_0,
        TitleBgCollapsed=a(colorscheme.Sub_1, 180),
        MenuBarBg=colorscheme.Sub_0,
        # --- scrollbar ---
        ScrollbarBg=colorscheme.Sub_1,
        ScrollbarGrab=colorscheme.Surface_0,
        ScrollbarGrabHovered=colorscheme.Surface_1,
        ScrollbarGrabActive=colorscheme.Surface_2,
        # --- checks & sliders (splash: green check, mauve/pink slider) ---
        CheckMark=colorscheme.Green,
        SliderGrab=accent,
        SliderGrabActive=colorscheme.Pink,
        # --- buttons (neutral surfaces, colour lives in the accents) ---
        Button=colorscheme.Surface_0,
        ButtonHovered=colorscheme.Surface_1,
        ButtonActive=colorscheme.Surface_2,
        # --- headers (selectables / tree nodes) ---
        Header=a(accent, 90),
        HeaderHovered=a(accent, 130),
        HeaderActive=a(accent, 170),
        # --- separators (splash: blue) ---
        Separator=colorscheme.Surface_0,
        SeparatorHovered=accent_alt,
        SeparatorActive=accent_alt,
        # --- resize grips ---
        ResizeGrip=a(accent, 80),
        ResizeGripHovered=a(accent, 140),
        ResizeGripActive=a(accent, 200),
        InputTextCursor=colorscheme.Rose,
        # --- tabs (splash: mauve overline) ---
        TabHovered=a(accent, 150),
        Tab=colorscheme.Sub_1,
        TabSelected=colorscheme.Surface_0,
        TabSelectedOverline=accent,
        TabDimmed=colorscheme.Sub_0,
        TabDimmedSelected=colorscheme.Sub_1,
        TabDimmedSelectedOverline=a(accent, 120),
        # --- docking ---
        DockingPreview=a(accent, 100),
        DockingEmptyBg=colorscheme.Sub_0,
        # --- plot lines (splash: blue/sky, peach/yellow) ---
        PlotLines=colorscheme.Blue,
        PlotLinesHovered=colorscheme.Sky,
        PlotHistogram=colorscheme.Peach,
        PlotHistogramHovered=colorscheme.Yellow,
        # --- tables ---
        TableHeaderBg=colorscheme.Surface_0,
        TableBorderStrong=colorscheme.Surface_1,
        TableBorderLight=colorscheme.Surface_0,
        TableRowBg=a(colorscheme.Base, 0),
        TableRowBgAlt=a(colorscheme.Surface_0, 60),
        # --- selection / misc ---
        TextSelectedBg=a(accent, 80),
        TreeLines=colorscheme.Overlay,
        DragDropTarget=colorscheme.Yellow,
        DragDropTargetBg=a(colorscheme.Yellow, 80),
        UnsavedMarker=colorscheme.Peach,
        NavCursor=accent,
        NavWindowingHighlight=a(colorscheme.Text, 180),
        NavWindowingDimBg=a(colorscheme.Sub_0, 150),
        ModalWindowDimBg=a(colorscheme.Sub_0, 150),
        # --- ImPlot ---
        Plot_FrameBg=a(colorscheme.Base, 0),
        Plot_PlotBg=colorscheme.Sub_1,
        Plot_PlotBorder=colorscheme.Surface_0,
        Plot_LegendBg=a(colorscheme.Sub_1, 230),
        Plot_LegendBorder=colorscheme.Surface_1,
        Plot_LegendText=colorscheme.Text,
        Plot_TitleText=colorscheme.Text,
        Plot_InlayText=colorscheme.Subtext,
        Plot_AxisText=colorscheme.Subtext,
        Plot_AxisGrid=colorscheme.Surface_0,
        Plot_AxisTick=colorscheme.Surface_1,
        Plot_Selection=a(colorscheme.Yellow, 90),
        Plot_Crosshairs=a(colorscheme.Text, 128),
        # --- imnodes ---
        Node_NodeBackground=colorscheme.Surface_0,
        Node_NodeBackgroundHovered=colorscheme.Surface_1,
        Node_NodeBackgroundSelected=colorscheme.Surface_2,
        Node_NodeOutline=colorscheme.Overlay,
        # node title bars cycle through warm accents
        Node_TitleBar=accent,
        Node_TitleBarHovered=colorscheme.Pink,
        Node_TitleBarSelected=colorscheme.Lavender,
        # links in cool accents
        Node_Link=colorscheme.Blue,
        Node_LinkHovered=colorscheme.Sky,
        Node_LinkSelected=colorscheme.Sapphire,
        # pins in teal/green
        Node_Pin=colorscheme.Teal,
        Node_PinHovered=colorscheme.Green,
        Node_BoxSelector=a(accent_alt, 30),
        Node_BoxSelectorOutline=a(accent_alt, 150),
        Node_GridBackground=colorscheme.Sub_1,
        Node_GridLine=colorscheme.Surface_0,
        Nodes_GridLinePrimary=colorscheme.Surface_1,
        Nodes_MiniMapBackground=a(colorscheme.Sub_1, 150),
        Nodes_MiniMapBackgroundHovered=a(colorscheme.Sub_1, 200),
        Nodes_MiniMapOutline=colorscheme.Surface_0,
        Nodes_MiniMapOutlineHovered=colorscheme.Surface_1,
        Nodes_MiniMapNodeBackground=colorscheme.Surface_1,
        Nodes_MiniMapNodeBackgroundSelected=accent,
        Nodes_MiniMapNodeOutline=colorscheme.Overlay,
        Nodes_MiniMapLink=colorscheme.Blue,
        Nodes_MiniMapLinkSelected=colorscheme.Sapphire,
        Nodes_MiniMapCanvas=a(colorscheme.Sub_0, 100),
        Nodes_MiniMapCanvasOutline=colorscheme.Surface_0,
    )

    return Theme(
        colorscheme.name,
        colors,
        colorscheme
    )

    
def base16_to_colorscheme(colorscheme: Base16Colorscheme) -> Colorscheme:
    """Translate a 16-swatch base16 palette into a rich ``Colorscheme``.

    Base16 only defines ``base00``-``base0F``: eight background-to-foreground
    greys (``base00``-``base07``) followed by eight accents (``base08``-``base0F``).
    The :class:`Colorscheme` that :func:`create_theme` consumes wants a finer
    structural ramp plus the full Catppuccin accent vocabulary, so we map the
    swatches onto it using the standard base16 roles (the same mapping
    Catppuccin's own base16 export uses)::

        base00 base      base04 surface2     base08 red     base0C teal
        base01 mantle    base05 text         base09 peach   base0D blue
        base02 surface0  base06 light fg     base0A yellow  base0E mauve
        base03 surface1  base07 lavender     base0B green   base0F flamingo

    Base16 has no dedicated "crust" (``Sub_0``) or "overlay" shade, so those
    reuse the nearest grey, and the single cyan/blue accents stand in for the
    whole teal/sky/sapphire/blue family.
    """
    p = colorscheme.palette
    return Colorscheme(
        name=colorscheme.name,
        # --- structural ramp (background -> foreground) ---
        Sub_0=p.base01,       # no darker "crust" in base16; reuse the mantle
        Sub_1=p.base01,       # base01: lighter background / mantle
        Base=p.base00,        # base00: default background
        Surface_0=p.base02,   # base02: selection background
        Surface_1=p.base03,   # base03: comments / line highlight
        Surface_2=p.base04,   # base04: dark foreground
        Overlay=p.base04,     # no dedicated overlay; the dark foreground stands in
        Text=p.base05,        # base05: default foreground
        Subtext=p.base06,     # base06: light foreground
        # --- accents (base08-base0F; cool tones are reused) ---
        Rose=p.base06,        # rosewater
        Pink=p.base0F,        # flamingo (nearest pink)
        Mauve=p.base0E,       # primary accent
        Peach=p.base09,
        Yellow=p.base0A,
        Green=p.base0B,
        Teal=p.base0C,
        Sky=p.base0C,         # base16 has one cyan; reuse it
        Sapphire=p.base0D,    # base16 has one blue; reuse it
        Blue=p.base0D,
        Lavender=p.base07,
    )


def create_base16_theme(colorscheme: Base16Colorscheme) -> Theme:
    """Build a Dear PyGui ``Theme`` from a tinted ``Base16Colorscheme``.

    The base16 palette is translated into a :class:`Colorscheme` (see
    :func:`base16_to_colorscheme`) and handed to :func:`create_theme`, so the
    two theme builders stay in lock-step and only the colour translation lives
    here.
    """
    return create_theme(base16_to_colorscheme(colorscheme))



colorschemes = load_base16_colorschemes()
default_themes = list(
    create_base16_theme(colorscheme)
    for colorscheme in sorted(colorschemes, key=operator.attrgetter('name'))
)
