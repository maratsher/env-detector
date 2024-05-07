import os
import cv2
import numpy as np
import json


class FileManager:
    def __init__(self, directory):
        self.directory = directory

    def get_latest_json_file(self):
        json_files = [f for f in os.listdir(self.directory) if f.endswith('.json')]
        latest_file = max(json_files, key=lambda x: os.path.getmtime(os.path.join(self.directory, x)))
        return os.path.join(self.directory, latest_file)\

class JSONParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_json(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        
        # frame path    
        frame_path = data['rawImg']

        # bboxes
        bboxes = []        
        passages = data.get('passages', [])        
        for passage in passages:
            car_box = passage.get('carBox')
            if car_box is not None:
                bbox = [car_box['x_min'], car_box['y_min'], car_box['x_max'], car_box['y_max']]
                bboxes.append(bbox)
        
        return frame_path, bboxes
    

class ImageProcessor:
    def __init__(self, image_path):
        self._image_path = image_path
        self._width = 2448
        self._height = 2048

    def load_img(self):
        with open(self._image_path, 'rb') as file:
            buff = file.read()
            img_array = np.frombuffer(buff, dtype=np.uint8).reshape((self._height, self._width))

        frame = cv2.cvtColor(img_array, cv2.COLOR_BayerRG2GRAY)
        return frame
    
         

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
        self.frame = image_processor.load_img()
        
        return self.frame, self.bboxes   
    
    
imflow = ImageFlow("/Users/maratsher/Work/enviromental-detector/jsons")

frame, bboxes = imflow.get_frame()

print(frame.shape)
print(bboxes)

for (x_min, y_min, x_max, y_max) in bboxes:
    # Нарисовать прямоугольник
    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0) , 4)

# Отображение результата
cv2.imshow('Image with Bounding Boxes', frame)
cv2.waitKey(0)
cv2.destroyAllWindows()