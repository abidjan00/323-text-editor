import tkinter as tk


class SearchManager:
    def __init__(self, editor, parent):
        self.editor = editor
        self.search_frame = tk.Frame(parent)

        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", self.search_text)

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            command=self.search_text
        )
        self.search_button.pack(side="right")

    def search_text(self, event=None):
        self.editor.text_area.tag_remove("highlight", "1.0", tk.END)

        query = self.search_entry.get()

        if not query:
            return "break"

        start = "1.0"

        while True:
            start = self.editor.text_area.search(
                query,
                start,
                stopindex=tk.END
            )

            if not start:
                break

            end = f"{start}+{len(query)}c"

            self.editor.text_area.tag_add("highlight", start, end)
            start = end

        self.editor.text_area.tag_config("highlight", background="#ffb6c1")
        return "break"

    def focus_search(self, event=None):
        if not self.search_frame.winfo_ismapped():
            self.search_frame.pack(fill="x")

        self.search_entry.focus()
        return "break"

    def toggle_search(self):
        if self.search_frame.winfo_ismapped():
            self.search_frame.pack_forget()
        else:
            self.search_frame.pack(fill="x")
            self.search_entry.focus()

    def apply_theme(self, colors):
        self.search_frame.config(bg=colors["window"])
        self.search_entry.config(
            bg=colors["field"],
            fg=colors["text"],
            insertbackground=colors["insert"],
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=colors["border"],
            font=("Consolas", 9)
        )
        self.search_button.config(
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["field"],
            activeforeground=colors["text"],
            relief=tk.RIDGE,
            bd=2,
            font=("Consolas", 9, "bold")
        )
