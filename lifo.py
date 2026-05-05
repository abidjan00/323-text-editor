import tkinter as tk


class LifoManager:
    def __init__(self, editor, max_states=100):
        self.editor = editor
        self.max_states = max_states

    def capture_state(self, event=None):
        current = self.editor.get_editor_content()

        if self.editor.undo_stack[-1] == current:
            return

        self.editor.undo_stack.append(current)
        self.editor.redo_stack.clear()

        if len(self.editor.undo_stack) > self.max_states:
            self.editor.undo_stack.pop(0)

        tab = self.editor.current_tab()

        if tab:
            tab["content"] = current
            tab["undo_stack"] = self.editor.undo_stack
            tab["redo_stack"] = self.editor.redo_stack
            self.editor.memory.remember(self.editor.current_file, current)

    def undo(self):
        if len(self.editor.undo_stack) <= 1:
            return

        current = self.editor.get_editor_content()
        self.editor.redo_stack.append(current)

        self.editor.undo_stack.pop()

        self.editor.text_area.delete("1.0", tk.END)
        self.editor.text_area.insert(tk.END, self.editor.undo_stack[-1])
        self.editor.save_current_tab_state()
        self.editor.update_analytics()
        self.editor.logger.log("UNDO")

    def redo(self):
        if not self.editor.redo_stack:
            return

        next_state = self.editor.redo_stack.pop()
        self.editor.undo_stack.append(next_state)

        self.editor.text_area.delete("1.0", tk.END)
        self.editor.text_area.insert(tk.END, next_state)
        self.editor.save_current_tab_state()
        self.editor.update_analytics()
        self.editor.logger.log("REDO")

    def undo_event(self, event=None):
        self.undo()
        return "break"

    def redo_event(self, event=None):
        self.redo()
        return "break"
