# Copyright 2022 The SharpAI Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from getpass import getpass

class BaseSharpAICLICommand(ABC):
    @staticmethod
    @abstractmethod
    def register_subcommand(parser: ArgumentParser):
        raise NotImplementedError()

    @abstractmethod
    def run(self):
        raise NotImplementedError()

class UserCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        login_parser = parser.add_parser(
            "login", help="Log in using the same credentials as on sharpai.org"
        )
        login_parser.set_defaults(func=lambda args: LoginCommand(args))
class BaseUserCommand:
    def __init__(self, args):
        self.args = args
        #self._api = HfApi()
class LoginCommand(BaseUserCommand):
    def run(self):
        print(  # docstyle-ignore
            """
        :'######::'##::::'##::::'###::::'########::'########:::::'###::::'####:
        '##... ##: ##:::: ##:::'## ##::: ##.... ##: ##.... ##:::'## ##:::. ##::
        ##:::..:: ##:::: ##::'##:. ##:: ##:::: ##: ##:::: ##::'##:. ##::: ##::
        . ######:: #########:'##:::. ##: ########:: ########::'##:::. ##:: ##::
        :..... ##: ##.... ##: #########: ##.. ##::: ##.....::: #########:: ##::
        '##::: ##: ##:::: ##: ##.... ##: ##::. ##:: ##:::::::: ##.... ##:: ##::
        . ######:: ##:::: ##: ##:::: ##: ##:::. ##: ##:::::::: ##:::: ##:'####:
        :......:::..:::::..::..:::::..::..:::::..::..:::::::::..:::::..::....::

        """
        )
        username = input("Username: ")
        token = getpass("Password: ")
        #_login(self._api, token=token)