class MemoryManager:
    def __init__(self, logger, limit=5):
        self.logger = logger
        self.limit = limit
        self.files = {}
        self.order = []

    def remember(self, file_path, content):
        if file_path in self.order:
            self.order.remove(file_path)
        elif len(self.order) >= self.limit:
            oldest = self.order.pop(0)
            self.files.pop(oldest, None)
            self.logger.log("MEMORY_EVICT: " + oldest)

        self.order.append(file_path)
        self.files[file_path] = content

    def has(self, file_path):
        return file_path in self.files

    def get(self, file_path):
        return self.files[file_path]

    def rename(self, old_path, new_path):
        if old_path in self.files:
            self.files[new_path] = self.files.pop(old_path)

        if old_path in self.order:
            self.order[self.order.index(old_path)] = new_path

    def remove(self, file_path):
        self.files.pop(file_path, None)

        if file_path in self.order:
            self.order.remove(file_path)
