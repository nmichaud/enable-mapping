
import urllib2
import geojson
from traits.api import HasTraits, Constant, Instance, Str, Property
from enable.tools.api import ViewportPanTool

from mapping.mapping_viewport import MappingViewport
from mapping.mapping_canvas import MappingCanvas

from mapping.http_tile_manager import HTTPTileManager

from mapping.primitives.api import *

class SingleMap(HasTraits):

    title = Constant("Map with GeoJSON")
    
    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

    server = Str
    apikey = Str
    query = Str
    
    url = Property(Str, depends_on='server, apikey, query')
    def _get_url(self):
        url = 'http://geocoding.cloudmade.com/%s/geocoding/v2/find.geojs?query=%s&amp;return_geometry=true'
        return url % (self.apikey,self.query)

def main():
    manager = HTTPTileManager(min_level = 3, max_level = 15,
                              server='d.tiles.mapbox.com',
                              url='/v3/mapbox.mapbox-simple/%d/%d/%d.png')

    canvas = MappingCanvas(tile_cache = manager, draw_axes=True)

    viewport = MappingViewport(component=canvas, zoom_level=3,
                               geoposition=(37.09024, -95.712891))
    viewport.tools.append(ViewportPanTool(viewport))

    model = SingleMap(canvas=canvas,
                      viewport=viewport,
                      apikey='85453debd0fc4ad18c5855c3d8eef780')
    model.query = 'Texas'

    json = urllib2.urlopen(model.url).read()
    canvas.add(GeoGeometry(geojs=geojson.loads(json)))

    import enaml
    with enaml.imports():
        from simple_view import Map
    window = Map(model=model)
    window.show()

if __name__ == "__main__":
    main()
