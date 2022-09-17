import os
import platform
import uuid
from PIL import ImageGrab

#The output of platform.system() is as follows:

# Linux: Linux
# Mac: Darwin
# Windows: Windows

system = platform.system()

def screen_capture(save_path):
    img = None
    try:
        if system == 'Linux':
            img = ImageGrab.grab(xdisplay="")
        else:
            img = ImageGrab.grab()
    except Exception as e:
        print(e)
        return None
    if img == None:
        return None
    rgb_img = img.convert('RGB')
    random_uuid4_str = str(uuid.uuid4())
    filename = random_uuid4_str+'.jpg'

    src_file_path = os.path.join(save_path,filename)
    rgb_img.save(src_file_path,'JPEG')
    detector_filepath = os.path.join('/opt/nvr/detector/images/', filename)

    return detector_filepath

if __name__ == '__main__':

    detector_filepath = screen_capture('/home/simba/.sharpai/screen_monitor/images/')

