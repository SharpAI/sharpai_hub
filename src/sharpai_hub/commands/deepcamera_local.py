import os
import subprocess
import requests
from argparse import ArgumentParser
from os.path import expanduser
from shutil import which
import time

from . import BaseSharpAICLICommand
from ..sharpai_api import SharpAIFolder,SA_API
from ..utils.check_env import check_environment, get_docker_compose_arch_filename
from ..utils.get_ip import get_local_ip
from ..utils.config_tools import inplace_change

class LocalDeepCameraCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        deepcamera_parser = parser.add_parser(
            "local_deepcamera", help="{start,stop} deepcamera app control"
        )
        deepcamera_subparsers = deepcamera_parser.add_subparsers(
            help="local deepcamera management command"
        )
        deepcamera_start_parser = deepcamera_subparsers.add_parser(
            "start", help="start local deepcamera"
        )
        deepcamera_stop_parser = deepcamera_subparsers.add_parser(
            "stop", help="stop local deepcamera"
        )

        deepcamera_start_parser.set_defaults(func=lambda args: LocalDeepCameraStartCommand(args))
        deepcamera_stop_parser.set_defaults(func=lambda args: LocalDeepCameraStopCommand(args))
class BaseLocalDeepCameraCommands:
    def __init__(self, args):
        self.runtime_folder = expanduser("~/.sharpai/local_deepcamera")
        self.args = args
        self._api = SA_API()
        self.docker_compose_path = which('docker-compose')

    def check_credential(self):
        self.userInfo = SharpAIFolder.get_token()
        if self.userInfo is None:
            print('Please login with command: sharpai-cli login')
            exit(-1)
        device_id = SharpAIFolder.get_device_id()
        if device_id is None:
            print('Please register device with command: sharpai-cli device register')
            exit(-1)

class LocalDeepCameraStartCommand(BaseLocalDeepCameraCommands):
    def run(self):
        check_environment()
        self.check_credential()

        os.makedirs(self.runtime_folder, exist_ok=True)
        docker_compose_yml = get_docker_compose_arch_filename()

        if docker_compose_yml != 'docker-compose-x86.yml':
            print('Local deployment only support X86 platform, if you want to run local deployment on your own device, please file an issue on github for feature request: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        yml_url = f'https://raw.githubusercontent.com/SharpAI/applications/main/deepcamera_local/{docker_compose_yml}'
        env_url = 'https://raw.githubusercontent.com/SharpAI/applications/main/deepcamera_local/.env'
        
        yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        env_path = os.path.join(self.runtime_folder,'.env')
        
        response=requests.get(yml_url)
        open(yml_path, "wb").write(response.content)

        response=requests.get(env_url)
        open(env_path, "wb").write(response.content)

        print('Downloaded the latest docker-compose.yml')
        local_ip = get_local_ip()
        print(f'Your local IP is {local_ip}, sharpai-cli is setting the configuration file for you, if the local_ip is incorrect, please file a bug or modify it manually.')
        
        inplace_change(env_path,'AWS_READABLE_PREFIX=http://minio:9000/faces/',f'AWS_READABLE_PREFIX=http://{local_ip}:9000/faces/')
        
        inplace_change(env_path,'MQTT_BROKER_ADDRESS=mqttserver',f'MQTT_BROKER_ADDRESS={local_ip}')
        time.sleep(2)
        
        print('Start to pull latest docker images, it will take a while for the first time')

        command = f'{self.docker_compose_path} -f {yml_path} pull'
        subprocess.getoutput(command)
        
        print('Starting DeepCamera with docker-compose')
        device_id = SharpAIFolder.get_device_id()
        
        print(f'Please add your device id ({device_id}) to your home on http://localhost:3000')
        print('wait for 5s for you to copy the device id.')
        time.sleep(5)
        
        args = [self.docker_compose_path, '-f' , yml_path,'up']
        subprocess.Popen( args= args, cwd=self.runtime_folder)
        
class LocalDeepCameraStopCommand(BaseLocalDeepCameraCommands):
    def run(self):
        check_environment()
        
        yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        
        args = [self.docker_compose_path, '-f' , yml_path,'down']
        subprocess.Popen( args= args, cwd=self.runtime_folder)

