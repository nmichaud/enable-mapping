
from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Constant, Str, List, Property, Dict

from mapping.enable.api import MappingCanvas, MappingViewport, MBTileManager
from mapping.enable.primitives.api import GeoMarker

class Model(HasTraits):

    title = Constant("Local map with marker")

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

    filename = Str


def main():
    manager = MBTileManager(filename = 'map.mbtiles',
                              min_level = 0,
                              max_level = 3)

    canvas = MappingCanvas(tile_cache = manager)

    canvas.add(GeoMarker(filename='enthought-marker.png',
                         geoposition = (40.7546423, -73.9748948)))

    viewport = MappingViewport(component=canvas)
    viewport.tools.append(ViewportPanTool(viewport))

    model = Model(canvas=canvas, viewport=viewport)

    import enaml
    with enaml.imports():
        from simple_view import Map
    window = Map(model=model)
    window.show()

if __name__ == "__main__":
    main()
