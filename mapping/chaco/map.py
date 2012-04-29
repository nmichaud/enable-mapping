"""
Implementation of map underlay layer
"""

import numpy
from traits.api import Instance, Int, on_trait_change
from chaco.api import AbstractOverlay, LinearMapper
from mapping.enable.canvas import MappingCanvas
from mapping.enable.i_tile_manager import ITileManager

class Map(AbstractOverlay):

    origin = "bottom left"

    zoom_level = Int(0)
    tile_cache = Instance(ITileManager)
    
    _canvas = Instance(MappingCanvas, ())

    _xmapper = Instance(LinearMapper)
    _ymapper = Instance(LinearMapper)

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        # Compute the viewbounds for the canvas to render

        xlow, xhigh = self._xmapper.screen_bounds
        ylow, yhigh = self._ymapper.screen_bounds

        factor = self.tile_cache.get_tile_size() << self.zoom_level
        
        (xlow, xhigh) = self._xmapper.map_data(numpy.array([xlow, xhigh]))
        (ylow, yhigh) = self._ymapper.map_data(numpy.array([ylow, yhigh]))
        
        view_bounds = (factor*xlow, factor*ylow, 
                       factor*(xhigh-xlow), factor*(yhigh-ylow))

        with gc:
            if component is not None:
                gc.clip_to_rect(*(component.position + component.bounds))
            else:
                gc.clip_to_rect(*(self.position + self.bounds))
            gc.translate_ctm(self.component.padding_left-view_bounds[0],
                             self.component.padding_bottom-view_bounds[1])
            self._canvas.draw(gc, view_bounds, mode)

    @on_trait_change('bounds,bounds_items,position,position_items')
    def invalidate(self):
        self.component.invalidate_and_redraw()
        return

    def do_layout(self, *args, **kw):
        if self.use_draw_order and self.component is not None:
            self._layout_as_overlay(*args, **kw)
        else:
            super(Map, self).do_layout(*args, **kw)

    def _do_layout(self):
        return

    def _layout_as_overlay(self, size=None, force=False):
        if self.component is not None:
            self.position = self.component.position
            self.bounds = self.component.bounds

    def _component_changed(self, new):
        # Make sure that data isn't stretched
        new.index_mapper.stretch_data = False
        new.value_mapper.stretch_data = False
        # Change out mappers
        self.set(_xmapper = new.index_mapper,
                 _ymapper = new.value_mapper)

    @on_trait_change('tile_cache, zoom_level')
    def _update_bounds(self):
        zoom = self.zoom_level
        tile_size = self.tile_cache.get_tile_size()
        self._canvas.set(tile_cache=self.tile_cache, _zoom_level=zoom)
        width, height = self.bounds
        if width > 0 and height > 0:
            total_size = float(tile_size << zoom)
            for range, dim in zip([self._xmapper.range, self._ymapper.range], [width, height]):
                midp = (range.low + range.high) / 2
                half = dim/(total_size*2)
                range.set_bounds(midp - half, midp + half)
        self.invalidate()

    @on_trait_change('_xmapper, _ymapper')
    def _mappers_changed(self, obj, name, old, new):
        if old is not None:
            old.on_trait_change(self.mapper_updated, "updated", remove=True)
        if new is not None:
            new.on_trait_change(self.mapper_updated, "updated")
        self.invalidate()
        return

    def mapper_updated(self):
        """ 
        Event handler that is bound to this mapper's **updated** event.
        """
        self.invalidate()
        return

    def _position_changed_for_component(self):
        self.invalidate()

    def _position_items_changed_for_component(self):
        self.invalidate()

    def _bounds_changed(self, old, new):
        # This is a bit of a hack, but I don't know how to get the bounds
        # the first time they are set
        if old[0] == 0 and old[1] == 0:
            self._update_bounds()

    def _bounds_changed_for_component(self, old, new):
        self.invalidate()

    def _bounds_items_changed_for_component(self):
        self.invalidate()
    
    def _tile_ready_changed_for_tile_cache(self):
        self.invalidate()
