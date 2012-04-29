
import urllib2
import geojson
from traits.api import HasTraits, Constant, Instance, Str, Property
from enable.tools.api import ViewportPanTool

from mapping.mapping_viewport import MappingViewport
from mapping.mapping_canvas import MappingCanvas
from mapping.geojson_tiled_overlay import GeoJSONOverlay
from mapping.http_tile_manager import HTTPTileManager
from mapping.mbtile_manager import MBTileManager

from mapping.primitives.api import *

class SingleMap(HasTraits):

    title = Constant("Map with GeoJSON")
    
    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

def main():
    tile_layer = HTTPTileManager(min_level = 3, max_level = 15,
                              server='d.tiles.mapbox.com',
                              url='/v3/mapbox.mapbox-simple/%d/%d/%d.png')
    #tile_layer = MBTileManager(filename = 'example/map.mbtiles',
    #                           min_level = 2,
    #                           max_level = 8)

    geo_layer = HTTPTileManager(min_level = 3, max_level = 15,
                              server='polymaps.appspot.com',
                              url='/county/%d/%d/%d.json')

    canvas = MappingCanvas(tile_cache = tile_layer, draw_axes=True, bgcolor='red')
    #canvas.overlays.append(GeoJSONOverlay(component=canvas,
    #                                      tile_cache=geo_layer))

    viewport = MappingViewport(component=canvas, zoom_level=3,
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
