import os
import tkinter as tk
from tkinter import filedialog, messagebox

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Monkey 1.0.0")
        self.root.geometry("800x600")

        self.current_file = None
        self.undo_stack = [""]
        self.redo_stack = []
        self.open_tabs = {}
        self.tab_order = []
        self.dark_mode = tk.BooleanVar(value=False)
        self.sidebar_visible = tk.BooleanVar(value=True)
        self.explorer_path = os.path.expanduser("~")
        self.explorer_items = []

        # ram simulation
        self.memory = {}
        self.memory_order = []
        self.MEMORY_LIMIT = 5

        # main content area
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill="both")

        # sidebar explorer
        self.sidebar_frame = tk.Frame(self.main_frame, width=180)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.sidebar_header = tk.Frame(self.sidebar_frame)
        self.sidebar_header.pack(fill="x")

        self.sidebar_label = tk.Label(
            self.sidebar_header,
            text=self.explorer_path,
            anchor="w"
        )
        self.sidebar_label.pack(side="left", fill="x", expand=True)

        self.up_button = tk.Button(
            self.sidebar_header,
            text="Up",
            command=self.go_up_folder
        )
        self.up_button.pack(side="right")

        self.refresh_button = tk.Button(
            self.sidebar_header,
            text="Refresh",
            command=self.refresh_explorer
        )
        self.refresh_button.pack(side="right")

        self.file_listbox = tk.Listbox(self.sidebar_frame, activestyle="none")
        self.file_listbox.pack(side="left", fill="both", expand=True)
        self.file_listbox.bind("<Double-Button-1>", self.open_selected_file)
        self.file_listbox.bind("<Return>", self.open_selected_file)

        self.explorer_scrollbar = tk.Scrollbar(
            self.sidebar_frame,
            command=self.file_listbox.yview
        )
        self.explorer_scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=self.explorer_scrollbar.set)

        # text area + scrollbar container
        self.text_frame = tk.Frame(self.main_frame)
        self.text_frame.pack(side="left", expand=True, fill="both")

        self.tab_frame = tk.Frame(self.text_frame)
        self.tab_frame.pack(fill="x")

        self.editor_frame = tk.Frame(self.text_frame)
        self.editor_frame.pack(expand=True, fill="both")

        self.scrollbar = tk.Scrollbar(self.editor_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.autosave_file = "autosave.txt"

        self.text_area = tk.Text(
            self.editor_frame,
            wrap="word",
            yscrollcommand=self.scrollbar.set
        )
        self.text_area.pack(side="left", expand=True, fill="both")

        self.scrollbar.config(command=self.text_area.yview)

        # analytics status bar
        self.analytics_label = tk.Label(
            root,
            text="Words: 0 | Characters: 0 | Lines: 0",
            anchor="w"
        )
        self.analytics_label.pack(fill="x", side="bottom")

        self.text_area.bind("<KeyRelease>", self.on_key_event)

        # keyboard shortcuts 
        self.root.bind("<Control-z>", self.undo_event)
        self.root.bind("<Control-y>", self.redo_event)
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

        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Rename", command=self.rename_file)
        self.file_menu.add_command(label="Delete", command=self.delete_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)

        self.edit_menu.add_command(label="Undo", command=self.undo)
        self.edit_menu.add_command(label="Redo", command=self.redo)

        # VIEW MENU
        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Search", command=self.toggle_search)
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

        # search bar (hidden initially)
        self.search_frame = tk.Frame(self.root)

        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", self.search_text)

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            command=self.search_text
        )
        self.search_button.pack(side="right")

        # shortcut
        self.root.bind("<Control-f>", self.focus_search)

        self.refresh_explorer()
        self.apply_theme()
        self.check_recovery()
        self.start_autosave()

    def on_key_event(self, event):
        self.capture_state()
        self.update_analytics()

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
        self.sidebar_frame.config(bg=colors["window"])
        self.sidebar_header.config(bg=colors["window"])
        self.search_frame.config(bg=colors["window"])
        self.sidebar_label.config(
            bg=colors["window"],
            fg=colors["muted"]
        )
        self.analytics_label.config(
            bg=colors["window"],
            fg=colors["muted"]
        )
        self.file_listbox.config(
            bg=colors["field"],
            fg=colors["text"],
            selectbackground=colors["select"],
            selectforeground=colors["text"]
        )
        self.refresh_button.config(
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["field"],
            activeforeground=colors["text"]
        )
        self.up_button.config(
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["field"],
            activeforeground=colors["text"]
        )
        self.text_area.config(
            bg=colors["editor"],
            fg=colors["text"],
            insertbackground=colors["insert"],
            selectbackground=colors["select"],
            selectforeground=colors["text"]
        )
        self.search_entry.config(
            bg=colors["field"],
            fg=colors["text"],
            insertbackground=colors["insert"]
        )
        self.search_button.config(
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["field"],
            activeforeground=colors["text"]
        )
        self.refresh_tabs()

        for menu in (self.menu, self.file_menu, self.edit_menu, self.view_menu):
            menu.config(
                bg=colors["window"],
                fg=colors["text"],
                activebackground=colors["field"],
                activeforeground=colors["text"]
            )

    def log(self, action):
        from datetime import datetime

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("log.txt", "a") as f:
            f.write(f"[{time}] {action}\n")

    def refresh_explorer(self):
        self.file_listbox.delete(0, tk.END)
        self.explorer_items = []
        self.sidebar_label.config(text=self.explorer_path)

        try:
            entries = os.listdir(self.explorer_path)
        except Exception as e:
            self.log("EXPLORER_ERROR: " + str(e))
            return

        folders = []
        files = []

        for name in entries:
            path = os.path.join(self.explorer_path, name)

            if os.path.isdir(path):
                folders.append((name, path))
            elif os.path.isfile(path):
                files.append((name, path))

        for name, path in sorted(folders, key=lambda item: item[0].lower()):
            self.explorer_items.append(path)
            self.file_listbox.insert(tk.END, "[D] " + name)

        for name, path in sorted(files, key=lambda item: item[0].lower()):
            self.explorer_items.append(path)
            self.file_listbox.insert(tk.END, "[F] " + name)

    def open_selected_file(self, event=None):
        selected = self.file_listbox.curselection()

        if not selected:
            return "break"

        selected_path = self.explorer_items[selected[0]]

        if os.path.isdir(selected_path):
            self.explorer_path = selected_path
            self.refresh_explorer()
        else:
            self.load_file(selected_path)

        return "break"

    def go_up_folder(self):
        parent = os.path.dirname(self.explorer_path)

        if parent and parent != self.explorer_path:
            self.explorer_path = parent
            self.refresh_explorer()

    def toggle_sidebar(self):
        if self.sidebar_visible.get():
            self.sidebar_frame.pack(side="left", fill="y", before=self.text_frame)
        else:
            self.sidebar_frame.pack_forget()

    def get_editor_content(self):
        return self.text_area.get("1.0", "end-1c")

    def current_tab(self):
        if not self.current_file:
            return None

        return self.open_tabs.get(self.current_file)

    def remember_file(self, file_path, content):
        if file_path in self.memory_order:
            self.memory_order.remove(file_path)
        elif len(self.memory_order) >= self.MEMORY_LIMIT:
            oldest = self.memory_order.pop(0)
            self.memory.pop(oldest, None)
            self.log("MEMORY_EVICT: " + oldest)

        self.memory_order.append(file_path)
        self.memory[file_path] = content

    def save_current_tab_state(self):
        tab = self.current_tab()

        if not tab:
            return

        content = self.get_editor_content()
        tab["content"] = content
        tab["undo_stack"] = self.undo_stack
        tab["redo_stack"] = self.redo_stack
        self.remember_file(self.current_file, content)

    def refresh_tabs(self):
        for child in self.tab_frame.winfo_children():
            child.destroy()

        if self.dark_mode.get():
            active_bg = "#4a4a4d"
            inactive_bg = "#2d2d30"
            fg = "#f2f2f2"
            close_bg = "#3a3a3d"
        else:
            active_bg = "#ffffff"
            inactive_bg = "#e5e5e5"
            fg = "#000000"
            close_bg = "#dddddd"

        title_counts = {}

        for file_path in self.tab_order:
            title = os.path.basename(file_path)
            title_counts[title] = title_counts.get(title, 0) + 1

        for file_path in self.tab_order:
            tab = self.open_tabs.get(file_path)

            if not tab:
                continue

            title = tab["title"]

            if title_counts.get(title, 0) > 1:
                title = f"{title} - {os.path.basename(os.path.dirname(file_path))}"

            tab_bg = active_bg if file_path == self.current_file else inactive_bg

            tab_container = tk.Frame(
                self.tab_frame,
                bg=tab_bg,
                bd=1,
                relief=tk.RAISED if file_path == self.current_file else tk.FLAT
            )
            tab_container.pack(side="left", padx=(0, 1), pady=(0, 1))

            button = tk.Button(
                tab_container,
                text=title,
                relief=tk.FLAT,
                bg=tab_bg,
                fg=fg,
                activebackground=active_bg,
                activeforeground=fg,
                command=lambda path=file_path: self.switch_tab(path)
            )
            button.pack(side="left")

            close_button = tk.Button(
                tab_container,
                text="x",
                width=2,
                relief=tk.FLAT,
                bg=close_bg,
                fg=fg,
                activebackground=active_bg,
                activeforeground=fg,
                command=lambda path=file_path: self.close_tab(path)
            )
            close_button.pack(side="left")

    def switch_tab(self, file_path):
        if file_path == self.current_file:
            return

        tab = self.open_tabs.get(file_path)

        if not tab:
            return

        self.save_current_tab_state()

        self.current_file = file_path
        self.undo_stack = tab["undo_stack"]
        self.redo_stack = tab["redo_stack"]

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, tab["content"])

        self.update_analytics()
        self.refresh_tabs()
        self.log("SWITCH_TAB: " + file_path)

    def close_current_tab(self):
        if self.current_file:
            self.close_tab(self.current_file)

    def close_tab_event(self, event=None):
        self.close_current_tab()
        return "break"

    def close_tab(self, file_path):
        tab = self.open_tabs.get(file_path)

        if not tab:
            return

        if file_path == self.current_file:
            self.save_current_tab_state()
        else:
            self.remember_file(file_path, tab["content"])

        try:
            tab_index = self.tab_order.index(file_path)
        except ValueError:
            tab_index = 0

        self.open_tabs.pop(file_path, None)

        if file_path in self.tab_order:
            self.tab_order.remove(file_path)

        if not self.tab_order:
            self.current_file = None
            self.undo_stack = [""]
            self.redo_stack = []
            self.text_area.delete(1.0, tk.END)
            self.update_analytics()
            self.refresh_tabs()
            self.log("CLOSE_TAB: " + file_path)
            return

        if file_path == self.current_file:
            next_index = min(tab_index, len(self.tab_order) - 1)
            next_file = self.tab_order[next_index]
            self.current_file = None
            self.switch_tab(next_file)
        else:
            self.refresh_tabs()

        self.log("CLOSE_TAB: " + file_path)

    # state capture
    def capture_state(self, event=None):
        current = self.get_editor_content()

        if self.undo_stack[-1] == current:
            return

        self.undo_stack.append(current)
        self.redo_stack.clear()

        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)

        tab = self.current_tab()

        if tab:
            tab["content"] = current
            tab["undo_stack"] = self.undo_stack
            tab["redo_stack"] = self.redo_stack
            self.remember_file(self.current_file, current)

    # analytics update
    def update_analytics(self, event=None):
        content = self.text_area.get("1.0", "end-1c")

        words = len(content.split())
        chars = len(content)
        lines = content.count("\n") + 1

        self.analytics_label.config(
            text=f"Words: {words} | Characters: {chars} | Lines: {lines}"
        )

    # undo
    def undo(self):
        if len(self.undo_stack) > 1:
            current = self.get_editor_content()
            self.redo_stack.append(current)

            self.undo_stack.pop()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.undo_stack[-1])
            self.save_current_tab_state()
            self.update_analytics()

    # event wrapper
    def undo_event(self, event):
        self.undo()
        self.log("UNDO")
        return "break"

    # redo
    def redo(self):
        if self.redo_stack:
            current = self.get_editor_content()
            self.undo_stack.append(current)

            next_state = self.redo_stack.pop()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, next_state)
            self.save_current_tab_state()
            self.update_analytics()
            self.log("REDO")

    # event wrapper 
    def redo_event(self, event):
        self.redo()
        return "break"

    def load_file(self, file_path):
        file_path = os.path.abspath(file_path)

        if file_path in self.open_tabs:
            self.switch_tab(file_path)
            return

        self.save_current_tab_state()

        if file_path in self.memory:
            content = self.memory[file_path]
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

        file_name = os.path.basename(file_path)

        self.open_tabs[file_path] = {
            "title": file_name,
            "content": content,
            "undo_stack": [content],
            "redo_stack": []
        }
        self.tab_order.append(file_path)
        self.remember_file(file_path, content)

        # display file
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, content)

        self.current_file = file_path
        self.undo_stack = self.open_tabs[file_path]["undo_stack"]
        self.redo_stack = self.open_tabs[file_path]["redo_stack"]
        self.update_analytics()
        self.refresh_tabs()

        self.log("OPEN_FILE: " + file_path)

    # open
    def open_file(self):
        file_path = filedialog.askopenfilename()

        if not file_path:
            self.log("OPEN_FILE_CANCELLED")
            return

        self.load_file(file_path)

    # save file
    def save_file(self):
        content = self.get_editor_content()

        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.save_current_tab_state()
            self.log("SAVE_FILE: " + self.current_file)
        else:
            path = filedialog.asksaveasfilename()
            if path:
                path = os.path.abspath(path)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.current_file = path
                self.open_tabs[path] = {
                    "title": os.path.basename(path),
                    "content": content,
                    "undo_stack": self.undo_stack,
                    "redo_stack": self.redo_stack
                }
                self.tab_order.append(path)
                self.remember_file(path, content)
                self.refresh_tabs()
                self.log("SAVE_FILE: " + path)
                self.refresh_explorer()

    def save_event(self, event=None):
        self.save_file()
        return "break"

    def select_all_event(self, event=None):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return "break"

    def copy_event(self, event=None):
        self.text_area.event_generate("<<Copy>>")
        return "break"

    def paste_event(self, event=None):
        self.text_area.event_generate("<<Paste>>")
        self.capture_state()
        self.update_analytics()
        return "break"

    def cut_event(self, event=None):
        self.text_area.event_generate("<<Cut>>")
        self.capture_state()
        self.update_analytics()
        return "break"
    
    def start_autosave(self):
        self.root.after(5000, self.autosave)
    
    def autosave(self):
        try:
            self.save_current_tab_state()
            content = self.get_editor_content()
            with open(self.autosave_file, "w", encoding="utf-8") as f:
                f.write(content)
        except:
            pass

        self.root.after(5000, self.autosave)


    def check_recovery(self):
        if not os.path.exists(self.autosave_file):
            return

        with open(self.autosave_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            return

        recover = messagebox.askyesno(
            "Recovery",
            "Recovered unsaved session found. Restore it?"
        )

        if recover:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)
            self.capture_state()
            self.update_analytics()
            self.log("RECOVERY_LOADED")
        else:
            self.log("RECOVERY_DISCARDED")

    # search
    def search_text(self, event=None):
        self.text_area.tag_remove("highlight", "1.0", tk.END)

        query = self.search_entry.get()

        if not query:
            return

        start = "1.0"

        while True:
            start = self.text_area.search(query, start, stopindex=tk.END)

            if not start:
                break

            end = f"{start}+{len(query)}c"

            self.text_area.tag_add("highlight", start, end)
            start = end

        self.text_area.tag_config("highlight", background="#ffb6c1")
        return "break"

    def focus_search(self, event=None):
        if not self.search_frame.winfo_ismapped():
            self.search_frame.pack(fill="x")

        self.search_entry.focus()
        return "break"

    def toggle_search(self):
        if self.search_frame.winfo_ismapped():
            self.search_frame.pack_forget()
        else:
            self.search_frame.pack(fill="x")
            self.search_entry.focus()

    def rename_file(self):
        if not self.current_file:
            self.log("RENAME_FAILED_NO_FILE")
            return

        new_name = filedialog.asksaveasfilename()

        if not new_name:
            self.log("RENAME_CANCELLED")
            return

        try:
            self.save_current_tab_state()
            old_name = self.current_file
            new_name = os.path.abspath(new_name)
            os.rename(self.current_file, new_name)
            self.log(f"RENAME: {old_name} -> {new_name}")

            if old_name in self.open_tabs:
                self.open_tabs[new_name] = self.open_tabs.pop(old_name)
                self.open_tabs[new_name]["title"] = os.path.basename(new_name)

            if old_name in self.tab_order:
                self.tab_order[self.tab_order.index(old_name)] = new_name

            if old_name in self.memory:
                self.memory[new_name] = self.memory.pop(old_name)

            if old_name in self.memory_order:
                self.memory_order[self.memory_order.index(old_name)] = new_name

            self.current_file = new_name
            self.refresh_tabs()
            self.refresh_explorer()
        except Exception as e:
            self.log("RENAME_ERROR: " + str(e))

    def delete_file(self):
        if not self.current_file:
            self.log("DELETE_FAILED_NO_FILE")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Delete this file?")

        if not confirm:
            self.log("DELETE_CANCELLED")
            return

        try:
            deleted_file = self.current_file
            os.remove(deleted_file)
            self.log("DELETE_FILE: " + deleted_file)

            self.text_area.delete(1.0, tk.END)
            self.open_tabs.pop(deleted_file, None)
            self.memory.pop(deleted_file, None)

            if deleted_file in self.tab_order:
                self.tab_order.remove(deleted_file)

            if deleted_file in self.memory_order:
                self.memory_order.remove(deleted_file)

            if self.tab_order:
                next_file = self.tab_order[-1]
                self.current_file = None
                self.switch_tab(next_file)
            else:
                self.current_file = None
                self.undo_stack = [""]
                self.redo_stack = []
                self.update_analytics()
                self.refresh_tabs()

            self.refresh_explorer()
        except Exception as e:
            self.log("DELETE_ERROR: " + str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()
