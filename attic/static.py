#!/usr/bin/env python3


import pathlib
import typing as t
import mimetypes


mimetypes.add_type("text/gemini", ".gmi")


class ResolvedFile:
    def __init__(self, filepath: pathlib.Path, mimetype: str = None):
        self.path = filepath
        if mimetype is not None:
            self.mimetype = mimetype
        else:
            mimetype, encoding = mimetypes.guess_type(filepath, strict=False)
            self.mimetype = mimetype or "application/octet-stream"

    def __repr__(self):
        return f'<ResolvedFile [{self.mimetype}] {self.path}>'


class ResolvedDir:
    def __init__(self, child_paths: t.List[str]):
        self.child_paths = child_paths

    def __repr__(self):
        return f"<ResolvedDir {', '.join(self.child_paths)}>"


class StaticFileResolver:
    def __init__(self, root: str = '.', index_file: str = 'index.gmi'):
        self.root = pathlib.Path(root).resolve(strict=True)
        self.index_file = index_file
        self.files = {}
        self.dirs = {}

    def scan(self):
        self.files = {}
        self.dirs = {}

        def get_parent_path(parent):
            parent_path = str(parent.relative_to(self.root))
            if parent_path == '.':
                return '/'
            else:
                return '/' + parent_path + ('/' if parent_path else '')

        def scan_dir(parent):
            print('scanning', parent)
            found_index_file = False
            child_paths = []
            if not parent == self.root:
                parent_path = get_parent_path(parent.parent)
                child_paths.append('..' + parent_path)
            for child in parent.iterdir():
                if child.is_file():
                    local_path = child.relative_to(self.root)
                    self.add_file('/' + str(local_path), local_path)
                    if child.name == self.index_file:
                        parent_path = get_parent_path(parent)
                        self.add_file(parent_path, local_path)
                        found_index_file = True
                    child_paths.append(str(child.relative_to(parent)))

                elif child.is_dir():
                    scan_dir(child)
                    child_paths.append(str(child.relative_to(parent)) + '/')
            if not found_index_file:
                parent_path = get_parent_path(parent)
                self.add_dir(parent_path, child_paths)

        scan_dir(self.root)

    def add_file(self, remote: str, local: pathlib.Path, mimetype: str = None):
        f = ResolvedFile(self.root / local, mimetype)
        self.files[remote] = f
        print('f', remote, '->', f)

    def resolve_file(self, remote: str) -> t.Optional[ResolvedFile]:
        return self.files.get(remote)

    def add_dir(self, remote: str, child_paths: t.List[str]):
        d = ResolvedDir(child_paths)
        self.dirs[remote] =d
        print('d', remote, '->', d)

    def resolve_dir(self, remote: str) -> t.Optional[ResolvedDir]:
        if not remote.endswith('/'):
            remote += '/'
        return self.dirs.get(remote)
