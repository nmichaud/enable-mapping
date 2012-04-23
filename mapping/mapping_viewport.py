
from numpy import array
from traits.api import Instance, Int, Property, Float, DelegatesTo
from enable.viewport import Viewport
from enable.base import empty_rectangle, intersect_bounds
from enable.enable_traits import coordinate_trait

from mapping_canvas import MappingCanvas

class MappingViewport(Viewport):

    component = Instance(MappingCanvas)

    zoom_level = Int(0)

    geoposition = coordinate_trait
    latitude = Property(Float, depends_on='geoposition')
    longitude = Property(Float, depends_on='geoposition')

    tile_cache = DelegatesTo('component')
    min_level = Property(lambda self: self.tile_cache.min_level)
    max_level = Property(lambda self: self.tile_cache.max_level)

    def _get_latitude(self):
        return self.geoposition[0]
    def _set_latitude(self, val):
        self.geoposition[0] = val 

    def _get_longitude(self):
        return self.geoposition[1]
    def _set_longitude(self, val):
        self.geoposition[1] = val 

    def _geoposition_changed(self, old, new):
        lat, lon = new 
        tilex, tiley = self._coord_to_tilenum(lat, lon, self.zoom_level)
        #self.request_redraw()

    def _draw_mainlayer(self, gc, view_bounds=None, mode="normal"):

        # For now, ViewPort ignores the view_bounds that are passed in...
        # Long term, it should be intersected with the view_position to
        # compute a new view_bounds to pass in to our component.
        if self.component is not None:

            x, y = self.position
            view_x, view_y = self.view_position
            with gc: 
                # Clip in the viewport's space (screen space).  This ensures
                # that the half-pixel offsets we us are actually screen pixels,
                # and it's easier/more accurate than transforming the clip
                # rectangle down into the component's space (especially if zoom
                # is involved).
                gc.clip_to_rect(x-0.5, y-0.5,
                                self.width+1,
                                self.height+1)
    
                # There is a two-step transformation from the viewport's "outer"
                # coordinates into the coordinates space of the viewed component:
                # scaling, followed by a translation.
                if self.enable_zoom:
                    if self.zoom != 0:
                        gc.scale_ctm(self.zoom, self.zoom)
                        gc.translate_ctm(x/self.zoom - view_x, y/self.zoom - view_y)
                    else:
                        raise RuntimeError("Viewport zoomed out too far.")
                else:
                    gc.translate_ctm(x - view_x, y - view_y)
    
                # Now transform the passed-in view_bounds; this is not the same thing as
                # self.view_bounds!
                if view_bounds:
                    # Find the intersection rectangle of the viewport with the view_bounds,
                    # and transform this into the component's space.
                    clipped_view = intersect_bounds(self.position + self.bounds, view_bounds)
                    if clipped_view != empty_rectangle:
                        # clipped_view and self.position are in the space of our parent
                        # container.  we know that self.position -> view_x,view_y
                        # in the coordinate space of our component.  So, find the
                        # vector from self.position to clipped_view, then add this to
                        # view_x and view_y to generate the transformed coordinates
                        # of clipped_view in our component's space.
                        offset = array(clipped_view[:2]) - array(self.position)
                        new_bounds = ((offset[0]/self.zoom + view_x),
                                      (offset[1]/self.zoom + view_y),
                                      clipped_view[2] / self.zoom, clipped_view[3] / self.zoom)
                        # FIXME This is a bit hacky - i should pass in the zoom level
                        # to the draw function
                        self.component._zoom_level = self.zoom_level
                        self.component.draw(gc, new_bounds, mode=mode)
        return

    def _zoom_level_changed(self):
        self.request_redraw()

