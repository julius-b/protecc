from game import Game
from client import NetClient
import time
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("nick", help="nickname")
parser.add_argument("lobby", help="lobby")
args = parser.parse_args()

client = NetClient('localhost', 3579, args.nick, 123)
threading.Thread(target=client.run, daemon=True).start()

while True:
    pid = client.pid
    if pid == None:
        print("waiting for pid...")
        time.sleep(0.5)
        continue
    else:
        break

g = Game(client, pid)
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
