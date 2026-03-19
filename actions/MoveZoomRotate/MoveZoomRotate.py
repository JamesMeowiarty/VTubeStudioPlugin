# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.DeckManagement.InputIdentifier import Input, InputEvent, InputIdentifier

# Import python modules
import os
from loguru import logger as log

from GtkHelper.ScaleRow import ScaleRow

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GObject, Gtk, Adw

class MoveZoomRotate(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.has_configuration = True

    def on_tick(self):
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "pan.png")
        self.set_media(media_path=icon_path, size=0.75)


        if not self.plugin_base.auth_lock:
            try:
                self.plugin_base.get_connected()
                if self.plugin_base.auth:
                    pos = self.plugin_base.backend.getModelPosition()
                    self.set_bottom_label(f"{round(pos['x'],2)}, {round(pos['y'],2)}")
                else:
                    log.info("Not connected. Make sure VTubeStudio api is running")
            except Exception as e:
                self.plugin_base.auth = False
                log.error(f"Error during connection/authentication process: {e}")


    def event_callback(self, event: InputEvent, data: dict = None):
        if event == Input.Key.Events.SHORT_UP:
            self.on_key_down()
        
    def on_ready(self) -> None:
        self.on_tick()


    def on_key_down(self) -> None:
        try:
            settings = self.get_settings()
            if self.plugin_base.auth_lock:
                self.plugin_base.auth_lock = False
                self.plugin_base.get_connected()
            pos = self.plugin_base.backend.getModelPosition()
            x = settings.get("x", pos['x'])
            y = settings.get("y", pos['y'])
            zoom = settings.get("zoom", pos['size'])
            rot = settings.get("rotate", pos["rot"])
            move_time = settings.get("time", 0)

            x = max(-1000, min(1000, x))
            y = max(-1000, min(1000, y))
            rot = max(-360, min(360, rot))
            zoom = max(-100, min(100, zoom))

            self.plugin_base.backend.moveModel(x, y, rot, zoom, False, move_time)
        except Exception as e:
            log.error(f"on_key_down error: {e}")
            self.plugin_base.get_connected(True)
    
    def get_config_rows(self) -> list:
        self.x = ScaleRow(title=self.plugin_base.lm.get("actions.movezoomrotate.x"), value=0, min=-1, max=1, step=0.05, draw_value=True)
        self.y = ScaleRow(title=self.plugin_base.lm.get("actions.movezoomrotate.y"), value=0, min=-1, max=1, step=0.05, draw_value=True)
        self.zoom = ScaleRow(title=self.plugin_base.lm.get("actions.movezoomrotate.zoom"), value= 1, min=-100, max=100, step=1, draw_value=True)
        self.rotate = ScaleRow(title=self.plugin_base.lm.get("actions.movezoomrotate.rotate"), value= 1, min=-360, max=360, step=1, draw_value=True)
        self.time_scale = ScaleRow(title=self.plugin_base.lm.get("plugin.time"), value=0, min=0, max=2, step=0.25, draw_value=True)

        self.x.scale.connect("value-changed", self.on_x_change)
        self.y.scale.connect("value-changed", self.on_y_change)
        self.zoom.scale.connect("value-changed", self.on_zoom_change)
        self.rotate.scale.connect("value-changed", self.on_rotate_change)
        self.time_scale.scale.connect("value-changed", self.on_time_change)

        self.load_config_settings()

        return [self.x, self.y, self.zoom, self.rotate, self.time_scale]
 
    def load_config_settings(self):
        settings = self.get_settings()
        if settings == None:
            return
        
        # Initialize any uninitialized settings
        settings_variables = ["x", "y", "zoom", "rotate", "time"]
        settings_need_initialized = False
        for settings_variable in settings_variables:
            if not settings.get(settings_variable):
                settings[settings_variable] = 0
                settings_need_initialized
        if settings_need_initialized:
            self.set_settings(settings)

        self.x.scale.set_value(settings.get("x"))
        self.y.scale.set_value(settings.get("y"))
        self.zoom.scale.set_value(settings.get("zoom"))
        self.rotate.scale.set_value(settings.get("rotate"))
        self.time_scale.scale.set_value(settings.get("time"))
 
    def on_x_change(self, scale, *args):
        settings = self.get_settings()

        amount = scale.get_value()

        settings["x"] = amount
        self.set_settings(settings)

    def on_y_change(self, scale, *args):
        settings = self.get_settings()

        amount = scale.get_value()

        settings["y"] = amount
        self.set_settings(settings)

    def on_zoom_change(self, scale, *args):
        settings = self.get_settings()

        amount = scale.get_value()

        settings["zoom"] = amount
        self.set_settings(settings)

    def on_rotate_change(self, scale, *args):
        settings = self.get_settings()

        amount = scale.get_value()

        settings["rotate"] = amount
        self.set_settings(settings)

    def on_time_change(self, scale, *args):
        settings = self.get_settings()

        amount = scale.get_value()

        settings["time"] = amount
        self.set_settings(settings)
