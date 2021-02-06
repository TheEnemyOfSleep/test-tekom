from datetime import date, datetime, timedelta
from typing import Any
import requests
import time
import sys
import argparse
import json
import logging

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

logging.basicConfig(filename='script.log', level=logging.INFO, format='[%(asctime)s] - %(url)s - %(message)s')
logger = logging.getLogger()

logging.getLogger('urllib3').setLevel('CRITICAL')
logger.addHandler(console_handler)


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
            logger.info('available', extra=url)
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