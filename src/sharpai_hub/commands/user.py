from argparse import ArgumentParser
from getpass import getpass
from ..sharpai_api import SharpAIFolder,SA_API

from . import BaseSharpAICLICommand

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
        self._api = SA_API()
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

        http://dp.sharpai.org:3000
        """
        )
        username = input("Username: ")
        password = getpass("Password: ")
        response = self._api.login(username,password)
        if response.ok:
            print(f"Login successful, saving token to file: {SharpAIFolder.path_token}")
            json_val = response.json()
            login_token = json_val['data']['authToken']
            userId = json_val['data']['userId']

            SharpAIFolder.save_token(login_token,username,userId)

            userInfo = SharpAIFolder.get_token()
            #print(f'user information {userInfo}')
        else:
            print(f'Login failed, server response: {response.json()}')