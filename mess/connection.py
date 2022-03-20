import typing as t
import asyncio
import logging

from .event import Event
from .driver import Driver
from .channel import Channel
from .message_envelope import MessageEnvelope


logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, identity: int, name: str, driver: Driver, metadata: t.Dict[str, str]):
        self.identity = identity
        self.name = name
        self.driver = driver
        self.metadata = metadata

        self._channels: t.Dict[Channel] = {}
        self._lock_channels = asyncio.Lock()
        self.driver.channel_added += self.add_channel
        self.driver.message_received += self.route_message

    def __repr__(self):
        return f'<Connection {self.identity} "{self.name}">'

    async def add_channel(self, channel: Channel):
        logger.info(f'Adding {channel}...')
        async with self._lock_channels:
            self._channels[channel.identity] = channel
            logger.info(f'Added {channel} to {self}')

    async def get_channels(self):
        logger.info('Waiting for lock to be able to get them channels')
        async with self._lock_channels:
            return list(self._channels.values())

    async def route_message(self, message_envelope: MessageEnvelope):
        async with self._lock_channels:
            channel = self._channels.get(message_envelope.channel_id)
        if channel is None:
            logger.error(f'Got message with unknown channel {message_envelope.channel_id}')
            return
        await channel.add_message(message_envelope.message)
