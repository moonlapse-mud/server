from .protostate import *
from collections import deque
import trio.socket as socket


class Protocol:
    def __init__(self, server, sock):
        self.server = server
        self.socket: socket.socket = sock
        self.state = EntryState(self)
        self.outgoing = deque()
        self.incoming = deque()

    async def tick(self):
        # process all packets in incoming queue
        for p in list(self.incoming):
            self.state.dispatch_packet(p)
            self.incoming.popleft()

        # send all packets in queue back to client in order
        for p in list(self.outgoing):
            await self.send_packet(p)
            self.outgoing.popleft()

    def disconnect(self, reason="graceful"):
        print(f"{self} disconnected. Reason: {reason}")
        self.server.protocols.pop(self.fileno())

    async def send_packet(self, p: Packet):
        print(f"sending ({p}) to {self}", flush=True)
        await self.socket.send(p.to_bytes(self.server.pubkey))

    async def read_loop(self):
        while True:
            try:
                bs = await self.socket.recv(4)  # read header bytes
                if not bs:
                    # disconnected
                    self.disconnect()
                    return

                header = Header.from_bytes(bs)

                data = await self.socket.recv(header.length)
                if not data:
                    # disconnected
                    self.disconnect()
                    return

                p = from_bytes(bs + data, self.server.privkey)
                print(f"{self} received {p}. Adding to incoming queue.", flush=True)
                self.incoming.append(p)
            except Exception as e:
                print(f"{self} received some bytes, but they were not well formed.")
                print(e)

    def fileno(self):
        return self.socket.fileno()

    def __str__(self):
        return f"Protocol:{self.fileno()}@{self.state.__class__.__name__}"
