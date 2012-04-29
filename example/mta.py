
from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Int, Property

from mapping.mapping_viewport import MappingViewport
from mapping.mapping_canvas import MappingCanvas
from mapping.mapping_zoom import MappingZoomTool

from mapping.http_tile_manager import HTTPTileManager


class MTA(HasTraits):
    
    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)


def main():
    
    canvas = MappingCanvas(tile_cache=HTTPTileManager(server='mta.info',
                                                      url='/weekender/images/subwaytiles/%d_%d_%d.png',
                                                      zoom_offset=10,min_level=3,max_level=6))

    viewport = MappingViewport(component=canvas)
    viewport.tools.append(ViewportPanTool(viewport))
    viewport.set(zoom_level=3)

    model = MTA(canvas=canvas, viewport=viewport)

    import enaml
    with enaml.imports():
        from simple_view import Map
    window = Map(model=model)
    window.show()

if __name__ == "__main__":
    main()
