import sys
import time
import requests
from datetime import datetime, timedelta
from typing import Any

from utils import Arguments, LoggerValidation


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
        args = Arguments()
        logger = LoggerValidation(__name__, args).get_logger()
        alarm = Alarm(args.resourses, args.interval)

        while True:
            alarm()

    except KeyboardInterrupt:
        sys.exit(0)