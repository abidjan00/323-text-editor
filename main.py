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

        # ram simulation
        self.memory = {}
        self.memory_order = []
        self.MEMORY_LIMIT = 5

        # text area
        self.text_area = tk.Text(root, wrap="word")
        self.text_area.pack(expand=True, fill="both")
        # analytics status bar
        self.analytics_label = tk.Label(
            root,
            text="Words: 0 | Characters: 0 | Lines: 0",
            anchor="w"
        )
        self.analytics_label.pack(fill="x", side="bottom")

        self.text_area.bind("<KeyRelease>", self.on_key_event)

        # keyboard shortcuts 
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


    def on_key_event(self, event):
        self.capture_state()
        self.update_analytics()

    def log(self, action):
        from datetime import datetime

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("log.txt", "a") as f:
            f.write(f"[{time}] {action}\n")

    # state capture
    def capture_state(self, event=None):
        current = self.text_area.get(1.0, tk.END).rstrip()

        if self.undo_stack[-1] == current:
            return

        self.undo_stack.append(current)
        self.redo_stack.clear()

        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)


    # analytics update
    def update_analytics(self, event=None):
        content = self.text_area.get("1.0", "end-1c")

        words = len(content.split())
        chars = len(content)
        lines = content.count("\n") + 1

        self.analytics_label.config(
            text=f"Words: {words} | Characters: {chars} | Lines: {lines}"
    )

    # undo
    def undo(self):
        if len(self.undo_stack) > 1:
            current = self.text_area.get(1.0, tk.END).rstrip()
            self.redo_stack.append(current)

            self.undo_stack.pop()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.undo_stack[-1])

    # event wrapper
    def undo_event(self, event):
        self.undo()
        self.log("UNDO")
        return "break"

    # redo
    def redo(self):
        if self.redo_stack:
            current = self.text_area.get(1.0, tk.END).rstrip()
            self.undo_stack.append(current)

            next_state = self.redo_stack.pop()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, next_state)
            self.log("REDO")

    # event wrapper 
    def redo_event(self, event):
        self.redo()
        return "break"

    # open
    def open_file(self):
        file_path = filedialog.askopenfilename()

        if not file_path:
            self.log("OPEN_FILE_CANCELLED")
            return

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        file_name = file_path.split("/")[-1]

        # MEMORY MANAGEMENT
        if file_name not in self.memory:

            if len(self.memory_order) >= self.MEMORY_LIMIT:
                oldest = self.memory_order.pop(0)
                del self.memory[oldest]
                self.log("MEMORY_EVICT: " + oldest)

            self.memory_order.append(file_name)

        self.memory[file_name] = content

        # display file
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, content)

        self.current_file = file_path

        self.log("OPEN_FILE: " + file_path)

    # save file

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
                self.log("SAVE_FILE: " + path)


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()