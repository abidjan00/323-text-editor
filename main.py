import tkinter as tk
from analytics import AnalyticsManager
from autosave import AutosaveManager
from explorer import SidebarExplorer
from fileops import FileOperations
from lifo import LifoManager
from log import AppLogger
from memory import MemoryManager
from search import SearchManager
from tab_manager import TabManager

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Monkey 1.0.0")
        self.root.geometry("800x600")

        self.current_file = None
        self.undo_stack = [""]
        self.redo_stack = []
        self.tab_manager = None
        self.explorer = None
        self.autosave_manager = None
        self.fileops = None
        self.lifo = None
        self.logger = AppLogger()
        self.memory = None
        self.search_manager = None
        self.dark_mode = tk.BooleanVar(value=False)
        self.sidebar_visible = tk.BooleanVar(value=True)

        # main content area
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill="both")

        self.explorer = SidebarExplorer(self, self.main_frame)

        # text area + scrollbar container
        self.text_frame = tk.Frame(self.main_frame)
        self.text_frame.pack(side="left", expand=True, fill="both")

        self.tab_frame = tk.Frame(self.text_frame)
        self.tab_frame.pack(fill="x")

        self.editor_frame = tk.Frame(self.text_frame)
        self.editor_frame.pack(expand=True, fill="both")

        self.scrollbar = tk.Scrollbar(self.editor_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.text_area = tk.Text(
            self.editor_frame,
            wrap="word",
            yscrollcommand=self.scrollbar.set
        )
        self.text_area.pack(side="left", expand=True, fill="both")

        self.scrollbar.config(command=self.text_area.yview)
        self.memory = MemoryManager(self.logger)
        self.tab_manager = TabManager(self)
        self.autosave_manager = AutosaveManager(self)
        self.fileops = FileOperations(self)
        self.lifo = LifoManager(self)
        self.search_manager = SearchManager(self, self.root)
        self.analytics_manager = AnalyticsManager(self)
        self.analytics_manager.pack()
        self.analytics_manager.bind_events()

        # keyboard shortcuts 
        self.root.bind("<Control-z>", self.lifo.undo_event)
        self.root.bind("<Control-y>", self.lifo.redo_event)
        self.root.bind("<Control-s>", self.save_event)
        self.root.bind("<Control-a>", self.select_all_event)
        self.root.bind("<Control-c>", self.copy_event)
        self.root.bind("<Control-v>", self.paste_event)
        self.root.bind("<Control-x>", self.cut_event)
        self.root.bind("<Control-w>", self.close_tab_event)

        # menu
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command=self.fileops.open_file)
        self.file_menu.add_command(label="Save", command=self.fileops.save_file)
        self.file_menu.add_command(label="Rename", command=self.fileops.rename_file)
        self.file_menu.add_command(label="Delete", command=self.fileops.delete_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)

        self.edit_menu.add_command(label="Undo", command=self.lifo.undo)
        self.edit_menu.add_command(label="Redo", command=self.lifo.redo)

        # view
        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(
            label="Search",
            command=self.search_manager.toggle_search
        )
        self.view_menu.add_checkbutton(
            label="Explorer",
            variable=self.sidebar_visible,
            command=self.toggle_sidebar
        )
        self.view_menu.add_checkbutton(
            label="Dark Mode",
            variable=self.dark_mode,
            command=self.apply_theme
        )

        # shortcut
        self.root.bind("<Control-f>", self.search_manager.focus_search)

        self.refresh_explorer()
        self.apply_theme()
        self.autosave_manager.check_recovery()
        self.autosave_manager.start()

    def update_analytics(self, event=None):
        self.analytics_manager.update(event)

    def apply_theme(self):
        if self.dark_mode.get():
            colors = {
                "window": "#1f1f1f",
                "editor": "#252526",
                "text": "#f2f2f2",
                "muted": "#d0d0d0",
                "field": "#2d2d30",
                "button": "#3a3a3d",
                "select": "#5a4b57",
                "insert": "#ffffff"
            }
        else:
            colors = {
                "window": "#f0f0f0",
                "editor": "#ffffff",
                "text": "#000000",
                "muted": "#000000",
                "field": "#ffffff",
                "button": "#f0f0f0",
                "select": "#c7d8ff",
                "insert": "#000000"
            }

        self.root.config(bg=colors["window"])
        self.main_frame.config(bg=colors["window"])
        self.text_frame.config(bg=colors["window"])
        self.editor_frame.config(bg=colors["window"])
        self.tab_frame.config(bg=colors["window"])
        self.analytics_manager.apply_theme(colors)
        self.explorer.apply_theme(colors)
        self.search_manager.apply_theme(colors)
        self.text_area.config(
            bg=colors["editor"],
            fg=colors["text"],
            insertbackground=colors["insert"],
            selectbackground=colors["select"],
            selectforeground=colors["text"]
        )
        self.refresh_tabs()

        for menu in (self.menu, self.file_menu, self.edit_menu, self.view_menu):
            menu.config(
                bg=colors["window"],
                fg=colors["text"],
                activebackground=colors["field"],
                activeforeground=colors["text"]
            )

    def refresh_explorer(self):
        self.explorer.refresh()

    def open_selected_file(self, event=None):
        return self.explorer.open_selected_file(event)

    def go_up_folder(self):
        self.explorer.go_up_folder()

    def toggle_sidebar(self):
        self.explorer.toggle(self.sidebar_visible.get(), self.text_frame)

    def get_editor_content(self):
        return self.text_area.get("1.0", "end-1c")

    def current_tab(self):
        return self.tab_manager.current_tab()

    def save_current_tab_state(self):
        self.tab_manager.save_current_tab_state()

    def refresh_tabs(self):
        self.tab_manager.refresh_tabs()

    def switch_tab(self, file_path):
        self.tab_manager.switch_tab(file_path)

    def close_current_tab(self):
        if self.current_file:
            self.close_tab(self.current_file)

    def close_tab_event(self, event=None):
        self.close_current_tab()
        return "break"

    def close_tab(self, file_path):
        self.tab_manager.close_tab(file_path)

    def save_event(self, event=None):
        self.fileops.save_file()
        return "break"

    def select_all_event(self, event=None):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        self.update_analytics()
        return "break"

    def copy_event(self, event=None):
        self.text_area.event_generate("<<Copy>>")
        return "break"

    def paste_event(self, event=None):
        self.text_area.event_generate("<<Paste>>")
        self.lifo.capture_state()
        self.update_analytics()
        return "break"

    def cut_event(self, event=None):
        self.text_area.event_generate("<<Cut>>")
        self.lifo.capture_state()
        self.update_analytics()
        return "break"
    
if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()
