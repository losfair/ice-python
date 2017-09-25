import pyice
import time
import asyncio

async def run():
    client = pyice.rpc.Client("127.0.0.1:1653")
    pool = pyice.rpc.ClientConnectionPool(client)
    await pool.init()

    print("Connected")

    for i in range(100000):
        ret = await pool.call("add", [
            pyice.rpc.Param.build_i32(i - 1),
            pyice.rpc.Param.build_i32(i + 1)
        ])
        if ret == None:
            print("RPC Call failed")
        else:
            print(ret.get_i32())

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
