import socket
from moonlapseshared.packet import *


class Protocol:
    def __init__(self, server, sock):
        self.server = server
        self.socket: socket.socket = sock

    def read(self):
        # todo: error handling
        bs = self.socket.recv(4)     # read header bytes
        header = Header.from_bytes(bs)
        data = self.socket.recv(header.length)
        p = from_bytes(bs + data, self.server.privkey)
        print(f"{self} received {p}")

    def fileno(self):
        return self.socket.fileno()
