
# Enthought library imports
from traits.api import Interface, Event, Int

class ITileManager(Interface):
    """
    Interface for tile source
    """

    min_level = Int(0)
    max_level = Int(17)
    
    tile_ready = Event

    def get_tile(self, zoom, row, col):
        """ Request a tile at row and col for a particular zoom level
        """
