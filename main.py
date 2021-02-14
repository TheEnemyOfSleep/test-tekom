import os
import sys
import json
import time
import logging
import requests
import argparse
from datetime import datetime, timedelta
from typing import Any
from dotenv import load_dotenv

from handlers import (
                    TlsSMTPHandler,
                    TelegramHandler
                    )


# Get environment variable
load_dotenv()
# Email variables
MAIL_HOST = (os.getenv('MAIL_HOST'), int(os.getenv('MAIL_PORT')))
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
EMAIL_FROM_ADDRES = os.getenv('EMAIL_FROM_ADDRES')
if os.getenv('EMAIL_TO_ADDRES'):
    EMAIL_TO_ADDRES = os.getenv('EMAIL_TO_ADDRES').split(' ')
else:
    EMAIL_TO_ADDRES = os.getenv('EMAIL_TO_ADDRES')

# Telegram variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# Set parses for tests
parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
interval = parser.add_argument('-i', '--interval',
                                type=int,
                                default=18000,
                                help=r'interval of the timer by seconds')
telegram = parser.add_argument('--telegram', 
                    type=json.loads,
                    help=r"""
                    set telegram parameters like: 
                    '{
                        "token": "mytoken",
                        "channel_id": -1234556789123
                    }' in windows use \" for double quotes
                    or use dotenv file""")
smtp_arg = parser.add_argument('--smtp',
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

data_group = parser.add_mutually_exclusive_group(required=True)
data_group.add_argument('-f', '--file', type=str, help=r'json file with resourses')
data_group.add_argument('-d', '--data', nargs='+', help=r'list data with resourses')

args = parser.parse_args()


# Logging
logging.basicConfig(filename='script.log',
                    level=logging.INFO, format='[%(asctime)s] - %(url)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger('urllib3').setLevel('CRITICAL')


# Console logging
log_console_format = '[%(asctime)s] - %(url)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_console_format))

logger.addHandler(console_handler)

# Email handler
log_mail_format = '[%(asctime)s] - %(url)s - %(message)s'
if  all([MAIL_HOST, EMAIL_LOGIN, SECRET_PASSWORD, EMAIL_FROM_ADDRES, EMAIL_TO_ADDRES]) or \
    (args.smtp and all(key in args.smtp for key in ['mailhost', 'fromaddr', 'toaddrs',
                                                    'subject', 'credentials'])):
    email_handler = TlsSMTPHandler(mailhost=MAIL_HOST,
                    fromaddr=EMAIL_FROM_ADDRES,
                    toaddrs=EMAIL_TO_ADDRES,
                    subject="Ошибка в скрипте, ресурс недоступен!",
                    credentials=(EMAIL_LOGIN, SECRET_PASSWORD),
                    secure=())
    email_handler.setLevel(logging.ERROR)
    email_handler.setFormatter(logging.Formatter(log_mail_format))

    logger.addHandler(email_handler)
elif args.smtp:
    raise argparse.ArgumentError(smtp_arg,"""
                                ArgumentError: argument would has keys: 
                                (mailhost, fromaddr, toaddrs, subject, credentials)
                                or use .env file with
                                MAIL_HOST, EMAIL_LOGIN, SECRET_PASSWORD,
                                EMAIL_FROM_ADDRES and EMAIL_TO_ADDRES variables
                                """)
# Telegram handler
if all([TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID]) or \
    (args.telegram and all(key in args.telegram for key in ['token', 'channel_id'])):

    log_telegram_format ='Ошибка в скрипте, ресурс недоступен!\n[%(asctime)s] - %(url)s - %(message)s'
    telegram_handler = TelegramHandler(TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID)
    telegram_handler.setLevel(logging.ERROR)
    telegram_handler.setFormatter(logging.Formatter(log_telegram_format))

    logger.addHandler(telegram_handler)
elif args.telegram:
    raise argparse.ArgumentError(telegram,
                                'ArgumentError: argument would has keys: token and channel_id \
                                or use .env file with TELEGRAM_TOKEN and TELEGRAM_CHANNEL_ID variables')


class Alarm:
    def __init__(self, resourses: Any, interval: int = 10):
        self.first_time = True
        self.interval = interval
        self.set_time = datetime.min
        self.resourse = resourses
    
    def __call__(self):

        if self.first_time:
            self.first_time = False
            self.alarm()
        else:
            self.alarm()
    
    def alarm(self):
        self.current_time = datetime.now()
        time.sleep(1)
        if self.current_time > self.set_time:
            self.main()
            self.set_time = self.current_time + timedelta(seconds=self.interval)

    def check_request(self, site) -> Any:
        url = dict(url=site)
        try:
            r = requests.get(site)
            if r.status_code >= 200 and r.status_code < 300:
                logger.info('available', extra=url)
            else:
                logger.error('not available', extra=url)
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            logger.error('not available', extra=url)

    def main(self):
        if isinstance(self.resourse, list):
            for site in self.resourse:
                self.check_request(site)


if __name__ == "__main__":
    try:
        if args.file:
            with open(args.file) as json_file:
                resourse = json.load(json_file)
                resourse = list(resourse.values())
        else:
            resourse = args.data

        timer_interval = args.interval
        print(args.smtp)

        alarm = Alarm(resourse, timer_interval)

        while True:
            alarm()
    except KeyboardInterrupt:
        sys.exit(0)