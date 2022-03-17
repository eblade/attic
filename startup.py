import os
import asyncio
import logging

from mess.driver import Driver
from mess.connection import Connection
from mess.router import Router
from mess.channel import Channel


logger = logging.getLogger(__name__)
if os.path.exists('attic.log'):
    os.remove('attic.log')
logging.basicConfig(filename='attic.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s')


class SignalDriver(Driver):
    async def fetch_channels(self):
        logger.info('Fetching channels...')
        await asyncio.sleep(0.1)
        logger.info('Fetched channels.')
        self.channel_added.fire(Channel(1, 'test_channel'))
        logger.info('Fired an event.')
        self.channel_added.fire(Channel(2, 'another_test_channel'))
        logger.info('Fired another event.')


signal_driver = SignalDriver()
signal_connection = Connection(1, "signal", signal_driver, {})


router = Router()
router.add_connection(signal_connection)


async def startup():
    logger.info('Starting')
    await signal_driver.fetch_channels()
    logger.info('Startup done')
    await asyncio.sleep(1.0)
    logger.info('Waited a second')
    logger.info(await signal_connection.get_channels())


loop = asyncio.get_event_loop()
logger.info(f'Loop is {id(loop)}')
asyncio.run_coroutine_threadsafe(startup(), loop)
loop.run_forever()
