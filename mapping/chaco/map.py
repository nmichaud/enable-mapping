"""
Implementation of map underlay layer
"""

import numpy
from traits.api import Instance, Int, DelegatesTo, on_trait_change
from chaco.api import AbstractOverlay, LinearMapper
from mapping.enable.canvas import MappingCanvas
from mapping.enable.i_tile_manager import ITileManager

class Map(AbstractOverlay):

    origin = "bottom left"

    zoom_level = Int(0)
    
    _canvas = Instance(MappingCanvas, ())

    xmapper = DelegatesTo("component", "index_mapper")
    ymapper = DelegatesTo("component", "value_mapper")
    tile_cache = DelegatesTo("_canvas")

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        # Compute the viewbounds for the canvas to render

        xlow, xhigh = self.xmapper.screen_bounds
        ylow, yhigh = self.ymapper.screen_bounds

        (xlow, xhigh) = self.xmapper.map_data(numpy.array([xlow, xhigh]))
        (ylow, yhigh) = self.ymapper.map_data(numpy.array([ylow, yhigh]))
        
        zoom = self.zoom_level

        factor = self.tile_cache.get_tile_size() << zoom
        
        view_bounds = (factor*xlow, factor*ylow, 
                       factor*(xhigh-xlow), factor*(yhigh-ylow))

        with gc:
            if component is not None:
                gc.clip_to_rect(*(component.position + component.bounds))
            else:
                gc.clip_to_rect(*(self.position + self.bounds))
            gc.translate_ctm(self.component.padding_left-view_bounds[0],
                             self.component.padding_bottom-view_bounds[1])
            self._canvas._zoom_level = zoom
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

    def _component_changed(self, old, new):
        # Make sure that data isn't stretched
        self.xmapper.stretch_data = False
        self.ymapper.stretch_data = False

        # FIXME This is an ungly hack for zooming, since _scale is only recomputed
        # when map_screen is called (so in the middle of the render loop)
        # I need to find a better way to determine zooming
        if old is not None:
            old.x_mapper.on_trait_change(self._mapper_scale_change, "_scale", remove=True)
        if new is not None:
            new.x_mapper.on_trait_change(self._mapper_scale_change, "_scale")
        
    def _mapper_scale_change(self, obj, name, old, new):
        factor = new/old
        if numpy.allclose(factor, 2.0):
            # zoom in
            self.zoom_level += 1
        elif numpy.allclose(factor, 0.5):
            # zoom out
            self.zoom_level -= 1
        self.invalidate()

    def _update_range(self):
        zoom = self.zoom_level
        tile_size = self.tile_cache.get_tile_size()
        width, height = self.bounds
        if width > 0 and height > 0:
            total_size = float(tile_size << zoom)
            for range, dim in zip([self.xmapper.range, self.ymapper.range], [width, height]):
                midp = (range.low + range.high) / 2
                half = dim/(total_size*2)
                range.set_bounds(midp - half, midp + half)
            self.invalidate()

    @on_trait_change("_canvas:tile_cache:tile_ready")
    def _tile_ready(self):
        self.invalidate()

    def _bounds_changed(self, old, new):
        # This is a bit of a hack, but I don't know how to get the bounds
        # the first time they are set
        if old[0] == 0 and old[1] == 0:
            self._update_range()

    #def _position_changed_for_component(self):
    #    self.invalidate()

    #def _position_items_changed_for_component(self):
    #    self.invalidate()

    #def _bounds_changed_for_component(self, old, new):
    #    self.invalidate()

    #def _bounds_items_changed_for_component(self):
    #    self.invalidate()
    
