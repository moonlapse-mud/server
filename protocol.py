import socket
from moonlapseshared.packet import *


class Protocol:
    def __init__(self, server, sock):
        self.server = server
        self.socket: socket.socket = sock

    def disconnect(self, reason="graceful"):
        print(f"{self} disconnected. Reason: {reason}")
        self.server.selector.unregister(self)
        self.server.protocols.pop(self.fileno())

    def read(self):
        try:
            bs = self.socket.recv(4)     # read header bytes
            if not bs:
                # disconnected
                self.disconnect()
                return

            header = Header.from_bytes(bs)
            data = self.socket.recv(header.length)
            p = from_bytes(bs + data, self.server.privkey)
            print(f"{self} received {p}")
        except Exception:
            print(f"{self} received some bytes, but they were not well formed.")

    def fileno(self):
        return self.socket.fileno()
