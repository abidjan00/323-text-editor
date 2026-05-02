import os
import tkinter as tk
from tkinter import messagebox


class AutosaveManager:
    def __init__(self, editor, autosave_file="autosave.txt", interval=5000):
        self.editor = editor
        self.autosave_file = autosave_file
        self.interval = interval

    def start(self):
        self.editor.root.after(self.interval, self.autosave)

    def autosave(self):
        try:
            self.editor.save_current_tab_state()
            content = self.editor.get_editor_content()

            with open(self.autosave_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass

        self.editor.root.after(self.interval, self.autosave)

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
            self.editor.text_area.delete("1.0", tk.END)
            self.editor.text_area.insert(tk.END, content)
            self.editor.lifo.capture_state()
            self.editor.update_analytics()
            self.editor.log("RECOVERY_LOADED")
        else:
            self.editor.log("RECOVERY_DISCARDED")
