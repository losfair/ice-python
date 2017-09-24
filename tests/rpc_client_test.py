import pyice
import time

def on_call_done(ret):
    print(ret.get_i32())

def on_connect_done(conn):
    print("Connected")
    conn.call("add", [
        pyice.rpc.Param.build_i32(1),
        pyice.rpc.Param.build_i32(2)
    ], on_call_done)

client = pyice.rpc.Client("127.0.0.1:1653")
client.connect(on_connect_done)

while True:
    time.sleep(10000000)
