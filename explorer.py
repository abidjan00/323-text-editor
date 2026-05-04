import os
import tkinter as tk


class SidebarExplorer:
    def __init__(self, editor, parent):
        self.editor = editor
        self.parent = parent
        self.explorer_path = os.path.expanduser("~")
        self.explorer_items = []

        self.sidebar_frame = tk.Frame(parent, width=180)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        header_height = getattr(editor, "top_bar_height", 34)
        self.sidebar_header = tk.Frame(self.sidebar_frame, height=header_height)
        self.sidebar_header.pack(fill="x")
        self.sidebar_header.pack_propagate(False)

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
            command=self.refresh
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

    def refresh(self):
        self.file_listbox.delete(0, tk.END)
        self.explorer_items = []
        self.sidebar_label.config(text=self.explorer_path)

        try:
            entries = os.listdir(self.explorer_path)
        except Exception as e:
            self.editor.logger.log("EXPLORER_ERROR: " + str(e))
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
            self.refresh()
        else:
            self.editor.fileops.load_file(selected_path)

        return "break"

    def go_up_folder(self):
        parent = os.path.dirname(self.explorer_path)

        if parent and parent != self.explorer_path:
            self.explorer_path = parent
            self.refresh()

    def toggle(self, visible, before_widget):
        if visible:
            self.sidebar_frame.pack(side="left", fill="y", before=before_widget)
        else:
            self.sidebar_frame.pack_forget()

    def apply_theme(self, colors):
        self.sidebar_frame.config(bg=colors["window"])
        self.sidebar_header.config(bg=colors["window"])
        self.sidebar_label.config(
            bg=colors["window"],
            fg=colors["muted"],
            font=("Consolas", 9, "bold")
        )
        self.file_listbox.config(
            bg=colors["field"],
            fg=colors["text"],
            selectbackground=colors["select"],
            selectforeground=colors["text"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=2,
            highlightbackground=colors["border"],
            font=("Consolas", 9)
        )
        self.refresh_button.config(
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["field"],
            activeforeground=colors["text"],
            relief=tk.RIDGE,
            bd=2,
            font=("Consolas", 8, "bold")
        )
        self.up_button.config(
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["field"],
            activeforeground=colors["text"],
            relief=tk.RIDGE,
            bd=2,
            font=("Consolas", 8, "bold")
        )
