import time
import logging
import requests    
from screen_capture import screen_capture


img_dir = '/home/simba/AI_OS/yolov7_reid/volumes/images/'
while True:
    detector_filepath = screen_capture(img_dir)
    print(f'saving file to {img_dir}, file path in docker is {detector_filepath}')
    try:
        r = requests.post('http://localhost:3000/submit/image', json={"filename": detector_filepath, 'camera_id':'screen'})
    except requests.exceptions.ConnectionError as e:
        print('image submitting error')
        print(e)
    time.sleep(3)
