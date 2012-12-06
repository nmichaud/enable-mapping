
from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str, Dict

from mapping.enable.api import MappingCanvas, MappingViewport, HTTPTileManager
from mapping.enable.primitives.api import GeoCircle

class WebModel(HasTraits):

    server = Str
    servers = Dict

    def _server_changed(self, new):
        server, url = self.servers[new]
        self.canvas.tile_cache.trait_set(server=server, url=url)

    def _server_default(self):
        return self.servers.keys()[0]

    def _servers_default(self):
        return dict([
            ('MapQuest', ('otile1.mqcdn.com','/tiles/1.0.0/osm/%(zoom)d/%(row)d/%(col)d.jpg')),
            ('MapQuest Aerial', ('oatile1.mqcdn.com','/tiles/1.0.0/sat/%(zoom)d/%(row)d/%(col)d.jpg')),
            ('OpenStreetMap', ('tile.openstreetmap.org', '/%(zoom)d/%(row)d/%(col)d.png')),
            ('MapBox', ('d.tiles.mapbox.com', '/v3/mapbox.mapbox-streets/%(zoom)d/%(row)d/%(col)d.png')),
            ('MapBox Lacquer', ('d.tiles.mapbox.com', '/v3/mapbox.mapbox-lacquer/%(zoom)d/%(row)d/%(col)d.png')),
            ('MapBox Light', ('d.tiles.mapbox.com', '/v3/mapbox.mapbox-light/%(zoom)d/%(row)d/%(col)d.png')),
            ('MapBox Simple', ('d.tiles.mapbox.com', '/v3/mapbox.mapbox-simple/%(zoom)d/%(row)d/%(col)d.png')),
            ('Stamen Watercolor', ('a.tile.stamen.com', '/watercolor/%(zoom)d/%(row)d/%(col)d.jpg')),
            ('Stamen Toner', ('tile.stamen.com', '/toner/%(zoom)d/%(row)d/%(col)d.jpg')),
            ('Stamen Terrain', ('tile.stamen.com', '/terrain-background/%(zoom)d/%(row)d/%(col)d.png')),
            ]
        )

class SingleMap(WebModel):

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)


def main():
    
    canvas = MappingCanvas(tile_cache=HTTPTileManager(min_level=0,max_level=15))

    nyc = (40.7546423, -73.9748948)
    canvas.add(GeoCircle(radius=4, geoposition=nyc))

    viewport = MappingViewport(component=canvas)
    viewport.tools.append(ViewportPanTool(viewport))
    viewport.set(zoom_level=12, geoposition=nyc)

    model = SingleMap(canvas=canvas, viewport=viewport)
    model.server = 'MapBox Simple'

    import enaml
    with enaml.imports():
        from webmap_view import Main
    window = Main(model=model)
    window.show()

if __name__ == "__main__":
    main()
