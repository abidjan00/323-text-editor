import re
from tkinter import messagebox

try:
    import language_tool_python
except ImportError:
    language_tool_python = None


COMMON_FIXES = {
    "teh": "the",
    "recieve": "receive",
    "seperate": "separate",
    "definately": "definitely",
    "occured": "occurred",
    "becuase": "because",
    "dont": "don't",
    "cant": "can't",
    "wont": "won't",
    "im": "I'm",
}


def register(editor, plugin_manager):
    def clear_grammar_marks():
        editor.text_area.tag_remove("grammar_error", "1.0", "end")
        editor.logger.log("PLUGIN_GRAMMAR_MARKS_CLEARED")

    def clear_marks_after_edit(event=None):
        clear_grammar_marks()

    def mark_range(start, end):
        editor.text_area.tag_add("grammar_error", start, end)

    def check_with_languagetool(content):
        if language_tool_python is None:
            return None

        with language_tool_python.LanguageTool("en-US") as tool:
            matches = tool.check(content)
            issues = []

            for match in matches:
                start = f"1.0+{match.offset}c"
                end = f"1.0+{match.offset + match.errorLength}c"
                mark_range(start, end)

                replacement = ""
                if match.replacements:
                    replacement = " -> " + match.replacements[0]

                issues.append(match.message + replacement)

        return issues

    def auto_fix_grammar():
        clear_grammar_marks()
        content = editor.get_editor_content()

        if language_tool_python is None:
            messagebox.showinfo(
                "Grammar Checker",
                "Auto fix needs language_tool_python installed."
            )
            editor.logger.log("PLUGIN_GRAMMAR_FIX_MISSING_LANGUAGETOOL")
            return

        try:
            with language_tool_python.LanguageTool("en-US") as tool:
                fixed_content = tool.correct(content)
        except Exception as error:
            messagebox.showerror(
                "Grammar Checker",
                f"Could not auto fix grammar.\n\n{error}"
            )
            editor.logger.log("PLUGIN_GRAMMAR_FIX_ERROR: " + str(error))
            return

        editor.text_area.delete("1.0", "end")
        editor.text_area.insert("end", fixed_content)
        editor.lifo.capture_state()
        editor.update_analytics()
        editor.logger.log("PLUGIN_GRAMMAR_AUTO_FIX")
        messagebox.showinfo("Grammar Checker", "Grammar auto fix completed.")

    def check_with_basic_rules(content):
        issues = []

        for wrong, correct in COMMON_FIXES.items():
            pattern = r"\b" + re.escape(wrong) + r"\b"

            for match in re.finditer(pattern, content, flags=re.IGNORECASE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                mark_range(start, end)
                issues.append(f"{match.group()} -> {correct}")

        repeated_word_pattern = r"\b(\w+)\s+\1\b"

        for match in re.finditer(repeated_word_pattern, content, flags=re.IGNORECASE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            mark_range(start, end)
            issues.append(f"Repeated word: {match.group()}")

        return issues

    def check_grammar():
        clear_grammar_marks()
        content = editor.get_editor_content()

        editor.text_area.tag_config(
            "grammar_error",
            underline=True,
            foreground="#c62828"
        )

        try:
            issues = check_with_languagetool(content)
        except Exception as error:
            issues = None
            editor.logger.log("PLUGIN_LANGUAGETOOL_ERROR: " + str(error))

        if issues is None:
            issues = check_with_basic_rules(content)

        if not issues:
            messagebox.showinfo("Grammar Checker", "No common grammar issues found.")
            editor.logger.log("PLUGIN_GRAMMAR_CHECK_CLEAR")
            return

        message = "\n".join(issues[:12])

        if len(issues) > 12:
            message += f"\n...and {len(issues) - 12} more"

        messagebox.showinfo("Grammar Checker", message)
        editor.logger.log(f"PLUGIN_GRAMMAR_CHECK: {len(issues)} issues")

    if not getattr(editor, "grammar_checker_bound", False):
        editor.text_area.bind("<KeyPress>", clear_marks_after_edit, add="+")
        editor.grammar_checker_bound = True

    plugin_manager.add_command("Check Grammar (Beta)", check_grammar)
    plugin_manager.add_command("Clear Grammar Marks", clear_grammar_marks)
