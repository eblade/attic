from typing import Dict, Set


class State:
    def __init__(self):
        self.categories: Dict[str. str] = {}
        self.things: Dict[str. str] = {}

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
                    raise KeyError('Duplicate category key: "{short}"')
                self.categories[short] = category

    def load_things(self, path: str):
        self.categories = {}
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                elif line.startswith('#'):
                    continue
                category, thing = line.split(maxsplit=1)
                if category not in self.categories:
                    raise KeyError('Category not found: "{category}"')
                if thing in self.things:
                    raise KeyError('Duplicate thing: "{thing}"')
                self.things[thing] = category
