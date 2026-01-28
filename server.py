import socket
import struct
import threading
import queue
import traceback
import coloredlogs, logging

# TODO accept as cmd line arg
PORT = 3579

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG') # , logger=log

# TODO mutex for all lobby edits - mutex per lobby
class Lobby():
    def __init__(self, host, txbuf):
        pid = 0
        self.auth = {host: pid}
        self.peers = {pid: txbuf}

    def add(self, nick, txbuf):
        # TODO need mutex around this
        # update txbuf - only one connection per peer, assume reconnect, TODO determine if active connection, should be removed via close!
        # DON'T REMOVE, KEEP server-gen ID!
        if nick not in self.auth:
            self.auth[nick] = len(self.auth)
        pid = self.auth[nick]
        self.peers[pid] = txbuf

class Server():
    def __init__(self):
        self.lobbies = {}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket = s
        self.threads = []

    def run(self):
        log.debug("initiating listener...")
        self.socket.bind(('', PORT))
        self.socket.listen()
        log.info(f"listening on port {PORT}...")

        try:
            while True:
                self.threads = [t for t in self.threads if t.is_alive()]
                log.debug(f"active connections: #{len(self.threads)}")

                (conn, addr) = self.socket.accept()
                log.info(f"new connection: {addr}")
                t = threading.Thread(target=self.new_conn, args=(conn, addr), daemon=True)
                t.start()
                self.threads.append(t)
        except KeyboardInterrupt:
            log.info("interrupt received")
        finally:
            self.close()
    
    def new_conn(self, conn, addr):
        client = Connection(conn, addr, self.lobbies)
        client.handle()

    def close(self):
        log.info("shutting down...")
        self.socket.close()

class Connection():
    def __init__(self, socket, addr, lobbies):
        self.s = socket
        self.addr = addr
        self.lobbies = lobbies
        self.txbuf = queue.Queue()
        self.stop_event = threading.Event()
        self.tag = f"[{self.addr}]"

    # only return once done
    def handle(self):
        try:
            self.nick = self.recv_msg().decode().strip()
            log.info(f"{self.tag} nick: '{self.nick}'")

            self.lobby = struct.unpack('!I', self.recv_msg())[0]
            log.info(f"{self.tag} lobby: '{self.lobby}'")

            if not self.lobby:
                log.info("received empty lobby")
                # TODO reply with lobby
            
            # TODO mutex on lobbies
            if self.lobby in self.lobbies:
                log.info(f"{self.tag} joining lobby: {self.lobby}")
                self.lobbies[self.lobby].add(self.nick, self.txbuf)
            else:
                log.info(f"{self.tag} new lobby: {self.lobby}")
                self.lobbies[self.lobby] = Lobby(self.nick, self.txbuf)

            self.pid = self.lobbies[self.lobby].auth[self.nick]
            log.info(f"{self.tag} assigned pid: {self.pid}")
            self.tag = f"[{self.addr}:{self.nick}[{self.pid}]@{self.lobby}]"

            self.send(struct.pack('!B', self.pid))

            # TODO maybe to tx in thread instead and sent None to txbuf when rx returns
            rx = threading.Thread(target=self.rx, daemon=True)
            rx.start()

            self.tx()
            # dup
            self.stop_event.set()

            rx.join()
        except Exception as e:
            log.error(traceback.format_exc())
        finally:
            self.close()

    def tx(self):
        while not self.stop_event.is_set():
            try:
                m = self.txbuf.get(timeout=1)
            except queue.Empty:
                continue

            log.debug(f"{self.tag} tx: {m}")

            if m is None:
                self.stop_event.set()
                break

            self.send(m)
    
    def rx(self):
        try:
            while not self.stop_event.is_set():
                m = self.recv_msg()
                dest = self.lobbies[self.lobby].peers
                log.info(f"{self.tag} rx (-> #{len(dest)-1}): {m}")
                # TODO test exception here

                for peer, peerbuf in dest.items():
                    if peer == self.pid:
                        continue
                    log.info(f"{self.tag} tx -> {peer} ({peerbuf.qsize()})")
                    peerbuf.put(m)
        finally:
            self.stop_event.set()

    def send(self, m: bytes):
        # 2 byte header
        header = struct.pack('!H', len(m))
        self.s.sendall(header + m)

    def recv_msg(self):
        raw_len = self.recv_exact(2)
        msg_len = struct.unpack('!H', raw_len)[0]
        return self.recv_exact(msg_len)

    def recv_exact(self, n):
        m = b''
        while len(m) < n:
            chunk = self.s.recv(n - len(m))
            if not chunk:
                raise ConnectionError("Socket closed")
            m += chunk
        return m

    def close(self):
        # TODO ensure queues are dead
        self.stop_event.set()
        self.s.close()

Server().run()
