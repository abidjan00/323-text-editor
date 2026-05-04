import os
import zipfile
from pathlib import Path
from tkinter import messagebox


class CompressionManager:
    def __init__(self, editor):
        self.editor = editor

    def optimize_text(self, content):
        lines = [line.rstrip() for line in content.splitlines()]

        while lines and not lines[-1]:
            lines.pop()

        optimized = "\n".join(lines)

        if len(optimized.encode("utf-8")) > len(content.encode("utf-8")):
            return content

        return optimized

    def format_size(self, size):
        if size < 1024:
            return f"{size} bytes"

        return f"{size / 1024:.2f} KB"

    def optimize_current_file(self):
        if not self.editor.current_file:
            messagebox.showinfo(
                "Optimize File",
                "Open or save a file before optimizing it."
            )
            self.editor.logger.log("OPTIMIZE_FAILED_NO_FILE")
            return

        current_path = Path(self.editor.current_file)
        content = self.editor.get_editor_content()
        optimized_content = self.optimize_text(content)
        original_size = os.path.getsize(current_path) if current_path.exists() else len(content.encode("utf-8"))

        try:
            current_path.write_text(optimized_content, encoding="utf-8")
        except OSError as error:
            self.editor.logger.log("OPTIMIZE_ERROR: " + str(error))
            messagebox.showerror(
                "Optimize File",
                f"Could not optimize file.\n\n{error}"
            )
            return

        optimized_size = current_path.stat().st_size

        self.editor.text_area.delete("1.0", "end")
        self.editor.text_area.insert("end", optimized_content)
        self.editor.undo_stack = [optimized_content]
        self.editor.redo_stack = []
        self.editor.save_current_tab_state()
        self.editor.update_analytics()

        self.editor.refresh_explorer()
        self.editor.logger.log(
            f"OPTIMIZE_FILE: {current_path} ({original_size} -> {optimized_size})"
        )
        messagebox.showinfo(
            "Optimize File",
            "File optimized successfully.\n\n"
            f"Original size: {self.format_size(original_size)}\n"
            f"Optimized size: {self.format_size(optimized_size)}"
        )

    def compress_current_file(self):
        if not self.editor.current_file:
            messagebox.showinfo(
                "Compress",
                "Open or save a file before compressing it."
            )
            self.editor.logger.log("COMPRESS_FAILED_NO_FILE")
            return

        current_path = Path(self.editor.current_file)
        zip_path = current_path.with_name(current_path.stem + "_compressed.zip")
        content = self.editor.get_editor_content()
        optimized_content = self.optimize_text(content)
        optimized_bytes = optimized_content.encode("utf-8")
        archive_file_name = current_path.stem + "_compressed" + current_path.suffix

        try:
            with zipfile.ZipFile(
                zip_path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9
            ) as zip_file:
                zip_file.writestr(archive_file_name, optimized_bytes)
        except OSError as error:
            self.editor.logger.log("COMPRESS_ERROR: " + str(error))
            messagebox.showerror(
                "Compress",
                f"Could not compress file.\n\n{error}"
            )
            return

        original_size = os.path.getsize(current_path) if current_path.exists() else len(content.encode("utf-8"))
        optimized_size = len(optimized_bytes)
        compressed_size = zip_path.stat().st_size

        self.editor.refresh_explorer()
        self.editor.logger.log(
            f"COMPRESS_FILE: {current_path} -> {zip_path} "
            f"({original_size} -> {optimized_size} -> {compressed_size})"
        )
        messagebox.showinfo(
            "Compress",
            "Optimized ZIP created successfully.\n\n"
            f"Original size: {self.format_size(original_size)}\n"
            f"Optimized in ZIP: {self.format_size(optimized_size)}\n"
            f"ZIP size: {self.format_size(compressed_size)}"
        )
