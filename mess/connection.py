import typing as t
import asyncio
import logging

from .event import Event
from .driver import Driver
from .channel import Channel


logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, identity: int, name: str, driver: Driver, metadata: t.Dict[str, str]):
        self.identity = identity
        self.name = name
        self.driver = driver
        self.metadata = metadata

        self._channels: t.List[Channel] = []
        self._lock_channels = asyncio.Lock()
        self.driver.channel_added += self.add_channel

    def __repr__(self):
        return f'<Connection {self.identity} "{self.name}">'

    async def add_channel(self, channel: Channel):
        logger.info(f'Adding {channel}... {self._lock_channels}')
        async with self._lock_channels:
            self._channels.append(channel)
            logger.info(f'Added {channel} to {self}')

    async def get_channels(self):
        logger.info('Waiting for lock to be able to get them channels')
        async with self._lock_channels:
            return self._channels.copy()
