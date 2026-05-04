import tkinter as tk
import tkinter.font as tkfont
from tkinter import colorchooser
from tkinter import ttk
from analytics import AnalyticsManager
from autosave import AutosaveManager
from code_runner import CodeRunner
from compression import CompressionManager
from explorer import SidebarExplorer
from fileops import FileOperations
from lifo import LifoManager
from log import AppLogger
from memory import MemoryManager
from search import SearchManager
from tab_manager import TabManager
from version_control import VersionControlManager

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
        self.code_runner = None
        self.compression_manager = None
        self.fileops = None
        self.lifo = None
        self.logger = AppLogger()
        self.memory = None
        self.search_manager = None
        self.version_control = None
        self.dark_mode = tk.BooleanVar(value=False)
        self.sidebar_visible = tk.BooleanVar(value=True)
        self.bold_active = tk.BooleanVar(value=False)
        self.italic_active = tk.BooleanVar(value=False)
        self.underline_active = tk.BooleanVar(value=False)
        self.font_family = tk.StringVar(value="Arial")
        self.font_size = tk.StringVar(value="12")
        self.current_text_color = "#000000"
        self.format_fonts = []
        self.last_selected_range = None
        self.top_bar_height = 34

        # main content area
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill="both")

        self.explorer = SidebarExplorer(self, self.main_frame)

        # text area + scrollbar container
        self.text_frame = tk.Frame(self.main_frame)
        self.text_frame.pack(side="left", expand=True, fill="both")

        self.toolbar_frame = tk.Frame(self.text_frame, height=self.top_bar_height)
        self.toolbar_frame.pack(fill="x")
        self.toolbar_frame.pack_propagate(False)

        self.bold_button = tk.Button(
            self.toolbar_frame,
            text="B",
            width=3,
            command=self.apply_bold
        )
        self.bold_button.pack(side="left", padx=2, pady=2)

        self.italic_button = tk.Button(
            self.toolbar_frame,
            text="I",
            width=3,
            command=self.apply_italic
        )
        self.italic_button.pack(side="left", padx=2, pady=2)

        self.underline_button = tk.Button(
            self.toolbar_frame,
            text="U",
            width=3,
            command=self.apply_underline
        )
        self.underline_button.pack(side="left", padx=2, pady=2)

        self.font_family_box = ttk.Combobox(
            self.toolbar_frame,
            textvariable=self.font_family,
            values=("Arial", "Calibri", "Courier New", "Georgia", "Times New Roman"),
            width=16,
            state="readonly"
        )
        self.font_family_box.pack(side="left", padx=2, pady=2)
        self.font_family_box.bind("<<ComboboxSelected>>", self.apply_font_family)

        self.font_size_box = ttk.Combobox(
            self.toolbar_frame,
            textvariable=self.font_size,
            values=("10", "12", "14", "16", "18", "20", "24", "28", "32"),
            width=5,
            state="readonly"
        )
        self.font_size_box.pack(side="left", padx=2, pady=2)
        self.font_size_box.bind("<<ComboboxSelected>>", self.apply_font_size)

        self.color_button = tk.Button(
            self.toolbar_frame,
            text="Color",
            command=self.apply_text_color
        )
        self.color_button.pack(side="left", padx=2, pady=2)

        self.tab_frame = tk.Frame(self.text_frame)
        self.tab_frame.pack(fill="x")

        self.editor_frame = tk.Frame(self.text_frame)
        self.editor_frame.pack(expand=True, fill="both")

        self.scrollbar = tk.Scrollbar(self.editor_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.text_area = tk.Text(
            self.editor_frame,
            wrap="word",
            yscrollcommand=self.scrollbar.set,
            font=("Arial", 12)
        )
        self.text_area.pack(side="left", expand=True, fill="both")
        self.text_area.bind("<Button-1>", self.focus_text_area, add="+")
        self.text_area.bind("<ButtonRelease-1>", self.remember_selected_range, add="+")
        self.text_area.bind("<KeyRelease>", self.remember_selected_range, add="+")

        self.scrollbar.config(command=self.text_area.yview)
        self.memory = MemoryManager(self.logger)
        self.tab_manager = TabManager(self)
        self.autosave_manager = AutosaveManager(self)
        self.code_runner = CodeRunner(self)
        self.compression_manager = CompressionManager(self)
        self.fileops = FileOperations(self)
        self.lifo = LifoManager(self)
        self.version_control = VersionControlManager(self)
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
        self.root.bind("<Control-b>", self.bold_event)
        self.root.bind("<Control-i>", self.italic_event)
        self.root.bind("<Control-u>", self.underline_event)
        self.root.bind("<F5>", self.run_python_event)

        # menu
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command=self.fileops.open_file)
        self.file_menu.add_command(label="Save", command=self.fileops.save_file)
        self.file_menu.add_command(label="Rename", command=self.fileops.rename_file)
        self.file_menu.add_command(label="Delete", command=self.fileops.delete_file)
        self.file_menu.add_command(
            label="Compress",
            command=self.compression_manager.compress_current_file
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)

        self.edit_menu.add_command(label="Undo", command=self.lifo.undo)
        self.edit_menu.add_command(label="Redo", command=self.lifo.redo)

        self.version_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Version", menu=self.version_menu)
        self.version_menu.add_command(
            label="Save Snapshot",
            command=self.version_control.snapshot_current_file
        )
        self.version_menu.add_command(
            label="Restore Version",
            command=self.version_control.show_restore_window
        )

        self.run_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Run", menu=self.run_menu)
        self.run_menu.add_command(
            label="Run Python",
            command=self.code_runner.run_python_code
        )

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
        self.toolbar_frame.config(bg=colors["window"])
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
        self.apply_toolbar_theme(colors)
        self.update_format_button_states()

        for menu in (
            self.menu,
            self.file_menu,
            self.edit_menu,
            self.version_menu,
            self.run_menu,
            self.view_menu
        ):
            menu.config(
                bg=colors["window"],
                fg=colors["text"],
                activebackground=colors["field"],
                activeforeground=colors["text"]
            )

    def apply_toolbar_theme(self, colors):
        for button in (
            self.bold_button,
            self.italic_button,
            self.underline_button,
            self.color_button
        ):
            button.config(
                bg=colors["button"],
                fg=colors["text"],
                activebackground=colors["field"],
                activeforeground=colors["text"]
            )

        style = ttk.Style()
        style.configure(
            "TCombobox",
            fieldbackground=colors["field"],
            background=colors["button"],
            foreground=colors["text"]
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

    def run_python_event(self, event=None):
        self.code_runner.run_python_code()
        return "break"

    def focus_text_area(self, event=None):
        self.text_area.focus_set()

    def selected_range(self):
        selected = self.text_area.tag_ranges(tk.SEL)

        if len(selected) >= 2:
            self.last_selected_range = (str(selected[0]), str(selected[1]))
            return self.last_selected_range

        return self.last_selected_range

    def remember_selected_range(self, event=None):
        selected = self.text_area.tag_ranges(tk.SEL)

        if len(selected) >= 2:
            self.last_selected_range = (str(selected[0]), str(selected[1]))

    def update_format_button_states(self):
        if self.dark_mode.get():
            active_bg = "#5a4b57"
            inactive_bg = "#3a3a3d"
            fg = "#f2f2f2"
        else:
            active_bg = "#c7d8ff"
            inactive_bg = "#f0f0f0"
            fg = "#000000"

        self.bold_button.config(
            bg=active_bg if self.bold_active.get() else inactive_bg,
            fg=fg
        )
        self.italic_button.config(
            bg=active_bg if self.italic_active.get() else inactive_bg,
            fg=fg
        )
        self.underline_button.config(
            bg=active_bg if self.underline_active.get() else inactive_bg,
            fg=fg
        )

    def apply_current_format_to_selection(self):
        selected = self.selected_range()

        if not selected:
            self.logger.log("FORMAT_SKIPPED_NO_SELECTION")
            self.text_area.focus_set()
            return

        start, end = selected
        family = self.font_family.get()
        size = int(self.font_size.get())
        weight = "bold" if self.bold_active.get() else "normal"
        slant = "italic" if self.italic_active.get() else "roman"
        underline = self.underline_active.get()
        color_key = self.current_text_color.lstrip("#")
        tag_name = (
            "format_"
            + family.replace(" ", "_")
            + f"_{size}_{weight}_{slant}_{int(underline)}_{color_key}"
        )
        text_font = tkfont.Font(
            family=family,
            size=size,
            weight=weight,
            slant=slant,
            underline=underline
        )
        self.format_fonts.append(text_font)
        self.text_area.tag_config(
            tag_name,
            font=text_font,
            foreground=self.current_text_color
        )
        self.text_area.tag_add(tag_name, start, end)
        self.text_area.tag_raise(tag_name)
        self.text_area.focus_set()
        self.lifo.capture_state()
        self.update_analytics()
        self.logger.log("FORMAT_APPLY: " + tag_name)

    def apply_bold(self):
        self.bold_active.set(not self.bold_active.get())
        self.update_format_button_states()
        self.apply_current_format_to_selection()

    def apply_italic(self):
        self.italic_active.set(not self.italic_active.get())
        self.update_format_button_states()
        self.apply_current_format_to_selection()

    def apply_underline(self):
        self.underline_active.set(not self.underline_active.get())
        self.update_format_button_states()
        self.apply_current_format_to_selection()

    def apply_font_family(self, event=None):
        self.apply_current_format_to_selection()
        return "break"

    def apply_font_size(self, event=None):
        self.apply_current_format_to_selection()
        return "break"

    def apply_text_color(self):
        color = colorchooser.askcolor(color=self.current_text_color)[1]

        if not color:
            self.logger.log("FORMAT_COLOR_CANCELLED")
            return

        self.current_text_color = color
        self.apply_current_format_to_selection()

    def bold_event(self, event=None):
        self.apply_bold()
        return "break"

    def italic_event(self, event=None):
        self.apply_italic()
        return "break"

    def underline_event(self, event=None):
        self.apply_underline()
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
