from os.path import join, dirname, abspath, isfile
import os
import sys
import json
import logging
import argparse
import logging.config
from typing import Union
from dotenv import load_dotenv


# Email variables
load_dotenv()
EMAIL_HOST_NAME = os.getenv('MAIL_HOST')
EMAIL_PORT = int(os.getenv('MAIL_PORT')) if os.getenv('MAIL_PORT') else None
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
EMAIL_FROM_ADDRES = os.getenv('EMAIL_FROM_ADDRES')
USE_TLS = os.getenv('USE_TLS') or False
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT') or 'Ошибка в скрипте, ресурс недоступен!'
if os.getenv('EMAIL_TO_ADDRES'):
    EMAIL_TO_ADDRES = os.getenv('EMAIL_TO_ADDRES').split(' ')
else:
    EMAIL_TO_ADDRES = os.getenv('EMAIL_TO_ADDRES')

# Telegram variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')


def check_dict_key(arg_dict, key: str):
    try:
        return arg_dict[key]
    except (KeyError, TypeError):
        return None


# more prettify solution from https://stackoverflow.com/questions/39967787/python-argparse-in-separate-function-inside-a-class-and-calling-args-from-init
class Arguments:
    def __init__(self,
                argv: list=None,
                interval: int=18000,
                telegram: Union[str, None]=None,
                smtp: Union[str, None]=None,
                file: Union[str, None]=None,
                data: Union[list, None]=None) -> None:
        self.interval  = interval
        self.telegram  = telegram
        self.smtp      = smtp
        self.resourses = file or data
        self.pars_args(argv)


    def pars_args(self, argv: list=None):
        parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
        self.interval_obj = parser.add_argument('-i', '--interval',
                                        type=int,
                                        default=18000,
                                        help=r'interval of the timer by seconds')
        self.telegram_obj = parser.add_argument('--telegram', 
                            type=json.loads,
                            help=r"""
                            set telegram parameters like: 
                            '{
                                "token": "mytoken",
                                "channel_id": -1234556789123
                            }' in windows use \" for double quotes
                            or use dotenv file""")
        self.smtp_arg_obj = parser.add_argument('--smtp',
                            type=json.loads,
                            help=r"""
                            set smtp parameters like:
                            '{
                                "mailhost": ["smtp.email.com", 587],
                                "fromaddr": "script@example.com",
                                "toaddrs" ["toaddres@example.com"],
                                "credentials"=["youlogin.example.com", "foobar123"]
                            }' in windows use \" for double quotes
                            or use dotenv file""")

        self.data_group_obj = parser.add_mutually_exclusive_group(required=True)
        self.data_group_obj.add_argument('-f', '--file', type=str, help=r'json file with resourses')
        self.data_group_obj.add_argument('-d', '--data', nargs='+', help=r'list data with resourses')

        args = parser.parse_args(argv)

        self.interval = args.interval
        self.telegram = args.telegram
        self.smtp     = args.smtp

        if args.file:
            with open(args.file) as json_file:
                self.resourses = json.load(json_file)
                self.resourses = list(self.resourses.values())
        elif args.data:
            self.resourses = args.data
        else:
            self.resourses = ['https://github.com/', 'https://www.jenkins.io/', 'https://192.168.1.70/']


    def get_smtp_params(self) -> Union[dict, None]:
        smtp_params = {'smtp': {}}

        if self.smtp:
            smtp_params['smtp']['hostname'] = check_dict_key(self.smtp, 'hostname') or EMAIL_HOST_NAME
            smtp_params['smtp']['port'] = check_dict_key(self.smtp, 'port') or EMAIL_PORT
            smtp_params['smtp']['sender'] = check_dict_key(self.smtp, 'sender') or EMAIL_FROM_ADDRES
            smtp_params['smtp']['recipient'] = check_dict_key(self.smtp, 'recipient') or EMAIL_TO_ADDRES
            smtp_params['smtp']['subject'] = check_dict_key(self.smtp, 'subject') or EMAIL_SUBJECT
            smtp_params['smtp']['username'] = check_dict_key(self.smtp, 'username') or EMAIL_LOGIN
            smtp_params['smtp']['password'] = check_dict_key(self.smtp, 'password') or SECRET_PASSWORD
            smtp_params['smtp']['use_tls'] = check_dict_key(self.smtp, 'use_tls') or USE_TLS

        else:
            smtp_params['smtp']['hostname'], smtp_params['smtp']['port'], \
            smtp_params['smtp']['sender'], smtp_params['smtp']['recipient'], \
            smtp_params['smtp']['username'], smtp_params['smtp']['password'], \
            smtp_params['smtp']['use_tls'], smtp_params['smtp']['subject'] = \
            EMAIL_HOST_NAME, EMAIL_PORT, \
            EMAIL_FROM_ADDRES, EMAIL_TO_ADDRES, \
            EMAIL_LOGIN, SECRET_PASSWORD, \
            USE_TLS, EMAIL_SUBJECT \

        check_smtp_params = smtp_params['smtp'].copy()
        check_smtp_params.pop('subject')

        if not any(list(check_smtp_params.values())):
            return None
        else:
            smtp_params['smtp']['level'] = check_dict_key(self.smtp, 'level') or "ERROR"
            smtp_params['smtp']['formatter'] = check_dict_key(self.smtp, 'formatter') or "standard"
            # Pls don't touch this
            smtp_params['smtp']['class'] = check_dict_key(self.smtp, 'class') or "aiolog.smtp.Handler"

            return smtp_params


    def get_telegram_params(self) -> dict:
        telegram_params = {'telegram': {}}

        if self.telegram:
            telegram_params['telegram']['token'] = check_dict_key(self.telegram, 'token') or TELEGRAM_TOKEN
            telegram_params['telegram']['chat_id'] = check_dict_key(self.telegram, 'chat_id') or TELEGRAM_CHANNEL_ID
        else:
             telegram_params['telegram']['token'], telegram_params['telegram']['chat_id'] = TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID

        if not any(list(telegram_params.values())):
            return None
        else:
            telegram_params['telegram']['level'] = "ERROR"
            telegram_params['telegram']['formatter'] = "standard"
            telegram_params['telegram']['class'] = "aiolog.telegram.Handler"

            return telegram_params
 
 
