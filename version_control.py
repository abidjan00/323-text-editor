import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


class VersionControlManager:
    def __init__(self, editor, version_folder=".versions"):
        self.editor = editor
        self.version_folder = Path(version_folder)
        self.version_folder.mkdir(exist_ok=True)

    def safe_file_name(self, file_path):
        absolute_path = os.path.abspath(file_path)
        safe_name = absolute_path.replace(":", "").replace("\\", "__").replace("/", "__")
        return safe_name

    def create_snapshot(self, file_path, content):
        if not file_path:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = self.safe_file_name(file_path)
        snapshot_path = self.version_folder / f"{safe_name}_{timestamp}.txt"

        try:
            snapshot_path.write_text(content, encoding="utf-8")
            self.editor.logger.log(f"VERSION_SNAPSHOT: {file_path} -> {snapshot_path}")
        except OSError as error:
            self.editor.logger.log("VERSION_SNAPSHOT_ERROR: " + str(error))

    def list_versions(self, file_path):
        safe_name = self.safe_file_name(file_path)
        versions = []

        for snapshot_path in self.version_folder.glob(f"{safe_name}_*.txt"):
            timestamp = snapshot_path.stem.replace(safe_name + "_", "")
            versions.append((timestamp, snapshot_path))

        return sorted(versions, reverse=True)

    def snapshot_current_file(self):
        if not self.editor.current_file:
            messagebox.showinfo("Version Control", "Save the file first before creating a version.")
            self.editor.logger.log("VERSION_SNAPSHOT_FAILED_NO_FILE")
            return

        content = self.editor.get_editor_content()
        self.create_snapshot(self.editor.current_file, content)
        messagebox.showinfo("Version Control", "Snapshot saved.")

    def show_restore_window(self):
        if not self.editor.current_file:
            messagebox.showinfo("Version Control", "Open or save a file before restoring versions.")
            self.editor.logger.log("VERSION_RESTORE_FAILED_NO_FILE")
            return

        versions = self.list_versions(self.editor.current_file)

        if not versions:
            messagebox.showinfo("Version Control", "No saved versions found for this file.")
            self.editor.logger.log("VERSION_RESTORE_FAILED_EMPTY")
            return

        window = tk.Toplevel(self.editor.root)
        window.title("Restore Version")
        window.geometry("420x300")

        label = tk.Label(window, text="Select a version to restore:", anchor="w")
        label.pack(fill="x", padx=10, pady=(10, 5))

        listbox = tk.Listbox(window)
        listbox.pack(expand=True, fill="both", padx=10)

        for timestamp, snapshot_path in versions:
            display_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S_%f").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            listbox.insert(tk.END, display_time)

        def restore_selected():
            selected = listbox.curselection()

            if not selected:
                return

            snapshot_path = versions[selected[0]][1]
            self.restore_version(snapshot_path)
            window.destroy()

        restore_button = tk.Button(window, text="Restore", command=restore_selected)
        restore_button.pack(pady=10)

    def restore_version(self, snapshot_path):
        try:
            content = snapshot_path.read_text(encoding="utf-8")
        except OSError as error:
            self.editor.logger.log("VERSION_RESTORE_ERROR: " + str(error))
            messagebox.showerror("Version Control", f"Could not restore version.\n\n{error}")
            return

        self.editor.text_area.delete("1.0", tk.END)
        self.editor.text_area.insert(tk.END, content)
        self.editor.undo_stack = [content]
        self.editor.redo_stack = []
        self.editor.save_current_tab_state()
        self.editor.fileops._run_worker(
            self.editor.fileops._write_file_async,
            self.editor.current_file,
            content
        )
        self.editor.update_analytics()
        self.editor.text_area.focus_set()
        self.editor.logger.log(f"VERSION_RESTORE: {snapshot_path}")
        messagebox.showinfo("Version Control", "Version restored.")
