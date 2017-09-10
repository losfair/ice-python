from . import core

running_servers = []

class Server:
    def __init__(self):
        self.inst = core.lib.ice_create_server()
        self.dispatch_table = {
            -1: DispatchInfo("", self.default_endpoint)
        }
        self.started = False
        self.callback_handle = core.ffi.callback("AsyncEndpointHandler", self.async_endpoint_cb)

        core.lib.ice_server_disable_request_logging(self.inst)
        core.lib.ice_server_set_async_endpoint_cb(
            self.inst,
            self.callback_handle
        )
    
    def __del__(self):
        if self.started == False:
            print("Warning: Server leaked")
    
    def require_not_started(self):
        if self.started:
            raise Exception("Server already started")
    
    def route(self, dispatch_info, flags = []):
        self.require_not_started()

        if not isinstance(dispatch_info, DispatchInfo):
            raise Exception("DispatchInfo required")

        ep = core.lib.ice_server_router_add_endpoint(self.inst, dispatch_info.path.encode())
        for f in flags:
            core.lib.ice_core_endpoint_set_flag(ep, f.encode(), True)

        ep_id = core.lib.ice_core_endpoint_get_id(ep)

        self.dispatch_table[ep_id] = dispatch_info
    
    def listen(self, addr):
        self.require_not_started()
        self.started = True
        running_servers.append(self)
        core.lib.ice_server_listen(self.inst, addr.encode())

    def async_endpoint_cb(self, id, call_info):
        req = Request(call_info)
        self.dispatch_table[id].call(req)

    def default_endpoint(self, req):
        req.create_response().set_status(404).set_body("Not found").send()

class DispatchInfo:
    def __init__(self, path, cb):
        if not callable(cb):
            raise Exception("Callable required")

        self.path = path
        self.callback = cb
    
    def call(self, req):
        try:
            self.callback(req)
        except Exception as e:
            req.create_response().set_status(500).set_body(str(e)).send()

class Request:
    def __init__(self, call_info):
        self.call_info = call_info
        self.inst = core.lib.ice_core_borrow_request_from_call_info(call_info)
        self.valid = True
    
    def __del__(self):
        if self.valid:
            self.create_response().set_status(500).send()

    def require_valid(self):
        if self.valid == False:
            raise Exception("Invalid request")
    
    def create_response(self):
        self.require_valid()
        
        return Response(self)
    
    def send_response(self, resp):
        self.require_valid()
        resp.require_valid()

        self.valid = False
        resp.valid = False

        core.lib.ice_core_fire_callback(self.call_info, resp.inst)


class Response:
    def __init__(self, req):
        self.request = req
        self.inst = core.lib.ice_glue_create_response()
        self.valid = True
    
    def __del__(self):
        if self.valid:
            self.valid = False
            core.lib.ice_glue_destroy_response(self.inst)
    
    def require_valid(self):
        if self.valid == False:
            raise Exception("Invalid response")
    
    def set_status(self, status):
        self.require_valid()
        core.lib.ice_glue_response_set_status(self.inst, status)
        return self
    
    def set_body(self, body):
        self.require_valid()

        if type(body) == str:
            body = body.encode()

        core.lib.ice_glue_response_set_body(self.inst, body, len(body))
        return self

    def send(self):
        self.require_valid()
        self.request.send_response(self)