# Logging
# Modified solution from https://github.com/imbolc/aiolog/blob/master/examples/utils.py
rel = lambda path: join(dirname(abspath(__file__)), path)  # noqa
sys.path.insert(0, rel('../'))


class LoggerValidation:
    def __init__(self, name: str, arguments: Arguments) -> None:
        self._arguments = arguments
        self.name = name

    def add_handlers(self, data, params: dict, hname: str) -> None:
        # If there no any of arguments then handler won't be created
        if isinstance(params, dict):
            assert all(list(params[hname].values())), \
                    ('You trie use {} extensions, ',
                    'but not set all required args'.format(hname))
            try:
                data['handlers'][hname]
            except KeyError:
                data['handlers'].update(params)
                data['loggers']['']['handlers'].append(hname)

            return data


    def set_dict_config(self, data: dict) -> None:
        self.add_handlers(data, self._arguments.get_smtp_params(), 'smtp')
        self.add_handlers(data, self._arguments.get_telegram_params(), 'telegram')
        logging.config.dictConfig(data)


    def get_logger(self) -> logging.Logger:
        fname = rel('./cfg.json')
        if not isfile(fname):
            data = {
                'version': 1,
                'formatters': {
                    'standard': {
                        'format': "[%(asctime)s] - %(url)s - %(message)s"
                    }
                },
                'handlers': {
                    'console': {
                        'class': "logging.StreamHandler",
                        'level': "DEBUG",
                        'formatter': "standard"            
                    },
                    'file': {
                        'class': "logging.FileHandler",
                        'filename': "script.log",
                        'formatter': "standard"
                    },
                },
                'loggers': {
                    '': {
                        'handlers': [
                            "console",
                            "file"
                        ],
                        'level': "DEBUG"
                    }
                }
            }
            self.set_dict_config(data)
        else:
            with open(fname) as f:
                data = json.load(f)
                self.set_dict_config(data)

        return logging.getLogger(self.name)