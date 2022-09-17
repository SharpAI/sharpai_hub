from argparse import ArgumentParser
from getpass import getpass
from ..sharpai_api import SharpAIFolder,SA_API

from . import BaseSharpAICLICommand
from ..utils.get_id import get_id

class DeviceCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        device_parser = parser.add_parser(
            "device", help="{register, unregister} management"
        )
        device_subparsers = device_parser.add_subparsers(
            help="device management command"
        )
        device_register_parser = device_subparsers.add_parser(
            "register", help="register device to sharpai hub"
        )
        device_unregister_parser = device_subparsers.add_parser(
            "unregister", help="unregister device from sharpai hub"
        )

        device_register_parser.set_defaults(func=lambda args: RegisterCommand(args))
        device_unregister_parser.set_defaults(func=lambda args: UnRegisterCommand(args))
class BaseDeviceCommand:
    def __init__(self, args):
        self.args = args
        self._api = SA_API()

class RegisterCommand(BaseDeviceCommand):
    def run(self):
        device_id = get_id().replace(':','')
        SharpAIFolder.save_device_id(device_id)

        self._api.register_device(device_id)
class UnRegisterCommand(BaseDeviceCommand):
    def run(self):
        device_id = None
        device_id = SharpAIFolder.get_device_id()

        if device_id is None:
            device_id = get_id().replace(':','')

        self._api.unregister_device(device_id)

