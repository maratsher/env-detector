from env_detector.images_reader import FileManager, JSONParser, ImageProcessor

class ImageFlow():
    def __init__(self, directory):
        self.directory = directory
        self.frame = None
        self.bboxes = None

    def stop(self):
        self.running = False

    def get_frame(self):
        file_manager = FileManager(self.directory)
        json_file = file_manager.get_latest_json_file()
        json_parser = JSONParser(json_file)
        frame_path, self.bboxes = json_parser.parse_json()

        image_processor = ImageProcessor(frame_path)
        try:
            self.frame = image_processor.load_img()
        except Exception:
            self.frame = None
        
        return self.frame, self.bboxes
