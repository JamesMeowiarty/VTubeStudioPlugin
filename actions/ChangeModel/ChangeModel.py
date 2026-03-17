# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.DeckManagement.InputIdentifier import Input, InputEvent, InputIdentifier

# Import python modules
import os
from loguru import logger as log

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GObject, Gtk, Adw

class ChangeModel(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.has_configuration = True

    def on_tick(self):
        settings = self.get_settings()
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "vts.png")
        self.set_media(media_path=icon_path, size=0.75)

        if not self.plugin_base.auth_lock:
            try:
                self.plugin_base.get_connected()
                if self.plugin_base.auth:
                    self.set_label(text=settings.get("model_name"), position="bottom", update=True)
                else:
                    log.info("Not connected. Make sure VTubeStudio api is running")
            except Exception as e:
                self.plugin_base.auth = False
                log.error(f"Error during connection/authentication process: {e}")

        
    def on_ready(self) -> None:
        self.on_tick()

    def on_key_down(self) -> None:
        ## removing possible api lock because of user interaction
        try:
            if self.plugin_base.auth_lock:
                self.plugin_base.auth_lock = False
                self.plugin_base.get_connected()
            settings = self.get_settings()
            model_name = settings.get("model_name")
            self.plugin_base.backend.changeModel(self.models_dict[model_name])
        except Exception as e:
            log.error(f"on_key_down error: {e}")
            self.plugin_base.get_connected(True)
    
    def get_config_rows(self) -> list:
        self.models_string_list = Gtk.StringList()
        self.models_row = Adw.ComboRow(title=self.plugin_base.lm.get("actions.changemodel.changemodel"), model=self.models_string_list)
        self.models_row.set_enable_search(True)

        self.load_model_string_list()

        self.models_row.connect("notify::selected-item", self.on_model_change)

        self.load_config_settings()

        return [self.hotkey_row]
 
    def load_model_string_list(self):
        self.models_dict = self.plugin_base.backend.getModels()
        for i in range(self.models_string_list.get_n_items()):
            self.models_string_list.remove(0)
        for model_name in self.models_dict.keys():
            self.models_string_list.append(model_name)
 
    def load_config_settings(self):
        settings = self.get_settings()
        log.info(f"Loaded settings: {settings}")
        if settings == None:
            return
        model_name = settings.get("model_name")
        for i, model_string_model in enumerate(self.models_string_list):
            if model_string_model.get_string() == model_name:
                self.models_row.set_selected(i)
                return
 
    def on_hotkey_change(self, combo, *args):
        model_name = combo.get_selected_item().get_string()

        settings = self.get_settings()
        settings["model_name"] = model_name
        settings['model_id'] = self.models_dict[model_name]

        self.set_settings(settings)
