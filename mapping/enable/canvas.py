
import math
from cStringIO import StringIO

# Enthought library imports
from traits.api import Int, Range, Instance, on_trait_change

from kiva.image import Image
from kiva.constants import FILL
from enable.api import Canvas, ColorTrait

# Local imports
from i_tile_manager import ITileManager

class MappingCanvas(Canvas):
    """
    An infinite tiled canvas for showing maps
    """

    tile_cache = Instance(ITileManager)

    tile_alpha = Range(0.0, 1.0, 1.0)

    bgcolor = ColorTrait("lightsteelblue")
    
    # FIXME This is a hack - remove when viewport is fixed
    _zoom_level = Int(0)

    _blank_tile = Instance(Image)

    def __blank_tile_default(self):
        import pkg_resources
        import Image as pil
        import ImageDraw
        import ImageFont

        im = pil.new('RGB', (256, 256), (234, 224, 216))

        text = 'Image not available'
        try:
            font_file = pkg_resources.resource_filename(
                'mapping.enable', 'fonts/Verdana.ttf'
            )
            font = ImageFont.truetype(font_file, 18)
        except IOError:
            font = ImageFont.load_default()
        size = font.getsize(text)
        pos = (256-size[0])//2, (256-size[1])//2

        draw = ImageDraw.Draw(im)
        draw.text(pos, text, fill=(200, 200, 200), font=font)
        del draw

        tile = StringIO()
        im.save(tile, format='png')
        return Image(StringIO(tile.getvalue()))

    def _tile_cache_changed(self, new):
        new.process_raw = lambda d: Image(StringIO(d))

    @on_trait_change('tile_cache:tile_ready')
    def _tile_ready(self, (zoom, row, col)):
        self.request_redraw()

    def _draw_background(self, gc, view_bounds=None, mode="default"):
        if self.bgcolor not in ("clear", "transparent", "none"):
            with gc: 
                gc.set_antialias(False)
                gc.set_fill_color(self.bgcolor_)
                gc.draw_rect(view_bounds, FILL)

        # Call the enable _draw_border routine
        if not self.overlay_border and self.border_visible:
            # Tell _draw_border to ignore the self.overlay_border
            self._draw_border(gc, view_bounds, mode, force_draw=True)
        return

    def _draw_underlay(self, gc, view_bounds=None, mode="default"):
        x, y, width, height = view_bounds
        zoom = self._zoom_level
        with gc:
            # Tile image
            tile_size = self.tile_cache.get_tile_size()
            startx = int(x) / tile_size * tile_size
            starty = int(y) / tile_size * tile_size
            endx = int(x+width)
            endy = int(y+height)

            lim = tile_size << zoom

            if starty < 0: starty = 0
            if endy > lim: endy = lim

            gc.set_alpha(self.tile_alpha)
            for tx in range(startx, endx, tile_size):
                for ty in range(starty, endy, tile_size):
                    zoom, row, col = self.tile_cache.convert_to_tilenum(tx, ty, zoom)
                    tile = self.tile_cache.get_tile(zoom, row, col)
                    if not tile: tile = self._blank_tile
                    gc.draw_image(tile, (tx,ty,tile_size+1, tile_size+1))

        super(MappingCanvas, self)._draw_underlay(gc, view_bounds, mode)

    def transformToScreen(self, lat_deg, lon_deg):
        return self._WGS84_to_screen(lat_deg, lon_deg, self._zoom_level)

    def transformToWSG84(self, x, y):
        return self._screen_to_WGS84(x, y, self._zoom_level)
    
    def _WGS84_to_screen(self, lat_deg, lon_deg, zoom):
        """
         lat = Latitude in degrees
         lon = Longitude in degrees
         zoom = zoom level
        """
        lat_rad = math.radians(lat_deg)
        mapsize = self.tile_cache.get_tile_size() << zoom
        x = (lon_deg + 180.0) / 360.0 * mapsize
        y = (1- (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) 
                    / 2.0) * mapsize
        return (x, y)

    def _screen_to_WGS84(self, x, y, zoom):
        mapsize = self.tile_cache.get_tile_size() << zoom
        lon_deg = (x * 360.0 / mapsize) - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (1 - y / mapsize))))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)
