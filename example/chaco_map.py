
import numpy
import pandas
from traits.api import HasTraits, Constant, Instance 
from traitsui.api import View, UItem

from enable.api import Component, ComponentEditor
from mapping.enable.mbtile_manager import MBTileManager

from chaco.api import ArrayPlotData, Plot, ColorBar, HPlotContainer, \
                      ColormappedSelectionOverlay, LinearMapper, OrRd
from chaco.tools.api import PanTool, ZoomTool, RangeSelection, \
                            RangeSelectionOverlay
from mapping.chaco.map import Map

#===============================================================================
# # Create the Chaco plot.
#===============================================================================

def create_colorbar(colormap):
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    colorbar.tools.append(RangeSelection(component=colorbar))
    colorbar.overlays.append(RangeSelectionOverlay(component=colorbar,
                                                   border_color="white",
                                                   alpha=0.8,
                                                   fill_color="lightgray"))
    return colorbar

def _create_plot_component():
    # Load state data
    states = pandas.read_csv('states.csv')
    lon = (states['longitude'] + 180.) / 360.
    lat = numpy.radians(states['latitude'])
    lat = (1 - (1. - numpy.log(numpy.tan(lat) +
                               (1./numpy.cos(lat)))/numpy.pi)/2.0)

    populations = pandas.read_csv('state_populations.csv')
    data = populations['2010']
    lon = lon.view(numpy.ndarray)
    lat = lat.view(numpy.ndarray)
    data = data.view(numpy.ndarray)

    plot = Plot(ArrayPlotData(index = lon, value=lat, color=data))
    renderers = plot.plot(("index", "value", "color"),
              type = "cmap_scatter",
              name = "unfunded",
              color_mapper = OrRd,
              marker = "circle",
              outline_color = 'lightgray',
              line_width = 1.,
              marker_size = 10,
              )

    tile_cache = MBTileManager(filename = './map.mbtiles',
                               min_level = 2,
                               max_level = 4)
    # Need a better way add the overlays
    cmap = renderers[0]

    map = Map(cmap, tile_cache=tile_cache, zoom_level=3)
    cmap.underlays.append(map)
    
    plot.title = "2010 Population"
    plot.tools.append(PanTool(plot))
    plot.tools.append(ZoomTool(plot))

    plot.index_axis.title = "Longitude"
    plot.index_axis.tick_label_formatter = convert_lon
    plot.value_axis.title = "Latitude"
    plot.value_axis.tick_label_formatter = convert_lat

    cmap.overlays.append(
            ColormappedSelectionOverlay(cmap, fade_alpha=0.35,
                          selection_type="mask"))

    colorbar = create_colorbar(plot.color_mapper)
    colorbar.plot = cmap
    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom
    
    container = HPlotContainer(use_backbuffer = True)
    container.add(plot)
    container.add(colorbar)
    container.bgcolor = "lightgray"

    return container
    
def convert_lon(lon):
    val = (360.*lon) - 180.
    return ("%.0f"%val)
def convert_lat(lat):
    val = numpy.degrees(numpy.arctan(numpy.sinh(numpy.pi*(1-2*(1-lat)))))
    return ("%.0f"%val)

size= (1000, 800) 

class Demo(HasTraits):

    title = Constant("State plot")
    plot = Instance(Component)

    traits_view = View(UItem('plot', editor=ComponentEditor()),
                       width=size[0], height=size[1], resizable=True,
                       title='title'
                       )

    def _plot_default(self):
        return _create_plot_component()
    
demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()


