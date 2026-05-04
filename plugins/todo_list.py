def register(editor, plugin_manager):
    def insert_todo_list():
        template = (
            "TODO LIST\n"
            "- [ ] Task 1\n"
            "- [ ] Task 2\n"
            "- [ ] Task 3\n"
        )
        editor.text_area.insert("insert", template)
        editor.lifo.capture_state()
        editor.update_analytics()
        editor.logger.log("PLUGIN_INSERT_TODO_LIST")

    plugin_manager.add_command("Insert TODO List", insert_todo_list)
