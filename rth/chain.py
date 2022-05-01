import typing
from .state import State


class Chain:
    def __init__(self, state: State, persistance: typing.Optional[typing.TextIO] = None):
        self.state = state
        self.events = []
        self.persistance = persistance
        self.loaded = False

    def load_previous(self):
        if self.persistance is None:
            self.loaded = True
            return
        self.persistance.seek(0)
        for line in self.persistance.readlines():
            instruction, thing = line.strip().split(maxsplit=1)
            if instruction == 'a':
                self.add_thing(thing)
            elif instruction == 'r':
                self.remove_thing(thing)
            else:
                raise ValueError(f'Unrecognized instruction: "{instruction}"')
        self.loaded = True

    def store(self, instruction, data):
        if not self.loaded:
            return
        if self.persistance is None:
            return
        self.persistance.write(f'{instruction} {data}\n')

    def add_thing(self, thing: str):
        self.state.add(thing)
        self.store('a', thing)

    def remove_thing(self, thing: str):
        self.state.remove(thing)
        self.store('r', thing)
