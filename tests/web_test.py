import asyncio

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    print("Warning: Unable to initialize uvloop")

from pyice import web_async
from pyice import web
import threading
import time

server = web.Server(web.ServerConfig().set_num_executors(3).set_listen_addr("127.0.0.1:2716"))

@server.define_route("/hello_world")
def hello_world(req):
    req.create_response().set_body("Hello world!").send()

@server.define_route("/hello_world_threaded")
def hello_world_threaded(req):
    t = threading.Thread(target = lambda: hello_world(req))
    t.start()

@server.define_route("/hello_world_async")
async def hello_world_async(req):
    req.create_response().set_body("Hello world! (Async)").send()

@server.define_route(None)
def default_target(req):
    req.create_response().set_body("Target not found").send()

server.listen()

while True:
    time.sleep(10000000)
