#!/usr/bin/env python


from argparse import ArgumentParser
from sharpai_hub.utils.debughelper import event
from sharpai_hub.commands.user import UserCommands
from sharpai_hub.commands.device import DeviceCommands
from sharpai_hub.commands.deepcamera import DeepCameraCommands
from sharpai_hub.commands.deepcamera_local import LocalDeepCameraCommands
from sharpai_hub.commands.yoloparking import YoloParkingCommands
from sharpai_hub.commands.falldetection import FallDetectionCommands
from sharpai_hub.commands.screen_monitor import ScreenMonitorCommands
from sharpai_hub.commands.yolov7_reid import Yolov7ReIDCommands

def main():
    parser = ArgumentParser(
        "sharpai-cli", usage="sharpai-cli <command> [<args>]"
    )
    commands_parser = parser.add_subparsers(help="sharpai-cli command helpers")

    # Register commands
    UserCommands.register_subcommand(commands_parser)
    DeviceCommands.register_subcommand(commands_parser)
    DeepCameraCommands.register_subcommand(commands_parser)
    YoloParkingCommands.register_subcommand(commands_parser)
    FallDetectionCommands.register_subcommand(commands_parser)
    LocalDeepCameraCommands.register_subcommand(commands_parser)
    ScreenMonitorCommands.register_subcommand(commands_parser)
    Yolov7ReIDCommands.register_subcommand(commands_parser)

    # Let's go
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        event('wrong command format')
        exit(1)

    # Run
    service = args.func(args)
    service.run()


if __name__ == "__main__":
    main()