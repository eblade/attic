import typing as t
from datetime import datetime


from .attachment import Attachment


class Message:
    def __init__(self, identity: int, ts: datetime, message: str, attachments: t.List[Attachment]):
        self.identity = identity
        self.ts = ts
        self.message = message
        self.attachments = attachments

    def __repr__(self):
        return f'<Message {self.identity} {self.ts}>'

