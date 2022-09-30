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

class Yolov7PersonDetectorCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        main_parser = parser.add_parser(
            "yolov7_person_detector", help="{start,stop} yolov7 person detector"
        )
        subparsers = main_parser.add_subparsers(
            help="Yolov7 Person Detector"
        )
        start_parser = subparsers.add_parser(
            "start", help="start yolov7 person detector"
        )
        stop_parser = subparsers.add_parser(
            "stop", help="stop yolov7 person detector"
        )
        youtube_parser = subparsers.add_parser(
            "youtube", help="play youtube video to test person detector"
        )
        screen_parser = subparsers.add_parser(
            "screen", help="capture screen and send image to test REID"
        )

        start_parser.set_defaults(func=lambda args: Yolov7PersonDetectorStartCommand(args))
        stop_parser.set_defaults(func=lambda args: Yolov7PersonDetectorStopCommand(args))
        youtube_parser.set_defaults(func=lambda args: Yolov7PersonDetectorYoutubeCommand(args))
        screen_parser.set_defaults(func=lambda args: Yolov7PersonDetectorScreenCaptureCommand(args))
class BaseYolov7PersonDetectorCommands:
    def __init__(self, args):
        self.runtime_folder = expanduser("~/.sharpai/yolov7_person_detector")
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
    def is_person_detector_configured(self):
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
        try:
            self.telegram_token = envs['TELEGRAM_TOKEN']
        except KeyError:
            self.telegram_token = None
    def save_environments(self):
        with open(self.env_path, "w") as f:
            if self.telegram_token != None:
                f.write(f"TELEGRAM_TOKEN={self.telegram_token}\n")
        
    def helper_to_setup_person_detector(self):
        os.makedirs(self.img_dir, exist_ok=True)
        log_handle = open(self.log_path,'a')
        print('You haven\'t configured person detector yet, SharpAI CLI will help you go through:\
                \n- 1. Pulling latest docker images from docker-hub, time may vary depending on you network situation...')

        f = open(self.env_path,"w")

        print('Pulling latest docker images from docker hub...')
        args = [self.docker_compose_path, '-f' , self.yml_path,'pull']
        p = subprocess.Popen(args= args, cwd=self.runtime_folder)
        p.wait()

        telegram_token = input('- 2. If you want to use Telegram bot to send message to you, please input the token, otherwise, press Enter to skip:')
        if telegram_token != '':
            self.telegram_token = telegram_token
        self.save_environments()
        return True

class Yolov7PersonDetectorStartCommand(BaseYolov7PersonDetectorCommands):
    def run(self):
        check_environment()
        self.check_credential()

        os.makedirs(self.runtime_folder, exist_ok=True)
        docker_compose_yml = get_docker_compose_arch_filename()

        if docker_compose_yml == None:
            print('Your platform is not supported, please file an issue on github for feature request: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        yml_url = f'https://raw.githubusercontent.com/SharpAI/applications/main/yolov7_person_detector/{docker_compose_yml}'

        response=requests.get(yml_url)
        open(self.yml_path, "wb").write(response.content)

        print('The latest docker-compose.yml has downloaded')
        # print('Start to pull latest docker images, it will take a while for the first time')
        # print('When service start, please access http://localhost:8080 to access demo GUI')

        if self.is_person_detector_configured() == False:
            if self.helper_to_setup_person_detector() == False:
                print('Failed to setup person detector')
                exit(-1)

        print('Pulling latest docker images from docker hub...')
        args = [self.docker_compose_path, '-f' , self.yml_path,'pull']
        p = subprocess.Popen(args= args, cwd=self.runtime_folder)
        p.wait()

        args = [self.docker_compose_path, '-f' , self.yml_path,'up','-d']
        subprocess.Popen(args= args, cwd=self.runtime_folder)

        print('Starting service')
        event('yolov7_person_detector started')

class Yolov7PersonDetectorStopCommand(BaseYolov7PersonDetectorCommands):
    def run(self):
        check_environment()
        args = [self.docker_compose_path, '-f' , self.yml_path,'down']
        subprocess.Popen( args= args, cwd=self.runtime_folder)
class Yolov7PersonDetectorYoutubeCommand(BaseYolov7PersonDetectorCommands):
    def run(self):
        video_url = input('Please provide the youtube url, for example(https://youtu.be/zPre8MgmcHY): ')
        requests.post('http://localhost:3000/submit/video_url', json={"video_url": video_url})
class Yolov7PersonDetectorScreenCaptureCommand(BaseYolov7PersonDetectorCommands):
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
