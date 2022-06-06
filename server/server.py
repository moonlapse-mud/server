import os
import sys
from .protocol import *
from moonlapseshared import crypto
from typing import Dict
import trio.socket as socket
import trio


PORT = 42523
TICKRATE = 0.5


class Server:
    def __init__(self):
        self.protocols: Dict[int, Protocol] = {}     # map of socket FD : Protocol
        self.socket: socket.socket = None      # accept listener
        self.pubkey, self.privkey = crypto.load_rsa_keypair(os.path.dirname(os.path.realpath(sys.argv[0])))
        self.tickrate = TICKRATE      # 20 ticks per second

    async def start(self):
        try:
            # set up listen socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            await self.socket.bind(('', PORT))
            self.socket.listen(1)
            print(f"Moonlapse Server listening on {PORT}")

            async with trio.open_nursery() as nursery:
                # start tick timer
                nursery.start_soon(self._tick_loop)

                # start accept loop
                await self._accept_loop(nursery)
        except Exception as e:
            print(f"Error setting up the server. {e}")
            sys.exit(1)

    async def _accept_loop(self, nursery):
        while True:
            try:
                proto_s, _ = await self.socket.accept()
                print("New connection!", flush=True)
                proto = Protocol(self, proto_s)
                self.protocols[proto_s.fileno()] = proto
                nursery.start_soon(proto.read_loop)
            except Exception as e:
                print(f"Error during accept. {e}")

    async def _tick_loop(self):
        while True:
            await trio.sleep(1.0 / self.tickrate)

            for proto in self.protocols.values():
                await proto.tick()
