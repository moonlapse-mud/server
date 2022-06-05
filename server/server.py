from selectors import *
import os
import sys
import threading
import time
from .protocol import *
import socket
from moonlapseshared import crypto
from typing import Dict


PORT = 42523
TICKRATE = 0.5


class Server:
    def __init__(self):
        self.selector = DefaultSelector()
        self.protocols: Dict[int, Protocol] = {}     # map of socket FD : Protocol
        self.socket = None      # accept listener
        self.pipe_r, self.pipe_w = os.pipe()    # pipe used for timer
        self.pubkey, self.privkey = crypto.load_rsa_keypair(os.path.dirname(os.path.realpath(sys.argv[0])))
        self.timer = threading.Thread(target=self._timer_loop, daemon=True)
        self.tickrate = TICKRATE      # 20 ticks per second

    def start(self):
        try:
            # set up listen socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('', PORT))
            self.socket.listen(1)
            print(f"Moonlapse Server listening on {PORT}")

            self.timer.start()
            self._main_loop()
        except Exception as e:
            print(f"Error setting up the server. {e}")
            sys.exit(1)

    def _accept(self, sock: socket.socket):
        try:
            print("Received new connection")
            proto_s, _ = sock.accept()
            proto = Protocol(self, proto_s)
            self.protocols[proto_s.fileno()] = proto
            self.selector.register(proto, EVENT_READ, self._read)
        except Exception as e:
            print(f"Error during accept. {e}")

    def _read(self, proto: Protocol):
        proto.read()

    def _main_loop(self):
        self.selector.register(self.socket, EVENT_READ, self._accept)
        self.selector.register(self.pipe_r, EVENT_READ, self._tick)

        while True:
            events = self.selector.select()
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)

    def _tick(self, _):
        os.read(self.pipe_r, 1)
        for proto in self.protocols.values():
            proto.tick()

    def _timer_loop(self):
        while True:
            time.sleep(1.0 / self.tickrate)
            os.write(self.pipe_w, b'1')
