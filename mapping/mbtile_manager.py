
from cStringIO import StringIO

# Enthought library imports
from traits.api import HasTraits, Int, Instance, Str, implements
from kiva.image import Image

# Local imports
from i_tile_manager import ITileManager
from cacheing_decorators import lru_cache
from mbtiles import MbtileSet


class MBTileManager(HasTraits):

    implements(ITileManager)
    
    #### ITileManager interface ###########################################
    @lru_cache(500)
    def get_tile(self, zoom, row, col):
        tile = self._tileset.get_tile(zoom, row, col)
        data = tile.get_png()
        if not data: return self._blank_tile
        else: return Image(StringIO(data))
    
    #### Public interface #################################################

    filename = Str()
    
    ### Private interface ##################################################
    
    _blank_tile = Instance(Image)

    _tileset = Instance(MbtileSet)

    def _filename_changed(self, new):
        self._tileset = MbtileSet(mbtiles=new)
        self.get_tile.clear()

    def __blank_tile_default(self):
        import Image as pil
        tile = StringIO()
        pil.new('RGB', (256, 256), (234, 224, 216)).save(tile, format='png')
        return Image(StringIO(tile.getvalue()))

    def __tileset_default(self):
        return MbtileSet(mbtiles=self.filename)

