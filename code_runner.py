import os
import subprocess
import sys
import tempfile
import threading
import tkinter as tk


class CodeRunner:
    def __init__(self, editor):
        self.editor = editor
        self.output_window = None
        self.output_text = None

    def run_python_code(self):
        code = self.editor.get_editor_content()

        if not code.strip():
            self.editor.logger.log("CODE_RUN_SKIPPED_EMPTY")
            self.show_output("No Python code to run.")
            return

        self.show_output("Running Python code...\n")
        worker = threading.Thread(target=self._run_python_worker, args=(code,), daemon=True)
        worker.start()

    def _run_python_worker(self, code):
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8"
            ) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout

            if result.stderr:
                output += ("\n" if output else "") + result.stderr

            if not output:
                output = "Program finished with no output."

            self.editor.logger.log(f"CODE_RUN_EXIT: {result.returncode}")
        except subprocess.TimeoutExpired:
            output = "Program stopped: execution took longer than 10 seconds."
            self.editor.logger.log("CODE_RUN_TIMEOUT")
        except Exception as error:
            output = f"Could not run Python code.\n\n{error}"
            self.editor.logger.log("CODE_RUN_ERROR: " + str(error))
        finally:
            if temp_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

        self.editor.root.after(0, lambda: self.show_output(output))

    def show_output(self, output):
        if not self.output_window or not self.output_window.winfo_exists():
            self.output_window = tk.Toplevel(self.editor.root)
            self.output_window.title("Python Output")
            self.output_window.geometry("650x320")

            self.output_text = tk.Text(self.output_window, wrap="word", font=("Consolas", 11))
            self.output_text.pack(expand=True, fill="both")

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)
        self.output_window.lift()
