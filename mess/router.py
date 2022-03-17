import typing as t


from .connection import Connection
from .message import Message



class Router:
    def __init__(self):
        self.connections: t.Dict[str, Connection] = []

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def recieve(self, message: Message):
        pass
