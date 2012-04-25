
from traits.api import DelegatesTo, Property
from enable.tools.viewport_zoom_tool import ViewportZoomTool

class MappingZoomTool(ViewportZoomTool):

    zoom_level = DelegatesTo('component')
    min_level = Property(lambda self: self.component.min_level)
    max_level = Property(lambda self: self.component.max_level)

    def _min_zoom_default(self):
        if self.zoom_level == self.min_level: return 1.0
        else: return 0.5

    def _max_zoom_default(self):
        if self.zoom_level == self.max_level: return 1.0
        else: return 2.0

    def _zoom_level_changed(self, old, new):
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        if new == self.min_level:
            self.min_zoom = 1.0
        if new == self.max_level:
            self.max_zoom = 1.0

    def normal_mouse_wheel(self, event):
        """ Handles the mouse wheel being used when the tool is in the 'normal'
        state.

        Scrolling the wheel "up" zooms in; scrolling it "down" zooms out.
        self.component is the viewport
        self.component.component is the canvas

        """
        if self.enable_wheel and event.mouse_wheel != 0:

            position = self.component.view_position
            scale = self.component.zoom
            transformed_x = event.x / scale + position[0]
            transformed_y = event.y / scale + position[1]
            
            # Calculate zoom
            if event.mouse_wheel < 0:
                zoom = 1.0 / (1.0 + 0.5 * self.wheel_zoom_step)
                new_zoom = self.component.zoom * zoom
            elif event.mouse_wheel > 0:
                zoom = 1.0 + 0.5 * self.wheel_zoom_step
                new_zoom = self.component.zoom * zoom
            
            # Change zoom level if necessary
            factor = 1
            if new_zoom < self.min_zoom:
                new_zoom = 1.0
                factor = 0.5
                if self.zoom_level > self.min_level: self.zoom_level -= 1
                else: return
            elif new_zoom > self.max_zoom:
                new_zoom = 1.0
                factor = 2
                if self.zoom_level < self.max_level: self.zoom_level += 1
                else: return
            
            x_pos = (transformed_x - (transformed_x - position[0]) / zoom) * factor
            y_pos = (transformed_y - (transformed_y - position[1]) / zoom) * factor

            self.component.zoom = new_zoom

            bounds = self.component.view_bounds
            self.component.set(view_bounds = [bounds[0] / zoom , bounds[1] / zoom],
                               view_position = [x_pos, y_pos])

            event.handled = True
            self.component.request_redraw()
        return
