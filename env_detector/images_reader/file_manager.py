import os

class FileManager:
    def __init__(self, directory):
        self.directory = directory

    def get_latest_json_file(self):
        json_files = [f for f in os.listdir(self.directory) if f.endswith('.json')]
        latest_file = max(json_files, key=lambda x: os.path.getmtime(os.path.join(self.directory, x)))
        return os.path.join(self.directory, latest_file)