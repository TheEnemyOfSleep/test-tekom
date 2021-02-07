from datetime import date, datetime, timedelta
from typing import Any
import requests
import time
import sys
import argparse
import json
import logging
from handlers import TlsSMTPHandler
from logging.handlers import SMTPHandler
import os
from dotenv import load_dotenv

from requests import exceptions

# Set parses for tests
parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-f', '--file', type=str, help='json file with resourses')
group.add_argument('-d', '--data', nargs='+', help='list, tuple, dict data with resourses')

# Logging
log_console_format = '[%(asctime)s] - %(url)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_console_format))

load_dotenv()
GMAIL_LOGIN = os.getenv('GMAIL_LOGIN')
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')

log_mail_format = '[%(asctime)s] - %(url)s - %(message)s'
gmail_handler = TlsSMTPHandler(mailhost=('smtp.gmail.com', 587),
                fromaddr="script@example.com",
                toaddrs="zedavis2011@gmail.com",
                subject="Ошибка в скрипте, ресурс недоступен!",
                credentials=(GMAIL_LOGIN, SECRET_PASSWORD),
                secure=())
gmail_handler.setLevel(logging.ERROR)
gmail_handler.setFormatter(logging.Formatter(log_mail_format))


logging.basicConfig(filename='script.log', level=logging.INFO, format='[%(asctime)s] - %(url)s - %(message)s')
logger = logging.getLogger()

logging.getLogger('urllib3').setLevel('CRITICAL')
logger.addHandler(console_handler)

logger.addHandler(gmail_handler)


class Alarm:
    def __init__(self, resourses: Any):
        self.first_time = True
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
            self.set_time = self.current_time + timedelta(seconds=10)

    def check_request(self, site):
        url = dict(url=site)
        try:
            r = requests.get(site)
            if r.status_code >= 200 and r.status_code < 300:
                logger.info('available', extra=url)
            else:
                logger.error('not available', extra=url)
        except requests.exceptions.ConnectionError:
            logger.error('not available', extra=url)
        except requests.exceptions.HTTPError as err:
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

    alarm = Alarm(resourse)
    try:
        while True:
            alarm()
            # main(resourse)
    except KeyboardInterrupt:
        sys.exit(0)