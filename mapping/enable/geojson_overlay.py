
import geojson
import numpy as np

# Enthought library imports
from traits.api import Str, List, Instance, Array, on_trait_change
from chaco.api import AbstractOverlay
from enable.compiled_path import CompiledPath
from kiva.constants import STROKE, FILL_STROKE

class GeoJSONOverlay(AbstractOverlay):

    geojs_filename = Str

    _polys = List
    _paths = List(CompiledPath)

    _colors = Array

    def _geojs_filename_changed(self, name):
        data = file(name).read()
        polys = process_raw(data.replace('\r\n', ''))
        # Generate compiled path from the polygons
        paths = []
        for poly in polys:
            path = CompiledPath()
            for p in poly:
                path.lines(p)
            paths.append(path)
        self._paths = paths

        red = np.array([202, 0, 32])/255.
        blue = np.array([5, 113, 176])/255.
        colors = red * np.random.random_integers(0,1,len(paths)).reshape(-1,1)
        colors[np.sum(colors,axis=-1)==0] = blue
        self._colors = colors

        # Store the polygons just in case we need to regenerate the path
        self._polys = polys
        self.request_redraw()

    def overlay(self, other_component, gc, view_bounds=None, mode="default"):
        x, y, width, height = view_bounds
        zoom = other_component._zoom_level
        factor = 256 << zoom
        with gc:
            gc.clip_to_rect(x,y,width, height)

            gc.set_stroke_color((1, 1, 1))
            gc.set_line_width(1)
            
            gc.scale_ctm(factor, factor)
            
            for path, color in zip(self._paths, self._colors):
                gc.begin_path()
                gc.add_path(path)
                gc.set_fill_color(color)
                gc.draw_path(FILL_STROKE)
        super(GeoJSONOverlay, self).overlay(other_component, gc, view_bounds, mode)


def process_raw(data):
    # Process into a list of polygons?
    geojs = geojson.loads(data.replace('\r\n', ''))
    
    geotype = geojs.type
    polys = []
    if geotype == "FeatureCollection":
        features = geojs.features
        for feature in geojs.features:
            p = []
            if feature.geometry:
                process_geometry(feature.geometry, p)
                polys.append(p)
    elif geotype == "Feature":
        process_geometry(geojs.geometry, polys)

    return polys

def process_geometry(obj, polys):
    if obj.type == "MultiPolygon":
        for poly in obj.coordinates:
            polys.extend(WGS84_to_screen(np.array(poly)))
    elif obj.type == "Polygon":
        polys.extend(WGS84_to_screen(np.array(obj.coordinates)))
    elif obj.type == "GeometryCollection":
        for geo in obj.geometries:
            process_geometry(geo, polys)
    else:
        raise Exception("Can't handle %s geometry"%obj.type)

def WGS84_to_screen(coords):
    coords[:,:,0] = (coords[:,:,0] + 180.) / 360.
    coords[:,:,1] = np.radians(coords[:,:,1])
    coords[:,:,1] = (1 - (1. - np.log(np.tan(coords[:,:,1]) + 
                                     (1 / np.cos(coords[:,:,1]))) / np.pi) / 2.0)
    return coords
