import asyncio
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from pyice import web_async_v4 as web_async
from pyice import web_v4 as web
import threading
import time

def hello_world(req):
    req.create_response().set_body("Hello world!").send()

def hello_world_threaded(req):
    t = threading.Thread(target = lambda: hello_world(req))
    t.start()

async def hello_world_async(req):
    req.create_response().set_body("Hello world! (Async)").send()

server = web.Server(web.ServerConfig().set_num_executors(3).set_listen_addr("127.0.0.1:2716"))

hello_world_target = web.DispatchInfo(
    "/hello_world",
    hello_world
)
server.route(hello_world_target)

hello_world_threaded_target = web.DispatchInfo(
    "/hello_world_threaded",
    hello_world_threaded
)
server.route(hello_world_threaded_target)

hello_world_async_target = web_async.AsyncDispatchInfo(
    "/hello_world_async",
    hello_world_async
)
server.route(hello_world_async_target)

server.listen()

while True:
    time.sleep(10000000)
