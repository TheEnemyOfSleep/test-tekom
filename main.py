from asyncio.exceptions import CancelledError
import sys
import time
import requests
import aiolog
import asyncio
from utils import Arguments, LoggerValidation


async def check_request(site):
    url = dict(url=site)
    try:
        r = requests.get(site)
        if r.status_code >= 200 and r.status_code < 300:
            logger.info('available', extra=url)
        else:
            logger.error('not available', extra=url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        logger.error('not available', extra=url)


async def main(resourse):
    while True:
        if isinstance(resourse, list):
            for site in resourse:
                await check_request(site)
        await asyncio.sleep(args.interval)


if __name__ == "__main__":
    args = Arguments()
    logger = LoggerValidation(__name__, args).get_logger()

    aiolog.start()
    loop = asyncio.get_event_loop()
    task = loop.create_task(main(args.resourses))
    try:

        loop.run_until_complete(task)
        loop.run_until_complete(aiolog.stop())
    except KeyboardInterrupt:
        task.cancel()
        loop.stop()
    except CancelledError:
        pass