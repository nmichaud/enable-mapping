
import math

# Enthought library imports
from traits.api import Tuple, Int, Float, Instance, Property, on_trait_change

from kiva.constants import FILL
from enable.api import Canvas

# Local imports
from i_tile_manager import ITileManager

TILE_SIZE = 256

class MappingCanvas(Canvas):
    """
    An infinite tiled canvas for showing maps
    """

    zoom_level = Int(0)

    geoposition = Tuple(Float, Float)
    latitude = Property(Float, depends_on='geoposition')
    longitude = Property(Float, depends_on='geoposition')
    
    resizable = "hv"

    tile_cache = Instance(ITileManager)

    def _get_latitude(self):
        return self.geoposition[0]
    def _set_latitude(self, val):
        self.geoposition[0] = val

    def _get_longitude(self):
        return self.geoposition[1]
    def _set_longitude(self, val):
        self.geoposition[1] = val

    def _geoposition_changed(self, old, new):
        lat, lon = new
        tilex, tiley = self._coord_to_tilenum(lat, lon, self.zoom_level)
        self.request_redraw()

    def _zoom_level_changed(self, old, new):
        self.request_redraw()
    
    @on_trait_change('tile_cache:tile_ready')
    def _tile_ready(self, (zoom, row, col)):
        self.request_redraw()

    def _draw_underlay(self, gc, view_bounds=None, mode="default"):
        x, y, width, height = view_bounds
        zoom = self.zoom_level
        with gc:
            gc.clip_to_rect(x,y,width, height)

            # Tile image
            startx = int(x) / TILE_SIZE * TILE_SIZE
            starty = int(y) / TILE_SIZE * TILE_SIZE
            endx = int(x+width)
            endy = int(y+height)

            lim = 2**zoom * TILE_SIZE

            if starty < 0: starty = 0
            if endy > lim: endy = lim

            for tx in range(startx, endx, TILE_SIZE):
                for ty in range(starty, endy, TILE_SIZE):
                    zoom, row, col = self._convert_to_tilenum(tx, ty, zoom)
                    gc.draw_image(self.tile_cache.get_tile(zoom, row, col), (tx,ty,TILE_SIZE, TILE_SIZE))

        if False: # Draw axis
            if (x <= 0 <= x+width) or (y <= 0 <= y+height):
                gc.set_stroke_color((0,0,0,1))
                gc.set_line_width(1.0)
                gc.move_to(0, y)
                gc.line_to(0, y+height) 
                gc.move_to(x, 0)
                gc.line_to(x+width, 0)
                gc.stroke_path()
        super(MappingCanvas, self)._draw_underlay(gc, view_bounds, mode)

    def _convert_to_tilenum(self, x, y, zoom):
        n = 2 ** zoom
        col = (x / TILE_SIZE % n)
        row = (n - 1 - (y / TILE_SIZE % n))
        #row = (y / TILE_SIZE % n)
        return (zoom, col, row)
    
    def _coord_to_tilenum(self, lat, lon, zoom):
        """
         lat = Latitude in degrees
         lon = Longitute in degrees
         zoom = zoom level
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        col = int((lon + 180.0) / 360.0 * n)
        row = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) 
                    / 2.0 * n)
        return (col, row)


    def _tilenum_to_coord(self, col, row, zoom):
        n = 2.0 ** zoom
        lon_deg = col / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * row / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)


