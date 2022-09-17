from gettext import gettext
import os
from os.path import expanduser
import json
from typing import BinaryIO, Dict, Iterable, Iterator, List, Optional, Tuple, Union
import requests

class SA_API:
    def __init__(self):
        self.server='http://dp.sharpai.org:3000'

    def login(self,username,password):
        request_url = self.server + '/api/v1/login'
        result = requests.post(request_url, data={'username': username,'password':password})
        return result

    def get_group_id(self,userInfo):
        request_url = self.server + '/api/v1/groups'
        response = requests.get(request_url, params={'groupName': 'home', 'creator': userInfo['username']})
        if response.ok:
            groupId = response.json()['_id']
            SharpAIFolder.save_group_id(groupId)
            return groupId
        print(f'Get group ID failed, server response {response.json()}')
        return None

    def register_device(self,deviceId):
        userInfo = SharpAIFolder.get_token()
        if userInfo is None:
            print('Please login first: sharpai_cli login')
            return
        group_id = self.get_group_id(userInfo)

        request_url = self.server + '/api/v1/groups/'+group_id+'/devices'
        headers = {
            'X-User-Id': userInfo['userId'],
            'X-Auth-Token': userInfo['token']
        }
        device_name = input('Please input the device name:')
        data = {
            'uuid':deviceId,
            'deviceName': device_name,
            'type':'in'
        }
        response = requests.post(request_url,headers=headers,data=data)

        if response.ok:
            print('Device successfully added')
        else:
            print(f'{response.status_code}')
            print(f'Add device failed, server response: {response.content}')

    def unregister_device(self,device_id):
        userInfo = SharpAIFolder.get_token()
        if userInfo is None:
            print('Please login first: sharpai_cli login')
            return
        request_url = self.server + '/api/v1/devices/' + device_id
        headers = {
            'X-User-Id': userInfo['userId'],
            'X-Auth-Token': userInfo['token']
        }

        response = requests.delete(request_url,headers=headers)

        if response.ok:
            print('Device successfully deleted')
            print(f'{response.json()}')
        else:
            print(f'{response.status_code}')
            print(f'Delete device failed, server response: {response.content}')
        
class SharpAIFolder:
    path_token = expanduser("~/.sharpai/token.json")
    path_device_id = expanduser("~/.sharpai/device_id")
    path_group_id = expanduser("~/.sharpai/group_id")
    path_token_env = expanduser("~/.sharpai/token.env")
    @classmethod
    def save_group_id(cls, groupId):
        """
        Save token, creating folder as needed.

        Args:
            deviceId (`str`):
                The device to save to the [`SharpAIFolder`]
        """
        os.makedirs(os.path.dirname(cls.path_group_id), exist_ok=True)

        with open(cls.path_group_id, "w+") as f:
            f.write(groupId)
    @classmethod
    def save_device_id(cls, deviceId):
        """
        Save token, creating folder as needed.

        Args:
            deviceId (`str`):
                The device to save to the [`SharpAIFolder`]
        """
        os.makedirs(os.path.dirname(cls.path_device_id), exist_ok=True)

        with open(cls.path_device_id, "w+") as f:
            f.write(deviceId)
    @classmethod
    def get_device_id(cls):
        """
        Save token, creating folder as needed.

        Args:
            deviceId (`str`):
                The device to save to the [`SharpAIFolder`]
        """
        device_id = None
        try:
            with open(cls.path_device_id, "r") as f:
                device_id = f.read()
        except:
            pass
        return device_id

    @classmethod
    def save_token(cls, token, username, userId):
        """
        Save token, creating folder as needed.

        Args:
            token (`str`):
            username (`str`):
            userId (`str`):
                The user credentials to save to the [`SharpAIFolder`]
        """
        os.makedirs(os.path.dirname(cls.path_token), exist_ok=True)

        userInfo = {
            'username':username,
            'userId':userId,
            'token':token
        }
        with open(cls.path_token, "w+") as f:
            json.dump(userInfo,f)
        tokenEnv = 'SHARP_AI_TOKEN={}\nSHARP_AI_USER_ID={}\nSHARP_AI_USERNAME={}\n'.format(token,userId,username)
        with open(cls.path_token_env, "w+") as f:
            f.write(tokenEnv)

    @classmethod
    def get_token(cls) -> Optional[Dict]:
        """
        Get token or None if not existent.

        Returns:
            `Dict` or `None`: The token, `None` if it doesn't exist.

        """
        userInfo = None
        try:
            with open(cls.path_token, "r") as f:
                userInfo = json.load(f)
        except FileNotFoundError:
            pass
        return userInfo

    @classmethod
    def delete_token(cls):
        """
        Deletes the token from storage. Does not fail if token does not exist.
        """
        try:
            os.remove(cls.path_token)
        except FileNotFoundError:
            pass

