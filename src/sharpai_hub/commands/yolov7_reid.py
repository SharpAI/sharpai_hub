import os
import time
import subprocess
import logging
import requests
import webbrowser
from argparse import ArgumentParser
from os.path import expanduser
from shutil import which

from . import BaseSharpAICLICommand
from ..sharpai_api import SA_API
from ..utils.check_env import check_environment, get_docker_compose_arch_filename
from ..utils.screen_capture import screen_capture
from ..utils.debughelper import event
from ..utils.labelstudio import check_label_studio_access,create_labelstudio_image_classification_project

class Yolov7ReIDCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        main_parser = parser.add_parser(
            "yolov7_reid", help="{start,stop} yolov7 reid control"
        )
        subparsers = main_parser.add_subparsers(
            help="Yolov7 ReID"
        )
        start_parser = subparsers.add_parser(
            "start", help="start yolov7 reid application"
        )
        stop_parser = subparsers.add_parser(
            "stop", help="stop yolov7 reid application"
        )
        youtube_parser = subparsers.add_parser(
            "youtube", help="play youtube video to test REID"
        )
        screen_parser = subparsers.add_parser(
            "screen", help="capture screen and send image to test REID"
        )

        start_parser.set_defaults(func=lambda args: Yolov7ReIDStartCommand(args))
        stop_parser.set_defaults(func=lambda args: Yolov7ReIDStopCommand(args))
        youtube_parser.set_defaults(func=lambda args: Yolov7ReIDYoutubeCommand(args))
        screen_parser.set_defaults(func=lambda args: Yolov7ReIDScreenCaptureCommand(args))
