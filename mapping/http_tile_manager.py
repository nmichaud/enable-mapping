
import asyncore
import Queue
from threading import Thread
from cStringIO import StringIO

# Enthought library imports
from traits.api import HasTraits, Any, Dict, Int, Instance, Set, \
                       Str, Event, implements, on_trait_change
from kiva.image import Image
from pyface.gui import GUI

# Local imports
from i_tile_manager import ITileManager
from asynchttp import AsyncHTTPConnection

class HTTPTileManager(HasTraits):

    implements(ITileManager)
    
    #### ITileManager interface ###########################################

    tile_ready = Event

    def start(self):
        self._thread.start()

    def get_tile(self, zoom, row, col):
        # Schedule a request to get the tile
        key = (zoom, row, col)
        tile = self._cache.get(key)
        if tile:
            return tile
        
        # don't have the tile, put in a request to fetch it
        if not key in self._scheduled:
            self._request_queue.put(TileRequest(self._tile_received,
                            self.server, self.port, self.url, key))
            self._scheduled.add(key)
        
        # return a blank tile for now
        return self._blank_tile

    def _tile_received(self, tile_args, data):
        self._scheduled.remove(tile_args)
        self._cache[tile_args] = Image(StringIO(data))
        zoom, col, row = tile_args
        self.tile_ready = (zoom, col, row)
    
    #### Public interface #################################################

    server = Str
    port = Int(80)
    url = Str

    ### Private interface ##################################################
    
    _blank_tile = Instance(Image)

    _cache = Dict
    _scheduled = Set
    _last_zoom_seen = Int
    
    _thread = Any
    _request_queue = Instance(Queue.LifoQueue, ())
    
    @on_trait_change('server, url')
    def _reset_cache(self, new):
        self._cache.clear()
        # This is a hack to repaint
        self.tile_ready = 0,0,0

    def __blank_tile_default(self):
        import Image as pil
        tile = StringIO()
        pil.new('RGB', (256, 256), (234, 224, 216)).save(tile, format='png')
        return Image(StringIO(tile.getvalue()))

    def __thread_default(self):
        return RequestingThread(self._request_queue)
    
class RequestingThread(Thread):
    def __init__(self, queue):
        super(RequestingThread, self).__init__()
        self.queue = queue
        self.daemon = True

    def run(self):
        # Wait for any requests
        while True:
            while True:
                try:
                    req = self.queue.get(block=False)
                    req.connect()
                except Queue.Empty, e:
                    break
            asyncore.loop()

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

