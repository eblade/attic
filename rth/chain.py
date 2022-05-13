import logging
import typing
from .state import State


logger = logging.getLogger(__name__)


class Chain:
    def __init__(self, state: State, persistance: typing.Optional[typing.TextIO] = None):
        self.state = state
        self.events = []
        self.persistance = persistance
        self.loaded = False
        logger.debug('Chain initialized')

    def load_previous(self):
        if self.persistance is None:
            self.loaded = True
            logger.info('There is no persistence set up')
            return
        self.persistance.seek(0)
        for line in self.persistance.readlines():
            instruction, rest = line.strip().split('\t', maxsplit=1)
            if instruction == 'a':
                self.add_thing(rest)
            elif instruction == 'r':
                self.remove_thing(rest)
            elif instruction == 'c':
                thing, comment = rest.strip().split('\t', maxsplit=1)
                self.comment(thing, comment)
            else:
                raise ValueError(f'Unrecognized instruction: "{instruction}"')
        self.loaded = True
        logger.info('Chain replayed from persistance')

    def store(self, instruction, *data):
        if not self.loaded:
            return
        if self.persistance is None:
            return
        tab = '\t'
        s = f'{instruction}{tab}{tab.join(data)}'
        self.persistance.write(f'{s}\n')
        logger.debug(f'Stored "{s}"')

    def add_thing(self, thing: str):
        self.state.add(thing)
        self.store('a', thing)

    def remove_thing(self, thing: str, current_count: typing.Optional[int] = None):
        if current_count is not None:
            actual_count = self.state.counts.get(thing, 0)
            if actual_count == current_count - 1:
                logging.debug(f'Same remove attempted by multiple clients for thing "{thing}"')
        self.state.remove(thing)
        self.store('r', thing)

    def comment(self, thing: str, comment: str):
        self.state.comment(thing, comment)
        self.store('c', thing, comment)
