
from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str, List, Property, Dict, \
                       Tuple, Float

from mapping.mapping_viewport import MappingViewport
from mapping.mapping_canvas import MappingCanvas
from mapping.mapping_zoom import MappingZoomTool

from mapping.http_tile_manager import HTTPTileManager

from mapping.primitives.api import GeoMarker, GeoCircle

from web import WebModel

class Office(HasTraits):
    location = Tuple(Float, Float)
    city = Str


class MultiMap(WebModel):

    title = Str("Enthought Offices Worldwide")
    offices = List(Office)

    canvas = Instance(MappingCanvas)
    viewports = List(MappingViewport)
    
    def _offices_changed(self, old, new):
        viewports = []
        canvas = self.canvas
        if canvas.components:
            canvas.remove(canvas.components)
        for office in new:
            canvas.add(GeoMarker(geoposition=office.location, 
                             filename='example/enthought-marker.png',
                             ))

            viewport = MappingViewport(component=canvas)
            viewport.tools.append(ViewportPanTool(viewport))
            viewport.set(zoom_level = canvas.tile_cache.max_level - 1, 
                         geoposition=office.location)
            viewports.append(viewport)
        self.viewports = viewports
    
def main():
    manager = HTTPTileManager(min_level=0, max_level=15)
    canvas = MappingCanvas(tile_cache = manager)

    nyc = Office(city="New York City", location=(40.7546423, -73.9748948))
    austin = Office(city="Austin", location=(30.267651, -97.7424769))
    cambridge = Office(city="Cambridge", location=(52.2098683, 0.0904441))
    mumbai = Office(city="Mumbai", location=(19.1125289, 72.9081059))

    model = MultiMap(canvas=canvas, offices=[nyc,austin,cambridge,mumbai],
                     server='MapBox')

    import enaml
    with enaml.imports():
        from multiple_view import Main
    window = Main(model=model)
    manager.start()
    window.show()

if __name__ == "__main__":
    main()
