from datetime import datetime


def register(editor, plugin_manager):
    def insert_datetime():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        editor.text_area.insert("insert", timestamp)
        editor.lifo.capture_state()
        editor.update_analytics()
        editor.logger.log("PLUGIN_INSERT_DATETIME")

    plugin_manager.add_command("Insert Date/Time", insert_datetime)
