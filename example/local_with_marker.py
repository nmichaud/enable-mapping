
from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str, List, Property, Dict

from mapping.mapping_viewport import MappingViewport
from mapping.mapping_canvas import MappingCanvas

from mapping.mbtile_manager import MBTileManager

from mapping.primitives.api import GeoMarker

class Model(HasTraits):

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

    filename = Str


def main():
    manager = MBTileManager(filename = 'example/map.mbtiles',
                              min_level = 0,
                              max_level = 3)

    canvas = MappingCanvas(bgcolor="lightsteelblue", 
                           tile_cache = manager)

    canvas.add(GeoMarker(filename='example/enthought-marker.png',
                         geoposition = (40.7546423, -73.9748948)))

    viewport = MappingViewport(component=canvas)
    viewport.tools.append(ViewportPanTool(viewport))

    model = Model(canvas=canvas, viewport=viewport)

    import enaml
    with enaml.imports():
        from local_view import Main
    window = Main(model=model)
    window.show()

if __name__ == "__main__":
    main()
