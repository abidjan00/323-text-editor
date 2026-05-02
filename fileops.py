import os
import threading
from tkinter import filedialog, messagebox


class FileOperations:
    def __init__(self, editor):
        self.editor = editor

    def _run_worker(self, target, *args):
        worker = threading.Thread(target=target, args=args, daemon=True)
        worker.start()

    def _finish_load(self, file_path, content):
        self.editor.tab_manager.create_tab(file_path, content)
        self.editor.logger.log("OPEN_FILE: " + file_path)

    def _load_error(self, file_path, error):
        self.editor.logger.log("OPEN_FILE_ERROR: " + str(error))
        messagebox.showerror("Open Error", f"Could not read {file_path}\n\n{error}")

    def _read_file_async(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as error:
            self.editor.root.after(0, lambda: self._load_error(file_path, error))
            return

        self.editor.root.after(0, lambda: self._finish_load(file_path, content))

    def _save_complete(self, file_path):
        self.editor.logger.log("SAVE_FILE: " + file_path)
        self.editor.refresh_explorer()

    def _save_error(self, file_path, error):
        self.editor.logger.log("SAVE_FILE_ERROR: " + str(error))
        messagebox.showerror("Save Error", f"Could not write {file_path}\n\n{error}")

    def _write_file_async(self, file_path, content):
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
        except Exception as error:
            self.editor.root.after(0, lambda: self._save_error(file_path, error))
            return

        self.editor.root.after(0, lambda: self._save_complete(file_path))

    def load_file(self, file_path):
        file_path = os.path.abspath(file_path)

        if file_path in self.editor.tab_manager.open_tabs:
            self.editor.switch_tab(file_path)
            return

        self.editor.save_current_tab_state()

        if self.editor.memory.has(file_path):
            content = self.editor.memory.get(file_path)
            self.editor.tab_manager.create_tab(file_path, content)
            self.editor.logger.log("OPEN_FILE: " + file_path)
            return

        self.editor.logger.log("OPEN_FILE_START: " + file_path)
        self._run_worker(self._read_file_async, file_path)

    def open_file(self):
        file_path = filedialog.askopenfilename()

        if not file_path:
            self.editor.logger.log("OPEN_FILE_CANCELLED")
            return

        self.load_file(file_path)

    def save_file(self):
        content = self.editor.get_editor_content()

        if self.editor.current_file:
            self.editor.save_current_tab_state()
            self._run_worker(self._write_file_async, self.editor.current_file, content)
            return

        path = filedialog.asksaveasfilename()

        if path:
            path = os.path.abspath(path)
            self.editor.tab_manager.create_tab(path, content)
            self._run_worker(self._write_file_async, path, content)
            self.editor.refresh_explorer()

    def rename_file(self):
        if not self.editor.current_file:
            self.editor.logger.log("RENAME_FAILED_NO_FILE")
            return

        new_name = filedialog.asksaveasfilename()

        if not new_name:
            self.editor.logger.log("RENAME_CANCELLED")
            return

        try:
            self.editor.save_current_tab_state()
            old_name = self.editor.current_file
            new_name = os.path.abspath(new_name)
            os.rename(self.editor.current_file, new_name)
            self.editor.logger.log(f"RENAME: {old_name} -> {new_name}")

            self.editor.memory.rename(old_name, new_name)

            self.editor.tab_manager.rename_tab(old_name, new_name)
            self.editor.refresh_explorer()
        except Exception as e:
            self.editor.logger.log("RENAME_ERROR: " + str(e))

    def delete_file(self):
        if not self.editor.current_file:
            self.editor.logger.log("DELETE_FAILED_NO_FILE")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Delete this file?")

        if not confirm:
            self.editor.logger.log("DELETE_CANCELLED")
            return

        try:
            deleted_file = self.editor.current_file
            os.remove(deleted_file)
            self.editor.logger.log("DELETE_FILE: " + deleted_file)

            self.editor.tab_manager.remove_tab(deleted_file)
            self.editor.memory.remove(deleted_file)

            self.editor.refresh_explorer()
        except Exception as e:
            self.editor.logger.log("DELETE_ERROR: " + str(e))
