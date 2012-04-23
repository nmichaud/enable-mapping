
from traits.api import Property

from enable.enable_traits import coordinate_trait
from enable.primitives.api import Shape

class GeoPrimitive(Shape):
    """ Coordinates are in Lat/Long using WGS84 Datum
    """

    geoposition  = coordinate_trait
    
    position = Property(coordinate_trait)

    def _get_position(self):
        # Translate the geoposition to screen space
        lat, lon = self.geoposition
        x, y = self.container.transformToScreen(lon, lat)
        # shift based on bounds
        w, h = self.bounds
        return x-w/2, y-h/2

    def _text_default(self):
        # Disable text labels for now
        return ''

    def normal_left_down(self, event):
        # Disable mouse interaction for now
        return

