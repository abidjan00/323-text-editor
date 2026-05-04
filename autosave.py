from pathlib import Path
import tkinter as tk
from tkinter import messagebox


class AutosaveManager:
    def __init__(self, editor, autosave_file="autosave.txt", interval=5000):
        self.editor = editor
        self.autosave_file = Path(autosave_file)
        self.interval = interval
        self.after_id = None

    def start(self):
        self.schedule_next_autosave()

    def schedule_next_autosave(self):
        self.after_id = self.editor.root.after(self.interval, self.autosave)

    def autosave(self):
        try:
            content = self.editor.get_editor_content()
            self.editor.save_current_tab_state()
            self.write_autosave(content)
        except OSError as error:
            self.log_error("AUTOSAVE_WRITE_ERROR", error)
        finally:
            self.schedule_next_autosave()

    def check_recovery(self):
        content = self.read_autosave()

        if not content or not content.strip():
            return

        if self.ask_to_recover():
            self.restore_content(content)
            self.editor.logger.log("RECOVERY_LOADED")
        else:
            self.editor.logger.log("RECOVERY_DISCARDED")

        self.clear_autosave()

    def read_autosave(self):
        if not self.autosave_file.exists():
            return ""

        try:
            return self.autosave_file.read_text(encoding="utf-8")
        except OSError as error:
            self.log_error("AUTOSAVE_READ_ERROR", error)
            return ""

    def write_autosave(self, content):
        self.autosave_file.write_text(content, encoding="utf-8")

    def clear_autosave(self):
        try:
            self.write_autosave("")
        except OSError as error:
            self.log_error("AUTOSAVE_CLEAR_ERROR", error)

    def ask_to_recover(self):
        return messagebox.askyesno(
            "Recovery",
            "Recovered unsaved session found. Restore it?"
        )

    def restore_content(self, content):
        self.editor.current_file = None
        self.editor.undo_stack = [content]
        self.editor.redo_stack = []

        self.editor.text_area.config(state=tk.NORMAL, takefocus=True)
        self.editor.text_area.delete("1.0", tk.END)
        self.editor.text_area.insert(tk.END, content)
        self.editor.text_area.mark_set(tk.INSERT, "end-1c")
        self.editor.text_area.focus_set()
        self.editor.root.after(100, self.editor.text_area.focus_force)

        self.editor.refresh_tabs()
        self.editor.update_analytics()

    def log_error(self, label, error):
        self.editor.logger.log(f"{label}: {error}")
