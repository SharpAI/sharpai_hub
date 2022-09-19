import os
import time
import subprocess
import logging
import requests
from argparse import ArgumentParser
from os.path import expanduser
from shutil import which

from . import BaseSharpAICLICommand
from ..sharpai_api import SA_API
from ..utils.check_env import check_environment, get_docker_compose_arch_filename
from ..utils.screen_capture import screen_capture
from ..utils.debughelper import event
from ..utils.labelstudio import check_label_studio_access,create_labelstudio_image_classification_project

class ScreenMonitorCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        main_parser = parser.add_parser(
            "screen_monitor", help="{start,stop} screen monitor control"
        )
        subparsers = main_parser.add_subparsers(
            help="Screen monitor management"
        )
        start_parser = subparsers.add_parser(
            "start", help="start screen monitor application"
        )
        stop_parser = subparsers.add_parser(
            "stop", help="stop screen monitor application"
        )

        start_parser.set_defaults(func=lambda args: ScreenMonitorStartCommand(args))
        stop_parser.set_defaults(func=lambda args: ScreenMonitorStopCommand(args))
class BaseScreenMonitorCommands:
    def __init__(self, args):
        self.runtime_folder = expanduser("~/.sharpai/screen_monitor")
        self.args = args
        self._api = SA_API()
        self.docker_compose_path = which('docker-compose')
        self.img_dir = os.path.join(self.runtime_folder, 'images')
        self.env_path = os.path.join(self.runtime_folder,'.env')
        self.yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        self.log_path = os.path.join(self.runtime_folder,'log.txt')
        self.labelstudio_server_url = 'http://localhost:8080'

    def check_credential(self):
        pass
    def is_labelstudio_configured(self):
        if os.path.exists(self.env_path):
            self.load_env()
            return True
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
    def save_environments(self):
        with open(self.env_path, "w") as f:
            f.write(f"LABEL_STUDIO_URL=http://labelstudio:8080\n")
            f.write(f"LABEL_STUDIO_PROJECT_ID={self.labelstudio_project_id}\n")
            f.write(f"LABEL_STUDIO_TOKEN={self.labelstudio_token}\n")
        
    def helper_to_setup_labelstudio(self):
        os.makedirs(self.img_dir, exist_ok=True)
        log_handle = open(self.log_path,'a')
        print('You haven\'t configured labelstudio service, SharpAI CLI will help you go through:\
                \n- 1. Pulling latest docker images from docker-hub, time may vary depending on you network situation...')

        f = open(self.env_path,"w")
        command = f'{self.docker_compose_path} -f {self.yml_path} pull'

        output = subprocess.getoutput(command)
        print('- 2. Starting Labelstudio service', end = '')

        command = f'{self.docker_compose_path} -f {self.yml_path} up -d labelstudio'
        output = subprocess.getoutput(command)
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
            import webbrowser
            webbrowser.open(self.labelstudio_server_url)
        except Exception as e:
            pass
        print('- 4. Please land on Labelstudio UI, Screen Monitor application need Labelstudio token to save screenshots of the entire screen. ALL information will be saved LOCALLY.\n'
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
        print('- 6. Please provide a class list, for example: gaming,learning,coding')
        classes_str = input('Class list: ')
        classes = classes_str.split(',')
        
        resp = create_labelstudio_image_classification_project(self.labelstudio_server_url, self.labelstudio_token,'screen monitor', classes)
        if resp is None:
            print('Failed to create labelstudio project. Please file a bug: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        self.labelstudio_project_id = resp['id']
        self.save_environments()
        return True
    def start_screen_capture(self):

        while True:
            detector_filepath = screen_capture(self.img_dir)
            logging.debug(f'saving file to {self.img_dir}, file path in docker is {detector_filepath}')
            try:
                r = requests.post('http://localhost:3000/submit/image', json={"filename": detector_filepath, 'camera_id':'screen'})
            except requests.exceptions.ConnectionError as e:
                print('image submitting error')
                print(e)
            time.sleep(3)

class ScreenMonitorStartCommand(BaseScreenMonitorCommands):
    def run(self):
        check_environment()
        self.check_credential()

        os.makedirs(self.runtime_folder, exist_ok=True)
        docker_compose_yml = get_docker_compose_arch_filename()

        if docker_compose_yml == None:
            print('Your platform is not supported, please file an issue on github for feature request: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        if docker_compose_yml != 'docker-compose-x86.yml':
            print('Only support X86 platform, please file an issue on github for feature request: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        yml_url = f'https://raw.githubusercontent.com/SharpAI/applications/main/screen_monitor/{docker_compose_yml}'

        response=requests.get(yml_url)
        open(self.yml_path, "wb").write(response.content)

        print('The latest docker-compose.yml is downloaded')
        # print('Start to pull latest docker images, it will take a while for the first time')
        # print('When service start, please access http://localhost:8080 to access demo GUI')

        if self.is_labelstudio_configured() == False:
            if self.helper_to_setup_labelstudio() == False:
                print('Failed to set labelstudio')
                exit(-1)

        command = f'{self.docker_compose_path} -f {self.yml_path} pull'
        subprocess.getoutput(command)
        
        
        log_handle = open(self.log_path,'a')
        args = [self.docker_compose_path, '-f' , self.yml_path,'up']
        subprocess.Popen(args= args, cwd=self.runtime_folder, stdout=log_handle, stderr=log_handle)

        print('Starting screen monitor')
        event('screen monitor start')
        self.start_screen_capture()
            
class ScreenMonitorStopCommand(BaseScreenMonitorCommands):
    def run(self):
        check_environment()
        
        args = [self.docker_compose_path, '-f' , self.yml_path,'down']
        subprocess.Popen( args= args, cwd=self.runtime_folder)

