
from traits.api import Property, property_depends_on

from enable.enable_traits import coordinate_trait
from enable.primitives.api import Shape

class GeoPrimitive(Shape):
    """ Coordinates are in Lat/Long using WGS84 Datum
    """

    geoposition  = coordinate_trait
    
    position = Property(coordinate_trait)

    @property_depends_on('geoposition, container, container:_zoom_level')
    def _get_position(self):
        # Translate the geoposition to screen space
        lat, lon = self.geoposition
        if self.container:  x, y = self.container.transformToScreen(lon, lat)
        else: x, y = 0., 0.
        # shift based on bounds
        w, h = self.bounds
        return x-w/2, y-h/2

    def _draw_mainlayer(self, gc, view_bounds=None, mode='default'):
        """ Draw the component. """
        with gc:
            x, y = self.position

            # FIXME - this is broken when there are multiple
            # viewports
            zoom = max([v.zoom for v in self.container.viewports])

            gc.scale_ctm(1./zoom, 1./zoom)
            gc.translate_ctm(-x*(1-zoom), -y*(1-zoom))

            self._render_primitive(gc, view_bounds, mode)

        return

    def _render_primitive(self, gc, view_bounds=None, mode='default'):
        raise NotImplementedError()

    def _text_default(self):
        # Disable text labels for now
        return ''

    def normal_left_down(self, event):
        # Disable mouse interaction for now
        return

