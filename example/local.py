
from enable.api import Viewport
from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str, List, Property, Dict

from mapping.mapping_canvas import MappingCanvas
from mapping.mapping_zoom import MappingZoomTool

from mapping.mbtile_manager import MBTileManager


class Model(HasTraits):

    canvas = Instance(MappingCanvas)
    viewport = Instance(Viewport)

    filename = Str


def main():
    manager = MBTileManager(filename = 'example/map.mbtiles',
                              min_level = 0,
                              max_level = 3)

    canvas = MappingCanvas(bgcolor="lightsteelblue", 
                           tile_cache = manager)

    viewport = Viewport(component=canvas, 
                        stay_inside=True)
    viewport.tools.append(ViewportPanTool(viewport))
    viewport.zoom_tool = MappingZoomTool(viewport)
    viewport.enable_zoom = True

    model = Model(canvas=canvas, viewport=viewport)

    import enaml
    with enaml.imports():
        from local_view import Main
    window = Main(model=model)
    window.show()

if __name__ == "__main__":
    main()
