from os.path import join, dirname, abspath, isfile
import os
import sys
import json
import logging
import argparse
import logging.config
from typing import Any, Union


# Email variables
MAIL_HOST = (os.getenv('MAIL_HOST'), int(os.getenv('MAIL_PORT')) if os.getenv('MAIL_PORT') else None)
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
EMAIL_FROM_ADDRES = os.getenv('EMAIL_FROM_ADDRES')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT') or 'Ошибка в скрипте, ресурс недоступен!'
if os.getenv('EMAIL_TO_ADDRES'):
    EMAIL_TO_ADDRES = os.getenv('EMAIL_TO_ADDRES').split(' ')
else:
    EMAIL_TO_ADDRES = os.getenv('EMAIL_TO_ADDRES')
smtp_list = [MAIL_HOST, EMAIL_FROM_ADDRES, EMAIL_TO_ADDRES, EMAIL_LOGIN, SECRET_PASSWORD]

# Telegram variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')


def check_dict_key(arg_dict, key: str):
    try:
        return arg_dict[key]
    except (KeyError, TypeError):
        return None


# more prettify solution from https://stackoverflow.com/questions/39967787/python-argparse-in-separate-function-inside-a-class-and-calling-args-from-init
class Arguments():
    def __init__(self,
                interval: int = 18000,
                telegram: Union[str, None]=None,
                smtp: Union[str, None]=None,
                file: Union[str, None]=None,
                data: Union[list, None]=None) -> None:
        self.interval = interval
        self.telegram = telegram
        self.smtp = smtp
        self.file = file
        self.data = data
        self.pars_args()


    def pars_args(self, argv=None):
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
        self.smtp = args.smtp

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
            smtp_params['smtp']['mailhost'] = check_dict_key(self.smtp, 'mailhost') or MAIL_HOST
            smtp_params['smtp']['fromaddr'] = check_dict_key(self.smtp, 'fromaddr') or EMAIL_FROM_ADDRES
            smtp_params['smtp']['toaddrs'] = check_dict_key(self.smtp, 'toaddrs') or EMAIL_TO_ADDRES
            smtp_params['smtp']['subject'] = check_dict_key(self.smtp, 'subject') or EMAIL_SUBJECT
            smtp_params['smtp']['credentials'] = check_dict_key(self.smtp, 'email_login') or EMAIL_LOGIN,\
                check_dict_key(self.smtp, 'email_password') or SECRET_PASSWORD
        else:
            smtp_params['smtp']['mailhost'], smtp_params['smtp']['fromaddr'], smtp_params['smtp']['toaddrs'], \
            smtp_params['smtp']['subject'], smtp_params['smtp']['credentials'] = \
            MAIL_HOST, EMAIL_FROM_ADDRES, EMAIL_TO_ADDRES, EMAIL_SUBJECT, (EMAIL_LOGIN, SECRET_PASSWORD)
        
        check_smtp_params = smtp_params['smtp'].copy()
        check_smtp_params.pop('subject')
        check_smtp_params.pop('mailhost')

        if not any(list(check_smtp_params.values())):
            return None

        smtp_params['smtp']['level'] = "ERROR"
        smtp_params['smtp']['formatter'] = "standard"
        smtp_params['smtp']['class'] = "handlers.TlsSMTPHandler"
        return smtp_params


    def get_telegram_params(self) -> dict:
        telegram_params = {'telegram': {}}

        if self.telegram:
            telegram_params['telegram']['token'] = check_dict_key(self.telegram, 'token') or TELEGRAM_TOKEN
            telegram_params['telegram']['channel_id'] = check_dict_key(self.telegram, 'channel_id') or TELEGRAM_CHANNEL_ID
        else:
             telegram_params['telegram']['token'], telegram_params['telegram']['channel_id'] = TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID

        telegram_params['telegram']['level'] = "ERROR"
        telegram_params['telegram']['formatter'] = "standard"
        telegram_params['telegram']['class'] = "handlers.TelegramHandler"

        return telegram_params
# Logging
# Modified solution from https://github.com/imbolc/aiolog/blob/master/examples/utils.py

rel = lambda path: join(dirname(abspath(__file__)), path)  # noqa
sys.path.insert(0, rel('../'))


class LoggerValidation:
    def __init__(self, name: str, option_args: Arguments) -> None:
        self.option_args = option_args
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
        self.add_handlers(data, self.option_args.get_smtp_params(), 'smtp')
        self.add_handlers(data, self.option_args.get_telegram_params(), 'telegram')
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
                },
            }
            self.set_dict_config(data)
        else:
            with open(fname) as f:
                data = json.load(f)
                self.set_dict_config(data)

        return logging.getLogger(self.name)