import typing as t
import asyncio
import logging

from .message import Message
from .event import Event


logger = logging.getLogger(__name__)


class Channel:
    def __init__(self, identity: int, name: str):
        self.identity = identity
        self.name = name

        self._messages: t.List[Message] = []
        self._lock_messages = asyncio.Lock()
        self.messages_added = Event()

    def __repr__(self):
        return f'<Channel {self.identity} "{self.name}">'

    async def add_message(self, message: Message):
        logger.info(f'Adding {message}...')
        async with self._lock_messages:
            self._messages.append(message)
            self.messages_added.fire(message)
            logger.info(f'Added {message} to {self}')

    async def get_messages(self):
        async with self._lock_messages:
            return self._messages.copy()

