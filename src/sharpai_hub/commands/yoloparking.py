import os
import subprocess
import requests
from argparse import ArgumentParser
from os.path import expanduser
from shutil import which

from . import BaseSharpAICLICommand
from ..utils.debughelper import event
from ..sharpai_api import SharpAIFolder,SA_API
from ..utils.check_env import check_environment, get_docker_compose_arch_filename

class YoloParkingCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        yoloparking_parser = parser.add_parser(
            "yoloparking", help="{start,stop} yoloparking app control"
        )
        yoloparking_subparsers = yoloparking_parser.add_subparsers(
            help="device management command"
        )
        yoloparking_start_parser = yoloparking_subparsers.add_parser(
            "start", help="start yolo parking application"
        )
        yoloparking_stop_parser = yoloparking_subparsers.add_parser(
            "stop", help="stop yolo parking application"
        )

        yoloparking_start_parser.set_defaults(func=lambda args: YoloParkingStartCommand(args))
        yoloparking_stop_parser.set_defaults(func=lambda args: YoloParkingStopCommand(args))
class BaseYoloParkingCommands:
    def __init__(self, args):
        self.runtime_folder = expanduser("~/.sharpai/yoloparking")
        self.args = args
        self._api = SA_API()
        self.docker_compose_path = which('docker-compose')

    def check_credential(self):
        self.userInfo = SharpAIFolder.get_token()
        if self.userInfo is None:
            print('Please login with command: sharpai_cli login')
            exit(-1)
        device_id = SharpAIFolder.get_device_id()
        if device_id is None:
            print('Please register device with command: sharpai_cli device register')
            exit(-1)

class YoloParkingStartCommand(BaseYoloParkingCommands):
    def run(self):
        check_environment()
        self.check_credential()

        os.makedirs(self.runtime_folder, exist_ok=True)
        docker_compose_yml = get_docker_compose_arch_filename()
            
        if docker_compose_yml == None:
            print('Your platform is not supported, please file an issue on github for feature request: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        yml_url = f'https://raw.githubusercontent.com/SharpAI/applications/main/yoloparking/{docker_compose_yml}'
        env_url = 'https://raw.githubusercontent.com/SharpAI/applications/main/yoloparking/.env'
        
        yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        env_path = os.path.join(self.runtime_folder,'.env')
        
        response=requests.get(yml_url)
        open(yml_path, "wb").write(response.content)

        response=requests.get(env_url)
        open(env_path, "wb").write(response.content)

        print('Downloaded the latest docker-compose.yml')
        print('Start to pull latest docker images, it will take a while for the first time')
        print('When service start, please access http://localhost:8000 to access demo GUI')

        command = f'{self.docker_compose_path} -f {yml_path} pull'
        subprocess.getoutput(command)
        
        print('Starting DeepCamera with docker-compose')
        args = [self.docker_compose_path, '-f' , yml_path,'up']
        subprocess.Popen( args= args, cwd=self.runtime_folder)
        event('yoloparking start')
        
class YoloParkingStopCommand(BaseYoloParkingCommands):
    def run(self):
        check_environment()
        
        yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        
        args = [self.docker_compose_path, '-f' , yml_path,'down']
        subprocess.Popen( args= args, cwd=self.runtime_folder)

