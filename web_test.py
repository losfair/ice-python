import web
import time

server = web.Server()
server.listen("127.0.0.1:2716")

while True:
    time.sleep(10000000)
