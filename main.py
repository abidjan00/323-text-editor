import tkinter as tk
from tkinter import filedialog

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Monkey 1.0.0")
        self.root.geometry("800x600")

        # state system
        self.undo_stack = [""]
        self.redo_stack = []

        self.current_file = None

        # text area
        self.text_area = tk.Text(root, wrap="word")
        self.text_area.pack(expand=True, fill="both")

        # IMPORTANT: capture edits safely
        self.text_area.bind("<KeyRelease>", self.capture_state)

        # keyboard shortcuts (MUST return None-safe)
        self.root.bind("<Control-z>", self.undo_event)
        self.root.bind("<Control-y>", self.redo_event)

        # menu
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=edit_menu)

        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

    # ---------------- STATE CAPTURE ----------------
    def capture_state(self, event=None):
        current = self.text_area.get(1.0, tk.END).rstrip()

        if self.undo_stack[-1] == current:
            return

        self.undo_stack.append(current)
        self.redo_stack.clear()

        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)

    # ---------------- UNDO CORE ----------------
    def undo(self):
        if len(self.undo_stack) > 1:
            current = self.text_area.get(1.0, tk.END).rstrip()
            self.redo_stack.append(current)

            self.undo_stack.pop()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.undo_stack[-1])

    # event wrapper (CRITICAL)
    def undo_event(self, event):
        self.undo()
        return "break"

    # ---------------- REDO CORE ----------------
    def redo(self):
        if self.redo_stack:
            current = self.text_area.get(1.0, tk.END).rstrip()
            self.undo_stack.append(current)

            next_state = self.redo_stack.pop()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, next_state)

    # event wrapper (CRITICAL)
    def redo_event(self, event):
        self.redo()
        return "break"

    # ---------------- FILE OPS ----------------
    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)

            self.undo_stack = [content]
            self.redo_stack.clear()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.text_area.get(1.0, tk.END))
        else:
            path = filedialog.asksaveasfilename()
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get(1.0, tk.END))
                self.current_file = path


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()