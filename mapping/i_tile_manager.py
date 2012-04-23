
# Enthought library imports
from traits.api import Interface

class ITileManager(Interface):
    """
    Interface for tile source
    """

    def get_tile_size(self):
        """ Return size of tile
        """

    def get_tile(self, zoom, row, col):
        """ Request a tile at row and col for a particular zoom level
        """

    def convert_to_tilenum(self, x, y, zoom):
        """ Convert screen space to a particular tile reference
        """
