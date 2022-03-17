import typing as t
from datetime import datetime


from .channel import Channel
from .attachment import Attachment


class Message:
    def __init__(self, identity: int, channel: Channel, ts: datetime, message: str, attachments: t.List[Attachment]):
        self.identity = identity
        self.channel = channel
        self.ts = ts
        self.message = message
        self.attachments = attachments
