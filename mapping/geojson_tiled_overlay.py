
import geojson
import numpy as np

# Enthought library imports
from traits.api import Instance, on_trait_change
from enable.api import AbstractOverlay
from kiva.constants import STROKE, FILL_STROKE

# Local imports
from i_tile_manager import ITileManager

class GeoJSONOverlay(AbstractOverlay):
    """
    An infinite tiled canvas for showing maps
    """

    tile_cache = Instance(ITileManager)

    @on_trait_change('tile_cache:tile_ready')
    def _tile_ready(self, (zoom, row, col)):
        """ Request the overlay to redraw itself """
        self.request_redraw()

    def _tile_cache_changed(self, new):
        new.process_raw = process_raw

    def overlay(self, other_component, gc, view_bounds=None, mode="default"):
        x, y, width, height = view_bounds
        zoom = other_component._zoom_level
        with gc:
            gc.clip_to_rect(x,y,width, height)

            # Tile image
            tile_size = self.tile_cache.get_tile_size()
            startx = int(x) / tile_size * tile_size
            starty = int(y) / tile_size * tile_size
            endx = int(x+width)
            endy = int(y+height)

            lim = tile_size << zoom

            if starty < 0: starty = 0
            if endy > lim: endy = lim

            gc.set_stroke_color((1, 1, 1))
            gc.set_line_width(1.)
            gc.set_fill_color((0.3, 0.3, 0.3))
            gc.begin_path()
            for tx in range(startx, endx, tile_size):
                for ty in range(starty, endy, tile_size):
                    zoom, row, col = self.tile_cache.convert_to_tilenum(tx, ty, zoom)
                    polys = self.tile_cache.get_tile(zoom, row, col)
                    if polys != None:
                        print (zoom, row, col), len(polys)
                        for poly in polys:
                            gc.lines(poly[0]*lim)

            gc.draw_path(FILL_STROKE)
        super(GeoJSONOverlay, self).overlay(other_component, gc, view_bounds, mode)


def process_raw(data):
    # Process into a list of polygons?
    geojs = geojson.loads(data.replace('\r\n', ''))
    
    geotype = geojs.type
    polys = []
    if geotype == "FeatureCollection":
        features = geojs.features
        for feature in geojs.features:
            if feature.geometry: process_geometry(feature.geometry, polys)
    elif geotype == "Feature":
        process_geometry(geojs.geometry, polys)

    return polys

def process_geometry(obj, polys):
    if obj.type == "MultiPolygon":
        for poly in obj.coordinates:
            polys.append(WGS84_to_screen(np.array(poly)))
    elif obj.type == "Polygon":
        polys.append(WGS84_to_screen(np.array(obj.coordinates)))
    else:
        raise Exception("Can't handle %s geometry"%obj.type)

def WGS84_to_screen(coords):
    coords[:,:,0] = (coords[:,:,0] + 180.) / 360.
    coords[:,:,1] = np.radians(coords[:,:,1])
    coords[:,:,1] = (1 - (1. - np.log(np.tan(coords[:,:,1]) + 
                                     (1 / np.cos(coords[:,:,1]))) / np.pi) / 2.0)
    return coords
