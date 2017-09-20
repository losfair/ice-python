from . import web_v4 as web
import asyncio
import threading

global_event_loop = asyncio.new_event_loop()
event_loop_executor = threading.Thread(target = lambda: global_event_loop.run_forever())
event_loop_executor.daemon = True
event_loop_executor.start()

class AsyncDispatchInfo(web.DispatchInfo):
    def call(self, req):
        if hasattr(self, "event_loop"):
            t = self.event_loop
        else:
            t = global_event_loop
        asyncio.run_coroutine_threadsafe(self.async_call(req), t)

    async def async_call(self, req):
        try:
            await self.callback(req)
        except Exception as e:
            req.create_response().set_status(500).set_body(str(e)).send()
