
from numpy import array, transpose, zeros, concatenate, newaxis, invert, isnan, empty
from traits.api import Instance, List, DelegatesTo, Array
from chaco.api import ColormappedScatterPlot, render_markers
from enable.api import MarkerNameDict, CustomMarker, AbstractMarker
from enable.compiled_path import CompiledPath
from kiva.constants import FILL_STROKE

from mapping.enable.i_tile_manager import ITileManager
from mapping.chaco.map import Map

class ChoroplethPlot(ColormappedScatterPlot):

    tile_cache = DelegatesTo("_map_overlay")
    zoom_level = DelegatesTo("_map_overlay")
    
    compiled_paths = List(CompiledPath)

    _map_overlay = Instance(Map, ())

    _cached_paths = Array

    def __init__(self, *args, **kw):
        super(ChoroplethPlot, self).__init__(*args, **kw)
        self._map_overlay.component = self
        self.underlays.append(self._map_overlay)

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        self._gather_points()
        if len(self._cached_data_pts) == 0:
            pass
        else:
            # maps screen points
            colors = self._cached_data_pts[:,2]
            screen_pts = self.map_screen(self._cached_data_pts)
            pts = concatenate((screen_pts, colors[:,newaxis]), axis=1)
            self._render(gc, (pts, self._cached_paths))

    def _gather_points(self):
        """ 
        Collects the data points that are within the plot bounds and caches them

        TODO: account for bounding boxes of polygon paths
        """
        if self._cache_valid:
            return

        if not self.index or not self.value:
            self._cached_data_pts = []
            self._cache_valid = True
            return

        index, index_mask = self.index.get_data_mask()
        value, value_mask = self.value.get_data_mask()
        paths = self.compiled_paths

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            self._cached_data_pts = []
            self._cache_valid = True
            return

        index_range_mask = self.index_mapper.range.mask_data(index)
        value_range_mask = self.value_mapper.range.mask_data(value)
        nan_mask = invert(isnan(index_mask)) & invert(isnan(value_mask))
        point_mask = index_mask & value_mask & nan_mask & \
                     index_range_mask & value_range_mask

        if self.color_data is not None:
            if self.color_data.is_masked():
                color_data, color_mask = self.color_data.get_data_mask()
                point_mask = point_mask & color_mask
            else:
                color_data = self.color_data.get_data()

            #color_nan_mask = isreal(color_data)
            color_nan_mask = invert(isnan(color_data))

            point_mask = point_mask & color_nan_mask
            points = transpose(array((index,value,color_data)))
        else:
            points = transpose(array((index, value)))

        paths = array(paths)

        self._cached_data_pts = points[point_mask]
        self._cached_paths = paths[point_mask]

        self._cache_valid = True
        return

    def _render(self, gc, (points, paths), icon_mode=True):
        """
        This same method is used both to render the scatterplot and to
        draw just the iconified version of this plot, with the latter
        simply requiring that a few steps be skipped.
        """

        gc.save_state()
        gc.clip_to_rect(self.x, self.y, self.width, self.height)

        factor = self.tile_cache.get_tile_size() << self.zoom_level

        render_variable_markers(gc, points, paths, factor,
                       self.color_mapper, self.fill_alpha, self.line_width, 
                       self.outline_color_)

        # Draw the default axes, if necessary
        self._draw_default_axes(gc)
        gc.restore_state()

def render_variable_markers(gc, points, paths, factor, color_mapper,
                            fill_alpha, line_width, outline_color):
    """ Helper function for a PlotComponent instance to render a
    set of (x,y) points onto a graphics context.  Currently, it makes some
    assumptions about the attributes on the plot object; these may be factored
    out eventually.

    """

    if len(points) == 0:
        return

    xs, ys, colors = transpose(points)
    
    # Map the colors
    colors = color_mapper.map_screen(colors)
    alphas = (zeros(len(colors))+fill_alpha)[:, newaxis]
    colors = concatenate((colors[:, :3], alphas), axis=1)

    with gc:
        gc.set_stroke_color(outline_color)
        gc.set_line_width(line_width)

        mode = FILL_STROKE

        for x, y, c, p in zip(xs, ys, colors, paths):
            with gc:
                gc.set_fill_color(c)
                gc.translate_ctm(x, y)
                gc.scale_ctm(factor, factor)
                gc.begin_path()
                gc.add_path(p)
                gc.draw_path(mode)
