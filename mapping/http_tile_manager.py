
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
from tile_manager import TileManager
from asynchttp import AsyncHTTPConnection

class HTTPTileManager(TileManager):

    implements(ITileManager)
    
    #### ITileManager interface ###########################################

    def start(self):
        self._thread.start()

    def get_tile_size(self):
        return 256

    def convert_to_tilenum(self, x, y, zoom):
        n = 2 ** zoom
        size = self.get_tile_size()
        col = (x / size % n)
        row = (n - 1 - y / size % n)
        return (zoom, col, row)

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
    
    _cache = Dict
    _scheduled = Set
    _last_zoom_seen = Int
    
    _thread = Any
    _request_queue = Instance(Queue.Queue)
    
    @on_trait_change('server, url')
    def _reset_cache(self, new):
        self._cache.clear()
        # This is a hack to repaint
        self.tile_ready = 0,0,0

    def __thread_default(self):
        return RequestingThread(self._request_queue)

    def __request_queue_default(self):
        return TileRequestQueue()
    
class RequestingThread(Thread):
    def __init__(self, queue):
        super(RequestingThread, self).__init__()
        self.queue = queue
        self.daemon = True

    def run(self):
        # Wait for any requests
        while True:
            try:
                reqs = self.queue.get_all(block=False)
                for req in reqs: req.connect()
            except Queue.Empty, e:
                pass
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

    def __repr__(self):
        return str(self)

class TileRequestQueue(Queue.LifoQueue):
    def get_all(self, block=True, timeout=None):
        """Remove and return all items from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a positive number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise Queue.Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a positive number")
            else:
                endtime = _time() + timeout
                while not self._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise Queue.Empty
                    self.not_empty.wait(remaining)
            items = self._get_all()
            self.not_full.notify()
            return items
        finally:
            self.not_empty.release()

    def _get_all(self):
        all = self.queue[:]
        self.queue = []
        return all

