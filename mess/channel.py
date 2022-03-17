class Channel:
    def __init__(self, identity: int, name: str):
        self.identity = identity
        self.name = name

    def __repr__(self):
        return f'<Channel {self.identity} "{self.name}">'

