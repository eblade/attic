#!/usr/bin/env python3

import os
import shutil
from datetime import datetime
from socketserver import ThreadingTCPServer, StreamRequestHandler
from urllib.parse import unquote
from attic.static import StaticFileResolver, ResolvedFile


MAX_QUERY_LENGTH = 4096


class SpartanRequestHandler(StreamRequestHandler):
    @classmethod
    def maker(cls, resolver):
        def make(*args, **kwargs):
            return cls(resolver, *args, **kwargs)
        return make

    def __init__(self, resolver, *args, **kwargs):
        self.resolver = resolver
        super().__init__(*args, **kwargs)

    def handle(self):
        try:
            self._handle()
        except ValueError as e:
            self.write_status(4, e)
        except Exception:
            self.write_status(5, "Internal Server Error")
            raise

    def _handle(self):
        request = self.rfile.readline(MAX_QUERY_LENGTH)
        request = request.decode("ascii").strip("\r\n")
        print(f'{datetime.now().isoformat()} "{request}"')

        hostname,path, content_length = request.split(" ")
        if not path:
            raise ValueError('Not Found')

        path = unquote(path)

        if resolved_file := self.resolver.resolve_file(path):
            self.write_file(resolved_file)
        elif resolved_dir := self.resolver.resolve_dir(path):
            if not path.endswith('/'):
                self.write_status(3, f"{path}/")
            else:
                self.write_status(2, "text/gemini")
                for child in resolved_dir.child_paths:
                    if child.startswith('../'):
                        label, path = child.split('/', 1)
                        self.write_line(f"=>/{path} {label}")
                    else:
                        self.write_line(f"=>{child}")
        else:
            raise ValueError("Not Found")

    def write_file(self, resolved_file: ResolvedFile):
        with resolved_file.path.open("rb") as fp:
            self.write_status(2, resolved_file.mimetype)
            shutil.copyfileobj(fp, self.wfile)

    def write_line(self, text):
        self.wfile.write(f"{text}\n".encode("utf-8"))

    def write_status(self, code, meta):
        self.wfile.write(f"{code} {meta}\r\n".encode("ascii"))

if __name__ == '__main__':
    resolver = StaticFileResolver('/home/johan.egneblad/git/gemini/content')
    #resolver = StaticFileResolver('test')
    resolver.scan()
    #resolver.add_file('/test.gmi', 'test.gmi')
    #resolver.add_file('/index.gmi', 'index.gmi')
    #resolver.add_file('/', 'index.gmi')
    #resolver.add_dir('/fake/', ['index.gmi', 'test.gmi'])
    ThreadingTCPServer.allow_reuse_address = True
    server = ThreadingTCPServer(('127.0.0.1', 3000),
                                SpartanRequestHandler.maker(resolver))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.socket.close()
