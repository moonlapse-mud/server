import manage
from server.server import Server
import trio


if __name__ == '__main__':
    s = Server()
    trio.run(s.start)
