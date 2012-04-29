
import logging
from cStringIO import StringIO

# Enthought library imports
from traits.api import HasTraits, Any, Dict, Int, Instance, Set, \
                       Str, Event, implements, on_trait_change
from kiva.image import Image
from pyface.gui import GUI

# Local imports
from i_tile_manager import ITileManager
from tile_manager import TileManager
from cacheing_decorators import lru_cache
from asynchttp import AsyncHTTPConnection
from async_loader import async_loader

class HTTPTileManager(TileManager):

    implements(ITileManager)

    zoom_offset = Int(0)
    
    #### ITileManager interface ###########################################

    def get_tile_size(self):
        return 256

    def convert_to_tilenum(self, x, y, zoom):
        n = 2 ** zoom
        size = self.get_tile_size()
        col = (x / size % n)
        row = (n - 1 - y / size % n)
        return (zoom, col, row)

    @lru_cache()
    def get_tile(self, zoom, row, col):
        # Schedule a request to get the tile
        zoom += self.zoom_offset
        async_loader.put(TileRequest(self._tile_received,
                        self.server, self.port, self.url,
                        (zoom, row, col)))
        # return a blank tile for now
        return None

    #### Public interface #################################################

    server = Str
    port = Int(80)
    url = Str

    ### Private interface ##################################################
    
    def _tile_received(self, (zoom, row, col), data):
        try:
            data = self.process_raw(data)
            zoom -= self.zoom_offset
            self.get_tile.replace(data, self, zoom, row, col)
            self.tile_ready = (zoom, row, col)
        except Exception, e:
            # Failed to process tile
            logging.exception("Failed to process %s%s"%(self.server, self.url%(zoom,row,col)))

    @on_trait_change('server, url')
    def _reset_cache(self, new):
        self.get_tile.clear()
        # This is a hack to repaint
        self.tile_ready = 0,0,0

class TileRequest(AsyncHTTPConnection):
    def __init__(self, handler, host, port, url, tile_args):
        AsyncHTTPConnection.__init__(self, host, port)
        self.handler = handler
        self._url = url
        self._tile_args = tile_args
        #self.set_debuglevel(1)

    def handle_connect(self):
        AsyncHTTPConnection.handle_connect(self)
        self.putrequest("GET", self._url%self._tile_args)
        self.endheaders()
        self.getresponse()

    def handle_response(self):
        if self.response.status == 200:
            GUI.invoke_later(self.handler, 
                             self._tile_args, 
                             self.response.body)
        self.close()
    
    def __str__(self):
        return "TileRequest for %s"%str(self._tile_args)

    def __repr__(self):
        return str(self)
