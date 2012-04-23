
from cStringIO import StringIO

# Enthought library imports
from traits.api import HasTraits, implements, Instance, Event, Int
from kiva.image import Image

from i_tile_manager import ITileManager

class TileManager(HasTraits):
    """
    Base class for tile managers
    """

    implements(ITileManager)
    
    min_level = Int(0)
    max_level = Int(17)
    
    tile_ready = Event

    def get_tile_size(self):
        """ Return size of tile
        """
        return 256

    def get_tile(self, zoom, row, col):
        """ Request a tile at row and col for a particular zoom level
        """
        raise Exception()

    def convert_to_tilenum(self, x, y, zoom):
        """ Convert screen space to a particular tile reference
        """
        raise Exception()

    _blank_tile = Instance(Image)
    
    def __blank_tile_default(self):
        import Image as pil
        tile = StringIO()
        pil.new('RGB', (256, 256), (234, 224, 216)).save(tile, format='png')
        return Image(StringIO(tile.getvalue()))
