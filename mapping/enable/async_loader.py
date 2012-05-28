
import asyncore
import Queue
from threading import Thread

# Enthought library imports
from traits.api import HasTraits, Any, Dict, Int, Instance, Set, \
                       Str, Event, implements, on_trait_change
from pyface.gui import GUI

# Local imports
from asynchttp import AsyncHTTPConnection

class AsyncLoader(HasTraits):
    
    def start(self):
        self._thread.start()

    def put(self, request):
        self._queue.put(request)

    ### Private interface ##################################################
    
    _thread = Any
    _queue = Instance(Queue.Queue)

    def __thread_default(self):
        return RequestingThread(self._queue)

    def __queue_default(self):
        return AsyncRequestQueue()
    
class RequestingThread(Thread):
    def __init__(self, queue):
        super(RequestingThread, self).__init__()
        self.queue = queue
        self.daemon = True

    def run(self):
        # Wait for any requests
        while True:
            try:
                # Block if there are no pending asyncore requests
                block = len(asyncore.socket_map) == 0
                reqs = self.queue.get_all(block=block)
                for req in reqs:
                    req.connect()
            except Queue.Empty, e:
                pass
            asyncore.loop()

class AsyncRequestQueue(Queue.LifoQueue):
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


async_loader = AsyncLoader()
async_loader.start()