class BaseYolov7ReIDCommands:
    def __init__(self, args):
        self.runtime_folder = expanduser("~/.sharpai/yolov7_reid")
        self.args = args
        self._api = SA_API()
        self.docker_compose_path = which('docker-compose')
        self.img_dir = os.path.join(self.runtime_folder,'volumes', 'images')
        self.env_path = os.path.join(self.runtime_folder,'.env')
        self.yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        self.log_path = os.path.join(self.runtime_folder,'log.txt')
        self.labelstudio_server_url = 'http://localhost:8080'
        self.first_run = True
        self.telegram_token = None

    def check_credential(self):
        pass
    def is_labelstudio_configured(self):
        if os.path.exists(self.env_path):
            try:
                self.load_env()
                self.first_run = False
                return True
            except KeyError:
                return False
        return False
    def get_env_data_as_dict(self, path: str) -> dict:
        with open(path, 'r') as f:
            return dict(tuple(line.replace('\n', '').split('=')) for line 
                        in f.readlines() if not line.startswith('#'))
    def load_env(self):
        envs = self.get_env_data_as_dict(self.env_path)
        # self.labelstudio_server_url = envs['LABEL_STUDIO_URL']
        self.labelstudio_project_id = envs['LABEL_STUDIO_PROJECT_ID']
        self.labelstudio_token = envs['LABEL_STUDIO_TOKEN']

        try:
            self.telegram_token = envs['TELEGRAM_TOKEN']
        except KeyError:
            self.telegram_token = None
    def save_environments(self):
        with open(self.env_path, "w") as f:
            f.write(f"LABEL_STUDIO_URL=http://labelstudio:8080\n")
            f.write(f"LABEL_STUDIO_PROJECT_ID={self.labelstudio_project_id}\n")
            f.write(f"LABEL_STUDIO_TOKEN={self.labelstudio_token}\n")

            if self.telegram_token != None:
                f.write(f"TELEGRAM_TOKEN={self.telegram_token}\n")
        
    def helper_to_setup_labelstudio(self):
        os.makedirs(self.img_dir, exist_ok=True)
        log_handle = open(self.log_path,'a')
        print('You haven\'t configured labelstudio service, SharpAI CLI will help you go through:\
                \n- 1. Pulling latest docker images from docker-hub, time may vary depending on you network situation...')

        f = open(self.env_path,"w")

        print('Pulling latest docker images from docker hub...')
        args = [self.docker_compose_path, '-f' , self.yml_path,'pull']
        p = subprocess.Popen(args= args, cwd=self.runtime_folder)
        p.wait()

        print('- 2. Starting Labelstudio service', end = '')

        args = [self.docker_compose_path, '-f' , self.yml_path,'up','-d','labelstudio']
        subprocess.Popen(args= args, cwd=self.runtime_folder)

        while True:
            try:
                resp = requests.get(self.labelstudio_server_url)
                print('.')
                if resp.ok == False:
                    print('Failed to start labelstudio, please file issue on https://github.com/SharpAI/DeepCamera/issues')
                    exit(-1)
                break
            except Exception as e:
                print('.',end='',flush=True)
                time.sleep(1)
                pass
        print('- 3. Opening local labelstudio server with browser, you can manually access url: http://localhost:8080 if you face any problem.')
        try:
            webbrowser.open(self.labelstudio_server_url)
        except Exception as e:
            pass
        print('- 4. Please land on Labelstudio UI http://localhost:8080, Screen Monitor application need Labelstudio token to save screenshots of the entire screen. ALL information will be saved LOCALLY.\n'
              '  - 1. In the Label Studio UI, click the user icon in the upper right.\n'
              '  - 2. Click Account & Settings.\n'
              '  - 3. Copy the access token.')
        while True:
            self.labelstudio_token = input('Labelstudio token:')
            if check_label_studio_access(self.labelstudio_server_url,self.labelstudio_token) == False:
                print('- Please check if you have correct token')
                continue
            break
        
        # print(f'- 5. Saving token into local env file: {self.env_path}')
        # print('- 6. Please provide a class list, for example: dad')
        # classes_str = input('Class list: ')
        classes = ['unknown'] # classes_str.split(',')
        
        resp = create_labelstudio_image_classification_project(self.labelstudio_server_url, self.labelstudio_token,'yolov7 reid', classes)
        if resp is None:
            print('Failed to create labelstudio project. Please file a bug: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        self.labelstudio_project_id = resp['id']

        telegram_token = input('- 5. If you want to use Telegram bot to send message to you, please input the token, otherwise, press Enter to skip:')
        if telegram_token != '':
            self.telegram_token = telegram_token
        self.save_environments()
        return True

class Yolov7ReIDStartCommand(BaseYolov7ReIDCommands):
    def run(self):
        check_environment()
        self.check_credential()

        os.makedirs(self.runtime_folder, exist_ok=True)
        docker_compose_yml = get_docker_compose_arch_filename()

        if docker_compose_yml == None:
            print('Your platform is not supported, please file an issue on github for feature request: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        yml_url = f'https://raw.githubusercontent.com/SharpAI/applications/main/yolov7_reid/{docker_compose_yml}'

        response=requests.get(yml_url)
        open(self.yml_path, "wb").write(response.content)

        print('The latest docker-compose.yml has downloaded')
        # print('Start to pull latest docker images, it will take a while for the first time')
        # print('When service start, please access http://localhost:8080 to access demo GUI')

        if self.is_labelstudio_configured() == False:
            if self.helper_to_setup_labelstudio() == False:
                print('Failed to set labelstudio')
                exit(-1)

        print('Pulling latest docker images from docker hub...')
        args = [self.docker_compose_path, '-f' , self.yml_path,'pull']
        p = subprocess.Popen(args= args, cwd=self.runtime_folder)
        p.wait()

        args = [self.docker_compose_path, '-f' , self.yml_path,'up','-d']
        subprocess.Popen(args= args, cwd=self.runtime_folder)

        print('Starting service')

        if self.first_run:
            event('yolov7_reid first run')
            print('Please follow the instruction to setup Home-Assistant: https://github.com/SharpAI/DeepCamera/blob/master/docs/connect_to_ha.md')
            time.sleep(3)
            webbrowser.open('https://github.com/SharpAI/DeepCamera/blob/master/docs/connect_to_ha.md')

        event('yolov7_reid started')

class Yolov7ReIDStopCommand(BaseYolov7ReIDCommands):
    def run(self):
        check_environment()
        args = [self.docker_compose_path, '-f' , self.yml_path,'down']
        subprocess.Popen( args= args, cwd=self.runtime_folder)
class Yolov7ReIDYoutubeCommand(BaseYolov7ReIDCommands):
    def run(self):
        video_url = input('Please provide the youtube url, for example(https://youtu.be/zPre8MgmcHY): ')
        requests.post('http://localhost:3000/submit/video_url', json={"video_url": video_url})
class Yolov7ReIDScreenCaptureCommand(BaseYolov7ReIDCommands):
    def run(self):
        while True:
            detector_filepath = screen_capture(self.img_dir)
            logging.debug(f'saving file to {self.img_dir}, file path in docker is {detector_filepath}')
            try:
                r = requests.post('http://localhost:3000/submit/image', json={"filename": detector_filepath, 'camera_id':'screen'})
                print(r.json())
            except requests.exceptions.ConnectionError as e:
                print('image submitting error')
                print(e)
            except Exception as e:
                print(f'exception: {e}')
            time.sleep(1)
