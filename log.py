from datetime import datetime


class AppLogger:
    def __init__(self, log_file="log.txt"):
        self.log_file = log_file

    def log(self, action):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time}] {action}\n")
