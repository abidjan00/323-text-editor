import os
from tkinter import filedialog, messagebox


class FileOperations:
    def __init__(self, editor):
        self.editor = editor

    def load_file(self, file_path):
        file_path = os.path.abspath(file_path)

        if file_path in self.editor.tab_manager.open_tabs:
            self.editor.switch_tab(file_path)
            return

        self.editor.save_current_tab_state()

        if self.editor.memory.has(file_path):
            content = self.editor.memory.get(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

        self.editor.tab_manager.create_tab(file_path, content)
        self.editor.logger.log("OPEN_FILE: " + file_path)

    def open_file(self):
        file_path = filedialog.askopenfilename()

        if not file_path:
            self.editor.logger.log("OPEN_FILE_CANCELLED")
            return

        self.load_file(file_path)

    def save_file(self):
        content = self.editor.get_editor_content()

        if self.editor.current_file:
            with open(self.editor.current_file, "w", encoding="utf-8") as f:
                f.write(content)

            self.editor.save_current_tab_state()
            self.editor.logger.log("SAVE_FILE: " + self.editor.current_file)
            return

        path = filedialog.asksaveasfilename()

        if path:
            path = os.path.abspath(path)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            self.editor.tab_manager.create_tab(path, content)
            self.editor.logger.log("SAVE_FILE: " + path)
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
