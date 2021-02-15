import sys
import requests
from threading import Timer
from utils import Arguments, LoggerValidation


class ScriptTimer(object):
    def __init__(self, interval, function, *args, **kwargs) -> None:
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
    
    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)
    
    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True
    
    def stop(self):
        self._timer.cancel()
        self.is_running = False

def check_request(site):
    url = dict(url=site)
    try:
        r = requests.get(site)
        if r.status_code >= 200 and r.status_code < 300:
            logger.info('available', extra=url)
        else:
            logger.error('not available', extra=url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        logger.error('not available', extra=url)


def main(resourse):
    if isinstance(resourse, list):
        for site in resourse:
            check_request(site)


if __name__ == "__main__":
    try:
        args = Arguments()
        logger = LoggerValidation(__name__, args).get_logger()
        script_timer = ScriptTimer(args.interval, main, args.resourses)
        main(args.resourses)
        script_timer.start()
    except KeyboardInterrupt:
        try:
            script_timer.stop()
        except AttributeError:
            sys.exit(0)
