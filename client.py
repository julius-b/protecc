import socket
import struct
import time
import threading
import queue
import traceback
import coloredlogs, logging
import json
from const import *

# queue: don't block game thread

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG') # , logger=log

# TODO automatic reconnect (same queue instance for client)
# - on connect send/request full current state!
# reusing socket after '[Errno 111] Connection refused': '[Errno 9] Bad file descriptor'
class NetClient():
    def __init__(self, host, port, nick, lobby = 0):
        self.rxbuf = queue.Queue()
        self.txbuf = queue.Queue()
        self.host = host
        self.port = port
        self.nick = nick
        self.lobby = lobby
        self.pid = None

    def run(self):
        while True:
            self.stop_event = threading.Event()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.socket = s
            # clear txbuf or send on new conn?
            try:
                log.info(f"attempting to establish a connection: {self.host}:{self.port}...")
                self.socket.connect((self.host, self.port))
                log.info(f"connection established: {self.host}:{self.port}")

                # auth
                self.send(self.nick.encode())
                self.send(struct.pack('!I', self.lobby))
                self.pid = struct.unpack('!B', self.recv_msg())[0]
                log.info(f"received pid: {self.pid}")

                rx = threading.Thread(target=self.rx)
                rx.start()

                self.tx()
                # dup
                self.stop_event.set()

                rx.join()
            except Exception as e:
                log.error(f"connection failure: {self.host}:{self.port}")
                log.error(traceback.format_exc())
                self.close()
            finally:
                # net-client runs as daemon, won't stop app from shutting down
                log.info('standby...')
                time.sleep(1)
    
    def tx(self):
        while not self.stop_event.is_set():
            try:
                m = self.txbuf.get(timeout=0.5)
            except queue.Empty:
                continue

            log.debug(f"tx: {m}")

            if m is None:
                self.stop_event.set()
                break

            self.send(m)
    
    # decode msg here rather than in game loop
    def rx(self):
        try:
            while not self.stop_event.is_set():
                m = self.recv_msg()
                print(f"rx: {m}")
                # TODO determine first byte
                pp = struct.unpack(PLAYER_PACKET, m)
                print(f"pp: {pp}")
                self.rxbuf.put(pp)
                # TODO test exception here
        except Exception as e:
            self.stop_event.set()

    def send(self, m: bytes):
        log.debug(f"send: {m}")
        # 2 byte header
        header = struct.pack('!H', len(m))
        self.socket.sendall(header + m)

    def recv_msg(self):
        raw_len = self.recv_exact(2)
        msg_len = struct.unpack('!H', raw_len)[0]
        return self.recv_exact(msg_len)

    def recv_exact(self, n):
        m = b''
        while len(m) < n:
            chunk = self.socket.recv(n - len(m))
            if not chunk:
                raise ConnectionError("Socket closed")
            m += chunk
        return m

    def close(self):
        log.info("shutting down...")
        self.socket.close()
