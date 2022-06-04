import socket
from moonlapseshared.packet import *
from protostate import *


class Protocol:
    def __init__(self, server, sock):
        self.server = server
        self.socket: socket.socket = sock
        self.state = EntryState(self)

    def disconnect(self, reason="graceful"):
        print(f"{self} disconnected. Reason: {reason}")
        self.server.selector.unregister(self)
        self.server.protocols.pop(self.fileno())

    def send_packet(self, p: Packet):
        print(f"sending ({p}) to {self}")
        self.socket.send(p.to_bytes(self.server.pubkey))

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
            self.state.dispatch_packet(p)
        except Exception as e:
            print(f"{self} received some bytes, but they were not well formed.")
            print(e)

    def fileno(self):
        return self.socket.fileno()

    def __str__(self):
        return f"Protocol:{self.fileno()}@{self.state.__class__.__name__}"
