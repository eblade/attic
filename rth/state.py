import logging
from typing import Dict, List


logger = logging.getLogger(__name__)


class State:
    def __init__(self):
        self.categories: Dict[str, str] = {}
        self.things: Dict[str, str] = {}
        self.counts: Dict[str, int] = {}
        self.comments: Dict[str, List[str]] = {}

    def load_categories(self, path: str):
        self.categories = {}
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                elif line.startswith('#'):
                    continue
                short, category = line.split(maxsplit=1)
                if short in self.categories:
                    raise KeyError(f'Duplicate category key: "{short}"')
                self.categories[short] = category

    def load_things(self, path: str):
        self.things = {}
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                elif line.startswith('#'):
                    continue
                category, thing = line.split(maxsplit=1)
                if category not in self.categories:
                    raise KeyError(f'Category not found: "{category}"')
                if thing in self.things:
                    raise KeyError(f'Duplicate thing: "{thing}"')
                self.things[thing] = category

    def add(self, thing: str):
        if thing not in self.things:
            raise KeyError(f'There is no such thing: {thing}')
        if thing not in self.counts:
            self.counts[thing] = 1
        else:
            self.counts[thing] += 1

    def remove(self, thing: str):
        if thing not in self.things:
            raise KeyError(f'There is no such thing: {thing}')
        if thing not in self.counts:
            self.counts[thing] = -1
        else:
            self.counts[thing] -= 1
        if self.counts[thing] <= 0 and thing in self.comments:
            del self.comments[thing]

    def comment(self, thing: str, comment: str):
        if thing not in self.things:
            raise KeyError(f'There is no such thing: {thing}')
        if thing not in self.counts:
            logger.warn(f'Tried to comment on uncounted thing "{thing}"')
            return
        current_count = self.counts[thing]
        if current_count <= 0:
            logger.warn(f'Tried to comment on thing "{thing}" with count {current_count}')
            return
        if thing not in self.comments:
            self.comments[thing] = [comment]
        else:
            self.comments[thing].append(comment)
