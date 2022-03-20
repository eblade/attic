from .message import Message


class MessageEnvelope:
    def __init__(self, message: Message, channel_id: int):
        self.message = message
        self.channel_id = channel_id
