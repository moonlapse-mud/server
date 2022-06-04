from selectors import *
import os
import sys
import threading
from protocol import *
import socket
from moonlapseshared import crypto


PORT = 42523


class Server:

    def __init__(self):
        self.selector = DefaultSelector()
        self.protocols = {}     # map of socket FD : Protocol
        self.socket = None
        self.pipe_r, self.pipe_w = os.pipe()    # pipe used for timer
        self.pubkey, self.privkey = crypto.load_rsa_keypair(os.path.dirname(os.path.realpath(sys.argv[0])))
        self.timer = None
        self.tickrate = 0.5      # 20 ticks per second

    def start(self):
        # todo: error handling
        # set up listen socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', PORT))
        self.socket.listen(1)
        print(f"Moonlapse Server listening on {PORT}")

        # set up tick timer
        self.timer = threading.Timer(1.0 / self.tickrate, self._timer_callback)
        self.timer.start()

        self._main_loop()

    def accept(self, sock: socket.socket):
        print("Received new connection")
        proto_s, _ = sock.accept()
        proto = Protocol(self, proto_s)
        self.protocols[proto_s.fileno()] = proto
        self.selector.register(proto, EVENT_READ, self.read)

    def read(self, proto: Protocol):
        proto.read()

    def _main_loop(self):
        self.selector.register(self.socket, EVENT_READ, self.accept)
        self.selector.register(self.pipe_r, EVENT_READ, self._tick)

        while True:
            events = self.selector.select()
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)

    def _tick(self, _):
        os.read(self.pipe_r, 1)
        print("Tick!")

    def _timer_callback(self):
        os.write(self.pipe_w, b'1')

        # restarting the timer
        self.timer = threading.Timer(1.0 / self.tickrate, self._timer_callback)
        self.timer.start()
