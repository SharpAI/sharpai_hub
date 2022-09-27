import io
import os
import subprocess
from shutil import which
import platform

def check_environment():
    check_if_docker_installed()
    check_if_docker_has_permission()
    check_if_docker_compose_installed()

def check_if_docker_installed():
    if which('docker'):
        pass
    else:
        print('docker is not installed, please install docker: https://docs.docker.com/engine/install/')
        exit(-1)
def check_if_docker_compose_installed():
    if which('docker-compose'):
        docker_compose_path = which('docker-compose')
    else:
        print('docker-compose is not installed, please install docker-compose: pip install docker-compose')
        exit(-1)
def check_if_docker_has_permission():
    output = subprocess.getoutput("docker ps")
    if 'CONTAINER ' not in output:
        print('The user has no permission to docker, please run following command to assign permission:\n')
        print('1. sudo groupadd docker')
        print('2. sudo usermod -aG docker $USER')
        print('3. newgrp docker')
        print('logout/login your account, if there\'s issue still, please reboot')
        #print(output)
        exit(-1)
def is_raspberrypi():
    if os.name != 'posix':
        return False
    chips = ('BCM2708','BCM2709','BCM2711','BCM2835','BCM2836')
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line.startswith('Hardware'):
                    _, value = line.strip().split(':', 1)
                    value = value.strip()
                    if value in chips:
                        return True
    except Exception:
        pass
    return False
def get_docker_compose_arch_filename():
    processor = platform.processor()
    # print(processor)
    arch = None
    docker_compose_yml = None
    if processor == 'x86_64':
        arch = 'x86'
        docker_compose_yml = 'docker-compose-x86.yml'
    elif processor == 'i386':
        arch = 'x86'
        docker_compose_yml = 'docker-compose-x86.yml'
    elif 'Intel64' in processor:
        arch = 'x86'
        docker_compose_yml = 'docker-compose-x86.yml'
    elif processor == 'aarch64':
        if 'tegra' in platform.platform():
            arch = 'aarch64'
            output = subprocess.getoutput("apt show nvidia-jetpack")
            version = output.split('Version: ')[1].split('.')[0:2]
            if version[0] == '4' and version[1]=='5':
                docker_compose_yml = 'docker-compose-l4t-r32.6.1.yml'
            if version[0] == '4' and version[1]=='6':
                docker_compose_yml = 'docker-compose-l4t-r32.6.1.yml'
            elif version[0] == '5' and version[1]=='0':
                docker_compose_yml = 'docker-compose-l4t-r35.1.0.yml'
        elif is_raspberrypi():
            docker_compose_yml = 'docker-compose-arm64.yml'
        else:
            print(f'Your platform dose not support yet, please file a bug: {subprocess.getoutput("apt show nvidia-jetpack")}')
            
    return docker_compose_yml
