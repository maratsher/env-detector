import json

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
    
    
    
