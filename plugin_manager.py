import importlib.util
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


class PluginManager:
    def __init__(self, editor, plugin_folder="plugins"):
        self.editor = editor
        self.plugin_folder = Path(plugin_folder)
        self.plugin_folder.mkdir(exist_ok=True)
        self.loaded_plugins = {}
        self.plugin_menu = None

    def attach_menu(self, menu_bar):
        self.plugin_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Plugins", menu=self.plugin_menu)
        self.plugin_menu.add_command(label="Reload Plugins", command=self.load_plugins)
        self.plugin_menu.add_separator()

    def load_plugins(self):
        if not self.plugin_menu:
            return

        self.clear_plugin_commands()
        self.loaded_plugins.clear()

        for plugin_path in sorted(self.plugin_folder.glob("*.py")):
            self.load_plugin(plugin_path)

        self.editor.logger.log(f"PLUGIN_RELOAD: {len(self.loaded_plugins)} loaded")

    def clear_plugin_commands(self):
        last_index = self.plugin_menu.index("end")

        if last_index is None:
            return

        if last_index >= 2:
            self.plugin_menu.delete(2, "end")

    def load_plugin(self, plugin_path):
        plugin_name = plugin_path.stem

        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, "register"):
                self.editor.logger.log(f"PLUGIN_SKIPPED_NO_REGISTER: {plugin_name}")
                return

            module.register(self.editor, self)
            self.loaded_plugins[plugin_name] = module
            self.editor.logger.log("PLUGIN_LOADED: " + plugin_name)
        except Exception as error:
            self.editor.logger.log(f"PLUGIN_ERROR: {plugin_name}: {error}")
            messagebox.showerror(
                "Plugin Error",
                f"Could not load plugin '{plugin_name}'.\n\n{error}"
            )

    def add_command(self, label, command):
        if not self.plugin_menu:
            return

        self.plugin_menu.add_command(label=label, command=command)
