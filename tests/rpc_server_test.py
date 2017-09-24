import pyice
import time

def add(ctx):
    a = ctx.get_param(0).get_i32()
    b = ctx.get_param(1).get_i32()
    ctx.end(pyice.rpc.Param.build_i32(a + b))

config = pyice.rpc.ServerConfig()
config.add_method("add", add)

server = pyice.rpc.Server(config)
server.start("127.0.0.1:1653")

while True:
    time.sleep(10000000)
