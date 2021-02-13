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


# Set global variables
timer_interval = 18000   # default inverval = 5 hours

# Get environment variable
load_dotenv()
GMAIL_LOGIN = os.getenv('GMAIL_LOGIN')
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
GMAIL_FROM_ADDRES = os.getenv('GMAIL_FROM_ADDRES')
GMAIL_TO_ADDRES = os.getenv('GMAIL_TO_ADDRES')

# Set parses for tests
parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
parser.add_argument('-i', '--interval', type=int, help='interval of the timer by seconds')

data_group = parser.add_mutually_exclusive_group(required=True)
data_group.add_argument('-f', '--file', type=str, help='json file with resourses')
data_group.add_argument('-d', '--data', nargs='+', help='list data with resourses')

# Logging
log_console_format = '[%(asctime)s] - %(url)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_console_format))

log_mail_format = '[%(asctime)s] - %(url)s - %(message)s'
gmail_handler = TlsSMTPHandler(mailhost=('smtp.gmail.com', 587),
                fromaddr=GMAIL_FROM_ADDRES,
                toaddrs="zedavis2011@gmail.com",
                subject="Ошибка в скрипте, ресурс недоступен!",
                credentials=(GMAIL_LOGIN, SECRET_PASSWORD),
                secure=())
gmail_handler.setLevel(logging.ERROR)
gmail_handler.setFormatter(logging.Formatter(log_mail_format))

log_telegram_format ='Ошибка в скрипте, ресурс недоступен!\n[%(asctime)s] - %(url)s - %(message)s'
telegram_handler = TelegramHandler()
telegram_handler.setLevel(logging.ERROR)
telegram_handler.setFormatter(logging.Formatter(log_mail_format))


logging.basicConfig(filename='script.log', level=logging.INFO, format='[%(asctime)s] - %(url)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger('urllib3').setLevel('CRITICAL')

# Set handlers
logger.addHandler(console_handler)
logger.addHandler(gmail_handler)
logger.addHandler(telegram_handler)


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

        if isinstance(self.resourse, str):
            self.check_request(self.resourse)
        elif isinstance(self.resourse, list):
            for site in self.resourse:
                self.check_request(site)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.file:
        with open(args.file) as json_file:
            resourse = json.load(json_file)
            resourse = list(resourse.values())
    else:
        resourse = args.data

    if args.interval:
        timer_interval = args.interval

    alarm = Alarm(resourse, timer_interval)
    try:
        while True:
            alarm()
    except KeyboardInterrupt:
        sys.exit(0)