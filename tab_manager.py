import os
import tkinter as tk


class TabManager:
    def __init__(self, editor):
        self.editor = editor
        self.open_tabs = {}
        self.tab_order = []

    def current_tab(self):
        if not self.editor.current_file:
            return None

        return self.open_tabs.get(self.editor.current_file)

    def remember_tab(self, file_path, content):
        self.editor.memory.remember(file_path, content)

    def create_tab(self, file_path, content):
        file_path = os.path.abspath(file_path)

        if file_path in self.open_tabs:
            self.switch_tab(file_path)
            return

        file_name = os.path.basename(file_path)

        self.open_tabs[file_path] = {
            "title": file_name,
            "content": content,
            "undo_stack": [content],
            "redo_stack": []
        }

        self.tab_order.append(file_path)
        self.remember_tab(file_path, content)
        self.switch_tab(file_path)

    def switch_tab(self, file_path):
        file_path = os.path.abspath(file_path)

        if file_path == self.editor.current_file:
            return

        tab = self.open_tabs.get(file_path)

        if not tab:
            return

        self.save_current_tab_state()

        self.editor.current_file = file_path
        self.editor.undo_stack = tab["undo_stack"]
        self.editor.redo_stack = tab["redo_stack"]

        self.editor.text_area.delete("1.0", tk.END)
        self.editor.text_area.insert(tk.END, tab["content"])

        self.editor.update_analytics()
        self.editor.refresh_tabs()
        self.editor.logger.log("SWITCH_TAB: " + file_path)

    def save_current_tab_state(self):
        tab = self.current_tab()

        if not tab:
            return

        content = self.editor.get_editor_content()

        tab["content"] = content
        tab["undo_stack"] = self.editor.undo_stack
        tab["redo_stack"] = self.editor.redo_stack
        self.remember_tab(self.editor.current_file, content)

    def refresh_tabs(self):
        for child in self.editor.tab_frame.winfo_children():
            child.destroy()

        colors = getattr(self.editor, "theme_colors", {})
        active_bg = colors.get("active_tab", "#fff8fc")
        inactive_bg = colors.get("inactive_tab", "#ffd2e8")
        fg = colors.get("text", "#3a2030")
        close_bg = colors.get("button", "#ffc1df")
        border = colors.get("border", "#e86ca8")

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
                folder_name = os.path.basename(os.path.dirname(file_path))
                title = f"{title} - {folder_name}"

            tab_bg = active_bg if file_path == self.editor.current_file else inactive_bg

            tab_container = tk.Frame(
                self.editor.tab_frame,
                bg=tab_bg,
                bd=1,
                relief=tk.RIDGE,
                highlightbackground=border,
                highlightthickness=1
            )
            tab_container.pack(side="left", padx=(0, 1), pady=(0, 1))

            tab_button = tk.Button(
                tab_container,
                text=title,
                relief=tk.FLAT,
                bg=tab_bg,
                fg=fg,
                activebackground=active_bg,
                activeforeground=fg,
                font=("Consolas", 9, "bold"),
                command=lambda path=file_path: self.switch_tab(path)
            )
            tab_button.pack(side="left")

            close_button = tk.Button(
                tab_container,
                text="x",
                width=2,
                relief=tk.FLAT,
                bg=close_bg,
                fg=fg,
                activebackground=active_bg,
                activeforeground=fg,
                font=("Consolas", 9, "bold"),
                command=lambda path=file_path: self.close_tab(path)
            )
            close_button.pack(side="left")

    def close_tab(self, file_path):
        file_path = os.path.abspath(file_path)
        tab = self.open_tabs.get(file_path)

        if not tab:
            return

        if file_path == self.editor.current_file:
            self.save_current_tab_state()
        else:
            self.remember_tab(file_path, tab["content"])

        try:
            tab_index = self.tab_order.index(file_path)
        except ValueError:
            tab_index = 0

        self.open_tabs.pop(file_path, None)

        if file_path in self.tab_order:
            self.tab_order.remove(file_path)

        if not self.tab_order:
            self.editor.current_file = None
            self.editor.undo_stack = [""]
            self.editor.redo_stack = []
            self.editor.text_area.delete("1.0", tk.END)
            self.editor.update_analytics()
            self.editor.refresh_tabs()
            self.editor.logger.log("CLOSE_TAB: " + file_path)
            return

        if file_path == self.editor.current_file:
            next_index = min(tab_index, len(self.tab_order) - 1)
            next_file = self.tab_order[next_index]
            self.editor.current_file = None
            self.switch_tab(next_file)
        else:
            self.editor.refresh_tabs()

        self.editor.logger.log("CLOSE_TAB: " + file_path)

    def rename_tab(self, old_path, new_path):
        old_path = os.path.abspath(old_path)
        new_path = os.path.abspath(new_path)

        if old_path in self.open_tabs:
            self.open_tabs[new_path] = self.open_tabs.pop(old_path)
            self.open_tabs[new_path]["title"] = os.path.basename(new_path)

        if old_path in self.tab_order:
            self.tab_order[self.tab_order.index(old_path)] = new_path

        if self.editor.current_file == old_path:
            self.editor.current_file = new_path

        self.editor.refresh_tabs()

    def remove_tab(self, file_path):
        file_path = os.path.abspath(file_path)
        self.open_tabs.pop(file_path, None)

        if file_path in self.tab_order:
            self.tab_order.remove(file_path)

        if not self.tab_order:
            self.editor.current_file = None
            self.editor.undo_stack = [""]
            self.editor.redo_stack = []
            self.editor.text_area.delete("1.0", tk.END)
            self.editor.update_analytics()
            self.editor.refresh_tabs()
            return

        next_file = self.tab_order[-1]
        self.editor.current_file = None
        self.switch_tab(next_file)
