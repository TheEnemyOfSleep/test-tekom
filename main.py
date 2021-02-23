import aiolog
import datetime
import aiohttp
import asyncio
from asyncio.exceptions import CancelledError
from utils import Arguments, LoggerValidation


async def check_request(site):
    url = dict(url=site)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(site) as r:
                if r.status >= 200 and r.status < 300:
                    logger.info('available', extra=url)
                else:
                    logger.error('not available', extra=url)
        except (aiohttp.ClientConnectorError, aiohttp.ClientConnectorError):
            logger.error('not available', extra=url)


async def main(resourse):
    next_time = datetime.datetime.now() + datetime.timedelta(seconds=args.interval)
    if isinstance(resourse, list):
        for site in resourse:
            await check_request(site)
    while next_time > datetime.datetime.now():
        # Tick of timer
        await asyncio.sleep(1)
    else:
        await main(resourse)


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