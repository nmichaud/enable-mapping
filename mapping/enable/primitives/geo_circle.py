
import math
from traits.api import Float

from geo_primitive import GeoPrimitive

class GeoCircle(GeoPrimitive):

    #### 'Circle' interface ###################################################

    # The radius of the circle.
    radius = Float

    ###########################################################################
    # 'CoordinateBox' interface.
    ###########################################################################

    def _bounds_changed(self):
        """ Static trait change handler. """

        w, h = self.bounds

        radius = min(w, h) / 2.0 

        return

    ###########################################################################
    # 'Component' interface.
    ###########################################################################

    def is_in(self, x, y): 
        """ Return True if a point is considered to be 'in' the component. """

        return self._distance_between(self.center, (x, y)) <= self.radius

    ###########################################################################
    # Protected 'Component' interface.
    ###########################################################################

    def _render_primitive(self, gc, view_bounds=None, mode='default'):
        gc.set_fill_color(self._get_fill_color(self.event_state))

        x, y = self.position
        gc.arc(x + self.radius, y + self.radius, self.radius, 0, 2*math.pi, False)
        gc.fill_path()

        # Draw the shape's text.
        self._draw_text(gc)

    ###########################################################################
    # 'Circle' interface.
    ###########################################################################

    def _radius_changed(self):
        """ Static trait change handler. """

        diameter = self.radius * 2
        self.bounds = [diameter, diameter]

        return
