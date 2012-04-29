
import numpy as np

from traits.api import List, Array, Bool, Instance, on_trait_change
from kiva.constants import STROKE, FILL_STROKE

from geo_primitive import GeoPrimitive
from geojson import GeoJSON

class GeoGeometry(GeoPrimitive):

    geojs = Instance(GeoJSON)
    
    draw_mode = FILL_STROKE
    antialias = Bool(True)

    scale_with_zoom = True

    _polygons = List(Array)
    
    def _render_primitive(self, gc, view_bounds=None, mode='default'):
        """ Draw the component """
        with gc:
            if self.draw_mode == STROKE:
                gc.set_stroke_color((0.4, 0.4, 0.4))
                gc.set_line_width(1.0)
            else:
                gc.set_stroke_color((0.1, 0.1, 0.1))
                gc.set_line_width(1.0)
                gc.set_fill_color((0.4, 0.4, 0.4))

            gc.set_antialias(self.antialias)

            map_units = self.container.tile_cache.get_tile_size() << self.container._zoom_level
            
            gc.begin_path()
            for polygon in self._polygons:
                gc.lines( polygon[0] * map_units)
            
            gc.draw_path(self.draw_mode)

    @on_trait_change('container, container:_zoom_level')
    def _recalc_bounds(self):
        tile_size = self.container.tile_cache.get_tile_size()
        bl, tr = self.geojs.bounds
        bl = self.container.transformToScreen(bl[1], bl[0])
        tr = self.container.transformToScreen(tr[1], tr[0])
        self.bounds = (tr[0]-bl[0], tr[1]-bl[1])

    def _geojs_changed(self, new):
        # Retrieve the coordinates
        geojs = self.geojs
        
        geotype = geojs.type
        polys = []
        if geotype == "FeatureCollection":
            features = geojs.features
            for feature in geojs.features:
                self._process_geometry(feature.geometry, polys, )
        elif geotype == "Feature":
            self._process_geometry(geojs.geometry, polys, )
        else:
            raise Exception("Don't know how to handle this")
        self._polygons = polys
        
        # set position
        bl, tr = geojs.bounds
        self.geoposition = ((bl[1]+tr[1])/2., (bl[0]+tr[0])/2.)

    def _process_geometry(self, obj, polys):
        if obj.type == "MultiPolygon":
            for poly in obj.coordinates:
                polys.append(self._convert_WGS84_to_screen(np.array(poly), ))
        elif obj.type == "Polygon":
            polys.append(self._convert_WGS84_to_screen(np.array(obj.coordinates), ))
        else:
            raise Exception("Can't handle %s geometry"%obj.type)

    def _convert_WGS84_to_screen(self, coords):
        coords[:,:,0] = (coords[:,:,0] + 180.) / 360.
        coords[:,:,1] = np.radians(coords[:,:,1])
        coords[:,:,1] = (1 - (1. - np.log(np.tan(coords[:,:,1]) + (1 / np.cos(coords[:,:,1]))) / np.pi) / 2.0)
        return coords

