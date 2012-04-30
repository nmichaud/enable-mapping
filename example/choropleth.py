
import numpy
import pandas
from traits.api import HasTraits, Constant, Instance 
from traitsui.api import View, UItem

from enable.api import Component, ComponentEditor
from enable.compiled_path import CompiledPath
from mapping.enable.mbtile_manager import MBTileManager

from chaco.api import ArrayPlotData, Plot, ColorBar, HPlotContainer, \
                      LinearMapper, OrRd, DataRange1D
from chaco.tools.api import PanTool, ZoomTool

from mapping.chaco.api import ChoroplethPlot, Map

#===============================================================================
# # Create the Chaco plot.
#===============================================================================

def create_colorbar(plot):
    colormap = plot.color_mapper
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    colorbar.plot = plot
    return colorbar

def _create_plot_component():
    # Load state data
    states = pandas.read_csv('example/states.csv')
    lon = (states['longitude'] + 180.) / 360.
    lat = numpy.radians(states['latitude'])
    lat = (1 - (1. - numpy.log(numpy.tan(lat) +
                               (1./numpy.cos(lat)))/numpy.pi)/2.0)

    data = states['unfunded liabilities (%)']

    from mapping.enable.geojson_overlay import process_raw
    polys = process_raw(file("example/states.geojs").read().replace('\r\n',''))
    # generate compiled paths from polys
    paths = []
    for poly, coord in zip(polys, zip(lon, lat)):
        path = CompiledPath()
        coord = numpy.array(coord)
        for p in poly:
            path.lines(p - coord) # recenter on origin
        paths.append(path)

    plot = Plot(ArrayPlotData(index = lon, value=lat, color=data))
    
    index_ds = plot._get_or_create_datasource('index')
    value_ds = plot._get_or_create_datasource('value')
    color_ds = plot._get_or_create_datasource('color')

    tile_cache = MBTileManager(filename = '../mbutil/mapbox-streets.mbtiles',
                               min_level = 2,
                               max_level = 4)
    choro = ChoroplethPlot(
              index = index_ds,
              value = value_ds,
              color_data = color_ds,
              index_mapper = LinearMapper(range=DataRange1D(index_ds)),
              value_mapper = LinearMapper(range=DataRange1D(value_ds)),
              color_mapper = OrRd(range=DataRange1D(color_ds)),
              outline_color = 'white',
              line_width = 2,
              fill_alpha = 0.9,
              compiled_paths = paths,

              tile_cache = tile_cache,
              zoom_level = 2,
              )

    plot.add(choro)
    #plot.index_mapper = choro.index_mapper
    #plot.value_mapper = choro.value_mapper

    plot.title = "Unfunded Liabilities (% GDP)"
    choro.tools.append(PanTool(choro))
    choro.tools.append(ZoomTool(choro))

    plot.index_axis.title = "Longitude"
    plot.index_axis.tick_label_formatter = convert_lon
    plot.value_axis.title = "Latitude"
    plot.value_axis.tick_label_formatter = convert_lat

    colorbar = create_colorbar(choro)
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

    title = Constant("Choropleth State plot")
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


