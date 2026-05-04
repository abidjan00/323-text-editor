import os
import tkinter as tk


class AnalyticsManager:
    def __init__(self, editor):
        self.editor = editor
        self.label = tk.Label(
            editor.root,
            anchor="w"
        )

    def bind_events(self):
        self.editor.text_area.bind("<KeyRelease>", self.on_key_event)
        self.editor.text_area.bind("<ButtonRelease-1>", self.update)
        self.editor.text_area.bind("<FocusIn>", self.update)

    def pack(self):
        self.label.pack(fill="x", side="bottom")
        self.update()

    def apply_theme(self, colors):
        self.label.config(
            bg=colors["window"],
            fg=colors["muted"],
            font=("Consolas", 9, "bold")
        )

    def on_key_event(self, event=None):
        self.editor.lifo.capture_state()
        self.update()

    def update(self, event=None):
        self.label.config(text=self.get_stats_text())

    def get_stats_text(self):
        content = self.editor.get_editor_content()

        words = len(content.split())
        chars = len(content)
        lines = content.count("\n") + 1

        file_name = "Untitled"
        if self.editor.current_file:
            file_name = os.path.basename(self.editor.current_file)

        cursor_line, cursor_col = self.editor.text_area.index(tk.INSERT).split(".")
        cursor_col = int(cursor_col) + 1

        return (
            f"Words: {words} | Chars: {chars} | Lines: {lines}"
            f"    |    {file_name}    |    Ln {cursor_line}, Col {cursor_col}"
        )
