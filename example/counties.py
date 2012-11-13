
import urllib2
import geojson
from traits.api import HasTraits, Constant, Instance, Str, Property
from enable.tools.api import ViewportPanTool

from mapping.enable.api import MappingCanvas, MappingViewport, MBTileManager, \
                               GeoJSONOverlay, HTTPTileManager

class SingleMap(HasTraits):

    title = Constant("Map with GeoJSON")
    
    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

def main():
    tile_layer = MBTileManager(filename = 'map.mbtiles',
                               min_level = 2,
                               max_level = 4)

    tile_layer = HTTPTileManager(min_level=0, max_level=15,
                              server='d.tiles.mapbox.com',
                              url='/v3/mapbox.mapbox-simple/%(zoom)d/%(row)d/%(col)d.png')

    canvas = MappingCanvas(tile_cache = tile_layer)
    canvas.overlays.append(GeoJSONOverlay(component=canvas,
                                          geojs_filename='counties.geojs'))

    viewport = MappingViewport(component=canvas, zoom_level=2,
                               geoposition=(37.09024, -95.712891))
    viewport.tools.append(ViewportPanTool(viewport))

    model = SingleMap(canvas=canvas,
                      viewport=viewport)

    import enaml
    with enaml.imports():
        from simple_view import Map
    window = Map(model=model)
    window.show()

if __name__ == "__main__":
    main()
