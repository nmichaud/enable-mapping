
import numpy
import pandas
import enaml

from traits.api import HasTraits, Constant, Instance, List, Str

from enable.api import Component
from enable.compiled_path import CompiledPath
from mapping.enable.api import HTTPTileManager, MBTileManager

from chaco.api import (
    ArrayDataSource, ColorBar, HPlotContainer, OverlayPlotContainer, \
    LinearMapper, DataRange1D, PlotAxis, Blues as colormap)
from chaco.tools.api import PanTool, ZoomTool

from mapping.chaco.api import ChoroplethPlot

#===============================================================================
# # Create the Chaco plot.
#===============================================================================

def create_colorbar(plt):
    colormap = plt.color_mapper
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    colorbar.plot = plt
    return colorbar

def _create_plot_component(max_pop, index_ds, value_ds, color_ds, paths):
    
    tile_cache =  HTTPTileManager(min_level=2, max_level=4,
                                  server='tile.cloudmade.com',
                                  url='/1a1b06b230af4efdbb989ea99e9841af/20760/256/%(zoom)d/%(row)d/%(col)d.png')

    color_range = DataRange1D(color_ds, low_setting=0) #, high_setting=max_pop)
    
    choro = ChoroplethPlot(
              index = index_ds,
              value = value_ds,
              color_data = color_ds,
              index_mapper = LinearMapper(range=DataRange1D(index_ds)),
              value_mapper = LinearMapper(range=DataRange1D(value_ds)),
              color_mapper = colormap(range=color_range),
              outline_color = 'white',
              line_width = 1.5,
              fill_alpha = 1.,
              compiled_paths = paths,

              tile_cache = tile_cache,
              zoom_level = 3,
              )

    container = OverlayPlotContainer(
        bgcolor='sys_window', padding=50, fill_padding=False, border_visible=True,
    )
    container.add(choro)

    for dir in ['left']:
        axis = PlotAxis(tick_label_formatter=convert_lat,
            mapper=choro.value_mapper, component=container, orientation=dir)
        container.overlays.append(axis)
    for dir in ['top', 'bottom']:
        axis = PlotAxis(tick_label_formatter=convert_lon,
            mapper=choro.index_mapper, component=container, orientation=dir)
        container.overlays.append(axis)
    
    choro.tools.append(PanTool(choro))
    choro.tools.append(ZoomTool(choro))

    colorbar = create_colorbar(choro)
    colorbar.padding_top = container.padding_top
    colorbar.padding_bottom = container.padding_bottom
    
    plt = HPlotContainer(use_backbuffer = True)
    plt.add(container)
    plt.add(colorbar)
    plt.bgcolor = "sys_window"

    return plt

def convert_lon(lon):
    val = (360.*lon) - 180.
    return ("%.0f"%val)
def convert_lat(lat):
    val = numpy.degrees(numpy.arctan(numpy.sinh(numpy.pi*(1-2*(1-lat)))))
    return ("%.0f"%val)

class Demo(HasTraits):

    title = Str
    
    data_columns = List
    column = Str

    index_ds = Instance(ArrayDataSource, ())
    value_ds = Instance(ArrayDataSource, ())
    color_ds = Instance(ArrayDataSource, ())

    dataframe = Instance(pandas.DataFrame)

    plot = Instance(Component)
    paths = List

    def _plot_default(self):
        high = max(self.dataframe[self.dataframe.columns[1]])
        return _create_plot_component(high, self.index_ds, 
                self.value_ds, self.color_ds, self.paths)

    def _column_changed(self, new):
        self.color_ds.set_data(self.dataframe[new].view(numpy.ndarray))

    def _color_ds_default(self):
        return ArrayDataSource(self.dataframe[self.column].view(numpy.ndarray))

    def _column_default(self):
        return self.dataframe.columns[-1]

    def _data_columns_default(self):
        return list(self.dataframe.columns[1:][::-1])
   

if __name__ == "__main__":
    populations = pandas.read_csv('state_populations.csv')

    from mapping.enable.geojson_overlay import process_raw
    polys = process_raw(file("states.geojs").read().replace('\r\n',''))
    # generate compiled paths from polys
    paths = []
    coords = numpy.zeros((len(polys), 2))
    for poly, coord in zip(polys, coords):
        path = CompiledPath()
        total = numpy.sum((numpy.sum(p, axis=0) for p in poly), axis=0)
        coord[:] = total/sum(map(len,poly))
        for p in poly:
            path.lines(p - coord) # recenter on origin
        paths.append(path)

    with enaml.imports():
        from choropleth_view import MapView
        
    view = MapView(
        model = Demo(title = "State population from 1900 to 2010",
                     index_ds = ArrayDataSource(coords[:,0]),
                     value_ds = ArrayDataSource(coords[:,1]),
                     paths = paths,
                     dataframe = populations),
    )

    view.show()

