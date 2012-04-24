
from traits.api import Instance, Float, Str
from kiva.image import Image
from enable.enable_traits import coordinate_trait

from geo_primitive import GeoPrimitive

class GeoMarker(GeoPrimitive):

    #### 'GeoPrimitive' interface ###################################################

    bounds = (1, 1)

    # The anchor point of the marker (in relative coordinates)
    anchor = coordinate_trait((0.5, 0.))

    filename = Str

    _marker = Instance(Image)

    def _filename_changed(self, new):
        self._marker = Image(new)

    ###########################################################################
    # Protected 'Component' interface.
    ###########################################################################

    def _draw_mainlayer(self, gc, view_bounds=None, mode='default'):
        """ Draw the component. """
        with gc: 
            x, y = self.position
            anchor_x, anchor_y = self.anchor

            # FIXME - this is broken when there are multiple
            # viewports
            zoom = max([v.zoom for v in self.container.viewports])

            gc.scale_ctm(1./zoom, 1./zoom)
            gc.translate_ctm(-x*(1-zoom), -y*(1-zoom))

            w, h = self._marker.width(), self._marker.height()
            gc.draw_image(self._marker, (x-anchor_x*w, y-anchor_y*h, w, h))
        return

