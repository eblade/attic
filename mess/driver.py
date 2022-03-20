from abc import ABC, abstractmethod


from .event import Event


class Driver(ABC):
    def __init__(self):
        self.channel_added = Event()
        self.message_received = Event()
