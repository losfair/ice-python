import pyice
import time
import asyncio

async def run():
    client = pyice.rpc.Client("127.0.0.1:1653")
    conn = await client.connect()
    print("Connected")

    for i in range(100000):
        ret = await conn.call("add", [
            pyice.rpc.Param.build_i32(i - 1),
            pyice.rpc.Param.build_i32(i + 1)
        ])
        print(ret.get_i32())

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
